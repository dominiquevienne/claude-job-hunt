#!/usr/bin/env python3
"""Bast.af (`db.bast.af`, Afghanistan) — «Find Jobs, Careers & Employment in Kabul».

A Vite/React front on `www.bast.af` whose data lives on **another host**. That
separation is the whole reason this adapter exists in the shape it does.

**`robots.txt` BINDS A HOST, NOT A BRAND — and here the sibling's rules say NO.**
`www.bast.af` publishes `Disallow: /api/` to the `*` group that applies to us. *Read
as the verdict on the data route, that is a refusal written in the rules — borne 1 —
which blocks every route, browser included, and would have closed this board.*
**But the bundle names `baseURL: "https://db.bast.af/api"`, and `db.bast.af`
publishes NO `robots.txt` at all** (HTTP 404 → `state: absent`, `certain: True`: the
host looked and there is nothing, which is knowledge). *So the data host never
refused us, and `www`'s `Disallow: /api/` governs a path on `www` that may not even
exist.*

> **A refusal read on the wrong host is a false closure, and nothing downstream
> contradicts it.** *§3 bis says to guard the exact URL **host included**, but its
> canonical case is a sitemap on a sibling whose rules are merely ABSENT. Here they
> are PRESENT and negative, which is far more convincing and just as wrong.*

**This adapter therefore guards `db.bast.af` and refuses every other host**, `www`
included — not because `www` is hostile, but because it is not where the data is and
its rules are not the rules that apply.

**The stated total HOLDS, so the run ASSERTS it.** `total_jobs` was 11 and the walk
read 11 distinct ids across two pages (10 then 1), `?page=99` returning an empty
`data` with `has_more_pages: false`. *The pager declares itself and tells the truth
at every step — no clamp, no crush.* **A shortfall exits 6 and says so.**

**THE LITERAL STRING `"undefined"` IS STORED IN THE DATABASE AS A VALUE** — a
JavaScript artefact persisted by whatever posted the advert. Measured over the 11:

    number_Of_vacancy   `if x` 11   really  2        email   `if x` 10   really  4
    contract_duration   `if x` 11   really  3        reference `if x` 11 really  9
    probation_period    `if x` 11   really  8        experiance `if x` 11 really 10

*A field that is PRESENT is not a field that is FILLED, and `if x` cannot tell the
difference because `"undefined"` is a non-empty string.* **The `email` line is the one
that matters, because it is a CONTACT field: a `withheld_fields: ["email"]` written on
`if x` would declare we withheld a recruiter's address on SIX adverts where nobody
deposited one** — a lie about our own discretion, undetectable by re-reading since the
output is identical either way. **Hence `rempli()`, and the guard that reddens when the
floor is removed.**

**AND A SYSTEMATIC SENTINEL IS NOT AN ISOLATED ABERRANT VALUE.** `closing_date`
carries `2040-07-01` on **1 advert of 11**, among dates running 2026-10-18 to
2027-06-02. *One in eleven is an implausible data entry, not a template default —
contrast `iscikler` (#720), whose `2099-12-31` sat on **9 of 28**.* **The discriminant
is the SHARE, not the shape: a sentinel is dropped because the board never meant it as
a date; an outlier is CARRIED, because the board did mean it and one employer typed
something odd.** *Dropping it would substitute our judgement for the board's filing.*

**And #183: `gender` is posed on 3 of the 11 (male 1, female 2) and is NOT
propagated.** *That issue rested on Uzbek labour law, and **the law of Afghanistan is
NOT asserted here**: the field treatment is carried over because propagating a sex
requirement serves no candidate.* The field is named as withheld only when it was
posed AND is not `any`.

**But the FIELD is withheld and the board's PROSE is served untouched, and conflating
the two would be a serious loss.** *Measured on these 11: the words «&nbsp;male&nbsp;» and
«&nbsp;female&nbsp;» appear only in the adverts' own text, and several times they are the
OPPOSITE of a criterion* — «&nbsp;Female candidates are highly encouraged to apply&nbsp;»,
«&nbsp;attracting female applicants for gender parity in organization&nbsp;», «&nbsp;female
obstetricians and gynecologists&nbsp;», «&nbsp;face-to-face interview with female
beneficiaries&nbsp;». **Scrubbing the prose would delete an encouragement to apply, a
parity statement, a medical specialty and a description of who is served.** *#2 sexies
is explicit: «&nbsp;on ne propage pas le critère, on continue de servir l'annonce&nbsp;» —
the structured criterion is ours to drop, the advert is not ours to edit.*

Nothing is signed: the site sends `Bearer` only when a user is logged in, and we are
not a user.

Invocation:

    python3 bastaf.py jobs --country-code AFG
    python3 bastaf.py jobs --country-code AFG --max 3

Exit codes: 0 fine · 2 broken · 3 gone · 6 partial · 7 refused · 8 unknown.
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

# **L'hote des DONNEES**, et c'est le seul auquel on parle. `www.bast.af` porte la
# facade et un `Disallow: /api/` qui ne gouverne PAS cet hote-ci.
HOST = "db.bast.af"
LISTE = "/api/get_post_jobs"
PAGE_MAX = 60                       # borne de securite

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# L'Afghanistan numerote en `+93 7xx xxx xxx` ou `07xx xxx xxx` : le groupement
# est 4-3-3, pas 2-3-3. **Un premier jet comptait 7\d puis 3 puis 3, donc il ne
# POUVAIT PAS atteindre `0700 123 456` — une regle d'expurgation DECORATIVE, et
# c'est la garde qui l'a trouvee, pas la relecture.** Ancree quand meme, parce
# qu'une regle large mordrait les references d'annonce (`TKR/09/26/46`).
TEL_RE = re.compile(
    r"(?<![\w])(?:\+?93[\s\-.]?)?0?7\d{2}[\s\-.]?\d{3}[\s\-.]?\d{3}(?![\w])")
# **La sentinelle d'absence de ce board : la chaine `"undefined"`.**
VIDES = ("", "null", "undefined", "none", "n/a")
# #183 : le critere de sexe ne sort pas. `any` n'est pas un critere.
SEXE_NEUTRE = ("any", "both", "")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print("ERROR: %s" % msg, file=sys.stderr)
    sys.exit(code)


def note(msg):
    print("[bastaf] %s" % msg, file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die("%s: %s" % (url, a["reason"]), EXIT_UNKNOWN)
    if not a["allowed"]:
        die("%s: %s" % (url, a["reason"]), EXIT_REFUSED)
    return a


def request(url):
    """**Un seul hote, et ce n'est PAS celui de la facade.**

    `www.bast.af` refuse `/api/` par ecrit&nbsp;; cet adaptateur ne lui parle pas.
    `db.bast.af` ne publie aucune regle, donc aucun `Crawl-delay` n'est ecrit et
    les 2 s sont les NOTRES.
    """
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die("%s: not %s — never sent" % (url, HOST), EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die("%s: %s: %s" % (url, type(e).__name__, e))


def rempli(v):
    """**Un champ PRESENT n'est pas un champ REMPLI.**

    Ce board stocke la chaine `"undefined"` comme VALEUR — artefact JavaScript
    persiste — sur six champs, dont `email` sur 6 annonces de 11. *`if x` la
    trouve vraie, puisqu'elle n'est pas vide.* **Sans ce plancher, un
    `withheld_fields` nommerait un contact que personne n'a depose.**
    """
    if v is None:
        return False
    if isinstance(v, (list, dict)):
        return bool(v)
    return str(v).strip().lower() not in VIDES


def valeur(v):
    return str(v).strip() if rempli(v) else None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return TEL_RE.sub("[telephone withheld]", s).strip() or None


def text(x):
    """Le texte d'un champ HTML — les corps du board sont du HTML de l'editeur."""
    if not isinstance(x, str):
        return None
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</tr>", "\n", x)
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmlmod.unescape(t).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def provinces_de(v):
    """**Du JSON DANS une chaine** — `'["Kabul"]'` — donc un second decodage.

    *Porte la chaine brute si elle ne s'analyse pas&nbsp;: on ne jette pas une
    donnee qu'on ne sait pas lire.*
    """
    if not rempli(v):
        return None
    if isinstance(v, list):
        return [x for x in (valeur(i) for i in v) if x] or None
    try:
        d = json.loads(str(v))
    except ValueError:
        return valeur(v)
    if isinstance(d, list):
        return [x for x in (valeur(i) for i in d) if x] or None
    return valeur(d)


def nom_de(v):
    """Un objet imbrique (`company`, `contract_type`, `education_level`) ou rien."""
    if isinstance(v, dict):
        for k in ("company_name", "name", "education_level", "title"):
            if rempli(v.get(k)):
                return valeur(v[k])
    return valeur(v)


def record(ld, stamp):
    ident = ld.get("id")
    # #183 : le critere de sexe est RETENU, et nomme seulement s'il etait POSE.
    sexe = (str(ld.get("gender") or "").strip().lower())
    sexe_pose = rempli(ld.get("gender")) and sexe not in SEXE_NEUTRE
    retenus = (["gender"] if sexe_pose else []) + \
              (["email"] if rempli(ld.get("email")) else []) + \
              (["submission_email"] if rempli(ld.get("submission_email")) else [])
    return {
        "source": "bastaf", "country": stamp,
        "ledger_id": "bastaf:%s" % ident, "id": str(ident),
        "url": "https://www.bast.af/job-detail/%s" % ident,
        "title": scrub(valeur(ld.get("job_title"))),
        "employer": scrub(nom_de(ld.get("company"))),
        "location": provinces_de(ld.get("provinces")),
        "country_stated": valeur(ld.get("countries")),
        "employment_type": nom_de(ld.get("contract_type")) or valeur(ld.get("job_type")),
        "category": nom_de(ld.get("job_category")),
        "education_level": nom_de(ld.get("education_level")),
        "experience_years": valeur(ld.get("experiance")),
        "vacancies": valeur(ld.get("number_Of_vacancy")),
        "contract_duration": valeur(ld.get("contract_duration")),
        "probation_period": valeur(ld.get("probation_period")),
        "reference": valeur(ld.get("reference")),
        "posted": valeur(ld.get("post_date")),
        # **L'echeance se PORTE telle quelle, 2040 compris** : une valeur
        # aberrante isolee (1 sur 11) est une saisie de l'employeur, pas une
        # sentinelle de gabarit, et la jeter remplacerait son classement par le
        # notre. Le run COMPTE les implausibles et le dit.
        "deadline": valeur(ld.get("closing_date")),
        "status": valeur(ld.get("job_status")),
        # `salary_range` est du TEXTE LIBRE («As per Salary Scale») : aucun
        # chiffre, donc aucune unite a nommer — on porte ce que le board ecrit.
        "salary_text": scrub(valeur(ld.get("salary_range"))),
        "description": scrub(text(ld.get("job_description"))),
        "requirements": scrub(text(ld.get("job_requirement"))),
        "how_to_apply": scrub(text(ld.get("submission_guideline"))),
        "application_type": valeur(ld.get("application_type")),
        "enumerated_by": "api",
        "withheld_fields": retenus or None,
        "contacts_withheld": True,
    }


def page(n):
    url = "https://%s%s?page=%d" % (HOST, LISTE, n)
    code, corps = request(url)
    if code == 404:
        die("%s: HTTP 404 — the endpoint is gone" % url, EXIT_GONE)
    if code in (401, 403):
        die("%s: HTTP %d — the endpoint now demands a credential this adapter does "
            "not hold and will not forge" % (url, code), EXIT_REFUSED)
    if code != 200 or not corps:
        die("%s: HTTP %s" % (url, code))
    try:
        d = json.loads(corps)
    except ValueError as e:
        die("%s: the endpoint did not return JSON: %s" % (url, e))
    if not isinstance(d, dict):
        die("%s: the endpoint returned %s, not an object" % (url, type(d).__name__))
    pg = d.get("pagination") if isinstance(d.get("pagination"), dict) else {}
    return d.get("data") or [], pg, d.get("total_jobs")


def cmd_jobs(a):
    stamp = a.country_code
    vus, lignes, total = set(), [], None
    n, arret = 1, "has_more_pages went false"
    while n <= PAGE_MAX:
        data, pg, total_jobs = page(n)
        if total is None:
            total = total_jobs if total_jobs is not None else pg.get("total")
            note("the board STATES a total of %s" % total)
        neufs = [r for r in data if str(r.get("id")) not in vus]
        for r in neufs:
            vus.add(str(r.get("id")))
        note("page %d: %d row(s), %d new%s" % (
            n, len(data), len(neufs),
            "" if not pg else " (has_more_pages=%s)" % pg.get("has_more_pages")))
        lignes += neufs
        if not data:
            arret = "an empty page"
            break
        if not neufs:
            # le pager ne progresse plus : on s'arrete plutot que de boucler
            arret = "a page that added nothing (page %d)" % n
            break
        if not pg.get("has_more_pages"):
            break
        n += 1
    else:
        arret = "the %d-page safety bound" % PAGE_MAX

    plafonne = a.max is not None and len(lignes) > a.max
    if plafonne:
        lignes = lignes[:a.max]

    emis, implausibles, sexes = 0, 0, 0
    for ld in lignes:
        ligne = record(ld, stamp)
        print(json.dumps(ligne, ensure_ascii=False))
        sys.stdout.flush()                      # au fil de l'eau
        emis += 1
        if ligne["deadline"] and ligne["deadline"][:4] >= "2040":
            implausibles += 1
        if ligne["withheld_fields"] and "gender" in ligne["withheld_fields"]:
            sexes += 1

    note("%d advert(s) emitted; the walk ended on %s" % (emis, arret))
    if plafonne:
        note("stopped by --max %d — NOTHING here is said about what the board holds"
             % a.max)
    elif total is not None:
        if len(vus) == total:
            note("the stated total HOLDS: %d distinct id(s) against a stated %d"
                 % (len(vus), total))
        else:
            note("%d distinct id(s) read against a stated total of %d — %d SHORT; the "
                 "rows above are what was read, not what the board holds"
                 % (len(vus), total, total - len(vus)))
            sys.stderr.flush()
            sys.exit(EXIT_PARTIAL)
    if implausibles:
        note("%d advert(s) carry a deadline in 2040 or later — CARRIED as the board "
             "filed it: an isolated implausible entry is not a template sentinel, and "
             "dropping it would replace the board's filing with ours" % implausibles)
    if sexes:
        note("%d advert(s) posed a sex requirement; it is WITHHELD and named in "
             "withheld_fields, never propagated (#183)" % sexes)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Bast.af — Afghanistan adverts")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("jobs", help="emit the adverts the API serves")
    p.add_argument("--country-code", required=True,
                   help="the code STAMPED on every row (AFG for Afghanistan)")
    p.add_argument("--max", type=int, default=None,
                   help="cap the rows emitted; claims nothing about the board")
    a = ap.parse_args(argv)
    if a.cmd == "jobs":
        return cmd_jobs(a)
    ap.error("unknown command")


if __name__ == "__main__":
    sys.exit(main())
