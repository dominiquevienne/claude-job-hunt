#!/usr/bin/env python3
"""BeBee (`bebee.com`) — an aggregator, read through the sitemap index its own
`robots.txt` declares. Plain HTTP, no key, no cookie, no browser.

    bebee.py countries
    bebee.py list --country ch [--files N] [--limit N] [--fetch]
    bebee.py ad --url https://bebee.com/ch/jobs/<slug>

THE LIST WAS NEVER MISSING — WE WERE LOOKING IN THE MARKUP

This board's card said `indeterminate` because the home page carries no
enumerable list. *That was true of the markup, and it was read as a statement
about the board.* **`robots.txt` declares `Sitemap: https://bebee.com/sitemaps`,
and that index IS the list** — 3 407 children on 2026-09-08, of which 2 102 are
job files across 99 countries.

**And the asymmetry is worth knowing before editing this file**: `robots.txt`
disallows `/*?*page=`, `/*?*q=`, `/*?*sort=` and `/*?*location=`, so **the
paginated search is closed and the sitemap is not**. *A refusal on one path is
not a refusal on the host.* Never reach for the search to page further.

THE ANCHOR IS THE FILE'S OWN LENGTH, PRINTED BESIDE OUR COUNT

    50000 <loc> in this file: 50000 advertisement(s)

**The left number is counted before anything is parsed** — it is the raw
element count of the document the host served. *No empty board and no broken
reader can produce that sentence with a number on both sides*, which is what
issue #181 asks an adapter to make impossible.

IT IS AN AGGREGATOR, AND THE POSTER IS NOT THE EMPLOYER

**BeBee republishes other boards' postings** — the first Swiss address sampled
names `Equal.Jobs`, itself a Swiss board. So `hiringOrganization` can name the
republisher, and this adapter emits **`poster`**, never `employer`.

*`rocken.jobs` publishes 6 105 advertisements under one name and the field is
present, populated and wrong; `jobeo.ch` carries the real employer in the same
field.* **What is true of all three is that the field is the POSTER.**

WHAT THIS ADAPTER DOES NOT CLAIM

**The duplicate rate against the origin boards is NOT established**, and this
docstring does not guess it. *Fifty thousand Swiss addresses over six days is
about 8 300 a day, which no Swiss labour market produces* — the number counts
republished postings, and turning it into a market figure needs the origin
boards. **A duplicate is established by employer, title and city together —
never by a date two publishers set separately.**
"""

import argparse
import collections
import datetime
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _ldjson import objects as ldjson_objects
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BASE = "https://bebee.com"
INDEX = BASE + "/sitemaps"          # declared by robots.txt, not guessed
JOBS_PREFIX = "/sitemaps/jobs/"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL, EXIT_REFUSED, EXIT_UNKNOWN = 2, 3, 6, 7, 8

LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(\d{4}-\d{2}-\d{2})")
AD_PATH = re.compile(r"^/([a-z]{2})/jobs/([^/?#]+)$")

_PACE = Pace("bebee.com", own=1.0)
_ANNOUNCED = False


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[bebee] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)


def get(url):
    global _ANNOUNCED
    gate(url)
    if not _ANNOUNCED:
        _ANNOUNCED = True
        note(_PACE.source())
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "application/xml,text/html;q=0.9,*/*;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def index_children():
    code, body = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}")
    locs = LOC.findall(body)
    jobs = [u for u in locs
            if urllib.parse.urlsplit(u).path.startswith(JOBS_PREFIX)]
    note(f"{len(locs)} <loc> in the index: {len(jobs)} job file(s). "
         f"The index is declared by robots.txt, not guessed.")
    return jobs


def files_for(country, children):
    """The numbered files of one country, in order, `delta-` ones last.

    **`delta-` files are separated and counted, never merged silently.** They
    are incremental updates and a caller reading only the numbered files must
    know how many it left.
    """
    pre = f"{JOBS_PREFIX}{country}"
    mine = [u for u in children
            if urllib.parse.urlsplit(u).path.rstrip("/") == pre
            or urllib.parse.urlsplit(u).path.startswith(pre + "/")]
    numbered = [u for u in mine if "delta-" not in u]
    deltas = [u for u in mine if "delta-" in u]

    def rank(u):
        m = re.search(r"/(\d+)$", urllib.parse.urlsplit(u).path)
        return int(m.group(1)) if m else 1
    return sorted(numbered, key=rank), deltas


