#!/usr/bin/env python3
"""マイナビ転職 (`tenshoku.mynavi.jp`) — Japan's first adapter: seven job sitemaps, a site total that refutes them, and a full JobPosting on every advertisement.

  mynavi.py sitemap [--files N] [--since YYYY-MM-DD] [--limit N] [--no-site-total]
  mynavi.py ad --url <advertisement URL>

THE SITEMAP IS A SUPERSET OF THE BOARD, AND THE SITE'S OWN TOTAL SAYS SO

`sitemap/sitemap_index.xml` declares 345 children; seven are
`sitemap_jobs_NN.xml.gz` (50 000 `<loc>` each, the last 46 385 — served
already decoded, `Content-Encoding: x-gzip`). Every `<loc>` is
`/jobinfo-<id>-<a>-<b>-<c>/`: the id is the advertisement, the three numbers
a facet (occupation, area, order) — **346 385 URLs for 77 504 distinct ids**
on 2026-09-11, up to six variants of one advertisement. The home page states
**掲載求人数 61 989 件** (advertisements listed) the same day. *77 504 is not
61 989: the sitemap keeps ids whose `<lastmod>` goes back to 2024-02 —
closed advertisements still declared.* So the site's total is printed
beside the count as what it is — a second source that REFUTES «sitemap =
board» — and nothing here calls the sitemap the board's size. `<lastmod>` is
a real per-entry date (100 distinct values in one file), so `--since`
narrows on it; the advertisement's own `validThrough` is on the page.

EVERY ADVERTISEMENT CARRIES A JobPosting IN JSON-LD — title, hiring
organisation, `datePosted`, `validThrough`, `employmentType`, `industry`,
`occupationalCategory`, `jobLocation[]` with `addressRegion`, `baseSalary`
in JPY (min/max), `workHours`, `jobBenefits`, `experienceRequirements`,
`description` as HTML inside the JSON. **Nothing is translated: the adapter
emits the Japanese the site publishes**, UTF-8, tags stripped from the
prose fields.

THE RULES refuse 47 paths to `*` (`/a/`, `/b/`, `/entry/` …), none of them the
sitemap or `/jobinfo-…/`; no `Crawl-delay`; `certain: True`, read twice. The
transport served the root (214 kB, the title in Japanese) and every file
tried. Measured 2026-09-11 18:37–18:44 UTC.
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

BASE = "https://tenshoku.mynavi.jp"
INDEX = BASE + "/sitemap/sitemap_index.xml"
JOB_FILE = re.compile(r"/sitemap/sitemap_jobs_(\d+)\.xml\.gz$")
AD_RE = re.compile(r"^https://tenshoku\.mynavi\.jp/jobinfo-(\d+)-(\d+)-(\d+)-(\d+)/$")
ENTRY_RE = re.compile(r"<loc>([^<]+)</loc>\s*(?:<lastmod>([^<]*)</lastmod>)?")
TOTAL_RE = re.compile(r"掲載求人数\s*([\d,]+)\s*件")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[mynavi] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace("tenshoku.mynavi.jp", own=2.0)   # no Crawl-delay declared; 2 s is ours


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "ja,en;q=0.5",
    })
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            raw = r.read()
            # The job files come as `Content-Encoding: x-gzip` — or as a
            # `.gz` body with no such header — and a gzip stream decoded as
            # text is 118 502 replacement characters and zero <loc>. Undone
            # here, by the header or by the magic bytes, as fetch-body does.
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


def site_total():
    """`掲載求人数 N 件` off the home page, or None — the site's own count."""
    code, body = get(BASE + "/")
    if code != 200:
        return None
    # tags sit between the label and the figure; the visible text has none
    m = TOTAL_RE.search(re.sub(r"\s+", " ", text(body)))
    return int(m.group(1).replace(",", "")) if m else None


