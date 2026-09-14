#!/usr/bin/env python3
"""Buscojobs — one platform, one Next.js build, twenty-one countries on twenty-two hosts; `--host` names the front, the front names the country. Issue #425.

  buscojobs.py list --host ve.buscojobs.com [--pages N | --all] [--limit N]
  buscojobs.py ad --url <https://<front>/<slug>-ID-<n>>
  buscojobs.py hosts

THE ROUTE IS THE LISTING PAGE'S OWN PAYLOAD. Every front is the same
Next.js application — **one `buildId` on all sixteen fronts read on
2026-09-13, `5d4757de…`** — and `/ofertas/<p>` (`/vagas/<p>` on the
Portuguese fronts) server-renders its results into `__NEXT_DATA__`:
`pageProps.resultadosIniciales = {count, ofertas[15], facets}` — the
**count the site states** and fifteen full records per page (id, title,
employer, city, department, country, start date, a 150-character
excerpt, the flags). The page's JSON-LD `ItemList` carries the fifteen
public URLs in the same order, `…-ID-<IdOferta>`. **No key, no cookie,
no browser** — and a pace, below.

MEASURED 2026-09-13 23:31–23:47 UTC, one listing page per front, the
declared client, guard on the exact path (`*` group: only
`*fechainicio=` is refused; the `ClaudeBot` group refuses `/` and does
not bind `Claude-User` — decision of 2026-09-07). The count is the
payload's `resultadosIniciales.count`:

    ve.buscojobs.com        VE      6 262     www.buscojobs.com.ar   AR    108 822
    www.buscojobs.com.uy    UY      1 943     www.buscojobs.cl       CL     73 966
    www.buscojobs.com       UY      1 943  (the same front, `es-UY`, same count)
    www.buscojobs.com.pr    PR      8 901     www.buscojobs.com.co   CO    129 610
    www.buscojobs.com.py    PY         41     www.buscojobs.com.es   ES  2 858 489
    www.buscojobs.com.bo    BO          2     br.buscojobs.com       BR  1 556 164
    ni.buscojobs.com        NI         28     www.buscojobs.pt       PT    498 335
    www.buscojobs.com.do    DO      2 375     www.buscojobs.com.gt   GT      2 234
    www.buscojobs.com.ec    EC      2 586     www.buscojobs.com.pa   PA        988
    www.buscojobs.hn        HN          1     www.buscojobs.mx       MX  1 646 877
    www.buscojobs.com.sv    SV        842     www.buscojobs.pe       PE     34 141
    www.buscojobs.cr        CR      1 262

**THE CHALLENGE IS BEHAVIOURAL, AND IT WAS MEASURED TWICE.** Twenty-one
fronts read in 80 seconds (23:31–23:32, two requests each) left five
answering the listing with HTTP 405, 2 103 bytes titled «Human
Verification» (AWS WAF, `gokuProps`, md5 moving between reads) while
their root was served; the Venezuelan front served three listing pages
and one ad, then challenged the fourth request of the same minute. Five
minutes later, one request every 30 seconds: **seven of seven served**,
the Honduran listing included, and the four others were read at 20 s
(23:45–23:47). So the pace is **20 s between requests, per host** — the
figure the challenge answered, not a courtesy — and a challenge met on a
walk prints what was emitted, names the page, and exits 7: it is not
defeated and nobody is asked to defeat it (borne 2). `GT` states no
`Pais.Codigo` on its records; the country comes from this table.

THE SIX-MILLION-ROW FRONTS ARE AGGREGATES. Spain states 2 858 489, Brazil
1 556 164 — feeds, not postings by employers on the front. **The default
walk is bounded** (`--pages 10`, 150 rows) and says so; `--all` walks to
the count and is compared: «N emitted over P page(s), site states N —
equal», exit 6 on a gap. A walk that hits the challenge prints what it has
and exits 7, naming the page.

WHAT IS WITHHELD. The ad payload carries the employer's contact fields
(`EmailEmpresa`, `TelefonoEmpresa`, `NombreContactoEmpresa`,
`EmailContactoEmpresa`, `DireccionEmpresa`) — **never emitted**; addresses
and phone numbers in the prose are replaced. `EdadDesde`/`EdadHasta`/`Sexo`
— an age band and a sex — are criteria this project does not propagate
(#183): not emitted. `Confidencial` employers are emitted as null.
The employer object is reduced to its id and name before the record is built.
"""

import argparse
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

