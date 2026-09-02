#!/usr/bin/env python3
"""Fetch job ads from hellowork.com, France's largest private generalist board.

HelloWork (ex-RegionsJob, merged with Cadreo in 2022) is the board of French
SMEs and the regions — around 5 million visitors a month.

**Read `shared/boards/hellowork.md` before changing anything here.** Its
robots.txt disallows **every** query-string URL, with no search carve-out, plus
`/emploi/recherche.html`, `/api/`, `/search/` and `/rss/`; the sitemap it
advertises answers 403. What is left open is the site's own path-based facet
system — `/fr-fr/emploi/domaine_<d>.html`, optionally narrowed by city or by
job title — and the ad pages themselves. That is what this adapter reads, and
nothing else.

The consequence: **one facet page is 20 ads and there is no page 2**, because
pagination is a form that produces `?p=2`. Coverage comes from combining
facets, not from paging. `facets` enumerates the ones a domain actually offers,
so nobody has to guess a URL.

Usage:
  hellowork.py facets --domaine informatique
  hellowork.py search --domaine informatique
  hellowork.py search --domaine informatique --ville lyon --cp 69000
  hellowork.py search --metier administrateur-reseau --with-detail
  hellowork.py ad 82832314

Output: one JSON object per line (search), or one JSON object (ad).
"""

import argparse
import html
import json
import re

from _ldjson import absent_reason, postings
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://www.hellowork.com/fr-fr"
AD_URL = BASE + "/emplois/{}.html"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# A facet page serves exactly this many, and pagination is a query string,
# which robots.txt forbids. See the module docstring.
PAGE_ADS = 20

CARD_RE = re.compile(r'data-cy="serpCard"')
ID_RE = re.compile(r'href="/fr-fr/emplois/(\d+)\.html"')
# The title link's <h3> holds two <p>: the job title, then the employer.
HEAD_RE = re.compile(r'data-cy="offerTitle".*?<h3[^>]*>(.*?)</h3>', re.S)
P_RE = re.compile(r'<p[^>]*>(.*?)</p>', re.S)
PLACE_RE = re.compile(r'data-cy="localisationCard"[^>]*>\s*([^<]+)')
CONTRACT_RE = re.compile(r'data-cy="contractCard"[^>]*>\s*([^<]+)')
AGE_RE = re.compile(r'(il y a [^<]{2,30})<')

FACET_CITY_RE = re.compile(
    r'href="/fr-fr/emploi/domaine_([a-z0-9-]+)-ville_([a-z0-9-]+)-(\w+)\.html"')
FACET_JOB_RE = re.compile(r'href="/fr-fr/emploi/metier_([a-z0-9-]+)\.html"')


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def fetch(url):
    # The robots boundary, enforced in code rather than left to discipline:
    # every disallowed route on this site is reached by adding a query string,
    # so a URL carrying one is a bug, not a request to make.
    if "?" in url:
        die(f"refusing to request a URL with a query string: {url}\n"
            "HelloWork's robots.txt disallows /*? with no search exception. "
            "Pagination and search both live there. Combine facets instead.")
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "fr-FR,fr;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            die(f"nothing at that URL (HTTP {e.code}). For an ad, record it as "
                "discarded. For a facet, check it with `facets` — a domain or "
                "city slug that does not exist answers 404 with a full-looking "
                "page, not an error message.", code=3)
        if e.code in (403, 429):
            die(f"HelloWork answered HTTP {e.code}. Its WAF fronts the whole "
                "site — the sitemap it advertises answers 403 too. Stop and "
                "wait; do not retry in a loop and do not rotate the "
                "User-Agent to get around it.")
        die(f"HelloWork returned HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach HelloWork: {e}")


def clean(s):
    if s is None:
        return None
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s).replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip() or None


def to_text(markup):
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", markup or "")
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", txt)
    txt = re.sub(r"(?i)<li[^>]*>", "- ", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt).replace(" ", " ")
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", txt).strip()


def facet_url(a):
    if a.metier:
        return f"{BASE}/emploi/metier_{a.metier}.html"
    if not a.domaine:
        die("give --domaine or --metier. There is no unfiltered listing to "
            "sweep here: coverage comes from combining facets.")
    if a.ville:
        if not a.cp:
            die("--ville needs --cp, the town's postcode: the facet URL is "
                "`domaine_<d>-ville_<slug>-<postcode>.html`. Run `facets "
                f"--domaine {a.domaine}` to see the exact pairs the site "
                "publishes.")
        return f"{BASE}/emploi/domaine_{a.domaine}-ville_{a.ville}-{a.cp}.html"
    return f"{BASE}/emploi/domaine_{a.domaine}.html"


def split_cards(page):
    starts = [m.start() for m in CARD_RE.finditer(page)]
    return [page[x:y] for x, y in zip(starts, starts[1:] + [len(page)])]


def card_from_listing(block):
    m = ID_RE.search(block)
    if not m:
        return None
    ident = m.group(1)
    title = company = None
    head = HEAD_RE.search(block)
    if head:
        ps = [clean(p) for p in P_RE.findall(head.group(1))]
        ps = [p for p in ps if p]
        # First <p> is the job title, second the employer. Guard the order
        # rather than assume it: a card with one <p> is a title with no
        # employer, never an employer with no title.
        title = ps[0] if ps else None
        company = ps[1] if len(ps) > 1 else None
    place = PLACE_RE.search(block)
    contract = CONTRACT_RE.search(block)
    age = AGE_RE.search(block)
    return {
        "id": ident,
        "ledger_id": f"hellowork:{ident}",
        "url": AD_URL.format(ident),
        "title": title,
        "company": company,
        "location": clean(place.group(1)) if place else None,
        "contract": clean(contract.group(1)) if contract else None,
        "posted_age": clean(age.group(1)) if age else None,
    }


