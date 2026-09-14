#!/usr/bin/env python3
"""Úřad práce ČR (`up.gov.cz`, Czechia) — the public employment service's whole register of vacancies, through the open-data file the Ministry publishes for it (`data.mpsv.cz`), one file a day; the register's own figures printed beside every run; the contact person every record carries never emitted. Issue #350.

  uradprace.py list [--kraj <code|name>] [--okres <code|name>] [--obec <code|name>] [--isco <prefix>] [--profese <text>]
                    [--changed-since YYYY-MM-DD] [--limit N] [--cache DIR]

THE PORTAL'S OWN SEARCH IS BEHIND A WRITTEN REFUSAL — AND THE MINISTRY PUBLISHES THE REGISTER
INSTEAD. `https://up.gov.cz/volna-mista-v-cr` is a Nuxt page whose body is empty on the server
(«Volná místa - hledání», 1 216 076 B, not one vacancy in it): the search is a Polymer web
component (`/app/volna-mista/src/volna-mista-app.js`, 2.8 MB) that first POSTs
`/security-provider/rest/token` and then `/volna-mista/rest/volna-mista/dto/query` — and
`up.gov.cz/robots.txt` writes `User-agent: * / Disallow: */rest/*`. **A written refusal is
honoured by every route; this adapter never sends those requests and has no `ad` command.**

What the same operator publishes in writing for exactly this purpose is the open-data set
«Volná místa za celou ČR» (`https://data.mpsv.cz/web/data/volna-mista-za-celou-cr`, rules
open, certain, no Crawl-delay):

  GET https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json     {"polozky": [39 887 …]}, 189 957 345 B, refreshed once a day («1x denně»)
  GET https://data.mpsv.cz/od/soubory/ciselniky/{kraje,okresy,obce,cz-isco}.json   the code lists the records point into (14 regions, 78 districts, 6 258 municipalities, 1 995 CZ-ISCO codes)

**One file is the whole register — nothing is paged, nothing walked, nothing to be short of;**
the adapter checks the bytes received against `Content-Length` and dies on a short body rather
than count a truncated file. `--cache DIR` keeps the five files and reuses them for 24 hours —
the portal's own `config.json` says `vm.cache.hours = 24` and the set is daily.

THE FIGURES PRINTED (the file's own): postings in the file (`polozky`), positions summed
(`pocetMist`, «Počet nabízených volných míst»), the file's `Last-Modified`. The operator states
the same grandeur monthly — «Ke konci srpna bylo inzerováno celkem 99 274 volných pracovních
míst» (`up.gov.cz/nezamestnanost-v-cesku-srpen-2026`) against 101 207 positions summed here
on 2026-09-13 — a press figure, not fetched by the adapter.

THE RECORD (the set's own names, resolved through the code lists): `portalId` (id — the portal's
address is `https://up.gov.cz/volna-mista-v-cr#/volna-mista-detail/<portalId>`, the app's own
hash route, never fetched), `referencniCislo`, `pozadovanaProfese` (title), `profeseCzIsco`,
`zamestnavatel` (name, IČO — **null with a reason on the 22 records the employer asked to publish
without their identity, `ZverejnovatVpm/anosp`, whose place is withheld too**), `pocetMist`,
`mistoVykonuPrace` (an establishment's address, a municipality, one or more districts, a free
address, the whole country — typed by the set), salary bounds with `typMzdy` (monthly or hourly
— a period, so `salary_unit_stated` is true), hours a week, shift pattern, contract types,
minimum education, suitability, benefits, languages, skills, start and end dates, posted /
changed / expiry, the card and agency flags, and `upresnujiciInformace` as the description,
scrubbed. **`prvniKontaktSeZamestnavatelem` — the contact person's name, e-mail and telephone
— and the establishment's `email`/`telefon` are never emitted; 12 926 descriptions on the day
carried an e-mail address and 8 956 a telephone number: both scrubbed.**

Measured 2026-09-14 01:11 UTC by the declared client, the guard on each exact path:
39 887 postings, 101 207 positions, `Last-Modified: Sun, 13 Sep 2026 20:07:40 GMT`; 36 915
published with the employer, 2 950 EU-wide, 22 anonymous; easy-prace.cz republishes 24 546 of
them (`easyprace.md`) — the file carries 15 341 more.
"""

import argparse
import http.client
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "data.mpsv.cz"
DUMP = f"https://{HOST}/od/soubory/volna-mista/volna-mista.json"
CODELISTS = {"kraje": f"https://{HOST}/od/soubory/ciselniky/kraje.json",
             "okresy": f"https://{HOST}/od/soubory/ciselniky/okresy.json",
             "obce": f"https://{HOST}/od/soubory/ciselniky/obce.json",
             "cz-isco": f"https://{HOST}/od/soubory/ciselniky/cz-isco.json"}
