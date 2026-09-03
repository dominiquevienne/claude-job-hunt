#!/usr/bin/env python3
"""Read Chile's Bolsa Nacional de Empleo — a sitemap of nothing but ads, and a
board that is not UTF-8.

`bne.gob.cl`, the national employment service. **No key, no cookie, no
browser** — the *search* renders client-side, and **the advertisement pages do
not**: each carries a `JobPosting` in JSON-LD.

  GET /sitemap.xml            → 7 928 `<loc>`, **every one an advertisement**
  GET /oferta/<id>            → 200, a JobPosting in JSON-LD

**THE SITEMAP IS ALL ADS, WHICH IS RARE HERE.** 7 928 of 7 928 are
`/oferta/<id>` — no employer pages, no search landings. hr.ge's file is 39 247
`<loc>` of which **1 062** are ads; this one needs no filtering, and the
difference is worth stating because the habit of filtering is what protects
against the other kind.

**AND THE BOARD IS NOT UTF-8.** The response says `charset=ISO-8859-1`, the
markup says `windows-1252`, and this repository's house pattern —
`decode("utf-8", "replace")` — **loses 37 to 93 characters per advertisement**,
measured on eight of eight. On a Spanish board that is most of the text that
carries meaning, and **`errors="replace"` cannot fail**: it produces plausible
text with holes. `_decode.py` follows the declared charset and reports which
one it used.

TWO DOMAINS, ONE SITE, AND THE FILE POINTS AT THE OTHER ONE. `bne.cl` and
`bne.gob.cl` serve **the same 67 bytes**, md5 `7d46f6463cb7…`, `Allow: /` —
and **both declare their sitemap on `www.bne.gob.cl`**. `bne.cl` redirects to
`www.bne.cl`, so a verdict asked under the typed name is read from the
answering host: exactly what #99 keys the cache on, and the reason nothing here
records a host by hand.

**THE SEARCH IS NOT A ROUTE.** `/ofertas` answers 200 with 122 kB and **zero
`/oferta/` links** — the results arrive client-side, and its own pagination URL
(`numPaginaRecuperar`, `numResultadosPorPagina`) returns the same empty shell.
So enumeration goes through the sitemap, which is one request for the whole
board, and **`search` here is a scan with a stated cost** rather than a query
the site answers.

Verified against the live site on **2026-09-03**.
"""

import argparse
import html as html_mod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _ldjson import label, one, postings
from _robots import allowed as robots_allowed
from _sitemap import count_says, locs as sitemap_locs
from _zero import zero_note

BASE = "https://www.bne.gob.cl"
SITEMAP = BASE + "/sitemap.xml"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

EXIT_BROKEN, EXIT_GONE, EXIT_REFUSED = 2, 3, 7

AD_RE = re.compile(r"/oferta/(\d{4}-\d+)")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[bne.cl] {msg}", file=sys.stderr)


def get(url, timeout=45):
    """Fetch, and **decode with what the response declares.**"""
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, parts.path or "/")
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "es-CL,es;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            text, enc = decode_body(raw, r.headers)
            return r.getcode(), text, enc, raw
    except urllib.error.HTTPError as e:
        return e.code, "", None, b""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def card(text, ident, url):
    posts = postings(text)
    if not posts:
        return None
    p = posts[0]
    loc = one(p.get("jobLocation"))
    addr = one(loc.get("address"))
    desc = p.get("description") or ""
    return {
        "id": ident,
        "ledger_id": f"bne.cl:{ident}",
        "url": url,
        "title": label(p.get("title")),
        "company": label(p.get("hiringOrganization")),
        "location_text": " · ".join(
            x for x in (addr.get("addressLocality"), addr.get("addressRegion"),
                        addr.get("addressCountry")) if isinstance(x, str)
        ) or None,
        "posted": label(p.get("datePosted")),
        # The employer's own statement, and the one thing that outranks any
        # inference about whether an ad is open.
        "valid_through": label(p.get("validThrough")),
        "description_chars": len(re.sub(r"<[^>]+>", "", desc)),
    }


