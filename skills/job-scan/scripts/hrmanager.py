#!/usr/bin/env python3
"""HR-Manager / Talentech Talent Recruiter (a Nordic ATS, one tenant at a time): the employer's positions by the JobPortal API its own career site calls — `api.hr-manager.net/jobportal.svc/<alias>/positionlist/json/`, 50 a call by `take`/`skip`, `PositionCountCustomer` stated in every answer — and the advert by its permitted page on `candidate.hr-manager.net`. Issue #467.

  hrmanager.py jobs --tenant <alias> [--country-code ISO2] [--max-pages N]
  hrmanager.py ad --url "https://candidate.hr-manager.net/ApplicationInit.aspx?cid=<n>&ProjectId=<n>[&DepartmentId=<n>&MediaId=<n>]"

THE TENANT is the customer alias the employer's own site uses —
`candidate.hr-manager.net/vacancies/list.aspx?customer=<alias>` and
`api.hr-manager.net/jobportal.svc/<alias>/…` spell the same word
(`regionsyddanmark`, `regionh`, `kl`) — found by that signature, never
composed: an unknown alias answers 400 with `StatusCode: 1` («Value cannot
be null … connectionString»), exit 3.

THE ROUTE. `api.hr-manager.net` publishes no rules file (404 — knowledge,
no rules); `candidate.hr-manager.net` writes `Allow:
/ApplicationInit.aspx?`, `Disallow: /ApplicationInit.aspx?*SkipAdvertisement
=True*`, `Disallow: /` to `*` — the advert page is permitted, the hosted
list (`/vacancies/list.aspx`) and the application form are not, and
neither is requested. The API (measured 2026-09-20 on three tenants)
answers `Items[]` with `PositionCountCustomer` (the tenant's total),
`PositionCountList` (this answer's), `PositionCountSkipped`; `take=` sets
the page (50 here; the default is 25), `skip=` the offset (`top`,
`pagesize`, `limit`, `page` are ignored — measured). `incads=0`: the
advert bodies are not carried in the list; the `ad` command reads the
permitted page instead (`h1.ProjectName`, `#AdvertisementInnerContent`).

WITHHELD: `ProjectLeader*`, `ProjectParticipants`, `Users`,
`ProjectAdministratorId` (the hiring manager and the recruiters — names,
e-mails, telephones, portraits); the department's street, postal code and
PO box; the advert page's `contact` block dropped whole and the text
scrubbed of e-mail addresses and telephone numbers; the application form
(`SkipAdvertisement=True`, refused in writing anyway) never touched;
`contacts_withheld` on every record.
"""

import argparse
import html as htmlmod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD = "hrmanager"
API_HOST = "api.hr-manager.net"
PAGE_HOST = "candidate.hr-manager.net"
HOSTS = (API_HOST, PAGE_HOST)
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE_SIZE = 50

ALIAS_RE = re.compile(r"^[a-z0-9][a-z0-9_\-]*$", re.I)
DATE_RE = re.compile(r"/Date\((-?\d+)([+-]\d{4})?\)/")
TITLE_RE = re.compile(r'<h1 class="ProjectName"[^>]*>(.*?)</h1>', re.S)
CONTENT_RE = re.compile(r'<div id="AdvertisementInnerContent"[^>]*>(.*?)</div>\s*(?=<div|<!--|</td|</body)', re.S)
CONTACT_RE = re.compile(r'<div class="contact[ "].*?<div class="contactinfo">.*?</div>\s*</div>', re.S)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{6,}\d(?!\w)")
COUNTRIES = {"danmark": "DK", "denmark": "DK", "norge": "NO", "norway": "NO", "sverige": "SE", "sweden": "SE", "finland": "FI", "suomi": "FI",
             "island": "IS", "iceland": "IS", "deutschland": "DE", "germany": "DE", "tyskland": "DE", "united kingdom": "GB", "storbritannien": "GB",
             "nederland": "NL", "netherlands": "NL", "holland": "NL", "polen": "PL", "poland": "PL", "grønland": "GL", "greenland": "GL", "færøerne": "FO"}
