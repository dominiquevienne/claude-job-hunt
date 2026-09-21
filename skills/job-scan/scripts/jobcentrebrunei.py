#!/usr/bin/env python3
"""JobCentre Brunei (Pusat Pekerjaan Brunei) — Brunei's public employment service: `/search-job` is a Liferay page whose search portlet renders every vacancy server-side, states its own count («Showing 1 to 75 of 607 entries») and pages by the portlet's `cur` / `delta` parameters — read from the page, never composed; each vacancy at `/web/guest/view-job/-/jobs/<id>/<slug>` carries the employer's overview. The advert's AGE RANGE is never emitted. Issue #690.

  jobcentrebrunei.py jobs [--max-pages N] [--country-code BN]     the whole board (ceil(N/75) requests)
  jobcentrebrunei.py ad --url https://www.jobcentrebrunei.gov.bn/web/guest/view-job/-/jobs/211200374/shop-assistant

WHAT IT IS. The job portal of Brunei's public employment service — vacancies filed by employers
registered with the ROCBN, the country's official route to work. **Brunei's only other named board
is a private generalist (#691);** this one is the service itself.

THE RULES. `www.jobcentrebrunei.gov.bn/robots.txt` read and open on `/search-job` and on
`/web/guest/view-job/…`, no Crawl-delay; 2 s is ours. The guard is taken on the exact path.

THE LIST. `/search-job` (200; 437 124 B for 12 cards, 1 166 291 B for 75) is Liferay: the search
portlet's id carries an instance token (`com_liferay_portal_search_web_search_results_portlet_
SearchResultsPortlet_INSTANCE_<8 chars>`) that the page prints in its own pager links — **the
adapter reads it there**, because an instance token is the page's, not a shape to compose. The
pager's three parameters are `_<portlet>_cur` (1-based page), `_<portlet>_delta` (12 by default,
**75 is the site's own maximum**, offered in its «entries per page» control) and
`_<portlet>_resetCur=false`. **The page states its count** — «Showing 76 to 150 of 607 entries» —
and the walk stops there. Each card: the title, the employer, `jp_job_salary` («$ 500 - 600
Monthly», Brunei dollars), `jp_vacancy` («VACANCY: 4» — posts per advert), `jp_time` (Full time),
`jp_job_location` (district, mukim, kampong), `jp_closing-date`, and the link to the advert.

THE ADVERT. `/web/guest/view-job/-/jobs/<id>/<slug>` (200, ~200 KB) renders a `job-viewer` block:
the description and its bullet list, then a «Job Overview» of labelled rows — Date Posted, Hours,
Industry Type, Position, Salary, Experience, District, Mukim, Allowances Range, Driving License,
**Age**, Last date to apply — plus the employer's profile link and an «Active» ribbon. No
JobPosting, no JSON.

**WITHHELD: the advert's `Age` row** («Age 20-28»). Brunei's portal publishes an age range on
some vacancies; the plugin serves the advert and **does not propagate the criterion** (the
2026-09-04 decision, #183: a law that forbids what a board publishes does not stop us serving the
ad — it stops us carrying the criterion). Also withheld: e-mail addresses and telephone numbers
in the texts (the portal prints its own hotline on every page), the employer's logo, the
jobseeker area (a login, never touched). `contacts_withheld` on every record.

`--country-code` filters on the STAMP: the board is Brunei's and states no country, so the code
is written on every record and the run says it is the user's.

Measured 2026-09-21 13:14–13:15 UTC by the declared client, the guard on the exact path, two
reads of the list and of one advert: `/search-job` 200 ×2 (437 124 B, md5 98acba9488c0 /
4b098963c4cf — a portlet id moves), **«Showing 1 to 12 of 607 entries»** (579 on 2026-09-18 —
the count moves with the board), 12 cards; `cur=2&delta=75` 200 (1 166 291 B), «Showing 76 to 150
of 607 entries», 75 cards; the advert `211200374` 200 ×2 (200 814 B), its overview read and its
`Age 20-28` left out.
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

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "www.jobcentrebrunei.gov.bn"
PAGE_SIZE = 75            # the site's own maximum, from its «entries per page» control
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")   # «+673-8239933», the portal's own hotline on every page
DATE_RE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")                        # «07/10/2026» is a closing date, not a telephone
PORTLET_RE = re.compile(r"(com_liferay_portal_search_web_search_results_portlet_SearchResultsPortlet_INSTANCE_[A-Za-z0-9]+)")
STATED_RE = re.compile(r"Showing\s+[\d,]+\s+to\s+[\d,]+\s+of\s+([\d,]+)\s+entries", re.I)
CARD_RE = re.compile(r'<li class="list-group-item list-group-item-flex[^"]*"(.*?)</li>\s*(?=<li class="list-group-item|</ul>|</div>)', re.S)
AD_HREF_RE = re.compile(r'href="(/web/guest/view-job/-/jobs/(\d+)/[^"?]*)"')
CELL_FIELDS = ("job_salary", "job_location", "closing-date", "time", "vacancy")   # the card's cells, each named by its own class
TITLE_RE = re.compile(r"<h4 class=\"line-clamp\">\s*<a[^>]*>(.*?)</a>", re.S)
EMPLOYER_RE = re.compile(r"<p class=\"line-clamp\">\s*<a[^>]*>(.*?)</a>", re.S)
AD_PATH_RE = re.compile(r"^/web/guest/view-job/-/jobs/(\d+)/([^/]*)$")
ROW_RE = re.compile(r'<div class="jp_listing_list_icon_cont_wrapper">\s*<ul>\s*<li>(.*?)</li>\s*<li>(.*?)</li>', re.S)
VIEWER_RE = re.compile(r'<div class="job-viewer[^"]*"[^>]*>(.*?)(?=<div class="jp_footer_main_wrapper|</body>)', re.S)
WITHHELD_ROWS = ("age",)   # #183: the advert is served, the criterion is not carried
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobcentrebrunei] {msg}", file=sys.stderr)


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
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en, ms"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
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


def when(s):
    """`07/10/2026` → ISO; `21 September 2026` → ISO; anything else as read."""
    s = (s or "").strip()
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$", s)
    if m:
        months = {n.lower(): i for i, n in enumerate(
            ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"], 1)}
        mo = months.get(m.group(2).lower())
        if mo:
            return f"{m.group(3)}-{mo:02d}-{int(m.group(1)):02d}"
    return s or None


def portlet_of(markup):
    m = PORTLET_RE.search(markup or "")
    return m.group(1) if m else None


def stated_of(markup):
    m = STATED_RE.search(text(markup) or "")
    return int(re.sub(r"\D", "", m.group(1))) if m else None


def cards_of(markup):
    """The list's `li.list-group-item` cards → [(id, fields)] — the cells named by their class."""
    out = []
    for body in CARD_RE.findall(markup or ""):
        h = AD_HREF_RE.search(body)
        if not h:
            continue
        f = {"url": f"https://{HOST}{h.group(1)}"}
        t = TITLE_RE.search(body)
        e = EMPLOYER_RE.search(body)
        f["title"] = text(t.group(1)) if t else None
        f["employer"] = text(e.group(1)) if e else None
        for cls in CELL_FIELDS:
            # one regex per class: a single scanning regex lets the wrapper div
            # (`jp_job_post_right_cont`) swallow the cells nested inside it
            m = re.search(r'class="jp_' + re.escape(cls) + r'(?:\s+[^"]*)?"[^>]*>(.*?)</(?:li|div)>', body, re.S)
            f[cls] = text(m.group(1)) if m else None
        out.append((h.group(2), f))
    return out


