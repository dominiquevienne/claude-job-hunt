#!/usr/bin/env python3
"""UKG Pro, ex-UltiPro (`recruiting.ultipro.com`, `recruiting2.ultipro.com`) — an ATS, one tenant at a time: the tenant's job board page is permitted and read; the list it loads is REFUSED IN WRITING (`Disallow: */JobBoardView`) and requested only under the user's own `boards.ukgpro.override_robots: true`. Issue #463, the decision on #792.

  ukgpro.py jobs --tenant <code>/<guid> [--host recruiting2.ultipro.com] [--q TEXT] [--country-code ISO2] [--max-pages N]
  ukgpro.py ad --url https://recruiting.ultipro.com/<code>/JobBoard/<guid>/OpportunityDetail?opportunityId=<guid>

THE LIST ROUTE IS REFUSED, AND THAT IS THE FIRST THING THIS ADAPTER SAYS.
`recruiting.ultipro.com/robots.txt` (read 2026-09-20) writes to `User-agent: *`:
`Disallow: /`, `Allow: */JobBoard/`, `Disallow: */JobBoardView`, `Disallow:
*/JobBoard/*/Styles`, `Disallow: */JobBoard/*/AnonymousSessionCheck`. The
tenant's board `/<code>/JobBoard/<guid>` and its opportunity pages
`…/OpportunityDetail?opportunityId=…` fall under the Allow and are read
without any key; the call the board page makes for its list —
`POST …/JobBoard/<guid>/JobBoardView/LoadSearchResults` — falls under the
Disallow, and the page carries no list of its own (only the featured
opportunities, a subset).

**Without the key `jobs` requests nothing and exits 7**, naming the rule, the
key and the file it consulted. **With the key** — the owner's decision of
2026-09-13 (#403), «l'utilisateur doit pouvoir émettre une dérogation en son
âme et conscience», applied to this board on #792 (2026-09-20): the user's
line in the user's workspace — the guard flips the written «no» for this
board, prints the banner (what is crossed before what it costs), and the
adapter reads the board page, then the list 50 a page, 2 s apart, with the
page's own request (`opportunitySearch` + `matchCriteria`, the anti-forgery
token and cookies the page carries), to the `totalCount` the answer states.
`ad` needs no key: the opportunity page carries the opportunity as JSON.

**Written and exercised on fixtures of the page's own shapes (two tenants'
board pages, one opportunity page, the bundle `site.min.js` that builds the
request) on 2026-09-20; no request was made under `JobBoardView/` by this
repository** — the key was absent on this machine, by design, and it is not
the developer's to set. The first keyed run is the first measurement of the
list; the request body and the answer's shape (`opportunities`, `locations`,
`totalCount`, `initialTotalOpportunitiesCount`) are the bundle's.

WITHHELD: `SupervisorName` (the hiring manager, a person); the premises'
street (`Address.Line1/Line2`), postal code and coordinates; the description
scrubbed of e-mail addresses and telephone numbers; the application
(`QuickApply`, an account) never touched; `contacts_withheld` on every record.
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
from _iso3 import alpha2
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD = "ukgpro"
HOSTS = ("recruiting.ultipro.com", "recruiting2.ultipro.com")
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE_SIZE = 50                      # the page's own `pageSize: 50`

GUID = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
TENANT_RE = re.compile(r"^([A-Za-z0-9]+)/(" + GUID + r")$")
BOARD_PATH_RE = re.compile(r"^/([A-Za-z0-9]+)/JobBoard/(" + GUID + r")/?$")
AD_PATH_RE = re.compile(r"^/([A-Za-z0-9]+)/JobBoard/(" + GUID + r")/OpportunityDetail/?$")
TOKEN_RE = re.compile(r'name="__RequestVerificationToken"\s+type="hidden"\s+value="([^"]+)"')
SETTING_RE = {k: re.compile(r'\b' + k + r':\s*"([^"]*)"') for k in ("loadUrl", "opportunityLinkUrl")}
PAGE_SIZE_RE = re.compile(r"\bpageSize:\s*(\d+)")
FEATURED_RE = re.compile(r"initialFeaturedOpportunities:\s*(\[)")
DETAIL_RE = re.compile(r"US\.Opportunity\.CandidateOpportunityDetail\(\s*(\{)")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$])\+?\d[\d\s().\-]{7,}\d(?!\w)")

_PACES = {h: Pace(h, own=2.0) for h in HOSTS}   # no Crawl-delay written; 2 s is ours
_JAR = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_JAR))


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[ukgpro] {msg}", file=sys.stderr)


def gate(url):
    """The guard on the exact path, with this board's name — so the user's key, and only it, can turn the written «no».

    `_robots.allowed()` prints the banner itself when it crosses (#403); this
    function adds the refusal's own words when it does not, and the sentence
    to write — `boards.ukgpro.override_robots: true` — never only a path."""
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts), board=BOARD)
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: refused in writing — {a.get('host') or parts.netloc} writes `Disallow: {a.get('rule')}` to `User-agent: *`, and the list "
            f"this board's page loads is under it (the page itself is permitted, and carries no list). **This adapter requests nothing.** "
            f"The one exit is yours to take, in your own name: "
            f"{a.get('override_available', 'boards.' + BOARD + '.override_robots: true in config.yml')} — see shared/setup.md 5h and "
            f"shared/robots-policy.md; the address that would get blocked is yours.", EXIT_REFUSED)
    return a


def request(url, headers=None, data=None):
    """One of the two hosts, one cookie jar: the page's cookies replayed as the page does (the anti-forgery pair)."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc not in HOSTS:
        die(f"{url}: not a UKG Pro host — never sent", EXIT_REFUSED)
    gate(url)
    _PACES[parts.netloc].wait()
    h = {"User-Agent": UA, "Accept": "application/json" if data is not None else "text/html,application/xhtml+xml", "Accept-Language": "en"}
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
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span|font)\b[^>]*>", "", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def json_after(markup, opener_re, what):
    """The JSON value the page writes after `opener_re` (its `[` or `{` is group 1), decoded where it starts."""
    m = opener_re.search(markup or "")
    if not m:
        die(f"no `{what}` in the page — not a UKG Pro job board page, or its shape changed.", EXIT_PARTIAL)
    try:
        v, _end = json.JSONDecoder().raw_decode(markup[m.start(1):])
    except ValueError as e:
        die(f"`{what}` in the page is not JSON: {e}", EXIT_PARTIAL)
    return v


