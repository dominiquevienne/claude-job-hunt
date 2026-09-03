#!/usr/bin/env python3
"""Fetch French ads from randstad.fr — the second interim network here.

**6 755 ads**, from the three job-detail sitemaps the site's `robots.txt`
declares. Half the volume of `adecco.md`, and **better data on every axis that
matters**:

                        adecco.md            randstadfr.md
  postalCode            empty on every ad    on every ad
  city in the URL       truncated, unusable  matches the ad, 22 of 22
  currency              "France "            EUR
  employmentType        "Temps plein"/"null" CONTRACTOR — the schema vocabulary
  validThrough          a real date          absent, and honestly so

**The employer is `Randstad France` on every ad**, which is the one thing it
shares with its sibling: the client is described and never named, so there is
no company to research and no key to deduplicate against an employer's ATS.

  GET /robots.txt                       → Sitemap: //www.randstad.fr/sitemaps/sitemap.xml
  GET /sitemaps/sitemap.xml             → 32 sitemaps, 3 of job details
  GET /sitemaps/jobs/sitemap-jobdetails*.xml
  GET /emploi/<poste>_<ville>_<ref>/    → the ad, JSON-LD JobPosting

Usage:
  randstadfr.py discover --ville lyon
  randstadfr.py search --ville royan
  randstadfr.py search --departement 33 --limit 20

Output: one JSON object per line.
"""

import argparse
import html as html_mod
import json
import re

from _decode import decode_body
from _ldjson import one, postings
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _robots import allowed as robots_allowed

BASE = "https://www.randstad.fr"
INDEX = BASE + "/sitemaps/sitemap.xml"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

