#!/usr/bin/env python3
"""Fetch Swedish ads from Platsbanken — the richest record in this repository,
behind the tightest window.

**39 865 live ads offering 67 109 posts**, from Arbetsförmedlingen — Sweden's
public employment service — through the JobTech Dev open API. The **sixth
national public employment service** here after `job-room.md` (CH),
`france-travail.md` (FR), `empleate.md` (ES), `arbeitsagentur.md` (DE) and
`jobsireland.md` (IE), and **the first Swedish adapter**.

  GET https://jobsearch.api.jobtechdev.se/search?limit=100&offset=0
  https://arbetsformedlingen.se/platsbanken/annonser/<id>   → the ad, for a human

**No browser, no account, no key, no header.** It is an open-data product of
the Swedish state, published as such; there is nothing to authenticate and
nothing to override.

TWO NUMBERS IN ONE RESPONSE, AND THEY MEAN DIFFERENT THINGS.

    {"total": {"value": 39865}, "positions": 67109, …}

`total` counts **advertisements**, `positions` counts **posts**: 300 ads
measured offered 413 vacancies, one of them ten. Neither is wrong and neither
is "the size of the board" — `empleate.md` had the same split, but there it
took two endpoints to see it and here they sit side by side. Every run prints
both.

THE WINDOW IS 2 100 AND ALMOST NOTHING FITS IN IT.

    limit=100 & offset=2000  →  200
    limit=100 & offset=2001  →  400
    limit=101                →  400

`offset` stops at 2 000 and `limit` at 100, so **one query can reach 2 100 ads
out of 39 865**. That is a fifth of `arbeitsagentur.md`'s ceiling on a board a
twenty-fifth the size.

**Unlike the German API, this one refuses honestly**: HTTP 400 with a
`tracking_id` and a cause, not a silent truncation. It is a better-behaved
endpoint, and the adapter still checks before paging, because a caller who
retries past the ceiling gets an error rather than an answer and the run
should say which of the two it hit.

Measured, and it is unforgiving — even a single occupational field overflows:

    (no filter)                                 39 865   unreachable
    municipality = Stockholm                     6 371   unreachable
    region = Stockholm                          10 452   unreachable
    occupation-field = IT                        2 610   unreachable
    published-after = 12 hours ago               2 399   unreachable
    ────────────────────────────────────────────────────────────────
    Stockholm + published-after 1 day              751   fits
    Stockholm + published-after 3 days             819   fits
    IT + published-after 7 days                    843   fits
    region Stockholm + occupation-field IT       1 137   fits

**The recipe is a place or a field, plus a publication window.** Sweden posts
about 2 400 ads in twelve hours, so `--sedan` is not an optimisation here
either.

Usage:
  platsbanken.py count --kommun 0180
  platsbanken.py search --kommun 0180 --sedan 2026-08-31
  platsbanken.py search --q utvecklare

Output: one JSON object per line.
"""

import argparse
import collections
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://jobsearch.api.jobtechdev.se/search"
AD_URL = "https://arbetsformedlingen.se/platsbanken/annonser/{}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# Both measured against the live API: 2001 and 101 each answer 400.
MAX_LIMIT = 100
MAX_OFFSET = 2000
CEILING = MAX_OFFSET + MAX_LIMIT

WS_RE = re.compile(r"\s+")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[platsbanken] {msg}", file=sys.stderr)


def api(**params):
    params = {k: v for k, v in params.items() if v not in (None, "")}
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")[:300]
            if exc.code == 400:
                die(f"HTTP 400 from the API.\n  {url}\n  {body}\n"
                    f"offset stops at {MAX_OFFSET} and limit at {MAX_LIMIT} — "
                    "this endpoint refuses rather than truncating, so a 400 "
                    "here usually means the ceiling, not a bad parameter.")
            if attempt == 2:
                die(f"{url}: HTTP {exc.code}\n  {body}")
            time.sleep(1.5 * (attempt + 1))
        except (urllib.error.URLError, OSError) as exc:
            if attempt == 2:
                die(f"{url}: {exc}")
            time.sleep(1.5 * (attempt + 1))
    return {}


def params_of(a, limit, offset):
    return dict(limit=limit, offset=offset, q=a.q,
                municipality=a.kommun, region=a.region,
                **{"occupation-field": a.omrade,
                   "published-after": a.sedan})


