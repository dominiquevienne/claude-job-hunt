#!/usr/bin/env python3
"""Profession.hu — Hungary's first board, enumerated by 23 sector sitemaps; the listing's own «N db» as the witness, and the `/en/` twins never read because the rules refuse them.

  profession.py list [--limit N] [--no-site-total]
  profession.py ad --url <advertisement URL>

TWENTY-THREE SECTOR FILES, ONE ID, AND A REFUSED LANGUAGE

`sitemap-listings-index-hu.xml` names 23 sector files (`admin`, `banking`
… `skilled`, `ssc`); together they held 12 427 `<loc>` on 2026-09-13 17:20
UTC — **12 415 distinct advertisements** `/allas/<slug>-<id>` (ten sit in
two sectors, so the adapter dedups on the id) and **2 `/en/advertisement/…`
URLs, which the adapter never reads: `Disallow: /en/` is written to `*`**,
and a refusal read in the rules is honoured by every route. They are
counted apart, and they are not emitted. *The site's `robots.txt` refuses
45 paths — accounts, applications, the English version, its own PDFs — and
names no AI agent; `certain: True`, no `Crawl-delay` (1 s is ours).*

THE WITNESS is the listing page's own title: `/allasok` → «Állások, munkák
és állásajánlatok - **19329 db** - 2026 Szeptember» (also «19329 állás» in
the body). On 2026-09-13 the sitemaps carried 12 415 against 19 329
stated: **6 914 short**, and the adapter prints both — «12 415 emitted,
site states 19 329 — 6 914 short» — and never corrects one by the other.
*Whether the 6 914 are advertisements the sitemaps leave out, or a count
that includes what the sitemaps split, is a question for the listing walk
that this adapter does not do (it never reads `/allasok?page=`).*

THE ADVERTISEMENT PAGE carries a `JobPosting` in JSON-LD (`@id` …
`/JobPosting/<id>`, `title`, `description`, `datePosted`, `validThrough`,
`employmentType` in Hungarian — «Alkalmazotti jogviszony» —,
`hiringOrganization` with its own `@id` `/Organization/<orgId>` — the
EMPLOYER's id, kept apart —, `occupationalCategory`, `jobLocationType`
`TELECOMMUTE` when remote, `applicantLocationRequirements`; **`validThrough` is the read time plus
thirty days** — 19:21:22 then 19:23:12 on two reads two minutes apart —
a formula, kept as published and never offered as an expiry) — and **no
`jobLocation`**: the place is microdata on the page, `itemprop=
"addressLocality"` under «Munkavégzés helye», with a mode («Hibrid») before
the separator. No salary. No `mailto:`, no `tel:` — nothing of the kind is
read. Measured 2026-09-13 17:20 UTC (#359; page Hongrie of 2026-09-01:
11 451).
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
from _sitemap import count as sitemap_count, count_says, locs as sitemap_locs
from _ua import UA

HOST = "www.profession.hu"
BASE = "https://" + HOST
INDEX = BASE + "/sitemap-listings-index-hu.xml"
LISTING = BASE + "/allasok"
AD_RE = re.compile(r"^https://www\.profession\.hu/allas/([a-z0-9-]+)-(\d+)/?$")
EN_RE = re.compile(r"^https://www\.profession\.hu/en/")
STATED_RE = re.compile(r"<title>[^<]*?-\s*(\d[\d\s.]*)\s*db\s*-", re.S)
PLACE_RE = re.compile(r'itemprop="addressLocality"[^>]*>\s*(.*?)\s*<', re.S)
MODE_RE = re.compile(r'class="[^"]*address-data[^"]*"[^>]*>\s*(.*?)\s*<span class="location-separator"', re.S)

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[profession] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=1.0)   # no Crawl-delay declared; 1 s between the 23 files is ours


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.5", "Accept-Language": "hu,en;q=0.5"})
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
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", htmlmod.unescape(markup)).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def entry(url, lastmod, sector):
    m = AD_RE.match(url)
    if not m:
        return None
    return {"source": "profession", "country": "HU", "ledger_id": f"profession:{m.group(2)}", "id": m.group(2), "url": url,
            "slug": m.group(1), "sectors": [sector], "lastmod": lastmod}


def cmd_list(a):
    code, body = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}", EXIT_PARTIAL)
    files = [u for u in sitemap_locs(body) if "/sitemap-listings-" in u]
    if not files:
        die(f"{INDEX}: no sitemap-listings-<sector>-hu.xml — {count_says(body)}", EXIT_PARTIAL)
    rows, by_id, english, locs_total = [], {}, 0, 0
    for f in files:
        sector = re.search(r"sitemap-listings-([a-z]+)-hu\.xml", f)
        sector = sector.group(1) if sector else f
        code, body = get(f)
        if code != 200:
            die(f"{f}: HTTP {code} — {len(files)} sector file(s), one unread: the count below would be short and is not printed.", EXIT_PARTIAL)
        c = sitemap_count(body)
        if c["locs"] != c["urls"]:
            die(f"{f}: {c['locs']} <loc> against {c['urls']} <url> — the file does not agree with itself, and no count is printed.", EXIT_PARTIAL)
        locs_total += c["locs"]
        for block in re.findall(r"<url>(.*?)</url>", body, re.S):
            m = re.search(r"<loc>\s*(.*?)\s*</loc>", block, re.S)
            if not m:
                continue
            url = htmlmod.unescape(m.group(1))
            if EN_RE.match(url):
                english += 1   # `Disallow: /en/` — listed by the sitemap, refused by the rules, never read, never emitted
                continue
            lm = re.search(r"<lastmod>\s*(.*?)\s*</lastmod>", block, re.S)
            e = entry(url, lm.group(1) if lm else None, sector)
            if not e:
                continue
            if e["id"] in by_id:
                by_id[e["id"]]["sectors"].append(sector)   # ten advertisements sit in two sectors on 2026-09-13
                continue
            by_id[e["id"]] = e
            rows.append(e)
    if not rows:
        die(f"{len(files)} sector file(s), {locs_total} <loc>, none of the shape /allas/<slug>-<id> — {count_says(body)}", EXIT_PARTIAL)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    twice = sum(1 for r in rows if len(r["sectors"]) > 1)
    note(f"{len(files)} sector file(s), {th(locs_total)} <loc>; **{th(len(rows))} distinct advertisement id(s)** ({twice} listed in two sectors), "
         f"{english} `/en/` URL(s) set aside — `Disallow: /en/` is written, so they are neither read nor emitted"
         + (f" ({a.limit} printed under --limit)" if a.limit and len(rows) > a.limit else "") + ".")
    if a.no_site_total:
        return
    code, body = get(LISTING)
    m = STATED_RE.search(body) if code == 200 else None
    if not m:
        note(f"the listing {LISTING} answers HTTP {code} and states no «N db» in its title this run — no stated figure to print beside the {th(len(rows))}.")
        return
    stated = int(re.sub(r"\D", "", m.group(1)))
    if stated == len(rows):
        note(f"{th(len(rows))} emitted, site states {th(stated)} — equal.")
    else:
        note(f"{th(len(rows))} emitted, site states {th(stated)} — {th(abs(stated - len(rows)))} " + ("short" if stated > len(rows) else "more emitted than the site states")
             + "; the sitemaps and the listing's own title are two witnesses, and neither corrects the other — the listing pages are not walked.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/allas/<slug>-<id> (and never /en/, which the rules refuse)")
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
    org_id = re.search(r"/Organization/(\d+)", str(org.get("@id") or "")) if isinstance(org, dict) else None
    et = d.get("employmentType")
    place = PLACE_RE.search(body)
    mode = MODE_RE.search(body)
    cat = d.get("occupationalCategory")
    print(json.dumps({
        "source": "profession", "country": "HU", "ledger_id": f"profession:{ident}", "id": ident, "url": a.url,
        "title": text(d.get("title") or d.get("name")),
        "employer": (text(org.get("name")) or None) if isinstance(org, dict) else None,
        # the Organization's @id is the EMPLOYER's number, kept apart from the advertisement's
        "employer_id": org_id.group(1) if org_id else None,
        "place": text(place.group(1)) if place else None,
        "work_mode": (text(mode.group(1)) or None) if mode else None,
        "remote": d.get("jobLocationType") == "TELECOMMUTE",
        "employment_type": ", ".join(et) if isinstance(et, list) else et,
        "category": ", ".join(cat) if isinstance(cat, list) else cat,
        "posted": d.get("datePosted"),
        # `validThrough` is the READ time plus thirty days — 19:21:22 then 19:23:12 on two reads two minutes apart (2026-09-13):
        # a formula, not a date the employer set; kept as published, and never offered as an expiry
        "valid_through": None, "valid_through_as_published": d.get("validThrough"),
        "description": text(d.get("description"))[:20000], "language": "hu",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Profession.hu — 23 sector sitemaps deduped on the id, the listing's own «N db» as the witness, the refused /en/ twins never read.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every advertisement in the 23 sector sitemaps — 12 415 on 2026-09-13, 24 requests at 1 s, then the listing for its count")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advertisement, from its JSON-LD and the page's place microdata")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
