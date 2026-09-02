#!/usr/bin/env python3
"""Fetch job ads from a DigitalRecruiters careers site — the French retail ATS.

DigitalRecruiters (a Cegid company since 2022) runs white-label careers sites
for **multisite, multibrand** French employers — retail, franchise networks,
large service groups. That is why it is hard to find and worth having: the
careers site lives on the employer's own domain, so nothing about it says
"DigitalRecruiters" from outside.

The tenant key is therefore **the careers hostname itself**, not a slug:

  POST https://api.digitalrecruiters.com/public/v1/careers-site/job-ads
       ?domainName=<host>&locale=fr_FR&limit=1000&page=1
  → {"count": 948, "items": [...], "filters": {...}}   in ONE request

  GET  https://<host>/fr/annonce/<url>                 one ad, with JSON-LD

**It is a POST.** The same path answers `403` to a GET, which reads as "no
access" rather than "wrong method" — see `call`.

Usage:
  digitalrecruiters.py jobs --domain recrutement.monoprix.fr
  digitalrecruiters.py jobs --domain recrutement.monoprix.fr --with-detail
  digitalrecruiters.py filters --domain recrutement.monoprix.fr

Output: one JSON object per line (jobs), or one JSON object (filters).
"""

import argparse
import gzip
import html as html_mod
import json
import re

from _ldjson import postings
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = ("https://api.digitalrecruiters.com/public/v1/careers-site/job-ads")
SITE = "https://api.digitalrecruiters.com/careers/v1/careers-sites/{}"
AD_URL = "https://{}/{}/annonce/{}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

DOMAIN_RE = re.compile(r"^[a-z0-9.-]+\.[a-z]{2,}$", re.I)
HOST_RE = re.compile(r"https?://([a-z0-9.-]+)", re.I)

# `limit` has no observed ceiling — 1000 returned all 948 ads of the largest
# tenant sampled. But that single call also timed out at 60s on a later run,
# so the sweep pages instead: same total, no request big enough to hang.
PAGE_SIZE = 200
TIMEOUT = 120

# The careers hosts publish `Crawl-delay: 10`. The API host publishes no
# robots.txt at all, and the listing is one request anyway — but every ad read
# hits the careers host, so that is the pace this honours.
CRAWL_DELAY = 10.0


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def _read(r):
    body = r.read()
    if r.headers.get("Content-Encoding", "").lower() == "gzip":
        body = gzip.decompress(body)
    return body.decode("utf-8", errors="replace")


def call(url, post=False):
    data = b"{}" if post else None
    headers = {
        "User-Agent": UA,
        "Accept": "application/json" if post else "text/html",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Accept-Encoding": "gzip",
    }
    if post:
        headers["Content-Type"] = "application/json"
    try:
        with urllib.request.urlopen(
                urllib.request.Request(url, data=data, headers=headers),
                timeout=TIMEOUT) as r:
            raw = _read(r)
            return json.loads(raw) if post else raw
    except urllib.error.HTTPError as e:
        if e.code == 403:
            die("HTTP 403. On this API that usually means the **method** is "
                "wrong, not that access is denied: the job-ads route is a "
                "POST, and a GET to it answers 403. Check the verb before "
                "concluding anything about permissions.")
        if e.code == 404:
            die("HTTP 404. Check the careers domain — it is the hostname of "
                "the employer's careers site, and there is no directory to "
                "look one up in.", code=3)
        die(f"DigitalRecruiters returned HTTP {e.code}")
    except json.JSONDecodeError:
        die("that endpoint did not return JSON.")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach DigitalRecruiters: {e}")


def domain_of(a):
    if not a.domain:
        die("give --domain: the careers hostname, e.g. "
            "`recrutement.monoprix.fr`. **There is no tenant directory** — "
            "these sites are white-labelled on the employer's own domain, so "
            "nothing lists them. The URL comes from the user, as for umantis.")
    d = a.domain.strip()
    m = HOST_RE.match(d)
    if m:
        d = m.group(1)
    d = d.strip("/").lower()
    if not DOMAIN_RE.match(d):
        die(f"{a.domain!r} is not a hostname. Give the careers site's domain "
            "with no scheme and no path — `recrutement.monoprix.fr`.")
    return d


