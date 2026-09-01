#!/usr/bin/env python3
"""Fetch Irish ads from JobsIreland — the state board, where half the ads
are not jobs.

**4 934 live ads** from Ireland's public employment service, run by the
Department of Social Protection. The fifth national public employment service
here after `job-room.md` (CH), `france-travail.md` (FR), `empleate.md` (ES) and
`arbeitsagentur.md` (DE), and **the first Irish adapter**.

  GET /robots.txt                                  → three lines, no Disallow
  GET /Jobsireland.API/JobsIreland/BrowseJobs      → the ads, as an HTML fragment
       ?page=1&pageSize=100&location=&keyWord=
  GET /en-US/job-Details?id=<id>                   → the ad, for a human

**No browser, no account, no key.** `robots.txt` is a `User-agent: *` with
**no `Disallow` line at all** and a sitemap — the most permissive file in this
repository. No crawler and no AI agent is named.

The parameter names are not guessed: they are read out of the page's own
`$.ajax` call, which passes `keyWord`, `location`, `page`, `pageSize`,
`CareerlevelId`, `VacancyTypeId`, `ContractTypeId`, `NaceCode` and
`RemoteOrBlendedJobType`.

HALF THIS BOARD IS NOT ORDINARY EMPLOYMENT, AND NOTHING SAYS SO. Across the
250 newest ads:

    #JOB   position-box   106   ordinary paid jobs
    #CES   scheme-box     135   Community Employment Scheme
    #WPEP  yess-box         9   Work Placement Experience Programme

**And the mix moves with the page.** The board is sorted newest first, and
across `pageSize=100` pages the ordinary-job share ran 58, 33, 33, 48, 0 and 0
percent on pages 1, 2, 5, 20, 45 and 49 — page 45 was 99 scheme rows out of
100. So a shallow sweep over-samples real jobs and a deep one under-samples
them. Neither number is the board.

**CES is a state work-placement scheme** — part-time supervised placement for
long-term unemployed people, paid on a social-welfare rate, entered through an
Intreo office rather than by applying to an employer. It is a majority of the
board, and a candidate searching for a job needs to be told which of the three
they are looking at. `offer_kind` carries it on every card, and every run
prints the split.

THE TRAP THAT OUTLIVES THE BOARD: **the card's CSS class changes with the ad
type, so splitting on the class you see first silently selects one
population.**

    <div class="job-heading scheme-box"    …>   135
    <div class="job-heading position-box"  …>   106
    <div class="job-heading yess-box"      …>     9
    <div class="job-heading #boxclass"     …>     1

Split on `job-heading scheme-box` — the first variant that appears in the
response — and you get **136 of 251 cards, of which 135 are CES**. Not a
truncation you would notice: a full-looking result set, correctly parsed, from
which you would conclude that Ireland's public board is nothing but placement
schemes. The anchor here is `job-heading `, the common prefix, and the parse is
checked against the raw count of ad links in the same document.

AND SOME RESPONSES CARRY A TEMPLATE ROW. The fourth class, `#boxclass`, is an
uninterpolated template whose fields are the literal strings `#JobReference`,
`#StartDate`, `#EndDate`, `#VacancyTypeId`.

**It is intermittent** — present on pages 5, 20 and 45 of a `pageSize=100`
sweep and absent from pages 1, 2 and 49, so a page returns 100 cards or 101.
Emitted unfiltered it becomes an ad published on `#StartDate`, and a
spot-check of the first page would never see it. Same species as the
`#{company.slug}` template another session measured on trampos.co — a
placeholder that reached production and reads as data — with the intermittence
of the `Content-Encoding` flap on `infoempleo.md`.

Every field starting with `#` is refused, so the row is dropped whether or not
its class gives it away.

Usage:
  jobsireland.py count --location Dublin
  jobsireland.py search --location Dublin --limit 40
  jobsireland.py search --keyword developer --kind job

Output: one JSON object per line.
"""

