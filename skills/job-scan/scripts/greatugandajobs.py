#!/usr/bin/env python3
"""Great Uganda Jobs (`www.greatugandajobs.com`) — Joomla + JS Jobs, and a counter that counts everything ever posted.

  greatugandajobs.py list [--pages N] [--live] [--limit N] [--delay S]
  greatugandajobs.py ad   --url <advertisement URL>

THE COUNTER IS A CUMULATIVE TOTAL, AND IT IS NOT THE ANCHOR

The home page says «103 391 Jobs Posted» and the listing says «Total jobs:
102 836» (2026-09-11) — two figures, both cumulative, moving by hundreds a
week, and neither the number of open advertisements. `shared/plausible-and-
false.md` recorded the first as «a historical cumulative total» on 2026-09-02
(102 924 then). **They are printed by this adapter as what they are — the
site's cumulative counters — and never beside the count as its witness.**

THE ANCHOR IS THE DEADLINE, ON EVERY CARD

Every card carries «Deadline of this Job: <weekday, Month D YYYY>» and a
«Posted:» relative date. *Live versus expired is a comparison of that deadline
with today, per card, and it is the only figure here that separates open
advertisements from the archive.* The run prints `live` and `expired` beside
`distinct`, so a zero on the live side reads as what it is.

THE LIST MOVES BETWEEN TWO REQUESTS

`/jobs/?start=N` paginates, and N counts the whole page, Gold included: a
page is 8 «Gold» cards pinned on every page — paid placement — plus 20
regular ones (9 + 18 on one fetch), and `start=28` is the second page.
**Between two requests a minute apart the regular stream had gained new ids
at its head** (`start=20` carried 107 444 while page 1, fetched first,
topped at 107 435), so consecutive pages overlap or skip by however many
were posted meanwhile.
The adapter keys on the id, prints `rows read` beside `distinct`, and promises
nothing about completeness: this is a live stream read through a window, not
an inventory.

NO STRUCTURED DATA. The advertisement page carries a `BreadcrumbList` and no
`JobPosting`; `ad` reads the page's own labelled fields — Posted, Deadline,
No of Jobs — and the description text. The rules are Joomla's defaults
(technical paths refused, the listing open), read twice, `certain: True`, no
`Crawl-delay`; the transport served 200 with a stable fingerprint on the
root twice. Measured 2026-09-11 13:27–13:40 UTC.
"""

import argparse
import datetime as dt
import html as htmlmod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA
from _zero import empty_first_page

BASE = "https://www.greatugandajobs.com"
LIST = BASE + "/jobs/"
# `?start=N` counts the WHOLE page, pinned Gold cards included: `start=28`
# served 20 regular cards disjoint from page 1's 20, `start=20` served 11 of
# them again. Measured 2026-09-11 13:31 UTC, one fetch each.
STEP = 28
CARD_SPLIT = re.compile(r'<div class="js-toprow">')
TITLE_RE = re.compile(r'<a class="jobtitle" href="([^"]*job-detail/[^"]*-(\d+))"[^>]*>(.*?)</a>', re.S)
COMPANY_RE = re.compile(r'href="/jobs/company-detail/company-[^"]*-(\d+)/[^"]*"><img[^>]*title="([^"]*)"')
FIELD_RE = re.compile(r'<span class="js-bold">([^<]+?):(?:&nbsp;?)?\s*</span>\s*(?:<span class="get-text">)?([^<]*)')
STATUS_RE = re.compile(r'<span class="js-status[^"]*">([^<]*)</span>')
TOTAL_RE = re.compile(r'Total jobs:\s*<span>([\d,]+)</span>')
POSTED_COUNTER_RE = re.compile(r'([\d,]+)\s*</[^>]+>\s*(?:<[^>]+>\s*)*Jobs Posted')
DEADLINE_RE = re.compile(r"[A-Z][a-z]+day,\s+([A-Z][a-z]+)\s+(\d{1,2})\s+(\d{4})")
MONTHS = {m: i for i, m in enumerate(
    ("January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"), 1)}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[greatugandajobs] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# No `Crawl-delay` is declared; 2 s is ours — a default, not a measured margin.