def tenant_of(arg, host):
    """`<code>/<guid>` or the board's URL → (host, code, guid)."""
    s = (arg or "").strip()
    if "://" in s or s.split("/", 1)[0] in HOSTS:
        parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
        m = BOARD_PATH_RE.match(parts.path)
        if parts.netloc not in HOSTS or not m:
            die(f"{arg!r}: not a UKG Pro job board address (https://recruiting.ultipro.com/<code>/JobBoard/<guid>)")
        return parts.netloc, m.group(1), m.group(2).lower()
    m = TENANT_RE.match(s)
    if not m:
        die(f"{arg!r}: a tenant is spelled <code>/<guid> as the board's address does (UNI1076UNFI/86df2700-…), or the address itself")
    if host not in HOSTS:
        die(f"--host {host!r}: not one of {', '.join(HOSTS)}")
    return host, m.group(1), m.group(2).lower()


def place_of(loc):
    """City · region · country of a location — the premises' street, postal code and coordinates left behind."""
    a = loc.get("Address") if isinstance(loc.get("Address"), dict) else {}
    st = a.get("State") if isinstance(a.get("State"), dict) else {}
    co = a.get("Country") if isinstance(a.get("Country"), dict) else {}
    code = alpha2(co.get("Code")) if co.get("Code") else None
    return {"name": loc.get("LocalizedDescription") or loc.get("LocalizedName"), "city": a.get("City"),
            "region": st.get("Name") or st.get("Code"), "country": code, "country_name": co.get("Name")}


def row(o, host, code, guid):
    locs = [place_of(l) for l in (o.get("Locations") or []) if isinstance(l, dict)]
    first = locs[0] if locs else {}
    oid = o.get("Id")
    return {
        "source": BOARD, "tenant": f"{code}/{guid}", "ledger_id": f"{BOARD}:{code}:{oid}", "id": oid,
        "url": f"https://{host}/{code}/JobBoard/{guid}/OpportunityDetail?opportunityId={oid}",
        "title": o.get("Title"), "requisition": o.get("RequisitionNumber"), "category": o.get("JobCategoryName"),
        "full_time": o.get("FullTime"), "featured": o.get("Featured"),
        "place": first.get("city"), "region": first.get("region"), "country": first.get("country"),
        "locations": locs, "posted": o.get("PostedDate"),
        "summary": scrub(text(o.get("BriefDescription"))),
        "contacts_withheld": True,
    }


