#!/usr/bin/env python3
"""ADP Workforce Now — an ATS, one tenant at a time: the tenant's «Career Center» on `workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=<guid>` is a 19 KB shell, identical for every tenant, and the app fills its list by `GET …/careercenter/public/events/staffing/v1/job-requisitions?cid=…` — replayed with the page's own parameters, paged 20 at a time to the stated `totalNumber`; the requisition's description by `…/job-requisitions/<id>`. Issue #462.

  adpworkforcenow.py jobs --tenant 4f8b9ec0-f968-42cd-9774-88eb269c652e [--cc-id 19000101_000001] [--lang en_US] [--country-code US] [--max-pages N]
  adpworkforcenow.py jobs --tenant "https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=…&ccId=…"
  adpworkforcenow.py ad --url "https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=…&ccId=…&jobId=606158"

WHAT IT IS. ADP Workforce Now is a US HR suite whose recruiting module hosts the employer's «Career
Center» (hundreds of US and Canadian SMEs). **One adapter covers every employer that uses it, in
every country; the user names the tenant** by the `cid` GUID the URL spells, with the career
center id (`ccId`, `19000101_000001` unless the URL says otherwise) and the language (`en_US`).

THE RULES. `workforcenow.adp.com/robots.txt` answers 200 with a page that is not a rules file — an
absence of rules, `certain: False`; no Crawl-delay, 2 s is ours.

THE PAGE, THE CALLS. The shell (200, 19 449 B, the same bytes for every tenant) loads ADP's MDF
app; the calls it makes, read in a connected tab and replayed by the declared client on
2026-09-20 (no token, no cookie needed):

  GET /mascsr/default/careercenter/public/events/staffing/v1/job-requisitions
        ?cid=<guid>&timeStamp=<ms>&ccId=<ccId>&lang=<lang>&locale=<lang>&$top=20&$skip=<1 + 20·page>
      → meta.totalNumber (THE STATED COUNT), meta.startSequence, jobRequisitions[] (itemID,
        requisitionTitle, postDate, clientRequisitionID, workLevelCode, requisitionLocations[{address
        {cityName, countrySubdivisionLevel1, countryCode, postalCode}, nameCode}], customFieldGroup
        with ExternalJobID, JobClass, PostingDate, InternalPostingFlag…)
  GET …/job-requisitions/<ExternalJobID or itemID>?cid=…  → the same fields plus requisitionDescription (HTML)

**`$top` is capped at 20 by the service and `$skip` is 1-based** — `$skip=0` and `$skip=1` both
start at the first item; the page asks `$skip=1, 21, 41…` and so does the adapter (measured on an
85-requisition tenant: five pages, 85 distinct). The Career Center's own ad page is
`recruitment.html?cid=…&ccId=…&jobId=<ExternalJobID>` — the page then fetches
`job-requisitions/<ExternalJobID>`.

Measured 2026-09-20 12:3x UTC: tenant `4f8b9ec0-…` (a Kauai employer) totalNumber 11, 11 emitted;
tenant `89da4960-…` totalNumber 85, five pages, 85 emitted; the requisition's description read.

**WITHHELD:** postal codes not emitted (city, region, country are); descriptions scrubbed of e-mail
addresses and telephone numbers; internal-only postings (`InternalPostingFlag`) skipped; the
`screeningRequirements`, `sponsoredVisaTypeCodes` and tracking fields not emitted;
`contacts_withheld` on every record; the application (an ADP account) never touched.
"""

