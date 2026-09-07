#!/usr/bin/env python3
"""Jobrapide (`www.jobrapide.org`) — francophone Africa, Chad-centred.

  jobrapide.py list [--pages 3] [--since 2026-09-01] [--category avis-recrutement]
  jobrapide.py ad --url https://www.jobrapide.org/offres/avis-recrutement/<slug>/

**There is no sitemap and no structured job data.** The rules file declares no
`Sitemap:` line, and the single `ld+json` block on an advertisement says
`@type: Article` — `JobPosting` appears zero times. So the route is the
WordPress category archive and the parsing is HTML.

    /recrutement/offres/avis-recrutement/           body class `category-17`
    /recrutement/offres/avis-recrutement/page/N/    N up to 6 182

WHAT ONE PAGE CARRIES, MEASURED 2026-09-07

Each advertisement is a `div.article`, and three fields come off the archive
itself — **without opening the advertisement**:

    <h3><a href="/offres/<category>/<slug>/">title</a></h3>
    <b>Publié le: <a href="/2026/09/07/">7 septembre 2026</a></b>
    <ul class="post-categories"><li><a>Avis de recrutement</a>

**So `--since` costs one request per page and never one per advertisement.**
The date is taken from the `/YYYY/MM/DD/` link rather than from the French
sentence beside it: one is a machine's and the other is a month name.

CONSECUTIVE PAGES OVERLAP, AND NOT BY A FIXED AMOUNT

    page 1 ∩ page 2   2 advertisements
    page 2 ∩ page 3   0
    page 3 ∩ page 4   1
    40 rows read, 37 distinct — 7.5 % duplicated on this sample

**So `pages × 10` over-counts.** The overlap is not a constant offset that
could be subtracted; this module deduplicates by URL and **reports how many
duplicates it dropped**, because that figure is a property of the board and
not an artefact to hide.

*The card's order of magnitude — about 6 182 pages at roughly 10.7 each, so of
the order of 66 000 — was taken without this correction. It is an estimate
from three samples and it is still the only figure available; it is not made
more precise here.*

NO COUNTRY IS EMITTED PER ADVERTISEMENT, AND THAT IS A MEASUREMENT

The card attributes ten jurisdictions from 30 slugs. **Reading the country out
of a slug per row was tried here and abandoned**: on 37 slugs it named a
country for 26 and nothing for 11 — and three of those eleven are
`mamoudzou-france`, `grand-est-strasbourg` and `caritas-suisse`.

> **The board carries advertisements outside the ten countries its card
> declares, and an extractor that knows only African names calls them
> "no country".**

*A narrow extractor does not return less, it returns false, and its silence
has the shape of an absence.* That is the defect the card itself records
having made, reproduced here on the first attempt. **`countries` therefore
carries the board's declared jurisdictions and nothing is claimed per row.**

WHAT THIS BOARD POSTS IS MOSTLY NOT JOBS

Measured on the homepage's 65 distinct `/offres/` URLs: 16 scholarships, 10
procurement tenders, 10 recruitment notices, 5 competitive exams, 5
internships, 5 volunteering, 4 training courses. **`--category` selects one,
and the default is `avis-recrutement`** — the recruitment archive — rather
than everything, because everything is mostly not a vacancy.

Verified against the live site on 2026-09-07.
"""

import argparse
import html as html_mod
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path
from _ua import UA

BASE = "https://www.jobrapide.org"
ARCHIVE = BASE + "/recrutement/offres/{category}/"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# The board's declared jurisdictions, from the card. **Not a per-row claim.**
COUNTRIES = ["TD", "CM", "CG", "CI", "BJ", "BI", "MR", "ML", "SD", "SN"]

ARTICLE = re.compile(
    r'<div class="article">(.*?)(?=<div class="article">|<div class="pagination'
    r'|</main|$)', re.S)
TITLE = re.compile(
    r'<h3><a href="(https://www\.jobrapide\.org/offres/[^"]+)"[^>]*>(.*?)</a>',
    re.S)
