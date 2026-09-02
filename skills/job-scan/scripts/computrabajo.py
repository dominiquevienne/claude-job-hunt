#!/usr/bin/env python3
"""Fetch Latin American ads from Computrabajo — eighteen countries, one rule
file, and a robots.txt that closes the filters and leaves the search open.

Eighteen national sites — **`co cl pe mx ar ec ve cr pa gt bo do uy sv hn ni
py pr`** — serve **the same 874-byte `robots.txt`, md5 `cfcbd02061ac…`,
identical on all eighteen with no exception**. Verified 2026-09-02, checked as
`text/plain` and not merely as a status.

**No key, no cookie, no account, no browser.** Listings and ad pages both
answer plain `curl`.

  GET https://<cc>.computrabajo.com/ofertas-de-trabajo/?q=<keyword>&p=<page>
      → 200 text/html, ~310 KB, 20 <article class="box_offer"> cards
  GET https://<cc>.computrabajo.com/ofertas-de-trabajo/<slug>-<32-hex id>
      → 200 text/html, the ad

WHAT THE RULE FILE CLOSES IS THE FILTERS, NOT THE SEARCH. Every `Disallow` on
the listing path names a query parameter:

    /ofertas-de-trabajo/*dis=      *cont=     *pubdate=   *sal=    *by=
    /ofertas-de-trabajo/*emp=      *emq=      *ememq=     …and the em* family

**`q=` is not among them**, and neither is `p=`. So a keyword search and its
pagination are open, and **the site's own salary, date, contract-type,
disability and sort filters are closed to us**. This script refuses to build
any of them rather than quietly sending one, and narrowing is done after the
fetch, in the scoring rubric.

Also closed: `/hojas-de-vida/`, `/curriculums/` (CVs), `/Ajax/`,
`/_services/`, `/go/`. No AI agent is named, for or against.

THERE IS NO STRUCTURED DATA ON THE AD. The only `application/ld+json` on a
listing page or an ad page is an `Organization` graph for Computrabajo itself
— **no `JobPosting`**. Everything here is DOM extraction, anchored on
`<article class="box_offer" data-id="…">` and, on the ad, on the container
marked `div-link="oferta"`. Those are the most stable handles the markup
offers; they are still markup, and they will move.

Verified against `co.computrabajo.com` on **2026-09-02**.
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

from _zero import zero_note

COUNTRIES = ("co", "cl", "pe", "mx", "ar", "ec", "ve", "cr", "pa", "gt",
             "bo", "do", "uy", "sv", "hn", "ni", "py", "pr")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

# The query parameters the shared robots.txt disallows on the listing path.
# Named here so the refusal can quote them.
FORBIDDEN = ("dis", "cont", "pubdate", "sal", "by", "emp", "emq", "ememq",
             "emcont", "emsal", "empubdate", "ememsal", "emdis", "ememcont")

CARD = re.compile(r'<article[^>]*data-id=.([0-9A-F]{32}).*?(?=<article|\Z)',
                  re.S)
TITLE = re.compile(r'<a class="js-o-link[^"]*" href="([^"]+)"[^>]*>(.*?)</a>',
                   re.S)
COMPANY = re.compile(r'href="([^"]*/empresas/[^"]*)"[^>]*offer-grid-article-'
                     r'company-url>(.*?)</a>', re.S)
PLACE = re.compile(r'<p class="fs16 fc_base mt5">\s*<span class="mr10">'
                   r'(.*?)</span>', re.S)
WHEN = re.compile(r'<p class="fs13 fc_aux mt15">\s*(.*?)\s*</p>', re.S)
BODY = re.compile(r'<div[^>]*div-link="oferta"[^>]*>(.*?)</div>\s*<div',
                  re.S)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[computrabajo] {msg}", file=sys.stderr)


def text(fragment):
    t = re.sub(r"(?is)<(script|style|svg)[^>]*>.*?</\1>", " ", fragment or "")
    t = re.sub(r"(?i)</(p|div|li|br|h[1-6])>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return html_mod.unescape(re.sub(r"[ \t]+", " ", t)).strip()


def one_line(fragment):
    return re.sub(r"\s+", " ", text(fragment)).strip()


def get(host, path):
    url = f"https://{host}{path}"
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html",
        "Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            ctype = r.headers.get("Content-Type", "")
            if "text/html" not in ctype:
                die(f"{url}: Content-Type {ctype!r} — this board serves HTML.")
            return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        die(f"{url}: HTTP {exc.code}")
    except (urllib.error.URLError, OSError) as exc:
        die(f"{url}: {exc}")


def card(host, block, ident):
    m = TITLE.search(block)
    href = (m.group(1).split("#")[0] if m else None)
    comp = COMPANY.search(block)
    place = PLACE.search(block)
    when = WHEN.search(block)
    return {
        "id": ident,
        "ledger_id": f"computrabajo:{ident}",
        "url": (f"https://{host}{href}" if href else None),
        "title": one_line(m.group(2)) if m else None,
        # Named on 69 of 80 cards; the other 11 carry no employer at all.
        "company": one_line(comp.group(2)) if comp else None,
        # **The company page's slug is not the employer name.** On 4 of 80 it
        # differed — usually a long form against a short one (ANDISEG LTDA vs
        # "compañía andina de seguridad privada"), once a different name
        # entirely. Use the displayed name and this id; never the slug.
        "company_page": (comp.group(1) if comp else None),
        "location_text": one_line(place.group(1)) if place else None,
        # A tag, not a field: present on 28 of 80.
        "remote": "i_home" in block,
        # Relative and localised — "Hace 7 horas", "Ayer". There is no
        # absolute date anywhere on the card.
        "posted_relative": one_line(when.group(1)) if when else None,
    }


def cmd_search(a):
    host = f"{a.country}.computrabajo.com"
    seen, kept = set(), 0
    for page in range(1, a.pages + 1):
        q = {"q": a.keyword} if a.keyword else {}
        if page > 1:
            q["p"] = page
        path = "/ofertas-de-trabajo/"
        if q:
            path += "?" + urllib.parse.urlencode(q)
        body = get(host, path)
        if body is None:
            note(f"page {page}: 404 — stopping.")
            break
        blocks = list(CARD.finditer(body))
        if not blocks:
            # An honest end: page 200 of a search with 40 pages answers 200
            # with a shorter page and no cards. No repeat, no error.
            note(f"page {page} carried no card — that is this board's end of "
                 f"results, and it is an honest one.")
            break
        for m in blocks:
            c = card(host, m.group(0), m.group(1))
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            print(json.dumps(c, ensure_ascii=False))
            kept += 1
            if a.limit and kept >= a.limit:
                note(f"{kept} ads returned from {a.country} over {page} "
                     f"page(s).")
                return
        time.sleep(a.delay)
    if kept == 0:
        note(zero_note("computrabajo", what=a.keyword,
                       where=a.country))
    note(f"{kept} ads returned from {a.country}.")
    note("no salary is on the card and none is in any structured block — the "
         "site's salary filter is disallowed by robots.txt, so pay is read "
         "from the ad text or not at all.")


def cmd_ad(a):
    host = f"{a.country}.computrabajo.com"
    body = get(host, a.path)
    if body is None:
        die(f"{a.path}: 404 — the ad is gone.", 3)
    m = BODY.search(body)
    if not m:
        die("the ad body container `div-link=\"oferta\"` was not found. This "
            "board has no JobPosting JSON-LD to fall back on, so the parse is "
            "the markup — re-verify computrabajo.md.", 3)
    title = re.search(r'<h1[^>]*>(.*?)</h1>', body, re.S)
    ident = re.search(r"([0-9A-F]{32})", a.path)
    print(json.dumps({
        "id": ident.group(1) if ident else None,
        "ledger_id": f"computrabajo:{ident.group(1)}" if ident else None,
        "url": f"https://{host}{a.path}",
        "title": one_line(title.group(1)) if title else None,
        "description": text(m.group(1)) if a.with_text else None,
        "description_chars": len(text(m.group(1))),
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="read the result cards")
    s.add_argument("--country", required=True, choices=COUNTRIES)
    s.add_argument("--keyword")
    s.add_argument("--pages", type=int, default=1)
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=1.5)
    for f in FORBIDDEN:
        s.add_argument(f"--{f}", help=argparse.SUPPRESS)
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="read one ad by path")
    d.add_argument("--country", required=True, choices=COUNTRIES)
    d.add_argument("--path", required=True,
                   help="/ofertas-de-trabajo/<slug>-<id>")
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    used = [f for f in FORBIDDEN if getattr(a, f, None)]
    if used:
        die(f"{', '.join(used)} — every one of these is a query parameter the "
            f"shared robots.txt disallows on /ofertas-de-trabajo/. This "
            f"adapter does not build them. Filter after the fetch instead.")
    a.func(a)


if __name__ == "__main__":
    main()
