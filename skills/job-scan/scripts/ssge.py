#!/usr/bin/env python3
"""Enumerate ss.ge's job board — **and refuse to read it, on purpose.**

Georgia's largest classifieds site. Its jobs section is **1 705 live
advertisements**, and this adapter finds every one of them without fetching a
single advertisement page. That is not a limitation to be worked around; it is
the shape of the site, and the reason is written below.

THREE HOSTS AND THREE DIFFERENT `robots.txt` FILES, measured 2026-09-03:

    ss.ge          478 bytes   BOM, a malformed first line, and it
                               **disallows `/en/jobs` and `/ru/jobs`**
    home.ss.ge     105 bytes   a different file — **the job refusals are not
                               in it** — declaring `ss.ge/sitemap.xml`
    jobs.ss.ge      62 bytes   `Allow: /`, declaring `ss.ge/sitemap-jobs.xml`

**The host every request is redirected to has the more permissive file.**
`shared/robots-policy.md`'s *test the apex and the `www` separately* has never
bitten this hard: these are not two files differing by a `Sitemap:` line, they
are **three files with different refusals**, and which one governs depends on
which host you end up on.

**The jobs board is a subdomain, not a prefix and not a parameter.**
`ss.ge/jobs` → `ss.ge/ka/jobs` → `jobs.ss.ge/ka/`. So `ss.ge`'s refusal of
`/en/jobs` is a refusal of a **redirect stub**, and the file that governs the
board itself says `Allow: /`.

**AND THE BOARD IS BEHIND A CLOUDFLARE CHALLENGE.** `jobs.ss.ge/ka/` answers
**403 with "Just a moment…"**, as does `home.ss.ge`. Permission is open and
the door is shut — *a `robots.txt` verdict is not an access verdict*, in the
direction that costs.

**A challenge that asks for a click is a stop.** `shared/robots-policy.md` says
so, and this file obeys it: `ad` **does not fetch**. It hands the URL to the
person, who has a browser and a click.

WHAT IS READABLE, AND IT IS MOST OF WHAT MATTERS. `jobs.ss.ge`'s `robots.txt`
declares **`https://ss.ge/sitemap-jobs.xml`** — on the apex, which is *not*
challenged, and **absent from the apex's own sitemap index**, whose 21 files
are all real estate. Reading the file for discovery found what the index
omitted (#74). It holds 56 sub-sitemaps:

    20 × /ka/ads/<n>     the advertisements — **1 705 distinct**
    20 × /en/ads/<n>     the same ads in English
    16 × sitemap-listing-<n>.xml   search-filter URLs, **not advertisements**

TWO THINGS THIS FILE WILL NOT DO:

- **It never fetches `ss.ge/en/jobs/…` or `ss.ge/ru/jobs/…`.** The apex refuses
  them by name. That the jobs sitemap advertises English files under that very
  prefix is a **conflict between two of the operator's own files**, and a
  `Sitemap:` line is not a permission: the refusal governs.
- **It never fetches `jobs.ss.ge`.** See the challenge, above.

Verified against the live site on **2026-09-03**.
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request

from _robots import verdict as robots_verdict
from _sitemap import count as sitemap_count
from _sitemap import count_says, locs as sitemap_locs

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

JOBS_SITEMAP = "https://ss.ge/sitemap-jobs.xml"
EXIT_BROKEN, EXIT_REFUSED, EXIT_PARTIAL = 2, 7, 6

AD_RE = re.compile(r"https://jobs\.ss\.ge/(?P<lang>[a-z]{2})/details/"
                   r"(?P<slug>[^\"<&]*?)-(?P<id>\d+)")
# Paths the apex refuses by name. Checked before every fetch, because a
# refusal that only exists in a comment is not a refusal.
FORBIDDEN = ("/en/jobs", "/ru/jobs")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[ss.ge] {msg}", file=sys.stderr)


def check_robots(host):
    """Ask the module, on the host that will actually be fetched.

    **This adapter hard-coded its refusals and was the argument for not doing
    that.** `ss.ge`, `home.ss.ge` and `jobs.ss.ge` publish **three different
    files**, so a verdict is only meaningful per host — which is what
    `_robots.py` now keys on, and what a constant in this file can never
    track. Issue #100.

    A `sweep: False` **stops this command**, with exit 7 and the module's own
    reason. Nothing here decides on its own what a refusal means.
    """
    v = robots_verdict(host)
    if not v["sweep"]:
        die(f"{host}: {v['reason']}", EXIT_REFUSED)
    if v.get("requested_host") and v["host"] != v["requested_host"]:
        note(f"robots.txt for {v['requested_host']} was read from "
             f"{v['host']} — on this site that difference is the whole point.")
    return v


def get(url, timeout=90):
    if any(f in url for f in FORBIDDEN):
        die(f"{url}: `ss.ge/robots.txt` disallows this path by name. **The "
            f"jobs sitemap advertises files under it anyway** — that is a "
            f"conflict between two of the operator's own files, and a "
            f"`Sitemap:` line is not a permission. Not fetched.", EXIT_REFUSED)
    if "jobs.ss.ge" in url:
        die(f"{url}: `jobs.ss.ge` answers 403 behind a Cloudflare challenge — "
            f"and its `robots.txt` says `Allow: /`, so **this stop is not a "
            f"robots verdict**. "
            f"**A challenge that asks for a click is a stop, not an "
            f"obstacle** — it belongs to the person, in their browser. Not "
            f"fetched.", EXIT_REFUSED)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/xml,text/xml,*/*;q=0.8",
        "Accept-Language": "ka-GE,ka;q=0.9,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.getcode(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def families():
    check_robots("ss.ge")
    code, body = get(JOBS_SITEMAP, timeout=45)
    if code != 200:
        die(f"{JOBS_SITEMAP}: HTTP {code}. This file is declared **only by "
            f"`jobs.ss.ge/robots.txt`** and is absent from the apex's own "
            f"sitemap index — if it has moved, read that robots.txt again "
            f"rather than guessing a name.")
    subs = sitemap_locs(body)
    if not subs:
        die(f"{JOBS_SITEMAP}: {count_says(body)}")
    return {
        "ads_ka": [u for u in subs if "/ka/ads/" in u],
        "ads_en": [u for u in subs if "/en/ads/" in u],
        "listings": [u for u in subs if "sitemap-listing-" in u],
        "all": subs,
    }


def cmd_families(a):
    f = families()
    print(json.dumps({
        "sitemap": JOBS_SITEMAP,
        "sub_sitemaps": len(f["all"]),
        "advertisement_files_ka": len(f["ads_ka"]),
        "advertisement_files_en": len(f["ads_en"]),
        "search_landing_files": len(f["listings"]),
    }, ensure_ascii=False, indent=2))
    note("the 16 `sitemap-listing-*.xml` are **search-filter URLs, not "
         "advertisements** — counting them would report a board several times "
         "its size, the arithmetic that inflated Jobstore and hr.ge.")
    # **Precisely which paths are refused, because "the English ones" was
    # wrong and read as diligence.** The apex refuses `/en/jobs` and
    # `/ru/jobs`. The English *advertisement* families are at `/en/ads/<n>`
    # and are **not** refused; the English *listing* families are at
    # `/en/jobs/sitemap-listing-N.xml` and **are**.
    refused = [u for u in f["all"] if any(x in u for x in FORBIDDEN)]
    note(f"{len(refused)} of the {len(f['all'])} sub-sitemaps sit under a "
         f"path `ss.ge/robots.txt` refuses by name — the **English listing** "
         f"families under `/en/jobs/`. The English *advertisement* families "
         f"are `/en/ads/<n>` and are not refused. Neither the refusal nor the "
         f"permission is guessed: both are read off the file.")


def cmd_sitemap(a):
    f = families()
    files = f["ads_ka"] if a.lang == "ka" else f["ads_en"]
    seen, locs_total, skipped, stopped = set(), 0, 0, False
    for u in files:
        code, body = get(u)
        if code != 200:
            note(f"{u.split('/')[-1]}: HTTP {code} — skipped.")
            continue
        text = body.decode("utf-8", "replace")
        c = sitemap_count(body)
        locs_total += c["locs"]
        found = 0
        for m in AD_RE.finditer(text):
            ident = m.group("id")
            if ident in seen:
                continue
            seen.add(ident)
            found += 1
            print(json.dumps({
                "id": ident,
                "ledger_id": f"ss.ge:{ident}",
                # The language of the family being read, not a hardcoded one.
                "url": f"https://jobs.ss.ge/{m.group('lang')}/details/"
                       f"{m.group('slug')}-{ident}",
                "slug_words": m.group("slug").replace("-", " "),
                "read_needs_browser": True,
            }, ensure_ascii=False))
            if a.limit and len(seen) >= a.limit:
                stopped = True
                break
        # **Per file, `<loc>` against distinct ids.** One family gave 134
        # `<loc>` for 103 ids and another 302 for 300: the difference is
        # duplicates and URLs with no id, and only the pair shows it.
        #
        # **Not computed once `--limit` has cut the file short**, or the
        # difference is the limit and gets reported as duplicates — a false
        # number that reads exactly like diligence. Caught by running it.
        if not stopped and c["locs"] != found:
            skipped += c["locs"] - found
        if stopped:
            break
        time.sleep(a.delay)
    if stopped:
        note(f"{len(seen)} advertisement(s) — **stopped at --limit**, so no "
             f"count of the board follows from this run.")
    else:
        note(f"{len(seen)} distinct advertisement(s) from {locs_total} "
             f"`<loc>` across {len(files)} family file(s)"
             + (f" — {skipped} URL(s) were duplicates or carried no id."
                if skipped else "."))
    note("**not one advertisement page was fetched.** `jobs.ss.ge` is behind "
         "a Cloudflare challenge; the URLs above are for the person's own "
         "browser.")


def cmd_ad(a):
    # **The refusal below is not this file's opinion, it is the module's.**
    # `jobs.ss.ge` says `Allow: /` and answers 403 behind a challenge: the
    # verdict is permissive and the door is shut, which is why the stop is
    # written separately from the check rather than folded into it.
    check_robots("jobs.ss.ge")
    m = AD_RE.search(a.url or "")
    if not m:
        die(f"{a.url!r}: not an ss.ge advertisement URL. Expected "
            f"`https://jobs.ss.ge/<lang>/details/<slug>-<id>`.")
    print(json.dumps({
        "id": m.group("id"),
        "ledger_id": f"ss.ge:{m.group('id')}",
        "url": a.url,
        "slug_words": m.group("slug").replace("-", " "),
        "title": None,
        "description": None,
        "read_needs_browser": True,
        "reason": "jobs.ss.ge answers 403 behind a Cloudflare challenge",
    }, ensure_ascii=False))
    note("**this is everything knowable without a browser, and it is not the "
         "advertisement.** `jobs.ss.ge` presents a Cloudflare challenge; a "
         "challenge that asks for a click belongs to the person, not to a "
         "script. Open the URL — the id and the slug above are enough to file "
         "it in the ledger meanwhile.")
    sys.exit(EXIT_PARTIAL)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("families", help="what the jobs sitemap declares")
    f.set_defaults(func=cmd_families)

    s = sub.add_parser("sitemap", help="every advertisement URL and id")
    s.add_argument("--lang", choices=["ka", "en"], default="ka")
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=0.4)
    s.set_defaults(func=cmd_sitemap)

    d = sub.add_parser("ad", help="what an ad URL yields without a browser")
    d.add_argument("--url", required=True)
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
