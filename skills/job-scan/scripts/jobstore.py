#!/usr/bin/env python3
"""Discover Jobstore ads over plain HTTP — the half that does not need a
browser.

Jobstore runs 26 country sites off one host, `www.jobstore.com/<cc>/`, and
this adapter is **hybrid by necessity**: discovery is plain HTTP, **reading an
ad needs the user's Chrome**, because the ad page answers a plain client with
**HTTP 403 and a 5 832-byte "Just a moment…" interstitial** while the search
page and the sitemaps answer 200.

  GET /<cc>/sitemap/sitemap_index.xml        → 200 application/xml
  GET /<cc>/sitemap/job-<n>.xml              → 200, ONE AD PER <loc>
  GET /<cc>/jobs/search?q=&l=&page=          → 200, an ItemList of ad URLs
  GET /<cc>/job/l<id>/<slug>-job             → **403 to a plain client**

COUNT `job-*.xml` AND NOTHING ELSE. The Swiss index declares twelve
sub-sitemaps and only six of them are ads:

    job-1..6.xml            52 128 <loc>   ← the ads
    jobs-search-1..4.xml   ~200 000 <loc>  ← query landing pages
    employer-1.xml           3 876
    salary-1.xml             1 984

Summing every `<loc>` reports **more than 250 000 Swiss ads where there are
52 128**. Nothing errors, nothing warns, and the number is five times too
large — the one mistake here that produces a confident wrong figure. This
script reads `job-*.xml` only and says so.

WHAT THE HTTP HALF CAN AND CANNOT SEE. The search page's `ld+json` is an
`ItemList` of **URLs only** — no title, no employer, no location, no salary.
The ad id and a slug are all that plain HTTP yields, so the card here carries
`id`, `url` and a `title_from_slug` **named for what it is**: a guess derived
from a URL, not the board's own title.

APPLYING IS NOT WHAT THE BUTTON SAYS. The ad page shows **"Apply on company
site"**, twice. Its `href` is
`https://www.jobstore.com/jobseeker/apply/l<id>` — **a Jobstore path**, and
`robots.txt` disallows `/*/jobseeker/apply/`. Applying needs a Jobstore
account. Read from the DOM, not by clicking. **The plugin says so plainly
rather than repeating the label.**

Verified against the Swiss site on **2026-09-02**.
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _robots import allowed as robots_allowed

BASE = "https://www.jobstore.com"
from _ua import UA, browser_fallback

# The 26 country sites declared in robots.txt.
COUNTRIES = ("my", "sg", "id", "ph", "hk", "au", "nz", "th", "vn", "us", "uk",
             "nl", "es", "ae", "in", "ca", "za", "ie", "ch", "no", "dk", "at",
             "se", "pt", "pl", "il")

# The one reader — `_sitemap.py`. The pattern that used to live here
# missed CDATA-wrapped and namespace-prefixed `<loc>`, which is issue
# #55's fault repeated: it was fixed in four adapters by pasting, and
# five kept the naive form until 2026-09-03.
from _sitemap import locs as sitemap_locs
AD = re.compile(r"/(?P<cc>[a-z]{2})/job/(?P<id>l\d+)/(?P<slug>[^/\"?#]+)")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def _robots_gate(url, tag, exit_code=7):
    """Ask before fetching — per host and **per path**. Issues #100, #101.

    `verdict()` answers *is this host closed in one block*. **A site that
    refuses its ad path while leaving its root open passes that and refuses
    every advertisement** — `empleate.gob.hn` does exactly that, closing
    `/Vacantes/` to `User-agent: *` with `/` absent.

    It sits **inside the fetch function**, so every request is covered rather
    than the first one, and a refusal **stops the command** with exit 7 and the
    module's own words. **This adapter decides nothing about what a refusal
    means** — deciding is what turns a check into a decoration.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return None
    a = robots_allowed(parts.netloc, parts.path or "/")
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", exit_code)
    if a.get("requested_host") and a["host"] != a["requested_host"]:
        # **The tag, not a name copied with the function.** Twelve
        # adapters printed `[hellowork]` here, so a cross-host redirect on
        # `stepstone.de` or `hays.fr` announced itself as another board.
        print(f"[{tag}] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts. A platform that has "
              f"been renamed reaches an adapter this way before it reaches it "
              f"as a rename.", file=__import__("sys").stderr)
    return a



def note(msg):
    print(f"[jobstore] {msg}", file=sys.stderr)


def get(path):
    _robots_gate(BASE + path if not path.startswith("http") else path, 'jobstore')
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html,application/xml",
        "Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.headers.get("Content-Type", ""), r.read().decode(
                "utf-8", "replace")
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            # This adapter wrote the right sentence by hand before there was
            # a shared one. Same meaning, one voice, one exit code — and the
            # helper refuses to fire unless the guard actually permitted.
            die(*browser_fallback("www.jobstore.com", True, exc.code, url))
        die(f"{url}: HTTP {exc.code}")
    except (urllib.error.URLError, OSError) as exc:
        die(f"{url}: {exc}")


