#!/usr/bin/env python3
"""SparkHire Recruit (ex-Comeet) — an ATS, one tenant at a time: the tenant's careers page on `www.comeet.com/jobs/<slug>/<uid>` carries its `company_uid` and its public careers token in `COMPANY_DATA`, and the page fills its list by the careers API on `www.comeet.co` — the adapter replays that call with the page's own parameters, reads every published position with its details, and never emits the application address. Issue #452.

  sparkhire.py jobs --tenant quantummachines/D6.000 [--country-code IL]     the tenant's positions (2 requests: the page, the API)
  sparkhire.py jobs --tenant https://www.comeet.com/jobs/quantummachines/D6.000
  sparkhire.py ad --url <https://www.comeet.com/jobs/<slug>/<uid>/<position-slug>/<position-uid>>

WHAT IT IS. Comeet — bought by Spark Hire in 2023, its hosted careers pages still served by
`www.comeet.com` and its API by `www.comeet.co` — is the software behind an employer's «Careers»
page (Quantum Machines, CommIT, Paragon…). **One adapter covers every employer that uses it, in
every country; the user names the tenant** (`<slug>/<uid>` as the careers URL spells it), as for
Recruitee or iCIMS.

THE RULES. `www.comeet.com` and `www.comeet.co` publish the same file: `*` refused the marketing
site's search, categories, tags and `utm` URLs — nothing under `/jobs/` or `/careers-api/`; no
Crawl-delay, 2 s is ours. The guard is taken per host on the exact path.

THE PAGE, THE TOKEN, THE CALL. `/jobs/<slug>/<uid>` (200, 120–810 KB) is an AngularJS page whose
markup holds no position: `COMPANY_DATA = { "company_uid": "D6.000", "token": "6D02…", "slug": … }`,
and the page's script calls `https://www.comeet.co/careers-api/2.0/company/<uid>/positions?
token=<token>` (the token is the tenant's public careers key, printed in every visitor's page —
the 14.09 judgment on StaffPoint and Eezy: a route the page calls, replayed with its own
parameters). The API answers a JSON list (200, 233 KB for 51 positions with `details=true`) —
`uid`, `name`, `department`, `location` (name, city, state, country), `employment_type`,
`experience_level`, `workplace_type`, `time_updated`, `url_active_page` (the employer's own page),
`url_comeet_hosted_page`, `details` (Description, Requirements, Preferred Skills… as HTML), and
`email` / `email_alias` (the position's application address on `applynow.io`), `referrals_reward`,
`linkedin_job_posting_id`. **A tenant with no open position answers `[]` with 200 — the adapter
prints «0 positions — the tenant publishes none today», never an error.** No count is stated
anywhere: the API's list is the board, and `jobs` prints its length as the count.

**WITHHELD:** `email` and `email_alias` (the application address) never emitted; the details are
scrubbed of e-mail addresses and telephone numbers; the referral reward and the LinkedIn posting
id not emitted; `contacts_withheld` on every record; the application (a form on the hosted page)
never touched.

Measured 2026-09-16 22:26–22:28 UTC by the declared client, the guard on the exact path: both
rules files 200 (1 261 B); `/jobs/spark-hire/30.005` 200 → the API `[]` (Spark Hire's own tenant,
no open position); `/jobs/quantummachines/D6.000` 200 (293 973 B) → the API 51 positions in 232 918 B
(IL 16, US 16, DK 6, JP 3, DE 3, NL 3, KR, SG, HU 1, one without a country); `/jobs/comm-it/76.008`
200 (811 176 B).
"""

import argparse
import html as htmlmod
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

PAGE_HOST = "www.comeet.com"
API_HOST = "www.comeet.co"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\d[\d\s().\-]{7,}\d(?!\w)")   # an international shape: 9+ digits with separators — the details are prose, not numbers
TENANT_RE = re.compile(r"^([a-z0-9\-]+)/([0-9A-F]{2}\.[0-9A-F]{3})$")
AD_RE = re.compile(r"^/jobs/([a-z0-9\-]+)/([0-9A-F]{2}\.[0-9A-F]{3})/[^/]+/([0-9A-F]{2}\.[0-9A-F]{3})/?$")
COMPANY_DATA_RE = re.compile(r'"company_uid":\s*"([0-9A-F]{2}\.[0-9A-F]{3})",\s*"token":\s*"([0-9A-F]+)"')
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[sparkhire] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, accept="text/html,application/xhtml+xml"):
    parts = urllib.parse.urlsplit(url)
    if parts.netloc not in (PAGE_HOST, API_HOST):
        die(f"{url}: not a SparkHire host — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(parts.netloc, Pace(parts.netloc, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": accept, "Accept-Language": "en"})
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
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", markup or "")
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span)\b[^>]*>", "", t)   # inline tags leave no space behind
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def tenant_of(arg):
    """`<slug>/<uid>` or the careers URL → (slug, uid)."""
    s = arg.strip()
    if "://" in s or s.startswith(PAGE_HOST):
        parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
        m = re.match(r"^/jobs/([a-z0-9\-]+)/([0-9A-F]{2}\.[0-9A-F]{3})", parts.path)
        if parts.netloc != PAGE_HOST or not m:
            die(f"{arg}: not a SparkHire careers address (https://{PAGE_HOST}/jobs/<slug>/<uid>)")
        return m.group(1), m.group(2)
    m = TENANT_RE.match(s)
    if not m:
        die(f"{arg}: a tenant is written <slug>/<uid> as the careers URL spells it — quantummachines/D6.000")
    return m.group(1), m.group(2)


