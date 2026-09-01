#!/usr/bin/env python3
"""Fetch French ads from adecco.com — the largest interim network here.

**13 293 ads**, read from the country sitemap the site's own `robots.txt`
declares. Not the 20 000 its home page advertises: that number is marketing,
this one is counted.

  GET /robots.txt                        → Sitemap: …/jobsindex.xml
  GET /jobsindex.xml                     → 59 country sitemaps
  GET /sitemap-jobs-france-fr.xml        → 13 293 ads + per-ad lastmod
  GET /fr-fr/offres-emploi/<slug>/<id>   → the ad, with a JSON-LD JobPosting

**The country is in the sitemap's filename**, which is the cleanest geography
this repository has met — no locale to mistake for a country, as on `wttj.md`.

**Every ad names `adecco` as the employer.** Not sometimes: on every one of the
17 measured. This is an agency board, so there is no employer to research and
no key to deduplicate against a company's own ATS — the same terms
`michaelpage.md` ships on. What it does carry is a **salary on two ads in
three** — the field is on every ad, and says nothing on a third of them.

Usage:
  adecco.py discover --since 2026-09-01
  adecco.py search --region Morbihan --pages 3
  adecco.py search --all --limit 40

Output: one JSON object per line.
"""

import argparse
import html as html_mod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://www.adecco.com"
SITEMAP = BASE + "/sitemap-jobs-france-fr.xml"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

URL_BLOCK_RE = re.compile(r"(?s)<url>(.*?)</url>")
# Reads the plain `<loc>https://…</loc>` and the CDATA-wrapped form both.
# hays.fr serves the second, where the first non-space character after the tag
# is `<` and the strict pattern `<loc>\s*([^<\s]+)` matches nothing at all —
# 0 URLs from a valid 2.37 MB sitemap. See issue #55 and `hays-fr.md`.
LOC_RE = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?\s*([^\s\]<]+)")
MOD_RE = re.compile(r"<lastmod>([^<]*)")
LD_RE = re.compile(
    r"<script[^>]*type=\"application/ld\+json\"[^>]*>(.*?)</script>",
    re.S | re.I)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def safe_url(url):
    """Percent-encode the path.

    **3 339 of the 13 293 URLs in the sitemap carry raw UTF-8** — `puy-de-dôme`,
    `côtes-darmor`, `drôme`. Requested as they stand, urllib raises an ascii
    codec error and a quarter of the board is lost. Other clients fail more
    quietly. Encoded, they answer 200.
    """
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit(
        (p.scheme, p.netloc, urllib.parse.quote(p.path, safe="/"),
         p.query, p.fragment))


def get(url, retries=2, gone_is_ok=False):
    req = urllib.request.Request(safe_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "fr-FR,fr;q=0.9",
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                waf = r.headers.get("x-amzn-waf-action")
                if waf:
                    die(f"a WAF challenged {url}: HTTP {r.status}, "
                        f"x-amzn-waf-action: {waf}. A 2xx carrying no ad.")
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if gone_is_ok and e.code in (404, 410):
                # The sitemap lists ads the site has since retired, and it
                # says so properly: **410 Gone**, not a soft 404 and not a
                # 200 with an empty page. One dead ad is not a dead board,
                # so the sweep counts it and carries on.
                return None
            die(f"adecco returned HTTP {e.code} for {url}")
        except Exception as e:  # noqa: BLE001 - network shape varies
            if attempt == retries:
                die(f"could not reach adecco: {e}")
            time.sleep(2.0)
    return ""


def entries():
    """(url, lastmod) for every French ad.

    The sitemap writes **`<lastmod>` before `<loc>`**, which is the reverse of
    the usual order and of `wttj.py`'s source. A regex written as
    `<loc>…<lastmod>` matches **nothing at all** here and yields an empty board
    with no error — so each `<url>` block is taken whole and its tags looked up
    inside it, in whatever order they come.
    """
    page = get(SITEMAP)
    blocks = URL_BLOCK_RE.findall(page)
    if not blocks:
        die(f"{SITEMAP} parsed to zero <url> blocks out of {len(page)} "
            "characters. That is a read failure, not an empty board: check "
            "the document before believing the count.")
    out = []
    for b in blocks:
        loc = LOC_RE.search(b)
        if not loc:
            continue
        mod = MOD_RE.search(b)
        out.append((loc.group(1), (mod.group(1).strip() if mod else None)))
    if not out:
        # Zero <loc> inside a non-zero number of <url> blocks is impossible in
        # a valid sitemap, so the reader is wrong rather than the board empty.
        # That arithmetic — not the pattern — is what exposed the CDATA trap
        # on hays.fr. Issue #55.
        die(f"{SITEMAP} gave zero URLs out of {len(blocks)} <url> blocks. "
            "That combination cannot occur in a valid sitemap: it is a "
            "reading fault, not an empty board. Check <loc> for a wrapper "
            "this extractor does not handle.")
    return out


def description_text(raw):
    """The ad body as readable text.

    It arrives **escaped twice**: `&#60;div class&#61;&#34;…` is `<div
    class="…` written with numeric entities, so one unescape yields HTML and
    the tags then have to come out. Passed through as it stands, a cover letter
    would be written from `&#60;strong&#62;`.
    """
    if not raw:
        return None
    txt = html_mod.unescape(raw)
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</h\d>", "\n", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html_mod.unescape(txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n{3,}", "\n\n", txt).strip()


