#!/usr/bin/env python3
"""Sweep About SVG's job posts (Saint Vincent and the Grenadines) over plain HTTP.

    aboutsvg.py jobs --max-pages 4
    aboutsvg.py jobs --per-page 50 --no-site-witness

**THE ISSUE THAT ASKED FOR THIS ADAPTER DESCRIBED A ROUTE THAT NO LONGER
EXISTS, AND THE PREMISE IS THE FIRST THING THIS FILE RECORDS.** #733 measured,
on 2026-09-18, a `/jobs` page of **755 823 bytes whose served markup carried
the advertisements themselves** — employer links `/business/<slug>`, «&nbsp;##
HOW TO APPLY&nbsp;», 17 dated entries. Measured again 2026-11-04: that page is
**15 074 bytes with 437 characters of visible text**, and `/business/`,
`ACADO`, `LiAT`, `Coreas`, `Mustique` and `HOW TO APPLY` return **zero
occurrences each**. The site was rebuilt into a Vite + TanStack Router shell.
*The two md5 that differ at identical size are the «rendered element that
moves» the issue already noted — not an unstable board.*

WHERE THE DATA IS, AND IT IS A SECOND HOST. The bundle
`/assets/index-c9kot8E3.js` declares ``Wx=`https://api-next.aboutsvg.com` ``.
So the guard that matters is taken on THAT host (§3 bis: `robots.txt` binds a
HOST, not a brand), and it answers **404 on its own `robots.txt`** — `state:
absent`, `certain: True`, which is KNOWLEDGE and not an ignorance — while
`/api/health` answers `200 {"message": "API is healthy."}`.

    GET https://api-next.aboutsvg.com/api/collections/posts/records
        ?filter=(postType='job')&expand=business&sort=-postDate&perPage=50&page=N

**AND `postType` IS `job`, SINGULAR, WHERE THE INTERFACE SECTION IS `jobs`.**
The bundle's section table is `{food:food, jobs:jobs, events:events,
deals:deals, business:businesses, outage:outages}`; the records discriminate on
another field entirely. Composing the plural returns nothing, and nothing in
the answer says why.

THREE CANDIDATE ROUTES WERE REFUTED, not abandoned: `/api/browse?section=jobs`
→ `404 {"message": "The requested resource wasn't found."}`, the same by POST →
`404`, and `/api/collections/listings/records` → `404 {"message": "Missing
collection context."}`. The collection id `pbc_1125843985` was **extracted from
an image URL in the page**, never guessed, and it is what named `posts`.

TWO WITNESSES, AND THEY ARE COMPARED TO EACH OTHER. The site writes its own
section counts in the shell's chrome, and the API states `totalItems`:

    le chrome de /jobs   187        l API pour postType=job   187
    event 63 / 63        deal 5 / 5      -> trois sections sur trois concordent

*The chrome's count is the only witness that is not our own extraction, and it
lives on the OTHER host — so it is fetched once per run unless refused.*

**AND READING IT COST A CORRECTION OF THIS AUTHOR'S OWN MAKING, which is why
`site_witness()` asserts its label is unique.** The chrome reads «&nbsp;Food &
menus 274 Jobs 187 Events 63…&nbsp;», i.e. `<label> <count>`, and it was first
read as «&nbsp;274 Jobs&nbsp;» — a number attached to the WRONG label, and
274 belongs to Food & menus. A regex that merely finds digits near «Jobs»
reproduces that fault silently.

WHAT A RECORD CARRIES — **AND THE FIRST FIGURES WRITTEN HERE WERE A PAGE-1
RATE PRESENTED AS THE BOARD'S SHAPE, which is the trap §4 spends its length
on.** Page 1 is sorted `-postDate`, so it holds the freshest and most complete
records: measured there, `title` was 50/50 and `postDate` 50/50. **Measured on
the WHOLE run of 187** — `title` **148/187**, `posted` **125/187**,
`description` **159/187**, `company` **145/187**, `location_text` 108/187,
`source_stated` 3/187, `status` **`approved` 187/187**, 40 distinct employers.

So a third of the board carries no title and a third no date, and the employer
relation is absent on 42 — **none of which is invented**. The final line reports
these rates for the run that just happened rather than repeating the figures
above, because a fill rate is a property of a corpus and not of this file.

**EXPURGATION IS AN OBLIGATION HERE AND NOT A PRECAUTION: 45 of 50
advertisements carry an e-mail address and 10 of 50 a `+1 784` number.** They
are taken out of `content`, and the record SAYS which kinds were there — a
board that is merely poor must not read like a board we censored.

`skills` is a list of **identifiers and not names**, so it is not emitted: ids
would be data the reader cannot use, and expanding them is a second request per
run that buys a field nobody asked for.

THE HUMAN ADDRESS IS REASONED FROM A CLOSED LIST AND SAYS SO. The bundle
declares the route ``/$kind/$id`` and a closed list of five kinds — `post`,
`product`, `business`, `outage`, `person`. `post` is the only one that fits a
record of `posts`, so an advertisement reads at `https://aboutsvg.com/post/<id>`.
**This cannot be confirmed by a status code**: a single-page app serves its
shell for any path, so a `200` on a composed path proves nothing. Reasoned, and
declared as reasoned.
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path
from _robots import verdict as robots_verdict
from _ua import UA
from _withheld import withheld_a_contact

API = "api-next.aboutsvg.com"          # la route de DONNEES — la garde va sur CET hote
SITE = "aboutsvg.com"                  # la ou un humain lit l annonce
COLL = "posts"
# **SINGULIER.** La section de l interface s appelle `jobs` ; le champ des
# enregistrements vaut `job`. Composer le pluriel rend ZERO et n explique rien.
POST_TYPE = "job"
# De la liste FERMEE du bundle : `post`, `product`, `business`, `outage`, `person`.
AD_KIND = "post"
PER_PAGE = 50
TAG = "aboutsvg"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# Le chrome ecrit `<label> <compte>`, et la liste des labels est FERMEE.
CHROME_RE = re.compile(r"\bJobs\s+([\d   ,]{1,9}?)\s*(?=[A-Z])")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
# +1 784 est l indicatif de Saint-Vincent-et-les-Grenadines.
TEL_RE = re.compile(r"\+?\s*\(?\s*1?\s*784\s*\)?[\s.\-]?\d[\d\s.\-]{5,}\d")
BALISE_RE = re.compile(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[{TAG}] {msg}", file=sys.stderr)


def gate(url):
    """La garde sur l URL EXACTE, hote compris, au point ou chaque requete passe.

    **Deux hotes, deux verdicts.** `robots.txt` lie un HOTE et jamais une
    marque : lire le refus de l un comme le verdict sur l autre est la fausse
    fermeture que §3 bis documente. Ici les deux repondent ouvert, et c est
    mesure par hote et non deduit de l un.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return
    a = robots_allowed(parts.netloc, full_path(parts), agents=("claude-user",))
    if a["allowed"] is None:
        # Un INDETERMINE ne se sonde pas, et l ignorance ne libere pas.
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)


