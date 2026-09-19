#!/usr/bin/env python3
"""Dayforce (ex-Ceridian) — an ATS, one tenant at a time: the tenant's candidate portal on `jobs.dayforcehcm.com/<lang>/<slug>/<board>` is a Next.js page whose app fills its list by `POST /api/geo/<slug>/jobposting/search` with the portal's cookies and next-auth's CSRF token — replayed as the page does, paged 25 at a time to the stated `maxCount`; the ad is in the requisition page's own `__NEXT_DATA__`. Issue #458.

  dayforce.py jobs --tenant car [--board CANDIDATEPORTAL] [--lang en-US] [--country-code US] [--max-pages N]
  dayforce.py jobs --tenant https://jobs.dayforcehcm.com/en-US/car/CANDIDATEPORTAL
  dayforce.py ad --url https://jobs.dayforcehcm.com/en-US/car/CANDIDATEPORTAL/jobs/12216

WHAT IT IS. Dayforce is a North-American HR suite whose hiring module publishes the employer's
«Careers» page (Carnegie Museums of Pittsburgh `car`, WoodmenLife, Door County, Dayforce's own
`hcmportal`). **One adapter covers every employer that uses it, in every country; the user names
the tenant** by its namespace — the segment after the language in the portal URL
(`jobs.dayforcehcm.com/en-US/car/CANDIDATEPORTAL` → `car`, board `CANDIDATEPORTAL`) — as for
iCIMS or Cornerstone.

THE RULES. `jobs.dayforcehcm.com` answers its rules path 200 with a page that is not a rules file —
an absence of rules, `certain: False`, the transport decides; no Crawl-delay, 2 s is ours.

THE PAGE, THE CALLS. The portal (200, 434 KB) is Next.js with `USE_SSR`: its `__NEXT_DATA__`
dehydrates only `site-info` (`clientId`, `jobBoardId`, the board's settings — and
`clientCorrespondanceEmailAddress`, never emitted); the list is fetched by the app. Read in the
page's `_app` chunk (the axios interceptor adds `X-CSRF-TOKEN: getCsrfToken()` to every POST; the
search hook posts the router's query) and replayed by the declared client on 2026-09-20:

  GET  /en-US/<slug>/<board>                       → the portal; sets the next-auth cookies
  GET  /api/auth/csrf                              → {"csrfToken": …}
  POST /api/geo/<slug>/jobposting/search           (X-CSRF-TOKEN, the cookies, JSON)
       {clientNamespace, jobBoardCode, cultureCode, searchText: "", paginationStart: (page-1)*25, distanceUnit: 0}
       → maxCount (THE STATED COUNT), offset, count, jobPostings[] (jobPostingId, jobReqId, jobTitle,
         jobDescription as text, postingStartTimestampUTC, postingExpiryTimestampUTC, isEvergreen,
         hasVirtualLocation, postingLocations[{formattedAddress, cityName, stateCode, isoCountryCode}])

Without the token the search answers 403 «Forbidden»; with it, 200. The requisition page
`/en-US/<slug>/<board>/jobs/<id>` (200, 351 KB) dehydrates the `jobs` query: jobTitle, jobReqId,
postingStart/Expiry, isoCurrencyRegion, jobPostingContent (header, description, footer as HTML),
postingLocations, jobPostingAttributes (JobFamily, PayType…) — served to the client, no call.

Measured 2026-09-20: Carnegie Museums (`car`) maxCount 15, 15 emitted, equal; the ad 12216
(Museum Educator I) from its page.

**WITHHELD:** the client's correspondence address (`site-info`), `postingAppliedStatus`,
`searchScore`, assessment and template ids never emitted; descriptions scrubbed of e-mail
addresses and telephone numbers; `contacts_withheld` on every record; the application (an
account, a form) never touched.
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

HOST = "jobs.dayforcehcm.com"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE_SIZE = 25

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$])\+?\d[\d\s().\-]{7,}\d(?!\w)")   # an international shape: 9+ digits with separators
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_\-]*$", re.I)
LANG_RE = re.compile(r"^[a-z]{2}(?:-[A-Za-z]{2,4})?$")
PORTAL_RE = re.compile(r"^/([a-z]{2}(?:-[A-Za-z]{2,4})?)/([^/]+)/([^/]+)/?$")
AD_RE = re.compile(r"^/([a-z]{2}(?:-[A-Za-z]{2,4})?)/([^/]+)/([^/]+)/jobs/(\d+)/?$")
NEXT_DATA_RE = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written; 2 s is ours
_JAR = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_JAR))


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[dayforce] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, accept="text/html,application/xhtml+xml", headers=None, data=None):
    """One host, one cookie jar: the portal's cookies are replayed as the page does."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc != HOST:
        die(f"{url}: not a Dayforce host — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    h = {"User-Agent": UA, "Accept": accept, "Accept-Language": "en"}
    h.update(headers or {})
    req = urllib.request.Request(wire_url(url), headers=h, data=data, method="POST" if data is not None else "GET")
    try:
        with _OPENER.open(req, timeout=60) as r:
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


def tenant_of(arg, board, lang):
    """`<slug>` (+ --board, --lang) or the portal URL → (lang, slug, board)."""
    s = arg.strip()
    if "://" in s or s.startswith(HOST):
        parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
        m = PORTAL_RE.match(parts.path)
        if parts.netloc != HOST or not m:
            die(f"{arg}: not a Dayforce portal address (https://{HOST}/<lang>/<slug>/<board>)")
        return m.group(1), m.group(2), m.group(3)
    if not SLUG_RE.match(s) or not SLUG_RE.match(board) or not LANG_RE.match(lang):
        die(f"{arg}: a tenant is written as the namespace the portal URL spells — car (board {board}, lang {lang})")
    return lang, s, board


def portal_url(lang, slug, board, job_id=None):
    tail = f"/jobs/{job_id}" if job_id else ""
    return f"https://{HOST}/{lang}/{slug}/{board}{tail}"


def next_data(body, url):
    m = NEXT_DATA_RE.search(body)
    if not m:
        die(f"{url}: 200 without __NEXT_DATA__ — the page changed; not an empty board", EXIT_PARTIAL)
    try:
        return json.loads(m.group(1))
    except ValueError:
        die(f"{url}: __NEXT_DATA__ is not JSON — the page changed", EXIT_PARTIAL)


def queries(nd):
    return ((nd.get("props") or {}).get("pageProps") or {}).get("dehydratedState", {}).get("queries") or []


def site_info(nd):
    for q in queries(nd):
        k = q.get("queryKey") or []
        if k and k[0] == "site-info":
            return (q.get("state") or {}).get("data") or {}
    return {}


def open_portal(lang, slug, board):
    url = portal_url(lang, slug, board)
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — no such tenant or board", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    nd = next_data(body, url)
    si = site_info(nd)
    if si.get("clientNamespace") and si.get("clientNamespace") != slug:
        die(f"{url}: the page's clientNamespace {si.get('clientNamespace')!r} is not the address's {slug!r}", EXIT_PARTIAL)
    if si.get("isDisabled"):
        note(f"{slug}/{board}: site-info says the board is disabled")
    return si


def csrf_token():
    code, body = request(f"https://{HOST}/api/auth/csrf", accept="application/json")
    if code != 200:
        die(f"/api/auth/csrf: HTTP {code}", EXIT_PARTIAL)
    try:
        tok = json.loads(body).get("csrfToken")
    except (ValueError, AttributeError):
        tok = None
    if not tok:
        die("/api/auth/csrf: 200 without csrfToken — the route changed", EXIT_PARTIAL)
    return tok


def search_page(slug, board, lang, token, page):
    body = {"clientNamespace": slug, "jobBoardCode": board, "cultureCode": lang, "searchText": "", "paginationStart": (page - 1) * PAGE_SIZE, "distanceUnit": 0}
    url = f"https://{HOST}/api/geo/{urllib.parse.quote(slug, safe='')}/jobposting/search"
    code, raw = request(url, accept="application/json", headers={"Content-Type": "application/json", "X-CSRF-TOKEN": token, "Referer": portal_url(lang, slug, board)},
                        data=json.dumps(body).encode("utf-8"))
    if code == 403:
        die(f"the search, page {page}: HTTP 403 — the token or the cookies were not accepted", EXIT_PARTIAL)
    if code != 200:
        die(f"the search, page {page}: HTTP {code}", EXIT_PARTIAL)
    try:
        d = json.loads(raw)
    except ValueError:
        die(f"the search, page {page}: 200 and not JSON — the route changed", EXIT_PARTIAL)
    if not isinstance(d, dict) or not isinstance(d.get("jobPostings"), list):
        die(f"the search, page {page}: 200 without jobPostings — the route changed", EXIT_PARTIAL)
    return d


def locations_of(p):
    return [l for l in (p.get("postingLocations") or []) if isinstance(l, dict)]


def record(p, lang, slug, board, company):
    locs = locations_of(p)
    first = locs[0] if locs else {}
    jid = p.get("jobPostingId")
    return {
        "source": "dayforce", "tenant": f"{slug}/{board}", "country": first.get("isoCountryCode") or None,
        "countries": sorted({l.get("isoCountryCode") for l in locs if l.get("isoCountryCode")}) or None,
        "ledger_id": f"dayforce:{slug}:{jid}", "id": jid, "ref": p.get("jobReqId"),
        "url": portal_url(lang, slug, board, jid),
        "title": (p.get("jobTitle") or "").strip() or None, "company": company,
        "place": first.get("cityName") or None, "region": first.get("stateCode") or None, "location": first.get("formattedAddress") or None,
        "remote": bool(p.get("hasVirtualLocation")) or None,
        "posted": (p.get("postingStartTimestampUTC") or "")[:10] or None, "expires": (p.get("postingExpiryTimestampUTC") or "")[:10] or None,
        "evergreen": bool(p.get("isEvergreen")) or None,
        "description": scrub(text(p.get("jobDescription"))),
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    lang, slug, board = tenant_of(a.tenant, a.board, a.lang)
    si = open_portal(lang, slug, board)
    company = si.get("candidateCorrespondenceClientName") or None
    token = csrf_token()
    rows, seen, stated, page = [], set(), None, 1
    while True:
        d = search_page(slug, board, lang, token, page)
        if stated is None:
            stated = d.get("maxCount") if isinstance(d.get("maxCount"), int) else None
        got = [p for p in d["jobPostings"] if isinstance(p, dict)]
        fresh = [p for p in got if p.get("jobPostingId") not in seen]
        if page > 1 and got and not fresh:
            die(f"page {page} repeats page 1 — the pager does not page; stopping", EXIT_PARTIAL)
        for p in fresh:
            seen.add(p.get("jobPostingId"))
            rows.append(record(p, lang, slug, board, company))
        if not got or len(got) < PAGE_SIZE or (isinstance(stated, int) and len(seen) >= stated):
            break
        if a.max_pages and page >= a.max_pages:
            note(f"stopped at page {page} by request")
            break
        if isinstance(stated, int) and page >= -(-stated // PAGE_SIZE):
            break   # the stated count's last page
        page += 1
    if a.country_code:
        rows = [r for r in rows if (r["country"] or "").upper() == a.country_code.upper()]
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    where = f" for {a.country_code.upper()}" if a.country_code else ""
    if isinstance(stated, int):
        if stated == 0:
            note(f"{slug}/{board}: 0 postings — the search states maxCount 0 (200); the tenant publishes none today, not an error.")
        elif a.country_code:
            note(f"{th(len(rows))} emitted{where} of the {th(len(seen))} walked — the search states {th(stated)}.")
        elif len(rows) == stated:
            note(f"{th(len(rows))} emitted — the search states {th(stated)}: equal.")
        elif a.max_pages and len(rows) < stated:
            note(f"{th(len(rows))} emitted of the {th(stated)} the search states — walked {page} page(s) by request, not a shortfall.")
        else:
            note(f"{th(len(rows))} emitted — the search states {th(stated)}: {th(abs(stated - len(rows)))} {'short' if len(rows) < stated else 'over'}.")
    else:
        note(f"{th(len(rows))} emitted{where} — the search stated no maxCount (the route changed?); the count is ours.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url.strip())
    m = AD_RE.match(parts.path)
    if parts.netloc != HOST or not m:
        die(f"{a.url}: not a Dayforce requisition address (https://{HOST}/<lang>/<slug>/<board>/jobs/<id>)")
    lang, slug, board, jid = m.group(1), m.group(2), m.group(3), int(m.group(4))
    url = portal_url(lang, slug, board, jid)
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — no such requisition", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    nd = next_data(body, url)
    job = None
    for q in queries(nd):
        k = q.get("queryKey") or []
        if k and k[0] == "jobs" and len(k) > 2 and isinstance(k[2], dict) and str(k[2].get("id")) == str(jid):
            job = (q.get("state") or {}).get("data")
    if not isinstance(job, dict) or not job.get("jobTitle"):
        die(f"{url}: 200 without the requisition in __NEXT_DATA__ — gone, or the page changed", EXIT_PARTIAL)
    si = site_info(nd)
    c = job.get("jobPostingContent") or {}
    desc = "\n".join(x for x in (text(c.get("jobDescriptionHeader")), text(c.get("jobDescription")), text(c.get("jobDescriptionFooter"))) if x) or None
    attrs = {x.get("name"): x.get("value") for x in (job.get("jobPostingAttributes") or []) if isinstance(x, dict) and x.get("name")}
    locs = locations_of(job)
    first = locs[0] if locs else {}
    out = {
        "source": "dayforce", "tenant": f"{slug}/{board}", "country": first.get("isoCountryCode") or None,
        "countries": sorted({l.get("isoCountryCode") for l in locs if l.get("isoCountryCode")}) or None,
        "ledger_id": f"dayforce:{slug}:{jid}", "id": jid, "ref": job.get("jobReqId"), "url": url,
        "title": job["jobTitle"].strip(), "company": si.get("candidateCorrespondenceClientName") or None,
        "place": first.get("cityName") or None, "region": first.get("stateCode") or None, "location": first.get("formattedAddress") or None,
        "remote": bool(job.get("hasVirtualLocation")) or None,
        "posted": (job.get("postingStartTimestampUTC") or "")[:10] or None, "expires": (job.get("postingExpiryTimestampUTC") or "")[:10] or None,
        "currency": job.get("isoCurrencyRegion") or None, "pay_type": attrs.get("PayType"), "job_family": attrs.get("JobFamily"),
        "description": scrub(desc),
        "contacts_withheld": True,
    }
    print(json.dumps(out, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Dayforce — one tenant's postings, the calls its portal makes")
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the tenant's postings")
    j.add_argument("--tenant", required=True, help="the namespace (car) or the portal URL")
    j.add_argument("--board", default="CANDIDATEPORTAL", help="the job board code (default CANDIDATEPORTAL)")
    j.add_argument("--lang", default="en-US", help="the culture code (default en-US)")
    j.add_argument("--country-code", help="ISO2 — filters on the first location's country")
    j.add_argument("--max-pages", type=int, default=0, help="stop after N pages of 25 (0 = all)")
    j.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one requisition")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
