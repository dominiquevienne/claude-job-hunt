#!/usr/bin/env python3
"""Wuzzuf (`wuzzuf.net`) — Egypt's largest board: an inventory of addresses through the sitemap, and a challenge on every page.

  wuzzuf.py sitemap [--country eg|sa|ae|…] [--saudi] [--limit N]
  wuzzuf.py ad --url <advertisement URL>

TWO ROUTES ANSWER DIFFERENTLY, AND THE RULES PERMIT BOTH

The rules are the Cloudflare managed file with `ClaudeBot` named and refused and
`*` allowed (`Crawl-delay: 10`, a `Sitemap:` line) — under the owner's decision
of 2026-09-07 this project goes as `Claude-User`, and `identity()` says so. On
2026-09-11 the transport then split:

    /jobs/egypt, /jobs/p/<id>-<slug>     403, 5 666 B, «Just a moment...», md5
                                         moving at constant size — a challenge
    /sitemap.xml, /sitemap-job-1.xml     200 — the index, then 5 491 <loc>

**So the sitemap is the route, and it yields ADDRESSES, not advertisements.**
Every `<loc>` is `/jobs/p/<12-char id>-<title>-<company>-<city>-<country>` (or
`/internship/…`, or `/saudi/jobs/p/…`); the slug carries the country as its
tail, and nothing else can be read: the pages behind the addresses answer the
challenge. `ad` says exactly that, and reads nothing.

THE LASTMOD IS ONE VALUE ON ALL 5 491 — a regeneration stamp
(`2026-09-11T02:04:48+03:00` on every entry), not a posting date. Nothing here
dates an advertisement, and `--since` does not exist for that reason.

THE COUNT IS A COUNT OF ADDRESSES, AND THE CARD SAYS SO. `5 491 <loc>, 5 491
distinct, 5 321 in the /jobs/p/ shape and 170 in two others` — counted where
they are decided, printed beside each other. **No route this adapter may take
states how many are open**, so nothing anchors the figure to the board, and a
zero here would be «the sitemap held no address», said with the byte count.

Measured 2026-09-11 13:45–13:50 UTC. Requests are spaced by the host's own
`Crawl-delay: 10`, which `_pace` applies.
"""

import argparse
import collections
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _sitemap import locs as sitemap_locs
from _ua import UA, EXIT_NEEDS_BROWSER

BASE = "https://wuzzuf.net"
INDEX = BASE + "/sitemap.xml"
JOB_FILES = {"jobs": BASE + "/sitemap-job-1.xml", "saudi": BASE + "/sitemap-saudi-job-1.xml"}
AD_RE = re.compile(r"^https://wuzzuf\.net/(jobs/p|internship|saudi/jobs/p)/([a-z0-9]{12})-(.+)$")
# The slug's tail names the country, in the site's own words. Measured on
# 5 491 addresses: `egypt` 5 272, `saudi-arabia` 84, `arab-emirates` 34 …
COUNTRY_TAILS = (("saudi-arabia", "SA"), ("arab-emirates", "AE"), ("united-states", "US"),
                 ("united-kingdom", "GB"), ("egypt", "EG"), ("libya", "LY"), ("canada", "CA"),
                 ("qatar", "QA"), ("kuwait", "KW"), ("jordan", "JO"), ("germany", "DE"))
CHALLENGE_RE = re.compile(r"Just a moment|cf_chl|challenge-platform")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
# 9 is the repository's «permitted by the rules, refused by the transport» code;
# here the refusal is a challenge, and the message says so.


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[wuzzuf] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace("wuzzuf.net")     # the host declares Crawl-delay: 10, and that is what applies


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        try:
            body = decode_body(e.read(), e.headers)[0]
        except Exception:      # noqa: BLE001 - a refusal body is optional evidence
            body = ""
        return e.code, body
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def split_ad(url):
    """`(kind, id, slug, country)` for an advertisement address, or None."""
    m = AD_RE.match(url.strip())
    if not m:
        return None
    kind, ident, slug = m.groups()
    country = next((code for tail, code in COUNTRY_TAILS if slug.endswith(tail)), None)
    return kind, ident, slug, country


