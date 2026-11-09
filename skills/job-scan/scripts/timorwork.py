#!/usr/bin/env python3
"""Timor.Work (`timor.work`, Timor-Leste) — the NGO, UN and private-sector vacancies, read through the sitemap and the fields each page serves.

  timorwork.py sitemap  [--limit N]
  timorwork.py listing  [--limit N]
  timorwork.py ad --url <vacancy URL>

THE ISSUE'S PLATFORM AND ROUTE ARE BOTH WRONG, AND THE PLATFORM CAME FROM A CSS CLASS

#686 and `shared/boards/timor-work.md` call this "a Ghost publication"
paginating by `/page/N/`. **It is Django and Wagtail.** `robots.txt` says so
itself in its own comments — `Disallow: /admin/  # disable crawling django
admin` and `Disallow: /cms/  # and wagtail admin` — and every vacancy body is
a Wagtail StreamField, its blocks carrying `data-block-key`.

**The word `ghost` does occur in a vacancy page, exactly once, as
`class="btn btn-ghost"`** — a DaisyUI button. A platform was read off a CSS
class, which is "counting a keyword measures the translation" applied to a
stylesheet. Nothing followed from it that was true: there is no Ghost Content
API here, so there is no client key to read either.

AND THERE IS NO `/page/N/` PAGER. `?page=` and `/page/` both occur **zero**
times on the front. The bare `/jobs/` is a **404** (12 727 B, body not kept —
the refusal is on disk and does not get re-fetched). What DOES exist is the
facets the card named, one level down: `/jobs/tag/<slug>/` and
`/jobs/employer/<slug>/`, linked from every vacancy.

TWO ENUMERATORS, AND THEY NEST — WHICH IS THE ONLY REASON A COUNT IS SAYABLE

`/sitemap.xml` is a flat `urlset`: **1 306 `<loc>`, 1 305 distinct** — the
duplicate is the ROOT, listed twice — leaving **1 304 vacancy addresses**, all
on the apex, all a flat `/<slug>/` with no prefix. Checked rather than
assumed: the shortest slugs are `driver`, `accountant`, `ofisial-kampu`, and
**no slug is a page name or carries a second segment**, so the shape is not
hiding a category the way a path prefix can.

The front page lists **30** vacancies under "Latest jobs", and **all 30 are in
the sitemap** — difference empty. So the front NESTS, and the sitemap is a
genuine superset rather than a second, partly disjoint view.

**BUT THE SITEMAP IS NOT PRUNED, AND THAT IS THE MEASUREMENT THAT DECIDES WHAT
MAY BE CLAIMED.** Its `lastmod` runs from 2024-02-04 to 2026-11-07 — 523 in
2024, 378 in 2025, 397 in 2026 — and the first, median and last members, read
on 2026-11-09, carry deadlines of **Feb. 15 2024, Oct. 26 2024 and Oct. 23
2026**: all three EXPIRED. So `1 304` is a count of ADDRESSES ACCUMULATED OVER
THREE YEARS and **never a count of open vacancies**; the sitemap carries no
deadline, so only a page or the front says whether one is live. The `sitemap`
subcommand prints that sentence beside its figure rather than leaving the
number to be read as a board size.

**No count is stated anywhere** — the front says none, which is what the card
already declared — so there is no second source for the figure.

THE DEADLINE MONTH IS DJANGO'S AP-STYLE `N`, AND `%b` FAILS SILENTLY ON IT

Dates are served as `Deadline: Nov. 20, 2026` and `Posted: Oct. 12, 2024`.
**Five months are spelled in full and unpunctuated — March, April, May, June,
July — and `Sept.` is four letters**, which is Django's `N` vocabulary.
Measured on the 36 date values held: `Nov.` 16, **`June` 13**, `Oct.` 4,
`Feb.` 2, `Dec.` 1, and `datetime.strptime(..., "%b")` **rejects `June`** — so
a naive parser loses 13 of 36 without raising.

So the map below is written out for all twelve in both forms, and an
unrecognised month is NAMED rather than guessed. **Only five of the twelve
tokens were OBSERVED**; the other seven come from Django's documented `N`
format, which this host is established to run — that is a declared source and
not an inference from the sample.

> **And the direction of a silently unreadable deadline is the expensive one:**
> it reads as "unknown", and anything that treats unknown as current surfaces
> a two-year-old vacancy as an opening. `closes` is `None` with a named reason
> beside it, and `expired` is `None` too — never `False` by default.

**`today` is a PARAMETER of the pure functions and never `date.today()` inside
them.** A test asserting "expired" against the real clock is the dated literal
§4 bis documents as a bomb in a suite: it passes until a date passes.

Measured 2026-11-09 12:13–12:15 UTC, guard on each exact path in a turn
distinct from retrieval, one token. Issue #686.
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import datetime
import html as htmlmod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _sitemap import locs as sitemap_locs
from _ua import UA
from _zero import empty_first_page

BASE = "https://timor.work"
SITEMAP = BASE + "/sitemap.xml"
LISTING = BASE + "/"
COUNTRY = "TL"

# a flat single-segment slug: `[a-z0-9-]` admits no `/`, so `/jobs/tag/x/` and
# `/media/...` are excluded by the shape itself, and the root by the required
# first character
AD_RE = re.compile(r"^https://timor\.work/([a-z0-9][a-z0-9-]*)/$")

TITLE_RE = re.compile(r'(?is)<h1[^>]*class="[^"]*pg-title[^"]*"[^>]*>(.*?)</h1>')
# the employer sits in the narrow card's own `<h2>`, and the logo's `alt`
# repeats it as `<name> logo` -- two sources, compared rather than assumed
EMPLOYER_RE = re.compile(
    r'(?is)<h2 class="text-xl font-bold text-center">\s*(.*?)\s*</h2>')
EMPLOYER_ALT_RE = re.compile(r'(?is)<img[^>]+alt="([^"]*?)\s+logo"')
LOCATION_RE = re.compile(r'(?is)class="[^"]*job-location[^"]*"[^>]*>(.*?)</(?:p|div)>')
DEADLINE_RE = re.compile(r'(?is)class="[^"]*job-deadline[^"]*"[^>]*>\s*Deadline:\s*(.*?)\s*</p>')
POSTED_RE = re.compile(r'(?is)<span class="text-sm">\s*Posted:\s*(.*?)\s*</span>')
BODY_RE = re.compile(r'(?is)<div class="[^"]*pg-content[^"]*"[^>]*>(.*?)</div>\s*(?:<|$)')
# **scoped to the PILL, not to the href.** The nav carries a "By sector" menu
# of `/jobs/tag/` links and it comes FIRST: a motif on the href alone returned
# `education, communications, health-medicine, accounting-finance, governance`
# -- IDENTICAL on all three vacancies measured, which was the only tell, and
# the same fault as taking the first `/ui/public-area/` link on another board.
# The nav does NOT use this pill class (its count equals the pill match count
# on all three), and the vacancy's own tags VARY: `dfat, ngo, international,
# me` against `health-medicine, usaid` against `consultant, gedsi,
# agriculture, environment, world-vision, ngo, international, senior-level`.
# They appear TWICE per page -- the narrow card and the footer block -- so they
# are deduplicated in order of appearance.
TAG_RE = re.compile(r'(?is)<span class="inline-block bg-gray-200 rounded-full[^"]*">\s*'
                    r'<a href="/jobs/tag/([^"/]+)/"[^>]*>(.*?)</a>\s*</span>')


def _tags(markup):
    """The vacancy's own tags, deduplicated by slug, in order of appearance."""
    out, vus = [], set()
    for slug, label in TAG_RE.findall(markup):
        if slug in vus:
            continue
        vus.add(slug)
        out.append({"slug": slug, "label": text(label)})
    return out
