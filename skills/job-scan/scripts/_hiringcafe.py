#!/usr/bin/env python3
"""The one place a `hiringcafe.com` URL is built — and the one that refuses.

**Three commands built the same refused URL, each with its own client.**
`hiringcafe.py:119`, `ats.py:761` and `workday.py:317` all assembled

    https://hiringcafe.com/?searchState={"companyNames":["…"]}

and `hiringcafe.com/robots.txt` refuses exactly that shape to `User-agent: *`:

    Disallow: /*?searchState=*

**Issue #123 named only one of the three**, because the other two were found by
grepping for the file rather than for the URL. Two adapters more —
`pinpoint.py` and `recruitee.py` — inherit it by running `hiringcafe.py search`
as a subprocess.

**That is the defect this module exists to make impossible**, and it is the
same shape as `jobroom.py`'s three URL parsers fixed the same evening: several
places doing one thing slightly differently, one of them right by accident.
A single constructor cannot drift from itself.

WHY IT REFUSES FROM THE RECORD RATHER THAN ASKING

Asking `_robots.allowed()` would be the habit everywhere else in this
repository, and here it is wrong: **collection from this host is suspended**,
and a guard call is a request to the host like any other. So the verdict is
the one measured on **2026-09-03** and written into #123, and this module says
so rather than implying a fresh check.

**That is a dated fact, not a permanent one.** `hiringcafe.com` may publish
something else tomorrow; nothing here would notice. Re-measuring means lifting
the suspension first, and that is a decision, not a code path.

WHAT IS OPEN, MEASURED IN THE SAME PASS AND RECORDED IN #123

    /job/<slug>                 allowed — and carries `__NEXT_DATA__` with
                                91 fields, plus a JSON-LD JobPosting
    /jobs, /recently-posted-jobs allowed
    the six declared sitemaps    allowed
    /?searchState=*              REFUSED
    /viewjob/<id>                REFUSED

**The `ad` mode was licit from the beginning; only `search` was not.** Nothing
this project measures needs the refused URL — the country fields, the
compensation fields and the workplace fields are all on the allowed page.

Rebuilding the adapter onto that route waits on the browser-degraded mode
(#124), because the host answers 403 to a script on **every** path including
the ones it allows. **That is a separate decision and this module does not
anticipate it.**
"""

import json
import urllib.parse

__all__ = ["SEARCH_RULE", "MEASURED_ON", "search_url", "refusal"]

SEARCH_RULE = "/*?searchState=*"
MEASURED_ON = "2026-09-03"
BASE = "https://hiringcafe.com/"


def search_url(params):
    """The URL the three commands used to build — **for the record, not to
    fetch.**

    Returned so a refusal can quote the exact thing it is refusing. Nothing in
    this repository should pass it to a client; `refusal()` is what a caller
    wants.
    """
    return BASE + "?" + urllib.parse.urlencode(params)


def company_search_url(employer):
    """`searchState={"companyNames":["…"]}` — the shape `resolve` built."""
    return search_url({"searchState": json.dumps(
        {"companyNames": [employer]}, separators=(",", ":"))})


def refusal(tag, what="this search"):
    """The sentence a command prints instead of making the request.

    Written once so three commands cannot say three different things about
    one rule — which is how `ats.py` came to carry #59's misreading as a
    comment while `hiringcafe.py` had moved on.
    """
    return (
        f"[{tag}] {what} is built as `{BASE}?searchState=…`, and "
        f"**`hiringcafe.com/robots.txt` refuses that shape to `User-agent: *` "
        f"— `Disallow: {SEARCH_RULE}`** (measured {MEASURED_ON}, issue #123). "
        f"No request was made.\n"
        f"  **The `ad` mode was always licit; only this search was not.** "
        f"`/job/<slug>` is allowed and carries more than the refused URL did "
        f"— `__NEXT_DATA__` with 91 fields and a JSON-LD JobPosting — and the "
        f"six declared sitemaps are allowed too.\n"
        f"  **Collection from this host is suspended pending a decision**, so "
        f"the verdict above is read from the record rather than asked afresh: "
        f"a guard call is a request like any other. Resolving an employer's "
        f"ATS by hand meanwhile: open its careers page and read the host, the "
        f"tenant and the site out of the URL.")
