#!/usr/bin/env python3
"""Fetch Spanish public-sector announcements from Empléate — oposiciones.

The second index behind `empleate.gob.es`, and a different board from
`empleate.py` in every way that matters. **1 558 live announcements**, ~3 438
posts, from `open/publicoffersearch/selectBuscador`.

  GET /empleate/open/publicoffersearch/selectBuscador   → Solr, open, no key
       ?q=*&wt=json&rows=100&fq=speStateId:1
  https://empleate.gob.es/empleo/#/trabajoPublico?search=<id>   → the ad

**No browser, no account, no key.** Same `robots.txt` as the sibling: nine
lines, `Allow: /`, six logged-in paths closed, no crawler named.

Everything below was measured against the live index on 2026-09-01.

THE FIELD THAT NAMES THE DEADLINE IS A CONSTANT. `estadoPlazoF` reads
**"Abierto" on all 76 050 records** — including the 74 492 the same index marks
`Inactiva`, and including announcements whose closing date passed in 2025. It
is not a status; it is a string that is always there.

On a board of competitive examinations that is the whole object. Nobody applies
to an oposición they cannot enter. So the closing date is **computed from
`fechaPresentacion` and never read from `estadoPlazo`** — and the arithmetic is
not academic: **498 of the 1 558 live announcements (32%) have a deadline that
has already passed**, every one of them stamped "Abierto".

By default this adapter drops them and says how many it dropped.
`--incluir-cerradas` keeps them, marked.

THE SIBLING'S HABIT RETURNS AN EMPTY BOARD HERE. `empleate.py` relies on the
server injecting `(speStateId:1 OR speStateId:4)` whenever a request carries
any `fq`, and sends `checkVisible:1` for the sole purpose of triggering it.

**This endpoint injects nothing, and has no `checkVisible` field.** The same
call returns:

  publicoffersearch  fq=checkVisible:1  → 0 ads, echoed back unchanged
  publicoffersearch  fq=speStateId:1    → 1 558
  publicoffersearch  no fq              → 76 050, of which 74 492 inactive

Two adjacent endpoints on one host with opposite contracts, and neither
announces which it is. Here the live filter is **ours to supply** — there is no
safety net, and forgetting it returns 98% dead records rather than the 79% the
sibling would. So it is asserted in the echoed parameters on every response.

*(The same divergence runs the other way too: `fq=comunidadF:CASTILLA LEON`,
unquoted, answers `FAIL!` on the sibling and 1 509 here. Values are quoted
regardless.)*

IT IS NOT A NATIONAL BOARD IN PRACTICE. 1 334 of the 1 558 live records come
from **CIDO**, the Diputació de Barcelona's register, and **1 291 of the 1 391
that carry a province are Catalan** — Barcelona 965, Tarragona 161, Girona 104,
Lleida 61. Madrid has 42. The index is national; what is live in it is Catalan
local government. Every run says so.

AND THERE IS NO AD TEXT. `contenido` is one line — median **118 characters**,
longest 289. What the record carries is the title, the hiring body, the
civil-service group, the access route and the date. The notice itself lives on
`cido.diba.cat` or `administracion.gob.es`. `cover-letter` will have nothing to
read here and should be told so rather than left to invent.

Usage:
  oposiciones.py provincias
  oposiciones.py organismos --provincia BARCELONA
  oposiciones.py search --provincia BARCELONA --grupo A1
  oposiciones.py search --desde 2026-08-01 --dias-restantes 7

Output: one JSON object per line.
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta

BASE = "https://empleate.gob.es"
API = BASE + "/empleate/open/publicoffersearch/selectBuscador"
# The site's own share link for a public offer, read out of its `getOfferLink`
# / `FBshareOffer` pair: EURES, SNE, WEB and MISOS ads get `#/oferta/<id>`,
# everything in this index gets the search page pinned to the id. There is no
# per-ad page on empleate.gob.es for an oposición — the card links straight
# out to the partner.
AD_URL = BASE + "/empleo/#/trabajoPublico?search={}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

ROWS = 100

# Ours to supply. This endpoint injects nothing — see the module docstring.
LIVE_FQ = "speStateId:1"

# What the partner links are, and what reading them would cost. Neither host
# refuses us, so this is not the `empleate.md` case — but `administracion.gob.es`
# publishes a Crawl-delay of 60 seconds and a Visit-time window of 01:00–06:45
# GMT, which no unattended fetch here could honour. The link is for the user to
# click, not for a script to follow.
SOURCE_HOSTS = {
    "administracion.gob.es":
        "robots.txt: Crawl-delay 60, Visit-time 0100-0645 GMT",
    "cido.diba.cat":
        "no robots.txt published (connection refused on /robots.txt)",
}

# open/master/allgroups. A1/A2/B/C1/C2/E are the funcionario grades,
# GP1–GP5 the laboral ones.
GROUPS = ("A1", "A2", "B", "C1", "C2", "E",
          "GP1", "GP2", "GP3", "GP4", "GP5", "S/E F", "S/E L")

CATALAN_PROVINCES = ("BARCELONA", "TARRAGONA", "GIRONA", "LLEIDA")

# `provinciaF` is not always the post's province. Measured across all 1 558
# live records: **42 carry a province and a region that cannot both be true**,
# and all 42 of them are `provinciaF: MADRID` with `comunidadF: CATALUÑA` —
# Catalan posts advertised by nationally-seated bodies (Ineco, Tragsatec, a
# ministry), where CIDO has filled the province with the organisation's seat.
#
# The consequence is the trap a user actually hits: **`--provincia MADRID`
# returns 42 jobs, none of them in Madrid.** The 50 real Madrid-region records
# carry no province at all and are reachable only through
# `--comunidad MADRID`.
PROVINCE_TRAPS = {
    "MADRID": ("all 42 live records with provinciaF:MADRID are Catalan posts "
               "from nationally-seated bodies. The 50 real Madrid-region "
               "announcements carry no province at all — use "
               "--comunidad MADRID instead, or as well"),
}

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def geo_disagrees(c):
    """True when the record's province and region cannot both be right."""
    p, r = (c.get("province") or ""), (c.get("region") or "")
    if not p or not r:
        return False
    return (p in CATALAN_PROVINCES) != (r.upper() == "CATALUÑA")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[oposiciones] {msg}", file=sys.stderr)


