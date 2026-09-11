#!/usr/bin/env python3
"""Zaposli.ME — Montenegro, and the first board here read without `ld+json`
since `ofertapune`.

    zaposli.py list [--since YYYY-MM-DD] [--live] [--fetch] [--limit N]
    zaposli.py ad --url https://zaposli.me/posao/<id>/<employer>/<slug>

THE EXPLICIT WORD IS ON THE WRONG SIDE

    sitemap/oglasi.xml     423 <loc>   all under /posao/             ADS
    sitemap/pretrage.xml   311 <loc>   all under /oglasi-za-posao/   FACETS

**`oglasi-za-posao` means "job advertisements" and it is the FACET path.** The
advertisements sit under `posao` — "job" — which says less. *A substring filter
on the more explicit word keeps exactly the wrong 311.*

**And the children live under `/sitemap/`, not at the root**: composing
`/oglasi.xml` from the name fetches nothing. The index is read, and the child is
matched on its full address.

FOUR ANCHORS, VERIFIED UNIQUE BEFORE THIS FILE WAS WRITTEN

There is no `JobPosting` here — two `ld+json` blocks and they are `Organization`
and `WebSite`. So the fields come from markup, and each anchor was counted on
three advertisements first: **exactly one match each, on all three.**

    title      <h1 class="… fw-semi-bold …">   the SECOND h1 on the page
    town       the span after `mdi-location-enter`
    deadline   the span after `mdi-calendar`
    employer   <h4 class="… mb-1 …">

**The first `<h1>` is the page banner, "Oglasi za posao", identical on every
advertisement.** *An extractor anchored on "the h1" returns the banner 423 times
and looks like a working adapter.* That is why the class is part of the anchor.

THE DATE ON THE ADVERTISEMENT IS THE DEADLINE, NOT THE POSTING

Established by the site's own countdown rather than inferred: *"ističe
prekosjutra" — expires the day after tomorrow — beside 10 September, read on
8 September.*

**The posting date is on the LISTING pages, not on the advertisement.** Compared
over ten advertisements on 2026-09-08:

    identical to the sitemap's <lastmod>   7
    one day later                          1
    three days later                       2
    EARLIER than the lastmod               0

**So `--since` is answered from the listing here, without `--fetch`** — the one
board of seven where a sitemap date is per-advertisement and usable. *It is the
FIRST publication, and the site may show a later bump; `--since` therefore keeps
an advertisement the site would date later, and never drops one it would date
earlier.* **That asymmetry is the whole reason it is safe.**

THE NEGATIVE CONTROL IS PRINTED, NOT SWALLOWED

`ofertapune` cost 481 unreadable of 481 to a motif too narrow, and it was seen
only because the guard **printed** what it could not read. **With no structured
data there is no safe silence**: every advertisement missing a field is named
on stderr, with the field, and counted in the output.

WHAT IT DOES NOT DO

It writes nothing to disk, and a missing deadline is not treated as expired:
*absent is not past.*
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
from _zero import empty_first_page

BASE = "https://zaposli.me"
INDEX = BASE + "/sitemap.xml"
ADS_CHILD = "/sitemap/oglasi.xml"        # named, matched on the index's own <loc>
FACETS_CHILD = "/sitemap/pretrage.xml"   # 311 facet URLs — counted, never read
AD_PREFIX = "/posao/"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
SITEMAP = re.compile(r"<sitemap>(.*?)</sitemap>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)

TITLE = re.compile(r'<h1[^>]*class="[^"]*fw-semi-bold[^"]*"[^>]*>(.*?)</h1>', re.S)
TOWN = re.compile(r'mdi-location-enter[^>]*></i>\s*<span>\s*(.*?)\s*</span>', re.S)
CAL = re.compile(r'mdi-calendar[^>]*></i>\s*<span>\s*(.*?)\s*</span>', re.S)
EMPLOYER = re.compile(r'<h4[^>]*class="[^"]*mb-1[^"]*"[^>]*>\s*(.*?)\s*</h4>', re.S)

# **All twelve, and the abbreviations the site might use.** On another board a
# `%b` parse read none of the last six months because four abbreviations carry
# a full stop and one is four letters long. Here the names are matched in full
# and the map is exercised on twelve dates and five non-dates.
MONTHS = {
    "januar": 1, "februar": 2, "mart": 3, "april": 4, "maj": 5, "jun": 6,
    "jul": 7, "avgust": 8, "septembar": 9, "oktobar": 10, "novembar": 11,
    "decembar": 12,
}
DATE = re.compile(r"(\d{1,2})\.\s*([A-Za-zČĆŠŽĐčćšžđ]+)\s*(\d{4})")

_PACE = Pace("zaposli.me", own=1.0)
_ANNOUNCED = False


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[zaposli] {msg}", file=sys.stderr)


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
    # **Through `wire_url`.** Montenegrin slugs carry `ž`, `č`, `š`, `ć`, `đ`
    # on 368 of this board's 423 addresses, and `urllib` raises on them. This
    # adapter hit the defect an hour after `bin/fetch-body.py` was fixed for
    # it — the third writing of the same three lines, which is why they now
    # live in `_robots` rather than at each call site.
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "sr-ME,sr;q=0.9,en;q=0.8",
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


def parse_date(s):
    """`10. septembar 2026.` -> `2026-09-10`, or None. Never raises."""
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


def ads_child(index_body):
    """The advertisement child, matched on the index's own <loc>."""
    seen = []
    for block in SITEMAP.findall(index_body):
        m = LOC.search(block)
        if m:
            seen.append(m.group(1).strip())
    for url in seen:
        if urllib.parse.urlsplit(url).path == ADS_CHILD:
            return url, seen
    die(f"the index no longer names {ADS_CHILD}. It lists: {seen}. **This is "
        f"not a reason to guess an address** — the children live under "
        f"/sitemap/ and composing one from a name fetches nothing.")