def read_file(url, country):
    """One sitemap file. Returns (raw_loc_count, rows).

    **The raw count is taken before anything is parsed** — that is the anchor,
    and it must not come from the same pass that filters.
    """
    code, body = get(url)
    if code != 200:
        note(f"{url}: HTTP {code}")
        return 0, []
    raw = len(LOC.findall(body))
    rows = []
    for blk in ENTRY.findall(body):
        m = LOC.search(blk)
        if not m:
            continue
        u = m.group(1).strip()
        p = AD_PATH.match(urllib.parse.urlsplit(u).path)
        if not p or p.group(1) != country:
            continue
        d = LASTMOD.search(blk)
        rows.append((u, p.group(2), d.group(1) if d else None))
    note(f"{raw} <loc> in this file: {len(rows)} advertisement(s)")
    return raw, rows


def card(url, slug, lastmod, page):
    job = None
    for o in ldjson_objects(page):
        if isinstance(o, dict) and o.get("@type") == "JobPosting":
            job = o
            break
    if not job:
        return {"id": "bebee:" + slug, "url": url, "posted_sitemap": lastmod,
                "missing_fields": ["JobPosting"]}
    loc = job.get("jobLocation")
    if isinstance(loc, list):
        loc = loc[0] if loc else None
    addr = (loc or {}).get("address") if isinstance(loc, dict) else {}
    addr = addr or {}
    row = {
        "id": "bebee:" + slug,
        "url": url,
        "title": job.get("title"),
        # **`poster`, never `employer`.** This is an aggregator: the field can
        # name the board that republished the posting.
        "poster": (job.get("hiringOrganization") or {}).get("name"),
        "locality": addr.get("addressLocality"),
        "country": addr.get("addressCountry"),
        "posted": job.get("datePosted"),
        "valid_through": job.get("validThrough"),
        "posted_sitemap": lastmod,
        "countries": ["CH"],
    }
    missing = [k for k in ("title", "posted") if not row[k]]
    row["missing_fields"] = missing or None
    return row


def cmd_countries(a):
    children = index_children()
    per = collections.Counter(
        urllib.parse.urlsplit(u).path[len(JOBS_PREFIX):].split("/")[0]
        for u in children)
    print(json.dumps({"source": "bebee", "job_files": len(children),
                      "countries": len(per),
                      "files_per_country": dict(per.most_common())},
                     ensure_ascii=False, indent=1))


