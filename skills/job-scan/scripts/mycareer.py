#!/usr/bin/env python3
"""MyCareer — the Maldives government's employment service, read from its own
active filter rather than from a heuristic that looked right and was wrong.

    mycareer.py list [--since YYYY-MM-DD] [--fetch] [--limit N] [--archive]
    mycareer.py ad --url https://mycareer.gov.mv/en/jobs/<slug>

TWO QUANTITIES, AND THE SITE PUBLISHES BOTH

    /en/jobs                       1 397 pages   ~12 570 advertisements
    /en/jobs?filter[active]=1         13 pages       109 advertisements

**The unfiltered listing is the archive back to 2019-11-17.** Reading it and
counting would overstate the live Maldivian market by a factor of a hundred —
and nothing on the page says so, because both numbers are true.

THE HEURISTIC THAT LOOKED RIGHT

The listing is roughly newest-first and each dead advertisement carries a
`badge-expired` on its card, so «&nbsp;read pages in order, stop at the first
badge&nbsp;» seems to follow. **It is wrong, and two spread pages show it:**

    page 1      VVVVVVVVV        page 12     XXXXVXXXX
    page 2      VVVVVVVVV        page 13     VVXXXVVXX
    page 700    XXXXXXXXX        page 1397   XXXXXXXX

**Live advertisements sit after dead ones**, because the order is by posting
date and expiry is a per-advertisement deadline. *Stopping at the first badge
would have ended on page 12 and lost the five live advertisements behind it.*
**The pages that show this are 12 and 13; pages 1 and 2 agree with the
heuristic, and they are adjacent, which is why they are not a sample.**

WHY THE FILTER IS TRUSTED

It is the site's own, exercised in both directions on 2026-09-08:

    filter[active]=1     9 cards   0 expired   7 shared with unfiltered page 1
    filter[expired]=1    9 cards   9 expired   0 shared with either

**Zero overlap between the two, and the inverse filter returns the complement
it names.** *A filter tested only on the side one wants is not tested.*

THE ADVERTISEMENT IS NOT FETCHED

Title, employer, salary, employment type and town all sit on the listing card,
counted one-per-card across pages 1, 2, 12, 13, 700 and 1397. **So the whole
live market costs 13 requests, not 109.** *`--fetch` opens each advertisement
anyway, for the posting and closing dates, which the card does not carry.*

WHAT IT DOES NOT DO

No `JobPosting` and no `ld+json` exist anywhere on this site, so every field is
an HTML anchor and every missing one is named on stderr. **`--since` refuses
without `--fetch`**: the dates are on the advertisement, not the card, and a
filter that silently kept everything would be worse than none.
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
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BASE = "https://mycareer.gov.mv"
LIST = BASE + "/en/jobs"
AD_PREFIX = "/en/jobs/"

# **The active filter, percent-encoded.** The brackets are the site's own form
# field name — `filter[active]` — and they are sent encoded because that is
# what the site's paginator emits in its own links.
ACTIVE = "filter%5Bactive%5D=1"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL, EXIT_REFUSED, EXIT_UNKNOWN = 2, 3, 6, 7, 8

# One card runs from its own link to the next link, or to the end of the body.
CARD = re.compile(
    r'<a href="(https://mycareer\.gov\.mv/en/jobs/[^"]+)"'
    r' class="[^"]*custom-card-link"(.*?)'
    r'(?=<a href="https://mycareer\.gov\.mv/en/jobs/|</body>)', re.S)

# **Each of these was counted one-per-card on six pages before being used.**
# `EMPLOYMENT` is the one that is legitimately absent — 3 of 8 cards on page
# 1397 carry no employment type — so it is optional and the others are not.
TITLE = re.compile(r'<h5 class="mb-0">\s*(.*?)\s*</h5>', re.S)
EMPLOYER = re.compile(
    r'<small class="text-muted text-uppercase">\s*(.*?)\s*</small>', re.S)
SALARY = re.compile(r'<p class="mb-1 fw-medium">\s*(.*?)\s*</p>', re.S)
EMPLOYMENT = re.compile(r'fa-business-time"></i>\s*(.*?)\s*</div>', re.S)
TOWN = re.compile(r'fa-location-dot"></i>\s*(.*?)\s*</div>', re.S)
EXPIRED = re.compile(r'badge-expired')

# `Page 1 of 13` — the site's own bound, read rather than guessed.
PAGES = re.compile(r'Page\s+\d+\s+of\s+([\d,]+)')

# On the advertisement, not on the card.
PUBLISHED = re.compile(r'Published Date\s*</[^>]+>\s*<[^>]+>\s*(.*?)\s*<', re.S)
EXPIRY = re.compile(r'Expiry Date\s*</[^>]+>\s*<[^>]+>\s*(.*?)\s*<', re.S)
DATE = re.compile(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})')
MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}

_PACE = Pace("mycareer.gov.mv", own=1.0)
_ANNOUNCED = False


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[mycareer] {msg}", file=sys.stderr)


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
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en;q=0.9,dv;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def text(fragment):
    if fragment is None:
        return None
    s = html_mod.unescape(html_mod.unescape(re.sub(r"<[^>]+>", "", fragment)))
    return re.sub(r"\s+", " ", s).strip() or None


def one(rx, block):
    m = rx.search(block)
    return text(m.group(1)) if m else None


def parse_date(s):
    """`17 November 2019` -> `2019-11-17`, or None. Never raises."""
    if not s:
        return None
    m = DATE.search(s)
    if not m:
        return None
    month = MONTHS.get(m.group(2).lower())
    if not month:
        return None
    try:
        return datetime.date(int(m.group(3)), month, int(m.group(1))).isoformat()
    except ValueError:
        return None


def page_url(n, archive):
    q = f"page={n}" if archive else f"{ACTIVE}&page={n}"
    return f"{LIST}?{q}"


def card(url, block, page):
    """One listing card. `missing_fields` names what the card did not carry."""
    row = {
        "id": "mycareer:" + url.rstrip("/").rsplit("/", 1)[-1],
        "url": url,
        "seen_on_page": page,
        "title": one(TITLE, block),
        "employer": one(EMPLOYER, block),
        "town": one(TOWN, block),
        "salary_raw": one(SALARY, block),
        "employment_type": one(EMPLOYMENT, block),
        "expired": bool(EXPIRED.search(block)),
    }
    # **`employment_type` is not required**: 3 of 8 cards on page 1397 publish
    # none, so treating its absence as a defect would report a fault that is
    # the board's own choice.
    missing = [k for k in ("title", "employer", "town") if not row[k]]
    row["missing_fields"] = missing or None
    return row


def listing(archive, limit):
    """Read the paginated listing. Returns (rows, pages_read, declared)."""
    first = page_url(1, archive)
    code, body = get(first)
    if code != 200:
        die(f"{first}: HTTP {code}")
    m = PAGES.search(body)
    if not m:
        die("the listing no longer declares `Page N of M`; the bound this "
            "adapter walks has moved and guessing one would invent a "
            "denominator.", EXIT_BROKEN)
    declared = int(m.group(1).replace(",", ""))
    note(f"{'archive' if archive else 'active filter'}: "
         f"{declared} pages declared by the site")

    rows, read, n = [], 0, 1
    while n <= declared:
        body = body if n == 1 else None
        if body is None:
            u = page_url(n, archive)
            code, body = get(u)
            if code != 200:
                note(f"{u}: HTTP {code} — stopping, {read} pages read")
                break
        got = CARD.findall(body)
        if not got:
            note(f"page {n} carried no card; stopping at {read} pages read")
            break
        rows.extend(card(u, b, n) for u, b in got)
        read += 1
        n += 1
        body = None
        if limit and len(rows) >= limit:
            break
    # **The same advertisement can arrive twice.** Measured 2026-09-08: a
    # 13-page walk returned 109 rows and 107 distinct addresses, and the 109
    # AGREED with the counter the site prints on its home page. *A total that
    # matches its own source is not a check —* the duplicate pair is reported
    # here with the pages it came from, so a reader can tell a paginator
    # drifting under a new posting from a board that lists one advertisement
    # twice.
    seen, unique, dups = {}, [], []
    for r in rows:
        if r["url"] in seen:
            dups.append((r["url"], seen[r["url"]], r["seen_on_page"]))
            continue
        seen[r["url"]] = r["seen_on_page"]
        unique.append(r)
    return unique, read, declared, len(rows), dups


def cmd_list(a):
    if a.since and not a.fetch:
        die("`--since` needs `--fetch`: the posting date is on the "
            "advertisement, never on the listing card.", EXIT_UNKNOWN)

    rows, read, declared, raw, dups = listing(a.archive, a.limit)
    if a.limit:
        rows = rows[:a.limit]

    # **The negative control on the filter, and it prints either way.** If the
    # site's `filter[active]` ever stops filtering, this line is what says so —
    # nothing else in the output would change shape.
    stale = sum(1 for r in rows if r["expired"])
    if a.archive:
        note(f"archive mode: {stale} of {len(rows)} advertisements are marked "
             f"expired. **This is expected here** — the archive is the whole "
             f"history, and this count is the reason the default is filtered.")
    elif stale:
        note(f"WARNING: {stale} of {len(rows)} advertisements carry an expiry "
             f"badge while the ACTIVE filter is on. The site's filter has "
             f"changed meaning; do not trust this run's count.")
    else:
        note(f"none of the {len(rows)} advertisements carries an expiry badge "
             f"under the active filter. **This line is the negative control**: "
             f"it prints whether or not anything was wrong.")

    # **Both numbers, never just the agreeing one.**
    if dups:
        note(f"{len(dups)} duplicate address(es) dropped: {raw} rows read, "
             f"{len(rows)} distinct advertisements. Each is named with the "
             f"pages it came from — same page means the board lists it twice, "
             f"different pages means the paginator shifted under a new posting:")
        for u, first, again in dups:
            note(f"    page {first} then page {again}  {u}")
    else:
        note(f"{raw} rows read, all distinct. **Negative control**: this line "
             f"prints whether or not a duplicate was found.")

    incomplete = [r for r in rows if r["missing_fields"]]
    if incomplete:
        note(f"{len(incomplete)} of {len(rows)} cards are missing a required "
             f"field. Each is named:")
        for r in incomplete:
            note(f"    {r['id']:>28}  missing "
                 f"{', '.join(r['missing_fields'])}")
    else:
        note(f"every one of {len(rows)} cards yielded title, employer and "
             f"town. **Negative control**: this prints either way.")

    if not a.fetch:
        # **Both counts, side by side.** Without the pages read, a reader
        # cannot tell whether 109 is a site ceiling or something we counted.
        print(json.dumps({
            "source": "mycareer", "country": "MV",
            "mode": "archive" if a.archive else "active",
            "pages_declared": declared, "pages_read": read,
            "rows_read": raw, "found": len(rows), "duplicates": len(dups),
            "expired_marked": stale,
            "fetched": False, "ads": rows}, ensure_ascii=False, indent=1))
        return

    today = datetime.date.today().isoformat()
    kept, broken = [], []
    for r in rows:
        code, page = get(r["url"])
        if code != 200:
            broken.append((r["id"], f"HTTP {code}"))
            continue
        r = dict(r)
        r["posted"] = parse_date(one(PUBLISHED, page))
        r["deadline"] = parse_date(one(EXPIRY, page))
        kept.append(r)
    if a.since:
        before = len(kept)
        # A missing posting date is kept: absent is not old.
        kept = [r for r in kept if not r["posted"] or r["posted"] >= a.since]
        note(f"--since {a.since}: {len(kept)} of {before}; advertisements "
             f"without a posting date are kept — absent is not old.")
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{i} ({w})" for i, w in broken[:5]))

    print(json.dumps({
        "source": "mycareer", "country": "MV",
        "mode": "archive" if a.archive else "active",
        "pages_declared": declared, "pages_read": read,
        "rows_read": raw, "found": len(rows), "duplicates": len(dups),
        "read": len(kept) + len(broken),
        "kept": len(kept), "unreadable": len(broken),
        "as_of": today, "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken or incomplete:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    if not urllib.parse.urlsplit(a.url).path.startswith(AD_PREFIX):
        die(f"--url must be an advertisement under {AD_PREFIX}")
    code, page = get(a.url)
    if code in (404, 410):
        die(f"{a.url} is gone (HTTP {code}). Record it as discarded.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}")
    out = {
        "id": "mycareer:" + a.url.rstrip("/").rsplit("/", 1)[-1],
        "url": a.url,
        "posted": parse_date(one(PUBLISHED, page)),
        "deadline": parse_date(one(EXPIRY, page)),
        "expired": bool(EXPIRED.search(page)),
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    li = sub.add_parser("list")
    li.add_argument("--since", help="YYYY-MM-DD, needs --fetch")
    li.add_argument("--fetch", action="store_true",
                    help="open each advertisement for its dates")
    li.add_argument("--limit", type=int)
    li.add_argument("--archive", action="store_true",
                    help="the whole 1 397-page history, not the 13 live pages")
    li.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
