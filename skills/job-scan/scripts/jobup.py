#!/usr/bin/env python3
"""Sweep jobup.ch and jobs.ch over plain HTTP — no browser, no cookie, no login.

**The adapter files made the Chrome extension a prerequisite**, so a user
without it had no Swiss sweep at all, on the two largest boards in this
repository. Measured 2026-09-02: twelve ads and three listing pages answer
`200` to a plain request, and **the structured data is in the HTML that
arrives**. Issue #68.

WHERE THE DATA IS, WHICH IS NOT WHERE THE ISSUE EXPECTED IT. The listing page
carries **one `JobPosting` per card**, wrapped in an `ItemList`:

    {"@type": "ItemList", "itemListElement":
       [{"@type": "ListItem", "position": 1,
         "item": {"@type": "JobPosting", …}}, …]}

and those carry **title, employer, date, employment type, url, identifier and
the location** — `addressLocality` filled on 13 of 20. **The ad page's own
`jobLocation` is empty on 12 of 12**, so the geography lives on the listing and
only there. A sweep that reads ad pages for location loses it.

*(`_ldjson.py` unwraps `ItemList` because of this: it previously saw zero
postings on a page holding twenty.)*

TWO THINGS THE LISTING DOES NOT CARRY: the full description and any salary.
The description is on the ad page, in its own `JobPosting`, 1 443 to 6 247
characters. `--with-description` fetches it, one request per ad.

A PROMOTED CARD IS REPEATED ACROSS PAGES. Measured: one ad sat at position 13
of page 1 **and position 1 of page 2**. So ids are deduplicated and the repeats
are counted out loud — **but a repeat is not a pagination failure**, and the
two are told apart: a page whose ids are *entirely* contained in what came
before has not advanced (exit 6), while a handful of repeats is paid placement.

AND AN AD URL ANSWERS IN FOUR WAYS, WHICH `ad` READS BEFORE ITS BODY.
`shared/boards/jobup.md` has the table: `410` is gone and still serves the ad's
own block, an expired ad **redirects to its trade's category page** carrying
twenty valid postings and no mention of the job, `404` never existed, and only
a plain `200` is the advert. **The block count decides none of it** (#88).

    jobup.py search --site jobup --term developpeur --pages 2
    jobup.py search --site jobs-ch --term entwickler --location Bern
    jobup.py ad --url https://www.jobup.ch/fr/emplois/detail/<uuid>/
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _ldjson import label, one, postings

from _locations import drop_report

from _robots import verdict as robots_verdict

from _zero import zero_note

SITES = {
    "jobup": {"host": "www.jobup.ch", "path": "/fr/emplois/",
              "detail": "/fr/emplois/detail/"},
    "jobs-ch": {"host": "www.jobs.ch", "path": "/de/stellenangebote/",
                "detail": "/de/stellenangebote/detail/"},
}
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
EXIT_PARTIAL = 6


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobup] {msg}", file=sys.stderr)


def get(url):
    """Returns `(status, body, landed)`. **Where it landed is half the signal.**"""
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        # identity, because a compressed body makes every size measurement in
        # this file a different number (#71).
        "Accept-Encoding": "identity",
        "Accept": "text/html,application/xhtml+xml",
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.getcode(), r.read().decode("utf-8", "replace"), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace"), getattr(e, "url", url)
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def card(site, p):
    """One row, from the listing's own JobPosting. Values, never keys."""
    ident = one(p.get("identifier")).get("value")
    org = one(p.get("hiringOrganization"))
    addr = one(one(p.get("jobLocation")).get("address"))
    sal = one(p.get("baseSalary"))
    amount = one(sal.get("value"))
    # **The salary block is a shell.** Served as MonetaryAmount + an empty
    # QuantitativeValue on every ad measured: counting the key gives 100%,
    # counting the value gives 25% (#67).
    figure = amount.get("value") or amount.get("minValue") or amount.get("maxValue")
    return {
        "id": ident,
        "ledger_id": f"{site}:{ident}",
        "url": p.get("url"),
        "title": p.get("title"),
        "company": org.get("name"),
        # The ad page's own jobLocation is empty on every ad measured; this is
        # the only place the town appears.
        "location_text": addr.get("addressLocality"),
        "country": addr.get("addressCountry"),
        "posted": p.get("datePosted"),
        "employment_type": label(p.get("employmentType")),
        "salary_stated": bool(figure),
        "salary_value": figure,
        "salary_currency": sal.get("currency"),
    }


