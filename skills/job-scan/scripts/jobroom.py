#!/usr/bin/env python3
"""Fetch job ads from job-room.ch, the Swiss public employment service portal.

job-room.ch is run by SECO. Its search backend is a plain unauthenticated REST
API — no key, no cookie, no browser — and it carries the ads that employers
subject to the Swiss vacancy-reporting duty must publish, plus ads harvested
from other boards.

Usage:
  jobroom.py search --canton VD [--canton GE] [--keywords "infirmier"]
                    [--online-since 7] [--sort date_desc] [--pages 3]
  jobroom.py search --lat 46.5197 --lon 6.6323 --radius 20
  jobroom.py ad <uuid>

Output: one JSON object per line (search), or one JSON object (ad).
"""

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.job-room.ch/jobadservice/api/jobAdvertisements"
AD_URL = "https://www.job-room.ch/job-search/{}"
UA = "Mozilla/5.0 (compatible; claude-job-hunt/1.x; +personal job search)"

# A canton code the API does not know returns 0 ads and no error — as does a
# lowercase one. Both verified on 2026-08-28, hence this list.
CANTONS = {"AG", "AI", "AR", "BE", "BL", "BS", "FR", "GE", "GL", "GR", "JU",
           "LU", "NE", "NW", "OW", "SG", "SH", "SO", "SZ", "TG", "TI", "UR",
           "VD", "VS", "ZG", "ZH"}

MIN_RADIUS_KM = 10  # the API answers 400 below this
MAX_PAGE_SIZE = 100


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def call(url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"User-Agent": UA}
    if data:
        headers["content-type"] = "application/json"
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, data=data, headers=headers), timeout=60)
        return r.headers.get("X-Total-Count"), json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 400:
            die("job-room refused the query (HTTP 400). The API validates its "
                "input, so this is a malformed filter, not an empty result.")
        if e.code == 404:
            die("that ad no longer exists on job-room (HTTP 404) — record it "
                "as discarded, do not retry.", code=3)
        die(f"job-room returned HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach job-room: {e}")


def build_body(a):
    body = {}
    if a.canton:
        bad = [c for c in a.canton if c not in CANTONS]
        if bad:
            die(f"unknown canton code(s): {', '.join(bad)}. Use the official "
                "two-letter uppercase codes (VD, GE, ZH…) — the API returns 0 "
                "ads and no error for anything else, which reads as 'no jobs'.")
        body["cantonCodes"] = a.canton
    if a.lat is not None or a.lon is not None:
        if a.lat is None or a.lon is None:
            die("--lat and --lon go together")
        if a.radius < MIN_RADIUS_KM:
            die(f"--radius must be at least {MIN_RADIUS_KM} (km); the API "
                "answers 400 below that")
        body["radiusSearchRequest"] = {"geoPoint": {"lat": a.lat, "lon": a.lon},
                                       "distance": a.radius}
    if a.keywords:
        body["keywords"] = a.keywords
    if a.company:
        body["companyName"] = a.company
    if a.online_since:
        body["onlineSince"] = a.online_since
    if a.permanent is not None:
        body["permanent"] = a.permanent
    if a.workload_min is not None:
        body["workloadPercentageMin"] = a.workload_min
    if a.workload_max is not None:
        body["workloadPercentageMax"] = a.workload_max
    if not body:
        die("give at least one filter (--canton, --lat/--lon, --keywords…). An "
            "unfiltered sweep is 78,000 ads.")
    return body


def pick_description(descriptions):
    """Return (language, title, description) — longest description wins.

    languageIsoCode is unreliable: a French ad is routinely tagged 'de'. So the
    language is reported, never used to choose.

    **And it is not where truncated titles come from** — measured 2026-09-03
    on the four Infomaniak records that raised the question: **every one of
    them carries exactly one `jobDescriptions` entry**, so this `max()` has
    nothing to choose between. The truncation is in the feed, and `merge()`
    below is where it is repaired. Issue #97.
    """
    if not descriptions:
        return None, None, ""
    best = max(descriptions, key=lambda d: len(d.get("description") or ""))
    return (best.get("languageIsoCode"), best.get("title"),
            best.get("description") or "")


