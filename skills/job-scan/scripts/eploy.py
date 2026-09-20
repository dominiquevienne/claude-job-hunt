#!/usr/bin/env python3
"""Eploy (a UK ATS, one tenant at a time): the tenant's careers site on its own domain serves `/vacancies/vacancy-search-results.aspx?view=list` server-rendered, 12 a page, the count in the page's title, and pages beyond the first by the WebForms postback the pager's links spell out — replayed with the page's own hidden fields and cookies; the vacancy page carries a JobPosting. Issue #464.

  eploy.py jobs --tenant <host> [--country-code ISO2] [--max-pages N]
  eploy.py ad --url https://<host>/vacancies/<id>/<slug>.html

THE TENANT IS A HOST — the employer's own domain (`jobs.le.ac.uk`,
`jobs.manchester.gov.uk`, `careers.nhsprofessionals.nhs.uk`), found by the
family's signature (`/vacancies/vacancy-search-results.aspx`, `$Eploy(`,
`aspnetForm`), never composed. One run reads one host and refuses every
other before the gate (exit 7). The rules read on 2026-09-20 (three
tenants): no Disallow on `/vacancies/`, no Crawl-delay; 2 s between
requests is ours, and a Crawl-delay written by a tenant is honoured by
`Pace`.

THE LIST is server-rendered: `<div id="…VacancyListView_ctlNN_pnlList"
class="vsr-job">` cards, each with `<h2 class="vsr-job__title"><a
href="<id>/<slug>.html">`, its fields as `div_<Field>_<id>` items (a label
and a content — the tenant chooses which fields: Location, Salary, Hours,
End date, Vacancy type…), and a `More Info` link to the same page. **The
count is stated in the page's title (`<title>17 Vacancies - University of
Leicester</title>`) and in its `hero__title`;** a tenant with none says
«0 Vacancies» and «Your search returned no results». Page 2 and on are a
POSTBACK: the pager writes `__doPostBack('ctl00$ContentContainer$ctlNN$
VacancyPager','2')`, and the form must carry every hidden field of the
page it came from (`__VIEWSTATE`, `__VIEWSTATEGENERATOR`,
`__EVENTVALIDATION`, …), the selects' selected values, and the session's
cookies — without them the server answers page 1 again (measured
2026-09-20). The current page is `<span class="cpb">N</span>`; a postback
that answers the page it was sent from dies with 6.

THE VACANCY PAGE `/vacancies/<id>/<slug>.html` carries a schema.org
JobPosting (`_ldjson.postings`): title, datePosted, validThrough,
employmentType, skills, industry, hiringOrganization, jobLocation
(streetAddress and postalCode — NOT emitted), baseSalary, description.

WITHHELD: the street and the postal code of a workplace (the list's «All
Locations» is trimmed of them; the JobPosting's are not read out);
descriptions scrubbed of e-mail addresses and telephone numbers (the
Leicester posting names a contact address); the application
(`vacancy-apply.aspx`, an account) never touched; `contacts_withheld` on
every record. **The list states no country: `--country-code` STAMPS the
rows with the country the user names for that tenant, and says so.**
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
from _ldjson import postings as ld_postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD = "eploy"
LIST_PATH = "/vacancies/vacancy-search-results.aspx?view=list"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE_SIZE = 12                        # the list's own page, measured on three tenants

HOST_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$", re.I)
AD_PATH_RE = re.compile(r"^/vacancies/(\d+)/([^/]+)\.html$")
CARD_RE = re.compile(r'<div id="[^"]*VacancyListView_ctl\d+_pnlList" class="vsr-job[^"]*">')
TITLE_RE = re.compile(r'<h2 class="vsr-job__title">\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S)
ITEM_RE = re.compile(r'<div id="div_([A-Za-z0-9_]+?)_\d+" class="item vsr-job__list-item[^"]*"[^>]*>(.*?)(?=<div id="div_[A-Za-z0-9_]+_\d+" class="item|\Z)', re.S)
LABEL_RE = re.compile(r"<div class=\"label\"><span>(?:<i[^>]*data-tooltip='([^']*)'[^>]*>|([^<]+))")
CONTENT_RE = re.compile(r'<div data-id="div_content_[^"]+" class="content">(.*?)</div>\s*</div>', re.S)
READONLY_RE = re.compile(r'id="[^"]*lblReadonlySelected"[^>]*>(.*?)</span>', re.S)
COUNT_RE = re.compile(r"<title>\s*([\d,]+)\s+Vacanc", re.I)
HERO_RE = re.compile(r'class="hero__title">\s*([\d,]+)\s+Vacanc', re.I)
NO_RESULTS_RE = re.compile(r"Your search returned no results", re.I)
SIGNATURE_RE = re.compile(r"\$Eploy\(|id=\"aspnetForm\"")
INPUT_RE = re.compile(r"<input\b[^>]*>", re.S)
ATTR_RE = re.compile(r'\b(type|name|value)="([^"]*)"')
SELECT_RE = re.compile(r'<select[^>]*name="([^"]+)"[^>]*>(.*?)</select>', re.S)
SELECTED_RE = re.compile(r'<option[^>]*selected="selected"[^>]*value="([^"]*)"|<option[^>]*value="([^"]*)"[^>]*selected="selected"')
POSTBACK_RE = re.compile(r"__doPostBack\('([^']*VacancyPager)','(\d+)'\)")
CPB_RE = re.compile(r'class="cpb"[^>]*>\s*(\d+)\s*<')
UK_POSTCODE_RE = re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b", re.I)
STREET_WORD = r"(?:road|rd|street|st|lane|ln|avenue|ave|way|drive|dr|close|place|square|crescent|terrace|gardens|walk|row|court|hwy|highway)"
STREET_RE = re.compile(r"^\d+[\w\-/ ]*$|\b" + STREET_WORD + r"\.?(?:\s+(?:east|west|north|south))?$", re.I)
STREET_IN_RE = re.compile(r"\b\d+[\w\-/]*(?:\s+[A-Za-z'\-]+){0,4}?\s+" + STREET_WORD + r"\b(?:\s+(?:east|west|north|south))?", re.I)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$£€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
COUNTRY_NAMES = {"united kingdom": "GB", "uk": "GB", "great britain": "GB", "england": "GB", "scotland": "GB", "wales": "GB",
                 "northern ireland": "GB", "ireland": "IE", "republic of ireland": "IE", "united states": "US", "usa": "US",
                 "australia": "AU", "new zealand": "NZ", "canada": "CA", "germany": "DE", "france": "FR", "netherlands": "NL",
                 "spain": "ES", "italy": "IT", "belgium": "BE", "switzerland": "CH", "india": "IN", "singapore": "SG",
                 "united arab emirates": "AE", "south africa": "ZA"}

_PACES = {}
_JAR = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_JAR))
TENANT = {"host": None}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[eploy] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, data=None, headers=None):
    """The tenant's host and no other, one cookie jar: the postback carries the session the first page opened."""
    parts = urllib.parse.urlsplit(url)
    if not TENANT["host"] or parts.netloc.lower() != TENANT["host"]:
        die(f"{url}: not this run's Eploy tenant ({TENANT['host'] or 'none named'}) — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(parts.netloc, Pace(parts.netloc, own=2.0)).wait()   # a tenant's Crawl-delay is read by Pace; 2 s is ours
    h = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en-GB,en"}
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
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", markup or "", flags=re.S)
    t = re.sub(r'<span[^>]*style="display:\s*none[^"]*"[^>]*>.*?</span>', "", t, flags=re.S)   # a validator's message is not a value
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", t)
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span|font)\b[^>]*>", "", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def without_address(label):
    """«Pear Tree High School, Worcester Road, Cheadle Hulme, Stockport, SK8 5NW» → the segments that are neither a street nor a postcode."""
    parts = [p.strip() for p in (label or "").split(",") if p.strip()]
    kept = []
    for p in parts:
        if STREET_RE.search(p):
            continue
        p = " ".join(STREET_IN_RE.sub(" ", UK_POSTCODE_RE.sub(" ", p)).split())   # a postcode or a street inside a segment goes too
        if p:
            kept.append(p)
    return kept


