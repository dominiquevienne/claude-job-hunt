#!/usr/bin/env python3
"""Fetch French ads from hays.fr — a specialist recruiter, not an interim network.

**3 193 ads** from the job sitemap the site's `robots.txt` declares. Smaller
than `crit.md` (16 175), `adecco.md` (13 293) and `randstad-fr.md` (6 755), and
a **different population**: qualified profiles — finance, audit, IT,
engineering, construction management — where the other three carry production,
logistics and warehouse work.

  GET /robots.txt                        → Sitemap: …/sitemap/fr-FR/job-sitemap.xml
  GET /sitemap/fr-FR/job-sitemap.xml     → 3 193 ads, with per-ad lastmod
  GET /description-emploi/<slug>_<id>    → the ad, JSON-LD JobPosting

**The `<loc>` elements are wrapped in CDATA** — see `locs`. That single detail
is worth more than this board.

Usage:
  hays.py discover --since 2026-08-25
  hays.py search --lieu paris --limit 20
  hays.py search --since 2026-09-01

Output: one JSON object per line.
"""

import argparse
import html as html_mod
import json
import re

from _decode import decode_body
from _ldjson import absent_reason, one, postings
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _robots import allowed as robots_allowed

BASE = "https://www.hays.fr"
SITEMAP = BASE + "/sitemap/fr-FR/job-sitemap.xml"
from _ua import UA, browser_fallback
URL_BLOCK_RE = re.compile(r"(?s)<url>(.*?)</url>")
# **A `<loc>` can be wrapped in CDATA**, and this one is:
#
#     <loc>
#           <![CDATA[ https://www.hays.fr/description-emploi/… ]]>
#     </loc>
#
# The usual `<loc>\s*([^<\s]+)` matches **nothing at all** here, because the
# first non-space character after the tag is `<`. On a 2.37 MB, valid, 200-OK
# sitemap it returns zero URLs — a board that appears to publish nothing.
#
# What exposed it was arithmetic, not the code: the same file yielded **3 193
# `<lastmod>` and 0 `<loc>`**. A sitemap with dates and no URLs is impossible,
# so the reader was wrong. Had the file carried neither, "Hays publishes an
# empty sitemap" would have been written down and published.
LOC_RE = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?\s*([^\s\]<]+)")
MOD_RE = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?\s*([^\s\]<]+)")
AD_RE = re.compile(r"/description-emploi/(.+)$")


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



def fold(s):
    s = unicodedata.normalize("NFKD", urllib.parse.unquote(s or "").lower())
    return re.sub(r"[^a-z0-9]", "", s.encode("ascii", "ignore").decode())


