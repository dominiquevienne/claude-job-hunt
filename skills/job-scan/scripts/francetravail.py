#!/usr/bin/env python3
"""Fetch job ads from France Travail, the French public employment service.

France Travail (ex-Pôle emploi) publishes its whole vacancy database through a
free, documented REST API. It is the largest single source of French ads, and
it carries the SMEs, the public sector and the staffing agencies that no
meta-board indexes well.

Two things about this API decide the shape of this script, both measured on
2026-08-30 and both invisible from a single happy-path call:

  * A search with no `origineOffre` returns **only France Travail's own ads**,
    never the partner ads — which are 77% of the board. So a sweep runs both
    passes and says so. See `cmd_search`.
  * `range` cannot start past 3000 and cannot span more than 150, so at most
    the first 3150 hits of any search are reachable. Paging to the end is not
    the same as reading the board.

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

SCOPE = "api_offresdemploiv2 o2dsoffre"

ENV_ID = "FRANCE_TRAVAIL_CLIENT_ID"
ENV_SECRET = "FRANCE_TRAVAIL_CLIENT_SECRET"

# Measured 2026-08-30 against the live API, from its own 400 messages:
#   "La position de début doit être inférieure ou égale à 3000."
#   "La plage de résultats demandée est trop importante."   (span > 150)
# So the reachable window is offers 0..3149 — the first 3150 hits, no more.
MAX_START = 3000
MAX_PAGE = 150
REACHABLE = MAX_START + MAX_PAGE          # 3150

PUBLIEE_DEPUIS = {1, 3, 7, 14, 31}

# 1 = posted to France Travail directly. 2 = fed in by a partner board
# (Meteojob, DirectEmploi, Beetween, Gojob…). A search naming neither returns
# only 1 — see the module docstring and `cmd_search`.
ORIGINES = ("1", "2")


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
        if "invalid_scope" in detail:
            die("France Travail refused the scope. Retry with "
                f"--scope 'application_<your client_id> {scope}' — some "
                f"applications need the id in the scope.\n{detail}")
        if "invalid_client" in detail:
            die("France Travail did not recognise the credentials "
                "(invalid_client). Two causes, in order of likelihood: the "
                "secret was pasted across a line break and arrived truncated, "
                f"or {ENV_ID} is the application id rather than the OAuth "
                "client id. The subscription to 'Offres d'emploi v2' is not "
                f"the cause — that fails later, on the search.\n{detail}")
        die(f"token endpoint returned HTTP {e.code}: {detail}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach the France Travail token endpoint: {e}")


def api_message(raw):
    """The API states its refusals in French, in a `message` field. Use it."""
    try:
        return json.loads(raw).get("message") or raw[:200]
    except Exception:  # noqa: BLE001
        return raw[:200]


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
            # 204 is a real answer with an empty body: zero matches on a
            # search, and "this offer is gone" on a detail read. Returning {}
            # would make it indistinguishable from a parse failure.
            if r.status == 204:
                return 204, r.headers.get("Content-Range"), None
            raw = r.read()
            body = json.loads(raw) if raw else None
            return r.status, r.headers.get("Content-Range"), body
    except urllib.error.HTTPError as e:
        detail = api_message(e.read().decode(errors="replace"))
        if e.code == 400:
            die("France Travail refused the query (HTTP 400). It validates "
                "every parameter, so this is a malformed filter, not an empty "
                f"result:\n  {detail}")
        if e.code == 429:
            die("rate-limited (HTTP 429). The API publishes 10 requests per "
                "second per client in its X-Ratelimit headers; wait, do not "
                "loop.")
        die(f"France Travail returned HTTP {e.code}: {detail}")
    except Exception as e:  # noqa: BLE001
        die(f"could not reach the France Travail API: {e}")


def total_from(content_range):
    """`Content-Range: offres 0-149/13295` → 13295. `*/0` on a 204 → 0."""
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
        if not re.fullmatch(r"[0-9AB]{5}", a.commune.upper()):
            die(f"'{a.commune}' is not an INSEE commune code. It is five "
                "characters (2A/2B for Corsica), and it is not the postcode.")
        p["commune"] = a.commune
    if a.departement:
        p["departement"] = ",".join(a.departement)
    if a.region:
        p["region"] = ",".join(a.region)
    if a.distance is not None:
        if not a.commune:
            die("--distance only means something with --commune.")
        p["distance"] = a.distance
    elif a.commune:
        # Measured: commune alone behaves as distance=10, not distance=0 —
        # 75056 returned 25 676 bare and 9 709 at distance=0. Pin it, so the
        # radius is the caller's choice rather than the API's default.
        p["distance"] = 10
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
    if not p:
        die("give at least one filter (--departement, --commune, --mots-cles…)."
            " An unfiltered sweep is the whole national database, and only its "
            f"first {REACHABLE} rows are reachable anyway.")
    return p


def card(o, with_description=False):
    lieu = o.get("lieuTravail") or {}
    ent = o.get("entreprise") or {}
    sal = o.get("salaire") or {}
    origin = o.get("origineOffre") or {}
    partners = origin.get("partenaires") or []
    contact = o.get("contact") or {}
    apply_url = contact.get("urlPostulation")
    out = {
        "id": o.get("id"),
        "ledger_id": f"france-travail:{o.get('id')}",
        "url": AD_URL.format(o.get("id")),
        "title": o.get("intitule"),
        # Absent on about 1 ad in 18 overall, and on nearly 1 in 4 partner ads:
        # the employer is allowed to stay anonymous. Nothing else in the record
        # names them when this is None.
        "company": ent.get("nom"),
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
        "origin": origin.get("origine"),
        # The board the ad was fed in from, on origine 2. This — not
        # urlOrigine, which always points back at France Travail — is what
        # says the posting also lives somewhere else.
        "partner": partners[0].get("nom") if partners else None,
        "partner_url": partners[0].get("url") if partners else None,
        # Where the employer actually takes applications, when they said so.
        # Present on France Travail's own ads only, and often an ATS this
        # plugin already sweeps.
        "apply_url": apply_url,
        "apply_host": (urllib.parse.urlparse(apply_url).netloc
                       if apply_url else None),
    }
    if with_description:
        out["description"] = to_text(o.get("description"))
    return out


def cmd_token(a):
    t = token(a.scope)
    print(f"[france-travail] token acquired, {len(t)} chars", file=sys.stderr)
    print(json.dumps({"ok": True, "scope": a.scope}))


def sweep(params, a, origine):
    """One origine's worth of results. Returns rows emitted."""
    size = min(a.size, MAX_PAGE)
    rows, total = 0, None
    for page in range(a.page, a.page + a.pages):
        start = page * size
        if start > MAX_START:
            print(f"[france-travail] origine {origine}: stopping at offset "
                  f"{start}. The API refuses a start past {MAX_START}, so only "
                  f"the first {REACHABLE} hits of a search are reachable. This "
                  "sweep is truncated — narrow it (a single department, a "
                  "codeROME, publieeDepuis) rather than paging further.",
                  file=sys.stderr)
            break
        end = min(start + size, REACHABLE) - 1
        status, crange, body = call(
            "/offres/search",
            {**params, "origineOffre": origine, "range": f"{start}-{end}"},
            a.scope)
        if status == 204 or not body:
            if total is None:
                print(f"[france-travail] origine {origine}: 0 offers "
                      "(HTTP 204) — that is an empty result, not an error",
                      file=sys.stderr)
            break
        if total is None:
            total = total_from(crange)
            print(f"[france-travail] origine {origine}: {total} offers match "
                  f"(HTTP {status})", file=sys.stderr)
            if total is not None and total > REACHABLE:
                print(f"[france-travail] origine {origine}: only the first "
                      f"{REACHABLE} of {total} are reachable — this sweep "
                      "cannot be complete", file=sys.stderr)
        results = body.get("resultats") or []
        if not results:
            break
        for o in results:
            print(json.dumps(card(o), ensure_ascii=False))
            rows += 1
        if len(results) < size:
            break
    return rows


