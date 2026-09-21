#!/usr/bin/env python3
"""ePreselec (`<tenant>.epreselec.com`, the InfoJobs / Adevinta ATS — one tenant at a time): the tenant's `/Ofertas/Ofertas.aspx` is a server-rendered WebForms list with its count in the page («Total ofertas: 16»); `?Id_Oferta=<id>` renders the advert on the same page. Issue #490.

  epreselec.py jobs --tenant <name|host|url>
  epreselec.py ad --url https://<tenant>.epreselec.com/Ofertas/Ofertas.aspx?Id_Oferta=<id>

THE TENANT is the subdomain of `epreselec.com` the employer's careers site
lives on (`culligan`, `eroski`, `fcc`, `dia`, `compassgroup`, `salesland`),
found by the family's signature `epreselec.com/Ofertas/Ofertas.aspx` in a
search engine on 2026-09-21 — never composed: a subdomain that is no tenant
answers the site's own «404 - Page not found» — as an HTTP 200 (`bkspain`, 2 334 B; exit 3 here).
The vendor's `www.epreselec.com` is not a board.

THE RULES (196 B, read on `culligan` 2026-09-21 06:15 UTC): `dotbot` and
`trovitBot` refused `/`; `User-agent: *` refuses `/ScriptResource.axd`,
`/WebResource.axd`, `/*.axd$` — the framework's resources, not the pages;
no agent of this project named, no Crawl-delay.

THE TRANSPORT SERVES, THEN CHALLENGES — MEASURED 2026-09-21 06:15–06:17 UTC.
The first requests to the declared client were served: the list (200,
72 617 B, «Total ofertas: 16», sixteen rows) and an advert (200, 90 731 B)
twice each. **From about the twelfth request in two minutes every path —
`/`, `/robots.txt` included — answered HTTP 200 with the same 11 621 B
«Pardon Our Interruption»** (md5 f774ef2293e6 on every host and path: «As
you were browsing something about your browser made us think you were a
bot … You're a power user moving through this website with super-human
speed», with a CAPTCHA to «regain access»). A rate control served as a
200 — `_robots` reads that body as `unrecognised` (no rules, `certain:
False`) and the page reader here reads it as the challenge it is: **the
adapter dies with exit 9** (the browser exit of `_ua.browser_fallback`),
the CAPTCHA never answered, never asked of anyone (borne 2), and says
which request it was. Ten seconds between requests are this adapter's own
pace (`_pace`, `own=10.0`); a `jobs` run is two requests, an `ad` one.

THE LIST: `div.total-vacancies` «Total ofertas: N», then one `<li>` per
advert in `div.onepage-ofertas` — `a[data_idOferta="<id>"]`,
`span.op-titulo` the title, `span.op-fecha` the date («16 de septiembre,
2026»; emitted as written and as ISO). The province filter is a
`__doPostBack`, never replayed; the whole list is on the one page. No
location on the row — the advert has it.

THE ADVERT: `?Id_Oferta=<id>` renders `div#ctl00_CPH_Body_pnlVacancy` —
`<h1>` title, «Localidad», «Provincia», «Nº Vacantes (puestos)», and four
`<h3>` sections each in its labelled span: «Descripción»
(`lDescripcionEmpresa`, the employer's presentation), «Funciones»,
«Requisitos», «Se ofrece». No JobPosting. «Inscribirme a esta oferta» is a
postback into an account — never touched. The tenant's name is the page's
`<title>` («… - EROSKI - ePreselec») when the page carries one.

WITHHELD: the sections scrubbed of e-mail addresses and telephone
numbers; `contacts_withheld` on every record; the site states no country
— the family is Spanish, `--country-code` stamps what the user names.
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
from _ua import UA, browser_fallback

BOARD, DOMAIN = "epreselec", "epreselec.com"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

TENANT_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", re.I)
TOTAL_RE = re.compile(r'class="total-vacancies">\s*Total ofertas:\s*(\d+)', re.S)
ROW_RE = re.compile(r'<a[^>]*\bdata_idOferta="(?P<id>\d+)"[^>]*>(?P<body>.*?)</a>', re.S)
TITLE_RE = re.compile(r'<span class="op-titulo">(.*?)</span>', re.S)
DATE_RE = re.compile(r'<span class="op-fecha">(.*?)</span>', re.S)
LIST_RE = re.compile(r'<div class="onepage-ofertas">')
VAC_RE = re.compile(r'id="ctl00_CPH_Body_pnlVacancy"(.*)', re.S)
H1_RE = re.compile(r'<span id="ctl00_CPH_Body_lDescripcion">(.*?)</span>', re.S)
FIELD_RE = re.compile(r'<span id="ctl00_CPH_Body_(lLocalidadText|lProvinciaText|lNumVacantes)">(.*?)</span>', re.S)
SECTION_RE = re.compile(r'<span id="ctl00_CPH_Body_(lDescripcionEmpresa|lFunciones|lRequisitos|lSeOfrece)">(.*?)</span>\s*</p>', re.S)
PAGE_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
CHALLENGE_RE = re.compile(r"<title>\s*Pardon Our Interruption", re.I)
MONTHS = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
_PACES = {}
TENANT = {"host": None}
SECTION_NAMES = {"lDescripcionEmpresa": "Descripción", "lFunciones": "Funciones", "lRequisitos": "Requisitos", "lSeOfrece": "Se ofrece"}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[epreselec] {msg}", file=sys.stderr)


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
    """(status, body) — this run's tenant only, the guard first, 10 s apart; the challenge page ends the run with 9."""
    parts = urllib.parse.urlsplit(url)
    host = parts.netloc.lower()
    if not TENANT["host"] or host != TENANT["host"] or not host.endswith("." + DOMAIN):
        die(f"{url}: not this run's ePreselec tenant ({TENANT['host'] or 'none named'}) — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=10.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "es,en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            st, body = r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")
    if st == 200 and CHALLENGE_RE.search(body or ""):
        msg, code = browser_fallback(host, True, 200, url)
        die(f"{url}: HTTP 200 with the «Pardon Our Interruption» challenge ({len(body)} bytes) — the host's rate control, served as a 200 (2026-09-21: from about the twelfth request in two minutes, every path). "
            f"The CAPTCHA is never answered and never asked of anyone. " + msg, code)
    return st, body


def text(markup):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", markup or "", flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", t)
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span|font)\b[^>]*>", "", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def iso_date(s):
    """«16 de septiembre, 2026» → 2026-09-16; None when the shape is another."""
    m = re.search(r"(\d{1,2})\s+de\s+([a-záéíóú]+),?\s+(\d{4})", (s or "").lower())
    if not m or m.group(2) not in MONTHS:
        return None
    return f"{m.group(3)}-{MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}"