# front -> (country, listing path); read on 2026-09-13, one page each
HOSTS = {
    "ve.buscojobs.com": ("VE", "/ofertas"),
    "www.buscojobs.com.uy": ("UY", "/ofertas"),
    "www.buscojobs.com": ("UY", "/ofertas"),       # the same front under the bare name, `es-UY`
    "www.buscojobs.com.pr": ("PR", "/ofertas"),
    "www.buscojobs.com.py": ("PY", "/ofertas"),
    "www.buscojobs.com.bo": ("BO", "/ofertas"),
    "ni.buscojobs.com": ("NI", "/ofertas"),
    "www.buscojobs.com.do": ("DO", "/ofertas"),
    "www.buscojobs.com.ec": ("EC", "/ofertas"),
    "www.buscojobs.com.gt": ("GT", "/ofertas"),
    "www.buscojobs.com.pa": ("PA", "/ofertas"),
    "www.buscojobs.com.ar": ("AR", "/ofertas"),
    "www.buscojobs.cl": ("CL", "/ofertas"),
    "www.buscojobs.com.co": ("CO", "/ofertas"),
    "www.buscojobs.com.es": ("ES", "/ofertas"),
    "br.buscojobs.com": ("BR", "/vagas"),
    "www.buscojobs.pt": ("PT", "/vagas"),
    "www.buscojobs.hn": ("HN", "/ofertas"),        # these five challenged the burst of 23:32 and served the paced read of 23:40–23:5x
    "www.buscojobs.com.sv": ("SV", "/ofertas"),
    "www.buscojobs.cr": ("CR", "/ofertas"),
    "www.buscojobs.mx": ("MX", "/ofertas"),
    "www.buscojobs.pe": ("PE", "/ofertas"),
}