def fetch(url, retries=2):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json",
        "Accept-Language": "es-ES,es;q=0.9",
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as exc:
            if attempt == retries:
                die(f"{url}: {exc}")
            time.sleep(1.5 * (attempt + 1))
    return ""


def check_live_filter(params, url):
    """The live filter is ours, and this endpoint will not add it back.

    Its absence is 76 050 records instead of 1 558, 74 492 of them inactive —
    a board 49 times its real size. Checked on every response so that a change
    at the far end is a hard error rather than a plausible result.
    """
    echoed = params.get("fq", "")
    if LIVE_FQ not in echoed:
        die(f"the live filter is missing. The server echoed fq={echoed!r}, "
            f"which does not contain {LIVE_FQ}. Without it this endpoint "
            "returns 76 050 records, 74 492 of them inactive — it injects "
            f"nothing of its own.\n  {url}")


def solr(fq, rows=ROWS, start=0, sort=None, **extra):
    if "checkVisible" in fq:
        # empleate.py's base clause. There is no such field in this index: it
        # is echoed back unchanged and matches nothing at all.
        die("fq must not use checkVisible — that field does not exist in the "
            "public index and the clause returns 0 ads with no error. The "
            f"live filter here is {LIVE_FQ}. Got: {fq!r}")
    if LIVE_FQ not in fq:
        fq = f"{LIVE_FQ} AND {fq}" if fq else LIVE_FQ
    params = {"q": "*", "wt": "json", "rows": min(rows, ROWS),
              "start": start, "fq": fq}
    if sort:
        params["sort"] = sort
    params.update(extra)
    url = API + "?" + urllib.parse.urlencode(params)
    body = fetch(url)
    try:
        data = json.loads(body)
    except ValueError:
        die(f"the endpoint answered {body[:80]!r} — not JSON, on what is "
            f"very likely an HTTP 200.\n  {url}")
    check_live_filter(data.get("responseHeader", {}).get("params", {}), url)
    return data