def job_posting(page):
    # One reader for every board's ld+json: tolerant of the quote style
    # on the script tag, and strict=False on the parse. Issue #76.
    for d in postings(page):
        return d
    return None


def card_from_ad(ident, page):
    d = job_posting(page)
    if not d:
        why = absent_reason(page)
        die(f"no JobPosting block on /emplois/{ident}.html — {why.text} "
            f"Either the ad is gone and the site served a soft 404, or the "
            f"markup changed; report it with board-request rather than "
            f"guessing at selectors.", code=2 if why.our_fault else 3)
    org = d.get("hiringOrganization") or {}
    addr = (d.get("jobLocation") or {}).get("address") or {}
    sal = d.get("baseSalary") or {}
    val = sal.get("value") or {}
    exp = d.get("experienceRequirements") or {}
    edu = d.get("educationRequirements") or {}
    ind = d.get("industry")
    emp = d.get("employmentType")
    return {
        "id": ident,
        "ledger_id": f"hellowork:{ident}",
        "url": AD_URL.format(ident),
        "title": clean(d.get("title")),
        "company": clean(org.get("name")),
        "company_url": org.get("sameAs"),
        "city": clean(addr.get("addressLocality")),
        "region": clean(addr.get("addressRegion")),
        "postal_code": clean(addr.get("postalCode")),
        # schema.org's time basis (FULL_TIME…), not the French contract type.
        # The listing card's CDI/CDD is the one to score on.
        "employment_type": ", ".join(emp) if isinstance(emp, list) else emp,
        # Present only when the role is remote; absent, not "ONSITE", otherwise.
        "remote": d.get("jobLocationType") == "TELECOMMUTE",
        "salary_min": val.get("minValue"),
        "salary_max": val.get("maxValue"),
        "salary_value": val.get("value"),
        "salary_unit": val.get("unitText"),
        "salary_currency": sal.get("currency") or d.get("salaryCurrency"),
        "industry": ", ".join(ind) if isinstance(ind, list) else clean(ind),
        "category": clean(d.get("occupationalCategory")),
        "skills": d.get("skills"),
        "months_of_experience": exp.get("monthsOfExperience"),
        "education": edu.get("credentialCategory"),
        "qualifications": to_text(d.get("qualifications")),
        "published": d.get("datePosted"),
        # Formulaic — datePosted + 30 days on every ad measured. Not an expiry.
        "valid_through": d.get("validThrough"),
        "direct_apply": d.get("directApply"),
        "description": to_text(d.get("description")),
    }


def cmd_facets(a):
    if not a.domaine:
        die("give --domaine, e.g. `facets --domaine informatique`.")
    page = fetch(f"{BASE}/emploi/domaine_{a.domaine}.html")
    cities = sorted({(v, cp) for d, v, cp in FACET_CITY_RE.findall(page)
                     if d == a.domaine})
    jobs = sorted(set(FACET_JOB_RE.findall(page)))
    if not cities and not jobs:
        die(f"no facets found under domaine_{a.domaine}. Check the slug: an "
            "unknown domain answers 404 with a full-looking page.", code=3)
    print(json.dumps({"domaine": a.domaine,
                      "villes": [{"ville": v, "cp": cp} for v, cp in cities],
                      "metiers": jobs}, ensure_ascii=False, indent=1))
    print(f"[hellowork] {len(cities)} city facets, {len(jobs)} job facets — "
          f"each is {PAGE_ADS} ads", file=sys.stderr)


def cmd_search(a):
    url = facet_url(a)
    page = fetch(url)
    blocks = split_cards(page)
    if not blocks:
        print(f"[hellowork] no result cards at {url}. That is either a facet "
              "with nothing open, a slug that does not exist (which answers "
              "404 with a full page), or a markup change — the three look "
              "alike, so check it in a browser before concluding the market "
              "is empty.", file=sys.stderr)
        return
    rows = 0
    for b in blocks:
        c = card_from_listing(b)
        if not c:
            continue
        if a.with_detail:
            time.sleep(a.delay)
            c = {**c, **card_from_ad(c["id"], fetch(c["url"]))}
        print(json.dumps(c, ensure_ascii=False))
        rows += 1
    print(f"[hellowork] {rows} cards from {url}", file=sys.stderr)
    if rows >= PAGE_ADS:
        print(f"[hellowork] that is the cap, not the result count: a facet "
              f"page serves {PAGE_ADS} ads and pagination is a query string, "
              "which this site's robots.txt disallows. There are more matches "
              "than these — add facets (another city, another métier) rather "
              "than reading this as the whole market.", file=sys.stderr)


def cmd_ad(a):
    print(json.dumps(card_from_ad(a.id, fetch(AD_URL.format(a.id))),
                     ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("facets", help="list the facets a domain publishes")
    f.add_argument("--domaine", help="slug, e.g. informatique, sante, btp")
    f.set_defaults(func=cmd_facets)

    s = sub.add_parser("search", help="one facet page, 20 ads")
    s.add_argument("--domaine")
    s.add_argument("--ville", help="town slug; needs --cp")
    s.add_argument("--cp", help="the town's postcode, part of the facet URL")
    s.add_argument("--metier", help="job-title slug; used instead of --domaine")
    s.add_argument("--with-detail", action="store_true",
                   help="also read each ad page for the description, skills "
                        "and remote flag — 20 extra requests")
    s.add_argument("--delay", type=float, default=1.0,
                   help="seconds between ad reads (default 1)")
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="read one ad in full")
    d.add_argument("id")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