def cmd_sitemap(a):
    code, body = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}", EXIT_PARTIAL)
    children = sitemap_locs(body)
    files = sorted((u for u in children if JOB_FILE.search(u)),
                   key=lambda u: int(JOB_FILE.search(u).group(1)))
    if not files:
        die(f"{INDEX}: {len(children)} children and no `sitemap_jobs_NN.xml.gz` — the job "
            f"files moved; read the index before believing a zero.", EXIT_PARTIAL)
    take = files[:a.files] if a.files else files
    ids, raw, unmatched, per_file = {}, 0, 0, []
    for f in take:
        code, xml = get(f)
        if code != 200:
            die(f"{f}: HTTP {code}", EXIT_PARTIAL)
        n = 0
        for loc, lastmod in ENTRY_RE.findall(xml):
            raw += 1
            n += 1
            m = AD_RE.match(loc.strip())
            if not m:
                unmatched += 1
                continue
            ident = m.group(1)
            cur = ids.get(ident)
            if cur is None or (lastmod or "") > cur["lastmod"]:
                ids[ident] = {"url": loc.strip(), "lastmod": lastmod or "", "variants": (cur["variants"] if cur else 0) + 1}
            else:
                cur["variants"] += 1
        per_file.append(n)
        if n == 0:
            die(empty_first_page("mynavi", xml, "<loc>", where=f), EXIT_PARTIAL)
    rows = [{"source": "mynavi", "country": "JP", "ledger_id": f"mynavi:{i}", "id": i,
             "url": v["url"], "lastmod": v["lastmod"][:10] or None, "variants": v["variants"]}
            for i, v in ids.items()]
    if a.since:
        before = len(rows)
        rows = [r for r in rows if r["lastmod"] and r["lastmod"] >= a.since]
        note(f"--since {a.since}: {len(rows)} of {before} distinct ids have a `<lastmod>` on or after it.")
    rows.sort(key=lambda r: r["lastmod"] or "", reverse=True)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{raw} <loc> in {len(take)} of {len(files)} job file(s) ({'+'.join(map(str, per_file))}); "
         f"{raw - unmatched} matched the advertisement shape and {unmatched} did not; "
         f"**{len(ids)} distinct advertisement id(s)** — up to "
         f"{max((v['variants'] for v in ids.values()), default=0)} URL variants of one.")
    if a.no_site_total:
        note("site total not read (--no-site-total).")
        return
    stated = site_total()
    if stated is None:
        note("the home page states no 掲載求人数 this run — no second source.")
        return
    note(f"site states 掲載求人数 {stated:,} 件 on its home page".replace(",", " ")
         + (f" — the sitemap's {len(ids)} distinct ids are {'MORE' if len(ids) > stated else 'fewer'} "
            f"than that by {abs(len(ids) - stated)}"
            + (": the sitemap keeps ids whose `<lastmod>` goes back years — closed "
               "advertisements still declared — so it is a SUPERSET of the board, and "
               "this count is not the board's size."
               if len(ids) > stated else
               f" — {len(take)} of {len(files)} files were read; raise --files."
               if a.files and len(take) < len(files) else
               ". **A second source, and it does not confirm the sitemap: the two count different things.**")
            if len(ids) != stated else " — and the sitemap's distinct ids agree."))


def _money(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/jobinfo-<id>-<a>-<b>-<c>/")
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
    regions = [((l.get("address") or {}).get("addressRegion")) for l in locs if isinstance(l, dict)]
    sal = d.get("baseSalary") or {}
    val = sal.get("value") if isinstance(sal, dict) else {}
    print(json.dumps({
        "source": "mynavi", "country": "JP",
        "ledger_id": f"mynavi:{ident}", "id": ident, "url": a.url,
        "title": d.get("title"),
        "employer": org.get("name") if isinstance(org, dict) else None,
        "employer_url": org.get("sameAs") if isinstance(org, dict) else None,
        "employment_type": d.get("employmentType"),
        "industry": d.get("industry"),
        "occupation": d.get("occupationalCategory"),
        # one Place per office; the same prefecture repeats — deduplicated, order kept
        "regions": list(dict.fromkeys(r for r in regions if r)),
        "posted": d.get("datePosted"),
        "valid_through": d.get("validThrough"),
        "salary_currency": sal.get("currency") if isinstance(sal, dict) else None,
        "salary_min": _money((val or {}).get("minValue")) if isinstance(val, dict) else None,
        "salary_max": _money((val or {}).get("maxValue")) if isinstance(val, dict) else None,
        "salary_unit": (val or {}).get("unitText") if isinstance(val, dict) else None,
        "work_hours": text(d.get("workHours")),
        "benefits": text(d.get("jobBenefits")),
        "experience_requirements": text(d.get("experienceRequirements")),
        "description": text(d.get("description"))[:20000],
        "language": "ja",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="マイナビ転職 — Japan, through the job sitemaps it declares and the JSON-LD its pages carry.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="distinct advertisement ids from the job sitemaps — 1 request per file (10 MB each) + the index")
    s.add_argument("--files", type=int, help="read only the first N job files (7 exist)")
    s.add_argument("--since", help="keep ids whose <lastmod> is on or after YYYY-MM-DD")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true", help="skip the home-page count (one request)")
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one advertisement, from its JSON-LD — Japanese as published")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
