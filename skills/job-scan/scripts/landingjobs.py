#!/usr/bin/env python3
"""Landing.Jobs (`landing.jobs`) — the Lisbon-based European tech board, read through its sitemap and the JobPosting every advertisement carries; the search route is refused and never taken.

  landingjobs.py sitemap [--limit N] [--no-site-total]
  landingjobs.py ad --url <advertisement URL>

THE SITEMAP IS THE ROUTE — THE SEARCH IS REFUSED BY THE RULES

`robots.txt` refuses `/api/`, `/jobs/search`, `/job_closed.html` and four
back-office paths to `*`. The listing page `/jobs` is open and server-renders
50 static cards while stating its count — «55 results» on 2026-09-12 — and
everything past the 50th card goes through `/jobs/search` (`?page=2` on the
open path returns the same 50). **So the inventory is read from
`sitemap.xml`**, which on the same day held exactly 55 `/at/<company>/<slug>`
advertisements (plus 13 `/at/<company>` employer pages, 1 505 `/jobs/in|for/…`
facet pages and 567 blog posts — all told apart by shape, not by count). The
listing's stated count is the second source: «55 emitted, site states 55 —
equal», or «k short». `<lastmod>` on every entry, but 2026-09-01 on all 68 `/at/` entries
while one advertisement was created 2026-09-07 — not the advertisement's
date, and what it measures is not established; nothing to filter on, so no
`--since`.

EVERY ADVERTISEMENT CARRIES A JobPosting in JSON-LD — title, description
(HTML), datePosted, validThrough, employmentType, hiringOrganization,
identifier (the slug), jobLocation, experienceRequirements, directApply —
AND a React props block (`data-react-cache-id="jobPage/JobPage-0"`) with the
site's own record: numeric `id`, `state_name`, `closed_at`,
`remote_working_label` (Hybrid / Remote / Onsite), `job_type`, `office_
locations`, `must_have_skills`, `experience_min/max`, `salary` (null on every
page read — emitted raw as `salary_raw`), `visa_support`,
`relocation_paid`, `preferred_languages`. Both are read; the JobPosting is
the body, the props are the fields the JobPosting lacks.

A CLOSED ADVERTISEMENT presumably lands on `/job_closed.html` — the path the
rules refuse, named for that. *Not observed while writing this: every
advertisement read was live.* **No redirect is followed**: a 3xx to that
path is read as gone (exit 3), any other 3xx as indeterminate (exit 6), and
the refused page is never requested either way.

The rules carry no `Crawl-delay`; this adapter spaces 2 s. `certain: True`,
200 to the declared identity on every path read. Measured 2026-09-12
11:22–11:3x UTC.
"""

import argparse
import html as htmlmod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _ldjson import absent_reason, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _sitemap import locs as sitemap_locs
from _ua import UA
from _zero import empty_first_page

BASE = "https://landing.jobs"
SITEMAP = BASE + "/sitemap.xml"
LISTING = BASE + "/jobs"
AD_RE = re.compile(r"^https://landing\.jobs/at/([a-z0-9-]+)/([a-z0-9-]+)/?$")
COMPANY_RE = re.compile(r"^https://landing\.jobs/at/([a-z0-9-]+)/?$")
# <div aria-atomic="true" aria-live="polite" class="lj-jobAds-count js-jobAds-count">55 results</div>
SITE_COUNT_RE = re.compile(r'js-jobAds-count">\s*([\d,. ]+)\s*result')
PROPS_RE = re.compile(r'data-react-props="([^"]*)"[^>]*data-react-cache-id="jobPage/JobPage-0"')
CLOSED_PATH = "/job_closed.html"   # refused by the rules; a redirect there is the answer, never a request

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[landing.jobs] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Return the redirect instead of following it — a closed advertisement
    redirects to a path the rules refuse, and the redirect is the answer."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)
_PACE = Pace("landing.jobs", own=2.0)   # no Crawl-delay declared; 2 s is ours


def get(url):
    """(code, body, location) — a 3xx comes back as its code with the Location it named, unfollowed."""
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en,pt;q=0.7"})
    try:
        with _OPENER.open(req, timeout=60) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0], None
    except urllib.error.HTTPError as e:
        return e.code, "", e.headers.get("Location")
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h\d>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    """Thousands with a space — the repo's figure style."""
    return f"{n:,}".replace(",", " ")


def site_count(body):
    """The count the listing states about itself — «55 results» — or None when the phrase is not there this run."""
    m = SITE_COUNT_RE.search(body or "")
    return int(re.sub(r"[^\d]", "", m.group(1))) if m else None


def ad_id(company, slug):
    return f"{company}/{slug}"


