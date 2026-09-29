#!/usr/bin/env python3
"""Lambda / Ламбда (`lambda.global`), Mongolia: the adverts live in the page's streamed React payload, not in its HTML — and reading them needs a decode that, done wrong, returns TEXT rather than an error. Issue #661.

  lambdaglobal.py jobs [--country-code MN] [--max N]     the sitemap, then one request an advert

WHAT IT IS. A Mongolian recruitment platform, entirely localised in Cyrillic. Mongolia's other
named boards are `zangia` (delivered) and `biznetwork` (serves a parking page).

THE RULES. `lambda.global` serves its rules file (`state: read`, `certain: True`) and writes **no
Crawl-delay**; 2 s are ours. **It declares its sitemap on `lambda.global` — WITHOUT `www`, a host
the guard had not seen** — so the guard is re-taken on the declared host before reading it
(CLAUDE.md §3 bis: a sitemap can live on a host the guard has never seen).

THE ROUTE — **TWO ENUMERATORS, AND NEITHER CONTAINS THE OTHER.** The declared sitemap is an INDEX
pointing at `/sitemap-0.xml`: 1 412 `<loc>` (1 403 with a `lastmod`), of which **50 under `/jobs`**,
beside 1 152 `/salary`, 77 `/ai`, 51 `/companies`. The `/jobs` listing carries **30 advert links**,
no pager, and states no count.

**Three figures — 50, 30, none stated — read as «the sitemap is the enumerator». The MEMBERSHIP
test says otherwise: the two sets intersect in TWO.** *28 of the 30 linked adverts are absent from
the sitemap entirely, and 48 of the 50 sitemap adverts are absent from the listing.* **Same order of
magnitude, different members — and no total, no cardinal and no re-reading distinguishes that from
one set containing the other.** Measured 2026-09-29: walking the sitemap alone emits 19 adverts and
**loses at least 28 live ones**, four of which were sampled and all four carry a complete
`JobPosting`.

**So the run walks BOTH and emits their union, and it never claims a total.** *Neither enumerator
states a count, neither contains the other, so the board's size is NOT established by this route —
the closing line states each enumerator's own figure and their overlap, and says so.* **A witness
that agrees with itself is not a second witness** (`shared/boards/README.md`): the sitemap's 50 and
the listing's 30 are two populations, not two readings of one.

**THE ADVERT IS NOT IN THE HTML.** The advert page's rendered body is navigation only, and its
single `ld+json` block is an `Organization`. Each advert lives in the React Server Components
payload — `self.__next_f.push([1,"..."])` — as a `JobPosting` object.

**AND THE DECODE IS THE DANGEROUS PART.**

    brut = "".join(chunks)
    dec  = brut.encode().decode("unicode_escape")      # suffit pour du latin
    dec  = dec.encode("latin-1").decode("utf-8")       # INDISPENSABLE ici

> **A broken decode does not raise: it returns TEXT, and the text it returns does not contain what
> one is looking for.** *So it reads exactly like "the content is not there."*

Without the second line the payload comes back as mojibake, every search for an advert fails, and
the honest-looking conclusion is **"the HTTP route does not carry the adverts"** — a board declared
empty that is not. Nothing contradicts it: no exception, no error code, a payload read end to end.
*This adapter therefore CHECKS that what it decoded is legible before concluding anything* — by the
SIGNATURE OF THE FAILURE and not by a known word, see `lisible()`, because requiring a word of the
site's language assumes one reads it. **On a non-Latin site, a wrong decode and absent content are
indistinguishable without that check.** *And the signature is a RANGE, not a handful of characters:
measured on ten scripts, three named characters catch one, the two-byte lead range catches five, and
the range covering two- AND three-byte leads catches all ten — Burmese, Lao, Thai, Georgian and
Amharic open on U+00E0-U+00EF and escape the narrow form entirely.*

**AND COUNTING A KEYWORD MEASURES THE TRANSLATION, NOT THE CONTENT.** The payload carries `salary`,
`location`, `company` and `title` **as form labels and placeholders**. *A fully localised interface
dictionary contains every word of the domain, so finding one proves nothing.* **The advert is found
by STRUCTURE — an object declaring `"@type":"JobPosting"` — never by the occurrence of a term.**

**WITHHELD:** e-mail addresses and telephone numbers in free text. **`baseSalary.currency` is never
carried** and the salary travels as the string the site prints (the rule measured on one vendor's
two fronts, #638/#655); a Mongolian monthly figure runs to seven digits, so the LABELLED salary
field stays out of the telephone rule — the seuil-de-chiffres defect that destroyed 113 Burmese
salaries out of 115.

**AND THE SITEMAP NAMES ADVERTS THAT ARE GONE — a 200, and a payload read end to end.** A
withdrawn advert answers 200 with a whole, legible payload that declares **no structured object at
all**; a live one declares nine kinds (`JobPosting`, `Organization`, `Place`, `MonetaryAmount`, ...).
*Both pages are 200, both decode cleanly, and only the STRUCTURE separates them* — see
`structure_de()`. **31 of the sitemap's 50 are in that state, and the listing corroborates: NONE of
the 31 is linked from `/jobs`.** The run counts them apart, because «withdrawn» is a fact about the board and «no
JobPosting in a payload that HAS structure» would be a fact about our reading. **The closing line
states all four outcomes against the sitemap's count: emitted + unreachable + withdrawn + unread ==
named**, and the run dies rather than let an advert vanish between them.

`--country-code` STAMPS. Titles and descriptions are in Mongolian and are not translated.

Measured 2026-09-29 by the declared client, the guard on the exact path and on the DECLARED host:
`/sitemap.xml` 200 (an index); `/sitemap-0.xml` 200, 245 876 B — 1 412 `<loc>`, 50 adverts; `/jobs`
200, 849 452 B — 30 advert links, no pager, no count stated; one advert 362 485 B, its payload
carrying `"@type":"JobPosting"` with `identifier` "Job ID" 27449 and `hiringOrganization`
"Mongolian Express LLC".
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

HOST = "lambda.global"
SITEMAP = "/sitemap.xml"
LISTE = "/jobs"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
URL_RE = re.compile(r"<url>(.*?)</url>", re.S)
LOC_RE = re.compile(r"<loc>\s*(.*?)\s*</loc>", re.S)
LASTMOD_RE = re.compile(r"<lastmod>\s*(.*?)\s*</lastmod>", re.S)
INDEX_RE = re.compile(r"<sitemap>.*?<loc>\s*(.*?)\s*</loc>.*?</sitemap>", re.S)
SLUG_RE = re.compile(r"/jobs/([a-z0-9-]+-\d{6,})\b")
CHUNK_RE = re.compile(r'self\.__next_f\.push\(\[\d+,"(.*?)"\]\)', re.S)
TYPE_RE = re.compile(r'"@type"\s*:\s*"([A-Za-z]+)"')
# La SIGNATURE DE L'ECHEC, pas la presence du contenu : de l'UTF-8 lu en latin-1
# laisse une TETE de sequence suivie d'un octet de continuation (U+0080-U+00BF).
# Ce test ne demande pas de connaitre la langue du site, et c'est pour ca qu'il vaut
# sur un alphabet qu'on ne lit pas.
#
# **La borne haute est U+00EF et non U+00DF, et ce n'est pas un detail.** U+00C0-U+00DF
# ouvre les sequences a DEUX octets (cyrillique, arabe, persan, grec, hebreu) ; les
# ecritures a TROIS octets — birman, lao, thai, georgien, amharique — ouvrent sur
# U+00E0-U+00EF et passaient donc a travers. *Mesure du 2026-09-29 sur dix ecritures :
# trois caracteres nommes en attrapent 1, U+00C0-U+00DF en attrape 5, U+00C0-U+00EF les
# 10 ; zero faux positif sur du latin accentue sain, « ¿ » et « « » compris.*
MOJIBAKE_RE = re.compile("[\u00c0-\u00ef][\u0080-\u00bf]")
# Toute TETE possible, y compris celles qu'aucune paire ne suit : le DENOMINATEUR.
TETE_RE = re.compile("[\u00c0-\u00ff]")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[lambdaglobal] {msg}", file=sys.stderr)


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
    gate(url)                                   # sur le CHEMIN exact, hote compris
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # aucun Crawl-delay ecrit ; 2 s sont de nous
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml",
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


def money(s):
    """Un salaire LABELLISE : l'expurgation des courriels seule.

    La regle du telephone ne le touche pas : une paye mensuelle mongole a sept
    chiffres, donc elle a la FORME d'un numero — c'est le defaut qui a detruit
    113 salaires birmans sur 115 (CLAUDE.md §4). Le champ que le board imprime
    sous son propre libelle se lit comme un salaire, jamais comme du texte libre.
    """
    if s is None or s == "":
        return None
    return MAIL_RE.sub("[e-mail withheld]", str(s)).strip() or None


def text(x):
    """Le texte d'un champ, l'ELEMENT `<i>` retire et non sa seule balise.

    Une police d'icones met son glyphe DANS l'element — un caractere de la zone
    privee — et retirer la balise seule le laisse dans le texte, ou il se lit
    comme un caractere de la langue du site. 136 adaptateurs sur 138 portent
    encore ce defaut (`shared/boards/README.md`).
    """
    if not isinstance(x, str):
        return None
    t = re.sub(r"<i\b[^>]*>.*?</i>", " ", x, flags=re.S | re.I)   # l'ELEMENT, pas la balise
    t = re.sub(r"<br\s*/?>|</p>|</li>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmlmod.unescape(t).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def lisible(texte, seuil=0.5):
    """Le decodage a-t-il rendu du texte, ou du mojibake qui LUI RESSEMBLE ?

    **On mesure une PART, pas une densite — et la difference a ete mesuree sur des
    pages reelles, pas sur des mots composes.** *Une page francophone servie est a
    ~1,5 % de caracteres accentues : mal decodee, sa DENSITE de paires ne vaut que
    **0,016**, quand des MOTS non latins composes en rendent 0,33 a 0,47.* **Un
    seuil de densite regle sur des mots aurait donc laisse passer une page reelle
    mal decodee** — mesure du 2026-09-29 sur deux boards francophones servis
    (`emploisburkina.bf`, `www.asako.mg`, 115 000 caracteres de prose).

    La densite depend de la proportion d'ASCII autour, qui n'a rien a voir avec la
    question posee. La part n'en depend pas&nbsp;:

        part = paires / caracteres pouvant etre une TETE (U+00C0-U+00FF)

      * latin SAIN : un accentue est suivi d'une LETTRE — part 0,00 mesuree sur les
        deux corpus reels, 0,33 au pire sur des phrases composees a insecable ;
      * MAL DECODE : chaque tete est suivie d'une continuation — part 0,99 a 1,00 ;
      * non latin SAIN (cyrillique, birman) : aucune tete, 0/0 — **indecidable, donc
        LISIBLE**. *L'ignorance ne condamne pas plus qu'elle ne libere : ici elle
        laisse passer, et c'est `posting_de` qui tranchera sur la STRUCTURE.*
    """
    if not texte:
        return True
    tetes = len(TETE_RE.findall(texte))
    if not tetes:
        return True          # rien qui puisse etre une tete mal lue : rien a juger
    return len(MOJIBAKE_RE.findall(texte)) / tetes < seuil


def charge_de(markup):
    """La charge RSC, decodee — et l'aller-retour latin-1 est ce qui la rend lisible."""
    brut = "".join(CHUNK_RE.findall(markup or ""))
    if not brut:
        return ""
    try:
        dec = brut.encode("utf-8", "surrogatepass").decode("unicode_escape")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return ""
    try:
        return dec.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return dec      # deja correct : on ne force pas un aller-retour sans objet


