#!/usr/bin/env python3
"""Mero Rojgari — Nepal's largest listing, and it is NOT the archive it looks like.

    merorojgari.py list [--since YYYY-MM-DD] [--live] [--fetch] [--limit N] [--file N]
    merorojgari.py ad --url https://merorojgari.com/job/<slug>/

"ARCHIVE OF 1 766" IS A DESCRIPTION, AND THE MEASUREMENT REFUTES IT

The index's nine `job_listing-sitemap*.xml` all carry `lastmod 2026-07-20` —
**forty-nine days before this file was written** — and the entries inside them
stop there too. *That reads as a board that died in July.*

**It did not.** Four advertisements sampled ACROSS the files, not from the head:

    file 1, entry 0     posted 2026-07-31   validThrough 2026-11-28   LIVE
    file 1, entry 150   posted 2026-07-21   validThrough 2026-11-18   LIVE
    file 5, entry 100   posted 2026-05-31   validThrough 2026-09-28   LIVE
    file 9, entry 90    no `JobPosting` at all, on 98 591 characters of text

**Three of three that carry structured data are live, with end dates running
into November — and every one is posted LATER than the sitemap entry that lists
it.** *So the sitemap stopped regenerating and the advertisements did not stop
living. The stock and the flow classify in opposite directions here, which is
the confusion `shared/boards/…` records as ten times the archive and a fifth of
the flow.*

**A fourth of the sample carries no `JobPosting`.** Those are counted and
reported, never dropped in silence — *a number that silently drops a quarter is
indistinguishable from one that had nothing to drop.*

THE PATH DECIDES, AS IT DID ON THE TWO NEIGHBOURS

    advertisements   /job/<slug>/     200 of 200, 200 of 200, 183 of 183

*Neither the filename nor the `lastmod` was trusted: `merojob.py` documents why
the first fails and `kumarijob.py` why the second does not generalise.*

NINE FILES, DATE-WINDOWED, NEWEST FIRST

    file 1   2026-07-17 -> 2026-07-20      file 5   2026-05-24 -> 2026-05-27
    file 9   2026-04-21 -> 2026-04-24

**`--file N` reads one of the nine** so a caller can reach the recent end
without opening 1 766 pages. **And `--limit` takes the head of whatever was
selected**, which on file 1 is the newest and on file 9 the oldest — *it says so
on every run, because on the neighbouring board the same flag returned five
expired advertisements and looked like a dead board.*

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

BASE = "https://merorojgari.com"
FILES = [f"{BASE}/job_listing-sitemap{n}.xml" for n in range(1, 10)]
AD_PREFIX = "/job/"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)

_PACE = Pace("merorojgari.com", own=1.0)
_ANNOUNCED = False


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[merorojgari] {msg}", file=sys.stderr)


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
        "Accept-Language": "en-GB,en;q=0.9",
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


def entries(which):
    """(url, sitemap_lastmod, file_index). The path decides what is an ad."""
    rows, seen, other = [], set(), 0
    for idx in which:
        u = FILES[idx - 1]
        code, body = get(u)
        if code != 200:
            note(f"{u}: HTTP {code} — this file contributes nothing and is "
                 f"counted as absent, not as empty.")
            continue
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
            rows.append((url, d.group(1) if d else None, idx))
    if other:
        note(f"{other} entries are not under {AD_PREFIX} and are not counted "
             f"as advertisements.")
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


def card(url, lastmod, idx, posting):
    org = posting.get("hiringOrganization") or {}
    return {
        "id": "merorojgari:" + slug_of(url),
        "url": url,
        "title": unescape2(posting.get("title")),
        "employer": unescape2(org.get("name") if isinstance(org, dict) else org),
        "town": unescape2(town_of(posting)),
        "country": "Nepal",
        "posted": (posting.get("datePosted") or "")[:10] or None,
        "valid_through": (posting.get("validThrough") or "")[:10] or None,
        "employment_type": one(posting.get("employmentType")),
        "sitemap_file": idx,
        # **Earlier than the advertisement's own date on 3 of 3 measured.**
        "sitemap_lastmod_earlier": lastmod,
    }


def cmd_list(a):
    if a.since and not a.fetch:
        die("`--since` needs `--fetch`. The sitemap's <lastmod> is EARLIER "
            "than the advertisement's own `datePosted` on 3 of 3 measured — "
            "one entry listed 2026-07-20 carries 2026-07-31 on the page — so "
            "filtering on it drops advertisements that qualify.", EXIT_UNKNOWN)
    if a.live and not a.fetch:
        die("`--live` needs `--fetch`: `validThrough` lives on the "
            "advertisement.", EXIT_UNKNOWN)

    which = [a.file] if a.file else list(range(1, len(FILES) + 1))
    if a.file and not 1 <= a.file <= len(FILES):
        die(f"--file must be 1..{len(FILES)}; file 1 is the most recent "
            f"window and file {len(FILES)} the oldest.")
    rows = entries(which)
    raw = len(rows)
    if a.limit:
        rows = rows[:a.limit]
        note(f"--limit takes the FIRST {a.limit} of {raw}. Within a file the "
             f"head is its own window; across files, file 1 is the newest and "
             f"file {len(FILES)} the oldest. A truncated read is a smoke test, "
             f"never a picture of the board.")

    if not a.fetch:
        note(f"{raw} advertisements across {len(which)} file(s), listed "
             f"without opening them. **The listing's dates run EARLIER than "
             f"the ads' own** and no date is offered here.")
        print(json.dumps({"source": "merorojgari", "country": "NP",
                          "files_read": which, "sitemap_entries": raw,
                          "selected": len(rows), "fetched": False,
                          "ads": [{"id": "merorojgari:" + slug_of(u),
                                   "url": u, "sitemap_file": i}
                                  for u, _d, i in rows]},
                         ensure_ascii=False, indent=1))
        return

    if not a.limit and not a.file:
        note(f"opening {raw} pages at one second apart is about "
             f"{raw // 60} minutes. `--file 1` reads the most recent window "
             f"alone.")

    today = datetime.date.today().isoformat()
    kept, broken, expired, old = [], [], 0, 0
    for u, d, i in rows:
        code, page = get(u)
        if code != 200:
            broken.append((u, f"HTTP {code}"))
            continue
        posting, why = posting_on(page)
        if posting is None:
            broken.append((u, why))
            continue
        c = card(u, d, i, posting)
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
    print(json.dumps({"source": "merorojgari", "country": "NP",
                      "files_read": which, "sitemap_entries": raw,
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
        die(f"--url must be an advertisement under {AD_PREFIX}.")
    code, page = get(a.url)
    if code in (404, 410):
        die(f"{a.url} is gone (HTTP {code}). Record it as discarded.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}")
    posting, why = posting_on(page)
    if posting is None:
        die(f"{a.url}: {why} — a quarter of a four-advertisement sample was "
            f"like this, and the card says so.", EXIT_PARTIAL)
    print(json.dumps(card(a.url, None, None, posting),
                     ensure_ascii=False, indent=1))


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
    li.add_argument("--file", type=int, help="1 (most recent) .. 9 (oldest)")
    li.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
