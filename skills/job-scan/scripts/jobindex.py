#!/usr/bin/env python3
"""Jobindex (`www.jobindex.dk`) — Denmark's first adapter, and the board is
read on page 1 only, because its own rules refuse the second.

    jobindex.py search --q udvikler [--area <slug>] [--with-text] [--limit N]
    jobindex.py ad --id h1697049

WHAT THE HOST IS — measured 2026-09-11, 13:22–13:27 UTC

**Two hosts, two rules files, and only one of them is ours to read.** The
apex `jobindex.dk` publishes 47 bytes — `User-agent: * / Disallow: /` — and
the guard refuses even its `robots.txt`. `www.jobindex.dk` publishes 4 218
bytes of detailed rules (md5 `a386fea74e6744fec2a68f0a69c43815`, stable across
two reads). Every URL this adapter builds is on `www`, and the guard is asked
on each, inside `get()`.

**The written rules bound the sweep, not the site's size.** The `*` group on
`www` refuses `/jobsoegning*page=`, `*sort=`, `*jobage=`, `/jobsoegning?*&*&`
(two query parameters), `/api/` and `/job/*?`. So a search is ONE page of 20
with ONE parameter, and the second page is a written refusal — bound 1 of the
07.09 doctrine, honoured by every route, browser included. This adapter never
asks for it, and it says so beside every count.

**The sitemaps carry no advertisement — 7 181 `<loc>`, zero ads.**
`/sitemap.gz` (283 bytes gzip, magic `1f8b`, 906 decompressed) names five
children, all permitted: `googleforjobs.gz` is an honest empty `<urlset …/>`
(0 `<url>`), `company.gz` 3 915 employer pages, `content.gz` 1 508 CMS pages,
`area.gz` 759 `/jobsoegning/<area>` search pages, `salaryindex.gz` 999. A
count of `<loc>` here is a count of pages about jobs, never of jobs
(memory: compte-de-loc-nest-pas-compte-dannonces).

**Where the data is: a JSON the search page embeds.** `var Stash = {…}` in
the first `<script>`, under `jobsearch/result_app.storeData.searchResponse`:
`hitcount` (the board's own total for the query), `page_size` 20,
`total_pages`, and `results`, twenty objects each carrying `tid` (the stable
id — `h1697049`, `o41080`), `headline`, `companytext`, `area`, `firstdate`,
`lastdate`, `apply_deadline`, `share_url` (`/vis-job/<tid>`), `is_archived`.
**The RSS the page declares (`/jobsoegning.rss?q=…`) lists the same 20**
— a second branch, and it is capped the same way.

**And the ad has two pages.** `/vis-job/<tid>` is the canonical one the
site shares — a teaser with the company block and no `JobPosting` (0
`ld+json` of that type on 2026-09-11). The full text is at
`/jobannonce/<tid>/<slug>`, permitted (`Disallow: /jobannonce/korrektur/`
and `/embed/` only), between the `<!-- jobtext -->` comment and the share
block. `ad` reads the second through the first, because the slug is on the
first.

**What "37.600 job i dag" is.** The site's header counts the whole board;
the search's `hitcount` counts the query. Both are the site's, neither is
this adapter's, and the two are named apart.

Nothing is translated: the adapter emits what the site says, in Danish.
"""

import argparse
import html as htmlmod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path
from _ua import UA
from _zero import empty_first_page

HOST = "www.jobindex.dk"
BASE = f"https://{HOST}"
STASH = re.compile(r"var Stash = (\{.*?\});\s*(?://\]\]>|</script>)", re.S)
TID = re.compile(r"^[a-z]\d+$")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobindex] {msg}", file=sys.stderr)


def _robots_gate(url, exit_code=7):
    """Ask before fetching — per host and per path, inside `get()`. The apex
    refuses everything; a URL built on it would die here with exit 7 and the
    rule quoted, which is the point of asking on the exact URL."""
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", 8)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", exit_code)
    if a.get("requested_host") and a["host"] != a["requested_host"]:
        note(f"robots.txt for {a['requested_host']} was read from {a['host']} "
             f"— a redirect crossed hosts.")
    return a


# One request per query, two per ad; the host declares no Crawl-delay, so
# the spacing is this adapter's own, and `Pace` would take the host's if it
# ever declared one.
_PACE = Pace(HOST, own=2.0)


def get(url):
    _robots_gate(url)
    _PACE.wait()
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90)
        return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach {HOST}: {e}")


def to_text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?is)<br\s*/?>|</p>|</li>|</h\d>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    lines = [re.sub(r"[ \t]+", " ", htmlmod.unescape(l)).strip()
             for l in markup.split("\n")]
    return "\n".join(l for l in lines if l).strip()


def search_url(q, area=None):
    """One parameter, page 1 — the two things the rules leave open."""
    path = f"/jobsoegning/{area.strip('/')}" if area else "/jobsoegning"
    return BASE + path + ("?" + urllib.parse.urlencode({"q": q}) if q else "")


def ad_url(tid):
    """Contract 4: the canonical URL from the id, never scraped."""
    return f"{BASE}/vis-job/{tid}"


def search_response(body):
    """The embedded JSON, or `None` when the page carries no `Stash` — the
    reading-fault shape, not an empty result."""
    m = STASH.search(body)
    if not m:
        return None
    try:
        stash = json.loads(m.group(1))
        return stash["jobsearch/result_app"]["storeData"]["searchResponse"]
    except (ValueError, KeyError, TypeError):
        return None


