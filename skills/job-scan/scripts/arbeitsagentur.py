#!/usr/bin/env python3
"""Fetch German ads from the Bundesagentur für Arbeit — the largest job
database in Europe, and a board you cannot sweep.

**994 348 live ads.** Germany's federal employment agency, through the API the
German state documents at `jobsuche.api.bund.dev`. It is the fourth national
public employment service here after `job-room.md` (CH), `france-travail.md`
(FR) and `empleate.md` (ES), **the first German adapter of any kind**, and
thirty-five times the size of the largest board this repository had.

  GET jobsuche.api.bund.dev/openapi.yaml          → the state's own spec
  GET /pc/v6/jobs?wo=…&size=100&page=…            → the list, X-API-Key header
  GET /pc/v4/jobdetails/{base64(referenznummer)}  → the ad text

**No browser, no account, and the key is published in the specification** —
`clientId: jobboerse-jobsuche`, sent as `X-API-Key`. Nothing here is a
credential belonging to anybody: it is the identifier the operator prints in
its own public documentation for third parties to use.

`arbeitsagentur.de/robots.txt` is four lines and opens everything:
`Disallow:` empty, `Allow: /`. No crawler and no AI agent is named.

THE THING TO UNDERSTAND BEFORE ANYTHING ELSE: **you cannot read this board.**

    page=100, size=100   → 200, 100 ads
    page=101             → 400

**The reachable window is 10 000 ads per query, and the board is 994 348.**
Berlin alone is 45 901. A query answers with `maxErgebnisse: 45901` and will
hand over 10 000 of them, and there is no parameter that lifts the ceiling.

So the number this API reports is **not** the number it will give you, and an
adapter that pages until the pages run out will report a full sweep of Berlin
having read 22% of it. Every count printed here is therefore checked against
the ceiling *before* any paging, and a query that cannot be delivered whole is
**refused with the arithmetic**, not silently truncated. See `reachable`.

The way through is to slice until each slice fits. Measured:

    (no filter)                                   994 346   unreachable
    wo=Berlin                                      45 901   unreachable
    wo=Berlin & veroeffentlichtseit=7               8 786   fits
    wo=Berlin & veroeffentlichtseit=1               3 114   fits
    berufsfeld=Informatik                          10 002   MISSES BY TWO
    berufsfeld=Informatik & veroeffentlichtseit=7   1 775   fits

`berufsfeld=Informatik` is the one to remember: 10 002 against a ceiling of
10 000. It looks like it fits.

WHAT IT CARRIES THAT NOTHING ELSE HERE DOES. **`istArbeitnehmerUeberlassung`** —
the ad's own declaration that the work is *Leiharbeit*, hired out through a
temp agency, true on **15 of 40**. Every agency board in this repository —
`adecco.md`, `randstad-fr.md`, `crit.md`, `infoempleo.md` — leaves the reader to
infer that from the employer's name. This one states it, because German law
requires the employer to. `istPrivateArbeitsvermittlung` (5 of 40) marks
private placement the same way.

And **`allianzpartnerName` on 40 of 40** names the channel the ad arrived
through: `arbeitsagentur.de` on 8 of 40 — posted directly — and a partner on
the other 32. The board says out loud how much of itself is syndicated.

Usage:
  arbeitsagentur.py count --wo Berlin
  arbeitsagentur.py search --wo Berlin --seit 7 --limit 50
  arbeitsagentur.py read --wo München --seit 3 --limit 20

Output: one JSON object per line.
"""

import argparse
import base64
import collections
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body

ROOT = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service"
JOBS = ROOT + "/pc/v6/jobs"
DETAIL = ROOT + "/pc/v4/jobdetails/{}"
SPEC = "https://jobsuche.api.bund.dev/openapi.yaml"
# Printed in the operator's own OpenAPI description, for third parties.
API_KEY = "jobboerse-jobsuche"
from _ua import UA
# page=101 answers 400. 100 pages of 100 is the whole window.
PAGE_SIZE = 100
MAX_PAGE = 100
CEILING = PAGE_SIZE * MAX_PAGE

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[arbeitsagentur] {msg}", file=sys.stderr)