def cmd_sitemap(a):
    code, body = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}" + (" — the index too answers the challenge" if CHALLENGE_RE.search(body) else ""), EXIT_PARTIAL)
    children = sitemap_locs(body)
    files = [JOB_FILES["jobs"]] + ([JOB_FILES["saudi"]] if a.saudi else [])
    missing = [f for f in files if f not in children]
    if missing:
        die(f"{INDEX} declares {len(children)} children and not {', '.join(missing)} — the job file moved; read the index before believing a zero.", EXIT_PARTIAL)
    rows, raw, matched, unmatched, stamps = [], 0, 0, 0, collections.Counter()
    by_kind, by_country = collections.Counter(), collections.Counter()
    for f in files:
        code, body = get(f)
        if code != 200:
            die(f"{f}: HTTP {code}", EXIT_PARTIAL)
        urls = sitemap_locs(body)
        if not urls:
            die(f"{f}: {len(body)} characters and no <loc> — a reading that failed, not an empty sitemap.", EXIT_PARTIAL)
        stamps.update(re.findall(r"<lastmod>([^<]*)</lastmod>", body))
        for u in urls:
            raw += 1
            got = split_ad(u)
            if got is None:
                unmatched += 1
                continue
            matched += 1
            kind, ident, slug, country = got
            by_kind[kind] += 1
            by_country[country or "?"] += 1
            if a.country and (country or "").lower() != a.country.lower():
                continue
            rows.append({"source": "wuzzuf", "country": country, "ledger_id": f"wuzzuf:{ident}",
                         "id": ident, "url": u, "kind": kind, "slug": slug,
                         "readable_by_script": False})
    seen = {r["id"]: r for r in rows}
    for r in list(seen.values())[:a.limit] if a.limit else seen.values():
        print(json.dumps(r, ensure_ascii=False))
    if raw == 0:
        die(f"{len(files)} file(s) read and 0 <loc> between them", EXIT_PARTIAL)
    note(f"{raw} <loc> in {len(files)} file(s); {matched} matched the advertisement shape and "
         f"{unmatched} did not; {len(seen)} distinct id(s)"
         + (f" after --country {a.country}" if a.country else "") + ".")
    note("by shape: " + ", ".join(f"{k} {v}" for k, v in by_kind.most_common())
         + " · by country tail: " + ", ".join(f"{k} {v}" for k, v in by_country.most_common(8)))
    if len(stamps) == 1:
        note(f"every <lastmod> carries the same value ({next(iter(stamps))}) — a regeneration "
             f"stamp, not a posting date. Nothing here dates an advertisement.")
    else:
        note(f"{len(stamps)} distinct <lastmod> values — dates may be per entry this run; not relied on.")
    note("**These are addresses, not advertisements**: the pages behind them answer an "
         "anti-robot challenge to this client, so no title, employer, date or text is read — "
         "the slug is all there is. No route this adapter may take states how many are open.")


def cmd_ad(a):
    got = split_ad(a.url)
    if got is None:
        die(f"{a.url}: not an advertisement address — expected https://wuzzuf.net/jobs/p/<id>-<slug>")
    code, body = get(a.url)
    if code == 200 and not CHALLENGE_RE.search(body):
        # Not measured on 2026-09-11 — every page answered the challenge. If
        # this branch is ever reached, the host changed; say so and stop
        # rather than emit fields nobody has verified.
        die(f"{a.url}: HTTP 200, {len(body)} characters, and no challenge — the host serves "
            f"pages to this client now. **Nothing here is written for that page**: re-verify "
            f"wuzzuf.md before reading it as an advertisement.", EXIT_PARTIAL)
    if CHALLENGE_RE.search(body):
        die(f"{a.url}: HTTP {code}, {len(body)} characters, «Just a moment...» — **the rules "
            f"permit this path and the server answers an anti-robot challenge.** This adapter "
            f"does not attempt to pass it and does not ask anyone to; if the user's own browser "
            f"is let through, the page can be read there. Not an empty advertisement.",
            EXIT_NEEDS_BROWSER)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    die(f"{a.url}: HTTP {code}, {len(body)} characters", EXIT_PARTIAL)


def main():
    p = argparse.ArgumentParser(description="Wuzzuf — Egypt's largest board, read through the sitemap it declares; its pages answer a challenge.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="advertisement addresses from the job sitemap — 2 requests, 10 s apart")
    s.add_argument("--country", help="ISO-2 as the slug's tail maps it (eg, sa, ae, …)")
    s.add_argument("--saudi", action="store_true", help="also read sitemap-saudi-job-1.xml")
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one advertisement — names the challenge, reads nothing")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
