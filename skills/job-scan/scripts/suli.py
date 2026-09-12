#!/usr/bin/env python3
"""Suli (`suli.gl`) — Greenland's public job portal (Naalakkersuisut), read through the sitemap its rules declare and the `<head>` of each advertisement.

  suli.py sitemap [--culture en|da|kl] [--limit N] [--no-cross-cultures]
  suli.py ad --url <advertisement URL>

THE SITEMAP IS THE ROUTE, AND IT IS THE ONLY ONE THE RULES LEAVE OPEN

`robots.txt` is four lines: `Allow: /`, `Disallow: /umbraco/`, `Disallow:
/api/`, and the sitemap. **Every listing and every advertisement body on this
site is drawn by the browser from `/api/…`** — the job page is a React island
(`data-id="react-job-page" data-guid=…`) whose data call is
`/api/job-editor/job/<guid>` (read in `assets/jobHandler-*.js`, not called),
and the listing page `/en/jobs/` is 40 kB of chrome with zero advertisement
links. **A refusal written in the rules is honoured by every route, browser
included — nothing here reads `/api/`.** What is left, and what this adapter
reads: the sitemap (one file per culture, `?culture=en|da|kl`, 392 job URLs
each with a `<lastmod>` on 2026-09-12 10:55 UTC) and the `<head>` of an
advertisement page — `<title>` (the job title), `meta description` (the
employer's headline), `og:description` (the first ~150 characters of the
body, then «…»), and the job's GUID.

THE KEY. 353 of the 392 slugs end in eight hex digits — `regnskabschef-90b35708`
— and those digits are the first block of the job GUID
(`90b35708-9d35-424c-bfae-2f502b42d5b5`): **a stable id readable from the
sitemap without opening the page**, and the same in all three cultures. The
other 39 (`administrative-assistant`, `helena-testjob`, `softwareudvikler-web-
test`) carry no key in the slug and are all `<lastmod>` 2026-07-08 — the
oldest date in the file, and the population whose slugs name themselves as
tests. They are emitted with the slug as id and `key: slug`, never dropped:
which of them are real is the reader's call, and the adapter says how many
are which.

THE COUNT THE SITE STATES IS NOT REACHABLE BY THESE RULES — it lives in the
`/api/` listing. The second view is the other two culture files, which are the
same store under three sets of slugs: the adapter reads them and prints
«en 392 · da 392 · kl 392, 353 keys shared by all three» — or where they part.

`sulisussat.gl` is the same host under its older name: it redirects to
`suli.gl` (its `robots.txt` and `/da/jobs/` both land on `suli.gl`, canonical
`https://suli.gl/da/jobs/`), and the home page still links to it. No
`Crawl-delay`; `certain: True`; 200 to the declared identity on every path
read. Measured 2026-09-12 10:55–11:0x UTC.
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
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _sitemap import locs as sitemap_locs
from _ua import UA
from _zero import empty_first_page

BASE = "https://suli.gl"
INDEX = BASE + "/sitemap.xml"
CULTURES = ("en", "da", "kl")
# the job section's path segment differs by culture; the slug is the last one
JOB_SEGMENT = {"en": "jobs", "da": "jobs", "kl": "suliffissat-jobs"}
AD_RE = re.compile(r"^https://suli\.gl/(en|da|kl)/([a-z-]+)/([^/?#]+)/?$")
KEY_RE = re.compile(r"-([0-9a-f]{8})$")
GUID_RE = re.compile(r'data-id="react-job-page"[^>]*\bdata-guid="([0-9a-f-]{36})"')
TITLE_RE = re.compile(r"(?is)<title>\s*(.*?)\s*</title>")
META_RE = r'<meta\s+(?:name|property)="{name}"\s+content="([^"]*)"'
# the body's data call, read in assets/jobHandler-*.js and NEVER called: the rules refuse /api/
REFUSED_BODY_ROUTE = "/api/job-editor/job/<guid>"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[suli] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace("suli.gl", own=2.0)   # no Crawl-delay declared; 2 s is ours


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en,da;q=0.8,kl;q=0.7"})
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


def th(n):
    """Thousands with a space — the repo's figure style."""
    return f"{n:,}".replace(",", " ")


def culture_file(culture):
    return f"{INDEX}?culture={culture}"


def job_entries(xml, culture):
    """(slug, url, lastmod) for every advertisement URL of one culture file —
    the job section only, its own index page excluded."""
    out = []
    for m in re.finditer(r"(?is)<url>\s*<loc>\s*(?:<!\[CDATA\[)?\s*([^<\]\s]+)\s*(?:\]\]>)?\s*</loc>(.*?)</url>", xml):
        loc = m.group(1).strip()
        am = AD_RE.match(loc)
        if not am or am.group(1) != culture or am.group(2) != JOB_SEGMENT[culture]:
            continue
        lm = re.search(r"<lastmod>\s*([^<\s]+)\s*</lastmod>", m.group(2))
        out.append((am.group(3), loc, lm.group(1) if lm else None))
    return out


def key_of(slug):
    """The site's key when the slug carries it — eight hex digits, the first
    block of the job GUID — else None."""
    m = KEY_RE.search(slug)
    return m.group(1) if m else None


def row_for(slug, url, lastmod, culture):
    key = key_of(slug)
    return {"source": "suli", "country": "GL", "culture": culture,
            "ledger_id": f"suli:{key or slug}", "id": key or slug,
            "key": "guid8" if key else "slug",
            "url": url, "lastmod": lastmod}