import argparse
import html as htmlmod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "workforcenow.adp.com"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE_SIZE = 20   # the service's cap on $top

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$])\+?\d[\d\s().\-]{7,}\d(?!\w)")   # an international shape: 9+ digits with separators
GUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
CCID_RE = re.compile(r"^[0-9]{8}_[0-9]{6}$")
LANG_RE = re.compile(r"^[a-z]{2}_[A-Z]{2}$")
PAGE_PATH = "/mascsr/default/mdf/recruitment/recruitment.html"
API_PATH = "/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions"
_PACE = Pace(HOST, own=2.0)   # no rules file read; 2 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[adpworkforcenow] {msg}", file=sys.stderr)


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
    if parts.netloc != HOST:
        die(f"{url}: not an ADP Workforce Now host — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "application/json", "Accept-Language": "en"})
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


def tenant_of(arg, cc_id, lang):
    """`<cid guid>` (+ --cc-id, --lang) or the Career Center URL → (cid, ccId, lang)."""
    s = arg.strip()
    if "://" in s or s.startswith(HOST):
        parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
        q = urllib.parse.parse_qs(parts.query)
        cid = (q.get("cid") or [""])[0]
        if parts.netloc != HOST or parts.path.lower() != PAGE_PATH.lower() or not GUID_RE.match(cid):
            die(f"{arg}: not an ADP Workforce Now career-center address (https://{HOST}{PAGE_PATH}?cid=<guid>)")
        cc_id = (q.get("ccId") or [cc_id])[0]
        lang = (q.get("lang") or [lang])[0]
    else:
        cid = s
    if not GUID_RE.match(cid):
        die(f"{arg}: a tenant is written as the cid GUID the career-center URL spells")
    if not CCID_RE.match(cc_id) or not LANG_RE.match(lang):
        die(f"{arg}: ccId must look like 19000101_000001 and lang like en_US (got {cc_id!r}, {lang!r})")
    return cid.lower(), cc_id, lang


def page_url(cid, cc_id, lang, job_id=None):
    tail = f"&jobId={job_id}" if job_id else ""
    return f"https://{HOST}{PAGE_PATH}?cid={cid}&ccId={cc_id}&lang={lang}{tail}"


def api(cid, cc_id, lang, extra="", item=None):
    q = f"cid={cid}&timeStamp={int(time.time() * 1000)}&ccId={cc_id}&lang={lang}&locale={lang}{extra}"
    url = f"https://{HOST}{API_PATH}{'/' + str(item) if item else ''}?{q}"
    code, body = request(url)
    what = f"job-requisitions/{item}" if item else "job-requisitions"
    if code == 404:
        die(f"{what}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{what}: HTTP {code}", EXIT_PARTIAL)
    try:
        return json.loads(body)
    except ValueError:
        die(f"{what}: 200 and not JSON — the route changed", EXIT_PARTIAL)


def fields(r):
    g = r.get("customFieldGroup") or {}
    out = {}
    for f in g.get("stringFields") or []:
        out[(f.get("nameCode") or {}).get("codeValue")] = f.get("stringValue")
    for f in g.get("indicatorFields") or []:
        out[(f.get("nameCode") or {}).get("codeValue")] = f.get("indicatorValue")
    for f in g.get("dateFields") or []:
        out[(f.get("nameCode") or {}).get("codeValue")] = f.get("dateValue")
    return out


def record(r, cid, cc_id, lang):
    f = fields(r)
    locs = [l for l in (r.get("requisitionLocations") or []) if isinstance(l, dict)]
    first = locs[0] if locs else {}
    addr = first.get("address") or {}
    ext = f.get("ExternalJobID") or None
    name = ((first.get("nameCode") or {}).get("shortName") or "").strip()
    tail = name.rsplit(",", 1)[-1].strip().upper() if "," in name else ""
    country = addr.get("countryCode") or (tail if re.match(r"^[A-Z]{2}$", tail) else None)   # the address carries no countryCode; the location's name ends with it («Kalaheo, HI, US»)
    return {
        "source": "adpworkforcenow", "tenant": cid, "country": country,
        "ledger_id": f"adpworkforcenow:{cid}:{r.get('itemID')}", "id": r.get("itemID"), "ref": r.get("clientRequisitionID"), "external_id": ext,
        "url": page_url(cid, cc_id, lang, ext or r.get("itemID")),
        "title": (r.get("requisitionTitle") or "").strip() or None,
        "place": addr.get("cityName") or None, "region": ((addr.get("countrySubdivisionLevel1") or {}).get("codeValue") or None),
        "location": ((first.get("nameCode") or {}).get("shortName") or "").strip() or None,
        "work_level": ((r.get("workLevelCode") or {}).get("shortName") or None), "job_class": f.get("JobClass") or None,
        "posted": (r.get("postDate") or "")[:10] or None,
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    cid, cc_id, lang = tenant_of(a.tenant, a.cc_id, a.lang)
    rows, seen, stated, page = [], set(), None, 0
    while True:
        d = api(cid, cc_id, lang, extra=f"&$top={PAGE_SIZE}&$skip={1 + page * PAGE_SIZE}")
        got = d.get("jobRequisitions") if isinstance(d, dict) else None
        if not isinstance(got, list):
            die("job-requisitions: 200 without a jobRequisitions list — the route changed", EXIT_PARTIAL)
        meta = d.get("meta") or {}
        if stated is None:
            stated = meta.get("totalNumber") if isinstance(meta.get("totalNumber"), int) else None
        fresh = [r for r in got if isinstance(r, dict) and r.get("itemID") not in seen]
        if page > 0 and got and not fresh:
            die(f"page {page + 1} repeats an earlier page — the pager does not page; stopping", EXIT_PARTIAL)
        for r in fresh:
            seen.add(r.get("itemID"))
            if fields(r).get("InternalPostingFlag") is True:
                continue
            rows.append(record(r, cid, cc_id, lang))
        if not got or len(got) < PAGE_SIZE or (isinstance(stated, int) and len(seen) >= stated):
            break
        if a.max_pages and page + 1 >= a.max_pages:
            note(f"stopped at page {page + 1} by request")
            break
        if isinstance(stated, int) and (page + 1) >= -(-stated // PAGE_SIZE):
            break   # the stated count's last page
        page += 1
    if a.country_code:
        rows = [r for r in rows if (r["country"] or "").upper() == a.country_code.upper()]
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    where = f" for {a.country_code.upper()}" if a.country_code else ""
    if isinstance(stated, int):
        if stated == 0:
            note(f"{cid}: 0 requisitions — the service states totalNumber 0 (200); the tenant publishes none today, not an error.")
        elif a.country_code:
            note(f"{th(len(rows))} emitted{where} of the {th(len(seen))} walked — the service states {th(stated)}.")
        elif len(rows) == stated:
            note(f"{th(len(rows))} emitted — the service states {th(stated)}: equal.")
        elif a.max_pages and len(seen) < stated:
            note(f"{th(len(rows))} emitted of the {th(stated)} the service states — walked {page + 1} page(s) by request, not a shortfall.")
        else:
            note(f"{th(len(rows))} emitted — the service states {th(stated)}: {th(abs(stated - len(rows)))} {'short' if len(rows) < stated else 'over'} (internal postings are skipped).")
    else:
        note(f"{th(len(rows))} emitted{where} — the service stated no totalNumber (the route changed?); the count is ours.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url.strip())
    q = urllib.parse.parse_qs(parts.query)
    cid = (q.get("cid") or [""])[0].lower()
    job = (q.get("jobId") or [""])[0]
    if parts.netloc != HOST or parts.path.lower() != PAGE_PATH.lower() or not GUID_RE.match(cid) or not re.match(r"^[0-9]+(?:_[0-9]+)?$", job):
        die(f"{a.url}: not an ADP Workforce Now requisition address (…recruitment.html?cid=<guid>&ccId=…&jobId=<id>)")
    cc_id = (q.get("ccId") or ["19000101_000001"])[0]
    lang = (q.get("lang") or ["en_US"])[0]
    if not CCID_RE.match(cc_id) or not LANG_RE.match(lang):
        die(f"{a.url}: ccId must look like 19000101_000001 and lang like en_US")
    d = api(cid, cc_id, lang, item=job)
    r = d.get("jobRequisition") if isinstance(d, dict) and isinstance(d.get("jobRequisition"), dict) else d
    if not isinstance(r, dict) or not r.get("requisitionTitle"):
        die(f"job-requisitions/{job}: 200 without requisitionTitle — the route changed", EXIT_PARTIAL)
    out = record(r, cid, cc_id, lang)
    out["url"] = page_url(cid, cc_id, lang, job)
    out["description"] = scrub(text(r.get("requisitionDescription")))
    print(json.dumps(out, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(description="ADP Workforce Now — one tenant's requisitions, the calls its Career Center makes")
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the tenant's requisitions")
    j.add_argument("--tenant", required=True, help="the cid GUID or the Career Center URL")
    j.add_argument("--cc-id", default="19000101_000001", help="the career center id (default 19000101_000001)")
    j.add_argument("--lang", default="en_US", help="the language (default en_US)")
    j.add_argument("--country-code", help="ISO2 — filters on the first location's countryCode")
    j.add_argument("--max-pages", type=int, default=0, help="stop after N pages of 20 (0 = all)")
    j.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one requisition")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
