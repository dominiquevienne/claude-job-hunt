#!/usr/bin/env python3
"""Fetch Saudi ads from Mihnati — **17 from the home page, and that is not the
board.**

Mihnati is a Saudi job board running on Rozee's platform, and the platform
shows through in ways that matter. `robots.txt` closes 17 path families and
leaves the English site open; **the Arabic one is refused** — `Disallow: /ar/`
and `/EN/ar/` — along with `/hiring/`, `/people/`, `/UR/` and `/ZH/`.

  GET /EN/                          → 17 advertisements, server-rendered
  GET /EN/<slug>-jobs-<id>          → one advertisement, with `JobPosting`

**THE LISTING IS THE ONLY THING THAT IS SERVER-RENDERED, AND IT IS A STRIP.**
`/EN/category/<x>`, `/EN/channel/<x>`, `/EN/search/<x>` and `/EN/job/jsearch/`
all answer 200 with 200-460 kB and **zero advertisement links**: the results
are drawn by script. So `latest` returns the seventeen the home page carries
and **says they are seventeen**, not a total. Reading the rest needs a browser,
and this adapter does not pretend otherwise.

THREE THINGS THE `JobPosting` GETS WRONG, ALL MEASURED ON TEN OF TEN ADS,
2026-09-03:

**1. The currency is `PKR` on Saudi jobs.** Ten of ten — Jeddah, Riyadh,
Dammam, `addressCountry: SA` — carry `baseSalary.currency: "PKR"`. Pakistani
rupees, from the Pakistani platform underneath (the same one named in this
host's own `robots.txt`: `/rozee-a/`, `/rozee-b/`). **A row that copied that
field would price a Saudi salary in the wrong currency by a factor of about
seventy.** So `salary_currency_disagrees_with_country` travels beside it, and
the figure is never converted — **guessing the intended currency would be a
second invention on top of the first.**

**2. `identifier` is the employer's name, not an identifier.** Ten of ten:

    "identifier": {"@type": "PropertyValue", "name": "Ansaaj"}

The schema.org field for the posting's id holds the company. **An adapter
reading it as an id would key every advertisement by its employer**, and two
jobs at one company would collide in a ledger. The id here is the number at
the end of the URL, and nothing else is used.

**3. Every page carries the `JobPosting` twice.** Ten of ten, byte-identical.
`_ldjson.postings()` returns both, correctly — it is reporting what is there —
so this script takes the first and **counts the duplication rather than
letting it double a total**.

THE 404 ANNOUNCES ITSELF IN THE QUERY STRING. `/jobs` and `/sitemap.xml`
answer **200** after redirecting to `/site/error?e=cnf_jobs` and
`?e=cnf_sitemap.xml`. Another *200 with the wrong body* — but this one is
checkable without guessing, because the final URL names the missing
controller.

Verified against the live site on **2026-09-03**.
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request

from _decode import decode_body
from _ldjson import label, one, postings
from _robots import allowed as robots_allowed
from _zero import zero_note

BASE = "https://www.mihnati.com"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

EXIT_BROKEN, EXIT_GONE, EXIT_REFUSED, EXIT_UNKNOWN = 2, 3, 7, 8

SLUG = re.compile(r"/EN/([a-z0-9-]+-jobs-(\d+))")
NOT_FOUND = re.compile(r"/site/error\?e=cnf_")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[mihnati] {msg}", file=sys.stderr)


def gate(path):
    """Per path, because this host refuses families rather than the site.

    `/ar/` and `/EN/ar/` are closed — **the Arabic board is refused while the
    English one is open** — and so are `/hiring/`, `/people/`, `/UR/`, `/ZH/`.
    A host-level check would have missed every one of them.
    """
    a = robots_allowed("www.mihnati.com", path)
    if a["allowed"] is None:
        die(f"www.mihnati.com{path}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"www.mihnati.com{path}: {a['reason']}", EXIT_REFUSED)
    return a


def get(path):
    url = path if path.startswith("http") else BASE + path
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            landed = r.geturl()
            if NOT_FOUND.search(landed):
                # A 200 that is the site's own not-found page. It names the
                # missing controller in the query string, so this needs no
                # guessing at body shapes.
                return 404, "", landed
            return r.getcode(), decode_body(r.read(), r.headers)[0], landed
    except urllib.error.HTTPError as e:
        return e.code, "", url
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def address_of(posting):
    place = one(posting.get("jobLocation"))
    addr = one(place.get("address")) if place else {}
    country = addr.get("addressCountry")
    if isinstance(country, dict):
        country = country.get("name")
    return addr, country


def card(posting, url, ident, duplicated):
    addr, country = address_of(posting)
    salary = one(posting.get("baseSalary"))
    value = one(salary.get("value")) if salary else {}
    currency = salary.get("currency") if salary else None
    # **The platform's currency, not the job's.** Ten of ten Saudi ads say
    # PKR. The field is emitted as published and flagged, never corrected:
    # inventing the intended currency would be a second invention.
    mismatch = bool(currency and country and (
        (country == "SA" and currency != "SAR")))
    # **Count on the figure, not on the field.** `baseSalary.value.value` is
    # populated on every advertisement and reads `Confidential` when nothing
    # was published — the same shape as EmployTT's `Concealed`, and the same
    # trap: a key that is always present is not a rate of disclosure.
    figure = str(value.get("value") or "").strip()
    stated = bool(re.search(r"\d", figure))
    return {
        "id": ident,
        "ledger_id": f"mihnati:{ident}",
        "url": url,
        "title": posting.get("title"),
        "company": label(posting.get("hiringOrganization")),
        # **Never `identifier`** — see the header; it holds the employer name.
        "identifier_field_holds_the_employer": label(
            posting.get("identifier")),
        "location_text": (addr.get("addressLocality")
                          or addr.get("streetAddress") or None),
        "region": (addr.get("addressRegion") or "").strip() or None,
        "country": country,
        "employment_type": (posting.get("employmentType") or "").strip()
                           or None,
        "posted": posting.get("datePosted"),
        "valid_through": posting.get("validThrough"),
        "salary_unit": (value.get("unitText") or "").strip() or None,
        "salary_currency": currency,
        "salary_currency_disagrees_with_country": mismatch,
        "salary_text": figure or None,
        "salary_stated": stated,
        "description_chars": len(posting.get("description") or ""),
        "jobposting_blocks": duplicated,
    }


def read_ad(url, with_text=False):
    path = url[len(BASE):] if url.startswith(BASE) else url
    gate(path)
    code, body, landed = get(url)
    if code != 200:
        die(f"{url}: HTTP {code} (landed on {landed})", EXIT_GONE)
    found = postings(body)
    if not found:
        die(f"{url}: no JobPosting in the page. Every advertisement measured "
            f"carried one — twice — so this is a shape change, not an empty "
            f"advertisement.")
    m = SLUG.search(url)
    row = card(found[0], url, m.group(2) if m else None, len(found))
    if with_text:
        row["description"] = found[0].get("description")
    return row


def cmd_latest(a):
    gate("/EN/")
    code, body, _landed = get("/EN/")
    if code != 200:
        die(f"{BASE}/EN/: HTTP {code}")
    slugs = []
    for slug, ident in SLUG.findall(body):
        if (slug, ident) not in slugs:
            slugs.append((slug, ident))
    if not slugs:
        note(zero_note("mihnati"))
        return
    kept, mismatched, duplicated, salaried = 0, 0, 0, 0
    for slug, _ident in slugs[:a.limit] if a.limit else slugs:
        row = read_ad(f"{BASE}/EN/{slug}", a.with_text)
        print(json.dumps(row, ensure_ascii=False))
        kept += 1
        mismatched += bool(row["salary_currency_disagrees_with_country"])
        duplicated += row["jobposting_blocks"] > 1
        salaried += bool(row["salary_stated"])
        time.sleep(a.delay)
    note(f"{kept} advertisement(s) — **the home page's strip, not the "
         f"board.** The category, channel and search routes answer 200 with "
         f"no advertisement link in the markup: they draw their results by "
         f"script, so reading them needs a browser. {len(slugs)} slugs were "
         f"on the page.")
    note(f"salary: {salaried} of {kept} carry a figure. The rest read "
         f"`Confidential`, which is the board's own word — the field itself "
         f"is present on every advertisement, so counting keys would have "
         f"reported 100%.")
    if mismatched:
        note(f"**{mismatched} of {kept} price a Saudi salary in a currency "
             f"that is not SAR** — the platform underneath is Pakistani and "
             f"publishes `PKR`. The field is passed through as published and "
             f"flagged; **no figure was converted**, because guessing the "
             f"intended currency would be a second invention on top of the "
             f"first.")
    if duplicated:
        note(f"{duplicated} of {kept} pages carry the `JobPosting` twice. "
             f"Counted, not doubled.")



def cmd_ad(a):
    row = read_ad(a.url, a.with_text)
    print(json.dumps(row, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("latest", help="the home page's advertisement strip")
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=0.8)
    s.add_argument("--with-text", action="store_true", dest="with_text")
    s.set_defaults(func=cmd_latest)

    d = sub.add_parser("ad", help="read one advertisement by URL")
    d.add_argument("--url", required=True)
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
