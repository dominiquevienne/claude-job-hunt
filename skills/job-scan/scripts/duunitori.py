#!/usr/bin/env python3
"""Duunitori — Finland's first private board, which names `Claude-User` to let it in where `*` is refused; 92 job sitemap pages against the listing's own «Löysimme N työpaikkaa».

  duunitori.py list [--pages N] [--limit N] [--no-site-total]
  duunitori.py ad --url <advertisement URL>

A FILE THAT REFUSES EVERYONE AND NAMES US TO LET US IN

`robots.txt` (8 576 B) opens with `User-agent: *` / `Disallow: /` — the
site is closed to any unnamed client — then names sixteen agents one by
one, each with `Disallow:` (empty: allowed) and eighteen refused paths
(`/api/`, the salary facets, the favourite/report/similar actions under
an advertisement, `/health`). **`Claude-User` is one of the sixteen**, next
to Googlebot, Bingbot, ChatGPT-User and GPTBot: the guard answers
`claude-user`, the plugin presents itself under that name (§2 quater, the
05.09 decision: if a token is permitted, that is the one we use), and
`certain: True`. *The page Finlande of 2026-08-31 saw a Cloudflare challenge
on the rules file itself; on 2026-09-13 the file is served in 0.2 s.* No
`Crawl-delay` (1 s is ours).

THE SITEMAP: `/sitemap.xml` is an index of 1 300-odd files by type;
**`sitemap-jobentry.xml?p=1..92`** are the advertisements — 200 `<loc>` a
page, 98 on the last, **18 298 slots for 16 152 distinct ids** on
2026-09-13 18:05–18:07 UTC — **the paging is not a partition**: two
consecutive pages fetched seconds apart share 56–61 of their 200 URLs, so
~12 % of the slots repeat and as many advertisements may fall between
two pages; the adapter says how many repeated — all of the shape
`/tyopaikat/tyo/<slug>-<token>-<id>` (the token varies — `sdsuu`, `scsom`,
`srs-k` — and has no fixed shape: the id is the key, the slug the whole stem), a `lastmod` each. The adapter walks
the pages at 1 s; `--pages` bounds the walk and says so.

THE WITNESS: `/tyopaikat` states «Löysimme **18 302** työpaikkaa, joista
5 993 on julkaistu viimeisen …» and pages to `?sivu=916` (20 a page).
«16 152 emitted, site states 18 302 — 2 150 short», printed and never merged
(the gap is the paging's, not the listing's);
the second figure (published in the last week) is not a total and is not
read.

THE ADVERTISEMENT PAGE carries a `JobPosting` in JSON-LD — `title` is the
**normalised occupation** («harjoittelija» for «EY Trainee Program»), so
the title is the page's `<h1>` and the JSON-LD's goes to `occupation`;
`hiringOrganization.name` (lower-cased by the site — «ernst & young»),
`datePosted`, `validThrough` (the page's own «Päättyy 20.9.», not a
formula: 2026-09-20 on both), `employmentType`, `jobLocation.address`
(`addressLocality`, `addressCountry`), `description` (HTML). **The
description can carry a recruiter's address in its prose («contact EY's
recruitment team at …@fi.ey.com»): every e-mail address is redacted from
the emitted text**, and the page's `mailto:` is never read. No salary.

Measured 2026-09-13 18:02–18:0x UTC (#374; page Finlande of 2026-08-31).
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

HOST = "duunitori.fi"
BASE = "https://" + HOST
INDEX = BASE + "/sitemap.xml"
LISTING = BASE + "/tyopaikat"
JOBENTRY_RE = re.compile(r"^https://duunitori\.fi/sitemap-jobentry\.xml(?:\?p=(\d+))?$")
# the stem carries a source token before the id — `sdsuu`, `scsom`, `srs-k` — of no fixed shape: the id is the trailing number, the slug is the whole stem
AD_RE = re.compile(r"^https://duunitori\.fi/tyopaikat/tyo/([^/?#]+)-(\d+)/?$")
STATED_RE = re.compile(r"Löysimme\s+([\d\s\xa0]+?)\s*työpaikkaa")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[duunitori] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=1.0)   # no Crawl-delay declared to Claude-User; 1 s between the 92 pages is ours


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.5", "Accept-Language": "fi,en;q=0.5"})
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


def redact(s):
    """A recruiter's address in the prose of a description is a contact — it is not emitted."""
    return EMAIL_RE.sub("[e-mail withheld]", s or "")


def entry(url, lastmod):
    m = AD_RE.match(url)
    if not m:
        return None
    return {"source": "duunitori", "country": "FI", "ledger_id": f"duunitori:{m.group(2)}", "id": m.group(2), "url": url,
            "slug": m.group(1), "lastmod": lastmod}


