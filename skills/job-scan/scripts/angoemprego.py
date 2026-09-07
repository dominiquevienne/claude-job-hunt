#!/usr/bin/env python3
"""Ango Emprego (`angoemprego.com`) — Angola's second adapter.

  angoemprego.py list [--since 2026-08-01] [--limit 20] [--fetch] [--live]
  angoemprego.py ad --slug gerente-de-balcao

**The smallest archive of the three Angolan boards and the largest flow.**
`jobartis.com` holds 38 547 advertisements and published 202 since 1 August;
this one holds 1 434 and published 924. *That inversion is the whole reason
this board was built second and the largest was not built at all.*

WORDPRESS JOB MANAGER: THE ADVERTISEMENTS ARE IN THEIR OWN FILES

The index declares fifteen children. **Two carry advertisements and eight
carry blog posts**, and they are named rather than globbed:

    job_listing-sitemap.xml    1 000 <loc>
    job_listing-sitemap2.xml     434 <loc>
                               -----
                               1 434, all distinct, all under /vagas/
    post-sitemap1..8.xml       NOT read — blog posts
    job_listing_region · job_listing_tag · category · misc   NOT read

*Aggregating `job_listing*` with a wildcard would be one keystroke and would
also sweep `job_listing_region` and `job_listing_tag`, which are taxonomies.*
**A sibling file is not the same kind of thing as its neighbour**, and this
repository has swept 15 940 tenders into a job count that way once.

TWO BLOCKS, AND SIX YEARS OF NOTHING BETWEEN THEM

    2020   349 advertisements ·  9 dates · 2020-10-15 … 2020-11-23
                                          226 on one day — 65 % of the block
           ——— nothing at all between 2020-11-23 and 2026-07-29 ———
    2026 1 085 advertisements · 35 dates · 2026-07-29 … 2026-09-07
                                          busiest 96 — 8.8 % of the block
                                          median 30 a day

**The busiest-day check fired first at 15.8 % of the whole file, and reading
the distribution said what it was**: a launch block of 2020, not a defect in
the current flow. *The check flags; it does not conclude.* See
`shared/plausible-and-false.md`.

**So `--since` is what makes this board usable**, and the default listing
carries both blocks with their dates so the gap stays visible.

THE DATES ARE PUBLICATION DATES, AND THAT WAS CHECKED RATHER THAN ASSUMED

    lastmod 2026-08-18 · datePosted 2026-08-18     4 of 4 sampled
    lastmod 2026-08-26 · datePosted 2026-08-26
    lastmod 2026-08-20 · datePosted 2026-08-20
    lastmod 2026-08-18 · datePosted 2026-08-18

*The file has 44 distinct dates for 1 434 advertisements and **not one day
carrying a single advertisement**, which is what a regeneration stamp looks
like.* **It is not one**: the sitemap's date is the advertisement's own, on
four of four. **A suspicion checked and refuted is worth as much as one
confirmed**, and `myjobsfiji.com` — 3 187 entries under one `lastmod` — is
why it gets checked at all.

`baseSalary` IS present and is NOT emitted: it reads `currency: USD` with an
empty `value` on an Angolan board, where the currency is the kwanza. *The same
shape as `négociable XPF` on `burundijobs`* — **a field present and wrong is
worse than one absent**, and what a field is worth is a property of the board.

`strict=False` is applied from the first line here: its Angolan neighbour's
`JobPosting` block carries a raw control character, and the zero a
single-attempt parser returns looks exactly like a site with no structured
data.

Verified against the live site on 2026-09-07.
"""


import argparse
import datetime
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

BASE = "https://angoemprego.com"
# **Named, never globbed.** `job_listing_region` and `job_listing_tag` are
# taxonomies and would match a `job_listing*` wildcard.
SITEMAPS = (BASE + "/job_listing-sitemap.xml",
            BASE + "/job_listing-sitemap2.xml")
