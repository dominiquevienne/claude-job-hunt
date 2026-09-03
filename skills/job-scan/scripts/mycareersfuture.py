#!/usr/bin/env python3
"""Fetch Singapore ads from MyCareersFuture — the whole corpus, and none of
its text.

Singapore's national job portal, run by the **Skills and Workforce Development
Agency (SWDA)** — the renamed Workforce Singapore, which is why `wsg.gov.sg`
now lands on `swda.gov.sg`. Its public API needs **no key, no cookie, no
account and no browser**:

  GET  https://api.mycareersfuture.gov.sg/v2/jobs?limit=100&page=0
       → 200 JSON, {results[], total, countWithoutFilters, _links}
  GET  https://api.mycareersfuture.gov.sg/v2/jobs/<uuid>
       → 200 JSON, the same 29-key record, one ad
  https://www.mycareersfuture.gov.sg/job/<uuid>
       → the ad, for a human; the slug is rebuilt client-side

**The whole corpus is reachable.** Page 967 returns 78 rows and page 968
returns 0, so 96 778 ads on 96 869 reported — there is no pagination ceiling
of the kind Indeed and JobStreet impose. Verified 2026-09-02.

THE CONSTRAINT THAT SHAPES THIS ADAPTER IS NOT TECHNICAL. SWDA's terms of use
(read 2026-09-02, last updated 27 Aug 2026) contain **no anti-automation
clause, no quota, no rate limit and no mention of the API** — reading is not
the problem. What they do say, twice, is:

    "All rights reserved. No part of any works on the Website may be
     reproduced, stored in a retrieval system, or transmitted in any form or
     by any means … without written permission from SWDA."   (§15, §37)

    "Except as set forth below, caching and links to, and the framing of this
     website … is strictly prohibited."                      (§11, §33)

A pipeline ledger is a retrieval system, and it is a cache. **So this adapter
emits identifiers, URLs and the fields a match is scored on — never the text
of an ad.** `description` is read to measure it and dropped; the card carries
`description_chars` and nothing else. To read an ad, open its URL. Clause 16
provides for written permission to go further; asking for it is the user's
decision, not the plugin's.

THE SILENT NO-OP, AND THE LOUD ONE. The API is strict about **values** and
silent about **names**:

    ?categories=Not A Category      → 400, a real rejection
    ?employmentTypes=Full Time      → 200, 71 850 of 97 091 — the filter works
    ?employmentType=Full Time       → 200, 97 091 of 97 091 — SILENTLY IGNORED
    ?nonsense=zzz                   → 200, the whole corpus, no complaint

**A parameter name it does not know is accepted, ignored and answered 200**,
so the singular of a plural filter reads as a working search over the entire
board. A wrong *value* on a known name is a 400 you cannot miss; a wrong
*name* is a result set you will believe.

The response says so if you read it: **`total` equals `countWithoutFilters`
exactly when nothing filtered.** Every filtered call here compares the two and
says out loud when a filter did nothing, which is the only way to tell a
working filter from a typo.

`Re-open` IS A NORMAL STATUS. Of 40 ads drawn from the sitemap, 31 were
`Open` and **9 `Re-open`**, all 40 live. They are not rare and they are not
stale: the search is sorted newest-first, so `Re-open` rows sit deeper — page
0 was 100/100 `Open`, page 800 was 100/100 `Re-open`. **Code that keeps only
`status == "Open"` throws away a fifth of the board**, and a shallow sweep
never notices because it never reaches them.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _robots import allowed as robots_allowed

from _zero import zero_note

API = "https://api.mycareersfuture.gov.sg/v2/jobs"
WEB = "https://www.mycareersfuture.gov.sg/job/{uuid}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

# 101 is already a 400; the ceiling is 100, not 200.
MAX_LIMIT = 100

# The filters that are real, with the spelling that works. The singular of the
# first two is accepted and ignored — see the module docstring.
FILTERS = {
    "employment-types": "employmentTypes",
    "position-levels": "positionLevels",
    "salary": "salary",
    "categories": "categories",
}


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def _robots_gate(url, tag, exit_code=7):
    """Ask before fetching — per host and **per path**. Issues #100, #101.

    `verdict()` answers *is this host closed in one block*. **A site that
    refuses its ad path while leaving its root open passes that and refuses
    every advertisement** — `empleate.gob.hn` does exactly that, closing
    `/Vacantes/` to `User-agent: *` with `/` absent.

    It sits **inside the fetch function**, so every request is covered rather
    than the first one, and a refusal **stops the command** with exit 7 and the
    module's own words. **This adapter decides nothing about what a refusal
    means** — deciding is what turns a check into a decoration.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return None
    a = robots_allowed(parts.netloc, parts.path or "/")
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", exit_code)
    if a.get("requested_host") and a["host"] != a["requested_host"]:
        print(f"[mycareersfuture] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts. A platform that has "
              f"been renamed reaches an adapter this way before it reaches it "
              f"as a rename.", file=__import__("sys").stderr)
    return a



