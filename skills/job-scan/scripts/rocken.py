#!/usr/bin/env python3
"""ROCKEN (`rocken.jobs`) — Switzerland's largest inventory we have met, and the
cheapest to reach: plain HTTP, no key, no cookie, no browser.

    rocken.py list [--pages N] [--limit N] [--fetch] [--since YYYY-MM-DD]
    rocken.py ad --url https://rocken.jobs/jobs/<category>/<id>_<slug>-<DDMMYY>/

THE BOARD DECLARES ITS OWN TOTAL, AND THIS ADAPTER PRINTS IT BESIDE OURS

    <title>Stellensuche Schweiz - 5802 offene Stellen auf Rocken.jobs</title>

**That number does not come from our extraction**, so a broken reader shows the
board's figure against zero rather than a quiet zero — the distinction issue
#181 exists for, and only about a fifth of this repository's adapters can make
it.

THE POSTER IS NOT THE EMPLOYER, AND THE FIELD SAYS SO

`hiringOrganization.name` is **`ROCKEN` on every advertisement** — the
intermediary naming itself where the employer belongs; the texts say *«&nbsp;unser
Rocken Partner&nbsp;»*. **So this adapter emits `poster`, never `employer`.**

*Blanking the field by rule would be wrong in the other direction: on
`jobeo.ch`, a staffing-agency board of the same kind, the same field carries the
real employer on the advertisements read.* **What is true on both is that the
field is the POSTER** — a description of what it IS rather than of what one
deduces from it.

THE PAGINATION DRIFTS, AND THE OVERLAP IS NOT A BOARD PROPERTY

Measured 2026-09-08: pages 1 and 2 shared **one** advertisement — the last of
the first and the first of the second — while the title anchor moved from 5 802
to 5 803 between the two fetches. *One insertion at the top shifts one
advertisement across the boundary.* **A card recorded zero overlap the day
before and was right then; both readings are of a board that moves.**

So this adapter deduplicates on the identifier and prints `rows_read` beside
`found`. **A sum that matches its own source is not a check.**

WHAT IS NOT ESTABLISHED, AND IS NOT ASSUMED HERE

- **`de.rocken.jobs` has never been fetched.** Its rules permit; nothing else is
  known, and this adapter does not touch it.
- **The `DDMMYY` suffix of the slug** matched `datePosted` on one advertisement.
  *One is not a rule*, so the date is read from the advertisement and never
  from the slug.
- **Ten per page** is observed on the pages this adapter reads and printed, not
  assumed.
"""

import argparse
import datetime
import html as html_mod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BASE = "https://rocken.jobs"
LIST = BASE + "/jobs/"
PAGE = BASE + "/jobs/page/%d/"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL, EXIT_REFUSED, EXIT_UNKNOWN = 2, 3, 6, 7, 8

# `/jobs/<category>/<id>_<slug>-<DDMMYY>/` — the id is the stable part and the
# only one this adapter keys on.
AD = re.compile(
    r'href="https://rocken\.jobs/jobs/([a-z0-9-]+)/([a-z0-9]+)_([^"/]+)/"')
# **The board's own count, in its own title.** Read it before anything else: it
# is the only figure in this module that our extraction cannot break.
ANCHOR = re.compile(r"(\d[\d\s ]*)\s*offene\s+Stellen")
LASTPAGE = re.compile(r"/jobs/page/(\d+)/")

_PACE = Pace("rocken.jobs", own=1.0)
_ANNOUNCED = False


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[rocken] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)


def get(url):
    global _ANNOUNCED
    gate(url)
    if not _ANNOUNCED:
        _ANNOUNCED = True
        note(_PACE.source())
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "de-CH,de;q=0.9,fr;q=0.8,en;q=0.7",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def anchor_of(page):
    """The board's declared total, or None. **Never guessed.**"""
    m = ANCHOR.search(page)
    if not m:
        return None
    digits = re.sub(r"[^\d]", "", m.group(1))
    return int(digits) if digits else None