def cmd_sitemap(a):
    culture = a.culture
    code, body = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}", EXIT_PARTIAL)
    children = sitemap_locs(body)
    if culture_file(culture) not in children:
        die(f"{INDEX} declares {len(children)} children and not {culture_file(culture)} — "
            "the culture file moved; read the index before believing a zero.", EXIT_PARTIAL)
    code, xml = get(culture_file(culture))
    if code != 200:
        die(f"{culture_file(culture)}: HTTP {code}", EXIT_PARTIAL)
    all_locs = sitemap_locs(xml)
    entries = job_entries(xml, culture)
    if not entries:
        die(empty_first_page("suli", xml, f"/{culture}/{JOB_SEGMENT[culture]}/ <loc>",
                             where=culture_file(culture),
                             candidates=len(all_locs)), EXIT_PARTIAL)
    rows, seen = [], set()
    for slug, url, lastmod in entries:
        r = row_for(slug, url, lastmod, culture)
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        rows.append(r)
    keyed = [r for r in rows if r["key"] == "guid8"]
    unkeyed = [r for r in rows if r["key"] == "slug"]
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    dates = sorted({(r["lastmod"] or "")[:10] for r in unkeyed})
    note(f"{th(len(all_locs))} <loc> in {culture_file(culture)}, {th(len(entries))} in the job section, "
         f"**{th(len(rows))} distinct id(s)**: {th(len(keyed))} carry the site's key in the slug "
         f"(8 hex, the first block of the job GUID) and {th(len(unkeyed))} do not"
         + (f" — those {th(len(unkeyed))} are last modified on {', '.join(dates)}" if unkeyed else "")
         + f". <lastmod> present on {th(sum(1 for r in rows if r['lastmod']))} of {th(len(rows))}.")
    note("The site states no count on any path these rules open — the listing is drawn from "
         "/api/, which robots.txt refuses; the second view is the other culture files.")
    if a.no_cross_cultures:
        return
    counts, keysets = {culture: len(rows)}, {culture: {r["id"] for r in keyed}}
    for other in CULTURES:
        if other == culture:
            continue
        if culture_file(other) not in children:
            note(f"{culture_file(other)} is not declared by the index this run — no cross-culture view for it.")
            continue
        code, oxml = get(culture_file(other))
        if code != 200:
            note(f"{culture_file(other)}: HTTP {code} — no cross-culture view for it.")
            continue
        oe = job_entries(oxml, other)
        counts[other] = len({key_of(s) or s for s, _, _ in oe})
        keysets[other] = {key_of(s) for s, _, _ in oe if key_of(s)}
    shared = set.intersection(*keysets.values()) if keysets else set()
    parts = " · ".join(f"{c} {th(n)}" for c, n in counts.items())
    if len(set(counts.values())) == 1 and len(counts) == len(CULTURES):
        note(f"{parts} — equal; {th(len(shared))} keys shared by all three cultures, one store under three sets of slugs.")
    else:
        note(f"{parts} — the culture files part; {th(len(shared))} keys shared by the files read. "
             "Three views of one store should agree: read the index and the files before trusting any one count.")


def head_meta(body, name):
    m = re.search(META_RE.format(name=re.escape(name)), body or "")
    return htmlmod.unescape(m.group(1)).strip() if m else None


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m or m.group(2) != JOB_SEGMENT.get(m.group(1)):
        die(f"{a.url}: not an advertisement address — expected {BASE}/<en|da|kl>/<jobs|suliffissat-jobs>/<slug>/")
    culture, slug = m.group(1), m.group(3)
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    g = GUID_RE.search(body)
    if not g:
        die(f"{a.url}: no `react-job-page` island with a GUID in {th(len(body))} characters — "
            "the page shape moved, or this is not an advertisement.", EXIT_PARTIAL)
    guid = g.group(1)
    key = key_of(slug)
    if key and key != guid[:8]:
        note(f"the slug's key {key} is not the GUID's first block {guid[:8]} — the sitemap row and this "
             "row would not meet on one id; the GUID is emitted beside it either way.")
    # the same id the sitemap row carries — the slug's key when it has one, else the slug — so the two rows meet
    ident = key or slug
    t = TITLE_RE.search(body)
    snippet = head_meta(body, "og:description")
    print(json.dumps({
        "source": "suli", "country": "GL", "culture": culture,
        "ledger_id": f"suli:{ident}", "id": ident, "key": "guid8" if key else "slug",
        "guid": guid, "slug": slug, "url": a.url,
        "title": htmlmod.unescape(t.group(1)).strip() if t else None,
        "headline": head_meta(body, "description"),
        # the first ~150 characters of the body, as the site publishes them in og:description; the body itself is behind /api/
        "description_snippet": snippet,
        "description_truncated": bool(snippet and snippet.endswith("…")),
        "page_culture": head_meta(body, "culture"),
        "language": None,   # the head carries whichever language the employer filled; not detected here
    }, ensure_ascii=False))
    note(f"the advertisement body is drawn by the browser from {REFUSED_BODY_ROUTE}, which robots.txt "
         "refuses to everyone — not read, by any route. `description_snippet` is the head's og:description, "
         "cut by the site; employer and location are not in the head.")


def main():
    p = argparse.ArgumentParser(description="Suli — Greenland's job portal, through the culture sitemaps it declares and the <head> of its pages.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="distinct advertisement ids with <lastmod> — 2 requests, 4 with the other two cultures")
    s.add_argument("--culture", choices=CULTURES, default="en")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-cross-cultures", action="store_true")
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one advertisement's head — title, headline, snippet, GUID; the body is behind a refused path")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