def tenant_of(arg):
    """`eroski`, `eroski.epreselec.com` or a URL on it → the host."""
    s = (arg or "").strip().lower()
    if "://" in s or "/" in s:
        s = urllib.parse.urlsplit(s if "://" in s else "https://" + s).netloc
    if not s:
        die(f"--tenant {arg!r}: name the tenant (eroski), its host or its Ofertas.aspx URL")
    if "." not in s:
        if not TENANT_RE.match(s) or s in ("www", "app", "api", "admin"):
            die(f"--tenant {arg!r}: not a tenant name (the vendor's own host is not a board)")
        return f"{s}.{DOMAIN}"
    if not s.endswith("." + DOMAIN) or s in ("www." + DOMAIN,) or not TENANT_RE.match(s[: -len("." + DOMAIN)]):
        die(f"--tenant {arg!r}: not an ePreselec tenant host (<tenant>.{DOMAIN})")
    return s


def list_url(host):
    return f"https://{host}/Ofertas/Ofertas.aspx"


def ad_url(host, jid):
    return f"https://{host}/Ofertas/Ofertas.aspx?Id_Oferta={jid}"


NOT_FOUND_RE = re.compile(r"<title>\s*Page not found|404 - Page not found", re.I)


def status_of(st, url, host, body=""):
    if st == 404 or (st == 200 and NOT_FOUND_RE.search(body or "")):
        die(f"{url}: {'HTTP 404' if st == 404 else 'HTTP 200 with'} the site's own «404 - Page not found» (served as a 200 on 2026-09-21): {host} is not an ePreselec tenant, or the page is gone.", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)