PORTAL = "https://up.gov.cz/volna-mista-v-cr"
CACHE_HOURS = 24          # the portal's own `vm.cache.hours`; the set is refreshed once a day
ANONYMOUS = "ZverejnovatVpm/anosp"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+420[\s ]?|00420[\s ]?)?\d{3}[\s ]?\d{3}[\s ]?\d{3}(?!\d)")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[uradprace] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written on the open-data host; 2 s is ours, and a run is five requests


def request(url):
    """One GET — (code, text, headers). A body shorter than its `Content-Length` is a short file, not a smaller register: exit 6."""
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            raw = r.read()
            headers = r.headers
    except urllib.error.HTTPError as e:
        return e.code, "", e.headers
    except http.client.IncompleteRead as e:
        die(f"{url}: the body stopped after {th(len(e.partial))} bytes — a short file is not a smaller register", EXIT_PARTIAL)
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")
    declared = headers.get("Content-Length")
    if declared and declared.isdigit() and not headers.get("Content-Encoding") and int(declared) != len(raw):
        die(f"{url}: {th(len(raw))} bytes received, Content-Length {th(int(declared))} — a short file is not a smaller register", EXIT_PARTIAL)
    return 200, decode_body(raw, headers)[0], headers


def th(n):
    return f"{n:,}".replace(",", " ")


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def fold(s):
    """Accent-insensitive lower case — «Kralovehradecky» finds «Královéhradecký»."""
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn").casefold()