EMPLOYER_SLUG_RE = re.compile(r'(?is)<a href="/jobs/employer/([^"/]+)/"[^>]*>(.*?)</a>')
CARD_RE = re.compile(r'(?=<div class="bg-white rounded-lg border bg-card)')
CARD_TITLE_RE = re.compile(
    r'(?is)<h2 class="text-2xl font-bold mt-2">\s*<a href="([^"]+)"[^>]*>(.*?)</a>')
CARD_DESC_RE = re.compile(r'(?is)class="[^"]*job-description[^"]*"[^>]*>(.*?)</p>')

# **Django's AP-style `N`.** Five months are full and unpunctuated and `Sept.`
# is four letters; `%b` rejects those, and it rejected `June` on 13 of the 36
# values held. Written out in both forms so the map cannot be wrong by
# omission for anything this host serves.
MONTHS = {
    "jan": 1, "jan.": 1, "january": 1,
    "feb": 2, "feb.": 2, "february": 2,
    "mar": 3, "mar.": 3, "march": 3,
    "apr": 4, "apr.": 4, "april": 4,
    "may": 5, "may.": 5,
    "jun": 6, "jun.": 6, "june": 6,
    "jul": 7, "jul.": 7, "july": 7,
    "aug": 8, "aug.": 8, "august": 8,
    "sep": 9, "sep.": 9, "sept": 9, "sept.": 9, "september": 9,
    "oct": 10, "oct.": 10, "october": 10,
    "nov": 11, "nov.": 11, "november": 11,
    "dec": 12, "dec.": 12, "december": 12,
}
DATE_RE = re.compile(r"^([A-Za-z]+\.?)\s+(\d{1,2}),\s*(\d{4})$")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


