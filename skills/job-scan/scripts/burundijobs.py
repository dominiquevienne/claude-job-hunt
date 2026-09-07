#!/usr/bin/env python3
"""Burundi Jobs (`www.burundijobs.bi`) — the first adapter for Burundi.

  burundijobs.py list [--since 2026-08-01] [--limit 20] [--fetch] [--live]
  burundijobs.py ad --slug ingenieur-des-travaux

**Burundi had no board at all in this repository until today.** The country
page counted zero.

THE RULES OPEN THIS HOST TO ONE OF OUR TWO TOKENS, AND THAT IS RECENT

`www.burundijobs.bi/robots.txt` carries the Cloudflare managed block, 2 012
bytes: `User-agent: *` gets `Allow: /`, and ten AI agents are named and closed
— `ClaudeBot` among them. **`Claude-User` is not one of the ten.**

Until 2026-09-07 this module's guard unioned six names a site might use about
us, so this host was reported closed and nobody read it. The owner decided that
day that a named refusal binds the token it names and no other; `allowed()`
now answers under the token a request would actually carry. **This adapter is
the first to exist because of that decision**, and it presents `Claude-User`.

`Content-Signal: search=yes,ai-train=no,use=reference` — our use is reference,
and we do not train. The signal is carried on every verdict this module gets.

**There is an `iwj_candidate-sitemap.xml` beside the job one and this adapter
never reads it.** It lists people looking for work. Nothing here needs it, the
rules do not distinguish it, and *"the rules permit it"* is not why we read
something.

WHAT WAS MEASURED, 2026-09-07

    iwj_job-sitemap.xml     160 <loc>, 160 distinct, all /job/<slug>/
    lastmod                 57 distinct dates, 2024-01-01 -> 2026-09-05

**The sitemap is not a list of live pages**, and this is the figure that
matters:

    every one of the 160 fetched once, 2026-09-07, one request a second
        52  HTTP 200   -- and 52 of 52 carry a JobPosting
       108  HTTP 404   -- listed here, gone from the site

**And `lastmod` does not separate them.** August 2026 holds 25 live entries
and 33 dead ones. *`--since` narrows the list; it cannot replace fetching.*

    fields on the 52    title · description · datePosted · hiringOrganization
                        · baseSalary      52/52
                        validThrough      51/52
                        jobLocation       29/52
    titles read as procurement            24/52

**So `160` is the archive as the file remembers it, not the board.** Reporting
the file length as the board's size is the defect three adapters in this
repository have already carried — `jobsbotswana` at 367-against-368,
`caglobalint` at 183-against-180. Here the gap is not one entry, it is most of
them.

TWO FIELDS ARE PRESENT AND WRONG, AND THEY ARE NOT EMITTED

The InWave Jobs theme fills a `JobPosting` block, and two of its fields carry
the theme's defaults rather than the advertisement's facts:

    baseSalary.currency   XPF — the CFP franc, of French Polynesia and New
                          Caledonia. Burundi uses BIF. Every sampled ad says
                          XPF, so this is the template, not a mistake in one
                          posting.
    baseSalary.value      the string "négociable" — not a number
    addressCountry        a province: "Muramvya", "Plusieurs provinces"

**A field that is present and wrong is worse than one that is absent.** A
salary of *négociable XPF* on a Burundian advertisement would travel into the
ledger looking like data. Neither is emitted. What the page said about place is
kept verbatim in `place`, so nothing is discarded — it is just not called a
country. `countries` is `["BI"]`, from the board, which is the fact we have.

`employmentType` and `industry` are absent from every sampled posting, so there
is nothing to decide about them.

TENDERS SIT AMONG THE ADVERTISEMENTS

`appel d'offres`, `demande d'offre de service`, `fourniture de dolomie` — this
board carries procurement notices in the same sitemap as its job ads, the same
way `jobsnepal` does at 31 %.

**They are counted and reported; they are not silently filtered.** The share is
in the output as `tender_like`. `--jobs-only` drops them, and the flag says in
its help that the test is lexical: it reads French procurement wording in the
title and will miss a notice worded differently, and can catch a genuine
vacancy for a procurement officer. *A semantic defect does not yield to a
predicate* — so the count is published beside the filter, and the filter is
never the default.

Verified against the live site on 2026-09-07.
"""

