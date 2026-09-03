#!/usr/bin/env python3
"""Fetch BTP job ads from emploi.batiactu.com — French construction.

**9 984 ads** of construction, public works and building engineering: the
largest French sector this plugin had no coverage for at all. Every ad carries
**coordinates**, which almost no board does — and a `streetAddress` that is the
employer's head office rather than the job's site. See `card`.

The `robots.txt` closes exactly one thing that matters, the search page
(`/offre-emploi-recherche.php*`), and leaves the browse paths open:

  /offre-emploi-BTP/localisation/<region>       21 regions
  /offre-emploi-BTP/metier/<metier>             24 trades
  …?page=<n>                                    20 ads a page

**The region is not a location.** A third of the "Île-de-France" page was
somewhere else entirely — the filter matches the *employer entity's name*, and
"Eurovia Délégation Île-de-France Normandie" posts jobs in the Manche. So the
region is a way to page through the board, never a way to know where the work
is. Filter on the postcode instead, which is on every ad: see `--departement`.

Usage:
  batiactu.py regions
  batiactu.py search --region ile-de-france --pages 5
  batiactu.py search --region ile-de-france --departement 75 --departement 92
  batiactu.py search --metier architecte

Output: one JSON object per line.
"""

import argparse
import html as html_mod
import json
import re

from _decode import decode_body
from _ldjson import one, postings
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _robots import allowed as robots_allowed

BASE = "https://emploi.batiactu.com"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

PER_PAGE = 20

# The site's own region vocabulary, read from its footer on 2026-08-31. It is
# the **pre-2016** map — Aquitaine, Limousin, Picardie — not the thirteen
# current regions, so `nouvelle-aquitaine` and `hauts-de-france` are not values
# here. Checked before asking, because a slug the site does not know answers
# 200 with twenty ads (trap 3).
REGIONS = (
    "alsace", "aquitaine", "auvergne", "bourgogne", "bretagne",
    "centre-val-de-loire", "champagne-ardenne", "corse", "franche-comte",
    "ile-de-france", "languedoc-roussillon", "limousin", "lorraine",
    "midi-pyrenees", "nord-pas-de-calais", "normandie", "pays-de-la-loire",
    "picardie", "poitou-charentes", "provence-alpes-cote-d-azur",
    "rhone-alpes",
)

AD_RE = re.compile(r"/offre-emploi/([a-z0-9-]+?)-(\d+)\.php")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
SLUG_RE = re.compile(r"^[a-z0-9-]+$")


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
        print(f"[hellowork] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts. A platform that has "
              f"been renamed reaches an adapter this way before it reaches it "
              f"as a rename.", file=__import__("sys").stderr)
    return a



def get(path, retries=2):
    _robots_gate(BASE + path if not path.startswith("http") else path, 'batiactu')
    url = BASE + path
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "fr-FR,fr;q=0.9",
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return decode_body(r.read(), r.headers)[0]
        except urllib.error.HTTPError as e:
            die(f"batiactu returned HTTP {e.code} for {path}")
        except Exception as e:  # noqa: BLE001 - network shape varies
            if attempt == retries:
                die(f"could not reach batiactu: {e}")
            time.sleep(1.5)


def strip(markup):
    txt = re.sub(r"<[^>]+>", " ", markup or "")
    return re.sub(r"\s+", " ", html_mod.unescape(txt)).strip()


def ad_links(page):
    """(id, slug) for every ad on a page, in order, deduplicated."""
    out, seen = [], set()
    for slug, ident in AD_RE.findall(page):
        if ident not in seen:
            seen.add(ident)
            out.append((ident, slug))
    return out


def listing_path(axis, value, page):
    """Build a listing URL.

    Pagination is **`?page=N` and only that**. The path forms that look right —
    `/localisation/<r>/page/2` and `/localisation/<r>/2` — are accepted and
    **silently serve page 1 again**, so a sweep built on them re-reads the same
    twenty ads forever.

    The site's own pagination links are no help either: they are built by
    concatenation and come out malformed, pointing at another region entirely
    (`…/ile-de-france/ville/ville/…/localisation/midi-pyrenees?page=2`). They
    are never followed; the page number is counted here.
    """
    p = f"/offre-emploi-BTP/{axis}/{value}"
    return p + (f"?page={page}" if page > 1 else "")