def facet(field, fq="", limit=100):
    d = solr(fq, rows=0, facet="true", **{"facet.field": field,
                                          "facet.limit": str(limit)})
    ff = d.get("facet_counts", {}).get("facet_fields", {}).get(field, [])
    return [(name, n) for name, n in zip(ff[0::2], ff[1::2]) if n]


def text_of(html):
    return WS_RE.sub(" ", TAG_RE.sub(" ", html or "")).strip()


def day_of(stamp):
    return (stamp or "")[:10] or None


def host_of(url):
    if not url or url in ("#", "-"):
        return None
    m = re.match(r"^https?://(?:www\.)?([^/]+)", url)
    return m.group(1) if m else None


def card(d, today):
    ident = d.get("id")
    # `getOfferLink` in the site's own bundle treats "-" and "#" as absent.
    src = d.get("url")
    src = src if (src and src not in ("#", "-")) else None
    host = host_of(src)
    deadline = day_of(d.get("fechaPresentacion"))
    passed, left = None, None
    if deadline:
        passed = deadline < today
        try:
            left = (datetime.strptime(deadline, "%Y-%m-%d").date()
                    - datetime.strptime(today, "%Y-%m-%d").date()).days
        except ValueError:
            left = None
    return {
        "id": ident,
        "ledger_id": "oposiciones:{}".format(ident),
        "url": AD_URL.format(ident),
        "title": d.get("titulo"),
        # The hiring body, on every record measured — better than the private
        # board, where the employer is named on 29%.
        "company": d.get("organismo"),
        "unit": d.get("unidad"),
        "reference": d.get("externalId"),
        "source": d.get("origen"),
        "source_url": src,
        "source_url_host": host,
        "source_url_fetch_constraints": SOURCE_HOSTS.get(host),
        "province": d.get("provinciaF"),
        "region": d.get("comunidadF"),
        "scope": d.get("ambitoGeograficoF"),
        "latlon": d.get("localizacion"),
        # The application deadline. Computed state only — see below.
        "deadline": deadline,
        "deadline_passed": passed,
        "days_left": left,
        # "Abierto" on all 76 050 records in the index, live or not, expired
        # or not. Carried so nobody rediscovers it, never used.
        "deadline_status_field_literal": d.get("estadoPlazoF"),
        # Identical to `deadline` on 500 of 500 measured. Kept for the same
        # reason.
        "publication_end_literal": d.get("fechaFinPublicacionFormateada"),
        "group": d.get("grupoF"),
        "staff_type": d.get("personalF"),
        "access_route": d.get("tipoAccesoF"),
        "education": d.get("educacionF"),
        "positions": d.get("trabajosOfertados") or None,
        "published": d.get("fechaCreacionPortal"),
        "state": d.get("speState"),
        # One line, median 118 characters. This is not a job description and
        # must not be presented as one: the notice is on the source site.
        "summary": text_of(d.get("contenido")),
        "has_full_text": False,
    }


def quoted(value):
    return '"{}"'.format(str(value).replace('"', ""))


def build_fq(a):
    parts = []
    if a.provincia:
        parts.append("provinciaF:({})".format(
            " OR ".join(quoted(p) for p in a.provincia)))
    if a.comunidad:
        parts.append("comunidadF:({})".format(
            " OR ".join(quoted(c) for c in a.comunidad)))
    if a.grupo:
        parts.append("grupoF:({})".format(
            " OR ".join(quoted(g) for g in a.grupo)))
    if a.acceso:
        parts.append("tipoAccesoF:({})".format(
            " OR ".join(quoted(x) for x in a.acceso)))
    if a.personal:
        parts.append("personalF:({})".format(
            " OR ".join(quoted(x) for x in a.personal)))
    if a.ambito:
        parts.append("ambitoGeograficoF:({})".format(
            " OR ".join(quoted(x) for x in a.ambito)))
    if a.organismo:
        parts.append("organismo:{}".format(quoted(a.organismo)))
    if a.texto:
        parts.append("titulo:{}".format(quoted(a.texto)))
    if a.desde:
        parts.append(
            "fechaCreacionPortal:[{}T00:00:00Z TO *]".format(a.desde))
    return " AND ".join(parts)


def warn_province_traps(a):
    for p in (a.provincia or []):
        warning = PROVINCE_TRAPS.get(str(p).upper())
        if warning:
            note("--provincia {}: {}.".format(p, warning))