def note(msg):
    print(f"[mycareersfuture] {msg}", file=sys.stderr)


def get(url, retries=1):
    _robots_gate(url, 'mycareersfuture')
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(decode_body(r.read(), r.headers)[0])
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            if exc.code == 400:
                die(f"{url}: HTTP 400 — the API rejects unknown *values* on "
                    f"a known parameter (a category or employment type it "
                    f"does not have), `limit` above {MAX_LIMIT}, and an "
                    f"unknown `sortBy`. An unknown parameter *name*, by "
                    f"contrast, is accepted and ignored.")
            die(f"{url}: HTTP {exc.code}")
        except (urllib.error.URLError, OSError) as exc:
            if attempt == retries:
                die(f"{url}: {exc}")
            time.sleep(5)
    return None


def query(a, page):
    q = {"limit": min(a.limit_per_page, MAX_LIMIT), "page": page}
    if getattr(a, "keyword", None):
        q["search"] = a.keyword
    applied = []
    for cli, param in FILTERS.items():
        val = getattr(a, cli.replace("-", "_"), None)
        if val:
            q[param] = val
            applied.append(param)
    return f"{API}?{urllib.parse.urlencode(q)}", applied


def check_filters(d, applied, where):
    """`total` == `countWithoutFilters` means nothing filtered. Say so."""
    if not applied:
        return
    total, plain = d.get("total"), d.get("countWithoutFilters")
    if total is None or plain is None:
        return
    if total == plain:
        note(f"{where}: {', '.join(applied)} changed nothing — {total} with "
             f"the filter and {plain} without it. This API answers 200 to a "
             f"parameter name it does not know and ignores it, so a result "
             f"set that looks filtered may not be. Check the spelling.")
    else:
        note(f"{where}: filter kept {total} of {plain}.")


def card(r):
    """Identifiers, URLs and scoring fields. **No ad text** — see the header."""
    sal = r.get("salary") or {}
    addr = r.get("address") or {}
    meta = r.get("metadata") or {}
    hiring = (r.get("hiringCompany") or {}).get("name")
    posted = (r.get("postedCompany") or {}).get("name")
    uuid = r.get("uuid")
    return {
        "id": uuid,
        "ledger_id": f"mycareersfuture:{uuid}",
        "url": WEB.format(uuid=uuid),
        # The reference a human sees on the page, MCF-2026-1366420.
        "job_post_id": meta.get("jobPostId"),
        "title": r.get("title"),
        # `postedCompany` is named on every ad and is often an agency;
        # **`hiringCompany` was named on 59 of 997**. When it is absent there
        # is no key of any kind pointing at the real employer — see the file.
        "posted_company": posted,
        "hiring_company": hiring,
        "employer_named": bool(hiring),
        # 997 of 997 carried a salary, and 997 of 997 of those were monthly.
        # **The unit travels with the number.** This board is single-country,
        # so the currency is knowable — and that is exactly why it was missing:
        # obvious to whoever wrote the adapter, absent from the row a ledger
        # keeps. *A number in an unknown unit is worse than a number absent,
        # because it compares* — `shared/plausible-and-false.md`, mechanism 1.
        "salary_currency_of_the_board": "SGD",
        "salary_min": sal.get("minimum"),
        "salary_max": sal.get("maximum"),
        "salary_type": (sal.get("type") or {}).get("salaryType"),
        "employment_types": [t.get("employmentType")
                             for t in (r.get("employmentTypes") or [])],
        "position_levels": [p.get("position")
                            for p in (r.get("positionLevels") or [])],
        "categories": [c.get("category") for c in (r.get("categories") or [])],
        # Skills are the scoring surface this board gives instead of the text.
        "skills": [s.get("skill") for s in (r.get("skills") or [])],
        "ssoc_code": r.get("ssocCode"),
        # Present on 100 of 100; **0 on 10 of them**, which is "entry level",
        # not "unknown". Do not read a missing value into the zero.
        "minimum_years_experience": r.get("minimumYearsExperience"),
        "vacancies": r.get("numberOfVacancies"),
        "postal_code": addr.get("postalCode"),
        "flexible_work": [f.get("flexibleWorkArrangement")
                          for f in (r.get("flexibleWorkArrangements") or [])],
        "posted": (meta.get("newPostingDate") or "")[:10] or None,
        # A real closing date, on 997 of 997.
        "closes": (meta.get("expiryDate") or "")[:10] or None,
        # `Open` and `Re-open` are both live. Never filter on `Open` alone.
        "status": (r.get("status") or {}).get("jobStatus"),
        "source": r.get("sourceCode"),
        # The text itself is deliberately not here. Its length is, so a sweep
        # can tell an empty ad from a full one without keeping either.
        "description_chars": len(r.get("description") or ""),
    }