_CADENCE = {}


def get(url):
    """`(status, body, headers)` — et le statut DECIDE, pas la lisibilite du corps.

    **LA CADENCE SE CONSULTE PAR HOTE, et ici AUCUN DES DEUX n ecrit de
    `Crawl-delay`** — donc elle est a NOUS, et §3 bis dit qu un fichier muet ne
    dit pas qu il n y a pas de seuil : il ne nous dit pas ou il est, et la seule
    facon de l apprendre serait de le franchir. `Pace` le lit sur l hote et
    retombe sur notre defaut quand l hote se taît, au lieu de tirer a la vitesse
    de la boucle.
    """
    gate(url)
    hote = urllib.parse.urlsplit(url).netloc
    if hote:
        _CADENCE.setdefault(hote, Pace(hote, own=1.0)).wait()
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json, text/html;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], r.headers
    except urllib.error.HTTPError as e:
        return e.code, decode_body(e.read(), e.headers)[0], e.headers
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def records_url(page, per_page):
    q = {
        "filter": f"(postType='{POST_TYPE}')",
        "expand": "business",
        "sort": "-postDate",
        "perPage": str(per_page),
        "page": str(page),
    }
    return f"https://{API}/api/collections/{COLL}/records?" + urllib.parse.urlencode(q)


