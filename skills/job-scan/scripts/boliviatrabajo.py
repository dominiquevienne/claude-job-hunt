#!/usr/bin/env python3
"""BoliviaTrabajo (`trabajo.info.bo`, Bolivia) — «949 ofertas publicadas en Bolivia» on the list, twelve cards a page, and a full JobPosting with a currency on the ad page. Issue #431.

  boliviatrabajo.py list [--q TEXT] [--pages N | --all] [--limit N]
  boliviatrabajo.py ad --url <https://trabajo.info.bo/oferta/<id>-<slug>>

THE ROUTE IS THE LIST. `/ofertas?q=<text>&page=<p>` serves twelve
`<article>` cards — category, contract and salary badges, the title and
its link `oferta/<id>-<slug>`, «<employer> · <city> · Publicado: 12 Sep
2026» — under **«949 ofertas publicadas en Bolivia»** and a pager whose
last link is `page=80` (80 × 12 = 960 ≥ 949). `/buscar` is the same list
under another name (the same twelve ids on 2026-09-14). No key, no cookie,
no browser; `robots.txt` refuses the account, apply and CV routes and
`Allow: /` the rest; 3 s own spacing.

THE AD PAGE (`/oferta/<id>-<slug>`) carries a `JobPosting` in JSON-LD —
title, identifier, datePosted, validThrough, description, hiringOrganization,
jobLocation (city, region, street), employmentType, **baseSalary with its
currency (BOB) and unit (MONTH)** — and the same as prose («Jornada»,
«Modalidad», «Salario 5.500 Bs.», «Vigente»). Salary from the JSON-LD is
emitted with its currency; the badge's text («5.500 Bs.») as `salary_text`.
The modality («Presencial») is on the page's prose only.

WHAT IS WITHHELD. Addresses and phone numbers in the prose are replaced
(`[e-mail withheld]`, `[phone withheld]` — seven digits or more, Bolivian
mobiles are eight). The site's own `web@boliviatrabajo.bo` and WhatsApp
number sit in its footer, in no field this file emits.
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

HOST = "trabajo.info.bo"
BASE = f"https://{HOST}"
PAGE_SIZE = 12
DEFAULT_PAGES = 10
AD_RE = re.compile(r"^https?://(?:www\.)?trabajo\.info\.bo/oferta/(\d+)-[^/?#]*$")
CARD_RE = re.compile(r"<article\b(.*?)</article>", re.S)
LINK_RE = re.compile(r'<h3[^>]*>\s*<a[^>]*href="oferta/(\d+)-([^"]+)"[^>]*>(.*?)</a>', re.S)
BADGE_RE = re.compile(r'<span class="text-xs font-semibold[^"]*?(bg-bg-blue-soft|bg-slate-100|bg-accent/10)[^"]*">(.*?)</span>', re.S)   # the class names the badge: category / contract / salary
BADGE_KEY = {"bg-bg-blue-soft": "category", "bg-slate-100": "contract", "bg-accent/10": "salary_text"}
LINE_RE = re.compile(r'<div class="text-sm text-slate-500[^"]*">(.*?)</div>', re.S)
STATED_RE = re.compile(r"([\d.,]+)\s*ofertas publicadas")
LAST_RE = re.compile(r"page=(\d+)")
LD_RE = re.compile(r"<script[^>]*ld\+json[^>]*>(.*?)</script>", re.S)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\d[\d\s().-]{5,}\d(?!\w)")
MONTHS = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8, "sep": 9, "set": 9, "oct": 10, "nov": 11, "dic": 12,
          "jan": 1, "apr": 4, "aug": 8, "dec": 12}   # the list writes «12 Sep 2026» and «01 Aug 2026» — English abbreviations beside Spanish ones
DATE_RE = re.compile(r"(\d{1,2})\s+([A-Za-z]{3})\w*\s+(\d{4})")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACE = Pace(HOST, own=3.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[boliviatrabajo] {msg}", file=sys.stderr)


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
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def clean(s):
    s = re.sub(r"<(script|style|svg)\b.*?</\1>", "", s or "", flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</li>", "\n", s, flags=re.I)
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


def iso(es):
    """«12 Sep 2026» → «2026-09-12»; anything else as text."""
    m = DATE_RE.search(es or "")
    if not m or m.group(2).lower()[:3] not in MONTHS:
        return clean(es) or None
    return f"{m.group(3)}-{MONTHS[m.group(2).lower()[:3]]:02d}-{int(m.group(1)):02d}"


def stated(body):
    m = STATED_RE.search(body or "")
    return num(m.group(1)) if m else None


def last_page(body):
    pages = [int(x) for x in LAST_RE.findall(body or "")]
    return max(pages) if pages else None


def cards(body):
    out = []
    for blk in CARD_RE.findall(body or ""):
        link = LINK_RE.search(blk)
        if not link:
            continue
        ident, slug, title = link.groups()
        badges = {BADGE_KEY[k]: clean(v) for k, v in BADGE_RE.findall(blk)}
        line = LINE_RE.search(blk)
        parts = [p.strip() for p in clean(line.group(1)).split("·")] if line else []
        posted = next((p.split(":", 1)[1] for p in parts if p.lower().startswith("publicado")), None)
        rest = [p for p in parts if not p.lower().startswith("publicado")]
        out.append({
            "source": "boliviatrabajo", "country": "BO", "ledger_id": f"boliviatrabajo:{ident}", "id": ident, "url": f"{BASE}/oferta/{ident}-{slug}",
            "title": redact(clean(title)) or None,
            "employer": redact(rest[0]) or None if rest else None, "location": rest[1] or None if len(rest) > 1 else None,
            "category": badges.get("category") or None, "contract": badges.get("contract") or None,
            "salary_text": badges.get("salary_text") or None,
            "posted": iso(posted) if posted else None,
        })
    return out


def cmd_list(a):
    if a.pages is not None and a.pages < 1:
        die("--pages must be at least 1 (or use --all).")
    limit_pages = None if a.all else (a.pages or DEFAULT_PAGES)
    seen, emitted, page, site, last = set(), 0, 0, None, None
    while True:
        page += 1
        url = f"{BASE}/ofertas?" + urllib.parse.urlencode({"q": a.q or "", "page": page})
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if site is None:
            site = stated(body)
            if site is None:
                die(f"{url}: the page states no «N ofertas publicadas» ({len(body)} characters).", EXIT_PARTIAL)
            last = last_page(body)
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
            note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} ({label}) — walk bounded by request (--limit), not compared.")
            return
        if not rows or new == 0 or emitted >= site or (last and page >= last):
            break
        if limit_pages is not None and page >= limit_pages:
            note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} ({label}) — walk bounded by request (--pages {limit_pages}; --all walks to the count), not compared.")
            return
    if emitted == site:
        note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} ({label}) — equal.")
    else:
        note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} ({label}) — {th(abs(site - emitted))} {'short' if emitted < site else 'over'}.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an ad URL of this board (https://trabajo.info.bo/oferta/<id>-<slug>).")
    ident = m.group(1)
    code, body = request(a.url.strip())
    if code == 404:
        die(f"{a.url}: HTTP 404 — the ad is gone.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_PARTIAL)
    ld = None
    for blob in LD_RE.findall(body):
        try:
            j = json.loads(blob)
        except ValueError:
            continue
        if isinstance(j, dict) and j.get("@type") == "JobPosting":
            ld = j
            break
    if not ld:
        die(f"{a.url}: no JobPosting on the page — gone, or not the template this file reads.", EXIT_GONE)
    org = ld.get("hiringOrganization") or {}
    addr = (ld.get("jobLocation") or {}).get("address") or {}
    sal = ld.get("baseSalary") or {}
    val = sal.get("value") if isinstance(sal.get("value"), dict) else {}
    mod = re.search(r"Modalidad\s*</[^>]+>\s*<[^>]+>\s*([^<]{1,40}?)\s*<", body, re.S)
    stxt = re.search(r"Salario\s*</[^>]+>\s*<[^>]+>\s*([^<]{1,60}?)\s*<", body, re.S)
    r = {"source": "boliviatrabajo", "country": "BO", "ledger_id": f"boliviatrabajo:{ident}", "id": ident, "url": a.url.strip(),
         "title": redact(clean(ld.get("title") or "")) or None, "employer": redact(clean(org.get("name") or "")) or None,
         "location": clean(addr.get("addressLocality") or "") or None, "region": clean(addr.get("addressRegion") or "") or None,
         "posted": (ld.get("datePosted") or "")[:10] or None, "valid_through": (ld.get("validThrough") or "")[:10] or None,
         "employment_type": ld.get("employmentType") or None, "modality": clean(mod.group(1)) if mod else None,
         "salary_min": val.get("minValue"), "salary_max": val.get("maxValue"), "salary_currency": sal.get("currency") or None,
         "salary_unit": val.get("unitText") or None, "salary_text": clean(stxt.group(1)) if stxt else None,
         "description": redact(clean(ld.get("description") or "")) or None}
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="walk the list")
    l.add_argument("--q", default="", help="free text, the site's own `q`")
    g = l.add_mutually_exclusive_group()
    g.add_argument("--pages", type=int, default=None, help=f"pages to read (default {DEFAULT_PAGES}, bounded and said so)")
    g.add_argument("--all", action="store_true", help="walk to the count the site states, and compare")
    l.add_argument("--limit", type=int, default=0, help="stop after N rows (bounded, not compared)")
    l.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one ad by its public URL")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