class ShapeMoved(Exception):
    """200, and neither shape this adapter knows.

    **A pure function must not call `sys.exit`**: raising is what lets
    `tests/` tell "the shape moved" from "the vacancy is empty", which is the
    whole point of the message.
    """


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[timorwork] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# no `Crawl-delay` is declared -- the rules file is 102 bytes and carries two
# `Disallow:` lines and nothing else -- so 2 s is ours
_PACE = Pace("timor.work", own=2.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en,pt;q=0.6"})
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


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"[ \t]+", " ", htmlmod.unescape(markup)).strip()


def th(n):
    """Thousands with a space -- «1 304» -- the repo's figure style."""
    return f"{n:,}".replace(",", " ")


def when(s):
    """`(iso, None)` from «Nov. 20, 2026», or `(None, why)`.

    The month vocabulary is Django's `N`: five full unpunctuated names and a
    four-letter `Sept.`, none of which `%b` accepts. **An unrecognised month
    is NAMED**, because a deadline that silently fails to parse is read as
    unknown, and unknown treated as current surfaces a dead vacancy.
    """
    s = re.sub(r"\s+", " ", (s or "")).strip()
    if not s:
        return None, "no value"
    m = DATE_RE.match(s)
    if not m:
        return None, f"not the shape «Mon. D, YYYY»: {s!r}"
    mon, day, year = m.groups()
    num = MONTHS.get(mon.lower())
    if num is None:
        return None, (f"month not recognised: {mon!r} — Django's `N` format "
                      f"spells March, April, May, June and July in full")
    try:
        return datetime.date(int(year), num, int(day)).isoformat(), None
    except ValueError as e:
        return None, f"not a date: {s!r} ({e})"


def _expired(iso, today):
    """`True`/`False`, or **`None` when the deadline could not be read**.

    Never `False` by default: a dead vacancy that reports "not expired" is
    the one mistake this board makes easy.
    """
    if not iso or today is None:
        return None
    return datetime.date.fromisoformat(iso) < today