def cmd_list(a):
    code, body = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}", EXIT_PARTIAL)
    pages = sorted({int(m.group(1) or 1) for m in (JOBENTRY_RE.match(u) for u in sitemap_locs(body)) if m})
    if not pages:
        die(f"{INDEX}: no sitemap-jobentry.xml in the index — {count_says(body)}", EXIT_PARTIAL)
    last = pages[-1]
    walk = [p for p in pages if not a.pages or p <= a.pages]
    rows, seen, other, repeated, locs_total = [], set(), 0, 0, 0
    for p in walk:
        url = INDEX.replace("sitemap.xml", "sitemap-jobentry.xml") + (f"?p={p}" if p > 1 else "")
        code, body = get(url)
        if code != 200:
            die(f"{url}: HTTP {code} — page {p} of {last}: the count below would be short and is not printed.", EXIT_PARTIAL)
        c = sitemap_count(body)
        if c["locs"] != c["urls"]:
            die(f"{url}: {c['locs']} <loc> against {c['urls']} <url> — the file does not agree with itself, and no count is printed.", EXIT_PARTIAL)
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
                repeated += 1   # the same URL on two consecutive pages — the paging is not a partition (56–61 of 200 overlap, 2026-09-13)
                continue
            seen.add(e["id"])
            rows.append(e)
    if not rows:
        die(f"{len(walk)} jobentry page(s), {locs_total} <loc>, none of the shape /tyopaikat/tyo/<stem>-<id> — {count_says(body)}", EXIT_PARTIAL)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    bounded = len(walk) < len(pages)
    note(f"{len(walk)} of {len(pages)} jobentry page(s) read, {th(locs_total)} <loc>; **{th(len(rows))} distinct advertisement id(s)**"
         + (f", {th(repeated)} repeated across pages — the paging is not a partition, so as many may be missing at the page boundaries" if repeated else "")
         + (f", {other} of another shape set aside" if other else "") + (f" ({a.limit} printed under --limit)" if a.limit and len(rows) > a.limit else "")
         + (f" — the walk stopped at page {walk[-1]} of {last}, so the count is a lower bound" if bounded else "") + ".")
    if a.no_site_total:
        return
    code, body = get(LISTING)
    m = STATED_RE.search(text(body)) if code == 200 else None
    if not m:
        note(f"the listing {LISTING} answers HTTP {code} and states no «Löysimme N työpaikkaa» this run — no stated figure to print beside the {th(len(rows))}.")
        return
    stated = int(re.sub(r"\D", "", m.group(1)))
    if bounded:
        note(f"site states {th(stated)}; {th(len(rows))} emitted from a bounded walk, not compared.")
    elif stated == len(rows):
        note(f"{th(len(rows))} emitted, site states {th(stated)} — equal.")
    else:
        note(f"{th(len(rows))} emitted, site states {th(stated)} — {th(abs(stated - len(rows)))} " + ("short" if stated > len(rows) else "more emitted than the site states")
             + "; the sitemap and the listing's own count are two witnesses, and neither corrects the other.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/tyopaikat/tyo/<stem>-<id>")
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
    loc = d.get("jobLocation") or {}
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
    et = d.get("employmentType")
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    print(json.dumps({
        "source": "duunitori", "country": ((addr.get("addressCountry") or "").strip() or "FI") if isinstance(addr, dict) else "FI",
        "ledger_id": f"duunitori:{ident}", "id": ident, "url": a.url,
        # the JSON-LD `title` is the normalised occupation («harjoittelija»); the advertisement's own title is the <h1>
        "title": text(h1.group(1)) if h1 else text(d.get("title")),
        "occupation": text(d.get("title")) or None,
        "employer": (text(org.get("name")) or None) if isinstance(org, dict) else None,
        "employer_site": org.get("sameAs") if isinstance(org, dict) else None,
        "city": (text(addr.get("addressLocality")) or None) if isinstance(addr, dict) else None,
        "employment_type": ", ".join(et) if isinstance(et, list) else et,
        "posted": d.get("datePosted"), "valid_through": d.get("validThrough"),
        "description": redact(text(d.get("description")))[:20000], "language": "fi",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Duunitori — named as Claude-User in rules that refuse `*`; 92 job sitemap pages at 1 s against the listing's own «Löysimme N työpaikkaa»; JSON-LD on the advertisement, e-mail addresses redacted from its prose.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every advertisement in sitemap-jobentry.xml?p=1..92 — 18 298 on 2026-09-13, ~95 requests at 1 s; --pages bounds the walk")
    s.add_argument("--pages", type=int)
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advertisement, from its JSON-LD and its <h1>")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
