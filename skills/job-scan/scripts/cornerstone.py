#!/usr/bin/env python3
"""Cornerstone OnDemand — an ATS, one tenant at a time: the tenant's career site on `<slug>.csod.com/ux/ats/careersite/<site>/home` is a shell whose `csod.context` carries a per-visitor anonymous token and the search API's host, and the page fills its list by `POST <cloud>/rec-job-search/external/jobs` — the adapter replays that call with the page's own parameters, walks its pages, reads the requisition's details the way the page does, and never emits a person's id. Issue #456.

  cornerstone.py jobs --tenant henkel/1 [--country-code PL] [--max-pages N]     the tenant's requisitions (the page, then one API call a page of 25)
  cornerstone.py jobs --tenant https://laerdal.csod.com/ux/ats/careersite/4/home?c=laerdal
  cornerstone.py ad --url https://henkel.csod.com/ux/ats/careersite/1/home/requisition/88785?c=henkel

WHAT IT IS. Cornerstone OnDemand is the software behind an employer's «Careers» page (Henkel,
Laerdal, universities, administrations). **One adapter covers every employer that uses it, in
every country; the user names the tenant** as `<slug>/<site>` — the subdomain and the career-site
number the URL spells (`henkel.csod.com/ux/ats/careersite/1/…` → `henkel/1`), as for iCIMS or
SparkHire.

THE RULES. `<slug>.csod.com/robots.txt` is `User-agent: *` / `Crawl-delay: 10` and nothing else —
preceded by a byte-order mark that the guard mis-read as «no group» until #738; **10 s between two
requests to a tenant host is the host's own rule**, and `Pace` reads it. The API host
(`eu-fra.api.csod.com` for Henkel — the page names it in `endpoints.cloud`, never composed here)
answers its rules path with a page that is not a rules file: an absence of rules, 2 s is ours.

THE PAGE, THE TOKEN, THE CALLS. The career site (200, 5.3–5.5 KB) is `<div id="cs-root">` plus
`csod.context = {"corp": "henkel", "user": -100, "cultureID": 2, "cultureName": "en-GB",
"endpoints": {"cloud": "https://eu-fra.api.csod.com/", "api": "/"}, "token": "<JWT>", …}` — the
token is anonymous (`sub: -100`), issued to every visitor, three hours long, and lists the services
it opens (`rurls`); the page also sets session cookies (`ASP.NET_SessionId`, `cscx`) that the
tenant-host services require beside the token. Replayed exactly as the page does (the 14.09
judgment on StaffPoint, Eezy, SparkHire — a route the page calls, with the page's own parameters):

  POST <cloud>rec-job-search/external/jobs   Authorization: Bearer <token>, CSOD-Accept-Language
       {careerSiteId, careerSitePageId, pageNumber, pageSize, cultureId, cultureName, searchText: "",
        states: [], countryCodes: [], cities: [], placeID: "", radius, postingsWithinDays, …}
       → data.totalCount (the stated count), data.requisitions[] (requisitionId, displayJobTitle,
         locations[{city, state, country}], postingEffectiveDate, postingExpirationDate,
         externalDescription as text), data.filters (Country, State, City, DatePosted)
  GET  https://<slug>.csod.com/services/x/job-requisition/v2/requisitions/<id>/jobDetails?cultureId=N
       (token + the page's cookies) → displayTitle, ref, externalDescription (HTML), primaryLocation,
         additionalLocations, openDate, allowApply, companyApplyUrl, availableCultures — and
         hiringManagerId, owners, reviewers (people's ids: never emitted)

Henkel measured 2026-09-19 14:0x UTC: 1 083 requisitions stated, 25 a page; `countryCodes: ["PL"]`
narrows to 12 (a filter that reduces); the requisition's `jobDetails` 200 with the page's cookies,
401 «Check your credentials» without them.

**WITHHELD:** `hiringManagerId`, `owners`, `reviewers`, `positionOUId` (people and org ids) never
emitted; the descriptions scrubbed of e-mail addresses and telephone numbers; the application
(`companyApplyUrl` is the requisition page, printed as `url`; the apply workflow never touched);
`contacts_withheld` on every record. The token is used for the two calls the page makes and is
never printed.
"""

import argparse
import html as htmlmod
import http.cookiejar
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

TENANT_HOST_RE = re.compile(r"^([a-z0-9][a-z0-9\-]*)\.csod\.com$")
API_HOST_RE = re.compile(r"^[a-z0-9\-]+\.api\.csod\.com$")
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE_SIZE = 25

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\d[\d\s().\-]{7,}\d(?!\w)")   # an international shape: 9+ digits with separators — the descriptions are prose, not numbers
TENANT_RE = re.compile(r"^([a-z0-9][a-z0-9\-]*)/(\d+)$")
SITE_RE = re.compile(r"^/ux/ats/careersite/(\d+)/home(?:/requisition/(\d+))?/?$")
CONTEXT_RE = re.compile(r"csod\.context\s*=\s*(\{.*?\})\s*;\s*</script>", re.S)
_PACES = {}
_JARS = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[cornerstone] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def is_ours(host):
    return bool(TENANT_HOST_RE.match(host) or API_HOST_RE.match(host))