def structure_de(charge):
    """Les `@type` que la charge DECLARE — la mesure qui separe deux 200 identiques.

    Mesure le 2026-09-29 sur deux annonces du sitemap : la vivante en declare
    NEUF (`JobPosting`, `Organization`, `Place`, `MonetaryAmount`, ...), la
    retiree **aucun**, sa charge etant par ailleurs entiere et lisible (142 166
    caracteres). *Une charge lisible sans le moindre objet structure est une
    annonce retiree que le sitemap nomme encore ; ce n'est pas une lecture
    manquee.* **Et le discriminant est STRUCTUREL parce qu'un compte de mots ne
    mesurerait ici que le dictionnaire de l'interface.**
    """
    return set(TYPE_RE.findall(charge or ""))


def posting_de(charge):
    """L'objet qui se DECLARE `JobPosting`, extrait par equilibrage d'accolades.

    On le trouve par STRUCTURE et jamais par l'occurrence d'un terme : le
    dictionnaire d'interface de ce site contient `salary`, `location`, `company`
    et `title` comme libelles de formulaire.
    """
    for m in re.finditer(r'"@type"\s*:\s*"JobPosting"', charge or ""):
        deb = charge.rfind("{", 0, m.start())
        while deb >= 0:
            fin = _fin_objet(charge, deb)
            if fin is not None:
                try:
                    d = json.loads(charge[deb:fin])
                except ValueError:
                    d = None
                if isinstance(d, dict) and d.get("@type") == "JobPosting":
                    return d
            deb = charge.rfind("{", 0, deb)
    return {}