URL_BLOCK_RE = re.compile(r"(?s)<url>(.*?)</url>")
SITEMAP_BLOCK_RE = re.compile(r"(?s)<sitemap>(.*?)</sitemap>")
# Reads the plain `<loc>https://…</loc>` and the CDATA-wrapped form both.
# hays.fr serves the second, where the first non-space character after the tag
# is `<` and the strict pattern `<loc>\s*([^<\s]+)` matches nothing at all —
# 0 URLs from a valid 2.37 MB sitemap. See issue #55 and `hays-fr.md`.
SITEMAP_LOC_RE = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?\s*([^\s\]<]+)")
MOD_RE = re.compile(r"<lastmod>([^<]*)")
# **This site writes `<script type='application/ld+json'>` with single
# quotes**, and a pattern requiring double ones matches nothing: the adapter
# then reports `json_ld: false` on every ad — a total failure wearing the face
# of "this board publishes no structured data". Quote style is not a contract.
#
# The pattern that survived that lesson now lives in `_ldjson.py` and serves
# every board here, because ten of the eighteen readers in this repository
# had the brittle form and only this one had been bitten. Issue #76.
DEPT_RE = re.compile(r"^(?:\d{2}|2[AB])$")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def _robots_gate(url, tag, exit_code=7):
    """Ask before fetching — per host and **per path**. Issues #100, #101.

    `verdict()` answers *is this host closed in one block*. **A site that
    refuses its ad path while leaving its root open passes that and refuses
    every advertisement** — `empleate.gob.hn` does exactly that, closing
    `/Vacantes/` to `User-agent: *` with `/` absent.

    It sits **inside the fetch function**, so every request is covered rather
    than the first one, and a refusal **stops the command** with exit 7 and the
    module's own words. **This adapter decides nothing about what a refusal
    means** — deciding is what turns a check into a decoration.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return None
    a = robots_allowed(parts.netloc, parts.path or "/")
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", exit_code)
    if a.get("requested_host") and a["host"] != a["requested_host"]:
        print(f"[randstadfr] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts. A platform that has "
              f"been renamed reaches an adapter this way before it reaches it "
              f"as a rename.", file=__import__("sys").stderr)
    return a



def fold(s):
    """Lowercase, unaccented, letters only — for comparing town names.

    `Aire-sur-l'Adour` in the ad and `aire-sur-ladour` in the URL are the same
    town; the apostrophe and the accents are the only difference.
    """
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return re.sub(r"[^a-z]", "", s.encode("ascii", "ignore").decode())


def get(url, gone_is_ok=False, retries=2):
    _robots_gate(url, 'randstadfr')
    p = urllib.parse.urlsplit(url)
    safe = urllib.parse.urlunsplit(
        (p.scheme, p.netloc, urllib.parse.quote(p.path, safe="/"),
         p.query, p.fragment))
    req = urllib.request.Request(safe, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "fr-FR,fr;q=0.9",
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return decode_body(r.read(), r.headers)[0]
        except urllib.error.HTTPError as e:
            if gone_is_ok and e.code in (404, 410):
                # An ad the sitemap still lists and the site has retired. One
                # dead ad is not a dead board.
                return None
            die(f"randstad.fr returned HTTP {e.code} for {url}")
        except Exception as e:  # noqa: BLE001 - network shape varies
            if attempt == retries:
                die(f"could not reach randstad.fr: {e}")
            time.sleep(2.0)
    return ""


def job_sitemaps():
    idx = get(INDEX)
    all_maps = SITEMAP_LOC_RE.findall(idx)
    if not all_maps:
        # In a sitemap index the mandatory container is <sitemap>, not <url>.
        # Naming its count tells the reader which half failed. Issue #55.
        blocks = len(SITEMAP_BLOCK_RE.findall(idx))
        die(f"{INDEX} parsed to zero <loc> out of {len(idx)} characters and "
            f"{blocks} <sitemap> blocks. That is a read failure, not an "
            "empty board — zero <loc> inside a non-zero number of blocks "
            "cannot occur in a valid sitemap index.")
    out = sorted(u for u in all_maps if "jobdetails" in u)
    if not out:
        die("the sitemap index declared no jobdetails file. It listed: "
            + ", ".join(u.rsplit("/", 1)[-1] for u in all_maps[:8]))
    return out


def entries():
    """(url, lastmod) for every ad, across the job-detail sitemaps.

    **`lastmod` here is batched, not per ad**: 535 distinct values across
    5 000 URLs, so roughly nine ads share a timestamp. It is a real signal —
    unlike `figaro-emploi.md`, where 30 000 entries carry one build stamp — but
    it is coarser than `wttj.md`'s 7 691 in 10 000. Use `--since` to skip a
    re-scan, not to date an ad.
    """
    out = []
    for sm in job_sitemaps():
        page = get(sm)
        blocks = URL_BLOCK_RE.findall(page)
        if not blocks:
            die(f"{sm} parsed to zero <url> blocks out of {len(page)} "
                "characters — a read failure, not an empty sitemap.")
        before = len(out)
        for b in blocks:
            loc = SITEMAP_LOC_RE.search(b)
            if not loc:
                continue
            mod = MOD_RE.search(b)
            out.append((loc.group(1), mod.group(1).strip() if mod else None))
        if len(out) == before:
            # Zero <loc> in N <url> blocks is impossible in a valid sitemap.
            # Issue #55.
            die(f"{sm} gave zero URLs out of {len(blocks)} <url> blocks. "
                "That combination cannot occur in a valid sitemap: it is a "
                "reading fault, not an empty sitemap.")
        time.sleep(0.4)
    return out


def url_town(url):
    """The town from the URL slug — `<poste>_<ville>_<ref>`.

    **Reliable here**, unlike `adecco.md`, where the slug's tail is a
    department truncated to its last word. Checked on 22 of 22: the URL's town
    and the ad's `addressLocality` are the same place once accents and
    apostrophes are folded away.
    """
    tail = url.rstrip("/").rsplit("/", 1)[-1].split("_")
    return tail[1] if len(tail) > 1 else None


def money(v):
    """A figure, or None when the board wrote zero.

    `14 → 0 → HOUR` is an hourly rate with no ceiling, not a range down to
    nothing. Emitting the zero invites a reader to print "14 to 0 €".
    """
    if v is None:
        return None
    v = str(v).strip()
    if not v:
        return None
    try:
        return None if float(v) == 0 else v
    except ValueError:
        return v


def text_of(raw):
    if not raw:
        return None
    t = html_mod.unescape(raw)
    t = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</h\d>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html_mod.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def card(url, lastmod):
    page = get(url, gone_is_ok=True)
    ident = url.rstrip("/").rsplit("/", 1)[-1]
    if page is None:
        return {"id": ident, "ledger_id": f"randstad-fr:{ident}", "url": url,
                "gone": True}
    # One reader for every board's ld+json: tolerant of the quote style
    # on the script tag, and strict=False on the parse. Issue #76.
    jp = (postings(page) or [None])[-1]
    if jp is None:
        if "JobPosting" in page:
            # The page says JobPosting and the parser did not find one. That
            # is a broken reader, not a board without structured data, and the
            # difference is worth an exit code.
            die(f"{url} contains 'JobPosting' but no ld+json block parsed. "
                "The markup changed — check the quote style and the script "
                "attributes before believing any count from this run.")
        return {"id": ident, "ledger_id": f"randstad-fr:{ident}", "url": url,
                "json_ld": False}
    addr = one(jp.get("jobLocation")).get("address") or {}
    sal = one(jp.get("baseSalary")).get("value") or {}
    return {
        "id": ident,
        "ledger_id": f"randstad-fr:{ident}",
        "url": url,
        "reference": one(jp.get("identifier")).get("value"),
        "title": jp.get("title"),
        # The agency, on every ad. Flagged rather than left to be mistaken for
        # the workplace — the client is described in the body and never named.
        "company": one(jp.get("hiringOrganization")).get("name"),
        "employer_is_the_agency": True,
        "locality": addr.get("addressLocality"),
        "region": addr.get("addressRegion"),
        # Present on every ad measured — which `adecco.md` never manages.
        "postcode": addr.get("postalCode"),
        "country": addr.get("addressCountry"),
        # The schema.org vocabulary, correctly spelled.
        "employment_type": jp.get("employmentType"),
        "salary_min": money(sal.get("minValue")),
        "salary_max": money(sal.get("maxValue")),
        "salary_unit": sal.get("unitText"),
        "salary_currency": one(jp.get("baseSalary")).get("currency"),
        "sector": jp.get("industry"),
        "published": jp.get("datePosted"),
        # Absent on every ad, and that is the honest answer rather than
        # datePosted plus a constant.
        "valid_through": jp.get("validThrough"),
        "lastmod": lastmod,
        "description": text_of(jp.get("description")),
        "json_ld": True,
    }


def narrow(rows, a):
    if a.ville:
        want = fold(a.ville)
        before = len(rows)
        rows = [r for r in rows if fold(url_town(r[0])) == want]
        print(f"[randstad-fr] {len(rows)} of {before} in {a.ville!r}, "
              "filtered on the URL before any fetch", file=sys.stderr)
    if a.since:
        before = len(rows)
        rows = [r for r in rows if (r[1] or "") >= a.since]
        print(f"[randstad-fr] {len(rows)} of {before} since {a.since}",
              file=sys.stderr)
    return rows


def cmd_discover(a):
    rows = narrow(entries(), a)
    for url, mod in rows[:a.limit or None]:
        ident = url.rstrip("/").rsplit("/", 1)[-1]
        print(json.dumps({"url": url, "id": ident,
                          "ledger_id": f"randstad-fr:{ident}",
                          "town_from_url": url_town(url), "lastmod": mod},
                         ensure_ascii=False))
    print(f"[randstad-fr] {min(len(rows), a.limit or len(rows))} ad URLs",
          file=sys.stderr)


def cmd_search(a):
    rows = entries()
    print(f"[randstad-fr] {len(rows)} ads in the sitemaps", file=sys.stderr)
    rows = narrow(rows, a)
    depts = set(a.departement or [])
    for d in depts:
        if not DEPT_RE.match(d):
            die(f"{d!r} is not a two-character department code.")
    kept, dropped, gone, read = 0, 0, 0, 0
    for url, mod in rows:
        if a.limit and kept >= a.limit:
            break
        if read >= a.max_read:
            print(f"[randstad-fr] stopped after reading {read} ads — the cap. "
                  "A --departement filter reads from the top of the sitemap "
                  "until it finds matches, because the postcode is only on "
                  "the ad. Narrow with --ville, which is free, or raise "
                  "--max-read.", file=sys.stderr)
            break
        read += 1
        c = card(url, mod)
        if c.get("gone"):
            gone += 1
            time.sleep(a.delay)
            continue
        if depts and (c.get("postcode") or "")[:2] not in depts:
            dropped += 1
            time.sleep(a.delay)
            continue
        print(json.dumps(c, ensure_ascii=False))
        kept += 1
        time.sleep(a.delay)
    print(f"[randstad-fr] {kept} ads returned, {read} read", file=sys.stderr)
    if dropped:
        print(f"[randstad-fr] {dropped} dropped by --departement, read to be "
              "filtered: the postcode is on the ad, not in the URL. Narrow "
              "with --ville first, which is free.", file=sys.stderr)
    if gone:
        print(f"[randstad-fr] {gone} were already gone", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, helptext in (("discover", cmd_discover, "ad URLs only"),
                               ("search", cmd_search, "read the ads")):
        c = sub.add_parser(name, help=helptext)
        c.add_argument("--ville", help="town as in the URL, e.g. royan. Free")
        c.add_argument("--since", help="lastmod >= this ISO date — batched, "
                                       "see `entries`")
        c.add_argument("--limit", type=int)
        if name == "search":
            c.add_argument("--departement", action="append",
                           help="two characters, checked on the ad's postcode")
            c.add_argument("--max-read", type=int, default=120,
                           dest="max_read",
                           help="stop after reading this many ads (default "
                                "120). A department filter can otherwise walk "
                                "the whole sitemap")
            c.add_argument("--delay", type=float, default=0.6)
        c.set_defaults(func=fn)
    a = p.parse_args()
    if a.cmd == "search" and not (a.ville or a.since or a.departement
                                  or a.limit):
        die("give --ville, --since, --departement or --limit. Without one "
            "the sweep reads all 6 755 ads.")
    a.func(a)


if __name__ == "__main__":
    main()
