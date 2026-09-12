#!/usr/bin/env python3
"""type (`type.jp`) — a Japanese board read through the job sitemap it declares and the JobPosting every advertisement carries.

  typejp.py sitemap [--limit N] [--no-site-total]
  typejp.py ad --url <advertisement URL>

THE SITEMAP IS THE ROUTE, THE ROOT'S CATEGORY COUNTS ARE THE SECOND SOURCE

`sitemap.xml` is an index of 21 children; `sitemaps-job-detail.xml` holds the
advertisements — 2 335 `<loc>` of the shape `/job-<n>/<id>_detail/` on
2026-09-12, all distinct, **every `<lastmod>` the same value** (a
regeneration stamp, not a posting date: `--since` does not exist here for
that reason; the advertisement's `datePosted` and `validThrough` are on its
page). The home page lists its categories with a count each — «IT・Web
エンジニア（1005件）», «営業系（482件）» … — and the adapter prints their SUM
beside its count as the site's own figure, **named as a sum of categories an
advertisement may belong to several of**, never as «the board states N».

EVERY ADVERTISEMENT CARRIES A JobPosting IN JSON-LD — title, hiring
organisation, `identifier` (the employer's id on the site), `datePosted`,
`validThrough`, `employmentType`, `industry`, `occupationalCategory`,
`jobLocation[]` (prefecture and city), `baseSalary` in JPY (min/max, YEAR),
`skills`, `workHours`, `jobBenefits`, `description` as HTML in the JSON.
**Nothing is translated: the adapter emits the Japanese the site publishes.**

THE RULES refuse 10 paths to `*` (`/skillsheet/`, `/experience…`), none of
them the sitemap or `/job-N/`; no `Crawl-delay`; `certain: True`, read twice.
Root 200, 71 745 B, the title in Japanese. Measured 2026-09-11 18:37–2026-09-12
01:12 UTC.
"""

import argparse
import collections
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

BASE = "https://type.jp"
INDEX = BASE + "/sitemap.xml"
JOBS = BASE + "/sitemaps-job-detail.xml"
AD_RE = re.compile(r"^https://type\.jp/job-(\d+)/(\d+)_detail/?$")
ENTRY_RE = re.compile(r"<loc>([^<]+)</loc>\s*(?:<lastmod>([^<]*)</lastmod>)?")
# «IT・Webエンジニア （1005件）» — a space may sit before the parenthesis
CATEGORY_RE = re.compile(r"([^（(\s]{2,30})\s*[（(]\s*([\d,]+)\s*件\s*[）)]")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[type.jp] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace("type.jp", own=2.0)   # no Crawl-delay declared; 2 s is ours


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


def category_counts(body):
    """`{category: count}` off the home page's «職種から探す» block — the
    site's own figures, per category; an advertisement may sit in several."""
    return {c.strip(): int(n.replace(",", "")) for c, n in CATEGORY_RE.findall(text(body))}


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
    raw, unmatched, rows, seen, stamps = 0, 0, [], set(), collections.Counter()
    for loc, lastmod in ENTRY_RE.findall(xml):
        raw += 1
        if lastmod:
            stamps[lastmod] += 1
        m = AD_RE.match(loc.strip())
        if not m:
            unmatched += 1
            continue
        ident = m.group(2)
        if ident in seen:
            continue
        seen.add(ident)
        rows.append({"source": "type.jp", "country": "JP", "ledger_id": f"type.jp:{ident}",
                     "id": ident, "url": loc.strip(), "kind": m.group(1)})
    if raw == 0:
        die(empty_first_page("type.jp", xml, "<loc>", where=JOBS), EXIT_PARTIAL)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{raw} <loc> in {JOBS.split('/')[-1]}; {raw - unmatched} matched the advertisement shape and "
         f"{unmatched} did not; **{len(rows)} distinct advertisement id(s)**.")
    if len(stamps) == 1:
        note(f"every <lastmod> carries the same value ({next(iter(stamps))}) — a regeneration stamp, "
             f"not a posting date; `datePosted` and `validThrough` are on each page.")
    if a.no_site_total:
        return
    code, home = get(BASE + "/")
    cats = category_counts(home) if code == 200 else {}
    if not cats:
        note("the home page states no category counts this run — no second source.")
        return
    total = sum(cats.values())
    note(f"site states {total:,} across {len(cats)} categories on its home page ".replace(",", " ")
         + f"({', '.join(f'{c} {n}' for c, n in list(cats.items())[:4])} …) — **a sum of categories an "
         f"advertisement may belong to several of, so it is an upper bound on the board, not its size**; "
         f"the sitemap's {len(rows)} distinct ids stand beside it, not against it.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/job-<n>/<id>_detail/")
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
    locs = d.get("jobLocation") or []
    if isinstance(locs, dict):
        locs = [locs]
    places = []
    for l in locs:
        ad = (l.get("address") or {}) if isinstance(l, dict) else {}
        p = " ".join(x for x in (ad.get("addressRegion"), ad.get("addressLocality")) if x)
        if p and p not in places:
            places.append(p)
    sal = d.get("baseSalary") or {}
    def money(v):
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return None
    print(json.dumps({
        "source": "type.jp", "country": "JP", "ledger_id": f"type.jp:{ident}", "id": ident, "url": a.url,
        "title": text(d.get("title")),
        "employer": org.get("name") if isinstance(org, dict) else None,
        "employer_id": idv.get("value") if isinstance(idv, dict) else None,
        "employment_type": d.get("employmentType"),
        "industry": d.get("industry"), "occupation": d.get("occupationalCategory"),
        "places": places,
        "posted": d.get("datePosted"), "valid_through": d.get("validThrough"),
        "salary_currency": sal.get("currency") if isinstance(sal, dict) else None,
        "salary_min": money(sal.get("minValue")) if isinstance(sal, dict) else None,
        "salary_max": money(sal.get("maxValue")) if isinstance(sal, dict) else None,
        "salary_unit": (sal.get("unitText") or "").strip() if isinstance(sal, dict) else None,
        "skills": text(d.get("skills")), "work_hours": text(d.get("workHours")),
        "benefits": text(d.get("jobBenefits")),
        "description": text(d.get("description"))[:20000], "language": "ja",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="type.jp — Japan, through the job sitemap it declares and the JSON-LD its pages carry.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="distinct advertisement ids — 2 requests, 3 with the home-page total")
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