def parse_ad(slug, url, body, today=None):
    """`(record, notes)` from one served vacancy page — **no network at all.**

    `today` is a PARAMETER and never `date.today()` here: an assertion about
    expiry against the real clock passes until a date passes.
    """
    notes = []
    t = TITLE_RE.search(body)
    title = text(t.group(1)) if t else None
    e = EMPLOYER_RE.search(body)
    employer = text(e.group(1)) if e else None
    ea = EMPLOYER_ALT_RE.search(body)
    employer_alt = text(ea.group(1)) if ea else None
    if employer and employer_alt and employer.lower() != employer_alt.lower():
        notes.append(f"the employer heading says {employer!r} and the logo's alt "
                     f"says {employer_alt!r} — two sources, one grandeur, and they "
                     f"disagree on this vacancy")
    loc = LOCATION_RE.search(body)
    d = DEADLINE_RE.search(body)
    p = POSTED_RE.search(body)
    closes, why_c = when(text(d.group(1))) if d else (None, "no `job-deadline` on the page")
    posted, why_p = when(text(p.group(1))) if p else (None, "no `Posted:` on the page")
    b = BODY_RE.search(body)
    tags = _tags(body)
    # the employer FACET links are a navigation list -- 20 on every page
    # measured -- so the employer is NEVER taken from them
    if not title and not employer:
        raise ShapeMoved(
            f"{url}: 200 and neither a `pg-title` nor an employer heading. "
            f"**This says the page shape moved, not that the vacancy is empty.**")
    for why, which in ((why_c, "deadline"), (why_p, "posted")):
        if why:
            notes.append(f"{which}: {why} — emitted raw, parsed as null.")
    out = {
        "source": "timorwork", "country": COUNTRY,
        "ledger_id": f"timorwork:{slug}", "id": slug, "url": url,
        "title": title,
        "employer": employer,
        "employer_alt": employer_alt,
        "city": text(loc.group(1)) if loc else None,
        "posted": posted, "posted_raw": text(p.group(1)) if p else None,
        "closes": closes, "closes_raw": text(d.group(1)) if d else None,
        # `None` when the deadline could not be read, never `False`
        "expired": _expired(closes, today),
        "as_of": today.isoformat() if today else None,
        "tags": tags,
        "description": (text(b.group(1)) if b else "")[:20000] or None,
        # the page declares no zone and no time: the deadline is a DATE
        "dates_tz": None,
        "language": "en",
    }
    return out, notes


def parse_listing(body, today=None):
    """`(rows, notes)` from the front page's "Latest jobs" cards.

    Each card carries the whole record inline -- employer and its facet slug,
    title, city, a clamped description and the deadline -- so the live
    vacancies are reachable without one fetch per address.
    """
    rows, notes = [], []
    for card in CARD_RE.split(body)[1:]:
        m = CARD_TITLE_RE.search(card)
        if not m:
            continue
        href, titre = m.group(1), text(m.group(2))
        em = EMPLOYER_SLUG_RE.search(card)
        loc = LOCATION_RE.search(card)
        d = DEADLINE_RE.search(card)
        desc = CARD_DESC_RE.search(card)
        closes, why = when(text(d.group(1))) if d else (None, "no `job-deadline` on the card")
        if why:
            notes.append(f"{href}: deadline: {why} — emitted raw, parsed as null.")
        slug = href.strip("/")
        rows.append({
            "source": "timorwork", "country": COUNTRY,
            "ledger_id": f"timorwork:{slug}", "id": slug,
            "url": BASE + href,
            "title": titre,
            "employer": text(em.group(2)) if em else None,
            "employer_slug": em.group(1) if em else None,
            "city": text(loc.group(1)) if loc else None,
            "closes": closes, "closes_raw": text(d.group(1)) if d else None,
            "expired": _expired(closes, today),
            "as_of": today.isoformat() if today else None,
            "tags": _tags(card),
            "description": text(desc.group(1)) if desc else None,
            "language": "en",
        })
    return rows, notes


