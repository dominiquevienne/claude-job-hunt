#!/usr/bin/env python3
"""job.am — Armenia (`job.am`).

  jobam.py list [--since 2026-08-20] [--limit 20] [--search ծրագրավորող] [--fetch]
  jobam.py ad --slug shinararutyun-78613

**Rank 1 in Armenia refuses us, so this is the country's readable market.**

ITS SITEMAP IS A ROLLING THIRTY-DAY WINDOW, AND THAT IS NOT A SIZE

    https://job.am/sitemap/jobs.xml
      2026-09-04 22:38 UTC · 449 518 bytes · 1 185 <loc> · 1 185 distinct · 0 duplicates
      25 dates, 2026-08-06 → 2026-09-04 — exactly thirty calendar days

Another session read the same file at **20:46 UTC** and found **1 231 entries
over 26 dates, 2026-08-05 → 2026-09-04** — thirty-one days.

**Between the two readings the window rolled and took 2026-08-05 with it.** The
gap is 46 advertisements; an average day in this file carries 47.4.

**This is a distinct mechanism from advertisements being added and removed, and
its signature differs: the oldest date vanishes entire.** A count that changes
throughout is a board trading; a count that loses its first day is a retention
window turning over. **So `1 185` is not the size of the board — it is what the
board keeps.**

**And there is no second file to check it against.** `hellojob.az` publishes
`vacancies` and `expired-vacancies`, so a total is conserved when
advertisements move between them and any other cause breaks the sum. Here the
partition is not closed — `jobs`, `companies` and `blog` do not exchange
members — **so the conservation argument is unavailable, and saying so is part
of the measurement.**

WHAT AN ADVERTISEMENT CARRIES, ON FIFTEEN DRAWN AT RANDOM

    title · employer · datePosted · validThrough · jobLocation · description   15/15
    baseSalary                                                                  0/15
    employmentType                                                             15/15 — free text

**Fifteen distinct employers on fifteen advertisements**, so the file is not one
poster's batch. The sample is `random.sample`, not the head or the tail: on
`jobsbotswana.info` the last eight entries were a single advertiser and gave a
rate two and a half times the truth.

**`employmentType` is Armenian free text, not the schema.org vocabulary.**
`Լրիվ դրույք` — full time — on fourteen, `Լրիվ դրույք, Կես դրույք` on one. It
carries real information in a vocabulary the field name does not promise, so it
is emitted as **`employment_type_text`** and never as `employment_type`. The
`kalibrr.md` rule: a field whose meaning depends on a caveat gets a name that
carries the caveat.

*Three boards, three verdicts on one field, in one night: `keejob` returns
`OTHER` on every advertisement and it is dropped; `jobsbotswana` returns the
real enum and it is emitted; here it is free text and it is renamed. **What a
field is worth is a property of the board.***

Verified against the live site on **2026-09-04**.
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

BASE = "https://job.am"
SITEMAP = BASE + "/sitemap/jobs.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobam] {msg}", file=sys.stderr)


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
        "Accept-Language": "hy,en;q=0.8",
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
    rows.sort(key=lambda r: (r[1] or ""), reverse=True)
    return rows, raw


def posting_on(page):
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


def flat(v):
    """A schema.org value that is sometimes a string and sometimes an object.

    `addressCountry` reads `"AM"` on some advertisements and
    `{"@type": "Country", "name": "..."}` on others. Assuming the string form
    raised `AttributeError` on the first fetch — **the variant was in the data
    before it was in the code**, which is the ordinary case and the reason to
    run the adapter rather than reason about the schema.
    """
    if isinstance(v, dict):
        v = v.get("name") or v.get("@id") or ""
    return (v or "").strip() if isinstance(v, str) else None


def card(url, lastmod, posting=None):
    out = {"source": "jobam", "url": url, "slug": slug_of(url),
           "posted": lastmod, "countries": ["AM"]}
    if posting is None:
        return out
    org = posting.get("hiringOrganization") or {}
    place = posting.get("jobLocation") or {}
    addr = (place.get("address") or {}) if isinstance(place, dict) else {}
    out.update({
        "title": html_mod.unescape(posting.get("title") or "").strip() or None,
        "employer": ((org.get("name") or "").strip()
                     if isinstance(org, dict) else None) or None,
        "city": flat(addr.get("addressLocality")) or None,
        "region": flat(addr.get("addressRegion")) or None,
        "country_code": flat(addr.get("addressCountry")) or None,
        "posted": (posting.get("datePosted") or "")[:10] or lastmod,
        "valid_through": (posting.get("validThrough") or "")[:10] or None,
        # **Armenian free text, not the schema.org enum.** Named for what it is,
        # so a caller cannot filter on `FULL_TIME` and silently get nothing.
        "employment_type_text": posting.get("employmentType") or None,
    })
    return out


def cmd_list(a):
    rows, raw = entries()
    dates = sorted({d for _u, d in rows if d})
    note(f"{SITEMAP} · {raw} <loc> · {len(rows)} distinct · "
         f"{len(dates)} dates {dates[0]} → {dates[-1]} — **a rolling window**, "
         f"not the size of the board: the oldest day leaves entire.")
    if a.since:
        rows = [r for r in rows if r[1] and r[1] >= a.since]
        note(f"{len(rows)} posted {a.since} or later")
    if a.limit:
        rows = rows[: a.limit]
    if not a.fetch and not a.search:
        print(json.dumps({"source": "jobam", "country": "AM",
                          "sitemap_entries": raw, "distinct": len(rows),
                          "window_from": dates[0], "window_to": dates[-1],
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
        posting, why = posting_on(page)
        if posting is None:
            broken.append((u, why))
            continue
        c = card(u, d, posting)
        if needle and needle not in fold(c.get("title") or ""):
            continue
        kept.append(c)
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{slug_of(u)} ({w})" for u, w in broken[:5]))
    print(json.dumps({"source": "jobam", "country": "AM",
                      "sitemap_entries": raw, "window_from": dates[0],
                      "window_to": dates[-1], "read": len(kept) + len(broken),
                      "kept": len(kept), "unreadable": len(broken), "ads": kept},
                     ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}/hy/job/{a.slug}"
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

    li = sub.add_parser("list", help="advertisements in the rolling window")
    li.add_argument("--since", metavar="YYYY-MM-DD")
    li.add_argument("--limit", type=int)
    li.add_argument("--search", help="match the title; folds accents")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for its fields; without it the listing "
                         "is the sitemap alone")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
