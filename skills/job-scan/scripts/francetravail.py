#!/usr/bin/env python3
"""Fetch job ads from France Travail, the French public employment service.

France Travail (ex-Pôle emploi) publishes its whole vacancy database through a
free, documented REST API. It is the largest single source of French ads, and
it carries the SMEs, the public sector and the staffing agencies that no
meta-board indexes well.

Unlike every other no-browser adapter here, this one needs credentials: an
OAuth2 client_id / client_secret pair, created for free at francetravail.io.
They are read from the environment, never from config.yml — see `creds()`.

Usage:
  francetravail.py token                       # check the credentials work
  francetravail.py search --departement 75 --publiee-depuis 7 --pages 3
  francetravail.py search --commune 69381 --distance 20 --mots-cles "infirmier"
  francetravail.py ad <id>
  francetravail.py referentiel departements

Output: one JSON object per line (search), or one JSON object (ad).
"""

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

TOKEN_URL = ("https://entreprise.francetravail.fr/connexion/oauth2/"
             "access_token?realm=%2Fpartenaire")
API = "https://api.francetravail.io/partenaire/offresdemploi/v2"
AD_URL = "https://candidat.francetravail.fr/offres/recherche/detail/{}"
UA = "Mozilla/5.0 (compatible; claude-job-hunt/1.x; +personal job search)"

# The scope the API subscription grants. Some applications also require
# "application_<client_id>" as a third element; --scope overrides the whole
# string when the token call comes back with invalid_scope.
SCOPE = "api_offresdemploiv2 o2dsoffre"

ENV_ID = "FRANCE_TRAVAIL_CLIENT_ID"
ENV_SECRET = "FRANCE_TRAVAIL_CLIENT_SECRET"

# The API serves at most the first 1 150 hits of any search: range goes from
# 0-0 to 1000-1149, and 150 is the largest page. A search wider than that is
# not paginated to the end — it is truncated, and the caller has to narrow it.
MAX_PAGE = 150
MAX_OFFSET = 1149

# `commune` takes an INSEE code, and the three cities with arrondissements do
# not have a usable one: their aggregate code returns nothing. Map each to its
# first arrondissement so a wrong answer becomes a loud one.
ARRONDISSEMENT_ONLY = {
    "75056": ("Paris", "75101-75120"),
    "69123": ("Lyon", "69381-69389"),
    "13055": ("Marseille", "13201-13216"),
}

PUBLIEE_DEPUIS = {1, 3, 7, 14, 31}


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def creds():
    """client_id / client_secret, from the environment only.

    Deliberately not a config.yml key. config.yml is a plain file in the user's
    workspace that gets read aloud, copied into issues and backed up; an OAuth
    secret does not belong in it.
    """
    cid, secret = os.environ.get(ENV_ID), os.environ.get(ENV_SECRET)
    if not cid or not secret:
        die(f"set {ENV_ID} and {ENV_SECRET} in the environment. Create them "
            "for free at https://francetravail.io — an account, an "
            "application, then subscribe it to 'Offres d'emploi v2'. They are "
            "never read from config.yml.")
    return cid, secret


_token = None