def sweep(a, today):
    warn_province_traps(a)
    fq = build_fq(a)
    # The deadline filter is applied in the query when it can be, because it
    # removes a third of the index before anything is read.
    if not a.incluir_cerradas:
        floor = today
        if a.dias_restantes:
            floor = (datetime.strptime(today, "%Y-%m-%d").date()
                     + timedelta(days=a.dias_restantes)).isoformat()
        clause = "fechaPresentacion:[{}T00:00:00Z TO *]".format(floor)
        fq = f"{fq} AND {clause}" if fq else clause
    first = solr(fq, rows=ROWS, sort="fechaPresentacion asc")
    total = first["response"]["numFound"]
    note("{} announcements match — fq={}".format(total, fq))
    if total == 0:
        note("a real zero: the live filter was applied and echoed back. Note "
             "that only 1 558 of the index's 76 050 records are live, and "
             "1 060 of those still have an open deadline.")
        return None
    want = a.limit or total
    docs, start = list(first["response"]["docs"]), 0
    while len(docs) < want and start + len(first["response"]["docs"]) < total:
        start += ROWS
        page = solr(fq, rows=ROWS, start=start, sort="fechaPresentacion asc")
        got = page["response"]["docs"]
        if not got:
            note("page at start={} came back empty, stopping at {} of {}"
                 .format(start, len(docs), total))
            break
        docs.extend(got)
        time.sleep(a.delay)
    return docs[:want], total


def report(cards, a):
    closed = sum(1 for c in cards if c["deadline_passed"])
    if a.incluir_cerradas:
        note("{} of {} have a deadline that has already passed — kept because "
             "--incluir-cerradas was given, and marked deadline_passed. The "
             "board's own estadoPlazoF calls every one of them \"Abierto\"."
             .format(closed, len(cards)))
    else:
        note("closed announcements were excluded in the query. 498 of the "
             "1 558 live records have an expired deadline, and the board "
             "stamps all of them \"Abierto\" — the date is the only truth "
             "here. Pass --incluir-cerradas to see them.")
    soon = [c for c in cards if c["days_left"] is not None
            and 0 <= c["days_left"] <= 7]
    if soon:
        note("{} close within 7 days.".format(len(soon)))
    # `provinciaF` and `comunidadF` disagree on 42 of the 1 558 live records,
    # and the disagreement is systematic rather than scattered — see
    # `CATALAN_PROVINCES` above and the note in cmd_search.
    bad = [c for c in cards if geo_disagrees(c)]
    if bad:
        note("{} of {} carry a province and a region that cannot both be "
             "right — e.g. {!r} in province {} but region {}. On this board "
             "`provinciaF` sometimes holds the hiring body's seat rather than "
             "the post's location. Trust the title."
             .format(len(bad), len(cards), (bad[0]["title"] or "")[:60],
                     bad[0]["province"], bad[0]["region"]))
    cat = sum(1 for c in cards
              if c["region"] and "CATALU" in c["region"].upper())
    if cat:
        note("{} of {} are in Catalonia. That is the board, not the query: "
             "1 334 of its 1 558 live records come from CIDO, the Diputació "
             "de Barcelona's register.".format(cat, len(cards)))
    thin = sum(1 for c in cards if len(c["summary"]) < 200)
    note("{} of {} carry under 200 characters. There is no ad text in this "
         "index at all — median 118 characters — so cover-letter has nothing "
         "to read and the notice must be opened at the source."
         .format(thin, len(cards)))


def cmd_search(a):
    today = a.hoy or date.today().isoformat()
    got = sweep(a, today)
    if not got:
        return
    docs, total = got
    cards = [card(d, today) for d in docs]
    for c in cards:
        print(json.dumps(c, ensure_ascii=False))
    note("{} announcements returned of {} matching".format(len(cards), total))
    report(cards, a)


def cmd_discover(a):
    today = a.hoy or date.today().isoformat()
    got = sweep(a, today)
    if not got:
        return
    docs, total = got
    for d in docs:
        print(json.dumps({
            "id": d.get("id"),
            "ledger_id": "oposiciones:{}".format(d.get("id")),
            "url": AD_URL.format(d.get("id")),
            "title": d.get("titulo"),
            "company": d.get("organismo"),
            "province": d.get("provinciaF"),
            "deadline": day_of(d.get("fechaPresentacion")),
            "group": d.get("grupoF"),
        }, ensure_ascii=False))
    note("{} announcements listed of {} matching".format(len(docs), total))