PAGE_SIZE = 15
DEFAULT_PAGES = 10
ID_RE = re.compile(r"-ID-(\d+)/?$")
AD_RE = re.compile(r"^https?://([a-z0-9.-]+)/[^/?#]*-ID-(\d+)/?$")
NEXT_RE = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
LD_RE = re.compile(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', re.S)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\d[\d\s().-]{6,}\d(?!\w)")
CONTACT_KEYS = ("EmailEmpresa", "TelefonoEmpresa", "NombreContactoEmpresa", "EmailContactoEmpresa", "DireccionEmpresa", "PaginaWebEmpresa")
FLAGS = (("PermiteTeletrabajo", "remote"), ("PermiteTrabajoHibrido", "hybrid"), ("PermiteHorarioFlexible", "flexible_hours"),
         ("EsPasantia", "internship"), ("PrimerEmpleo", "first_job"), ("PermiteDiscapacidad", "disability_welcome"))

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[buscojobs] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def front(host):
    """The front's (country, listing path) — or a refusal that names why."""
    if host not in HOSTS:
        die(f"{host}: not a front read by this adapter — `hosts` lists the {len(HOSTS)} read on 2026-09-13; a new one is measured, not assumed.")
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
    """One GET, gated on the exact path, paced per host — `(code, body)`; a challenge is a code, not a body."""
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    _PACES.setdefault(host, Pace(host, own=20.0)).wait()   # measured: a burst is challenged, 30 s is served — 20 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        try:
            body = decode_body(e.read(), e.headers)[0]
        except Exception:
            body = ""
        return e.code, body
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def challenged(code, body):
    return code == 405 and "Human Verification" in (body or "")


def next_data(body, url):
    m = NEXT_RE.search(body or "")
    if not m:
        die(f"{url}: no __NEXT_DATA__ in the page ({len(body or '')} characters) — not the application this file reads.", EXIT_PARTIAL)
    try:
        return json.loads(m.group(1))["props"]["pageProps"]
    except (ValueError, KeyError, TypeError) as e:
        die(f"{url}: __NEXT_DATA__ unreadable ({type(e).__name__}).", EXIT_PARTIAL)


def ad_urls(body):
    """`{id: url}` from the page's JSON-LD ItemList — the public address of each row, in the page's own words."""
    out = {}
    for m in LD_RE.finditer(body or ""):
        try:
            j = json.loads(m.group(1))
        except ValueError:
            continue
        for it in (j.get("itemListElement") or []) if isinstance(j, dict) else []:
            u = it.get("url") if isinstance(it, dict) else None
            k = ID_RE.search(u or "")
            if k:
                out[k.group(1)] = u
    return out


def redact(s):
    """Addresses and phone numbers in the prose are contacts — withheld. A phone is nine digits or more (a date has eight, a salary rarely nine)."""
    s = EMAIL_RE.sub("[e-mail withheld]", s or "")
    return PHONE_RE.sub(lambda m: "[phone withheld]" if sum(c.isdigit() for c in m.group(0)) >= 9 else m.group(0), s)


def name(d, key="Nombre"):
    return ((d or {}).get(key) or "").strip() or None if isinstance(d, dict) else None


def record(o, host, country, urls=None):
    ident = str(o.get("IdOferta") or "").strip()
    conf = bool(o.get("Confidencial"))
    emp = None if conf else (o.get("NombreEmpresa") or name(o.get("Empresa")) or "").strip() or None
    r = {
        "source": "buscojobs", "country": country, "host": host, "ledger_id": f"buscojobs:{host}:{ident}", "id": ident,
        "url": (urls or {}).get(ident) or o.get("UrlOferta") or f"https://{host}/oferta-ID-{ident}",
        "title": redact(o.get("CargoVacante") or "").strip() or None,
        "employer": redact(emp) if emp else None, "confidential": conf or None,
        "city": name(o.get("Ciudad")), "region": name(o.get("Departamento")),
        "posted": o.get("FechaInicio") or None, "source_feed": o.get("Fuente") or None,
        "flags": [label for key, label in FLAGS if o.get(key) in (1, True)],
        "summary": redact(o.get("Descripcion") or "").strip() or None,
    }
    if "NroPuestosVacantes" in o:   # the ad payload
        sd, sh = o.get("SueldoDesde") or 0, o.get("SueldoHasta") or 0
        r.update({
            "positions": o.get("NroPuestosVacantes") or None, "valid_through": o.get("FechaFin") or None,
            "occupation": name(o.get("Cargo")), "contract": o.get("TipoContrato") or None,
            "schedule": name(o.get("JornadaLaboral")), "hours": redact(o.get("Horario") or "").strip() or None,
            "seniority": name(o.get("NivelJerarquico")),
            # the payload names no unit for `SueldoDesde`/`SueldoHasta`; the figure travels with its unit declared unknown, never guessed from the front
            "salary_min": sd or None, "salary_max": sh or None, "salary_currency": None,
            "languages": [name(x) for x in o.get("Idiomas") or [] if name(x)],
            "skills": [name(x) for x in o.get("Conocimientos") or [] if name(x)],
            "description": redact(o.get("DescripcionMarkdown") or o.get("Descripcion") or "").strip() or None,
            "status": o.get("EstadoNombre") or None,
        })
        r.pop("summary", None)
    return r


def cmd_hosts(a):
    for h, (c, p) in HOSTS.items():
        print(f"{h}\t{c}\t{p}\tread 2026-09-13")


def cmd_list(a):
    country, path = front(a.host)
    if a.pages is not None and a.pages < 1:
        die("--pages must be at least 1 (or use --all).")
    limit_pages = None if a.all else (a.pages or DEFAULT_PAGES)
    seen, emitted, page, site = set(), 0, 0, None
    while True:
        page += 1
        url = f"https://{a.host}{path}" + (f"/{page}" if page > 1 else "")
        code, body = request(url)
        if challenged(code, body):
            note(f"{th(emitted)} emitted over {page - 1} page(s), site states {th(site) if site is not None else '?'} — page {page} answered a challenge "
                 f"(HTTP 405 «Human Verification»); not defeated, the walk stops here.")
            sys.exit(EXIT_REFUSED)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        pp = next_data(body, url)
        res = pp.get("resultadosIniciales") or {}
        rows = res.get("ofertas")
        if not isinstance(rows, list):
            die(f"{url}: no resultadosIniciales.ofertas in the payload — keys {sorted(pp)}.", EXIT_PARTIAL)
        if site is None:
            try:
                site = int(res.get("count"))
            except (TypeError, ValueError):
                die(f"{url}: the payload states no count ({res.get('count')!r}).", EXIT_PARTIAL)
        urls = ad_urls(body)
        new = 0
        for o in rows:
            r = record(o, a.host, country, urls)
            if not r["id"] or r["id"] in seen:
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


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an ad URL of a Buscojobs front (https://<front>/<slug>-ID-<n>).")
    host, ident = m.group(1), m.group(2)
    country, _ = front(host)
    code, body = request(a.url.strip())
    if challenged(code, body):
        die(f"{a.url}: the ad page answered a challenge (HTTP 405 «Human Verification») — not defeated.", EXIT_REFUSED)
    if code == 404:
        die(f"{a.url}: HTTP 404 — the ad is gone.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_PARTIAL)
    pp = next_data(body, a.url)
    o = pp.get("oferta")
    if not isinstance(o, dict) or not o.get("IdOferta"):
        die(f"{a.url}: the page carries no `oferta` — gone, or never public.", EXIT_GONE)
    if str(o.get("IdOferta")) != ident:
        die(f"{a.url}: the page carries oferta {o.get('IdOferta')}, the URL names {ident}.", EXIT_PARTIAL)
    for k in CONTACT_KEYS:
        o.pop(k, None)   # the employer's contact fields never leave this file
    if isinstance(o.get("Empresa"), dict):
        o["Empresa"] = {k: v for k, v in o["Empresa"].items() if k in ("IdEmpresa", "Nombre")}
    r = record(o, host, country)
    r["url"] = o.get("UrlOferta") or a.url.strip()
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="walk one front's listing")
    l.add_argument("--host", required=True, help="the front, e.g. ve.buscojobs.com — see `hosts`")
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
