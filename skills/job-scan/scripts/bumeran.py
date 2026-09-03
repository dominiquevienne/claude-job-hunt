#!/usr/bin/env python3
"""Enumerate the Bumeran/Jobint family — seven brands, one shape, and the ad
page needs a browser while the directory does not.

**One platform wearing national brands**, and the tell is in the filenames:
every brand serves `sitemap_avisos_bum.xml` at the same path — `_bum` for
Bumeran, surviving under names that share nothing with it. A checksum would
never have found it.

MEASURED 2026-09-03, and **the count is the reason this file exists**:

    bumeran.com.pe      Peru        34 809 ads
    laborum.cl          Chile       15 901
    bumeran.com.ar      Argentina    6 804
    multitrabajos.com   Ecuador      5 771
    konzerta.com        Panama       2 814
    bumeran.com.mx      Mexico       1 795
    bumeran.com.ve      Venezuela      757
                                   ───────
                                    68 651

**DISCOVERY IS PLAIN HTTP AND READING AN AD IS NOT.** The ad page answers
`200` with **64 180 bytes** of React shell — `<title>` empty, no `og:title`,
no `ld+json`, and a `<noscript>` reading *"You need to enable JavaScript to
run this app"*. **Fifty-six characters of visible text.** The facet pages are
the same shell, byte for byte.

**And this one is not a missing parameter.** Applifly looked identical from one
request and was fixed by adding `source=`; here the check was run —
`/api/...` under four shapes answers **403 with the same 5 516 bytes every
time, including for a path that cannot exist.** *An identical size across four
probes is agreement produced by nothing having answered*, so the 403 says the
edge blocks `/api`, not that an endpoint is missing. `robots.txt` does not
mention `/api` at all: this is a WAF rule and not a refusal.

WHAT YOU GET WITHOUT A BROWSER, AND IT IS NOT NOTHING:

- **Every ad's URL and id**, 68 651 of them across seven countries.
- **The slug**, which carries words from the posting — *filterable, and it is
  not the title.* This file emits `slug_words` under that name and never as
  `title`, because nothing here has read the title. Believing a slug is a
  title is how a row gets the right words and the wrong claim.
- **The board's own facet vocabulary** — province, city, area, subarea,
  contract, seniority — parsed from 3 953 listing URLs. **Language-independent
  where a keyword is not**, which is the answer `_zero.py` asks for when a
  search in the user's own language returns nothing.

A NAME THAT LOOKS LIKE THE FAMILY AND IS NOT. `laborum.pe` serves a
`robots.txt` with an entirely different vocabulary — `/myprofile`,
`/wishlist`, `/postulations` — and **no `_bum` sitemap at all**. It is not in
`SITES` and it is named here so nobody adds it on the strength of its name.

AND THE TENANTS ARE NOT IDENTICAL. `bumeran.com.mx` and `bumeran.com.ve`
declare **four** sitemaps where the other five declare five: no
`sitemap_tags_bum.xml`. Small, and exactly the assumption to avoid — Indeed is
one template on forty-nine hosts, SuccessFactors serves two URL shapes by
tenant.

Verified against all seven live sites on **2026-09-03**.
"""

import argparse
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _robots import verdict as robots_verdict
from _sitemap import count as sitemap_count
from _sitemap import count_says, locs as sitemap_locs
from _zero import zero_note

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

EXIT_BROKEN, EXIT_PARTIAL, EXIT_REFUSED = 2, 6, 7

# host → (country, ads measured 2026-09-03). **The count is dated because it
# is a measurement, not a property**: re-run `sites --check` rather than
# quoting it.
SITES = {
    "bumeran.com.pe": ("Peru", 34809),
    "laborum.cl": ("Chile", 15901),
    "bumeran.com.ar": ("Argentina", 6804),
    "multitrabajos.com": ("Ecuador", 5771),
    "konzerta.com": ("Panama", 2814),
    "bumeran.com.mx": ("Mexico", 1795),
    "bumeran.com.ve": ("Venezuela", 757),
}

ADS_SITEMAP = "/sitemap_avisos_bum.xml"
FACETS_SITEMAP = "/sitemap_listados_ubicacion_bum.xml"

