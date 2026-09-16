#!/usr/bin/env python3
"""Empleos.hn (`empleos.hn`) — the Red de Desarrollo Sostenible's free Honduran board, a Drupal site: the advanced search `/busqueda-avanzada?page=N` (0-based) serves sixteen cards a page on the server with a pager to its last page, the site prints no total, and each ad carries a JobPosting beside labelled fields; the pager's reach printed beside every walk; the application e-mail never emitted. Issue #439.

  empleos_hn.py list [--pages N]     the cards of /busqueda-avanzada?page=0 … until the pager's last page (20 pages on the day, 2 s apart)
  empleos_hn.py ad --url <https://empleos.hn/jobs/<slug>>

THE RULES. Drupal's file for `*`: the engine's directories, `/admin/`, `/search/`, `/node/add/`,
`/user/login`, `/user/register` … refused; no Crawl-delay, 2 s is ours. `/busqueda-avanzada` is a
Drupal view, not `/search/`; the adapter never sends `/search/`, `/user/`, `/register_asp`,
`/register_emp` (refused before the gate).

THE LIST. The root and `/empleos` show six cards and no pager; `/busqueda-avanzada` (200, ~66 KB)
serves sixteen `tarjeta` cards a page — the title in `nombre-empresa` (the class names are swapped
on the site: `nombre-empresa` holds the TITLE, `nombre-posicion` the EMPLOYER), the department in
`ubicacion`, «Fecha Max. Postulación» as a `<time datetime>`, a «Ver Más» link to `/jobs/<slug>` —
and a Drupal pager `?page=0 … 19` (the last page is read from the pager's largest number). The
site prints no total: `list` prints emitted against the pager's reach (pages × 16 is a bound) and
says so. The walk dedups by slug, dies (exit 6) on a 200 without a card or on page 0 served again.
THE AD. `/jobs/<slug>` (200, ~52 KB) carries a JobPosting — title, datePosted, validThrough,
employmentType («Indefinido»), hiringOrganization (name, @id), jobLocation (locality = the
department, HN), a baseSalary skeleton (HNL, MONTH, no value) — beside Drupal fields: «Nivel de
experiencia», «Número de Vacantes», «Modalidad», «Género», «Vehículo o Licencia», «Categoría»,
«Departamento», «Tipo de Contrato», «Fecha max. de Postulación», «Descripción» (HTML), and
«Correo para aplicar:» — the employer's application address, Cloudflare-obfuscated on the page.
**The application address is never emitted, not even obfuscated; the description is scrubbed of
e-mail addresses and Honduran telephone numbers; `contacts_withheld` on every record.**

Measured 2026-09-16 06:25–06:27 UTC by the declared client, the guard on the exact path: robots 200
(2 027 B); `/` 83 125 B, 6 cards; `/busqueda-avanzada` 65 830 B, 16 cards, pager to 19; `?page=3`
16 cards; `/sitemap.xml` 404; the ad 52 269 B with its JobPosting.
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
from _ldjson import one, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "empleos.hn"
LIST = f"https://{HOST}/busqueda-avanzada"
PER_PAGE = 16
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+?504[\s\-]?)?[2389]\d{3}[\s\-]?\d{4}(?!\d)")   # Honduran 8-digit numbers (2 landline, 3/8/9 mobile), with or without +504
AD_RE = re.compile(r"^/jobs/([a-z0-9\-]+)/?$")
REFUSED_RE = re.compile(r"^/(?:admin|search|node/add|user|register_asp|register_emp|comment/reply|filter/tips|media/oembed|cdn-cgi)(?:/|$)")
CARD_RE = re.compile(r'<div class="tarjeta">(.*?)<a href="(https://empleos\.hn/jobs/[^"]+|/jobs/[^"]+)" class="boton-ver-mas">', re.S)
TITLE_RE = re.compile(r'<div class="nombre-empresa">(.*?)</div>', re.S)
EMPLOYER_RE = re.compile(r'<div class="nombre-posicion">(.*?)<br>', re.S)
PLACE_RE = re.compile(r'<div class="ubicacion">(?:<span[^>]*>[^<]*</span>)?\s*([^<]+?)\s*</div>', re.S)
TIME_RE = re.compile(r'<time datetime="([^"]+)"')
PAGE_RE = re.compile(r'href="\?page=(\d+)"')
FIELD_RE = re.compile(r'<div class="field__label">\s*([^<]+?)\s*</div>\s*<div class="field__item">(.*?)</div>\s*</div>', re.S)

_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written; 2 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[empleos_hn] {msg}", file=sys.stderr)


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
        die(f"{url}: refused in writing to `*` (the search, the accounts) or the e-mail protection — never sent", EXIT_REFUSED)
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


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t))
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def slug_of(href):
    m = AD_RE.match(urllib.parse.urlsplit(href).path)
    return m.group(1) if m else None


def cards(body):
    out = []
    for inner, href in CARD_RE.findall(body):
        slug = slug_of(href)
        if not slug:
            continue
        t = TITLE_RE.search(inner)
        e = EMPLOYER_RE.search(inner)
        p = PLACE_RE.search(inner)
        tm = TIME_RE.search(inner)
        out.append({
            "source": "empleos_hn", "country": "HN", "ledger_id": f"empleos_hn:{slug}", "id": slug, "url": f"https://{HOST}/jobs/{slug}",
            "title": text(t.group(1)) if t else None, "company": text(e.group(1)) if e else None, "department": text(p.group(1)) if p else None,
            "valid_through": (tm.group(1) or "")[:10] or None if tm else None,
            "contacts_withheld": True, "language": "es",
        })
    return out


def cmd_list(a):
    out, seen, first_ids, pages, last = [], set(), None, 0, 0
    n = 0
    while True:
        url = LIST if n == 0 else f"{LIST}?page={n}"
        code, body = request(url)
        if code == 404:
            break
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if n == 0:
            last = max((int(x) for x in PAGE_RE.findall(body)), default=0)
        cs = cards(body)
        if not cs:
            die(f"{url}: 200 and no card — the template changed; not an empty page", EXIT_PARTIAL)
        ids = [c["id"] for c in cs]
        if first_ids is None:
            first_ids = ids
        elif ids == first_ids:
            die(f"{url}: the same cards as page 0 — the pager is not honoured; stopped", EXIT_PARTIAL)
        new = 0
        for c in cs:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            out.append(c)
            new += 1
        pages += 1
        if new == 0 or n >= last or (a.pages and pages >= a.pages):
            break
        n += 1
    for c in out:
        print(json.dumps(c, ensure_ascii=False))
    emitted = len(out)
    if a.pages and pages >= a.pages and n < last:
        note(f"{th(emitted)} emitted from {pages} page(s) of the {last + 1} the pager names (the site prints no total; {last + 1} × {PER_PAGE} = {th((last + 1) * PER_PAGE)} is the bound) — walked by request (--pages), not a shortfall.")
    else:
        note(f"{th(emitted)} emitted from {pages} page(s), the pager's {last + 1} walked to the last; the site prints no total — the walk is the count, {th((last + 1) * PER_PAGE)} its bound.")
    note("cards only — `ad --url` reads a JobPosting and the ad's fields; the application address never emitted.")


def record(body, slug, url):
    jp = (postings(body) or [None])[-1]
    fields = {text(k): v for k, v in FIELD_RE.findall(body)}
    if jp is None and "Descripción" not in fields:
        return None
    jp = jp or {}
    org = one(jp.get("hiringOrganization"))
    addr = one(one(jp.get("jobLocation")).get("address"))
    sal = one(jp.get("baseSalary"))
    val = one(sal.get("value")) if sal else {}
    cat = text(fields.get("Categoría", ""))
    return {
        "source": "empleos_hn", "country": "HN", "ledger_id": f"empleos_hn:{slug}", "id": slug, "url": url,
        "title": htmlmod.unescape(jp.get("title") or "").strip() or None,
        "company": (org.get("name") or "").strip() or None, "company_id": org.get("@id") or None,
        "employment_type": jp.get("employmentType") or text(fields.get("Tipo de Contrato", "")),
        "department": addr.get("addressLocality") or text(fields.get("Departamento", "")), "address_country": addr.get("addressCountry") or None,
        "salary_currency": sal.get("currency") or None, "salary_unit": val.get("unitText") or None, "salary": val.get("value") or None,
        "posted": (jp.get("datePosted") or "")[:10] or None, "valid_through": (jp.get("validThrough") or "")[:10] or None,
        "experience": text(fields.get("Nivel de experiencia", "")), "openings": text(fields.get("Número de Vacantes", "")), "modality": text(fields.get("Modalidad", "")),
        "gender": text(fields.get("Género", "")), "vehicle": text(fields.get("Vehículo o Licencia", "")), "category": cat,
        "description": scrub(text(fields.get("Descripción", ""))),
        "contacts_withheld": True, "language": "es",
    }


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc not in (HOST, "www." + HOST) or not m:
        die(f"{a.url}: not a job address (https://{HOST}/jobs/<slug>)")
    url = f"https://{HOST}/jobs/{m.group(1)}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    rec = record(body, m.group(1), url)
    if rec is None:
        die(f"{url}: 200 without a JobPosting and without the ad's fields — the template changed", EXIT_PARTIAL)
    print(json.dumps(rec, ensure_ascii=False))
    note(f"{url}: read from its JobPosting and its fields; the application address never emitted; description scrubbed.")


def main():
    p = argparse.ArgumentParser(description="Empleos.hn — the advanced search's cards walked to the pager's last page, each ad from its JobPosting and fields; the application address never emitted. Issue #439.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="/busqueda-avanzada?page=0 … to the pager's last page, 2 s apart")
    l_.add_argument("--pages", type=int, help="stop after N pages (a bound, printed as such)")
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
