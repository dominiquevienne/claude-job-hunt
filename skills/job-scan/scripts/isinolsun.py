#!/usr/bin/env python3
"""İşin Olsun — Turkey's largest blue-collar board, enumerated by two job-detail sitemaps against the root's own «N İş İlanı»; the advertisement page itself stalls for a plain client, and the adapter says so instead of pretending to read it.

  isinolsun.py list [--limit N] [--no-site-total]
  isinolsun.py ad --url <advertisement URL>      # attempts the page and REPORTS — no reader is written (see below)

TWO SITEMAPS, ONE HEX KEY, AND THE ROOT'S OWN COUNT

`robots.txt` is 66 B — `Allow: /`, one Sitemap line — and `/sitemap.xml`
names 30 files, two of them advertisements: `sitemaps/jobdetailsitemap1.xml`
(9 790 616 B, 50 000 `<loc>`) and `jobdetailsitemap2.xml` (7 432 763 B,
37 504) on 2026-09-13 17:39 UTC — **87 504 URLs of one shape**,
`/is-ilani/<slug>-0ioj<32 hex>`, every key distinct, a `lastmod` each (eight
slugs of one employer carry a literal tab — the key behind them is sound) (the
other 28 files are positions, cities, towns, companies, facets — never
read). The slug is the title and the employer run together in Turkish
(«tatli-ustasi-carmen-tatlicilik»); the adapter emits it as `slug` and
does not pretend to split it. **The witness is the root page's own «87.394
İş İlanı»** (with «16.155.987 İndirme», a download count, beside it): «87 504
emitted, site states 87 394 — 110 more emitted than the site states», printed
and never merged.

THE ADVERTISEMENT PAGE IS NOT SERVED TO A PLAIN CLIENT — measured, not
assumed. On 2026-09-13 17:41–17:47 UTC every request under `/is-ilani/…`
and `/is-ilanlari…` **stalled without a byte** — 25 s, 120 s, HEAD or GET,
under the declared identity and under curl's own name alike — while `/`,
`/robots.txt` and the sitemaps answered in 0.2–0.4 s. Nothing refused us
in writing; the page's backend simply never answers this client. So `ad
--url` **attempts the page once (30 s), and reports**: served → the status,
the size and how many `JobPosting` it carries, and that no reader exists
yet because no page was ever served to write one against; stalled → the
dated fact, exit 6. *A browser route is the next measurement, and it is a
different session's instrument.* No contact is read, by construction.

THE RULES: `Allow: /`, no agent named, no `Crawl-delay` (2 s is ours, on
a board of this size); `certain: True`. Measured 2026-09-13 17:38–17:47
UTC (#382; page Turquie of 2026-09-01: 82 407).
"""

import argparse
import html as htmlmod
import json
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _ldjson import postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _sitemap import count as sitemap_count, count_says, locs as sitemap_locs
from _ua import UA

HOST = "isinolsun.com"
BASE = "https://" + HOST
INDEX = BASE + "/sitemap.xml"
# the slug is `[^/]+?`, not `[a-z0-9-]+?`: eight URLs of one employer carry a literal TAB inside the slug (2026-09-13), and the key behind it is sound
AD_RE = re.compile(r"^https://(?:www\.)?isinolsun\.com/is-ilani/([^/]+?)-0ioj([0-9A-F]{32})/?$")
STATED_RE = re.compile(r"([\d.]+)\s*İş İlanı")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[isinolsun] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # no Crawl-delay declared; 2 s is ours — two files of 7 and 10 MB


def get(url, timeout=120):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.5", "Accept-Language": "tr,en;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (TimeoutError, socket.timeout) as e:
        return None, f"stalled: no answer in {timeout} s ({type(e).__name__})"
    except (urllib.error.URLError, OSError) as e:
        if isinstance(getattr(e, "reason", None), (TimeoutError, socket.timeout)):
            return None, f"stalled: no answer in {timeout} s ({type(e.reason).__name__})"
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", htmlmod.unescape(markup)).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def entry(url, lastmod):
    m = AD_RE.match(url)
    if not m:
        return None
    return {"source": "isinolsun", "country": "TR", "ledger_id": f"isinolsun:{m.group(2)}", "id": m.group(2), "url": url,
            "slug": m.group(1), "lastmod": lastmod}


