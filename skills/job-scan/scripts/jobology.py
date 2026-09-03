#!/usr/bin/env python3
"""Fetch job ads from the nine Jobology sector boards — one contract, nine sites.

Jobology runs **nine French sector job boards** on one platform, and they share
a single URL contract, a single `robots.txt` and a single page structure. So
this is a platform adapter, like `taleez.py` or `digitalrecruiters.py`: pick the
site, the rest is identical.

  jobtransport.com   transport et logistique      15 654 ads
  distrijob.fr       distribution et retail       22 361
  jobvitae.fr        santé, soignant, médical     17 950
  clicandtour.fr     tourisme, hôtellerie, resto   4 796
  clicandpower.fr    énergie                       3 775
  clicandsea.fr      maritime et naval             3 344
  clicandsport.fr    sport                         2 411
  clicandearth.fr    environnement                 1 916
  supply-chain.fr    logistique et supply chain      460

Browsing is by path, never by query string — the `robots.txt` closes the facet
parameters (`fpos`, `fsec`, `fexp`, `fdate`, `freg`…) and leaves the paths open:

  /emploi/<metier>.aspx                       nationwide, 20 ads a page
  /emploi/<metier>/<region>.aspx              narrowed
  /emploi/<metier>[/<region>]/page-<n>.aspx   pagination

**Past the last page the site does not stop.** It keeps serving twenty
plausible, on-topic ads for any page number — page 9999 answers like page 9 —
and the same URL returns a different set on a second call. See `sweep` for the
two bounds that make a run terminate.

Usage:
  jobology.py sites
  jobology.py metiers --site jobtransport.com
  jobology.py search --site jobvitae.fr --metier infirmier --pages 5
  jobology.py search --site distrijob.fr --metier vendeur --region occitanie

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

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# The nine, read from jobology.fr's own "nos sites emploi spécialisés" page and
# each one verified live. `ads` is what the home page announced on 2026-08-31 —
# a scale marker, not a target: no listing page states a total (trap 5).
SITES = {
    "jobtransport.com": ("transport et logistique", 15654),
    "distrijob.fr": ("distribution et retail", 22361),
    "jobvitae.fr": ("santé, soignant, médical", 17950),
    "clicandtour.fr": ("tourisme, hôtellerie, restauration", 4796),
    "clicandpower.fr": ("énergie", 3775),
    "clicandsea.fr": ("maritime et naval", 3344),
    "clicandsport.fr": ("sport", 2411),
    "clicandearth.fr": ("environnement", 1916),
    "supply-chain.fr": ("logistique et supply chain", 460),
}

PER_PAGE = 20

# Ad links, and the number at the end of the slug is the id.
AD_RE = re.compile(r"/offre-emploi/([a-z0-9-]+?)-(\d+)\.aspx")
# `/emploi/<metier>.aspx` — the vocabulary of métier slugs the site publishes.
METIER_RE = re.compile(r"/emploi/([a-z0-9-]+)\.aspx")
# `/emploi/<metier>/<region>.aspx` on a region index page.
REGION_RE = re.compile(r"/emploi/[a-z0-9-]+/([a-z0-9-]+)\.aspx")
# The alphabetical index of job titles, and the region index.
LETTER_RE = re.compile(r"/recherche-emploi/list/spos/l/([a-z])\.aspx")
REGIDX_RE = re.compile(r"/recherche-emploi/list/spos/reg/(\d+)\.aspx")
# Two URL forms carry the pagination, and they are not interchangeable:
# `/emploi/<m>/page-2.aspx` and `/emploi/mc/<m>/page/83.aspx`. The site
# links the low pages in one form and the last page in the other, so a
# regex that reads only one of them under-counts the board — measured, it
# capped chauffeur-spl at 2 pages instead of 83.
PAGE_RE = re.compile(r"/page[-/](\d+)(?:\.aspx)?")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)


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



def get(site, path, retries=2):
    _robots_gate(f"https://www.{site}{path}", 'jobology')
    url = f"https://www.{site}{path}"
    if "?" in url:
        # The robots.txt disallows `/*?$` and every facet parameter it uses
        # (fpos, fsec, fexp, fdate, freg…). The paths are open; the query
        # string is not. Everything this adapter needs is a path.
        die(f"refusing to request a URL with a query string: {url}")
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
            die(f"{site} returned HTTP {e.code} for {path}")
        except Exception as e:  # noqa: BLE001 - network shape varies
            if attempt == retries:
                die(f"could not reach {site}: {e}")
            time.sleep(1.5)


def strip(markup):
    txt = re.sub(r"<[^>]+>", " ", markup or "")
    return re.sub(r"\s+", " ", html_mod.unescape(txt)).strip()


def ad_ids(page):
    """Ad ids on a page, in order, deduplicated."""
    out, seen = [], set()
    for slug, ident in AD_RE.findall(page):
        if ident not in seen:
            seen.add(ident)
            out.append((ident, slug))
    return out


def last_page(page):
    """Highest page number the pagination advertises, or None.

    This is the only upper bound the site gives: no listing page states a
    total. Beyond it the server keeps answering with ads (trap 1), so this
    number is what stops a sweep from running forever.
    """
    n = [int(x) for x in PAGE_RE.findall(page)]
    return max(n) if n else None


def check_site(site):
    if site not in SITES:
        die(f"{site!r} is not one of the nine Jobology boards. Run `sites`.\n"
            "  " + "\n  ".join(SITES))
    return site


def metier_vocabulary(site):
    """Métier slugs the site publishes, from its own A–Z index.

    Worth the requests: a métier slug that does not exist answers **200 with
    zero ads and no error** (trap 3), which is indistinguishable from a trade
    nobody is hiring for. Checking the slug first turns a silent empty board
    into a message.
    """
    home = get(site, "/")
    letters = sorted(set(LETTER_RE.findall(home)))
    slugs = set(METIER_RE.findall(home))
    for letter in letters:
        page = get(site, f"/recherche-emploi/list/spos/l/{letter}.aspx")
        slugs |= set(METIER_RE.findall(page))
        time.sleep(0.4)
    return sorted(slugs)


def regions(site):
    """Region slugs, read from the site's own region index pages."""
    ad = None
    home = get(site, "/")
    for ident, _slug in ad_ids(home)[:1]:
        ad = ident
    ids = set(REGIDX_RE.findall(home))
    if not ids and ad:
        # The region index links live in the ad-page footer, not the home page.
        for _i, slug in ad_ids(home)[:1]:
            ids |= set(REGIDX_RE.findall(get(site, f"/offre-emploi/{slug}-{ad}.aspx")))
    out = set()
    for rid in sorted(ids)[:30]:
        page = get(site, f"/recherche-emploi/list/spos/reg/{rid}.aspx")
        out |= set(REGION_RE.findall(page))
        time.sleep(0.4)
    return sorted(out)


