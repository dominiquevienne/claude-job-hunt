#!/usr/bin/env python3
"""is-cikler (`iscikler.com`, Northern Cyprus) — «Kuzey Kibris'in Is Arama Portali».

A Vite/React shell whose JSON API is the route. **The board STATES a total and KEEPS
it**, which makes it the first Northern Cyprus host in this repository whose witness
can be ASSERTED rather than merely noted.

**NOTHING IS SIGNED AND NOTHING IS FORGED, and that is a deliberate limit.** The
site's own bundle signs every request:

    X-Request-Timestamp · X-Request-Nonce · X-Request-Signature (a hash of the body)
    X-Client-Fingerprint = btoa(navigator.userAgent + navigator.language)

*A per-request signature plus a browser fingerprint is a mechanism to ensure requests
come from the official client, so computing it would be **defeating an anti-automation
control** — which borne 2 forbids, for our HTTP client exactly as for the browser
route.* **The question was never whether we could compute it: it was whether the
control is ENFORCED.** Measured 2026-10-02 by one honest request as the declared
client: `GET /api/jobs` answers **200** unforged. **The headers are client-side
decoration on this endpoint.**

> **So this adapter sends its own identity and nothing else.** *If the server ever
> begins to enforce the signature, the run gets 401/403 and STOPS saying so* — see
> `cmd_jobs`. **A control that is enforced is a wall, not a puzzle to solve**, and the
> candidate is not a means.

**The witness holds, so the run ASSERTS it.** `meta.total` was 28 and one page
returned 28 distinct ids. *`per_page` is CLAMPED to 50 **by the server**, which
declares the clamp in its own `meta.per_page`* — so the walk pages by what the server
grants, not by what we asked, and a shortfall against the stated total is reported as
a shortfall (exit 6) rather than passed off as the whole inventory.

**Three sentinels, each of which would publish something the board never said:**

| the field | what it holds | what this adapter does |
| :-- | :-- | :-- |
| `salary_min`/`salary_max` | **`"0.00"` on 10 of 28** | carries NO salary — *a wage of zero is not a wage* |
| `salary_min` | `null` on 7 | carries nothing, flags nothing: honest absence |
| `expires_at` | **`2099-12-31 23:59:59` on 9 of 28** | carries NO deadline — a sentinel for «none» |

**That zero is the FOURTH mechanism of the salary family** — #638/#655 a currency that
was WRONG, #722 a currency on NULL values, #721 a row COMMENTED OUT, and here the
string `"0.00"`. *Four hosts, four mechanisms, one rule: a salary is carried only when
the board states an amount.*

**And the 11 real salaries are 5- and 6-figure TL (20 000 - 120 000) — exactly the
digit range where a nine-digit telephone rule destroyed 113 of 115 Burmese salaries.**
*Measured here rather than assumed: the anchored rule — `+90`/`0` then `5xx` or `392` —
matches none of the 11.* **The anchor is what saves them.**

**THE BOARD DOES NOT EXPIRE ITS ADVERTS: 19 of 28 were past their `expires_at` while
all 28 were `status: approved`.** *So past deadlines are emitted and NAMED, never
dropped — dropping them would substitute our judgement for the board's own filing
(#724).*

Invocation:

    python3 iscikler.py jobs --country-code CYN
    python3 iscikler.py jobs --country-code CYN --max 5

Exit codes: 0 fine · 2 broken · 3 gone · 6 partial · 7 refused · 8 unknown.
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

HOST = "iscikler.com"
API = "/api/jobs"
PER_PAGE = 50                 # ce qu'on DEMANDE ; le serveur impose son propre plafond
PAGE_MAX = 60                 # borne de securite

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# Meme pays que `ekonomikibris` et `kibriseleman` : ancre sur ce que le pays
# NUMEROTE. Une regle a neuf chiffres detruirait les 11 salaires reels, qui font
# cinq et six chiffres.
TEL_RE = re.compile(
    r"(?<![\w])(?:\+?90[\s\-.]?)?\(?0?\)?[\s\-.]?(?:5\d{2}|392)\)?"
    r"[\s\-.]?\d{3}[\s\-.]?\d{2}[\s\-.]?\d{2}(?![\w])")
# **La sentinelle d'echeance** : une date lointaine qui veut dire « aucune ».
SENTINELLE = "2099"
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print("ERROR: %s" % msg, file=sys.stderr)
    sys.exit(code)


def note(msg):
    print("[iscikler] %s" % msg, file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die("%s: %s" % (url, a["reason"]), EXIT_UNKNOWN)
    if not a["allowed"]:
        die("%s: %s" % (url, a["reason"]), EXIT_REFUSED)
    return a


def request(url):
    """**Notre identite, et RIEN d'autre.**

    Aucun `X-Request-Signature`, aucun `X-Client-Fingerprint`. Le client du site
    en pose&nbsp;; les reproduire serait dejouer un controle anti-automatisation
    (borne 2). Le serveur ne les exige pas sur ce point d'entree — mesure du
    2026-10-02 — et s'il se met a les exiger, on recoit 401/403 et on s'arrete.
    """
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die("%s: not %s — never sent" % (url, HOST), EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # aucun Crawl-delay ecrit
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die("%s: %s: %s" % (url, type(e).__name__, e))


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return TEL_RE.sub("[telephone withheld]", s).strip() or None


def text(x):
    if not isinstance(x, str):
        return None
    t = re.sub(r"<[^>]+>", " ", x)
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def montant(v):
    """Un montant, ou RIEN — et `"0.00"` n'est pas un montant.

    *Une paye de zero n'est pas une paye&nbsp;: la porter publierait «&nbsp;ce poste paie
    0 TL&nbsp;», ce que le board n'a jamais dit.* **Quatrieme mecanisme de la famille
    du salaire**, apres une monnaie FAUSSE (#638/#655), une monnaie sur des valeurs
    NULLES (#722) et une ligne COMMENTEE (#721).
    """
    if v in (None, "", "null"):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if f == 0 else v


def salaire_de(ld):
    bas, haut = montant(ld.get("salary_min")), montant(ld.get("salary_max"))
    if bas and haut and bas != haut:
        return "%s - %s" % (bas, haut)
    return bas or haut or None


def monnaie_de(ld):
    """L'unite du salaire — **le board la nomme dans son CLIENT, pas dans sa charge**.

    La charge de `/api/jobs` ne porte aucune monnaie sur ses 24 champs. Mais le
    bundle du site rend le salaire ainsi&nbsp;:

        [g.salary_min, " - ", g.salary_max, " ", g.salary_currency || "TL"]

    et son formulaire de depot envoie `currency: k || "TRY"`. **Donc l'unite est
    DECLAREE par le board — deux fois, par defaut — et «&nbsp;TL&nbsp;» n'est pas une
    inference de notre part.** *Un chiffre de salaire sans unite est le defaut que
    `SalaryCarriesItsUnit` existe pour attraper&nbsp;; inventer une monnaie en serait
    un pire.* Rend `(monnaie, vient_du_defaut_du_board)`.
    """
    v = ld.get("salary_currency")
    if v:
        return str(v), False
    return "TL", True


def echeance_de(ld):
    """L'echeance, sauf la SENTINELLE.

    `2099-12-31 23:59:59` sur 9 annonces sur 28 veut dire «&nbsp;aucune&nbsp;»&nbsp;;
    la porter comme une date serait une precision fausse.
    """
    v = ld.get("expires_at")
    if not v or str(v).startswith(SENTINELLE):
        return None, bool(v)
    return str(v), False


def record(ld, stamp):
    ident = ld.get("id")
    sal = salaire_de(ld)
    monnaie, par_defaut = monnaie_de(ld)
    echeance, sentinelle = echeance_de(ld)
    return {
        "source": "iscikler", "country": stamp,
        "ledger_id": "iscikler:%s" % ident, "id": str(ident),
        "slug": ld.get("slug"),
        "url": "https://%s/jobs/%s" % (HOST, ld.get("slug") or ident),
        "title": scrub(text(ld.get("title"))),
        "employer": scrub(text(ld.get("company_name") or ld.get("employer_name"))),
        "employer_website": ld.get("company_website") or None,
        "location": text(ld.get("location")),
        "employment_type": ld.get("employment_type") or None,
        "category": ld.get("category") or None,
        "experience_level": ld.get("experience_level") or None,
        "education_level": ld.get("education_level") or None,
        "posted": str(ld["created_at"]) if ld.get("created_at") else None,
        "deadline": echeance,
        "deadline_sentinel": sentinelle,     # l'echeance etait 2099 : « aucune »
        "salary": sal,                       # jamais "0.00" : zero n'est pas un montant
        # **Un chiffre porte son unite**, et celle-ci vient du board (son propre
        # rendu : `salary_currency || "TL"`), jamais d'une inference de notre part.
        "salary_currency": monnaie if sal else None,
        "salary_currency_is_board_default": bool(sal) and par_defaut,
        "status": ld.get("status") or None,
        "views": ld.get("views"),
        "description": scrub(text(ld.get("description"))),
        "requirements": scrub(text(ld.get("requirements"))),
        "enumerated_by": "api",
        "contacts_withheld": True,
    }


def page(n):
    url = "https://%s%s?per_page=%d&page=%d" % (HOST, API, PER_PAGE, n)
    code, corps = request(url)
    if code in (401, 403):
        # **Le controle est devenu EXIGE** : on s'arrete et on le dit. On ne le
        # resout pas — borne 2, et le candidat n'est pas un moyen.
        die("%s: HTTP %d — the request signature the site's own client computes is "
            "now ENFORCED. This adapter does not compute it and does not forge a "
            "client fingerprint: that would be defeating an anti-automation control. "
            "The route stops here and is recorded, not solved." % (url, code),
            EXIT_REFUSED)
    if code == 404:
        die("%s: HTTP 404 — the endpoint is gone" % url, EXIT_GONE)
    if code != 200 or not corps:
        die("%s: HTTP %s" % (url, code))
    try:
        d = json.loads(corps)
    except ValueError as e:
        die("%s: the endpoint did not return JSON: %s" % (url, e))
    if not isinstance(d, dict) or not d.get("success"):
        die("%s: the endpoint answered success=%r" % (url, (d or {}).get("success")))
    meta = d.get("meta") if isinstance(d.get("meta"), dict) else {}
    return d.get("data") or [], meta


def cmd_jobs(a):
    stamp = a.country_code
    vus, lignes, total, accorde = set(), [], None, None
    n = 1
    arret = "the stated total was reached"
    while n <= PAGE_MAX:
        data, meta = page(n)
        if total is None:
            total = meta.get("total")
            accorde = meta.get("per_page")
            if accorde and accorde != PER_PAGE:
                # **Le serveur impose son plafond et il l'ANNONCE** : on pagine sur
                # ce qu'il accorde, jamais sur ce qu'on a demande.
                note("per_page %d requested, %s GRANTED — the server declares its own "
                     "clamp in meta.per_page, and the walk follows it"
                     % (PER_PAGE, accorde))
            note("the board STATES a total of %s" % total)
        neufs = [r for r in data if str(r.get("id")) not in vus]
        for r in neufs:
            vus.add(str(r.get("id")))
        note("page %d: %d row(s), %d new" % (n, len(data), len(neufs)))
        lignes += neufs
        if not data:
            arret = "an empty page"
            break
        if not neufs:
            arret = "a page that added nothing (page %d)" % n
            break
        if total is not None and len(vus) >= total:
            break
        n += 1
    else:
        arret = "the %d-page safety bound" % PAGE_MAX

    plafonne = a.max is not None and len(lignes) > a.max
    if plafonne:
        lignes = lignes[:a.max]

    emis, sentinelles, passees = 0, 0, 0
    aujourdhui = "2026-10-02"
    for ld in lignes:
        ligne = record(ld, stamp)
        print(json.dumps(ligne, ensure_ascii=False))
        sys.stdout.flush()           # au fil de l'eau
        emis += 1
        if ligne["deadline_sentinel"]:
            sentinelles += 1
        if ligne["deadline"] and ligne["deadline"][:10] < aujourdhui:
            passees += 1

    note("%d advert(s) emitted; the walk ended on %s" % (emis, arret))
    if plafonne:
        note("stopped by --max %d — NOTHING here is said about what the board holds"
             % a.max)
    elif total is not None:
        # **Le temoin est ENONCE, donc il s'ASSERTE** — et un manque se dit.
        if len(vus) == total:
            note("the stated total HOLDS: %d distinct id(s) against meta.total %d"
                 % (len(vus), total))
        else:
            note("%d distinct id(s) read against a stated total of %d — %d SHORT"
                 % (len(vus), total, total - len(vus)))
            if emis:
                note("the rows above are what was read, not what the board holds")
            sys.stderr.flush()
            sys.exit(EXIT_PARTIAL)
    if sentinelles:
        note("%d advert(s) carried the 2099 deadline sentinel, which means «none» and "
             "is NOT emitted as a date" % sentinelles)
    if passees:
        note("%d emitted advert(s) state a deadline already past, and the board still "
             "files them as approved — they are emitted and named, never dropped"
             % passees)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="is-cikler — Northern Cyprus adverts")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("jobs", help="emit the adverts the API serves")
    p.add_argument("--country-code", required=True,
                   help="the code STAMPED on every row (CYN for Northern Cyprus)")
    p.add_argument("--max", type=int, default=None,
                   help="cap the rows emitted; claims nothing about the board")
    a = ap.parse_args(argv)
    if a.cmd == "jobs":
        return cmd_jobs(a)
    ap.error("unknown command")


if __name__ == "__main__":
    sys.exit(main())
