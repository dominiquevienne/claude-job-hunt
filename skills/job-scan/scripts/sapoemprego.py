#!/usr/bin/env python3
"""SAPO Emprego (`emprego.sapo.pt`) — Portugal's general board, read through the offer sitemap its rules declare and the JobPosting every offer page carries; the search route is refused and captcha-gated, and never taken.

  sapoemprego.py sitemap [--since YYYY-MM-DD] [--limit N] [--no-site-total]
  sapoemprego.py ad --url <offer URL>

THE ROUTE IS THE SITEMAP; THE COUNT IS ON THE OPEN LISTING PAGE

`robots.txt` allows `/offers` and `/offers/` and **refuses `/offers/search`**
— the POST the listing's own app makes, and the one its search form guards
with a captcha (`offers.search.validation`, `g-recaptcha-response`). Neither
is touched. `offers.xml` (declared by the index) held 22 890
`/offers/<canonical>?id=<uuid>` on 2026-09-13 10:3x UTC, each with a
`<lastmod>` (15 381 in September, 7 489 in August — an active set,
`changefreq: always`). The open page `/offers` server-embeds its first rows
and a `pagination` prop — `{"total": 9999, "page": 1, "size": 9,
"offers_total": 23555}` — and **`offers_total` is the count the site states**;
the adapter prints it beside the file's: «22 890 emitted, site states 23 555 —
665 short». `total: 9999` is a page-count cap, not a count.

THE ID is the `?id=<uuid>` on every address — the canonical slug is not
unique (the same job posted twice carries two uuids and one slug). Every
offer page carries a JobPosting in JSON-LD: title, description (HTML),
datePosted, validThrough, industry, employmentType, jobLocation (locality,
region, PT), hiringOrganization, url. **No salary field on the page read**.

THE HOST RATE-LIMITS HARD: the third request in ten seconds answered
`429 Too Many Requests` (nginx, 162 B) on 2026-09-13 10:18 UTC, and a 429 is
a refusal that asks for less, not more — this adapter spaces 5 s and stops
on a 429 without retrying. Measured 2026-09-13 10:18–10:4x UTC, every
fetch under the declared identity, the guard on the exact path first.
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

BASE = "https://emprego.sapo.pt"
INDEX = BASE + "/sitemap.xml"
OFFERS_XML = BASE + "/offers.xml"
LISTING = BASE + "/offers"
AD_RE = re.compile(r"^https://emprego\.sapo\.pt/offers/([^/?#]+)\?id=([0-9a-f-]{36})$")
PAGINATION_RE = re.compile(r":pagination='(\{[^']*\})'")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[sapo-emprego] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace("emprego.sapo.pt", own=5.0)   # no Crawl-delay declared; the host answered 429 at three requests in ten seconds


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "pt,en;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        if e.code == 429:
            # a refusal that asks for less: stop, say so, do not retry
            die(f"{url}: HTTP 429 — the host asks for fewer requests; nothing is retried.", EXIT_REFUSED)
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    """Thousands with a space — the repo's figure style."""
    return f"{n:,}".replace(",", " ")


def site_count(body):
    """`offers_total` from the `:pagination` prop the open listing page embeds — the site's own count — or None."""
    m = PAGINATION_RE.search(body or "")
    if not m:
        return None
    try:
        d = json.loads(htmlmod.unescape(m.group(1)))
    except ValueError:
        return None
    v = d.get("offers_total")
    return int(v) if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()) else None


def entries(xml):
    out = []
    for m in re.finditer(r"(?is)<url>\s*<loc>\s*(?:<!\[CDATA\[)?\s*([^<\]\s]+)\s*(?:\]\]>)?\s*</loc>(.*?)</url>", xml):
        loc = htmlmod.unescape(m.group(1).strip())
        am = AD_RE.match(loc)
        if not am:
            continue
        lm = re.search(r"<lastmod>\s*([^<\s]+)\s*</lastmod>", m.group(2))
        out.append((am.group(2), am.group(1), loc, lm.group(1)[:10] if lm else None))
    return out