def describe(a):
    bits = []
    for k, v in (("q", a.q), ("kommun", a.kommun), ("region", a.region),
                 ("occupation-field", a.omrade), ("published-after", a.sedan)):
        if v:
            bits.append(f"{k}={v}")
    return " ".join(bits) or "(no filter — the whole board)"


def reachable(total, a, wanted):
    """Refuse a query the window cannot deliver, before paging into a 400."""
    if total <= CEILING or (wanted and wanted <= CEILING):
        return
    die(f"this query matches {total} ads and the API window is {CEILING} "
        f"(offset <= {MAX_OFFSET}, limit <= {MAX_LIMIT}) — "
        f"{total - CEILING} are unreachable, and no parameter widens it.\n"
        f"  query: {describe(a)}\n"
        "Narrow it until it fits. What works, measured:\n"
        "  --kommun 0180 --sedan <yesterday>      Stockholm 6 371 -> 751\n"
        "  --omrade <field> --sedan <a week ago>  IT 2 610 -> 843\n"
        "  --region 01 --omrade <field>           1 137\n"
        "A place or a field ALONE overflows; it takes two.\n"
        f"Or pass --limit N with N <= {CEILING} to take the first N knowingly.")


def text_of(s):
    return WS_RE.sub(" ", s).strip() if isinstance(s, str) else None


def label(x):
    return (x or {}).get("label") if isinstance(x, dict) else None


def concepts(items):
    """The taxonomy entries, as plain labels with their weight."""
    out = []
    for c in items or []:
        if isinstance(c, dict) and c.get("label"):
            out.append({"label": c["label"], "weight": c.get("weight")})
    return out or None


def card(x):
    ident = x.get("id")
    emp = x.get("employer") or {}
    ad = x.get("workplace_address") or {}
    coords = ad.get("coordinates") or [None, None]
    lon, lat = (coords + [None, None])[:2]
    must = x.get("must_have") or {}
    nice = x.get("nice_to_have") or {}
    desc = x.get("description") or {}
    return {
        "id": ident,
        "ledger_id": f"platsbanken:{ident}",
        "url": x.get("webpage_url") or AD_URL.format(ident),
        "title": x.get("headline"),
        "company": emp.get("name"),
        "workplace": emp.get("workplace"),
        # The Swedish company registration number, on 293 of 300. No other
        # board here gives a legal identifier — it is a dedup key that
        # survives a rename and crosses to any other Swedish source.
        "company_registration_number": emp.get("organization_number"),
        "company_website": emp.get("url"),
        "street": ad.get("street_address"),
        "postcode": ad.get("postcode"),
        "city": ad.get("city"),
        "municipality": ad.get("municipality"),
        "municipality_code": ad.get("municipality_code"),
        "region": ad.get("region"),
        "country": ad.get("country"),
        "latitude": lat,
        "longitude": lon,
        "occupation": label(x.get("occupation")),
        "occupation_group": label(x.get("occupation_group")),
        "occupation_field": label(x.get("occupation_field")),
        "employment_type": label(x.get("employment_type")),
        "duration": label(x.get("duration")),
        "working_hours_type": label(x.get("working_hours_type")),
        "scope_of_work": x.get("scope_of_work"),
        # "Arbete på plats" on 300 of 300 measured — this field did not
        # distinguish anything in the sample. Carried, not relied on.
        "workplace_model": label(x.get("workplace_model")),
        # **The type of pay, never the amount.** salary_type is filled on
        # 300 of 300 and salary_description on 0 of 300. A presence check on
        # the first reports total salary coverage of nothing.
        "salary_type": label(x.get("salary_type")),
        "salary_description": x.get("salary_description") or None,
        "salary_amount_stated": bool(x.get("salary_description")),
        "positions": x.get("number_of_vacancies"),
        "experience_required": x.get("experience_required"),
        "driving_licence_required": x.get("driving_license_required"),
        "published": x.get("publication_date"),
        "last_publication": x.get("last_publication_date"),
        # On 300 of 300 — every ad states when applications close.
        "application_deadline": x.get("application_deadline"),
        "source_type": x.get("source_type"),
        "removed": bool(x.get("removed")),
        # A structured requirement schema no other board here has — and one
        # that is mostly empty: skills on 5 of 300, languages on 43,
        # work_experiences on 33, education on 10. A rich schema is not rich
        # data, so the counts are emitted rather than the shape.
        "must_have_skills": concepts(must.get("skills")),
        "must_have_languages": concepts(must.get("languages")),
        "must_have_experience": concepts(must.get("work_experiences")),
        "must_have_education": concepts(must.get("education")),
        "nice_to_have_skills": concepts(nice.get("skills")),
        "nice_to_have_languages": concepts(nice.get("languages")),
        "nice_to_have_experience": concepts(nice.get("work_experiences")),
        "description": text_of(desc.get("text")),
    }


