#!/usr/bin/env python3
"""Job Search Zambia — the dated half of Zambia's three boards.

    jobsearchzm.py list [--since YYYY-MM-DD] [--live] [--fetch] [--limit N]
    jobsearchzm.py ad --slug zambia-it-operations-intern

THE SITEMAP CARRIES DATES, AND THAT IS THE DIFFERENCE FROM ITS NEIGHBOUR

`gozambiajobs.py` refuses `--since` because its sitemap has no `<lastmod>` at
all. **This one has 23 distinct dates over 153 entries** (2026-07-15 →
2026-09-04, heaviest day 24), so `--since` is answered from the listing —
**one request rather than 153.**

*A date filter is only as good as the field it reads. Here the field exists at
the listing level, and the count it produces is checkable against the
distribution published in `shared/boards/jobsearchzm.md`.*

THREE SHAPES THAT DIFFER FROM THE NEIGHBOURING BOARD, EACH MEASURED FIRST

Read on 2026-09-05 before this file was written, because assuming them would
have produced empty fields in silence:

    jobLocation.address   a STRING — "Kabwe" — not a PostalAddress object
    employmentType        a LIST — ["INTERN"] — not a bare string
    title                 DOUBLE-escaped: "&amp;#8211;" for an en dash

**The third is the one that bites quietly.** One `html.unescape` leaves
`&#8211;` sitting in the title; it takes a second pass. *A publisher that
HTML-escapes an entity that was already an entity is the same fault that broke
an ld+json block on another board — there it raised, here it just looks wrong.*

WHAT IT DOES NOT DO

**It writes nothing to disk**, like every adapter here. And it does not treat a
missing `validThrough` as expired: `--live` keeps what carries no end date,
because *absent* is not *past*.
"""

import argparse
import datetime
import html as html_mod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _robots import allowed as robots_allowed
from _ua import UA

BASE = "https://jobsearchzm.com"
SITEMAP = BASE + "/job_listing-sitemap.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobsearchzm] {msg}", file=sys.stderr)


def gate(url):
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
        "Accept-Language": "en-GB,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def slug_of(url):
    return url.rstrip("/").rsplit("/", 1)[-1]


def unescape2(s):
    """Twice, because this publisher escapes entities that were entities."""
    return html_mod.unescape(html_mod.unescape(s or "")).strip()


def entries():
    """(url, lastmod) from the listing. The dates are the point of this board."""
    code, body = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    rows, seen = [], set()
    for block in ENTRY.findall(body):
        u = LOC.search(block)
        if not u:
            continue
        url = u.group(1).strip()
        # A count of <loc> is not a count of advertisements; only /job/ is one.
        if "/job/" not in url or url in seen:
            continue
        seen.add(url)
        d = LASTMOD.search(block)
        rows.append((url, d.group(1) if d else None))
    return rows


def posting_on(page):
    for block in LDJSON.findall(page):
        try:
            data = json.loads(block, strict=False)
        except ValueError:
            return None, "ld+json present and unparseable"
        for obj in (data if isinstance(data, list) else [data]):
            if isinstance(obj, dict) and obj.get("@type") == "JobPosting":
                return obj, None
    return None, "no JobPosting in ld+json"


def one(v):
    """employmentType arrives as a list here, as a string on the neighbour."""
    if isinstance(v, list):
        return v[0] if v else None
    return v


def town_of(posting):
    """`address` is a plain string on this board, not a PostalAddress."""
    loc = posting.get("jobLocation")
    loc = loc[0] if isinstance(loc, list) and loc else loc
    if not isinstance(loc, dict):
        return None
    addr = loc.get("address")
    if isinstance(addr, str):
        return addr.strip() or None
    if isinstance(addr, dict):
        return addr.get("addressLocality") or addr.get("addressRegion")
    return None


def card(url, lastmod, posting):
    org = posting.get("hiringOrganization") or {}
    return {
        "id": "jobsearchzm:" + slug_of(url),
        "url": url,
        "title": unescape2(posting.get("title")),
        "employer": org.get("name") if isinstance(org, dict) else org,
        "town": town_of(posting),
        "country": "Zambia",
        "posted": (posting.get("datePosted") or "")[:10] or lastmod,
        "valid_through": (posting.get("validThrough") or "")[:10] or None,
        "employment_type": one(posting.get("employmentType")),
    }


def cmd_list(a):
    rows = entries()
    raw = len(rows)
    if a.since:
        rows = [(u, d) for u, d in rows if d and d >= a.since]
    if a.limit:
        rows = rows[:a.limit]

    if not a.fetch:
        note(f"{raw} in the sitemap, {len(rows)} after filters, listed without "
             f"opening them: one request instead of {len(rows)}. Dates are the "
             f"sitemap's <lastmod>.")
        print(json.dumps({"source": "jobsearchzm", "country": "ZM",
                          "sitemap_entries": raw, "selected": len(rows),
                          "fetched": False,
                          "ads": [{"id": "jobsearchzm:" + slug_of(u),
                                   "url": u, "posted": d} for u, d in rows]},
                         ensure_ascii=False, indent=1))
        return

    today = datetime.date.today().isoformat()
    kept, broken, expired = [], [], 0
    for u, d in rows:
        code, page = get(u)
        if code != 200:
            broken.append((u, f"HTTP {code}"))
            continue
        posting, why = posting_on(page)
        if posting is None:
            broken.append((u, why))
            continue
        c = card(u, d, posting)
        # Absent is not past: an advertisement with no end date is kept.
        if a.live and c["valid_through"] and c["valid_through"] < today:
            expired += 1
            continue
        kept.append(c)

    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{slug_of(u)} ({w})" for u, w in broken[:5]))
    if a.live:
        note(f"{expired} dropped on a past `validThrough`; those without one "
             f"are kept.")
    print(json.dumps({"source": "jobsearchzm", "country": "ZM",
                      "sitemap_entries": raw, "read": len(kept) + len(broken),
                      "kept": len(kept), "unreadable": len(broken),
                      "expired_dropped": expired if a.live else None,
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}/job/{a.slug}/"
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.slug} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
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

    li = sub.add_parser("list", help="advertisements from the sitemap")
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="filters on the sitemap's own <lastmod>; no page is "
                         "opened for it")
    li.add_argument("--live", action="store_true",
                    help="needs --fetch: drops a past `validThrough`, keeps "
                         "an absent one")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for its fields")
    li.add_argument("--limit", type=int)
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    if a.cmd == "list" and a.live and not a.fetch:
        die("--live needs --fetch: `validThrough` lives on the page, not in "
            "the sitemap.", EXIT_UNKNOWN)
    a.func(a)


if __name__ == "__main__":
    main()