def listing_path(metier, region, page):
    base = f"/emploi/{metier}"
    if region:
        base += f"/{region}"
    if page > 1:
        base += f"/page-{page}"
    return base + ".aspx"


def card(site, ident, slug):
    """One ad, from its page's JSON-LD JobPosting."""
    page = get(site, f"/offre-emploi/{slug}-{ident}.aspx")
    # One reader for every board's ld+json: tolerant of the quote style
    # on the script tag, and strict=False on the parse. Issue #76.
    jp = (postings(page) or [None])[-1]
    if jp is None:
        t = TITLE_RE.search(page)
        return {
            "id": ident,
            "ledger_id": f"jobology:{site}:{ident}",
            "url": f"https://www.{site}/offre-emploi/{slug}-{ident}.aspx",
            "site": site,
            "title": strip(t.group(1)) if t else None,
            "json_ld": False,
        }
    org = jp.get("hiringOrganization") or {}
    loc = one(jp.get("jobLocation")).get("address") or {}
    sal = one(jp.get("baseSalary")).get("value") or {}
    # Free text, not a number: '13.5 - 15.5 par heure', 'Selon expérience',
    # '13ème mois', and one seen as '2.486.62 EUR brut'. Filled on ~78% of ads
    # and saying nothing on a good share of those. Passed through verbatim
    # rather than parsed into a figure it does not contain.
    salary = sal.get("value") or sal.get("minValue")
    return {
        "id": ident,
        "ledger_id": f"jobology:{site}:{ident}",
        "url": f"https://www.{site}/offre-emploi/{slug}-{ident}.aspx",
        "site": site,
        "sector": SITES[site][0],
        "title": jp.get("title"),
        # Named on every ad measured — but two thirds of them are staffing
        # agencies, not the end employer. See the adapter doc.
        "company": org.get("name"),
        "locality": loc.get("addressLocality"),
        "region": loc.get("addressRegion"),
        "postcode": loc.get("postalCode"),
        # `FULL-TIME` with a hyphen, which is not the schema.org spelling.
        "employment_type": jp.get("employmentType"),
        "salary_text": salary,
        "published": jp.get("datePosted"),
        # validThrough is datePosted + 30 days on every ad measured, so it is
        # a formula, not an expiry. Deliberately not emitted as `closes`.
        "valid_through_formula": jp.get("validThrough"),
        "description": jp.get("description"),
        "json_ld": True,
    }