def cmd_sitemap(a):
    code, xml, _ = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_PARTIAL)
    raw, ads, companies, other, seen = 0, [], 0, 0, set()
    for loc in sitemap_locs(xml):
        raw += 1
        loc = loc.strip()
        m = AD_RE.match(loc)
        if m:
            ident = ad_id(m.group(1), m.group(2))
            if ident in seen:
                continue
            seen.add(ident)
            ads.append({"source": "landing.jobs", "country": "PT", "ledger_id": f"landing.jobs:{ident}",
                        "id": ident, "url": loc, "company": m.group(1), "slug": m.group(2)})
        elif COMPANY_RE.match(loc):
            companies += 1
        else:
            other += 1
    if raw == 0:
        die(empty_first_page("landing.jobs", xml, "<loc>", where=SITEMAP), EXIT_PARTIAL)
    if not ads:
        die(f"{SITEMAP}: {th(raw)} <loc> and none of the shape /at/<company>/<slug> — the address shape moved, "
            "or the board has nothing; from here they look alike.", EXIT_PARTIAL)
    for r in ads[:a.limit] if a.limit else ads:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{th(raw)} <loc> in sitemap.xml: **{th(len(ads))} distinct advertisement(s)** (/at/<company>/<slug>), "
         f"{th(companies)} employer page(s) (/at/<company>), {th(other)} other (facets, blog, chrome). "
         "The <lastmod> is the same on every /at/ entry and is not the advertisement's date — nothing to filter on.")
    if a.no_site_total:
        return
    code, page, _ = get(LISTING)
    stated = site_count(page) if code == 200 else None
    if stated is None:
        note(f"{LISTING} states no count this run (HTTP {code}) — no second source.")
        return
    n, gap = th(len(ads)), th(abs(stated - len(ads)))
    if stated == len(ads):
        note(f"{n} emitted, site states {th(stated)} on {LISTING} — equal.")
    else:
        note(f"{n} emitted, site states {th(stated)} on {LISTING} — {gap} "
             + ("short" if stated > len(ads) else "more in the sitemap than the site states")
             + "; the listing serves 50 static cards and the rest through /jobs/search, which the rules refuse — "
             "the sitemap is the inventory, the listing the count.")


def props_of(body):
    m = PROPS_RE.search(body or "")
    if not m:
        return {}
    try:
        return ((json.loads(htmlmod.unescape(m.group(1))) or {}).get("jobAd") or {})
    except ValueError:
        return {}


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/at/<company>/<slug>")
    company, slug = m.group(1), m.group(2)
    code, body, location = get(a.url)
    if 300 <= code < 400:
        where = urllib.parse.urlsplit(location or "").path
        if where == CLOSED_PATH:
            die(f"{a.url}: HTTP {code} → {CLOSED_PATH} — the advertisement is closed; the closed page is refused by the rules and was not requested.", EXIT_GONE)
        die(f"{a.url}: HTTP {code} → {location!r} — a redirect this adapter does not follow.", EXIT_PARTIAL)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    found = postings(body)
    if not found:
        why = absent_reason(body)
        if getattr(why, "our_fault", False):
            die(f"{a.url}: {why} **The page announces a JobPosting and this read none.**")
        die(f"{a.url}: {why}", EXIT_PARTIAL)
    d = found[0]
    p = props_of(body)
    attrs = p.get("attributes") or {}
    org = d.get("hiringOrganization") or {}
    loc = d.get("jobLocation") or {}
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
    exp = d.get("experienceRequirements") or {}
    # `salary` was null on every page read while writing this (3 of 3); its filled shape is not known here,
    # so it is emitted as published under a name that says so — never parsed into min/max by guess
    print(json.dumps({
        "source": "landing.jobs", "country": "PT", "ledger_id": f"landing.jobs:{ad_id(company, slug)}",
        "id": ad_id(company, slug), "job_ad_id": p.get("id"), "url": a.url,
        "title": text(d.get("title")),
        "employer": org.get("name") if isinstance(org, dict) else None,
        "employer_site": org.get("sameAs") if isinstance(org, dict) else None,
        "employment_type": d.get("employmentType"), "contract": attrs.get("job_type"),
        "city": addr.get("addressLocality"), "region": addr.get("addressRegion"), "country_code": addr.get("addressCountry"),
        "office_locations": [x.get("label") for x in (attrs.get("office_locations") or []) if isinstance(x, dict)],
        "remote": attrs.get("remote_working_label"), "global_remote": attrs.get("is_global_remote"),
        "posted": d.get("datePosted"), "valid_through": d.get("validThrough"),
        "state": attrs.get("state_name"), "closed_at": attrs.get("closed_at"),
        "experience_months": exp.get("monthsOfExperience") if isinstance(exp, dict) else None,
        "experience_label": attrs.get("experience_label"),
        "skills": [s.get("name") for s in (attrs.get("must_have_skills") or []) if isinstance(s, dict)],
        "languages": attrs.get("preferred_languages_labels") or [],
        "salary_raw": attrs.get("salary"),
        "visa_support": attrs.get("visa_support"), "relocation_paid": attrs.get("relocation_paid"),
        "direct_apply": d.get("directApply"), "category": attrs.get("category"),
        "description": text(d.get("description"))[:20000], "language": "en",
    }, ensure_ascii=False))
    if not p:
        note("no `jobPage/JobPage-0` props block on this page — the site's own fields (state, remote label, skills, salary) are empty for that reason, not because the advertisement lacks them.")
    if attrs.get("state_name") and attrs.get("state_name") != "published":
        note(f"the site's own state is «{attrs.get('state_name')}» (closed_at {attrs.get('closed_at')!r}) — the page still served a JobPosting.")


def main():
    p = argparse.ArgumentParser(description="Landing.Jobs — through the sitemap it declares and the JSON-LD its pages carry; the search route is refused and never taken.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="distinct advertisement addresses — 1 request, 2 with the listing's stated count")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one advertisement, from its JSON-LD and the page's own record")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
