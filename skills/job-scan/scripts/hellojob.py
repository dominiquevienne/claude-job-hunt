#!/usr/bin/env python3
"""HelloJob — Azerbaijan (`www.hellojob.az`).

  hellojob.py list [--since 2026-08-06] [--limit 20] [--search satış] [--fetch]
  hellojob.py ad --slug layihe-rehberi-15784394

**The only board of the series that does the freshness work itself.**
`/sitemap.xml` declares seven children, and two of them are
`vacancies.xml` and `expired-vacancies.xml` — **live and dead in separate
files, by the site's own reckoning.**

Everywhere else this had to be inferred: `jobsbotswana.info` keeps expired
advertisements among the live ones and only a `validThrough` separates them,
`ihararejobs.com` gives 64 % of its entries the date of the measurement, and
`myjobsfiji.com` gives all 3 187 the same one. **An adapter that is told which
advertisements are live cannot be wrong about it**, and that is worth more than
the volume.

WHAT WAS MEASURED — URL, TIME, RAW COUNT AND DISTINCT COUNT

    https://www.hellojob.az/vacancies.xml
      2026-09-04 22:31 UTC · 190 929 bytes · 588 <loc> · 588 distinct · 0 duplicates
      44 dates, 2026-02-10 → 2026-09-04 · 533 within thirty days

    https://www.hellojob.az/expired-vacancies.xml
      2026-09-04 22:31 UTC · 8 546 148 bytes · 27 402 <loc> · 27 402 distinct
      2 098 dates, 2019-05-02 → 2026-09-04 — **not read by this adapter**

**Counting both files gives 27 990 and that is a different quantity, not a
bigger one.** A caller who wants the archive should say so.

TWO MEASUREMENTS, THREE HOURS APART, AND THE TOTAL IS CONSERVED

Another session measured the same two files at 21:08 UTC: **591 live and
27 399 expired**. This one, at 22:31: **588 and 27 402**.

    591 + 27 399 = 27 990
    588 + 27 402 = 27 990

**Three advertisements moved from one file to the other and nothing else
changed.** That is not a disagreement between two counts; it is a board
running, and the conserved total is what shows it.

**And the other explanation was tested rather than dismissed.** The earlier
measurement was taken under a browser `User-Agent`, this one under ours, so
"the content depends on who asks" predicted the same gap. A 2×2 square at
22:34 UTC — two agents, two files — returned **588 and 27 402 under both**.
Identity has no effect here, so the elapsed time is the whole of it.

WHERE THE FIELDS COME FROM

**There is no `JobPosting`.** The page's only `ld+json` is a `FAQPage` of
site-help boilerplate — six questions about how to use the search — and it
carries nothing about the advertisement.

The fields are in a labelled list, `<li><span>LABEL</span>…<p>VALUE</p></li>`:

    Şəhər           city, followed by a street address
    Kateqoriya      category
    Maaş            salary — `2500 - 3000 AZN`, or `Razılaşma ilə` (negotiable)
    Bitmə tarixi    expiry, in Azerbaijani words: `14 oktyabr 2026`

The role comes from `<title>` before ` vakansiyası`, and the employer from the
`description` meta before ` şirkəti`. **Measured on eight advertisements: 8/8
on every field.**

**`Razılaşma ilə` is emitted as written, in `salary_text`, and no number is
parsed out of it.** It means *by agreement*, which is a real answer and not a
missing one — and a `salary_min` of `None` would merge it with an
advertisement that simply omits the field.

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

BASE = "https://www.hellojob.az"
SITEMAP = BASE + "/vacancies.xml"
EXPIRED = BASE + "/expired-vacancies.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)
TITLE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
DESC = re.compile(
    r'<meta[^>]+name=["\']description["\'][^>]*content=["\'](.*?)["\']', re.S)
TAGS = re.compile(r"<[^>]+>")

# Azerbaijani month names, for `Bitmə tarixi`. Listed rather than parsed by
# locale: the runner's locale is not the site's, and `%B` would depend on it.
MONTHS = {"yanvar": 1, "fevral": 2, "mart": 3, "aprel": 4, "may": 5,
          "iyun": 6, "iyul": 7, "avqust": 8, "sentyabr": 9, "oktyabr": 10,
          "noyabr": 11, "dekabr": 12}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[hellojob] {msg}", file=sys.stderr)


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
        "Accept-Language": "az,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
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


def entries(url=SITEMAP):
    code, body = get(url)
    if code != 200:
        die(f"{url}: HTTP {code}")
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
        die(f"{url} parsed to zero entries from {len(body)} characters — read "
            f"the bytes before believing the zero.")
    rows.sort(key=lambda r: (r[1] or ""), reverse=True)
    return rows, raw


def labelled(page, label):
    """`<li><span>LABEL</span> … <p>VALUE</p></li>`, flattened."""
    m = re.search(r"<li>\s*<span>\s*" + re.escape(label) + r"\s*</span>(.*?)</li>",
                  page, re.S)
    if not m:
        return None
    v = re.sub(r"\s+", " ", html_mod.unescape(TAGS.sub(" ", m.group(1)))).strip()
    return v or None


def az_date(text):
    """`14 oktyabr 2026` → `2026-10-14`. Returns None rather than guessing."""
    m = re.match(r"\s*(\d{1,2})\s+([a-zçəğıöşü]+)\s+(\d{4})", (text or "").lower())
    if not m or m.group(2) not in MONTHS:
        return None
    return f"{m.group(3)}-{MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}"


def card(url, lastmod, page=None):
    out = {"source": "hellojob", "url": url, "slug": slug_of(url),
           "posted": lastmod, "countries": ["AZ"], "state": "live"}
    if page is None:
        return out
    t = TITLE.search(page)
    raw_title = html_mod.unescape(t.group(1)).strip() if t else ""
    out["title"] = raw_title.split(" vakansiyası")[0].strip() or None
    d = DESC.search(page)
    desc = html_mod.unescape(d.group(1)) if d else ""
    out["employer"] = (desc.split(" şirkəti")[0].strip()
                       if " şirkəti" in desc else None)
    place = labelled(page, "Şəhər")
    out["city"] = place.split(",")[0].strip() if place else None
    out["location_raw"] = place
    out["category"] = labelled(page, "Kateqoriya")
    sal = labelled(page, "Maaş")
    # **Emitted as written, and no number parsed out of it.** `Razılaşma ilə`
    # means *by agreement* — a real answer, not a missing one, and a numeric
    # `None` would merge it with an advertisement that omits the field.
    out["salary_text"] = sal
    out["expires"] = az_date(labelled(page, "Bitmə tarixi"))
    return out


def cmd_list(a):
    rows, raw = entries()
    note(f"{SITEMAP} · {raw} <loc> · {len(rows)} distinct · "
         f"**live only** — {EXPIRED.rsplit('/', 1)[-1]} holds the archive and "
         f"is not read. Counting both is a different quantity, not a bigger one.")
    if a.since:
        rows = [r for r in rows if r[1] and r[1] >= a.since]
        note(f"{len(rows)} posted {a.since} or later")
    if a.limit:
        rows = rows[: a.limit]
    if not a.fetch and not a.search:
        print(json.dumps({"source": "hellojob", "country": "AZ",
                          "sitemap_entries": raw, "live": len(rows),
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
        c = card(u, d, page)
        if needle and needle not in fold(c.get("title") or ""):
            continue
        kept.append(c)
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{slug_of(u)} ({w})" for u, w in broken[:5]))
    print(json.dumps({"source": "hellojob", "country": "AZ",
                      "sitemap_entries": raw, "read": len(kept) + len(broken),
                      "kept": len(kept), "unreadable": len(broken), "ads": kept},
                     ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}/vakansiya/{a.slug}"
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.slug} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    print(json.dumps(card(url, None, page), ensure_ascii=False, indent=1))


def cmd_counts(a):
    """Both files, with the provenance a count needs to be checkable."""
    import datetime
    live, live_raw = entries(SITEMAP)
    dead, dead_raw = entries(EXPIRED)
    print(json.dumps({
        "measured_at_utc": datetime.datetime.now(
            datetime.timezone.utc).replace(microsecond=0).isoformat(),
        "live": {"url": SITEMAP, "raw": live_raw, "distinct": len(live)},
        "expired": {"url": EXPIRED, "raw": dead_raw, "distinct": len(dead)},
        "total": len(live) + len(dead),
        "note": "the total is conserved as advertisements move between the "
                "two files; a gap in `live` alone is not a disagreement",
    }, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="live advertisements")
    li.add_argument("--since", metavar="YYYY-MM-DD")
    li.add_argument("--limit", type=int)
    li.add_argument("--search", help="match the title; folds accents")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for its fields; without it the "
                         "listing is the sitemap alone")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad)

    co = sub.add_parser("counts", help="both files, with URL, time and counts")
    co.set_defaults(func=cmd_counts)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
