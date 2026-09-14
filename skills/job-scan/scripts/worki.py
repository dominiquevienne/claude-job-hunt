#!/usr/bin/env python3
"""Worki (`www.worki.sk`, ex-istp.sk) — the Slovak board the old public labour-market guide redirects to: a server-rendered listing that states its count («Zobraziť 623 pracovných ponúk» on 2026-09-14) and pages at `/ponuka-prace/<n>`, twenty cards a page; a jobs sitemap of the same ids; the ad a labelled page — facts, sections, the employer's public record — **cut at «Kontaktná osoba», which is never read; the texts scrubbed**. The state's portal (`sluzbyzamestnanosti.md`) republishes 537 of the 623 (`zdrojPonuky=WRK`), title/employer/place/salary only; the direct read adds the 86 others and every ad's body. Issue #344.

  worki.py list [--limit N] [--pages N]     the listing walked page by page (20 a page; 32 pages for 623 — 2 s apart)
  worki.py sitemap [--limit N]              every /ponuka-prace/<employer>/<id>-<slug> row of sitemap.jobs.xml (2 requests)
  worki.py ad --url <https://www.worki.sk/ponuka-prace/<employer>/<id>-<slug>>

THE RULES (200 B): `*` reads `Disallow: /organization`, `/admin`, `/*/pracovna-ponuka/*/poslat-zivotopis*`,
`/pracovna-ponuka/*/poslat-zivotopis*`, `/nelmio/csp/report*`; `Sitemap: /sitemap.xml`. No
Crawl-delay; 2 s is ours. The refused paths are the employer back-office, the CV-sending form
and a CSP endpoint — none of them is a page this script reads; `request()` refuses them anyway.

THE LIST. `/ponuka-prace` (200, ~342 KB) is server-rendered: the filter button prints the
site's own count («Zobraziť 623 pracovných ponúk»), twenty cards follow in `#offers`, the pager
links `/ponuka-prace/2` … `/ponuka-prace/32`. A card: the ad link (`/ponuka-prace/<employer-slug>/
<id>-<slug>`, `?useFilter=1` dropped), a «TOP» badge, the title, the employer with its
`/zoznam-zamestnavatelov/<id>-<slug>` link, the place line, the contract line («Práca na
živnosť», «Trvalý pracovný pomer» …), the salary line («od 150 € do 2 000 € za mesiac» — a
floor, a ceiling, a period, as printed) and the freshness line («Aktualizované dnes / včera /
pred N dňami»). The root page's «1 818 pracovných ponúk» is another figure (positions, or a
marketing count) and is not read. THE SITEMAP. `/sitemap.xml` is an index of three files;
`sitemap.jobs.xml` names 623 ads with a `lastmod` that is the file's generation time (06:00
local, every row) — not a date of the ad, never emitted as one.

THE AD. `/ponuka-prace/<employer>/<id>-<slug>` (200, ~239 KB): no JSON-LD. The header carries
the employer and the `<h1>`; a facts block («Miesto výkonu práce» with the street address and
the notes, «Dátum nástupu», «Dátum pridania ponuky» — «11. 6. 2026 (aktualizácia 14. 9. 2026)»,
«Druh pracovného pomeru», «Mzda (v hrubom)» with a note, «Počet voľných pracovných miest»);
then «Údaje o pracovnom mieste» — `<h4>` sections (Náplň práce, Informácie o výberovom
procese, Pracovný režim, Pracovné miesto vhodné aj pre, Ponúkané výhody); «Požiadavky na
zamestnanca» — sections (Požadované vzdelanie, Dĺžka praxe, Digitálne zručnosti, Vodičské
oprávnenie, Všeobecné spôsobilosti a predpoklady, Ďalšie požiadavky); «Údaje o
zamestnávateľovi» — Obchodné meno, IČO, Adresa, Internetová stránka, Charakteristika
spoločnosti (the employer's public register record); **and «Kontaktná osoba» — a name and a
telephone — where the page is cut before reading; every text scrubbed of e-mail addresses
and Slovak telephone numbers (the selection-process text on the ad read carried the
employer's own e-mail); `contacts_withheld` on every record; the CV form (`poslat-zivotopis`,
refused in writing) never touched.**

Measured 2026-09-14 04:2x UTC by the declared client, the guard on the exact path: the root
174 816 B («1818»); `/ponuka-prace` 342 025 B, «623», 20 cards, 32 pages; `sitemap.jobs.xml`
623 rows; the ad 239 358 B; the state's `zdrojPonuky=WRK` 537 rows, all 537 in the 623.
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

HOST = "www.worki.sk"
LIST = f"https://{HOST}/ponuka-prace"
SITEMAP_INDEX = f"https://{HOST}/sitemap.xml"
PER_PAGE = 20

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+421[\s ]?|00421[\s ]?|0)(?:\d[\s ]?){8,9}\d(?!\d)")
AD_RE = re.compile(r"^/ponuka-prace/([^/]+)/(\d+)-([^/?]+)/?$")
REFUSED_RE = re.compile(r"^/(?:organization|admin)(?:/|$)|/poslat-zivotopis|^/nelmio/csp/report")
COUNT_RE = re.compile(r"Zobraziť\s+(\d[\d ]*)\s+pracovn")
CARD_SPLIT = '<div class="bg-white shadow shadow-lg-hover'
CARD_LINK_RE = re.compile(r'<h2[^>]*>\s*<a href="(https://www\.worki\.sk/ponuka-prace/[^/"]+/(\d+)-[^"?]+)(?:\?[^"]*)?"[^>]*>(.*?)</a>', re.S)
EMPLOYER_RE = re.compile(r'<h3[^>]*>\s*<a href="https://www\.worki\.sk/zoznam-zamestnavatelov/(\d+)-[^"]*"[^>]*>(.*?)</a>', re.S)
ICON_RE = re.compile(r'<i class="fal fa-([a-z-]+) w-1\.5rem"></i></div>\s*<div class="flex-grow-1[^"]*">(.*?)</div>', re.S)
SITEMAP_ROW_RE = re.compile(r"<url><loc>([^<]+)</loc>(?:<lastmod>([^<]+)</lastmod>)?", re.S)
FACT_RE = re.compile(r'<div class="fw-light">(.*?)</div>\s*<div class="fw-semibold">(.*?)</div>\s*</div>\s*</div>\s*</div>', re.S)
SECTION_RE = re.compile(r'<h4 class="h6[^"]*">(.*?)</h4>(.*?)(?=<h4 class="h6|<h2 class="h5|</section>)', re.S)
CUT_MARKERS = ("Kontaktná osoba", "Podobné pracovné ponuky")

_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written; 2 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[worki] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    if REFUSED_RE.search(urllib.parse.urlsplit(url).path):
        die(f"{url}: refused in writing (the back-office, the CV form, the CSP endpoint) — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9", "Accept-Language": "sk"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    markup = re.sub(r"<!--.*?-->", "", markup or "", flags=re.S)
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup)
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t ​]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def num(s):
    """«2 000» / «2&nbsp;000» → 2000; None when nothing numeric."""
    d = re.sub(r"[^\d,]", "", s or "").replace(",", ".")
    if not re.fullmatch(r"\d+(?:\.\d+)?", d):
        return None
    v = float(d)
    return int(v) if v.is_integer() else v


CUR_RE = r"(€|EUR|CZK|Kč|USD|\$|GBP|£)"
CURRENCIES = {"€": "EUR", "EUR": "EUR", "CZK": "CZK", "Kč": "CZK", "USD": "USD", "$": "USD", "GBP": "GBP", "£": "GBP"}


def salary_of(line):
    """«od 150 € do 2 000 € za mesiac» → (150, 2000, "EUR", "mesiac", stated, text); «1 800 € za mesiac» → the one figure as floor and ceiling; «od 50 000 CZK …» keeps its currency; a missing part is None; `stated` when a figure and a period are both printed."""
    t = re.sub(r"\s+", " ", htmlmod.unescape(line or "")).strip()
    lo = re.search(r"od\s*([\d ]+(?:,\d+)?)\s*" + CUR_RE, t)
    hi = re.search(r"do\s*([\d ]+(?:,\d+)?)\s*" + CUR_RE, t)
    per = re.search(r"za\s+([a-záčďéíľňóôŕšťúýž]+)", t)
    smin, smax = (num(lo.group(1)) if lo else None), (num(hi.group(1)) if hi else None)
    cur_sym = (lo or hi).group(2) if (lo or hi) else None
    if smin is None and smax is None:
        one = re.search(r"(?<![\d ])([\d ]+(?:,\d+)?)\s*" + CUR_RE, t)   # «1 800 € za mesiac» — one figure, the amount itself
        smin = smax = num(one.group(1)) if one else None
        cur_sym = one.group(2) if one else None
    unit = per.group(1) if per else None
    cur = CURRENCIES.get(cur_sym) if (smin is not None or smax is not None) else None
    return smin, smax, cur, unit, bool(unit) and (smin is not None or smax is not None), t or None


def stated(body):
    m = COUNT_RE.search(body or "")
    return num(m.group(1)) if m else None


def cards(body):
    out = []
    start = (body or "").find('id="offers"')
    if start < 0:
        return out
    for chunk in body[start:].split(CARD_SPLIT)[1:]:
        m = CARD_LINK_RE.search(chunk)
        if not m:
            continue
        url, jid, title_html = m.groups()
        emp = EMPLOYER_RE.search(chunk)
        lines = {k: text(v) for k, v in ICON_RE.findall(chunk)}
        smin, smax, cur, unit, st, sal_text = salary_of(lines.get("coins"))
        out.append({
            "source": "worki", "country": "SK", "ledger_id": f"worki:{jid}", "id": jid, "url": url,
            "title": text(re.sub(r"<span[^>]*>.*?</span>", "", title_html, flags=re.S)), "top": "badge" in title_html,
            "company": text(emp.group(2)) if emp else None, "company_id": emp.group(1) if emp else None,
            "place": lines.get("location-dot") or None, "contract": lines.get("file-contract") or None,
            "salary_min": smin, "salary_max": smax, "salary_currency": cur, "salary_unit": unit, "salary_unit_stated": st, "salary_text": sal_text,
            "updated_text": lines.get("calendar-days") or None,
            "language": "sk", "contacts_withheld": True,
        })
    return out


def cmd_list(a):
    rows, seen, page, total, first_ids = [], set(), 1, None, None
    while True:
        url = LIST if page == 1 else f"{LIST}/{page}"
        code, body = request(url)
        if code == 404 and page > 1:
            break
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if page == 1:
            total = stated(body)
            if total is None:
                die(f"{url}: 200 and no «Zobraziť N pracovných ponúk» in the page — the template changed; not an empty market", EXIT_PARTIAL)
        cs = cards(body)
        if not cs:
            if page == 1:
                die(f"{url}: 200 and not one card in #offers — the template changed; not an empty market", EXIT_PARTIAL)
            break
        ids = [c["id"] for c in cs]
        if page == 1:
            first_ids = ids
        elif ids == first_ids:
            die(f"{url}: page {page} serves page 1's cards again — the pager changed; stopping rather than doubling", EXIT_PARTIAL)
        new = 0
        for c in cs:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            rows.append(c)
            new += 1
            if a.limit and len(rows) >= a.limit:
                break
        if a.limit and len(rows) >= a.limit:
            break
        if new == 0 or len(cs) < PER_PAGE or (a.pages and page >= a.pages) or (total is not None and len(rows) >= total):
            break
        page += 1
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    n = len(rows)
    if (a.limit and a.limit < total) or (a.pages and n < total):
        note(f"{th(n)} emitted of the {th(total)} the site states on {LIST} ({page} page(s) read) — walked by request (--limit/--pages), not a shortfall.")
    else:
        verdict = "equal" if n == total else (f"{th(total - n)} short" if n < total else f"{th(n - total)} more emitted")
        note(f"{th(n)} emitted in {page} page(s), the site states {th(total)} — {verdict}.")
    note("the card's own lines: place, contract, salary as printed, freshness; the ad's «Kontaktná osoba» is never read.")


def sitemap_rows():
    code, body = request(SITEMAP_INDEX)
    if code != 200:
        die(f"{SITEMAP_INDEX}: HTTP {code}", EXIT_PARTIAL)
    m = re.search(r"<loc>(https://www\.worki\.sk/sitemap\.jobs\.xml)</loc>", body)
    if not m:
        die(f"{SITEMAP_INDEX}: 200 without sitemap.jobs.xml in the index — the shape changed", EXIT_PARTIAL)
    code, body = request(m.group(1))
    if code != 200:
        die(f"{m.group(1)}: HTTP {code}", EXIT_PARTIAL)
    rows, seen, other = [], set(), 0
    for loc, lastmod in SITEMAP_ROW_RE.findall(body):
        mm = AD_RE.match(urllib.parse.urlsplit(loc).path)
        if not mm:
            other += 1
            continue
        if mm.group(2) in seen:
            continue
        seen.add(mm.group(2))
        rows.append({"source": "worki", "country": "SK", "ledger_id": f"worki:{mm.group(2)}", "id": mm.group(2), "url": loc, "employer_slug": mm.group(1), "slug": mm.group(3), "file_generated": (lastmod or "")[:10] or None, "language": "sk", "contacts_withheld": True})
    if not rows:
        die(f"{m.group(1)}: 200 and not one /ponuka-prace/<employer>/<id>- row among {th(other)} — the shape changed", EXIT_PARTIAL)
    return rows, other


def cmd_sitemap(a):
    rows, other = sitemap_rows()
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{th(len(rows))} ad row(s) in sitemap.jobs.xml ({th(other)} other) — the file's lastmod is its generation time, not a date of the ad; `list` prints the site's stated count.")
    if a.limit and a.limit < len(rows):
        note(f"{th(len(emitted))} emitted of the {th(len(rows))} — bounded by --limit.")


def cut(body):
    """The page up to the first contact / related-offers marker — «Kontaktná osoba» is never read."""
    end = len(body)
    for mk in CUT_MARKERS:
        i = body.find(mk)
        if i >= 0:
            end = min(end, i)
    return body[:end]


def record(body, jid, url):
    body = cut(body)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    emp = re.search(r'<a href="https://www\.worki\.sk/zoznam-zamestnavatelov/(\d+)-[^"]*"[^>]*class="link-primary[^"]*"[^>]*>(.*?)</a>', body, re.S)
    if not h1 and not emp:
        return None
    facts = {text(k): text(v) for k, v in FACT_RE.findall(body)}
    sections = {}
    for k, v in SECTION_RE.findall(body):
        key = text(k)
        if key and key not in sections:
            sections[key] = scrub(text(v))
    sal = facts.get("Mzda (v hrubom)") or ""
    smin, smax, cur, unit, st, sal_text = salary_of(" ".join(l for l in sal.split("\n") if "€" in l))   # the figure lines; the site's note below them is kept in salary_text
    added = re.match(r"\s*(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})", facts.get("Dátum pridania ponuky") or "")
    upd = re.search(r"aktualizácia\s+(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})", facts.get("Dátum pridania ponuky") or "")
    iso = lambda m: f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}" if m else None
    positions = facts.get("Počet voľných pracovných miest")
    place_lines = (facts.get("Miesto výkonu práce") or "").split("\n")
    return {
        "source": "worki", "country": "SK", "ledger_id": f"worki:{jid}", "id": jid, "url": url,
        "title": text(h1.group(1)) if h1 else None,
        "company": text(emp.group(2)) if emp else sections.get("Obchodné meno"), "company_id": emp.group(1) if emp else None,
        "company_reg_no": sections.get("IČO"), "company_address": sections.get("Adresa"), "company_site": sections.get("Internetová stránka"), "company_text": sections.get("Charakteristika spoločnosti"),
        "place": place_lines[0] or None, "place_notes": [p for p in place_lines[1:] if p] or None,
        "start_date": facts.get("Dátum nástupu") or None,
        "posted": iso(added), "updated": iso(upd), "contract": facts.get("Druh pracovného pomeru") or None,
        "salary_min": smin, "salary_max": smax, "salary_currency": cur, "salary_unit": unit, "salary_unit_stated": st, "salary_text": scrub(sal.replace("\xa0", " ")) or None,
        "positions": int(positions) if positions and positions.isdigit() else positions,
        "description": sections.get("Náplň práce"), "selection_process": sections.get("Informácie o výberovom procese"),
        "work_regime": sections.get("Pracovný režim"), "suitable_for": sections.get("Pracovné miesto vhodné aj pre"), "benefits": sections.get("Ponúkané výhody"),
        "education": sections.get("Požadované vzdelanie"), "experience": sections.get("Dĺžka praxe"), "digital_skills": sections.get("Digitálne zručnosti"), "driving_licence": sections.get("Vodičské oprávnenie"),
        "competences": sections.get("Všeobecné spôsobilosti a predpoklady"), "other_requirements": sections.get("Ďalšie požiadavky"),
        # «Kontaktná osoba» — a name and a telephone — is cut before reading; the CV form is never touched
        "language": "sk", "contacts_withheld": True,
    }


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc not in (HOST, "worki.sk") or not m:
        die(f"{a.url}: not a job address (https://{HOST}/ponuka-prace/<employer>/<id>-<slug>)")
    url = f"https://{HOST}{parts.path.rstrip('/')}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    rec = record(body, m.group(2), url)
    if rec is None:
        die(f"{url}: 200 without the ad's header — the template changed", EXIT_PARTIAL)
    print(json.dumps(rec, ensure_ascii=False))
    note(f"{url}: read up to «Kontaktná osoba», which is never read; texts scrubbed; the CV form never touched.")


def main():
    p = argparse.ArgumentParser(description="Worki — the listing's own count beside every walk, twenty cards a page; the ad cut before its contact person. Issue #344.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the listing walked page by page")
    l_.add_argument("--limit", type=int)
    l_.add_argument("--pages", type=int)
    l_.set_defaults(fn=cmd_list)
    s_ = sub.add_parser("sitemap", help="every ad row of sitemap.jobs.xml")
    s_.add_argument("--limit", type=int)
    s_.set_defaults(fn=cmd_sitemap)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
