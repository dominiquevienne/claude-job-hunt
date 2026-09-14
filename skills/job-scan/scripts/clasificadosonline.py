#!/usr/bin/env python3
"""Clasificados Online, section Empleos (`www.clasificadosonline.com`, Puerto Rico) — an ASP classifieds list of 30 a page; two numbers of the site's own printed beside every walk: the section's «3,581 Oportunidades de Empleos» and the list's «1 al 30 de 3000». Issue #442.

  clasificadosonline.py list [--pages N | --all] [--limit N] [--cat N] [--town NAME] [--q TEXT]
  clasificadosonline.py ad --url <https://www.clasificadosonline.com/Empleos/Detail.asp?JobId=N>

THE ROUTE IS THE LISTING, 30 A PAGE. `/Empleos/Listing.asp?JobsCat=%&subcat=%&Pueblo=&txkey=&Submit=ENCUENTRA+EMPLEO&offset=<0,30,60…>`
— each page ~0.9 MB of classic ASP tables — carries thirty rows, each as a
schema.org `JobPosting` microdata block (title, address, an
`itemprop="datePosted"` that is in fact the ad's expiry — see below,
hiringOrganization) followed by the `record-row` (the ad's link
`Detail.asp?JobId=<id>`, the title, the employer, the category in two
languages, the town, the salary as text «$10.5 / hr», the schedule «Full
Time»). The page states **«1 al 30 de 3000 empleos en Puerto Rico»**; the
section page `/empleos/` states **«3,581 Oportunidades de Empleos Puerto
Rico»** (2026-09-14 01:2x UTC; 3,520 the day before). Both are the site's
own; both are printed; **the walk is compared to the list's «de N»**, the
number the pager serves, and the section's figure is printed beside it —
when the two differ the difference is named, never resolved by this file.

THE RULES. `robots.txt` (292 bytes): `*` refuses only `/tomtom-sdk/`;
`anthropic-ai`, `Claude-Web`, `CCbot`, `GPTBot`… are refused `/` — none
of them is a token this project sends (`ClaudeBot`, `Claude-User`): a name
that looks like ours is not a name we send. Open, `certain: True`; 3 s
own spacing.

THE AD PAGE (`Detail.asp?JobId=`) carries microdata — title, datePosted,
validThrough, hiringOrganization, employmentType, workHours,
salaryCurrency, a description — and the prose. Measured 2026-09-14 on one
ad: the list row's `datePosted` meta equals the ad's `validThrough`
(9/20/2026 8:47:10 PM), the ad's `datePosted` is 9/13 — so the list's
meta is emitted as `valid_through`, never as `posted`. Dates are US
`m/d/yyyy h:mm:ss AM/PM`, emitted ISO.

WHAT IS WITHHELD. A classifieds carries phone numbers in the prose:
addresses and phone numbers are replaced (`[e-mail withheld]`, `[phone
withheld]` — seven digits or more, the island's numbers are ten). Salary
is the site's text, never parsed («$10.5 / hr», «Desde $10.50 Hasta
$10.50 hr»).
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

HOST = "www.clasificadosonline.com"
BASE = f"https://{HOST}"
SECTION = f"{BASE}/empleos/"
PAGE_SIZE = 30
DEFAULT_PAGES = 10
AD_RE = re.compile(r"^https?://www\.clasificadosonline\.com/Empleos/Detail\.asp\?JobId=(\d+)$", re.I)
ROW2_RE = re.compile(r'<div itemscope="" itemtype="https://schema\.org/JobPosting">(.*?)<table class="record-row[^"]*">(.*?)</table>', re.S)
META_RE = re.compile(r'<meta itemprop="(\w+)" content="([^"]*)"')
LINK_RE = re.compile(r'<a href="Detail\.asp\?JobId=(\d+)" class="recordRowTitle">(.*?)</a>', re.S)
EMP_RE = re.compile(r'<a href="/PartnersListingJobsID\.asp\?ID=\d+" class="[^"]*recordRowText">(.*?)</a>', re.S)
CAT_RE = re.compile(r'class=" espLine  recordRowText ">(.*?)</a>', re.S)
TOWN_RE = re.compile(r'Pueblo=[^"]*"\s*>(.*?)</a>', re.S)
SAL_RE = re.compile(r'<span class="recordRowShadowBold">(.*?)</span>\s*(.*?)<br>', re.S)
LIST_RE = re.compile(r'(\d[\d,]*)\s+al\s+(\d[\d,]*)\s+de\s+(\d[\d,]*)\s+empleos')
SECTION_RE = re.compile(r'([\d,]+)&nbsp;Oportunidades de Empleos')
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$])\+?\(?\d[\d\s().-]{5,}\d(?!\w)")
DATE_RE = re.compile(r"\s*(\d{1,2})/(\d{1,2})/(\d{4})(?:\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([AP]M))?\s*$")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACE = Pace(HOST, own=3.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[clasificadosonline] {msg}", file=sys.stderr)


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


def request(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def clean(s):
    s = re.sub(r"<(script|style)\b.*?</\1>", "", s or "", flags=re.S | re.I)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def redact(s):
    s = EMAIL_RE.sub("[e-mail withheld]", s or "")
    return PHONE_RE.sub(lambda m: "[phone withheld]" if sum(c.isdigit() for c in m.group(0)) >= 7 else m.group(0), s)


def num(s):
    return int(re.sub(r"[^\d]", "", s or "") or 0)


def iso(us):
    """«9/20/2026 8:47:10 PM» → «2026-09-20T20:47:10»; a bare date → «2026-09-20»; anything else as text."""
    m = DATE_RE.match(us or "")
    if not m:
        return clean(us) or None
    mo, d, y, h, mi, sec, ap = m.groups()
    out = f"{y}-{int(mo):02d}-{int(d):02d}"
    if h:
        hh = int(h) % 12 + (12 if ap == "PM" else 0)
        out += f"T{hh:02d}:{mi}:{sec or '00'}"
    return out


def stated_list(body):
    m = LIST_RE.search(body or "")
    return (num(m.group(1)), num(m.group(2)), num(m.group(3))) if m else None


def stated_section(body):
    m = SECTION_RE.search(body or "")
    return num(m.group(1)) if m else None


def rows(body):
    out = []
    for meta, rec in ROW2_RE.findall(body or ""):
        m = dict(META_RE.findall(meta))
        link = LINK_RE.search(rec)
        if not link:
            continue
        ident, title = link.groups()
        emp, cat, town, sal = EMP_RE.search(rec), CAT_RE.search(rec), TOWN_RE.search(rec), SAL_RE.search(rec)
        out.append({
            "source": "clasificadosonline", "country": "PR", "ledger_id": f"clasificadosonline:{ident}", "id": ident,
            "url": f"{BASE}/Empleos/Detail.asp?JobId={ident}",
            "title": redact(clean(title)) or None, "employer": redact(clean(emp.group(1))) or None if emp else redact(clean((m.get("hiringOrganization") or "").split(",")[0])) or None,
            "category": clean(cat.group(1)) or None if cat else None, "location": clean(town.group(1)) or None if town else None,
            "salary_text": redact(re.sub(r"\s+", " ", clean(sal.group(1)))) or None if sal else None, "schedule": re.sub(r"\s+", " ", clean(sal.group(2))) or None if sal else None,
            "valid_through": iso(m.get("datePosted")) if m.get("datePosted") else None,   # the list's `datePosted` meta is the ad's expiry — measured on the ad page
        })
    return out


def cmd_list(a):
    if a.pages is not None and a.pages < 1:
        die("--pages must be at least 1 (or use --all).")
    limit_pages = None if a.all else (a.pages or DEFAULT_PAGES)
    q = {"JobsCat": a.cat or "%", "subcat": "%", "Pueblo": a.town or "", "txkey": a.q or "", "Submit": "ENCUENTRA EMPLEO"}
    code, body = request(SECTION)
    section = stated_section(body) if code == 200 else None
    seen, emitted, page, site = set(), 0, 0, None
    while True:
        url = f"{BASE}/Empleos/Listing.asp?" + urllib.parse.urlencode({**q, "offset": page * PAGE_SIZE}).replace("%25", "%").replace("+", "+")
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if site is None:
            st = stated_list(body)
            if not st:
                die(f"{url}: the list states no «A al B de N empleos» ({len(body)} characters).", EXIT_PARTIAL)
            site = st[2]
            note(f"the list states {th(site)} («{st[0]} al {st[1]} de {th(site)} empleos»); the section page states {th(section) if section else '?'} «Oportunidades de Empleos»"
                 + (f" — {th(abs(section - site))} {'more' if section > site else 'fewer'} than the list serves, a difference of the site's own." if section and section != site else "."))
        page += 1
        rs = rows(body)
        new = 0
        for r in rs:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            print(json.dumps(r, ensure_ascii=False))
            emitted += 1
            new += 1
            if a.limit and emitted >= a.limit:
                break
        if a.limit and emitted >= a.limit:
            note(f"{th(emitted)} emitted over {page} page(s), list states {th(site)} — walk bounded by request (--limit), not compared.")
            return
        if not rs or new == 0 or emitted >= site:
            break
        if limit_pages is not None and page >= limit_pages:
            note(f"{th(emitted)} emitted over {page} page(s), list states {th(site)} — walk bounded by request (--pages {limit_pages}; --all walks to the count), not compared.")
            return
    if emitted == site:
        note(f"{th(emitted)} emitted over {page} page(s), list states {th(site)} — equal.")
    else:
        note(f"{th(emitted)} emitted over {page} page(s), list states {th(site)} — {th(abs(site - emitted))} {'short' if emitted < site else 'over'}.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an ad URL of this board (https://www.clasificadosonline.com/Empleos/Detail.asp?JobId=N).")
    ident = m.group(1)
    code, body = request(a.url.strip())
    if code == 404:
        die(f"{a.url}: HTTP 404 — the ad is gone.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_PARTIAL)
    meta = {}
    for k, v in META_RE.findall(body):
        meta.setdefault(k, v)
    if not meta.get("title"):
        die(f"{a.url}: no JobPosting microdata on the page — gone, or not the template this file reads.", EXIT_GONE)
    parts = re.findall(r'<span class="Roboto comment[^"]*">(.*?)</span>', body, re.S)   # the ad's prose: the description span, then the requirements span
    desc = "\n".join(clean(x) for x in parts if clean(x)) or clean(meta.get("description") or "")
    sal = re.search(r'(Desde \$[^<]{0,60}?hr|From \$[^<]{0,60}?hr|\$[\d.,]+\s*/\s*hr)', body)
    r = {"source": "clasificadosonline", "country": "PR", "ledger_id": f"clasificadosonline:{ident}", "id": ident, "url": a.url.strip(),
         "title": redact(clean(meta.get("title") or "")) or None, "employer": redact(clean(meta.get("hiringOrganization") or "")) or None,
         "posted": iso(meta.get("datePosted")) if meta.get("datePosted") else None,
         "valid_through": iso(meta.get("validThrough")) if meta.get("validThrough") else None,
         "employment_type": clean(meta.get("employmentType") or "") or None, "work_hours": clean(meta.get("workHours") or "") or None,
         "salary_currency": clean(meta.get("salaryCurrency") or "") or None, "salary_text": redact(clean(sal.group(1))) if sal else None,
         "description": redact(desc) or None}
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="walk the Empleos listing")
    g = l.add_mutually_exclusive_group()
    g.add_argument("--pages", type=int, default=None, help=f"pages to read (default {DEFAULT_PAGES}, bounded and said so)")
    g.add_argument("--all", action="store_true", help="walk to the count the list states, and compare")
    l.add_argument("--limit", type=int, default=0, help="stop after N rows (bounded, not compared)")
    l.add_argument("--cat", default="", help="JobsCat number (the site's category id)")
    l.add_argument("--town", default="", help="Pueblo, as the site spells it")
    l.add_argument("--q", default="", help="free text (txkey)")
    l.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one ad by its public URL")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
