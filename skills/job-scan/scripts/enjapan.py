#!/usr/bin/env python3
"""エン転職 (`employment.en-japan.com`) — one of Japan's largest boards, read through the job sitemap its rules declare and the JobPosting every advertisement carries.

  enjapan.py sitemap [--since YYYY-MM-DD] [--limit N] [--no-site-total]
  enjapan.py ad --url <advertisement URL>

THE SITEMAP IS A SUBSET, AND THE ROOT STATES THE WHOLE — BOTH ARE PRINTED

`sitemap_index.xml` declares one job file, `sitemap_work_0001.xml.gz` —
10 811 `/desc_<id>/` addresses on 2026-09-12 15:3x UTC, every one with a
real `<lastmod>` (2025-12 → 2026-09; the newest dated the day before the
read). The front page states «求人数 125248 件！ 2026年9月10日 更新» — twelve
times the file. **The two numbers answer different questions and the adapter
prints both**: «10 811 emitted, site states 125 248 — 114 437 short; the
sitemap is the subset the site publishes to crawlers, the front page counts
its whole store». Neither is corrected into the other; `--since` filters on
the file's `<lastmod>`, which is the advertisement's own date.

THE RULES refuse `ClaudeBot` everything (`Disallow: /`) and give `Claude-User`
the `*` regime — open on `/desc_<id>/`, the sitemap and the root (decision of
2026-09-07: a named refusal of one token does not bind the other). The `*`
group refuses `*sort*`, `*refine*`, the faceted `/k_*/*_*/*_*/` and
`/s_*/…` listings, and **`/desc_eng*`** — the English rendering of an
advertisement is a refused path and is never fetched. `Crawl-delay: 30` sits
in the `GPTBot` group only; this adapter spaces 2 s.

EVERY ADVERTISEMENT CARRIES A JobPosting IN JSON-LD — title, description
(HTML escaped twice: `&amp;lt;p&amp;gt;`, unescaped twice here), datePosted,
validThrough, hiringOrganization, jobLocation (a list of places, ward +
prefecture), employmentType (a list), baseSalary (JPY, min/max, YEAR),
educationRequirements, experienceRequirements, industry, jobBenefits,
workHours, `identifier.value` (the site's employer-side number, NOT the URL's
`desc_<id>` — emitted as `identifier_value`, as published). The page also
prints «掲載期間 26/09/11 ～ 26/12/10» — the same dates as the JobPosting.
Everything is Japanese and nothing is translated. Measured 2026-09-12
15:26–15:3x UTC, every fetch under the declared identity.
"""

import argparse
import gzip
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

BASE = "https://employment.en-japan.com"
INDEX = BASE + "/sitemap_index.xml"
AD_RE = re.compile(r"^https?://employment\.en-japan\.com/desc_(\d+)/?$")
WORK_RE = re.compile(r"/sitemap_work_\d+\.xml(?:\.gz)?$")
# <div ...>求人数 <span>125248</span> 件！ 2026年9月10日 更新！  — the site's own figure, tags stripped first
SITE_COUNT_RE = re.compile(r"求人数\s*([\d,]+)\s*件")
SITE_DATE_RE = re.compile(r"(\d{4})年(\d{1,2})月(\d{1,2})日\s*更新")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[en-japan] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace("employment.en-japan.com", own=2.0)   # Crawl-delay: 30 binds GPTBot only; 2 s is ours


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.5",
        "Accept-Language": "ja,en;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    # the JobPosting's description is escaped twice on this site — &amp;lt;p&amp;gt; — so unescape until stable
    s = markup or ""
    for _ in range(3):
        u = htmlmod.unescape(s)
        if u == s:
            break
        s = u
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = re.sub(r"[ \t　]+", " ", s)
    return re.sub(r"(?:\s*\n\s*)+", "\n", s).strip()


def th(n):
    """Thousands with a space — the repo's figure style."""
    return f"{n:,}".replace(",", " ")


def site_count(body):
    """The count the front page states about itself — «求人数 125248 件！ 2026年9月10日 更新» — or (None, None)."""
    plain = re.sub(r"(?s)<[^>]+>", " ", body or "")
    m = SITE_COUNT_RE.search(plain)
    d = SITE_DATE_RE.search(plain)
    return (int(m.group(1).replace(",", "")) if m else None,
            f"{d.group(1)}-{int(d.group(2)):02d}-{int(d.group(3)):02d}" if d else None)


def entries(xml):
    """(id, url, lastmod) for every /desc_<id>/ in a job file."""
    out = []
    for m in re.finditer(r"(?is)<url>\s*<loc>\s*(?:<!\[CDATA\[)?\s*([^<\]\s]+)\s*(?:\]\]>)?\s*</loc>(.*?)</url>", xml):
        loc = m.group(1).strip()
        am = AD_RE.match(loc)
        if not am:
            continue
        lm = re.search(r"<lastmod>\s*([^<\s]+)\s*</lastmod>", m.group(2))
        out.append((am.group(1), loc, lm.group(1)[:10] if lm else None))
    return out