def api(url, retries=2, missing_ok=False):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "X-API-Key": API_KEY,
        "Accept": "application/json",
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(decode_body(r.read(), r.headers)[0])
        except urllib.error.HTTPError as exc:
            if exc.code in (404, 410) and missing_ok:
                return None
            if exc.code == 403:
                # The spec also lists /pc/v4/app/jobs, which answers 403 with a
                # one-byte body. Only /pc/v6/jobs is live. Say so rather than
                # letting a stale path read as a key problem.
                die("403 from the API. The key is the published "
                    f"{API_KEY!r}, and it works on /pc/v6/jobs — the older "
                    "/pc/v4/app/jobs path in the same specification is dead "
                    f"and answers 403 for everyone.\n  {url}")
            if attempt == retries:
                die(f"{url}: HTTP {exc.code}")
            time.sleep(1.5 * (attempt + 1))
        except (urllib.error.URLError, OSError) as exc:
            if attempt == retries:
                die(f"{url}: {exc}")
            time.sleep(1.5 * (attempt + 1))
    return None


def query(**params):
    params = {k: v for k, v in params.items() if v not in (None, "")}
    return JOBS + "?" + urllib.parse.urlencode(params)


def count(a, size=1, page=1):
    d = api(query(was=a.was, wo=a.wo, berufsfeld=a.berufsfeld,
                  arbeitgeber=a.arbeitgeber, veroeffentlichtseit=a.seit,
                  umkreis=a.umkreis, size=size, page=page))
    return d or {}


def describe(a):
    bits = []
    for k, v in (("was", a.was), ("wo", a.wo), ("berufsfeld", a.berufsfeld),
                 ("arbeitgeber", a.arbeitgeber), ("seit", a.seit),
                 ("umkreis", a.umkreis)):
        if v not in (None, ""):
            bits.append(f"{k}={v}")
    return " ".join(bits) or "(no filter — the whole board)"


def reachable(total, a, wanted):
    """Refuse to report a count the API will not deliver.

    `maxErgebnisse` is the number of matches; the API will hand over at most
    10 000 of them and there is no parameter that lifts that. Reporting the
    first without the second is the failure `shared/never-fail-silently.md`
    exists to prevent — the run would say "45 901 ads in Berlin" and read
    10 000, and nothing downstream could tell.
    """
    if total <= CEILING or (wanted and wanted <= CEILING):
        return
    die(f"this query matches {total} ads and the API will only ever return "
        f"{CEILING} of them — {total - CEILING} are unreachable, and no "
        "parameter lifts the ceiling (page 101 answers HTTP 400).\n"
        f"  query: {describe(a)}\n"
        "Narrow it until it fits, then run the slices. What works, measured:\n"
        "  --seit 7   on a city   (Berlin 45 901 → 8 786)\n"
        "  --seit 1   for a daily re-scan (Berlin → 3 114)\n"
        "  --was      a job title  (Berlin + 'Entwickler' → 173)\n"
        "Or pass --limit N with N <= 10000 to take the first N knowingly.")


def text_of(s):
    if not isinstance(s, str):
        return None
    return WS_RE.sub(" ", TAG_RE.sub(" ", s)).strip() or None


def money(x):
    lo, hi = x.get("gehaltsspanneVon"), x.get("gehaltsspanneBis")
    fixed = x.get("festgehalt")
    kind = x.get("verguetungsangabe")
    # KEINE_ANGABEN is the majority. STUNDENLOHN means the figures are an
    # hourly rate — 18.50 is not a monthly salary, and reading it as one is
    # the join.md minor-units error in a different disguise.
    return lo, hi, fixed, (kind if kind != "KEINE_ANGABEN" else None)