# **`[^/]+`, and the alternative was measured.** A slug pattern of
# `[a-z0-9-]+` silently dropped **1 160 of 5 771 ad URLs on one site — 20% of
# the board** — because Ecuadorian company names put dots and pipes in the
# slug: `vita-alimentos-c.a.`, `aceroscenter-cia.-ltda`,
# `recepcionista-|-hombre-mujer`. Every one of them was a real ad. The tight
# pattern failed in the direction every tooling defect fails in: **towards
# "there is nothing there".**
AD_URL = re.compile(r"/empleos/(?P<slug>[^/]+?)-(?P<id>\d{6,})\.html$", re.I)
# **The place prefix has three forms, and assuming one costs two thirds of the
# file.** Measured on 3 953 listing URLs: province **and** city, province
# alone, or neither.
#
#   /en-canar/azogues/empleos-area-…      province + city
#   /en-canar/empleos-area-…              province only
#   /empleos-area-…                       neither
#
# The first version demanded the city and read **1 260 of 3 953 — 32%**, while
# reporting the rest as "forms not measured". That sentence was true and
# useless: the shape was one optional segment away. Widening it left 597, all
# of them `empleos-` with **no** `area-` — a listing faceted only by contract
# and seniority. **Two rounds, and each time the unread remainder was a
# regular form rather than noise.** With both optional the file reads 3 953 of
# 3 953. And 77 were the bare
# `/en-<province>/<city>/empleos.html`, a place with no facet at all, so the
# facet segment is optional too. **Three rounds, and every unread remainder
# was a regular form rather than noise.** With all three optional the file
# reads 3 953 of 3 953. A count that improves three times under inspection was
# never a property of the site.
FACET_URL = re.compile(
    r"(?:/en-(?P<province>[a-z0-9-]+))?(?:/(?P<city>[a-z0-9-]+))?"
    r"/empleos(?:-(?:area-)?(?P<rest>[a-z0-9.|-]+))?\.html$", re.I)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[bumeran] {msg}", file=sys.stderr)


