#!/usr/bin/env python3
"""Angola Emprego (`angolaemprego.com`) — Angola's first adapter.

  angolaemprego.py list [--since 2026-08-01] [--limit 20] [--fetch] [--live]
  angolaemprego.py ad --slug oportunidade-urgente-medical-delegate

**Angola had a country page and no adapter.** Three boards were named there on
2026-09-04 and all three were left `à construire`; this is the one the page
measured as the most active.

THE SITEMAP IS ONE FLAT FILE AND MOST OF IT IS NOT ADVERTISEMENTS

    9 111 <loc> in a single sitemap.xml
      5 334  /noticias/    news articles
      3 724  /vagas/       advertisements      <- the only ones counted
          6  /cursos/ · /company/ · /sobre · /empresas

**A count of the file would report 9 111 and be wrong by a factor of 2.4.**
This site is a news outlet with a jobs section, which the country page had
already established; the module filters on `/vagas/` and **reports the raw
figure beside the kept one**, so the ratio stays visible rather than becoming
a number nobody can check.

DATES ARE ON THE SITEMAP, SO `--since` COSTS ONE REQUEST

    lastmod        3 724 of 3 724, 2025-03-29 … 2026-09-07
    distinct days  355
    busiest day    2026-08-14, 103 advertisements — 2.8 % of the total

**That last line is a check, not a statistic.** `jobartis.com`, the largest
board in this country, carries 2 525 distinct dates *and* 7 130
advertisements on one day of 2018 — **18 % of its archive in one import.** A
high count of distinct dates satisfies the instrument that separates an
archive from a stock and does not protect against an import; the busiest day
does. **Here it is 2.8 %, and this is a flow.**

    1 026 advertisements dated 2026-08-01 or later
      996 was the country page's figure on 2026-09-04

WITHOUT THE NON-STRICT FALLBACK, EVERY ADVERTISEMENT REPORTS NO DATA

The `JobPosting` block contains a raw control character, so `json.loads`
refuses it:

    Invalid control character at: line 5 column 33

**`strict=False` is not decoration on this board — it is the difference
between reading every advertisement and reading none.** *A parser that tries
once and gives up returns a confident zero, and its silence has the shape of
a site with no structured data.*

FIELDS, ON THE ADVERTISEMENT

    title · datePosted · validThrough · employmentType
    hiringOrganization.name · jobLocation.address.addressLocality
    identifier.value — the slug, so the ledger id is the board's own

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

BASE = "https://angolaemprego.com"
SITEMAP = BASE + "/sitemap.xml"
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
    print(f"[angolaemprego] {msg}", file=sys.stderr)


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
_PACE = Pace("angolaemprego.com", own=1.0)


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
    code, body, _l = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    rows, raw, seen = [], 0, set()
    for block in ENTRY.findall(body):
        loc = LOC.search(block)
        if not loc:
            continue
        raw += 1
        u = html_mod.unescape(loc.group(1).strip())
        if ADS not in u or u in seen:
            continue
        seen.add(u)
        d = LASTMOD.search(block)
        rows.append((u, d.group(1) if d else None))
    if not rows:
        die(f"{SITEMAP} parsed to zero advertisements from {len(body)} "
            f"characters — read the bytes before believing the zero.")
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
    addr = (place or {}).get("address") if isinstance(place, dict) else {}
    addr = addr if isinstance(addr, dict) else {}
    ident = posting.get("identifier")
    ident = ident.get("value") if isinstance(ident, dict) else ident
    kind = posting.get("employmentType")
    if isinstance(kind, list):
        kind = ", ".join(str(k) for k in kind) or None
    return {
        "source": "angolaemprego",
        "url": url,
        "slug": slug_of(url),
        # The board's own identifier, which is the slug — not one invented here.
        "ledger_id": f"angolaemprego:{ident or slug_of(url)}",
        "title": html_mod.unescape(posting.get("title") or "").strip() or None,
        "employer": (org or "").strip() or None,
        "city": (addr.get("addressLocality") or "").strip() or None,
        "employment_type": kind,
        "posted": (posting.get("datePosted") or "")[:10] or lastmod,
        "valid_through": (posting.get("validThrough") or "")[:10] or None,
        "countries": ["AO"],
    }


def cmd_list(a):
    rows, raw = entries()
    note(f"{raw} <loc> in the sitemap, {len(rows)} under `{ADS}`. **The rest "
         f"is a news site**: counting the file would report {raw} and be "
         f"wrong by a factor of {raw / max(1, len(rows)):.1f}.")
    if a.since:
        rows = [r for r in rows if r[1] and r[1] >= a.since]
        note(f"{len(rows)} with `lastmod` {a.since} or later — the date is on "
             f"the sitemap, so this cost no extra request.")
    if a.limit:
        rows = rows[: a.limit]
    if not (a.fetch or a.search or a.live):
        print(json.dumps({"source": "angolaemprego", "country": "AO",
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
    print(json.dumps({"source": "angolaemprego", "country": "AO",
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
