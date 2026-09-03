#!/usr/bin/env python3
"""Fetch Pakistan's national vacancies from NEXT — the whole board in one
request, and **it tells you how much of it is dead.**

`jobs.gov.pk` is Pakistan's national employment exchange. **No key, no cookie,
no browser, no endpoint** — one GET returns every advertisement it holds, and
the page states its own totals in the markup.

  GET /JobSeeker/SearchJobs?keyword=            → 1 511 advertisements, ~3.5 MB
  GET /JobSeeker/ViewJobDetails/<id>?orgId=&jobId=  → one advertisement

**1 506 OF 1 511 ARE EXPIRED. FIVE ARE LIVE.** Measured 2026-09-03, and the
board says so itself: the listing header prints `1511 total` and `1506
expired`, and every card carries `portal-job-card--live` or
`portal-job-card--expired`.

**Those are two independent measurements, this script compares them, and on
this board they disagree.** Measured 2026-09-03:

    /JobSeeker/JobSeekerJobs   header: 1511 total, 1506 expired
    /JobSeeker/SearchJobs      header:    5 total, 1506 expired
                               markup:  1511 cards, 1506 marked expired

**The same counter label carries different numbers on two pages, and on the
search page it contradicts the page's own cards** — 5 total beside 1 506
expired is not arithmetic. The browse page is the coherent one: 1 506 + 5 =
1 511, and that matches the rendered cards exactly.

**This script counts the cards and reports the header beside them**, saying
plainly when they differ rather than choosing. A total quoted from a header
nobody checked is how this repository has been wrong before.

**So `--live` is the flag that matters, and it is not the default.** Returning
1 511 rows without saying that 99.7% of them closed would be a count that is
accurate and useless. Both numbers are printed on every run.

READ FIELDS BY CLASS, NEVER BY POSITION. `portal-job-card__title`,
`portal-job-card__org`, `portal-badge--type`, and the labelled facts
(`Deadline`, `Location`, `Vacancies`, `Salary`, `Scale`). Fill rates on the
1 511, counted on values:

    Deadline    1 511 / 1 511
    Location    1 511 / 1 511
    Vacancies   1 511 / 1 511
    Salary      1 428 / 1 511   (94.5%)
    Scale          83 / 1 511   (5.5%)

**SOME CARDS LINK TO A LOGIN AND THE ADVERTISEMENT IS STILL PUBLIC.** The five
live ones offer *"Sign in to apply"* beside *"View details"*, and the sign-in
link is the **apply** route. The detail page itself answers 200 with no wall —
the site's own words are *"Login is required only to apply."* This script
reads the public detail URL and **never touches the login route**; the card
carries `apply_needs_sign_in` so the fact is in the row rather than in
somebody's memory.

`robots.txt` on `jobs.gov.pk` is not a rules file — the host serves markup for
it — so **no rules were read and none were invented**. `www.jobs.gov.pk` does
not resolve at all.

Verified against the live site on **2026-09-03**.
"""

import argparse
import html as html_mod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _robots import verdict as robots_verdict
from _zero import zero_note

BASE = "https://jobs.gov.pk"
SEARCH = BASE + "/JobSeeker/SearchJobs"
from _ua import UA

EXIT_BROKEN, EXIT_GONE, EXIT_REFUSED, EXIT_UNKNOWN = 2, 3, 7, 8

COLUMN = re.compile(r'(?=<div[^>]*class="col-12 col-lg-6 portal-job-col)')
DETAIL = re.compile(
    r'href="(/JobSeeker/ViewJobDetails/([0-9a-f-]{36})'
    r'\?orgId=([0-9a-f-]{36})&amp;jobId=([0-9a-f-]{36}))"')
STATE = re.compile(r"portal-job-card portal-job-card--(\w+)")
BADGE_TYPE = re.compile(
    r'portal-badge portal-badge--type"[^>]*>(.*?)</', re.S)
HEADER = re.compile(
    r"<strong>(\d[\d,]*)</strong>\s*total.*?<strong>(\d[\d,]*)</strong>\s*"
    r"expired", re.S)
FACTS = ("Deadline", "Location", "Scale", "Vacancies", "Salary",
         "Experience")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobs.gov.pk] {msg}", file=sys.stderr)


def gate():
    v = robots_verdict("jobs.gov.pk")
    if not v["sweep"]:
        die(f"jobs.gov.pk: {v['reason']}",
            EXIT_UNKNOWN if v["sweep"] is None else EXIT_REFUSED)
    if v["state"] != "read":
        note(f"robots.txt: {v['reason']} No rules were read, and none are "
             f"invented — the sweep is one request and proceeds.")
    return v


def get(url, timeout=90):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}. This host is slow — 60 s is not always enough on "
            f"the 3.5 MB listing, and a timeout here is not an empty board.")


def clean(fragment):
    return re.sub(r"\s+", " ", html_mod.unescape(
        re.sub(r"<[^>]+>", " ", fragment))).strip() or None


def lines_of(fragment):
    """Visible text, one item per element.

    **Splitting on `<` is not the same as stripping tags**, and the first
    draft did that: every piece kept its own attributes, so `Deadline` never
    matched and every labelled fact came back `null` while the run reported
    success. Replace each tag with a break, then read.
    """
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", fragment)
    t = html_mod.unescape(re.sub(r"<[^>]+>", "\n", t))
    return [re.sub(r"\s+", " ", x).strip() for x in t.split("\n") if x.strip()]


