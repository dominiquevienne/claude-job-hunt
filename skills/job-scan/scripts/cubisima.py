#!/usr/bin/env python3
"""Cubisima Empleos (`www.cubisima.com`) — Cuba's first adapter.

  cubisima.py places
  cubisima.py list --place la_habana [--limit 20]
  cubisima.py list --place la_habana --fetch --since 2026-09-01 [--limit 50]
  cubisima.py ad --id '38600!2'

**One request returns every advertisement id for a province.** The listing
page renders thirty cards and, in the same response, writes the complete
result set into a JavaScript array:

    localStorage.setItem('searchAnuncios', JSON.stringify(["38600!2", …]))

**6 068 ids for La Habana on 2026-09-07**, against pagination that runs to
page 203 — 203 × 30 = 6 090, which is the same set. *So the id list costs one
request and the fields cost one request each; those are different prices and
this module keeps them apart.*

NOTHING HERE IS A GUESSED URL

Cuba's page recorded three open hosts, no declared sitemap and no measurement.
There is still no sitemap. **Every path this module uses is written down by
the site itself:**

    /empleos                         linked from the home page
    /empleos/por-provincias          linked from /empleos
    /empleos/ofertas/-/<place>       linked from /empleos/por-provincias
    /empleos/empleo-api/<id>!<type>  the page's own click handler:
                                     fetch(`…/empleos/empleo-api/${guid}`)

**The `-` in the listing path is the site's own wildcard for «any
category»**, taken from its own links and not invented. *`portaljob-madagascar`
is the counter-case measured the same day: there the route was not declared
anywhere, and guessing one would have been a probe.*

THE CONTACT DETAILS ARE ON `ad` AND NEVER IN A SWEEP

The API returns the poster's e-mail, mobile and WhatsApp number. **`ad` emits
them — that is the advertisement a person is about to answer.** `list --fetch`
does not, at any size.

*The board publishes them either way; the difference is that one is a person
reading one advertisement and the other is this project accumulating a contact
list for a country.* **A field being available is not a reason to carry it.**

WHAT THE LISTING CARD CARRIES WITHOUT ANY FURTHER REQUEST

    title · employer · municipality, province · relative date («Hoy») · views

*The relative date is why `--since` requires `--fetch`*: «Hoy» and «Ayer»
cannot be compared to a date, and turning them into one at read time would
bake this run's clock into the row. `Fecha` from the API is a real timestamp —
`2026-09-07 10:20:26.000`.

NO STRUCTURED DATA, AND NONE NEEDED

`ld+json` and `JobPosting` are absent from every page here. The API supersedes
them: 43 fields, of which the ones this module emits are named below rather
than passed through, because half are internal codes (`CodigoTipoEmpleo`,
`IsConfirmed`, `Visible`) that mean nothing outside the site.

Verified against the live site on 2026-09-07.
"""

import argparse
import html as html_mod
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path
from _ua import UA

BASE = "https://www.cubisima.com"
PROVINCES = BASE + "/empleos/por-provincias"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# `searchAnuncios` holds the whole result set, not the rendered page.
IDS = re.compile(r"searchAnuncios',\s*JSON\.stringify\((\[.*?\])\)", re.S)
CARD = re.compile(r'<div class="card job-listing[^"]*"\s+id="([^"]+)"')
TITLE = re.compile(r'<h5 class="card-title[^"]*"[^>]*>(.*?)</h5>', re.S)
EMPLOYER = re.compile(r'fa-building[^>]*></i>\s*<span[^>]*>(.*?)</span>', re.S)
WHERE = re.compile(r'fa-map-marker-alt[^>]*></i>\s*([^<]{2,60})', re.S)
WHEN = re.compile(r'fa-clock[^>]*></i>\s*([^<&]{2,20})', re.S)
PLACE_LINK = re.compile(r'/empleos/ofertas/-/([^"\']+)["\']')

