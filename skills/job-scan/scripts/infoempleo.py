#!/usr/bin/env python3
"""Fetch Spanish ads from infoempleo.com — a generalist board, and a bad liar.

**7 621 active ads**, the third Spanish adapter here and the first that is not
a public register: `empleate.md` and `oposiciones.md` are both the SEPE's, and
this one is a private generalist board covering the whole country.

  GET /robots.txt              → two Sitemap: lines, one of them empty
  GET /sitemap-index.xml       → the real list
  GET /sitemap-ofertas-activas.xml   → 7 621 ad URLs, no lastmod
  GET /ofertasdetrabajo/<slug>/<place>/<id>/   → the ad, JSON-LD JobPosting

**No browser, no account, no key.** `robots.txt` names no crawler and no AI
agent; its 73 `Disallow` rules close faceted search under `/trabajo/`, the
training section and `/login/`, and leave `/ofertasdetrabajo/` open.

Everything here was verified against the live site on 2026-09-01.

THE TRAP THAT OUTLIVES THE BOARD — and it is not deterministic, which is what
makes it dangerous. **The site answers `Content-Encoding: deflate` on a
fraction of requests, unsolicited**, and the fraction is decided by which
backend takes the call. The same URL, same headers, same minute:

    try1  enc=deflate  raw= 39 057  →  decoded 159 803  ld+json blocks: 4
    try2  enc=deflate  raw= 39 057  →  decoded 159 803  ld+json blocks: 4
    try3  enc=-        raw=159 579  →                   ld+json blocks: 4
    try4  enc=-        raw=159 579  →                   ld+json blocks: 4

Six of eight came back deflated in one run, two of forty-five in the next.

A client that does not decompress does **not** get an error. It gets 37 111
characters of mangled bytes that decode with `errors="replace"`, carry no
`<script>` tag, contain no `JobPosting`, and read exactly like *an ad page with
no structured data*. HTTP 200, correct content type, plausible length.

So the failure is silent, intermittent, and **never reproduces on the same
ads** — a spot-check passes, and a re-run "fixes" a different subset. Measured
naively it reported 5 of 45 ads as carrying no structured data; measured with
the body decompressed, **44 of 45 do**, and the one that does not is a
genuinely expired ad.

This is the gzip trap of `jobindex.dk` and the CDATA trap of `hays-fr.md` with
the one property both of those lacked: it comes and goes. `read()` below always
decodes, and `card()` treats **zero ld+json blocks** — not "no JobPosting" — as
a failure to read, because a real ad page here always carries three or four.

THE SECOND ONE IS THE PREVIOUS RELEASE'S LESSON, INVERTED. `hays-fr.md` records
that the pay sits in `baseSalary.value.value` where four other boards use
`minValue` / `maxValue`. Here:

    "baseSalary": {"value": {"value": 0.0, "minValue": 22000.0,
                             "maxValue": 30000.0, "unitText": "YEAR"}}

`value.value` is **0.0 on every salaried ad measured** (9 of 9), and the truth
is in `minValue` / `maxValue`. An adapter written from the most recent lesson
in this repository reports **€0 on every ad that states a salary**. Read the
object, not the sub-field that worked last time.

Usage:
  infoempleo.py lugares
  infoempleo.py search --lugar madrid --limit 20
  infoempleo.py discover --lugar barcelona

Output: one JSON object per line.
"""

import argparse
import collections
import gzip
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zlib

BASE = "https://www.infoempleo.com"
# Taken from /sitemap-index.xml, NOT from robots.txt — see trap 3.
SITEMAP = BASE + "/sitemap-ofertas-activas.xml"
SITEMAP_INDEX = BASE + "/sitemap-index.xml"
# Declared in robots.txt, absent from the index, and 0 bytes on every request.
EMPTY_SITEMAP = BASE + "/sitemap-ofertas-activas-recientes.xml"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# Reads `<loc>https://…</loc>` and the CDATA-wrapped form both. hays.fr serves
# the second, where the first non-space character after the tag is `<`, and the
# strict pattern `<loc>\s*([^<\s]+)` matches nothing at all — 0 URLs from a
# valid 2.37 MB sitemap. infoempleo.com does not use CDATA today (checked:
# 7 621 <url>, 7 621 <loc>, no CDATA), so this is insurance against a change
# nobody would announce, not a fix for a live fault. See issue #55.
LOC_RE = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?\s*([^\s\]<]+)")
URL_BLOCK_RE = re.compile(r"<url>")
AD_RE = re.compile(r"/ofertasdetrabajo/([^/]+)/([^/]+)/(\d+)/")
LD_RE = re.compile(r"<script[^>]*application/ld\+json[^>]*>(.*?)</script>",
                   re.S | re.I)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[infoempleo] {msg}", file=sys.stderr)


