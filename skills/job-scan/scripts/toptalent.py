#!/usr/bin/env python3
"""Toptalent (`toptalent.co`, Türkiye — the graduates' board): the list's own loader, nine a page until an empty page, against the site's sitemap as the count it states; the ad page's fields, its e-mail withheld. Issue #388.

  toptalent.py list [--q TEXT] [--pages N | --all] [--limit N]
  toptalent.py sitemap
  toptalent.py ad --url <https://toptalent.co/<slug>-<id>>

THE ROUTE IS THE LIST'S OWN LOADER. `/is-ilanlari` renders the first nine
cards and scrolls the rest in through `POST /Job/SearchJob` — a JSON body
`{PageSize: 9, PageNumber: p, IsCardView: false, SearchKey, DepartmentIds,
CityIds, PositionLevelIds, OrderBy: "newests", FilterTags, DepartmentSeo,
CitySeo}` answering an HTML fragment of `a.position` cards (the ad's link
`/<slug>-<id>`, the title, the employer, the place, a «Son N Gün» badge).
Measured 2026-09-14 03:0x UTC: **page 1 answers nine cards, page 2 six
bytes** — a `PageSize` of 50 or 100 answers the same nine; a
`DepartmentSeo` the page does not name answers 500. The site states no
count in words: **its figure is its sitemap** (`/sitemap.xml`, 3 145
URLs, of which nine are ad pages `…-<id>`, the id six digits — a slug ending in a year is an article), read before every walk and
printed beside the emitted count — «9 emitted over 1 page(s), sitemap
lists 9 — equal». A small board on the day; the walk runs until the
loader answers an empty page, and compares.

THE AD PAGE (`/<slug>-<id>`): the title and the employer in the header
card, «Departman» and «Lokasyon» paragraphs, «Kimler Başvurabilir?» (who
may apply — the year of study, as buttons), a «Son N Gün» badge, and the
body in `div.job-content`. Its JSON-LD `JobPosting` is malformed (raw
control characters) and is not read. Descriptions end with the
recruiter's address — withheld.

THE RULES. `/robots.txt` (594 B): `*` refuses `/App_Data/`, `/Areas/`,
`/Account/`, `*/feed/`, the business-school routes, one named ad; the
list, the loader (`/Job/SearchJob`), the ad pages and the sitemap are
open, `certain: True`. 3 s own spacing.

WHAT IS WITHHELD. Addresses and phone numbers in the prose are replaced
(`[e-mail withheld]`, `[phone withheld]` — ten digits or more, Turkish
numbers are ten). The apply button needs an account and is never pressed.
"""

import argparse
import html
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