def sweep(site, metier, region, pages, delay, details):
    seen, rows, page_no, cap = set(), 0, 1, None
    while page_no <= pages:
        page = get(site, listing_path(metier, region, page_no))
        if cap is None:
            cap = last_page(page)
            if cap is not None:
                print(f"[jobology] pagination advertises {cap} page(s)",
                      file=sys.stderr)
        found = ad_ids(page)
        fresh = [(i, s) for i, s in found if i not in seen]
        if page_no == 1 and not found:
            die(f"no ads at all on /emploi/{metier}"
                + (f"/{region}" if region else "")
                + f".aspx for {site}. That is what a **wrong slug** looks "
                  "like here — 200, no error, an empty board. Check it with "
                  "`metiers --site " + site + "` before believing the trade "
                  "has no openings.")
        for ident, slug in fresh:
            seen.add(ident)
            print(json.dumps(card(site, ident, slug) if details else {
                "id": ident,
                "ledger_id": f"jobology:{site}:{ident}",
                "url": f"https://www.{site}/offre-emploi/{slug}-{ident}.aspx",
                "site": site,
            }, ensure_ascii=False))
            rows += 1
            if details:
                time.sleep(delay)
        # Two independent brakes, because this board stops on neither by
        # itself: past the last page it keeps serving twenty plausible ads
        # for any page number, and a repeat request returns a different set.
        if not fresh:
            print(f"[jobology] page {page_no} brought nothing new — stopping",
                  file=sys.stderr)
            break
        if cap is not None and page_no >= cap:
            print(f"[jobology] reached the advertised last page ({cap})",
                  file=sys.stderr)
            break
        page_no += 1
        time.sleep(delay)
    print(f"[jobology] {rows} ads from {site} — {metier}"
          + (f" / {region}" if region else ""), file=sys.stderr)
    if rows and rows % PER_PAGE == 0 and cap and page_no < cap:
        print("[jobology] stopped before the advertised end; raise --pages",
              file=sys.stderr)


def cmd_sites(_a):
    for host, (sector, ads) in SITES.items():
        print(json.dumps({"site": host, "sector": sector,
                          "ads_announced_2026_08_31": ads},
                         ensure_ascii=False))


def cmd_metiers(a):
    slugs = metier_vocabulary(check_site(a.site))
    print(f"[jobology] {len(slugs)} métier slugs on {a.site}", file=sys.stderr)
    for s in slugs:
        print(s)


def cmd_regions(a):
    for r in regions(check_site(a.site)):
        print(r)


def cmd_search(a):
    site = check_site(a.site)
    sweep(site, a.metier, a.region, a.pages, a.delay, not a.no_details)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("sites", help="the nine boards").set_defaults(func=cmd_sites)

    m = sub.add_parser("metiers", help="métier slugs a site publishes")
    m.add_argument("--site", required=True)
    m.set_defaults(func=cmd_metiers)

    r = sub.add_parser("regions", help="region slugs a site publishes")
    r.add_argument("--site", required=True)
    r.set_defaults(func=cmd_regions)

    s = sub.add_parser("search", help="sweep one métier on one site")
    s.add_argument("--site", required=True)
    s.add_argument("--metier", required=True, help="slug, e.g. chauffeur-spl")
    s.add_argument("--region", help="slug, e.g. occitanie")
    s.add_argument("--pages", type=int, default=5, help="20 ads each")
    s.add_argument("--delay", type=float, default=0.5)
    s.add_argument("--no-details", action="store_true",
                   help="listing only, no ad page fetched")
    s.set_defaults(func=cmd_search)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
