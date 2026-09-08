#!/usr/bin/env python3
"""Todas Vagas — Mozambique's first adapter, and its listing runs newest first.

    todasvagas.py list [--since YYYY-MM-DD] [--live] [--fetch] [--limit N]
    todasvagas.py ad --url https://todasvagas.com/vaga/<slug>

ONE FLAT SITEMAP, TWO KINDS OF THING, AND THE PATH SORTS THEM

`https://todasvagas.com/sitemap.xml` is not an index: **914 `<loc>` in one
file.** Measured 2026-09-08:

    /vaga/<slug>     855   advertisements
    /dicas/<slug>     52   articles — tips, not jobs
    seven site pages   7   /, /vagas, /empresas, /sobre, /contacto, …

**So the path decides, as it did on Nepal's three boards.** *Neither a filename
nor a `lastmod` could help here: there is one file and its dates are all the
same day.*

THE SITEMAP DATES THE REGENERATION, AND ALL OF IT AT ONCE

    900 of 914 entries carry 2026-09-08     the day this was measured
    the advertisements themselves span      2026-01-19 -> 2026-09-08

**`--since` is refused without `--fetch`**, in code, exit 8. *Sixth board on
which a sitemap date is not the advertisement's, and the third distinct way of
failing: here it is not inert and not earlier — it is a single stamp applied to
almost every row.*

`--limit` TAKES THE NEWEST HERE, AND THAT IS THE OPPOSITE OF THE NEIGHBOUR

    entry 0     posted 2026-09-08   validThrough 2026-10-23   LIVE
    entry 300   posted 2026-06-20   validThrough 2026-08-04   expired
    entry 600   posted 2026-03-18   validThrough 2026-05-02   expired
    entry 854   posted 2026-01-19   validThrough 2026-03-05   expired

**The file is ordered newest first**, so truncating reads the freshest end —
where `merojob.py` documents a file ordered the other way and warns that
`--limit` reads the stalest. *The order is a property of one publisher, not of
sitemaps: it was measured on four points here and it is stated as measured.*

**Three of four are expired**, so `--live` is the flag that matters on this
board.

SHAPES READ BEFORE THIS FILE WAS WRITTEN

    validThrough    ISO WITH an offset — "2026-10-23T04:17:13+02:00"
    datePosted      a bare date
    employmentType  a string, "FULL_TIME", 4 of 4
    jobLocation     a Place with a PostalAddress carrying addressLocality
    JobPosting      present 4 of 4

WHAT IT DOES NOT DO

It writes nothing to disk, and a missing `validThrough` is not treated as
expired: *absent is not past.*
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

BASE = "https://todasvagas.com"
SITEMAP = BASE + "/sitemap.xml"
AD_PREFIX = "/vaga/"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)

_PACE = Pace("todasvagas.com", own=1.0)
_ANNOUNCED = False


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[todasvagas] {msg}", file=sys.stderr)


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
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def unescape2(s):
    if s is None:
        return None
    return html_mod.unescape(html_mod.unescape(str(s))).strip() or None


def one(v):
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
    return urllib.parse.urlsplit(url).path.strip("/").rsplit("/", 1)[-1]


def entries():
    """(url, sitemap_lastmod). Everything not under /vaga/ is counted aside."""
    code, body = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    rows, seen, other = [], set(), 0
    for block in ENTRY.findall(body):
        m = LOC.search(block)
        if not m:
            continue
        url = m.group(1).strip()
        if not urllib.parse.urlsplit(url).path.startswith(AD_PREFIX):
            other += 1
            continue
        if url in seen:
            continue
        seen.add(url)
        d = LASTMOD.search(block)
        rows.append((url, d.group(1) if d else None))
    if other:
        note(f"{other} entries are not under {AD_PREFIX} and are NOT counted "
             f"as advertisements — 52 of them are `/dicas/` articles. The "
             f"count is reported rather than the filter assumed to have worked.")
    return rows


def posting_on(page):
    for block in LDJSON.findall(page):
        try:
            data = json.loads(block, strict=False)
        except ValueError:
            continue
        for obj in (data if isinstance(data, list) else [data]):
            if isinstance(obj, dict) and obj.get("@type") == "JobPosting":
                return obj, None
    return None, "no JobPosting in ld+json"


def card(url, lastmod, posting):
    org = posting.get("hiringOrganization") or {}
    return {
        "id": "todasvagas:" + slug_of(url),
        "url": url,
        "title": unescape2(posting.get("title")),
        "employer": unescape2(org.get("name") if isinstance(org, dict) else org),
        "town": unescape2(town_of(posting)),
        "country": "Mozambique",
        "posted": (posting.get("datePosted") or "")[:10] or None,
        # The offset is dropped deliberately: comparing dates, not instants.
        "valid_through": (posting.get("validThrough") or "")[:10] or None,
        "employment_type": one(posting.get("employmentType")),
        # One stamp on 900 of 914 rows — the regeneration, not the posting.
        "sitemap_lastmod_regeneration": lastmod,
    }


def cmd_list(a):
    if a.since and not a.fetch:
        die("`--since` needs `--fetch`. The sitemap stamps 900 of its 914 rows "
            "with one date — the day it was regenerated — while the "
            "advertisements span 2026-01-19 to 2026-09-08. Filtering on it "
            "returns everything or nothing.", EXIT_UNKNOWN)
    if a.live and not a.fetch:
        die("`--live` needs `--fetch`: `validThrough` lives on the "
            "advertisement.", EXIT_UNKNOWN)

    rows = entries()
    raw = len(rows)
    if a.limit:
        rows = rows[:a.limit]
        note(f"--limit takes the FIRST {a.limit} of {raw}, and this file is "
             f"ordered NEWEST first — measured on four points, entry 0 posted "
             f"2026-09-08 and entry 854 posted 2026-01-19. That is the "
             f"opposite of `merojob.py`, where the head is the stalest.")

    if not a.fetch:
        note(f"{raw} advertisements under {AD_PREFIX}, {len(rows)} after "
             f"--limit, listed without opening them. **No date is offered "
             f"here**: the listing carries the regeneration stamp.")
        print(json.dumps({"source": "todasvagas", "country": "MZ",
                          "sitemap_entries": raw, "selected": len(rows),
                          "fetched": False,
                          "ads": [{"id": "todasvagas:" + slug_of(u), "url": u}
                                  for u, _d in rows]},
                         ensure_ascii=False, indent=1))
        return

    if not a.limit:
        note(f"opening {raw} pages at one second apart is about "
             f"{raw // 60} minutes. Three of a four-point sample were expired, "
             f"so `--live` is the flag that matters here.")

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
        note(f"{len(broken)} of {len(rows)} carried no readable JobPosting and "
             f"are COUNTED, not dropped: "
             + "; ".join(f"{slug_of(u)} ({w})" for u, w in broken[:5]))
    if a.since:
        note(f"{old} dropped as posted before {a.since}.")
    if a.live:
        note(f"{expired} dropped on a past `validThrough`; those without one "
             f"are kept — absent is not past.")
    print(json.dumps({"source": "todasvagas", "country": "MZ",
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
    if not urllib.parse.urlsplit(a.url).path.startswith(AD_PREFIX):
        die(f"--url must be an advertisement under {AD_PREFIX}. The same "
            f"sitemap carries 52 `/dicas/` articles, which are not jobs.")
    code, page = get(a.url)
    if code in (404, 410):
        die(f"{a.url} is gone (HTTP {code}). Record it as discarded.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}")
    posting, why = posting_on(page)
    if posting is None:
        die(f"{a.url}: {why}")
    print(json.dumps(card(a.url, None, posting), ensure_ascii=False, indent=1))


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