def record(pid, f, stamp):
    vac = (f.get("vacancy") or "")
    n = re.sub(r"\D", "", vac)
    return {
        "source": "jobcentrebrunei", "country": stamp,
        "ledger_id": f"jobcentrebrunei:{pid}", "id": pid, "url": f.get("url"),
        "title": f.get("title"), "employer": f.get("employer"),
        "place": f.get("job_location"), "salary": f.get("job_salary"),
        "schedule": f.get("time"), "posts": int(n) if n else None,
        "closes": when((f.get("closing-date") or "").replace("CLOSING DATE:", "").strip()),
        "contacts_withheld": True,
    }


def list_url(portlet, page):
    q = {"p_p_id": portlet, "p_p_lifecycle": "0", "p_p_state": "normal", "p_p_mode": "view",
         f"_{portlet}_cur": str(page), f"_{portlet}_delta": str(PAGE_SIZE), f"_{portlet}_resetCur": "false"}
    return f"https://{HOST}/web/guest/search-job?" + urllib.parse.urlencode(q)


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    url = f"https://{HOST}/search-job"
    code, body = request(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    portlet = portlet_of(body)
    stated = stated_of(body)
    if not portlet:
        die(f"{url}: 200 without the search portlet's id — the page changed; not an empty board", EXIT_PARTIAL)
    if stated is None:
        die(f"{url}: 200 without «Showing … of N entries» — the page states no count; not an empty board", EXIT_PARTIAL)
    rows, seen, page = [], set(), 0
    pages_total = max(1, math.ceil(stated / PAGE_SIZE))
    while True:
        page += 1
        code, body = request(list_url(portlet, page))
        if code != 200:
            die(f"page {page}: HTTP {code}", EXIT_PARTIAL)
        found = cards_of(body)
        ids = {pid for pid, _f in found}
        if page > 1 and ids and ids <= seen:
            die(f"page {page} repeats the previous page's ids — the walk ended at {th(len(rows))} of {th(stated)} stated", EXIT_PARTIAL)
        for pid, f in found:
            if pid in seen:
                continue
            seen.add(pid)
            rows.append(record(pid, f, stamp))
        if page >= pages_total or not found or (a.max_pages and page >= a.max_pages):
            break
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if stated == 0:
        note("0 vacancies — the portal states 0 today; not an error.")
    else:
        note(f"{th(len(rows))} emitted, the portal states {th(stated)}" + (f" — {th(stated - len(rows))} short (the walk stopped at page {page} of {pages_total})" if len(rows) < stated else "") + ".")
    if stamp:
        note(f"country {stamp} is the user's stamp — the board is Brunei's and states no country.")
    note("the advert's age range never emitted (#183: the ad is served, the criterion is not carried); contacts scrubbed.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_PATH_RE.match(parts.path)
    if parts.scheme != "https" or parts.netloc != HOST or not m:
        die(f"{a.url}: not a JobCentre Brunei advert (https://{HOST}/web/guest/view-job/-/jobs/<id>/<slug>)")
    pid = m.group(1)
    url = f"https://{HOST}{parts.path}"                     # any query dropped
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    v = VIEWER_RE.search(body)
    if not v:
        die(f"{url}: 200 without the `job-viewer` block — gone, or the page changed", EXIT_PARTIAL)
    seg = v.group(1)
    overview, withheld = {}, []
    for label, value in ROW_RE.findall(seg):
        k = (text(label) or "").strip().lower().replace(" ", "_")
        val = text(value)
        if not k or not val:
            continue
        if k in WITHHELD_ROWS:
            withheld.append(k)
            continue
        overview[k] = scrub(val)
    whole = text(seg) or ""
    i = whole.find("Job Overview")
    desc = whole[:i] if i > 0 else whole
    desc = re.sub(r"^\s*Job Description\s*\n", "", desc)          # the block's own heading is not the advert
    desc = re.sub(r"\n\s*Share\s*(?:\n\s*-->)?\s*$", "", desc)      # nor its share widget
    desc = scrub(desc)
    row = {
        "source": "jobcentrebrunei", "country": a.country_code.upper() if a.country_code else None,
        "ledger_id": f"jobcentrebrunei:{pid}", "id": pid, "url": url,
        "title": scrub(text((re.search(r"<title>(.*?)</title>", body, re.S) or [None, ""])[1]) if re.search(r"<title>", body) else None),
        "employer": overview.get("employer") or scrub(text((re.search(r'<h5 class="font-weight-bold[^"]*">(.*?)</h5>', seg, re.S) or [None, ""])[1]) if re.search(r'<h5 class="font-weight-bold', seg) else None),
        "place": " · ".join(x for x in (overview.get("district"), overview.get("mukim"), overview.get("kampong")) if x) or None,
        "position": overview.get("position"), "industry": overview.get("industry_type"),
        "salary": overview.get("salary"), "allowances": overview.get("allowances_range"),
        "schedule": overview.get("hours"), "experience": overview.get("experience"),
        "driving_license": overview.get("driving_license_class") or overview.get("driving_license"),
        "posted": when(overview.get("date_posted")), "closes": when(overview.get("last_date_to_apply")),
        "description": desc,
        "withheld_rows": withheld or None,
        "contacts_withheld": True,
    }
    print(json.dumps(row, ensure_ascii=False))
    note(f"{url}: read from the page's job-viewer; " + (f"the advert's {', '.join(withheld)} row(s) never emitted (#183); " if withheld else "no age row on this advert; ") + "contacts scrubbed.")


def main(argv=None):
    p = argparse.ArgumentParser(description="JobCentre Brunei — the public employment service's vacancies, walked by the page's own Liferay pager against its stated count; the advert's age range never emitted. Issue #690.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the whole board (the portlet id and the count read from the page)")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the board states none)")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0, help=f"stop after N pages of {PAGE_SIZE} (0 = to the stated count)")
    j.set_defaults(fn=cmd_jobs)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on the record")
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
