#!/usr/bin/env python3
"""Naydizdes (`www.naydizdes.com/en/vakansii`) — a Turkmen classifieds site whose jobs
section MIXES employer vacancies with CVs of real people, and whose FILTER is therefore a
safety condition rather than an optimisation.

Measured 2026-10-28 19:19-19:25 UTC, guard taken on each exact path in a turn distinct
from the retrieval, one declared token (`claude-user`):

    /en/rabota/    "Jobs"         396   <- the MIXED section: do NOT enumerate from here
      /en/vakansii/  "Vacancies"  345   <- employer vacancies.  THIS is the enumerator
      /en/rezyume/   "Resume - CV"  51   <- CVs of real people.  NEVER walked
                                   ---
                                   396   51 + 345, and the regional split closes too:
                                         Ashgabat 375 + Ahal 4 + Balkan 7 + Dasoguz 2
                                         + Mary 8 = 396 (and 330+3+6+1+5 = 345)

So an adapter that walked `/en/rabota/<n>/` — which this board's card named as the jobs
enumerator until today — would emit **51 CVs of real people** into a jobs registry. Page
one of that pager carries 6 of them: `ishu-podrabotku` ("I am looking for part-time
work"), `ishu-rabotu-elektrikom`, `repetitor`, `voditel-suruji` and two first-person
service offers. The 2 222 `/item/` paths of the declared sitemap are a THIRD trap, already
recorded on the card: they are the whole classifieds site (an apartment, an IP camera, a
building-materials shop among three read) and ZERO of them is one of the 100 adverts the
jobs section's page one carries.

THE FILTER IS MEASURED IN BOTH DIRECTIONS ON A REAL CORPUS, never on a composed fixture:

    /en/rabota/   page 1   100 items ->  94 Vacancies +  6 Resume - CV
    /en/vakansii/ page 1   100 items -> 100 Vacancies +  0
    /en/vakansii/ page 4    45 items ->  45 Vacancies +  0

and the 6 are exactly the 6 that a set difference between the two page ones isolates —
two independent methods, same members. The category is declared THREE times and we assert
it at every one of them, as a POSITIVE floor: a record is a vacancy because it PASSES a
test, never because it is missing from a list.

    the listing's `item_extra`   "1 hour ago | Ashgabat | Vacancies | Building"
    the advert's JSON-LD         BreadcrumbList, last item `/en/<city>/vakansii/`
    the advert's labelled field  "Category: Jobs, Vacancies"

WHAT THE HOST SERVES, AND WHAT IT DOES NOT. There is NO `JobPosting` anywhere — the only
JSON-LD is a `BreadcrumbList` — so everything is read off the DOM. The advert page carries
`Field of activity`, `Listed by`, `Category`, `Location`, `Contact`, `Phone`, `Email`,
`Posted on`, `Views`, and NO salary field: a pay figure, when there is one, is prose
inside the description.

CONTACTS ARE GATED BY THE HOST ITSELF, and this is the cleanest case this repository has
met. Measured on the whole advert body, scripts included: **0 `mailto:`, 0 e-mail in
clear**, and the only phone-shaped string is the host's own mask `+9936XXXXX`. The real
values sit behind `data-target="<token>" data-toggle="cb_unproc"` — present, obfuscated,
three of them on the advert read. **We never decode them and we never carry the token**:
decoding would be the very act the rule exists to forbid, and their role is established by
their POSITION in the `Phone:` and `Email:` slots, not by decoding. The 8- and 9-digit runs
elsewhere in the body are image-asset filename hashes under `/user-content/uploads/cache/`,
and `imo` is the site's own channel (`call.imo.im/naydizdes`), not an advertiser's.

TWO THINGS THE SORTED LISTING CANNOT TELL YOU. Page one shows July and August bulletins in
October, so its order is not freshness; and the date is RELATIVE only — "1 hour ago",
"yesterday", "2 days ago" — with no `datetime`, no `datePosted` and no `article:published`
anywhere on the page. So `posted_relative` is carried AS READ and no absolute date is
fabricated from it.

AN ADVERT IS AN AGENCY BULLETIN. `Listed by: Agency`, and one advertiser (`infosta`) holds
152 of the 345. On the ONE advert read in full the 15 `•` bullets are the DUTIES of a
single numbered post (№2746) and not several openings, so `bullets` is carried as a shape
of the text and nothing is inferred from it about a number of posts — n=1, dated, not a
property of the board.

AND `Location` IS THE ADVERTISER'S, NOT RELIABLY THE WORKPLACE: that same advert reads
`Location: Ashgabat` in its field while its description says `Локация: Балканский велаят`.
Observed once, 2026-10-28, so it is dated and not a rate — but `place` is emitted as the
FIELD it comes from and never as the job's location.

`robots.txt` refuses seven motifs of FORM under `*` and declares `Crawl-delay: 5` on a line
outside any `User-agent` group; the conservative reading applies it, which is what the
guard module does. A census of the 100 advert paths of page one returns **0 refused on
100** — no known loss — and the filter is still evaluated per URL rather than taken as
acquired.

Issue #671.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import html as htmlmod
import json
import re
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "www.naydizdes.com"
BASE = "https://www.naydizdes.com"
SECTION = BASE + "/en/vakansii/"
PAGE = BASE + "/en/vakansii/{page}/"

# The MIXED parent and the CV child. Neither is ever enumerated, and a URL that names
# one is refused rather than filtered: see the module docstring.
MIXED_SEGMENT = "/rabota/"
CANDIDATE_SEGMENTS = ("/rezyume/", "/rezume/", "/resume/", "/soiskatel")
VACANCY_SEGMENT = "/vakansii/"
VACANCY_LABEL = "Vacancies"
CANDIDATE_LABEL = "Resume - CV"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# Same country as `isgar.py`, whose expressions these are: a Turkmen number is 8 digits,
# a monthly wage in manat is four, so the 8-digit floor cannot eat a salary here.
MAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TEL_RE = re.compile(r"(?:\+\s?993[\s\-()]*)?(?<!\d)\d{8}(?!\d)|\+\s?993[\s\-()\d]{4,}")
MSG_RE = re.compile(r"(?i)\b(?:whats?app|telegram|viber|imo)\b[\s:：]*[+\d][\d\s\-()]{5,}")

# `<li class="item ..." data-item="251279">` ... `item_title` ... `item_extra`
ITEM_RE = re.compile(
    r'<li class="item[^"]*" data-item="(\d+)">.*?'
    r'href="https://www\.naydizdes\.com(/en/item/[^"]+)".*?'
    r'class="item_title[^"]*">(.*?)</span>.*?'
    r'class="item_description[^"]*">(.*?)</span>.*?'
    r'class="item_extra">([^<]*)</small>', re.S)
# `<h1>Vacancies <sup class="item_count">345</sup>` — the host's own count, NOT ours
COUNT_RE = re.compile(r'<h1>([^<]*)<sup class="item_count">\s*([\d   ]+)')
PAGER_RE = re.compile(r'href="https://www\.naydizdes\.com/en/vakansii/(\d+)/?"')
FIELD_RE = re.compile(
    r'cf_label[^>]*>\s*([^<]{2,30}?)\s*:?\s*</span>\s*<span class="cf_value[^>]*>(.*?)</span>', re.S)
LD_RE = re.compile(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
GATED_RE = re.compile(r'data-toggle="cb_unproc"')
BODY_RE = re.compile(
    r'<p class="description(?: [^"]*)?"[^>]*>(.*?)</p>', re.S)
# The class LIST varies with the length of the text — `description limit_content_height`
# on one advert read, bare `description` on the next — so only the FIRST token is
# anchored, which is also what keeps `item_description` (TEN of them: the sidebar's
# neighbouring adverts) and `site_description` out. Both forms EXTRACTED from served
# bodies, each asserted to one match; the two-token form was a motif tried on one
# specimen and it returned nothing on the second.


def die(msg, code=EXIT_BROKEN):
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def note(msg):
    print(msg, file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# The host declares `Crawl-delay: 5` on a line outside any group; the conservative
# reading applies it, so our own floor matches it rather than undercutting it.
_PACE = Pace(HOST, own=5.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xml;q=0.9",
        "Accept-Language": "en,tk;q=0.8,ru;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def refuse_candidate(url):
    """A URL naming the CV child, or the mixed parent, is REFUSED and not filtered."""
    low = url.lower()
    for seg in CANDIDATE_SEGMENTS:
        if seg in low:
            die(f"{url}: a candidate CV path. **The rules permit it and this adapter does "
                f"not take it**: `/en/rezyume/` holds {CANDIDATE_LABEL} adverts — 51 of them, "
                "written by real people offering themselves — and the filter on "
                f"{VACANCY_SEGMENT} is a safety condition, not an optimisation.", EXIT_REFUSED)
    if MIXED_SEGMENT in low:
        die(f"{url}: `/en/rabota/` is the MIXED parent section (396 = 345 vacancies + 51 CVs) "
            f"and enumerating it emits CVs of real people. Walk {SECTION} instead.", EXIT_REFUSED)


def text(s):
    return re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<[^>]*>", " ", s or ""))).strip()


def scrub(s):
    if not s:
        return None
    s = MSG_RE.sub("[contact withheld]", s)
    s = MAIL_RE.sub("[email withheld]", s)
    s = TEL_RE.sub("[telephone withheld]", s)
    return s.strip() or None


def section_count(body):
    """The count the HOST prints in its own `<h1>`, with the heading that labels it."""
    m = COUNT_RE.search(body)
    if not m:
        return None, None
    digits = re.sub(r"[^\d]", "", m.group(2))
    return text(m.group(1)), (int(digits) if digits else None)


def extra(raw):
    """`1 hour ago | Ashgabat | Vacancies | Building` -> the four fields, as read."""
    parts = [p.strip() for p in text(raw).split("|")]
    while len(parts) < 4:
        parts.append(None)
    return parts[0] or None, parts[1] or None, parts[2] or None, parts[3] or None


def listing(body, where):
    """Every advert of one listing page, each asserted to DECLARE itself a vacancy."""
    rows, rejected = [], []
    for ident, path, title, desc, xtra in ITEM_RE.findall(body):
        when, place, category, field = extra(xtra)
        if category != VACANCY_LABEL:
            rejected.append((path, category))
            continue
        rows.append({
            "source": "naydizdes", "country": "TM",
            "ledger_id": f"naydizdes:{ident}", "id": ident,
            "url": BASE + path,
            "title": text(title) or None,
            "teaser": scrub(text(desc)) or None,
            "place": place, "category": category, "field_of_activity": field,
            # RELATIVE only: the host serves no absolute date anywhere on the page,
            # so none is derived. See the module docstring.
            "posted_relative": when, "posted": None,
        })
    if rejected:
        note(f"{where}: {len(rejected)} advert(s) did not declare themselves "
             f"`{VACANCY_LABEL}` and were DROPPED — {sorted({c for _, c in rejected})}. "
             "**On this enumerator that count is 0 when measured; a non-zero one means the "
             "section filter has drifted and the walk is emitting more than vacancies.**")
    return rows, rejected


def breadcrumb(body):
    """The advert's own declared category, from its only JSON-LD block."""
    for blob in LD_RE.findall(body):
        try:
            d = json.loads(blob)
        except ValueError:
            continue
        if d.get("@type") != "BreadcrumbList":
            continue
        items = d.get("itemListElement") or []
        if not items:
            continue
        last = items[-1]
        return last.get("name"), (last.get("item") or "")
    return None, ""