def place(x):
    locs = x.get("stellenlokationen") or []
    first = locs[0] if locs else {}
    adr = first.get("adresse") or {}
    return {
        "street": " ".join(v for v in (adr.get("strasse"),
                                       adr.get("hausnummer")) if v) or None,
        "postcode": adr.get("plz"),
        "city": adr.get("ort"),
        "district": adr.get("ortsteil"),
        "region": adr.get("region"),
        "country": adr.get("land"),
        "latitude": first.get("breite"),
        "longitude": first.get("laenge"),
        "locations_count": len(locs),
    }


def card(x, detail=None):
    ref = x.get("referenznummer")
    lo, hi, fixed, kind = money(x)
    p = place(x)
    out = {
        "id": ref,
        "ledger_id": f"arbeitsagentur:{ref}",
        # The reference is the key everywhere: the detail call is its base64,
        # and this is the page a human opens.
        "url": "https://www.arbeitsagentur.de/jobsuche/jobdetail/"
               + (ref or ""),
        "title": x.get("stellenangebotsTitel"),
        # Named on 200 of 200.
        "company": x.get("firma"),
        "occupation": x.get("hauptberuf"),
        "all_occupations": x.get("alleBerufe"),
        "offer_kind": x.get("stellenangebotsart"),
        "contract_duration": x.get("vertragsdauer"),
        "full_time": x.get("arbeitszeitVollzeit"),
        # 20 of 200. "Suitable for a career changer" — stated by the employer,
        # and the only field of its kind in this repository.
        "open_to_career_changers": x.get("quereinstiegGeeignet"),
        "salary_min": lo,
        "salary_max": hi,
        "salary_fixed": fixed,
        # STUNDENLOHN on most of the ads that state anything: the figures are
        # an HOURLY rate, not a monthly one.
        "salary_kind": kind,
        "salary_currency": "EUR" if (lo or hi or fixed) else None,
        "published": x.get("datumErsteVeroeffentlichung"),
        "updated": x.get("aenderungsdatum"),
        "starts": (x.get("eintrittszeitraum") or {}).get("von"),
        "external_url": x.get("externeURL"),
        # 38 of 200 — an anonymised ad, applied to through the agency.
        "reference_only": x.get("chiffrenummer"),
        "employer_hash": x.get("arbeitgeberKundennummerHash"),
    }
    out.update(p)
    if detail:
        out.update({
            "description": text_of(detail.get("stellenangebotsBeschreibung")),
            # Detail-only, and the reason to spend the request. German law
            # makes the employer declare this, so it is the publisher's own
            # statement rather than an inference from a name.
            "is_temp_agency_work": bool(
                detail.get("istArbeitnehmerUeberlassung")),
            "is_private_placement": bool(
                detail.get("istPrivateArbeitsvermittlung")),
            "education_required": detail.get("geforderterBildungsabschluss"),
            # The channel the ad came in through — arbeitsagentur.de means it
            # was posted here directly, anything else is syndicated.
            "partner_channel": detail.get("allianzpartnerName"),
            "partner_url": detail.get("allianzpartnerUrl"),
            "detail_read": True,
        })
    else:
        out["detail_read"] = False
    return out


def detail_for(ref):
    enc = base64.b64encode(ref.encode()).decode()
    return api(DETAIL.format(urllib.parse.quote(enc)), missing_ok=True)


