#!/usr/bin/env python3
"""Convocatorias del Gobierno de Puerto Rico (`www.empleos.pr.gov`) — the Registro Central de Convocatorias of the OATRH, the island's public-service job calls, through the Webflow pages the site serves; «Page N of M» printed beside every walk. Issue #441.

  empleos_pr.py list [--pages N] [--limit N]
  empleos_pr.py ad --url <https://www.empleos.pr.gov/convocatorias/<slug>>

THE ROUTE IS THE PAGE — a Webflow CMS site (Finsweet `cmsload` in pagination mode,
`cmsfilter` for the sidebar); every page is a plain GET and the list is what the
server renders, no API:

  GET /                                   -> 12 convocatorias, the pager «Page 1 of 12» (`aria-label`), the next link `?205b2a0f_page=2`
  GET /?205b2a0f_page=N                   -> page N, «Page N of 12»
  GET /convocatorias/<slug>               -> one convocatoria

The list's query key (`205b2a0f`) is read from the page's own «Next Page» link, never
assumed — a second collection on the same page (the agency select) has its own key.
**Webflow's conditional visibility is honoured**: a block whose class carries
`w-condition-invisible` is what the site hides (the closing date when the call is
«Hasta Nuevo Aviso», the maximum salary when none is set, a type that is not set) and
this adapter does not read it as shown.

Measured 2026-09-13 23:3x UTC by the declared client: «Page 1 of 12», 12 a page,
page 2 «Page 2 of 12», page 12 «Page 12 of 12» with 12 rows — 144 in the register;
the rules: `www.empleos.pr.gov` writes no robots.txt rule (an absence, `certain:
False`); no Crawl-delay — 3 s is ours. **`--pages` defaults to 20** (240 rows) — 12 is
under that, so the default walks the whole register.

THE ROW carries the position (`titulo`), the entity («Universidad de Puerto Rico
(UPR)», «Departamento de Educación (DEPR)» …), the region, the call number
(«UPR-SEA-26-01AE»), the closing date («September 30, 2026», or «Hasta Nuevo Aviso»),
the type when set («Externa», «Reapertura Externa», «Interna»), the minimum monthly
salary from the hidden filter field, and the pilot-plan flag. THE DETAIL adds the
occupational group, the salary block (minimum / maximum, monthly / annual, the
authorised recruiting salary — USD, the period stated), and the sections «Naturaleza
del Trabajo», «Condiciones de Trabajo», «Requisitos Mínimos», «Requisitos Especiales»,
«Naturaleza del Examen», «Notas Importantes». **The entity is the employer — the
State's own agencies.** No recruiter contact is emitted: the OATRH's address and mailbox
in the page footer are the office's, not a posting's, and they are dropped.
"""

import argparse
import html as htmlmod
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

HOST = "www.empleos.pr.gov"
BASE = f"https://{HOST}"
DETAIL_RE = re.compile(r"^https?://www\.empleos\.pr\.gov/convocatorias/([A-Za-z0-9._-]+)/?$")
PAGE_RE = re.compile(r'aria-label="Page (\d+) of (\d+)"')
NEXT_RE = re.compile(r'href="\?([0-9a-f]+)_page=(\d+)"[^>]*aria-label="Next Page"')
ITEM_RE = re.compile(r'<div[^>]*role="listitem"[^>]*class="conv-collection-item[^"]*"[^>]*>(.*?)<div id="hiddein-fields"[^>]*>(.*?)</div>\s*</div>', re.S)
INVISIBLE = "w-condition-invisible"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[empleos_pr] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=3.0)   # the site writes no rule; 3 s is ours


def request(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "es"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</td>|</th>|</tr>|</li>|</h\d>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t‍]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def visible(attrs):
    """Webflow hides a block by class — `w-condition-invisible` — and this adapter reads only what the site shows."""
    return INVISIBLE not in (attrs or "")


