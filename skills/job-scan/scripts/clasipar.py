#!/usr/bin/env python3
"""Clasipar, category Empleos (`clasipar.paraguay.com`, Paraguay) — a classifieds where «Busco» is an employer looking and «Ofrezco» a worker offering; the category's own «Búsqueda y postulación de Empleos (562)» beside every walk; invisible watermark spans stripped; contacts never shown. Issue #434.

  clasipar.py list [--mode busco|ofrezco|all] [--sub SLUG] [--pages N | --all] [--passes N] [--limit N]
  clasipar.py ad --url <https://clasipar.paraguay.com/empleos/<sub>/<slug>-<id>>

THE ROUTE IS THE CATEGORY LIST. `/empleos` and `/empleos/page-<p>` (the
page's own `rel="next"`) serve `article.box-anuncio` cards — the ad's
link `/empleos/<sub>/<slug>-<id>`, the title, «Gs. 4.200.000» as a price,
«<strong>Busco|Ofrezco</strong> | Ofrecido por: <strong>Particular|…</strong>»,
the subcategory and town («Otros empleos en Luque»), the advertiser's
page when it has one — with a JS-only filter form the adapter never
posts. Measured 2026-09-14 01:5x UTC: page 1 carries 33 cards (two of them
the «Premium» box), the next pages 25, the last (23) 12; **the category
page `/categorias/empleos` states «Búsqueda y postulación de Empleos
(562)»** and 23 pages of 25 hold ≈ 562. That is the witness. The menu's
«Empleos (1.248)» (category page) and «Empleos (900)» (list page) are
another figure of the site, written differently on two of its pages
minutes apart — printed, not compared.

BUSCO / OFREZCO. A classifieds mixes employers looking for people
(«Busco») and people offering their work («Ofrezco» — 15 of 33 on page 1,
9 of 12 on the last). **The default emits «Busco» only** — the job offers
— and says how many «Ofrezco» were passed over; `--mode all` emits both
with the `mode` field; the walk's comparison is on all rows read against
the category's count, because the count is the category's, not the mode's.

WATERMARKS. Every title and description is interleaved with spans styled
`font-size:0 !important` — «Encontrá todo lo que buscas en Clasipar.com»,
«Fuente del anuncio: <url>» — invisible to a reader, poison to a copy.
They are removed before any text is read. **The ad page masks the
advertiser's phone and e-mail («*********», «*******@********») behind a
button** — never pressed; addresses and numbers that survive in the prose
are replaced. The price («Gs. 4.200.000») is the site's text, never parsed.

THE PAGES ARE A RANDOM SAMPLE, NOT A SEQUENCE — measured 2026-09-14.
`/empleos/page-3` read twice five seconds apart: 25 cards each, **one in
common**, a different order; a full pass over the 23 pages (01:55–02:06
UTC, the site answering in ~25 s a page) read 570 cards and **364
distinct ids** — 198 short of the category's 562. Every page is a fresh
draw of the category, so a single pass cannot reach the count and this
file does not pretend it does: it dedups across pages, compares what it
read to the count, exits 6 on the gap and names the cause; `--passes N`
walks the pager N times and grows the union (each pass is a new draw —
the expected number of draws to see every ad is the coupon-collector's,
not the pager's). The sitemap index lists 1 611 site-wide ad sitemaps
(`ads1…ads1611.xml.gz`, every category) — not a route to 562 ads.

THE RULES. `robots.txt` (199 bytes): `*` refuses `/error/`, `/app/`,
`/config-paper/`; `bingbot` and `ia_archiver` refused `/`. Open, `certain:
True`; 3 s own spacing.
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

HOST = "clasipar.paraguay.com"
BASE = f"https://{HOST}"
DEFAULT_PAGES = 10
AD_RE = re.compile(r"^https?://clasipar\.paraguay\.com/empleos/([a-z0-9-]+)/[^/?#]+-(\d+)$")
CARD_RE = re.compile(r'<article class="box-anuncio[^"]*">(.*?)</article>', re.S)
LINK_RE = re.compile(r'<a href="(https://clasipar\.paraguay\.com/empleos/([a-z0-9-]+)/[^"]+-(\d+))"[^>]*class="titAnuncio"[^>]*>(.*?)</a>', re.S)
PRICE_RE = re.compile(r'<(?:p|h4|h3) class="(?:user-)?price">(.*?)</(?:p|h4|h3)>', re.S)
MODE_RE = re.compile(r"<strong>\s*(Busco|Ofrezco|BUSCO|OFREZCO)\s*</strong>")
BY_RE = re.compile(r"Ofrecido por:\s*<strong>(.*?)</strong>", re.S)
WHERE_RE = re.compile(r'title="([^"]*)">\s*([^<]*?)\s+en\s+([^<]+?)\s*</a>')
ADV_RE = re.compile(r'<a href="https://clasipar\.paraguay\.com/empresa/[^"]+"[^>]*>\s*(?:<img[^>]*>|Vendido por|Premium)?\s*([^<]*?)\s*</a>')
STATED_RE = re.compile(r"Búsqueda y postulación de Empleos(?:&nbsp;|\s)*<small>\(([\d.]+)\)</small>")
MENU_RE = re.compile(r"<span>Empleos \(([\d.]+)\)</span>")
LAST_RE = re.compile(r'data-page="(\d+)"')
WATERMARK_RE = re.compile(r'<span style="font-size:0 !important;"[^>]*>.*?</span>', re.S)
DETAIL_RE = re.compile(r'<span>([^<]+?):?</span>\s*<h6>(.*?)</h6>', re.S)
DESC_RE = re.compile(r'<p class="desc-user">(.*?)</p>', re.S)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().-]{5,}\d(?!\w)")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACE = Pace(HOST, own=3.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[clasipar] {msg}", file=sys.stderr)


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
    s = WATERMARK_RE.sub("", s or "")   # the invisible spans: promo lines and «Fuente del anuncio: <url>»
    s = re.sub(r"<(script|style|svg)\b.*?</\1>", "", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</li>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def redact(s):
    s = EMAIL_RE.sub("[e-mail withheld]", s or "")
    return PHONE_RE.sub(lambda m: "[phone withheld]" if sum(c.isdigit() for c in m.group(0)) >= 6 else m.group(0), s)


def num(s):
    return int(re.sub(r"[^\d]", "", s or "") or 0)


def iso(dmy):
    m = re.match(r"\s*(\d{2})/(\d{2})/(\d{4})\s*$", dmy or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else (clean(dmy) or None)


def stated(body):
    m = STATED_RE.search(body or "")
    return num(m.group(1)) if m else None


def menu(body):
    m = MENU_RE.search(body or "")
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
        url, sub, ident, title = link.groups()
        mode, by, price, where, adv = MODE_RE.search(blk), BY_RE.search(blk), PRICE_RE.search(blk), WHERE_RE.search(blk), ADV_RE.search(blk)
        out.append({
            "source": "clasipar", "country": "PY", "ledger_id": f"clasipar:{ident}", "id": ident, "url": url,
            "title": redact(clean(title)) or None, "mode": mode.group(1).lower() if mode else None,
            "offered_by": clean(by.group(1)) or None if by else None, "advertiser": redact(clean(adv.group(1))) or None if adv and clean(adv.group(1)) else None,
            "subcategory": sub, "location": clean(where.group(3)) or None if where else None,
            "price_text": clean(price.group(1)) or None if price else None,
            "premium": True if "box-anuncio--premium" in blk[:200] or "Premium" in blk else None,
        })
    return out


def cmd_list(a):
    if a.pages is not None and a.pages < 1:
        die("--pages must be at least 1 (or use --all).")
    limit_pages = None if a.all else (a.pages or DEFAULT_PAGES)
    mode = (a.mode or "busco").lower()
    if mode not in ("busco", "ofrezco", "all"):
        die("--mode is busco, ofrezco or all.")
    code, body = request(f"{BASE}/categorias/empleos")
    if code != 200:
        die(f"{BASE}/categorias/empleos: HTTP {code}", EXIT_PARTIAL)
    site = stated(body)
    if site is None:
        die(f"{BASE}/categorias/empleos: the category states no «Búsqueda y postulación de Empleos (N)» ({len(body)} characters).", EXIT_PARTIAL)
    m_cat = menu(body)
    root = f"{BASE}/empleos" + (f"/{a.sub}" if a.sub else "")
    seen, read, emitted, passed, page, last, pass_no, pages_read = set(), 0, 0, 0, 0, None, 1, 0
    while True:
        page += 1
        if last and page > last and pass_no < max(1, a.passes or 1) and limit_pages is None:
            note(f"pass {pass_no}: {th(read)} distinct read over {last} page(s) — every page is a fresh draw; starting pass {pass_no + 1}.")
            pass_no, page = pass_no + 1, 1
        url = root + (f"/page-{page}" if page > 1 else "")
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        pages_read += 1
        if pages_read == 1:
            last = last_page(body)
            m_list = menu(body)
            note(f"the category states {th(site)} («Búsqueda y postulación de Empleos»), pager to page {last}; the menu says «Empleos ({th(m_cat) if m_cat else '?'})» on the category page and "
                 f"«Empleos ({th(m_list) if m_list else '?'})» on the list — the site's own figures, printed, not compared.")
        rows = cards(body)
        new = 0
        for r in rows:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            read += 1
            new += 1
            if mode != "all" and r["mode"] != mode:
                passed += 1
                continue
            print(json.dumps(r, ensure_ascii=False))
            emitted += 1
            if a.limit and emitted >= a.limit:
                break
        tail = f" ({th(emitted)} «{mode}» emitted, {th(passed)} «{'ofrezco' if mode == 'busco' else 'busco'}» passed over)" if mode != "all" else ""
        if a.limit and emitted >= a.limit:
            note(f"{th(read)} read over {page} page(s), category states {th(site)}{tail} — walk bounded by request (--limit), not compared.")
            return
        if not rows or read >= site or (last and page >= last and pass_no >= max(1, a.passes or 1)):
            break
        if limit_pages is not None and pages_read >= limit_pages:
            note(f"{th(read)} read over {pages_read} page(s), category states {th(site)}{tail} — walk bounded by request (--pages {limit_pages}; --all walks to the count), not compared.")
            return
    if a.sub:
        note(f"{th(read)} read over {pages_read} page(s) of /empleos/{a.sub}{tail} — a subcategory walk, not compared to the category's {th(site)}.")
        return
    if read == site:
        note(f"{th(read)} read over {pages_read} page(s), category states {th(site)}{tail} — equal.")
    else:
        note(f"{th(read)} read over {pages_read} page(s), category states {th(site)}{tail} — {th(abs(site - read))} {'short' if read < site else 'over'}"
             f"{' (every page is a fresh random draw of the category — one pass cannot reach the count; --passes N grows the union)' if read < site else ''}.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an ad URL of this board (https://clasipar.paraguay.com/empleos/<sub>/<slug>-<id>).")
    sub, ident = m.groups()
    code, body = request(a.url.strip())
    if code == 404:
        die(f"{a.url}: HTTP 404 — the ad is gone.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_PARTIAL)
    t = re.search(r'<h2 class="tit-detalle">Detalle de:<span>(.*?)</span></h2>', body, re.S)
    d = DESC_RE.search(body)
    if not t and not d:
        die(f"{a.url}: no «Detalle de» on the page — gone, or not the template this file reads.", EXIT_GONE)
    details = {clean(k).rstrip(":").lower(): clean(v) for k, v in DETAIL_RE.findall(body)}
    price = re.search(r'<h3 class="user-price">(.*?)</h3>', body, re.S)
    mode = re.search(r"<strong>\s*(BUSCO|OFREZCO|Busco|Ofrezco)\s*</strong>", body)
    r = {"source": "clasipar", "country": "PY", "ledger_id": f"clasipar:{ident}", "id": ident, "url": a.url.strip(), "subcategory": sub,
         "title": redact(clean(t.group(1))) or None if t else None, "mode": mode.group(1).lower() if mode else None,
         "location": details.get("ciudad") or None, "zone": redact(details.get("zona") or "") or None,
         "posted": iso(details.get("publicado el")) if details.get("publicado el") else None,
         "price_text": clean(price.group(1)) or None if price else None,
         "description": redact(clean(d.group(1))) or None if d else None}
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="walk the Empleos category")
    l.add_argument("--mode", default="busco", help="busco (employers looking — the default), ofrezco (workers offering), all")
    l.add_argument("--sub", default="", help="a subcategory slug (administracion, ventas, …) — walked on its own, not compared")
    g = l.add_mutually_exclusive_group()
    g.add_argument("--pages", type=int, default=None, help=f"pages to read (default {DEFAULT_PAGES}, bounded and said so)")
    g.add_argument("--all", action="store_true", help="walk the whole pager, and compare to the count the category states")
    l.add_argument("--passes", type=int, default=1, help="with --all: walk the pager N times — every page is a fresh random draw, the union grows")
    l.add_argument("--limit", type=int, default=0, help="stop after N emitted rows (bounded, not compared)")
    l.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one ad by its public URL")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
