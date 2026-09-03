#!/usr/bin/env python3
"""Fetch job ads from apec.fr, France's executive employment agency.

The APEC is the Association pour l'emploi des cadres — the reference board for
French management and senior professional roles, carrying **77 023 ads** on the
day this was written. Its search backend answers unauthenticated JSON, with no
key, no cookie and no browser.

Two things shape this adapter, both measured on 2026-08-30:

  * **Pagination is unlimited.** `startIndex` walked to 76 900 and still
    returned 100 disjoint ads. Unlike every other French board here, the whole
    board is reachable — no cap, no truncation.
  * **The description is not.** `texteOffre` is a fixed 283-character teaser,
    cut mid-sentence, on every ad. The full text lives behind a detail endpoint
    fronted by a **DataDome captcha**, and this plugin never works around one.
    So this adapter is excellent triage and does not pretend to be more.

Usage:
  apec.py search --lieux 75 --lieux 92 --mots-cles "data engineer" --pages 3
  apec.py search --types-contrat 101888 --teletravail 20765
  apec.py filters --lieux 69

Output: one JSON object per line (search), or one JSON object (filters).
"""

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _robots import allowed as robots_allowed

API = "https://www.apec.fr/cms/webservices/rechercheOffre"
AD_URL = ("https://www.apec.fr/candidat/recherche-emploi.html"
          "/emploi/detail-offre/{}")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# Measured: range=100 returns 100, range=200 silently returns 20. An
# over-large page is not refused, it is quietly downgraded — so clamp rather
# than pass the caller's number through.
MAX_PAGE = 100

# The teaser's exact length on all 300 ads sampled. Used to say "truncated"
# with confidence rather than guessing from an ellipsis.
TEASER_LEN = 283

