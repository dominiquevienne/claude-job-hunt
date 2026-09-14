#!/usr/bin/env python3
"""Caribbean Jobs Online (`www.caribbeanjobsonline.com`) — one regional board, one list per territory; `--country` names the list, «Page 1 of 4» is what the page states, and the pages after the first live in the session. Issue #449.

  caribbeanjobsonline.py list --country bahamas [--pages N | --all] [--limit N]
  caribbeanjobsonline.py ad --url <https://www.caribbeanjobsonline.com/job/<slug>-<id>.htm>
  caribbeanjobsonline.py countries

THE ROUTE IS THE LIST PAGE AND ITS OWN LOADER. `GET /jobs/<slug>` renders
the first ten cards (`div.vac-result-row`: the ad's link `/job/<slug>-<id>.htm`,
the title, «Posted by <employer>», a summary line, «Salary & Benefits»,
«Town/City», sometimes «Contract Type») and states **`page_max_count = N`
— «Page 1 of N»**; the next pages are placeholders the page fills by
`POST /include/ajax_vacResults.asp?nextID=results_page<p>` **against the
ASP session the first GET opened** (`ASPSESSIONID…`): the `?pageno=`
links are decoration — `?pageno=2` answers the first page again, measured
2026-09-14 00:4x. So a walk is one GET and N−1 POSTs on one cookie jar,
and a POST past the last page answers an empty grid (160 bytes). No key,
no browser — a cookie the site itself sets.

THE WITNESS IS A PAGE COUNT, NOT AN ITEM COUNT: the page states how many
pages, never how many jobs. The walk prints «N emitted over P page(s),
site states P page(s) — pages equal»; a walk that reads fewer pages than
stated, or a stated page that comes back empty, exits 6. A list with no
cards states no page count at all (no `page_max_count`, no pager): it is
emitted as «0 emitted, the page lists nothing and states no page count».

MEASURED 2026-09-14 00:39–00:44 UTC, the 28 territory lists the root
names, one GET each, the declared client, guard on the exact path
(`/robots.txt`: `*` refuses `/candidate/*.asp?`, `/apply/`, `/rss/`… — the
list, the loader and `/job/` are open, `certain: True`):

    twelve lists carry cards          fifteen lists carry none (no pager, no count)
    jamaica          13 pages         anguilla · belize · bonaire · bvi ·
    bahamas           4 pages         caribbean-netherlands · dominica · grenada ·
    aruba, guyana,    2 pages each    martinique · montserrat · puerto-rico · saba ·
      trinidad-tobago                 sint-maarten · st-kitts-nevis ·
    bermuda 8 · barbados 4 ·          st-vincent-grenadines · turks-caicos ·
      suriname 4 · cayman-islands 2 · virgin-islands
      haiti 2 · antigua 1 · st-lucia 1  (one page each)

Every one of the 28 answers 200 and is accepted by `--country`; the card
declares in `countries:` the twelve that listed something on the day —
an empty list is a measurement, not a coverage. The ad page's own
location filter names the territories with live vacancies («Antigua,
Aruba, Bahamas, Barbados, Bermuda, Cayman Islands, Guyana, Haiti,
Jamaica, St Lucia, Suriname, Trinidad & Tobago», plus «Cruise Ship»):
the same twelve.

THE AD PAGE: `div.jobKeyPoints` rows — Organisation, Reference, Contract
Type, Industries, Location, Salary & Benefits, Date Posted (dd/mm/yyyy),
Expiry Date — then `vacDetails-job-summary` and `vacDetails-job-details`.
The apply and print routes (`/candidate/externalApply.asp`,
`printPreview.asp`) are refused by the rules and never touched.

WHAT IS WITHHELD. Addresses and phone numbers in the prose are replaced
(`[e-mail withheld]`, `[phone withheld]`, nine digits or more). Salary is
the site's text, never parsed.
"""

