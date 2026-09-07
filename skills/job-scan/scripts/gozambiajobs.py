#!/usr/bin/env python3
"""Go Zambia Jobs (`gozambiajobs.com`).

  gozambiajobs.py list [--limit 20] [--fetch] [--since 2026-08-01] [--live]
  gozambiajobs.py ad --slug 628419087-call-center-agents

**Two hosts, and the second is not the first.** The sitemap index is served
from `www.gozambiajobs.com`; every one of its entries points at the apex
`gozambiajobs.com`, without `www`. **A verdict taken at `www` covers nothing
on the bare host**, so the guard is asked on each URL as it is fetched.

`Crawl-delay: 1` is declared by the host and honoured.

WHAT WAS MEASURED, 2026-09-07

    sitemap-jobs-1.xml   358 <loc>, 358 distinct, every one under /jobs/
                         358 numeric ids, 358 distinct
    lastmod              none — not one entry carries a date
    a random 10          JobPosting on 10 of 10

**The card measured 368 two days earlier. There are 358.** The file lost ten
entries, so it is **not an archive that only grows**: advertisements leave it.
*A total taken from it is a reading at an instant, and the card's own question
— stock or flow — is answered at least this far: entries are removed.*

THE DATES ARE ABSENT FROM THE SITEMAP AND PRESENT IN THE ADVERTISEMENTS

The card recorded *"not one `<lastmod>` in 368 entries"* and concluded that
freshness could not be asked. **That is true of the sitemap and false of the
board**: `datePosted` and `validThrough` are on 10 of 10 sampled postings, in
full ISO form.

    datePosted      2026-08-21T09:25:03.000000Z
    validThrough    2026-09-20T09:25:03.000000Z

So `--since` and `--live` both work here — **and both need `--fetch`**, because
the sitemap carries nothing to filter on. A filter that silently returned
everything would read exactly like a board on which nothing expires.

FIELDS, ON A RANDOM TEN

    title · datePosted · validThrough · hiringOrganization
    identifier · employmentType                            10/10
    jobLocation                                             9/10
    baseSalary                                              2/10

**`baseSalary` is emitted here, and that is a decision about this board rather
than about the field.** Its currency is `ZMW` — the kwacha, which is Zambia's —
with real `minValue`/`maxValue` and a `unitText`. *On `burundijobs` the same
field reads `négociable XPF`, a Pacific franc in Burundi, and is dropped.*
**What a field is worth is a property of the board.**

`identifier.value` is the numeric id that opens the URL, so the ledger id is
the board's own and not one this adapter invented.

PROCUREMENT NOTICES: FIVE OF 358, AND THE TEST WAS TUNED AGAINST ITSELF

    invitation-to-bid · tender-for- · request-for-proposal
    call-for-expression-of-interest

**The first version of this pattern matched `procurement` and caught two
`procurement-manager` postings — real vacancies, one in four of its hits.**
The word is gone and the two are spared, checked in both directions. What
remains is five notices out of 358.

**They are counted and reported, never silently filtered.** `--jobs-only`
drops them, and the test is lexical: it reads English procurement wording in
the slug and will miss one worded otherwise.

Verified against the live site on 2026-09-07.
"""

import argparse
import datetime
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

APEX = "https://gozambiajobs.com"
SITEMAP = APEX + "/sitemap-jobs-1.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)

# **Lexical, English, and tuned against its own false positives.** See the
# docstring: `procurement` alone caught two real `procurement-manager` posts.
TENDER = re.compile(
    r"request-for-proposals?|expression-of-interest"
    r"|invitation-to-(?:bid|tender)|call-for-(?:proposals?|applications?)"
    r"|^\d+-tender-|-tender-for-", re.I)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[gozambiajobs] {msg}", file=sys.stderr)


def gate(url):
    """Per host and per path, on the URL about to be asked for.

    **The apex and `www` are two hosts**, and this board uses both: the index
    is served from one and points entirely at the other. A verdict taken on
    `www.gozambiajobs.com` says nothing about `gozambiajobs.com`.
    """
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    # An unknown is not a refusal: `not None` is `True` for both.
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace("gozambiajobs.com")


def get(url):
    gate(url)
    # The host asks for one second; `Pace` reads that from the rules rather
    # than taking a floor of ours.
    _PACE.wait()
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-ZM,en;q=0.9",
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
    seen, rows = set(), []
    for raw in LOC.findall(body):
        u = html_mod.unescape(raw.strip())
        if u in seen:
            continue
        seen.add(u)
        rows.append(u)
    if not rows:
        die(f"{SITEMAP} parsed to zero entries from {len(body)} characters — "
            f"read the bytes before believing the zero.")
    return rows


def posting_on(page):
    """The `[d]` fallback is not decoration: this theme emits its `JobPosting`
    as a bare top-level object, and a reader that only walks `@graph` reports
    *no structured data* on every advertisement."""
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


