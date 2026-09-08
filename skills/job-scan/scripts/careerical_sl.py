#!/usr/bin/env python3
"""Careerical Sierra Leone (`sierra.careerical.com`) — a local board, and its
schema is not valid JSON.

  careerical_sl.py list [--since 2026-01-01] [--limit 20]
  careerical_sl.py list --fetch --limit 10
  careerical_sl.py ad --slug undp-job-vacancy-for-national-youth-expert

**2 344 advertisements across three named sitemaps, and the most evenly spread
dates this repository has measured.**

    2 344 advertisements   1 377 distinct dates   2020-12-06 → 2026-08-28
    busiest day              6, which is 0.3 %
    in 2026                116        since 2026-08-01   17

*Against 1.4 % for `jobwebrwanda`, 18.5 % for `jobartis` and 60.5 % for
`ihararejobs`.* **A board that publishes a few a week for six years leaves a
flat distribution, and that is what a real one looks like** — which matters
here, because Sierra Leone's other live host is a node of a network whose
content carries five distinct marks of fabrication.

**This host is not that node.** Sierra Leone's country page separates them:
`sierraleonejobsearch.com` is the node; this is *«board local»*, added the
evening of 2026-09-04 after the page had already been written without it.

THREE SITEMAPS BY NAME, AND A TAXONOMY THAT A GLOB WOULD EAT

    job-sitemap.xml    1 000      <- Yoast's round cap
    job-sitemap2.xml   1 000      <- the cap again
    job-sitemap3.xml     344      <- partial, so the set is complete
                       -----
                       2 344      0 duplicates BETWEEN files

**`job_category-sitemap.xml` sits in the same index**, and a `job*` glob takes
it. The three are named individually. *And the cross-file duplicate check is
not ceremony: 403 of 1 783 URLs were duplicates between files on another board,
under a sum that added up perfectly.*

**Two round caps and a partial third is what a complete set looks like.** *A
single file at exactly 1 000 would have been a ceiling to distrust.*

THE `ld+json` IS HTML-ESCAPED AND IT IS NOT VALID JSON

Two defects, and only one of them is repairable:

    1.  the block is written with &quot; instead of "        -> html.unescape
    2.  `{"@context":"http:` — the value is truncated       -> one substitution
    3.  unescaped " inside `description`                    -> NOT repairable

*The third is what a repair cannot reach:* `such as"I will conduct stakeholder
engagement,"explain how` — **the string's own boundaries are the thing that was
lost**, so no rewrite can recover them without already knowing where the field
ends.

**So this module does not parse the document. It extracts the fields it
needs**, by name, from the unescaped text — and `description`, the field that
breaks the JSON, is the one field it does not want.

The order is: parse as JSON; if that fails, repair `@context` and parse; if
that fails, take the fields directly. **Each advertisement reports which path
it took in `read_by`, and `list --fetch` counts them** — *a shift in those
counts is the site changing, and it would otherwise be silent.*

*Measured on 5: 1 parsed after the `@context` repair alone on the first try,
3 the same way, 1 needed the field reader.*

THE SITEMAP DATE IS THE POSTING DATE — 4 OF 4 WHERE THE PAGE COULD BE READ

`lastmod` equals `datePosted` every time both were available, across dates from
2022 to 2026. **So `--since` costs three requests**, not one per advertisement.

WHAT THE SCHEMA CARRIES, AND WHAT SHAPE IT IS IN

`hiringOrganization` is a **bare string** here — `"Abt Associates"` — not an
`Organization` object, so a reader written for the usual shape reads `None`.
`baseSalary` is a `PriceSpecification` whose `price` is the word
`negotiable`, with `salaryCurrency` `"Le"`. **The salary is emitted as text and
never as a number**, because it is not one.

Verified against the live site on 2026-09-08.
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
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BASE = "https://sierra.careerical.com"
# **Named one by one.** `job_category-sitemap.xml` is in the same index and a
# `job*` glob would take it; it is a taxonomy.
SITEMAPS = (BASE + "/job-sitemap.xml",
            BASE + "/job-sitemap2.xml",
            BASE + "/job-sitemap3.xml")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(\d{4}-\d{2}-\d{2})", re.S)
AD_URL = re.compile(r"^https://sierra\.careerical\.com/job/([^/]+)/?$")
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)
# The one repairable defect: `@context` truncated to `http:`.
CONTEXT_CUT = re.compile(r'^\s*\{"@context":"http:')


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[careerical-sl] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# The host declares no `Crawl-delay`; this spacing is ours and declared as ours.
_PACE = Pace("sierra.careerical.com", own=1.5)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-SL,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def entries():
    """Every advertisement, from the three named sitemaps."""
    rows, per_file, seen = [], {}, set()
    for url in SITEMAPS:
        code, body = get(url)
        if code != 200:
            die(f"{url}: HTTP {code}")
        n = 0
        for block in ENTRY.findall(body):
            loc = LOC.search(block)
            if not loc:
                continue
            u = html_mod.unescape(loc.group(1).strip())
            m = AD_URL.match(u)
            if not m:
                continue
            n += 1
            if u in seen:
                continue
            seen.add(u)
            d = LASTMOD.search(block)
            rows.append({"source": "careerical-sl", "url": u,
                         "slug": m.group(1),
                         "ledger_id": f"careerical-sl:{m.group(1)}",
                         "posted": d.group(1) if d else None,
                         "countries": ["SL"]})
        per_file[url.rsplit("/", 1)[-1]] = n
    if not rows:
        die("the three sitemaps parsed to zero advertisements — read the "
            "bytes before believing the zero.")
    rows.sort(key=lambda r: (r["posted"] or ""), reverse=True)
    return rows, per_file


FIELDS = ("datePosted", "validThrough", "title", "employmentType",
          "occupationalCategory", "salaryCurrency", "hiringOrganization")


def fields_by_hand(text):
    """The scalar fields, taken by name from text that is not valid JSON.

    **`description` is deliberately not among them.** It is the field whose
    unescaped quotes break the document, and it is the one field this module
    has no use for: *what cannot be parsed is also what was not wanted.*
    """
    out = {}
    for name in FIELDS:
        m = re.search(rf'"{name}"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
        if m:
            out[name] = m.group(1)
    for key in ("addressLocality", "addressRegion"):
        m = re.search(rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
        if m:
            out[key] = m.group(1)
    price = re.search(r'"price"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
    if price:
        out["price"] = price.group(1)
    return out


def posting_on(page):
    """`(fields, how)` — and `how` names the path that worked.

    Three of them, in order of how much they assume about the site: valid
    JSON, JSON after the one repairable defect, and the fields alone.
    """
    for block in LDJSON.findall(page):
        text = html_mod.unescape(block.strip())
        if '"JobPosting"' not in text:
            continue
        # **`strict=False` is tried on both attempts, and it changes nothing
        # here.** It exists for raw control characters inside a string, which
        # is what made it load-bearing on `angolaemprego`; the defects on this
        # board are a truncated `@context` value and unescaped quotes, and a
        # lax parser has no opinion about either. *Measured on 2 blocks of the
        # same page: the JobPosting block fails raw and unescaped, strict and
        # lax — four attempts, four failures.* It is tried anyway, because the
        # day this board adds a control character the cost of not trying is a
        # third path taken for the wrong reason.
        for repair in (False, True):
            body = CONTEXT_CUT.sub("{", text, count=1) if repair else text
            for strict in (True, False):
                try:
                    d = json.loads(body, strict=strict)
                except ValueError:
                    continue
                if isinstance(d, dict):
                    how = "json after `@context` repair" if repair else "json"
                    return d, (how if strict else how + ", lax")
        got = fields_by_hand(text)
        if got.get("title") or got.get("datePosted"):
            return got, "fields — the block is not valid JSON"
        return None, "a JobPosting block that yielded no field"
    return None, "no JobPosting block on the page"


def card(row, post, how):
    org = post.get("hiringOrganization")
    # **A bare string here, not an Organization.** A reader written for the
    # usual shape returns `None` on every advertisement of this board.
    employer = org if isinstance(org, str) else (
        (org or {}).get("name") if isinstance(org, dict) else None)
    # **The place is in the wrong fields, and `addressLocality` is empty.**
    #
    #     "addressLocality": ""
    #     "addressRegion":   "Freetown|Sierra Leone"
    #     "postalCode":      "Freetown|Sierra Leone"     <- the same string
    #
    # A reader that takes `addressLocality`, which is what the schema is for,
    # gets nothing on this board. The town and the country are pipe-joined
    # into `addressRegion` and copied into `postalCode`, which is therefore
    # not a postal code and is not emitted.
    place = post.get("jobLocation")
    addr = (place.get("address") or {}) if isinstance(place, dict) else {}
    city = post.get("addressLocality") or (
        addr.get("addressLocality") if isinstance(addr, dict) else None)
    region = post.get("addressRegion") or (
        addr.get("addressRegion") if isinstance(addr, dict) else None)
    country_name = None
    if not city and region and "|" in region:
        city, _, country_name = region.partition("|")
    elif not city and region:
        city = region
    bs = post.get("baseSalary")
    price = post.get("price")
    if price is None and isinstance(bs, dict):
        price = bs.get("price")
    out = dict(row)
    out.update({
        "title": html_mod.unescape((post.get("title") or "").strip()) or None,
        "employer": html_mod.unescape((employer or "").strip()) or None,
        "city": (city or "").strip() or None,
        "city_source": ("`addressRegion`, split on `|` — `addressLocality` is "
                        "empty on this board"),
        "country_name": (country_name or "").strip() or None,
        "employment_type": post.get("employmentType") or None,
        "category": post.get("occupationalCategory") or None,
        # **Text, never a number.** `price` reads `negotiable` and the
        # currency is `Le`; parsing a figure out of that would invent one.
        "salary_text": (str(price).strip() or None) if price is not None else None,
        "salary_currency": post.get("salaryCurrency") or None,
        "posted_on_page": (post.get("datePosted") or "")[:10] or None,
        "valid_through": (post.get("validThrough") or "")[:10] or None,
        "read_by": how,
    })
    if out["posted_on_page"] and out["posted"] and out["posted_on_page"] != out["posted"]:
        out["date_conflict"] = (f"sitemap {out['posted']}, page "
                                f"{out['posted_on_page']} — `--since` uses "
                                f"the sitemap")
    return out


def cmd_list(a):
    rows, per_file = entries()
    if not rows:
        # **`max()` below raises on an empty sequence**, so the zero path
        # crashed instead of reporting — and the per-file counts, which are the
        # anchor, were never printed. #181.
        die(f"the named sitemaps hold "
            f"{' + '.join(f'{k}:{v}' for k, v in per_file.items())} "
            f"= {sum(per_file.values())} `<loc>` and **0 advertisement(s) were "
            f"parsed**. The files are there and this reader got nothing out of "
            f"them — a reading that failed, not an empty board.", EXIT_PARTIAL)
    total = sum(per_file.values())
    # **Counted once, before any filter.** `rows` is about to be narrowed by
    # `--since` and `--limit`, and a duplicate count taken after that would
    # describe the slice rather than the files.
    held = len(rows)
    duplicates = total - held
    note(f"{held} advertisement(s) from three named sitemaps — "
         + " + ".join(f"{k}:{v}" for k, v in per_file.items())
         + f" = {total}, and **{duplicates} duplicate(s) between files**.")
    newest = max((r["posted"] or "") for r in rows)
    note(f"most recent: {newest}.")
    if a.since:
        rows = [r for r in rows if r["posted"] and r["posted"] >= a.since]
        note(f"{len(rows)} dated {a.since} or later.")
    if a.search:
        rows = [r for r in rows if fold(a.search) in fold(r["slug"])]
    if a.limit:
        rows = rows[: a.limit]
    if not a.fetch:
        if a.live:
            die("`--live` needs `--fetch`: `validThrough` is on the "
                "advertisement page, not in the sitemap.")
        print(json.dumps({"source": "careerical-sl", "country": "SL",
                          "advertisements": held,
                          "sitemap_entries": total,
                          "sitemap_files": per_file,
                          "duplicates_between_files": duplicates,
                          "returned": len(rows), "ads": rows},
                         ensure_ascii=False, indent=1))
        return
    today = datetime.date.today().isoformat()
    kept, broken, dropped, how_counts, conflicts = [], [], 0, {}, 0
    for row in rows:
        code, page = get(row["url"])
        if code in (404, 410):
            broken.append((row["slug"][:36], f"gone — HTTP {code}"))
            continue
        if code != 200:
            broken.append((row["slug"][:36], f"HTTP {code}"))
            continue
        post, how = posting_on(page)
        if post is None:
            broken.append((row["slug"][:36], how))
            continue
        how_counts[how] = how_counts.get(how, 0) + 1
        c = card(row, post, how)
        if c.get("date_conflict"):
            conflicts += 1
        if a.live and c["valid_through"] and c["valid_through"] < today:
            dropped += 1
            continue
        kept.append(c)
    note("read by: " + ", ".join(f"{k} × {v}" for k, v in how_counts.items())
         + ". **A shift here is the site changing its markup.**")
    if conflicts:
        note(f"{conflicts} page(s) disagree with the sitemap's date — it "
             f"matched on 4 of 4 when this was written.")
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{s} ({w})" for s, w in broken[:5]))
    print(json.dumps({"source": "careerical-sl", "country": "SL",
                      "advertisements": held,
                      "read": len(rows), "kept": len(kept),
                      "unreadable": len(broken),
                      "expired_dropped": dropped if a.live else None,
                      "read_by": how_counts, "date_conflicts": conflicts,
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}/job/{a.slug.strip('/')}/"
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.slug} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    post, how = posting_on(page)
    if post is None:
        die(f"{url}: {how}")
    row = {"source": "careerical-sl", "url": url, "slug": a.slug.strip("/"),
           "ledger_id": f"careerical-sl:{a.slug.strip('/')}",
           "posted": None, "countries": ["SL"]}
    print(json.dumps(card(row, post, how), ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="advertisements, from three requests")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for employer, city and dates")
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="the sitemap's `lastmod`, equal to `datePosted` on "
                         "4 of 4 sampled — so this costs three requests")
    li.add_argument("--live", action="store_true",
                    help="drop advertisements whose `validThrough` has "
                         "passed. Requires --fetch")
    li.add_argument("--search", help="match the slug; folds accents")
    li.add_argument("--limit", type=int)
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
