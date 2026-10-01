#!/usr/bin/env python3
"""İş Kıbrıs (`www.iskibris.com`), Northern Cyprus: the reference portal — and **its two lists of facets have the SAME SIZE and DIFFERENT MEMBERS**, so the route is their union and no board total is established. Issue #719.

  iskibris.py jobs [--country-code CY] [--max N]      the union of the facet pages, 1 request each

WHAT IT IS. Northern Cyprus's main job portal (Next.js). The country's other named boards are
`kibriseleman`, `kktcportal`, `kibristailan`, `kariyerkktc` and `ekonomikibris` (#718–#726).

THE RULES. `www.iskibris.com` serves its rules file (`state: read`, `certain: True`) — `Allow: /*`,
**no Crawl-delay**, 2 s are ours — and declares `https://www.iskibris.com/sitemap.txt`, a TEXT
sitemap of 20 lines.

**THE ADVERTS ARE NOT WHERE THE SITEMAP PUTS THEM, AND NOT ON `/jobs`.** *The sitemap holds **zero**
`/jobs/<id>` entries: 20 section pages and nothing else.* And `/jobs` — the page an adapter would
reach for — ships `pageProps` containing **only an empty `query`**: no advert link, no `ld+json`, no
pager. *Its `__NEXT_DATA__` is empty of content because the page fetches its list in the browser.*
**Counting links there returns zero, and that zero says nothing about the board.**

Where they ARE: **`/quick-links/<slug>`, rendered server-side**, each shipping a Laravel paginator
in `__NEXT_DATA__` — `data` (24 adverts), `total`, `per_page`, `last_page`, `current_page`,
`next_page_url`.

**AND THE TWO LISTS OF SLUGS HAVE THE SAME SIZE AND DIFFERENT MEMBERS.** *Measured 2026-10-01:*

    sitemap /quick-links        12 slugs   6 sectors + 6 DISTRICTS
    homepage `jobsStats`        12 slugs   the same 6 sectors + 6 OTHER facets
    intersection                 6
    union                       18

> **Twelve against twelve is the most seductive form of this trap: equal cardinals invite the
> inference even harder than unequal ones.** *Neither list contains the other — six district pages
> exist only in the sitemap, and `education`, `health`, `internship`, `mass-media`, `part-time`,
> `student` only in the homepage's counters.* **So the run reads BOTH at runtime and walks their
> union**, which also means it follows the site if either list changes.

**NO BOARD TOTAL IS ESTABLISHED, AND THE SUM OF THE COUNTERS IS NOT ONE.** *The homepage's twelve
counters summed to 315 on 2026-09-18 and to 301 on 2026-10-01 — but they count FACETS, not adverts:*
`sales-jobs` is a sector while `part-time-jobs` is an employment type and `jobs-in-kyrenia` a
district, **so one advert is counted by several of them**. *A sum over overlapping facets is not a
count of anything.* **What IS a witness is each slug's own stated `total`**, and the run reports
emitted-against-stated per slug.

**THE PAGER IS CLAMPED — `?page=2` RE-SERVES PAGE 1.** *Measured: `/quick-links/sales-jobs?page=2`
returns `current_page: 1` and the identical 24 ids.* The page's `getServerSideProps` forwards only
the slug to the API, so **the HTML route yields page 1 and nothing more**. The run therefore asks
each slug exactly once and says how far short of the stated total it fell — *it never loops on a
pager that cannot advance*, which is the clamp branch of this repository's stop-rule family.

**AND THE REST IS ON A HOST THAT REFUSES US.** `next_page_url` names
`https://api.iskibris.com/api/jobs/quick-links?page=2`. *That host serves its own rules file
(`state: read`, `certain: True`, no `Disallow`, no Crawl-delay) — **the rules open it** — and the
application answers **403, 1 558 B, `<title>Forbidden</title>`, md5 `46e4fde5d0ba` IDENTICAL on two
reads.* **A STABLE fingerprint: this is a bare application refusal, not an anti-robot challenge**,
so borne 2 is not engaged — and it is not defeated either. *On an API host a blocked entry is
technical (token, session), which is not ours to adjudicate.* **The adapter never calls it.**

**WITHHELD:** e-mail addresses and telephone numbers in free text. *The list payload carries no
contact field at all* — no e-mail, no telephone — and `contacts_withheld` records that we would have
withheld one. **There is no salary field anywhere in the payload**, so neither the currency rule nor
the telephone-digits rule has anything to act on here; both are noted so the next reader does not
look for a bug in their absence.

`--country-code` STAMPS. Titles are Turkish; `custom_title_translation` is the site's own English
title when it sets one, and nothing is translated by us.

**AND THE RUN'S OWN OVERLAP FIGURES ARE DOWNSTREAM OF THE CLAMP.** *Measured 2026-10-01 over the
18 facets: 77 of 187 adverts were served by more than one facet; of the six districts, **0** adverts
appeared under two at once and **98** under none.* **That looks like «disjoint but not exhaustive»,
and the clamp forbids concluding it**: an advert past position 24 of its district page is invisible
to this route, so «under no district» is inflated, and the zero is consistent with disjointness
without establishing it. *A witness downstream of a filter cannot see the filter* — and the only
thing that could settle it is the API host, which refuses us. **The run says all of this rather than
publishing the tidier half.**

Measured 2026-10-01 by the declared client, the guard taken on each exact path and separately on the
API host: `/robots.txt` 200 (`Allow: /*`, sitemap declared); `/sitemap.txt` 200, 893 B, 20 lines,
**0 adverts**; `/jobs` 200 ×2, 79 431 / 79 443 B (a generated MUI class name moves), **0 advert
links**; `/` 200, 111 489 B, 12 counters summing 301, `featuredJobs` empty with
`featuredJobsError: False` — *a zero the site itself disambiguates*; `/quick-links/sales-jobs` 200,
168 558 B, 24 adverts, `total: 49`, `last_page: 3`; the same with `?page=2` → `current_page: 1`,
identical ids.
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

HOST = "www.iskibris.com"
SITEMAP = "/sitemap.txt"
API_HOST = "api.iskibris.com"          # refuse notre client : 403 statique, jamais appele
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
NEXT_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json"[^>]*>(.*?)</script>', re.S)
SLUG_RE = re.compile(r"/quick-links/([\w-]+)")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[iskibris] {msg}", file=sys.stderr)


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
        # **`api.iskibris.com` tombe ici, et c'est voulu.** Ses regles OUVRENT, mais
        # l'application rend un 403 statique (md5 stable sur deux lectures) : un refus
        # applicatif sur un hote d'API, qui n'est pas de notre ressort. On ne l'appelle pas.
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)                                   # sur le CHEMIN exact, hote compris
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # aucun Crawl-delay ecrit
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,text/plain",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def text(x):
    """Le texte d'un champ, l'ELEMENT `<i>` retire et non sa seule balise.

    Les champs de ce board sont du JSON sans balisage, donc la clause `<i>` n'y
    mord pas — elle est posee quand meme parce qu'une police d'icones met son
    glyphe DANS l'element, et que 136 adaptateurs sur 138 portent ce defaut.
    """
    if not isinstance(x, str):
        return None
    t = re.sub(r"<i\b[^>]*>.*?</i>", " ", x, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmlmod.unescape(t).replace("\xa0", " ")
    return " ".join(t.split()) or None


def charge(markup):
    """`__NEXT_DATA__`, decode — la page porte sa charge la, pas dans son balisage."""
    m = NEXT_RE.search(markup or "")
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except ValueError:
        return {}


def slugs_du_sitemap(corps):
    """Les facettes que le SITEMAP declare — 6 secteurs et 6 districts le 2026-10-01."""
    return list(dict.fromkeys(SLUG_RE.findall(corps or "")))


def slugs_de_l_accueil(pp):
    """Les facettes que l'ACCUEIL compte — **pas les memes**, et autant.

    `jobsStats` melange des secteurs et des TYPES d'emploi, donc ses cles
    recoupent celles du sitemap sans les contenir.
    """
    st = pp.get("jobsStats")
    return list(st.keys()) if isinstance(st, dict) else []


def record(a, slug, stamp):
    jt = a.get("job_title") if isinstance(a.get("job_title"), dict) else {}
    ident = a.get("id")
    return {
        "source": "iskibris", "country": stamp,
        "ledger_id": f"iskibris:{ident}", "id": str(ident) if ident is not None else None,
        "url": f"https://{HOST}/jobs/{ident}" if ident is not None else None,
        "title": scrub(text(a.get("title"))),
        "title_en": scrub(text(a.get("custom_title_translation")) or text(jt.get("titleEN"))),
        "employer": scrub(text(a.get("company_name"))),
        "employer_logo": a.get("company_logo") or None,
        "location": text(a.get("city_name")) or text(a.get("place_name")),
        "education": text(a.get("education_name")),
        "cv_required": bool(a.get("is_cv_required")) if a.get("is_cv_required") is not None else None,
        "status": a.get("status"),
        "posted": a.get("created_at"),
        "updated": a.get("updated_at"),
        "facet": slug,                      # la facette par laquelle on l'a RENCONTREE
        # **Aucun champ de contact dans la charge** : ni courriel ni telephone. Le drapeau
        # dit ce que NOUS aurions retenu, il ne pretend pas qu'on ait retenu quelque chose.
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    if a.max is not None and a.max < 0:
        die("--max: a count, or 0 for every advert the facets name")
    stamp = a.country_code.upper() if a.country_code else None

    code, sm = request(f"https://{HOST}{SITEMAP}")
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    du_sitemap = slugs_du_sitemap(sm)

    code, home = request(f"https://{HOST}/")
    if code != 200:
        die(f"/: HTTP {code}", EXIT_PARTIAL)
    pp_home = charge(home).get("props", {}).get("pageProps", {})
    de_l_accueil = slugs_de_l_accueil(pp_home)

    # **L'UNION, et l'intersection DITE** : deux listes de meme taille aux membres
    # differents ne se distinguent par aucun cardinal.
    union, origine = [], {}
    for source, lot in (("sitemap", du_sitemap), ("accueil", de_l_accueil)):
        for s in lot:
            if s in origine:
                origine[s] += "+" + source
                continue
            origine[s] = source
            union.append(s)
    commun = sum(1 for v in origine.values() if "+" in v)
    if not union:
        die(f"https://{HOST}: neither the sitemap nor the home page names a facet"
            f" — they changed shape; this is not an empty board", EXIT_PARTIAL)

    vus, rows, manques, clampes = set(), [], 0, 0
    enonce, emis_par_slug = {}, {}
    # **Les appartenances, pour MESURER si une famille de facettes est disjointe** au lieu
    # de le supposer : la somme d'une famille n'est un temoin que si ses membres ne se
    # recouvrent pas ET couvrent tout.
    appartenances = {}
    for slug in union:
        if a.max and len(rows) >= a.max:
            break
        url = f"https://{HOST}/quick-links/{urllib.parse.quote(slug)}"
        code, page = request(url)
        if code != 200:
            manques += 1
            note(f"{slug}: HTTP {code} — facet skipped")
            continue
        pp = charge(page).get("props", {}).get("pageProps", {})
        jobs = pp.get("jobs")
        if not isinstance(jobs, dict):
            manques += 1
            note(f"{slug}: 200 but no paginator in __NEXT_DATA__ — the page changed shape")
            continue
        if pp.get("jobsFetchError"):
            # Le site DIT que sa propre requete a echoue : ce n'est pas un zero du board.
            manques += 1
            note(f"{slug}: the page reports jobsFetchError — not an empty facet")
            continue
        enonce[slug] = jobs.get("total")
        data = jobs.get("data") or []
        # **Le pager est verrouille par construction** : on ne demande jamais de page 2.
        # Ce controle est PROSPECTIF — il dira le jour ou le site se mettra a avancer.
        if jobs.get("last_page") and jobs.get("last_page") > 1:
            clampes += 1
        n_slug = 0
        for x in data:
            if not isinstance(x, dict) or x.get("id") is None:
                continue
            appartenances.setdefault(x["id"], set()).add(slug)
            if x["id"] in vus:
                n_slug += 1                 # une annonce est comptee par plusieurs facettes :
                continue                    # deja emise ailleurs, mais bien servie par CELLE-CI
            # **Le plafond se teste ICI AUSSI, pas seulement entre facettes.** Teste au seul
            # tour de boucle exterieur, `--max 6` emettait les 24 annonces de la premiere
            # facette avant de s'arreter : le drapeau ne voulait pas dire ce qu'il annonce,
            # et rien dans la sortie ne le signalait.
            if a.max and len(rows) >= a.max:
                break                       # **sans incrementer** : ce qui n'est pas servi
            n_slug += 1                     # ne doit pas compter comme servi
            vus.add(x["id"])
            r = record(x, slug, stamp)
            r["facet_origin"] = origine[slug]
            rows.append(r)
            print(json.dumps(r, ensure_ascii=False))   # AU FIL DE L'EAU
        emis_par_slug[slug] = n_slug
        if a.max and len(rows) >= a.max:
            break

    plafonne = bool(a.max and len(rows) >= a.max)
    note(f"{th(len(rows))} distinct advert(s) emitted over {th(len(emis_par_slug))} facet(s)"
         + (f", {manques} facet(s) unreadable" if manques else "")
         + (" — stopped by --max" if plafonne else ""))
    note(f"the facets: the sitemap names {th(len(du_sitemap))}, the home page counts"
         f" {th(len(de_l_accueil))}, {th(commun)} in common, {th(len(union))} distinct."
         f" **Same size, different members — neither list contains the other**, so the run walks"
         f" their union and no cardinal would have revealed the gap.")
    manque_total = [(s, enonce[s], emis_par_slug.get(s, 0)) for s in enonce
                    if isinstance(enonce[s], int) and emis_par_slug.get(s, 0) < enonce[s]]
    if plafonne:
        # **UN MANQUE SOUS `--max` EST NOTRE PLAFOND, PAS CELUI DU BOARD.** Le dire en
        # manque de board serait un faux temoin fabrique par notre propre option — et il
        # se lirait exactement comme un manque mesure.
        note("stopped by --max, so NOTHING is said here about what the facets serve:"
             " any shortfall at this point is this run's cap, not the board's pager."
             " Re-run without --max for the pager's own verdict.")
    elif manque_total:
        court = sum(t - e for _s, t, e in manque_total)
        note(f"**{len(manque_total)} facet(s) served fewer than they state, {th(court)} advert(s)"
             f" short in total — THE PAGER IS CLAMPED**: `?page=2` re-serves page 1 (measured"
             f" 2026-10-01), so the HTML route carries the first page of each facet and no more."
             f" The remainder is on {API_HOST}, whose rules OPEN but whose application answers a"
             f" static 403 — a technical refusal on an API host, never defeated, never called.")
        for s, t, e in manque_total[:6]:
            note(f"    {s}: {e} emitted, the facet states {t}")
    if not clampes:
        note("no facet declared more than one page this run — if that holds, the clamp no longer"
             " costs anything and this note is the place that will say so.")
    note("the sum of the home page's counters is NOT a board total: they count overlapping facets"
         " (sector, employment type, district), so one advert is counted by several.")
    # **Et on MESURE le recouvrement plutot que de l'affirmer** — y compris pour la seule
    # famille qui pourrait porter un total : les districts.
    if appartenances and not plafonne:
        districts = {s for s in union if s.startswith("jobs-in-")}
        multi = sum(1 for v in appartenances.values() if len(v) > 1)
        d_multi = sum(1 for v in appartenances.values() if len(v & districts) > 1)
        d_aucun = sum(1 for v in appartenances.values() if not (v & districts))
        somme_d = sum(enonce[s] for s in districts if isinstance(enonce.get(s), int))
        note(f"overlap MEASURED, not assumed: {th(multi)} of {th(len(appartenances))} adverts were"
             f" served by more than one facet.")
        note(f"and the one family that could carry a total — the {len(districts)} districts,"
             f" stating {th(somme_d)} between them — does NOT:"
             f" {d_multi} advert(s) appear under two districts at once"
             f" and {d_aucun} under none (the payload's city can read «Diğer», other)."
             f" **Disjoint AND exhaustive is what a sum needs, and neither holds here**, so this"
             f" run states no board total and the per-facet figures above are the only witnesses.")
        note("AND BOTH OF THOSE FIGURES ARE MEASURED DOWNSTREAM OF THE CLAMP, which is a limit on"
             " THIS witness and not on the board: an advert past position 24 of its district page"
             " is invisible here, so «under no district» is inflated by the clamp, and «under two"
             " districts: 0» is consistent with disjointness without establishing it — a witness"
             " downstream of a filter cannot see the filter. Only the API host, which refuses us,"
             " could settle either.")
    note("no salary field exists in this payload, so neither the currency rule nor the"
         " telephone-digits rule has anything to act on; said so that their absence reads as"
         " measured rather than forgotten.")
    if stamp:
        note(f"country {stamp} is the user's stamp.")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="İş Kıbrıs (Northern Cyprus) — the union of the facet pages, because the "
                    "sitemap's list and the home page's list have the same size and different "
                    "members. The pager is clamped and the API host refuses us. Issue #719.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the union of the facet pages, 1 request each")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on every record (the board states none)")
    j.add_argument("--max", type=int, default=0,
                   help="stop after N distinct adverts (0 = every advert the facets serve)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
