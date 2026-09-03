#!/usr/bin/env python3
"""Read Jamaica's Labour Market Information System — the whole board in one
request, and a search that cannot fail.

`lmis.gov.jm`, run by the Ministry of Labour and Social Security. **No key, no
cookie, no browser** — the page renders client-side, and the endpoint it calls
answers a plain POST.

**The first public employment service in this series whose access is not
refused**, and the reason is worth stating precisely: its `robots.txt` is
**Drupal's shipped default**, 22 `Disallow` lines, all administrative —
`/node/add/`, `/user/`, `/search/`. **Nothing in it concerns the vacancies.**

**So the permission is accidental, and that does not make it less real.** The
symmetry with `empleate.gob.hn` is the point: there a file copied from Google's
documentation **forbids** the vacancies; here a file shipped with a CMS
**allows** them. **Neither operator wrote the rule that decides.** An
accidental permission is still a permission — and it is **not a welcome**. It
is an absence of objection, so this adapter fetches once, takes everything, and
does not come back.

  POST /api/job/listing   {"offset": 0, "limit": n}
      → 200 application/json, {"count": "16", "data": [...]}

**THE ENDPOINT ACCEPTS EVERY PARAMETER AND FILTERS ON NONE.** Measured
2026-09-03:

    {"job_title": "counsellor"}    → count 16, all 16 rows
    {"skills": "Communication"}    → count 16, all 16 rows
    {"job_title": "zzzznothing"}   → count 16, all 16 rows

`job_title` and `skills` are the site's **own** parameter names, read out of
`job-search.js`. They are accepted, echoed by nothing, and ignored. **A search
that cannot fail is not a search** — it is the `communalCodes` trap of
`job-room.md`, in its strongest form. So this file **offers no filter at all**
and narrows after the fetch, which costs nothing on a board of sixteen.

WHAT IS MEASURED, AND WHAT SIXTEEN ADS LET YOU SAY:

    ads                     16, and `count` agrees with the rows
    ads outside Jamaica      1 — a US Navy posting at Guantánamo, `CU`
    distinct employers       6
    expired but still listed 0 of 16
    location, skills filled  16 of 16
    `job_status`             "1" on 16 of 16 — constant, and a string
    `author`                 empty on 16 of 16

**`count` is a string, not a number** (`"16"`), and **`date` is relative
prose** — *"2 days 16 hours ago"* — not a date. `expiration_date` is ISO and is
the only date here that can be stored. **Zero expired of sixteen is measured
and is not a property**: sixteen is a small sample, and boards that serve
stale ads look identical until they do.

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

from _robots import allowed as robots_allowed
from _zero import zero_note

BASE = "https://lmis.gov.jm"
API = "/api/job/listing"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

EXIT_BROKEN, EXIT_GONE, EXIT_REFUSED, EXIT_UNKNOWN = 2, 3, 7, 8

# What a card may carry. The record has no contact details, so this is not the
# allow-list of `vieclam24h`/`hr.ge` — it is a choice of what a ledger uses.
KEEP = ("id", "title", "company", "location", "type", "expiration_date",
        "url", "skills")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[lmis.gov.jm] {msg}", file=sys.stderr)


def _robots_gate(path):
    """Per path, on the host about to be fetched. Issues #100, #101.

    **The permission here is a Drupal default nobody edited**, which is a
    reason to check it every run rather than to record it once: the day an
    operator writes their own file is the day a transcription would be wrong.
    """
    a = robots_allowed("lmis.gov.jm", path)
    if not a["allowed"]:
        die(f"{BASE}{path}: {a['reason']}", EXIT_REFUSED)
    return a


def fetch(offset=0, limit=100):
    _robots_gate(API)
    body = json.dumps({"offset": offset, "limit": limit}).encode()
    req = urllib.request.Request(BASE + API, data=body, headers={
        "User-Agent": UA,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Language": "en-JM,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        die(f"{BASE}{API}: HTTP {e.code}", EXIT_GONE)
    except (urllib.error.URLError, OSError, ValueError) as e:
        die(f"{BASE}{API}: {e}")


def _unescape(v):
    """`&amp;` reaches the ledger as `&amp;` unless somebody unescapes it.

    The skills list carries HTML entities — *"Career Guidance &amp;
    Counselling"* — because the field is authored in a rich-text widget. Same
    shape as job-room's markdown escaping: it looks like data and it is
    markup that survived.
    """
    if isinstance(v, str):
        return html_mod.unescape(v)
    if isinstance(v, list):
        return [_unescape(x) for x in v]
    return v


def card(row):
    out = {k: _unescape(row.get(k)) for k in KEEP}
    out["ledger_id"] = f"lmis-jm:{row.get('id')}"
    out["url"] = row.get("url") or f"{BASE}/jobs/detail/{row.get('id')}"
    # **Relative prose, kept as printed and never parsed into a date.**
    # "2 days 16 hours ago" is what the record carries; turning it into a
    # timestamp would invent a precision the board does not publish.
    out["posted_relative"] = row.get("date")
    out["description_chars"] = len(row.get("description") or "")
    return out


def cmd_search(a):
    d = fetch(0, a.limit or 200)
    rows = d.get("data") or []
    # **Two numbers that must agree**, and `count` is a string on this board.
    try:
        stated = int(str(d.get("count", "")).strip() or -1)
    except ValueError:
        stated = -1
    if not rows:
        die(zero_note("lmis-jm", extra=(
            "The endpoint answered 200 with an empty `data` list. This board "
            "is small — sixteen ads on 2026-09-03 — so an empty answer is "
            "plausible and is still not established: re-run before recording "
            "it.")))
    want = (a.keyword or "").strip().lower()
    kept = 0
    for r in rows:
        if want:
            hay = " ".join(str(r.get(k) or "") for k in
                           ("title", "company", "description", "type")).lower()
            if want not in hay:
                continue
        print(json.dumps(card(r), ensure_ascii=False))
        kept += 1
    # **Only when nothing truncated the list.** Comparing a stated total
    # against a `--limit`-capped list reports the limit as a discrepancy —
    # a false number that reads like a check, and the third time this session
    # produced one the same way.
    capped = bool(a.limit) and len(rows) >= a.limit
    if stated >= 0 and not capped and stated != len(rows):
        note(f"the endpoint states {stated} and returned {len(rows)} — **they "
             f"should agree**, and the difference is the part nobody is "
             f"reading.")
    if want:
        note(f"{kept} of {len(rows)} ad(s) match {a.keyword!r}. **The "
             f"narrowing is done here, not by the endpoint**: it accepts "
             f"`job_title` and `skills` — its own parameter names — and "
             f"ignores them, returning all {len(rows)} for a keyword that "
             f"matches nothing. A search that cannot fail is not a search.")
    else:
        note(f"{kept} ad(s)"
             + (f" — **stopped at --limit, so this is not the board's size**."
                if capped else
                f", which is the whole board in one request.")
             + f" `count` said {stated if stated >= 0 else '?'}.")


def cmd_ad(a):
    ident = a.id or (re.search(r"/jobs/detail/(\d+)", a.url or "") or
                     [None, None])[1]
    if not ident:
        die("give --id, or a --url of the form /jobs/detail/<id>.")
    # **There is no per-ad endpoint and the detail page renders client-side**
    # — 1 763 visible characters, no `JobPosting`. So one ad is found in the
    # listing, which is one request for a board of sixteen.
    rows = (fetch(0, 200).get("data") or [])
    for r in rows:
        if str(r.get("id")) == str(ident):
            out = card(r)
            if a.with_text:
                out["description"] = r.get("description")
                out["responsibilities"] = r.get("responsibilities")
                out["education"] = r.get("education")
                out["experiences"] = r.get("experiences")
            print(json.dumps(out, ensure_ascii=False))
            return
    die(f"id {ident} is not in the {len(rows)} ad(s) the board currently "
        f"lists. **On this board that means gone, not hidden**: the listing "
        f"is the whole board and there is nothing else to ask.", EXIT_GONE)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="the whole board, in one request")
    s.add_argument("--keyword", help="narrowed here, not by the endpoint")
    s.add_argument("--limit", type=int)
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="one ad, found in the listing")
    d.add_argument("--id")
    d.add_argument("--url")
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
