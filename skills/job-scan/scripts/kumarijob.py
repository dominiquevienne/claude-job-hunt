#!/usr/bin/env python3
"""Kumari Job — Nepal's open stock, and the only one of four still readable.

    kumarijob.py list [--since YYYY-MM-DD] [--live] [--fetch] [--limit N]
    kumarijob.py ad --url https://www.kumarijob.com/<employer>/<id>-<slug>

THREE FILES SAY "JOB" AND ONE HOLDS ADVERTISEMENTS

The index names eight children. Measured 2026-09-07, before this file was
written:

    sitemap-jobs.xml                167 advertisements
    sitemap-job-listings.xml         21 FACETS — /job-listing/banking-jobs-in-nepal
    sitemap-other-job-listings.xml   39 FACETS — jobs-by-city, employment-types

**Reading "every sitemap whose name says job" would report 227.** That is the
sibling-file trap `shared/robots-policy.md` records for `merojob.com`, where
`sitemap-tender_post-1.xml.gz` sits beside the jobs file with 15 940 tenders —
**the same shape with the categories inverted**: there a name that does not say
"job" holds non-jobs, here two names that DO say job hold none.

*So this adapter names one file and never globs. The two facet files carry a
single `lastmod` of 2026-05-22 against the ad file's daily one, which is a
second, independent signal that they are not the same kind of thing.*

THE SITEMAP'S DATE IS THE FILE'S, NOT THE ADVERTISEMENT'S

`sitemap-jobs.xml` carries **2 distinct `<lastmod>` over 167 entries** — the
regeneration, not the posting. The advertisements themselves span at least
**2026-08-20 → 2026-09-07** on the three read.

**So `--since` is refused without `--fetch`,** in code, with exit 8. Filtering
on a regeneration date would return everything or nothing and look like a
working filter either way. *This is the opposite of `jobsearchzm.py`, whose
listing carries 23 real dates and answers `--since` in one request; the
difference is measured, not assumed.*

TWO VOCABULARIES FOR ONE FIELD, ON THE SAME BOARD

    ad 76693   employmentType  "FULL_TIME"     schema.org's enumeration
    ad 76273   employmentType  "Full Time"     free text
    ad 75603   employmentType  "Full Time"

**One publisher, two spellings, read on three advertisements out of three
employers.** `norm_type()` folds them and keeps the original beside it, because
a fold that loses the source cannot be audited later.

WHAT WAS MEASURED BEFORE THIS FILE EXISTED

`jobLocation.address` is a **PostalAddress object** here — `streetAddress`,
`addressLocality` — where the Zambian neighbour serves a plain string.
`baseSalary` is absent on three of three. `validThrough` is present on three of
three, which is rare enough that `--live` is worth having.

WHAT IT DOES NOT DO

**It writes nothing to disk.** And it does not treat a missing `validThrough`
as expired: *absent is not past.*
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
from _pace import Pace
from _robots import allowed as robots_allowed, full_path
from _ua import UA

BASE = "https://www.kumarijob.com"
SITEMAP = BASE + "/sitemap-jobs.xml"

# **Named, never globbed.** The two below are facets and are listed so that a
# reader sees they were considered rather than missed.
NOT_ADVERTISEMENTS = ("/sitemap-job-listings.xml", "/sitemap-other-job-listings.xml")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)
# /<employer>/<id>-<slug> — two segments, the first is the employer.
AD_PATH = re.compile(r"^/([^/]+)/(\d+)-([^/]+)/?$")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[kumarijob] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)


# **A `list --fetch` opens 167 advertisements on one host.** The board declares
# no `Crawl-delay` today; `Pace` reads it live rather than trusting that — *a
# rate absent when a file is written is not a rate absent for ever* — and falls
# back to one second of ours, declared as ours.
_PACE = Pace("www.kumarijob.com", own=1.0)
_ANNOUNCED = False


def get(url):
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
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def parts_of(url):
    """(employer, id, slug) or None — the shape decides what is an ad."""
    m = AD_PATH.match(urllib.parse.urlsplit(url).path)
    return m.groups() if m else None


def unescape2(s):
    """Twice, and on every free-text field rather than the title alone."""
    if s is None:
        return None
    return html_mod.unescape(html_mod.unescape(str(s))).strip() or None


def norm_type(v):
    """Fold the two spellings this one board uses, and keep the original.

    **A fold that loses its source cannot be audited**, and the two forms were
    measured on the same board on the same day.
    """
    if isinstance(v, list):
        v = v[0] if v else None
    if v is None:
        return None, None
    folded = re.sub(r"[\s-]+", "_", str(v).strip()).upper()
    return folded, str(v)


def town_of(posting):
    """`address` is a PostalAddress object here, not a string."""
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


def entries():
    """(url, employer, lastmod). The lastmod is the FILE's, not the ad's."""
    code, body = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    rows, seen, skipped = [], set(), 0
    for block in ENTRY.findall(body):
        u = LOC.search(block)
        if not u:
            continue
        url = u.group(1).strip()
        p = parts_of(url)
        if p is None:
            skipped += 1          # a facet or a page, counted rather than lost
            continue
        if url in seen:
            continue
        seen.add(url)
        d = LASTMOD.search(block)
        rows.append((url, p[0], d.group(1) if d else None))
    if skipped:
        note(f"{skipped} entries in {SITEMAP} do not have the "
             f"/<employer>/<id>-<slug> shape and are not counted as ads.")
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


def card(url, employer_slug, lastmod, posting):
    org = posting.get("hiringOrganization") or {}
    folded, raw_type = norm_type(posting.get("employmentType"))
    p = parts_of(url)
    return {
        "id": "kumarijob:" + (p[1] if p else url),
        "url": url,
        "title": unescape2(posting.get("title")),
        "employer": unescape2(org.get("name") if isinstance(org, dict) else org),
        "employer_slug": employer_slug,
        "town": unescape2(town_of(posting)),
        "country": "Nepal",
        "posted": (posting.get("datePosted") or "")[:10] or None,
        "valid_through": (posting.get("validThrough") or "")[:10] or None,
        "employment_type": folded,
        "employment_type_raw": raw_type,
        # The file's regeneration date, kept apart from the ad's own date so
        # nobody mistakes one for the other.
        "sitemap_lastmod": lastmod,
    }


def cmd_list(a):
    if a.since and not a.fetch:
        die("`--since` needs `--fetch` on this board. The sitemap's <lastmod> "
            "is the FILE's regeneration date — 2 distinct values over 167 "
            "entries on 2026-09-07 — while the advertisements span at least "
            "2026-08-20 to 2026-09-07. Filtering on it would return all or "
            "nothing and look like a working filter either way.", EXIT_UNKNOWN)
    if a.live and not a.fetch:
        die("`--live` needs `--fetch`: `validThrough` lives on the "
            "advertisement, not in the listing.", EXIT_UNKNOWN)

    rows = entries()
    raw = len(rows)
    if a.limit:
        rows = rows[:a.limit]

    if not a.fetch:
        note(f"{raw} advertisements in {SITEMAP}, {len(rows)} after --limit, "
             f"listed without opening them. **No date is offered here**: the "
             f"listing dates the file, not the ads.")
        print(json.dumps({"source": "kumarijob", "country": "NP",
                          "sitemap_entries": raw, "selected": len(rows),
                          "fetched": False,
                          "ads": [{"id": "kumarijob:" + (parts_of(u)[1]),
                                   "url": u, "employer_slug": e,
                                   "sitemap_lastmod": d}
                                  for u, e, d in rows]},
                         ensure_ascii=False, indent=1))
        return

    today = datetime.date.today().isoformat()
    kept, broken, expired, dropped_old = [], [], 0, 0
    for u, e, d in rows:
        code, page = get(u)
        if code != 200:
            broken.append((u, f"HTTP {code}"))
            continue
        posting, why = posting_on(page)
        if posting is None:
            broken.append((u, why))
            continue
        c = card(u, e, d, posting)
        if a.since and (c["posted"] or "") < a.since:
            dropped_old += 1
            continue
        if a.live and c["valid_through"] and c["valid_through"] < today:
            expired += 1
            continue
        kept.append(c)

    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{u.rsplit('/', 1)[-1]} ({w})" for u, w in broken[:5]))
    if a.since:
        note(f"{dropped_old} dropped as posted before {a.since}; an ad with no "
             f"`datePosted` is dropped too and counted here.")
    if a.live:
        note(f"{expired} dropped on a past `validThrough`; those without one "
             f"are kept — absent is not past.")
    print(json.dumps({"source": "kumarijob", "country": "NP",
                      "sitemap_entries": raw, "read": len(kept) + len(broken)
                      + dropped_old + expired,
                      "kept": len(kept), "unreadable": len(broken),
                      "expired_dropped": expired if a.live else None,
                      "older_dropped": dropped_old if a.since else None,
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = a.url
    if parts_of(url) is None:
        die("--url must be a full advertisement address of the form "
            "https://www.kumarijob.com/<employer>/<id>-<slug>. **No URL is "
            "composed from a slug here**: the employer segment is part of the "
            "address and guessing it would fabricate a host path.")
    code, page = get(url)
    if code in (404, 410):
        die(f"{url} is gone (HTTP {code}). Record it as discarded.", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    posting, why = posting_on(page)
    if posting is None:
        die(f"{url}: {why}")
    p = parts_of(url)
    print(json.dumps(card(url, p[0], None, posting),
                     ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    li = sub.add_parser("list", help="the advertisement sitemap")
    li.add_argument("--since", help="YYYY-MM-DD on the ad's own datePosted; "
                                    "requires --fetch")
    li.add_argument("--live", action="store_true",
                    help="drop ads whose validThrough has passed; requires --fetch")
    li.add_argument("--fetch", action="store_true", help="open each ad")
    li.add_argument("--limit", type=int)
    li.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad", help="one advertisement")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