def to_text(markup):
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", markup or "")
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", txt)
    txt = re.sub(r"(?i)<li[^>]*>", "- ", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html_mod.unescape(txt).replace(" ", " ")
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", txt).strip()


def listing(domain, locale, limit=PAGE_SIZE, page=1):
    qs = urllib.parse.urlencode({"domainName": domain, "locale": locale,
                                 "limit": limit, "page": page})
    return call(f"{API}?{qs}", post=True)


def all_items(domain, locale, size):
    """Every ad, paged. Returns (items, count, brands)."""
    first = listing(domain, locale, limit=size, page=1)
    items = list(first.get("items") or [])
    total = first.get("count") or len(items)
    brands = {b.get("id"): b.get("name")
              for b in ((first.get("filters") or {}).get("brands") or [])}
    page = 2
    while len(items) < total:
        got = listing(domain, locale, limit=size, page=page).get("items") or []
        if not got:
            break
        items += got
        page += 1
        if page > 200:
            print("[digitalrecruiters] stopping after 200 pages — the count "
                  "and the pages disagree, which is a bug worth reporting",
                  file=sys.stderr)
            break
    return items, total, brands


def card(it, brands, domain, locale):
    brand_id = it.get("brand_id")
    return {
        # `id` is the composite <job_ad_id>-<location_id>, and it is the only
        # unique key: one ad opened in five towns shares one `job_ad_id`
        # across five distinct postings. Keying the ledger on job_ad_id
        # collapses them into one and loses four, silently.
        "id": it.get("id"),
        "ledger_id": f"digitalrecruiters:{it.get('id')}",
        "url": AD_URL.format(domain, locale.split("_")[0], it.get("url"))
        if it.get("url") else None,
        "job_ad_id": it.get("job_ad_id"),
        "title": it.get("title"),
        # The careers site can carry several brands, and the ad page names the
        # *group* for all of them. This is the only place the actual brand is.
        "brand": brands.get(brand_id),
        "brand_id": brand_id,
        "job_family": it.get("job"),
        "contract": it.get("contract"),
        "location": it.get("location"),
        # True when the ad was pulled in from another careers site, so the
        # same posting may also be reachable under that site's own domain.
        "aggregated": it.get("is_aggregated"),
        "external": it.get("is_external"),
        "career_domain": it.get("career_domain"),
    }


def ad_fields(page):
    # One reader for every board's ld+json: tolerant of the quote style
    # on the script tag, and strict=False on the parse. Issue #76.
    for d in postings(page):
        org = d.get("hiringOrganization") or {}
        addr = (d.get("jobLocation") or {}).get("address") or {}
        sal = d.get("baseSalary") or {}
        val = sal.get("value") or {}
        emp = d.get("employmentType")
        return {
            "employer": org.get("name"),
            "street": addr.get("streetAddress"),
            "city": addr.get("addressLocality"),
            "postal_code": addr.get("postalCode"),
            "country": addr.get("addressCountry"),
            "employment_type": ", ".join(emp) if isinstance(emp, list)
            else emp,
            "salary_min": val.get("minValue"),
            "salary_max": val.get("maxValue"),
            "salary_currency": sal.get("currency"),
            "published": d.get("datePosted"),
            "description": to_text(d.get("description")),
        }
    return None


def cmd_jobs(a):
    domain = domain_of(a)
    items, total, brands = all_items(domain, a.locale, a.page_size)
    print(f"[digitalrecruiters] {domain}: {total} ads, {len(items)} collected",
          file=sys.stderr)
    if total and len(items) < total:
        print(f"[digitalrecruiters] only {len(items)} of {total} came back — "
              "this sweep is incomplete, not the size of the board",
              file=sys.stderr)
    if len(brands) > 1:
        print(f"[digitalrecruiters] {len(brands)} brands on this site: "
              f"{', '.join(str(v) for v in brands.values())}. The ad pages "
              "name the group for all of them, so `brand` is the only field "
              "that separates them.", file=sys.stderr)
    rows, detailed = 0, 0
    for it in items:
        c = card(it, brands, domain, a.locale)
        # A whole tenant with details is prohibitive by design: 948 ads at the
        # published 10s crawl-delay is over two and a half hours. The cap is
        # here so `--with-detail` cannot become that by accident.
        if a.with_detail and c["url"] and detailed >= a.max_detail:
            c["detail_skipped"] = True
        elif a.with_detail and c["url"]:
            detailed += 1
            time.sleep(a.delay)
            extra = ad_fields(call(c["url"]))
            if extra:
                c.update(extra)
            else:
                c["detail_unavailable"] = True
        print(json.dumps(c, ensure_ascii=False))
        rows += 1
    print(f"[digitalrecruiters] {rows} cards returned", file=sys.stderr)
    if a.with_detail and rows > detailed:
        print(f"[digitalrecruiters] descriptions read for {detailed} of "
              f"{rows} — the rest carry detail_skipped. Raise --max-detail "
              "only with the pace in mind, or screen first and read the ads "
              "that pass.", file=sys.stderr)
    if not a.with_detail:
        print("[digitalrecruiters] the listing carries no description, no "
              "date and no salary — those are on the ad page, and reading "
              f"them costs one request each at {CRAWL_DELAY:g}s apart. Screen "
              "on title, contract and location first.", file=sys.stderr)


def cmd_filters(a):
    domain = domain_of(a)
    d = listing(domain, a.locale, limit=1)
    out = {"domain": domain, "count": d.get("count"), "filters": {}}
    for k, v in ((d.get("filters") or {}).items()):
        if isinstance(v, list):
            out["filters"][k] = [{"id": x.get("id"), "name": x.get("name"),
                                  "count": x.get("count")} for x in v]
    print(json.dumps(out, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--domain", help="the careers hostname")
    p.add_argument("--locale", default="fr_FR")
    sub = p.add_subparsers(dest="cmd", required=True)

    j = sub.add_parser("jobs", help="every ad on one careers site")
    j.add_argument("--domain")
    j.add_argument("--locale", default="fr_FR")
    j.add_argument("--with-detail", action="store_true",
                   help="read each ad page for the description, the street "
                        "address and the salary — one request per ad")
    j.add_argument("--max-detail", type=int, default=50,
                   help="how many ads to read in full (default 50)")
    j.add_argument("--page-size", type=int, default=PAGE_SIZE,
                   help=f"ads per request (default {PAGE_SIZE})")
    j.add_argument("--delay", type=float, default=CRAWL_DELAY,
                   help=f"seconds between ad reads (default {CRAWL_DELAY:g}, "
                        "the Crawl-delay these sites publish)")
    j.set_defaults(func=cmd_jobs)

    f = sub.add_parser("filters", help="the facet catalogue, with counts")
    f.add_argument("--domain")
    f.add_argument("--locale", default="fr_FR")
    f.set_defaults(func=cmd_filters)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