def posting(page):
    """The `JobPosting` block, or None. `jobLocation` is a LIST here."""
    for m in re.finditer(r"<script[^>]*ld\+json[^>]*>(.*?)</script>", page,
                         re.S):
        try:
            doc = json.loads(m.group(1))
        except Exception:  # noqa: BLE001 - a malformed block is not an error
            continue
        for o in (doc if isinstance(doc, list) else [doc]):
            if isinstance(o, dict) and o.get("@type") == "JobPosting":
                return o
    return None


def place(job):
    """`jobLocation` arrives as a LIST — reading it as a dict returns None for
    every field, which looks exactly like a board that publishes no location."""
    loc = job.get("jobLocation")
    if isinstance(loc, list):
        loc = loc[0] if loc else None
    if not isinstance(loc, dict):
        return {}
    return loc.get("address") or {}


def text(s):
    if not s:
        return None
    s = html_mod.unescape(re.sub(r"<[^>]+>", " ", str(s)))
    return re.sub(r"\s+", " ", s).strip() or None


def card(url, ident, category, page):
    job = posting(page)
    if not job:
        return {"id": "rocken:" + ident, "url": url, "category": category,
                "missing_fields": ["JobPosting"]}
    addr = place(job)
    row = {
        "id": "rocken:" + ident,
        "url": url,
        "title": text(job.get("title")),
        # **`poster`, not `employer` — it is `ROCKEN` on every advertisement.**
        "poster": text((job.get("hiringOrganization") or {}).get("name")),
        "category": category,
        "occupational_category": text(job.get("occupationalCategory")),
        "locality": addr.get("addressLocality"),
        "region": addr.get("addressRegion"),
        "country": addr.get("addressCountry"),
        "posted": job.get("datePosted"),
        "valid_through": job.get("validThrough"),
        "employment_type": job.get("employmentType"),
        "countries": ["CH"],
    }
    missing = [k for k in ("title", "locality", "posted") if not row[k]]
    row["missing_fields"] = missing or None
    return row


def listing(pages, limit):
    """Walk the paginated listing. Returns (rows, read, anchor, raw, dups)."""
    code, body = get(LIST)
    if code != 200:
        die(f"{LIST}: HTTP {code}")
    anchor = anchor_of(body)
    last = max((int(x) for x in LASTPAGE.findall(body)), default=1)
    if anchor is None:
        note("the title carries no `N offene Stellen` — the board's own count "
             "is the one figure our extraction cannot break, and it is absent. "
             "Counting continues; nothing corroborates it.")
    else:
        note(f"the board declares {anchor} open positions, and cites {last} "
             f"pages. This count is the site's, not ours.")

    seen, rows, raw, dups, read, n = {}, [], 0, [], 0, 1
    while n <= (pages or last):
        if n > 1:
            code, body = get(PAGE % n)
            if code != 200:
                note(f"page {n}: HTTP {code} — stopping, {read} pages read")
                break
        links = AD.findall(body)
        if not links:
            note(f"page {n} carried no advertisement link; stopping at {read} "
                 f"pages read")
            break
        # **Every advertisement is linked TWICE on its page** — measured on two
        # pages, 20 links for 10 advertisements, every one exactly twice. *A
        # repeat inside one page is a rendering artefact; a repeat ACROSS pages
        # is the board drifting under the read.* Counting them together
        # reported 20 duplicates for 20 advertisements, which is noise that
        # would hide the one real drift among it.
        on_page, per_page = [], {}
        for cat, ident, slug in links:
            if ident not in per_page:
                per_page[ident] = True
                on_page.append((cat, ident, slug))
        raw += len(on_page)
        for cat, ident, slug in on_page:
            if ident in seen:
                dups.append((ident, seen[ident], n))
                continue
            seen[ident] = n
            rows.append((f"{BASE}/jobs/{cat}/{ident}_{slug}/", ident, cat))
        read += 1
        note(f"page {n}: {len(links)} link(s) for {len(on_page)} "
             f"advertisement(s) — this board links each one twice")
        n += 1
        if limit and len(rows) >= limit:
            break
    return rows, read, anchor, raw, dups


