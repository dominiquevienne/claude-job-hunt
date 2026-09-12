#!/usr/bin/env python3
"""Green (`www.green-japan.com`) — the Japanese IT/Web board, read through its job sitemap and the JobPosting every advertisement carries.

  greenjapan.py sitemap [--limit N] [--no-site-total]
  greenjapan.py ad --url <advertisement URL>

THE SITEMAP IS THE ROUTE, THE SEARCH PAGE'S COUNT IS THE SECOND SOURCE

`sitemap.xml` is an index of a handful of children; `sitemap/jobs.xml` holds
the advertisements — 28 284 `<loc>` of the shape `/company/<company>/job/<id>`
on 2026-09-12 09:34 UTC, all distinct, **no `<lastmod>` at all** (nothing to
filter on; `--since` does not exist here for that reason). The search page
`/search` states its count in its own meta description — «求人を28284件掲載»
— and the adapter prints it beside its count: on the day it was written the
two were EQUAL, and the guard says «n emitted, site states N — k short»
whenever they are not.

EVERY ADVERTISEMENT CARRIES A JobPosting IN JSON-LD — title, hiring
organisation, `identifier` (the site's job id), `datePosted`, `validThrough`,
`employmentType`, `experienceRequirements`, `jobBenefits`, `workHours`,
`jobLocation` (one postal address, postcode and street in `addressLocality`),
`baseSalary` (`currency: "YEN"` — not the ISO code JPY — min/max, YEAR),
`description`. **Two values are emitted AS PUBLISHED and flagged, not
corrected:** `validThrough` is the read date plus one year (2027-09-12 on a
2026-09-12 read, on an advertisement posted 2025-11-07 — a rolling value, not
a deadline), and the currency is the site's `YEN`. **Nothing is translated.**

THE RULES refuse 10 paths to `*` (`/mypage0*`, `/messages/`, `/profiles/`…),
none of them the sitemap, `/search` or `/company/`; no `Crawl-delay`;
`certain: True`. Behind CloudFront, 200 to the declared identity. Measured
2026-09-12 09:33–09:40 UTC.
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

BASE = "https://www.green-japan.com"
INDEX = BASE + "/sitemap.xml"
JOBS = BASE + "/sitemap/jobs.xml"
SEARCH = BASE + "/search"
AD_RE = re.compile(r"^https://www\.green-japan\.com/company/(\d+)/job/(\d+)/?$")
# <meta content="求人を28284件掲載。…" name="Description">
SITE_COUNT_RE = re.compile(r"求人を\s*([\d,]+)\s*件")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[green-japan] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace("www.green-japan.com", own=2.0)   # no Crawl-delay declared; 2 s is ours


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "ja,en;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"[ \t]+", " ", htmlmod.unescape(markup)).strip()


def th(n):
    """Thousands with a space — «28 284» — the repo's figure style."""
    return f"{n:,}".replace(",", " ")


def site_count(body):
    """The count the search page states about itself — «求人を28284件掲載» in
    its meta description — or None when the phrase is not there this run."""
    m = SITE_COUNT_RE.search(body or "")
    return int(m.group(1).replace(",", "")) if m else None


def cmd_sitemap(a):
    code, body = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}", EXIT_PARTIAL)
    children = sitemap_locs(body)
    if JOBS not in children:
        die(f"{INDEX} declares {len(children)} children and not {JOBS} — the job file moved; read the index before believing a zero.", EXIT_PARTIAL)
    code, xml = get(JOBS)
    if code != 200:
        die(f"{JOBS}: HTTP {code}", EXIT_PARTIAL)
    raw, unmatched, rows, seen = 0, 0, [], set()
    for loc in sitemap_locs(xml):
        raw += 1
        m = AD_RE.match(loc.strip())
        if not m:
            unmatched += 1
            continue
        ident = m.group(2)
        if ident in seen:
            continue
        seen.add(ident)
        rows.append({"source": "green-japan", "country": "JP", "ledger_id": f"green-japan:{ident}",
                     "id": ident, "url": loc.strip(), "company_id": m.group(1)})
    if raw == 0:
        die(empty_first_page("green-japan", xml, "<loc>", where=JOBS), EXIT_PARTIAL)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{raw} <loc> in sitemap/jobs.xml; {raw - unmatched} matched the advertisement shape and "
         f"{unmatched} did not; **{len(rows)} distinct advertisement id(s)** across "
         f"{len({r['company_id'] for r in rows})} companies. No <lastmod> in this file.")
    if a.no_site_total:
        return
    code, page = get(SEARCH)
    stated = site_count(page) if code == 200 else None
    if stated is None:
        note(f"{SEARCH} states no count this run (HTTP {code}) — no second source.")
        return
    n, gap = th(len(rows)), th(abs(stated - len(rows)))
    if stated == len(rows):
        note(f"{n} emitted, site states {th(stated)} on {SEARCH} — equal.")
    else:
        note(f"{n} emitted, site states {th(stated)} on {SEARCH} — {gap} "
             + ("short" if stated > len(rows) else "more in the sitemap than the site states")
             + "; the sitemap and the search index are two views of one store.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/company/<company>/job/<id>")
    ident = m.group(2)
    code, body = get(a.url)
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
    org = d.get("hiringOrganization") or {}
    idv = d.get("identifier") or {}
    loc = d.get("jobLocation") or {}
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
    sal = d.get("baseSalary") or {}
    val = sal.get("value") if isinstance(sal, dict) else None
    if not isinstance(val, dict):
        val = sal if isinstance(sal, dict) else {}

    def money(v):
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return None
    print(json.dumps({
        "source": "green-japan", "country": "JP", "ledger_id": f"green-japan:{ident}", "id": ident,
        "url": a.url, "company_id": m.group(1),
        "title": text(d.get("title")),
        "employer": org.get("name") if isinstance(org, dict) else None,
        "employment_type": d.get("employmentType"),
        "address": text(addr.get("addressLocality")) or None,
        "posted": d.get("datePosted"),
        # emitted as published: the read date plus one year on every page read, not a deadline
        "valid_through": d.get("validThrough"),
        # emitted as published: the site writes "YEN", not the ISO code JPY
        "salary_currency": sal.get("currency") if isinstance(sal, dict) else None,
        "salary_min": money(val.get("minValue")),
        "salary_max": money(val.get("maxValue")),
        "salary_unit": (val.get("unitText") or "").strip() or None,
        "requirements": text(d.get("experienceRequirements")),
        "work_hours": text(d.get("workHours")),
        "benefits": text(d.get("jobBenefits")),
        "description": text(d.get("description"))[:20000], "language": "ja",
    }, ensure_ascii=False))
    note("`valid_through` and `salary_currency` are the site's values as published — "
         "the first is a rolling read-date-plus-one-year, the second is «YEN», not the ISO JPY; neither is corrected here.")


def main():
    p = argparse.ArgumentParser(description="Green — Japan's IT/Web board, through the job sitemap it declares and the JSON-LD its pages carry.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="distinct advertisement ids — 2 requests, 3 with the search page's count")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one advertisement, from its JSON-LD — Japanese as published")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
