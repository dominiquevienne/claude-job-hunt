#!/usr/bin/env python3
"""GLMIS — Ghana Labour Market Information System (`www.glmis.gov.gh`).

  glmis.py list [--job-type 1] [--region 3] [--subsector 8] [--workplace 2]
  glmis.py sweep --dimension job-type        # every declared value, deduplicated
  glmis.py ad --id 5424

**Ghana's first adapter.** Its only other card, `melr-gh.md`, is the ministry
site and is not a board: its single employment route answers 404. *It names
GLMIS in prose and gives no address; `glmis.md` records how the hostname was
obtained — read, not composed.*

THERE IS NO PAGINATION, AND THAT WAS ESTABLISHED BEFORE ANY COUNT

```
markup searched for   pagination · pager · page-link · PageNumber
                      pageIndex · LoadMore · data-page · next
found                 none, on any of them
the listing is        <form method="get" id="jobFilterForm"
                            action="/Jobs/Joblistings">
```

**So there is no page 2 to ask for.** Reach comes from the form's own filters,
and **the module never composes a page number or an advertisement id** — the
ids run 2312…5424 and enumerating them would be composition of exactly the
kind that naming a host from an acronym would be.

TEN PER QUERY, AND TEN MAY BE A CAP

Measured 2026-09-07, six requests:

```
no filter        10 ids
jobTypeId=1      10 ids   1 new
jobTypeId=2       0 ids           <- a real empty facet
jobTypeId=3       1 id
jobTypeId=4       1 id    1 new
jobTypeId=5       0 ids
                 --------
union            12 distinct advertisements, ids 2312 … 5424
```

**Two of the six returned exactly ten — the same number the unfiltered view
returns — so a cap of ten per query cannot be ruled out**, and more may sit
behind those two. *No total is stated by this module, and `content:` on the
card states none either.*

**The id range is evidence that more exist than are listed**, not a count of
them: a filtered query surfaced id 2312 that the unfiltered listing does not
show.

THE FILTER VALUES ARE DECLARED, NOT GUESSED

Every value below was read from the form's own `<select>` options on
2026-09-07. **A value this module does not know is refused rather than sent**
— submitting an unknown id would be composing a facet.

NO STRUCTURED DATA, SO HTML — AND THE NEGATIVE CONTROL IS PRINTED

`ld+json` is absent from the root, the listing and the advertisement.
**`JobPosting` appears nine times on the homepage and every one is a path
segment** — `/JobPostings/JobDetails/…` — not a schema type. *A counter that
matched the word would have reported nine structured advertisements on a site
with none.*

**`--strict` prints every card the parser could not read**, one per line.
*A narrow extractor does not return less, it returns false, and its silence
has the shape of an absence* — the defect this repository reproduced twice on
2026-09-07, once on the very card that documented it.

Verified against the live site on 2026-09-07.
"""

import argparse
import html as html_mod
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path
from _ua import UA

BASE = "https://www.glmis.gov.gh"
LISTING = BASE + "/Jobs/Joblistings"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# **Read from the form's own `<select>` options, 2026-09-07.** A value absent
# from these tables is refused rather than sent: submitting an unknown id
# would be composing a facet, which is the same fault as composing a hostname.
JOB_TYPES = {"1": "Full-time", "2": "Part-time", "3": "Contract",
             "4": "Temporary", "5": "Internship", "6": "Volunteer"}
WORKPLACES = {"1": "On-Site", "2": "Remote", "3": "Hybrid"}
DIMENSIONS = {"job-type": ("jobTypeId", JOB_TYPES),
              "workplace": ("workPlaceTypeId", WORKPLACES)}
# `regionStateId` (16) and `subSectorId` (22) are declared by the same form and
# are **deliberately not swept**: each extra dimension multiplies requests on a
# host that publishes about a dozen advertisements. They are accepted as
# single filters.

