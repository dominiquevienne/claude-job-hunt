#!/usr/bin/env python3
"""Oferta Pune (`ofertapune.net`) — Kosovo's first adapter.

  ofertapune.py list [--expiring-before 2026-10-01] [--city Prishtinë] [--limit 20]
  ofertapune.py ad --slug call-agent-deutsch

**Kosovo had a country page, six named hosts and no adapter.** Two answer 403
on `/robots.txt` itself; one is a client-rendered application; this is the one
that serves its inventory.

ONE REQUEST GIVES 481 ADVERTISEMENTS, COMPLETE

**No sitemap is declared and none is composed.** The homepage carries every
listing row in full, server-rendered:

```html
<a href="/jobs/<slug>">
  <div class="jobListTitle" date="21.09.2026">Call Agent (Deutsch)</div>
  <div class="saveToFavBtn" ids="109849"></div>
  <div class="jobListTitleComp">Sonnecto</div>
  <div class="jobListExpires">21.09.2026</div>
  <div class="jobListCity">Prishtinë</div>
```

    481 blocks · 481 distinct slugs
    ids  481/481 · employer 481/481 · expires 481/481 · city 480/481

**So the core fields cost one request and `--fetch` is not needed for them.**

THE DATE IS AN EXPIRY, NOT A POSTING DATE

`jobListExpires` and the `date=` attribute carry the same value, and the page
offers *«&nbsp;Më njofto para se të skadojë konkursi&nbsp;»* — notify me before
the competition expires. **A reader that took it for `datePosted` would date
every advertisement in the future**, and the rows would sort backwards.

*This board publishes no posting date at all*, so `--since` is not offered:
**a filter on a field the source does not carry would silently return
everything**, which reads exactly like a board on which nothing is old.
`--expiring-before` filters on what is actually there.

THE IDENTIFIER IS THE BOARD'S OWN, AND IT WAS CHECKED

`saveToFavBtn ids="109479"` on the listing, and `/jobs/accounts-receivable-clerk`
**redirects to `/jobs?id=109479`**. *The markup id and the canonical id are the
same number* — checked on one advertisement rather than assumed, so the ledger
id is the board's and not a slug standing in for one.

NO STRUCTURED DATA ANYWHERE

`ld+json` is absent from the homepage and from the advertisement; `JobPosting`
appears zero times. **The parsing is HTML, in Albanian**, and every field above
is read from a class name rather than from a schema.

**`--strict` prints every block the parser could not read.** *On 2026-09-07
that is nought of 481 — and it is printed rather than assumed, because a
narrow extractor does not return less, it returns false.*

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

BASE = "https://ofertapune.net"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# **The class name is a PREFIX of another one.** `jobListCntsInner` starts
# with `jobListCnts`, so splitting on the bare prefix cuts every block in
# two — before its title — and the parser reported 481 unreadable blocks
# out of 481. *Third instance today of a pattern matching a longer word:
# `<th` counted `<thead`, and `faqe` — Albanian for «page» — matched
# `perfaqesues`, «representative».* The delimiter demands what follows.
BLOCK = re.compile(r'<div class="jobListCnts[ "]')
LINK = re.compile(r'href="(https://ofertapune\.net/jobs/[^"#?]+)"')
TITLE = re.compile(r'<div class="jobListTitle" date="([^"]*)"[^>]*>(.*?)</div>', re.S)
IDS = re.compile(r'<div class="saveToFavBtn" ids="(\d+)"')
EMPLOYER = re.compile(r'<div class="jobListTitleComp"[^>]*>(.*?)</div>', re.S)
CITY = re.compile(r'<div class="jobListCity">(.*?)</div>', re.S)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[ofertapune] {msg}", file=sys.stderr)


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
_PACE = Pace("ofertapune.net", own=1.0)


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


def iso(d):
    """`21.09.2026` -> `2026-09-21`, or `None` — never a guess."""
    m = re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{4})", (d or "").strip())
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def rows_on(page):
    """`(rows, unreadable)`, and the second half is what makes the first
    trustworthy: a block carrying an advertisement link that could not be
    parsed comes back as its own text rather than vanishing."""
    rows, unreadable = [], []
    for block in BLOCK.split(page):
        link = LINK.search(block)
        if not link:
            continue
        title = TITLE.search(block)
        if not title:
            unreadable.append((link.group(1), clean(block)[:140]))
            continue
        url = link.group(1)
        ids = IDS.search(block)
        emp = EMPLOYER.search(block)
        city = CITY.search(block)
        rows.append({
            "source": "ofertapune",
            "url": url,
            "slug": url.rstrip("/").rsplit("/", 1)[-1],
            # **The board's own id**, and it is the same number the canonical
            # URL redirects to — checked, not assumed.
            "id": ids.group(1) if ids else None,
            "ledger_id": (f"ofertapune:{ids.group(1)}" if ids
                          else f"ofertapune:{url.rstrip('/').rsplit('/', 1)[-1]}"),
            "title": clean(title.group(2)) or None,
            "employer": clean(emp.group(1)) if emp else None,
            "city": clean(city.group(1)) if city else None,
            # **Named for what it is.** This is the deadline; the board
            # publishes no posting date, and calling it `posted` would date
            # every row in the future.
            "expires": iso(title.group(1)),
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
    if a.search:
        needle = fold(a.search)
        rows = [r for r in rows if needle in fold(r["title"] or "")]
    if a.limit:
        rows = rows[: a.limit]
    print(json.dumps({"source": "ofertapune", "country": "XK",
                      "returned": len(rows), "unreadable": len(bad),
                      "note": "`expires` is the deadline; this board "
                              "publishes no posting date, so no --since is "
                              "offered",
                      "ads": rows}, ensure_ascii=False, indent=1))
    if bad and not rows:
        sys.exit(EXIT_BROKEN)
    if bad:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}/jobs/{a.slug}"
    code, page, landed = get(url)
    if code in (404, 410):
        die(f"{a.slug} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    emp = re.search(r'<div class="jobInfoLeftHC">(.*?)</div>', page, re.S)
    exp = re.search(r'<div class="jobInfoLeftHC_O">(.*?)</div>', page, re.S)
    ident = None
    if landed:
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(landed).query)
        ident = (q.get("id") or [None])[0]
    print(json.dumps({
        "source": "ofertapune", "url": url, "slug": a.slug,
        # **From the redirect the board itself performed.** `/jobs/<slug>`
        # lands on `/jobs?id=<n>`, and that number is the one the listing
        # markup carries.
        "id": ident,
        "ledger_id": f"ofertapune:{ident or a.slug}",
        "title": clean(h1.group(1)) if h1 else None,
        "employer": clean(emp.group(1)) if emp else None,
        "expires": iso(clean(exp.group(1))) if exp else None,
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
    li.add_argument("--search", help="match the title; folds accents")
    li.add_argument("--limit", type=int)
    li.add_argument("--strict", action="store_true",
                    help="print every block the parser could not read")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
