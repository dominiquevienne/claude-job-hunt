#!/usr/bin/env python3
"""Fetch apprenticeship openings from La Bonne Alternance — a French state API.

Two things come back from one call, and the second is why this board exists:

  * **`jobs`** — posted apprenticeship ads, aggregated from other boards.
  * **`recruiters`** — companies that **take apprentices without having posted
    anything**. No other board here carries those, and for alternance they are
    most of the opportunity.

  GET https://api.apprentissage.beta.gouv.fr/api/job/v1/search
      ?latitude=&longitude=&radius=&departements=&romes=
      Authorization: Bearer <api key>
  → {"jobs": [...], "recruiters": [...], "warnings": [...]}

The key is **free and self-service** at api.apprentissage.beta.gouv.fr, and
read from the environment, never from config.yml — see `key()`.

**A sandbox key hands out staging URLs.** Every `recruiters[].apply.url`
measured came back on `labonnealternance-recette…`, which is the test
environment: give one to a candidate and it is a dead link. `search` flags them
rather than passing them off as real. See `RECETTE`.

Usage:
  labonnealternance.py search --departement 69
  labonnealternance.py search --lat 48.8566 --lon 2.3522 --radius 30
  labonnealternance.py search --departement 75 --rome M1805 --jobs-only

Output: one JSON object per line.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _ua import UA

from _secrets import get as secret_get
from _secrets import missing_note

API = "https://api.apprentissage.beta.gouv.fr/api/job/v1/search"
ACCESS_ENV = "LBA_API_KEY"

# Measured: both lists are capped, and the cap does not move with radius.
# A full-looking result is the ceiling, not the market.
JOBS_CAP = 300
RECRUITERS_CAP = 150

# A sandbox key returns apply URLs on the staging host for recruiters.
RECETTE = "labonnealternance-recette"

# Exactly two characters. See `dept_code` — every other shape fails silently
# and differently.
DEPT_RE = re.compile(r"^(?:\d{2}|2[AB])$")

# Boards this plugin sweeps directly. When La Bonne Alternance republishes one
# of their ads it carries the source's own id, so the duplicate is exact.
PARTNER_BOARDS = {
    "France Travail": "france-travail",
    "Meteojob": "meteojob",
}


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def key():
    """The API key: the environment, then the workspace file.

    Not a config.yml key: that file is read aloud, pasted into issues and
    backed up, and a bearer token has no business in it.
    """
    k = secret_get(ACCESS_ENV, "labonnealternance")
    if not k:
        die(missing_note([ACCESS_ENV], "labonnealternance",
                         "La Bonne Alternance",
                         "api.apprentissage.beta.gouv.fr — create an account "
                         "and generate a token"))
    return k


def call(params):
    url = API + "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {key()}",
        "Accept": "application/json",
        # **Sent nothing at all before**, so urllib announced
        # `Python-urllib/3.x` — not a declaration anybody chose, and the
        # opposite of what #120 settled. A key identifies the account; it does
        # not say who is calling. #130.
        "User-Agent": UA,
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:200]
        if e.code in (401, 403):
            die(f"the API rejected the key (HTTP {e.code}). Check {ACCESS_ENV}, "
                "and that the token has not expired in the developer "
                f"space.\n{detail}")
        die(f"La Bonne Alternance returned HTTP {e.code}: {detail}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach La Bonne Alternance: {e}")


def dept_code(v):
    """Validate a department code, because three shapes fail three ways.

    Measured, none of them an error:
      `69`  → 293 of 300 jobs in the Rhône.          correct
      `069` → **0 jobs**.                            silent zero
      `1`   → 300 jobs in 13, 14, 17 …               silent prefix match
      `075` → jobs in **07, the Ardèche**.           silently the wrong place

    The last is the worst kind of wrong answer: not empty, not everything, but
    a plausible board from somewhere else entirely. So the code is checked
    here rather than passed through.
    """
    v = str(v).strip().upper()
    if not DEPT_RE.match(v):
        die(f"{v!r} is not a department code for this API. It takes exactly "
            "two characters — `69`, `01`, `2A`. `069` returns nothing, `1` "
            "matches every department starting with 1, and `075` returns the "
            "Ardèche. None of them errors, so this is checked before asking.")
    return v


def card(x, kind):
    ident = x.get("identifier") or {}
    wp = x.get("workplace") or {}
    loc = wp.get("location") or {}
    dom = wp.get("domain") or {}
    naf = dom.get("naf") or {}
    offer = x.get("offer") or {}
    contract = x.get("contract") or {}
    apply_ = x.get("apply") or {}
    url = apply_.get("url")
    partner = ident.get("partner_label")
    board = PARTNER_BOARDS.get(partner)
    pid = ident.get("partner_job_id")
    out = {
        "id": ident.get("id"),
        "ledger_id": f"labonnealternance:{ident.get('id')}",
        # `kind` is the whole point of this board: an `opportunity` is a
        # company open to apprentices that has posted no ad at all.
        "kind": kind,
        "url": url,
        "title": offer.get("title"),
        # The employer is always named — this is not an agency board.
        "company": wp.get("brand") or wp.get("name") or wp.get("legal_name"),
        "siret": wp.get("siret"),
        "company_size": wp.get("size"),
        "website": wp.get("website"),
        "address": loc.get("address"),
        "naf": naf.get("label"),
        "opco": dom.get("opco"),
        "rome_codes": offer.get("rome_codes"),
        "contract_type": contract.get("type"),
        "contract_months": contract.get("duration"),
        "starts": contract.get("start"),
        "remote": contract.get("remote"),
        "source": partner,
        # Set when the ad was republished from a board this plugin sweeps
        # itself, using that board's own id. When the ledger already holds the
        # row, this is the same posting.
        "duplicate_of": f"{board}:{pid}" if board and pid else None,
        "description": offer.get("description"),
    }
    if url and RECETTE in url:
        # A sandbox key hands out test-environment links. Saying so is the
        # difference between "no apply link" and "a link that 404s for the
        # candidate after they have written the letter".
        out["url"] = None
        out["staging_url"] = url
        out["apply_url_unusable"] = True
    return out


def cmd_search(a):
    params = {}
    if a.departement:
        params["departements"] = [dept_code(d) for d in a.departement]
    if a.lat is not None and a.lon is not None:
        params.update({"latitude": a.lat, "longitude": a.lon})
        if a.radius is not None:
            params["radius"] = a.radius
    elif (a.lat is None) != (a.lon is None):
        die("--lat and --lon go together.")
    if a.rome:
        params["romes"] = ",".join(a.rome)
    if a.diploma:
        params["target_diploma_level"] = a.diploma
    if not params:
        die("give --departement, or --lat/--lon. An unfiltered call returns "
            "the caps below and tells you nothing about where the work is.")

    d = call(params)
    jobs = d.get("jobs") or []
    recruiters = d.get("recruiters") or []
    for w in d.get("warnings") or []:
        print(f"[lba] warning from the API: {json.dumps(w, ensure_ascii=False)}",
              file=sys.stderr)
    print(f"[lba] {len(jobs)} posted ads, {len(recruiters)} companies open to "
          "spontaneous applications", file=sys.stderr)
    if len(jobs) >= JOBS_CAP:
        print(f"[lba] {len(jobs)} is the cap, not the count — narrow with "
              "--rome or a smaller area rather than reading this as the "
              "whole market", file=sys.stderr)
    if len(recruiters) >= RECRUITERS_CAP:
        print(f"[lba] {len(recruiters)} companies is the cap too, and it does "
              "not move with --radius", file=sys.stderr)

    rows, staging = 0, 0
    for x in jobs:
        print(json.dumps(card(x, "job"), ensure_ascii=False))
        rows += 1
    if not a.jobs_only:
        for x in recruiters:
            c = card(x, "opportunity")
            staging += bool(c.get("apply_url_unusable"))
            print(json.dumps(c, ensure_ascii=False))
            rows += 1
    print(f"[lba] {rows} cards returned", file=sys.stderr)
    if staging:
        print(f"[lba] {staging} of them carry a **staging** apply URL "
              f"({RECETTE}…) and it is dropped: a sandbox key does not return "
              "usable links for companies. Ask support for a production key "
              "before relying on them.", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="ads and companies in an area")
    s.add_argument("--departement", action="append",
                   help="exactly two characters: 69, 01, 2A")
    s.add_argument("--lat", type=float)
    s.add_argument("--lon", type=float)
    s.add_argument("--radius", type=float, default=30)
    s.add_argument("--rome", action="append", help="ROME code, repeatable")
    s.add_argument("--diploma", help="target diploma level")
    s.add_argument("--jobs-only", action="store_true",
                   help="posted ads only, skipping the companies")
    s.set_defaults(func=cmd_search)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