def board_page(host, code, guid):
    """The tenant's board page (permitted): its token, settings and featured opportunities."""
    url = f"https://{host}/{code}/JobBoard/{guid}"
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404 — no such job board (the code and the guid are both part of the address)", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    tok = TOKEN_RE.search(body)
    settings = {k: (r.search(body).group(1) if r.search(body) else None) for k, r in SETTING_RE.items()}
    ps = PAGE_SIZE_RE.search(body)
    if not tok or not settings["loadUrl"]:
        die(f"{url}: no `__RequestVerificationToken` or no `loadUrl` in the page — not a UKG Pro job board page, or its shape changed.", EXIT_PARTIAL)
    expected = f"/{code}/JobBoard/{guid}/JobBoardView/LoadSearchResults"
    if settings["loadUrl"].lower() != expected.lower():
        die(f"{url}: the page loads {settings['loadUrl']!r}, not {expected!r} — not this tenant's board, or the route moved.", EXIT_PARTIAL)
    featured = json_after(body, FEATURED_RE, "initialFeaturedOpportunities")
    return {"url": url, "token": tok.group(1), "load_url": f"https://{host}{settings['loadUrl']}",
            "page_size": int(ps.group(1)) if ps else PAGE_SIZE,
            "featured": [o for o in featured if isinstance(o, dict)] if isinstance(featured, list) else []}


def search_body(q, skip, top):
    """The page's own request, as `site.min.js` builds it: `opportunitySearch` (posted date descending, no filter) and the anonymous handler's empty `matchCriteria`."""
    return json.dumps({
        "opportunitySearch": {"Top": top, "Skip": skip, "QueryString": q or "", "OrderBy": [
            {"Value": "postedDateDesc", "PropertyName": "PostedDate", "Ascending": False}], "Filters": []},
        "matchCriteria": {"PreferredJobs": [], "Educations": [], "LicenseAndCertifications": [], "Skills": [], "hasNoLicenses": False, "SkippedSkills": []},
    }).encode()


def load_page(page, q, skip):
    headers = {"X-RequestVerificationToken": page["token"], "Content-Type": "application/json; charset=utf-8",
               "Referer": page["url"], "Origin": page["url"].split("/", 3)[0] + "//" + urllib.parse.urlsplit(page["url"]).netloc,
               "X-Requested-With": "XMLHttpRequest"}
    st, body = request(page["load_url"], headers=headers, data=search_body(q, skip, page["page_size"]))
    if st in (403, 429):
        die(f"{page['load_url']}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{page['load_url']}: HTTP {st} at Skip={skip}", EXIT_PARTIAL)
    try:
        j = json.loads(body)
    except ValueError:
        die(f"{page['load_url']}: not JSON ({len(body)} characters) at Skip={skip}", EXIT_PARTIAL)
    if not isinstance(j, dict) or "totalCount" not in j or not isinstance(j.get("opportunities"), list):
        die(f"{page['load_url']}: no `totalCount` / `opportunities` in the answer — not the page's response shape.", EXIT_PARTIAL)
    return j["totalCount"], [o for o in j["opportunities"] if isinstance(o, dict)]


