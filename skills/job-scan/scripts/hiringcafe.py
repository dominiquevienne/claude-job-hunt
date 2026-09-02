#!/usr/bin/env python3
"""Fetch job cards and ad text from hiringcafe.com.

HiringCafe is a meta-board: it crawls employer career pages across ~40 ATS
platforms. Every card names the employer and links to that employer's own ATS,
so results are NOT aggregator reposts — see shared/boards/hiringcafe.md.

The site's own /api/search-jobs endpoint returns 401. This script reads the
server-rendered payload embedded in the page instead (__NEXT_DATA__), which
needs no key, no cookie and no browser.

Usage:
  hiringcafe.py search --country CH [--query "..."] [--posted-within week]
                       [--remote] [--sort date] [--pages 3]
  hiringcafe.py search --city Lausanne --admin1 Vaud --country CH \\
                       --lat 46.5197 --lon 6.6323 [--radius 25]
  hiringcafe.py ad <requisition_id>

Output: one JSON object per line (search), or one JSON object (ad).
Every failure is loud: a search that cannot be built exits non-zero rather
than returning an unfiltered or empty result set that looks like an answer.
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

from _locations import drop_report, matches_city

BASE = "https://hiringcafe.com/"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0 Safari/537.36"
)

# dateFetchedPastNDays is an ENUM, not a number of days. An unlisted value is
# silently accepted and WIDENS the result set. Verified live on 2026-08-27.
POSTED_WITHIN = {
    "all": -1,
    "day": 2,
    "3days": 4,
    "week": 14,
    "2weeks": 21,
    "3weeks": 29,
    "month": 61,
    "2months": 91,
    "quarter": 121,  # the site's own default
}

SORTS = {"relevance": "default", "date": "date", "date_asc": "date_asc",
         "salary": "compensation_desc"}


class _Redirect308(urllib.request.HTTPRedirectHandler):
    """Follow 308, which older urllib versions surface as an error.

    /job/<requisition_id> answers 308 towards the canonical slug URL, so an
    opener that does not follow it cannot read a single ad.
    """

    def http_error_308(self, req, fp, code, msg, headers):
        return self.http_error_307(req, fp, 307, msg, headers)


OPENER = urllib.request.build_opener(_Redirect308)


# Exit codes, because "the sweep was throttled" and "the adapter is broken"
# must not look the same to the caller.
EXIT_BROKEN = 2      # the shape changed, the ad is gone, the search is invalid
EXIT_THROTTLED = 6   # the site refused us; whatever came back is a partial pass


class Throttled(Exception):
    """A 403/429/5xx that survived the backoff. Transient, not broken."""


def get(url, attempts=4, first_wait=20.0):
    """Fetch with a timed backoff.

    hiring.cafe answers 403 intermittently and the refusal rate rises with the
    number of pages asked for: measured 2026-09-02, `--pages 6` failed 8 times
    out of 8, while one page at a time with 25 s between requests returned 6
    pages of 6. **So the remedy is waiting, not retrying quickly** — the waits
    are 20 s, 40 s, 80 s rather than the usual second or two.
    """
    wait = first_wait
    for attempt in range(1, attempts + 1):
        try:
            return OPENER.open(
                urllib.request.Request(url, headers={"User-Agent": UA}),
                timeout=60).read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code not in (403, 429) and e.code < 500:
                raise
            if attempt == attempts:
                raise Throttled(f"HTTP {e.code} after {attempts} attempts")
            print(f"[hiringcafe] HTTP {e.code} — waiting {wait:.0f}s "
                  f"(attempt {attempt} of {attempts}). This site throttles by "
                  f"pages requested; waiting works where retrying does not.",
                  file=sys.stderr)
            time.sleep(wait)
            wait *= 2
        except urllib.error.URLError as e:
            if attempt == attempts:
                raise Throttled(f"{e}")
            time.sleep(wait)
            wait *= 2
    raise Throttled("unreachable")


def fetch_page_props(params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    try:
        raw = get(url)
    except Throttled:
        raise
    except urllib.error.HTTPError as e:
        die(f"hiringcafe returned HTTP {e.code} for a search request")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach hiringcafe: {e}")
    m = re.search(r'id="__NEXT_DATA__"[^>]*>(.*?)</script>', raw, re.S)
    if not m:
        die("no __NEXT_DATA__ in the page — the site's rendering changed. "
            "Report it with /board-request (broken-adapter mode).")
    try:
        return json.loads(m.group(1))["props"]["pageProps"]
    except (ValueError, KeyError) as e:
        die(f"__NEXT_DATA__ did not have the expected shape: {e}")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def build_location(a):
    """Build the one location object the site accepts.

    Country search keys off address_components[].short_name ONLY.
    City search additionally REQUIRES an administrative_area_level_1 component
    and real coordinates: without either, the site returns 0 results and no
    error. Both verified live on 2026-08-27.
    """
    if a.city:
        missing = [k for k, v in (("--admin1", a.admin1), ("--country", a.country),
                                  ("--lat", a.lat), ("--lon", a.lon)) if v in (None, "")]
        if missing:
            die("a city search needs " + ", ".join(missing) + ". Without the region "
                "and coordinates hiringcafe returns 0 results and no error, which "
                "reads as 'no jobs'. Use --country alone for a country-wide sweep.")
        return {
            "formatted_address": f"{a.city}, {a.country}",
            "types": ["locality"],
            "geometry": {"location": {"lat": a.lat, "lon": a.lon}},
            "id": f"{a.city.lower()}-{a.country.lower()}",
            "address_components": [
                {"long_name": a.city, "short_name": a.city, "types": ["locality"]},
                {"long_name": a.admin1, "short_name": a.admin1,
                 "types": ["administrative_area_level_1"]},
                {"long_name": a.country, "short_name": a.country.upper(),
                 "types": ["country"]},
            ],
            "options": {"radius": a.radius, "radius_unit": a.radius_unit,
                        "ignore_radius": False},
        }
    if not a.country:
        die("give --country (ISO-2, e.g. CH) or a full --city/--admin1/--lat/--lon")
    if not re.fullmatch(r"[A-Za-z]{2}", a.country):
        die(f"--country must be an ISO-2 code, got {a.country!r}. A code the site "
            "does not know returns a small unrelated result set, not an error.")
    return {
        "formatted_address": a.country.upper(),
        "types": ["country"],
        "geometry": {"location": {"lat": 0, "lon": 0}},  # ignored for a country
        "id": "user_country",
        "address_components": [{"long_name": a.country.upper(),
                                "short_name": a.country.upper(),
                                "types": ["country"]}],
        "options": {"flexible_regions": ["anywhere_in_continent", "anywhere_in_world"]},
    }


def build_state(a):
    state = {"locations": [build_location(a)]}
    if a.query:
        state["searchQuery"] = a.query
    if a.posted_within and a.posted_within != "quarter":
        state["dateFetchedPastNDays"] = POSTED_WITHIN[a.posted_within]
    if a.remote:
        state["workplaceTypes"] = ["Remote"]
    if a.sort and a.sort != "relevance":
        state["sortBy"] = SORTS[a.sort]
    return state


def card(hit):
    job = hit.get("job_information") or {}
    v5 = hit.get("v5_processed_job_data") or {}
    org = hit.get("attributed_org") or {}
    enriched = hit.get("enriched_company_data") or {}
    req = hit.get("requisition_id")
    return {
        "id": req,
        "ledger_id": f"hiringcafe:{req}",
        "url": f"https://hiringcafe.com/job/{req}",
        "title": job.get("title"),
        "company": org.get("name") or enriched.get("name"),
        "company_attribution": org.get("method"),  # 'llm_pick' = a guess, not a fact
        "cities": v5.get("workplace_cities") or [],
        "countries": v5.get("workplace_countries") or [],
        "workplace_type": v5.get("workplace_type"),
        "commitment": v5.get("commitment") or [],
        "seniority": v5.get("seniority_level"),
        "published_estimate": v5.get("estimated_publish_date"),
        "ats": hit.get("source"),
        "ats_tenant": hit.get("board_token"),
        "apply_url": hit.get("apply_url"),
        "collapse_key": hit.get("collapse_key"),
    }


def cmd_search(a):
    state = build_state(a)
    seen, rows, total = set(), 0, None
    asked = a.pages
    got = 0
    throttled = None
    dropped, dropped_labels = 0, {}
    for page in range(a.page, a.page + a.pages):
        if page > a.page and a.delay:
            # One page at a time, spaced. This is the measured remedy: the
            # refusal rate tracks how many pages a run asks for.
            time.sleep(a.delay)
        params = {"searchState": json.dumps(state, separators=(",", ":"))}
        if page:
            params["page"] = page
        try:
            pp = fetch_page_props(params)
        except Throttled as exc:
            throttled = exc
            break
        got += 1
        if total is None:
            total = pp.get("ssrTotalCount")
            print(f"[hiringcafe] {total} ads, {pp.get('ssrCompanyCount')} companies",
                  file=sys.stderr)
            if not total:
                print("[hiringcafe] zero results — check the location and the "
                      "keywords before concluding the market is empty",
                      file=sys.stderr)
        page_rows = []
        for hit in pp.get("ssrHits") or []:
            if hit.get("is_expired"):
                continue
            key = hit.get("collapse_key") or hit.get("requisition_id")
            if key in seen:      # the same posting duplicated on the employer's ATS
                continue
            seen.add(key)
            page_rows.append(card(hit))
        if a.city_filter:
            # This board writes one city several ways in the same result set —
            # "Hanoi, Hanoi", "Hanoi, Ha Noi" and "Hanoi, Hà Nội" are 24 cards
            # for one place. Comparing whole strings loses a fifth to a third
            # of a capital, silently. `_locations` folds diacritics and
            # compares the first segment; see issue #65.
            page_rows, dropped_n, labels = drop_report(
                page_rows, a.city_filter,
                location_of=lambda r: (r.get("cities") or [None])[0])
            dropped += dropped_n
            for label, n in labels.items():
                dropped_labels[label] = dropped_labels.get(label, 0) + n
        for row in page_rows:
            print(json.dumps(row, ensure_ascii=False))
            rows += 1
        if pp.get("ssrIsLastPage"):
            break
    if throttled:
        # `shared/never-fail-silently.md` in both directions: a truncated
        # sweep must not exit 0, and it must not look like a broken adapter
        # either. Whatever came back is real and is already on stdout.
        print(f"[hiringcafe] THE SWEEP IS PARTIAL: {got} of {asked} page(s) "
              f"read before the site refused ({throttled}). {rows} unique "
              f"cards were returned and they are good; the rest were never "
              f"fetched. Re-run later, or with --pages 1 and a larger "
              f"--delay. Do not report this as a complete pass.",
              file=sys.stderr)
        if got == 0:
            die("hiringcafe refused every attempt. Nothing was read — this is "
                "a throttle, not a breakage, so try again in a few minutes "
                "rather than reporting the board broken.", EXIT_THROTTLED)
        sys.exit(EXIT_THROTTLED)
    print(f"[hiringcafe] {rows} unique cards returned over {got} page(s) "
          f"of {asked} asked", file=sys.stderr)
    if a.city_filter:
        print(f"[hiringcafe] --city-filter {a.city_filter!r} kept {rows} "
              f"and dropped {dropped}. Dropped labels: "
              + (", ".join(f"{k!r} ×{v}" for k, v in
                           sorted(dropped_labels.items(),
                                  key=lambda kv: -kv[1])[:8]) or "none")
              + ". A city filter that drops rows says how many, so the loss "
                "is visible rather than silent.", file=sys.stderr)


def to_text(markup):
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", markup or "")
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", txt)
    txt = re.sub(r"(?i)<li[^>]*>", "- ", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", txt).strip()


def cmd_ad(a):
    try:
        raw = get(f"https://hiringcafe.com/job/{a.requisition_id}")
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            die(f"ad {a.requisition_id} is gone (HTTP {e.code}) — it expired or was "
                "pulled. Record it as discarded, do not retry.", code=3)
        die(f"hiringcafe returned HTTP {e.code} for that ad")
    except Exception as e:  # noqa: BLE001
        die(f"could not reach hiringcafe: {e}")
    m = re.search(r'id="__NEXT_DATA__"[^>]*>(.*?)</script>', raw, re.S)
    if not m:
        die("no __NEXT_DATA__ on the ad page — report with /board-request")
    job = (json.loads(m.group(1))["props"]["pageProps"] or {}).get("job")
    if not job:
        die(f"no job payload for {a.requisition_id}")
    out = card(job)
    out["description"] = to_text((job.get("job_information") or {}).get("description"))
    print(json.dumps(out, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="list job cards")
    s.add_argument("--country", help="ISO-2 country code, e.g. CH")
    s.add_argument("--city")
    s.add_argument("--admin1", help="region/canton/state — REQUIRED with --city")
    s.add_argument("--lat", type=float)
    s.add_argument("--lon", type=float)
    s.add_argument("--radius", type=int, default=25)
    s.add_argument("--radius-unit", default="miles", choices=["miles", "kilometers"])
    s.add_argument("--query", help="keywords; quote them to match strictly")
    s.add_argument("--posted-within", default="quarter", choices=sorted(POSTED_WITHIN))
    s.add_argument("--remote", action="store_true")
    s.add_argument("--sort", default="relevance", choices=sorted(SORTS))
    s.add_argument("--page", type=int, default=0)
    s.add_argument("--pages", type=int, default=1)
    s.add_argument("--city-filter", dest="city_filter",
                   help="keep only cards whose first city segment matches "
                        "this, diacritics folded. Different from --city, "
                        "which asks the SITE to search a place: this checks "
                        "what came back, because the site labels one city "
                        "several ways. See issue #65")
    s.add_argument("--delay", type=float, default=25.0,
                   help="seconds between pages. The default is high on "
                        "purpose: 25 s apart returned 6 pages of 6 where a "
                        "burst of 6 failed 8 times out of 8")
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="read one ad in full")
    d.add_argument("requisition_id")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