def company_data(slug, uid):
    """The tenant's page → (company_uid, token) from its COMPANY_DATA."""
    url = f"https://{PAGE_HOST}/jobs/{slug}/{uid}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — no such tenant", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    m = COMPANY_DATA_RE.search(body)
    if not m:
        die(f"{url}: 200 without COMPANY_DATA's company_uid and token — the page changed; not an empty board", EXIT_PARTIAL)
    if m.group(1) != uid:
        die(f"{url}: the page's company_uid {m.group(1)} is not the address's {uid}", EXIT_PARTIAL)
    return m.group(1), m.group(2)


def positions(uid, token):
    url = f"https://{API_HOST}/careers-api/2.0/company/{uid}/positions?token={token}&details=true"
    code, body = request(url, accept="application/json")
    if code != 200:
        die(f"the careers API: HTTP {code}", EXIT_PARTIAL)
    try:
        data = json.loads(body)
    except ValueError:
        die("the careers API: 200 and not JSON — the route changed", EXIT_PARTIAL)
    if not isinstance(data, list):
        die("the careers API: 200 and not a list — the route changed", EXIT_PARTIAL)
    return data


def record(p, slug, uid):
    loc = p.get("location") or {}
    details = {}
    for d in p.get("details") or []:
        if d.get("name") and d.get("value"):
            details[d["name"]] = scrub(text(d["value"]))
    return {
        "source": "sparkhire", "tenant": f"{slug}/{uid}", "country": loc.get("country") or None,
        "ledger_id": f"sparkhire:{uid}:{p.get('uid')}", "id": p.get("uid"),
        "url": p.get("url_comeet_hosted_page") or p.get("url_active_page") or None, "employer_url": p.get("url_active_page") or None,   # the hosted page is per position; the employer's page may be one careers URL for all (CommIT)
        "title": (p.get("name") or "").strip() or None, "company": p.get("company_name") or None, "department": p.get("department") or None,
        "place": loc.get("city") or None, "region": loc.get("state") or None, "location": loc.get("name") or None,
        "employment_type": p.get("employment_type") or None, "experience_level": p.get("experience_level") or None, "workplace_type": p.get("workplace_type") or None,
        "updated": (p.get("time_updated") or "")[:10] or None,
        "details": details or None,
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    slug, uid = tenant_of(a.tenant)
    _uid, token = company_data(slug, uid)
    data = positions(uid, token)
    rows = [record(p, slug, uid) for p in data if isinstance(p, dict)]
    if a.country_code:
        rows = [r for r in rows if (r["country"] or "").upper() == a.country_code.upper()]
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if not data:
        note(f"{slug}/{uid}: 0 positions — the tenant publishes none today (the API answered a list, 200); not an error.")
    elif a.country_code:
        note(f"{th(len(rows))} emitted for {a.country_code.upper()} of the {th(len(data))} positions the API lists for {slug}/{uid} — no count is stated anywhere, the list is the board.")
    else:
        note(f"{th(len(rows))} emitted, the {th(len(data))} positions the API lists for {slug}/{uid} — no count is stated anywhere, the list is the board.")
    note("the application address, the referral reward and the LinkedIn id never emitted; details scrubbed.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc != PAGE_HOST or not m:
        die(f"{a.url}: not a position address (https://{PAGE_HOST}/jobs/<slug>/<uid>/<position>/<position-uid>)")
    slug, uid, pid = m.groups()
    _uid, token = company_data(slug, uid)
    url = f"https://{API_HOST}/careers-api/2.0/company/{uid}/positions/{pid}?token={token}"
    code, body = request(url, accept="application/json")
    if code == 404:
        die(f"{a.url}: the API knows no position {pid} — gone", EXIT_GONE)
    if code != 200:
        die(f"the careers API: HTTP {code}", EXIT_PARTIAL)
    try:
        p = json.loads(body)
    except ValueError:
        die("the careers API: 200 and not JSON — the route changed", EXIT_PARTIAL)
    if not isinstance(p, dict) or not p.get("uid"):
        die(f"{a.url}: the API answered without a position — gone", EXIT_GONE)
    print(json.dumps(record(p, slug, uid), ensure_ascii=False))
    note(f"{a.url}: read from the careers API; the application address never emitted; details scrubbed.")


def main():
    p = argparse.ArgumentParser(description="SparkHire Recruit (ex-Comeet) — one tenant's positions through the careers API its page calls, with the page's own token; the application address never emitted. Issue #452.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="one tenant's whole board (2 requests)")
    j.add_argument("--tenant", required=True, help="<slug>/<uid> as the careers URL spells it, or the URL itself")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="keep one country (the API's location.country)")
    j.set_defaults(fn=cmd_jobs)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