def cmd_sitemap(a):
    code, text, enc, raw = get(SITEMAP, timeout=90)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    urls = sitemap_locs(raw)
    if not urls:
        die(f"{SITEMAP}: {count_says(raw)}")
    ads = [u for u in urls if AD_RE.search(u)]
    for u in (ads[:a.limit] if a.limit else ads):
        m = AD_RE.search(u)
        print(json.dumps({"id": m.group(1),
                          "ledger_id": f"bne.cl:{m.group(1)}",
                          "url": u}, ensure_ascii=False))
    other = len(urls) - len(ads)
    note(f"{len(ads)} advertisement URL(s) of {len(urls)} `<loc>`"
         + (f" — {other} were something else." if other else
            " — **every entry is an advertisement**, which is unusual: this "
            "file needs no filtering, where hr.ge's carries 36 593 employer "
            "pages against 1 062 ads."))


def cmd_ad(a):
    ident = a.id or (AD_RE.search(a.url or "") or [None, None])[1]
    if not ident:
        die("give --id, or a --url of the form /oferta/<id>.")
    url = a.url if a.url and AD_RE.search(a.url) else f"{BASE}/oferta/{ident}"
    code, text, enc, _ = get(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE)
    c = card(text, ident, url)
    if not c:
        die(f"{url}: answered 200 with no `JobPosting`. On this board the ad "
            f"page is server-rendered and carries one, so this is a page that "
            f"is not an advertisement — not proof the ad is gone.", EXIT_GONE)
    if a.with_text:
        p = postings(text)[0]
        c["description"] = html_mod.unescape(
            re.sub(r"<[^>]+>", " ", p.get("description") or "")).strip()
    c["encoding"] = enc
    print(json.dumps(c, ensure_ascii=False))
    if enc and "replace" in enc:
        note("**nothing decoded strictly** — the text above may have holes in "
             "it. That is reported rather than hidden: `errors=replace` "
             "cannot fail, so a silent success here would be the failure.")


def cmd_search(a):
    """A scan, and it says so — the site answers no query without a browser."""
    code, text, enc, raw = get(SITEMAP, timeout=90)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    ids = [m.group(1) for m in (AD_RE.search(u) for u in sitemap_locs(raw))
           if m]
    want = (a.keyword or "").strip().lower()
    note(f"**this is a scan, not a query.** The board's own search renders "
         f"client-side, so matching means reading advertisements one by one: "
         f"{len(ids)} exist and this run will read at most {a.read}. Give "
         f"`--read` deliberately.")
    kept, read = 0, 0
    for ident in ids:
        if read >= a.read:
            break
        url = f"{BASE}/oferta/{ident}"
        code, text, enc, _ = get(url)
        read += 1
        if code != 200:
            continue
        c = card(text, ident, url)
        if not c:
            continue
        if want:
            hay = " ".join(str(c.get(k) or "") for k in
                           ("title", "company", "location_text")).lower()
            if want not in hay:
                time.sleep(a.delay)
                continue
        print(json.dumps(c, ensure_ascii=False))
        kept += 1
        if a.limit and kept >= a.limit:
            break
        time.sleep(a.delay)
    if kept == 0:
        note(zero_note("bne.cl", what=a.keyword, extra=(
            f"{read} advertisement(s) were read of {len(ids)} on the board. "
            f"**A zero here is a statement about {read} ads, not about "
            f"Chile** — raise `--read` before concluding.")))
        return
    note(f"{kept} match(es) after reading {read} of {len(ids)} — "
         f"**say both numbers**: the second is what the first is out of.")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("sitemap", help="every advertisement URL — one request")
    m.add_argument("--limit", type=int)
    m.set_defaults(func=cmd_sitemap)

    d = sub.add_parser("ad", help="one advertisement, from its JobPosting")
    d.add_argument("--id")
    d.add_argument("--url")
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)

    s = sub.add_parser("search", help="a scan with a stated cost")
    s.add_argument("--keyword")
    s.add_argument("--read", type=int, default=40,
                   help="how many ads to read; the board has ~7 900")
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=0.5)
    s.set_defaults(func=cmd_search)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
