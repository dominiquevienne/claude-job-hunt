#!/usr/bin/env python3
"""eJobsFiji (`ejobsfiji.com`) — Fiji's second board, and a small one.

  ejobsfiji.py list [--fetch] [--since 2026-08-01] [--live] [--limit 20]
  ejobsfiji.py ad --id 1120

**Nine advertisements in a sitemap of 397 URLs.** The other 388 are 377
company pages, 6 blog posts and the site's own static pages.

    /companies/…  377      /blogs/…   6      /jobs/…   10      static  4
    /jobs/view?id=<n>   9   <- the advertisements

*Fiji's country page recorded fourteen on 2026-09-04.* Both counts are of the
same thing three days apart, and neither corrects the other.

**Nothing has been published here since 2026-08-03** — thirty-five days at the
time of writing. The board is open, readable and quiet, which is three
different facts from «broken».

THE IDENTIFIER IS IN THE QUERY STRING

`/jobs/view?id=1120`. **The guard is taken on path *and* query** via
`full_path()`, which exists because 54 of this repository's 55 call sites once
took `parts.path` alone and would have asked a refused path without seeing it.
Here the query is not merely part of the URL — **it is the whole of the
identity**, since every advertisement shares the path `/jobs/view`.

The schema states the same number in `identifier.value`, and this module
prefers that when present: *a number the board publishes about itself beats
one we parsed out of a URL.*

DATES ARE REAL AND SPREAD, UNLIKE ITS NEIGHBOUR'S

    9 advertisements · 9 with `lastmod` · 6 distinct dates · 2026-05-29 → 2026-08-03

**So `--since` works on the sitemap alone**, and one request answers it.
*`myjobsfiji.md`, the other Fijian board, stamps all 3 152 of its entries with
one rebuild date and cannot do this.* **Two boards in one country, and the
same field is load-bearing on one and worthless on the other.**

*The busiest day carries four of nine, which is 44 %. That number is not
reported as a concentration ratio: at n = 9 it is four advertisements, and a
percentage would dress a count as a rate.*

IT SHARES AN ADVERTISEMENT WITH THE OTHER FIJIAN BOARD

Its most recent posting — Ram Sami & Sons, *«Heavy PSV Driver (Class 5)/
Salesman/Driver (Class 2)/ Merchandiser (Nakasi Area)»* — is also on
`myjobsfiji`, whose slug is the same title. **The two boards are not
independent**, and the measured overlap is recorded on both cards rather than
guessed from one example.

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
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BASE = "https://ejobsfiji.com"
SITEMAP = BASE + "/sitemap.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(\d{4}-\d{2}-\d{2})", re.S)
AD_URL = re.compile(r"^https://ejobsfiji\.com/jobs/view\?id=(\d+)$")
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[ejobsfiji] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    # **Path AND query.** Every advertisement here shares `/jobs/view`; the
    # query is the identity, and a guard that dropped it would be asking about
    # a path this board never serves on its own.
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace("ejobsfiji.com", own=1.5)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-FJ,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(v):
    """**The schema's strings carry HTML entities.** `hiringOrganization.name`
    arrives as `Ram Sami &amp; Sons (Fiji) Pte Limited` — the entity survives
    JSON decoding because it was never JSON escaping, it was HTML escaping
    applied before the block was serialised. Emitting it raw puts `&amp;` into
    every employer name that contains an ampersand.
    """
    return html_mod.unescape((v or "").strip()) or None


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def entries():
    code, body = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    ads, other = [], 0
    for block in ENTRY.findall(body):
        loc = LOC.search(block)
        if not loc:
            continue
        url = loc.group(1).strip()
        m = AD_URL.match(url)
        if not m:
            other += 1
            continue
        d = LASTMOD.search(block)
        ads.append({"source": "ejobsfiji", "url": url, "id": m.group(1),
                    "ledger_id": f"ejobsfiji:{m.group(1)}",
                    "sitemap_lastmod": d.group(1) if d else None,
                    "countries": ["FJ"]})
    if not ads:
        die(f"{SITEMAP} parsed to zero advertisements from {len(body)} "
            f"characters — read the bytes before believing the zero.")
    ads.sort(key=lambda r: int(r["id"]), reverse=True)
    return ads, other


def posting_on(page):
    for block in LDJSON.findall(page):
        for strict in (True, False):
            try:
                d = json.loads(block.strip(), strict=strict)
            except ValueError:
                continue
            for it in (d if isinstance(d, list) else [d]):
                if isinstance(it, dict) and it.get("@type") == "JobPosting":
                    return it, None, "strict" if strict else "lax"
            break
    return None, "no readable JobPosting on the page", None


def card(row, post, mode):
    org = post.get("hiringOrganization") or {}
    place = post.get("jobLocation") or {}
    addr = (place.get("address") or {}) if isinstance(place, dict) else {}
    ident = post.get("identifier") or {}
    declared = (str(ident.get("value")) if isinstance(ident, dict)
                and ident.get("value") is not None else None)
    out = dict(row)
    out.update({
        "title": text(post.get("title")),
        "employer": text(org.get("name")) if isinstance(org, dict) else None,
        "city": text(addr.get("addressLocality")),
        "street": text(addr.get("streetAddress")),
        "country_name": text(addr.get("addressCountry")),
        "posted": (post.get("datePosted") or "")[:10] or None,
        "valid_through": (post.get("validThrough") or "")[:10] or None,
        "direct_apply": post.get("directApply"),
        # **The board's own number wins over the one parsed from the URL.**
        # They agreed on every advertisement measured; the field says which
        # was used so a future disagreement is visible rather than silent.
        "id_source": ("schema identifier" if declared == row["id"] else
                      f"URL query — the schema says {declared!r}"
                      if declared else "URL query — the schema states none"),
        "json_pass": mode,
    })
    return out


def cmd_list(a):
    ads, other = entries()
    note(f"{len(ads)} advertisement(s) and {other} other URL(s). "
         f"**The other {other} are company pages, blog posts and static "
         f"pages** — counting the file would report this board "
         f"{(len(ads) + other) / len(ads):.0f}× larger.")
    newest = max((r["sitemap_lastmod"] or "") for r in ads)
    note(f"most recent `lastmod`: {newest}. **This board is open and quiet**, "
         f"which is not the same as broken.")
    rows = ads
    if a.since:
        rows = [r for r in rows if r["sitemap_lastmod"]
                and r["sitemap_lastmod"] >= a.since]
        note(f"{len(rows)} of {len(ads)} dated {a.since} or later — from the "
             f"sitemap, whose dates here are real and spread over six "
             f"distinct days.")
    if a.limit:
        rows = rows[: a.limit]
    if not a.fetch:
        if a.live:
            die("`--live` needs `--fetch`: `validThrough` is in the "
                "advertisement's schema, not in the sitemap.")
        print(json.dumps({"source": "ejobsfiji", "country": "FJ",
                          "sitemap_urls": len(ads) + other,
                          "advertisements": len(ads), "other_urls": other,
                          "returned": len(rows), "ads": rows},
                         ensure_ascii=False, indent=1))
        return
    today = datetime.date.today().isoformat()
    kept, broken, dropped, lax = [], [], 0, 0
    for row in rows:
        code, page = get(row["url"])
        if code != 200:
            broken.append((row["id"], f"HTTP {code}"))
            continue
        post, why, mode = posting_on(page)
        if post is None:
            broken.append((row["id"], why))
            continue
        if mode == "lax":
            lax += 1
        c = card(row, post, mode)
        if a.live and c["valid_through"] and c["valid_through"] < today:
            dropped += 1
            continue
        if a.search and fold(a.search) not in fold(c["title"] or ""):
            continue
        kept.append(c)
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{i} ({w})" for i, w in broken[:5]))
    print(json.dumps({"source": "ejobsfiji", "country": "FJ",
                      "advertisements": len(ads), "read": len(rows),
                      "kept": len(kept), "unreadable": len(broken),
                      "filtered_out": dropped, "lax_json": lax, "ads": kept},
                     ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}/jobs/view?id={a.id}"
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.id} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    post, why, mode = posting_on(page)
    if post is None:
        die(f"{url}: {why}")
    row = {"source": "ejobsfiji", "url": url, "id": a.id,
           "ledger_id": f"ejobsfiji:{a.id}", "sitemap_lastmod": None,
           "countries": ["FJ"]}
    print(json.dumps(card(row, post, mode), ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="advertisements from the sitemap")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for title, employer and dates")
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="the sitemap's `lastmod`, which is real here — six "
                         "distinct days over nine advertisements")
    li.add_argument("--live", action="store_true",
                    help="drop advertisements whose `validThrough` has "
                         "passed. Requires --fetch")
    li.add_argument("--search", help="match the title; needs --fetch")
    li.add_argument("--limit", type=int)
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by id")
    ad.add_argument("--id", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