def fetch_json(url, cache=None, name=None):
    """The file, from `--cache DIR` when younger than CACHE_HOURS, else from the host — (dict, Last-Modified or None, from_cache)."""
    path = os.path.join(cache, name) if cache and name else None
    if path and os.path.exists(path) and time.time() - os.path.getmtime(path) < CACHE_HOURS * 3600:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        return d, None, True
    code, text, headers = request(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    try:
        d = json.loads(text)
    except ValueError:
        die(f"{url}: not JSON ({th(len(text))} characters)", EXIT_PARTIAL)
    if path:
        os.makedirs(cache, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    return d, headers.get("Last-Modified"), False


def load_codes(cache=None):
    """id → name for the four lists, plus the district of each municipality and the region of each district."""
    codes = {"name": {}, "okres_of_obec": {}, "kraj_of_okres": {}}
    for key, url in CODELISTS.items():
        d, _, _ = fetch_json(url, cache, f"{key}.json")
        for it in d.get("polozky") or []:
            codes["name"][it["id"]] = ((it.get("nazev") or {}).get("cs") or "").strip() or None
            if key == "obce" and it.get("okres"):
                codes["okres_of_obec"][it["id"]] = it["okres"]
            if key == "okresy" and it.get("kraj"):
                codes["kraj_of_okres"][it["id"]] = it["kraj"]
    return codes


def tail(ref):
    """`Smennost/jednoSm` → `jednoSm`; the set's ids are `<list>/<code>`."""
    ref = (ref or {}).get("id") if isinstance(ref, dict) else ref
    return ref.split("/", 1)[1] if ref and "/" in ref else (ref or None)


def named(ref, codes):
    ref = (ref or {}).get("id") if isinstance(ref, dict) else ref
    return codes["name"].get(ref) if ref else None


def place(m, codes):
    """The workplace as the set types it — an establishment's address, a municipality, districts, a free address, the country — with region and district resolved through the lists; the establishment's `email`/`telefon` never read."""
    out = {"place_type": None, "workplace_name": None, "street": None, "postal_code": None, "municipality": None, "municipality_code": None,
           "districts": None, "region": None, "region_code": None, "address_text": None}
    if not m:
        return out
    kind = tail(m.get("typMistaVykonuPrace"))
    out["place_type"] = kind
    okres_ids, obec_id = [], None
    if kind == "adrprov":
        w = (m.get("pracoviste") or [None])[0] or {}
        a = w.get("adresa") or {}
        out["workplace_name"] = scrub(w.get("nazev"))
        street = (a.get("ulice") or {}).get("nazev")
        num = "/".join(str(x) for x in (a.get("cisloDomovni"), a.get("cisloOrientacni")) if x)
        out["street"] = " ".join(x for x in (street, num) if x) or None
        out["postal_code"] = a.get("psc") or None
        obec_id = (a.get("obec") or {}).get("id")
        okres_ids = [(a.get("okres") or {}).get("id")] if a.get("okres") else []
        out["region_code"] = tail(a.get("kraj"))
    elif kind == "obec":
        obec_id = (m.get("obec") or {}).get("id")
    elif kind == "okres":
        okres_ids = [o["id"] for o in (m.get("okresy") or []) if o.get("id")]
    elif kind == "adrvolna":
        out["address_text"] = scrub(m.get("adresaText"))
    elif kind == "celaCR":
        out["address_text"] = "celá ČR"
    if obec_id:
        out["municipality"], out["municipality_code"] = codes["name"].get(obec_id), tail(obec_id)
        if not okres_ids and codes["okres_of_obec"].get(obec_id):
            okres_ids = [codes["okres_of_obec"][obec_id]]
    if okres_ids:
        out["districts"] = [codes["name"].get(o) or tail(o) for o in okres_ids]
        if not out["region_code"] and codes["kraj_of_okres"].get(okres_ids[0]):
            out["region_code"] = tail(codes["kraj_of_okres"][okres_ids[0]])
    if out["region_code"]:
        out["region"] = codes["name"].get(f"Kraj/{out['region_code']}")
    return out


def record(it, codes):
    pid = it.get("portalId")
    emp = it.get("zamestnavatel") or {}
    anonymous = tail(it.get("zverejnovat")) == "anosp"
    unit = {"mesic": "month", "hod": "hour"}.get(tail(it.get("typMzdy")))
    smin, smax = it.get("mesicniMzdaOd"), it.get("mesicniMzdaDo")
    langs = [{"language": named(j.get("jazyk"), codes) or tail(j.get("jazyk")), "level": tail(j.get("urovenZnalosti")), "note": scrub(j.get("popis"))} for j in (it.get("pozadovanaJazykovaZnalost") or [])]
    r = {
        "source": "uradprace", "country": "CZ", "ledger_id": f"uradprace:{pid}", "id": str(pid),
        "reference": it.get("referencniCislo") or None,
        "url": f"{PORTAL}#/volna-mista-detail/{pid}",   # the app's own hash route; the record is the file's, the portal is never fetched
        "employer_url": it.get("urlAdresa") or None,
        "title": scrub((it.get("pozadovanaProfese") or {}).get("cs")),   # one profession on the day WAS an e-mail address
        "isco_code": tail(it.get("profeseCzIsco")), "isco": named(it.get("profeseCzIsco"), codes),
        "employer": None if anonymous else ((emp.get("nazev") or "").strip() or None),
        "employer_ico": None if anonymous else (emp.get("ico") or None),
        "employer_withheld": "the employer asked to be published without their identity (ZverejnovatVpm/anosp) — the set carries no name, IČO, address or place for this record" if anonymous else None,
        "positions": it.get("pocetMist"),
        "salary_min": smin, "salary_max": smax, "salary_currency": "CZK" if smin is not None or smax is not None else None,
        "salary_unit": unit if (smin is not None or smax is not None) else None, "salary_unit_stated": bool(unit) and (smin is not None or smax is not None),
        "hours_per_week": it.get("pocetHodinTydne"),
        "shift": tail(it.get("smennost")),
        "contract_types": [tail(v) for v in (it.get("pracovnePravniVztahy") or [])] or None,
        "min_education": tail(it.get("minPozadovaneVzdelani")),
        "suitable_for": [tail(v) for v in (it.get("vhodnostiPracovnihoMista") or [])] or None,
        "benefits": [tail(v.get("vyhoda")) for v in (it.get("vyhodyVolnehoMista") or []) if v.get("vyhoda")] or None,
        "languages": langs or None,
        "skills": [tail(v.get("dovednost")) for v in (it.get("pozadovanaDovednost") or []) if v.get("dovednost")] or None,
        "starts": it.get("terminZahajeniPracovnihoPomeru") or None, "ends": it.get("terminUkonceniPracovnihoPomeru") or None,
        "posted": (it.get("datumVlozeni") or "")[:10] or None, "changed": it.get("datumZmeny") or None, "expires": it.get("expirace") or None,
        "public_administration": it.get("statniSpravaSamosprava"), "blue_card": it.get("modraKarta"), "employee_card": it.get("zamestnaneckaKarta"),
        "non_eu_welcome": it.get("cizinecMimoEu"), "asylum_welcome": it.get("azylant"),
        "agency_placement": bool(it.get("souhlasAgenturyUzivatel")),
        "publication": tail(it.get("zverejnovat")),
        "up_office": tail(it.get("kontaktniPracoviste")),
        "description": scrub((it.get("upresnujiciInformace") or {}).get("cs")),
        # `prvniKontaktSeZamestnavatelem` — the contact person's name, e-mail, telephone and where to report — is never read
        "contacts_withheld": True,
        "language": "cs",
    }
    r.update(place(None if anonymous else it.get("mistoVykonuPrace"), codes))
    return r


def resolve(kind, value, codes):
    """`--kraj 19` or `--kraj praha` → the list's id; nothing matching is an error, never an empty market."""
    prefix = {"kraj": "Kraj/", "okres": "Okres/", "obec": "Obec/"}[kind]
    v = (value or "").strip()
    if not v:
        return None
    if f"{prefix}{v}" in codes["name"]:
        return f"{prefix}{v}"
    hits = [k for k, n in codes["name"].items() if k.startswith(prefix) and n and fold(v) in fold(n)]
    exact = [k for k in hits if fold(codes["name"][k]) == fold(v)]
    hits = exact or hits
    if len(hits) != 1:
        die(f"--{kind} {value!r}: {'no entry' if not hits else str(len(hits)) + ' entries'} in the site's list — " + (", ".join(sorted(codes['name'][k] for k in hits[:12])) if hits else "a code or a name is expected"))
    return hits[0]


def cmd_list(a):
    cache = getattr(a, "cache", None)
    codes = load_codes(cache)
    want = {k: resolve(k, getattr(a, k, None), codes) for k in ("kraj", "okres", "obec")}
    d, modified, cached = fetch_json(DUMP, cache, "volna-mista.json")
    items = d.get("polozky") if isinstance(d, dict) else None
    if not isinstance(items, list):
        die(f"{DUMP}: no `polozky` list in the file — the set's shape changed", EXIT_PARTIAL)
    since = getattr(a, "changed_since", None)
    rows, positions_all = [], 0
    for it in items:
        positions_all += it.get("pocetMist") or 0
        r = record(it, codes)
        if want["kraj"] and r["region_code"] != tail(want["kraj"]):
            continue
        if want["okres"] and (codes["name"][want["okres"]] not in (r["districts"] or [])):
            continue
        if want["obec"] and r["municipality_code"] != tail(want["obec"]):
            continue
        if a.isco and not (r["isco_code"] or "").startswith(a.isco):
            continue
        if a.profese and fold(a.profese) not in fold(r["title"] or ""):
            continue
        if since and (r["changed"] or "")[:10] < since:
            continue
        rows.append(r)
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n, total = len(emitted), len(items)
    filters = [f"--{k} {codes['name'][v]}" for k, v in want.items() if v] + [f"--isco {a.isco}" if a.isco else "", f"--profese {a.profese}" if a.profese else "", f"--changed-since {since}" if since else ""]
    filters = [f for f in filters if f]
    source = "the cached copy (--cache, younger than 24 h)" if cached else f"the file (Last-Modified: {modified or 'not sent'})"
    note(f"{th(total)} posting(s) in {source}, {th(positions_all)} position(s) summed — one file is the whole register, nothing paged.")
    if filters:
        note(f"{th(len(rows))} of them match {' '.join(filters)}.")
    if a.limit and a.limit < len(rows):
        note(f"{th(n)} emitted of the {th(len(rows))} — bounded by --limit, not a shortfall.")
    else:
        note(f"{th(n)} emitted, {th(sum(r['positions'] or 0 for r in emitted))} position(s).")
    note("the contact person every record carries (name, e-mail, telephone) is never emitted; descriptions scrubbed; the portal's own search is behind a written Disallow (*/rest/*) and is never sent — there is no `ad` command.")


def main():
    p = argparse.ArgumentParser(description="Úřad práce ČR — the whole register through the Ministry's open-data file, one file a day; the file's own figures beside every run; the contact person never emitted; the portal's refused search never sent. Issue #350.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the register — 190 MB in one request; --cache DIR keeps it 24 h")
    l_.add_argument("--kraj", help="a region — the site's code (19 is Praha) or a name, accents optional")
    l_.add_argument("--okres", help="a district — code or name")
    l_.add_argument("--obec", help="a municipality — code or name")
    l_.add_argument("--isco", help="a CZ-ISCO prefix, e.g. 25 for ICT professionals")
    l_.add_argument("--profese", help="a word of the profession's name, accents optional")
    l_.add_argument("--changed-since", dest="changed_since", help="YYYY-MM-DD — records changed on or after that day")
    l_.add_argument("--limit", type=int)
    l_.add_argument("--cache", help="a directory that keeps the five files for 24 hours (the set is daily)")
    l_.set_defaults(fn=cmd_list)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