def tenant_of(arg):
    s = (arg or "").strip().lower()
    if "://" in s or "/" in s:
        s = urllib.parse.urlsplit(s if "://" in s else "https://" + s).netloc
    if not s or not HOST_RE.match(s):
        die(f"{arg!r}: a tenant is a host — the employer's careers site (jobs.le.ac.uk), found by the family's signature, never composed")
    return s


def fields_of(blk):
    out = {}
    for fid, item in ITEM_RE.findall(blk):
        lab = LABEL_RE.search(item)
        c = CONTENT_RE.search(item)
        ro = READONLY_RE.search(item)
        val = text(ro.group(1)) if ro else (text(c.group(1)) if c else None)
        label = (lab.group(1) or lab.group(2) or "").strip().rstrip(":") if lab else fid
        out[fid] = (label, val)
    return out


def cards_of(markup):
    idx = [m.start() for m in CARD_RE.finditer(markup)]
    out = []
    for a, b in zip(idx, idx[1:] + [None]):
        blk = markup[a:b] if b else markup[a:a + 40000]
        m = TITLE_RE.search(blk)
        if not m:
            continue
        out.append((htmlmod.unescape(m.group(1)), text(m.group(2)), fields_of(blk)))
    return out


def stated_count(markup):
    m = COUNT_RE.search(markup) or HERO_RE.search(markup)
    if m:
        return int(m.group(1).replace(",", ""))
    return 0 if NO_RESULTS_RE.search(markup) else None