def site_witness():
    """Le compte que le SITE ecrit lui-meme, ou `(None, raison)`.

    **C est le seul temoin qui ne vient pas de notre extraction**, et il vit sur
    l AUTRE hote — donc il se garde separement et son absence ne casse rien.

    **ET SON LABEL EST ASSERTE UNIQUE, parce que l auteur de ce fichier s y est
    trompe le premier.** Le chrome ecrit `Food & menus 274 Jobs 187 Events 63`,
    c est-a-dire `<label> <compte>` ; lu comme «&nbsp;274 Jobs&nbsp;» il rend 274,
    qui est le compte des menus. Un motif qui cherche des chiffres AUTOUR du mot
    reproduit cette faute en silence, donc celui-ci exige UNE correspondance et
    refuse d en choisir une parmi plusieurs.
    """
    url = f"https://{SITE}/jobs"
    status, body, _h = get(url)
    if status != 200:
        return None, f"{url} answered HTTP {status}"
    texte = re.sub(r"\s+", " ", BALISE_RE.sub(" ", body or ""))
    trouves = CHROME_RE.findall(texte)
    if len(trouves) != 1:
        return None, (f"{url}: the chrome's `Jobs <count>` label matched "
                      f"{len(trouves)} time(s) and this witness needs exactly "
                      f"one — picking among several is how 274 was once read as "
                      f"the job count when it is the menu count")
    try:
        return int(re.sub(r"[^\d]", "", trouves[0])), None
    except ValueError:
        return None, f"{url}: {trouves[0]!r} is not a number"


def scrub(texte):
    """`(texte, kinds)` — les contacts hors d UN CHAMP, et le champ dit lesquels.

    Il ne recoit jamais une page entiere : le `tel:` du gabarit serait alors
    retenu sur chaque enregistrement, ce qui est une fausse affirmation sur une
    discretion que personne n a exercee.
    """
    pris = []
    out = texte or ""
    if MAIL_RE.search(out):
        pris.append("email")
        out = MAIL_RE.sub("[e-mail withheld]", out)
    if TEL_RE.search(out):
        pris.append("telephone")
        out = TEL_RE.sub("[telephone withheld]", out)
    return out, pris


def card(rec):
    biz = (rec.get("expand") or {}).get("business") or {}
    corps, pris = scrub(rec.get("content"))
    ident = rec.get("id") or ""
    r = {
        "id": ident,
        "ledger_id": f"{TAG}:{ident}",
        # Raisonne depuis la liste FERMEE du bundle, et une SPA ne peut pas le
        # confirmer par un code HTTP : elle sert sa coquille pour tout chemin.
        "url": f"https://{SITE}/{AD_KIND}/{ident}" if ident else None,
        "title": rec.get("title"),
        # ABSENT sur 12 des 50 mesures : il ne s invente pas.
        "company": biz.get("name") or None,
        "location_text": biz.get("address") or None,
        "country": "VC",
        "posted": rec.get("postDate") or None,
        "status_stated": rec.get("status"),
        "description": corps,
        "description_chars": len(corps),
        "withheld_fields": pris or None,
        "salary_stated": False,
        "source_stated": rec.get("sourceUrl") or rec.get("source") or None,
    }
    # **LA CLE EST ABSENTE QUAND RIEN N A ETE RETENU, et ce n est pas une
    # cosmetique :** l emettre a `False` declarerait une discretion qu on n a pas
    # exercee, et un board pauvre se lirait alors comme un board censure. La
    # declaration est une FONCTION du temoin et jamais une constante — #1238.
    if withheld_a_contact(pris):
        r["contacts_withheld"] = True
    return r