def cmd_provincias(a):
    rows = facet("provinciaF", limit=100)
    for name, count in rows:
        print(json.dumps({"provincia": name, "live": count},
                         ensure_ascii=False))
    listed = sum(c for _, c in rows)
    total = solr("", rows=0)["response"]["numFound"]
    note("{} provinces, {} of {} live announcements placed. The other {} are "
         "national or international in scope."
         .format(len(rows), listed, total, total - listed))
    note("This board is Catalan in practice — see the counts above.")


def cmd_organismos(a):
    fq = 'provinciaF:{}'.format(quoted(a.provincia[0])) if a.provincia else ""
    for name, count in facet("organismo", fq=fq, limit=60):
        print(json.dumps({"organismo": name, "live": count},
                         ensure_ascii=False))


def cmd_grupos(a):
    for name, count in facet("grupoF", limit=30):
        print(json.dumps({"grupo": name, "live": count}, ensure_ascii=False))
    note("A1–E are the funcionario grades, GP1–GP5 the laboral ones. "
         "open/master/allgroups is the code table.")


def cmd_accesos(a):
    for f, label in (("tipoAccesoF", "acceso"), ("personalF", "personal"),
                     ("ambitoGeograficoF", "ambito")):
        for name, count in facet(f, limit=30):
            print(json.dumps({label: name, "live": count}, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    for name, fn, h in (("provincias", cmd_provincias,
                         "provinces with live counts"),
                        ("grupos", cmd_grupos,
                         "civil-service groups with live counts"),
                        ("accesos", cmd_accesos,
                         "access route, staff type and scope"),
                        ("organismos", cmd_organismos,
                         "the hiring bodies, optionally in one province")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--provincia", action="append")
        c.add_argument("--delay", type=float, default=0.3)
        c.set_defaults(func=fn)

    for name, fn, h in (("discover", cmd_discover, "ids, titles, deadlines"),
                        ("search", cmd_search, "the full records")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--provincia", action="append",
                       help="uppercase, as the board writes it. "
                            "`provincias` lists them")
        c.add_argument("--comunidad", action="append")
        c.add_argument("--grupo", action="append",
                       help="civil-service group — A1, C2, GP1. `grupos`")
        c.add_argument("--acceso", action="append",
                       help="'Ingreso libre', 'Interinidad', "
                            "'Contratación fija'. `accesos`")
        c.add_argument("--personal", action="append",
                       help="'Personal Funcionario', 'Personal Laboral'")
        c.add_argument("--ambito", action="append",
                       help="Local, Autonómico, Nacional, Internacional")
        c.add_argument("--organismo", help="phrase in the hiring body's name")
        c.add_argument("--texto", help="phrase in the title")
        c.add_argument("--desde", metavar="YYYY-MM-DD",
                       help="published on or after this date")
        c.add_argument("--dias-restantes", dest="dias_restantes", type=int,
                       help="keep only announcements still open in N days — "
                            "use it when a dossier takes time to assemble")
        c.add_argument("--incluir-cerradas", dest="incluir_cerradas",
                       action="store_true",
                       help="keep announcements whose deadline has passed. "
                            "498 of the 1 558 live records are in that state, "
                            "all of them stamped \"Abierto\"")
        c.add_argument("--hoy", metavar="YYYY-MM-DD",
                       help="treat this as today. For testing")
        c.add_argument("--limit", type=int)
        c.add_argument("--delay", type=float, default=0.3)
        c.set_defaults(func=fn)

    a = p.parse_args()
    if a.cmd in ("search", "discover") and not (
            a.provincia or a.comunidad or a.grupo or a.acceso or a.personal
            or a.ambito or a.organismo or a.texto or a.desde or a.limit):
        die("give --provincia, --comunidad, --grupo, --acceso, --personal, "
            "--ambito, --organismo, --texto, --desde or --limit. Without one "
            "the sweep is every open announcement in Spain — 1 060 of them, "
            "and 965 in the province of Barcelona alone.")
    a.func(a)


if __name__ == "__main__":
    main()
