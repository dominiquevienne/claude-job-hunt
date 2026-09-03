#!/usr/bin/env python3
"""Fetch Spanish ads from Empléate — the SEPE's national job board.

**28 099 live ads**, the first Spanish board in this repository and the third
national public employment service after `job-room.md` (CH) and
`france-travail.md` (FR). One request returns **100 complete ads, full text
included**: there is no per-ad fetch, which makes this the cheapest board here
per ad.

  GET /robots.txt                                → Allow: /, six private paths closed
  GET /empleate/open/offersearch/selectBuscador  → Solr, open, no key
  https://empleate.gob.es/empleo/#/oferta/<id>   → the ad, for a human

**No browser, no account, no key.** `robots.txt` closes only the logged-in
areas — `/empleo/perfil/`, `/empleo/empresas/` — and names no crawler at all.

Everything below was measured against the live index on 2026-09-01.

THREE WAYS THIS ENDPOINT LIES QUIETLY. All three answer HTTP 200.

1. **Omit `fq` and you get 131 510 ads, of which 103 411 are dead.** The
   server injects the live filter `(speStateId:1 OR speStateId:4)` only when
   the request already carries an `fq` — with none, it applies none, and
   returns the whole index including every expired and withdrawn ad. Four
   times the board, well-formed, no warning. This adapter therefore always
   sends an `fq` and **verifies the injection came back** in
   `responseHeader.params.fq`; see `check_live_filter`.

2. **`FAIL!` is a 200 with `Content-type: application/json`.** A five-byte
   body that is not JSON. It is what the endpoint returns for an `fq` its
   validator rejects — an unquoted value containing a space
   (`comunidadF:CASTILLA LEON`), or any clause mentioning `speStateId`
   alongside another. A client that treats a parse failure as "no results"
   reports an empty board. Values are quoted here, `speStateId` is never sent,
   and a non-JSON body is a hard error.

3. **`rows` is capped at 100 in silence.** Ask for 1 000 and the response
   echoes `"rows":"100"` and carries 100 docs. A client paging `start += 1000`
   while receiving 100 reads **10% of the board** and reports a full sweep.
   Paging here advances by the number of documents actually returned.

A fourth, of a rarer species: **`url:"#"` matches all 28 099 ads.** SNE ads
store the literal `"#"` in `url`, which tokenises to nothing, so the clause is
a no-op that reads like a precise filter. The usual sitemap failure returns
zero; this one returns everything.

WHAT THE BOARD IS. Thirteen feeds, not one. SNE (9 819) is the regional
employment services, INSERTIA (7 235) and COGITI (3 285) are partner networks,
WEB (2 319) is Empléate's own direct-application ads. **TECNO_EMPLEO (2 436) is
Tecnoempleo**, whose own `robots.txt` refuses six Anthropic agents and which
`shared/robots-policy.md` rules out entirely. Reading it *here* is reading a
Spanish public register, not tecnoempleo.com — but the ad's `url` field points
back at that host, so this adapter never emits it as the ad URL and marks it
`source_url_do_not_fetch`. The full text is in the record regardless.

AGE. "Live" on this board means "not withdrawn", not "still hiring": **8 106 of
28 099 (29%) were posted over a year ago, 4 326 over three**, the oldest in
2020. Every run reports that split for what it returned. `--desde` is a
correctness control here, not an optimisation.

Usage:
  empleate.py provincias
  empleate.py fuentes
  empleate.py search --provincia MADRID --desde 2026-08-01
  empleate.py search --texto "desarrollador java" --limit 40
  empleate.py discover --comunidad "CATALUÑA" --desde 2026-08-25

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

from _decode import decode_body
from _robots import allowed as robots_allowed

BASE = "https://empleate.gob.es"
API = BASE + "/empleate/open/offersearch/selectBuscador"
MASTER = BASE + "/empleate/open/master/"
AD_URL = BASE + "/empleo/#/oferta/{}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# Trap 3. The server's own ceiling; asking for more is answered with 100 and
# an echoed `"rows":"100"`, never an error.
ROWS = 100

# Trap 1. The filter the site's own front end sends, and which the server
# injects when — and only when — the request carries an `fq` of its own.
LIVE_FQ = "(speStateId:1 OR speStateId:4)"

# The clause that is always safe to send: it changes nothing (28 099 with and
# without it) and its only job is to be present, so the injection happens.
BASE_FQ = "checkVisible:1"

# Hosts `shared/robots-policy.md` has already ruled out. Empléate carries
# their ads legitimately — it is a public register they chose to feed — but
# the `url` field on those records points at the refused host, and nothing
# downstream may follow it.
REFUSED_HOSTS = ("tecnoempleo.com", "infojobs.net")

# `modality`, from open/master/modalities. 25 790 of 28 099 are "0".
MODALITY = {"0": None, "1": "presencial", "2": "a distancia",
            "3": "teletrabajo", "4": "mixto"}

# `tipoContratoN`, from open/master/contracttypes.
CONTRACT = {"0": "sin especificar", "1": "laboral indiferente",
            "2": "laboral indefinido", "3": "laboral temporal",
            "4": "mercantil", "5": "en prácticas",
            "6": "formación y aprendizaje"}

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
# `,` followed by exactly two digits at the end is the Spanish decimal comma;
# `,` followed by three is an English thousands separator. Both occur in the
# same field. See `money`.
DECIMAL_RE = re.compile(r"^(\d+),(\d{2})$")
THOUSANDS_RE = re.compile(r"^(\d{1,3}(?:,\d{3})+)$")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def _robots_gate(url, tag, exit_code=7):
    """Ask before fetching — per host and **per path**. Issues #100, #101.

    `verdict()` answers *is this host closed in one block*. **A site that
    refuses its ad path while leaving its root open passes that and refuses
    every advertisement** — `empleate.gob.hn` does exactly that, closing
    `/Vacantes/` to `User-agent: *` with `/` absent.

    It sits **inside the fetch function**, so every request is covered rather
    than the first one, and a refusal **stops the command** with exit 7 and the
    module's own words. **This adapter decides nothing about what a refusal
    means** — deciding is what turns a check into a decoration.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return None
    a = robots_allowed(parts.netloc, parts.path or "/")
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", exit_code)
    if a.get("requested_host") and a["host"] != a["requested_host"]:
        print(f"[empleate] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts. A platform that has "
              f"been renamed reaches an adapter this way before it reaches it "
              f"as a rename.", file=__import__("sys").stderr)
    return a