def cmd_sitemap(a):
    code, body = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}", EXIT_PARTIAL)
    if OFFERS_XML not in sitemap_locs(body):
        die(f"{INDEX} does not declare {OFFERS_XML} — the offer file moved; read the index before believing a zero.", EXIT_PARTIAL)
    code, xml = get(OFFERS_XML)
    if code != 200:
        die(f"{OFFERS_XML}: HTTP {code}", EXIT_PARTIAL)
    raw = len(sitemap_locs(xml))
    es = entries(xml)
    if raw == 0:
        die(empty_first_page("sapo-emprego", xml, "<loc>", where=OFFERS_XML), EXIT_PARTIAL)
    if not es:
        die(f"{OFFERS_XML}: {th(raw)} <loc> and none of the shape /offers/<canonical>?id=<uuid> — the address shape moved.", EXIT_PARTIAL)
    rows, seen, undated, slugs = [], set(), 0, {}
    for uid, slug, url, lastmod in es:
        if uid in seen:
            continue
        seen.add(uid)
        slugs[slug] = slugs.get(slug, 0) + 1
        if lastmod is None:
            undated += 1
        if a.since and (lastmod is None or lastmod < a.since):
            continue
        rows.append({"source": "sapo-emprego", "country": "PT", "ledger_id": f"sapo-emprego:{uid}",
                     "id": uid, "canonical": slug, "url": url, "lastmod": lastmod})
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    dup = sum(1 for v in slugs.values() if v > 1)
    since = f" dated on or after {a.since}" if a.since else ""
    note(f"{th(raw)} <loc> in offers.xml; **{th(len(seen))} distinct offer id(s)** (uuid), {th(len(slugs))} distinct canonical slugs "
         f"({th(dup)} slugs carried by more than one id — the slug is not the key), {th(undated)} without <lastmod>; {th(len(rows))} emitted{since}.")
    if a.no_site_total:
        return
    code, page = get(LISTING)
    stated = site_count(page) if code == 200 else None
    if stated is None:
        note(f"{LISTING} states no `offers_total` this run (HTTP {code}) — no second source.")
        return
    n = len(seen)
    if stated == n:
        note(f"{th(n)} emitted, site states {th(stated)} (`offers_total` on {LISTING}) — equal.")
    else:
        note(f"{th(n)} emitted, site states {th(stated)} (`offers_total` on {LISTING}) — {th(abs(stated - n))} "
             + ("short" if stated > n else "more in the sitemap than the site states")
             + "; the listing's search is refused by the rules and captcha-gated, so the file is what a reader can reach.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an offer address — expected {BASE}/offers/<canonical>?id=<uuid>")
    slug, uid = m.group(1), m.group(2)
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
    loc = d.get("jobLocation") or {}
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
    et = d.get("employmentType")
    print(json.dumps({
        "source": "sapo-emprego", "country": "PT", "ledger_id": f"sapo-emprego:{uid}", "id": uid, "canonical": slug, "url": a.url,
        "title": text(d.get("title")),
        "employer": org.get("name") if isinstance(org, dict) else None,
        "employment_type": et if isinstance(et, list) else ([et] if et else []),
        "city": addr.get("addressLocality"), "region": addr.get("addressRegion"), "country_code": addr.get("addressCountry"),
        "industry": d.get("industry"),
        "posted": d.get("datePosted"), "valid_through": d.get("validThrough"),
        # no salary field in the JobPosting read; nothing invented
        "description": text(d.get("description"))[:20000], "language": "pt",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="SAPO Emprego — through the offer sitemap it declares and the JSON-LD its pages carry; the refused search is never taken.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="distinct offer ids with <lastmod> — 2 requests, 3 with the listing's stated count; 5 s apart")
    s.add_argument("--since", help="YYYY-MM-DD, on the file's <lastmod>")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one offer, from its JSON-LD")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
