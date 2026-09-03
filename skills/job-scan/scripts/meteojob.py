#!/usr/bin/env python3
"""Fetch job ads from meteojob.com, a French generalist board.

Meteojob is one of France's larger generalist boards, and it also feeds France
Travail — 30 of 150 sampled partner ads in Paris came from it. This adapter
reads the ads on Meteojob itself, where the employer is named and the ad
carries a stated expiry date, neither of which survives the France Travail
route.

**Read `shared/boards/meteojob.md` before changing anything here.** The site's
robots.txt disallows `/api/` and `/jobsearch/api/`, and disallows every
query-string URL except an explicit `Allow: /jobs?*`. So this adapter uses
`/jobs?what=&where=` and `/jobs/<id>` and nothing else — which costs it
pagination, because pages 2+ exist only behind the disallowed API. **One search
is 20 ads, and that is the whole board this adapter can see.** Never add a call
to `/jobsearch/api/` to get past it; run more, narrower searches instead.

Usage:
  meteojob.py search --what "infirmier" --where "Lyon"
  meteojob.py search --what "développeur" --where "Paris" --with-detail
  meteojob.py ad <id>

Output: one JSON object per line (search), or one JSON object (ad).
"""

import argparse
import html
import json
import re

from _decode import decode_body
from _ldjson import absent_reason, one, postings
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _robots import allowed as robots_allowed

SEARCH = "https://www.meteojob.com/jobs"
AD_URL = "https://www.meteojob.com/jobs/{}"
from _ua import UA
# One search page serves exactly this many, and there is no allowed way to ask
# for more. See the module docstring.
PAGE_ADS = 20

# The card container. Deliberately matched on the stable class only: every tag
# on this page also carries an `_ngcontent-candidate-front-c752671492`
# attribute whose hash changes with every front-end deploy, so anchoring on it
# would break the adapter on a release that changed nothing visible.
CARD_RE = re.compile(r'<article[^>]*cc-job-offer-list-item__card')
ID_RE = re.compile(r'href="/jobs/(\d+)"')
TITLE_RE = re.compile(r'<a[^>]*cc-job-offer-list-item__link[^>]*>([^<]+)<')
COMPANY_RE = re.compile(r'<p[^>]*class="d-inline-block mt-1 mb-2[^"]*"[^>]*>([^<]+)<')
BADGE_RE = re.compile(r'<div[^>]*class="cc-badge[^"]*"[^>]*>([^<]+)<')
AGE_RE = re.compile(r'<div[^>]*class="cc-font-size-small mt-1[^"]*"[^>]*>([^<]+)<')
# "Lyon (69)". The location badge is keyed by the ad's own id, which is a far
# steadier hook than its classes. Its text sits *after* a <mat-icon> whose own
# text is the icon's ligature name — so a naive capture yields "place", the
# icon, not the town. ICON_RE removes the icon element before the tags are
# stripped. (This is also why BADGE_RE never mistakes the location for a
# contract: its first child is that icon, not text.)
PLACE_RE = re.compile(r'id="\d+-job-locations"[^>]*>(.*?)</div>', re.S)
ICON_RE = re.compile(r'<mat-icon\b.*?</mat-icon>', re.S)


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
        print(f"[meteojob] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts. A platform that has "
              f"been renamed reaches an adapter this way before it reaches it "
              f"as a rename.", file=__import__("sys").stderr)
    return a



def fetch(url):
    _robots_gate(url, 'meteojob')
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "fr-FR,fr;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            # Measured: a withdrawn ad answers 410 Gone, not 404. Handling
            # only 404 turns a normal, expected outcome into a hard error.
            die(f"that ad is no longer on Meteojob (HTTP {e.code}) — record it "
                "as discarded, do not retry.", code=3)
        if e.code in (403, 429):
            die(f"Meteojob answered HTTP {e.code}. Stop and wait; do not "
                "retry in a loop and do not change the User-Agent to get "
                "around it.")
        die(f"Meteojob returned HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach Meteojob: {e}")


def clean(s):
    if s is None:
        return None
    s = html.unescape(s).replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip() or None


def to_text(markup):
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", markup or "")
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", txt)
    txt = re.sub(r"(?i)<li[^>]*>", "- ", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt).replace(" ", " ")
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", txt).strip()


def split_cards(page):
    starts = [m.start() for m in CARD_RE.finditer(page)]
    return [page[a:b] for a, b in zip(starts, starts[1:] + [len(page)])]


def card_from_listing(block):
    m = ID_RE.search(block)
    if not m:
        return None
    ident = m.group(1)
    badges = [clean(b) for b in BADGE_RE.findall(block)]
    # The contract badge is a short code (CDI, CDD, Intérim…); the pay badge
    # always carries a currency. Split on that rather than on badge order,
    # which varies with whether a salary was published at all.
    salary = next((b for b in badges if b and "€" in b), None)
    contract = next((b for b in badges if b and "€" not in b), None)

    def first(rx):
        m = rx.search(block)
        return clean(m.group(1)) if m else None

    def place():
        m = PLACE_RE.search(block)
        if not m:
            return None
        return clean(re.sub(r"<[^>]+>", " ", ICON_RE.sub(" ", m.group(1))))

    return {
        "id": ident,
        "ledger_id": f"meteojob:{ident}",
        "url": AD_URL.format(ident),
        "title": first(TITLE_RE),
        "company": first(COMPANY_RE),
        "location": place(),
        "contract": contract,
        "salary": salary,
        "posted_age": first(AGE_RE),
    }


