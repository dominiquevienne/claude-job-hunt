#!/usr/bin/env python3
"""Trabaja en el Estado (`www.trabajaenelestado.cl`, Servicio Civil) — Chile's public-service job calls, through the Elasticsearch route the page names and posts to itself; `hits.total` printed beside every walk; the detail addresses point at a host that says no and are never fetched. Issue #302.

  trabajaenelestado.py list [--estado postulacion|evaluacion|finalizadas|todos] [--region regionNN] [--pages N] [--limit N]

THE ROUTE IS THE PAGE'S OWN DATA CALL. `www.trabajaenelestado.cl` is a jQuery page whose
`doSearch()` posts a JSON query to

  POST https://elastic.serviciocivil.cl/listado_teee/_doc/_search     {from, size: 36, sort, query: {bool: {must: [{term: {"Estado": "postulacion"}}, …]}}}

and reads `hits.total` and `hits.hits[]._source`. This adapter sends the same shape — the
same index, the same `term` filters the page's buttons send (`Estado`, `Codigo Region`), the
page's own page size — with two differences said out loud: **the page's sort is a Painless
`_script`; this adapter sorts by the plain field `Datesum` (then `ID Conv`), because a client
does not send scripts to someone else's cluster**; and `track_total_hits: true`, so the total
is exact. The rules: `elastic.serviciocivil.cl/robots.txt` is 404 — an absence, certain, open;
`www.trabajaenelestado.cl/robots.txt` is an S3 `AccessDenied` — an absence since #283. No
Crawl-delay; 2 s is ours. Elasticsearch's window is 10 000 (`from + size`), which the page
itself caps at; the adapter stops there and says so.

THE RECORD (`_source`, the site's own field names): `ID Conv` (id), `Cargo` (title),
`Institucion/Entidad` (employer — the State's own service), `Ministerio`, `Region` and `Codigo
Region`, `Ciudad`, `Area de Trabajo`, `Cargo Profesional`, `Tipo Convocatoria` (EEPP …),
`Tipo Postulacion`, `Fecha inicio/cierre Convocatoria` (DD/MM/YYYY H:MM:SS, as stored),
`Estado` (postulacion / evaluacion / finalizadas), `URL`. **`Ganador` — the name of the
person appointed on a finished call — is personal data and is never emitted.**

**THE DETAIL IS ON A HOST THAT SAYS NO.** Most `URL`s (255 of 349 on the day) are
`https://www.empleospublicos.cl/pub/convocatorias/…` (the JUNJI feed points at `junji.myfront.cl`), and `www.empleospublicos.cl` publishes
`User-agent: * / Disallow: /` (`chile-public-sector.md`). The address is emitted as the
record's own field — a user may open it — and **this adapter never fetches it and has no
`ad` command**: the listing IS the record, and reading the operator's pages through the
index host that merely has no rules file would be choosing the host that says yes.

Measured 2026-09-13 23:59 UTC by the declared client: `Estado: postulacion` → `hits.total`
349, 36 a page; the record above from the first page.
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

HOST = "elastic.serviciocivil.cl"
SEARCH = f"https://{HOST}/listado_teee/_doc/_search"
SITE = "https://www.trabajaenelestado.cl"
PAGE_SIZE = 36            # the page's own `pCantidadXPag`
WINDOW = 10000            # Elasticsearch's from+size ceiling, which the page itself caps at
ESTADOS = ("postulacion", "evaluacion", "finalizadas", "todos")
REFUSING_HOST = "www.empleospublicos.cl"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[trabajaenelestado] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # no rules file on the index host; 2 s is ours


def request(body):
    """One POST of the query — (code, text)."""
    gate(SEARCH)
    _PACE.wait()
    req = urllib.request.Request(wire_url(SEARCH), data=json.dumps(body).encode(), method="POST",
                                 headers={"User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{SEARCH}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def query(estado, region, start):
    """The shape the page's own `doSearch()` posts — its `term` filters, its size — with a plain sort in place of its script."""
    must = []
    if estado != "todos":
        must.append({"term": {"Estado": estado}})
    if region:
        must.append({"term": {"Codigo Region": region}})
    return {"from": start, "size": PAGE_SIZE, "track_total_hits": True,
            "sort": [{"Datesum": "asc"}, {"ID Conv.keyword": "asc"}],
            "query": {"bool": {"must": must}} if must else {"match_all": {}}}


def total_of(d):
    t = (d.get("hits") or {}).get("total")
    if isinstance(t, dict):
        t = t.get("value")
    return t if isinstance(t, int) else None