POSTED = re.compile(r'href="https://www\.jobrapide\.org/(\d{4})/(\d{2})/(\d{2})/"')
CATEGORY = re.compile(r'class="post-categories"><li><a[^>]*>(.*?)</a>', re.S)
PAGES = re.compile(r'/page/(\d+)/')


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobrapide] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    # An unknown is not a refusal: `not None` is `True` for both.
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# The host declares no `Crawl-delay`; one second is ours and is declared as
# ours. Eight requests had been made to this host in total before this module
# existed, and the card counted them.
_PACE = Pace("www.jobrapide.org", own=1.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "fr-FR,fr;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, "", url
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def clean(s):
    return " ".join(html_mod.unescape(re.sub(r"<[^>]+>", "", s or "")).split())


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def slug_of(url):
    return url.rstrip("/").rsplit("/", 1)[-1]


def rows_on(page):
    """Every `div.article` on one archive page, as rows."""
    out = []
    for block in ARTICLE.findall(page):
        m = TITLE.search(block)
        if not m:
            continue
        d = POSTED.search(block)
        c = CATEGORY.search(block)
        url = html_mod.unescape(m.group(1))
        out.append({
            "source": "jobrapide",
            "url": url,
            "slug": slug_of(url),
            "title": clean(m.group(2)) or None,
            # From the dated permalink, not from « 7 septembre 2026 » beside
            # it: one is a machine's and the other is a month name.
            "posted": "-".join(d.groups()) if d else None,
            "category": clean(c.group(1)) if c else None,
            # **The board's jurisdictions, never a claim about this row.**
            # Reading a country out of the slug was tried and abandoned: see
            # the module docstring.
            "countries": COUNTRIES,
        })
    return out


def walk(category, pages):
    """Pages 1..N of one archive, **deduplicated, with the drop reported.**"""
    seen, rows, dropped, announced = set(), [], 0, None
    for n in range(1, pages + 1):
        url = ARCHIVE.format(category=category)
        if n > 1:
            url += f"page/{n}/"
        code, page, landed = get(url)
        if code == 404:
            note(f"page {n} answered 404 — the archive ends before here.")
            break
        if code != 200:
            die(f"{url}: HTTP {code}")
        if landed and landed.rstrip("/") != url.rstrip("/"):
            # **`final_url` is why this check exists.** `/offres/<category>/`
            # redirects to a single article, and only the provenance record
            # showed it: a count taken there would have been measured on a
            # page that is not a list.
            die(f"{url} redirected to {landed} — that is not an archive "
                f"page, and counting it would count one article.", EXIT_BROKEN)
        if announced is None:
            found = [int(x) for x in PAGES.findall(page)]
            announced = max(found) if found else None
        got = rows_on(page)
        if not got:
            note(f"page {n} parsed to zero advertisements from {len(page)} "
                 f"characters — read the bytes before believing the zero.")
        for r in got:
            if r["url"] in seen:
                dropped += 1
                continue
            seen.add(r["url"])
            rows.append(r)
    return rows, dropped, announced


def cmd_list(a):
    rows, dropped, announced = walk(a.category, a.pages)
    note(f"{len(rows)} distinct advertisements over {a.pages} page(s); "
         f"**{dropped} duplicate(s) dropped**. Consecutive pages overlap and "
         f"not by a fixed amount, so `pages × 10` over-counts.")
    if announced:
        note(f"the paginator announces {announced} pages. **That is the "
             f"board's claim, not a count** — no total is derived from it "
             f"here.")
    if a.since:
        before = len(rows)
        rows = [r for r in rows if r["posted"] and r["posted"] >= a.since]
        note(f"{len(rows)} of {before} posted {a.since} or later — the date "
             f"is on the archive page, so this cost no extra request.")
    if a.search:
        needle = fold(a.search)
        rows = [r for r in rows if needle in fold(r["title"] or "")]
    print(json.dumps({"source": "jobrapide", "category": a.category,
                      "pages_read": a.pages, "pages_announced": announced,
                      "distinct": len(rows), "duplicates_dropped": dropped,
                      "countries": COUNTRIES,
                      "note": "`countries` is the board's declared "
                              "jurisdictions; no country is claimed per "
                              "advertisement — see the module docstring.",
                      "ads": rows}, ensure_ascii=False, indent=1))


def cmd_ad(a):
    code, page, _landed = get(a.url)
    if code in (404, 410):
        die(f"{a.url} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}")
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    d = POSTED.search(page)
    print(json.dumps({
        "source": "jobrapide", "url": a.url, "slug": slug_of(a.url),
        "title": clean(h1.group(1)) if h1 else None,
        "posted": "-".join(d.groups()) if d else None,
        "countries": COUNTRIES,
        # **No `JobPosting` on this board**: the one `ld+json` block declares
        # `@type: Article`. Nothing structured is invented from the prose.
        "structured_data": "none — the page declares @type: Article",
    }, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="advertisements from a category archive")
    li.add_argument("--pages", type=int, default=3,
                    help="archive pages to read, from the first")
    li.add_argument("--category", default="avis-recrutement",
                    help="the archive to read. **The default is the "
                         "recruitment one**: this board also posts "
                         "scholarships, tenders, exams and training, and they "
                         "outnumber the vacancies")
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="filter on the posting date, which is on the archive "
                         "page — this costs no extra request")
    li.add_argument("--search", help="match the title; folds accents")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by URL")
    ad.add_argument("--url", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
