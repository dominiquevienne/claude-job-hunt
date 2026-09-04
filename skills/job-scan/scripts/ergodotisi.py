#!/usr/bin/env python3
"""Ergodotisi — Cyprus (`ergodotisi.com`).

  ergodotisi.py list [--search developer] [--limit 20] [--since 2026-08-05]
  ergodotisi.py ad   --id vacancy-7f53159c-63758277

**The cleanest index of the twenty-eight boards measured across Asia and Africa
on 2026-09-04.** `/sitemap.xml` declares three children and names them
honestly — `jobs.xml`, `companies.xml`, `other.xml` — so the advertisements are
reachable without counting companies, categories or site furniture. Two of
twenty-eight do that; the rest mix everything into one file.

TWO THOUSAND SIX HUNDRED AND FORTY-FOUR, AND THE FILE SAYS FIVE THOUSAND

`jobs.xml` holds **5 302 `<loc>` for 2 644 advertisements**: every one appears
twice, once under `/en-CY/jobs/` and once under `/el-CY/jobs/`.

**They are not translations.** Measured on one advertisement, 2026-09-05: the
two documents differ by 475 characters out of 77 000, and the difference is
`<html lang='en-CY'>` against `<html lang='el-CY'>`. **The title, the employer
and the body are identical** — it is one advertisement served under two paths,
and the prefix changes the interface, not the content. So this reads `/en-CY/`
only, and the count is halved rather than deduplicated by chance.

AND THE ONLY COUNT IN THE SERIES WITH AN INDEPENDENT WITNESS

The site advertises **"2 573 open jobs"** on its own pages. This adapter counts
2 644 from the sitemap. **Two provenances, and the gap runs the way the
mechanism predicts** — a sitemap keeps recently closed advertisements a while.
A number that agrees with a second source it does not depend on is worth more
than a larger number that agrees with nothing.

*Measured 2026-09-05: 5 302 `<loc>`, 2 644 advertisements, 53 distinct dates
from 2026-06-26 to 2026-09-04, and 5 214 of the entries dated within thirty
days — a current stock, not an archive.*

WHERE THE FIELDS COME FROM, AND WHAT IS NOT THERE

**There is no `ld+json` on an advertisement page.** No `JobPosting`, no
`hiringOrganization`, no `salary`. The fields come from the document title,
which follows one shape:

    <role> at <employer> | Ergodotisi

**That is a parse of a title, and it is stated as one.** `employer` is `None`
when the ` at ` separator is absent rather than guessed at, and the raw title
is always emitted beside the parsed fields so a reader can check the split.

**Titles are frequently in Greek even under `/en-CY/`**, because the prefix is
the interface and not the advertisement. `--search` folds accents and matches
either script as written; it does not translate.

Verified against the live site on **2026-09-05**.
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
from _robots import allowed as robots_allowed
from _ua import UA

BASE = "https://ergodotisi.com"
SITEMAP = BASE + "/sitemap/jobs.xml"
PREFIX = "/en-CY/jobs/"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# CDATA-aware: `liberiajobsearch.com` returned a clean zero to `<loc>([^<]+)`
# on 2026-09-05 because its values are wrapped, and a clean zero reads as an
# absence. This one is not wrapped; the pattern covers both anyway.
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)
TITLE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
OGTITLE = re.compile(
    r'<meta[^>]+property=["\']og:title["\'][^>]*content=["\'](.*?)["\']', re.S)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[ergodotisi] {msg}", file=sys.stderr)


def gate(url):
    """Per path, never per host — the distinction #156 made expensive."""
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, parts.path or "/")
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)