def cmd_jobs(a):
    host, code, guid = tenant_of(a.tenant, a.host)
    list_url = f"https://{host}/{code}/JobBoard/{guid}/JobBoardView/LoadSearchResults"
    gate(list_url)                       # the written «no» first — without the key, nothing is requested, not even the page
    page = board_page(host, code, guid)
    total, hits = load_page(page, a.q, 0)
    rows, seen, walked = [], set(), 1
    while True:
        new = 0
        for o in hits:
            if not o.get("Id") or o["Id"] in seen:
                continue
            seen.add(o["Id"])
            rows.append(row(o, host, code, guid))
            new += 1
        if hits and new == 0:
            die(f"{list_url}: page {walked} (Skip={(walked - 1) * page['page_size']}) repeated the previous one — the pager is not advancing; {th(len(rows))} kept of the {th(total)} stated.", EXIT_PARTIAL)
        if not hits or len(rows) >= (total or 0) or (a.max_pages and walked >= a.max_pages):
            break
        walked += 1
        _t, hits = load_page(page, a.q, (walked - 1) * page["page_size"])
    want = (a.country_code or "").strip().upper() or None
    emitted = [r for r in rows if not want or r["country"] == want or any(l.get("country") == want for l in r["locations"])]
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    where = f"(q={a.q!r})" if a.q else "(no filter)"
    bounded = a.max_pages and walked >= a.max_pages and (total or 0) > len(rows)
    if want:
        note(f"{th(n)} emitted for {want} of the {th(len(rows))} read over {walked} page(s) — the board states {th(total)} {where}, no country filter of its own; {len(page['featured'])} featured on the page.")
    elif bounded:
        note(f"{th(n)} emitted of the {th(total)} the board states {where} — {walked} page(s) of {page['page_size']} walked by request (--max-pages), not a shortfall.")
    elif n == total:
        note(f"{th(n)} emitted over {walked} page(s) — the board states {th(total)} {where}: equal; {len(page['featured'])} featured on the page.")
    else:
        note(f"{th(n)} emitted over {walked} page(s) — the board states {th(total)} {where}: {th(abs((total or 0) - n))} " + ("short" if (total or 0) > n else "more emitted than stated") + ".")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    m = AD_PATH_RE.match(parts.path)
    oid = (urllib.parse.parse_qs(parts.query).get("opportunityId") or [""])[0].lower()
    if parts.netloc not in HOSTS or not m or not re.match("^" + GUID + "$", oid):
        die(f"{a.url!r}: not an opportunity address (https://recruiting.ultipro.com/<code>/JobBoard/<guid>/OpportunityDetail?opportunityId=<guid>)")
    host, code, guid = parts.netloc, m.group(1), m.group(2).lower()
    url = f"https://{host}/{code}/JobBoard/{guid}/OpportunityDetail?opportunityId={oid}"
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped.", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    o = json_after(body, DETAIL_RE, "CandidateOpportunityDetail")
    if not isinstance(o, dict) or not o.get("Id"):
        die(f"{url}: the opportunity object carries no Id.", EXIT_PARTIAL)
    r = row(o, host, code, guid)
    pay = o.get("PayRange") if isinstance(o.get("PayRange"), dict) else {}
    r.update({
        "description": scrub(text(o.get("Description")))[:20000] if o.get("Description") else None,
        "updated": o.get("UpdatedDate"), "hours_per_week": o.get("HoursPerWeek"), "salaried": o.get("Salaried"),
        "closed": o.get("OpportunityIsClosed"), "travel": o.get("TravelDescription"),
        "pay_range": {"min": pay.get("PayRangeMinimum"), "max": pay.get("PayRangeMaximum"), "currency": o.get("PayRangeCurrencyCode")} if o.get("PayRangeVisible") else None,
        "education": [{"degree": e.get("DegreeName"), "major": e.get("MajorName"), "required": e.get("Required")} for e in (o.get("EducationCriteria") or []) if isinstance(e, dict)],
        "skills": [s.get("SkillName") or s.get("Name") for s in (o.get("SkillCriteria") or []) if isinstance(s, dict)],
        "experience": [{"years": w.get("Years") or w.get("YearsOfExperience"), "description": w.get("Description") or w.get("WorkExperienceDescription"), "required": w.get("Required")} for w in (o.get("WorkExperienceCriteria") or []) if isinstance(w, dict)],
        # SupervisorName — the hiring manager, a person — is never emitted, nor the street, the postal code or the coordinates
        "equal_opportunity": scrub(text(o.get("EqualOpportunityEmployerDescription"))),
    })
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="UKG Pro (ex-UltiPro) — one tenant's job board: the page (permitted) read, the list it loads (refused in writing, Disallow: */JobBoardView) requested only under the user's own boards.ukgpro.override_robots; totalCount beside every walk; the opportunity page needs no key; no contact. Issue #463.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the board's list, 50 a page, 2 s apart, newest first; without the key: nothing requested, exit 7")
    s.add_argument("--tenant", required=True, help="<code>/<guid> as the board's address spells it, or the address itself")
    s.add_argument("--host", default=HOSTS[0], help="recruiting.ultipro.com (default) or recruiting2.ultipro.com")
    s.add_argument("--q", help="free text, as the page's search box")
    s.add_argument("--country-code", help="keep the opportunities with a location in this ISO2 country (the board writes alpha-3; converted)")
    s.add_argument("--max-pages", type=int)
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one opportunity from its page (permitted, no key): the JSON the page carries; the hiring manager's name withheld")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