def to_text(markup):
    # <em> marks keyword hits and is glued to the word: "<em>Infirmier</em>-ère".
    # Dropping it with a space would produce "Infirmier -ère", so it goes first.
    txt = re.sub(r"(?i)</?em>", "", markup or "")
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", txt)
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", txt)
    txt = re.sub(r"(?i)<li[^>]*>", "- ", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    # Ads arrive with markdown-style escaping: "Nyon\-La Vallée", "80\%".
    txt = re.sub(r"\\+([-.*_%()\[\]#+])", r"\1", txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", txt).strip()


BOARD_REF = {
    "www.jobup.ch": "jobup",
    "www.jobs.ch": "jobs.ch",
}
UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def clean_url(url):
    """Drop the affiliate tracking query job-room appends to every externalUrl."""
    if not url:
        return None
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, "", ""))


def duplicate_of(url):
    """Ledger id of the same ad on a board this plugin already sweeps.

    A third of job-room's Romandie ads are syndicated from jobup, so the same
    posting is very often already in the ledger under a jobup id.
    """
    if not url:
        return None
    host = urllib.parse.urlparse(url).netloc
    board = BOARD_REF.get(host)
    if not board:
        return None
    m = UUID_RE.search(url)
    return f"{board}:{m.group(0)}" if m else None


def card(ad, with_description=False):
    jc = ad.get("jobContent") or {}
    co = jc.get("company") or {}
    loc = jc.get("location") or {}
    emp = jc.get("employment") or {}
    pub = ad.get("publication") or {}
    lang, title, description = pick_description(jc.get("jobDescriptions"))
    external = jc.get("externalUrl")
    out = {
        "id": ad.get("id"),
        "ledger_id": f"job-room:{ad.get('id')}",
        "url": AD_URL.format(ad.get("id")),
        # A keyword search wraps every match in <em> — strip it, or the title
        # reaches the ledger as "<em>Infirmier</em>-ère à 100%".
        "title": to_text(title) if title else None,
        "company": co.get("name"),
        "company_address": " ".join(x for x in (
            co.get("street"), co.get("houseNumber"), co.get("postalCode"),
            co.get("city")) if x) or None,
        "city": loc.get("city"),
        "postal_code": loc.get("postalCode"),
        "canton": loc.get("cantonCode"),
        "workload": f"{emp.get('workloadPercentageMin')}-"
                    f"{emp.get('workloadPercentageMax')}%",
        "permanent": emp.get("permanent"),
        "start_date": emp.get("startDate"),
        "published": pub.get("startDate"),
        "expires": pub.get("endDate"),
        "language_tag": lang,
        "source_system": ad.get("sourceSystem"),
        "external_url": clean_url(external),
        "external_host": urllib.parse.urlparse(external).netloc if external else None,
        "duplicate_of": duplicate_of(external),
        "avam_number": ad.get("stellennummerAvam"),
        "reporting_obligation": ad.get("reportingObligation"),
    }
    if with_description:
        out["description"] = to_text(description)
    return out


# A title the feed cut mid-phrase leaves its separator behind:
# `'Software Engineer -'`. It is a tell, not a proof.
ORPHAN_TAIL = re.compile(r"[\s]*[-–—:|/]\s*$")

# Names that appear in `company` and are the syndicator, not the employer.
SYNDICATORS = {"jobup", "jobs.ch", "jobcloud"}


