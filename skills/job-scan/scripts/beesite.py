#!/usr/bin/env python3
"""BeeSite (milch & zucker) — an ATS, one tenant at a time: the employer's career portal (`karriere.johanniter.de`, `jobs.lvr.de`) names its own search API in `/script/gjb_scripts.js` (`gjbAddress`, a host under `beesite.de`), and its list page fills itself by GET `<gjbAddress>search/?data=<JSON>` — the adapter replays that call with the page's own parameters, walks to the stated count, and never emits the ad's contact block or street. Issue #479.

  beesite.py jobs --tenant karriere.johanniter.de [--country-code DE] [--max-pages N]     the tenant's positions (1 + ceil(N/100) requests)
  beesite.py jobs --tenant https://jobs.lvr.de/index.php?ac=search_result
  beesite.py ad --url https://jobs.lvr.de/index.php?ac=jobad&id=20817

WHAT IT IS. BeeSite Recruiting is milch & zucker's applicant management system — the software
behind a German employer's «Karriereportal» (Die Johanniter, LVR, Universitätsklinikum Heidelberg;
large accounts and public bodies). Its signature in a URL: `index.php?ac=search_result` (the list)
and `index.php?ac=jobad&id=<n>` (an ad), on the employer's own host. **One adapter covers every
employer that uses it; the user names the tenant** by its careers host, as for iCIMS or Personio.

THE RULES. Taken per host on the exact path: the tenant's host (`robots.txt` absent or read, open
on `/index.php` and `/script/`), and the API host the tenant's script names (absent). No
Crawl-delay written anywhere read; 2 s is ours, per host.

THE SCRIPT, THE ADDRESS, THE CALL. `/script/gjb_scripts.js` (200, ~1.4 KB) ends with
`var gjbAddress = "https://api02-johanniter.beesite.de/";` — the «Global Jobboard» API of this
tenant, printed for every visitor. **A host without that script is not a tenant** (`jobs.pwc.de`:
404 — a former one), exit 3; an address outside `beesite.de` is refused before any request (7).
The page's client (`jquery.jobboard.container.js`) then GETs `<gjbAddress>search/?data=<JSON>` with
`{"LanguageCode": "DE", "SearchParameters": {"FirstItem": 1, "CountItem": 10, "Sort": [...],
"MatchedObjectDescriptor": [the fields it wants]}, "SearchCriteria": []}` — the HR-XML shape — and
the API answers `SearchResult.SearchResultCountAll` (**the stated count**) and
`SearchResultItems[].MatchedObjectDescriptor`: ID, PositionTitle, PositionURI, PositionLocation
(CountryCode, CountryName, CountrySubDivisionName, CityName), JobCategory, CareerLevel,
PositionIndustry, PositionSchedule, PositionOfferingType, ParentOrganizationName,
PublicationStartDate, PublicationEndDate. The adapter asks 100 an item (the client asks 10 on
screen and 10 000 for its map) and walks `FirstItem` to the stated count; a page that repeats the
previous page's ids ends the walk with exit 6.

THE AD. `index.php?ac=jobad&id=<n>` (200, 95–135 KB) carries one schema.org `JobPosting` — title,
description (HTML, escaped), datePosted, validThrough, employmentType, hiringOrganization,
jobLocation (with `streetAddress` and `postalCode`), identifier `J0000<id>` — and a
`job-ad-contact` block with a name and a telephone. **Emitted: the posting's text, scrubbed;
locality, region and country of the location. Never: the street, the postal code, the contact
block, any e-mail address or telephone in the text.** `contacts_withheld` on every record.

`--country-code` filters on `PositionLocation.CountryCode` when the API gives one and says so
when it does not (Johanniter's list carries `CountryName` only — «Deutschland» — when the code is
not asked; it is asked here).

Measured 2026-09-21 06:52–06:56 UTC by the declared client, the guard on the exact path, two
reads each: `karriere.johanniter.de` → `api02-johanniter.beesite.de`, **1 272** positions stated;
`jobs.lvr.de` → `lvr-beesite-gjb.app.beesite.de`, **320** stated (a 100-item page accepted, the
last page 20); `jobs.pwc.de` 404 on the script and the list (not a tenant today);
`karriere.klinikum.uni-heidelberg.de` sends its leaf without the intermediate
(CERTIFICATE_VERIFY_FAILED — the `_tls` shape, not measured here).
"""

import argparse
import html as htmlmod
import json
import math
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

import _ldjson
from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