def clean(v):
    """Trim the trailing spaces this board puts on almost every value."""
    if isinstance(v, str):
        v = v.strip()
        # The literal four-character string, not JSON null. A truthiness test
        # passes it; see the adapter doc.
        return None if v.lower() == "null" or v == "" else v
    return v


def money(v):
    """A salary figure, or None when the board wrote zero.

    `12.46 → 0 → Heure` is not a range from 12.46 to nothing; it is an hourly
    rate with no ceiling given. `0 → 0` is not a wage at all. Passing either
    through as a number invites a reader to print "12.46 to 0 €".
    """
    v = clean(v)
    if v is None:
        return None
    try:
        return None if float(str(v)) == 0 else v
    except ValueError:
        return v


def card(url, lastmod):
    page = get(url, gone_is_ok=True)
    ident = url.rstrip("/").rsplit("/", 1)[-1]
    if page is None:
        return {"id": ident, "ledger_id": f"adecco:{ident}", "url": url,
                "gone": True}
    jp = None
    for m in LD_RE.finditer(page):
        try:
            j = json.loads(m.group(1))
        except Exception:  # noqa: BLE001 - a broken block is not fatal
            continue
        for x in (j if isinstance(j, list) else [j]):
            if isinstance(x, dict) and x.get("@type") == "JobPosting":
                jp = x
    if jp is None:
        return {"id": ident, "ledger_id": f"adecco:{ident}", "url": url,
                "json_ld": False}
    addr = (jp.get("jobLocation") or {}).get("address") or {}
    sal = (jp.get("baseSalary") or {}).get("value") or {}
    return {
        "id": ident,
        "ledger_id": f"adecco:{ident}",
        "url": url,
        "job_id": clean(jp.get("jobId")),
        "title": clean(jp.get("title")),
        # Always the agency. Kept so nobody re-derives it, and flagged so
        # nobody mistakes it for the workplace.
        "company": clean((jp.get("hiringOrganization") or {}).get("name")),
        "employer_is_the_agency": True,
        "locality": clean(addr.get("addressLocality")),
        # The department, spelled out. This is the only reliable one —
        # never the URL, see the doc.
        "region": clean(addr.get("addressRegion")),
        # Present on every ad and empty on every ad.
        "postcode": clean(addr.get("postalCode")),
        "country": clean(addr.get("addressCountry")) or clean(jp.get("country")),
        # French free text — "Temps plein" — or the string "null". Never the
        # schema.org vocabulary this field is supposed to carry.
        "contract_text": clean(jp.get("employmentType")),
        "remote": clean(jp.get("isRemote")),
        # `baseSalary` is present on every ad and **means something on two
        # thirds of them**: 0–0 came back on 6 of 17, and `maxValue` is 0 on
        # every hourly ad measured. Zero is not a wage, so it is emitted as
        # absent rather than as a number a reader would put in a range.
        "salary_min": money(sal.get("minValue")),
        "salary_max": money(sal.get("maxValue")),
        # "Heure", "Annuel", or absent. Not a schema unitText either.
        "salary_unit": clean(sal.get("unitText")),
        # `currency` holds **"France "** on every ad — the country, in the
        # currency field. Emitted under a name that says what it is.
        "currency_field_holds_a_country": (jp.get("baseSalary") or {}).get(
            "currency"),
        "sector": clean(jp.get("industryTypeTitle")),
        "published": clean(jp.get("datePosted")),
        # Not a formula: 46 to 62 days across the sample, nine of seventeen at
        # 60. A real per-ad date, which is rare enough to say.
        "valid_through": clean(jp.get("validThrough")),
        "lastmod": lastmod,
        "description": description_text(jp.get("description")),
        "json_ld": True,
    }