import argparse
import html
import http.cookiejar
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "www.caribbeanjobsonline.com"
BASE = f"https://{HOST}"
LOADER = f"{BASE}/include/ajax_vacResults.asp?nextID=results_page"
# slug -> ISO 3166-1 alpha-2; every slug is a list the root names and that answered 200 on 2026-09-14
COUNTRIES = {
    "anguilla": "AI", "antigua": "AG", "aruba": "AW", "bahamas": "BS", "barbados": "BB", "belize": "BZ", "bermuda": "BM",
    "bonaire": "BQ", "bvi": "VG", "caribbean-netherlands": "BQ", "cayman-islands": "KY", "dominica": "DM", "grenada": "GD",
    "guyana": "GY", "haiti": "HT", "jamaica": "JM", "martinique": "MQ", "montserrat": "MS", "puerto-rico": "PR", "saba": "BQ",
    "sint-maarten": "SX", "st-kitts-nevis": "KN", "st-lucia": "LC", "st-vincent-grenadines": "VC", "suriname": "SR",
    "trinidad-tobago": "TT", "turks-caicos": "TC", "virgin-islands": "VI",
}
PAGE_SIZE = 10
DEFAULT_PAGES = 10
AD_RE = re.compile(r"^https?://www\.caribbeanjobsonline\.com/job/[^/?#]*-(\d+)\.htm$")
PAGES_RE = re.compile(r"page_max_count\s*=\s*(\d+);")
CARD_RE = re.compile(r'<div class="row cursor vac-result-row[^"]*"[^>]*title="([^"]*)">(.*?)View Details', re.S)   # the last card of a grid has no closing comment
LINK_RE = re.compile(r'href="(https://www\.caribbeanjobsonline\.com/job/[^"]+-(\d+)\.htm)"')
TITLE_RE = re.compile(r'<div class="col-md-12 jobtitle">\s*<b>(.*?)</b>', re.S)
EMP_RE = re.compile(r'Posted by\s*<a[^>]*>(.*?)</a>', re.S)
SUM_RE = re.compile(r'<div class="row marginTop10">\s*<div class="col-md-12">(.*?)</div>', re.S)
BAR_RE = re.compile(r'<b>([^<]+?):</b>\s*([^<]*)')
KEY_RE = re.compile(r'<div class="col-md-3 col-xs-12"><b>(.*?)</b></div>\s*<div class="col-md-9 col-xs-12 vacDetails-detailData">(.*?)</div>', re.S)
SUMMARY_RE = re.compile(r'<div class="[^"]*vacDetails-job-summary">(.*?)</div>', re.S)
DETAILS_RE = re.compile(r'<div class="[^"]*vacDetails-job-details">(.*?)</div>\s*</div>', re.S)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\d[\d\s().-]{6,}\d(?!\w)")
KEYS = {"organisation": "employer", "reference": "reference", "contract type": "contract", "industries": "industry", "location": "location",
        "salary & benefits": "salary_text", "date posted": "posted", "expiry date": "valid_through"}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACE = Pace(HOST, own=4.0)