def advert(url):
    """One advert page, with the POSITIVE floor asserted at both of its declarations."""
    refuse_candidate(url)
    code, body = get(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the advert is gone.", EXIT_GONE)
    if code != 200 or not body:
        die(f"{url}: HTTP {code}, {len(body)} byte(s).", EXIT_PARTIAL)
    name, item = breadcrumb(body)
    fields = {text(k): text(v) for k, v in FIELD_RE.findall(body)}
    declared = fields.get("Category") or ""
    # Two declarations, both asserted. Neither is trusted on its own.
    if name != VACANCY_LABEL or VACANCY_SEGMENT not in item:
        die(f"{url}: its breadcrumb declares {name!r} at {item!r}, not {VACANCY_LABEL!r} under "
            f"{VACANCY_SEGMENT}. **Not emitted**: on this board that is how a CV announces "
            "itself, and the floor is POSITIVE — a record is a vacancy because it passes a "
            "test, never because it is missing from a list.", EXIT_REFUSED)
    if VACANCY_LABEL not in declared:
        die(f"{url}: its `Category` field reads {declared!r}, which does not name "
            f"{VACANCY_LABEL!r}, while its breadcrumb does. **Two declarations that disagree "
            "are not a vacancy established**, so nothing is emitted.", EXIT_REFUSED)
    m = re.search(r'-(\d+)\.html', url)
    ident = m.group(1) if m else None
    bodies = BODY_RE.findall(body)
    full = scrub(text(bodies[0])) if bodies else None
    gated = len(GATED_RE.findall(body))
    out = {
        "source": "naydizdes", "country": "TM",
        "ledger_id": f"naydizdes:{ident}" if ident else None, "id": ident,
        "url": url,
        "title": text(re.search(r"<h1>(.*?)</h1>", body, re.S).group(1)) if "<h1>" in body else None,
        "category": declared or name,
        "field_of_activity": fields.get("Field of activity"),
        "listed_by": fields.get("Listed by"),
        "place": fields.get("Location"),
        "advertiser": fields.get("Contact"),
        "views": fields.get("Views"),
        "posted_relative": fields.get("Posted on"), "posted": None,
        "description": full,
        # a fact about the HOST, deciding nothing here
        "host_gates_contacts": bool(gated),
    }
    # Bullets, because an advert here is an agency BULLETIN and may carry several openings.
    if full:
        out["bullets"] = full.count("•")
    # DERIVED from what was actually present, and ABSENT when nothing was: we drop the
    # obfuscated `cb_unproc` tokens, which ARE the contact, and we never decode them.
    if gated:
        out["withheld_fields"] = ["email", "phone"]
    return out


def th(n):
    return f"{n:,}".replace(",", " ")


def cmd_list(a):
    rows, rejected, pages, n = [], 0, 0, 1
    heading = declared = None
    seen, end = set(), "walked to the last page the pager names"
    last = None
    while True:
        url = SECTION if n == 1 else PAGE.format(page=n)
        code, body = get(url)
        if code != 200 or not body:
            if n == 1:
                die(f"{url}: HTTP {code}, {len(body)} byte(s) — no first page, no walk.",
                    EXIT_PARTIAL)
            end = f"page {n} came back HTTP {code}"
            break
        pages += 1
        if n == 1:
            heading, declared = section_count(body)
            last = max((int(x) for x in PAGER_RE.findall(body)), default=1)
        got, bad = listing(body, url)
        rejected += len(bad)
        if not got:
            end = f"page {n} carried no advert this adapter would emit"
            break
        for r in got:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            rows.append(r)
        if a.max_pages and pages >= a.max_pages:
            end = f"capped by --max-pages at {pages} of {last}"
            break
        if n >= (last or 1):
            break
        n += 1
    out = rows[:a.limit] if a.limit else rows
    if a.details:
        for r in out:
            r.update({k: v for k, v in advert(r["url"]).items() if v is not None})
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{th(len(rows))} vacancy(ies) emitted over {pages} page(s) of the "
         f"{VACANCY_SEGMENT} pager, which names {last} page(s); {end}.")
    # The WITNESS: a count the host prints in its own heading, not one we extracted.
    capped = bool(a.max_pages) or (a.limit and a.limit < len(rows))
    if declared is not None and not capped:
        gap = declared - len(rows)
        note(f"{th(len(rows))} emitted against {th(declared)} that the host declares in its "
             f"own `<h1>{heading}</h1>` — {('exact' if gap == 0 else f'{th(abs(gap))} apart')}. "
             "**This is a witness and not our own extraction**: it also closes regionally "
             "(330+3+6+1+5) and against the mixed parent (345 vacancies + 51 CVs = 396 Jobs).")
    elif declared is not None:
        note(f"the host declares {th(declared)} in its own `<h1>{heading}</h1>`; this walk was "
             "CAPPED, so the difference is ours and says nothing about the board.")
    else:
        note("the host printed no count in its heading this run: the board's size is NOT "
             "established by this walk, and the figure above is what we emitted.")
    note(f"{rejected} advert(s) dropped for not declaring themselves `{VACANCY_LABEL}`. "
         f"**`/en/rezyume/` — {CANDIDATE_LABEL}, 51 adverts written by real people offering "
         "themselves — is never enumerated, and `/en/rabota/`, the mixed parent, is refused: "
         "page one of it carries 6 CVs among 100.**")
    if not a.details:
        note("`teaser` is the host's own truncated description; the full text, the advertiser, "
             "the field of activity and `Listed by` need `--details`, which costs one request "
             "per advert at 5 s apart. **`Listed by: Agency` and bullet lists mean a count of "
             "adverts is not a count of openings, and `Location` is the advertiser's field — one advert read in full put its post in Balkan while its field said Ashgabat.**")
    note("no absolute date anywhere: `posted_relative` is carried AS READ and `posted` stays "
         "null. **The listing's order is not freshness — page one shows July and August "
         "bulletins in October.**")


def cmd_one(a):
    print(json.dumps(advert(a.url), ensure_ascii=False))
    note("contacts: the host serves the phone only as its own mask `+9936XXXXX` and the "
         "e-mail behind a `Show email` toggle; the real values sit in obfuscated "
         "`data-toggle=\"cb_unproc\"` attributes which this adapter DROPS and never decodes.")


def main():
    p = argparse.ArgumentParser(
        description="Naydizdes (Turkmenistan) — walks `/en/vakansii/`, the VACANCIES-only "
                    "enumerator, and never `/en/rabota/`, the mixed parent that holds 51 CVs "
                    "of real people among its 396 adverts. Every record is asserted to "
                    "declare itself a vacancy.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every vacancy the `/en/vakansii/` pager names, 5 s apart")
    s.add_argument("--limit", type=int)
    s.add_argument("--max-pages", type=int, help="stop after N pages")
    s.add_argument("--details", action="store_true",
                   help="fetch each advert page for its full text (one request per advert)")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("one", help="one advert page, with the category floor asserted")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_one)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
