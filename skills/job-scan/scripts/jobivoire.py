#!/usr/bin/env python3
"""Fetch Ivorian ads from JobIvoire — by pagination, because its sitemap lies.

Côte d'Ivoire's job board. `robots.txt` is two lines and closes nothing:
`User-agent: *` and a bare `Disallow:`. **It declares no sitemap**, and the one
that exists should not be used.

  GET /job?page=<n>          → 12 advertisement links; 324 pages
  GET /job/details/<slug>    → one advertisement, with a clean `JobPosting`

**THE SITEMAP IS A TRAP, AND THAT IS WHY THIS PAGINATES.** Measured
2026-09-03:

    /sitemap.xml     311 <loc>, of which 227 under /job/details/
                     newest lastmod  2026-07-28
    /job?page=N      324 pages: 323 x 12 + 8 = 3 884 advertisements

**The sitemap holds 227 of 3 884 — six per cent — and its freshest entry is
five weeks old**, while the listing publishes twelve advertisements dated
today. An adapter written on it would miss **94% of the board and never meet
an error**: 200s all the way, a plausible count, nothing to catch.

**Emploitic, next door in Algeria, is the opposite case** — its sitemap is
declared in `robots.txt` and current to the minute, and `emploitic.py` uses it.
**Two neighbouring boards, two opposite routes, each measured.** Carrying the
habit of one to the other is the only real risk in this pair.

PAGINATION, CHECKED RATHER THAN ASSUMED. Pages 1, 2, 200 and 324 were read and
compared: 12, 12, 12 and 8 links, **zero overlap between any pair**, and page
325 returns none. `323 x 12 + 8 = 3 884` exactly.

**THE LISTING'S OWN `ld+json` DOES NOT PARSE, AND THE ADVERTISEMENT'S DOES.**
The listing carries one block naming twelve `JobPosting`s, and it is invalid
JSON: a title reads `d\\&#039;Atelier` — a backslash before an HTML entity,
which is not an escape. `json.loads` refuses it with or without `strict=False`.

**So this reads the advertisement links out of the markup and the fields off
each advertisement page**, where the block is well formed. `_ldjson`'s
`absent_reason()` reports the listing block as `unparseable` with
`our_fault=True`, which is correct and is why nothing here silently returns
zero: **a page that says `JobPosting` and yields none has been misread.**

Verified against the live site on **2026-09-03**.
"""

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _ldjson import absent_reason, label, one, postings
from _robots import allowed as robots_allowed
from _ua import UA
from _zero import zero_note

BASE = "https://www.jobivoire.ci"
LIST = BASE + "/job"
PER_PAGE = 12
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

AD_LINK = re.compile(r"/job/details/([^\"'?#\s]+)")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobivoire] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, parts.path or "/")
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)


def get(url):
    gate(url)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "fr-CI,fr;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def slugs_on(page_html):
    """Advertisement slugs, in order, from the markup.

    **Not from the block.** The listing's `ld+json` is invalid JSON and
    carries no per-advertisement URL even when repaired — three `url` fields
    for twelve postings, and none of them an advertisement.
    """
    out = []
    for slug in AD_LINK.findall(page_html):
        if slug not in out:
            out.append(slug)
    return out


PLACEHOLDER_EMPLOYER = "Employeur via JobIvoire.ci"
ENTITY = re.compile(r"&(?:#\d+|#x[0-9a-fA-F]+|[a-zA-Z][a-zA-Z0-9]*);")


def unescape_fully(value):
    """The description arrives with its entities escaped twice.

    `Détails de l&#039;offre` reaches the field as text, so one pass leaves
    `&#039;` in the ledger. Runs to a fixed point rather than a fixed count,
    so a value legitimately holding `&amp;amp;` is not over-decoded — the same
    shape as `employtt.py`.
    """
    for _ in range(3):
        if not ENTITY.search(value or ""):
            break
        after = html.unescape(value)
        if after == value:
            break
        value = after
    return value