def cmd_discover(a):
    rows = entries()
    n = 0
    for url, mod in rows:
        if a.since and (mod or "") < a.since:
            continue
        ident = url.rstrip("/").rsplit("/", 1)[-1]
        print(json.dumps({"url": url, "id": ident,
                          "ledger_id": f"adecco:{ident}", "lastmod": mod},
                         ensure_ascii=False))
        n += 1
        if a.limit and n >= a.limit:
            break
    print(f"[adecco] {n} of {len(rows)} ads in the France sitemap",
          file=sys.stderr)
    print("[adecco] these are URLs. The department in the slug is truncated "
          "and unusable — read the doc before filtering on it.",
          file=sys.stderr)


def cmd_search(a):
    rows = entries()
    print(f"[adecco] {len(rows)} ads in the France sitemap", file=sys.stderr)
    if a.since:
        rows = [r for r in rows if (r[1] or "") >= a.since]
        print(f"[adecco] {len(rows)} since {a.since}", file=sys.stderr)
    if a.ville:
        v = a.ville.strip().lower()
        before = len(rows)
        rows = [r for r in rows if v in r[0].lower()]
        print(f"[adecco] {len(rows)} of {before} match --ville {a.ville!r} "
              "in the slug, filtered before any fetch", file=sys.stderr)
    want = (a.region or "").strip().lower() or None
    kept, dropped, read, gone = 0, 0, 0, 0
    for url, mod in rows:
        if a.limit and kept >= a.limit:
            break
        if read >= a.pages * 20:
            break
        c = card(url, mod)
        read += 1
        if c.get("gone"):
            gone += 1
            time.sleep(a.delay)
            continue
        if want:
            got = (c.get("region") or "").lower()
            if got != want:
                dropped += 1
                time.sleep(a.delay)
                continue
        print(json.dumps(c, ensure_ascii=False))
        kept += 1
        time.sleep(a.delay)
    print(f"[adecco] {kept} kept, {read} ads read", file=sys.stderr)
    if gone:
        print(f"[adecco] {gone} were already gone — the sitemap lists retired "
              "ads and the site answers 410 for them, which is honest and "
              "worth saying rather than hiding", file=sys.stderr)
    if dropped:
        print(f"[adecco] {dropped} dropped by --region. The department cannot "
              "be known before reading the ad: the sitemap slug truncates it "
              "— 'seine-et-marne' becomes 'marne' — so filtering costs a "
              "fetch per ad. Narrow with --since first.", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("discover", help="ad URLs from the France sitemap")
    d.add_argument("--since", help="keep lastmod >= this ISO date")
    d.add_argument("--limit", type=int)
    d.set_defaults(func=cmd_discover)

    s = sub.add_parser("search", help="read ads, optionally by department")
    s.add_argument("--region", help="department spelled out, e.g. Morbihan — "
                   "checked on the ad, so it costs one fetch per candidate")
    s.add_argument("--ville", help="substring of the URL slug, e.g. lorient. "
                   "Free: it filters before fetching. The commune is in the "
                   "slug; the department in it is truncated and unusable")
    s.add_argument("--all", action="store_true", help="no department filter")
    s.add_argument("--since", help="keep lastmod >= this ISO date")
    s.add_argument("--pages", type=int, default=3, help="20 ads read each")
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=0.6)
    s.set_defaults(func=cmd_search)

    a = p.parse_args()
    if a.cmd == "search" and not (a.region or a.ville or a.since or a.all):
        die("give --ville, --region, --since or --all. Without one of them the "
            "sweep reads all 13 293 ads one page load at a time.")
    a.func(a)


if __name__ == "__main__":
    main()