ADS = "/vagas/"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[angoemprego] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    # An unknown is not a refusal: `not None` is `True` for both.
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# The host declares no `Crawl-delay`; one second is ours and is declared as
# ours. Since #179 this spacing is shared across processes, so a sweep and a
# hand-run `bin/fetch-body.py` no longer hit the host together.
_PACE = Pace("angoemprego.com", own=1.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "pt-AO,pt;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, "", url
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def slug_of(url):
    return url.rstrip("/").rsplit("/", 1)[-1]


def entries():
    """`(ads, raw)` — **both numbers, because the ratio is the finding.**"""
    rows, raw, seen = [], 0, set()
    for sm in SITEMAPS:
        code, body, _l = get(sm)
        if code != 200:
            die(f"{sm}: HTTP {code}")
        found = 0
        for block in ENTRY.findall(body):
            loc = LOC.search(block)
            if not loc:
                continue
            raw += 1
            found += 1
            u = html_mod.unescape(loc.group(1).strip())
            if ADS not in u or u in seen:
                continue
            seen.add(u)
            d = LASTMOD.search(block)
            rows.append((u, d.group(1) if d else None))
        if not found:
            # **Per file, not only at the end.** A second sitemap that turns
            # empty is invisible once the first has filled the list.
            note(f"{sm} parsed to zero entries from {len(body)} characters — "
                 f"read the bytes before believing the zero.")
    if not rows:
        die(f"{len(SITEMAPS)} sitemap(s) parsed to zero advertisements — "
            f"read the bytes before believing the zero.")
    rows.sort(key=lambda r: (r[1] or ""), reverse=True)
    return rows, raw


def posting_on(page):
    """**`strict=False` is the whole reason this board is readable.**

    Its `JobPosting` block carries a raw control character and `json.loads`
    refuses it outright. A parser that tries once returns nothing on every
    advertisement, and *nothing* looks exactly like a site that publishes no
    structured data.
    """
    for b in LDJSON.findall(page):
        for strict in (True, False):
            try:
                d = json.loads(b.strip(), strict=strict)
            except ValueError:
                continue
            graph = d.get("@graph") if isinstance(d, dict) else None
            items = graph or (d if isinstance(d, list) else [d])
            for it in items:
                if isinstance(it, dict) and it.get("@type") == "JobPosting":
                    return it, None
            break
    return None, "no readable JobPosting on the page"


def card(url, lastmod, posting):
    org = posting.get("hiringOrganization")
    org = org.get("name") if isinstance(org, dict) else org
    place = posting.get("jobLocation")
    place = place[0] if isinstance(place, list) and place else place
    addr = (place or {}).get("address") if isinstance(place, dict) else None
    # **`address` is a bare string here, not a `PostalAddress`.** The Angolan
    # neighbour writes the object; this board writes `"Luanda"`. A reader that
    # only knows the object form returns `None` on every advertisement — and
    # `None` reads as *this board states no place*, which is false.
    city = (addr.get("addressLocality") if isinstance(addr, dict)
            else addr if isinstance(addr, str) else None)
    kind = posting.get("employmentType")
    if isinstance(kind, list):
        kind = ", ".join(str(k) for k in kind) or None
    return {
        "source": "angoemprego",
        "url": url,
        "slug": slug_of(url),
        # **The slug, because `identifier.value` is not an identifier here.**
        # It holds `https://angoemprego.com/?post_type=job_listing&#038;p=…`
        # — a query URL, HTML-escaped twice. The slug is the board's own, it
        # is in the URL, and it is stable.
        "ledger_id": f"angoemprego:{slug_of(url)}",
        "title": html_mod.unescape(posting.get("title") or "").strip() or None,
        "employer": (org or "").strip() or None,
        "city": (city or "").strip() or None,
        "employment_type": kind,
        "posted": (posting.get("datePosted") or "")[:10] or lastmod,
        "valid_through": (posting.get("validThrough") or "")[:10] or None,
        "countries": ["AO"],
    }


def cmd_list(a):
    rows, raw = entries()
    note(f"{raw} <loc> across {len(SITEMAPS)} named job sitemaps, "
         f"{len(rows)} distinct under `{ADS}`. **The blog lives in eight "
         f"other files and none of them is read.**")
    if a.since:
        rows = [r for r in rows if r[1] and r[1] >= a.since]
        note(f"{len(rows)} with `lastmod` {a.since} or later — the date is on "
             f"the sitemap, so this cost no extra request.")
    if a.limit:
        rows = rows[: a.limit]
    if not (a.fetch or a.search or a.live):
        print(json.dumps({"source": "angoemprego", "country": "AO",
                          "sitemap_entries": raw, "advertisements": len(rows),
                          "ads": [{"url": u, "slug": slug_of(u), "posted": d}
                                  for u, d in rows]},
                         ensure_ascii=False, indent=1))
        return
    today = datetime.date.today().isoformat()
    kept, broken, gone, expired = [], [], 0, 0
    needle = fold(a.search) if a.search else None
    for u, d in rows:
        code, page, landed = get(u)
        if code in (404, 410):
            gone += 1
            continue
        if code != 200:
            broken.append((u, f"HTTP {code}"))
            continue
        if landed and landed.rstrip("/") != u.rstrip("/"):
            # **A redirect is not an advertisement.** Five of six listed URLs
            # bounced to the root on `emploisburkina.bf`, and only this field
            # showed it.
            broken.append((u, f"redirected to {landed}"))
            continue
        posting, why = posting_on(page)
        if posting is None:
            broken.append((u, why))
            continue
        c = card(u, d, posting)
        if a.live and c["valid_through"] and c["valid_through"] < today:
            expired += 1
            continue
        if needle and needle not in fold(c["title"] or ""):
            continue
        kept.append(c)
    if gone:
        note(f"{gone} answered 404 or 410 — still listed in the sitemap.")
    if a.live:
        note(f"{expired} dropped on a past `validThrough`.")
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{slug_of(u)} ({w})" for u, w in broken[:5]))
    print(json.dumps({"source": "angoemprego", "country": "AO",
                      "sitemap_entries": raw, "asked": len(rows),
                      "kept": len(kept), "gone": gone,
                      "unreadable": len(broken),
                      "expired_dropped": expired if a.live else None,
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken or gone:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}{ADS}{a.slug}"
    code, page, landed = get(url)
    if code in (404, 410):
        die(f"{a.slug} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    if landed and landed.rstrip("/") != url.rstrip("/"):
        die(f"{url} redirected to {landed} — that is not this advertisement.",
            EXIT_BROKEN)
    posting, why = posting_on(page)
    if posting is None:
        die(f"{url}: {why}")
    print(json.dumps(card(url, None, posting), ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="advertisements from the sitemap")
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="filter on `lastmod`, which is on the sitemap — this "
                         "costs no extra request")
    li.add_argument("--limit", type=int)
    li.add_argument("--search", help="match the title; folds accents")
    li.add_argument("--live", action="store_true",
                    help="drop advertisements whose `validThrough` has passed")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for its fields; without it the "
                         "listing is the sitemap alone, one request")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
