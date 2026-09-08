#!/usr/bin/env python3
"""iHarare Jobs (`ihararejobs.com`) — Zimbabwe's only reachable board.

  ihararejobs.py list [--limit 20] [--search engineer]
  ihararejobs.py list --fetch --since 2026-08-01 [--live] [--limit 50]
  ihararejobs.py ad --slug insurance-interns-6310

**6 295 advertisements in one sitemap**, every one distinct and every one
carrying the board's own id in its URL. The country's rank-1 board answers
HTTP 500, so without this there is nothing.

READING THIS BOARD CHANGES IT — MEASURED, NOT SUSPECTED

**`lastmod` in the sitemap is not a publication date. It moves when the page
is fetched, and our own requests moved it.**

    read 1  18:08:41Z       6 295 advertisements
    read 2  18:16:22Z       6 295 advertisements, 0 gained, 0 lost
            7 min 41 s apart, read off the provenance records
    lastmod changed              6
    of those, fetched by us      6
    of those, NOT fetched by us  0   out of 6 286 untouched

Nine pages were fetched between the two reads. Six moved; the other three were
already stamped with the current date and could not move within a field of
day granularity. **Nothing we did not touch moved at all.**

*The mechanism is an inference — a view counter writing a timestamp would do
this — but the observation needs no mechanism:* **a sweep of this board dates
everything it reads to the day of the sweep.** That is why 60.5 % of the file
carried the current date at read 1 and 22 % the day before, across only 28
distinct dates spanning 2024-01-30 to today. *This repository already held
«3 417 dates moving under identical URLs» here and had not found the cause.*

**So `--since` is refused on the sitemap and offered only with `--fetch`**,
where it filters the `datePosted` of the advertisement itself. A `--since` on
`lastmod` would return almost the whole board and call it this week's — and
it would be OUR OWN CRAWL that made it look that way.

**And it means our reading pollutes a signal other readers use.** The pace is
two seconds and `list` costs one request; `--fetch` is opt-in for that reason
as much as for politeness.

THE REAL DATES ARE IN THE SCHEMA, IN DJANGO'S FORMAT

Each advertisement carries one `JobPosting` with a genuine `datePosted` and
`validThrough` — but written for a human:

    "Sept. 7, 2026, 12:44 p.m."      "Oct. 9, 2024"      "April 29, 2024"
    "June 5, 2024, 1:36 p.m."        "May 3, 2024"       "Aug. 14, 2024"

**This is Django's `N j, Y` — AP style.** Four of the twelve months are
abbreviated to three letters and a dot, five are spelled out in full, and
**September is `Sept.`, which is four.** `%b` parses none of the last six, and
`value[:10]` yields `Sept. 7, 2`, which is not a date and does not look like
an error. The month table below is explicit and every one of the twelve is
exercised in the tests.

`strict=False` IS LOAD-BEARING HERE, AND MORE SO THAN NEXT DOOR

**Six of eight sampled advertisements need the lax pass**; the descriptions
carry raw control characters. A parser that tries once reads three quarters of
this board as having no structured data at all — a confident, quiet zero.
*`angolaemprego.md` records the same trap at a much lower rate.*

THE EMPLOYER IS USUALLY REAL AND SOMETIMES THE SITE

`hiringOrganization.name` reads `iHarare Jobs` — with the board's own street
address — on **1 of 8 sampled**; the other seven name Old Mutual, the World
Food Programme, two universities, an embassy. The site's own name is emitted
as written with `employer_is_site: true`, never as `None`: *«the board did not
name an employer»* and *«we could not find one»* are different facts.

`addressLocality` is genuine — Harare, Bindura, Gweru — even when the street
address is the board's.

THE FILE HOLDS 208 CATEGORY PAGES AND 105 DUPLICATES, AND NEITHER IS AN AD

    6 503 <loc>  =  6 295 advertisements  +  208 /categories/ pages
    the 105 duplicated <loc> and the 104 without `lastmod` are ALL categories

**Counting the file would report the board 3.3 % larger than it is**, and the
duplicates would have been blamed on the advertisements.

AN UNKNOWN ADVERTISEMENT ANSWERS 200 WITH THE LISTING PAGE

Not 404, not 410: **50 kB, `<h1>Browse Jobs</h1>`, no `ld+json`.** A soft 404
is worse than a hard one in both directions — a sweep banks it as a live page
that merely lacks structured data, and a check asking «did it 404?» reports
the advertisement as still there. `ad` exits 3 on it and `list --fetch` names
it `gone` rather than `unreadable`.

THE RULES FILE HAS NO `User-agent:` LINE AT ALL

Seven `Disallow:` directives and no group — so they belong to no agent, and
the guard answers `allowed: True` for every one of them. **See #180.** *This
module fetches none of the seven regardless*: `/login/`, `/static/`,
`/register/`, `/candidate/`, `/employer_admin/`, `/admin/`, `/vacancy/apply/`.
The inventory is under `/job/` and under `/sitemap.xml`, neither of which the
file names.

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
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BASE = "https://ihararejobs.com"
SITEMAP = BASE + "/sitemap.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(\d{4}-\d{2}-\d{2})", re.S)
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)
ID_IN_URL = re.compile(r"-(\d+)/?$")

# **This host answers an unknown advertisement with HTTP 200 and its listing
# page** — 50 kB, `<h1>Browse Jobs</h1>`, no `ld+json`. A soft 404 is worse
# than a hard one in both directions: a sweep banks it as a live page that
# merely has no structured data, and a check that asks «did it 404?» reports
# the advertisement as still there. The marker is the listing's own heading,
# under a `/job/<slug>/` path where it cannot legitimately appear.
SOFT_404 = re.compile(r"<h1[^>]*>\s*Browse Jobs\s*</h1>", re.I)

# **Django's `N` filter, AP style — not `%b`.** Five months are spelled out and
# `Sept.` is four letters, so `datetime.strptime(…, "%b")` fails on half of
# them. Written out because getting one wrong yields `None` on a twelfth of the
# board and nothing says which twelfth.
MONTHS = {"jan": 1, "feb": 2, "march": 3, "april": 4, "may": 5, "june": 6,
          "july": 7, "aug": 8, "sept": 9, "oct": 10, "nov": 11, "dec": 12}

# **#180 is decided, so this module keeps no copy of the refused list.**
# `allowed()` now returns `None` — INDETERMINATE — for a path an orphaned
# `Disallow` matches, and `gate()` already stops on `None`. A second list here
# would be somewhere for the two to drift apart, and it claimed a *refusal*
# (exit 7) where the repository has decided we cannot establish one (exit 8).


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[ihararejobs] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# The host declares no `Crawl-delay`; two seconds are ours and declared as ours.
_PACE = Pace("ihararejobs.com", own=2.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-ZW,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def clean(s):
    return " ".join(html_mod.unescape(re.sub(r"<[^>]+>", " ", s or "")).split())


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def iso(value):
    """`"Sept. 7, 2026, 12:44 p.m."` -> `"2026-09-07"`, or `None`.

    **Never a guess and never a slice.** `value[:10]` on this format yields
    `Sept. 7, 2`, which is not a date and does not read like a failure.
    """
    # **An ISO date is accepted too, and that is not indulgence.** If this
    # host ever switches to `2026-09-07`, a parser that only knows the AP
    # form returns `None` on every advertisement — a total, silent loss that
    # looks exactly like a board with no dates.
    m = re.match(r"\s*(\d{4}-\d{2}-\d{2})(?!\d)", value or "")
    if m:
        return m.group(1)
    m = re.match(r"\s*([A-Za-z]+)\.?\s+(\d{1,2}),\s*(\d{4})", value or "")
    if not m:
        return None
    month = MONTHS.get(m.group(1).lower())
    return f"{m.group(3)}-{month:02d}-{int(m.group(2)):02d}" if month else None


def slug_of(url):
    return url.rstrip("/").rsplit("/", 1)[-1]


def entries():
    """`(advertisements, counts)` — categories are counted and excluded."""
    code, body = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    rows, counts = [], {"loc": 0, "category": 0, "duplicate": 0}
    seen = set()
    for block in ENTRY.findall(body):
        loc = LOC.search(block)
        if not loc:
            continue
        counts["loc"] += 1
        url = html_mod.unescape(loc.group(1).strip())
        if "/job/" not in url:
            counts["category"] += 1
            continue
        if url in seen:
            counts["duplicate"] += 1
            continue
        seen.add(url)
        ident = ID_IN_URL.search(url)
        d = LASTMOD.search(block)
        rows.append({
            "source": "ihararejobs",
            "url": url,
            "slug": slug_of(url),
            "id": ident.group(1) if ident else None,
            "ledger_id": f"ihararejobs:{ident.group(1) if ident else slug_of(url)}",
            # **Named for what it is, and it is not a publication date.** Our
            # own fetches moved six of these in under eight minutes.
            "sitemap_lastmod": d.group(1) if d else None,
            "lastmod_means": "when the page was last touched, our own reads "
                             "included — not when it was published",
            "countries": ["ZW"],
        })
    if not rows:
        die(f"{SITEMAP} parsed to zero advertisements from {len(body)} "
            f"characters — read the bytes before believing the zero.")
    rows.sort(key=lambda r: int(r["id"] or 0), reverse=True)
    return rows, counts


def posting_on(page):
    """`(posting, why, mode)` — and `mode` says which pass read it."""
    for block in LDJSON.findall(page):
        for strict in (True, False):
            try:
                d = json.loads(block.strip(), strict=strict)
            except ValueError:
                continue
            items = d if isinstance(d, list) else [d]
            for it in items:
                if isinstance(it, dict) and it.get("@type") == "JobPosting":
                    return it, None, "strict" if strict else "lax"
            break
    return None, "no readable JobPosting on the page", None


def card(url, row, posting, mode):
    org = posting.get("hiringOrganization") or {}
    name = (org.get("name") or "").strip() if isinstance(org, dict) else ""
    place = posting.get("jobLocation") or {}
    addr = (place.get("address") or {}) if isinstance(place, dict) else {}
    out = dict(row)
    out.update({
        "title": clean(posting.get("title")) or None,
        "employer": name or None,
        # **The site's own name, not a missing value.** 1 of 8 sampled.
        "employer_is_site": name.lower() == "iharare jobs",
        "city": (addr.get("addressLocality") or "").strip() or None,
        "country_name": (addr.get("addressCountry") or "").strip() or None,
        "salary": (posting.get("baseSalary") if isinstance(
            posting.get("baseSalary"), str) else None),
        # **The real dates, from the advertisement and not from the sitemap.**
        "posted": iso(posting.get("datePosted")),
        "posted_raw": posting.get("datePosted"),
        "valid_through": iso(posting.get("validThrough")),
        "json_pass": mode,
    })
    return out


def cmd_list(a):
    rows, counts = entries()
    # **The ratio divided by the count that is zero in the one case this
    # sentence exists for.** `<loc>` beside advertisements is the anchor: a
    # reader that stopped parsing prints `6295 <loc>: 0`, which no empty board
    # can produce. Dividing by `len(rows)` raised ZeroDivisionError instead,
    # so the anchor was destroyed on exactly its own path. #181.
    if not rows:
        die(f"{counts['loc']} `<loc>` in the sitemap and 0 advertisement(s) "
            f"parsed. **A sitemap with URLs and no advertisements is a "
            f"reading that failed, not an empty board** — the file is there "
            f"and this reader got nothing out of it.", EXIT_PARTIAL)
    note(f"{counts['loc']} <loc>: {len(rows)} advertisement(s), "
         f"{counts['category']} category page(s), {counts['duplicate']} "
         f"duplicate(s). **Counting the file would report the board "
         f"{100 * (counts['loc'] - len(rows)) / len(rows):.1f} % larger.**")
    if a.since and not a.fetch:
        die("`--since` needs `--fetch`. **The sitemap's `lastmod` is not a "
            "publication date on this board** — it moves when a page is "
            "fetched, and our own reads moved six of them in under eight minutes. "
            "Filtering on it would return almost the whole board and call it "
            "recent. With `--fetch` the filter applies to the "
            "advertisement's own `datePosted`.")
    if a.live and not a.fetch:
        die("`--live` needs `--fetch`: `validThrough` is on the "
            "advertisement, not in the sitemap.")
    if a.search and not a.fetch:
        rows = [r for r in rows if fold(a.search) in fold(r["slug"])]
    if not a.fetch:
        held = len(rows)
        if a.limit:
            rows = rows[: a.limit]
        print(json.dumps({"source": "ihararejobs", "country": "ZW",
                          "sitemap_locs": counts["loc"],
                          "advertisements": held,
                          "returned": len(rows),
                          "category_pages": counts["category"],
                          "duplicate_locs": counts["duplicate"],
                          "note": "`sitemap_lastmod` is when the page was "
                                  "last touched — our reads move it. Use "
                                  "--fetch for the real `posted`",
                          "ads": rows}, ensure_ascii=False, indent=1))
        return
    if a.limit:
        rows = rows[: a.limit]
    note(f"opening {len(rows)} page(s) at {_PACE.source()}. **Each one moves "
         f"that advertisement's `lastmod` to today** — see the module "
         f"docstring before sweeping the whole board.")
    kept, broken, dropped, lax = [], [], 0, 0
    for row in rows:
        code, page = get(row["url"])
        if code in (404, 410):
            broken.append((row["slug"], f"HTTP {code}"))
            continue
        if code != 200:
            broken.append((row["slug"], f"HTTP {code}"))
            continue
        posting, why, mode = posting_on(page)
        if posting is None:
            broken.append((row["slug"],
                           "gone — HTTP 200 serving the listing page"
                           if SOFT_404.search(page) else why))
            continue
        if mode == "lax":
            lax += 1
        c = card(row["url"], row, posting, mode)
        if a.since and (not c["posted"] or c["posted"] < a.since):
            dropped += 1
            continue
        if a.live and c["valid_through"] and c["valid_through"] < a.today:
            dropped += 1
            continue
        if a.search and fold(a.search) not in fold(c["title"] or ""):
            continue
        kept.append(c)
    if lax:
        note(f"{lax} of {len(kept) + len(broken) + dropped} needed the lax "
             f"JSON pass. **A parser that tries once reads those as having "
             f"no structured data** — a confident zero.")
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{s} ({w})" for s, w in broken[:5]))
    print(json.dumps({"source": "ihararejobs", "country": "ZW",
                      "read": len(kept) + len(broken) + dropped,
                      "kept": len(kept), "unreadable": len(broken),
                      "filtered_out": dropped, "lax_json": lax,
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}/job/{a.slug.strip('/')}/"
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.slug} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    posting, why, mode = posting_on(page)
    if posting is None:
        if SOFT_404.search(page):
            die(f"{a.slug} is gone: this host answers an unknown "
                f"advertisement with HTTP 200 and its listing page. Record "
                f"it as discarded.", EXIT_GONE)
        die(f"{url}: {why}")
    ident = ID_IN_URL.search(url)
    row = {"source": "ihararejobs", "url": url, "slug": slug_of(url),
           "id": ident.group(1) if ident else None,
           "ledger_id": f"ihararejobs:{ident.group(1) if ident else slug_of(url)}",
           "countries": ["ZW"]}
    print(json.dumps(card(url, row, posting, mode),
                     ensure_ascii=False, indent=1))


def main():
    import datetime
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="advertisements from the sitemap")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for the real `datePosted`, employer "
                         "and city. **It also moves that advertisement's "
                         "sitemap `lastmod` to today** — this board's dates "
                         "record visits")
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="the advertisement's own `datePosted`. Requires "
                         "--fetch: the sitemap's date records our reads")
    li.add_argument("--live", action="store_true",
                    help="drop advertisements whose `validThrough` has "
                         "passed. Requires --fetch")
    li.add_argument("--search", help="matches the slug alone without --fetch, "
                                     "and the title with it; folds accents")
    li.add_argument("--limit", type=int)
    li.set_defaults(func=cmd_list,
                    today=datetime.date.today().isoformat())

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad, today=datetime.date.today().isoformat())

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