def card(ident, slug):
    """One ad, from its page's JSON-LD JobPosting."""
    page = get(f"/offre-emploi/{slug}-{ident}.php")
    # One reader for every board's ld+json: tolerant of the quote style
    # on the script tag, and strict=False on the parse. Issue #76.
    jp = (postings(page) or [None])[-1]
    url = f"{BASE}/offre-emploi/{slug}-{ident}.php"
    if jp is None:
        t = TITLE_RE.search(page)
        return {"id": ident, "ledger_id": f"batiactu:{ident}", "url": url,
                "title": strip(t.group(1)) if t else None, "json_ld": False}
    addr = one(jp.get("jobLocation")).get("address") or {}
    sal = one(jp.get("baseSalary")).get("value") or {}
    org = one(jp.get("hiringOrganization")).get("name")
    geo = jp.get("geo") or {}
    return {
        "id": ident,
        "ledger_id": f"batiactu:{ident}",
        "url": url,
        "title": jp.get("title"),
        # Named on every ad — but read the adapter doc: agencies are a large
        # share, and some ads name **Pole Emploi**, which means the ad is a
        # France Travail republication and the real employer is not here.
        "company": org,
        "from_france_travail": bool(org and "pole emploi" in org.lower()),
        # `streetAddress` is **the employer's registered address, not the
        # job's**. "20 rue Thierry Sabine" — Eurovia's — came back on ads in
        # twenty different communes, Paris to Précy-sur-Marne. Joined to
        # `addressLocality` it composes an address that does not exist, so it
        # is emitted under a name that cannot be mistaken for the workplace.
        "employer_street": addr.get("streetAddress"),
        "locality": addr.get("addressLocality"),
        "region": addr.get("addressRegion"),
        "postcode": addr.get("postalCode"),
        # These, by contrast, are the job's and they are right: 21 distinct
        # pairs over 32 ads, each matching its commune. With the postcode they
        # are the location to trust.
        "lat": geo.get("latitude"),
        "lon": geo.get("longitude"),
        "employment_type": jp.get("employmentType"),
        # Structured when present — minValue/maxValue/unitText — but present on
        # roughly a fifth of ads.
        "salary_min": sal.get("minValue"),
        "salary_max": sal.get("maxValue"),
        "salary_unit": sal.get("unitText"),
        "published": jp.get("datePosted"),
        # 90 days on most ads but ten different values across a sample, so it
        # is a default rather than a formula — and not verified as an expiry.
        "valid_through": jp.get("validThrough"),
        # `industry` held the company name on every ad measured, so it is not
        # emitted as a sector. Kept under a name that says what it is.
        "industry_field_holds_company_name": jp.get("industry"),
        "description": jp.get("description"),
        "json_ld": True,
    }


def sweep(axis, value, pages, delay, depts, details):
    seen, kept, dropped, page_no = set(), 0, 0, 1
    while page_no <= pages:
        page = get(listing_path(axis, value, page_no))
        found = ad_links(page)
        if page_no == 1 and not found:
            die(f"no ads at all on /offre-emploi-BTP/{axis}/{value}.")
        fresh = [(i, s) for i, s in found if i not in seen]
        if not fresh:
            # Pagination here is honest: past the last page the server returns
            # a page with no ads at all, and keeps doing so (page 9999 too).
            # Measured: PACA page 121 gave 8, page 122 gave zero.
            print(f"[batiactu] page {page_no} is empty — end of {value}",
                  file=sys.stderr)
            break
        for ident, slug in fresh:
            seen.add(ident)
            c = card(ident, slug) if details else {
                "id": ident, "ledger_id": f"batiactu:{ident}",
                "url": f"{BASE}/offre-emploi/{slug}-{ident}.php"}
            if depts:
                cp = (c.get("postcode") or "")[:2]
                if cp not in depts:
                    dropped += 1
                    if details:
                        time.sleep(delay)
                    continue
            print(json.dumps(c, ensure_ascii=False))
            kept += 1
            if details:
                time.sleep(delay)
        page_no += 1
        time.sleep(delay)
    print(f"[batiactu] {kept} ads from {axis}/{value}", file=sys.stderr)
    if dropped:
        print(f"[batiactu] {dropped} dropped by --departement. That is normal "
              "here and not a bug: the region page filters on the employer's "
              "name, not the job's address, so ads from anywhere in France "
              "appear on it.", file=sys.stderr)
    if len(seen) and page_no > pages:
        print(f"[batiactu] stopped at --pages {pages}; there may be more",
              file=sys.stderr)


def cmd_regions(_a):
    for r in REGIONS:
        print(r)


def cmd_search(a):
    if a.region and a.metier:
        die("give --region or --metier, not both: the site has no combined "
            "path for them.")
    if a.region:
        if a.region not in REGIONS:
            die(f"{a.region!r} is not one of this site's regions. It uses the "
                "**pre-2016** map, so there is no `nouvelle-aquitaine` and no "
                "`hauts-de-france`. An unknown slug is not an error here: it "
                "answers 200 with twenty plausible ads. Run `regions`.")
        axis, value = "localisation", a.region
    elif a.metier:
        if not SLUG_RE.match(a.metier):
            die(f"{a.metier!r} is not a slug.")
        axis, value = "metier", a.metier
    else:
        die("give --region or --metier.")
    depts = set(a.departement or [])
    for d in depts:
        if not re.fullmatch(r"\d{2}|2[AB]", d):
            die(f"{d!r} is not a two-character department code.")
    sweep(axis, value, a.pages, a.delay, depts, not a.no_details)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("regions", help="the 21 region slugs").set_defaults(
        func=cmd_regions)
    s = sub.add_parser("search", help="sweep one region or one trade")
    s.add_argument("--region", help="slug — see `regions`")
    s.add_argument("--metier", help="slug, e.g. architecte")
    s.add_argument("--departement", action="append",
                   help="keep only ads whose postcode starts with this. "
                        "Repeatable. The only trustworthy location filter")
    s.add_argument("--pages", type=int, default=5, help="20 ads each")
    s.add_argument("--delay", type=float, default=0.5)
    s.add_argument("--no-details", action="store_true",
                   help="listing only — but then --departement cannot work, "
                        "because the postcode lives on the ad page")
    s.set_defaults(func=cmd_search)
    a = p.parse_args()
    if getattr(a, "no_details", False) and getattr(a, "departement", None):
        die("--departement needs the ad pages; drop --no-details.")
    a.func(a)


if __name__ == "__main__":
    main()
