#!/usr/bin/env python3
"""Kariéra (`kariera.zoznam.sk`, Slovakia — the Zoznam portal's board) — the list paged by offset, thirty cards a page, its pager's last page and its own offers sitemap as the two figures of the site; the ad page's labelled fields; the sitemap as the fast enumeration. Issue #345.

  kariera.py list [--pages N | --all] [--limit N]
  kariera.py sitemap [--limit N]
  kariera.py ad --url <https://kariera.zoznam.sk/pracovna-ponuka/<id>/<slug>>

THE ROUTE IS THE LIST, PAGED BY OFFSET. `/pracovne-ponuky?od=<0,30,60…>`
serves thirty `div.offer` cards — the ad's link `pracovna-ponuka/<id>/<slug>`,
the title, the employer (`/ponuky-spolocnosti/<slug>`), the locality, «od
1524 EUR/Mesiac» as the site writes it, the date «14.09.2026», a «Top»
badge — and a pager whose last link is `?od=8130` (page 272 of 30).
**The site states no count in words: its two figures are the pager's
last page and its offers sitemap** — `/sitemap-29052025/offers`, 1.36 MB,
**8 159 URLs** with `lastmod` on 2026-09-14 (272 × 30 = 8 160 ≥ 8 159).
`list --all` walks the pager and compares the distinct ids to the
sitemap's count; `sitemap` enumerates the 8 159 in one request (id, url,
lastmod) and prints the pager's figure beside it. The site also carries
«Top» ads repeated across pages — a key seen twice is counted once.

THE RULES. `/robots.txt` (1 208 B): the seven translated mutations
(`/en/`, `/de/`, `/cs/`…) and `/job-offers/`, `/job-offer/` are refused,
so are `/*?q=*` (the free-text search), `/rss/`, `/export/`, `/cv/`; the
Slovak list, `?od=` paging, the ad pages and the sitemap are open,
`certain: True`. 3 s own spacing.

THE AD PAGE (`/pracovna-ponuka/<id>/<slug>`) is a `ul.offer-detail-info`
of labelled blocks — «Miesto práce», «Ponúkaný plat (základná mzda)»,
«Druh pracovného pomeru», «Termín nástupu do práce» — then the sections
«Informácie o pracovnom mieste», «Benefity a ďalšie výhody», «Informácie
pre uchádzača», «Všeobecne požadované znalosti», «Požiadavky na
zamestnanca» (education, languages, skills), «Informácie o spoločnosti».
Salary is the site's text («2 945 EUR» + its sentence), never parsed.

WHAT IS WITHHELD. A contact person, address or phone number in the prose
is replaced (`[e-mail withheld]`, `[phone withheld]` — nine digits or
more, Slovak numbers are nine; a salary is never redacted); the employer's name and its public page
are the board's own and are emitted.

THE PUBLIC SERVICE REPUBLISHES THIS BOARD. `sluzbyzamestnanosti.py`
reads the state's store and names kariera.sk as one of its six external
sources, with `urlExternyPortal` pointing at these very ad pages — the
overlap is measured in the card, and this adapter is worth what the
direct read adds: the list's thirty a page with salary text and date,
the ad page's sections, and the sitemap's `lastmod`.
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

HOST = "kariera.zoznam.sk"
BASE = f"https://{HOST}"
LIST = f"{BASE}/pracovne-ponuky"
SITEMAP = f"{BASE}/sitemap-29052025/offers"
PAGE_SIZE = 30
DEFAULT_PAGES = 10
AD_RE = re.compile(r"^https?://kariera\.zoznam\.sk/pracovna-ponuka/(\d+)/[^/?#]*$")
CARD_RE = re.compile(r'<div class="offer(?: highlight)?"><div class="offer-top">(.*?)offer_id=(\d+)"', re.S)
LINK_RE = re.compile(r'<h2 class="offer-title"><a href="(?:redirect\.php\?[^"]*url=)?(pracovna-ponuka/(\d+)/[^"&]+)"[^>]*>(.*?)</a>', re.S)
EMP_RE = re.compile(r'<div class="offer-employer">(.*?)</div>', re.S)
LOC_RE = re.compile(r'<div class="offer-locality">(.*?)</div>', re.S)
SAL_RE = re.compile(r'<ul class="offer-info"><li><img[^>]*>(.*?)</li>', re.S)
DATE_RE = re.compile(r'<span class="date">(\d{2})\.(\d{2})\.(\d{4})</span>')
TOP_RE = re.compile(r'<span class="top">Top</span>')
LAST_RE = re.compile(r'pracovne-ponuky\?od=(\d+)"[^>]*class="end"')
SM_RE = re.compile(r"<url>\s*<loc>([^<]+)</loc>\s*(?:<lastmod>([^<]+)</lastmod>)?", re.S)
BLOCK_RE = re.compile(r'<div class="offer-label">\s*(.*?)\s*</div>\s*(.*?)</div>\s*(?:<a href="#" class="btn-label-more">[^<]*</a>\s*)?</div>\s*</li>', re.S)
SECTION_RE = re.compile(r'<h([23])[^>]*>\s*(.*?)\s*</h\1>(.*?)(?=<h[23]|<div class="offer-detail-bottom|</section>|<footer)', re.S)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\d[\d\s().-]{6,}\d(?!\w)")
LABELS = {"miesto práce": "location", "ponúkaný plat (základná mzda)": "salary_text", "ponúkaný plat": "salary_text", "druh pracovného pomeru": "contract",
          "termín nástupu do práce": "start", "minimálne požadované vzdelanie": "education", "jazykové znalosti": "languages", "znalosti": "skills"}
SECTIONS = {"informácie o pracovnom mieste": "description", "benefity a ďalšie výhody": "benefits", "informácie pre uchádzača": "applicant_info",
            "všeobecne požadované znalosti": "requirements", "charakteristika spoločnosti": "employer_description"}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACE = Pace(HOST, own=3.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[kariera] {msg}", file=sys.stderr)


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
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xml"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def clean(s):
    s = re.sub(r"<(script|style|svg)\b.*?</\1>", "", s or "", flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</li>|</div>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def redact(s):
    """Addresses and phone numbers — nine digits or more (Slovak numbers are nine, «+421» twelve); a salary «od 1 700 - 2 200 EUR» has eight and stays;
    a reference number («Ref. č.: 1234567890», measured on 5 of 8 159 titles) is announced by «ref» just before it and is not a phone."""
    s = EMAIL_RE.sub("[e-mail withheld]", s or "")

    def sub(m):
        if sum(c.isdigit() for c in m.group(0)) < 9:
            return m.group(0)
        if re.search(r"ref\.?\s*(?:č\.?|c\.?|no\.?|number)?\s*:?\s*$", s[max(0, m.start() - 14):m.start()], re.I):
            return m.group(0)
        return "[phone withheld]"
    return PHONE_RE.sub(sub, s)


def last_offset(body):
    m = LAST_RE.search(body or "")
    return int(m.group(1)) if m else None


def cards(body):
    out = []
    for blk, fav in CARD_RE.findall(body or ""):
        link = LINK_RE.search(blk)
        if not link:
            continue
        path, ident, title = link.groups()
        emp, loc, sal, d = EMP_RE.search(blk), LOC_RE.search(blk), SAL_RE.search(blk), DATE_RE.search(blk)
        out.append({
            "source": "kariera", "country": "SK", "ledger_id": f"kariera:{ident}", "id": ident, "url": f"{BASE}/{path}",
            "title": redact(clean(title)) or None, "employer": redact(clean(emp.group(1))) or None if emp else None,
            "location": clean(loc.group(1)) or None if loc else None,
            "salary_text": re.sub(r"\s+", " ", clean(sal.group(1))) or None if sal else None,   # a salary is digits; it is not redacted
            "posted": f"{d.group(3)}-{d.group(2)}-{d.group(1)}" if d else None,
            "top": True if TOP_RE.search(blk) else None,
        })
    return out


def sitemap_rows(body):
    out = []
    for loc, lastmod in SM_RE.findall(body or ""):
        m = re.search(r"/pracovna-ponuka/(\d+)/", loc)
        if m:
            out.append({"source": "kariera", "country": "SK", "ledger_id": f"kariera:{m.group(1)}", "id": m.group(1), "url": loc.strip(), "lastmod": (lastmod or "").strip() or None})
    return out


def sitemap_count():
    code, body = request(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_PARTIAL)
    rows = sitemap_rows(body)
    if not rows:
        die(f"{SITEMAP}: no ad URL in the sitemap ({len(body)} characters).", EXIT_PARTIAL)
    return rows


def cmd_list(a):
    if a.pages is not None and a.pages < 1:
        die("--pages must be at least 1 (or use --all).")
    limit_pages = None if a.all else (a.pages or DEFAULT_PAGES)
    site = len({r["id"] for r in sitemap_count()})
    seen, emitted, page, last, dups = set(), 0, 0, None, 0
    while True:
        page += 1
        url = LIST + (f"?od={(page - 1) * PAGE_SIZE}" if page > 1 else "")
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if page == 1:
            last = last_offset(body)
            if last is None:
                die(f"{url}: the list has no pager end (`?od=N` with class end) — not the list this file reads ({len(body)} characters).", EXIT_PARTIAL)
            last = last // PAGE_SIZE + 1
            note(f"the offers sitemap lists {th(site)} ads; the pager ends at page {last} of {PAGE_SIZE} ({th(last * PAGE_SIZE)} at most).")
        rows = cards(body)
        new = 0
        for r in rows:
            if r["id"] in seen:
                dups += 1
                continue
            seen.add(r["id"])
            print(json.dumps(r, ensure_ascii=False))
            emitted += 1
            new += 1
            if a.limit and emitted >= a.limit:
                break
        if a.limit and emitted >= a.limit:
            note(f"{th(emitted)} emitted over {page} page(s), sitemap lists {th(site)} — walk bounded by request (--limit), not compared.")
            return
        if not rows or page >= last:
            break
        if limit_pages is not None and page >= limit_pages:
            note(f"{th(emitted)} emitted over {page} page(s), sitemap lists {th(site)} — walk bounded by request (--pages {limit_pages}; --all walks the pager), not compared.")
            return
    extra = f" ({dups} key(s) seen twice across pages — «Top» ads repeat)" if dups else ""
    if emitted == site:
        note(f"{th(emitted)} emitted over {page} page(s), sitemap lists {th(site)} — equal{extra}.")
    else:
        note(f"{th(emitted)} emitted over {page} page(s), sitemap lists {th(site)} — {th(abs(site - emitted))} {'short' if emitted < site else 'over'}{extra}.")
        sys.exit(EXIT_PARTIAL)


def cmd_sitemap(a):
    rows = sitemap_count()
    seen, n = set(), 0
    for r in rows:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        print(json.dumps(r, ensure_ascii=False))
        n += 1
        if a.limit and n >= a.limit:
            break
    code, body = request(LIST)
    last = last_offset(body) if code == 200 else None
    pages = (last // PAGE_SIZE + 1) if last is not None else None
    note(f"{th(n)} emitted from the offers sitemap ({th(len(rows))} URLs, {th(len(seen))} distinct ids); the list's pager ends at page {pages} of {PAGE_SIZE}"
         + (f" ({th(pages * PAGE_SIZE)} at most — {'consistent' if pages and (pages - 1) * PAGE_SIZE < len(seen) <= pages * PAGE_SIZE else 'NOT consistent'} with the sitemap)." if pages else " (pager not read)."))


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an ad URL of this board (https://kariera.zoznam.sk/pracovna-ponuka/<id>/<slug>).")
    ident = m.group(1)
    code, body = request(a.url.strip())
    if code == 404:
        die(f"{a.url}: HTTP 404 — the ad is gone.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_PARTIAL)
    if 'class="offer-detail-info"' not in body:
        die(f"{a.url}: no `offer-detail-info` on the page — gone, or not the template this file reads.", EXIT_GONE)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    emp = re.search(r'<div class="offer-company">\s*<a[^>]*>(.*?)</a>', body, re.S)
    r = {"source": "kariera", "country": "SK", "ledger_id": f"kariera:{ident}", "id": ident, "url": a.url.strip(),
         "title": redact(clean(h1.group(1))) or None if h1 else None, "employer": redact(clean(emp.group(1))) or None if emp else None}
    for label, value in BLOCK_RE.findall(body):
        key = LABELS.get(clean(label).rstrip(":").lower())
        if key:
            v = re.sub(r"\s+", " ", clean(value))
            r[key] = (v if key == "salary_text" else redact(v)) or None
    for _, head, value in SECTION_RE.findall(body):
        key = SECTIONS.get(clean(head).rstrip(":").lower())
        if key and key not in r:
            r[key] = redact(clean(value)) or None
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="walk the list paged by offset")
    g = l.add_mutually_exclusive_group()
    g.add_argument("--pages", type=int, default=None, help=f"pages to read (default {DEFAULT_PAGES}, bounded and said so)")
    g.add_argument("--all", action="store_true", help="walk the whole pager, and compare to the offers sitemap")
    l.add_argument("--limit", type=int, default=0, help="stop after N rows (bounded, not compared)")
    l.set_defaults(fn=cmd_list)
    s = sub.add_parser("sitemap", help="enumerate the offers sitemap (id, url, lastmod) — one request")
    s.add_argument("--limit", type=int, default=0)
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one ad by its public URL")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
