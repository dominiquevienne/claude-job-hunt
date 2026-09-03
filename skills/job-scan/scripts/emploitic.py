#!/usr/bin/env python3
"""Fetch Algerian ads from Emploitic — by the sitemap the operator declares.

Algeria's largest private job board. **No key, no cookie, no browser**: every
advertisement carries a `JobPosting` and a `__NEXT_DATA__`, and the route is
the one `robots.txt` names itself.

  GET /robots.txt          → `Sitemap: https://emploitic.com/sitemap.xml`
  GET /sitemap.xml         → three families; `sitemap-jobs.xml` is the ads
  GET /sitemap-jobs.xml    → 4 506 <loc>, every one an advertisement
  GET <ad url>             → one `JobPosting`, plus `__NEXT_DATA__`

**THE SITEMAP IS THE ROUTE HERE, AND THE NEIGHBOURING BOARD'S IS A TRAP.**
`jobivoire.ci` publishes a sitemap too and it is five weeks stale; this one is
current to the minute — newest `lastmod` **2026-09-03T20:37**, measured while
this file was written. **The two boards are read in opposite ways for reasons
measured on each**, and `jobivoire.py` carries the other half of that warning.
Do not carry the habit of one across to the other.

**BOTH URL SHAPES ARE ADVERTISEMENTS, AND THAT WAS CHECKED.** The file mixes

    /offres-d-emploi/<sector>/<slug>                          977
    /entreprises/<company>/offres-d-emploi/<sector>/<slug>   3 530

and the second shape reads like an employer landing page. **It is not**: three
sampled across the range each carry exactly one `JobPosting`. Counting only
the first shape would have reported a board a fifth of its size — the mistake
`hr.ge` records in the other direction, where 39 247 `<loc>` held 1 062 ads.

**TITLES ARE NOT ALWAYS PLAIN TEXT.** One employer publishes
`𝗧𝗲𝗰𝗵𝗻𝗶𝗰𝗼 𝗰𝗼𝗺𝗺𝗲𝗿𝗰𝗶𝗮𝗹` in mathematical-bold Unicode. The card carries the
title as published and flags it, because a keyword match against `Technico`
fails on characters that look identical to a reader.

Verified against the live site on **2026-09-03**.
"""

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _ldjson import label, one, postings, absent_reason
from _robots import allowed as robots_allowed
from _sitemap import locs as sitemap_locs
from _ua import UA
from _zero import zero_note

BASE = "https://emploitic.com"
JOBS_SITEMAP = BASE + "/sitemap-jobs.xml"
EXIT_BROKEN, EXIT_GONE, EXIT_REFUSED, EXIT_UNKNOWN = 2, 3, 7, 8
AD_PATH = re.compile(r"/offres-d-emploi/")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[emploitic] {msg}", file=sys.stderr)


def gate(url):
    """Per path — the file refuses `/partenaires/` and nothing else."""
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
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "fr-DZ,fr;q=0.9,ar;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def styled(text):
    """Is the title written in look-alike Unicode rather than letters?

    **A reader cannot tell and a keyword match can.**

    **`NFKD` is the wrong test and the first draft used it**: it decomposes
    every French accent, so `Chargé(e) Administration…` came back styled and
    the run reported *2 of 2*. A check that fires on everything is not a
    check. **`NFKC` composes the accents back and still folds the
    mathematical alphabets to ASCII**, so only the second kind changes.
    """
    if not text:
        return False
    return unicodedata.normalize("NFKC", text) != text


def card(url, posting):
    addr = one(one(posting.get("jobLocation")).get("address"))
    title = posting.get("title")
    return {
        "id": url.rstrip("/").rsplit("/", 1)[-1],
        "ledger_id": f"emploitic:{url.rstrip('/').rsplit('/', 1)[-1]}",
        "url": url,
        "title": title,
        "title_is_styled_unicode": styled(title),
        "company": label(posting.get("hiringOrganization")),
        "location_text": addr.get("addressLocality"),
        "region": addr.get("addressRegion"),
        "country": addr.get("addressCountry"),
        "employment_type": posting.get("employmentType"),
        "posted": posting.get("datePosted"),
        "valid_through": posting.get("validThrough"),
        "description_chars": len(posting.get("description") or ""),
    }


def read_ad(url, with_text=False):
    code, raw = get(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE)
    page = decode_body(raw, None)[0]
    found = postings(page)
    if not found:
        why = absent_reason(page)
        die(f"{url}: {why.text}",
            EXIT_BROKEN if why.our_fault else EXIT_GONE)
    row = card(url, found[0])
    if with_text:
        row["description"] = found[0].get("description")
    return row


def cmd_sitemap(a):
    code, raw = get(JOBS_SITEMAP)
    if code != 200:
        die(f"{JOBS_SITEMAP}: HTTP {code}")
    urls = [u for u in sitemap_locs(raw) if AD_PATH.search(u)]
    direct = sum(1 for u in urls if "/entreprises/" not in u)
    note(f"{len(urls)} advertisement URL(s): {direct} under "
         f"`/offres-d-emploi/` and {len(urls) - direct} under "
         f"`/entreprises/<company>/offres-d-emploi/`. **Both shapes are "
         f"advertisements** — three of the second were opened across the "
         f"range and each carried one `JobPosting`. Counting only the first "
         f"would report a board a fifth of its size.")
    for u in urls[:a.limit] if a.limit else urls:
        print(json.dumps({"url": u}, ensure_ascii=False))


def cmd_search(a):
    code, raw = get(JOBS_SITEMAP)
    if code != 200:
        die(f"{JOBS_SITEMAP}: HTTP {code}")
    urls = [u for u in sitemap_locs(raw) if AD_PATH.search(u)]
    if not urls:
        note(zero_note("emploitic"))
        return
    kept, styled_titles = 0, 0
    for u in urls[:a.limit] if a.limit else urls:
        row = read_ad(u, a.with_text)
        print(json.dumps(row, ensure_ascii=False))
        kept += 1
        styled_titles += bool(row["title_is_styled_unicode"])
        time.sleep(a.delay)
    note(f"{kept} advertisement(s) of {len(urls)} in the declared sitemap — "
         f"one request each, because the sitemap carries URLs and the fields "
         f"live on the page.")
    if styled_titles:
        note(f"{styled_titles} of {kept} title(s) are written in look-alike "
             f"Unicode rather than letters. **A reader cannot tell and a "
             f"keyword match can** — they are emitted as published and "
             f"flagged, never normalised in place.")


def cmd_ad(a):
    print(json.dumps(read_ad(a.url, a.with_text), ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("sitemap", help="advertisement URLs, one request")
    m.add_argument("--limit", type=int)
    m.set_defaults(func=cmd_sitemap)

    s = sub.add_parser("search", help="read advertisements from the sitemap")
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=0.8)
    s.add_argument("--with-text", action="store_true", dest="with_text")
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="read one advertisement by URL")
    d.add_argument("--url", required=True)
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