def parse_list(body):
    """(total, rows) — rows None when the page carries no list."""
    if not LIST_RE.search(body or ""):
        return None, None
    m = TOTAL_RE.search(body)
    total = int(m.group(1)) if m else None
    rows = []
    for r in ROW_RE.finditer(body):
        b = r.group("body")
        t = TITLE_RE.search(b)
        d = DATE_RE.search(b)
        rows.append((r.group("id"), text(t.group(1)) if t else None, text(d.group(1)) if d else None))
    return total, rows


def company_of(body):
    pt = PAGE_TITLE_RE.search(body or "")
    if not pt:
        return None
    parts = [p.strip() for p in htmlmod.unescape(pt.group(1)).split(" - ")]
    parts = [p for p in parts if p and p.lower() != "epreselec" and not p.lower().startswith("ofertas de empleo")]
    return parts[-1] if parts else None


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    TENANT["host"] = host
    country = (a.country_code or "").strip().upper() or None
    url = list_url(host)
    st, body = request(url)
    status_of(st, url, host, body)
    total, rows = parse_list(body)
    if rows is None:
        die(f"{url}: no offers list in the page (no `onepage-ofertas`) — not an ePreselec careers page, or the page changed shape.", EXIT_PARTIAL)
    company = company_of(body)
    seen, out = set(), []
    for jid, title, date in rows:
        if jid in seen:
            continue
        seen.add(jid)
        out.append({"source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{jid}", "id": jid, "url": ad_url(host, jid),
                    "title": title, "company": company, "country": country, "posted": iso_date(date), "posted_as_written": date, "contacts_withheld": True})
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    stamp = f"; country {country} stamped from --country-code (the site states none)" if country else ""
    if total is None:
        note(f"{th(n)} emitted — the page states no count{stamp}.")
    elif n == total:
        note(f"{th(n)} emitted — the page states {th(total)}: equal{stamp}.")
    else:
        note(f"{th(n)} emitted — the page states {th(total)}: {th(abs(total - n))} " + ("short (rows the page did not render)" if total > n else "more emitted than stated") + f"{stamp}.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    host = parts.netloc.lower()
    q = urllib.parse.parse_qs(parts.query)
    jid = (q.get("Id_Oferta") or q.get("id_oferta") or [""])[0]
    if not host.endswith("." + DOMAIN) or host == "www." + DOMAIN or parts.path.lower() != "/ofertas/ofertas.aspx" or not jid.isdigit():
        die(f"{a.url!r}: not an ePreselec advert address (https://<tenant>.{DOMAIN}/Ofertas/Ofertas.aspx?Id_Oferta=<id>)")
    TENANT["host"] = host
    url = ad_url(host, jid)
    st, body = request(url)
    status_of(st, url, host, body)
    vm = VAC_RE.search(body)
    h1 = H1_RE.search(vm.group(1)) if vm else None
    if not vm or not h1 or not text(h1.group(1)):
        die(f"{url}: no advert rendered in the page (no `pnlVacancy` title) — the advert is gone, or the id is another tenant's.", EXIT_PARTIAL)
    seg = vm.group(1)
    fields = {k: text(v) for k, v in FIELD_RE.findall(seg)}
    sections = {SECTION_NAMES[k]: scrub(text(v)) for k, v in SECTION_RE.findall(seg)}
    r = {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{jid}", "id": jid, "url": url,
        "title": text(h1.group(1)), "company": company_of(body),
        "place": fields.get("lLocalidadText"), "province": fields.get("lProvinciaText"),
        "vacancies": int(fields["lNumVacantes"]) if fields.get("lNumVacantes", "").isdigit() else fields.get("lNumVacantes"),
        "description": (sections.get("Funciones") or sections.get("Descripción") or "")[:20000] or None,
        "sections": {k: (v or "")[:8000] for k, v in sections.items() if v} or None,
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="ePreselec — one tenant's offers list (its count in the page) and adverts; the host's 200 challenge ends the run with 9; no contact. Issue #490.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the tenant's Ofertas.aspx list, one request; the count beside the emitted number")
    s.add_argument("--tenant", required=True, help="the subdomain (eroski), the host, or the list's URL")
    s.add_argument("--country-code", help="ISO2 to stamp the rows with — the site states no country")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by ?Id_Oferta=; sections scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
