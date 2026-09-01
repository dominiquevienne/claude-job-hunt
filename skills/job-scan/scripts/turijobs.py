#!/usr/bin/env python3
"""Fetch Spanish hospitality ads from turijobs.com — and count how many
people already applied.

**2 863 active ads** in tourism and hospitality — hotels, kitchens, front
desk, spa, housekeeping. The fourth Spanish adapter here and the first
sector board: `empleate.md` and `oposiciones.md` are the SEPE's registers,
`infoempleo.md` is a generalist. Tourism is the sector the generalists cover
worst in Spain, and this is where the chains post.

  GET /robots.txt                         → nine Sitemap: lines, one per locale
  GET /es/sitemap/index.xml               → nine files
  GET /es/sitemap/active-offers.xml       → 2 863 ads, a real lastmod on each
  GET /es/oferta-trabajo/<city>/<slug>/<id>   → the ad, inside __NEXT_DATA__

**No browser, no account, no key.**

WHAT IT HAS THAT NOTHING ELSE HERE DOES. `applies` — **the number of people
who have already applied**, median 10, up to 156. No other board in this
repository publishes it, and it answers a question a candidate cannot
otherwise ask: is this a queue of three or of a hundred and fifty.

It also carries a **real postcode on 38 of 40** — where `infoempleo.md` and
`hays-fr.md` have none at all — plus coordinates, the employer's own street
address, and the employer's careers site.

THE SALARY FIELD READS THREE DIFFERENT WAYS AND ONLY ONE IS TRUE.

    salary object present                    40 of 40   →  "100% have a salary"
    salaryVisible: true                      27 of 40   →  "67% have a salary"
    a figure: salaryMin or salaryMax > 0      2 of 40   →  5%

`salary` is **never absent** — it is an object on every ad, so a presence
check reports total coverage. `salaryVisible` is true on two thirds — and
**25 of those 27 carry `salaryMin: 0, salaryMax: 0`**. `salaryType` says
`YEAR` on 26 ads, of which 2 state an amount: even the unit is filled in
where there is no number.

This is `infoempleo.md`'s `value: 0.0` one level worse: there the zero sat in
a sub-field, here the whole object is present *and* a boolean says it is
visible. Only `> 0` is a salary; everything else is emitted as absent, with
the flags kept so nobody re-derives this.

THE EMPLOYER IS NAMED, AND NOT WHERE YOU WOULD LOOK. `company.name` **does not
exist** — 0 of 35. The name is in `company.brandName`, filled on 35 of 35:
Meliá, Barceló, Catalonia Hotels, H10, Hilton Barcelona. A reader that asks
for `name`, which is what every JSON-LD board here uses, gets `None` on a
board that names the employer on every single ad.

And these are the **real employers**, not agencies — the opposite of
`infoempleo.md`, where 32 of 44 were ETTs. The concentration is in the chains
instead: 16 distinct employers across 35 ads, Meliá alone 15.

A LOCALE IS NOT A COUNTRY. The `/es/` sitemap is the Spanish-language board,
not the Spanish one: **10 of 40 sampled ads were outside Spain** — Germany 4,
Portugal 3, France, Italy, Mexico. Same lesson as `wttj.md`, at two and a half
times the rate. `--pais ES` filters on the ad's own `countryISO`, and every
run reports the split.

Usage:
  turijobs.py ciudades
  turijobs.py search --ciudad barcelona --pais ES
  turijobs.py search --desde 2026-08-25 --limit 30

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
import urllib.request
import zlib

BASE = "https://www.turijobs.com"
SITEMAP = BASE + "/es/sitemap/active-offers.xml"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# The house pattern since issue #55: reads the plain and the CDATA-wrapped
# form both. turijobs does not use CDATA today (2 863 <url>, 2 863 <loc>).
LOC_RE = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?\s*([^\s\]<]+)")
MOD_RE = re.compile(r"<lastmod>([^<]*)")
URL_BLOCK_RE = re.compile(r"(?s)<url>(.*?)</url>")
ND_RE = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
# /es/oferta-trabajo/<city>/<slug>/<id>
AD_RE = re.compile(r"/es/oferta-trabajo/([^/]+)/([^/]+)/(\d+)")

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[turijobs] {msg}", file=sys.stderr)


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
                enc = (r.headers.get("Content-Encoding") or "").lower()
            if enc == "gzip":
                raw = gzip.decompress(raw)
            elif enc in ("deflate", "zlib"):
                try:
                    raw = zlib.decompress(raw)
                except zlib.error:
                    raw = zlib.decompress(raw, -zlib.MAX_WBITS)
            return raw.decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as exc:
            if attempt == retries:
                die(f"{url}: {exc}")
            time.sleep(1.5 * (attempt + 1))
    return ""


def fold(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def text_of(html):
    """Strip the markup, which is heavy and machine-written.

    Every paragraph carries an inline `style` with a generated font name —
    `__IBMPlexSans_873584` — that changes on every build. Nothing in it is
    worth keeping.
    """
    if not isinstance(html, str):
        return None
    return WS_RE.sub(" ", TAG_RE.sub(" ", html)).strip() or None


def labels(features):
    """`features` is a dict keyed by slot number, each value `{id, label}`.

    Filled on 25 of 25, and it carries what the prose does not: the education
    level, the experience band, the contract, the working time, the job family
    and **the kind of employer** — "Cadena hotelera", "Empresa de selección /
    ETT". That last one is why this board can say whether the employer is the
    hotel or an agency, which `infoempleo.md` cannot.
    """
    if not isinstance(features, dict):
        return []
    out = []
    for v in features.values():
        if isinstance(v, dict) and v.get("label"):
            out.append(v["label"])
    return out


def entries():
    page = get(SITEMAP)
    blocks = URL_BLOCK_RE.findall(page)
    out = []
    for b in blocks:
        loc = LOC_RE.search(b)
        if not loc or not AD_RE.search(loc.group(1)):
            continue
        mod = MOD_RE.search(b)
        out.append((loc.group(1), mod.group(1).strip() if mod else None))
    if not out:
        # Issue #55's invariant: zero <loc> inside a non-zero number of <url>
        # blocks cannot occur in a valid sitemap, so the reader is wrong
        # rather than the board empty.
        if blocks:
            die(f"{SITEMAP} gave zero ad URLs out of {len(blocks)} <url> "
                "blocks. That combination cannot occur in a valid sitemap: "
                "it is a reading fault, not an empty board.")
        die(f"{SITEMAP} parsed to zero <url> blocks out of {len(page)} "
            "characters — a read failure, not an empty board.")
    return out


def money(sal):
    """A figure, or nothing. See the module docstring.

    `salary` is an object on every ad and `salaryVisible` is true on two
    thirds, but only `salaryMin` / `salaryMax` above zero is a salary. Both
    flags are returned so the caller can see why an ad that "has" a salary
    has no number.
    """
    sal = sal or {}
    lo = sal.get("salaryMin") or 0
    hi = sal.get("salaryMax") or 0
    return (lo or None, hi or None, sal.get("salaryType") or None,
            bool(sal.get("salaryVisible")))


def card(url, lastmod):
    m = AD_RE.search(url)
    city_url, slug, ident = m.groups() if m else (None, None, None)
    page = get(url)
    nd = ND_RE.search(page)
    if not nd:
        # The whole ad rides in __NEXT_DATA__; its absence is a failure to
        # read the page, not an ad without content. Same reasoning as
        # infoempleo.md's "zero ld+json blocks is an invariant violation".
        die(f"{url} carries no __NEXT_DATA__ block ({len(page)} chars). The "
            "entire ad is inside it, so this is a failure to read the page, "
            "not an ad with nothing in it.")
    try:
        data = json.loads(nd.group(1))
    except ValueError as exc:
        die(f"{url}: __NEXT_DATA__ did not parse ({exc}).")
    props = (data.get("props") or {}).get("pageProps") or {}
    o = (props.get("offerData") or {}).get("offerDetail")
    if not o:
        return {"id": ident, "ledger_id": f"turijobs:{ident}", "url": url,
                "expired": True, "next_data": True}
    loc = o.get("location") or {}
    co = o.get("company") or {}
    lo, hi, unit, visible = money(o.get("salary"))
    dates = o.get("dates") or {}
    zip_code = loc.get("zipCode")
    return {
        "id": ident,
        "ledger_id": f"turijobs:{ident}",
        "url": url,
        "title": o.get("title"),
        # `company.name` does not exist on this board — 0 of 35. brandName is
        # filled on 35 of 35, and it is the real employer, not an agency.
        "company": co.get("brandName") or co.get("enterpriseName"),
        # Differs from brandName on 6 of 35 — the legal entity behind the
        # brand.
        "company_legal_name": co.get("enterpriseName"),
        "company_sector": co.get("sector"),
        "company_website": co.get("webUrl"),
        "company_address": co.get("address"),
        "company_city": co.get("cityName"),
        # `ownerName` holds a natural person — the recruiter who posted the
        # ad, "Marta Pérez Fernández" — on every ad measured. It is not the
        # employer, it is not needed to decide or to apply, and
        # shared/robots-policy.md is explicit that none of this licenses
        # personal data. It is read and deliberately not emitted.
        "country": loc.get("countryISO"),
        "country_name": loc.get("countryName"),
        "region": loc.get("regionName"),
        "city": loc.get("cityName"),
        "city_from_url": city_url,
        # 38 of 40, and only 3 of those are a `<province>000` placeholder.
        # The best postcode coverage of the Spanish boards here.
        "postcode": zip_code,
        "postcode_looks_like_placeholder": bool(
            zip_code and str(zip_code).endswith("000")),
        "latitude": loc.get("latitude"),
        "longitude": loc.get("longitude"),
        "vacancies": o.get("vacancies"),
        # The count of applications already sent. Nothing else here has it.
        "applicants_so_far": o.get("applies"),
        "salary_min": lo,
        "salary_max": hi,
        "salary_unit": unit,
        # True on 27 of 40 — and 25 of those carry no figure at all. Kept so
        # the absence of a number on a "visible" salary is explicable.
        "salary_marked_visible": visible,
        "salary_currency": "EUR" if (lo or hi) else None,
        "published": dates.get("publicationDate") or o.get("publicationDate"),
        "updated": dates.get("updatingDate") or o.get("updatingDate"),
        "expires": dates.get("finishDate") or o.get("expiringDate"),
        "lastmod": lastmod,
        "tags": o.get("cardTags"),
        "description": text_of(o.get("description")),
        # A dict, not prose: {"DEGREE": [...], "EXP_YEARS": [...]} on 25 of
        # 25, plus LANGUAGES and WORK_PERMIT on 2. Passed through structured
        # rather than flattened into a sentence nobody wrote.
        "requirements": o.get("requirements") or None,
        "additional_requirements": text_of(o.get("additionalRequirements")),
        "features": labels(o.get("features")),
        # `benefits`, `assignments`, `skills` and `preferences` exist in the
        # payload and were **empty on 25 of 25**. They are read here so that
        # the day they start being filled it is one line, and reported as
        # absent rather than silently dropped.
        "benefits": o.get("benefits") or None,
        "employer_is_anonymous": bool(o.get("isBlind")),
        "next_data": True,
    }


def narrow(rows, a):
    if a.ciudad:
        want = fold(a.ciudad)
        before = len(rows)
        rows = [r for r in rows
                if want == fold((AD_RE.search(r[0]) or [None, ""]) and
                                AD_RE.search(r[0]).group(1))]
        note(f"{len(rows)} of {before} match --ciudad {a.ciudad!r} in the URL, "
             "filtered before any fetch")
        if not rows:
            note("no city by that name. `turijobs.py ciudades` lists the 127 "
                 "the sitemap uses — a wrong one is an empty board, not an "
                 "error.")
    if a.desde:
        before = len(rows)
        rows = [r for r in rows if (r[1] or "") >= a.desde]
        note(f"{len(rows)} of {before} with lastmod on or after {a.desde} — "
             "free, the sitemap dates every ad")
    return rows


def cmd_ciudades(a):
    rows = entries()
    c = collections.Counter(AD_RE.search(u).group(1) for u, _ in rows)
    for city, n in c.most_common(a.limit or None):
        print(json.dumps({"ciudad": city, "ads": n}, ensure_ascii=False))
    note(f"{len(c)} cities across {len(rows)} ads, read out of the URL — "
         "--ciudad costs no fetch.")
    note("Some of these are not in Spain: the /es/ sitemap is the "
         "Spanish-LANGUAGE board. lisboa, porto, inglaterra and malta all "
         "appear. Use --pais ES to keep Spain only.")


def cmd_discover(a):
    rows = narrow(entries(), a)
    for url, mod in rows[:a.limit or None]:
        m = AD_RE.search(url)
        print(json.dumps({"url": url, "id": m.group(3),
                          "ledger_id": f"turijobs:{m.group(3)}",
                          "city_from_url": m.group(1), "lastmod": mod},
                         ensure_ascii=False))
    note(f"{min(len(rows), a.limit or len(rows))} ad URLs. The country is only "
         "known once an ad is read — see search --pais.")


def cmd_search(a):
    rows = entries()
    note(f"{len(rows)} active ads in the sitemap")
    rows = narrow(rows, a)
    kept = gone = wrong_country = 0
    countries = collections.Counter()
    salaried = visible_but_empty = 0
    for url, mod in rows:
        if a.limit and kept >= a.limit:
            break
        c = card(url, mod)
        if c.get("expired"):
            gone += 1
            time.sleep(a.delay)
            continue
        countries[c["country"]] += 1
        if a.pais and (c["country"] or "").upper() != a.pais.upper():
            wrong_country += 1
            time.sleep(a.delay)
            continue
        if c["salary_min"] or c["salary_max"]:
            salaried += 1
        elif c["salary_marked_visible"]:
            visible_but_empty += 1
        print(json.dumps(c, ensure_ascii=False))
        kept += 1
        time.sleep(a.delay)
    note(f"{kept} ads returned")
    if gone:
        note(f"{gone} had no offerDetail in their payload — withdrawn since "
             "the sitemap was built.")
    if wrong_country:
        note(f"{wrong_country} were dropped by --pais {a.pais}. Read "
             f"countries: {dict(countries)}. A locale is not a country: the "
             "/es/ sitemap carried 10 of 40 ads outside Spain when measured.")
    elif len(countries) > 1:
        note(f"countries in what was returned: {dict(countries)} — the /es/ "
             "sitemap is the Spanish-language board, not the Spanish one. "
             "Use --pais ES to keep Spain only.")
    note(f"salary: {salaried} of {kept} state a figure. A further "
         f"{visible_but_empty} are flagged salaryVisible with no number at "
         "all — on this board the object is always present and the flag is "
         "not the answer.")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("ciudades", help="the cities in the sitemap, with "
                                        "counts. Free")
    c.add_argument("--limit", type=int)
    c.set_defaults(func=cmd_ciudades)

    for name, fn, h in (("discover", cmd_discover, "ad URLs and dates"),
                        ("search", cmd_search, "read the ads")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--ciudad", help="city as written in the URL — "
                                        "barcelona, islas-baleares, madrid. "
                                        "**Free**. `ciudades` lists them")
        c.add_argument("--desde", metavar="YYYY-MM-DD",
                       help="lastmod on or after this date. **Free** — the "
                            "sitemap dates every ad, 2 506 distinct values "
                            "across 2 863")
        c.add_argument("--limit", type=int)
        if name == "search":
            c.add_argument("--pais", metavar="ISO2",
                           help="keep only this country, e.g. ES. Costs a "
                                "fetch per ad: the country is inside the ad")
            c.add_argument("--delay", type=float, default=0.5)
        c.set_defaults(func=fn)

    a = p.parse_args()
    if a.cmd == "search" and not (a.ciudad or a.desde or a.limit):
        die("give --ciudad, --desde or --limit. Without one the sweep reads "
            "all 2 863 ads, one request each — and each page is ~700 KB for "
            "6 KB of ad.")
    a.func(a)


if __name__ == "__main__":
    main()