def token(scope=SCOPE):
    global _token
    if _token:
        return _token
    cid, secret = creds()
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": cid,
        "client_secret": secret,
        "scope": scope,
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=body, headers={
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            _token = json.load(r)["access_token"]
            return _token
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        if e.code == 400 and "invalid_scope" in detail:
            die("France Travail refused the scope. Retry with "
                f"--scope 'application_<your client_id> {scope}' — some "
                f"applications need the id in the scope.\n{detail}")
        if e.code in (400, 401):
            die("France Travail rejected the credentials (HTTP "
                f"{e.code}). Check {ENV_ID}/{ENV_SECRET}, and that the "
                f"application is subscribed to 'Offres d'emploi v2'.\n{detail}")
        die(f"token endpoint returned HTTP {e.code}: {detail}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach the France Travail token endpoint: {e}")


def call(path, params=None, scope=SCOPE):
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Authorization": f"Bearer {token(scope)}",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            # 204 means the request was fine and there is nothing to return —
            # a real answer, not a failure. Returning {} here would make it
            # indistinguishable from an empty result set, so say which it was.
            if r.status == 204:
                return 204, None, None
            raw = r.read()
            body = json.loads(raw) if raw else None
            return r.status, r.headers.get("Content-Range"), body
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        if e.code == 400:
            die("France Travail refused the query (HTTP 400). It validates its "
                f"parameters, so this is a malformed filter, not an empty "
                f"result.\n{detail}")
        if e.code == 404:
            die("that offer no longer exists (HTTP 404) — record it as "
                "discarded, do not retry.", code=3)
        if e.code == 429:
            die("rate-limited (HTTP 429). Wait before retrying; do not loop.")
        die(f"France Travail returned HTTP {e.code}: {detail}")
    except Exception as e:  # noqa: BLE001
        die(f"could not reach the France Travail API: {e}")


def total_from(content_range):
    """`Content-Range: offres 0-149/1247` → 1247. Absent on a full 200."""
    if not content_range:
        return None
    m = re.search(r"/(\d+)\s*$", content_range)
    return int(m.group(1)) if m else None


def to_text(markup):
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", markup or "")
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", txt)
    txt = re.sub(r"(?i)<li[^>]*>", "- ", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", txt).strip()


def build_params(a):
    p = {}
    if a.mots_cles:
        p["motsCles"] = " ".join(a.mots_cles)
    if a.commune:
        warn = ARRONDISSEMENT_ONLY.get(a.commune)
        if warn:
            city, codes = warn
            die(f"{a.commune} is the aggregate INSEE code for {city}, which "
                f"this API does not search on. Use an arrondissement code "
                f"({codes}) — or --departement, which does cover the whole "
                "city.")
        p["commune"] = a.commune
    if a.departement:
        p["departement"] = ",".join(a.departement)
    if a.region:
        p["region"] = ",".join(a.region)
    if a.distance is not None:
        if not a.commune:
            die("--distance only means something with --commune; on its own "
                "it is accepted and does nothing.")
        p["distance"] = a.distance
    if a.type_contrat:
        p["typeContrat"] = ",".join(a.type_contrat)
    if a.experience:
        p["experience"] = a.experience
    if a.qualification:
        p["qualification"] = a.qualification
    if a.temps_plein is not None:
        p["tempsPlein"] = "true" if a.temps_plein else "false"
    if a.code_rome:
        p["codeROME"] = ",".join(a.code_rome)
    if a.publiee_depuis is not None:
        if a.publiee_depuis not in PUBLIEE_DEPUIS:
            die(f"--publiee-depuis takes only {sorted(PUBLIEE_DEPUIS)} days; "
                "any other value is refused with HTTP 400.")
        p["publieeDepuis"] = a.publiee_depuis
    if a.origine_offre:
        p["origineOffre"] = a.origine_offre
    if not p:
        die("give at least one filter (--departement, --commune, --mots-cles…)."
            " An unfiltered sweep is the whole national database, and the API "
            f"would hand back only its first {MAX_OFFSET + 1} rows anyway.")
    return p


def card(o, with_description=False):
    lieu = o.get("lieuTravail") or {}
    ent = o.get("entreprise") or {}
    sal = o.get("salaire") or {}
    origin = o.get("origineOffre") or {}
    partners = origin.get("partenaires") or []
    external = origin.get("urlOrigine")
    out = {
        "id": o.get("id"),
        "ledger_id": f"france-travail:{o.get('id')}",
        "url": AD_URL.format(o.get("id")),
        "title": o.get("intitule"),
        # Employers may post without naming themselves; when they do, this is
        # None and the ledger's employer dedup has nothing to work with.
        "company": ent.get("nom"),
        "company_described": bool(ent.get("description")),
        "city": lieu.get("libelle"),
        "commune_insee": lieu.get("commune"),
        "postal_code": lieu.get("codePostal"),
        "contract": o.get("typeContratLibelle") or o.get("typeContrat"),
        "contract_nature": o.get("natureContrat"),
        "duration": o.get("dureeTravailLibelle"),
        "experience": o.get("experienceLibelle"),
        "qualification": o.get("qualificationLibelle"),
        "salary": sal.get("libelle"),
        "rome_code": o.get("romeCode"),
        "rome_label": o.get("romeLibelle"),
        "sector": o.get("secteurActiviteLibelle"),
        "published": o.get("dateCreation"),
        "updated": o.get("dateActualisation"),
        "alternance": o.get("alternance"),
        # origine 1 = posted to France Travail directly; 2 = syndicated from a
        # partner board, where urlOrigine is the ad's real home and the likely
        # duplicate of a row another adapter already wrote.
        "origin": origin.get("origine"),
        "origin_partner": partners[0].get("nom") if partners else None,
        "external_url": external,
        "external_host": (urllib.parse.urlparse(external).netloc
                          if external else None),
    }
    if with_description:
        out["description"] = to_text(o.get("description"))
    return out


def cmd_token(a):
    t = token(a.scope)
    print(f"[france-travail] token acquired, {len(t)} chars", file=sys.stderr)
    print(json.dumps({"ok": True, "scope": a.scope}))


def cmd_search(a):
    params = build_params(a)
    size = min(a.size, MAX_PAGE)
    rows, total = 0, None
    for page in range(a.page, a.page + a.pages):
        start = page * size
        if start > MAX_OFFSET:
            print(f"[france-travail] stopping at offset {start}: the API "
                  f"serves only the first {MAX_OFFSET + 1} hits of a search. "
                  "Narrow it — by departement, by codeROME, by publieeDepuis "
                  "— rather than paging further; the rest is not reachable.",
                  file=sys.stderr)
            break
        end = min(start + size - 1, MAX_OFFSET)
        status, crange, body = call("/offres/search",
                                    {**params, "range": f"{start}-{end}"},
                                    a.scope)
        if status == 204 or not body:
            print("[france-travail] the API answered 'no content' — that is "
                  "zero matching offers, not an error", file=sys.stderr)
            break
        if total is None:
            total = total_from(crange)
            print(f"[france-travail] {total if total is not None else '?'} "
                  f"offers match (HTTP {status})", file=sys.stderr)
            if total == 0:
                print("[france-travail] zero results — check the INSEE commune "
                      "code and the departement before concluding the market "
                      "is empty", file=sys.stderr)
            if total is not None and total > MAX_OFFSET + 1:
                print(f"[france-travail] {total} matches but only the first "
                      f"{MAX_OFFSET + 1} are reachable — this sweep is "
                      "truncated, not complete", file=sys.stderr)
        results = body.get("resultats") or []
        if not results:
            break
        for o in results:
            print(json.dumps(card(o), ensure_ascii=False))
            rows += 1
        if len(results) < size:
            break
    print(f"[france-travail] {rows} cards returned", file=sys.stderr)


def cmd_ad(a):
    status, _, body = call(f"/offres/{a.id}", scope=a.scope)
    if status == 204 or not body:
        die(f"offer {a.id} exists but the API returned no content for it "
            "(HTTP 204) — read it on the site instead of guessing.", code=3)
    print(json.dumps(card(body, with_description=True),
                     ensure_ascii=False, indent=1))


def cmd_referentiel(a):
    _, _, body = call(f"/referentiel/{a.name}", scope=a.scope)
    print(json.dumps(body, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scope", default=SCOPE,
                   help="OAuth scope; override when the token call returns "
                        "invalid_scope")
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("token", help="check the credentials work")
    t.set_defaults(func=cmd_token)

    s = sub.add_parser("search", help="list offers")
    s.add_argument("--mots-cles", action="append")
    s.add_argument("--commune", help="INSEE code, not a postcode")
    s.add_argument("--departement", action="append", help="'75', repeatable")
    s.add_argument("--region", action="append")
    s.add_argument("--distance", type=int, help="km around --commune")
    s.add_argument("--type-contrat", action="append",
                   help="CDI, CDD, MIS (intérim), SAI…")
    s.add_argument("--experience", choices=["1", "2", "3"],
                   help="1 <1 an, 2 de 1 à 3 ans, 3 >3 ans")
    s.add_argument("--qualification", choices=["0", "9"],
                   help="0 non-cadre, 9 cadre")
    s.add_argument("--temps-plein", type=lambda v: v.lower() == "true",
                   default=None, help="true|false")
    s.add_argument("--code-rome", action="append", help="'M1805', repeatable")
    s.add_argument("--publiee-depuis", type=int,
                   help="days: 1, 3, 7, 14 or 31 only")
    s.add_argument("--origine-offre", choices=["1", "2"],
                   help="1 France Travail, 2 partner boards")
    s.add_argument("--page", type=int, default=0)
    s.add_argument("--pages", type=int, default=1)
    s.add_argument("--size", type=int, default=50,
                   help=f"per page, max {MAX_PAGE}")
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="read one offer in full")
    d.add_argument("id")
    d.set_defaults(func=cmd_ad)

    r = sub.add_parser("referentiel", help="read a reference list")
    r.add_argument("name", help="departements, communes, typesContrats, "
                                "metiers, regions, naturesContrats…")
    r.set_defaults(func=cmd_referentiel)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