def note(msg):
    print(f"[empleate] {msg}", file=sys.stderr)


def fetch(url, retries=2):
    _robots_gate(url, 'empleate')
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json",
        "Accept-Language": "es-ES,es;q=0.9",
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return decode_body(r.read(), r.headers)[0]
        except (urllib.error.URLError, OSError) as exc:
            if attempt == retries:
                die(f"{url}: {exc}")
            time.sleep(1.5 * (attempt + 1))
    return ""


def check_live_filter(params, url):
    """Trap 1. The live filter must come back in the echoed parameters.

    Its absence is not "fewer ads" — it is 131 510 instead of 28 099, four
    fifths of them expired. Nothing downstream can tell the difference, so it
    is checked here and it is fatal.
    """
    echoed = params.get("fq", "")
    if not echoed.startswith(LIVE_FQ):
        die("the live filter was not applied. The server echoed "
            f"fq={echoed!r}, which does not start with {LIVE_FQ}. Without it "
            "the endpoint returns the whole index — 131 510 ads, four fifths "
            f"of them expired — with no error at all.\n  {url}")


def solr(fq, rows=ROWS, start=0, sort=None, **extra):
    if "speStateId" in fq:
        # Trap 2. The server passes an `fq` mentioning speStateId through
        # unvalidated and then rejects it with `FAIL!`. The live filter is the
        # server's job, never ours.
        die(f"fq must not mention speStateId — the server injects "
            f"{LIVE_FQ} itself and answers FAIL! otherwise. Got: {fq!r}")
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
        # Trap 2. 200, `Content-type: application/json`, body `FAIL!`.
        die(f"the endpoint answered {body[:80]!r} — a 200 with an "
            "application/json content type and a body that is not JSON. "
            "That is how it rejects an fq: an unquoted value containing a "
            "space, or a clause naming speStateId. It is not an empty "
            f"board.\n  {url}")
    check_live_filter(data.get("responseHeader", {}).get("params", {}), url)
    return data


