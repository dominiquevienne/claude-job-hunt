#!/usr/bin/env python3
"""MeroJob — Nepal's largest, and three layers of date of which one is true.

    merojob.py list [--since YYYY-MM-DD] [--live] [--fetch] [--limit N]
    merojob.py ad --url https://merojob.com/<slug>

THE INDEX IS ON ONE HOST AND EVERY CHILD ON ANOTHER

    https://merojob.com/sitemap.xml            the index
    https://sg.merojob.com/sitemap-*.xml.gz    all fourteen children

**`sg.merojob.com` is a host no card declared and no guard had been asked
about** — `shared/robots-policy.md` rule 5. Each URL is gated on the host that
will actually be fetched, and both hosts are declared on this card.

TENDERS ARE NOT FILTERED BY FILENAME HERE — THE PATH DECIDES

`sitemap-tender_post-1.xml.gz` holds **15 940 entries since 2017**, a sibling of
the 239-entry jobs file in the same index. *Reading "every sitemap in the index"
would report 16 179 Nepali jobs.*

**But the filename is not what this adapter trusts, because a filename is not a
predicate.** Measured 2026-09-07:

    jobs     https://merojob.com/<slug>            depth 1, 239 of 239
    tenders  https://merojob.com/etender/<slug>    depth 2, 15 940 of 15 940

**The path separates them cleanly, so `/etender/` is rejected explicitly and
counted** — a second, independent check that the named file is the one intended.
*`kumarijob.py` documents the mirror image: there, two files whose names DO say
"job" hold only facets.*

THREE LAYERS OF DATE, AND ONLY THE DEEPEST IS TRUE

Measured 2026-09-07, and this is why `--since` refuses without `--fetch`:

    the index's <lastmod> for the child   2026-09-07T03:00   regenerated today
    the child's own <lastmod> per entry   2 values over 239: 09-03 and 09-04
    the advertisement's datePosted        2026-08-24 -> 2026-09-07, spread

**An advertisement posted today carries `2026-09-04` in the sitemap.** So the
middle layer is neither the regeneration nor the posting: it is inert, and it
is the one a reader would take for a date. *A `--since` built on it would
return all or nothing and look like a filter that works.*

**A note on how this was nearly got wrong.** The first two advertisements read
were adjacent in the file and both expired, which suggested a frozen archive of
dead ads. **A sample spread across the file — entries 0, 60, 120, 180, 238 —
gives 4 live of 5.** *Two adjacent rows are not a sample; that is the defect
`jobsbotswana.md` carries and it was reproduced here before it was caught.*

`--limit` TAKES THE HEAD, AND THE HEAD IS THE STALEST

    list --fetch --live --limit 5   ->  kept 0, expired 5
    a sample spread over the file   ->  4 live of 5

**The first entries of this file are the oldest advertisements**, so truncating
reads exactly the wrong end. *`--limit` is for a cheap smoke test and says so on
every run; a reader who wants a picture of the board must spread, not truncate —
the two ends are the two worst sampling points.*

SHAPES, READ BEFORE THIS FILE WAS WRITTEN

    employmentType   a LIST — ["FULL_TIME"] — a string on kumarijob.com
    datePosted       full ISO with milliseconds, not a bare date
    validThrough     present 5 of 5
    baseSalary       absent 5 of 5

WHAT IT DOES NOT DO

**It writes nothing to disk**, and a missing `validThrough` is not treated as
expired: *absent is not past.*
"""

import argparse
import datetime
import gzip
import html as html_mod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path
from _ua import UA

BASE = "https://merojob.com"
# **Named, never globbed**, and its host differs from the index's on purpose.
JOBS = "https://sg.merojob.com/sitemap-job_post-1.xml.gz"
TENDERS = "https://sg.merojob.com/sitemap-tender_post-1.xml.gz"
TENDER_PREFIX = "/etender/"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)

# A `list --fetch` opens 239 pages. The board declares no `Crawl-delay` today;
# `Pace` reads it live rather than trusting that, and falls back to a second of
# ours, declared as ours.
_PACE = Pace("merojob.com", own=1.0)
_ANNOUNCED = False


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[merojob] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)


def get(url, binary=False):
    global _ANNOUNCED
    gate(url)
    if not _ANNOUNCED:
        _ANNOUNCED = True
        note(_PACE.source())
    _PACE.wait()
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-GB,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            if binary:
                return r.getcode(), raw
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, b"" if binary else ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def gunzip(raw):
    try:
        return gzip.decompress(raw)
    except (OSError, EOFError):
        return raw          # served uncompressed; the extension promised, it did not attest


def unescape2(s):
    if s is None:
        return None
    return html_mod.unescape(html_mod.unescape(str(s))).strip() or None


def one(v):
    """employmentType is a LIST here and a string on the Nepali neighbour."""
    if isinstance(v, list):
        return v[0] if v else None
    return v


def town_of(posting):
    loc = posting.get("jobLocation")
    loc = loc[0] if isinstance(loc, list) and loc else loc
    if not isinstance(loc, dict):
        return None
    addr = loc.get("address")
    if isinstance(addr, str):
        return addr.strip() or None
    if isinstance(addr, dict):
        return (addr.get("addressLocality") or addr.get("addressRegion")
                or addr.get("streetAddress"))
    return None


def slug_of(url):
    return urllib.parse.urlsplit(url).path.strip("/")