def cmd_search(a):
    site = SITES[a.site]
    v = robots_verdict(site["host"])
    if not v["sweep"]:
        die(f"{site['host']}: {v['reason']}", 7)
    seen, rows, repeats = set(), [], 0
    for page in range(1, a.pages + 1):
        q = {"term": a.term} if a.term else {}
        if page > 1:
            q["page"] = page
        url = f"https://{site['host']}{site['path']}?" + urllib.parse.urlencode(q)
        status, body, _ = get(url)
        if status != 200:
            die(f"{url}: HTTP {status}")
        found = postings(body)
        if not found:
            note(f"page {page} carried no JobPosting — stopping. **This is a "
                 f"reading failure or the end of the results, and they are not "
                 f"the same**: a listing page with results carries one block "
                 f"per card.")
            break
        ids = {one(p.get("identifier")).get("value") for p in found}
        # Entirely repeated → the pagination did not advance. A few repeats →
        # paid placement, which is what a promoted card looks like.
        if ids and ids <= seen:
            note(f"page {page} repeats page {page - 1} entirely — the "
                 f"pagination did not advance. Stopping rather than looping; "
                 f"{len(rows)} row(s) so far and they are good.")
            sys.exit(EXIT_PARTIAL)
        for p in found:
            row = card(a.site, p)
            if not row["id"] or row["id"] in seen:
                repeats += 1
                continue
            seen.add(row["id"])
            rows.append(row)
        time.sleep(a.delay)
    if a.location:
        rows, dropped = drop_report(rows, a.location)
        if dropped:
            note(dropped)
    for row in rows[:a.limit] if a.limit else rows:
        print(json.dumps(row, ensure_ascii=False))
    if not rows:
        note(zero_note(a.site, what=a.term, where=a.location))
    stated = sum(1 for r in rows if r["salary_stated"])
    located = sum(1 for r in rows if r["location_text"])
    note(f"{len(rows)} ad(s) over {a.pages} page(s). "
         f"salary: {stated} of {len(rows)} carry a figure — **the block is "
         f"present on all of them and empty on most** (#67). "
         f"location: {located} of {len(rows)}; the ad page does not carry it "
         f"at all, so this is the only source.")
    if repeats:
        note(f"{repeats} card(s) repeated across pages and were deduplicated — "
             f"paid placement, not a pagination failure: one ad was measured "
             f"at position 13 of page 1 and position 1 of page 2.")


def cmd_ad(a):
    host = urllib.parse.urlsplit(a.url).netloc
    v = robots_verdict(host)
    if not v["sweep"]:
        die(f"{host}: {v['reason']}", 7)
    status, body, landed = get(a.url)
    # **Status, then where it landed, then the ad's own isActive — the block
    # count decides none of it.** jobup.md carries the four-state table (#88).
    if status == 410:
        die(f"{a.url}: HTTP 410 — the board says this ad is gone. It still "
            f"serves the ad's own text and its own JobPosting block, so a "
            f"check that counts blocks would call it open.", 3)
    if status == 404:
        die(f"{a.url}: HTTP 404 — this id never existed on this board. That is "
            f"a different fact from an ad that closed.", 3)
    if landed.rstrip("/") != a.url.rstrip("/"):
        die(f"{a.url} redirected to {landed}. **It is forbidden to conclude "
            f"'open' from a page reached by a redirect**: an expired ad lands "
            f"on its trade's category page, which carries ~20 valid "
            f"JobPosting blocks and no mention of the job (#88).", 3)
    found = postings(body)
    if not found:
        die(f"{a.url}: HTTP 200, no redirect, and no JobPosting. Read the page "
            f"before concluding anything — this is neither a served ad nor a "
            f"recognised absence.")
    p = found[0]
    row = card("jobup" if "jobup" in host else "jobs-ch", p)
    row["url"] = a.url
    desc = p.get("description") or ""
    row["description_chars"] = len(desc)
    if a.with_text:
        row["description"] = desc
    print(json.dumps(row, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="read the listing, one request per page")
    s.add_argument("--site", choices=sorted(SITES), default="jobup")
    s.add_argument("--term")
    s.add_argument("--location", help="town filter, accent-insensitive")
    s.add_argument("--pages", type=int, default=1)
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=1.0)
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="one ad, with its open/closed state")
    d.add_argument("--url", required=True)
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
