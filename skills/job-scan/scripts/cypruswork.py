#!/usr/bin/env python3
"""Cyprus Work (`www.cypruswork.com`) — Cyprus's general board, read through its one sitemap and the JobPosting every advertisement carries.

  cypruswork.py sitemap [--limit N] [--no-site-total]
  cypruswork.py ad --url <advertisement URL>

THE SITEMAP IS THE ROUTE, THE LISTING'S OWN `<h1>` IS THE SECOND SOURCE

`/sitemap.xml` is one `urlset`, no index: 10 708 `<loc>` on 2026-09-12
11:01 UTC, of which **1 475 are advertisements** — `/job/<id>/<slug>/`, 1 475
distinct ids — and 8 874 are `/company/` pages, the rest facets, categories,
cities and blog. **Counting the file would report the board 7× larger.** The
listing `/jobs/` states its count in its own `<h1>` — «1475 jobs» — and the
adapter prints it beside its count: on the day it was written the two were
EQUAL, and the guard says «n emitted, site states N — k short» whenever they
are not. **The `<lastmod>` is one value on all 1 475, the day of the read: a
rebuild stamp, not a posting date — so there is no `--since` here; the date
is `datePosted` on the advertisement.**

EVERY ADVERTISEMENT CARRIES A JobPosting IN JSON-LD — `title`, `description`
(HTML), `datePosted` and `validThrough` (with offset, `+03:00`),
`employmentType` (a list), `hiringOrganization` (`name`, `sameAs`),
`occupationalCategory` (a list) and `industry` (the same joined), `directApply`,
`jobLocation.address` (`addressLocality`, `addressRegion`, `addressCountry`
as a name — «Cyprus»), `baseSalary` (`currency`, min/max, `unitText`).
The country is read from the advertisement and emitted as the ISO-2 when the
name is Cyprus; any other name is emitted as published, not mapped.

THE RULES are Cloudflare's managed block — nine crawlers named and refused,
`ClaudeBot` among them, `*` open — followed by the operator's own: `*` refused
`/files/files/`, `/download/`, `/application-redirect/`, a dozen SEO crawlers
refused by name, `Sitemap: /sitemap.xml`. `identity()` answers `claude-user`
(owner's decision of 2026-09-07), `verdict()` sweeps since #230; no
`Crawl-delay`; `certain: True`. **Its sibling `www.cyprusjobs.com`, under the
same managed block, refuses the client with a static 403 — the rules file
predicts nothing about the transport** (#233, lot 3). Measured 2026-09-12
11:00–11:03 UTC.
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

BASE = "https://www.cypruswork.com"
SITEMAP = BASE + "/sitemap.xml"
LISTING = BASE + "/jobs/"
AD_RE = re.compile(r"^https://www\.cypruswork\.com/job/(\d+)/[^/]*/?$")
# <h1 class="search-results__title …"> 1475 jobs </h1>
LASTMOD_RE = re.compile(r"<loc>\s*([^<]+?)\s*</loc>\s*<lastmod>\s*([^<]+?)\s*</lastmod>")
SITE_COUNT_RE = re.compile(r"<h1[^>]*>\s*([\d,]+)\s+jobs?\s*</h1>", re.I)
COUNTRY = {"cyprus": "CY"}
GREEK_RE = re.compile(r"[\u0370-\u03FF\u1F00-\u1FFF]")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[cypruswork] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace("www.cypruswork.com", own=2.0)   # no Crawl-delay declared; 2 s is ours


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en,el;q=0.5"})
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
    """Thousands with a space — «1 475» — the repo's figure style."""
    return f"{n:,}".replace(",", " ")


def site_count(body):
    """The count the listing states about itself — «1475 jobs» in its `<h1>` —
    or None when the phrase is not there this run."""
    m = SITE_COUNT_RE.search(body or "")
    return int(m.group(1).replace(",", "")) if m else None