import argparse
import collections
import html as html_mod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://jobsireland.ie"
API = BASE + "/Jobsireland.API/JobsIreland/BrowseJobs"
AD_URL = BASE + "/en-US/job-Details?id={}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# The common prefix of all four card classes. Anchoring on any one variant
# selects one ad type — see the module docstring.
CARD_SPLIT_RE = re.compile(r'(?=<div class="job-heading )')
CARD_CLASS_RE = re.compile(r'<div class="job-heading ([^"]*)"')
LINK_RE = re.compile(r"job-Details\?id=(\d+)", re.I)
TOTAL_RE = re.compile(r'class="totalCount"[^>]*value="?(\d+)')
EMPLOYER_RE = re.compile(r'alt="Logo of ([^"]*)"')
# Irish postcode: one letter, two digits, space, four alphanumerics.
EIRCODE_RE = re.compile(r"\b([A-Z]\d{2}\s?[A-Z0-9]{4})\b")
COUNTY_RE = re.compile(r"Co\.\s*([A-Za-zÁ-ÿ' ]+)")

# `VacancyTypeId` → what the ad actually is. Read off the reference prefix as
# well, which agrees on every card measured.
KINDS = {
    "0": ("job", "an ordinary paid vacancy"),
    "3": ("ces", "Community Employment Scheme — a state work-placement for "
                 "long-term unemployed people, entered through an Intreo "
                 "office, paid on a social-welfare rate"),
    "10": ("wpep", "Work Placement Experience Programme — a state placement, "
                   "not an employment contract"),
}

WS_RE = re.compile(r"\s+")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobsireland] {msg}", file=sys.stderr)


def get(url, retries=2):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-IE,en;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as exc:
            if attempt == retries:
                die(f"{url}: {exc}")
            time.sleep(2.0 * (attempt + 1))
    return ""


def field(block, name):
    m = re.search(r'id="%s"\s+value="([^"]*)"' % name, block)
    if not m:
        return None
    v = html_mod.unescape(m.group(1)).strip()
    # The template row's fields are the literal placeholders — `#StartDate`,
    # `#JobReference`. Never let one through as a value.
    return None if v.startswith("#") else (v or None)


def is_template(block):
    """True for the uninterpolated template row. Intermittent — see above."""
    cls = CARD_CLASS_RE.search(block)
    if cls and cls.group(1).startswith("#"):
        return True
    return field(block, "JobId") is None


def parse(page):
    """Every card, checked against the ad links in the same document.

    Zero cards, or fewer cards than there are ad links, means the splitter is
    wrong rather than the board empty — the invariant from issue #55, applied
    to HTML instead of a sitemap.
    """
    links = set(LINK_RE.findall(page))
    blocks = [b for b in CARD_SPLIT_RE.split(page) if 'id="JobId"' in b]
    real = [b for b in blocks if not is_template(b)]
    if links and len(real) < len(links):
        die(f"parsed {len(real)} cards but the same document carries "
            f"{len(links)} ad links. The splitter is wrong, not the board "
            "empty — the card class varies with the ad type "
            "(scheme-box / position-box / yess-box), so anchoring on one "
            "variant silently keeps a single population.")
    if links and not real:
        die(f"parsed no cards from {len(page)} characters that contain "
            f"{len(links)} ad links. A reading fault, not an empty board.")
    return real, len(blocks) - len(real)


def total_of(page):
    m = TOTAL_RE.search(page)
    return int(m.group(1)) if m else None


def card(block):
    ident = field(block, "JobId")
    loc = field(block, "Location")
    ref = field(block, "JobReference")
    vtype = field(block, "VacancyTypeId")
    kind, kind_note = KINDS.get(str(vtype), ("unknown", None))
    eir = EIRCODE_RE.search(loc or "")
    county = COUNTY_RE.search(loc or "")
    emp = EMPLOYER_RE.search(block)
    published = field(block, "StartDate")
    closes = field(block, "EndDate")
    return {
        "id": ident,
        "ledger_id": f"jobsireland:{ident}",
        "url": AD_URL.format(ident),
        "reference": ref,
        "title": field(block, "JobTitle"),
        # Named on 159 of 251 overall — but 89 of 106 on ordinary jobs and
        # only 61 of 135 on the CES scheme rows, so the coverage depends on
        # which population you drew.
        "company": html_mod.unescape(emp.group(1)).strip() if emp else None,
        # **What the ad actually is.** More than half this board is a state
        # placement scheme rather than a job — see the module docstring.
        "offer_kind": kind,
        "offer_kind_note": kind_note,
        "vacancy_type_id": vtype,
        "paid_position": "PAID POSITION" in block,
        "location_text": loc,
        # An Eircode on 195 of 251 — a real postcode, which `infoempleo.md`
        # and `hays-fr.md` have none of.
        "postcode": eir.group(1) if eir else None,
        "county": county.group(1).strip() if county else None,
        "published": (published or "")[:10] or None,
        # The closing date, real and per ad — 2026-09-02 to 2026-10-27 across
        # the sample, none of them already past.
        "closes": (closes or "")[:10] or None,
    }