_PACES = {h: Pace(h, own=2.0) for h in HOSTS}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[hrmanager] {msg}", file=sys.stderr)


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
    if parts.netloc not in HOSTS:
        die(f"{url}: not an HR-Manager host — never sent", EXIT_REFUSED)
    gate(url)
    _PACES[parts.netloc].wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "application/json, text/html", "Accept-Language": "da,en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        try:
            return e.code, decode_body(e.read(), e.headers)[0]
        except Exception:                                  # noqa: BLE001 — the code is what matters
            return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", markup or "", flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", t)
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span|font)\b[^>]*>", "", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def when(v):
    """`/Date(1790200799000+0200)/` → ISO 8601 in the offset the API wrote; anything else as it came."""
    m = DATE_RE.match(v or "") if isinstance(v, str) else None
    if not m:
        return v or None
    ms = int(m.group(1))
    off = m.group(2)
    tz = timezone(timedelta(hours=int(off[:3]), minutes=int(off[0] + off[3:]))) if off else timezone.utc
    return datetime.fromtimestamp(ms / 1000, tz).isoformat(timespec="minutes")


def tenant_of(arg):
    s = (arg or "").strip()
    if "://" in s or "/" in s:
        parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
        q = urllib.parse.parse_qs(parts.query)
        m = re.match(r"^/jobportal\.svc/([^/]+)/", parts.path)
        alias = (q.get("customer") or [None])[0] or (m.group(1) if m else None)
        if parts.netloc not in (API_HOST, PAGE_HOST) or not alias:
            die(f"{arg!r}: not an HR-Manager tenant address (…/vacancies/list.aspx?customer=<alias> or …/jobportal.svc/<alias>/…)")
        s = alias
    if not ALIAS_RE.match(s):
        die(f"{arg!r}: a tenant is the customer alias the employer's site uses (regionsyddanmark), found by the signature, never composed")
    return s.lower()


def name_of(v):
    return v.get("Name") if isinstance(v, dict) else None


def country_of(name):
    if not name or not isinstance(name, str):
        return None
    n = name.strip()
    if len(n) == 2 and n.isalpha():
        return n.upper()
    return COUNTRIES.get(n.lower())


def row(it, alias, country_stamp):
    tree = it.get("DepartmentTree") if isinstance(it.get("DepartmentTree"), dict) else {}
    dept = it.get("Department") if isinstance(it.get("Department"), dict) else {}
    url = it.get("AdvertisementUrlSecure") or it.get("AdvertisementUrl")
    langs = [l.get("Code") for l in (it.get("Languages") or []) if isinstance(l, dict) and l.get("Code")]
    country = country_of(tree.get("Country") or dept.get("Country")) or country_stamp
    return {
        "source": BOARD, "tenant": alias, "ledger_id": f"{BOARD}:{alias}:{it.get('Id')}", "id": it.get("Id"),
        "url": url, "title": it.get("Name"), "company": it.get("CustomerName"),
        "department": (dept.get("Name") or "").strip() or None, "organisation": tree.get("Name"),
        "place": name_of(it.get("PositionLocation")) or dept.get("City") or tree.get("City") or None,
        "region": tree.get("County") or dept.get("County") or None, "country": country, "country_name": tree.get("Country") or dept.get("Country") or None,
        # the department's Address, Zip and POBox are the premises' address and are not emitted
        "category": name_of(it.get("PositionCategory")), "position_type": it.get("PositionType") or None,
        "work_hours": it.get("WorkHours") or None, "workplace": it.get("WorkPlace") or None,
        "published": when(it.get("Published")), "updated": when(it.get("LastUpdated")), "closes": when(it.get("ApplicationDue")),
        "starts": "ASAP" if it.get("StartDateASAP") else when(it.get("StartDate")),
        "summary": scrub(text(it.get("ShortDescription"))), "languages": langs or None,
        # ProjectLeader*, ProjectParticipants, Users, ProjectAdministratorId — the hiring manager and the recruiters — are never emitted
        "contacts_withheld": True,
    }


def page(alias, skip):
    url = f"https://{API_HOST}/jobportal.svc/{alias}/positionlist/json/?incads=0&take={PAGE_SIZE}&skip={skip}"
    st, body = request(url)
    try:
        j = json.loads(body) if body else {}
    except ValueError:
        j = {}
    status = (j.get("TransactionStatus") or {}) if isinstance(j, dict) else {}
    if st == 400 or status.get("StatusCode") not in (0, None):
        die(f"{url}: HTTP {st}, StatusCode {status.get('StatusCode')} — {status.get('Description', '').strip() or 'no description'}: no such tenant alias, or the API refused it", EXIT_GONE if st == 400 else EXIT_PARTIAL)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    if not isinstance(j, dict) or "PositionCountCustomer" not in j or not isinstance(j.get("Items"), list):
        die(f"{url}: no `PositionCountCustomer` / `Items` in the answer — not the JobPortal API's shape.", EXIT_PARTIAL)
    return j.get("PositionCountCustomer"), j.get("CustomerName"), [i for i in j["Items"] if isinstance(i, dict)]