def cmd_list(a):
    if a.since and not a.fetch:
        die("`--since` needs `--fetch`: the listing carries no date. The slug "
            "ends in `DDMMYY` and it matched `datePosted` on ONE advertisement "
            "— one is not a rule, so it is not used as a date.", EXIT_UNKNOWN)

    rows, read, anchor, raw, dups = listing(a.pages, a.limit)
    if a.limit:
        rows = rows[:a.limit]

    if dups:
        note(f"{len(dups)} duplicate id(s) dropped: {raw} rows read, "
             f"{len(rows)} distinct. **This board moves while it is read** — on "
             f"2026-09-08 one advertisement was the last of page 1 and the "
             f"first of page 2 while the declared total rose by one. Each is "
             f"named with the pages it came from:")
        for ident, first, again in dups:
            note(f"    page {first} then page {again}  {ident}")
    else:
        note(f"{raw} rows read, all distinct. **This line prints either way**, "
             f"and the two counts are taken on different sides of the set.")

    if anchor is not None:
        gap = anchor - len(rows)
        partial = bool(a.pages or a.limit)
        if partial:
            # **The comparison is only meaningful on a complete walk.** After
            # one page the difference is 5 796 and means nothing about the
            # board — presenting it beside the anchor would make a partial run
            # look like a catastrophic shortfall.
            note(f"board declares {anchor}; this run read {read} page(s) on "
                 f"purpose and holds {len(rows)}. **No comparison is made**: "
                 f"the anchor answers «how many are there», and a bounded run "
                 f"does not answer it.")
        else:
            note(f"board declares {anchor}; this run holds {len(rows)} "
                 f"distinct over {read} page(s) — {gap:+d}. *A gap of one or "
                 f"two is this board drifting under the read; a gap of ten is "
                 f"not.*")

    if not a.fetch:
        print(json.dumps({"source": "rocken", "country": "CH",
                          "board_declares": anchor, "pages_read": read,
                          "rows_read": raw, "found": len(rows),
                          "duplicates": len(dups), "fetched": False,
                          "ads": [{"id": "rocken:" + i, "url": u,
                                   "category": c} for u, i, c in rows]},
                         ensure_ascii=False, indent=1))
        return

    kept, broken, incomplete = [], [], []
    for url, ident, cat in rows:
        code, page = get(url)
        if code != 200:
            broken.append((ident, f"HTTP {code}"))
            continue
        c = card(url, ident, cat, page)
        if c.get("missing_fields"):
            incomplete.append((ident, c["missing_fields"]))
        kept.append(c)
    if a.since:
        before = len(kept)
        kept = [c for c in kept if not c.get("posted") or c["posted"] >= a.since]
        note(f"--since {a.since}: {len(kept)} of {before}; an advertisement "
             f"with no `datePosted` is kept — absent is not old.")
    if incomplete:
        note(f"{len(incomplete)} of {len(rows)} advertisements are missing at "
             f"least one field. Each is named:")
        for i, f in incomplete:
            note(f"    {i:>14}  missing {', '.join(f)}")
    else:
        note(f"every one of {len(rows)} advertisements yielded title, locality "
             f"and posting date. **Negative control**: printed either way.")
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{i} ({w})" for i, w in broken[:5]))

    print(json.dumps({"source": "rocken", "country": "CH",
                      "board_declares": anchor, "pages_read": read,
                      "rows_read": raw, "found": len(rows),
                      "duplicates": len(dups), "kept": len(kept),
                      "unreadable": len(broken), "incomplete": len(incomplete),
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken or incomplete:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = re.match(r"/jobs/([a-z0-9-]+)/([a-z0-9]+)_", parts.path)
    if not m:
        die("--url must be /jobs/<category>/<id>_<slug>-<DDMMYY>/")
    code, page = get(a.url)
    if code in (404, 410):
        die(f"{a.url} is gone (HTTP {code}). Record it as discarded.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}")
    c = card(a.url, m.group(2), m.group(1), page)
    print(json.dumps(c, ensure_ascii=False, indent=1))
    if c.get("missing_fields"):
        note(f"missing: {', '.join(c['missing_fields'])}")
        sys.exit(EXIT_PARTIAL)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    li = sub.add_parser("list")
    li.add_argument("--pages", type=int, help="default: every page the site cites")
    li.add_argument("--limit", type=int)
    li.add_argument("--fetch", action="store_true")
    li.add_argument("--since", help="YYYY-MM-DD, needs --fetch")
    li.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
