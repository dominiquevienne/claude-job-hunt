#!/usr/bin/env python3
"""KosovaJob (`kosovajob.com`) — Kosovo's second board, and the larger one.

  kosovajob.py list [--expiring-before 2026-10-01] [--city Prishtinë] [--limit 20]
  kosovajob.py ad --employer sonnecto --slug call-agent-deutsch

**566 advertisements from one request**, server-rendered, no sitemap declared
and none composed. `ofertapune.py` gives 481 from the same country the same
day; **148 of them are on both**, so the two together are not 1 047.

IT SHARES OFERTAPUNE'S TEMPLATE AND NOT ITS DATABASE

Both hosts serve `jobListCnts` / `jobListCntsInner` / `jobListTitle date=` /
`jobListCity` / `jobListExpires`, and the same advertisement leads both
homepages. **But the ids differ**: Sonnecto's *Call Agent (Deutsch)* is
`109849` on ofertapune and `47268` here. *A shared template names a supplier,
not an operator* — and two different id spaces carrying the same vacancy is an
employer posting twice, not one board wearing two names.

THE OVERLAP, AND WHY IT IS 148 AND NOT A RATE

Both boards' listing URLs end in a title-derived slug, so the slug is the only
key on offer. **It is an identifier on one board and not on the other**: 481
advertisements carry 481 distinct slugs on ofertapune, while 566 here carry
516 — `recepsioniste` is worn by six different vacancies and
`kamariere-shankiste` by six more.

So the intersection was confirmed against a second field rather than trusted:
**148 shared slugs, and the employer agrees on 148 of 148.** The five that
first looked like disagreements were one employer spelled two ways —
`H&M` folds to `h-m` here and `hamp-m` there, likewise `Q.T.S`, `G&G Group`
and `Lily's Cafe`.

*It is a floor, not a rate.* Both figures are what one request returned on
2026-09-07; neither board states a total, so neither 481 nor 566 is a claim
about everything either board holds.

TWO PLACES WHERE THE SHARED TEMPLATE DIVERGES, AND BOTH BITE

1. **`jobListExpires` is a countdown here and a date there.** It reads
   `15 ditë` — *fifteen days* — where ofertapune prints `21.09.2026`. A parser
   copied across would produce `None` on every row, or worse, parse the `15`.
   **The absolute deadline is in the `date=` attribute of `jobListTitle`**,
   as `2026-09-21 23:55:00`, and that is what this module reads.
2. **`ids=` is a position counter here and the advertisement's id there.**
   It runs `"5 0 100"`, `"6 0 101"` down the page. Reading it as an identifier
   would mint a ledger key that changes every time the page is reordered.
   **The listing carries no id at all**; `jobID="47268"` exists only on the
   advertisement page, so `list` keys on `<employer>/<slug>` and says so.

THE ONLY DATE IS AGAIN A DEADLINE

`Skadon 21/09/26 (15 ditë)` on the advertisement page, `date=` on the listing,
and no posting date anywhere on either. **`--since` is therefore not offered**:
a filter on a field the source does not carry returns everything in silence,
which reads exactly like a board on which nothing is old.

NO STRUCTURED DATA

`ld+json` and `JobPosting` are both absent from the homepage and from the
advertisement page. Every field is read from a class name, in Albanian.

WHAT WAS MEASURED, 2026-09-07

    /robots.txt        44 bytes — `Disallow: /cgi-bin/` and nothing else
    homepage           566 blocks, 516 distinct slugs, 391 employers
    fields             title 566/566 · employer 566/566 (in the URL)
                       expires 566/566 · city 566/566
    ld+json            0 · JobPosting 0

**`--strict` prints every block the parser could not read**, because a narrow
extractor does not return less, it returns false.

Verified against the live site on 2026-09-07.
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
from _pace import Pace
from _robots import allowed as robots_allowed, full_path
from _ua import UA

BASE = "https://kosovajob.com"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# **`jobListCntsInner` begins with `jobListCnts`.** Splitting on the bare
# prefix cuts every block in two, before its title, and the parser reports
# every block unreadable — which is what it did on ofertapune before the
# delimiter demanded the character that follows.
BLOCK = re.compile(r'<div class="jobListCnts[ "]')
LINK = re.compile(r'href="https://kosovajob\.com/([a-z0-9-]+)/([a-z0-9-]+)"')
TITLE = re.compile(r'<div class="jobListTitle" date="([^"]*)"[^>]*>(.*?)</div>',
                   re.S)
CITY = re.compile(r'<div class="jobListCity">(.*?)</div>', re.S)
JOBID = re.compile(r'jobID="(\d+)"')

# Paths that are not advertisements but match `/<a>/<b>`.
NOT_AN_AD = {"images", "css", "js", "admin", "blog", "press", "kontakt"}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[kosovajob] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    # An unknown is not a refusal: `not None` is `True` for both.
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# The host declares no `Crawl-delay`; one second is ours and declared as ours.
_PACE = Pace("kosovajob.com", own=1.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "sq-XK,sq;q=0.9,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, "", url
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def clean(s):
    return " ".join(html_mod.unescape(re.sub(r"<[^>]+>", " ", s or "")).split())


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def iso_attr(d):
    """`2026-09-21 23:55:00` -> `2026-09-21`, or `None` — never a guess."""
    m = re.match(r"(\d{4}-\d{2}-\d{2})\b", (d or "").strip())
    return m.group(1) if m else None


def iso_short(d):
    """`21/09/26` -> `2026-09-21`, or `None`.

    **Two-digit years only**, and only this century: `26` is 2026. A four-digit
    year here would mean the page changed format, and `None` says so rather
    than inventing a date from the first two digits.
    """
    m = re.search(r"\b(\d{2})/(\d{2})/(\d{2})\b", (d or "").strip())
    return f"20{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def rows_on(page):
    """`(rows, unreadable)`. The second half is what makes the first
    trustworthy: a block carrying an advertisement link that could not be
    parsed comes back as its own text rather than vanishing."""
    rows, unreadable = [], []
    for block in BLOCK.split(page):
        link = LINK.search(block)
        if not link or link.group(1) in NOT_AN_AD:
            continue
        employer, slug = link.group(1), link.group(2)
        title = TITLE.search(block)
        if not title:
            unreadable.append((f"{employer}/{slug}", clean(block)[:140]))
            continue
        city = CITY.search(block)
        rows.append({
            "source": "kosovajob",
            "url": f"{BASE}/{employer}/{slug}",
            "employer_slug": employer,
            "slug": slug,
            # **The listing carries no identifier.** `ids=` is a position
            # counter down the page; the board's `jobID` appears only on the
            # advertisement page. The path is stable and the counter is not,
            # so the ledger key is the path and this says which it is.
            "id": None,
            "id_source": "the listing publishes none; jobID is on the ad page",
            "ledger_id": f"kosovajob:{employer}/{slug}",
            "title": clean(title.group(2)) or None,
            "city": clean(city.group(1)) if city else None,
            # **The deadline, from the attribute and not from
            # `jobListExpires`** — that div reads `15 ditë` here, a countdown,
            # where the same div on ofertapune carries a date.
            "expires": iso_attr(title.group(1)),
            "countries": ["XK"],
        })
    return rows, unreadable


def cmd_list(a):
    code, page, landed = get(BASE + "/")
    if code != 200:
        die(f"{BASE}/: HTTP {code}")
    if landed and landed.rstrip("/") != BASE:
        die(f"{BASE}/ redirected to {landed} — that is not the listing.")
    rows, bad = rows_on(page)
    if not rows:
        die(f"the homepage parsed to zero advertisements from {len(page)} "
            f"characters — read the bytes before believing the zero.")
    note(f"{len(rows)} advertisement(s) from one request. **No sitemap is "
         f"declared and none was composed**; the homepage carries every row.")
    if bad:
        note(f"{len(bad)} block(s) carried an advertisement link and could "
             f"not be parsed"
             + (":" if a.strict else " — pass --strict to see them"))
        if a.strict:
            for u, text in bad:
                print(f"  [{u}] {text}", file=sys.stderr)
    if a.expiring_before:
        before = len(rows)
        rows = [r for r in rows if r["expires"]
                and r["expires"] < a.expiring_before]
        note(f"{len(rows)} of {before} expire before {a.expiring_before}. "
             f"**This is the deadline, not a posting date** — the board "
             f"publishes none.")
    if a.city:
        needle = fold(a.city)
        rows = [r for r in rows if needle in fold(r["city"] or "")]
    if a.employer:
        needle = fold(a.employer)
        rows = [r for r in rows if needle in fold(r["employer_slug"])]
    if a.search:
        needle = fold(a.search)
        rows = [r for r in rows if needle in fold(r["title"] or "")]
    if a.limit:
        rows = rows[: a.limit]
    print(json.dumps({"source": "kosovajob", "country": "XK",
                      "returned": len(rows), "unreadable": len(bad),
                      "note": "`expires` is the deadline; this board "
                              "publishes no posting date, so no --since is "
                              "offered. 148 of these are also on ofertapune "
                              "(2026-09-07) — do not add the two boards up",
                      "ads": rows}, ensure_ascii=False, indent=1))
    if bad and not rows:
        sys.exit(EXIT_BROKEN)
    if bad:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}/{a.employer}/{a.slug}"
    code, page, _landed = get(url)
    if code in (404, 410):
        die(f"{a.employer}/{a.slug} is gone (HTTP {code}). Record it as "
            f"discarded.", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    ident = JOBID.search(page)
    field = {}
    for m in re.finditer(r'listingArea3(Cat|Exp|Orar)"[^>]*>[^<]*'
                         r'<b class="listingAreaInfo">(.*?)</b>', page, re.S):
        field[m.group(1)] = clean(m.group(2))
    site = re.search(r'<a href="(https?://(?!(?:www\.)?kosovajob\.com)'
                     r'[^"]+)"[^>]*rel="nofollow"', page)
    print(json.dumps({
        "source": "kosovajob", "url": url,
        "employer_slug": a.employer, "slug": a.slug,
        # **Only the advertisement page carries it**, which is why `list`
        # keys on the path and reports `id: null` rather than a counter.
        "id": ident.group(1) if ident else None,
        # **The path, even though the number is right here.** `list` cannot
        # see `jobID` without one request per advertisement, so keying `ad`
        # on the number would give the same vacancy two ledger ids depending
        # on which command found it — `kosovajob:47268` from here and
        # `kosovajob:sonnecto/call-agent-deutsch` from the listing. *A key
        # that depends on the route taken is not a key.* The number travels
        # in `id`, where it costs nothing and claims nothing.
        "ledger_id": f"kosovajob:{a.employer}/{a.slug}",
        "title": clean(h1.group(1)) if h1 else None,
        "employer_site": site.group(1) if site else None,
        "category": field.get("Cat"),
        "schedule": field.get("Orar"),
        "expires": iso_short(field.get("Exp")),
        "countries": ["XK"],
        "structured_data": "none — no ld+json and no JobPosting on this site",
    }, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="every advertisement, from one request")
    li.add_argument("--expiring-before", dest="expiring_before",
                    metavar="YYYY-MM-DD",
                    help="the deadline, which is the only date this board "
                         "publishes. **There is no --since**: a filter on a "
                         "posting date the source does not carry would return "
                         "everything in silence")
    li.add_argument("--city", help="match the city; folds accents")
    li.add_argument("--employer", help="match the employer slug in the URL")
    li.add_argument("--search", help="match the title; folds accents")
    li.add_argument("--limit", type=int)
    li.add_argument("--strict", action="store_true",
                    help="print every block the parser could not read")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement, by employer and slug")
    ad.add_argument("--employer", required=True)
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