def facet(field, fq=BASE_FQ, limit=100):
    d = solr(fq, rows=0, facet="true", **{"facet.field": field,
                                          "facet.limit": str(limit)})
    ff = d.get("facet_counts", {}).get("facet_fields", {}).get(field, [])
    return list(zip(ff[0::2], ff[1::2]))


def text_of(html):
    return WS_RE.sub(" ", TAG_RE.sub(" ", html or "")).strip()


def money(raw):
    """Read a salary figure, both notations, and say which one was read.

    The same field holds `16200,00` (Spanish decimal comma) and `19,500`
    (English thousands separator). Applying either rule to both is wrong by a
    factor of a thousand in one direction or the other: `19,500` read as
    Spanish is €19.50 a year, `16200,00` read as English is €1 620 000. The
    separator is disambiguated by what follows it — two digits or three — and
    anything that matches neither is returned unparsed rather than guessed.
    """
    if raw in (None, "", "0"):
        return None, None
    s = str(raw).strip()
    m = DECIMAL_RE.match(s)
    if m:
        return float(f"{m.group(1)}.{m.group(2)}"), "decimal comma"
    if THOUSANDS_RE.match(s):
        return float(s.replace(",", "")), "thousands comma"
    if s.isdigit():
        return float(s), "plain"
    return None, f"unparsed: {s!r}"


def host_of(url):
    if not url or url in ("#", "-"):
        return None
    m = re.match(r"^https?://(?:www\.)?([^/]+)", url)
    return m.group(1) if m else None


def card(d):
    ident = d.get("id")
    src = d.get("url")
    # Trap 4's cousin: `#` is stored as a value, not as an absent field.
    src = src if (src and src not in ("#", "-")) else None
    host = host_of(src)
    refused = bool(host and any(host.endswith(h) for h in REFUSED_HOSTS))
    smin, smin_how = money(d.get("salarioMin"))
    smax, smax_how = money(d.get("salarioMax"))
    return {
        "id": ident,
        "ledger_id": "empleate:{}".format(ident),
        # Always the register's own page. Never `url`: on 2 436 ads that is
        # tecnoempleo.com, which shared/robots-policy.md rules out, and the
        # full text is in this record anyway.
        "url": AD_URL.format(ident),
        "title": d.get("titulo"),
        # Present on 8 010 of 28 099 only. On SNE ads — 9 819, the largest
        # feed — there is no employer field at all: the application route is
        # an office or an email written inside the description.
        "company": d.get("creador"),
        "company_id": d.get("companyContact"),
        "source_feed": d.get("entitytype"),
        "source_url": src,
        "source_url_host": host,
        "source_url_do_not_fetch": refused,
        "province": d.get("provinciaF"),
        "region": d.get("comunidadF"),
        "city": d.get("ciudadF"),
        # 9 432 of 28 099. `ciudad` is an INSEE-like municipal code, not a
        # postcode; `cp` is the postcode.
        "postcode": d.get("cp"),
        "latlon": d.get("localizacion"),
        "country": d.get("paisF"),
        "category": d.get("categoriaF"),
        "subcategory": d.get("subcategoriaF"),
        "sector": d.get("sectorF"),
        "contract": CONTRACT.get(str(d.get("tipoContratoN")),
                                 d.get("tipoContratoN")),
        "working_time": d.get("jornadaF"),
        # 25 790 of 28 099 are "No informado". This board does not tell you
        # whether a job is remote; 110 ads in the whole index say so.
        "modality": MODALITY.get(str(d.get("modality"))),
        "education": d.get("educacionF"),
        "education_required": d.get("educacionReqF"),
        "experience": d.get("experienciaF"),
        "min_experience_years": d.get("minExperiencia"),
        "positions": d.get("trabajosOfertados"),
        "disability_friendly": d.get("discapacidad"),
        "salary_min": smin,
        "salary_max": smax,
        "salary_min_raw": d.get("salarioMin"),
        "salary_max_raw": d.get("salarioMax"),
        "salary_read_as": smin_how or smax_how,
        "salary_currency": "EUR" if (smin or smax) else None,
        "published": d.get("fechaCreacionPortal"),
        "created": d.get("fechaCreacion"),
        "state": d.get("speState"),
        "contact_email": d.get("email") if d.get("verMail") else None,
        "description": text_of(d.get("contenido")),
        "requirements": text_of(d.get("oReq")),
        "training_required": text_of(d.get("formacionReq")),
        "driving_licence": d.get("carneConducir"),
        "schedule": d.get("horario"),
        "duration": d.get("duracion"),
    }