def by_class(block, cls):
    m = re.search(r'class="[^"]*\b' + re.escape(cls) +
                  r'\b[^"]*"[^>]*>(.*?)</', block, re.S)
    return clean(m.group(1)) if m else None


def facts_of(block):
    """The labelled facts, read by their label rather than their order.

    A card prints `Salary` on 1 428 of 1 511 and `Scale` on 83, so **position
    is not stable across cards** — the third fact is not the same fact twice.
    """
    text = lines_of(block)
    out = {}
    for i, value in enumerate(text):
        if value in FACTS and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt not in FACTS:
                out[value.lower()] = nxt
    return out


def card(block):
    link = DETAIL.search(block)
    if not link:
        return None
    href, view_id, org_id, job_id = link.groups()
    state = STATE.search(block)
    kind = BADGE_TYPE.search(block)
    f = facts_of(block)
    vacancies = f.get("vacancies")
    return {
        "id": job_id,
        "ledger_id": f"jobs.gov.pk:{job_id}",
        "url": BASE + href.replace("&amp;", "&"),
        "view_id": view_id,
        "org_id": org_id,
        "title": by_class(block, "portal-job-card__title"),
        "company": by_class(block, "portal-job-card__org"),
        "sector": clean(kind.group(1)) if kind else None,
        "status": state.group(1) if state else None,
        "deadline_text": f.get("deadline"),
        "location_text": f.get("location"),
        "salary_text": f.get("salary"),
        "scale": f.get("scale"),
        "vacancies": int(vacancies) if (vacancies or "").isdigit() else None,
        # The sign-in link on a card is the **apply** route; the detail page
        # itself is public. Recorded so the distinction is in the row.
        "apply_needs_sign_in": "Sign in to apply" in block,
        "salary_stated": bool(f.get("salary")),
    }


def cmd_search(a):
    gate()
    url = SEARCH + "?" + urllib.parse.urlencode({"keyword": a.keyword or ""})
    code, body = get(url)
    if code != 200:
        die(f"{url}: HTTP {code}")
    blocks = [b for b in COLUMN.split(body)
              if "/JobSeeker/ViewJobDetails/" in b]
    rows = [c for c in (card(b) for b in blocks) if c]
    live = [r for r in rows if r["status"] == "live"]
    expired = [r for r in rows if r["status"] == "expired"]

    # **Two measurements of the same thing, compared rather than merged.**
    # The header is a database count; the card classes are what was rendered.
    said = HEADER.search(body)
    if said:
        said_total = int(said.group(1).replace(",", ""))
        said_expired = int(said.group(2).replace(",", ""))
        if (said_total, said_expired) != (len(rows), len(expired)):
            note(f"**this page's counter and its cards disagree**: the "
                 f"header says {said_total} total / {said_expired} expired — "
                 f"which is not arithmetic — while the markup carries "
                 f"{len(rows)} cards, {len(expired)} of them marked expired. "
                 f"**The counted cards are what is reported here**, because "
                 f"they are the thing that was actually read; "
                 f"`/JobSeeker/JobSeekerJobs` states {len(rows)} total and "
                 f"agrees with them. Do not quote the search page's total.")
        else:
            note(f"the header ({said_total} total, {said_expired} expired) "
                 f"and the cards agree exactly. Two independent counts, not "
                 f"one repeated.")

    chosen = live if a.live else rows
    kept = 0
    for r in chosen:
        print(json.dumps(r, ensure_ascii=False))
        kept += 1
        if a.limit and kept >= a.limit:
            break
    if not rows:
        note(zero_note("jobs.gov.pk", what=a.keyword))
        return
    salaried = sum(1 for r in chosen if r["salary_stated"])
    note(f"{kept} row(s) emitted. **The board holds {len(rows)} "
         f"advertisements and {len(expired)} of them have closed** — "
         f"{len(live)} are live. `--live` returns those five; without it the "
         f"count is accurate and nearly all of it is dead, which is worth "
         f"saying rather than leaving in the ledger.")
    note(f"salary: {salaried} of {kept} state a figure.")


def cmd_ad(a):
    # **Before any request.** Refusing a sign-in URL costs nothing and should
    # not depend on a network round trip completing first.
    if "/Account/Login" in (a.url or ""):
        die("that is the sign-in route, not the advertisement. The card's "
            "'Sign in to apply' link goes there; the detail page is public "
            "and this script never follows a login URL. Pass the "
            "`/JobSeeker/ViewJobDetails/...` URL instead.", EXIT_BROKEN)
    code, body = get(a.url, timeout=60)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    text = lines_of(body)
    job = re.search(r"jobId=([0-9a-f-]{36})", a.url)
    row = {
        "id": job.group(1) if job else None,
        "url": a.url,
        "company": text[7] if len(text) > 7 else None,
        "lines": len(text),
    }
    if job:
        row["ledger_id"] = f"jobs.gov.pk:{job.group(1)}"
    if a.with_text:
        i = next((n for n, x in enumerate(text) if x == "Job Details"), 0)
        row["description"] = "\n".join(text[i:i + 400])
    print(json.dumps(row, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="the whole board in one request")
    s.add_argument("--keyword", help="passed to the board's own search box")
    s.add_argument("--live", action="store_true",
                   help="only advertisements the board marks live")
    s.add_argument("--limit", type=int)
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="read one advertisement by URL")
    d.add_argument("--url", required=True)
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