# **Emitted from the API, named one by one.** The record has 43 fields and
# about half are internal codes that mean nothing outside this site.
FIELDS = {
    "title": "Titulo", "role": "Plaza", "employer": "CodigoEntidad",
    "category": "Categoria", "province": "CodigoEmpleoProvincia",
    "municipality": "CodigoEmpleoMunicipio", "contract": "CodigoTipoContrato",
    "level": "CodigoNivel", "schedule": "Horario", "shift": "JornadaLaboral",
    "salary_text": "SalarioText", "requirements": "Requisitos",
    "details": "Detalles", "employer_activity": "ObjetoSocial",
    "views": "Visitas",
}
# **Present in the response and deliberately not carried in a sweep.**
CONTACT = {"contact_name": "Contacto", "email": "Correo", "phone": "Telefono",
           "mobile": "Movil", "whatsapp": "WhatsApp", "web": "Web",
           "address": "DireccionContacto"}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[cubisima] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# The host declares no `Crawl-delay`; this spacing is ours and declared as ours.
_PACE = Pace("www.cubisima.com", own=1.5)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9",
        "Accept-Language": "es-CU,es;q=0.9,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def clean(s):
    return " ".join(html_mod.unescape(re.sub(r"<[^>]+>", " ", s or "")).split())


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def cmd_places(a):
    places = places_declared()
    if not places:
        die(f"{PROVINCES} declared no place link in {len(page)} characters — "
            f"read the bytes before believing the zero.")
    note(f"{len(places)} place(s) declared by the site. **These are its own "
         f"links**, not a list this module keeps.")
    print(json.dumps({"source": "cubisima", "country": "CU",
                      "places": places}, ensure_ascii=False, indent=1))


def places_declared():
    """The place slugs the site links on its own provinces page."""
    code, page = get(PROVINCES)
    if code != 200:
        die(f"{PROVINCES}: HTTP {code}")
    return list(dict.fromkeys(PLACE_LINK.findall(page)))


def listing(place):
    # **An unknown place is not an empty result — it is the whole country.**
    # `--place zzz_pas_un_lieu` returned 9 486 advertisements, the unfiltered
    # national set, with `"place": "zzz_pas_un_lieu"` printed beside it. *A
    # typo would have produced a number that is real, large, plausible and
    # about the wrong thing*, and nothing in the output would have said so.
    # So the slug is checked against the site's own list before use, at the
    # cost of one request.
    known = places_declared()
    if place not in known:
        near = [k for k in known if fold(place)[:6] in fold(k)][:5]
        die(f"`{place}` is not one of the {len(known)} places this site "
            f"links. **An unknown place does not return nothing here: it "
            f"returns the whole country** — 9 486 advertisements on "
            f"2026-09-07 — under the name you typed. "
            + (f"Closest declared: {', '.join(near)}." if near else
               "Run `places` for the list."))
    url = f"{BASE}/empleos/ofertas/-/{place}"
    code, page = get(url)
    if code != 200:
        die(f"{url}: HTTP {code}")
    m = IDS.search(page)
    if not m:
        die(f"{url}: no `searchAnuncios` array in {len(page)} characters. "
            f"**That array is the whole result set**; without it this module "
            f"would report the thirty rendered cards as the board.")
    ids = json.loads(m.group(1))
    cards, seen = {}, CARD.findall(page)
    for guid in seen:
        i = page.find(f'id="{guid}"')
        block = page[i:i + 1800]
        t, e, w, d = (TITLE.search(block), EMPLOYER.search(block),
                      WHERE.search(block), WHEN.search(block))
        cards[guid] = {
            "title": clean(t.group(1)) if t else None,
            "employer": clean(e.group(1)) if e else None,
            "where": clean(w.group(1)) if w else None,
            # **Relative, and named so.** «Hoy» is not a date and must not be
            # turned into one at read time.
            "posted_relative": clean(d.group(1)) if d else None,
        }
    return url, ids, cards


def api(guid):
    url = f"{BASE}/empleos/empleo-api/{urllib.parse.quote(guid, safe='!')}"
    code, body = get(url)
    # **This API answers an unknown id with 400 and an empty body**, not 404.
    # Treated as gone rather than broken: the request was well formed and the
    # advertisement is not there.
    if code in (400, 404, 410):
        return None, f"gone — HTTP {code}, empty body"
    if code != 200:
        return None, f"HTTP {code}"
    try:
        d = json.loads(body)
    except ValueError as e:
        return None, f"unreadable JSON: {e}"
    return (d.get("data") or d), None


