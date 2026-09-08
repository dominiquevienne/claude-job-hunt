#!/usr/bin/env python3
"""Albedis (`www.albedis.com`) — a Swiss agency, and its JSON-LD does not parse.

  albedis.py sitemap [--lang fr] [--limit N]
  albedis.py ad --url <advertisement URL>

**Every advertisement carries a `JobPosting`, and a plain `json.loads` reads
none of them.** #189 recorded the host as unstructured for that reason: a parse
failure was read as an absence, and a fully structured site was reported as one
to be scraped from markup. The malformation is a TYPE confusion — a JSON array
serialised into a string and emitted unescaped — and `_ldjson` mends it since
`ed57b58`. Nothing here re-implements that: this adapter calls `postings()` and
`absent_reason()` and lets the module answer.

  **A parse failure is INDETERMINATE, never ABSENT.** `absent_reason()` says
  whose fault an empty result is, and a page that announces a `JobPosting` and
  yields none exits loudly rather than emitting a row.

THE SITEMAP IS THE ROUTE, AND EVERY ADDRESS COMES FROM IT

`sitemap_jobs0.xml` holds 380 `<loc>` — 95 advertisements, each published in
four languages, 95 x 4 = 380 exactly (2026-09-08).

  /emploi/<id>-<slug>-fr/               /jobs/<id>-<slug>-en/
  /stellenangebot/<id>-<slug>-de/       /annuncio-di-lavoro/<id>-<slug>-it/

**The language is the path SEGMENT, not a prefix, and the id is at the HEAD of
the slug.** Both were got wrong before being measured.

**NO URL IS EVER COMPOSED HERE.** Addresses are served from the sitemap as they
are found. On a neighbouring host a composed address answered HTTP 200 and led
nowhere, which is indistinguishable from a live link and would have reached the
ledger.

AND `95 x 4 = 380` IS NOT AN ANCHOR

It checks the sitemap against ITSELF. A partition of one's own output is an
arithmetic identity: it cannot fail while the reading fails. **This site
declares no running total anywhere this adapter looked**, so there is nothing
external to check the count against, and that gap is stated rather than papered
over with the multiplication.

*And if a total did appear, it would still have to be shown to count
ADVERTISEMENTS: on `xpress.jobs` the board's own `recordCount` is a true
external figure and counts row slots, not advertisements.*

THE EMPLOYER IS NOT IN `hiringOrganization`

It reads `albedis` on every advertisement measured, and the descriptions say
*"Notre client, acteur majeur du secteur de la construction"* — the end employer
is deliberately unnamed. The field is emitted as `depositor`, which is what it
is. **On other hosts the same field IS the employer**, so it is carried rather
than dropped, under a name that does not assert what it does not know.

THE LEDGER KEY IS THE NUMERIC URL ID

Two identifiers coexist and both are stable across the four languages: the URL
id, and `identifier.value` reading `INT-…`. The `INT-` form has **two lengths**
— `INT-121357` and `INT-4163915104116` — so a parser assuming six digits
breaks. The numeric id is the key; `INT-` travels beside it because it is the
reference a recruiter quotes.

MEASURED ON FOUR ADVERTISEMENTS OF 95, and that is written on the card too.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _ldjson import absent_reason, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _sitemap import locs as sitemap_locs
from _ua import UA

BASE = "https://www.albedis.com"
SITEMAP = BASE + "/sitemap_jobs0.xml"

# The language is the path SEGMENT. Measured 2026-09-08 on all 380 `<loc>`.
LANGS = {"emploi": "fr", "stellenangebot": "de", "jobs": "en",
         "annuncio-di-lavoro": "it"}
# The id is at the HEAD of the slug, not its tail.
AD_RE = re.compile(r"^/(" + "|".join(LANGS) + r")/(\d+)-(.+?)/?$")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[albedis] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# The host declares no `Crawl-delay`; this spacing is ours. **Unlike
# `xpress.jobs` no rate limit was measured here** — 2 s is a default, not a
# margin under a known ceiling, and it is declared as such.
_PACE = Pace("www.albedis.com", own=2.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "fr-CH,fr;q=0.9,de;q=0.8,it;q=0.7,en;q=0.6",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def split_ad(url):
    """(id, lang, url) for an advertisement address, or None."""
    p = urllib.parse.urlsplit(url)
    m = AD_RE.match(p.path)
    if not m:
        return None
    return m.group(2), LANGS[m.group(1)], url


def cmd_sitemap(a):
    code, body = get(SITEMAP)
    if code == 404:
        die(f"{SITEMAP}: HTTP 404 — the advertisement sitemap is gone", EXIT_GONE)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}. **A readable body is not an answer — the "
            f"code decides.**")
    urls = sitemap_locs(body)
    if not urls:
        die(f"{SITEMAP}: {len(body)} characters and no `<loc>`. **This is a "
            f"reading that failed, not an empty sitemap** — a sitemap with no "
            f"URLs does not exist.", EXIT_PARTIAL)

    # **Counted where they are decided.** `matched` and `unmatched` grow in
    # different branches, so their sum is a check and not an identity.
    by_id, matched, unmatched = {}, 0, 0
    for u in urls:
        got = split_ad(u)
        if got is None:
            unmatched += 1
            continue
        matched += 1
        ident, lang, addr = got
        by_id.setdefault(ident, {})[lang] = addr

    for ident, forms in sorted(by_id.items()):
        if a.lang and a.lang not in forms:
            continue
        print(json.dumps({
            "source": "albedis", "country": "CH",
            "ledger_id": f"albedis:{ident}", "id": ident,
            "url": forms.get(a.lang) if a.lang else forms.get("fr"),
            "forms": forms, "languages": sorted(forms),
        }, ensure_ascii=False))

    note(f"{len(urls)} `<loc>`; {matched} matched the advertisement shape and "
         f"{unmatched} did not; {len(by_id)} distinct advertisement id(s).")
    sizes = sorted({len(f) for f in by_id.values()})
    note(f"language forms per advertisement: {sizes} — "
         + ("every advertisement carries the same number of forms."
            if len(sizes) == 1 else "**they differ, so the corpus is uneven.**"))
    note("**No running total is declared by this site**, so nothing external "
         "checks these figures. `95 x 4 = 380` compares the sitemap with "
         "itself and cannot fail while the reading fails.")


def cmd_ad(a):
    got = split_ad(a.url)
    if got is None:
        die(f"{a.url}: not an advertisement address. Expected "
            f"/<{'|'.join(LANGS)}>/<id>-<slug>/ — **the id is at the head of "
            f"the slug and the language is the segment.**")
    ident, lang, _ = got
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer.**")
    found = postings(body)
    if not found:
        why = absent_reason(body)
        if getattr(why, "our_fault", False):
            die(f"{a.url}: {why} **The page announces a JobPosting and this "
                f"read none — that is a misreading here, not a board that "
                f"publishes nothing.**")
        die(f"{a.url}: {why}", EXIT_PARTIAL)
    if len(found) > 1:
        note(f"{len(found)} JobPosting blocks on one page — the container "
             f"bound this adapter relies on has changed. Emitting the first.")
    d = found[0]
    org = (d.get("hiringOrganization") or {})
    ident_obj = d.get("identifier") or {}
    loc = (d.get("jobLocation") or {})
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
    print(json.dumps({
        "source": "albedis", "country": "CH",
        "ledger_id": f"albedis:{ident}", "id": ident, "url": a.url,
        "language": lang,
        "title": d.get("title"),
        # **Not `employer`.** On this host the field names the agency.
        "depositor": org.get("name") if isinstance(org, dict) else None,
        "reference": ident_obj.get("value") if isinstance(ident_obj, dict) else None,
        "locality": addr.get("addressLocality"),
        "region": addr.get("addressRegion"),
        "employment_type": d.get("employmentType"),
        "industry": d.get("industry"),
        "posted": d.get("datePosted"),
        "description_chars": len(d.get("description") or ""),
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description="Swiss advertisements from Albedis, through the sitemap "
                    "it declares and the JSON-LD its pages carry.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="advertisement addresses, one request")
    s.add_argument("--lang", choices=sorted(set(LANGS.values())),
                   help="emit only this language form")
    s.add_argument("--limit", type=int, help=argparse.SUPPRESS)
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one advertisement, read from its JSON-LD")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