def cmd_count(a):
    url, applied = query(a, 0)
    d = get(url)
    if d is None:
        die("the search endpoint returned 404, which it does not do for a "
            "search — re-verify mycareersfuture.md.")
    check_filters(d, applied, "count")
    print(json.dumps({
        "query": {"keyword": a.keyword,
                  "filters": {p: getattr(a, c.replace("-", "_"))
                              for c, p in FILTERS.items()
                              if getattr(a, c.replace("-", "_"), None)}},
        "matches": d.get("total"),
        "without_filters": d.get("countWithoutFilters"),
    }, ensure_ascii=False))


def cmd_search(a):
    seen, kept, page, total = set(), 0, 0, None
    statuses = {}
    while True:
        url, applied = query(a, page)
        d = get(url)
        if d is None:
            die("404 on a search URL — re-verify mycareersfuture.md.")
        rows = d.get("results") or []
        if page == 0:
            total = d.get("total")
            check_filters(d, applied, "search")
        if not rows:
            # The end of the corpus is a 200 with an empty list, never a 404
            # and never an error. Page 968 does this; so does page 5 000.
            note(f"page {page} returned 0 rows — that is how this API says "
                 f"'past the end'. Stopping.")
            break
        for r in rows:
            c = card(r)
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            statuses[c["status"]] = statuses.get(c["status"], 0) + 1
            print(json.dumps(c, ensure_ascii=False))
            kept += 1
            if a.limit and kept >= a.limit:
                break
        if a.limit and kept >= a.limit:
            break
        page += 1
        if a.pages and page >= a.pages:
            break
        time.sleep(a.delay)
    if kept == 0:
        note(zero_note("mycareersfuture", what=a.keyword))
    note(f"{kept} ads returned of {total} matching.")
    note("status mix: " + ", ".join(f"{k} {v}" for k, v in statuses.items())
         + ". `Re-open` is live — 9 of 40 sitemap ads carried it — and the "
           "sort is newest-first, so a shallow sweep sees `Open` only.")
    note("no ad text was written: SWDA's terms forbid storing Website Content "
         "in a retrieval system, so the card carries `description_chars` and "
         "the URL. Read the ad at its URL.")


def cmd_ad(a):
    d = get(f"{API}/{a.id}")
    if d is None:
        # {"message": "UUID is not found in the database."} — the same 404 for
        # a malformed id and for an ad that is gone.
        die(f"{a.id}: not in the database. On this API a well-formed id that "
            f"has been taken down and a malformed id give the same 404.", 3)
    c = card(d)
    print(json.dumps(c, ensure_ascii=False))
    if a.print_description:
        # Printed for immediate reading, never for the ledger. The terms
        # forbid storing it; stdout here is a screen, not a store.
        note("printing the ad text for immediate reading — do not write it to "
             "the ledger or to any file.")
        print(d.get("description") or "", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, h in (("count", cmd_count, "how many match"),
                        ("search", cmd_search, "read the ads"),
                        ("ad", cmd_ad, "read one ad by uuid")):
        c = sub.add_parser(name, help=h)
        if name == "ad":
            c.add_argument("--id", required=True, help="the ad's uuid")
            c.add_argument("--print-description", action="store_true",
                           dest="print_description",
                           help="print the ad text to stderr for immediate "
                                "reading. It is never stored")
        else:
            c.add_argument("--keyword", help="free text; `search=`")
            c.add_argument("--salary", type=int,
                           help="minimum monthly salary in SGD")
            c.add_argument("--employment-types", dest="employment_types",
                           help="'Full Time', 'Part Time', 'Contract'… "
                                "**plural**; the singular is silently ignored")
            c.add_argument("--position-levels", dest="position_levels",
                           help="'Manager', 'Senior Executive'… plural")
            c.add_argument("--categories", help="e.g. 'Information Technology'")
        if name == "search":
            c.add_argument("--limit", type=int, help="ads to return in total")
            c.add_argument("--pages", type=int, help="pages to read")
            c.add_argument("--limit-per-page", type=int, default=MAX_LIMIT,
                           dest="limit_per_page",
                           help=f"rows per call, {MAX_LIMIT} max — 101 is a "
                                f"400")
            c.add_argument("--delay", type=float, default=1.0)
        else:
            c.set_defaults(limit_per_page=MAX_LIMIT)
        c.set_defaults(func=fn)
    a = p.parse_args()
    if getattr(a, "limit_per_page", MAX_LIMIT) > MAX_LIMIT:
        die(f"--limit-per-page above {MAX_LIMIT} is an HTTP 400 at the API. "
            f"101 already fails.")
    a.func(a)


if __name__ == "__main__":
    main()
