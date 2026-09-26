#!/usr/bin/env python3
"""CVConnect (`cvconnect.la`), Laos — the country's FIRST adapter. Two of its counters disagree and only one is backed by anything: page 1 states «4 jobs of all 4» and carries four, while every later page states «of all 1700» and carries none. And its class names are swapped — the div called `company-name` holds the job title, the div called `title` holds the employer. Issue #654.

  cvconnect.py jobs [--country-code LA] [--max-pages N]     1 request a page

WHAT IT IS. Laos had **zero** adapters before this one. The board is `search_jobs.php`, served
identically at `/` and at `/search_jobs.php` — the same body to the byte, which is why a
«different» path yields nothing new.

THE RULES. `cvconnect.la` serves its rules file (`state: read`, `certain: True`) on `/` and on
`/search_jobs.php`, writes **no Crawl-delay** (2 s are ours) and declares no sitemap. The guard is
taken on the exact path, query string included.

**A STATED TOTAL THAT NO PAGE SUBSTANTIATES IS NOT A MEASUREMENT.**

    /search_jobs.php?page=1     «Show 1 - 4 jobs of all 4 jobs»        4 adverts
    /search_jobs.php?page=2     «Show 31 - 60 jobs of all 1700 jobs»   0 adverts
    /search_jobs.php?page=3     «Show 61 - 90 jobs of all 1700 jobs»   0 adverts

Pages after the first compute their range at thirty a page and announce **1 700** while carrying
nothing at all. *If the board held 1 700, page 2 would carry thirty.*

> **The danger is not a missing witness: it is two witnesses that each agree with themselves.**
> *An adapter taking «of all N» from any page reports 1 700 against 4 emitted and exits partial for
> ever; one taking page 1 alone is right today and would never learn it was lucky.*

So the stated count is taken **only from a page that carries what it counts**, and the other figure
is **printed anyway** — it is what a future reader will find and believe.

**THIS IS A FOURTH BRANCH OF THE STOP-RULE FAMILY**, beside the clamp (a board that re-serves its
last page), the crush (identical bytes at every page) and the reset (a fall back to the first
slice). **It is the only one where the board never contradicts itself**: «31 - 60 of 1700» is
perfect arithmetic at thirty a page. The single rule that covers all four: **stop on what a page
CARRIES, never on what it STATES.**

**THE CLASS NAMES ARE SWAPPED, AND THE SITE CORROBORATES THE TRUTH ELSEWHERE.**

    <div class="job-des-item-company-name"><h4>ຊ່ວຍຄົວ</h4>       <- the TITLE
    <div class="job-des-item-title"><b><p>IMSOUK SUKI</p>         <- the EMPLOYER

Reading by the site's own marks would swap the two on every record. **What settles it is that the
employer is written in two further places** — the card's `<a alt="…">` and its `<img title="…">` —
and both match `job-des-item-title`. *So «read by what the site marks» needs its own caveat: a mark
is evidence, not proof, and a mark contradicted by two others loses.* The record carries
`employer_corroborated` — how many of those two agreed — so a future change shows up as a number
falling to zero rather than as a silently swapped field.

**AND A SEPARATOR OCCURRING ONCE PER ITEM SEPARATES NOTHING.** The list carries
`<!-- ===== EXPIRED JOBS ===== -->` **four times for four adverts**, once after each: a
per-iteration emission, not a section header. *Nothing is inferred from it — it nearly read as
«three of these four are expired».* **The test is cardinality: as many separators as items means it
separates nothing.** Expiry is read from the date range the site prints, carried as written.

**WITHHELD:** e-mail addresses and telephone numbers in free text. No salary is published on the
card and none is invented.

`--country-code` STAMPS. Titles and places are in Lao and are not translated.

Measured 2026-09-26 00:5x–02:3x UTC by the declared client, the guard on the exact path, two reads:
`/` 200, 26 044 B, md5 1fe44106c0c7, **identical to the byte to `/search_jobs.php`**; the page that
carries its adverts stated **4** — it stated **7** on 2026-09-17, so this count moves about 40 % a
week and **every figure here carries its date**; ids 2519, 2548, 2552, 2565.
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
from _ua import UA

HOST = "cvconnect.la"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
CARD_RE = re.compile(r'<a href="https://cvconnect\.la/jobs/(\d+)/"([^>]*)>(.*?)</a>', re.S)
ALT_RE = re.compile(r'alt="([^"]*)"')
IMG_TITLE_RE = re.compile(r'<img[^>]*title="([^"]*)"')
# **Les deux divs sont NOMMES A L'ENVERS** : voir le docstring. On garde les noms
# du site dans les constantes pour que la contradiction reste lisible ici.
NAMED_COMPANY_RE = re.compile(r'<div class="job-des-item-company-name">(.*?)</div>', re.S)
NAMED_TITLE_RE = re.compile(r'<div class="job-des-item-title">(.*?)</div>', re.S)
PLACE_RE = re.compile(r'<div class="job-des-item-cat">(.*?)</div>', re.S)
# Deux `-time` par carte : distingues par l'ICONE que le site pose, jamais par l'ordre.
TIME_RE = re.compile(r'<div class="job-des-item-time"><p[^>]*>\s*<i[^>]*>(\w+)</i>\s*(.*?)</p>', re.S)
STATED_RE = re.compile(r"Show\s+([\d,]+)\s*-\s*([\d,]+)\s+jobs\s+of\s+all\s+([\d,]+)\s+jobs", re.I)
SEPARATOR_RE = re.compile(r"=+\s*EXPIRED JOBS\s*=+")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[cvconnect] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    # **LE TEXTE D'UNE ICONE N'EST PAS DU CONTENU.** Le site rend ses pictogrammes
    # en police a ligatures — `<i class="material-icons">location_on</i>` — donc un
    # strip de balises ordinaire laisse « location_on » COLLE devant le lieu. La
    # sortie reste lisible et fausse : « location_on Ban Sibounhueng ».
    t = re.sub(r"<i\b[^>]*>.*?</i>", " ", markup or "", flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>", " ", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return " ".join(t.split()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def first_group(rx, s):
    m = rx.search(s or "")
    return m.group(1) if m else None


def stated_of(body):
    """(first, last, total) as the page writes it, or None."""
    m = STATED_RE.search(body or "")
    return tuple(int(x.replace(",", "")) for x in m.groups()) if m else None


def cards_of(body):
    out = []
    for ident, attrs, inner in CARD_RE.findall(body or ""):
        employeur = text(first_group(NAMED_TITLE_RE, inner))
        titre = text(first_group(NAMED_COMPANY_RE, inner))
        # Les deux marques qui corroborent l'employeur, et le COMPTE qu'elles font.
        corrobore = [x.strip() for x in (first_group(ALT_RE, attrs), first_group(IMG_TITLE_RE, inner))
                     if x and x.strip()]
        temoins = sum(1 for c in corrobore if employeur and c == employeur.strip())
        age = dates = None
        for icone, val in TIME_RE.findall(inner):
            if icone == "timer":
                age = text(val)
            elif icone == "date_range":
                dates = text(val)
        out.append({"id": ident, "title": titre, "employer": employeur,
                    "employer_corroborated": temoins,
                    "place": text(first_group(PLACE_RE, inner)),
                    "age": age, "dates": dates})
    return out


def record(c, stamp):
    return {
        "source": "cvconnect", "country": stamp,
        "ledger_id": f"cvconnect:{c['id']}", "id": c["id"],
        "url": f"https://{HOST}/jobs/{c['id']}/",
        "title": scrub(c["title"]), "employer": scrub(c["employer"]),
        # combien des deux marques independantes confirment l'employeur (0, 1 ou 2)
        "employer_corroborated": c["employer_corroborated"],
        "place": scrub(c["place"]), "posted_age": c["age"], "dates": c["dates"],
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    rows, seen, page = [], set(), 0
    porte, sans_contenu, separateurs, cartes = None, [], 0, 0
    while True:
        page += 1
        url = f"https://{HOST}/search_jobs.php?page={page}"
        code, body = request(url)
        if code == 404:
            die(f"{url}: HTTP 404", EXIT_GONE)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        st = stated_of(body)
        found = cards_of(body)
        if page == 1 and "list-group-item" not in body:
            die(f"{url}: 200 without a single card — the list changed shape", EXIT_PARTIAL)
        if not found:
            # **On s'arrete sur ce que la page PORTE, jamais sur ce qu'elle ANNONCE** —
            # et l'annonce d'une page vide se dit quand meme.
            if st:
                sans_contenu.append((page, st[2]))
            break
        if st and porte is None:
            porte = st[2]                    # le seul enonce adosse a du contenu
        separateurs += len(SEPARATOR_RE.findall(body))
        cartes += len(found)
        neufs = 0
        for c in found:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            rows.append(record(c, stamp))
            neufs += 1
        if not neufs:
            die(f"page {page} repeats the previous page's adverts — the walk ended at {len(rows)}", EXIT_PARTIAL)
        if a.max_pages and page >= a.max_pages:
            break

    for r in rows:
        print(json.dumps(r, ensure_ascii=False))

    plafonne = bool(a.max_pages and page >= a.max_pages)
    pleines = page if plafonne else page - 1
    note(f"{len(rows)} emitted over {pleines} page(s) that carried adverts"
         + (" — stopped by --max-pages" if plafonne else "")
         + f"; the first page CARRYING its adverts states {porte}.")
    for p, tot in sans_contenu:
        note(f"page {p} states «of all {tot} jobs» and carries NOTHING — not a measurement of this"
             f" board, printed because a future reader will find that figure and believe it.")
    if separateurs and separateurs == cartes:
        note(f"the «EXPIRED JOBS» separator occurs {separateurs} times for {cartes} advert(s) — as"
             f" many as there are items, so it separates nothing; expiry is read from `dates`.")
    faibles = [r["id"] for r in rows if r["employer_corroborated"] < 1]
    if faibles:
        note(f"{len(faibles)} advert(s) whose employer is corroborated by NEITHER the link's alt nor"
             f" the image's title ({', '.join(faibles[:5])}) — the class names are swapped on this"
             f" board, so an uncorroborated employer may be a title.")
    if stamp:
        note(f"country {stamp} is the user's stamp.")
    if porte is not None and not plafonne and len(rows) != porte:
        die(f"{len(rows)} emitted against {porte} stated by the page that carries them", EXIT_PARTIAL)


def main(argv=None):
    p = argparse.ArgumentParser(description="CVConnect (Laos) — the stated count is taken only from a page that carries what it counts; the class names are swapped and the employer is corroborated twice. Issue #654.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the list, 1 request a page")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0, help="stop after N pages (0 = until a page carries none)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