def decode(raw, enc):
    """Undo whatever the backend that answered decided to apply.

    See the module docstring. `deflate` arrives unsolicited on a fraction of
    responses, and both the zlib-wrapped and the raw form are seen, so both
    are tried before giving up.
    """
    enc = (enc or "").lower()
    if enc == "gzip":
        return gzip.decompress(raw)
    if enc in ("deflate", "zlib"):
        try:
            return zlib.decompress(raw)
        except zlib.error:
            return zlib.decompress(raw, -zlib.MAX_WBITS)
    return raw


def get(url, retries=2):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                enc = r.headers.get("Content-Encoding")
            try:
                body = decode(raw, enc)
            except Exception as exc:  # noqa: BLE001 - name it, do not swallow
                die(f"{url}: Content-Encoding was {enc!r} and the body would "
                    f"not decompress ({exc}). Reading it raw would yield a "
                    "page that looks structurally empty rather than an error.")
            return body.decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as exc:
            if attempt == retries:
                die(f"{url}: {exc}")
            time.sleep(1.5 * (attempt + 1))
    return ""


def fold(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def entries():
    body = get(SITEMAP)
    urls = [u for u in LOC_RE.findall(body) if "/ofertasdetrabajo/" in u]
    if not urls:
        # Arithmetic before conclusions. Zero <loc> inside a non-zero number
        # of <url> blocks is impossible in any valid sitemap, so it says the
        # reader is wrong rather than the board being empty. That is what
        # exposed the CDATA fault on hays.fr — not the code, the counting.
        # (`<lastmod>` is optional in the spec, so it cannot play this role.)
        blocks = len(URL_BLOCK_RE.findall(body))
        if blocks:
            die(f"read 0 ad URLs out of {blocks} <url> blocks in a "
                f"{len(body)} character sitemap. That combination is "
                "impossible in a valid sitemap, so this is a reading fault, "
                "not an empty board — check <loc> for a wrapper this "
                f"extractor does not handle.\n  {SITEMAP}")
        die("the offers sitemap yielded no ad URLs and no <url> blocks "
            f"either ({len(body)} characters). It is normally ~900 KB and "
            f"~7 600 entries.\n  {SITEMAP}\n"
            "Note that robots.txt also declares "
            f"{EMPTY_SITEMAP},\n  which is 0 bytes on every request — if that "
            "is what was read, read /sitemap-index.xml instead.")
    return urls


def parts(url):
    m = AD_RE.search(url)
    return m.groups() if m else (None, None, None)


def text_of(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()


def money(base):
    """Read the pay, and refuse the sub-field that worked on the last board.

    `value.value` is 0.0 on every salaried ad here — see the module docstring.
    Only `minValue` / `maxValue` carry a figure, and a 0 in any of them means
    absent rather than free.
    """
    v = (base or {}).get("value") or {}
    lo, hi = v.get("minValue") or None, v.get("maxValue") or None
    return lo, hi, v.get("unitText"), v.get("value")


def address_of(jp):
    """`jobLocation` is a dict on most ads and a list on the multi-site ones."""
    loc = jp.get("jobLocation")
    if isinstance(loc, list):
        locs = [x for x in loc if isinstance(x, dict)]
    elif isinstance(loc, dict):
        locs = [loc]
    else:
        locs = []
    addrs = [(x.get("address") or {}) for x in locs]
    return (addrs[0] if addrs else {}), len(addrs)


def card(url):
    slug, place, ident = parts(url)
    page = get(url)
    blocks = LD_RE.findall(page)
    if not blocks:
        # The signature of an undecoded body, not of an ad without data: a
        # real page here always carries three or four blocks. See trap 1.
        die(f"{url} carries no ld+json block at all ({len(page)} chars). A "
            "live ad page on this site always has three or four. That is the "
            "signature of a body that was not decompressed, not of an ad "
            "with no structured data — check Content-Encoding handling "
            "before believing this.")
    jp = None
    for b in blocks:
        try:
            j = json.loads(b)
        except Exception:  # noqa: BLE001 - one broken block is not fatal
            continue
        for x in (j if isinstance(j, list) else [j]):
            if isinstance(x, dict) and x.get("@type") == "JobPosting":
                jp = x
    if jp is None:
        # Blocks present, no JobPosting among them: the ad is gone. Measured
        # on 1 of 45 — the sitemap is called "activas" and is not perfect.
        return {"id": ident, "ledger_id": f"infoempleo:{ident}", "url": url,
                "place_from_url": place, "expired": True,
                "ld_json_blocks": len(blocks), "json_ld": False}
    addr, nloc = address_of(jp)
    lo, hi, unit, zero = money(jp.get("baseSalary"))
    org = jp.get("hiringOrganization") or {}
    return {
        "id": ident,
        "ledger_id": f"infoempleo:{ident}",
        "url": url,
        "reference": (jp.get("identifier") or {}).get("value"),
        "title": jp.get("title"),
        # Named on 44 of 44 — but 32 of those 44 are staffing agencies, so
        # the name is often the intermediary rather than the workplace.
        "company": org.get("name"),
        "place_from_url": place,
        # The province. Present on 43 of 44, where addressLocality — the town
        # — is on 39.
        "region": addr.get("addressRegion"),
        "location_text": addr.get("addressLocality"),
        # Absent on 44 of 44, exactly as on hays-fr.md. Emitted as None so it
        # is never mistaken for one.
        "postcode": addr.get("postalCode") or None,
        "country": addr.get("addressCountry"),
        "locations_count": nloc,
        "employment_type": jp.get("employmentType"),
        "work_hours": jp.get("workHours"),
        "experience": jp.get("experienceRequirements"),
        "industry": jp.get("industry"),
        "occupation": jp.get("occupationalCategory"),
        # Identical to `industry` on 18 of 18 measured — it is the sector
        # again, not a qualification. Kept so nobody reads it as one.
        "qualifications_field_duplicates_industry": (
            jp.get("qualifications") == jp.get("industry")),
        "salary_min": lo,
        "salary_max": hi,
        "salary_unit": unit,
        # Always 0.0 when a salary is stated. Recorded, never used.
        "salary_value_field_literal": zero,
        "salary_currency": (jp.get("baseSalary") or {}).get("currency"),
        "published": jp.get("datePosted"),
        # Real and per-ad — 20 to 283 days after datePosted across the sample,
        # not a formula. None had already passed.
        "valid_through": jp.get("validThrough"),
        "description": text_of(jp.get("description")),
        "ld_json_blocks": len(blocks),
        "json_ld": True,
    }


def narrow(urls, a):
    if a.lugar:
        want = fold(a.lugar)
        before = len(urls)
        urls = [u for u in urls if want == fold(parts(u)[1] or "")]
        note(f"{len(urls)} of {before} match --lugar {a.lugar!r} in the URL, "
             "filtered before any fetch")
        if not urls:
            note("no place by that name. `infoempleo.py lugares` lists the "
                 "1 201 the sitemap actually uses — a wrong one is an empty "
                 "board, not an error.")
    return urls


def cmd_lugares(a):
    urls = entries()
    c = collections.Counter(parts(u)[1] for u in urls)
    for place, n in c.most_common(a.limit or None):
        print(json.dumps({"lugar": place, "ads": n}, ensure_ascii=False))
    note(f"{len(c)} distinct places across {len(urls)} ads. This is free — it "
         "is read out of the URL, so --lugar costs no fetch.")
    note("'multiprovincia' is a real value, not a placeholder: ads posted "
         "across several provinces at once.")


def cmd_discover(a):
    urls = narrow(entries(), a)
    for u in urls[:a.limit or None]:
        slug, place, ident = parts(u)
        print(json.dumps({"url": u, "id": ident,
                          "ledger_id": f"infoempleo:{ident}",
                          "place_from_url": place, "slug": slug},
                         ensure_ascii=False))
    note(f"{min(len(urls), a.limit or len(urls))} ad URLs. The sitemap has no "
         "lastmod, so dates cost a fetch — see search --desde.")


def cmd_search(a):
    urls = entries()
    note(f"{len(urls)} ads in the offers sitemap")
    urls = narrow(urls, a)
    kept = gone = skipped_old = 0
    for u in urls:
        if a.limit and kept >= a.limit:
            break
        c = card(u)
        if c.get("expired"):
            gone += 1
            time.sleep(a.delay)
            continue
        if a.desde and (c.get("published") or "") < a.desde:
            skipped_old += 1
            time.sleep(a.delay)
            continue
        print(json.dumps(c, ensure_ascii=False))
        kept += 1
        time.sleep(a.delay)
    note(f"{kept} ads returned")
    if gone:
        note(f"{gone} were already gone — ld+json present but no JobPosting "
             "among the blocks. The sitemap is called 'ofertas-activas' and "
             "is not perfect; measured at 1 in 45.")
    if skipped_old:
        note(f"{skipped_old} were older than --desde. That filter costs a "
             "fetch each: the sitemap carries no lastmod, so the date is only "
             "known once the ad is read.")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("lugares", help="the places the sitemap uses, with "
                                       "ad counts. Free")
    c.add_argument("--limit", type=int)
    c.set_defaults(func=cmd_lugares)

    for name, fn, h in (("discover", cmd_discover, "ad URLs only"),
                        ("search", cmd_search, "read the ads")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--lugar", help="place as written in the URL — madrid, "
                                       "barcelona, multiprovincia. **Free**: "
                                       "matched before any fetch. `lugares`")
        c.add_argument("--limit", type=int)
        if name == "search":
            c.add_argument("--desde", metavar="YYYY-MM-DD",
                           help="datePosted >= this date. Costs a fetch per "
                                "ad: the sitemap has no lastmod")
            c.add_argument("--delay", type=float, default=0.6)
        c.set_defaults(func=fn)

    a = p.parse_args()
    if a.cmd == "search" and not (a.lugar or a.limit or a.desde):
        die("give --lugar, --limit or --desde. Without one the sweep reads "
            "all 7 621 ads, one request each.")
    a.func(a)


if __name__ == "__main__":
    main()
