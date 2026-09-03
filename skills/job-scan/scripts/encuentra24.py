#!/usr/bin/env python3
"""Read the jobs section of Encuentra24 — Central American classifieds, twelve
countries on one host.

**Not a job board with a country per domain: one host with a country-and-
language prefix**, `/panama-es/`, `/costa-rica-en/`. So there is no host
enumeration to do, and the prefixes are not guessed — **`robots.txt` names all
twenty-four of them**, one `Disallow` per prefix. Read for permission that is a
list of paths; read for information it is the site's own country list (#74).

  GET /robots.txt                                    → 10 084 bytes, the
                                                       twenty-four prefixes
  GET /<prefix>/empleos-ofertas-de-trabajos          → 20 ads  (Spanish)
  GET /<prefix>/jobs-work-employ-job-offers          → 20 ads  (English)
  GET /<prefix>/<category>/<slug>/<id>               → one ad, with a
                                                       `JobPosting` in JSON-LD

**PAST THE LAST PAGE IT SERVES PAGE ONE, WITH `200`.** Measured on Panama,
2026-09-03: pages 1, 2 and 3 are disjoint — 60 distinct ads — and **pages 50
and 500 return page 1's twenty ads exactly**. Binary search puts the last real
page at **30**, about 600 ads.

An adapter that trusts the status code paginates for ever **and re-emits page
one's ads as new at every page past the end**. So `search` compares every page
against the first and stops when they match, which is `philjobnet.py`'s rule
arriving through a different door: *a page that answered 200 has not
necessarily advanced.*

THE PAGINATION IS A PATH, AND THE SITE SAYS SO ITSELF. `?page=2` answers
**308** with `Location: …/empleos-ofertas-de-trabajos.2?page=2`. **The redirect
is the documentation** — the shape is `<category>.<n>`.

TWO NAMES THAT LOOK RIGHT AND ARE NOT:

- **`/panama-es/trabajos` and `/panama-es/empleo` both answer `200`** with
  ~97 KB titled *"Últimas novedades en Panamá"* — the site's generic latest
  listings, not the jobs section. Only `empleos` reaches jobs, and only
  `empleos-ofertas-de-trabajos` reaches the offers.
- **The category slug is language-specific and not a translation pair**:
  `empleos-ofertas-de-trabajos` under `-es`, `jobs-work-employ-job-offers`
  under `-en`. `jobs-job-offers`, the obvious guess, **redirects to the site
  root** — a guessed name that answers, which is worse than one that does not.

AND THE PREFIXES ARE NOT SYMMETRIC. `dominican-en` sits beside
`dominicana-es`, and `spain-en` beside `espana-es`. **A reader that pairs
`<country>-es` with `<country>-en` loses both**, which is why they are read
from the file rather than composed.

`baseSalary` IS FREE TEXT, NOT AN AMOUNT — `"Salario más bono $$"` on the
measured ad. It is emitted as `salary_text` and nothing computes on it.

Verified against the live site on **2026-09-03**.
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _ldjson import label, one, postings
from _robots import verdict as robots_verdict
from _zero import zero_note

BASE = "https://www.encuentra24.com"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL, EXIT_REFUSED = 2, 3, 6, 7

# The offers category, by the prefix's language. **Not a translation pair** —
# see the header; `jobs-job-offers` redirects to the site root.
CATEGORY = {"es": "empleos-ofertas-de-trabajos",
            "en": "jobs-work-employ-job-offers"}

# Measured 2026-09-03 by reading robots.txt, and kept only as a fallback for a
# run that cannot fetch it. `prefixes` re-reads the file every time.
KNOWN_PREFIXES = (
    "chile-en", "chile-es", "colombia-en", "colombia-es", "costa-rica-en",
    "costa-rica-es", "dominican-en", "dominicana-es", "el-salvador-en",
    "el-salvador-es", "espana-es", "guatemala-en", "guatemala-es",
    "honduras-en", "honduras-es", "nicaragua-en", "nicaragua-es", "panama-en",
    "panama-es", "paraguay-en", "paraguay-es", "puerto-rico-en",
    "puerto-rico-es", "spain-en",
)

PREFIX_RE = re.compile(r"^Disallow:\s*/([a-z]+(?:-[a-z]+)*-(?:es|en))/", re.M)
AD_RE = re.compile(r"/(?P<prefix>[a-z-]+)/(?P<cat>[a-z0-9-]+)/"
                   r"(?P<slug>[a-z0-9-]+)/(?P<id>\d{5,})")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[encuentra24] {msg}", file=sys.stderr)


def get(path, timeout=45):
    url = path if path.startswith("http") else BASE + path
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        # Without these the same URL answers 403 — header sniffing, and
        # nothing in robots.txt refuses the path.
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.getcode(), r.read().decode("utf-8", "replace"), r.geturl()
    except urllib.error.HTTPError as e:
        if e.code == 403:
            die(f"{url}: HTTP 403. This host refuses a request without "
                f"`Accept`/`Accept-Language`; if this script is sending them "
                f"and is still refused, the sniffing changed.", EXIT_REFUSED)
        return e.code, "", url
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def prefixes():
    """The country-and-language prefixes, read from `robots.txt`.

    **Not composed from a country list.** `dominican-en` sits beside
    `dominicana-es` and `spain-en` beside `espana-es`; anything that pairs
    `<country>-es` with `<country>-en` loses both.
    """
    code, body, _ = get("/robots.txt", timeout=25)
    if code != 200 or "Disallow" not in body:
        note(f"robots.txt answered {code} — falling back to the "
             f"{len(KNOWN_PREFIXES)} prefixes measured 2026-09-03. **That "
             f"list is dated and this run did not confirm it.**")
        return list(KNOWN_PREFIXES), False
    found = sorted(set(PREFIX_RE.findall(body)))
    return found, True


def lang_of(prefix):
    return "en" if prefix.endswith("-en") else "es"


# **The two spellings that are one country.** Measured 2026-09-03:
# `dominicana-es` and `dominican-en` return **the same twelve ads**, and
# `panama-es` / `panama-en` the same twenty. The corpus is one; the prefix is
# a language, not a market.
COUNTRY_ALIAS = {"dominican": "dominicana", "spain": "espana"}


def country_of(prefix):
    """The ledger's key, and it must not be the prefix.

    `encuentra24:panama-es:32343238` and `encuentra24:panama-en:32343238` are
    **one advertisement**, and keying on the prefix would put it in the ledger
    twice — the defect just repaired on job-room, arriving by another road.
    """
    base = re.sub(r"-(?:es|en)$", "", prefix)
    return COUNTRY_ALIAS.get(base, base)


def ids_on(html, prefix, cat):
    """Ad ids in document order, deduplicated — **and only this category's**.

    Filtering on the prefix alone is not enough: the English page carries
    links to ads in other categories, and the first version returned **30 ids
    where the Spanish page returned 20**, ten of them not jobs at all.
    """
    out, seen = [], set()
    for m in AD_RE.finditer(html):
        if m.group("prefix") != prefix or m.group("cat") != cat:
            continue
        i = m.group("id")
        if i in seen:
            continue
        seen.add(i)
        out.append((i, m.group("slug"), m.group("cat")))
    return out


def cmd_prefixes(a):
    v = robots_verdict("www.encuentra24.com")
    if not v["sweep"]:
        die(f"www.encuentra24.com: {v['reason']}", EXIT_REFUSED)
    found, live = prefixes()
    print(json.dumps({"read_from_robots": live, "count": len(found),
                      "prefixes": found}, ensure_ascii=False, indent=2))
    if live:
        new = sorted(set(found) - set(KNOWN_PREFIXES))
        gone = sorted(set(KNOWN_PREFIXES) - set(found))
        if new or gone:
            note(f"the file has changed since 2026-09-03 — added: "
                 f"{new or 'none'}; removed: {gone or 'none'}.")
    note("these are the site's own path prefixes, not a country list this "
         "adapter invented. `dominican-en` / `dominicana-es` and `spain-en` / "
         "`espana-es` are not translation pairs.")


def cmd_search(a):
    v = robots_verdict("www.encuentra24.com")
    if not v["sweep"]:
        die(f"www.encuentra24.com: {v['reason']}", EXIT_REFUSED)
    prefix = a.prefix.strip().lower()
    known, _live = prefixes()
    if prefix not in known:
        die(f"{prefix!r} is not a prefix this site declares. Run `prefixes` "
            f"— it reads them from robots.txt rather than composing them.")
    cat = CATEGORY[lang_of(prefix)]
    first, kept, page, read = None, 0, 1, 0
    while True:
        path = f"/{prefix}/{cat}" + (f".{page}" if page > 1 else "")
        code, html, landed = get(path)
        if code != 200:
            note(f"page {page}: HTTP {code} — stopping. {kept} ad(s) so far "
                 f"and they are good.")
            break
        rows = ids_on(html, prefix, cat)
        if not rows:
            note(f"page {page} carried no ad link — stopping.")
            break
        ids = [r[0] for r in rows]
        # **The check that matters.** Past the last page this site serves page
        # one again, with 200: pages 50 and 500 returned page 1's twenty ads
        # exactly, while pages 1–3 were disjoint. Without this the sweep runs
        # for ever and re-emits page one as new.
        if first is None:
            first = ids
        elif ids == first:
            note(f"page {page} is page 1 again — that is this site's way of "
                 f"saying there is no page {page}. Stopping at {page - 1} "
                 f"page(s), {kept} ad(s). Not an error.")
            break
        read = page
        for ident, slug, c in rows:
            print(json.dumps({
                "id": ident,
                "ledger_id": f"encuentra24:{country_of(prefix)}:{ident}",
                "url": f"{BASE}/{prefix}/{c}/{slug}/{ident}",
                "prefix": prefix,
                "country": country_of(prefix),
                # The slug's words, and they are not the title: the title is
                # on the ad page, in its `JobPosting`.
                "slug_words": slug.replace("-", " "),
                "page": page,
            }, ensure_ascii=False))
            kept += 1
            if a.limit and kept >= a.limit:
                note(f"{kept} ad(s) over {page} page(s) — stopped at --limit.")
                return
        if a.pages and page >= a.pages:
            break
        page += 1
        time.sleep(a.delay)
    if kept == 0:
        note(zero_note("encuentra24", where=prefix, extra=(
            "The category answered 200. On this site `trabajos` and `empleo` "
            "also answer 200 with the generic latest-listings page, so check "
            "the category before reading this as an empty market.")))
        return
    # **The page size is not the same in both languages.** Measured: 20 ads a
    # page under `-es` and 30 under `-en`, on the same corpus. Reported rather
    # than assumed, because a hard-coded 20 turns into a wrong total.
    # `read`, not `page`: the loop's counter has already moved on to the page
    # that turned out not to exist. Reporting it would overstate the sweep by
    # one every time.
    note(f"{kept} ad(s) over {read} page(s), {len(first or [])} on the first.")


def cmd_ad(a):
    v = robots_verdict("www.encuentra24.com")
    if not v["sweep"]:
        die(f"www.encuentra24.com: {v['reason']}", EXIT_REFUSED)
    code, html, landed = get(a.url)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    posts = postings(html)
    if not posts:
        die(f"{a.url}: no `JobPosting` in the page's JSON-LD. That is not "
            f"proof the ad is gone — check the URL is an ad and not a "
            f"category page.", EXIT_PARTIAL)
    p = posts[0]
    loc = one(p.get("jobLocation"))
    addr = one(loc.get("address"))
    m = AD_RE.search(a.url)
    out = {
        "id": m.group("id") if m else None,
        "ledger_id": (f"encuentra24:{country_of(m.group('prefix'))}:"
                      f"{m.group('id')}" if m else None),
        "url": a.url,
        "title": label(p.get("title")),
        "company": label(p.get("hiringOrganization")),
        "location_text": " · ".join(
            x for x in (addr.get("addressLocality"), addr.get("addressRegion"),
                        addr.get("addressCountry")) if isinstance(x, str)) or None,
        "posted": label(p.get("datePosted")),
        "employment_type": label(p.get("employmentType")),
        # **Free text, not an amount.** `"Salario más bono $$"` on the measured
        # ad: the key is present on ads that state no figure at all, so read
        # the string and never compute on it.
        # `label()` and not `one()`: `one()` returns `{}` for a string by
        # design, and this field is a string here. Caught by the field coming
        # back as `{}` on an ad that plainly had a value.
        "salary_text": label(p.get("baseSalary")),
        "salary_is_structured": isinstance(p.get("baseSalary"), dict),
        "industry": label(p.get("industry")),
        "occupational_category": label(p.get("occupationalCategory")),
        "description_chars": len(p.get("description") or ""),
    }
    if a.with_text:
        out["description"] = p.get("description")
        out["qualifications"] = p.get("qualifications")
        out["responsibilities"] = p.get("responsibilities")
    print(json.dumps(out, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    x = sub.add_parser("prefixes", help="the site's own country/language list")
    x.set_defaults(func=cmd_prefixes)

    s = sub.add_parser("search", help="the offers category, page by page")
    s.add_argument("--prefix", required=True, help="e.g. panama-es")
    s.add_argument("--pages", type=int)
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=1.0)
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="one ad by URL, from its JobPosting")
    d.add_argument("--url", required=True)
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