def quoted(value):
    """Trap 2. An unquoted value with a space is answered with `FAIL!`."""
    return '"{}"'.format(str(value).replace('"', ""))


def build_fq(a):
    parts = [BASE_FQ]
    if a.provincia:
        parts.append("provinciaF:({})".format(
            " OR ".join(quoted(p) for p in a.provincia)))
    if a.comunidad:
        parts.append("comunidadF:({})".format(
            " OR ".join(quoted(c) for c in a.comunidad)))
    if a.categoria:
        parts.append("categoriaF:({})".format(
            " OR ".join(quoted(c) for c in a.categoria)))
    if a.fuente:
        parts.append("entitytype:({})".format(
            " OR ".join(quoted(f) for f in a.fuente)))
    if a.sin_fuente:
        for f in a.sin_fuente:
            parts.append("-entitytype:{}".format(quoted(f)))
    if a.texto:
        parts.append("titulo:{}".format(quoted(a.texto)))
    if a.desde:
        parts.append(
            "fechaCreacionPortal:[{}T00:00:00Z TO *]".format(a.desde))
    return " AND ".join(parts)


def sweep(a):
    fq = build_fq(a)
    first = solr(fq, rows=ROWS, sort="fechaCreacionPortal desc")
    total = first["response"]["numFound"]
    note("{} live ads match — fq={}".format(total, fq))
    if total == 0:
        note("nothing matched. The filter was applied (the server echoed it), "
             "so this is a real zero, not a rejected query.")
        return
    want = a.limit or total
    docs, start = list(first["response"]["docs"]), 0
    while len(docs) < want and start + len(first["response"]["docs"]) < total:
        # Trap 3. Advance by what came back, never by what was asked for.
        start += ROWS
        page = solr(fq, rows=ROWS, start=start, sort="fechaCreacionPortal desc")
        got = page["response"]["docs"]
        if not got:
            note("page at start={} came back empty, stopping at {} of {}"
                 .format(start, len(docs), total))
            break
        docs.extend(got)
        time.sleep(a.delay)
    return docs[:want], total


def age_report(cards, total):
    dated = [c["published"][:10] for c in cards if c.get("published")]
    if not dated:
        return
    cutoff_1y, cutoff_3y = "2025-09-01", "2023-09-01"
    old1 = sum(1 for d in dated if d < cutoff_1y)
    old3 = sum(1 for d in dated if d < cutoff_3y)
    note("age of what was returned: {} of {} posted over a year ago, {} over "
         "three. This board keeps withdrawn-but-not-deleted ads: 8 106 of its "
         "28 099 live ads are over a year old. Use --desde."
         .format(old1, len(dated), old3))


def cmd_search(a):
    got = sweep(a)
    if not got:
        return
    docs, total = got
    cards = [card(d) for d in docs]
    refused = 0
    for c in cards:
        if c["source_url_do_not_fetch"]:
            refused += 1
        print(json.dumps(c, ensure_ascii=False))
    note("{} ads returned of {} matching".format(len(cards), total))
    age_report(cards, total)
    if refused:
        note("{} of them are syndicated from a host shared/robots-policy.md "
             "rules out — the ad URL emitted is empleate.gob.es and the full "
             "text is in the record; source_url_do_not_fetch marks them so "
             "nothing follows the link.".format(refused))
    thin = sum(1 for c in cards if len(c["description"]) < 200)
    if thin:
        note("{} of {} carry under 200 characters of description — the "
             "PORTALENTO and CASTILLA_Y_LEON feeds are largely a title and a "
             "line.".format(thin, len(cards)))