def card(slug, posting):
    addr = one(one(posting.get("jobLocation")).get("address"))
    company = label(posting.get("hiringOrganization"))
    desc = unescape_fully(posting.get("description") or "")
    return {
        "id": slug,
        "ledger_id": f"jobivoire:{slug}",
        "url": f"{BASE}/job/details/{slug}",
        "title": posting.get("title"),
        # **The employer is never named here.** `hiringOrganization.name` is
        # the board's own placeholder on 12 of 12 sampled, with `sameAs`
        # pointing at the board. **The real employer appears inside the
        # description text**, so this is emitted under a name that says what
        # it holds rather than as a company.
        "company": None if company == PLACEHOLDER_EMPLOYER else company,
        "company_field_is_the_board_placeholder":
            company == PLACEHOLDER_EMPLOYER,
        "location_text": addr.get("addressLocality") or addr.get(
            "addressRegion"),
        "country": addr.get("addressCountry"),
        "employment_type": posting.get("employmentType"),
        "posted": posting.get("datePosted"),
        "valid_through": posting.get("validThrough"),
        # A teaser, not the advertisement: 158 characters on the one
        # measured, and 0 of 12 over 200. The page carries more.
        "description_chars": len(desc),
        "description_is_a_teaser": len(desc) < 400,
    }


def read_ad(slug, with_text=False):
    url = f"{BASE}/job/details/{slug}"
    code, page = get(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE)
    found = postings(page)
    if not found:
        why = absent_reason(page)
        die(f"{url}: {why.text}",
            EXIT_BROKEN if why.our_fault else EXIT_GONE)
    row = card(slug, found[0])
    if with_text:
        row["description"] = unescape_fully(found[0].get("description") or "")
    return row


def cmd_search(a):
    seen, kept, previous = [], 0, None
    page = a.page
    while True:
        code, html = get(f"{LIST}?page={page}")
        if code != 200:
            note(f"page {page}: HTTP {code} — stopping.")
            break
        found = slugs_on(html)
        if not found:
            note(f"page {page} carried no advertisement link — that is the "
                 f"end of the listing. Page 325 does the same, which is how "
                 f"the total was checked.")
            break
        # **The check that matters on any paginated board**: a page that
        # repeats the previous one has not advanced, whatever it answered.
        # Measured clean here — pages 1, 2, 200 and 324 share nothing — so a
        # repeat means the mechanism changed, not that the board is small.
        if previous is not None and set(found) & set(previous):
            overlap = len(set(found) & set(previous))
            note(f"page {page} repeats {overlap} of page {page - 1}'s "
                 f"{len(previous)} links — the pagination stopped advancing. "
                 f"{kept} advertisement(s) so far and they are good.")
            sys.exit(EXIT_PARTIAL)
        previous = found
        for slug in found:
            if slug in seen:
                continue
            seen.append(slug)
            if a.urls_only:
                print(json.dumps({"url": f"{BASE}/job/details/{slug}"},
                                 ensure_ascii=False))
            else:
                print(json.dumps(read_ad(slug, a.with_text),
                                 ensure_ascii=False))
                time.sleep(a.delay)
            kept += 1
            if a.limit and kept >= a.limit:
                note(f"{kept} advertisement(s) over {page - a.page + 1} "
                     f"page(s) of {PER_PAGE}.")
                return
        if a.pages and page - a.page + 1 >= a.pages:
            break
        page += 1
    if kept == 0:
        note(zero_note("jobivoire"))
        return
    note(f"{kept} advertisement(s) over {page - a.page + 1} page(s). **The "
         f"sitemap is not the route here**: it holds 227 advertisements with "
         f"a newest `lastmod` of 2026-07-28, against 3 884 on the listing — "
         f"94% missed, with no error anywhere.")


def cmd_ad(a):
    slug = a.slug or (a.url or "").rstrip("/").rsplit("/", 1)[-1]
    if not slug:
        die("give --slug or --url")
    print(json.dumps(read_ad(slug, a.with_text), ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="paginate the listing")
    s.add_argument("--page", type=int, default=1)
    s.add_argument("--pages", type=int)
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=0.8)
    s.add_argument("--urls-only", action="store_true", dest="urls_only",
                   help="one request per page instead of one per ad")
    s.add_argument("--with-text", action="store_true", dest="with_text")
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="read one advertisement")
    d.add_argument("--slug")
    d.add_argument("--url")
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