def title_from_slug(slug):
    slug = re.sub(r"-job$", "", slug)
    return slug.replace("-", " ").strip().title() or None


def card(cc, url):
    m = AD.search(url)
    if not m:
        return None
    return {
        "id": m.group("id"),
        "ledger_id": f"jobstore:{cc}:{m.group('id')}",
        # **A Jobstore URL, and the file says so.** It is not the employer's
        # posting and must never be handed over as one.
        "url": f"{BASE}/{cc}/job/{m.group('id')}/{m.group('slug')}",
        "url_is_jobstore": True,
        "country": cc,
        # Derived from the URL slug, not read from the board. Plain HTTP sees
        # no title here.
        "title_from_slug": title_from_slug(m.group("slug")),
        "needs_browser_to_read": True,
    }


def cmd_count(a):
    ctype, body = get(f"/{a.country}/sitemap/sitemap_index.xml")
    if "xml" not in ctype:
        die(f"the sitemap index answered {ctype!r} rather than XML — a "
            f"sitemap that is not XML is not a sitemap.")
    files = sitemap_locs(body)
    ads = [f for f in files if re.search(r"/job-\d+\.xml$", f)]
    other = [f for f in files if f not in ads]
    note(f"{len(files)} sub-sitemaps declared; {len(ads)} carry ads. The "
         f"others are landing pages, employers and salary pages: "
         f"{', '.join(f.rsplit('/', 1)[-1] for f in other)}")
    total = 0
    for f in ads:
        _, xml = get(f[len(BASE):])
        n = len(sitemap_locs(xml))
        total += n
        note(f"  {f.rsplit('/', 1)[-1]}: {n}")
        time.sleep(a.delay)
    print(json.dumps({"country": a.country, "ad_sitemaps": len(ads),
                      "ads": total,
                      "note": "job-*.xml only; jobs-search-*.xml are query "
                              "landing pages and counting them inflates this "
                              "figure about fivefold"}, ensure_ascii=False))


def cmd_search(a):
    seen, kept = set(), 0
    for page in range(1, a.pages + 1):
        q = f"?q={a.keyword or ''}&l={a.location or ''}"
        if page > 1:
            q += f"&page={page}"
        ctype, body = get(f"/{a.country}/jobs/search{q}")
        urls = list(sitemap_locs(body)) or re.findall(
            r'"url"\s*:\s*"([^"]+/job/l\d+/[^"]+)"', body)
        if not urls:
            note(f"page {page}: no ad URL in the ItemList — stopping.")
            break
        for u in urls:
            c = card(a.country, u)
            if not c or c["id"] in seen:
                continue
            seen.add(c["id"])
            print(json.dumps(c, ensure_ascii=False))
            kept += 1
            if a.limit and kept >= a.limit:
                break
        if a.limit and kept >= a.limit:
            break
        time.sleep(a.delay)
    note(f"{kept} ad URLs discovered. **Titles here are derived from the URL "
         f"slug**, and everything else — employer, location, salary, the ad "
         f"text — needs the browser: the ad page answers a plain client with "
         f"403 and an interstitial.")
    note("applying needs a Jobstore account. The button says 'Apply on "
         "company site' and links to /jobseeker/apply/<id> on jobstore.com.")


def cmd_corpus(a):
    """Every ad URL for a country, from job-*.xml. One request per 10 000."""
    ctype, body = get(f"/{a.country}/sitemap/sitemap_index.xml")
    ads = [f for f in sitemap_locs(body) if re.search(r"/job-\d+\.xml$", f)]
    kept = 0
    for f in ads:
        _, xml = get(f[len(BASE):])
        for u in sitemap_locs(xml):
            c = card(a.country, u)
            if not c:
                continue
            print(json.dumps(c, ensure_ascii=False))
            kept += 1
            if a.limit and kept >= a.limit:
                note(f"{kept} ad URLs (limit reached).")
                return
        time.sleep(a.delay)
    note(f"{kept} ad URLs from {len(ads)} job-*.xml file(s).")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, h in (("count", cmd_count, "how many ads the country has"),
                        ("search", cmd_search, "discover ad URLs by keyword"),
                        ("corpus", cmd_corpus, "every ad URL, from job-*.xml")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--country", required=True, choices=COUNTRIES)
        c.add_argument("--delay", type=float, default=1.5)
        if name == "search":
            c.add_argument("--keyword")
            c.add_argument("--location")
            c.add_argument("--pages", type=int, default=1)
        if name in ("search", "corpus"):
            c.add_argument("--limit", type=int)
        c.set_defaults(func=fn)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