HOST = "toptalent.co"
BASE = f"https://{HOST}"
LOADER = f"{BASE}/Job/SearchJob"
SITEMAP = f"{BASE}/sitemap.xml"
PAGE_SIZE = 9
DEFAULT_PAGES = 10
AD_RE = re.compile(r"^https?://(?:www\.)?toptalent\.co/([a-z0-9-]+-(\d{5,8}))/?$")   # ad ids are six digits; a year («…-2023») is an article
CARD_RE = re.compile(r'<a href="/([a-z0-9-]+-(\d{5,8}))" class="position">(.*?)</a>\s*(?=<div class="row">|<a href="/[a-z0-9-]+-\d{5,8}" class="position"|\s*$)', re.S)   # a «build your CV» banner sits between two cards
TITLE_RE = re.compile(r'<h5 class="card-title[^"]*">(.*?)</h5>', re.S)
TEXT_RE = re.compile(r'<p class="card-text">(.*?)</p>', re.S)
BADGE_RE = re.compile(r"badge-circle-[a-z]+'>\s*(.*?)\s*</span>", re.S)
SM_RE = re.compile(r"<loc>\s*(https://toptalent\.co/[a-z0-9-]+-(\d{5,8}))\s*</loc>")   # «…-2023» is an article, not an ad
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().-]{7,}\d(?!\w)")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACE = Pace(HOST, own=3.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[toptalent] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, payload=None):
    """One GET, or a JSON POST to the list's loader — gated on the exact path, paced. `(code, body)`."""
    gate(url)
    _PACE.wait()
    headers = {"User-Agent": UA, "Accept": "text/html,application/xml"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()
    req = urllib.request.Request(wire_url(url), data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def clean(s):
    s = re.sub(r"<(script|style|svg)\b.*?</\1>", "", s or "", flags=re.S | re.I)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<br\s*/?>|</p>|</li>|</div>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(html.unescape(s)).replace("\xa0", " ")   # the site double-encodes («&amp;ouml;»)
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def redact(s):
    s = EMAIL_RE.sub("[e-mail withheld]", s or "")
    return PHONE_RE.sub(lambda m: "[phone withheld]" if sum(c.isdigit() for c in m.group(0)) >= 10 else m.group(0), s)


def payload(page, q=""):
    return {"PageSize": PAGE_SIZE, "PageNumber": page, "IsCardView": False, "SearchKey": q or "", "DepartmentIds": [], "CityIds": [],
            "PositionLevelIds": [], "OrderBy": "newests", "FilterTags": [], "DepartmentSeo": "", "CitySeo": ""}


def cards(body):
    out = []
    for slug, ident, blk in CARD_RE.findall(body or ""):
        t, x = TITLE_RE.search(blk), TEXT_RE.search(blk)
        lines = [l.strip() for l in clean(x.group(1)).split("\n") if l.strip()] if x else []
        badge = BADGE_RE.search(blk)
        out.append({
            "source": "toptalent", "country": "TR", "ledger_id": f"toptalent:{ident}", "id": ident, "url": f"{BASE}/{slug}",
            "title": redact(clean(t.group(1))) or None if t else None,
            "employer": redact(lines[0]) or None if lines else None, "location": lines[1] or None if len(lines) > 1 else None,
            "badge": clean(badge.group(1)) or None if badge else None,
        })
    return out


def sitemap_ids():
    code, body = request(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_PARTIAL)
    rows = [{"source": "toptalent", "country": "TR", "ledger_id": f"toptalent:{i}", "id": i, "url": u} for u, i in SM_RE.findall(body)]
    if not rows and "<loc>" not in body:
        die(f"{SITEMAP}: not a sitemap ({len(body)} characters).", EXIT_PARTIAL)
    return rows


def cmd_list(a):
    if a.pages is not None and a.pages < 1:
        die("--pages must be at least 1 (or use --all).")
    limit_pages = None if a.all else (a.pages or DEFAULT_PAGES)
    site = len({r["id"] for r in sitemap_ids()})
    seen, emitted, page = set(), 0, 0
    while True:
        page += 1
        code, body = request(LOADER, payload(page, a.q))
        if code != 200:
            die(f"{LOADER} page {page}: HTTP {code}", EXIT_PARTIAL)
        rows = cards(body)
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
        label = f"q={a.q!r}" if a.q else "all"
        if a.limit and emitted >= a.limit:
            note(f"{emitted} emitted over {page} page(s), sitemap lists {site} ({label}) — walk bounded by request (--limit), not compared.")
            return
        if not rows or new == 0:
            page -= 1   # the empty page is the end, not a page read
            break
        if limit_pages is not None and page >= limit_pages:
            note(f"{emitted} emitted over {page} page(s), sitemap lists {site} ({label}) — walk bounded by request (--pages {limit_pages}; --all walks to the empty page), not compared.")
            return
    if a.q:
        note(f"{emitted} emitted over {page} page(s) for {label} — a search, not compared to the sitemap's {site}.")
        return
    if emitted == site:
        note(f"{emitted} emitted over {page} page(s), sitemap lists {site} — equal.")
    else:
        note(f"{emitted} emitted over {page} page(s), sitemap lists {site} — {abs(site - emitted)} {'short' if emitted < site else 'over'}.")
        sys.exit(EXIT_PARTIAL)


def cmd_sitemap(a):
    rows = sitemap_ids()
    seen = set()
    for r in rows:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        print(json.dumps(r, ensure_ascii=False))
    note(f"{len(seen)} ad URL(s) in the sitemap ({len(rows)} entries).")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an ad URL of this board (https://toptalent.co/<slug>-<id>).")
    slug, ident = m.groups()
    code, body = request(a.url.strip())
    if code == 404:
        die(f"{a.url}: HTTP 404 — the ad is gone.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_PARTIAL)
    content = re.search(r'<div class="col-12 job-content">(.*?)</div>\s*</div>\s*</div>', body, re.S)
    if not content:
        die(f"{a.url}: no `job-content` on the page — gone, or not the template this file reads.", EXIT_GONE)
    t = re.search(r"<title>\s*Toptalent\.co \| (.*?)\s*-\s*([^<-]+?)\s*</title>", body, re.S)
    dept = re.search(r"<h5[^>]*>\s*Departman\s*</h5>\s*<p>(.*?)</p>", body, re.S)
    loc = re.search(r"<h5[^>]*>\s*Lokasyon\s*</h5>\s*<p>(.*?)</p>", body, re.S)
    who = re.findall(r'<h5[^>]*>\s*Kimler Başvurabilir\?\s*</h5>(.*?)</div>', body, re.S)
    who_v = re.findall(r'value="([^"]+)"', who[0]) if who else []
    badge = re.search(r"badge-circle-[a-z]+[^>]*>\s*(Son \d+ Gün)\s*<", body)
    r = {"source": "toptalent", "country": "TR", "ledger_id": f"toptalent:{ident}", "id": ident, "url": a.url.strip(),
         "title": redact(clean(t.group(1))) or None if t else None, "employer": redact(clean(t.group(2))) or None if t else None,
         "department": clean(dept.group(1)).lstrip("• ").strip() or None if dept else None,
         "location": clean(loc.group(1)) or None if loc else None,
         "who_may_apply": [html.unescape(v) for v in who_v] or None,
         "badge": badge.group(1) if badge else None,
         "description": redact(clean(content.group(1))) or None}
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="walk the list's loader nine a page until it answers nothing")
    l.add_argument("--q", default="", help="free text (SearchKey)")
    g = l.add_mutually_exclusive_group()
    g.add_argument("--pages", type=int, default=None, help=f"pages to read (default {DEFAULT_PAGES}, bounded and said so)")
    g.add_argument("--all", action="store_true", help="walk to the empty page, and compare to the sitemap")
    l.add_argument("--limit", type=int, default=0)
    l.set_defaults(fn=cmd_list)
    s = sub.add_parser("sitemap", help="the ad URLs the site's sitemap lists")
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one ad by its public URL")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
