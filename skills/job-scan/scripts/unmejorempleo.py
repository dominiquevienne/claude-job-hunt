#!/usr/bin/env python3
"""Un Mejor Empleo — one PHP template, one front per country; `--host` names the front, the front names the country; «Empleos 1 a 20 de 1,519» is the count the page states. Issue #427.

  unmejorempleo.py list --host www.unmejorempleo.com.ve [--pages N | --all] [--limit N]
  unmejorempleo.py ad --url <https://<front>/empleo-en_<slug>-<id>.html>
  unmejorempleo.py hosts

THE ROUTE IS THE LISTING PAGE. `/empleos?np=<p>` (p from 0) serves twenty
cards a page — `<div class="item-normal">` / `item-destacado` — each with
the ad's link (`empleo-en_<region>_<slug>-<id>.html`), the title, «Ubicación:
X | Estado: Y», an excerpt, «Publicación: dd/mm/yyyy - Salario: <text>».
The header states **«Empleos 1 a 20 de 1,519»** and the masthead
«Tenemos 1,519 ofertas»: the first is the witness. The pager's own links
carry `t=<total>` — a client-supplied echo this file never sends; `np`
alone pages the same twenty. **No key, no cookie, no browser.** Plain HTML:
the page's JSON-LD is malformed (raw newlines inside a string) and is not
read.

THE AD PAGE is `<h4>Label</h4> value` pairs inside `article.trabajo`:
Empresa (a link to the employer's page), Descripción de la Empresa,
Estado, Localidad, Tipo de Contratación, Descripción de la Plaza, Mínimo
Nivel Académico / de Inglés / Experiencia. No date, no salary on the ad
page — those are the card's. The employer's page (`empresa-empleo_en_…`)
is not read.

MEASURED 2026-09-13 23:5x (VE) and 2026-09-14 00:19–00:21 UTC (the
rest), one listing page per front, the declared client, guard on the
exact path (`/robots.txt` on the Venezuelan front: `User-agent: * /
Crawl-delay: 4`, no `Disallow` — the delay is honoured by `Pace`, 5 s is
ours). The fronts are the fourteen the Venezuelan root names in its
«Cambiar país» list; **thirteen served their listing with a stated
count, and `www.unmejorempleo.com` — the chooser — answers 404 on
`/empleos`** and is not a front:

    www.unmejorempleo.com.ve  VE  1 519     www.unmejorempleo.com.gt  GT  2 466
    ar.unmejorempleo.com      AR    224     www.unmejorempleo.com.mx  MX    741
    hn.unmejorempleo.com      HN    422     www.unmejorempleo.com.pa  PA    160
    www.unmejorempleo.cl      CL    214     www.unmejorempleo.com.pe  PE  1 017
    www.unmejorempleo.co.cr   CR    380     www.unmejorempleo.com.sv  SV  1 590
    www.unmejorempleo.com.co  CO  1 727     www.unmejorempleo.es      ES    449
    www.unmejorempleo.com.ec  EC    807

Twenty cards a page on every front; the biggest walk (Guatemala, 124
pages) is ten minutes at 5 s. The default walk is bounded (`--pages 10`,
200 rows) and says so; `--all` walks to the count and is compared —
«N emitted over P page(s), site states N — equal», exit 6 on a gap.

WHAT IS WITHHELD. Addresses and phone numbers in the prose are replaced
(`[e-mail withheld]`, `[phone withheld]`, nine digits or more); the
front's own `candidatos@` / `empresas@` addresses are the operator's, not
a recruiter's, and are not in any field this file emits. Salary is the
card's text («A convenir», «Pago por comisiones», «----------» → null),
never parsed into a number.
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

# front -> country — a front enters only once its own listing was read (the counts are in the docstring)
HOSTS = {
    "www.unmejorempleo.com.ve": "VE", "ar.unmejorempleo.com": "AR", "hn.unmejorempleo.com": "HN", "www.unmejorempleo.cl": "CL",
    "www.unmejorempleo.co.cr": "CR", "www.unmejorempleo.com.co": "CO", "www.unmejorempleo.com.ec": "EC", "www.unmejorempleo.com.gt": "GT",
    "www.unmejorempleo.com.mx": "MX", "www.unmejorempleo.com.pa": "PA", "www.unmejorempleo.com.pe": "PE", "www.unmejorempleo.com.sv": "SV",
    "www.unmejorempleo.es": "ES",
}   # www.unmejorempleo.com is the country chooser: `/empleos` answers 404 there — not a front

PAGE_SIZE = 20
DEFAULT_PAGES = 10
AD_RE = re.compile(r"^https?://([a-z0-9.-]+)/(empleo-en_[^/?#]+-(\d+)\.html)$")
CARD_RE = re.compile(r'<div class="item-(?:normal|destacado)(?: item-last)?">(.*?)</ul>\s*</div>', re.S)   # the twentieth card is `item-normal item-last`
LINK_RE = re.compile(r'<h3[^>]*>\s*<a\s+href="(empleo-en_[^"]+-(\d+)\.html)"\s*>(.*?)<i\b', re.S)
LOC_RE = re.compile(r'<li class="text-primary">\s*Ubicaci(?:&oacute;|ó)n:\s*(.*?)\s*\|\s*Estado\s*:\s*(.*?)\s*</li>', re.S)
EXC_RE = re.compile(r'<li>(?!\s*<)(.*?)</li>', re.S)
DATE_RE = re.compile(r'Publicaci(?:&oacute;|ó)n:\s*(\d{2})/(\d{2})/(\d{4})\s*-\s*Salario:\s*(.*?)\s*</li>', re.S)
STATED_RE = re.compile(r'Empleos\s+\d[\d,.]*\s+a\s+\d[\d,.]*\s+de\s+([\d,.]+)')
TENEMOS_RE = re.compile(r'Tenemos\s*<strong>\s*([\d,.]+)\s*ofertas')
H4_RE = re.compile(r'<h4[^>]*>(.*?)</h4>(.*?)(?=<h4|<div class="row">\s*<div class="col-xs-12 aplicar)', re.S)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\d[\d\s().-]{6,}\d(?!\w)")
NO_SALARY = {"", "-", "--", "----------", "-----", "n/a", "no especificado"}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[unmejorempleo] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def front(host):
    if host not in HOSTS:
        die(f"{host}: not a front read by this adapter — `hosts` lists the {len(HOSTS)} read; a new one is measured, not assumed.")
    return HOSTS[host]


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    """One GET, gated on the exact path, paced per host by the rules' `Crawl-delay` or our own 5 s — `(code, body)`."""
    a = gate(url)
    host = urllib.parse.urlsplit(url).netloc
    _PACES.setdefault(host, Pace(host, own=5.0)).wait()   # Pace reads the host's own Crawl-delay (4 s here); 5 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def clean(s):
    """Tags out, entities decoded, whitespace folded."""
    s = re.sub(r"<(script|style|ins)\b.*?</\1>", "", s or "", flags=re.S | re.I)   # an ad slot sits inside the Localidad value
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def redact(s):
    s = EMAIL_RE.sub("[e-mail withheld]", s or "")
    return PHONE_RE.sub(lambda m: "[phone withheld]" if sum(c.isdigit() for c in m.group(0)) >= 9 else m.group(0), s)