def cmd_search(a):
    params = build_params(a)
    origines = (a.origine_offre,) if a.origine_offre else ORIGINES
    if not a.origine_offre:
        # Measured 2026-08-30: a search naming no origine returned origine 1
        # and nothing else, across the whole reachable window. Partner ads are
        # 77% of the board and are simply absent from it. Both passes, always,
        # unless the caller asked for one.
        print("[france-travail] sweeping both origins: a search that names "
              "neither returns France Travail's own ads only, and silently "
              "omits the partner ads that are most of the board",
              file=sys.stderr)
    rows = sum(sweep(params, a, o) for o in origines)
    print(f"[france-travail] {rows} cards returned", file=sys.stderr)


def cmd_ad(a):
    status, _, body = call(f"/offres/{a.id}", scope=a.scope)
    if status == 204 or not body:
        die(f"offer {a.id} is gone — the API answers 204 with an empty body "
            "for an id it no longer serves. Record it as discarded, do not "
            "retry.", code=3)
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
    s.add_argument("--distance", type=int,
                   help="km around --commune; defaults to 10, which is also "
                        "what the API applies when it is omitted")
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
    s.add_argument("--origine-offre", choices=list(ORIGINES),
                   help="1 France Travail's own, 2 partner boards. Omit to "
                        "sweep both, which is the only complete option")
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
