#!/usr/bin/env python3
"""Read swissdevjobs.ch — Swiss tech roles, with a salary on almost every ad.

A real multi-employer board, unlike the per-tenant ATS family in `ats.py`: one
request returns every live vacancy, and the employer is named on each.

    GET https://swissdevjobs.ch/api/jobsLight

No key, no cookie, no browser, no paging. `robots.txt` disallows `/api/` for
`Meta-ExternalAgent` by name and for nobody else.

Two fields make this board worth more than its size:

  * a salary range on 169 of 170 ads — an employer's own figure, tier (A), where
    most boards publish none at all;
  * latitude and longitude on 170 of 170 — so `--near` filters by real distance
    instead of guessing a commute from a place name.

Usage:
  swissdevjobs.py list [--search laravel] [--tech PHP] [--city Zurich]
                       [--remote] [--posted-within-days 30] [--salary-min 120000]
                       [--seniority Senior] [--near 46.52,6.63 --radius-km 60]
                       [--with-description]
  swissdevjobs.py ad    --slug <jobUrl slug>
  swissdevjobs.py check --slug <jobUrl slug>
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")
API = "https://swissdevjobs.ch/api/jobsLight"
SITE = "https://swissdevjobs.ch"


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def get_json(url):
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={
                "User-Agent": UA, "Accept": "application/json"}), timeout=60)
        return json.load(r)
    except urllib.error.HTTPError as e:
        die(f"{url} returned HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach {urllib.parse.urlparse(url).netloc}: {e}")


def head_status(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        return urllib.request.urlopen(req, timeout=30).status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:  # noqa: BLE001
        return None


def fold(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def haversine(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def fetch_board():
    d = get_json(API)
    if not isinstance(d, list):
        die("swissdevjobs returned something that is not the job list — the "
            "endpoint shape changed. Do not fall back to /api/jobs: it is "
            "deprecated and answers a plain-text notice with HTTP 200.")
    return d


def row(j, distance_km=None, with_description=False):
    slug = j.get("jobUrl")
    city = j.get("actualCity")
    npa = j.get("postalCode")
    out = {
        "id": j.get("_id"),
        "ledger_id": f"swissdevjobs:{j.get('_id')}",
        "url": f"{SITE}/jobs/{slug}" if slug else None,
        "apply_url": f"{SITE}/jobs/{slug}" if slug else None,
        "title": j.get("name"),
        "company": j.get("company"),
        "location": " ".join(x for x in (npa, city) if x) or None,
        # Street, postcode and town, straight from the employer. The job-room-ch
        # module records these as the fields most often missing from a PRE.
        "address": {k: v for k, v in (("street", j.get("address")),
                                      ("postal_code", npa),
                                      ("locality", city)) if v} or None,
        "published": j.get("activeFrom"),
        # An employer's own figure — tier (A) in shared/salary-estimate.md, not
        # an estimate. Present on all but one ad of the board.
        "salary_from": j.get("annualSalaryFrom"),
        "salary_to": j.get("annualSalaryTo"),
        "salary_currency": "CHF" if j.get("annualSalaryFrom") else None,
        "day_rate_from": j.get("contractRateFrom"),
        "day_rate_to": j.get("contractRateTo"),
        "technologies": j.get("technologies") or [],
        "seniority": j.get("expLevel"),
        "job_type": j.get("jobType"),
        "workplace": j.get("workplace"),
        "remote": j.get("workplace") == "remote",
        "latitude": j.get("latitude"),
        "longitude": j.get("longitude"),
        # "Yes"/"No" strings, NOT booleans — and "Yes" is rare (2 of 170
        # measured). Reading the key's presence as a yes overstates it by two
        # orders of magnitude.
        "visa_sponsorship": j.get("hasVisaSponsorship"),
        "company_size": j.get("companySize"),
        "company_type": j.get("companyType"),
    }
    if distance_km is not None:
        out["distance_km"] = round(distance_km, 1)
    if with_description:
        # jobsLight carries no description — the name says so. The ad page is
        # client-rendered, so there is no no-browser route to the body text.
        out["description"] = None
        out["description_note"] = (
            "not available: /api/jobsLight carries no body text and the ad page "
            "is client-rendered. Open the url in a browser, or paste the text "
            "into cover-letter.")
    return out


def keep(j, a):
    if a.search:
        hay = fold(f"{j.get('name')} {j.get('company')} {j.get('techCategory')}")
        if fold(a.search) not in hay:
            return False
    if a.tech:
        techs = [fold(t) for t in (j.get("technologies") or [])]
        if not any(fold(t) in techs for t in a.tech):
            return False
    if a.city and fold(a.city) not in fold(j.get("actualCity")):
        return False
    if a.remote and j.get("workplace") != "remote":
        return False
    if a.seniority and fold(a.seniority) != fold(j.get("expLevel")):
        return False
    if a.salary_min:
        top = j.get("annualSalaryTo") or j.get("annualSalaryFrom")
        if not top or top < a.salary_min:
            return False
    if a.posted_within_days:
        raw = (j.get("activeFrom") or "")[:10]
        try:
            age = (dt.date.today() - dt.date.fromisoformat(raw)).days
        except ValueError:
            return False
        if age > a.posted_within_days:
            return False
    return True


def cmd_list(a):
    board = fetch_board()
    origin = None
    if a.near:
        try:
            lat, lon = (float(x) for x in a.near.split(","))
        except ValueError:
            die("--near wants 'lat,lon', e.g. --near 46.52,6.63")
        origin = (lat, lon)

    kept = []
    for j in board:
        if j.get("isPaused"):
            continue
        if not keep(j, a):
            continue
        dist = None
        if origin:
            if j.get("latitude") is None or j.get("longitude") is None:
                continue
            dist = haversine(origin[0], origin[1], j["latitude"], j["longitude"])
            if a.radius_km and dist > a.radius_km:
                continue
        kept.append((dist, j))

    if origin:
        kept.sort(key=lambda p: p[0])

    print(f"[swissdevjobs] {len(kept)} of {len(board)} postings kept",
          file=sys.stderr)
    if origin and a.radius_km:
        print(f"  within {a.radius_km} km of {a.near} — straight-line distance, "
              "not travel time", file=sys.stderr)
    for dist, j in kept:
        print(json.dumps(row(j, dist, a.with_description), ensure_ascii=False))

    # This board is German-speaking Switzerland. Saying so on every run beats
    # letting an empty result read as "nothing is hiring".
    if not kept:
        print("  note: swissdevjobs is overwhelmingly Zurich/Bern/Basel — on a "
              "measured full board, 2 of 170 ads were in Suisse romande and 4 "
              "were remote. An empty result here is usually the board, not the "
              "market.", file=sys.stderr)
    return 0


def find_by_slug(board, slug):
    want = fold(slug)
    return next((j for j in board if fold(j.get("jobUrl")) == want), None)


def cmd_ad(a):
    j = find_by_slug(fetch_board(), a.slug)
    if j is None:
        die(f"no live posting with slug {a.slug!r} — it was filled or pulled. "
            "Record it as discarded.", code=3)
    print(json.dumps(row(j, None, with_description=True),
                     ensure_ascii=False, indent=1))
    return 0


def cmd_check(a):
    j = find_by_slug(fetch_board(), a.slug)
    if j is not None and not j.get("isPaused"):
        verdict, why = "open", "listed in /api/jobsLight"
    elif j is not None:
        verdict, why = "paused", "listed but flagged isPaused"
    else:
        # The listing is the authority; the page is a second opinion that
        # happens to be usable here because a wrong slug really does 404
        # instead of returning the SPA shell.
        code = head_status(f"{SITE}/jobs/{a.slug}")
        verdict = "closed" if code == 404 else "unknown"
        why = (f"absent from /api/jobsLight and the ad page returned {code}"
               if code == 404 else
               f"absent from /api/jobsLight but the ad page returned {code} — "
               "not conclusive, check by hand")
    print(json.dumps({"slug": a.slug, "verdict": verdict, "why": why,
                      "url": f"{SITE}/jobs/{a.slug}"}, ensure_ascii=False))
    return 0 if verdict in ("open", "paused") else 3


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="the whole board, filtered locally")
    li.add_argument("--search", help="matched on title, company and category")
    li.add_argument("--tech", action="append",
                    help="technology tag, repeatable (e.g. --tech PHP --tech Laravel)")
    li.add_argument("--city")
    li.add_argument("--remote", action="store_true")
    li.add_argument("--seniority", help="Junior | Regular | Senior | Lead")
    li.add_argument("--salary-min", type=int,
                    help="keep ads whose top of range reaches this (CHF/year)")
    li.add_argument("--posted-within-days", type=int)
    li.add_argument("--near", help="'lat,lon' to sort and filter by distance")
    li.add_argument("--radius-km", type=float)
    li.add_argument("--with-description", action="store_true",
                    help="adds an explicit note that no body text exists here")

    ad = sub.add_parser("ad", help="one posting in full")
    ad.add_argument("--slug", required=True)

    ck = sub.add_parser("check", help="is this posting still live?")
    ck.add_argument("--slug", required=True)

    a = p.parse_args()
    return {"list": cmd_list, "ad": cmd_ad, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