def cmd_sitemap(a):
    code, xml = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_PARTIAL)
    raw, unmatched, rows, seen = 0, 0, [], set()
    # the <lastmod> beside each advertisement <loc>, measured this run and not
    # assumed: one distinct value is a rebuild stamp, more would be a date
    stamps = {lm for u, lm in LASTMOD_RE.findall(xml) if AD_RE.match(u.strip())}
    for loc in sitemap_locs(xml):
        raw += 1
        m = AD_RE.match(loc.strip())
        if not m:
            unmatched += 1
            continue
        ident = m.group(1)
        if ident in seen:
            continue
        seen.add(ident)
        rows.append({"source": "cypruswork", "country": "CY", "ledger_id": f"cypruswork:{ident}",
                     "id": ident, "url": loc.strip()})
    if raw == 0:
        die(empty_first_page("cypruswork", xml, "<loc>", where=SITEMAP), EXIT_PARTIAL)
    if not rows:
        die(f"{SITEMAP}: {raw} <loc> and not one of the shape /job/<id>/<slug>/ — the "
            f"advertisement addresses moved; nothing here says the board is empty.", EXIT_PARTIAL)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{raw} <loc> in the sitemap; {raw - unmatched} matched the advertisement shape and "
         f"{unmatched} did not (company pages, facets, categories); "
         f"**{len(rows)} distinct advertisement id(s)**"
         + (f" ({a.limit} printed under --limit)" if a.limit else "") + ". "
         + (f"One <lastmod> value on every advertisement entry ({next(iter(stamps))}) — a rebuild "
            f"stamp, not a date; read datePosted on the advertisement."
            if len(stamps) == 1 else
            f"{len(stamps)} distinct <lastmod> values on the advertisement entries — "
            f"{'none at all' if not stamps else 'the stamp is not the single rebuild value this adapter was written against'}; "
            f"still not read as a date here."))
    if a.no_site_total:
        return
    code, page = get(LISTING)
    stated = site_count(page) if code == 200 else None
    if stated is None:
        note(f"{LISTING} states no count this run (HTTP {code}) — no second source.")
        return
    n, gap = th(len(rows)), th(abs(stated - len(rows)))
    if stated == len(rows):
        note(f"{n} emitted, site states {th(stated)} on {LISTING} — equal.")
    else:
        note(f"{n} emitted, site states {th(stated)} on {LISTING} — {gap} "
             + ("short" if stated > len(rows) else "more in the sitemap than the site states")
             + "; the sitemap and the listing are two views of one store.")


def _first(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/job/<id>/<slug>/")
    ident = m.group(1)
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
    loc = _first(d.get("jobLocation")) or {}
    addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
    sal = d.get("baseSalary") or {}
    val = sal.get("value") if isinstance(sal, dict) else None
    if not isinstance(val, dict):
        val = sal if isinstance(sal, dict) else {}
    country_name = text(addr.get("addressCountry")) if isinstance(addr, dict) else ""
    et = d.get("employmentType")
    cats = d.get("occupationalCategory")

    title, desc = text(d.get("title")), text(d.get("description"))

    def money(v):
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return None
    print(json.dumps({
        "source": "cypruswork",
        # the ISO-2 when the advertisement names Cyprus; any other name as published
        "country": COUNTRY.get(country_name.lower(), country_name or None),
        "ledger_id": f"cypruswork:{ident}", "id": ident, "url": a.url,
        "title": title,
        "employer": org.get("name") if isinstance(org, dict) else None,
        "employer_site": org.get("sameAs") if isinstance(org, dict) else None,
        "employment_type": ", ".join(et) if isinstance(et, list) else et,
        "categories": cats if isinstance(cats, list) else ([cats] if cats else []),
        "city": text(addr.get("addressLocality")) or None,
        "region": text(addr.get("addressRegion")) or None,
        "posted": d.get("datePosted"),
        "valid_through": d.get("validThrough"),
        "direct_apply": d.get("directApply"),
        "salary_currency": sal.get("currency") if isinstance(sal, dict) else None,
        "salary_min": money(val.get("minValue")),
        "salary_max": money(val.get("maxValue")),
        "salary_unit": (val.get("unitText") or "").strip() or None,
        "description": desc[:20000],
        # the board is bilingual and says nothing per advertisement: Greek script
        # in the title or the body says «el», otherwise «en» — a reading, not a field
        "language": "el" if GREEK_RE.search(title + " " + desc[:2000]) else "en",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Cyprus Work — Cyprus's general board, through the one sitemap it declares and the JSON-LD its pages carry.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="distinct advertisement ids — 1 request, 2 with the listing's count")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one advertisement, from its JSON-LD")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
