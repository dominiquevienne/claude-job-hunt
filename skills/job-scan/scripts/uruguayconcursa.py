#!/usr/bin/env python3
"""Uruguay Concursa (`www.uruguayconcursa.gub.uy`) — the Uruguayan state's calls for candidates («llamados», ONSC), through the JSON API the page itself posts to; «Mostrando TODOS los Llamados Abiertos (363)» printed beside every walk; the employer is the state body and is public; contacts in the prose are withheld. Issue #435.

  uruguayconcursa.py list [--status Abierto|Inscripciones Cerradas|Finalizado UC|...|all] [--q text] [--pages N] [--limit N]
  uruguayconcursa.py ad --url <https://www.uruguayconcursa.gub.uy/llamado/<id>>

THE ROUTE IS THE API THE ANGULAR SHELL CALLS — read in `main-5J773LRE.js`
(`apiUrl:"/api-backend"`, `llamadosEndpoint = /api-backend/llamados`):

  POST /api-backend/llamados/find   {"llamadosFiltros": {"PaginaActual": p, "CntPorPagina": n, "ListaLlaEstWeb": ["Abierto"], "Descripcion": q}}
                                     -> {"ListaLlamados": [...], "Resultado": "Mostrando TODOS los Llamados Abiertos (363)", "cntPaginas": "8", "cntTotal": "363"}
  GET  /api-backend/llamados/get/?Llaid=<id>   -> {"ListaLlamados": [one record, the same 33 fields]}

Measured 2026-09-13 23:13–23:14 UTC by the declared client: unfiltered
`find` states 42 217 (the whole archive, every status), the `Abierto`
filter states **363** over 8 pages of 50 — page 1 and page 2 share no
id; `recientes` states 410; `statuses` answers 404 (the page's fallback
is a hard-coded list); `get` returns the very record `find` already
carried, no extra field. The rules: `/robots.txt` unreadable → no written
rule, `certain: False` — nothing refuses the API; 3 s between requests
is ours. **The state body is the employer and is public** (`Inciso` ·
`UnidadEjecutora`); **e-mail addresses and phone numbers in the prose
fields are contacts and are withheld** — 88 addresses in the 50 records
of page 1, all in `LlaMedPos`/`LlaReqExc`/`LlaConTra`.

THE RECORD: `LlaId`, `LlaNum` («0049/2026»), `LlaTit`, `CarNom`,
`Inciso`, `UnidadEjecutora`, `LlaLugDes` (place of work), `LlaRet`
(salary as the state writes it — «$60.610 nominales a valores de Enero
2026» — kept as text, never parsed into a number), `LlaCarHor` (hours),
`TipVinDsc` (bond), `TipTarDsc` (task type), `LlaFchApeIns`/`LlaFchCieIns`
(registration window, ISO dates), `LlaEstWeb` (status), the four legal
quota flags (Afro, Trans, Disc, VicDelVio), `listaOrganismoCantPuestos`
(posts per body — summed as `positions`), `listaEtapaProceso`,
`LlaReqExc` (excluding requirements), `LlaConTra`, `LlaRegInc`,
`LlaTieCon`. The public page of a llamado is `/llamado/<LlaId>`.
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

HOST = "www.uruguayconcursa.gub.uy"
BASE = f"https://{HOST}"
API = f"{BASE}/api-backend/llamados"
AD_RE = re.compile(r"^https?://www\.uruguayconcursa\.gub\.uy/llamado/(\d+)/?$")
PAGE_SIZE = 50
STATED_RE = re.compile(r"\((\d+)\)\s*$")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?598[\s.-]?)?(?:0?9\d[\s.-]?\d{3}[\s.-]?\d{3}|2\d{3}[\s.-]?\d{4})(?!\d)")
STATUSES = ("Abierto", "Inscripciones Cerradas", "Finalizado UC", "No Publicado")
QUOTAS = (("LlaAfro", "Afro"), ("LlaTrans", "Trans"), ("LlaDisc", "Discapacidad"), ("LlaVicDelVio", "VicDelVio"))

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[uruguayconcursa] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=3.0)   # no rule could be read; 3 s is ours


def request(url, payload=None):
    """One JSON request — GET, or POST of a JSON body — gated on the exact path."""
    gate(url)
    _PACE.wait()
    headers = {"User-Agent": UA, "Accept": "application/json"}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode()
    req = urllib.request.Request(wire_url(url), data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def redact(s):
    """An address or a phone number in the state's prose is a contact — withheld, never emitted."""
    s = EMAIL_RE.sub("[e-mail withheld]", s or "")
    return PHONE_RE.sub("[phone withheld]", s)


def parse(body, url):
    try:
        j = json.loads(body)
    except ValueError:
        die(f"{url}: not JSON ({len(body or '')} characters) — a firewall page or a redirect, not the API.", EXIT_PARTIAL)
    if not isinstance(j, dict) or not isinstance(j.get("ListaLlamados"), list):
        die(f"{url}: no ListaLlamados in the answer — keys {sorted(j) if isinstance(j, dict) else type(j).__name__}.", EXIT_PARTIAL)
    return j


def stated(j):
    """The count the site states: `cntTotal`, else the «(N)» its `Resultado` sentence ends with."""
    for k in ("cntTotal",):
        v = j.get(k)
        if v not in (None, ""):
            try:
                return int(str(v).replace(".", "").strip())
            except ValueError:
                pass
    m = STATED_RE.search(str(j.get("Resultado") or ""))
    return int(m.group(1)) if m else None