def _fin_objet(s, deb):
    """L'index APRES l'accolade fermante qui repond a `s[deb]`, ou None."""
    prof, i, n = 0, deb, len(s)
    while i < n:
        c = s[i]
        if c == '"':
            i += 1
            while i < n:
                if s[i] == "\\":
                    i += 2
                    continue
                if s[i] == '"':
                    break
                i += 1
            if i >= n:
                return None
        elif c == "{":
            prof += 1
        elif c == "}":
            prof -= 1
            if prof == 0:
                return i + 1
        i += 1
    return None


def adverts_of(sitemap):
    """Les entrees `/jobs/` du sitemap, avec leur `lastmod` quand il y en a un."""
    out = []
    for block in URL_RE.findall(sitemap or ""):
        loc = LOC_RE.search(block)
        if not loc:
            continue
        u = htmlmod.unescape(loc.group(1))
        if "/jobs/" not in urllib.parse.urlsplit(u).path:
            continue
        lm = LASTMOD_RE.search(block)
        out.append((u, lm.group(1).strip() if lm else None))
    return out


def lieu_de(ld):
    a = (ld.get("jobLocation") or {})
    a = a.get("address") if isinstance(a, dict) else None
    if not isinstance(a, dict):
        return None
    parts = [a.get(k) for k in ("addressLocality", "addressRegion", "addressCountry")]
    return ", ".join(text(p) or "" for p in parts if isinstance(p, str) and p.strip()) or None


