#!/usr/bin/env python3
"""Fetch ads from Adzuna — nineteen countries on one key, and 250 calls a day.

Adzuna aggregates job ads in nineteen countries and publishes a single REST
API where the country is a path segment, so one adapter reaches Switzerland,
France, Germany, Austria, the Netherlands, Belgium, Italy, Spain, Poland, the
UK, the US, Canada, Australia, New Zealand, India, Singapore, South Africa,
Brazil and Mexico.

  GET https://api.adzuna.com/v1/api/jobs/<country>/search/<page>
      ?app_id=…&app_key=…&results_per_page=50&what=…&where=…
  GET https://api.adzuna.com/v1/api/jobs/<country>/ad/<adref>
      → undocumented, and it answers — see below

THE BUDGET IS THE DESIGN. The published limits are **25 calls a minute, 250 a
day, 1 000 a week and 2 500 a month**, for everything together. Fifty ads a
call is the ceiling, so a day's budget is 12 500 ads across every country and
every search. **Sweeping nineteen countries does not fit**, and neither does
paging deep on one. This script asks for `results_per_page=50` always, reads
one page per search by default, and refuses to exceed `--max-calls` in a
single run so a loop cannot spend the day's allowance.

`results_per_page` **caps at 50 silently**: 100 and 101 both answer 200 with
50 rows and no complaint. Code that asks for 100 and assumes it got 100 will
page twice as often as it thinks.

THE DESCRIPTION IS A 500-CHARACTER TEASER, and the spec says so — *"truncated
to 500 characters"*. Measured: the median and the maximum are both exactly
500, on every country sampled. **This is a discovery board, not a scoring
board.** The full text lives with the advertiser, behind `redirect_url`, which
is also the link Adzuna's terms require you to send people to.

THE SALARY MAY BE ADZUNA'S GUESS. `salary_is_predicted == '1'` means the
figure came from their Jobsworth estimator, not from the advert. On 50 GB ads:
16 carried a salary, **6 of them predicted**, 10 real. So this script never
emits a field called `salary_min`. It emits **`salary_min_stated`** — the
advertiser's, or nothing — and **`salary_min_adzuna_estimate`** separately.
A number the board invented must not be able to look like a number the
employer wrote.

Everything here was verified against the live API on **2026-09-02** with the
user's own key.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _language import speaks_codes

from _secrets import get as secret_get
from _secrets import missing_note
from _zero import zero_note

API = "https://api.adzuna.com/v1/api"
# **The declaration is central and was applied per adapter**, so this
# file kept a local string of its own and #120 never reached it. It
# named no agent token, carried no version and no contact URL — and it
# described the tool as *"personal job search; one user"*, which this
# repository stopped being. `_ua.UA` is the one declaration. #130.
from _ua import UA

# The API's own list, and it publishes it: an unknown code is a 404 whose JSON
# body names every supported one. Ireland is not among them.
COUNTRIES = ("gb", "us", "at", "au", "be", "br", "ca", "ch", "de", "es", "fr",
             "in", "it", "mx", "nl", "nz", "pl", "sg", "za")

# **The currency of the index, because the payload has none.** Measured
# 2026-09-03: an Adzuna result object carries `id`, `title`, `company`,
# `location`, `category`, `created`, `description`, `redirect_url`, `adref`,
# `contract_time` and `salary_is_predicted` — and **no currency field
# anywhere in the response**. The amounts in `salary_min` / `salary_max` are
# in the local currency of the country index that was queried, and that is a
# fact about *our own request*, not an inference about the advertisement.
#
# **Emitting the numbers without it was a defect, not a shortcut.** This
# adapter serves nineteen countries from one code path; `salary_min: 90000`
# is CHF, GBP, USD, BRL or ZAR depending on a flag, and a ledger that merges
# two countries and sorts by pay is comparing units. *A number in the wrong
# unit is worse than a number absent, because it compares* —
# `shared/plausible-and-false.md`, mechanism 1.
INDEX_CURRENCY = {
    "at": "EUR", "au": "AUD", "be": "EUR", "br": "BRL", "ca": "CAD",
    "ch": "CHF", "de": "EUR", "es": "EUR", "fr": "EUR", "gb": "GBP",
    "in": "INR", "it": "EUR", "mx": "MXN", "nl": "EUR", "nz": "NZD",
    "pl": "PLN", "sg": "SGD", "us": "USD", "za": "ZAR",
}

MAX_PER_PAGE = 50


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def speaks_of(a):
    """`--speaks fr,en` as codes, complaining about what it cannot read.

    **The script does not read `config.yml`** — no adapter here does. The
    skill passes `languages.working` down, because the sweep needs to know
    which of a market's languages the person can actually work in before it
    suggests searching in one of them.
    """
    raw = [x.strip() for x in (a.speaks or "").split(",") if x.strip()]
    codes, unread = speaks_codes(raw)
    if unread:
        note(f"--speaks: {', '.join(unread)} not recognised as a language "
             f"name — ignored rather than guessed. Use a plain name "
             f"(`French`) or a code (`fr`).")
    return codes


def note(msg):
    print(f"[adzuna] {msg}", file=sys.stderr)


def credentials():
    """The environment first, then a credentials file in the workspace.

    **"From the environment, and from nowhere else" was unworkable outside a
    terminal.** In an app-hosted shell the environment may reset between calls, so an exported
    variable does not survive from one to the next: `set -a; . ~/.adzuna.env;
    set +a` is not merely tedious there, it **cannot work**. Issue #110.

    The environment still wins. `config.yml` still never holds a key — that
    file is read aloud, pasted into issues and backed up — and the file lives
    in the user's workspace, which is not a repository.
    """
    app_id = secret_get("ADZUNA_APP_ID", "adzuna")
    app_key = secret_get("ADZUNA_APP_KEY", "adzuna")
    if not app_id or not app_key:
        die(missing_note(["ADZUNA_APP_ID", "ADZUNA_APP_KEY"], "adzuna",
                         "Adzuna", "developer.adzuna.com/signup"))
    return app_id, app_key


class Budget:
    """250 calls a day, shared by every country and every search."""

    def __init__(self, cap):
        self.cap = cap
        self.spent = 0

    def take(self, what):
        if self.spent >= self.cap:
            die(f"--max-calls {self.cap} reached before {what}. The daily "
                f"allowance is 250 calls for all searches together; this run "
                f"stops rather than spending it. Narrow the search or raise "
                f"--max-calls deliberately.", 4)
        self.spent += 1


def get(budget, path, app_id, app_key, retry=True, **params):
    budget.take(path)
    params.update({"app_id": app_id, "app_key": app_key})
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    # Never let the key reach a log line or an error message.
    shown = path
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            ctype = r.headers.get("Content-Type", "")
            body = decode_body(r.read(), r.headers)[0]
            if "json" not in ctype:
                die(f"{shown}: HTTP 200 but Content-Type {ctype!r}. This API "
                    f"answers errors with an HTML page, so a non-JSON 200 is "
                    f"not a result.")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        ctype = exc.headers.get("Content-Type", "")
        body = decode_body(exc.read(), exc.headers)[0]
        if "json" in ctype:
            try:
                msg = json.loads(body).get("display") or body[:200]
            except ValueError:
                msg = body[:200]
            if exc.code == 404:
                die(f"{shown}: HTTP 404 — {msg}", 3)
            if exc.code in (401, 410):
                die(f"{shown}: HTTP {exc.code} — {msg}. The live API answers "
                    f"401 AUTH_FAIL where its own spec documents 410; treat "
                    f"both as a bad key.")
            die(f"{shown}: HTTP {exc.code} — {msg}")
        # The same 1 996-byte "Uh oh" HTML page answers three different
        # things: a call with no credentials (400), a transient failure on
        # search (503) and the ad endpoint misbehaving (503). It is never
        # JSON, so `.json()` on an error is the crash this guards.
        if exc.code >= 500 and retry:
            note(f"{shown}: HTTP {exc.code} with an HTML body — transient. "
                 f"One retry in 10 s, then it stops.")
            time.sleep(10)
            budget.spent -= 1
            return get(budget, path, app_id, app_key, retry=False, **{
                k: v for k, v in params.items()
                if k not in ("app_id", "app_key")})
        die(f"{shown}: HTTP {exc.code} with an HTML body ({len(body)} bytes), "
            f"not JSON. A call with no credentials answers this way (400), "
            f"and so does the API under load (503) — the page is identical, "
            f"so read the status, not the body.")
    except (urllib.error.URLError, OSError) as exc:
        die(f"{shown}: {exc}")


def card(country, r):
    predicted = str(r.get("salary_is_predicted") or "") == "1"
    lo, hi = r.get("salary_min"), r.get("salary_max")
    company = (r.get("company") or {}).get("display_name")
    loc = r.get("location") or {}
    return {
        "id": str(r.get("id")),
        "ledger_id": f"adzuna:{country}:{r.get('id')}",
        # The terms require sending people to the advertiser through this URL;
        # it is the ad's canonical link here, not a courtesy.
        "url": r.get("redirect_url"),
        "country": country,
        "title": r.get("title"),
        "company": company,
        "location_text": loc.get("display_name"),
        # 4 to 6 levels: country, region, county, town, district.
        "location_area": loc.get("area"),
        "latitude": r.get("latitude"),
        "longitude": r.get("longitude"),
        # **Present, plausible, and empty on most rows.** Adzuna classifies
        # under a third of its Swiss index: expect `Unknown` / `unknown` on
        # roughly seven Swiss rows in ten (measured 2026-09-02). Read it as
        # "Adzuna happened to classify this one", never as a trade.
        "category": (r.get("category") or {}).get("label"),
        "category_tag": (r.get("category") or {}).get("tag"),
        "contract_type": r.get("contract_type"),
        "contract_time": r.get("contract_time"),
        "posted": (r.get("created") or "")[:10] or None,
        # **The advertiser's figure, or nothing.**
        "salary_min_stated": None if predicted else lo,
        "salary_max_stated": None if predicted else hi,
        # **Named for where it comes from.** The API publishes no currency;
        # this is the currency of the index that was queried, and the field
        # says so rather than passing for something the board declared.
        "salary_currency_of_the_index": INDEX_CURRENCY.get(country),
        # **Adzuna's Jobsworth estimate.** Never merge these two.
        "salary_min_adzuna_estimate": lo if predicted else None,
        "salary_max_adzuna_estimate": hi if predicted else None,
        # Hard-truncated at 500 by the API, on every ad measured.
        "description_teaser": r.get("description"),
        "description_chars": len(r.get("description") or ""),
        "teaser_truncated": len(r.get("description") or "") >= 500,
        # Feeds the `ad` command; it is a liveness check, not a fuller record.
        "adref": r.get("adref"),
    }


def cmd_count(a):
    app_id, app_key = credentials()
    b = Budget(a.max_calls)
    q = {"results_per_page": 1}
    if a.what:
        q["what"] = a.what
    if a.where:
        q["where"] = a.where
    if a.max_days_old:
        q["max_days_old"] = a.max_days_old
    if a.salary_min:
        q["salary_min"] = a.salary_min
    d = get(b, f"/jobs/{a.country}/search/1", app_id, app_key, **q)
    print(json.dumps({
        "country": a.country,
        "query": {"what": a.what, "where": a.where,
                  "max_days_old": a.max_days_old, "salary_min": a.salary_min},
        "matches": d.get("count"),
        "mean_salary": d.get("mean"),
    }, ensure_ascii=False))
    note(f"{b.spent} call(s) of the 250/day allowance.")


def cmd_search(a):
    app_id, app_key = credentials()
    b = Budget(a.max_calls)
    q = {"results_per_page": MAX_PER_PAGE}
    if a.what:
        q["what"] = a.what
    if a.where:
        q["where"] = a.where
    if a.distance:
        q["distance"] = a.distance
    if a.max_days_old:
        q["max_days_old"] = a.max_days_old
    if a.salary_min:
        q["salary_min"] = a.salary_min
    if a.category:
        q["category"] = a.category
        # **A filter that discards most of the market, silently.** Measured
        # 2026-09-02: 70.7% of the Swiss index is `category=unknown`
        # (57 663 of 81 516), 67.9% of the German and 49.5% of the French.
        # So `--category it-jobs` on `ch` returns 1 150 ads where
        # `--what Entwickler` alone returns 12 691 — nine tenths of the
        # development market gone, with a 200 and a plausible count. This is
        # the same silence as a zero (issue #70) and it never trips the
        # zero check, because 1 150 is not zero.
        note(f"--category {a.category} filters on Adzuna's own classification, "
             f"and that classification is mostly empty: 70.7% of the Swiss "
             f"index, 67.9% of the German and 49.5% of the French are "
             f"`unknown` (measured 2026-09-02). On `ch`, `it-jobs` returns "
             f"1 150 ads against 12 691 for the keyword `Entwickler` alone. "
             f"**Use it to narrow a keyword search, not to sweep a market** — "
             f"the count it gives you is a count of what Adzuna classified, "
             f"not of what exists.")
    kept, total, predicted, stated = 0, None, 0, 0
    for page in range(1, a.pages + 1):
        d = get(b, f"/jobs/{a.country}/search/{page}", app_id, app_key, **q)
        rows = d.get("results") or []
        if total is None:
            total = d.get("count")
        if len(rows) < MAX_PER_PAGE and page == 1 and len(rows) < (total or 0):
            note(f"asked for {MAX_PER_PAGE} rows and got {len(rows)} — the "
                 f"API caps a page at {MAX_PER_PAGE} whatever you ask for.")
        if not rows:
            note(f"page {page} returned no results — stopping.")
            break
        for r in rows:
            c = card(a.country, r)
            if c["salary_min_adzuna_estimate"]:
                predicted += 1
            if c["salary_min_stated"]:
                stated += 1
            print(json.dumps(c, ensure_ascii=False))
            kept += 1
            if a.limit and kept >= a.limit:
                break
        if a.limit and kept >= a.limit:
            break
        time.sleep(a.delay)
    if kept == 0:
        note(zero_note("adzuna", what=a.what, where=a.where,
                       market=a.country, speaks=speaks_of(a)))
    note(f"{kept} ads returned of {total} matching, in {b.spent} call(s) of "
         f"the 250/day allowance.")
    note(f"salary: {stated} stated by the advertiser, {predicted} estimated by "
         f"Adzuna. The estimates are in their own fields and must never be "
         f"scored as pay.")
    note("descriptions are 500-character teasers; the full text is at "
         "`url` (redirect_url), which is also where the terms require the "
         "user to be sent.")


def cmd_ad(a):
    """Re-read one ad by its adref — a liveness check, nothing more.

    The endpoint is not in Adzuna's OpenAPI, but it answers: 2 of 3 tried
    returned the same record with the same 500-character description, and the
    third returned **HTTP 503 with an HTML page**. It confirms an ad is still
    current; it does not buy more text.
    """
    app_id, app_key = credentials()
    b = Budget(a.max_calls)
    d = get(b, f"/jobs/{a.country}/ad/{urllib.parse.quote(a.adref, safe='')}",
            app_id, app_key)
    print(json.dumps(card(a.country, d), ensure_ascii=False))
    note("this endpoint is undocumented and was flaky under test — a 503 with "
         "an HTML body is one of its answers. Treat a failure as 'unknown', "
         "never as 'the ad is gone'.")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, h in (("count", cmd_count, "how many match"),
                        ("search", cmd_search, "read the ads"),
                        ("ad", cmd_ad, "re-read one ad by adref")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--country", required=True, choices=COUNTRIES)
        c.add_argument("--max-calls", type=int, default=10,
                       dest="max_calls",
                       help="hard stop for this run. The allowance is 250 a "
                            "day for every search together")
        if name == "ad":
            c.add_argument("--adref", required=True)
        else:
            c.add_argument("--what", help="keywords")
            c.add_argument("--speaks", help="the languages you work in, "
                                            "comma-separated (`fr,en`). Used "
                                            "only when a search returns zero, "
                                            "to say which of the market's "
                                            "languages you could search in "
                                            "and what the others return")
            c.add_argument("--where", help="place name; an unknown one is an "
                                           "honest count of 0")
            c.add_argument("--max-days-old", type=int, dest="max_days_old")
            c.add_argument("--salary-min", type=int, dest="salary_min")
        if name == "search":
            c.add_argument("--distance", type=int,
                           help="km around --where; the API defaults to 5")
            c.add_argument("--category", help="a tag from the categories "
                                              "endpoint, e.g. it-jobs")
            c.add_argument("--pages", type=int, default=1,
                           help="pages of 50. Default 1 — the budget is small")
            c.add_argument("--limit", type=int)
            c.add_argument("--delay", type=float, default=2.5,
                           help="seconds between calls; the minute limit is 25")
        c.set_defaults(func=fn)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