def row(host, href, title, fields, country):
    mm = re.match(r"^(?:/vacancies/)?(\d+)/([^/]+)\.html$", href)
    vid = mm.group(1) if mm else None
    by_label = {lab.lower(): val for lab, val in fields.values() if val}
    loc_raw = (fields.get("VacV_AllLocations") or fields.get("VacV_LocationID") or (None, None))[1]
    loc = without_address(loc_raw) if loc_raw else []
    return {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{vid}", "id": vid,
        "url": f"https://{host}/vacancies/{vid}/{mm.group(2)}.html" if mm else f"https://{host}/vacancies/{href.lstrip('/')}",
        "title": title, "country": country,
        "place": loc[-1] if loc else None, "site": loc[0] if len(loc) > 1 else None,
        "salary": fields.get("VacV_DisplaySalary", (None, None))[1], "hours_per_week": fields.get("VacV_HoursPerWeek", (None, None))[1],
        "vacancy_type": fields.get("VacV_VacancyTypeID", (None, None))[1], "closes": fields.get("VacV_AdvertisingEndDate", (None, None))[1],
        "division": (fields.get("VacV_PositionID", (None, None))[1] if fields.get("VacV_PositionID", (None, None))[1] not in (None, "Please Select", "Not Specified") else None),
        "fields": {lab: val for lab, val in fields.values() if val and lab not in ("All Locations", "Location", "Vacancy ID")},   # the tenant's own labels, the address fields left out
        "contacts_withheld": True,
    }