CARD = re.compile(r'<div class="card[^"]*"')
AD_ID = re.compile(r"/JobPostings/JobDetails/(\d+)")
HEADING = re.compile(r"<h\d[^>]*>\s*(?:<a[^>]*>)?(.*?)(?:</a>)?\s*</h\d>", re.S)
SECTOR = re.compile(r'/sectors/([^"]+)"')


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[glmis] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    # An unknown is not a refusal: `not None` is `True` for both.
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# The host publishes no `robots.txt` — a 404, which is an absence and
# therefore knowledge — so it declares no rate. One second is ours, and it is
# declared as ours.
_PACE = Pace("www.glmis.gov.gh", own=1.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-GH,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, "", url
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def clean(s):
    """Strip tags, and **the leading `>` too.**

    `CARD.split()` cuts inside the opening tag, so each block starts with the
    remains of that tag's attributes and its closing `>`. Left in, every card
    text began with `"> "` — small, and the kind of thing that travels into a
    ledger and is read as data.
    """
    txt = " ".join(html_mod.unescape(re.sub(r"<[^>]+>", " ", s or "")).split())
    return txt.lstrip("> ").strip()


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def cards_on(page):
    """`(rows, unreadable)` — and the second half is the point.

    Every card block that carries an advertisement link is returned as a row;
    every card that carries one and could not be parsed comes back in
    `unreadable`, **as its own cleaned text**, so `--strict` can print what the
    parser did not understand rather than leave it looking like an absence.
    """
    rows, unreadable = [], []
    for block in CARD.split(page):
        m = AD_ID.search(block)
        if not m:
            continue
        ident = m.group(1)
        text = clean(block)
        head = HEADING.search(block)
        title = clean(head.group(1)) if head else None
        if not title:
            unreadable.append((ident, text[:160]))
            continue
        sector = SECTOR.search(block)
        # **Matched against the declared vocabularies, never inferred.** These
        # are the labels the form's own `<select>` publishes.
        jt = next((v for v in JOB_TYPES.values() if v.lower() in text.lower()),
                  None)
        wp = next((v for v in WORKPLACES.values()
                   if v.lower() in text.lower()), None)
        rows.append({
            "source": "glmis",
            "id": ident,
            "ledger_id": f"glmis:{ident}",
            "url": f"{BASE}/JobPostings/JobDetails/{ident}",
            "title": title,
            "subsector": (urllib.parse.unquote(sector.group(1)).strip()
                          if sector else None),
            "job_type": jt,
            "workplace": wp,
            # **The employer and the place are in this text and are not split
            # out.** The card writes them side by side with no markup between
            # them, and guessing the boundary would invent one. The whole line
            # travels, named for what it is.
            "card_text": text,
            "countries": ["GH"],
        })
    return rows, unreadable


def fetch_listing(params):
    url = LISTING + ("?" + urllib.parse.urlencode(params) if params else "")
    code, page, landed = get(url)
    if code != 200:
        die(f"{url}: HTTP {code}")
    if landed and landed.rstrip("/") != url.rstrip("/") and "?" not in landed:
        die(f"{url} redirected to {landed} — that is not the listing.",
            EXIT_BROKEN)
    return cards_on(page)


def check(dimension, value):
    field, table = DIMENSIONS[dimension]
    if value not in table:
        die(f"{value!r} is not a declared {dimension}. The form publishes "
            f"{', '.join(f'{k}={v}' for k, v in table.items())} — and a value "
            f"it does not publish is not sent.")
    return field


def cmd_list(a):
    params = {}
    for dim, val in (("job-type", a.job_type), ("workplace", a.workplace)):
        if val:
            params[check(dim, val)] = val
    if a.region:
        params["regionStateId"] = a.region
    if a.subsector:
        params["subSectorId"] = a.subsector
    if a.search:
        params["search"] = a.search
    rows, bad = fetch_listing(params)
    note(f"{len(rows)} advertisement(s). **Ten is what one query returns and "
         f"may be a cap** — the unfiltered listing returns exactly ten and so "
         f"does `jobTypeId=1`. There is no pagination on this site.")
    if bad:
        note(f"{len(bad)} card(s) carried an advertisement link and could not "
             f"be parsed" + (":" if a.strict else " — pass --strict to see them"))
        if a.strict:
            for ident, text in bad:
                print(f"  [{ident}] {text}", file=sys.stderr)
    print(json.dumps({"source": "glmis", "country": "GH",
                      "query": params or None, "returned": len(rows),
                      "unreadable": len(bad),
                      "note": "no total is derivable: the site has no "
                              "pagination and ten may be a per-query cap",
                      "ads": rows}, ensure_ascii=False, indent=1))
    if bad and not rows:
        sys.exit(EXIT_BROKEN)
    if bad:
        sys.exit(EXIT_PARTIAL)


def cmd_sweep(a):
    """Walk one declared dimension, deduplicating — never composing a value."""
    field, table = DIMENSIONS[a.dimension]
    seen, rows, per = {}, [], []
    base, first_bad = fetch_listing({})
    bad_total = len(first_bad)
    for r in base:
        seen[r["id"]] = r
    per.append(("(no filter)", len(base), len(base)))
    for value, label in sorted(table.items()):
        got, bad = fetch_listing({field: value})
        bad_total += len(bad)
        new = sum(1 for r in got if r["id"] not in seen)
        for r in got:
            seen.setdefault(r["id"], r)
        per.append((f"{label} ({value})", len(got), new))
    rows = list(seen.values())
    for label, got, new in per:
        note(f"  {label:22} {got:3} returned · {new:3} new")
    note(f"{len(rows)} distinct advertisement(s) over {len(per)} request(s). "
         f"**This is a union, not a total**: any query returning ten may be "
         f"capped, and the ids reach far beyond what is listed.")
    print(json.dumps({"source": "glmis", "country": "GH",
                      "dimension": a.dimension, "requests": len(per),
                      "distinct": len(rows), "unreadable": bad_total,
                      "per_facet": [{"facet": f, "returned": g, "new": n}
                                    for f, g, n in per],
                      "ads": rows}, ensure_ascii=False, indent=1))


def cmd_ad(a):
    url = f"{BASE}/JobPostings/JobDetails/{a.id}"
    code, page, _l = get(url)
    if code in (404, 410):
        die(f"{a.id} is gone (HTTP {code}). Record it as discarded.", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    head = HEADING.search(page)
    print(json.dumps({
        "source": "glmis", "id": str(a.id), "ledger_id": f"glmis:{a.id}",
        "url": url, "title": clean(head.group(1)) if head else None,
        "countries": ["GH"],
        # **A recruitment jurisdiction, not a workplace.** This board carries
        # overseas placements recruited from Ghana — one measured advertisement
        # hires for Dubai — and `countries` lists where recruitment happens.
        "note": "countries is the recruitment jurisdiction; this board posts "
                "overseas placements",
        "structured_data": "none — no ld+json anywhere on this site",
    }, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="one query against the listing form")
    li.add_argument("--job-type", dest="job_type",
                    help="a declared value: " + ", ".join(
                        f"{k}={v}" for k, v in JOB_TYPES.items()))
    li.add_argument("--workplace", help="a declared value: " + ", ".join(
        f"{k}={v}" for k, v in WORKPLACES.items()))
    li.add_argument("--region", help="regionStateId, declared by the form")
    li.add_argument("--subsector", help="subSectorId, declared by the form")
    li.add_argument("--search", help="the form's own free-text field")
    li.add_argument("--strict", action="store_true",
                    help="print every card the parser could not read")
    li.set_defaults(func=cmd_list)

    sw = sub.add_parser("sweep", help="every declared value of one dimension")
    sw.add_argument("--dimension", choices=sorted(DIMENSIONS), required=True)
    sw.set_defaults(func=cmd_sweep)

    ad = sub.add_parser("ad", help="one advertisement by id")
    ad.add_argument("--id", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