def merge(cards):
    """One vacancy, one card — and the title from whichever record has it.

    **THE MEASUREMENT, 2026-09-03.** The same jobup ad reaches job-room twice:
    once through the **employer's own API feed** and once through **Jobup's
    syndication**, both carrying the same `duplicate_of`. They do not carry
    the same title:

        duplicate_of        API feed (employer)          EXTERN (Jobup)
        jobup:478b69aa      'Backend Software Engineer'  '… (Hosting)'
        jobup:4302da20      'Software Engineer PHP'      '… (Médias)'

    **Two of two: the employer's feed drops the parenthesis and the
    syndicated record keeps it.** With `(kDrive)`, `(Hosting)`, `(Médias)`
    and `(Core DevOps)` open at one employer, that is the difference between
    four roles and one string — and the ledger's duplicate check reads the
    title (*"same company and a comparable role"*). It nearly produced a
    second application to a post already applied for.

    **AND THE COMPANY IS WRONG ON THE OTHER RECORD.** The syndicated one names
    `Jobup` — the syndicator — where the API one names the employer. So the
    duplicate check's two halves are broken on **opposite records of the same
    ad**: the one with the usable role has the wrong company, and the one with
    the right company has the amputated role. Merging is what makes either
    half work.

    **A second defect it fixes on the way**: without this, both records enter
    the ledger, under two `job-room:` ids, as two rows for one vacancy.

    Nothing is chosen silently — `title_source` and `company_source` say which
    record each field came from, and `records` says how many were joined.
    """
    by_dup, out = {}, []
    for c in cards:
        key = c.get("duplicate_of")
        if not key:
            out.append(c)          # nothing to join on; emit as it came
            continue
        by_dup.setdefault(key, []).append(c)

    for key, group in by_dup.items():
        if len(group) == 1:
            c = group[0]
            # Unpaired, so nothing corroborates it. Flag rather than repair:
            # there is no second record to take a better value from, and
            # inventing one is the guess this whole file exists to avoid.
            if c.get("title") and ORPHAN_TAIL.search(c["title"]):
                c["title_looks_truncated"] = True
            if (c.get("company") or "").strip().lower() in SYNDICATORS:
                c["company_is_syndicator"] = True
            c["records"] = 1
            out.append(c)
            continue
        # **Longest title wins**, which is the honest form of "the one that was
        # not cut": on both measured pairs the fuller title is also the longer.
        # Two pairs is a small sample and the rule says what it is.
        best_title = max(group, key=lambda c: len(c.get("title") or ""))
        # The employer's name over a syndicator's: prefer the record whose
        # company differs from the external host's brand.
        employer = next(
            (c for c in group
             if (c.get("company") or "").strip().lower()
             not in SYNDICATORS), group[0])
        base = dict(employer)
        base["title"] = best_title.get("title")
        base["title_source"] = best_title.get("source_system")
        base["company_source"] = employer.get("source_system")
        base["records"] = len(group)
        base["merged_ids"] = sorted(c.get("id") for c in group)
        if best_title is not employer:
            base["merged_note"] = (
                f"title from the {best_title.get('source_system')} record and "
                f"company from the {employer.get('source_system')} one — the "
                f"same vacancy reaches job-room twice and neither copy is "
                f"complete.")
        out.append(base)
    return out


def cmd_search(a):
    body = build_body(a)
    size = min(a.size, MAX_PAGE_SIZE)
    rows, total = 0, None
    for page in range(a.page, a.page + a.pages):
        qs = urllib.parse.urlencode({"page": page, "size": size, "sort": a.sort})
        count, ads = call(f"{API}/_search?{qs}", body)
        if total is None:
            total = count
            print(f"[job-room] {total} ads match", file=sys.stderr)
            if total == "0":
                print("[job-room] zero results — check the canton code and the "
                      "keywords before concluding the market is empty",
                      file=sys.stderr)
        if not ads:
            break
        page_cards = [card(x.get("jobAdvertisement") or x) for x in ads]
        merged = merge(page_cards)
        if len(merged) < len(page_cards):
            print(f"[job-room] {len(page_cards)} records → {len(merged)} "
                  f"vacancies: the same ad arrives through the employer's "
                  f"feed and through Jobup's syndication, with different "
                  f"titles and different company names. Merged; see "
                  f"`merged_note`.", file=sys.stderr)
        for c in merged:
            print(json.dumps(c, ensure_ascii=False))
            rows += 1
        if len(ads) < size:
            break
    print(f"[job-room] {rows} cards returned", file=sys.stderr)


def cmd_ad(a):
    _, d = call(f"{API}/{a.uuid}")
    ad = d.get("jobAdvertisement", d)
    print(json.dumps(card(ad, with_description=True), ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="list ads")
    s.add_argument("--canton", action="append", help="official code, repeatable")
    s.add_argument("--lat", type=float)
    s.add_argument("--lon", type=float)
    s.add_argument("--radius", type=int, default=20, help="km, minimum 10")
    s.add_argument("--keywords", action="append")
    s.add_argument("--company")
    s.add_argument("--online-since", type=int, help="days")
    s.add_argument("--permanent", type=lambda v: v.lower() == "true",
                   default=None, help="true|false")
    s.add_argument("--workload-min", type=int)
    s.add_argument("--workload-max", type=int)
    s.add_argument("--sort", default="date_desc", choices=["date_desc", "date_asc"])
    s.add_argument("--page", type=int, default=0)
    s.add_argument("--pages", type=int, default=1)
    s.add_argument("--size", type=int, default=50)
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="read one ad in full")
    d.add_argument("uuid")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