def record(src, es_id=None):
    """The site's `ID Conv` is the id; **28 of 349 records on the day carried none** (the JUNJI feed) — the index's own `_id` stands in, and the record says so."""
    conv = str(src.get("ID Conv") or "").strip()
    ident = conv or (str(es_id).strip() if es_id else "")
    url = (src.get("URL") or "").strip() or None
    return {
        "source": "trabajaenelestado", "country": "CL", "ledger_id": f"trabajaenelestado:{ident}", "id": ident,
        "id_is_index_id": not conv,   # true when the site gave no `ID Conv` and the index's `_id` is used
        "url": url,
        "url_not_fetched": f"{REFUSING_HOST} publishes Disallow: / — the address is the record's own field, never read by this adapter" if url and REFUSING_HOST in url else None,
        "title": (src.get("Cargo") or "").strip() or None,
        "employer": (src.get("Institucion/Entidad") or "").strip() or None,   # the State's own service — the employer
        "ministry": (src.get("Ministerio") or "").strip() or None,
        "region": (src.get("Region") or "").strip() or None, "region_code": src.get("Codigo Region") or None,
        "city": (src.get("Ciudad") or "").strip() or None,
        "area": (src.get("Area de Trabajo") or "").strip() or None,
        "professional_category": (src.get("Cargo Profesional") or "").strip() or None,
        "call_type": src.get("Tipo Convocatoria") or None,
        "application_type": src.get("Tipo Postulacion") or None,
        "opens": src.get("Fecha inicio Convocatoria") or None,          # DD/MM/YYYY H:MM:SS as stored
        "closes": src.get("Fecha cierre Convocatoria") or None,
        "status": src.get("Estado") or None,
        # `Ganador` — the appointed person's name on finished calls — is personal data and is not emitted
        "language": "es",
    }


def cmd_list(a):
    if a.estado not in ESTADOS:
        die(f"--estado {a.estado!r}: the site's states are {', '.join(ESTADOS)}")
    rows, seen, start, pageno, total = [], set(), 0, 0, None
    where = f"(Estado {a.estado}" + (f", {a.region}" if a.region else "") + ")"
    while True:
        pageno += 1
        code, text = request(query(a.estado, a.region, start))
        if code != 200:
            die(f"{SEARCH} (page {pageno}): HTTP {code}", EXIT_PARTIAL if code < 500 else EXIT_PARTIAL)
        try:
            d = json.loads(text)
        except ValueError:
            die(f"{SEARCH} (page {pageno}): not JSON ({len(text)} characters)", EXIT_PARTIAL)
        if total is None:
            total = total_of(d)
            if total is None:
                die(f"{SEARCH}: no `hits.total` in the answer — the index's shape changed; a walk without it is not compared.", EXIT_PARTIAL)
        hits = (d.get("hits") or {}).get("hits") or []
        new = 0
        for h in hits:
            r = record(h.get("_source") or {}, h.get("_id"))
            if not r["id"] or r["id"] in seen:
                continue
            seen.add(r["id"])
            rows.append(r)
            new += 1
        start += PAGE_SIZE
        if not hits or new == 0 or len(rows) >= total:
            break
        if a.pages and pageno >= a.pages:
            break
        if a.limit and len(rows) >= a.limit:
            break
        if start >= WINDOW:
            note(f"the index's window ends at {th(WINDOW)}; {th(total)} stated — the rest is not reachable by paging, as the page itself caps.")
            break
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    bounded = (a.pages and pageno >= a.pages and total > pageno * PAGE_SIZE) or (a.limit and a.limit < total)
    if bounded:
        note(f"{th(n)} emitted of the {th(total)} the index states {where} — {pageno} page(s) of {PAGE_SIZE} walked by request (--pages/--limit), not a shortfall.")
    elif n == total:
        note(f"{th(n)} emitted over {pageno} page(s), index states {th(total)} {where} — equal.")
    else:
        note(f"{th(n)} emitted over {pageno} page(s), index states {th(total)} {where} — {th(abs(total - n))} " + ("short" if total > n else "more emitted than the index states") + ".")
    refusing = sum(1 for r in emitted if r["url_not_fetched"])
    note(f"{th(refusing)} of the {th(n)} addresses are on {REFUSING_HOST}, which says no in writing — every address is emitted as data and none is fetched; there is no `ad` command.")


def main():
    p = argparse.ArgumentParser(description="Trabaja en el Estado — Chile's public-service calls through the Elasticsearch route the page posts to itself; hits.total beside every walk; the appointed person's name never emitted; the refusing host never fetched. Issue #302.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the calls, 36 a page, 2 s apart, 10 pages unless told otherwise")
    l_.add_argument("--estado", default="postulacion", help="postulacion (open — the page's default) · evaluacion · finalizadas · todos")
    l_.add_argument("--region", help="the site's own code — region13 is the Región Metropolitana")
    l_.add_argument("--pages", type=int, default=10)
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