def job_posting(page):
    # One reader for every board's ld+json: tolerant of the quote style
    # on the script tag, and strict=False on the parse. Issue #76.
    for d in postings(page):
        return d
    return None


def card_from_ad(ident, page):
    d = job_posting(page)
    if not d:
        why = absent_reason(page)
        die(f"no JobPosting block on /jobs/{ident} — {why.text} Either the ad "
            f"is gone and the site served a soft landing page, or the markup "
            f"changed; report it with board-request rather than guessing at "
            f"selectors.", code=2 if why.our_fault else 3)
    org = d.get("hiringOrganization") or {}
    addr = one(d.get("jobLocation")).get("address") or {}
    sal = d.get("baseSalary") or {}
    val = sal.get("value") or {}
    ident_field = d.get("identifier") or {}
    emp = d.get("employmentType")
    return {
        "id": ident,
        "ledger_id": f"meteojob:{ident}",
        "url": AD_URL.format(ident),
        "title": clean(d.get("title")),
        "company": clean(org.get("name")),
        "company_url": org.get("sameAs"),
        "city": clean(addr.get("addressLocality")),
        "region": clean(addr.get("addressRegion")),
        "postal_code": clean(addr.get("postalCode")),
        "country": addr.get("addressCountry"),
        # schema.org's time-basis vocabulary (FULL_TIME, TEMPORARY…), which
        # is NOT the French contract type. The listing card's "CDI" / "CDD" is
        # the useful one, so this gets its own key rather than overwriting it
        # when the two are merged by --with-detail.
        "employment_type": ", ".join(emp) if isinstance(emp, list) else emp,
        # Usually a min/max pair; a flat `value` is the exception (hourly ads).
        # `unitText` was absent on 5 of 6 ads sampled, so the period is often
        # simply unstated — do not assume "per year" because the figure is big.
        "salary_min": val.get("minValue"),
        "salary_max": val.get("maxValue"),
        "salary_value": val.get("value"),
        "salary_unit": val.get("unitText"),
        "salary_currency": sal.get("currency"),
        "industry": clean(d.get("industry")),
        "category": clean(d.get("occupationalCategory")),
        "published": d.get("datePosted"),
        # Meteojob states an expiry on its ads, which most boards do not. It
        # answers "is this still open?" with no request at all.
        "expires": d.get("validThrough"),
        # False on every ad sampled: applying happens off Meteojob.
        "direct_apply": d.get("directApply"),
        "employer_reference": ident_field.get("value"),
        "description": to_text(d.get("description")),
    }


def cmd_search(a):
    qs = urllib.parse.urlencode({"what": a.what or "", "where": a.where or ""})
    page = fetch(f"{SEARCH}?{qs}")
    blocks = split_cards(page)
    if not blocks:
        print("[meteojob] no result cards on the page. That is either a search "
              "with no matches or a markup change — the two look identical "
              "here, so check the query in a browser before concluding the "
              "market is empty.", file=sys.stderr)
        return
    rows = 0
    for b in blocks:
        c = card_from_listing(b)
        if not c:
            continue
        if a.with_detail:
            time.sleep(a.delay)
            c = {**c, **card_from_ad(c["id"], fetch(c["url"]))}
        print(json.dumps(c, ensure_ascii=False))
        rows += 1
    print(f"[meteojob] {rows} cards returned", file=sys.stderr)
    if rows >= PAGE_ADS:
        print(f"[meteojob] that is the cap, not the result count: one search "
              f"serves {PAGE_ADS} ads and the site's robots.txt puts pages 2+ "
              "behind a disallowed API. There are almost certainly more "
              "matches than these — narrow the search (a tighter --what, a "
              "smaller --where) and run it again rather than treating this as "
              "the whole market.", file=sys.stderr)


def cmd_ad(a):
    print(json.dumps(card_from_ad(a.id, fetch(AD_URL.format(a.id))),
                     ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="one search, 20 ads")
    s.add_argument("--what", help="keywords, job title")
    s.add_argument("--where", help="town, department or region")
    s.add_argument("--with-detail", action="store_true",
                   help="also read each ad page for the description and the "
                        "stated expiry date — 20 extra requests")
    s.add_argument("--delay", type=float, default=1.0,
                   help="seconds between ad reads (default 1)")
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="read one ad in full")
    d.add_argument("id")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    if a.cmd == "search" and not (a.what or a.where):
        die("give --what, --where, or both. An empty search returns the site's "
            f"generic front page of {PAGE_ADS} ads, which is not a sweep.")
    a.func(a)


if __name__ == "__main__":
    main()
