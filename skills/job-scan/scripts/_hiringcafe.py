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
repository, and here it is wrong: the rule is **written**, `Disallow:
/*?searchState=*`, and a guard call is a request to the host like any other.
So the verdict is the one measured on **2026-09-03** and written into #123,
and this module says so rather than implying a fresh check.

**That is a dated fact, not a permanent one.** `hiringcafe.com` may publish
something else tomorrow; nothing here would notice.

THE DECISION — 2026-09-11, THE REPOSITORY'S OWNER, VERBATIM (#198)

    « Je confirme la dérogation hiringcafe, assigne #198 »

Given after being shown: that the pilot's local doctrine named
SmartRecruiters as the one exception; that the refusal to lift is a `Disallow` WRITTEN in the rules, not
a refusal at the transport; and that the realistic cost is HiringCafe
blocking the address the requests come from — the candidate's, not this
project's. **Unconditional.** Until then this module carried a second refusal
beside the rule — «&nbsp;collection from this host is suspended pending a
decision&nbsp;» — and **both are lifted by that decision, together**: a flag
that lifted the rule and left the suspension would look like it acts and act
on half.

**How it is lifted: `boards.hiringcafe.override_robots: true` in the user's
own `config.yml`**, read by `hiringcafe.py` (`_override.enabled`), for this
host only, announced on every run where it acts — the SmartRecruiters
procedure of `shared/robots-policy.md`, applied a third time. Absent key: the
refusal below, which names the file consulted and the sentence to add. **It
does not follow from the policy's four questions** — the rule is
even-handed, aimed at nobody in particular — and the record says so rather
than pretending it does; see `shared/robots-policy.md`.

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

__all__ = ["SEARCH_RULE", "MEASURED_ON", "DECIDED_ON", "HOST", "search_url",
           "refusal"]

SEARCH_RULE = "/*?searchState=*"
MEASURED_ON = "2026-09-03"
DECIDED_ON = "2026-09-11"          # the owner's override decision, #198
HOST = "hiringcafe.com"
BASE = f"https://{HOST}/"


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


def refusal(tag, what="this search", where=None):
    """The sentence a command prints instead of making the request.

    Written once so three commands cannot say three different things about
    one rule — which is how `ats.py` came to carry #59's misreading as a
    comment while `hiringcafe.py` had moved on.

    `where` is what `_override.enabled("hiringcafe")` consulted — the
    sentence, not only the path — when the caller reads the key. **A caller
    that does not read it says so**: `ats.py resolve` and `workday.py
    resolve` print this too, and the key does not reach them; the honest
    line is «&nbsp;this command does not read the key, `hiringcafe.py
    search` does&nbsp;» rather than an instruction that would change
    nothing here.
    """
    lift = (f"  Consulted: {where}." if where else
            f"  **This command does not read the key**; `hiringcafe.py "
            f"search` does.")
    return (
        f"[{tag}] {what} is built as `{BASE}?searchState=…`, and "
        f"**`{HOST}/robots.txt` refuses that shape to `User-agent: *` "
        f"— `Disallow: {SEARCH_RULE}`** (measured {MEASURED_ON}, issue #123). "
        f"No request was made.\n"
        f"  **The `ad` mode was always licit; only this search was not.** "
        f"`/job/<slug>` is allowed and carries more than the refused URL did "
        f"— `__NEXT_DATA__` with 91 fields and a JSON-LD JobPosting — and the "
        f"six declared sitemaps are allowed too.\n"
        f"  **The repository's owner decided on {DECIDED_ON} that this refusal "
        f"may be crossed (#198)** — on the user's own consent: "
        f"`boards.hiringcafe.override_robots: true` in config.yml, which "
        f"`shared/setup.md` writes only after saying what is crossed and what "
        f"it costs — **your own address**, not this project's.\n"
        f"{lift}")
