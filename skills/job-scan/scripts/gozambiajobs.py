#!/usr/bin/env python3
"""Go Zambia Jobs — Zambia's first board in this repository.

    gozambiajobs.py list [--fetch] [--since YYYY-MM-DD] [--live] [--limit N]
    gozambiajobs.py ad --slug 516181873-sales-operations-supervisor

TWO HOSTS, AND THE SECOND IS NOT THE FIRST

The sitemap index is served from `www.gozambiajobs.com`; **all forty-one of its
entries point at the bare apex `gozambiajobs.com`.** A verdict taken at `www`
covers nothing on the apex, so `gate()` is called on each URL as it is used,
host included — never once at the root. `merojob.com` declares its sitemaps on
`sg.merojob.com`, and this is the same shape one host closer to home.

THE SITEMAP CARRIES NO DATES AT ALL

**Not one `<lastmod>` in 368 entries** (2026-09-05). So `--since` cannot be
answered from the listing, and this adapter does not pretend otherwise: it
**refuses** unless `--fetch` is given, because the alternative is a filter that
silently returns everything or nothing.

`datePosted` and `validThrough` do exist — in the page's `ld+json`, one request
per advertisement. That is what `--fetch` buys, and it is why the flag is not
free: 368 requests instead of one.

WHAT A PAGE CARRIES, MEASURED RATHER THAN ASSUMED

Read on 2026-09-05 before this file was written:

    @type JobPosting · title · datePosted · validThrough · employmentType
    hiringOrganization {name, sameAs} · jobLocation {Place → PostalAddress}
    description · baseSalary ABSENT

`employmentType` is the schema.org enumeration here — `FULL_TIME` — so it is
emitted as `employment_type`. **That is the fourth verdict on this field in two
days**: dropped on `keejob` (absent), emitted on `jobsbotswana` (enumeration),
renamed `employment_type_text` on `job.am` (free-text Armenian). *The field name
records which of the four this board is, so a later reader does not have to
guess.*

WHAT IT DOES NOT DO

**It writes nothing to disk.** No adapter in this repository does — bodies are
fetched, parsed and emitted. Provenance for one-off retrievals belongs to
`bin/fetch-body.py`, not here.
"""

import argparse
import datetime
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

INDEX = "https://www.gozambiajobs.com/sitemap.xml"
APEX = "https://gozambiajobs.com"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN, EXIT_USAGE = 7, 8, 9

LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[gozambiajobs] {msg}", file=sys.stderr)


def gate(url):
    """Ask on the exact URL, host included. The index and its entries differ."""
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


def slug_of(url):
    return url.rstrip("/").rsplit("/", 1)[-1]


def jobs_sitemap():
    """The index names its children; the jobs file is one of forty-one."""
    code, body = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}")
    children = [u.strip() for u in LOC.findall(body)]
    jobs = [u for u in children if "sitemap-jobs" in u]
    if not jobs:
        die(f"{INDEX} declares {len(children)} children and none is a jobs "
            f"sitemap. The index changed shape; do not guess a path.")
    return jobs


def entries():
    urls, seen = [], set()
    for sm in jobs_sitemap():
        code, body = get(sm)
        if code != 200:
            die(f"{sm}: HTTP {code}")
        for u in LOC.findall(body):
            u = u.strip()
            # A count of <loc> is not a count of advertisements: the index also
            # serves companies, blog, tags and locations. Only /jobs/ is one.
            if "/jobs/" not in u or u in seen:
                continue
            seen.add(u)
            urls.append(u)
    return urls


def posting_on(page):
    for block in LDJSON.findall(page):
        try:
            data = json.loads(block, strict=False)
        except ValueError:
            # A publisher that HTML-escapes an apostrophe after JSON-escaping it
            # breaks the block. Say so rather than counting the page as empty.
            return None, "ld+json present and unparseable"
        for obj in (data if isinstance(data, list) else [data]):
            if isinstance(obj, dict) and obj.get("@type") == "JobPosting":
                return obj, None
    return None, "no JobPosting in ld+json"


def text(v):
    if isinstance(v, dict):
        return v.get("name") or v.get("value")
    return v


def place(v):
    one = v[0] if isinstance(v, list) and v else v
    addr = (one or {}).get("address") if isinstance(one, dict) else None
    if not isinstance(addr, dict):
        return None, None
    return (addr.get("addressLocality") or addr.get("addressRegion"),
            addr.get("addressCountry"))


def card(url, posting):
    town, country = place(posting.get("jobLocation"))
    org = posting.get("hiringOrganization") or {}
    return {
        "id": "gozambiajobs:" + slug_of(url),
        "url": url,
        "title": html_mod.unescape(posting.get("title") or "").strip(),
        "employer": text(org),
        "employer_site": org.get("sameAs") if isinstance(org, dict) else None,
        "town": town,
        "country": country,
        "posted": (posting.get("datePosted") or "")[:10] or None,
        "valid_through": (posting.get("validThrough") or "")[:10] or None,
        # schema.org enumeration on this board — see the module docstring.
        "employment_type": posting.get("employmentType"),
    }


def cmd_list(a):
    if a.since and not a.fetch:
        die("--since needs --fetch on this board: the sitemap carries no "
            "<lastmod> at all, so a date filter has nothing to read. "
            "With --fetch the date comes from each page's ld+json, at one "
            "request per advertisement.", EXIT_USAGE)
    if a.live and not a.fetch:
        die("--live needs --fetch: `validThrough` lives on the page.",
            EXIT_USAGE)

    urls = entries()
    raw = len(urls)
    if a.limit:
        urls = urls[:a.limit]

    if not a.fetch:
        note(f"{raw} advertisement(s) in the sitemap, listed without opening "
             f"them: one request instead of {raw}. No dates exist at this "
             f"level — the sitemap has no <lastmod>.")
        print(json.dumps({"source": "gozambiajobs", "country": "ZM",
                          "sitemap_entries": raw, "fetched": False,
                          "ads": [{"id": "gozambiajobs:" + slug_of(u),
                                   "url": u} for u in urls]},
                         ensure_ascii=False, indent=1))
        return

    today = datetime.date.today().isoformat()
    kept, broken, expired = [], [], 0
    for u in urls:
        code, page = get(u)
        if code != 200:
            broken.append((u, f"HTTP {code}"))
            continue
        posting, why = posting_on(page)
        if posting is None:
            broken.append((u, why))
            continue
        c = card(u, posting)
        if a.since and (c["posted"] or "") < a.since:
            continue
        if a.live and c["valid_through"] and c["valid_through"] < today:
            expired += 1
            continue
        kept.append(c)

    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{slug_of(u)} ({w})" for u, w in broken[:5]))
    if a.live:
        note(f"{expired} dropped: `validThrough` is past. They remain in the "
             f"sitemap.")
    print(json.dumps({"source": "gozambiajobs", "country": "ZM",
                      "sitemap_entries": raw, "read": len(kept) + len(broken),
                      "kept": len(kept), "unreadable": len(broken),
                      "expired_dropped": expired if a.live else None,
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{APEX}/jobs/{a.slug}"
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.slug} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    posting, why = posting_on(page)
    if posting is None:
        die(f"{url}: {why}")
    print(json.dumps(card(url, posting), ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="advertisements from the sitemap")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for its fields; without it the listing "
                         "is the sitemap alone, and carries no dates")
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="needs --fetch: the sitemap has no <lastmod>")
    li.add_argument("--live", action="store_true",
                    help="needs --fetch: drop advertisements whose "
                         "`validThrough` has passed")
    li.add_argument("--limit", type=int)
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
