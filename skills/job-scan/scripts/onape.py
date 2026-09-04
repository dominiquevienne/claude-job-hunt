#!/usr/bin/env python3
"""ONAPE — Chad's Office National pour la Promotion de l'Emploi (`onape.td`).

  onape.py list [--search mécanicien] [--pages 1]
  onape.py ad   --slug un-une-aide-mecanicienne-3 [--text]

**A public employment service, WordPress, and it names its own files.** The
index at `/wp-sitemap.xml` separates `job_listing` from `company`,
`testimonial`, `tribe_venue` and the taxonomies — so the advertisements are
reachable without guessing and without counting anything else. Measured
2026-09-04: **30 advertisements**, `2026-07-18` → `2026-09-04`, 31 of the
entries dated inside the last thirty days.

**THIRTY, NOT THIRTY-TWO, AND THE DIFFERENCE IS THE POINT.** The sitemap holds
**32 `<loc>` for 30 distinct URLs** — one advertisement is listed three times.
A count taken off the file length would be wrong by two, and wrong in the
direction that flatters. `_seen` deduplicates and `list` reports both numbers,
because *the gap between them is a property of the site* and hiding it would
make the next reader recompute it.

WHAT THE ADVERTISEMENTS CARRY, MEASURED ON EIGHT OF THEM

Each page holds exactly one well-formed `ld+json` `JobPosting` — `datePosted`,
`validThrough`, `title`, `description`, `jobLocation`, `identifier`.

**`hiringOrganization.name` is empty on eight of eight.** Not missing, not
sometimes blank: present as a key with an empty string, every time. So this
adapter **does not emit an employer it does not have** — the field is `None`
and the card says why, rather than inventing "ONAPE" as the employer of a job
ONAPE only publishes.

**`jobLocation.address` is a plain string, not a `PostalAddress`.** It reads
`"Ouaddai, Abéché"` or `"Ouaddai, Abéché, Farch"` — region first, then city,
sometimes a village. Split on commas; do not expect `addressLocality`.

**`validThrough` is usually real and sometimes not.** Seven of eight fall a few
days after `datePosted`; one reads `2032-11-23`, six years out. It is reported
as it stands and never used to decide whether an advertisement is live.

**`description` is HTML escaped twice** — the block carries `&lt;p&gt;`, so one
unescape yields markup and the second yields text.

Verified against the live site on **2026-09-04**.
"""

import argparse
import html as html_mod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _robots import allowed as robots_allowed
from _ua import UA

BASE = "https://onape.td"
SITEMAP = BASE + "/wp-sitemap-posts-job_listing-1.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

LOC = re.compile(r"<loc>([^<]+)</loc>")
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[onape] {msg}", file=sys.stderr)


def gate(url):
    """Ask about **this path**, not about the host.

    `onape.td` sweeps, so a host-level verdict would answer yes to everything —
    which is exactly how `vieclam24h.py` came to fetch the one path its host
    refused (#156).
    """
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
        "Accept-Language": "fr-TD,fr;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def ad_urls():
    """Every advertisement URL, **deduplicated, with both counts reported.**"""
    code, body = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    raw = LOC.findall(body)
    if not raw:
        die(f"{SITEMAP} parsed to zero <loc> from {len(body)} characters — "
            f"the file shape changed, or something other than a sitemap came "
            f"back. Read the bytes before believing the zero.")
    seen, out = set(), []
    for u in raw:
        u = html_mod.unescape(u.strip())
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out, len(raw)


def slug_of(url):
    return url.rstrip("/").rsplit("/", 1)[-1]


def posting_on(page):
    """The one `JobPosting` block, or None with a reason the caller reports."""
    blocks = LDJSON.findall(page)
    for b in blocks:
        try:
            d = json.loads(b.strip())
        except ValueError:
            continue
        for cand in (d if isinstance(d, list) else [d]):
            if isinstance(cand, dict) and cand.get("@type") == "JobPosting":
                return cand, None
    return None, (f"no parseable JobPosting in {len(blocks)} ld+json block(s)")


def text_of(markup):
    """`description` is escaped twice: one pass yields markup, two yield text."""
    once = html_mod.unescape(markup or "")
    stripped = re.sub(r"<[^>]+>", " ", once)
    return re.sub(r"\s+", " ", html_mod.unescape(stripped)).strip()


def card(url, posting, with_text=False):
    place = posting.get("jobLocation") or {}
    address = place.get("address") if isinstance(place, dict) else None
    parts = [p.strip() for p in str(address or "").split(",") if p.strip()]
    org = (posting.get("hiringOrganization") or {})
    name = (org.get("name") or "").strip() if isinstance(org, dict) else ""
    out = {
        "source": "onape",
        "url": url,
        "slug": slug_of(url),
        "title": html_mod.unescape(posting.get("title") or "").strip(),
        # **Empty on eight of eight measured advertisements.** Reported as
        # `None` rather than filled with the publisher's own name: ONAPE
        # publishes these, it does not employ for them.
        "employer": name or None,
        "employer_absent": not name,
        "region": parts[0] if parts else None,
        "city": parts[1] if len(parts) > 1 else None,
        "location_raw": address or None,
        "posted": (posting.get("datePosted") or "")[:10] or None,
        # Reported, never used to decide whether an advertisement is live: one
        # of eight reads 2032.
        "valid_through": (posting.get("validThrough") or "")[:10] or None,
        "countries": ["TD"],
    }
    if with_text:
        out["description"] = text_of(posting.get("description"))
    return out


def cmd_list(a):
    urls, raw_count = ad_urls()
    if a.search:
        needle = a.search.lower()
    kept, broken = [], []
    for url in urls[: a.limit] if a.limit else urls:
        code, page = get(url)
        if code in (404, 410):
            broken.append((url, f"HTTP {code}"))
            continue
        if code != 200:
            broken.append((url, f"HTTP {code}"))
            continue
        posting, why = posting_on(page)
        if posting is None:
            broken.append((url, why))
            continue
        c = card(url, posting, with_text=a.text)
        if a.search and needle not in (c["title"] or "").lower():
            continue
        kept.append(c)
    note(f"{raw_count} <loc> in the sitemap, {len(urls)} distinct — "
         f"{raw_count - len(urls)} duplicate entr"
         f"{'y' if raw_count - len(urls) == 1 else 'ies'}. "
         f"**The distinct count is the board's size.**")
    if broken:
        note(f"{len(broken)} advertisement(s) did not yield a JobPosting: "
             + "; ".join(f"{slug_of(u)} ({w})" for u, w in broken[:5]))
    print(json.dumps({"source": "onape", "country": "TD",
                      "sitemap_entries": raw_count, "distinct": len(urls),
                      "read": len(kept) + len(broken), "kept": len(kept),
                      "unreadable": len(broken), "ads": kept},
                     ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}/poste/{a.slug}/"
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.slug} is gone (HTTP {code}) — expired or withdrawn. Record it "
            f"as discarded, do not retry.", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    posting, why = posting_on(page)
    if posting is None:
        die(f"{url}: {why}")
    print(json.dumps(card(url, posting, with_text=a.text),
                     ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="every advertisement, deduplicated")
    li.add_argument("--search", help="filter on the title, locally")
    li.add_argument("--limit", type=int, help="stop after N advertisements")
    li.add_argument("--text", action="store_true", help="include descriptions")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True)
    ad.add_argument("--text", action="store_true")
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