def query(a, page, size):
    p = {"page": page, "pageSize": size}
    if a.keyword:
        p["keyWord"] = a.keyword
    if a.location:
        p["location"] = a.location
    return API + "?" + urllib.parse.urlencode(p)


def describe(a):
    bits = []
    if a.keyword:
        bits.append(f"keyword={a.keyword!r}")
    if a.location:
        bits.append(f"location={a.location!r}")
    if a.kind:
        bits.append(f"kind={a.kind}")
    return " ".join(bits) or "(the whole board)"


def cmd_count(a):
    page = get(query(a, 1, 1))
    total = total_of(page)
    if total is None:
        die("no totalCount in the response. That hidden input is how the "
            "board's size is read, so the run stops rather than reporting a "
            "number it cannot source.")
    print(json.dumps({"query": describe(a), "matches": total},
                     ensure_ascii=False))


def sweep(a):
    size = min(a.page_size, 250)
    first = get(query(a, 1, size))
    total = total_of(first)
    if total is None:
        die("no totalCount in the response — a read failure, not an empty "
            "board.")
    note(f"{total} ads match — {describe(a)}")
    rows, templates = parse(first)
    pages = 1
    want = a.limit or total
    while len(rows) < want and len(rows) < total:
        pages += 1
        got, t = parse(get(query(a, pages, size)))
        templates += t
        if not got:
            note(f"page {pages} came back with no cards, stopping at "
                 f"{len(rows)} of {total}")
            break
        rows.extend(got)
        time.sleep(a.delay)
    if templates:
        note(f"{templates} template row(s) dropped across {pages} page(s) — "
             "an uninterpolated card whose fields are the literal strings "
             "#JobReference, #StartDate and #EndDate. It appears on some "
             "pages and not others, so a page returns 100 cards or 101.")
    return rows[:want], total


def cmd_search(a):
    rows, total = sweep(a)
    kinds = collections.Counter()
    kept = 0
    for b in rows:
        c = card(b)
        kinds[c["offer_kind"]] += 1
        if a.kind and c["offer_kind"] != a.kind:
            continue
        print(json.dumps(c, ensure_ascii=False))
        kept += 1
    note(f"{kept} ads returned of {len(rows)} read, out of {total} matching")
    note("what they are: " + ", ".join(f"{k} {v}" for k, v in kinds.most_common())
         + ". `ces` is the Community Employment Scheme — a state placement "
           "entered through an Intreo office, not a job you apply to; `wpep` "
           "is the Work Placement Experience Programme. Only `job` is "
           "ordinary employment.")
    if not a.kind and kinds.get("ces", 0) > kinds.get("job", 0):
        note("more than half of what was returned is a placement scheme "
             "rather than a job. Pass --kind job to keep ordinary vacancies "
             "only.")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, h in (("count", cmd_count, "how many match"),
                        ("search", cmd_search, "read the ads")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--location", help="free text — Dublin, Cork, a county")
        c.add_argument("--keyword", help="free text in the title")
        c.add_argument("--kind", choices=("job", "ces", "wpep"),
                       help="keep one kind only. **`job` is the one that is "
                            "ordinary employment** — the other two are state "
                            "placement schemes")
        if name == "search":
            c.add_argument("--limit", type=int)
            c.add_argument("--page-size", type=int, default=100,
                           dest="page_size",
                           help="up to 250; 1000 works but the response is "
                                "4.5 MB and slow")
            c.add_argument("--delay", type=float, default=0.5)
        c.set_defaults(func=fn)
    a = p.parse_args()
    if a.cmd == "search" and not (a.location or a.keyword or a.limit or a.kind):
        die("give --location, --keyword, --kind or --limit. Without one the "
            "sweep is all 4 934 ads, and more than half of those are "
            "placement schemes rather than jobs.")
    a.func(a)


if __name__ == "__main__":
    main()
