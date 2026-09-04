#!/usr/bin/env python3
"""Jobs Botswana (`jobsbotswana.info`).

  jobsbotswana.py list [--since 2026-08-05] [--limit 20] [--live] [--fetch]
  jobsbotswana.py ad --slug workshop-manager-bango-trading

**367 advertisements, and the sitemap holds 368.** The extra entry is
`/jobs/` — the listing page itself, sitting among the advertisements. Counting
the file length reports the board one larger than it is, which is small here
and was 183-against-180 on `caglobalint.com` and 32-against-30 on `onape.td`
the same night. **Three boards, three different ways of not being their own
file length.**

WordPress with the Noo Jobmonster theme: `/sitemap_index.xml` declares sixteen
children and `noo_job-sitemap.xml` is the only one of advertisements. The other
fifteen are two of companies, one of products, four of taxonomies, and the
rest pages and posts.

WHAT WAS MEASURED, 2026-09-05

    noo_job-sitemap.xml   368 <loc>, 368 distinct, 367 advertisements
    dates                 31 distinct, 2025-12-10 → 2026-09-04
                          357 of 367 dated within thirty days

**`lastmod` equals `datePosted` on ten of ten checked**, so the sitemap's date
is the posting date and not a regeneration stamp. That had to be checked:
`myjobsfiji.com` gave every one of its 3 187 entries the same `lastmod`, and a
freshness count taken from it would have been a count of one afternoon's
rebuild.

**Expired advertisements stay in the file.** Of the ten oldest, five have a
`validThrough` in the past. `--live` filters on it; without the flag everything
is returned and `valid_through` travels with each row.

THE EMPLOYER IS USUALLY REAL AND SOMETIMES THE SITE

`hiringOrganization.name` reads `Jobs Botswana` — the site itself — on **2 of a
random 20**. The other 18 name a genuine employer.

**The rate came out at 62 % on the first sample and 10 % on the second**, and
the difference is the sampling: the first was the last eight entries of the
file, which are one poster's batch of trade vacancies. **A contiguous slice
from one end of a sorted file is not a sample**, and this adapter's figures
come from `random.sample`.

The site's own name is emitted as written with `employer_is_site: true`, never
as `None`: *"the board did not name an employer"* and *"we could not find one"*
are different facts.

FIELDS, ON TWENTY ADVERTISEMENTS

    title · employer · datePosted · validThrough · jobLocation   20/20
    employmentType    FULL_TIME 18, CONTRACTOR 2 — real, and emitted
    baseSalary        0/12 — never present
    industry          10/12, and it mixes sectors with job titles
                      ("Construction", but also "Driver", "Sales Manager")

**`employmentType` is emitted here and is not on `keejob.py`**, where it reads
`OTHER` on every advertisement. Same field, same schema, opposite worth: **what
a field is worth is a property of the board, not of the vocabulary.**

`industry` is not emitted. A field that holds a sector on one row and a job
title on the next cannot be filtered on, and passing it through would invite
exactly that.

Verified against the live site on **2026-09-05**.
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
from _robots import allowed as robots_allowed
from _ua import UA

BASE = "https://jobsbotswana.info"
SITEMAP = BASE + "/noo_job-sitemap.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobsbotswana] {msg}", file=sys.stderr)


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
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-GB,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def slug_of(url):
    return url.rstrip("/").rsplit("/", 1)[-1]


def entries():
    """Advertisements only — the bare `/jobs/` listing page is not one."""
    code, body = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    rows, raw, seen = [], 0, set()
    for block in ENTRY.findall(body):
        loc = LOC.search(block)
        if not loc:
            continue
        raw += 1
        u = html_mod.unescape(loc.group(1).strip())
        if u.rstrip("/").endswith("/jobs") or u in seen:
            continue
        seen.add(u)
        d = LASTMOD.search(block)
        rows.append((u, d.group(1) if d else None))
    if not rows:
        die(f"{SITEMAP} parsed to zero advertisements from {len(body)} "
            f"characters — read the bytes before believing the zero.")
    # **Newest first, because the file is oldest first.** Left as served,
    # `--limit 4` returned the four oldest advertisements — all four expired,
    # so `--limit 4 --live` returned nothing at all and looked like a broken
    # board. A default that makes the common request return the wrong end is a
    # defect even when every row is correct.
    rows.sort(key=lambda r: (r[1] or ""), reverse=True)
    return rows, raw


def posting_on(page):
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
    org = posting.get("hiringOrganization") or {}
    name = (org.get("name") or "").strip() if isinstance(org, dict) else ""
    place = posting.get("jobLocation") or {}
    addr = (place.get("address") or {}) if isinstance(place, dict) else {}
    return {
        "source": "jobsbotswana",
        "url": url,
        "slug": slug_of(url),
        "title": html_mod.unescape(posting.get("title") or "").strip() or None,
        "employer": name or None,
        # **The site's own name, not a missing value.** `None` would merge
        # "the board named no employer" with "we could not find one".
        "employer_is_site": name.lower() == "jobs botswana",
        "city": (addr.get("addressLocality") or "").strip() or None,
        "country_code": (addr.get("addressCountry") or "").strip() or None,
        "employment_type": posting.get("employmentType") or None,
        "posted": (posting.get("datePosted") or "")[:10] or lastmod,
        "valid_through": (posting.get("validThrough") or "")[:10] or None,
        "countries": ["BW"],
    }
    # `industry` is deliberately absent: it holds a sector on one row and a job
    # title on the next, so it cannot be filtered on.


def cmd_list(a):
    rows, raw = entries()
    note(f"{raw} <loc> in the sitemap, {len(rows)} advertisements — the "
         f"difference is the `/jobs/` listing page, which is not one.")
    if a.since:
        rows = [r for r in rows if r[1] and r[1] >= a.since]
        note(f"{len(rows)} posted {a.since} or later")
    if a.limit:
        rows = rows[: a.limit]
    if not a.fetch and not a.search and not a.live:
        print(json.dumps({"source": "jobsbotswana", "country": "BW",
                          "sitemap_entries": raw, "advertisements": len(rows),
                          "ads": [{"url": u, "slug": slug_of(u), "posted": d}
                                  for u, d in rows]},
                         ensure_ascii=False, indent=1))
        return
    today = datetime.date.today().isoformat()
    kept, broken, expired = [], [], 0
    needle = fold(a.search) if a.search else None
    for u, d in rows:
        code, page = get(u)
        if code != 200:
            broken.append((u, f"HTTP {code}"))
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
    if a.live:
        note(f"{expired} advertisement(s) dropped: `validThrough` is past. "
             f"They remain in the sitemap.")
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{slug_of(u)} ({w})" for u, w in broken[:5]))
    print(json.dumps({"source": "jobsbotswana", "country": "BW",
                      "sitemap_entries": raw, "read": len(kept) + len(broken),
                      "kept": len(kept), "unreadable": len(broken),
                      "expired_dropped": expired if a.live else None,
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}/jobs/{a.slug}/"
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.slug} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
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
    li.add_argument("--since", metavar="YYYY-MM-DD")
    li.add_argument("--limit", type=int)
    li.add_argument("--search", help="match the title; folds accents")
    li.add_argument("--live", action="store_true",
                    help="drop advertisements whose `validThrough` has passed "
                         "— five of the ten oldest have")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for its fields; without it the listing "
                         "is the sitemap alone — one request instead of 367")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