def card(r):
    tid = r.get("tid") or ""
    return {
        "id": tid,
        "ledger_id": f"jobindex:{tid}",
        "url": ad_url(tid),
        "title": r.get("headline"),
        "company": r.get("companytext") or (r.get("company") or {}).get("name"),
        "provider": "jobindex",
        "location": r.get("area"),
        "country": "DK",
        "countries": ["DK"],
        # the listing's two dates, named for what the site calls them: the
        # day it went up, and the last day it is shown
        "firstdate": r.get("firstdate"),
        "lastdate": r.get("lastdate"),
        "apply_deadline": r.get("apply_deadline"),
        "home_workplace": r.get("home_workplace"),
        "is_archived": r.get("is_archived"),
        "language": "da",
    }


# ---------------------------------------------------------------- commands --

def cmd_search(a):
    url = search_url(a.q, a.area)
    status, body = get(url)
    if status != 200:
        die(f"{HOST} answered HTTP {status} on {url}", code=4)
    sr = search_response(body)
    if sr is None:
        # **The page carries no results JSON** — the markup moved, or a
        # shell was served. Not an empty board: the size beside the zero.
        die(empty_first_page("jobindex", body, what="`Stash` results JSON",
                             where=url, what_asked=a.q), 6)
    results = sr.get("results") or []
    hitcount = sr.get("hitcount")
    total_pages = sr.get("total_pages")
    if not results and hitcount == 0:
        note(f"0 results, and the site states hitcount 0 for {a.q!r}"
             f"{' in ' + a.area if a.area else ''} — a real zero: the query "
             f"matched nothing on a board that answered with its own count.")
        return
    if not results:
        die(empty_first_page("jobindex", body, what="result",
                             candidates=len(results), where=url,
                             what_asked=a.q)
            + f" And the site states hitcount {hitcount!r}: the two disagree.", 6)
    kept = 0
    for r in results:
        c = card(r)
        if a.with_text and c["id"]:
            c["text"] = ad_text(c["id"])
        print(json.dumps(c, ensure_ascii=False))
        kept += 1
        if a.limit and kept >= a.limit:
            break
    # **Two counters from two branches**: `kept` is what this run emitted,
    # `hitcount` is what the site states for the query — and the gap between
    # them is the rules', not the board's.
    note(f"{kept} emitted of {len(results)} returned on page 1; the site "
         f"states hitcount {hitcount} over {total_pages} page(s) of "
         f"{sr.get('page_size')}. **Page 1 is the cap, by the site's own "
         f"rules** — `Disallow: /jobsoegning*page=` — so this count is never "
         f"the size of the result, and the adapter does not ask for page 2.")
    if a.limit and kept < len(results):
        note(f"stopped at --limit {a.limit}; {len(results)} were on the page.")


def ad_text(tid):
    """The full text lives on `/jobannonce/<tid>/<slug>`, reached through the
    canonical page that carries the slug."""
    status, body = get(ad_url(tid))
    if status == 404:
        die(f"no advertisement {tid} (HTTP 404) — it was filled or pulled. "
            f"Record it as discarded.", 3)
    if status != 200:
        die(f"{HOST} answered HTTP {status} for {tid}", 4)
    m = re.search(rf'href="(https://{re.escape(HOST)}/jobannonce/{re.escape(tid)}/[^"]*)"', body)
    if not m:
        # the teaser page is what there is: say which page the text came from
        return {"source": "vis-job (teaser — no /jobannonce/ link on the page)",
                "text": to_text(body)[:4000]}
    status, full = get(m.group(1))
    if status != 200:
        return {"source": f"vis-job (the /jobannonce/ page answered HTTP {status})",
                "text": to_text(body)[:4000]}
    i = full.find("<!-- jobtext -->")
    end = re.search(r'<[a-z]+[^>]*class="[^"]*jobad-element-share', full[max(i, 0):])
    j = (max(i, 0) + end.start()) if end else -1
    seg = full[i:j] if i >= 0 and j > i else full
    if i < 0:
        note(f"{tid}: no `<!-- jobtext -->` marker on {m.group(1)} — the whole "
             f"page's text is returned, and the markup has moved.")
    return {"source": m.group(1), "text": to_text(seg)}


def cmd_ad(a):
    if not TID.match(a.id):
        die(f"{a.id!r} is not a Jobindex id — one letter and digits, e.g. "
            f"h1697049 or o41080, the `tid` of a card.")
    t = ad_text(a.id)
    print(json.dumps({"id": a.id, "ledger_id": f"jobindex:{a.id}",
                      "url": ad_url(a.id), "provider": "jobindex",
                      "country": "DK", **t}, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="page 1 of a query — the rules refuse page 2")
    s.add_argument("--q", default="", help="the query, one parameter (Danish or English as the site takes it)")
    s.add_argument("--area", help="an area or category path the site's sitemap declares, e.g. it/systemudvikling")
    s.add_argument("--with-text", action="store_true", dest="with_text",
                   help="also read each ad's full text (two requests per ad)")
    s.add_argument("--limit", type=int, default=0)
    s.set_defaults(func=cmd_search)
    d = sub.add_parser("ad", help="one advertisement's full text, from its tid")
    d.add_argument("--id", required=True)
    d.set_defaults(func=cmd_ad)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