import argparse
import datetime
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

BASE = "https://www.burundijobs.bi"
SITEMAP = BASE + "/iwj_job-sitemap.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)

# **Lexical, French, and declared as such.** Read the docstring before
# extending this: it is a reported count first and a filter second.
TENDER = re.compile(
    r"appel\s+d.?offres?|avis\s+d.?appel"
    r"|demande\s+d.?offres?\s+de\s+service"
    # `d’intérêt` carries an accent, and `inter` does not match `intér`. The
    # first version of this line missed every *manifestation d’intérêt* on the
    # board for that one letter.
    r"|manifestation\s+d.?int"
    r"|appel\s+.\s*(?:projets?|manifestation)"
    r"|fourniture[s]?\s+d|acquisition\s+de",
    re.I)

# **`appel à candidature` is deliberately NOT here.** It is used for
# scholarships on this board and for recruitment throughout francophone
# Africa: including it would drop real vacancies, and excluding it leaves
# *Appel à candidature — Programme de Bourses d'Études* counted as a job.
# **Both choices are wrong on some rows**, which is what it means for a
# semantic distinction to have no lexical answer. The count is published so
# the reader can see the residue rather than trust the filter.


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[burundijobs] {msg}", file=sys.stderr)


def gate(url):
    """Per path, on the exact URL — **query included.**

    A guard taken on `parts.path` alone answers a different question from the
    one the fetch asks, and 54 call sites in this repository did exactly that
    until 2026-09-07.
    """
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace("www.burundijobs.bi", own=1.0)


def get(url):
    gate(url)
    # `Pace` reads the host's own `Crawl-delay` itself; this host declares
    # none, so the 1 s floor above is ours and is declared as ours.
    _PACE.wait()
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "fr-BI,fr;q=0.9",
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


def slug_of(url):
    return url.rstrip("/").rsplit("/", 1)[-1]


def entries():
    code, body = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    rows, raw, seen = [], 0, set()
    for block in ENTRY.findall(body):
        loc = LOC.search(block)
        if not loc:
            continue
        raw += 1
        u = html_mod.unescape(loc.group(1).strip())
        if u in seen:
            continue
        seen.add(u)
        d = LASTMOD.search(block)
        rows.append((u, d.group(1) if d else None))
    if not rows:
        die(f"{SITEMAP} parsed to zero entries from {len(body)} characters — "
            f"read the bytes before believing the zero.")
    # Newest first: the file is oldest-first, and most of the old end is gone.
    rows.sort(key=lambda r: (r[1] or ""), reverse=True)
    return rows, raw


def posting_on(page):
    """**The `[d]` fallback matters.** The theme emits its `JobPosting` as a
    bare top-level object with no `@graph`, and a reader that only walks
    `@graph` reports *no posting here* on every single advertisement. That
    happened during this adapter's own measurement, and it looked exactly like
    a board with no structured data."""
    for b in LDJSON.findall(page):
        for strict in (True, False):
            try:
                d = json.loads(b.strip(), strict=strict)
            except ValueError:
                continue
            graph = d.get("@graph") if isinstance(d, dict) else None
            items = graph or (d if isinstance(d, list) else [d])
            for it in items:
                if isinstance(it, dict) and it.get("@type") == "JobPosting":
                    return it, None
            break
    return None, "no readable JobPosting on the page"


def _place(posting):
    """The place as the page wrote it, never renamed into a country."""
    jl = posting.get("jobLocation")
    if isinstance(jl, list):
        jl = jl[0] if jl else None
    addr = (jl or {}).get("address") if isinstance(jl, dict) else None
    if not isinstance(addr, dict):
        return None, None
    locality = (addr.get("addressLocality") or "").strip() or None
    # `addressCountry` holds a province here — kept, and not called a country.
    written = (addr.get("addressCountry") or "").strip() or None
    return locality, written