_PACE = Pace("www.greatugandajobs.com", own=2.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-UG,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", htmlmod.unescape(markup)).strip()


def deadline_iso(value):
    """«Thursday, October 8 2026» → `2026-10-08`; anything else `None`."""
    m = DEADLINE_RE.search(value or "")
    if not m or m.group(1) not in MONTHS:
        return None
    try:
        return dt.date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2))).isoformat()
    except ValueError:
        return None


def cards(body):
    """`(rows, unlinked)` — one row per card of the main list; `unlinked` grows
    where a card carries no `jobtitle` link, in its own branch."""
    i = body.find('id="js-jobs-wrapper"')
    if i < 0:
        return [], 0
    rows, unlinked, seen = [], 0, set()
    for chunk in CARD_SPLIT.split(body[i:])[1:]:
        m = TITLE_RE.search(chunk)
        if not m:
            unlinked += 1
            continue
        path, ident, title = m.group(1), m.group(2), text(m.group(3))
        if ident in seen:
            continue
        seen.add(ident)
        comp = COMPANY_RE.search(chunk)
        fields = {k.strip(): text(v) for k, v in FIELD_RE.findall(chunk)}
        statuses = [text(s) for s in STATUS_RE.findall(chunk)]
        deadline = deadline_iso(fields.get("Deadline of this Job"))
        rows.append({
            "source": "greatugandajobs", "country": "UG",
            "ledger_id": f"greatugandajobs:{ident}", "id": ident,
            "url": BASE + htmlmod.unescape(path),
            "title": title,
            "employer": comp.group(2) if comp else None,
            "employer_id": comp.group(1) if comp else None,
            "category": fields.get("Job Category"),
            "posted_text": fields.get("Posted"),
            "deadline": deadline,
            "duty_station": fields.get("Duty Station"),
            "employment_type": statuses[0] if statuses and statuses[0] not in ("New", "Gold", "Featured") else None,
            "gold": "Gold" in statuses,        # pinned on every page — paid placement
            "featured": "Featured" in statuses,
        })
    return rows, unlinked