def cmd_discover(a):
    got = sweep(a)
    if not got:
        return
    docs, total = got
    for d in docs:
        print(json.dumps({
            "id": d.get("id"),
            "ledger_id": "empleate:{}".format(d.get("id")),
            "url": AD_URL.format(d.get("id")),
            "title": d.get("titulo"),
            "province": d.get("provinciaF"),
            "published": d.get("fechaCreacionPortal"),
            "source_feed": d.get("entitytype"),
        }, ensure_ascii=False))
    note("{} ads listed of {} matching".format(len(docs), total))


def cmd_provincias(a):
    rows = facet("provinciaF", limit=100)
    for name, count in rows:
        print(json.dumps({"provincia": name, "live_ads": count},
                         ensure_ascii=False))
    listed = sum(c for _, c in rows)
    total = solr(BASE_FQ, rows=0)["response"]["numFound"]
    note("{} provinces, {} ads. {} of {} live ads carry no province at all — "
         "mostly remote and syndicated listings."
         .format(len(rows), listed, total - listed, total))


def cmd_comunidades(a):
    for name, count in facet("comunidadF", limit=50):
        print(json.dumps({"comunidad": name, "live_ads": count},
                         ensure_ascii=False))


def cmd_categorias(a):
    for name, count in facet("categoriaF", limit=60):
        print(json.dumps({"categoria": name, "live_ads": count},
                         ensure_ascii=False))


def cmd_fuentes(a):
    for name, count in facet("entitytype", limit=50):
        sample = solr("entitytype:{}".format(quoted(name)), rows=1)
        docs = sample["response"]["docs"]
        host = host_of(docs[0].get("url")) if docs else None
        refused = bool(host and any(host.endswith(h) for h in REFUSED_HOSTS))
        print(json.dumps({"fuente": name, "live_ads": count,
                          "off_site_host": host,
                          "host_refuses_us": refused}, ensure_ascii=False))
        time.sleep(a.delay)
    note("thirteen feeds, not one board. The `host_refuses_us` ones are read "
         "here — a Spanish public register — and never at the source; see "
         "shared/robots-policy.md.")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    for name, fn, h in (("provincias", cmd_provincias,
                         "the 52 provinces and their live counts"),
                        ("comunidades", cmd_comunidades,
                         "the 19 autonomous communities and their counts"),
                        ("categorias", cmd_categorias,
                         "the 23 job categories and their counts"),
                        ("fuentes", cmd_fuentes,
                         "the feeds behind the board, and which hosts "
                         "refuse us at the source")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--delay", type=float, default=0.3)
        c.set_defaults(func=fn)

    for name, fn, h in (("discover", cmd_discover, "ids, titles and URLs"),
                        ("search", cmd_search, "the full ads")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--provincia", action="append",
                       help="province as the board writes it, uppercase — "
                            "MADRID, BARCELONA, 'A CORUÑA'. Repeatable. "
                            "List them with `provincias`")
        c.add_argument("--comunidad", action="append",
                       help="autonomous community — 'CATALUÑA', "
                            "'CASTILLA LEON'. Repeatable")
        c.add_argument("--categoria", action="append",
                       help="category as `categorias` prints it. Repeatable")
        c.add_argument("--fuente", action="append",
                       help="keep only this feed — SNE, WEB, INSERTIA. "
                            "Repeatable")
        c.add_argument("--sin-fuente", action="append", dest="sin_fuente",
                       help="drop this feed. Repeatable")
        c.add_argument("--texto", help="phrase in the title")
        c.add_argument("--desde", metavar="YYYY-MM-DD",
                       help="fechaCreacionPortal >= this date. Strongly "
                            "recommended: 8 106 of the 28 099 live ads are "
                            "over a year old")
        c.add_argument("--limit", type=int)
        c.add_argument("--delay", type=float, default=0.3)
        c.set_defaults(func=fn)

    a = p.parse_args()
    if a.cmd in ("search", "discover") and not (
            a.provincia or a.comunidad or a.categoria or a.fuente
            or a.texto or a.desde or a.limit):
        die("give --provincia, --comunidad, --categoria, --texto, --desde or "
            "--limit. Without one the sweep is all 28 099 live ads, and 8 106 "
            "of those were posted over a year ago.")
    a.func(a)


if __name__ == "__main__":
    main()