def entries():
    """(url, lastmod). Tenders are rejected BY PATH and counted."""
    code, raw = get(JOBS, binary=True)
    if code != 200:
        die(f"{JOBS}: HTTP {code}")
    # **Through `decode_body`, not by hand.** A gzipped sitemap arrives with no
    # usable charset header once decompressed, so the declaration that counts is
    # the XML's own — and that module reads it and warns once when it falls back.
    body = decode_body(gunzip(raw), None)[0]
    rows, seen, tenders, other = [], set(), 0, 0
    for block in ENTRY.findall(body):
        u = LOC.search(block)
        if not u:
            continue
        url = u.group(1).strip()
        path = urllib.parse.urlsplit(url).path
        if path.startswith(TENDER_PREFIX):
            tenders += 1
            continue
        if path.strip("/").count("/") != 0 or not path.strip("/"):
            other += 1          # not the depth-1 shape an advertisement has
            continue
        if url in seen:
            continue
        seen.add(url)
        d = LASTMOD.search(block)
        rows.append((url, d.group(1) if d else None))
    if tenders:
        note(f"{tenders} entries under {TENDER_PREFIX} rejected BY PATH. The "
             f"sibling file {TENDERS} holds about 15 940 of them; this one is "
             f"expected to hold none, and the count says whether that held.")
    if other:
        note(f"{other} entries are not the depth-1 shape of an advertisement "
             f"and are not counted.")
    return rows


def posting_on(page):
    for block in LDJSON.findall(page):
        try:
            data = json.loads(block, strict=False)
        except ValueError:
            continue            # this board ships more than one ld+json block
        for obj in (data if isinstance(data, list) else [data]):
            if isinstance(obj, dict) and obj.get("@type") == "JobPosting":
                return obj, None
    return None, "no JobPosting in ld+json"


def card(url, lastmod, posting):
    org = posting.get("hiringOrganization") or {}
    return {
        "id": "merojob:" + slug_of(url),
        "url": url,
        "title": unescape2(posting.get("title")),
        "employer": unescape2(org.get("name") if isinstance(org, dict) else org),
        "town": unescape2(town_of(posting)),
        "country": "Nepal",
        "posted": (posting.get("datePosted") or "")[:10] or None,
        "valid_through": (posting.get("validThrough") or "")[:10] or None,
        "employment_type": one(posting.get("employmentType")),
        # Kept apart and named for what it is: neither the regeneration date
        # nor the posting date. An ad posted 2026-09-07 carries 2026-09-04 here.
        "sitemap_lastmod_inert": lastmod,
    }


def cmd_list(a):
    if a.since and not a.fetch:
        die("`--since` needs `--fetch` on this board. The sitemap's <lastmod> "
            "is INERT — 2 distinct values over 239 entries on 2026-09-07, "
            "while an advertisement posted that same day carries 2026-09-04. "
            "It is neither the regeneration date nor the posting date, and a "
            "filter on it returns all or nothing.", EXIT_UNKNOWN)
    if a.live and not a.fetch:
        die("`--live` needs `--fetch`: `validThrough` lives on the "
            "advertisement.", EXIT_UNKNOWN)

    rows = entries()
    raw = len(rows)
    if a.limit:
        rows = rows[:a.limit]
        note(f"--limit takes the FIRST {a.limit} of {raw}, and the head of "
             f"this file is its oldest advertisements: `--live --limit 5` "
             f"keeps none while a spread sample keeps 4 of 5. Use it as a "
             f"smoke test, never as a picture of the board.")

    if not a.fetch:
        note(f"{raw} advertisements in {JOBS}, {len(rows)} after --limit, "
             f"listed without opening them. **No date is offered here.**")
        print(json.dumps({"source": "merojob", "country": "NP",
                          "sitemap_entries": raw, "selected": len(rows),
                          "fetched": False,
                          "ads": [{"id": "merojob:" + slug_of(u), "url": u}
                                  for u, _d in rows]},
                         ensure_ascii=False, indent=1))
        return

    today = datetime.date.today().isoformat()
    kept, broken, expired, old = [], [], 0, 0
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
        if a.since and (c["posted"] or "") < a.since:
            old += 1
            continue
        if a.live and c["valid_through"] and c["valid_through"] < today:
            expired += 1
            continue
        kept.append(c)

    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{slug_of(u)} ({w})" for u, w in broken[:5]))
    if a.since:
        note(f"{old} dropped as posted before {a.since}; an ad with no "
             f"`datePosted` is dropped too and counted here.")
    if a.live:
        note(f"{expired} dropped on a past `validThrough`; those without one "
             f"are kept — absent is not past.")
    print(json.dumps({"source": "merojob", "country": "NP",
                      "sitemap_entries": raw,
                      "read": len(kept) + len(broken) + old + expired,
                      "kept": len(kept), "unreadable": len(broken),
                      "expired_dropped": expired if a.live else None,
                      "older_dropped": old if a.since else None,
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = a.url
    path = urllib.parse.urlsplit(url).path
    if path.startswith(TENDER_PREFIX):
        die(f"{url} is a TENDER, not an advertisement. This board publishes "
            f"about 15 940 of them under {TENDER_PREFIX} and they are not "
            f"jobs.", EXIT_BROKEN)
    code, page = get(url)
    if code in (404, 410):
        die(f"{url} is gone (HTTP {code}). Record it as discarded.", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    posting, why = posting_on(page)
    if posting is None:
        die(f"{url}: {why}")
    print(json.dumps(card(url, None, posting), ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    li = sub.add_parser("list")
    li.add_argument("--since", help="YYYY-MM-DD on the ad's datePosted; needs --fetch")
    li.add_argument("--live", action="store_true", help="needs --fetch")
    li.add_argument("--fetch", action="store_true")
    li.add_argument("--limit", type=int)
    li.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