def cmd_list(a):
    today = dt.date.today().isoformat()
    seen, rows_read, per_page, kept = {}, 0, [], 0
    stated = None
    for page in range(a.pages):
        url = LIST + (f"?start={page * STEP}" if page else "")
        code, body = get(url)
        if code == 404:
            die(f"{url}: HTTP 404 — the listing is gone", EXIT_GONE)
        if code != 200:
            die(f"{url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
        if stated is None:
            m = TOTAL_RE.search(body)
            stated = int(m.group(1).replace(",", "")) if m else None
        found, unlinked = cards(body)
        if not found and page == 0:
            die(empty_first_page("greatugandajobs", body, "card", where=url,
                                 candidates=len(CARD_SPLIT.findall(body))), EXIT_PARTIAL)
        if not found:
            note(f"page {page + 1} carried no card — the end of the stream.")
            break
        rows_read += len(found) + unlinked
        per_page.append(f"{len(found)}+{unlinked}u" if unlinked else str(len(found)))
        new = 0
        for r in found:
            if r["id"] in seen:
                continue
            seen[r["id"]] = r
            new += 1
        if new == 0:
            note(f"page {page + 1} brought nothing new — stopping.")
            break
        if page + 1 < a.pages:
            time.sleep(a.delay)
    live = [r for r in seen.values() if r["deadline"] and r["deadline"] >= today]
    expired = [r for r in seen.values() if r["deadline"] and r["deadline"] < today]
    undated = [r for r in seen.values() if not r["deadline"]]
    out = live if a.live else list(seen.values())
    for r in out[:a.limit] if a.limit else out:
        print(json.dumps(r, ensure_ascii=False))
        kept += 1
    gold = sum(1 for r in seen.values() if r["gold"])
    note(f"{kept} emitted{' (live only)' if a.live else ''} of {len(seen)} distinct; "
         f"{rows_read} rows read on {len(per_page)} page(s) ({'+'.join(per_page)}), "
         f"{rows_read - len(seen)} repeated across pages — {gold} Gold cards are "
         f"pinned on every page.")
    note(f"live {len(live)} · expired {len(expired)} · undated {len(undated)}, by the "
         f"deadline every card carries, against {today}. **That is the anchor: live "
         f"versus archive.**")
    counter = (f"site states «Total jobs: {stated:,}» on the listing".replace(",", " ")
               if stated is not None else "the listing states no total this run")
    note(counter + " — **a cumulative counter of everything ever posted, not the "
         "number open**; it is not compared with the count above. The stream "
         "moves between requests, so no completeness is claimed for the window "
         "read.")


AD_PAIR_RE = re.compile(r'<span class="js_job_data_title">([^<]*?)(?:&nbsp;?)?</span>\s*'
                        r'<span class="js_job_data_value">(.*?)</span>', re.S)


def cmd_ad(a):
    """One advertisement: the page's own labelled pairs and its visible text.

    No `JobPosting` here — the page carries a `BreadcrumbList` only. The
    labelled pairs (`js_job_data_title` / `js_job_data_value`) carry the
    dates and the count; the description is the visible text between «JOB
    DETAILS:» and «Job application procedure», which is how the page lays
    it out (measured on id 107326, 2026-09-11) — a layout, not a schema, and
    the row says so in `description_source`.
    """
    m = re.search(r"job-detail/[^/?#]*-(\d+)", a.url)
    if not m:
        die(f"{a.url}: not an advertisement address — expected …/jobs/job-detail/job-<slug>-<id>")
    ident = m.group(1)
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer.**")
    pairs = {text(k).rstrip(":"): text(v) for k, v in AD_PAIR_RE.findall(body)}
    if not pairs:
        die(f"{a.url}: 200 with {len(body)} characters and no `js_job_data_title` pair — "
            f"not an advertisement page, or the JS Jobs layout moved.", EXIT_PARTIAL)
    full = text(body)
    d0 = full.find("JOB DETAILS:")
    d1 = full.find("Job application procedure", d0) if d0 >= 0 else -1
    description = full[d0 + len("JOB DETAILS:"):d1].strip() if d0 >= 0 and d1 > d0 else None
    procedure = full[d1:d1 + 1500].strip() if d1 > 0 else None
    # No <h1> on the page: the title is the <title>, prefixed «Job - ».
    h1 = re.search(r"<title>(.*?)</title>", body, re.S)
    print(json.dumps({
        "source": "greatugandajobs", "country": "UG",
        "ledger_id": f"greatugandajobs:{ident}", "id": ident, "url": a.url,
        "title": re.sub(r"^Job - ", "", text(h1.group(1))) if h1 else None,
        "category": pairs.get("Job Category"),
        "employment_type": pairs.get("Job Type"),
        "posted": pairs.get("Posted"),                 # dd-mm-yyyy, as the site writes it
        "deadline_text": pairs.get("Deadline of this Job"),
        "deadline": deadline_iso(pairs.get("Deadline of this Job")),
        "duty_station": pairs.get("Duty Station"),
        "jobs_count": pairs.get("No of Jobs"),
        "fields": pairs,
        "description": description[:20000] if description else None,
        "application_procedure": procedure,
        "description_source": ("visible text between «JOB DETAILS:» and «Job application "
                               "procedure» — a page layout, not a schema; no JobPosting on this site"),
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Uganda's largest board — JS Jobs on Joomla, "
                                            "read through the listing's own pages.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="the listing, 20 regular + pinned Gold cards a page")
    s.add_argument("--pages", type=int, default=3)
    s.add_argument("--live", action="store_true", help="emit only cards whose deadline is today or later")
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=2.0)
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advertisement — labelled fields and text, no JSON-LD here")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