def cmd_sitemap(a):
    code, xml = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_PARTIAL)
    raw = sitemap_locs(xml)
    if not raw:
        die(empty_first_page("timorwork", xml, "<loc>", where=SITEMAP), EXIT_PARTIAL)
    rows, seen, unmatched = [], set(), 0
    for loc in raw:
        m = AD_RE.match(loc.strip())
        if not m:
            unmatched += 1
            continue
        slug = m.group(1)
        if slug in seen:
            continue
        seen.add(slug)
        rows.append({"source": "timorwork", "country": COUNTRY,
                     "ledger_id": f"timorwork:{slug}", "id": slug,
                     "url": loc.strip()})
    if not rows:
        die(f"{SITEMAP}: {th(len(raw))} <loc> and not one of the shape "
            f"https://timor.work/<slug>/ — the vacancy addresses moved. "
            f"**Nothing here says the board is empty.**", EXIT_PARTIAL)
    for r in (rows[:a.limit] if a.limit else rows):
        print(json.dumps(r, ensure_ascii=False))
    note(f"{th(len(raw))} <loc>, {th(len(raw) - unmatched)} of the vacancy shape and "
         f"{unmatched} not (the root, listed twice); **{th(len(rows))} distinct "
         f"vacancy address(es)**"
         + (f" ({a.limit} printed under --limit)" if a.limit else "") + ".")
    note("**This is a count of ADDRESSES and not of open vacancies.** The sitemap is "
         "not pruned — its `lastmod` spans 2024-02-04 to 2026-11-07 and the first, "
         "median and last members all carried EXPIRED deadlines when this was "
         "written — and it carries no deadline at all, so nothing here says whether "
         "an address is live. Use `listing` for the current ones, or `ad` for a "
         "deadline. No count is stated anywhere on the site, so there is no second "
         "source for this figure.")


def cmd_listing(a):
    code, body = get(LISTING)
    if code != 200:
        die(f"{LISTING}: HTTP {code}", EXIT_PARTIAL)
    rows, notes = parse_listing(body, today=datetime.date.today())
    if not rows:
        die(empty_first_page("timorwork", body, "job-deadline", where=LISTING),
            EXIT_PARTIAL)
    for r in (rows[:a.limit] if a.limit else rows):
        print(json.dumps(r, ensure_ascii=False))
    for n in notes:
        note(n)
    vivantes = sum(1 for r in rows if r["expired"] is False)
    inconnues = sum(1 for r in rows if r["expired"] is None)
    note(f"{len(rows)} vacancy card(s) on the front; **{vivantes} with a deadline at "
         f"or after today**, {sum(1 for r in rows if r['expired'] is True)} past, "
         f"{inconnues} whose deadline could not be read"
         + (" — an unreadable deadline is NOT counted as live" if inconnues else "") + ".")
    note("The front states no count of its own, and it does not paginate: `?page=` "
         "and `/page/` both occur zero times. So this is the latest page and not the "
         "board — every one of these addresses is in the sitemap, which is the "
         "superset.")


def cmd_ad(a):
    url = a.url.strip()
    m = AD_RE.match(url)
    if not m:
        die(f"{url}: not a vacancy address — expected {BASE}/<slug>/")
    code, body = get(url)
    if code == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}. **A readable body is not an answer — the code "
            f"decides.**")
    try:
        out, notes = parse_ad(m.group(1), url, body, today=datetime.date.today())
    except ShapeMoved as e:
        die(str(e), EXIT_PARTIAL)
    print(json.dumps(out, ensure_ascii=False))
    for n in notes:
        note(n)


def main():
    p = argparse.ArgumentParser(
        description="Timor.Work — Timor-Leste's NGO, UN and private-sector "
                    "vacancies, through its sitemap and the fields its pages serve.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="every vacancy ADDRESS, three years deep and "
                                       "not pruned — see the note it prints")
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_sitemap)
    l = sub.add_parser("listing", help="the front page's latest vacancies, with "
                                       "their deadlines, in one request")
    l.add_argument("--limit", type=int)
    l.set_defaults(fn=cmd_listing)
    d = sub.add_parser("ad", help="one vacancy, from the fields it serves")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