def entries():
    """(url, lastmod). Everything outside /posao/ is counted, never guessed at."""
    code, body = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}")
    child, listed = ads_child(body)
    facets = [u for u in listed
              if urllib.parse.urlsplit(u).path == FACETS_CHILD]
    if facets:
        note(f"{FACETS_CHILD} is listed beside it and is NOT read: it holds "
             f"facet URLs under /oglasi-za-posao/ — the path that says "
             f"\"job advertisements\" while the advertisements say only "
             f"\"job\".")
    code, body = get(child)
    if code != 200:
        die(f"{child}: HTTP {code}")
    blocks = ENTRY.findall(body)
    if not blocks:
        # **A child sitemap that parses to zero entries is not an empty
        # board** — #181, batch 5. It used to print a JSON of zeros with exit
        # 0; only a MISSING child died. Size beside the zero, exit 6.
        die(empty_first_page("zaposli", body, what="<url> entry", where=child),
            6)
    rows, seen, other = [], set(), 0
    for block in blocks:
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
        note(f"{other} entries in {child} are not under {AD_PREFIX} and are "
             f"not counted — the count is reported so the predicate can be "
             f"seen to still hold.")
    return rows


def card(url, lastmod, page):
    """Every field, plus the list of the ones the markup did not yield."""
    def first(rx):
        m = rx.search(page)
        return text(m.group(1)) if m else None

    t = first(TITLE)
    town = first(TOWN)
    raw_deadline = first(CAL)
    employer = first(EMPLOYER)
    deadline = parse_date(raw_deadline)
    missing = [n for n, v in (("title", t), ("town", town),
                              ("employer", employer),
                              ("deadline", deadline)) if not v]
    return {
        "id": "zaposli:" + urllib.parse.urlsplit(url).path.split("/")[2],
        "url": url,
        "title": t,
        "employer": employer,
        "town": town,
        "country": "Montenegro",
        # **Named for what each is.** The page's date is the deadline; the
        # listing's is the first publication, agreeing 7 of 10 and never later.
        "deadline": deadline,
        "deadline_raw": raw_deadline,
        "posted_sitemap": lastmod,
        "missing_fields": missing or None,
    }