def shown(markup, attr, value):
    """The text of the first VISIBLE element carrying `attr="value"`, or None."""
    for m in re.finditer(r'<div([^>]*\b%s="%s"[^>]*)>(.*?)</div>' % (re.escape(attr), re.escape(value)), markup or "", re.S):
        if visible(m.group(1)):
            t = text(m.group(2))
            return t or None
    return None


def stated(body):
    """(page, pages) from the pager's own «Page N of M»."""
    m = PAGE_RE.search(body or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def next_key(body):
    """The list's query key, read off the page's own «Next Page» link."""
    m = NEXT_RE.search(body or "")
    return m.group(1) if m else None


def money(s):
    if not s:
        return None
    m = re.search(r"\d[\d,]*(?:\.\d+)?", s)
    return float(m.group(0).replace(",", "")) if m else None


def rows(body):
    out = []
    for m in ITEM_RE.finditer(body or ""):
        card, hidden = m.group(1), m.group(2)
        link = re.search(r'href="(/convocatorias/([A-Za-z0-9._-]+))"', card)
        if not link:
            continue
        slug = link.group(2)
        closing = shown(card, "class", "item-data fecha-cierre")   # the date block when it is shown; the «Hasta Nuevo Aviso» block is shown instead when the date is not
        piloto = bool(re.search(r'con-item="plan-piloto"(?![^>]*%s)' % INVISIBLE, card))
        smin = money(shown(hidden, "class", "salario-minimo"))
        out.append({
            "source": "empleos_pr", "country": "PR", "ledger_id": f"empleos_pr:{slug}", "id": slug,
            "url": f"{BASE}/convocatorias/{slug}",
            "title": shown(card, "con-item", "titulo-puesto"),
            "employer": shown(card, "con-item", "agency-name"),          # the entity or municipality — the State's own agency is the employer
            "region": shown(card, "con-item", "region-name"),
            "call_number": shown(card, "con-item", "jobNumber"),
            "call_type": shown(card, "con-item", "external-internal"),  # Externa / Interna / Reapertura … — null when the site shows none
            "closing": closing,                                          # «September 30, 2026» as printed, or «Hasta Nuevo Aviso»
            "pilot_plan": piloto,
            "salary_min": smin, "salary_currency": "USD" if smin else None,
            "salary_period": "MONTH" if smin else None, "salary_unit_stated": bool(smin),   # the detail's own label «Salario Mínimo Mensual»
            "language": "es",
        })
    return out


def cmd_list(a):
    code, body = request(BASE + "/")
    if code != 200:
        die(f"{BASE}/: HTTP {code}", EXIT_PARTIAL)
    s = stated(body)
    if s is None:
        if not rows(body):
            note("no «Page N of M» pager and no convocatoria on the page — the register shows nothing.")
            return
        die(f"{BASE}/: convocatorias on the page and no «Page N of M» pager — the count line changed; a walk without it is not compared.", EXIT_PARTIAL)
    pages_stated = s[1]
    key = next_key(body)
    out, seen, pageno = [], set(), 1
    while True:
        for r in rows(body):
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            out.append(r)
        if pageno >= pages_stated:
            break
        if a.pages and pageno >= a.pages:
            break
        if a.limit and len(out) >= a.limit:
            break
        if not key:
            die(f"{BASE}/: page {pageno} of {pages_stated} and no «Next Page» link to read the list's key from.", EXIT_PARTIAL)
        pageno += 1
        code, body = request(f"{BASE}/?{key}_page={pageno}")
        if code != 200:
            die(f"{BASE}/?{key}_page={pageno}: HTTP {code}", EXIT_PARTIAL)
        now = stated(body)
        if now is None or now[0] != pageno:
            die(f"{BASE}/?{key}_page={pageno}: asked for page {pageno}, the pager says {now!r} — the page did not turn.", EXIT_PARTIAL)
    emitted = out[:a.limit] if a.limit else out
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    bounded = (a.pages and pageno < pages_stated) or (a.limit and a.limit < len(out))
    if bounded:
        note(f"{th(n)} emitted over {pageno} of the {pages_stated} page(s) the site states — walked by request (--pages/--limit), not a shortfall.")
    else:
        note(f"{th(n)} emitted over {pageno} page(s), site states {pages_stated} page(s) — every page walked; the site states no total, the pages are the witness.")


def section(body, heading):
    """The rich-text block right after an `inner-section-title` — when the site shows it and it is not bound empty."""
    m = re.search(r'<div[^>]*class="inner-section-title[^"]*"[^>]*>\s*%s\s*</div>\s*<div([^>]*)>(.*?)</div>' % re.escape(heading), body or "", re.S)
    if not m or not visible(m.group(1)) or "w-dyn-bind-empty" in m.group(1):
        return None
    return text(m.group(2)) or None


def salary_block(body, label):
    """«<label>:» followed by a `wfu-format="usd"` value, inside a data-block the site shows."""
    m = re.search(r'<div([^>]*class="data-block[^"]*")[^>]*>\s*<div[^>]*>%s\s*</div>\s*<div[^>]*wfu-format="usd"[^>]*>([^<]*)</div>' % re.escape(label), body or "", re.S)
    if not m or not visible(m.group(1)):
        return None
    return money(m.group(2))


def cmd_ad(a):
    m = DETAIL_RE.match((a.url or "").strip())
    if not m:
        die(f"{a.url}: not a convocatoria address — expected {BASE}/convocatorias/<slug>")
    slug = m.group(1)
    code, body = request(a.url)
    if code in (404, 410):
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    title = shown(body, "fs-cmsfilter-field", "titulo")
    if not title or "inner-section-title" not in body:
        die(f"{a.url}: not a convocatoria page ({len(body)} characters) — a redirect or the site's 404 template.", EXIT_PARTIAL)
    closing = shown(body, "class", "item-data fecha-cierre")
    smin_m, smax_m = salary_block(body, "Salario Mínimo Mensual:"), salary_block(body, "Salario Máximo Mensual:")
    smin_y, smax_y = salary_block(body, "Salario Mínimo Anual:"), salary_block(body, "Salario Máximo Anual:")
    period = "MONTH" if (smin_m or smax_m) else ("YEAR" if (smin_y or smax_y) else None)
    print(json.dumps({
        "source": "empleos_pr", "country": "PR", "ledger_id": f"empleos_pr:{slug}", "id": slug, "url": a.url,
        "title": title,
        "employer": shown(body, "fs-cmsfilter-field", "entidad-gubernamental"),
        "region": shown(body, "fs-cmsfilter-field", "region-pueblo"),
        "call_number": shown(body, "fs-cmsfilter-field", "numero-convocatoria"),
        "call_type": shown(body, "fs-cmsfilter-field", "tipo-convocatoria"),
        "occupational_group": shown(body, "fs-cmsfilter-field", "grupo-ocupacional"),
        "closing": closing,
        "salary_min": smin_m or smin_y, "salary_max": smax_m or smax_y,
        "salary_currency": "USD" if period else None, "salary_period": period, "salary_unit_stated": bool(period),
        "salary_authorised": salary_block(body, "Salario Autorizado para Reclutar:"),
        "nature_of_work": section(body, "Naturaleza del Trabajo:"),
        "working_conditions": section(body, "Condiciones de Trabajo:"),
        "minimum_requirements": section(body, "Requisitos Mínimos"),
        "special_requirements": section(body, "Requisitos Especiales"),
        "examination": section(body, "Naturaleza del Examen"),
        "notes": section(body, "Notas Importantes"),
        "language": "es",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Convocatorias del Gobierno de Puerto Rico — the OATRH's central register, through the Webflow pages the site serves; «Page N of M» beside every walk; the State's agencies are the employers. Issue #441.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the active convocatorias, 12 a page, 3 s apart, 20 pages unless told otherwise")
    l_.add_argument("--pages", type=int, default=20)
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one convocatoria in full — the sections, the salary block with its period, the closing date")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