_JAR = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_JAR))


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[caribbeanjobsonline] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, post=False):
    """One request on the process's cookie jar — the loader reads the session the list opened. `(code, body)`."""
    gate(url)
    _PACE.wait()
    headers = {"User-Agent": UA, "Accept": "text/html"}
    if post:
        headers["X-Requested-With"] = "XMLHttpRequest"
    req = urllib.request.Request(wire_url(url), data=b"" if post else None, headers=headers)
    try:
        with _OPENER.open(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def clean(s):
    s = re.sub(r"<(script|style)\b.*?</\1>", "", s or "", flags=re.S | re.I)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<br\s*/?>|</p>|</li>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def redact(s):
    s = EMAIL_RE.sub("[e-mail withheld]", s or "")
    return PHONE_RE.sub(lambda m: "[phone withheld]" if sum(c.isdigit() for c in m.group(0)) >= 9 else m.group(0), s)


def iso(d):
    m = re.match(r"\s*(\d{2})/(\d{2})/(\d{4})\s*$", d or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else (clean(d) or None)


def stated_pages(body):
    m = PAGES_RE.search(body or "")
    return int(m.group(1)) if m else None


def cards(body, slug, country):
    out = []
    for row_title, blk in CARD_RE.findall(body or ""):
        link = LINK_RE.search(blk)
        if not link:
            continue
        url, ident = link.groups()
        t = TITLE_RE.search(blk)
        emp = EMP_RE.search(blk)
        sm = SUM_RE.search(blk)
        bar = {k.strip().lower(): clean(v) for k, v in BAR_RE.findall(re.sub(r"<!--.*?-->", "", blk, flags=re.S))}
        out.append({
            "source": "caribbeanjobsonline", "country": country, "territory": slug, "ledger_id": f"caribbeanjobsonline:{ident}", "id": ident, "url": url,
            "title": redact(clean(row_title) or clean(t.group(1)) if t else clean(row_title)) or None,
            "employer": redact(clean(emp.group(1))) or None if emp else None,
            "location": redact(bar.get("town/city", "")) or None, "contract": bar.get("contract type") or None,
            "salary_text": redact(bar.get("salary & benefits", "")) or None,
            "summary": redact(clean(sm.group(1))) or None if sm else None,
        })
    return out


def cmd_countries(a):
    for s, c in COUNTRIES.items():
        print(f"{s}\t{c}\t{BASE}/jobs/{s}")


def cmd_list(a):
    slug = a.country.strip().lower()
    if slug not in COUNTRIES:
        die(f"{a.country}: not a list the root names — `countries` lists the {len(COUNTRIES)} read on 2026-09-14; a new one is measured, not assumed.")
    country = COUNTRIES[slug]
    if a.pages is not None and a.pages < 1:
        die("--pages must be at least 1 (or use --all).")
    limit_pages = None if a.all else (a.pages or DEFAULT_PAGES)
    seen, emitted, page = set(), 0, 0
    url = f"{BASE}/jobs/{slug}"
    code, body = request(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    if not re.search(r'title="Jobs in ', body) and "vac_res_grid" not in body and "results_page1" not in body:
        die(f"{url}: not the list page this file reads ({len(body)} characters).", EXIT_PARTIAL)
    site = stated_pages(body)
    rows = cards(body, slug, country)
    if site is None:
        if rows:
            die(f"{url}: {len(rows)} card(s) and no `page_max_count` — the page changed shape.", EXIT_PARTIAL)
        note(f"0 emitted, the page lists nothing and states no page count ({slug}, {country}) — a measurement, not a refusal.")
        return
    while True:
        page += 1
        if page > 1:
            code, body = request(f"{LOADER}{page}", post=True)
            if code != 200:
                die(f"{LOADER}{page}: HTTP {code}", EXIT_PARTIAL)
            rows = cards(body, slug, country)
            if not rows:
                note(f"{th(emitted)} emitted over {page - 1} page(s), site states {th(site)} page(s) ({slug}, {country}) — page {page} came back empty, {th(site - page + 1)} page(s) short.")
                sys.exit(EXIT_PARTIAL)
        new = 0
        for r in rows:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            print(json.dumps(r, ensure_ascii=False))
            emitted += 1
            new += 1
            if a.limit and emitted >= a.limit:
                break
        if a.limit and emitted >= a.limit:
            note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} page(s) ({slug}, {country}) — walk bounded by request (--limit), not compared.")
            return
        if page >= site:
            break
        if limit_pages is not None and page >= limit_pages:
            note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} page(s) ({slug}, {country}) — walk bounded by request (--pages {limit_pages}; --all walks to the stated pages), not compared.")
            return
    note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} page(s) ({slug}, {country}) — pages equal.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an ad URL of this board (https://www.caribbeanjobsonline.com/job/<slug>-<id>.htm).")
    ident = m.group(1)
    code, body = request(a.url.strip())
    if code == 404:
        die(f"{a.url}: HTTP 404 — the ad is gone.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_PARTIAL)
    keys = {clean(k).lower(): clean(v) for k, v in KEY_RE.findall(body)}
    if not keys:
        die(f"{a.url}: no `jobKeyPoints` rows on the page — gone, or not the template this file reads.", EXIT_GONE)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    r = {"source": "caribbeanjobsonline", "ledger_id": f"caribbeanjobsonline:{ident}", "id": ident, "url": a.url.strip(),
         "title": redact(clean(h1.group(1))) or None if h1 else None}
    for label, key in KEYS.items():
        v = keys.get(label)
        if key in ("posted", "valid_through"):
            r[key] = iso(v) if v else None
        else:
            r[key] = redact(v) or None if v else None
    sm, dt = SUMMARY_RE.search(body), DETAILS_RE.search(body)
    r["summary"] = redact(clean(sm.group(1))) or None if sm else None
    r["description"] = redact(clean(dt.group(1))) or None if dt else None
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="walk one territory's list")
    l.add_argument("--country", required=True, help="the list's slug, e.g. bahamas — see `countries`")
    g = l.add_mutually_exclusive_group()
    g.add_argument("--pages", type=int, default=None, help=f"pages to read (default {DEFAULT_PAGES}, bounded and said so)")
    g.add_argument("--all", action="store_true", help="walk to the page count the site states, and compare")
    l.add_argument("--limit", type=int, default=0, help="stop after N rows (bounded, not compared)")
    l.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one ad by its public URL")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    c = sub.add_parser("countries", help="the 28 lists the root names, and their ISO code")
    c.set_defaults(fn=cmd_countries)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