def get(url):
    gate(url)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-GB,en;q=0.9,el;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def entries():
    """`(url, lastmod)` for the English path only, with both counts reported."""
    code, body = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    rows = []
    for block in ENTRY.findall(body):
        loc = LOC.search(block)
        if not loc:
            continue
        u = html_mod.unescape(loc.group(1).strip())
        d = LASTMOD.search(block)
        rows.append((u, d.group(1) if d else None))
    if not rows:
        die(f"{SITEMAP} parsed to zero entries from {len(body)} characters — "
            f"read the bytes before believing the zero: the shape changed, or "
            f"something other than a sitemap came back.")
    english = [r for r in rows if PREFIX in r[0]]
    greek = [r for r in rows if "/el-CY/jobs/" in r[0]]
    return english, len(rows), len(greek)


def ident(url):
    return url.rstrip("/").rsplit("/", 1)[-1]


def parse_title(raw):
    """`<role> at <employer> | Ergodotisi` — a parse of a title, said as one.

    **`employer` is `None` when the separator is absent**, never a guess. A
    role containing the word " at " would split wrongly; the raw title travels
    beside the fields so that is visible rather than silent.
    """
    t = html_mod.unescape(raw or "").strip()
    t = re.sub(r"\s*\|\s*Ergodotisi\s*$", "", t)
    role, employer = t, None
    if " at " in t:
        role, employer = t.rsplit(" at ", 1)
    city = None
    m = re.search(r"\(([^()]{2,40})\)\s*$", role.strip())
    if m:
        city = m.group(1).strip()
        role = role[: m.start()].strip()
    return role.strip(), (employer.strip() if employer else None), city


def card(url, lastmod, page=None):
    raw = ""
    if page:
        m = OGTITLE.search(page) or TITLE.search(page)
        raw = m.group(1) if m else ""
    role, employer, city = parse_title(raw)
    return {
        "source": "ergodotisi", "url": url, "id": ident(url),
        "title": role or None, "employer": employer, "city": city,
        "title_raw": html_mod.unescape(raw).strip() or None,
        "posted": lastmod, "countries": ["CY"],
    }


def cmd_list(a):
    english, total, greek = entries()
    note(f"{total} <loc> · {len(english)} under {PREFIX} · {greek} under "
         f"/el-CY/jobs/ — **the same advertisements under two paths**, not "
         f"translations. The English side is the count.")
    rows = english
    if a.since:
        rows = [r for r in rows if r[1] and r[1] >= a.since]
        note(f"{len(rows)} dated {a.since} or later")
    if a.limit:
        rows = rows[: a.limit]
    if not a.fetch and not a.search:
        print(json.dumps({"source": "ergodotisi", "country": "CY",
                          "sitemap_entries": total, "advertisements": len(english),
                          "listed": len(rows),
                          "ads": [card(u, d) for u, d in rows]},
                         ensure_ascii=False, indent=1))
        return
    kept, broken = [], []
    needle = fold(a.search) if a.search else None
    for u, d in rows:
        code, page = get(u)
        if code != 200:
            broken.append((u, f"HTTP {code}"))
            continue
        c = card(u, d, page)
        if needle and needle not in fold(c["title_raw"] or ""):
            continue
        kept.append(c)
    if broken:
        note(f"{len(broken)} page(s) did not answer 200: "
             + "; ".join(f"{ident(u)} ({w})" for u, w in broken[:5]))
    print(json.dumps({"source": "ergodotisi", "country": "CY",
                      "sitemap_entries": total, "advertisements": len(english),
                      "read": len(kept) + len(broken), "kept": len(kept),
                      "unreadable": len(broken), "ads": kept},
                     ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}{PREFIX}{a.id}"
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.id} is gone (HTTP {code}) — expired or withdrawn. Record it as "
            f"discarded, do not retry.", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    print(json.dumps(card(url, None, page), ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="advertisements from the sitemap")
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="keep entries whose lastmod is on or after this date")
    li.add_argument("--limit", type=int)
    li.add_argument("--search", help="match the title; folds accents, does not "
                                     "translate — many titles are in Greek")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for its title; without it the listing "
                         "is the sitemap alone and carries no titles")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by id")
    ad.add_argument("--id", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
