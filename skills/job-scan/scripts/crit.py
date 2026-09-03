#!/usr/bin/env python3
"""Fetch French ads from crit-job.com — the largest interim board here.

**16 175 ads**, from the offers sitemap the site's `robots.txt` declares —
more than `adecco.md` (13 293) and more than twice `randstad-fr.md` (6 755).

It has the best salary data of any French board in this repository: a **minimum
and a maximum, in euros, on every ad measured** — where Adecco and Randstad
both write a minimum and leave the maximum at zero on hourly work.

  GET /robots.txt              → Sitemap: …/offres/sitemap.xml
  GET /offres/sitemap.xml      → 16 175 ads, each with a real lastmod
  GET /offres/<uuid>           → the ad, JSON-LD JobPosting

**`lastmod` is genuinely per ad**: 13 893 distinct values across 16 175 — the
best ratio in the repository, ahead of `wttj.md`'s 7 691 in 10 000. That
matters more here than anywhere else, because **the URL is a UUID**: there is
no town and no department in it, so `--since` is the only narrowing that costs
nothing. See `sweep`.

Usage:
  crit.py discover --since 2026-08-25
  crit.py search --departement 30 --max-read 200
  crit.py search --since 2026-08-30 --limit 40

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
import urllib.error
import urllib.parse
import urllib.request

from _robots import allowed as robots_allowed

BASE = "https://www.crit-job.com"
SITEMAP = BASE + "/offres/sitemap.xml"
from _ua import UA
URL_BLOCK_RE = re.compile(r"(?s)<url>(.*?)</url>")
# Reads the plain `<loc>https://…</loc>` and the CDATA-wrapped form both.
# hays.fr serves the second, where the first non-space character after the tag
# is `<` and the strict pattern `<loc>\s*([^<\s]+)` matches nothing at all —
# 0 URLs from a valid 2.37 MB sitemap. See issue #55 and `hays-fr.md`.
LOC_RE = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?\s*([^\s\]<]+)")
MOD_RE = re.compile(r"<lastmod>([^<]*)")
AD_RE = re.compile(r"/offres/([0-9a-f]{8}-[0-9a-f-]{27})")
DEPT_RE = re.compile(r"^(?:\d{2}|2[AB])$")
# `<h2 …>Profil recherché</h2><p …>…</p>`. The classes on both are Emotion
# build hashes — `css-aocjcp`, `css-1nm1tyc` — which change on every deploy,
# so the heading's **text** is the anchor. Same lesson as the Vue `data-v-*`
# attributes on figaro-emploi.md.
SECTION_RE = re.compile(
    r"<h2[^>]*>\s*Profil recherch\w*\s*</h2>\s*<p[^>]*>(.*?)</p>",
    re.S | re.I)


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
        print(f"[crit] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts. A platform that has "
              f"been renamed reaches an adapter this way before it reaches it "
              f"as a rename.", file=__import__("sys").stderr)
    return a



def get(url, gone_is_ok=False, retries=2):
    _robots_gate(url, 'crit')
    req = urllib.request.Request(url, headers={
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
                return None
            die(f"crit-job returned HTTP {e.code} for {url}")
        except Exception as e:  # noqa: BLE001 - network shape varies
            if attempt == retries:
                die(f"could not reach crit-job: {e}")
            time.sleep(2.0)
    return ""


def entries():
    page = get(SITEMAP)
    blocks = URL_BLOCK_RE.findall(page)
    if not blocks:
        die(f"{SITEMAP} parsed to zero <url> blocks out of {len(page)} "
            "characters. A read failure, not an empty board.")
    out, locs = [], 0
    for b in blocks:
        loc = LOC_RE.search(b)
        if loc:
            locs += 1
        if not loc or not AD_RE.search(loc.group(1)):
            # The first entry is the listing page itself, not an ad.
            continue
        mod = MOD_RE.search(b)
        out.append((loc.group(1), mod.group(1).strip() if mod else None))
    if not locs:
        # Counted on <loc> read, not on ads kept: this board legitimately
        # drops a non-ad entry, and the invariant must not be confused by it.
        # Zero <loc> in N <url> blocks is impossible in a valid sitemap.
        # Issue #55.
        die(f"{SITEMAP} gave zero URLs out of {len(blocks)} <url> blocks. "
            "That combination cannot occur in a valid sitemap: it is a "
            "reading fault, not an empty board.")
    return out


def text_of(raw):
    if not raw:
        return None
    t = html_mod.unescape(raw)
    t = re.sub(r"(?i)<br\s*/?>|</p>|</li>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html_mod.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip() or None


def card(url, lastmod):
    page = get(url, gone_is_ok=True)
    m = AD_RE.search(url)
    ident = m.group(1) if m else url.rsplit("/", 1)[-1]
    if page is None:
        return {"id": ident, "ledger_id": f"crit:{ident}", "url": url,
                "gone": True}
    # One reader for every board's ld+json: tolerant of the quote style
    # on the script tag, and strict=False on the parse. Issue #76.
    jp = (postings(page) or [None])[-1]
    if jp is None:
        if "JobPosting" in page:
            die(f"{url} contains 'JobPosting' but no ld+json block parsed — "
                "the markup changed. Do not trust any count from this run.")
        return {"id": ident, "ledger_id": f"crit:{ident}", "url": url,
                "json_ld": False}
    addr = one(jp.get("jobLocation")).get("address") or {}
    sal = one(jp.get("baseSalary")).get("value") or {}
    ids = jp.get("identifier") or []
    if isinstance(ids, dict):
        ids = [ids]
    ref = next((i.get("value") for i in ids
                if str(i.get("name", "")).lower() == "reference"), None)
    # The profile block lives **outside** the JSON-LD: the structured
    # description covers "Description du poste" only, and "Profil recherché"
    # is a sibling section worth roughly as many characters again.
    prof = SECTION_RE.search(page)
    return {
        "id": ident,
        "ledger_id": f"crit:{ident}",
        "url": url,
        "reference": ref,
        "title": jp.get("title"),
        # The **local branch** — CRIT LUNEL, CRIT CHAUMONT — not just "Crit",
        # which says roughly where the assignment is run from. Still the
        # agency: the client is described and never named.
        "company": one(jp.get("hiringOrganization")).get("name"),
        "employer_is_the_agency": True,
        "locality": addr.get("addressLocality"),
        "postcode": addr.get("postalCode"),
        # **The country's name, not its ISO code** — "France", where every
        # other board here writes "FR". Matching on `== "FR"` finds nothing.
        "country_name": addr.get("addressCountry"),
        # `OTHER` on 14 of 20 — a valid schema value carrying no information.
        # Do not filter on it.
        "employment_type": jp.get("employmentType"),
        "occupational_category": jp.get("occupationalCategory"),
        "starts": jp.get("jobStartDate"),
        "salary_min": sal.get("minValue"),
        "salary_max": sal.get("maxValue"),
        "salary_unit": sal.get("unitText"),
        "salary_currency": one(jp.get("baseSalary")).get("currency"),
        "published": jp.get("datePosted"),
        # Absent on every ad, which is the honest answer.
        "valid_through": jp.get("validThrough"),
        "lastmod": lastmod,
        "description": text_of(jp.get("description")),
        "profile": text_of(prof.group(1)) if prof else None,
        "json_ld": True,
    }


def sweep(a, details):
    rows = entries()
    print(f"[crit] {len(rows)} ads in the sitemap", file=sys.stderr)
    if a.since:
        before = len(rows)
        rows = [r for r in rows if (r[1] or "") >= a.since]
        print(f"[crit] {len(rows)} of {before} since {a.since} — the only "
              "free narrowing here, because the URL is a UUID and carries no "
              "town", file=sys.stderr)
    depts = set(getattr(a, "departement", None) or [])
    for d in depts:
        if not DEPT_RE.match(d):
            die(f"{d!r} is not a two-character department code.")
    kept, read, dropped, gone = 0, 0, 0, 0
    for url, mod in rows:
        if a.limit and kept >= a.limit:
            break
        if details and read >= a.max_read:
            print(f"[crit] stopped after reading {read} ads — the cap. A "
                  "--departement filter has to read each ad, because the "
                  "postcode is not in the URL. Narrow with --since, or raise "
                  "--max-read.", file=sys.stderr)
            break
        if not details:
            print(json.dumps({"url": url, "id": AD_RE.search(url).group(1),
                              "ledger_id": f"crit:{AD_RE.search(url).group(1)}",
                              "lastmod": mod}, ensure_ascii=False))
            kept += 1
            continue
        c = card(url, mod)
        read += 1
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
    print(f"[crit] {kept} ads returned" + (f", {read} read" if details else ""),
          file=sys.stderr)
    if dropped:
        print(f"[crit] {dropped} dropped by --departement", file=sys.stderr)
    if gone:
        print(f"[crit] {gone} were already gone", file=sys.stderr)


def cmd_discover(a):
    sweep(a, details=False)


def cmd_search(a):
    sweep(a, details=True)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("discover", help="ad URLs and their dates")
    d.add_argument("--since", help="lastmod >= this ISO date. Real per ad")
    d.add_argument("--limit", type=int)
    d.set_defaults(func=cmd_discover)

    s = sub.add_parser("search", help="read the ads")
    s.add_argument("--since", help="lastmod >= this ISO date. Real per ad")
    s.add_argument("--departement", action="append",
                   help="two characters, checked on the ad's postcode")
    s.add_argument("--limit", type=int)
    s.add_argument("--max-read", type=int, default=150, dest="max_read",
                   help="stop after reading this many ads (default 150)")
    s.add_argument("--delay", type=float, default=0.5)
    s.set_defaults(func=cmd_search)

    a = p.parse_args()
    if a.cmd == "search" and not (a.since or a.departement or a.limit):
        die("give --since, --departement or --limit. Without one the sweep "
            "reads all 16 175 ads.")
    a.func(a)


if __name__ == "__main__":
    main()
