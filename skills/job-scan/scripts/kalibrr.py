#!/usr/bin/env python3
"""Fetch Indonesian and Philippine ads from Kalibrr — where an empty search
answers with somebody else's results.

Kalibrr is South-East Asia's private board, and one adapter serves **two
countries**: 1 045 Indonesian and 778 Philippine ads on 2026-09-02. Public
JSON, **no key, no cookie, no browser**. `robots.txt` is 59 bytes of
`text/plain` and closes two paths, neither of them a job.

  GET /kjs/job_board/search?country=Indonesia&limit=100&offset=0
      → 200 {"jobs":[…], "count":1045, "from_alternative":false, …}
  https://www.kalibrr.com/c/<company-code>/jobs/<id>
      → the ad, server-rendered; the slug is optional

A SEARCH THAT MATCHES NOTHING IS ANSWERED WITH A SUBSTITUTE SET, AND THE ONLY
SIGN IS ONE BOOLEAN:

    ?country=Indonesia    → count 1045, from_alternative false
    ?country=Philippines  → count  778, from_alternative false
    ?country=Singapore    → count  818, from_alternative TRUE
    ?text=zzzzqqqq        → count  818, from_alternative TRUE
    (no country at all)   → count  818, from_alternative false

Kalibrr does not operate in Singapore and has no ad matching `zzzzqqqq`. Both
return **the same 818 ads, headed by the same employer**, with a full payload
and HTTP 200. Nothing else in the response differs.

Note the last line: **the unfiltered call returns that same 818 and is smaller
than either country on its own.** The default is not "everything" — it is the
fallback set. A sweep with no country reads a curated remainder and calls it
the board.

So `--country` is required here, and **any response carrying
`from_alternative` is refused rather than scored**.

THE SALARY IS CONVERTED TO PHILIPPINE PESOS AND THE LABEL DOES NOT SAY SO.
Every salaried ad on this endpoint carries `salary_currency: "PHP"` —
including the Indonesian ones, whose amounts arrive as
`22962.742977478316`, a rupiah figure converted at some rate. The sibling
endpoint `/api/job_board/search` keeps the two fields this one drops:
`salary_currency_orig: "IDR"` and `converted_salary: true`.

Read an Indonesian `base_salary` as pesos and you are wrong by a factor of
about 250. **This adapter therefore never emits `salary_min`.** It emits
`salary_php_min`, `salary_php_max` and `salary_converted`, so nothing
downstream can mistake a converted figure for the employer's.

Everything here was verified against the live service on **2026-09-02**.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _zero import zero_note

KJS = "https://www.kalibrr.com/kjs/job_board/search"
# The older endpoint. Honest about emptiness — `?country=Singapore` is a plain
# `count: 0` — but less complete (1 011 ID and 674 PH against 1 045 and 778)
# and missing `is_hybrid`, `is_open_to_fresh_grads` and `job_sds_skills`. It
# is the place to go for `salary_currency_orig`.
API = "https://www.kalibrr.com/api/job_board/search"
AD = "https://www.kalibrr.com/c/{code}/jobs/{id}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

# The two markets the board actually serves. Anything else is answered with
# the fallback set rather than a zero.
COUNTRIES = ("Indonesia", "Philippines")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[kalibrr] {msg}", file=sys.stderr)


def get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        die(f"{url}: HTTP {exc.code}")
    except (urllib.error.URLError, OSError) as exc:
        die(f"{url}: {exc}")


def search_url(a, offset, base=KJS):
    q = {"limit": a.page_size, "offset": offset, "country": a.country}
    if getattr(a, "keyword", None):
        q["text"] = a.keyword
    return f"{base}?{urllib.parse.urlencode(q)}"


def guard(d, where):
    """`from_alternative` means the answer is not to the question asked."""
    if d.get("from_alternative"):
        die(f"{where}: the board answered `from_alternative: true` — it found "
            f"nothing for this search and substituted {d.get('count')} "
            f"unrelated ads. That is what `country=Singapore` and a nonsense "
            f"keyword both return. Nothing here is scored. Check the country "
            f"spelling ({' or '.join(COUNTRIES)}) and the keyword.", 3)
    if d.get("from_correction") or d.get("correction_text_search"):
        note(f"{where}: the board corrected the search text to "
             f"{d.get('correction_text_search')!r}. The results answer the "
             f"corrected term, not yours.")


def card(j):
    loc = ((j.get("google_location") or {}).get("address_components") or {})
    company = j.get("company") or {}
    code = company.get("code")
    ident = j.get("id")
    sal_min, sal_max = j.get("base_salary"), j.get("maximum_salary")
    return {
        "id": str(ident),
        "ledger_id": f"kalibrr:{ident}",
        # Rebuilt from the company code and the id; the slug is decorative and
        # `/c/<code>/jobs/<id>` answers 200 on its own.
        "url": AD.format(code=code, id=ident) if code else None,
        "title": j.get("name"),
        "company": company.get("name") or j.get("company_name"),
        "company_code": code,
        "company_industry": company.get("industry"),
        "city": loc.get("city"),
        "region": loc.get("region"),
        "country": loc.get("country"),
        "function": j.get("function"),
        # **Pesos, whatever the country.** See the module docstring: the
        # Indonesian amounts are converted and this endpoint drops the
        # original currency. Never rename these to `salary_min`.
        "salary_php_min": sal_min,
        "salary_php_max": sal_max,
        "salary_interval": j.get("salary_interval"),
        "salary_converted": bool(sal_min) and loc.get("country") != "Philippines",
        # A boolean that is true on 88% of ads while 19% carry a figure. It is
        # not the presence of a salary and must never be read as one.
        "salary_shown_flag": j.get("salary_shown"),
        "posted": (j.get("activation_date") or "")[:10] or None,
        # A real closing date, on 1 139 of 1 139.
        "closes": (j.get("application_end_date") or "")[:10] or None,
        "work_from_home": j.get("is_work_from_home"),
        "hybrid": j.get("is_hybrid"),
        "open_to_fresh_grads": j.get("is_open_to_fresh_grads"),
        "education_level": j.get("education_level"),
        "work_experience": j.get("work_experience"),
        "tenure": j.get("tenure"),
        "openings": j.get("number_of_openings"),
        # Present on ~5%: an external ATS the ad hands off to.
        "apply_redirect_url": j.get("apply_redirect_url"),
        "description_chars": len(j.get("description") or ""),
    }


def sweep(a, want_rows=True):
    offset, seen, rows = 0, set(), []
    reported = None
    while True:
        d = get(search_url(a, offset))
        guard(d, f"{a.country} offset={offset}")
        count = d.get("count")
        if reported is None:
            reported = count
        jobs = d.get("jobs") or []
        if not jobs:
            # Past the end the board returns no rows AND drops `count` back to
            # the fallback total — 1 045 becomes 818 at offset 1 100. Neither
            # is an error; both mean stop.
            if count != reported:
                note(f"past the end: no rows, and `count` fell from "
                     f"{reported} to {count} — the fallback total. Stopping.")
            break
        for j in jobs:
            if j.get("id") in seen:
                continue
            seen.add(j["id"])
            rows.append(j)
            if a.limit and len(rows) >= a.limit:
                return rows, reported
        offset += a.page_size
        if a.pages and offset >= a.pages * a.page_size:
            break
        time.sleep(a.delay)
    return rows, reported


def cmd_count(a):
    d = get(search_url(a, 0))
    guard(d, a.country)
    print(json.dumps({
        "country": a.country,
        "keyword": a.keyword,
        "matches": d.get("count"),
        "from_alternative": d.get("from_alternative"),
    }, ensure_ascii=False))


def cmd_search(a):
    rows, reported = sweep(a)
    salaried = 0
    for j in rows:
        c = card(j)
        if c["salary_php_min"]:
            salaried += 1
        if a.with_description:
            # Kalibrr's terms permit downloading materials "solely for your
            # personal and non-commercial use" — so the text may be kept for
            # the user's own scoring. It may not be republished.
            c["description"] = j.get("description")
        print(json.dumps(c, ensure_ascii=False))
    if not rows:
        note(zero_note("kalibrr", what=a.keyword, where=a.country))
    note(f"{len(rows)} ads returned of {reported} reported for {a.country}.")
    if rows:
        pct = salaried * 100 // len(rows)
        note(f"salary figure on {salaried} of {len(rows)} ({pct}%) — and "
             f"`salary_shown` is true on about 88% of ads regardless, so the "
             f"flag is not the field. Amounts are in PHP even for Indonesia; "
             f"`salary_converted` marks those.")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, h in (("count", cmd_count, "how many match"),
                        ("search", cmd_search, "read the ads")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--country", required=True, choices=COUNTRIES,
                       help="required: without it the board returns its "
                            "fallback set of 818, which is smaller than "
                            "either country")
        c.add_argument("--keyword", help="free text; `text=`")
        c.add_argument("--page-size", type=int, default=100,
                       dest="page_size",
                       help="rows per call. 500 was accepted; 100 is polite")
        c.add_argument("--delay", type=float, default=1.0)
        if name == "search":
            c.add_argument("--limit", type=int)
            c.add_argument("--pages", type=int)
            c.add_argument("--with-description", action="store_true",
                           dest="with_description",
                           help="include the ad text in the card")
        c.set_defaults(func=fn, limit=None, pages=None,
                       with_description=False)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