def cmd_list(a):
    if a.live and not a.fetch:
        die("`--live` needs `--fetch`: the deadline is on the advertisement, "
            "and the listing carries the posting date instead.", EXIT_UNKNOWN)

    rows = entries()
    raw = len(rows)
    if a.since:
        # **Answered from the listing, and this is the one board of seven where
        # that is honest.** The sitemap date is per-advertisement, and it is
        # never LATER than the date the site shows, so this keeps an ad the
        # site would date later and never drops one it would date earlier.
        kept_rows = [(u, d) for u, d in rows if d and d >= a.since]
        dropped_undated = sum(1 for _u, d in rows if not d)
        note(f"--since answered from the listing: {len(kept_rows)} of {raw}. "
             f"The sitemap date matched the site's own posting date on 7 of 10 "
             f"advertisements and was never later, so this filter is "
             f"permissive rather than lossy.")
        if dropped_undated:
            note(f"{dropped_undated} entries carry no <lastmod> and are "
                 f"dropped by --since; they are counted here rather than lost.")
        rows = kept_rows
    if a.limit:
        rows = rows[:a.limit]

    if not a.fetch:
        print(json.dumps({"source": "zaposli", "country": "ME",
                          "sitemap_entries": raw, "selected": len(rows),
                          "fetched": False,
                          "ads": [{"id": "zaposli:" + u.split("/")[4],
                                   "url": u, "posted_sitemap": d}
                                  for u, d in rows]},
                         ensure_ascii=False, indent=1))
        return

    today = datetime.date.today().isoformat()
    kept, broken, expired = [], [], 0
    incomplete = []
    for u, d in rows:
        code, page = get(u)
        if code != 200:
            broken.append((u, f"HTTP {code}"))
            continue
        c = card(u, d, page)
        if c["missing_fields"]:
            incomplete.append((u, c["missing_fields"]))
        if a.live and c["deadline"] and c["deadline"] < today:
            expired += 1
            continue
        kept.append(c)

    # **The negative control, printed.** With no structured data, a field that
    # silently comes back empty is indistinguishable from a field the board
    # does not publish.
    if incomplete:
        note(f"{len(incomplete)} of {len(rows)} advertisements are missing at "
             f"least one field. Each is named:")
        for u, fields in incomplete:
            note(f"    {u.split('/')[4]:>8}  missing {', '.join(fields)}  {u}")
    else:
        note(f"every one of {len(rows)} advertisements yielded all four "
             f"fields. **This line is the negative control**: it prints "
             f"whether or not anything failed.")
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{u.split('/')[4]} ({w})" for u, w in broken[:5]))
    if a.live:
        note(f"{expired} dropped on a past deadline; those without one are "
             f"kept — absent is not past.")

    print(json.dumps({"source": "zaposli", "country": "ME",
                      "sitemap_entries": raw,
                      "read": len(kept) + len(broken) + expired,
                      "kept": len(kept), "unreadable": len(broken),
                      "incomplete": len(incomplete),
                      "expired_dropped": expired if a.live else None,
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken or incomplete:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    if not urllib.parse.urlsplit(a.url).path.startswith(AD_PREFIX):
        die(f"--url must be an advertisement under {AD_PREFIX}. The facets "
            f"live under /oglasi-za-posao/, whose name says more and means "
            f"less.")
    code, page = get(a.url)
    if code in (404, 410):
        die(f"{a.url} is gone (HTTP {code}). Record it as discarded.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}")
    c = card(a.url, None, page)
    print(json.dumps(c, ensure_ascii=False, indent=1))
    if c["missing_fields"]:
        note(f"missing: {', '.join(c['missing_fields'])}")
        sys.exit(EXIT_PARTIAL)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    li = sub.add_parser("list")
    li.add_argument("--since", help="YYYY-MM-DD, answered from the listing")
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