def positions(rec):
    tot = 0
    for o in rec.get("listaOrganismoCantPuestos") or []:
        try:
            tot += int(o.get("LlaOrgCntPue") or 0)
        except (TypeError, ValueError):
            pass
    return tot or None


def record(rec):
    ident = str(rec.get("LlaId") or "").strip()
    inciso = (rec.get("Inciso") or "").strip() or None
    ue = (rec.get("UnidadEjecutora") or "").strip() or None
    employer = " · ".join(x for x in (inciso, ue) if x) or None
    quotas = [label for key, label in QUOTAS if rec.get(key) is True]
    desc = "\n\n".join(f"{h}\n{redact(rec.get(k))}" for h, k in (("Requisitos excluyentes", "LlaReqExc"), ("Otras condiciones de trabajo", "LlaConTra"),
                                                            ("Tiempo de contratación", "LlaTieCon"), ("Incompatibilidades", "LlaRegInc")) if (rec.get(k) or "").strip())
    return {
        "source": "uruguayconcursa", "country": "UY", "ledger_id": f"uruguayconcursa:{ident}", "id": ident,
        "url": f"{BASE}/llamado/{ident}", "reference": rec.get("LlaNum") or None,
        "title": redact(rec.get("LlaTit") or rec.get("CarNom") or "").strip() or None, "occupation": (rec.get("CarNom") or "").strip() or None,
        "employer": employer, "inciso": inciso, "unidad_ejecutora": ue, "location": redact(rec.get("LlaLugDes") or "").strip() or None,
        "posted": rec.get("LlaFchApeIns") or None, "valid_through": rec.get("LlaFchCieIns") or None, "status": rec.get("LlaEstWeb") or None,
        "contract": rec.get("TipVinDsc") or None, "task_type": rec.get("TipTarDsc") or None,
        "salary_text": redact(rec.get("LlaRet") or "").strip() or None, "hours": redact(rec.get("LlaCarHor") or "").strip() or None,
        "positions": positions(rec), "quotas": quotas, "stages": [s.strip() for s in rec.get("listaEtapaProceso") or [] if str(s).strip()],
        "description": desc or None, "application": "www.uruguayconcursa.gub.uy" if "uruguayconcursa" in (rec.get("LlaMedPos") or "") else None,
    }


def cmd_list(a):
    status = (a.status or "Abierto").strip()
    filt = {"PaginaActual": 1, "CntPorPagina": PAGE_SIZE}
    label = "all statuses"
    if status.lower() != "all":
        filt["ListaLlaEstWeb"] = [s.strip() for s in status.split(",") if s.strip()]
        label = "status " + ", ".join(filt["ListaLlaEstWeb"])
    if a.q:
        filt["Descripcion"] = a.q.strip()
        label += f", q={a.q.strip()!r}"
    url = f"{API}/find"
    seen, emitted, page, site, pages_said, bounded = set(), 0, 0, None, None, False
    while True:
        page += 1
        filt["PaginaActual"] = page
        code, body = request(url, {"llamadosFiltros": dict(filt)})
        if code != 200:
            die(f"{url} (page {page}): HTTP {code}", EXIT_PARTIAL if page > 1 else EXIT_BROKEN)
        j = parse(body, url)
        if site is None:
            site = stated(j)
            try:
                pages_said = int(str(j.get("cntPaginas") or "").strip() or 0) or None
            except ValueError:
                pages_said = None
            if site is None:
                die(f"{url}: the answer states no count — neither cntTotal nor «(N)» in Resultado ({str(j.get('Resultado'))[:80]!r}).", EXIT_PARTIAL)
        rows = j["ListaLlamados"]
        for rec in rows:
            r = record(rec)
            if not r["id"] or r["id"] in seen:
                continue
            seen.add(r["id"])
            print(json.dumps(r, ensure_ascii=False))
            emitted += 1
            if a.limit and emitted >= a.limit:
                bounded = True
                break
        if bounded or not rows or len(rows) < PAGE_SIZE:
            break
        if pages_said and page >= pages_said:
            break
        if a.pages and page >= a.pages:
            bounded = True
            break
    if bounded:
        note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} ({label}) — walk bounded by request (--pages/--limit), not compared.")
        return
    if emitted == site:
        note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} ({label}) — equal.")
    else:
        note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} ({label}) — {th(abs(site - emitted))} {'short' if emitted < site else 'over'}.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    m = AD_RE.match(a.url or "")
    if not m:
        die(f"{a.url}: not a llamado URL (expected https://{HOST}/llamado/<id>).")
    ident = m.group(1)
    url = f"{API}/get/?Llaid={urllib.parse.quote(ident)}"
    code, body = request(url)
    if code == 404:
        die(f"{a.url}: HTTP 404 — the llamado is gone.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_PARTIAL)
    j = parse(body, url)
    if not j["ListaLlamados"]:
        die(f"{a.url}: the API returns no record for Llaid={ident} — gone, or never public.", EXIT_GONE)
    print(json.dumps(record(j["ListaLlamados"][0]), ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="the llamados by status (Abierto by default, `all` for the whole archive — 42 217 on 2026-09-13), 50 a page, 3 s apart, walked to the count the API states")
    s.add_argument("--status", default="Abierto", help="one or more of " + ", ".join(STATUSES) + " (comma-separated), or `all`")
    s.add_argument("--q", help="free text (the API's Descripcion filter)")
    s.add_argument("--pages", type=int, help="stop after N pages (bounded walk, not compared)")
    s.add_argument("--limit", type=int, help="stop after N records (bounded walk, not compared)")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one llamado by its public URL — the same record `list` carries")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