def collect(a, want_detail):
    first = count(a, size=PAGE_SIZE, page=1)
    total = first.get("maxErgebnisse")
    if total is None:
        die("the API returned no maxErgebnisse. That field is how a count is "
            "checked against the 10 000 ceiling, so the run stops rather "
            "than reporting a number it cannot bound.")
    note(f"{total} ads match — {describe(a)}")
    reachable(total, a, a.limit)
    rows = list(first.get("ergebnisliste") or [])
    want = min(a.limit or total, total, CEILING)
    page = 1
    while len(rows) < want and page < MAX_PAGE:
        page += 1
        d = count(a, size=PAGE_SIZE, page=page)
        got = d.get("ergebnisliste") or []
        if not got:
            note(f"page {page} came back empty, stopping at {len(rows)} "
                 f"of {total}")
            break
        rows.extend(got)
        time.sleep(a.delay)
    rows = rows[:want]
    if want < total:
        note(f"returning {len(rows)} of {total} — capped by "
             f"{'--limit' if a.limit else 'the API ceiling'}. The rest is not "
             "an empty board, it is unread.")
    return rows, total


def emit(rows, a, want_detail):
    kinds = collections.Counter()
    temp = direct = 0
    read = 0
    for x in rows:
        d = None
        if want_detail:
            d = detail_for(x.get("referenznummer") or "")
            if d:
                read += 1
                if d.get("istArbeitnehmerUeberlassung"):
                    temp += 1
                if (d.get("allianzpartnerName") or "") == "arbeitsagentur.de":
                    direct += 1
            time.sleep(a.delay)
        c = card(x, d)
        kinds[c["offer_kind"]] += 1
        print(json.dumps(c, ensure_ascii=False))
    note(f"{len(rows)} ads emitted; kinds: {dict(kinds)}")
    if want_detail:
        note(f"{read} of {len(rows)} details read. {temp} declare "
             "Arbeitnehmerüberlassung — temp-agency work, stated by the "
             "employer because German law requires it, not inferred from a "
             f"name. {direct} were posted to arbeitsagentur.de directly; the "
             "rest arrived through a partner.")
    else:
        note("no descriptions: the ad text is only in the detail endpoint, "
             "one request per ad. Use `read` instead of `search` for it.")


def cmd_count(a):
    d = count(a, size=1)
    total = d.get("maxErgebnisse")
    fits = total is not None and total <= CEILING
    print(json.dumps({
        "query": describe(a),
        "matches": total,
        "reachable": min(total or 0, CEILING),
        "unreachable": max(0, (total or 0) - CEILING),
        "fits_under_ceiling": fits,
    }, ensure_ascii=False))
    if not fits:
        note(f"{total} matches, {CEILING} reachable. Narrow with --seit, "
             "--was or --berufsfeld until this says true.")


def cmd_search(a):
    rows, _ = collect(a, False)
    emit(rows, a, False)


def cmd_read(a):
    rows, _ = collect(a, True)
    emit(rows, a, True)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, h in (("count", cmd_count,
                         "how many match, and whether they are reachable"),
                        ("search", cmd_search, "the listing, no ad text"),
                        ("read", cmd_read,
                         "the listing plus the description, one request "
                         "per ad")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--wo", help="place — Berlin, München, a postcode")
        c.add_argument("--was", help="free text in the job title")
        c.add_argument("--berufsfeld", help="occupational field — Informatik")
        c.add_argument("--arbeitgeber", help="employer name")
        c.add_argument("--seit", type=int, metavar="DAYS",
                       help="published within N days, 0–100. **The filter "
                            "that makes a city fit**: Berlin 45 901 → 8 786 "
                            "at 7 days")
        c.add_argument("--umkreis", type=int, metavar="KM",
                       help="radius around --wo")
        c.add_argument("--limit", type=int,
                       help="take the first N knowingly, up to 10 000")
        c.add_argument("--delay", type=float, default=0.3)
        c.set_defaults(func=fn)
    a = p.parse_args()
    if a.cmd in ("search", "read") and not (
            a.wo or a.was or a.berufsfeld or a.arbeitgeber or a.seit
            or a.limit):
        die("give --wo, --was, --berufsfeld, --arbeitgeber, --seit or "
            "--limit. The board is 994 348 ads and the API will return "
            f"{CEILING} of any query, so an unfiltered sweep is not a sweep.")
    a.func(a)


if __name__ == "__main__":
    main()