def cmd_jobs(a):
    v = robots_verdict(API)
    if not v["sweep"]:
        die(f"{API}: {v['reason']}", EXIT_UNKNOWN if v["sweep"] is None else EXIT_REFUSED)

    temoin_site, pourquoi = (None, "not asked")
    if not a.no_site_witness:
        temoin_site, pourquoi = site_witness()
        if temoin_site is None:
            note(f"the site's own count could not be read — {pourquoi}. The run "
                 f"continues on the API's own total, which is still not our "
                 f"extraction; it is one witness instead of two, and that is "
                 f"weaker and said so.")

    vus, lignes = set(), []
    total_api, pages_api, pages_lues = None, None, 0
    for page in range(1, a.max_pages + 1):
        url = records_url(page, a.per_page)
        status, body, _h = get(url)
        if status != 200:
            die(f"{url}: HTTP {status} — the status decides, not whether the "
                f"body reads.", EXIT_GONE if status in (404, 410) else EXIT_BROKEN)
        try:
            d = json.loads(body)
        except ValueError as e:
            die(f"{url}: the answer is not JSON ({e}); {len(body or '')} characters")
        if page == 1:
            total_api, pages_api = d.get("totalItems"), d.get("totalPages")
        items = d.get("items") or []
        pages_lues = page
        if not items:
            break
        for rec in items:
            # **Le filtre a-t-il tenu ?** Un `postType` autre que le notre veut
            # dire que la requete n a pas filtre ce qu on croit, et emettre
            # quand meme melangerait des menus dans un registre d emploi.
            if rec.get("postType") != POST_TYPE:
                die(f"{url} returned a record whose postType is "
                    f"{rec.get('postType')!r} and not {POST_TYPE!r}: the filter "
                    f"did not hold, and emitting would put another section's "
                    f"entries into a jobs ledger")
            if rec.get("status") and rec.get("status") != "approved":
                note(f"record {rec.get('id')} states status "
                     f"{rec.get('status')!r} and not 'approved' — measured "
                     f"'approved' on 50 of 50, so this is new; it is emitted "
                     f"with the state it states rather than dropped.")
            ident = rec.get("id")
            if not ident or ident in vus:
                continue
            vus.add(ident)
            lignes.append(card(rec))
        if pages_api is not None and page >= pages_api:
            break
        time.sleep(a.delay)

    for ligne in lignes[:a.limit] if a.limit else lignes:
        print(json.dumps(ligne, ensure_ascii=False))

    # **LES DEUX TEMOINS SE COMPARENT L UN A L AUTRE, et pas seulement a nous.**
    if temoin_site is not None and total_api is not None and temoin_site != total_api:
        note(f"**the two witnesses disagree**: the site's chrome says "
             f"{temoin_site} and the API's own total says {total_api}. Both are "
             f"the host's numbers and neither is our extraction, so this is a "
             f"fact about the board and not about this tool — measured equal at "
             f"187 on 2026-11-04, and equal on `event` and `deal` too.")
    avec_employeur = sum(1 for r in lignes if r["company"])
    retenus = sum(1 for r in lignes if r["withheld_fields"])
    # **Les taux de remplissage sortent pour LA PASSE QUI VIENT D AVOIR LIEU.**
    # Mesures sur la page 1 ils valaient 50/50 sur le titre et la date ; sur les
    # 187 ils valent 148 et 125, parce que la page 1 est triee `-postDate` et
    # porte donc les plus completes. Un taux de page 1 n est pas un taux de
    # board, et le publier d ici le figerait.
    remplissage = {ch: sum(1 for r in lignes if r.get(ch))
                   for ch in ("title", "posted", "description", "location_text")}
    fin = ("complete" if total_api is not None and len(lignes) >= total_api
           else f"stopped at the --max-pages ceiling of {a.max_pages}"
           if pages_lues >= a.max_pages else "ended by itself")
    # **UNE SEULE EXPRESSION, assemblee par morceaux NOMMES.** La premiere
    # version concatenait huit fragments en ligne et deux substitutions s y sont
    # chevauchees : la sortie disait « states 187employer: … — the relation is .
    # fill, … » puis repetait `employer:`. Une phrase abimee se lit, donc elle se
    # remarque — mais elle ne se remarque qu a l EXECUTION, et c est la seule
    # raison pour laquelle celle-la a ete vue.
    morceaux = [f"{len(lignes)} ad(s) over {pages_lues} page(s) — {fin}"]
    morceaux.append(f"; the API states {total_api}" if total_api is not None
                    else "; the API stated no total")
    if temoin_site is not None:
        morceaux.append(f" and the site's own chrome states {temoin_site}")
    morceaux.append(". fill, for THIS run and not a figure from this file: "
                    + ", ".join(f"{k} {n} of {len(lignes)}"
                                for k, n in remplissage.items()))
    morceaux.append(" — a page-1 rate is not a board rate, and page 1 is the "
                    "freshest, so these move between runs. ")
    morceaux.append(f"employer: {avec_employeur} of {len(lignes)} — the relation "
                    f"is absent on the rest and is never invented. ")
    morceaux.append(f"contacts taken out of {retenus} of {len(lignes)} "
                    f"description(s); `skills` is a list of IDENTIFIERS and not "
                    f"names, so it is not emitted.")
    note("".join(morceaux))
    if total_api is not None and len(lignes) < total_api:
        note(f"{total_api - len(lignes)} short of the {total_api} the API "
             f"states — partial, and the exit code says so.")
        sys.exit(EXIT_PARTIAL)


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the job posts, one request per page")
    s.add_argument("--max-pages", type=int, default=10, dest="max_pages")
    s.add_argument("--per-page", type=int, default=PER_PAGE, dest="per_page")
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=1.0)
    s.add_argument("--no-site-witness", action="store_true", dest="no_site_witness",
                   help="skip the second host's count; one witness instead of two")
    s.set_defaults(func=cmd_jobs)
    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