def fold(s):
    """Compare without accents or case — the slugs are already unaccented, so
    a search for `diseñador` must fold or it matches nothing."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def host_of(site):
    s = (site or "").strip().lower().replace("https://", "").strip("/")
    s = s[4:] if s.startswith("www.") else s
    if s not in SITES:
        die(f"{s!r} is not one of this family's sites. Known: "
            f"{', '.join(sorted(SITES))}. **`laborum.pe` is deliberately not "
            f"here** — the name looks like the family and the site is not it.")
    return "www." + s


def get(url, timeout=120):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/xml,text/xml,text/html;q=0.9",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.getcode(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def check_robots(host):
    v = robots_verdict(host)
    if not v["sweep"]:
        die(f"{host}: {v['reason']}", EXIT_REFUSED)
    return v


def cmd_sites(a):
    for host, (country, ads) in sorted(SITES.items(),
                                       key=lambda kv: -kv[1][1]):
        row = {"site": host, "country": country, "ads_measured_2026_09_03": ads}
        if a.check:
            check_robots("www." + host)
            code, body = get(f"https://www.{host}{ADS_SITEMAP}")
            if code != 200:
                row["live"] = None
                row["note"] = f"HTTP {code} on the ads sitemap"
            else:
                c = sitemap_count(body)
                row["live"] = c["locs"]
                row["says"] = count_says(body)
                row["drift"] = c["locs"] - ads
        print(json.dumps(row, ensure_ascii=False))
    if not a.check:
        note("these counts are dated measurements, not properties. "
             "`sites --check` re-counts them live.")


def cmd_search(a):
    host = host_of(a.site)
    check_robots(host)
    code, body = get(f"https://{host}{ADS_SITEMAP}")
    if code != 200:
        die(f"{host}{ADS_SITEMAP}: HTTP {code}")
    urls = sitemap_locs(body)
    if not urls:
        die(f"{host}{ADS_SITEMAP}: {count_says(body)}")
    want = fold(a.keyword) if a.keyword else None
    kept, seen = 0, set()
    for u in urls:
        m = AD_URL.search(u)
        if not m:
            continue
        ident = m.group("id")
        if ident in seen:
            continue
        slug = m.group("slug")
        words = slug.replace("-", " ")
        if want and want not in fold(words):
            continue
        seen.add(ident)
        print(json.dumps({
            "id": ident,
            "ledger_id": f"bumeran:{host_of(a.site)[4:]}:{ident}",
            "url": u,
            # **Not the title.** These are the slug's words; nothing here has
            # read the posting. See the header.
            "slug_words": words,
            "country": SITES[host_of(a.site)[4:]][0],
            "description_needs_browser": True,
        }, ensure_ascii=False))
        kept += 1
        if a.limit and kept >= a.limit:
            break
    total = sum(1 for u in urls if AD_URL.search(u))
    skipped = len(urls) - total
    if skipped:
        note(f"**{skipped} of {len(urls)} sitemap URLs did not match the ad "
             f"shape and were not read.** That is a finding, not a detail: "
             f"the first version of this pattern skipped 20% of a board this "
             f"way, in silence. Report the number and look at one.")
    if kept == 0:
        note(zero_note("bumeran", what=a.keyword, extra=(
            f"The sitemap carried {total} ad URLs, so the board is not empty "
            f"— the keyword matched none of their **slugs**, which are not "
            f"titles and carry only part of the wording. Try the facet "
            f"vocabulary instead: `facets --site {a.site}`.")))
        return
    note(f"{kept} of {total} ad URL(s)"
         + (f" whose slug contains {a.keyword!r}" if a.keyword else "") + ".")
    note("`slug_words` is the slug, not the title. The description is not in "
         "the page: it renders client-side, so reading one ad needs the "
         "browser.")


def cmd_facets(a):
    host = host_of(a.site)
    check_robots(host)
    code, body = get(f"https://{host}{FACETS_SITEMAP}")
    if code != 200:
        die(f"{host}{FACETS_SITEMAP}: HTTP {code}")
    urls = sitemap_locs(body)
    if not urls:
        die(f"{host}{FACETS_SITEMAP}: {count_says(body)}")
    places, tails, read = {}, {}, 0
    for u in urls:
        m = FACET_URL.search(u)
        if not m:
            continue
        read += 1
        prov = m.group("province") or "(no province in the URL)"
        city = m.group("city")
        places.setdefault(prov, set())
        if city:
            places[prov].add(city)
        # The tail mixes area, subarea, contract and seniority in one segment
        # and the site does not delimit them. **Reported as it is written**,
        # because splitting it would be a guess about a grammar nobody has
        # documented.
        tail = m.group("rest") or "(no facet — the place alone)"
        tails[tail] = tails.get(tail, 0) + 1
    print(json.dumps({
        "site": host_of(a.site)[4:],
        "country": SITES[host_of(a.site)[4:]][0],
        "listing_urls": len(urls),
        "parsed": read,
        "provinces": {p: sorted(c) for p, c in sorted(places.items())},
        "facet_tails": dict(sorted(tails.items(), key=lambda kv: -kv[1])
                            [:a.limit or 40]),
    }, ensure_ascii=False, indent=2))
    if read < len(urls):
        note(f"{len(urls) - read} of {len(urls)} listing URLs did not match "
             f"the expected shape and were **not** counted. They are not "
             f"errors — the grammar has forms this file has not measured.")
    note("these facets are the board's own vocabulary and are "
         "language-independent, which a keyword is not — see "
         "`shared/search-language.md` and issue #70.")


def cmd_ad(a):
    m = AD_URL.search(a.url)
    if not m:
        die(f"{a.url}: not an ad URL for this family. Expected "
            f"`/empleos/<slug>-<id>.html`.")
    host = urllib.parse.urlsplit(a.url).netloc
    print(json.dumps({
        "id": m.group("id"),
        "url": a.url,
        "slug_words": m.group("slug").replace("-", " "),
        "host": host,
        "description": None,
        "description_needs_browser": True,
    }, ensure_ascii=False))
    note("the ad page answers 200 with 64 KB of React shell and 56 characters "
         "of visible text — `<noscript>You need to enable JavaScript`. "
         "Nothing of the posting is in it, and this is not a missing "
         "parameter: `/api/...` answers 403 with an identical body for four "
         "different paths, one of which cannot exist. **Open this URL in the "
         "browser to read the ad.**")
    sys.exit(EXIT_PARTIAL)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sites", help="the seven brands, with their ad counts")
    s.add_argument("--check", action="store_true",
                   help="re-count live instead of quoting the table")
    s.set_defaults(func=cmd_sites)

    q = sub.add_parser("search", help="ad URLs, optionally filtered on slug")
    q.add_argument("--site", required=True)
    q.add_argument("--keyword")
    q.add_argument("--limit", type=int)
    q.set_defaults(func=cmd_search)

    f = sub.add_parser("facets", help="the board's own place and job taxonomy")
    f.add_argument("--site", required=True)
    f.add_argument("--limit", type=int)
    f.set_defaults(func=cmd_facets)

    d = sub.add_parser("ad", help="what is knowable from an ad URL, and what "
                                  "is not")
    d.add_argument("--url", required=True)
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