def card(url, lastmod, posting):
    org = posting.get("hiringOrganization")
    if isinstance(org, dict):
        org = org.get("name")
    org = (org or "").strip() or None
    title = html_mod.unescape(posting.get("title") or "").strip() or None
    locality, written = _place(posting)
    return {
        "source": "burundijobs",
        "url": url,
        "slug": slug_of(url),
        "title": title,
        "employer": org,
        "city": locality,
        # **What the page put in `addressCountry`, under a name that does not
        # claim it is one.** It holds "Muramvya" and "Plusieurs provinces".
        "place_as_written": written,
        "posted": (posting.get("datePosted") or "")[:10] or lastmod,
        "valid_through": (posting.get("validThrough") or "")[:10] or None,
        "tender_like": bool(title and TENDER.search(title)),
        "countries": ["BI"],
    }
    # `baseSalary` is deliberately absent: currency XPF on every posting is
    # the theme's default and the value is the word "négociable".
    # `employmentType` and `industry` are absent from the source.


def cmd_list(a):
    rows, raw = entries()
    note(f"{raw} <loc> in the sitemap. **Most of them are gone from the "
         f"site**: this file is an archive index, not a list of live pages.")
    if a.since:
        rows = [r for r in rows if r[1] and r[1] >= a.since]
        note(f"{len(rows)} with lastmod {a.since} or later")
    if a.limit:
        rows = rows[: a.limit]
    if not (a.fetch or a.search or a.live or a.jobs_only):
        print(json.dumps({"source": "burundijobs", "country": "BI",
                          "sitemap_entries": raw, "listed": len(rows),
                          "note": "URLs only — pass --fetch to see which "
                                  "still exist; the sitemap keeps entries "
                                  "whose pages are gone.",
                          "ads": [{"url": u, "slug": slug_of(u), "lastmod": d}
                                  for u, d in rows]},
                         ensure_ascii=False, indent=1))
        return
    today = datetime.date.today().isoformat()
    kept, broken, gone, expired, tenders = [], [], 0, 0, 0
    needle = fold(a.search) if a.search else None
    for u, d in rows:
        code, page = get(u)
        if code in (404, 410):
            gone += 1
            continue
        if code != 200:
            broken.append((u, f"HTTP {code}"))
            continue
        posting, why = posting_on(page)
        if posting is None:
            broken.append((u, why))
            continue
        c = card(u, d, posting)
        if c["tender_like"]:
            tenders += 1
            if a.jobs_only:
                continue
        if a.live and c["valid_through"] and c["valid_through"] < today:
            expired += 1
            continue
        if needle and needle not in fold(c["title"] or ""):
            continue
        kept.append(c)
    note(f"{gone} of {len(rows)} answered 404 or 410 — **listed in the "
         f"sitemap and no longer on the site.**")
    note(f"{tenders} title(s) read as a procurement notice. The test is "
         f"lexical and French; it is a count, not a verdict.")
    if a.live:
        note(f"{expired} dropped on a past `validThrough`.")
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{slug_of(u)} ({w})" for u, w in broken[:5]))
    print(json.dumps({"source": "burundijobs", "country": "BI",
                      "sitemap_entries": raw, "asked": len(rows),
                      "gone": gone, "kept": len(kept),
                      "unreadable": len(broken), "tender_like": tenders,
                      "expired_dropped": expired if a.live else None,
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken or gone:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}/job/{a.slug}/"
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.slug} is gone (HTTP {code}) — it is still in the sitemap. "
            f"Record it as discarded.", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    posting, why = posting_on(page)
    if posting is None:
        die(f"{url}: {why}")
    print(json.dumps(card(url, None, posting), ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="entries from the job sitemap")
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="filter on the sitemap's `lastmod`")
    li.add_argument("--limit", type=int)
    li.add_argument("--search", help="match the title; folds accents")
    li.add_argument("--live", action="store_true",
                    help="drop ads whose `validThrough` has passed")
    li.add_argument("--jobs-only", action="store_true", dest="jobs_only",
                    help="drop titles that read as procurement notices. "
                         "**Lexical and French**: it will miss a notice "
                         "worded otherwise and can catch a real vacancy for "
                         "a procurement officer. The count is reported "
                         "whether or not you pass this.")
    li.add_argument("--fetch", action="store_true",
                    help="open each page; without it the listing is the "
                         "sitemap alone, and the sitemap keeps dead entries")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