# Employers who pay to stay anonymous get this sentinel in `nomCommercial`,
# which is a filled field containing no employer. 10 of 300 ads.
CONFIDENTIAL = "ZZ_Confidentiel"


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def _robots_gate(url, tag, exit_code=7):
    """Ask before fetching — per host and **per path**. Issues #100, #101.

    `verdict()` answers *is this host closed in one block*. **A site that
    refuses its ad path while leaving its root open passes that and refuses
    every advertisement** — `empleate.gob.hn` does exactly that, closing
    `/Vacantes/` to `User-agent: *` with `/` absent.

    It sits **inside the fetch function**, so every request is covered rather
    than the first one, and a refusal **stops the command** with exit 7 and the
    module's own words. **This adapter decides nothing about what a refusal
    means** — deciding is what turns a check into a decoration.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return None
    a = robots_allowed(parts.netloc, parts.path or "/")
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", exit_code)
    if a.get("requested_host") and a["host"] != a["requested_host"]:
        print(f"[hellowork] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts. A platform that has "
              f"been renamed reaches an adapter this way before it reaches it "
              f"as a rename.", file=__import__("sys").stderr)
    return a



def call(body):
    _robots_gate(API, 'apec')
    req = urllib.request.Request(
        API, data=json.dumps(body).encode(),
        headers={"User-Agent": UA, "Content-Type": "application/json",
                 "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:200]
        if e.code == 400:
            die("the APEC refused the query (HTTP 400). It validates filter "
                "values, so this is a bad id — an unknown `lieux` code, for "
                f"one — not an empty result.\n{detail}")
        if e.code == 500:
            die("the APEC answered HTTP 500. Some filter names the site's own "
                "UI uses are not accepted here and fail this way rather than "
                f"being ignored; check the ones you passed.\n{detail}")
        if e.code == 403 and "captcha" in detail:
            die("blocked by the APEC's captcha (DataDome). Stop — the plugin "
                "never solves a captcha and never rotates its User-Agent to "
                "avoid one. Wait, and slow the sweep down.")
        die(f"the APEC returned HTTP {e.code}: {detail}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach the APEC: {e}")


def to_text(markup):
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>", "\n", markup or "")
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt).replace(" ", " ")
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", txt).strip()


def build(a, start, size):
    body = {
        "typeClient": "CADRE",
        "activeFiltre": True,
        "sorts": [{"type": a.sort, "direction": a.direction}],
        "pagination": {"range": size, "startIndex": start},
    }
    if a.mots_cles:
        body["motsCles"] = " ".join(a.mots_cles)
    if a.lieux:
        body["lieux"] = a.lieux
    if a.fonctions:
        body["fonctions"] = a.fonctions
    if a.types_contrat:
        body["typesContrat"] = a.types_contrat
    if a.teletravail:
        body["typesTeletravail"] = a.teletravail
    if a.experience:
        body["niveauxExperience"] = a.experience
    if a.secteurs:
        body["secteursActivite"] = a.secteurs
    return body


def card(o):
    name = o.get("nomCommercial")
    confidential = bool(o.get("offreConfidentielle")) or name == CONFIDENTIAL
    teaser = to_text(o.get("texteOffre"))
    ident = o.get("id")
    return {
        "id": ident,
        "ledger_id": f"apec:{ident}",
        "url": AD_URL.format(ident),
        "reference": o.get("numeroOffre"),
        "title": o.get("intitule"),
        # None rather than the sentinel: a confidential ad names nobody, and
        # "ZZ_Confidentiel" reaching the ledger as an employer is worse than a
        # blank, because it looks like a company.
        "company": None if confidential else name,
        "confidential": confidential,
        "location": o.get("lieuTexte"),
        "salary": o.get("salaireTexte"),
        "published": o.get("datePublication"),
        "validated": o.get("dateValidation"),
        "contract_type_id": o.get("typeContrat"),
        "sector_id": o.get("secteurActivite"),
        "lat": o.get("latitude"),
        "lon": o.get("longitude"),
        # Named `teaser`, never `description`: it is cut mid-sentence at a
        # fixed length. Anything scoring this must know it is not the ad.
        "teaser": teaser,
        "teaser_truncated": len(o.get("texteOffre") or "") >= TEASER_LEN,
        "full_text_available": False,
    }


def cmd_search(a):
    size = min(a.size, MAX_PAGE)
    if a.size > MAX_PAGE:
        print(f"[apec] page size clamped to {MAX_PAGE}: a larger `range` is "
              "not refused, it silently returns 20.", file=sys.stderr)
    rows, total = 0, None
    for page in range(a.page, a.page + a.pages):
        start = page * size
        d = call(build(a, start, size))
        if total is None:
            total = d.get("totalCount")
            print(f"[apec] {total} ads match", file=sys.stderr)
            if total == 0:
                print("[apec] zero results — the API refuses an unknown filter "
                      "id with a 400, so this is a real empty set, not a typo",
                      file=sys.stderr)
        results = d.get("resultats") or []
        if not results:
            break
        for o in results:
            print(json.dumps(card(o), ensure_ascii=False))
            rows += 1
        if len(results) < size:
            break
        time.sleep(a.delay)
    print(f"[apec] {rows} cards returned of {total}", file=sys.stderr)
    print("[apec] every card carries a 283-character teaser, not the ad. Score "
          "the triage fields — title, employer, location, salary — and read "
          "the full text on the site; `cover-letter <URL>` will ask for it to "
          "be pasted, because the detail endpoint is behind a captcha.",
          file=sys.stderr)


def cmd_filters(a):
    """Dump the facet ids and their counts.

    There is no public referential: the API publishes ids, never labels. But
    the search response returns every facet with a count, and those counts are
    what let each filter name here be verified — passing `typesContrat:
    ["101888"]` returned exactly the 70 948 the facet claimed. Treat this as
    the id catalogue, and confirm any id by the count it produces.
    """
    d = call(build(a, 0, 1))
    out = {"totalCount": d.get("totalCount"), "filters": {}}
    for f in d.get("offreFilters") or []:
        out["filters"][f.get("offreFiltering")] = {
            str(i.get("key")): i.get("count") for i in
            (f.get("offreFilterItems") or [])}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    print("[apec] ids only — the API publishes no labels for them. Confirm an "
          "id by passing it and checking the total matches the count here.",
          file=sys.stderr)


def add_filters(p):
    p.add_argument("--mots-cles", action="append")
    p.add_argument("--lieux", action="append",
                   help="department code as a string ('75', '69'); also 799 "
                        "France, 102099 abroad. An unknown value is a 400")
    p.add_argument("--fonctions", action="append", help="JOB_CODE id")
    p.add_argument("--types-contrat", action="append",
                   help="CONTRACT_TYPE id — 101888 is the big one (70 948)")
    p.add_argument("--teletravail", action="append", help="REMOTE_WORK id")
    p.add_argument("--experience", action="append", help="EXPERIENCE id")
    p.add_argument("--secteurs", action="append", help="NAF_CODE id")
    p.add_argument("--sort", default="DATE", choices=["DATE", "SCORE"])
    p.add_argument("--direction", default="DESCENDING",
                   choices=["DESCENDING", "ASCENDING"])


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="list ads")
    add_filters(s)
    s.add_argument("--page", type=int, default=0)
    s.add_argument("--pages", type=int, default=1)
    s.add_argument("--size", type=int, default=50, help=f"max {MAX_PAGE}")
    s.add_argument("--delay", type=float, default=1.0,
                   help="seconds between pages (default 1)")
    s.set_defaults(func=cmd_search)

    f = sub.add_parser("filters", help="the facet id catalogue, with counts")
    add_filters(f)
    f.set_defaults(func=cmd_filters)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