def collect(a):
    first = api(**params_of(a, MAX_LIMIT, 0))
    total = (first.get("total") or {}).get("value")
    positions = first.get("positions")
    if total is None:
        die("the API returned no total.value. That field is how a count is "
            "checked against the window, so the run stops rather than "
            "reporting a number it cannot bound.")
    note(f"{total} ads offering {positions} posts match — {describe(a)}")
    reachable(total, a, a.limit)
    rows = list(first.get("hits") or [])
    want = min(a.limit or total, total, CEILING)
    offset = 0
    while len(rows) < want and offset + MAX_LIMIT <= MAX_OFFSET:
        offset += MAX_LIMIT
        got = api(**params_of(a, MAX_LIMIT, offset)).get("hits") or []
        if not got:
            note(f"offset {offset} came back empty, stopping at {len(rows)} "
                 f"of {total}")
            break
        rows.extend(got)
        time.sleep(a.delay)
    rows = rows[:want]
    if want < total:
        note(f"returning {len(rows)} of {total} — capped by "
             f"{'--limit' if a.limit else 'the API window'}. The rest is not "
             "an empty board, it is unread.")
    return rows, total, positions


def cmd_count(a):
    d = api(**params_of(a, 0, 0))
    total = (d.get("total") or {}).get("value")
    print(json.dumps({
        "query": describe(a),
        "ads": total,
        "positions": d.get("positions"),
        "reachable": min(total or 0, CEILING),
        "unreachable": max(0, (total or 0) - CEILING),
        "fits_in_window": total is not None and total <= CEILING,
    }, ensure_ascii=False))
    if total and total > CEILING:
        note(f"{total} match and the window is {CEILING}. A place or a field "
             "alone overflows — add --sedan.")


def cmd_search(a):
    rows, total, positions = collect(a)
    salaried = deadline = withreq = 0
    fields = collections.Counter()
    for x in rows:
        c = card(x)
        if c["salary_amount_stated"]:
            salaried += 1
        if c["application_deadline"]:
            deadline += 1
        if any(c[k] for k in ("must_have_skills", "must_have_languages",
                              "must_have_experience", "must_have_education")):
            withreq += 1
        fields[c["occupation_field"]] += 1
        print(json.dumps(c, ensure_ascii=False))
    n = len(rows)
    note(f"{n} ads emitted, offering {sum(x.get('number_of_vacancies') or 0 for x in rows)} posts")
    note(f"salary: {salaried} of {n} state an AMOUNT. Every ad states a "
         "salary TYPE, which is not the same thing — a presence check on "
         "salary_type reports full coverage of nothing.")
    note(f"application deadline on {deadline} of {n}; structured requirements "
         f"on {withreq} of {n} — the schema is far richer than the data.")
    note("top fields: " + ", ".join(f"{k} {v}" for k, v in fields.most_common(4)))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, h in (("count", cmd_count,
                         "how many match, and whether the window can reach "
                         "them"),
                        ("search", cmd_search, "read the ads")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--q", help="free text")
        c.add_argument("--kommun", metavar="CODE",
                       help="municipality code — 0180 is Stockholm")
        c.add_argument("--region", metavar="CODE",
                       help="region code — 01 is Stockholms län")
        c.add_argument("--omrade", metavar="CONCEPT_ID",
                       dest="omrade",
                       help="occupation-field concept id")
        c.add_argument("--sedan", metavar="ISO8601",
                       help="published after — '2026-08-31T00:00:00'. **The "
                            "filter that makes a place fit**")
        c.add_argument("--limit", type=int,
                       help=f"take the first N knowingly, up to {CEILING}")
        if name == "search":
            c.add_argument("--delay", type=float, default=0.3)
        c.set_defaults(func=fn)
    a = p.parse_args()
    if a.cmd == "search" and not (a.q or a.kommun or a.region or a.omrade
                                  or a.sedan or a.limit):
        die("give --q, --kommun, --region, --omrade, --sedan or --limit. The "
            f"board is 39 865 ads and one query reaches {CEILING}, so an "
            "unfiltered sweep is not a sweep.")
    a.func(a)


if __name__ == "__main__":
    main()