def salaire_de(ld):
    """La CHAINE que le site imprime. **`currency` n'est jamais porte** (#638/#655)."""
    bs = ld.get("baseSalary")
    if isinstance(bs, str):
        return money(text(bs))
    if not isinstance(bs, dict):
        return None
    v = bs.get("value")
    if isinstance(v, str):
        return money(text(v))
    if isinstance(v, dict):
        bas, haut, un = v.get("minValue"), v.get("maxValue"), v.get("value")
        if un not in (None, ""):
            return money(un if not isinstance(un, str) else text(un))
        if bas not in (None, "") and haut not in (None, ""):
            return money(f"{bas} - {haut}")
        for x in (bas, haut):
            if x not in (None, ""):
                return money(x)
    return None


def record(url, lastmod, ld, stamp):
    org = ld.get("hiringOrganization") if isinstance(ld.get("hiringOrganization"), dict) else {}
    ident = ld.get("identifier")
    ident = ident.get("value") if isinstance(ident, dict) else ident
    return {
        "source": "lambdaglobal", "country": stamp,
        "ledger_id": f"lambdaglobal:{ident}" if ident not in (None, "") else f"lambdaglobal:{url}",
        "id": str(ident) if ident not in (None, "") else None,
        "url": url,
        "title": scrub(text(ld.get("title"))),
        "employer": scrub(text(org.get("name"))),
        "employer_url": org.get("url") or org.get("@id") or None,
        "salary": salaire_de(ld),
        "employment_type": ld.get("employmentType"),
        "location": lieu_de(ld),
        "posted": ld.get("datePosted"),
        "valid_through": ld.get("validThrough"),
        "lastmod": lastmod,
        "description": scrub(text(ld.get("description"))),
        "contacts_withheld": True,
    }