def _salary(posting):
    """Emitted, because on this board the field carries a real figure.

    `ZMW` is the kwacha, and the values are numbers with a `unitText`. *The
    same key is dropped on `burundijobs`, where every posting reads
    `négociable XPF` — a Pacific franc in Burundi.* **What a field is worth is
    a property of the board.**
    """
    sal = posting.get("baseSalary")
    if not isinstance(sal, dict):
        return None
    value = sal.get("value")
    value = value if isinstance(value, dict) else {}
    lo, hi = value.get("minValue"), value.get("maxValue")
    if lo is None and hi is None and value.get("value") is None:
        return None
    return {"currency": sal.get("currency"),
            "min": lo, "max": hi, "value": value.get("value"),
            "unit": value.get("unitText")}


def card(url, posting):
    org = posting.get("hiringOrganization")
    org = org.get("name") if isinstance(org, dict) else org
    ident = posting.get("identifier")
    ident = ident.get("value") if isinstance(ident, dict) else ident
    place = posting.get("jobLocation")
    place = place[0] if isinstance(place, list) and place else place
    addr = (place or {}).get("address") if isinstance(place, dict) else {}
    addr = addr if isinstance(addr, dict) else {}
    slug = slug_of(url)
    return {
        "source": "gozambiajobs",
        "url": url,
        "slug": slug,
        # The board's own id, and it is the one that opens the URL.
        "id": str(ident) if ident else slug.split("-", 1)[0],
        "ledger_id": f"gozambiajobs:{ident or slug.split('-', 1)[0]}",
        "title": html_mod.unescape(posting.get("title") or "").strip() or None,
        "employer": (org or "").strip() or None,
        "region": (addr.get("addressRegion") or "").strip() or None,
        # The page writes a country NAME, not a code; `countries` carries the
        # code, and the written form is kept rather than translated.
        "country_as_written": (addr.get("addressCountry") or "").strip() or None,
        "employment_type": posting.get("employmentType") or None,
        "posted": (posting.get("datePosted") or "")[:10] or None,
        "valid_through": (posting.get("validThrough") or "")[:10] or None,
        "salary": _salary(posting),
        "tender_like": bool(TENDER.search(slug)),
        "countries": ["ZM"],
    }


def cmd_list(a):
    rows = entries()
    note(f"{len(rows)} advertisements in the sitemap. **It carries no "
         f"`lastmod`** — the dates are on the pages, so `--since` and "
         f"`--live` need `--fetch`.")
    tender_slugs = sum(1 for u in rows if TENDER.search(slug_of(u)))
    note(f"{tender_slugs} slug(s) read as a procurement notice. The test is "
         f"lexical and English; it is a count, not a verdict.")
    if a.limit:
        rows = rows[: a.limit]
    if not (a.fetch or a.since or a.live or a.search or a.jobs_only):
        print(json.dumps({"source": "gozambiajobs", "country": "ZM",
                          "sitemap_entries": len(rows),
                          "note": "URLs only — the sitemap has no dates, so "
                                  "pass --fetch for anything date-shaped",
                          "ads": [{"url": u, "slug": slug_of(u),
                                   "id": slug_of(u).split("-", 1)[0]}
                                  for u in rows]},
                         ensure_ascii=False, indent=1))
        return
    if (a.since or a.live) and not a.fetch:
        note("--since / --live imply --fetch here: the dates are on the "
             "pages and the sitemap has none.")
    today = datetime.date.today().isoformat()
    kept, broken, gone, expired, tenders = [], [], 0, 0, 0
    needle = fold(a.search) if a.search else None
    for u in rows:
        code, page = get(u)
        if code in (404, 410):
            gone += 1
            continue
        if code != 200:
            broken.append((u, f"HTTP {code}"))
            continue
        posting, why = posting_on(page)
        if posting is None:
            broken.append((u, why))
            continue
        c = card(u, posting)
        if c["tender_like"]:
            tenders += 1
            if a.jobs_only:
                continue
        if a.since and (not c["posted"] or c["posted"] < a.since):
            continue
        if a.live and c["valid_through"] and c["valid_through"] < today:
            expired += 1
            continue
        if needle and needle not in fold(c["title"] or ""):
            continue
        kept.append(c)
    if gone:
        note(f"{gone} answered 404 or 410 — listed in the sitemap and no "
             f"longer on the site.")
    if a.live:
        note(f"{expired} dropped on a past `validThrough`.")
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{slug_of(u)} ({w})" for u, w in broken[:5]))
    print(json.dumps({"source": "gozambiajobs", "country": "ZM",
                      "asked": len(rows), "kept": len(kept), "gone": gone,
                      "unreadable": len(broken), "tender_like": tenders,
                      "expired_dropped": expired if a.live else None,
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken or gone:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{APEX}/jobs/{a.slug}"
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.slug} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    posting, why = posting_on(page)
    if posting is None:
        die(f"{url}: {why}")
    print(json.dumps(card(url, posting), ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="advertisements from the job sitemap")
    li.add_argument("--limit", type=int)
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="filter on `datePosted`, which is on the page — "
                         "implies --fetch")
    li.add_argument("--live", action="store_true",
                    help="drop advertisements whose `validThrough` has passed "
                         "— implies --fetch")
    li.add_argument("--search", help="match the title; folds accents")
    li.add_argument("--jobs-only", action="store_true", dest="jobs_only",
                    help="drop slugs that read as procurement notices — five "
                         "of 358 on 2026-09-07. **Lexical and English**; the "
                         "count is reported whether or not you pass this")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for its fields; without it the "
                         "listing is the sitemap alone, one request")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