def num(s):
    return int(re.sub(r"[^\d]", "", s or "") or 0)


def stated(body):
    m = STATED_RE.search(body or "") or TENEMOS_RE.search(body or "")
    return num(m.group(1)) if m else None


def salary(text):
    t = clean(text)
    return None if t.lower() in NO_SALARY else redact(t)


def cards(body, host, country):
    out = []
    for blk in CARD_RE.findall(body or ""):
        m = LINK_RE.search(blk)
        if not m:
            continue
        path, ident, title = m.groups()
        loc = LOC_RE.search(blk)
        d = DATE_RE.search(blk)
        exc = [x for x in EXC_RE.findall(blk) if "Publicaci" not in x and "Ubicaci" not in x]
        out.append({
            "source": "unmejorempleo", "country": country, "host": host, "ledger_id": f"unmejorempleo:{host}:{ident}", "id": ident,
            "url": f"https://{host}/{path}", "title": redact(clean(title)) or None,
            "location": redact(clean(loc.group(1))) or None if loc else None, "region": clean(loc.group(2)) or None if loc else None,
            "posted": f"{d.group(3)}-{d.group(2)}-{d.group(1)}" if d else None,
            "salary_text": salary(d.group(4)) if d else None,
            "summary": redact(clean(exc[0])) or None if exc else None,
            "featured": True if "Oferta destacada" in blk[:200] else None,
        })
    return out


