#!/usr/bin/env python3
"""XpressJobs (`xpress.jobs`) — Sri Lanka, and the listing row IS the advertisement.

  xpressjobs.py search [--keyword X] [--pages N] [--limit N]

**Every HTML route on this host returns the same 1 766-byte shell** — `/Jobs`,
a sector page, an organisation page — with no payload carrier and no
`JobPosting`. The board is behind a JSON API its own front end calls, and the
path was found by loading one page in a browser: it is not in the 4.3 MB
bundle, which assembles the base at runtime.

  **The browser DISCOVERED the path. It does not read the board.**
  `robots.txt` permits `/api/jobs/searchJobs`, so the reading goes through the
  ordinary guarded fetcher like every other adapter here.

THE ANCHOR IS `recordCount`, AND IT SITS ON THE ROWS

Every row carries `recordCount` — the board's own total, not a count of what
this script parsed. It is printed beside our own count on every run, because a
partition of one's own output is an arithmetic identity and cannot fail while
the extraction fails.

  page 218 -> 20 rows      218 x 20 + 4 = 4 364
  page 219 ->  4 rows      recordCount  = 4 364
  page 400 ->  0 rows      a clean stop, not an error
                           (fetched 2026-09-08 12:00:14 to 12:00:44 UTC —
                            times taken from the provenance beside each body,
                            not from memory)

**AND AN EMPTY PAGE CARRIES NO ANCHOR.** `recordCount` lives on rows, so the
page that ends the sweep has none. The total is therefore captured from the
FIRST non-empty page and held; a run that never sees a row has no anchor at
all, and says so rather than reporting zero.

THE STOCK MOVES WITHIN THE HOUR: 4 354 and 4 356 when the route was found,
4 364 at 11:59:42 UTC and 4 365 some three minutes later, all on
2026-09-08. A mismatch of a few between our count and `recordCount` is
this board being alive; it is reported, never reconciled away.

AND NO `url` IS EMITTED, for the same reason. There is no address field in the
API response, so any URL would be one this script composed — and every HTML
route on this host answers 200 with the same shell, so a composed address would
LOOK right and resolve to nothing. `jobId` is emitted instead: it is the site's
own identifier and it is what the ledger keys on.

NO PER-ADVERTISEMENT ENDPOINT IS DECLARED HERE, because none was verified.
`overview` is a summary of about 120 characters and not the description, and
the HTML advertisement routes serve the shell above. What this script emits is
what the API gives.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA
from _zero import zero_note

BASE = "https://xpress.jobs"
SEARCH = BASE + "/api/jobs/searchJobs"
PAGE_SIZE = 20

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[xpressjobs] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# The host declares no `Crawl-delay`; this spacing is ours and declared as ours.
# **3 s, and the figure is measured, not chosen.** At 1.5 s a full sweep took
# HTTP 400 at the 26th request, 51 seconds in — roughly 30 requests a minute.
# Page 26 fetched alone immediately afterwards returned its 20 rows, so the 400
# was a rate and not a page. The limit is the host's and this is our margin
# under it.
_PACE = Pace("xpress.jobs", own=3.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "application/json",
        "Accept-Language": "en-LK,en;q=0.9,si;q=0.8,ta;q=0.7",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def page_url(page, keyword=""):
    q = urllib.parse.urlencode({
        "page": page, "pageSize": PAGE_SIZE, "keyword": keyword,
        "locations": "", "sectors": "",
    })
    return f"{SEARCH}?{q}"


class Truncated(Exception):
    """The sweep stopped early. It carries no verdict about the board."""


def fetch_page(page, keyword):
    url = page_url(page, keyword)
    code, body = get(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the search endpoint is gone", EXIT_GONE)
    if code in (400, 429, 503):
        # **Measured: this host answers 400 when swept too fast.** One backoff,
        # then the caller is told how far it got rather than being left with a
        # truncation that looks like a result.
        note(f"HTTP {code} on page {page} — backing off 30 s and retrying once")
        time.sleep(30)
        code, body = get(url)
    if code != 200:
        raise Truncated(f"{url}: HTTP {code}. **A readable body is not an "
                        f"answer — the code decides.**")
    try:
        rows = json.loads(body)
    except ValueError as e:
        die(f"{url}: the body is not JSON ({e}). **This is a parse failure "
            f"and not an empty board** — the two are different findings.")
    if not isinstance(rows, list):
        die(f"{url}: expected a list at the top level, got "
            f"{type(rows).__name__}. The shape changed.")
    return rows


def row_out(r):
    return {
        "source": "xpressjobs",
        "country": "LK",
        "ledger_id": f"xpressjobs:{r.get('jobId')}",
        "id": r.get("jobId"),
        "title": r.get("jobTitle"),
        "employer": r.get("organizationName"),
        "employer_id": r.get("organizationId"),
        "location_text": (r.get("locations") or "").strip() or None,
        "employment_type": r.get("jobType"),
        "posted": r.get("createdDate"),
        "expires": r.get("expiryDateOnWebsite"),
        "remote": r.get("remote"),
        "overview_chars": len(r.get("overview") or ""),
        "government": r.get("isGovernmentJob"),
    }


def cmd_search(a):
    # **`kept` and `seen_ids` grow in the SAME branch**, so `kept - len(seen_ids)`
    # is zero by construction and would report "0 duplicates" over a sweep that
    # skipped sixteen hundred. Duplicates are counted where they are skipped.
    kept, seen_ids, record_count, pages, dupes = 0, set(), None, 0, 0
    page = 1
    while True:
        try:
            rows = fetch_page(page, a.keyword)
        except Truncated as e:
            # **A sweep that stops early announces itself.** Without this the
            # caller sees N rows and an error, and nothing says N of how many.
            note(str(e))
            report(kept, dupes, record_count, pages, a, truncated=True)
            sys.exit(EXIT_PARTIAL)
        if not rows:
            break
        pages += 1
        if record_count is None:
            # **Captured from the FIRST non-empty page**: the page that ends
            # the sweep carries no rows and therefore no anchor.
            record_count = rows[0].get("recordCount")
        for r in rows:
            jid = r.get("jobId")
            if jid in seen_ids:
                dupes += 1
                continue
            seen_ids.add(jid)
            print(json.dumps(row_out(r), ensure_ascii=False))
            kept += 1
            if a.limit and kept >= a.limit:
                note(f"stopped at --limit {a.limit}")
                return report(kept, dupes, record_count, pages, a,
                              partial=True)
        if a.pages and pages >= a.pages:
            return report(kept, dupes, record_count, pages, a,
                          partial=True)
        page += 1
    return report(kept, dupes, record_count, pages, a)


def report(kept, dupes, record_count, pages, a, partial=False,
           truncated=False):
    if kept == 0:
        # Never "the board is empty": say which of the two this cannot tell.
        note(zero_note("xpressjobs", what=a.keyword or None, market="LK"))
        if record_count is None:
            note("and no `recordCount` was seen either — the anchor lives on "
                 "the rows, so a run that returns none has nothing to check "
                 "itself against. **This is an unknown, not a zero.**")
        sys.exit(EXIT_PARTIAL)
    note(f"{kept} distinct advertisement(s) over {pages} page(s); "
         f"{dupes} duplicate row(s) skipped, so the pager served "
         f"{kept + dupes} slots for {kept} advertisements.")
    if truncated:
        note(f"**THE SWEEP DID NOT FINISH.** What is above is {kept} "
             f"advertisement(s), not the board" +
             (f", which declares {record_count}." if record_count else
              " — and no `recordCount` was captured, so there is nothing to "
              "measure the shortfall against.") +
             " **This is a partial read and not a count.**")
        return
    if record_count is None:
        note("**no `recordCount` on the rows** — the board's own total was not "
             "seen, so nothing but this script's own counting attests the "
             "figure above.")
    elif partial:
        note(f"the board declares **{record_count}**; this run was bounded and "
             f"read {kept} of them.")
    elif kept == record_count:
        note(f"the board declares **{record_count}** and this run read exactly "
             f"that. Two independent counts agree.")
    else:
        gap = record_count - kept
        note(f"the board declares **{record_count}** and this run read {kept} "
             f"distinct — a difference of {gap}.")
        if dupes and abs(gap - dupes) <= max(5, record_count // 200):
            note(f"**And {dupes} duplicate rows were skipped, which accounts "
                 f"for it.** `recordCount` counts the ROW SLOTS this pager "
                 f"serves, not distinct advertisements: the two agree on slots "
                 f"and neither of them counts the board. **The number of "
                 f"advertisements is {kept}.**")
        elif abs(gap) <= max(5, record_count // 200):
            note("a gap this small is churn — the stock moved between the "
                 "first page and the last.")
        else:
            note(f"**{gap} is too large to be churn and {dupes} duplicates do "
                 f"not account for it.** Neither figure is established here; "
                 f"what is certain is {kept} distinct `jobId` read over "
                 f"{pages} pages.")


def main():
    p = argparse.ArgumentParser(
        description="Sri Lankan advertisements from XpressJobs, through the "
                    "JSON API its own front end calls.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="advertisements, one page of 20 per request")
    s.add_argument("--keyword", default="",
                   help="the board's own keyword filter; empty means every ad")
    s.add_argument("--pages", type=int, help="stop after N pages")
    s.add_argument("--limit", type=int, help="stop after N advertisements")
    s.set_defaults(fn=cmd_search)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
