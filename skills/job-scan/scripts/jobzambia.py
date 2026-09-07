#!/usr/bin/env python3
"""Job Zambia — dated at the listing, undated at the end.

    jobzambia.py list [--since YYYY-MM-DD] [--fetch] [--limit N]
    jobzambia.py ad --slug corporate-social-investment-officer

`--live` IS REFUSED HERE, AND THE REFUSAL WAS MEASURED

Its sibling `jobsearchzm.py` implements `--live`. This one cannot: **twelve
advertisements were read on 2026-09-05 and none of the twelve carried a
`validThrough`.** So the option is refused rather than accepted and left
without effect.

*A `--live` that never drops anything is indistinguishable from a board on
which nothing expires.* The first reading of this board saw one advertisement
without an end date; one observation would not have justified wiring a refusal,
so twelve were read before this line was written.

`--since` IS IMPLEMENTED, AND FOR THE OPPOSITE REASON

The sitemap carries `<lastmod>` on every entry — **18 distinct dates over 45
advertisements, heaviest day 4** — so the filter is answered from the listing
and opens no page.

THE SHAPES, MEASURED BEFORE THE CODE WAS WRITTEN

Identical to its sibling and different from `gozambiajobs`, which is why
neither was assumed:

    jobLocation.address   a STRING — "Lusaka, Zambia" — not a PostalAddress,
                          and sometimes a list of four towns in one string
    employmentType        a LIST — ["FULL_TIME"]
    title                 DOUBLE-escaped: "&amp;#8211;" for an en dash

**Every free-text field is unescaped, not only the title** — the control that
checked `title` alone printed a raw entity in `town` on the line above its own
green assertion.
"""

import argparse
import html as html_mod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed
from _ua import UA

BASE = "https://jobzambia.com"
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
    print(f"[jobzambia] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, parts.path or "/")
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)


_PACER = None


def pacer(host):
    """One request per advertisement under `--fetch`, so the host's rate binds.

    The board declares no `Crawl-delay` today; `Pace` reads it live rather than
    trusting that, because *a rate absent at the time of writing is not a rate
    absent for ever* — and a host that starts asking would be ignored by an
    adapter that decided once.
    """
    global _PACER
    if _PACER is None:
        _PACER = Pace(host)
        if _PACER.delay:
            note(_PACER.source())
    return _PACER


def get(url):
    gate(url)
    pacer(urllib.parse.urlsplit(url).netloc).wait()
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
    """Twice, because this publisher escapes entities that were entities.

    Applied to EVERY free-text field. The first run of the shape control
    checked `title` alone and printed `Solwezi &amp; Kalumbila` in `town`
    on the line above its own green assertion.
    """
    if s is None:
        return None
    return html_mod.unescape(html_mod.unescape(s)).strip() or None


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
    # Every free-text field, not just the title: the entity that survived a
    # first run of this control was sitting in `town`, one line below the
    # assertion that only looked at `title`.
    return {
        "id": "jobzambia:" + slug_of(url),
        "url": url,
        "title": unescape2(posting.get("title")),
        "employer": unescape2(org.get("name") if isinstance(org, dict) else org),
        "town": unescape2(town_of(posting)) or None,
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
        print(json.dumps({"source": "jobzambia", "country": "ZM",
                          "sitemap_entries": raw, "selected": len(rows),
                          "fetched": False,
                          "ads": [{"id": "jobzambia:" + slug_of(u),
                                   "url": u, "posted": d} for u, d in rows]},
                         ensure_ascii=False, indent=1))
        return

    kept, broken = [], []
    for u, d in rows:
        code, page = get(u)
        if code != 200:
            broken.append((u, f"HTTP {code}"))
            continue
        posting, why = posting_on(page)
        if posting is None:
            broken.append((u, why))
            continue
        kept.append(card(u, d, posting))

    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{slug_of(u)} ({w})" for u, w in broken[:5]))
    print(json.dumps({"source": "jobzambia", "country": "ZM",
                      "sitemap_entries": raw, "read": len(kept) + len(broken),
                      "kept": len(kept), "unreadable": len(broken),
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
                    help="REFUSED on this board: no advertisement carries a "
                         "`validThrough` (0 of 12 read on 2026-09-05)")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for its fields")
    li.add_argument("--limit", type=int)
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    if a.cmd == "list" and a.live:
        die("--live cannot be answered on this board: no advertisement "
            "carries a `validThrough`. Twelve were read on 2026-09-05 and "
            "none had one, so the filter would drop nothing and the board "
            "would read as one on which nothing expires. Its sibling "
            "jobsearchzm.py does implement --live.", EXIT_UNKNOWN)
    a.func(a)


if __name__ == "__main__":
    main()