def form_of(markup, target, page):
    """The page's own form, as the pager's link would submit it: every hidden field, the selects' selected values, the event."""
    f = []
    for tag in INPUT_RE.findall(markup):
        at = dict(ATTR_RE.findall(tag))
        if at.get("type", "").lower() != "hidden" or not at.get("name") or at["name"] in ("__EVENTTARGET", "__EVENTARGUMENT"):
            continue
        f.append((at["name"], htmlmod.unescape(at.get("value", ""))))
    for name, body in SELECT_RE.findall(markup):
        m = SELECTED_RE.search(body)
        if m:
            f.append((name, htmlmod.unescape(m.group(1) if m.group(1) is not None else m.group(2))))
    f.insert(0, ("__EVENTARGUMENT", str(page)))
    f.insert(0, ("__EVENTTARGET", target))
    return urllib.parse.urlencode(f).encode()


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    TENANT["host"] = host
    url = f"https://{host}{LIST_PATH}"
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404 — no Eploy list on this host", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    if not SIGNATURE_RE.search(body):
        die(f"{url}: not an Eploy careers site (no `$Eploy(` and no `aspnetForm` in the page).", EXIT_PARTIAL)
    total = stated_count(body)
    cards = cards_of(body)
    country = (a.country_code or "").strip().upper() or None
    rows, seen, walked = [], set(), 1
    current = body
    while True:
        new = 0
        for href, title, fields in cards:
            r = row(host, href, title, fields, country)
            if not r["id"] or r["id"] in seen:
                continue
            seen.add(r["id"])
            rows.append(r)
            new += 1
        if cards and new == 0:
            die(f"{url}: page {walked} repeated the previous one — the postback did not advance; {th(len(rows))} kept of the {th(total or 0)} stated.", EXIT_PARTIAL)
        links = {int(p): t for t, p in (POSTBACK_RE.findall(htmlmod.unescape(current)))}
        nxt = walked + 1
        if not cards or nxt not in links or (total is not None and len(rows) >= total) or (a.max_pages and walked >= a.max_pages):
            break
        data = form_of(current, links[nxt], nxt)
        st, current = request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded", "Referer": url, "Origin": f"https://{host}"})
        if st != 200:
            die(f"{url}: HTTP {st} on the postback to page {nxt}", EXIT_PARTIAL)
        cpb = CPB_RE.search(current)
        if not cpb or int(cpb.group(1)) != nxt:
            die(f"{url}: the postback to page {nxt} answered page {cpb.group(1) if cpb else '?'} — the pager needs the page's own fields and cookies; {th(len(rows))} kept of the {th(total or 0)} stated.", EXIT_PARTIAL)
        walked = nxt
        cards = cards_of(current)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    n = len(rows)
    stamp = f"; country {country} stamped from --country-code (the list states none)" if country else ""
    if total is None:
        note(f"{th(n)} emitted over {walked} page(s) — the page states no count (no «N Vacancies» in its title){stamp}.")
    elif a.max_pages and walked >= a.max_pages and total > n:
        note(f"{th(n)} emitted of the {th(total)} the site states — {walked} page(s) of {PAGE_SIZE} walked by request (--max-pages), not a shortfall{stamp}.")
    elif n == total:
        note(f"{th(n)} emitted over {walked} page(s) — the site states {th(total)}: equal{stamp}.")
    else:
        note(f"{th(n)} emitted over {walked} page(s) — the site states {th(total)}: {th(abs(total - n))} " + ("short" if total > n else "more emitted than stated") + f"{stamp}.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    m = AD_PATH_RE.match(parts.path)
    if not parts.netloc or not HOST_RE.match(parts.netloc) or not m:
        die(f"{a.url!r}: not an Eploy vacancy address (https://<host>/vacancies/<id>/<slug>.html)")
    host = parts.netloc.lower()
    TENANT["host"] = host
    url = f"https://{host}/vacancies/{m.group(1)}/{m.group(2)}.html"
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped.", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    ps = ld_postings(body)
    if not ps:
        die(f"{url}: no JobPosting in the page — an Eploy vacancy page carries one; the shape changed, or this is not one.", EXIT_PARTIAL)
    p = ps[0]
    org = p.get("hiringOrganization") if isinstance(p.get("hiringOrganization"), dict) else {}
    loc = p.get("jobLocation") if isinstance(p.get("jobLocation"), dict) else {}
    addr = loc.get("address") if isinstance(loc.get("address"), dict) else {}
    cn = addr.get("addressCountry")
    country = COUNTRY_NAMES.get(str(cn).strip().lower()) if cn else None
    if not country and isinstance(cn, str) and len(cn.strip()) == 2:
        country = cn.strip().upper()
    sal = p.get("baseSalary") if isinstance(p.get("baseSalary"), dict) else {}
    sv = sal.get("value") if isinstance(sal.get("value"), dict) else {}
    r = {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{m.group(1)}", "id": m.group(1), "url": url,
        "title": p.get("title"), "company": org.get("name"), "country": country, "country_name": cn if isinstance(cn, str) else None,
        "place": addr.get("addressLocality"), "region": addr.get("addressRegion"),
        # streetAddress and postalCode are the premises' address and are not emitted
        "posted": p.get("datePosted"), "closes": p.get("validThrough"), "employment_type": p.get("employmentType"),
        "salary": sv.get("value") or sal.get("value") if not isinstance(sal.get("value"), dict) else sv.get("value"),
        "salary_currency": sal.get("currency"), "skills": p.get("skills"), "industry": p.get("industry"),
        "description": (scrub(text(p.get("description"))) or "")[:20000] or None,
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Eploy — one tenant's careers site: the server-rendered list 12 a page, the pages beyond the first by the pager's own postback with the page's fields and cookies, the count from the page's title beside every walk; the vacancy page's JobPosting; no contact. Issue #464.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the tenant's list, 12 a page, 2 s apart, to the stated count")
    s.add_argument("--tenant", required=True, help="the tenant's host (jobs.le.ac.uk) or its URL")
    s.add_argument("--country-code", help="ISO2 to stamp the rows with — the list states no country; the user names the tenant's")
    s.add_argument("--max-pages", type=int)
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one vacancy by its page's JobPosting; street and postal code withheld, description scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