def cmd_jobs(a):
    alias = tenant_of(a.tenant)
    stamp = (a.country_code or "").strip().upper() or None
    total, customer, items = page(alias, 0)
    rows, seen, walked = [], set(), 1
    while True:
        new = 0
        for it in items:
            if it.get("Id") is None or it["Id"] in seen:
                continue
            seen.add(it["Id"])
            rows.append(row(it, alias, stamp))
            new += 1
        if items and new == 0:
            die(f"{alias}: the call at skip={(walked - 1) * PAGE_SIZE} repeated the previous one — `skip` is not advancing; {th(len(rows))} kept of the {th(total)} stated.", EXIT_PARTIAL)
        last = -(-(total or 0) // PAGE_SIZE)
        if not items or len(rows) >= (total or 0) or walked >= last or (a.max_pages and walked >= a.max_pages):
            break
        walked += 1
        _t, _c, items = page(alias, (walked - 1) * PAGE_SIZE)
    want = stamp
    emitted = [r for r in rows if not want or r["country"] == want]
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    who = f"{customer or alias}"
    if want:
        note(f"{th(n)} emitted for {want} of the {th(len(rows))} read over {walked} call(s) — the API states {th(total)} for {who}; a position without a country in its department tree is stamped {want}.")
    elif a.max_pages and walked >= a.max_pages and (total or 0) > len(rows):
        note(f"{th(n)} emitted of the {th(total)} the API states for {who} — {walked} call(s) of {PAGE_SIZE} by request (--max-pages), not a shortfall.")
    elif n == total:
        note(f"{th(n)} emitted over {walked} call(s) — the API states {th(total)} for {who}: equal.")
    else:
        note(f"{th(n)} emitted over {walked} call(s) — the API states {th(total)} for {who}: {th(abs((total or 0) - n))} " + ("short" if (total or 0) > n else "more emitted than stated") + ".")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    q = {k.lower(): v[0] for k, v in urllib.parse.parse_qs(parts.query).items()}
    if parts.netloc != PAGE_HOST or parts.path.lower() != "/applicationinit.aspx" or not q.get("cid", "").isdigit() or not q.get("projectid", "").isdigit():
        die(f"{a.url!r}: not an HR-Manager advert address (https://{PAGE_HOST}/ApplicationInit.aspx?cid=<n>&ProjectId=<n>…)")
    keep = [("cid", q["cid"]), ("ProjectId", q["projectid"])] + [(k, q[k.lower()]) for k in ("DepartmentId", "MediaId") if q.get(k.lower())]
    url = f"https://{PAGE_HOST}/ApplicationInit.aspx?" + urllib.parse.urlencode(keep)   # never SkipAdvertisement=True — the form, refused in writing
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped.", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    t = TITLE_RE.search(body)
    c = CONTENT_RE.search(body)
    if not t or not c:
        die(f"{url}: no `ProjectName` or no `AdvertisementInnerContent` in the page — not an advert page, or the advert is gone.", EXIT_PARTIAL)
    content = CONTACT_RE.sub("", c.group(1))
    r = {
        "source": BOARD, "ledger_id": f"{BOARD}:cid{q['cid']}:{q['projectid']}", "id": int(q["projectid"]), "customer_id": int(q["cid"]), "url": url,
        "title": text(t.group(1)),
        "description": (scrub(text(content)) or "")[:20000] or None,
        # the page's `contact` block (name, title, telephone, portrait) is dropped whole
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="HR-Manager / Talentech — one tenant's positions by the JobPortal API its career site calls (take/skip, PositionCountCustomer beside every walk) and the advert by its permitted page; the hiring manager and the recruiters never emitted. Issue #467.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the tenant's positions, 50 a call, 2 s apart, to the stated PositionCountCustomer")
    s.add_argument("--tenant", required=True, help="the customer alias (regionsyddanmark), or a list/API address that carries it")
    s.add_argument("--country-code", help="keep the positions whose department tree names this ISO2 country (a tree without a country is stamped with it)")
    s.add_argument("--max-pages", type=int)
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its permitted page on candidate.hr-manager.net; the contact block dropped, the text scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
