#!/usr/bin/env python3
"""HonduTrabajos (`www.hondutrabajos.com`, Honduras) — the list paged at the root, «+4,017 ofertas laborales activas» printed beside every walk; the ad page's own JobPosting; the recruiter's address in the prose withheld. Issue #438.

  hondutrabajos.py list [--pages N | --all] [--limit N]
  hondutrabajos.py ad --url <https://www.hondutrabajos.com/empleo/<slug>-<key>>

THE ROUTE IS THE ROOT, PAGED. `/?page=<p>` serves twelve `div.job-card`
blocks a page — the ad's link `/empleo/<slug>-<key>`, the title, the
employer (`/empresa/<slug>`), the department, the modality («Remoto» /
«Oficina» / «Híbrido»), the badges (contract, experience, «¡Cierra
pronto!», «Nuevo»), «hace N días» and the numeric id in `toggleSave(N)`
— under **«+4,017 ofertas laborales activas en Honduras»** and a pager
whose last link is `?page=335` (335 × 12 = 4 020 ≥ 4 017). Laravel,
server-rendered; no key, no cookie, no browser. `robots.txt`: `User-agent:
* / Allow: /`, a sitemap; 3 s between requests is ours.

THREE NUMBERS ON THE FRONT PAGE, AND WHICH ONE IS THE LIST'S. Read
2026-09-13 20:12 by the country search: «4,016 ofertas», «Ofertas Activas
818», «Más de 115 vacantes activas». Read 2026-09-14 00:56 by this file:
«+4,017 ofertas laborales activas», the stat box «4,017+ Ofertas Activas»,
the banner «Más de 115 vacantes activas» unchanged. **The witness is the
list's own «+N ofertas laborales activas»** — the number the pager
agrees with (335 pages of 12); the «818» of the day before was the stat
box, which now shows the same 4 017; the banner's «Más de 115» is a
lower bound written by hand and is printed, not compared.

THE AD PAGE carries a `JobPosting` in JSON-LD (title, description,
datePosted, validThrough, employmentType, hiringOrganization,
jobLocation) and a «DATOS TÉCNICOS» block (UBICACIÓN EXACTA, CONTRATO,
MODALIDAD, VACANTES, EXPERIENCIA). **The description often ends with
«Correo para aplicar: <address>»** — the recruiter's address, withheld
(`[e-mail withheld]`), as is any phone number; the employer's name and
public page are the board's own and are emitted. Salary is whatever the
prose says, never parsed.
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

HOST = "www.hondutrabajos.com"
BASE = f"https://{HOST}"
PAGE_SIZE = 12
DEFAULT_PAGES = 10
AD_RE = re.compile(r"^https?://www\.hondutrabajos\.com/empleo/([^/?#]+)$")
CARD_RE = re.compile(r'<div\s+class="job-card[^"]*"(.*?)toggleSave\((\d+)\)', re.S)
LINK_RE = re.compile(r'<a href="(https://www\.hondutrabajos\.com/empleo/([^"]+))"[^>]*title="([^"]*)"')
EMP_RE = re.compile(r'<a href="https://www\.hondutrabajos\.com/empresa/[^"]+"[^>]*>\s*(.*?)\s*</a>', re.S)
LOC_RE = re.compile(r'<span class="truncate">(.*?)</span>', re.S)
MODE_RE = re.compile(r'hidden sm:inline">\s*(Remoto|Oficina|Híbrido|Hibrido|Presencial)\s*<', re.S)
BADGE_RE = re.compile(r'tracking-wider[^"]*">\s*(.*?)\s*</span>', re.S)
EXP_RE = re.compile(r'dark:border-slate-650">\s*(.*?)\s*</span>', re.S)
AGO_RE = re.compile(r'<span>\s*(hace [^<]+?)\s*</span>')
STATED_RE = re.compile(r'\+?\s*([\d,.]+)\s*ofertas laborales activas')
LAST_RE = re.compile(r'\?page=(\d+)')
BANNER_RE = re.compile(r'Más de\s*([\d,.]+)\s*vacantes activas')
LD_RE = re.compile(r'<script[^>]*ld\+json[^>]*>(.*?)</script>', re.S)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\d[\d\s().-]{6,}\d(?!\w)")
TECH = {"UBICACIÓN EXACTA": "location", "CONTRATO": "contract", "MODALIDAD": "modality", "VACANTES": "positions", "EXPERIENCIA": "experience", "REQUISITOS ADICIONALES": "requirements"}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACE = Pace(HOST, own=3.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[hondutrabajos] {msg}", file=sys.stderr)


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
    return PHONE_RE.sub(lambda m: "[phone withheld]" if sum(c.isdigit() for c in m.group(0)) >= 8 else m.group(0), s)


def num(s):
    return int(re.sub(r"[^\d]", "", s or "") or 0)


def stated(body):
    m = STATED_RE.search(body or "")
    return num(m.group(1)) if m else None


def last_page(body):
    pages = [int(x) for x in LAST_RE.findall(body or "")]
    return max(pages) if pages else None


def cards(body):
    out = []
    for blk, ident in CARD_RE.findall(body or ""):
        link = LINK_RE.search(blk)
        if not link:
            continue
        url, slug, title = link.groups()
        emp, loc, mode, ago = EMP_RE.search(blk), LOC_RE.search(blk), MODE_RE.search(blk), AGO_RE.search(blk)
        badges = [clean(b) for b in BADGE_RE.findall(blk)]
        exp = EXP_RE.search(blk)
        out.append({
            "source": "hondutrabajos", "country": "HN", "ledger_id": f"hondutrabajos:{slug.rsplit('-', 1)[-1]}", "id": ident, "key": slug.rsplit("-", 1)[-1], "url": url,
            "title": redact(clean(title)) or None, "employer": redact(clean(emp.group(1))) or None if emp else None,
            "location": clean(loc.group(1)) or None if loc else None, "modality": clean(mode.group(1)) if mode else None,
            "contract": next((b for b in badges if b not in ("¡Cierra pronto!", "Nuevo", "Destacado")), None),
            "experience": clean(exp.group(1)) or None if exp else None,
            "closing_soon": True if "¡Cierra pronto!" in badges else None, "new": True if "Nuevo" in blk else None,
            "posted_relative": clean(ago.group(1)) if ago else None,
        })
    return out


def cmd_list(a):
    if a.pages is not None and a.pages < 1:
        die("--pages must be at least 1 (or use --all).")
    limit_pages = None if a.all else (a.pages or DEFAULT_PAGES)
    seen, emitted, page, site, last, banner, dups = set(), 0, 0, None, None, None, 0
    while True:
        page += 1
        url = f"{BASE}/" + (f"?page={page}" if page > 1 else "")
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if site is None:
            site = stated(body)
            if site is None:
                die(f"{url}: the page states no «+N ofertas laborales activas» ({len(body)} characters).", EXIT_PARTIAL)
            last = last_page(body)
            b = BANNER_RE.search(body)
            banner = num(b.group(1)) if b else None
            note(f"site states {th(site)} active ads; pager's last page {last} ({PAGE_SIZE} a page); banner «Más de {th(banner) if banner else '?'} vacantes activas» — a hand-written floor, not compared.")
        rows = cards(body)
        new = 0
        for r in rows:
            if r["key"] in seen:
                dups += 1   # a live list shifts under a long walk: a key seen twice is counted once, and the tally says how many
                continue
            seen.add(r["key"])
            print(json.dumps(r, ensure_ascii=False))
            emitted += 1
            new += 1
            if a.limit and emitted >= a.limit:
                break
        if a.limit and emitted >= a.limit:
            note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} — walk bounded by request (--limit), not compared.")
            return
        if not rows or new == 0 or emitted >= site or (last and page >= last):
            break
        if limit_pages is not None and page >= limit_pages:
            note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} — walk bounded by request (--pages {limit_pages}; --all walks to the count), not compared.")
            return
    if emitted == site:
        note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} — equal.")
    else:
        note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} — {th(abs(site - emitted))} {'short' if emitted < site else 'over'}"
             f"{f' ({dups} key(s) seen twice across pages: the list moved under the walk)' if dups else ''}.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an ad URL of this board (https://www.hondutrabajos.com/empleo/<slug>-<key>).")
    slug = m.group(1)
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
    addr = ((ld.get("jobLocation") or {}).get("address") or {})
    ident = None
    sv = re.search(r"toggleSave\((\d+)\)", body)
    if sv:
        ident = sv.group(1)
    r = {"source": "hondutrabajos", "country": "HN", "ledger_id": f"hondutrabajos:{slug.rsplit('-', 1)[-1]}", "id": ident, "key": slug.rsplit("-", 1)[-1],   # the ledger key is the URL's own suffix, on the list and on the ad alike
         "url": a.url.strip(), "title": redact(clean(ld.get("title") or "")) or None,
         "employer": redact(clean(org.get("name") or "")) or None, "employer_url": org.get("sameAs") or None,
         "location": clean(addr.get("addressLocality") or addr.get("streetAddress") or "") or None,
         "posted": (ld.get("datePosted") or "")[:10] or None, "valid_through": (ld.get("validThrough") or "")[:10] or None,
         "employment_type": ld.get("employmentType") or None,
         "description": redact(clean(ld.get("description") or "")) or None}
    for label, key in TECH.items():
        mm = re.search(r">\s*" + re.escape(label) + r"\s*<.*?<(?:p|div|span)[^>]*>\s*([^<]{1,160}?)\s*<", body, re.S)
        if mm:
            v = clean(mm.group(1))
            r[key] = (num(v) or None) if key == "positions" else (redact(v) or None)
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="walk the list paged at the root")
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