def cmd_list(a):
    code, body = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}" if code else f"{INDEX}: {body}", EXIT_PARTIAL)
    files = [u for u in sitemap_locs(body) if "/jobdetailsitemap" in u]
    if not files:
        die(f"{INDEX}: no sitemaps/jobdetailsitemap<n>.xml in the index — {count_says(body)}", EXIT_PARTIAL)
    rows, seen, other, locs_total = [], set(), 0, 0
    for f in files:
        code, body = get(f)
        if code != 200:
            die((f"{f}: HTTP {code}" if code else f"{f}: {body}") + f" — {len(files)} job-detail file(s), one unread: the count below would be short and is not printed.", EXIT_PARTIAL)
        c = sitemap_count(body)
        if c["locs"] != c["urls"]:
            die(f"{f}: {c['locs']} <loc> against {c['urls']} <url> — the file does not agree with itself, and no count is printed.", EXIT_PARTIAL)
        locs_total += c["locs"]
        for block in re.findall(r"<url>(.*?)</url>", body, re.S):
            m = re.search(r"<loc>\s*(.*?)\s*</loc>", block, re.S)
            if not m:
                continue
            lm = re.search(r"<lastmod>\s*(.*?)\s*</lastmod>", block, re.S)
            e = entry(htmlmod.unescape(m.group(1)), lm.group(1) if lm else None)
            if not e:
                other += 1
                continue
            if e["id"] in seen:
                continue
            seen.add(e["id"])
            rows.append(e)
    if not rows:
        die(f"{len(files)} job-detail file(s), {locs_total} <loc>, none of the shape /is-ilani/<slug>-0ioj<hex> — {count_says(body)}", EXIT_PARTIAL)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{len(files)} job-detail file(s), {th(locs_total)} <loc>; **{th(len(rows))} distinct advertisement key(s)** of the shape /is-ilani/<slug>-0ioj<hex>"
         + (f", {other} of another shape set aside" if other else "") + (f" ({a.limit} printed under --limit)" if a.limit and len(rows) > a.limit else "") + ".")
    if a.no_site_total:
        return
    code, body = get(BASE + "/")
    m = STATED_RE.search(text(body)) if code == 200 else None
    if not m:
        note(f"the root answers {'HTTP ' + str(code) if code else body} and states no «N İş İlanı» this run — no stated figure to print beside the {th(len(rows))}.")
        return
    stated = int(m.group(1).replace(".", ""))
    if stated == len(rows):
        note(f"{th(len(rows))} emitted, site states {th(stated)} — equal.")
    else:
        note(f"{th(len(rows))} emitted, site states {th(stated)} — {th(abs(stated - len(rows)))} " + ("short" if stated > len(rows) else "more emitted than the site states")
             + "; the sitemaps and the root's own count are two witnesses, and neither corrects the other.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/is-ilani/<slug>-0ioj<32 hex>")
    code, body = get(a.url, timeout=a.timeout)
    if code is None:
        die(f"{a.url}: {body}. **Measured 2026-09-13 17:41–17:47 UTC: every request under /is-ilani/ stalled without a byte — 25 s, 120 s, HEAD or GET, "
            "under the declared identity and under curl's own name — while the root and the sitemaps answered in under a second. Nothing refused us in writing; "
            "the page's backend does not answer a plain client. The sitemap is the route; the page is a browser question, and no reader is written against a page never served.**", EXIT_PARTIAL)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    found = postings(body)
    die(f"{a.url}: SERVED — HTTP 200, {len(body)} characters, {len(found)} JobPosting in JSON-LD. **No reader exists yet: on 2026-09-13 no advertisement page was ever served to this "
        "client, so none was written against; this is the measurement that reopens the question — record it on the card and write the reader from the page.**", EXIT_PARTIAL)


def main():
    p = argparse.ArgumentParser(description="İşin Olsun — two job-detail sitemaps (87 504 keys on 2026-09-13) against the root's own «N İş İlanı»; the advertisement page stalls for a plain client, and `ad` reports that instead of reading.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every advertisement key in the two job-detail sitemaps — three requests of 4 KB, 10 MB and 7 MB at 2 s, then the root for its count")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="attempt one advertisement page and REPORT — served or stalled; no reader is written (the page never answered a plain client on 2026-09-13)")
    d.add_argument("--url", required=True)
    d.add_argument("--timeout", type=float, default=30)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