def get(url, gone_is_ok=False, retries=2):
    _robots_gate(url, 'hays')
    p = urllib.parse.urlsplit(url)
    safe = urllib.parse.urlunsplit(
        (p.scheme, p.netloc, urllib.parse.quote(p.path, safe="/%"),
         p.query, p.fragment))
    req = urllib.request.Request(safe, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "fr-FR,fr;q=0.9",
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return decode_body(r.read(), r.headers)[0]
        except urllib.error.HTTPError as e:
            if gone_is_ok and e.code in (404, 410):
                # Retired ads answer an honest 410. Seven of the 3 193 in the
                # sitemap were pre-2026 and every one tested was gone.
                return None
            if e.code in (403, 429):
                die(*browser_fallback("www.hays.fr", True, e.code, url))
            die(f"hays.fr returned HTTP {e.code} for {url}")
        except Exception as e:  # noqa: BLE001 - network shape varies
            if attempt == retries:
                die(f"could not reach hays.fr: {e}")
            time.sleep(2.0)
    return ""


def entries():
    page = get(SITEMAP)
    blocks = URL_BLOCK_RE.findall(page)
    if not blocks:
        die(f"{SITEMAP} parsed to zero <url> blocks out of {len(page)} "
            "characters — a read failure, not an empty board.")
    out = []
    for b in blocks:
        loc = LOC_RE.search(b)
        if not loc:
            continue
        mod = MOD_RE.search(b)
        out.append((loc.group(1), mod.group(1) if mod else None))
    if not out:
        die(f"{SITEMAP} held {len(blocks)} <url> blocks and no readable "
            "<loc>. Check the CDATA handling before believing the board is "
            "empty — see the comment on LOC_RE.")
    return out


def slug_tail(url):
    """The place written at the end of the slug, before the numeric id.

    `…-gestionnaire-formation-h-f-loire-atlantique_1453408` → the tail is what
    the ad calls its location, and it matches `addressLocality` — but see the
    doc: that field holds a town, a department or a region depending on the ad.
    """
    m = AD_RE.search(url)
    if not m:
        return None
    return urllib.parse.unquote(m.group(1)).rsplit("_", 1)[0]


def text_of(raw):
    if not raw:
        return None
    t = html_mod.unescape(raw)
    t = re.sub(r"(?i)<br\s*/?>|</p>|</li>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html_mod.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip() or None


def card(url, lastmod):
    page = get(url, gone_is_ok=True)
    ident = url.rstrip("/").rsplit("_", 1)[-1]
    if page is None:
        return {"id": ident, "ledger_id": f"hays-fr:{ident}", "url": url,
                "gone": True}
    # One reader for every board's ld+json: tolerant of the quote style
    # on the script tag, and strict=False on the parse. Issue #76.
    jp = (postings(page) or [None])[-1]
    if jp is None:
        # **Whose failure is this?** `absent_reason` answers it instead of
        # letting the sentence imply the board. A block that is present and
        # unreadable, or a page that says JobPosting and yields none, is our
        # bug and exits loudly; a page with no structured data is a fact about
        # the page. Issue #76.
        why = absent_reason(page)
        if why.our_fault:
            die(f"{url}: {why.text}")
        return {"id": ident, "ledger_id": f"hays-fr:{ident}", "url": url,
                "json_ld": False}
    addr = one(jp.get("jobLocation")).get("address") or {}
    # **The pay is in `baseSalary.value.value`, as prose** — not in `minValue`
    # / `maxValue`, where adecco, randstad-fr and crit all put theirs. Reading
    # only those sub-fields reports "no salary" on a board that states one on
    # every ad. `incentiveCompensation` repeats the same string.
    sal = one(jp.get("baseSalary")).get("value") or {}
    pay = sal.get("value") or jp.get("incentiveCompensation")
    post = addr.get("postalCode")
    return {
        "id": ident,
        "ledger_id": f"hays-fr:{ident}",
        "url": url,
        "reference": jp.get("identifier"),
        "title": jp.get("title"),
        # "Hays" on every ad. A specialist recruiter: the client is described
        # and never named.
        "company": one(jp.get("hiringOrganization")).get("name"),
        "employer_is_the_agency": True,
        # A town, a department or a region depending on the ad — "Paris",
        # "Loire-Atlantique", "Nord Pas-de-Calais". Not a granularity you can
        # assume.
        "location_text": addr.get("addressLocality"),
        "region": addr.get("addressRegion"),
        # The literal string "NA" on every ad measured. Emitted as None so it
        # cannot be mistaken for a postcode, and kept below so nobody
        # rediscovers it.
        "postcode": None if (post or "").strip().upper() == "NA" else post,
        "postcode_field_literal": post,
        "country": addr.get("addressCountry"),
        "employment_type": jp.get("employmentType"),
        # Real sectors — "Cabinet d'Audit et d'Expertise comptable",
        # "Construction, Bâtiment & Travaux Publics".
        "industry": jp.get("industry"),
        "salary_text": pay,
        "salary_currency": one(jp.get("baseSalary")).get("currency"),
        "published": jp.get("datePosted"),
        # datePosted + 90 days, measured at 89, 90 or 91 across 14 ads —
        # a formula, not a deadline.
        "valid_through_formula": jp.get("validThrough"),
        "lastmod": lastmod,
        "description": text_of(jp.get("description")),
        "json_ld": True,
    }


def narrow(rows, a):
    if a.lieu:
        want = fold(a.lieu)
        before = len(rows)
        rows = [r for r in rows if want in fold(slug_tail(r[0]) or "")]
        print(f"[hays] {len(rows)} of {before} match --lieu {a.lieu!r} in the "
              "slug, filtered before any fetch", file=sys.stderr)
    if a.since:
        before = len(rows)
        rows = [r for r in rows if (r[1] or "") >= a.since]
        print(f"[hays] {len(rows)} of {before} since {a.since}",
              file=sys.stderr)
    return rows


def cmd_discover(a):
    rows = narrow(entries(), a)
    for url, mod in rows[:a.limit or None]:
        ident = url.rstrip("/").rsplit("_", 1)[-1]
        print(json.dumps({"url": url, "id": ident,
                          "ledger_id": f"hays-fr:{ident}",
                          "place_from_url": slug_tail(url), "lastmod": mod},
                         ensure_ascii=False))
    print(f"[hays] {min(len(rows), a.limit or len(rows))} ad URLs",
          file=sys.stderr)


def cmd_search(a):
    rows = entries()
    print(f"[hays] {len(rows)} ads in the sitemap", file=sys.stderr)
    rows = narrow(rows, a)
    kept, gone = 0, 0
    for url, mod in rows:
        if a.limit and kept >= a.limit:
            break
        c = card(url, mod)
        if c.get("gone"):
            gone += 1
            time.sleep(a.delay)
            continue
        print(json.dumps(c, ensure_ascii=False))
        kept += 1
        time.sleep(a.delay)
    print(f"[hays] {kept} ads returned", file=sys.stderr)
    if gone:
        print(f"[hays] {gone} were already gone — the sitemap keeps a handful "
              "of pre-2026 entries and the site answers 410 for them",
              file=sys.stderr)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, h in (("discover", cmd_discover, "ad URLs only"),
                        ("search", cmd_search, "read the ads")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--lieu", help="place as written in the slug — paris, "
                                      "loire-atlantique. Free")
        c.add_argument("--since", help="lastmod >= this ISO date")
        c.add_argument("--limit", type=int)
        if name == "search":
            c.add_argument("--delay", type=float, default=0.5)
        c.set_defaults(func=fn)
    a = p.parse_args()
    if a.cmd == "search" and not (a.lieu or a.since or a.limit):
        die("give --lieu, --since or --limit. Without one the sweep reads all "
            "3 193 ads.")
    a.func(a)


if __name__ == "__main__":
    main()