def row(guid, rec, with_contact):
    out = {"source": "cubisima", "id": guid,
           "ledger_id": f"cubisima:{guid}", "countries": ["CU"]}
    for name, key in FIELDS.items():
        v = rec.get(key)
        out[name] = v if v not in ("", "-", None) else None
    # `2026-09-07 10:20:26.000` -> `2026-09-07`, or None. Never a slice of an
    # unrecognised value.
    m = re.match(r"\s*(\d{4}-\d{2}-\d{2})\b", str(rec.get("Fecha") or ""))
    out["posted"] = m.group(1) if m else None
    if with_contact:
        for name, key in CONTACT.items():
            v = rec.get(key)
            out[name] = v if v not in ("", "-", None) else None
    else:
        out["contact_withheld"] = ("this board publishes the poster's e-mail "
                                   "and phone; `ad` emits them, a sweep does "
                                   "not")
    return out


def cmd_list(a):
    url, ids, cards = listing(a.place)
    note(f"{len(ids)} advertisement id(s) for `{a.place}` **from one "
         f"request**, and {len(cards)} card(s) rendered on this page. "
         f"*The array is the whole result set; the cards are one page of it.*")
    if a.since and not a.fetch:
        die("`--since` needs `--fetch`. The card carries a relative date "
            "(«Hoy», «Ayer»), and turning that into a date at read time would "
            "bake this run's clock into the row. `Fecha` from the "
            "advertisement API is a real timestamp.")
    if not a.fetch:
        rows = [dict({"source": "cubisima", "id": g,
                      "ledger_id": f"cubisima:{g}", "countries": ["CU"]},
                     **cards.get(g, {"on_this_page": False}))
                for g in ids]
        if a.limit:
            rows = rows[: a.limit]
        print(json.dumps({"source": "cubisima", "country": "CU",
                          "place": a.place, "advertisements": len(ids),
                          "cards_on_page": len(cards), "returned": len(rows),
                          "note": "fields come from the card for the "
                                  "advertisements rendered on this page; use "
                                  "--fetch for the rest",
                          "ads": rows}, ensure_ascii=False, indent=1))
        return
    todo = ids[: a.limit] if a.limit else ids
    note(f"calling the advertisement API for {len(todo)} of {len(ids)} at "
         f"{_PACE.source()}. **Contact details are withheld in this mode.**")
    kept, broken, dropped = [], [], 0
    for guid in todo:
        rec, why = api(guid)
        if rec is None:
            broken.append((guid, why))
            continue
        r = row(guid, rec, with_contact=False)
        if a.since and (not r["posted"] or r["posted"] < a.since):
            dropped += 1
            continue
        if a.search and fold(a.search) not in fold(r["title"] or ""):
            continue
        kept.append(r)
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{g} ({w})" for g, w in broken[:5]))
    print(json.dumps({"source": "cubisima", "country": "CU", "place": a.place,
                      "advertisements": len(ids), "read": len(todo),
                      "kept": len(kept), "unreadable": len(broken),
                      "filtered_out": dropped, "ads": kept},
                     ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    rec, why = api(a.id)
    if rec is None:
        die(f"{a.id}: {why}",
            EXIT_GONE if (why or "").startswith("gone") else EXIT_BROKEN)
    print(json.dumps(row(a.id, rec, with_contact=True),
                     ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("places", help="the places the site itself links")
    pl.set_defaults(func=cmd_places)

    li = sub.add_parser("list", help="every advertisement id for one place")
    li.add_argument("--place", required=True,
                    help="a slug from `places`, e.g. `la_habana`")
    li.add_argument("--fetch", action="store_true",
                    help="call the advertisement API for each id. **Contact "
                         "details are withheld in this mode**")
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="the advertisement's own `Fecha`. Requires --fetch: "
                         "the card's date is relative")
    li.add_argument("--search", help="match the title; folds accents")
    li.add_argument("--limit", type=int)
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement, contact included")
    ad.add_argument("--id", required=True, help="e.g. `38600!2`")
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
