#!/usr/bin/env python3
"""Discover job ads on welcometothejungle.com — sitemap side only.

**This script does half the job, and the half it does not do needs the user's
Chrome.** Read `shared/boards/wttj.md` before using it.

  discovery  →  this script, plain HTTP, sanctioned by robots.txt
  reading    →  the browser, because every HTML page answers a WAF challenge

**Every HTML page on this site answers `HTTP 202` with the header
`x-amzn-waf-action: challenge`** — an AWS WAF challenge. Not a 403, not a block
page: a 2xx status with a 2 450-byte body that contains no ad. Slowing down does
not help; measured, one request every 6 s and one every 12 s were challenged 10
times out of 10. So this script **never requests an ad page**, and would be
lying if it did.

What it does instead is the part the site invites: `robots.txt` publishes a
sitemap index, and the sitemaps are served to a plain client without challenge.
Nine files of 10 000 URLs, **88 222 ads**, each with a real per-ad `lastmod`.

  GET /robots.txt                              → Sitemap: …/sitemaps/index.xml.gz
  GET /sitemaps/index.xml.gz                   → 24 sitemaps, 9 of job listings
  GET /sitemaps/job-listings.<n>.xml.gz        → 10 000 ad URLs + lastmod

Usage:
  wttj.py sitemaps
  wttj.py discover --locale fr --since 2026-08-25
  wttj.py discover --company carrefour
  wttj.py companies --top 30

Output: one JSON object per line — a URL and what can be known without
fetching it. Hand those URLs to the browser step.
"""

import argparse
import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.request

BASE = "https://www.welcometothejungle.com"
INDEX = BASE + "/sitemaps/index.xml.gz"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

LOC_RE = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")
URL_ENTRY_RE = re.compile(
    r"<url>\s*<loc>\s*([^<\s]+)\s*</loc>(?:\s*<lastmod>([^<]*)</lastmod>)?",
    re.S)
# /fr/companies/<company>/jobs/<slug>[_<city>][_<id>]
AD_RE = re.compile(r"^/(fr|en)/companies/([^/]+)/jobs/(.+)$")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def get(url, retries=2):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Encoding": "gzip",
        "Accept-Language": "fr-FR,fr;q=0.9",
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                waf = r.headers.get("x-amzn-waf-action")
                if waf:
                    # The signature this whole adapter is shaped around. A 2xx
                    # status and a body that is not the thing you asked for.
                    die(f"the WAF challenged this request ({url}): "
                        f"HTTP {r.status}, x-amzn-waf-action: {waf}. "
                        "The sitemaps are normally served without challenge — "
                        "if this persists, the site has tightened and the "
                        "discovery half needs the browser too.")
                raw = r.read()
        except urllib.error.HTTPError as e:
            die(f"welcometothejungle returned HTTP {e.code} for {url}")
        except Exception as e:  # noqa: BLE001 - network shape varies
            if attempt == retries:
                die(f"could not reach welcometothejungle: {e}")
            time.sleep(2.0)
            continue
        try:
            return gzip.decompress(raw).decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001 - not every file is gzipped
            return raw.decode("utf-8", errors="replace")
    return ""


def job_sitemaps():
    idx = get(INDEX)
    out = [u for u in LOC_RE.findall(idx) if "job-listings" in u]
    if not out:
        die("the sitemap index declared no job-listings file. It listed: "
            + ", ".join(u.rsplit("/", 1)[-1] for u in LOC_RE.findall(idx)[:8]))
    return sorted(out)


def entries(url):
    """(path, lastmod) for each ad in one sitemap file."""
    for loc, mod in URL_ENTRY_RE.findall(get(url)):
        yield loc.replace(BASE, ""), (mod or "").strip() or None


def parse(path):
    m = AD_RE.match(path)
    if not m:
        return None
    locale, company, tail = m.groups()
    return {
        "url": BASE + path,
        "locale": locale,
        # The company is a path segment, so it is known before any fetch —
        # unusually, this board names the employer in the URL itself.
        "company_slug": company,
        "slug": tail,
        # Deliberately NOT a city. The tail is `<job>_<city>_<id>` on some ads
        # and `<job>_<city>` on others, and `_` also occurs inside the job
        # slug, so splitting it guesses. Measured on 10 000 URLs: 6 576 end in
        # something that looks like an id and 3 424 do not, and no rule
        # separates them. The location comes from the ad page, in the browser.
        "city_from_url": None,
    }


def cmd_sitemaps(_a):
    for u in job_sitemaps():
        print(u)


def cmd_discover(a):
    files = job_sitemaps()
    if a.file is not None:
        if not 0 <= a.file < len(files):
            die(f"--file must be between 0 and {len(files) - 1}")
        files = [files[a.file]]
    seen, kept = 0, 0
    for f in files:
        for path, mod in entries(f):
            seen += 1
            row = parse(path)
            if row is None:
                continue
            if a.locale and row["locale"] != a.locale:
                continue
            if a.company and row["company_slug"] != a.company:
                continue
            if a.since and (mod or "") < a.since:
                continue
            row["lastmod"] = mod
            row["ledger_id"] = f"wttj:{row['company_slug']}/{row['slug']}"
            print(json.dumps(row, ensure_ascii=False))
            kept += 1
            if a.limit and kept >= a.limit:
                print(f"[wttj] stopped at --limit {a.limit}", file=sys.stderr)
                _summary(kept, seen)
                return
        time.sleep(a.delay)
    _summary(kept, seen)


def _summary(kept, seen):
    print(f"[wttj] {kept} ads discovered out of {seen} in the sitemaps",
          file=sys.stderr)
    print("[wttj] these are URLs, not ads. Reading them needs the user's "
          "Chrome — see shared/boards/wttj.md. A locale is NOT a country: "
          "/fr/ ads were measured in Cologne, Rio de Janeiro and Martinique.",
          file=sys.stderr)


def cmd_companies(a):
    counts = {}
    files = job_sitemaps()
    if a.file is not None:
        files = [files[a.file]]
    for f in files:
        for path, _mod in entries(f):
            row = parse(path)
            if row is None or (a.locale and row["locale"] != a.locale):
                continue
            counts[row["company_slug"]] = counts.get(row["company_slug"], 0) + 1
        time.sleep(a.delay)
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:a.top]
    for slug, n in top:
        print(json.dumps({"company_slug": slug, "ads": n,
                          "url": f"{BASE}/fr/companies/{slug}/jobs"},
                         ensure_ascii=False))
    print(f"[wttj] {len(counts)} companies seen", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sitemaps", help="the job-listing sitemap files").set_defaults(
        func=cmd_sitemaps)

    d = sub.add_parser("discover", help="ad URLs from the sitemaps")
    d.add_argument("--locale", choices=["fr", "en"],
                   help="the URL's language — NOT the job's country")
    d.add_argument("--company", help="company slug, e.g. carrefour")
    d.add_argument("--since", help="keep lastmod >= this ISO date")
    d.add_argument("--file", type=int, help="one sitemap file, 0-based")
    d.add_argument("--limit", type=int)
    d.add_argument("--delay", type=float, default=1.0)
    d.set_defaults(func=cmd_discover)

    c = sub.add_parser("companies", help="who is hiring, and how much")
    c.add_argument("--locale", choices=["fr", "en"], default="fr")
    c.add_argument("--top", type=int, default=30)
    c.add_argument("--file", type=int)
    c.add_argument("--delay", type=float, default=1.0)
    c.set_defaults(func=cmd_companies)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