def opener(host):
    """One cookie jar per tenant host: the page's session cookies, replayed as the page does."""
    if host not in _JARS:
        _JARS[host] = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    return _JARS[host]


def request(url, accept="text/html,application/xhtml+xml", headers=None, data=None):
    parts = urllib.parse.urlsplit(url)
    if not is_ours(parts.netloc):
        die(f"{url}: not a Cornerstone host — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(parts.netloc, Pace(parts.netloc, own=2.0)).wait()   # the tenant's Crawl-delay: 10 is read by Pace; 2 s is ours where none is written
    h = {"User-Agent": UA, "Accept": accept, "Accept-Language": "en"}
    h.update(headers or {})
    req = urllib.request.Request(wire_url(url), headers=h, data=data, method="POST" if data is not None else "GET")
    try:
        with opener(parts.netloc).open(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", markup or "")
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span|font)\b[^>]*>", "", t)   # inline tags leave no space behind
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def tenant_of(arg):
    """`<slug>/<site>` or the career-site URL → (slug, site)."""
    s = arg.strip()
    if "://" in s or ".csod.com" in s:
        parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
        h = TENANT_HOST_RE.match(parts.netloc)
        m = SITE_RE.match(parts.path)
        if not h or not m:
            die(f"{arg}: not a Cornerstone career-site address (https://<slug>.csod.com/ux/ats/careersite/<site>/home)")
        return h.group(1), m.group(1)
    m = TENANT_RE.match(s)
    if not m:
        die(f"{arg}: a tenant is written <slug>/<site> as the career-site URL spells it — henkel/1")
    return m.group(1), m.group(2)


def page_url(slug, site, req_id=None):
    tail = f"/requisition/{req_id}" if req_id else ""
    return f"https://{slug}.csod.com/ux/ats/careersite/{site}/home{tail}?c={slug}"


def context(slug, site, req_id=None):
    """The tenant's page → its `csod.context` (corp, cultureID, cultureName, endpoints.cloud, token)."""
    url = page_url(slug, site, req_id)
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — no such tenant or site", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    m = CONTEXT_RE.search(body)
    if not m:
        die(f"{url}: 200 without csod.context — the page changed; not an empty board", EXIT_PARTIAL)
    try:
        ctx = json.loads(m.group(1))
    except ValueError:
        die(f"{url}: csod.context is not JSON — the page changed", EXIT_PARTIAL)
    if ctx.get("corp") != slug:
        die(f"{url}: the page's corp {ctx.get('corp')!r} is not the address's {slug!r}", EXIT_PARTIAL)
    cloud = (ctx.get("endpoints") or {}).get("cloud") or ""
    if not ctx.get("token") or not API_HOST_RE.match(urllib.parse.urlsplit(cloud).netloc):
        die(f"{url}: csod.context without a token or a *.api.csod.com cloud endpoint — the page changed", EXIT_PARTIAL)
    return ctx


def auth(ctx):
    return {"Authorization": f"Bearer {ctx['token']}", "CSOD-Accept-Language": ctx.get("cultureName") or "en-US"}


def search_page(ctx, site, page, country_code=None):
    body = {"careerSiteId": int(site), "careerSitePageId": int(site), "pageNumber": page, "pageSize": PAGE_SIZE,
            "cultureId": ctx.get("cultureID"), "cultureName": ctx.get("cultureName"), "searchText": "",
            "states": [], "countryCodes": [country_code.upper()] if country_code else [], "cities": [], "placeID": "",
            "radius": None, "postingsWithinDays": None, "customFieldCheckboxKeys": [], "customFieldDropdowns": [], "customFieldRadios": []}
    url = ctx["endpoints"]["cloud"].rstrip("/") + "/rec-job-search/external/jobs"
    h = dict(auth(ctx), **{"Content-Type": "application/json"})
    code, raw = request(url, accept="application/json", headers=h, data=json.dumps(body).encode("utf-8"))
    if code != 200:
        die(f"the search API, page {page}: HTTP {code}", EXIT_PARTIAL)
    try:
        d = json.loads(raw)
    except ValueError:
        die(f"the search API, page {page}: 200 and not JSON — the route changed", EXIT_PARTIAL)
    data = d.get("data") if isinstance(d, dict) else None
    if not isinstance(data, dict) or not isinstance(data.get("requisitions"), list):
        die(f"the search API, page {page}: 200 without data.requisitions — the route changed", EXIT_PARTIAL)
    return data


def record(r, slug, site):
    locs = [l for l in (r.get("locations") or []) if isinstance(l, dict)]
    first = locs[0] if locs else {}
    rid = r.get("requisitionId")
    return {
        "source": "cornerstone", "tenant": f"{slug}/{site}", "country": first.get("country") or None,
        "countries": sorted({l.get("country") for l in locs if l.get("country")}) or None,
        "ledger_id": f"cornerstone:{slug}:{rid}", "id": rid,
        "url": page_url(slug, site, rid),
        "title": (r.get("displayJobTitle") or "").strip() or None, "company": slug,
        "place": first.get("city") or None, "region": first.get("state") or None,
        "posted": r.get("postingEffectiveDate") or None,
        "expires": (r.get("postingExpirationDate") or None) if r.get("postingExpirationDate") not in ("-", "") else None,
        "description": scrub(text(r.get("externalDescription"))),
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    slug, site = tenant_of(a.tenant)
    ctx = context(slug, site)
    rows, seen, stated, page = [], set(), None, 1
    while True:
        data = search_page(ctx, site, page, a.country_code)
        if stated is None:
            stated = data.get("totalCount")
        got = [r for r in data["requisitions"] if isinstance(r, dict)]
        fresh = [r for r in got if r.get("requisitionId") not in seen]
        if page > 1 and got and not fresh:
            die(f"page {page} repeats page 1 — the pager does not page; stopping", EXIT_PARTIAL)
        for r in fresh:
            seen.add(r.get("requisitionId"))
            rows.append(record(r, slug, site))
        if not got or len(got) < PAGE_SIZE or (isinstance(stated, int) and len(seen) >= stated):
            break
        if a.max_pages and page >= a.max_pages:
            note(f"stopped at page {page} by request")
            break
        if isinstance(stated, int) and page >= -(-stated // PAGE_SIZE):
            break   # the stated count's last page — a pager that keeps answering past it is not walked
        page += 1
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    where = f" for {a.country_code.upper()}" if a.country_code else ""
    if isinstance(stated, int):
        if stated == 0:
            note(f"{slug}/{site}: 0 requisitions{where} — the API states 0 (200); the tenant publishes none today, not an error.")
        elif len(rows) == stated:
            note(f"{th(len(rows))} emitted{where} — the API states {th(stated)}: equal.")
        elif a.max_pages and len(rows) < stated:
            note(f"{th(len(rows))} emitted{where} of the {th(stated)} the API states — walked {page} page(s) by request, not a shortfall.")
        else:
            note(f"{th(len(rows))} emitted{where} — the API states {th(stated)}: {th(abs(stated - len(rows)))} {'short' if len(rows) < stated else 'over'}.")
    else:
        note(f"{th(len(rows))} emitted{where} — the API stated no totalCount (the route changed?); the count is ours.")


def ad_of(arg):
    parts = urllib.parse.urlsplit(arg.strip())
    h = TENANT_HOST_RE.match(parts.netloc)
    m = SITE_RE.match(parts.path)
    if not h or not m or not m.group(2):
        die(f"{arg}: not a Cornerstone requisition address (https://<slug>.csod.com/ux/ats/careersite/<site>/home/requisition/<id>)")
    return h.group(1), m.group(1), m.group(2)


def cmd_ad(a):
    slug, site, rid = ad_of(a.url)
    ctx = context(slug, site, rid)   # the requisition page: its token and its cookies
    url = f"https://{slug}.csod.com/services/x/job-requisition/v2/requisitions/{rid}/jobDetails?cultureId={ctx.get('cultureID')}"
    code, raw = request(url, accept="application/json", headers=auth(ctx))
    if code == 404:
        die(f"{url}: HTTP 404 — no such requisition", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    try:
        d = json.loads(raw).get("data") or {}
    except (ValueError, AttributeError):
        die(f"{url}: 200 and not JSON — the route changed", EXIT_PARTIAL)
    if not d.get("displayTitle"):
        die(f"{url}: 200 without displayTitle — the route changed", EXIT_PARTIAL)
    p = d.get("primaryLocation") or {}
    extra = [l for l in (d.get("additionalLocations") or []) if isinstance(l, dict)]
    out = {
        "source": "cornerstone", "tenant": f"{slug}/{site}", "country": p.get("country") or None,
        "countries": sorted({l.get("country") for l in [p] + extra if l.get("country")}) or None,
        "ledger_id": f"cornerstone:{slug}:{rid}", "id": int(rid), "ref": d.get("ref") or None,
        "url": page_url(slug, site, rid),
        "title": d["displayTitle"].strip(), "company": slug,
        "place": p.get("city") or None, "region": p.get("state") or None, "location": p.get("title") or None,
        "posted": (d.get("openDate") or "")[:10] or None,
        "apply_open": str(d.get("allowApply")).lower() == "true",
        "description": scrub(text(d.get("externalDescription"))),
        "contacts_withheld": True,
    }
    print(json.dumps(out, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Cornerstone OnDemand — one tenant's requisitions, the calls its page makes")
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the tenant's requisitions")
    j.add_argument("--tenant", required=True, help="<slug>/<site> (henkel/1) or the career-site URL")
    j.add_argument("--country-code", help="ISO2 — the API's countryCodes filter")
    j.add_argument("--max-pages", type=int, default=0, help="stop after N pages of 25 (0 = all)")
    j.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one requisition")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