def nommees(url):
    """Le sitemap declare, index suivi : [(url d'annonce, lastmod)]."""
    code, body = request(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    named = adverts_of(body)
    for enfant in [htmlmod.unescape(u) for u in INDEX_RE.findall(body)]:
        c, b = request(enfant)
        if c != 200:
            die(f"{enfant}: HTTP {c} — the index names a child that does not answer", EXIT_PARTIAL)
        named += adverts_of(b)
    vus, uniques = set(), []
    for u, lm in named:
        if u in vus:
            continue
        vus.add(u)
        uniques.append((u, lm))
    return uniques


def liees(url):
    """Les annonces que la LISTE lie — le second enumerateur, celui du site lui-meme.

    Elle ne pagine pas et n'enonce aucun compte : ce qu'elle lie est ce qu'elle
    montre. **Elle ne recouvre pas le sitemap** — deux membres communs sur 30 le
    2026-09-29 — donc elle s'ajoute, elle ne le remplace pas.
    """
    code, body = request(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    slugs = list(dict.fromkeys(SLUG_RE.findall(body)))
    if not slugs:
        die(f"{url}: 200 but the listing links no advert — the page changed shape;"
            f" this is not an empty board", EXIT_PARTIAL)
    return [(f"https://{HOST}/jobs/{sl}", None) for sl in slugs]


def cmd_jobs(a):
    if a.max is not None and a.max < 0:
        die("--max: a count, or 0 for every advert the enumerators name")
    stamp = a.country_code.upper() if a.country_code else None
    veut = a.enumerator
    du_sitemap = nommees(f"https://{HOST}{SITEMAP}") if veut in ("both", "sitemap") else []
    de_la_liste = liees(f"https://{HOST}{LISTE}") if veut in ("both", "listing") else []

    # L'UNION, l'ordre preserve, et l'origine de chaque annonce retenue.
    named, origine = [], {}
    for source, lot in (("sitemap", du_sitemap), ("listing", de_la_liste)):
        for u, lm in lot:
            if u in origine:
                origine[u] += "+" + source
                continue
            origine[u] = source
            named.append((u, lm))
    commun = sum(1 for v in origine.values() if "+" in v)
    if not named:
        die(f"https://{HOST}: neither enumerator names an advert — they changed shape;"
            f" this is not an empty board", EXIT_PARTIAL)

    rows, manques, sans_ld, retirees = [], 0, 0, 0
    for u, lm in named:
        if a.max and len(rows) >= a.max:
            break
        code, page = request(u)
        if code != 200:
            manques += 1
            note(f"{u}: HTTP {code} — advert skipped")
            continue
        charge = charge_de(page)
        if not lisible(charge):
            # **On ne conclut PAS a une absence sur un decodage suspect.**
            die(f"{u}: the decoded payload reads as mojibake — a wrong decode returns TEXT and not"
                f" an error, and would read as «the advert is not there». Refusing to conclude.",
                EXIT_BROKEN)
        types = structure_de(charge)
        ld = posting_de(charge)
        if not ld:
            if not types:
                retirees += 1     # charge entiere, lisible, AUCUN objet structure
                note(f"{u}: 200 and a legible payload carrying no structured object at all"
                     f" — the advert is withdrawn and {origine[u]} still names it")
            else:
                # La charge PORTE de la structure et pas celle-la : c'est notre lecture
                # qui est en cause, pas le board. On le dit fort, et on nomme ce qu'on a vu.
                sans_ld += 1
                note(f"{u}: the payload declares {sorted(types)} but no JobPosting"
                     f" — the advert's shape changed; this reads on US, not on the board")
            continue
        r = record(u, lm, ld, stamp)
        r["enumerated_by"] = origine[u]
        rows.append(r)
        print(json.dumps(r, ensure_ascii=False))     # AU FIL DE L'EAU : une coupure du transport
                                                     # ne doit pas emporter ce qui a ete lu

    plafonne = bool(a.max and len(rows) >= a.max)
    note(f"{th(len(rows))} emitted"
         + (f", {th(manques)} unreachable" if manques else "")
         + (f", {th(retirees)} withdrawn (200, legible, no structured object)" if retirees else "")
         + (f", {th(sans_ld)} whose payload has structure but no JobPosting" if sans_ld else "")
         + (" — stopped by --max." if plafonne else " — every advert the enumerators name."))
    note(f"the enumerators: sitemap names {th(len(du_sitemap))}, the /jobs listing links"
         f" {th(len(de_la_liste))}, {th(commun)} in common, {th(len(named))} distinct."
         f" **NEITHER states a count and neither contains the other, so the board's size is not"
         f" established by this route** — these are two populations, not two readings of one.")
    note("the advert lives in the React payload and not in the HTML; it is found by"
         " \"@type\":\"JobPosting\", never by a keyword — this site's interface dictionary carries"
         " salary, location, company and title as form labels.")
    note("baseSalary.currency is never carried; the salary travels as the string the site prints.")
    if stamp:
        note(f"country {stamp} is the user's stamp.")
    # **emitted + unreachable + withdrawn + unread == named** : l'invariant qui refuse
    # qu'une annonce disparaisse sans etre comptee dans l'une des quatre issues.
    if not plafonne and len(rows) + manques + retirees + sans_ld != len(named):
        die(f"{len(rows)} + {manques} + {retirees} + {sans_ld} != {len(named)} named"
            f" — advert(s) dropped in silence", EXIT_PARTIAL)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Lambda (Mongolia) — the sitemap the rules declare is the route; the advert "
                    "lives in the React payload, and the decode is checked before any absence is "
                    "concluded. Issue #661.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the sitemap, then one request an advert")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on every record (the board states none)")
    j.add_argument("--enumerator", choices=("both", "sitemap", "listing"), default="both",
                   help="which enumerator to walk (default both — neither contains the other)")
    j.add_argument("--max", type=int, default=0,
                   help="stop after N adverts (0 = every advert the sitemap names)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
