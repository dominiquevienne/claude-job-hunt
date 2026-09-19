#!/usr/bin/env python3
"""Paylocity — an ATS, one tenant at a time: the tenant's careers page on `recruiting.paylocity.com/recruiting/jobs/All/<guid>` carries every open job in its own `window.pageData.Jobs` — no API, no token, no page; the job page is server-rendered with its description. Issue #460.

  paylocity.py jobs --tenant 67c76e24-da8b-4733-a8b3-9c1fe859c5b9 [--country-code US]     the tenant's jobs (1 request)
  paylocity.py jobs --tenant https://recruiting.paylocity.com/recruiting/jobs/All/67c76e24-da8b-4733-a8b3-9c1fe859c5b9/Peak-Support-LLC
  paylocity.py ad --url https://recruiting.paylocity.com/Recruiting/Jobs/Details/4517495

WHAT IT IS. Paylocity is a US payroll and HR suite whose recruiting module hosts the employer's
«Job Opportunities» page (Peak Support, Louisiana Machinery's NAPA stores, hundreds of US
SMEs). **One adapter covers every employer that uses it, in every country; the user names the
tenant** by the module's GUID the URL spells (`…/jobs/All/<guid>/<slug>` → the GUID; the slug is
decorative), or pastes the page URL. The host is `recruiting.paylocity.com`; a numbered twin
(`2000recruiting.paylocity.com`) serves the same pages for older modules and is admitted too.

THE RULES. `recruiting.paylocity.com/robots.txt` answers 404 — an absence of rules, certain; no
Crawl-delay, 2 s is ours.

THE PAGE. `/recruiting/jobs/All/<guid>` (200; 36 582 B for Peak Support, 67 242 B for Louisiana
Machinery's «ALL JOB POSTINGS» — identical on two reads) is an ASP.NET page whose inline
`window.pageData = {…}` carries the whole module: `ModuleTitle` (the employer), `ModuleId`,
`Departments`, `Locations`, and `Jobs[]` — every open job with `JobId`, `JobTitle`,
`LocationName`, `PublishedDate`, `Description` (a ~100-character summary), `IsInternal`,
`HiringDepartment`, `IsRemote`, `JobLocation{Name, Address, City, State, Zip, Country, County}` — `Country` in three letters («PHL», «USA»), emitted as ISO2 by `_iso3.alpha2` with the original beside it.
No count is stated and nothing pages: the list is the board (Peak Support 17, Louisiana
Machinery 62 on 2026-09-19 22:1x UTC). The job page `/Recruiting/Jobs/Details/<JobId>` (200,
26 432 B ×2) is server-rendered: `pageData = {jobTitle, moduleName}`, a `job-preview-header`
(location line: «Fully Remote • Remote - Philippines, PHL») and a `job-preview-details` block
with the description as HTML under «Description»; no JobPosting.

**WITHHELD:** the location's street (`Address`, `Address2`, `Zip`, `SmartyAddressId`) never
emitted (city, state, country and the location's name are); descriptions scrubbed of e-mail
addresses and telephone numbers; `TrackingPixels`, logos and the lead-join form not emitted;
`contacts_withheld` on every record; the application (`/Recruiting/Jobs/Apply/<id>`) never
touched.
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
from _iso3 import alpha2
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST_RE = re.compile(r"^(?:\d+)?recruiting\.paylocity\.com$")
HOST = "recruiting.paylocity.com"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$])\+?\d[\d\s().\-]{7,}\d(?!\w)")   # an international shape: 9+ digits with separators
GUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
LIST_RE = re.compile(r"^/[Rr]ecruiting/[Jj]obs/[Aa]ll/([0-9a-fA-F-]{36})(?:/[^/]*)?/?$")
AD_RE = re.compile(r"^/[Rr]ecruiting/[Jj]obs/[Dd]etails/(\d+)/?$")
PAGEDATA_RE = re.compile(r"window\.pageData\s*=\s*(\{.*?\});\s*</script>", re.S)
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[paylocity] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    parts = urllib.parse.urlsplit(url)
    if not HOST_RE.match(parts.netloc):
        die(f"{url}: not a Paylocity recruiting host — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(parts.netloc, Pace(parts.netloc, own=2.0)).wait()   # no rules file (404); 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en"})
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
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span|font)\b[^>]*>", "", t)   # inline tags leave no space behind
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def tenant_of(arg):
    """`<guid>` or the page URL → (host, guid)."""
    s = arg.strip()
    if "://" in s or "paylocity.com" in s:
        parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
        m = LIST_RE.match(parts.path)
        if not HOST_RE.match(parts.netloc) or not m or not GUID_RE.match(m.group(1)):
            die(f"{arg}: not a Paylocity careers address (https://{HOST}/recruiting/jobs/All/<guid>)")
        return parts.netloc, m.group(1).lower()
    if not GUID_RE.match(s):
        die(f"{arg}: a tenant is written as the module GUID the careers URL spells — 67c76e24-da8b-4733-a8b3-9c1fe859c5b9")
    return HOST, s.lower()


def page_data(body, url):
    m = PAGEDATA_RE.search(body)
    if not m:
        die(f"{url}: 200 without window.pageData — the page changed; not an empty board", EXIT_PARTIAL)
    try:
        return json.loads(m.group(1))
    except ValueError:
        die(f"{url}: window.pageData is not JSON — the page changed", EXIT_PARTIAL)


def record(j, host, guid, company):
    loc = j.get("JobLocation") if isinstance(j.get("JobLocation"), dict) else {}
    jid = j.get("JobId")
    return {
        "source": "paylocity", "tenant": guid, "country": alpha2(loc.get("Country")) if loc.get("Country") else None, "country_alpha3": loc.get("Country") or None,
        "ledger_id": f"paylocity:{guid}:{jid}", "id": jid,
        "url": f"https://{host}/Recruiting/Jobs/Details/{jid}",
        "title": (j.get("JobTitle") or "").strip() or None, "company": company,
        "place": loc.get("City") or None, "region": loc.get("State") or None, "location": j.get("LocationName") or loc.get("Name") or None,
        "remote": bool(j.get("IsRemote")) or None, "department": j.get("HiringDepartment") or None,
        "posted": (j.get("PublishedDate") or "")[:10] or None,
        "summary": scrub(text(j.get("Description"))),
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    host, guid = tenant_of(a.tenant)
    url = f"https://{host}/recruiting/jobs/All/{guid}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — no such module", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    d = page_data(body, url)
    jobs = d.get("Jobs")
    if not isinstance(jobs, list):
        die(f"{url}: pageData without a Jobs list — the page changed; not an empty board", EXIT_PARTIAL)
    company = (d.get("ModuleTitle") or "").strip() or None
    rows, seen = [], set()
    for j in jobs:
        if isinstance(j, dict) and j.get("JobId") not in seen and not j.get("IsInternal"):
            seen.add(j.get("JobId"))
            rows.append(record(j, host, guid, company))
    if a.country_code:
        rows = [r for r in rows if (r["country"] or "").upper() == a.country_code.upper()]
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if not jobs:
        note(f"{company or guid}: 0 jobs — pageData.Jobs is empty (200); the module publishes none today, not an error.")
    else:
        note(f"{th(len(rows))} emitted{' for ' + a.country_code.upper() if a.country_code else ''} of the {th(len(seen))} jobs pageData carries for {company or guid} — no count is stated anywhere and nothing pages, the list is the board.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url.strip())
    m = AD_RE.match(parts.path)
    if not HOST_RE.match(parts.netloc) or not m:
        die(f"{a.url}: not a Paylocity job address (https://{HOST}/Recruiting/Jobs/Details/<id>)")
    jid = int(m.group(1))
    url = f"https://{parts.netloc}/Recruiting/Jobs/Details/{jid}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — no such job", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    d = page_data(body, url)
    title = (d.get("jobTitle") or "").strip()
    if not title:
        die(f"{url}: pageData without a jobTitle — the page changed", EXIT_PARTIAL)
    det = re.search(r'class="job-preview-details"[^>]*>(.*?)(?:<div class="job-preview-footer|</main>|</body>)', body, re.S)
    desc = None
    if det:
        block = re.sub(r'<div class="mobile-apply-btn">.*?</div>\s*', "", det.group(1), flags=re.S)
        block = re.sub(r'<div class="job-listing-header">\s*Description\s*</div>', "", block, count=1)
        desc = scrub(text(block))
    hdr = re.search(r'class="job-preview-header"[^>]*>(.*?)<div class="job-preview-details"', body, re.S)
    line = text(hdr.group(1)) if hdr else None
    out = {
        "source": "paylocity", "ledger_id": f"paylocity:{jid}", "id": jid, "url": url,
        "title": title, "company": (d.get("moduleName") or "").strip() or None,
        "location": (line.splitlines()[-1] if line else None),
        "description": desc,
        "contacts_withheld": True,
    }
    print(json.dumps(out, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Paylocity — one tenant's jobs, from its careers page's pageData")
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the tenant's jobs")
    j.add_argument("--tenant", required=True, help="the module GUID or the careers page URL")
    j.add_argument("--country-code", help="ISO2 — filters on JobLocation.Country (three letters on the board, converted)")
    j.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one job")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