def cmd_list(a):
    if a.since and not a.fetch:
        die("`--since` needs `--fetch`. The sitemap's `<lastmod>` equalled "
            "`datePosted` on 2 of 2 advertisements read, and two is not a "
            "rule — the date is taken from the advertisement.", EXIT_UNKNOWN)

    children = index_children()
    numbered, deltas = files_for(a.country, children)
    if not numbered:
        die(f"the index declares no job file for `{a.country}`. It declares "
            f"{len(children)} in all; run `countries` to see which.", EXIT_GONE)
    note(f"country `{a.country}`: {len(numbered)} numbered file(s) and "
         f"{len(deltas)} `delta-` file(s). **The deltas are counted and NOT "
         f"read here** — they are incremental updates, and merging them "
         f"silently would make this run's denominator unreproducible.")

    want = numbered[:a.files] if a.files else numbered
    seen, rows, raw_total, dups = {}, [], 0, []
    for i, u in enumerate(want, 1):
        raw, got = read_file(u, a.country)
        raw_total += raw
        for url, slug, lm in got:
            if slug in seen:
                dups.append((slug, seen[slug], i))
                continue
            seen[slug] = i
            rows.append((url, slug, lm))
        if a.limit and len(rows) >= a.limit:
            break
    # **The summary is computed BEFORE `--limit` truncates.** Printing five
    # kept rows against fifty thousand `<loc>` reads as a catastrophic
    # shortfall when it is a ceiling the caller asked for — the same defect
    # `rocken.py` carried for one commit.
    distinct = len(rows)
    if a.limit:
        rows = rows[:a.limit]

    if dups:
        note(f"{len(dups)} address(es) appear in more than one file:")
        for s, f1, f2 in dups[:5]:
            note(f"    file {f1} then file {f2}  {s[:60]}")
    else:
        note(f"{raw_total} <loc> read across {len(want)} file(s): "
             f"{distinct} distinct advertisement(s), none shared between "
             f"files. **This line prints either way.**")
    if a.limit and distinct > len(rows):
        note(f"--limit {a.limit} kept {len(rows)} of the {distinct} read. "
             f"**The ceiling is the caller's, not a shortfall.**")

    if len(want) < len(numbered):
        note(f"{len(want)} of {len(numbered)} numbered files read on purpose — "
             f"**no total for `{a.country}` is claimed by this run.**")

    if not a.fetch:
        print(json.dumps({"source": "bebee", "country": a.country.upper(),
                          "files_declared": len(numbered),
                          "delta_files_not_read": len(deltas),
                          "files_read": len(want), "loc_read": raw_total,
                          "found": len(rows), "duplicates": len(dups),
                          "fetched": False,
                          "ads": [{"id": "bebee:" + s, "url": u,
                                   "posted_sitemap": d} for u, s, d in rows]},
                         ensure_ascii=False, indent=1))
        return

    kept, broken, incomplete = [], [], []
    for url, slug, lm in rows:
        code, page = get(url)
        if code != 200:
            broken.append((slug, f"HTTP {code}"))
            continue
        c = card(url, slug, lm, page)
        if c.get("missing_fields"):
            incomplete.append((slug, c["missing_fields"]))
        kept.append(c)
    if a.since:
        before = len(kept)
        kept = [c for c in kept if not c.get("posted") or c["posted"] >= a.since]
        note(f"--since {a.since}: {len(kept)} of {before}; an advertisement "
             f"with no `datePosted` is kept — absent is not old.")
    if incomplete:
        note(f"{len(incomplete)} of {len(rows)} advertisements are missing a "
             f"required field. Each is named:")
        for s, f in incomplete:
            note(f"    {s[:52]:>52}  missing {', '.join(f)}")
    else:
        note(f"every one of {len(rows)} advertisements yielded a title and a "
             f"posting date. **Negative control**: printed either way.")
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{s[:28]} ({w})" for s, w in broken[:5]))

    print(json.dumps({"source": "bebee", "country": a.country.upper(),
                      "files_declared": len(numbered),
                      "delta_files_not_read": len(deltas),
                      "files_read": len(want), "loc_read": raw_total,
                      "found": len(rows), "duplicates": len(dups),
                      "kept": len(kept), "unreadable": len(broken),
                      "incomplete": len(incomplete),
                      "as_of": datetime.date.today().isoformat(),
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken or incomplete:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    p = AD_PATH.match(urllib.parse.urlsplit(a.url).path)
    if not p:
        die("--url must be /<cc>/jobs/<slug>")
    code, page = get(a.url)
    if code in (404, 410):
        die(f"{a.url} is gone (HTTP {code}). Record it as discarded.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}")
    c = card(a.url, p.group(2), None, page)
    print(json.dumps(c, ensure_ascii=False, indent=1))
    if c.get("missing_fields"):
        note(f"missing: {', '.join(c['missing_fields'])}")
        sys.exit(EXIT_PARTIAL)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    co = sub.add_parser("countries")
    co.set_defaults(fn=cmd_countries)
    li = sub.add_parser("list")
    li.add_argument("--country", required=True,
                    help="two-letter code as the index spells it, e.g. `ch`")
    li.add_argument("--files", type=int, default=1,
                    help="numbered files to read; default 1, and the run says "
                         "so rather than claiming a total")
    li.add_argument("--limit", type=int)
    li.add_argument("--fetch", action="store_true")
    li.add_argument("--since", help="YYYY-MM-DD, needs --fetch")
    li.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
