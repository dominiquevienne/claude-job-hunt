#!/usr/bin/env python3
"""Discover job ads on welcometothejungle.com — sitemap side only.

**This script does half the job, and the half it does not do needs the user's
browser session.** Read `shared/boards/wttj.md` before using it.

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
import urllib.parse
import urllib.request

from _decode import decode_body
from _robots import allowed as robots_allowed

BASE = "https://www.welcometothejungle.com"
INDEX = BASE + "/sitemaps/index.xml.gz"
from _ua import UA
# Reads the plain `<loc>https://…</loc>` and the CDATA-wrapped form both, and
# no longer requires `</loc>` to follow the URL directly — that extra
# strictness made this the tightest of the four naive readers, failing on a
# merely pretty-printed sitemap where the looser three still worked. hays.fr
# serves the CDATA form, where the first non-space character after the tag is
# `<` and the strict pattern yields 0 URLs from a valid 2.37 MB file.
# Issue #55.
LOC_RE = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?\s*([^\s\]<]+)")
MOD_RE = re.compile(r"<lastmod>([^<]*)")
# Taken block by block rather than as one `<loc>…<lastmod>` pattern: adecco.py
# records that its sitemap writes those two tags in the reverse order, and a
# regex that fixes an order matches nothing at all when the order changes.
URL_BLOCK_RE = re.compile(r"(?s)<url>(.*?)</url>")
SITEMAP_BLOCK_RE = re.compile(r"(?s)<sitemap>(.*?)</sitemap>")
# /fr/companies/<company>/jobs/<slug>[_<city>][_<id>]
AD_RE = re.compile(r"^/(fr|en)/companies/([^/]+)/jobs/(.+)$")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def _robots_gate(url, tag, exit_code=7):
    """Ask before fetching — per host and **per path**. Issues #100, #101.

    `verdict()` answers *is this host closed in one block*. **A site that
    refuses its ad path while leaving its root open passes that and refuses
    every advertisement** — `empleate.gob.hn` does exactly that, closing
    `/Vacantes/` to `User-agent: *` with `/` absent.

    It sits **inside the fetch function**, so every request is covered rather
    than the first one, and a refusal **stops the command** with exit 7 and the
    module's own words. **This adapter decides nothing about what a refusal
    means** — deciding is what turns a check into a decoration.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return None
    a = robots_allowed(parts.netloc, parts.path or "/")
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", exit_code)
    if a.get("requested_host") and a["host"] != a["requested_host"]:
        print(f"[wttj] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts. A platform that has "
              f"been renamed reaches an adapter this way before it reaches it "
              f"as a rename.", file=__import__("sys").stderr)
    return a



def get(url, retries=2):
    _robots_gate(url, 'wttj')
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
                raw, hdrs = r.read(), r.headers
        except urllib.error.HTTPError as e:
            die(f"welcometothejungle returned HTTP {e.code} for {url}")
        except Exception as e:  # noqa: BLE001 - network shape varies
            if attempt == retries:
                die(f"could not reach welcometothejungle: {e}")
            time.sleep(2.0)
            continue
        try:
            return decode_body(gzip.decompress(raw), hdrs)[0]
        except Exception:  # noqa: BLE001 - not every file is gzipped
            return decode_body(raw, hdrs)[0]
    return ""


def job_sitemaps():
    idx = get(INDEX)
    everything = LOC_RE.findall(idx)
    if not everything:
        die(_zero(INDEX, len(idx), len(SITEMAP_BLOCK_RE.findall(idx)),
                   "<sitemap>"))
    out = [u for u in everything if "job-listings" in u]
    if not out:
        die("the sitemap index declared no job-listings file. It listed: "
            + ", ".join(u.rsplit("/", 1)[-1] for u in everything[:8]))
    return sorted(out)


def _zero(url, n, blocks=0, container="<url>"):
    """The message a silent zero deserves.

    A `.gz` read as text yields no `<loc>` from a perfectly healthy file, and
    the run then reports "0 ads" — a 200, a plausible body, the wrong content,
    nothing raised. A sibling session met exactly this on another board's
    sitemap the same week. So zero URLs is treated as a failure to read, never
    as an empty board: an empty board would still be a `<urlset>` with tags in
    it, and the caller is told which of the two it is.

    The block count settles which. **Zero `<loc>` inside a non-zero number of
    `<url>` blocks cannot occur in a valid sitemap**, so it names the reader as
    the fault rather than leaving the caller to guess. That arithmetic — not
    the pattern — is what exposed the CDATA trap on hays.fr. `<lastmod>` cannot
    play the same role: the sitemaps.org schema makes it optional, so a valid
    file may carry none. Issue #55.
    """
    if blocks:
        return (f"{url} gave zero URLs out of {blocks} {container} blocks in "
                f"{n} characters. That combination cannot occur in a valid "
                "sitemap: the reader is at fault, not the board. Check "
                f"{container}'s child <loc> for a wrapper — CDATA, say — that "
                "this extractor does not handle.")
    return (f"{url} parsed to zero URLs and zero {container} blocks out of "
            f"{n} characters. That is what a gzip layer read as text looks "
            "like — a healthy file reporting nothing. Check the decompression "
            "before believing the board is empty. If the body really is an "
            "empty <urlset/>, say so; do not report it as a count.")


def entries(url):
    """(path, lastmod) for each ad in one sitemap file."""
    page = get(url)
    blocks = URL_BLOCK_RE.findall(page)
    found = []
    for b in blocks:
        loc = LOC_RE.search(b)
        if not loc:
            continue
        mod = MOD_RE.search(b)
        found.append((loc.group(1), mod.group(1) if mod else None))
    if not found:
        die(_zero(url, len(page), len(blocks)))
    for loc, mod in found:
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