def cmd_sitemap(a):
    code, body = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}", EXIT_PARTIAL)
    children = [c for c in sitemap_locs(body) if WORK_RE.search(c)]
    if not children:
        die(f"{INDEX} declares {len(sitemap_locs(body))} children and none of the shape sitemap_work_NNNN — the job file moved; read the index before believing a zero.", EXIT_PARTIAL)
    rows, seen, raw_total, undated = [], set(), 0, 0
    for child in children:
        code, xml = get(child)
        if code != 200:
            die(f"{child}: HTTP {code}", EXIT_PARTIAL)
        es = entries(xml)
        raw_total += len(sitemap_locs(xml))
        if not es:
            die(empty_first_page("en-japan", xml, "/desc_<id>/ <loc>", where=child), EXIT_PARTIAL)
        for ident, url, lastmod in es:
            if ident in seen:
                continue
            seen.add(ident)
            if lastmod is None:
                undated += 1
            if a.since and (lastmod is None or lastmod < a.since):
                continue
            rows.append({"source": "en-japan", "country": "JP", "ledger_id": f"en-japan:{ident}",
                         "id": ident, "url": url, "lastmod": lastmod})
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    since = f" dated on or after {a.since}" if a.since else ""
    note(f"{th(raw_total)} <loc> across {len(children)} job file(s); **{th(len(seen))} distinct advertisement id(s)**, "
         f"{th(undated)} without <lastmod>; {th(len(rows))} emitted{since}.")
    if a.no_site_total:
        return
    code, page = get(BASE + "/")
    stated, stated_on = site_count(page) if code == 200 else (None, None)
    if stated is None:
        note(f"{BASE}/ states no count this run (HTTP {code}) — no second source.")
        return
    n = len(seen)
    on = f" (updated {stated_on})" if stated_on else ""
    if stated == n:
        note(f"{th(n)} in the sitemap, site states {th(stated)}{on} — equal.")
    else:
        note(f"{th(n)} in the sitemap, site states {th(stated)}{on} — {th(abs(stated - n))} "
             + ("short" if stated > n else "more in the sitemap than the site states")
             + "; the sitemap is the subset the site publishes to crawlers, the front page counts its whole store — two questions, both printed.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/desc_<id>/ (and never /desc_eng…, which the rules refuse)")
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
    locs = d.get("jobLocation") or []
    if isinstance(locs, dict):
        locs = [locs]
    places = []
    for loc in locs:
        addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
        places.append(" ".join(x for x in (addr.get("addressRegion"), addr.get("addressLocality")) if x))
    sal = d.get("baseSalary") or {}
    val = sal.get("value") if isinstance(sal, dict) else None
    if not isinstance(val, dict):
        val = sal if isinstance(sal, dict) else {}
    idv = d.get("identifier") or {}
    et = d.get("employmentType")

    def money(v):
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return None
    print(json.dumps({
        "source": "en-japan", "country": "JP", "ledger_id": f"en-japan:{ident}", "id": ident, "url": a.url,
        "title": text(d.get("title")),
        "employer": org.get("name") if isinstance(org, dict) else None,
        # the site's own employer-side number, not the URL's desc_<id> — as published
        "identifier_value": idv.get("value") if isinstance(idv, dict) else None,
        "employment_type": et if isinstance(et, list) else ([et] if et else []),
        "places": places,
        "posted": d.get("datePosted"), "valid_through": d.get("validThrough"),
        "salary_currency": sal.get("currency") if isinstance(sal, dict) else None,
        "salary_min": money(val.get("minValue")), "salary_max": money(val.get("maxValue")),
        "salary_unit": (val.get("unitText") or "").strip() or None,
        "education": text(d.get("educationRequirements")) or None,
        "requirements": text(d.get("experienceRequirements")) or None,
        "industry": d.get("industry") if isinstance(d.get("industry"), list) else ([d.get("industry")] if d.get("industry") else []),
        "work_hours": text(d.get("workHours")) or None,
        "benefits": text(d.get("jobBenefits")) or None,
        "description": text(d.get("description"))[:20000], "language": "ja",
    }, ensure_ascii=False))
    note("`identifier_value` is the site's employer-side number as published, not the advertisement id; "
         "the description was HTML-escaped twice by the site and is unescaped here. Nothing is translated.")


def main():
    p = argparse.ArgumentParser(description="エン転職 — through the job sitemap it declares and the JSON-LD its pages carry; the front page's count printed beside the file's.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="distinct advertisement ids with <lastmod> — 2 requests, 3 with the front page's count")
    s.add_argument("--since", help="YYYY-MM-DD, on the file's <lastmod>")
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