def cmd_hosts(a):
    for h, c in HOSTS.items():
        print(f"{h}\t{c}")


def cmd_list(a):
    country = front(a.host)
    if a.pages is not None and a.pages < 1:
        die("--pages must be at least 1 (or use --all).")
    limit_pages = None if a.all else (a.pages or DEFAULT_PAGES)
    seen, emitted, page, site = set(), 0, 0, None
    while True:
        url = f"https://{a.host}/empleos" + (f"?np={page}" if page else "")
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if site is None:
            site = stated(body)
            if site is None:
                die(f"{url}: the page states no count — neither «Empleos A a B de N» nor «Tenemos N ofertas» ({len(body)} characters).", EXIT_PARTIAL)
        rows = cards(body, a.host, country)
        page += 1
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
            note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} ({country}) — walk bounded by request (--limit), not compared.")
            return
        if not rows or new == 0 or emitted >= site:
            break
        if limit_pages is not None and page >= limit_pages:
            note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} ({country}) — walk bounded by request (--pages {limit_pages}; --all walks to the count), not compared.")
            return
    if emitted == site:
        note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} ({country}) — equal.")
    else:
        note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} ({country}) — {th(abs(site - emitted))} {'short' if emitted < site else 'over'}.")
        sys.exit(EXIT_PARTIAL)


LABELS = {
    "empresa": "employer", "descripcion de la empresa": "employer_description", "estado": "region", "localidad": "location",
    "tipo de contratacion": "contract", "descripcion de la plaza": "description", "minimo nivel academico requerido": "education",
    "minimo nivel de ingles requerido": "english", "minima experiencia laboral requerida": "experience", "salario": "salary_text",
}


def fold(s):
    s = clean(s).lower()
    return "".join(c for c in s.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n") if c.isalnum() or c == " ").strip()


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an ad URL of an Un Mejor Empleo front (https://<front>/empleo-en_<slug>-<id>.html).")
    host, path, ident = m.groups()
    country = front(host)
    code, body = request(a.url.strip())
    if code == 404:
        die(f"{a.url}: HTTP 404 — the ad is gone.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_PARTIAL)
    art = re.search(r"<article class='trabajo'>(.*?)</article>", body, re.S) or re.search(r'<article class="trabajo">(.*?)</article>', body, re.S)
    if not art:
        die(f"{a.url}: no `article.trabajo` on the page — gone, or not the template this file reads.", EXIT_GONE)
    h1 = re.search(r"<h1>(.*?)</h1>", body, re.S)
    r = {"source": "unmejorempleo", "country": country, "host": host, "ledger_id": f"unmejorempleo:{host}:{ident}", "id": ident,
         "url": a.url.strip(), "title": redact(clean(h1.group(1))) or None if h1 else None}
    for label, value in H4_RE.findall(art.group(1)):
        key = LABELS.get(fold(label))
        if not key:
            continue
        v = redact(clean(value))
        r[key] = (salary(v) if key == "salary_text" else v) or None
    if not r.get("description") and not r.get("employer"):
        die(f"{a.url}: the article carries neither a description nor an employer — not the template this file reads.", EXIT_PARTIAL)
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="walk one front's listing")
    l.add_argument("--host", required=True, help="the front, e.g. www.unmejorempleo.com.ve — see `hosts`")
    g = l.add_mutually_exclusive_group()
    g.add_argument("--pages", type=int, default=None, help=f"pages to read (default {DEFAULT_PAGES}, bounded and said so)")
    g.add_argument("--all", action="store_true", help="walk to the count the site states, and compare")
    l.add_argument("--limit", type=int, default=0, help="stop after N rows (bounded, not compared)")
    l.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one ad by its public URL; the front is read from the URL")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    h = sub.add_parser("hosts", help="the fronts this file reads")
    h.set_defaults(fn=cmd_hosts)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