VENDOR_DOMAIN = ".beesite.de"
PAGE_SIZE = 100
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")   # «0228 668-215», «+49 (0)221 809-0»: 8+ digits with the separators German numbers use
DATE_RE = re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b")                       # «ab 15.11.2026» is a date, not a telephone — it stays
ADDRESS_RE = re.compile(r'var\s+gjbAddress\s*=\s*"(https://[^"]+)"')
AD_ID_RE = re.compile(r"(?:^|&)id=(\d+)(?:&|$)")
FIELDS = ["ID", "PositionTitle", "PositionURI", "PositionLocation.CountryCode", "PositionLocation.CountryName",
          "PositionLocation.CountrySubDivisionName", "PositionLocation.CityName", "JobCategory.Name",
          "CareerLevel.Name", "PositionIndustry.Name", "PositionSchedule.Name", "PositionOfferingType.Name",
          "ParentOrganizationName", "OrganizationShortName", "PublicationStartDate", "PublicationEndDate"]
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[beesite] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, hosts, accept="text/html,application/xhtml+xml"):
    """One GET under the declared identity — only to the tenant's host or the API host its script names."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc not in hosts:
        die(f"{url}: not the tenant's host nor its API — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(parts.netloc, Pace(parts.netloc, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": accept, "Accept-Language": "de, en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", markup or "")
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span)\b[^>]*>", "", t)   # inline tags leave no space behind
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def tenant_of(arg):
    """A careers host, or any URL on it → the host."""
    s = arg.strip()
    parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
    host = parts.netloc.lower()
    if not host or "/" in host or not re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", host):
        die(f"{arg}: a tenant is its careers host — karriere.johanniter.de, jobs.lvr.de — or a URL on it")
    return host


def api_of(host):
    """The tenant's `/script/gjb_scripts.js` → its API base (`https://<x>.beesite.de/`)."""
    url = f"https://{host}/script/gjb_scripts.js"
    code, body = request(url, {host}, accept="*/*")
    if code == 404:
        die(f"{url}: HTTP 404 — the host does not serve BeeSite's jobboard script: not a tenant (today)", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    m = ADDRESS_RE.search(body)
    if not m:
        die(f"{url}: 200 without `var gjbAddress = \"https://…\"` — the script changed; not an empty board", EXIT_PARTIAL)
    base = m.group(1).rstrip("/") + "/"
    api_host = urllib.parse.urlsplit(base).netloc.lower()
    if not api_host.endswith(VENDOR_DOMAIN) or api_host == VENDOR_DOMAIN[1:]:
        die(f"{url}: the script names {api_host}, not a host under {VENDOR_DOMAIN[1:]} — never sent", EXIT_REFUSED)
    return base, api_host


def search(base, api_host, first, count):
    q = {"LanguageCode": "DE",
         "SearchParameters": {"FirstItem": first, "CountItem": count,
                              "Sort": [{"Criterion": "PublicationStartDate", "Direction": "DESC"}],
                              "MatchedObjectDescriptor": FIELDS},
         "SearchCriteria": []}
    url = base + "search/?" + urllib.parse.urlencode({"data": json.dumps(q, separators=(",", ":"))})
    code, body = request(url, {api_host}, accept="application/json")
    if code != 200:
        die(f"the search API: HTTP {code}", EXIT_PARTIAL)
    try:
        data = json.loads(body)
    except ValueError:
        die("the search API: 200 and not JSON — the route changed", EXIT_PARTIAL)
    sr = data.get("SearchResult") if isinstance(data, dict) else None
    if not isinstance(sr, dict) or not isinstance(sr.get("SearchResultItems"), list) or not isinstance(sr.get("SearchResultCountAll"), int):
        die("the search API: 200 without SearchResult.SearchResultItems and SearchResultCountAll — the route changed; not an empty board", EXIT_PARTIAL)
    return sr["SearchResultCountAll"], [i.get("MatchedObjectDescriptor") or {} for i in sr["SearchResultItems"] if isinstance(i, dict)]


def first_name(d, key):
    """`[{"Name": …}, …]` → the names joined; `[]` or absent → None."""
    v = d.get(key)
    if isinstance(v, list):
        names = [x.get("Name") for x in v if isinstance(x, dict) and x.get("Name")]
        return " / ".join(names) or None
    return None


def record(d, host):
    loc = (d.get("PositionLocation") or [{}])[0] if isinstance(d.get("PositionLocation"), list) else {}
    pid = str(d.get("ID") or "").strip() or None
    return {
        "source": "beesite", "tenant": host,
        "country": (loc.get("CountryCode") or "").upper() or None, "country_name": loc.get("CountryName") or None,
        "ledger_id": f"beesite:{host}:{pid}", "id": pid,
        "url": d.get("PositionURI") or (f"https://{host}/index.php?ac=jobad&id={pid}" if pid else None),
        "title": (d.get("PositionTitle") or "").strip() or None,
        "company": d.get("ParentOrganizationName") or d.get("OrganizationShortName") or None,
        "place": loc.get("CityName") or None, "region": loc.get("CountrySubDivisionName") or None,
        "category": first_name(d, "JobCategory"), "career_level": first_name(d, "CareerLevel"),
        "industry": first_name(d, "PositionIndustry"), "schedule": first_name(d, "PositionSchedule"),
        "contract": first_name(d, "PositionOfferingType"),
        "published": (d.get("PublicationStartDate") or "")[:10] or None, "expires": (d.get("PublicationEndDate") or "")[:10] or None,
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    base, api_host = api_of(host)
    stated, items = search(base, api_host, 1, PAGE_SIZE)
    rows, seen = [], set()
    pages_total = max(1, math.ceil(stated / PAGE_SIZE))
    page = 1
    while True:
        ids = {str(d.get("ID")) for d in items if d.get("ID")}
        if page > 1 and ids and ids <= seen:
            die(f"page {page} repeats the previous page's ids — the walk ended at {th(len(rows))} of {th(stated)} stated", EXIT_PARTIAL)
        for d in items:
            if str(d.get("ID")) in seen:
                continue
            seen.add(str(d.get("ID")))
            rows.append(record(d, host))
        if page >= pages_total or not items or (a.max_pages and page >= a.max_pages):
            break
        page += 1
        _stated, items = search(base, api_host, (page - 1) * PAGE_SIZE + 1, PAGE_SIZE)
    if a.country_code:
        cc = a.country_code.upper()
        coded = sum(1 for r in rows if r["country"])
        rows = [r for r in rows if r["country"] == cc]
        if coded == 0:
            note(f"--country-code {cc}: the API gave no CountryCode on any of the {th(len(seen))} positions — nothing to filter on, 0 emitted; `country_name` carries what it says.")
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if stated == 0:
        note(f"{host}: 0 positions — the API states 0 today (SearchResultCountAll), the list answered 200; not an error.")
    elif a.country_code:
        note(f"{th(len(rows))} emitted for {a.country_code.upper()} of the {th(len(seen))} read; the API states {th(stated)} for {host}.")
    else:
        note(f"{th(len(rows))} emitted, the API states {th(stated)} for {host}" + (f" — {th(stated - len(rows))} short (the walk stopped at page {page})" if len(rows) < stated else "") + ".")
    note("the ad's contact block, street and postal code never emitted; texts scrubbed.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    host = parts.netloc.lower()
    m = AD_ID_RE.search(parts.query or "")
    if parts.scheme != "https" or not host or parts.path != "/index.php" or "ac=jobad" not in (parts.query or "") or not m:
        die(f"{a.url}: not a BeeSite ad address (https://<tenant>/index.php?ac=jobad&id=<n>)")
    pid = m.group(1)
    url = f"https://{host}/index.php?ac=jobad&id={pid}"
    code, body = request(url, {host})
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    posts = _ldjson.postings(body)
    if not posts:
        if 'data-jobad-id="' not in body:
            die(f"{url}: 200 without a JobPosting and without the ad container — gone or the page changed", EXIT_GONE)
        die(f"{url}: the ad container is there and no JobPosting is — the page changed", EXIT_PARTIAL)
    p = posts[0]
    org = p.get("hiringOrganization") if isinstance(p.get("hiringOrganization"), dict) else {}
    jl = p.get("jobLocation")
    jl = jl[0] if isinstance(jl, list) and jl else (jl if isinstance(jl, dict) else {})
    addr = jl.get("address") if isinstance(jl.get("address"), dict) else {}
    ident = p.get("identifier") if isinstance(p.get("identifier"), dict) else {}
    row = {
        "source": "beesite", "tenant": host,
        "country": (addr.get("addressCountry") or "").upper()[:2] or None,
        "ledger_id": f"beesite:{host}:{pid}", "id": pid, "url": url,
        "title": scrub(text(htmlmod.unescape(p.get("title") or ""))),
        "company": org.get("name") or None,
        "place": addr.get("addressLocality") or None, "region": addr.get("addressRegion") or None,
        "employment_type": p.get("employmentType") or None,
        "published": (p.get("datePosted") or "")[:10] or None, "expires": (p.get("validThrough") or "")[:10] or None,
        "reference": ident.get("value") or None,
        "description": scrub(text(htmlmod.unescape(p.get("description") or ""))),
        "contacts_withheld": True,
    }
    print(json.dumps(row, ensure_ascii=False))
    note(f"{url}: read from the page's JobPosting; the contact block, street and postal code never emitted; text scrubbed.")


def main(argv=None):
    p = argparse.ArgumentParser(description="BeeSite (milch & zucker) — one tenant's positions through the search API its own page calls, with the page's own parameters; contacts and streets never emitted. Issue #479.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="one tenant's whole board (the script, then ceil(N/100) API pages)")
    j.add_argument("--tenant", required=True, help="the careers host (karriere.johanniter.de) or a URL on it")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="keep one country (the API's PositionLocation.CountryCode)")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0, help="stop after N API pages of 100 (0 = to the stated count)")
    j.set_defaults(fn=cmd_jobs)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
