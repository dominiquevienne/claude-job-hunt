#!/usr/bin/env python3
"""Eezy (`tyopaikat.eezy.fi`) — the Finnish staffing group's board, a Next.js site whose list is filled on the client by the page's own GraphQL query to the group's API (`api.eezy.fi/api`, `elasticJobs`): the adapter replays that query exactly as the page makes it — the query text read from the page's own script on every run, the page's own variables — and prints emitted against the `available` the answer states; the ad page server-rendered with its `jobAdvert` object; **`recruitmentPerson` — name, e-mail, telephone, photo — on the ad and never emitted; the client's name withheld when the site hides it (`hideCustomer`)**. Issue #379.

  eezy.py list [--limit N]                    the site's list: 3 requests (the page, its script, the query) — 236 rows on 2026-09-14
  eezy.py ad --url <https://tyopaikat.eezy.fi/fi/tyopaikat/<id>>

THE RULES. `tyopaikat.eezy.fi/robots.txt` (200) is a single `Sitemap:` line — no group, no
refusal; `api.eezy.fi/robots.txt` 404 — no rules; `eezy.fi` (the corporate site, WordPress)
`User-Agent: * / Disallow:` (empty — everything open). No Crawl-delay anywhere; 2 s is ours.

THE INVENTORIES THAT ARE NOT. `eezy.fi/tyopaikat-sitemap.xml` (782 rows) is facets —
`tyopaikat.eezy.fi/fi?job=…&location=…` — not ads. `tyopaikat.eezy.fi/sitemap.xml`, the one the
rules name, is an RSS feed («Eezy työpaikkailmoitukset», 338 items): **10 advertisements**
(the `Personnel` source, with a description and a real lastmod) and 328 location facets whose
`lastmod` is the moment of the read. The listing `/fi` (200, 44 KB, `__NEXT_DATA__`) ships the
filter values only — `fieldOfWorks`, `locations` — and fills its jobs on the client.

THE LIST IS THE PAGE'S OWN QUERY. The page's `_app-*.js` carries the Apollo client (`uri:
"https://api.eezy.fi" + "/api"`) and the query text — `elasticJobs(filter:{searchStringArr,
locations, isTraining, from, to, tags, fieldOfWorks}) { pageResults { available from to
showingFallbackAdverts } jobs { id name logo customer customerDescription hideCustomer source
fieldOfWorks workLocations { name } } }` — which the page sends with `{locations: [], from: 0,
to: 20}` (`ITEMS_TO_FETCH` 20) and pages by 20. The adapter reads the text from the script on
every run, sends the page's first call, then one call with `to` = `available`. **The page's
own query, to the page's own API, with the page's own variables; nothing is guessed.** The row:
`id` (22 chars for the `Core` source, 5 for `Personnel`), `name`, `customer` — **only when
`hideCustomer` is false; the site hides it on 159 of 236 and so does the adapter** —
`source`, `fieldOfWorks`, `workLocations` (region and town names). No date on the row.

THE AD. `/fi/tyopaikat/<id>` (200, ~80 KB) is server-rendered with `pageProps.jobAdvert`:
`name`, `worktitle`, `description` (HTML) and `descriptionPlain` (plain on `Personnel`, HTML on
`Core`), `customer` / `hideCustomer` / `customerDescription`, `startTime`, `endTime`,
`typeOfWorkRelationship`, `workRelationshipMode`, `fieldOfWorks`, `locationCity`,
`locationAddress`, `workLocations`, `isDeleted`, `applyLink` (the ATS — `talent.core.eezy.fi`
or `ats.talentadore.com` — never followed) **and `recruitmentPerson` {firstname, lastname,
photo, email, phoneNumber} — never emitted; the text scrubbed of e-mail addresses and Finnish
telephone numbers («p. 040 183 6260 tai saara.saalo@eezy.fi» on the Personnel ads).**

Measured 2026-09-14 04:0x–04:1x UTC by the declared client, the guard on the exact path: the
RSS 99 204 B / 338 items / 10 ads; `/fi` 43 994 B; `_app` 514 225 B; the query `to: 20` →
`available` 236, 20 jobs; `to: 300` → 236 jobs, 236 distinct; the ads 82 481 B (Personnel)
and a Core ad with its `recruitmentPerson`.
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

HOST = "tyopaikat.eezy.fi"
LIST = f"https://{HOST}/fi"
API = "https://api.eezy.fi/api"
PAGE = 20   # the page's ITEMS_TO_FETCH

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+358[\s ]?|0)(?:\d[\s -]?){6,10}\d(?!\d)")
AD_RE = re.compile(r"^/(fi|en|se)/tyopaikat/([A-Za-z0-9_\-]{4,40})/?$")
APP_RE = re.compile(r'src="(/_next/static/chunks/pages/_app-[a-f0-9]+\.js)"')
QUERY_RE = re.compile(r'\["(\\n\s+query\((?:(?!"\]\);).)*?elasticJobs\((?:(?!"\]\);).)*?)"\]\);', re.S)
NEXT_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)

_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[eezy] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, data=None, headers=None):
    """GET, or — with `data` — the page's own POST; the guard on the exact path either way, 2 s per host."""
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    if host not in _PACES:
        _PACES[host] = Pace(host, own=2.0)   # no Crawl-delay written anywhere; 2 s is ours
    _PACES[host].wait()
    h = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9", "Accept-Language": "fi"}
    h.update(headers or {})
    req = urllib.request.Request(wire_url(url), data=data, method="POST" if data is not None else "GET", headers=h)
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
    markup = re.sub(r"<!--.*?-->", "", markup or "", flags=re.S)
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup)
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t ​]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    s = PHONE_RE.sub("[telephone withheld]", s)
    # a line that carried a telephone or an e-mail is the contact line — it names the consultant too, so the whole line goes
    s = "\n".join("[contact withheld]" if "withheld]" in line else line for line in s.split("\n"))
    return s.strip() or None


def app_url(page_body):
    m = APP_RE.search(page_body or "")
    return f"https://{HOST}{m.group(1)}" if m else None


def list_query(chunk_body):
    """The `elasticJobs` query the page's own script carries — its text, as the page sends it — or `None`."""
    m = QUERY_RE.search(chunk_body or "")
    if not m:
        return None
    try:
        return json.loads('"' + m.group(1) + '"')
    except ValueError:
        return None


def elastic_jobs(query, to):
    body = json.dumps({"query": query, "variables": {"locations": [], "from": 0, "to": to}}).encode("utf-8")
    code, raw = request(API, data=body, headers={"Accept": "*/*", "Content-Type": "application/json"})
    if code != 200:
        die(f"{API} (the page's elasticJobs query): HTTP {code}", EXIT_PARTIAL)
    try:
        d = json.loads(raw)
    except ValueError:
        die(f"{API}: 200 and not JSON — the API changed shape", EXIT_PARTIAL)
    e = ((d.get("data") or {}).get("elasticJobs") if isinstance(d, dict) else None) or {}
    if not isinstance(e.get("pageResults"), dict) or "jobs" not in e:
        die(f"{API}: 200 without `elasticJobs.pageResults` — the query changed shape ({json.dumps(d.get('errors'))[:200] if isinstance(d, dict) and d.get('errors') else 'no error named'})", EXIT_PARTIAL)
    return e


def company(o):
    """The client's name as the site shows it — withheld when the site hides it."""
    return None if o.get("hideCustomer") else ((o.get("customer") or "").strip() or None)


def row(j):
    return {
        "source": "eezy", "country": "FI", "ledger_id": f"eezy:{j.get('id')}", "id": j.get("id"),
        "url": f"https://{HOST}/fi/tyopaikat/{j.get('id')}",
        "title": (j.get("name") or "").strip() or None,
        "company": company(j), "company_hidden": bool(j.get("hideCustomer")), "agency": "Eezy",
        "fields": [f for f in (j.get("fieldOfWorks") or []) if f] or None,
        "places": [l.get("name") for l in (j.get("workLocations") or []) if isinstance(l, dict) and l.get("name")] or None,
        "feed": j.get("source"),   # Core (the group's own ATS) or Personnel (Talentadore)
        "language": "fi", "contacts_withheld": True,
    }


def cmd_list(a):
    code, page = request(LIST)
    if code != 200:
        die(f"{LIST}: HTTP {code}", EXIT_PARTIAL)
    au = app_url(page)
    if not au:
        die(f"{LIST}: 200 and no app script named in the page — the template changed", EXIT_PARTIAL)
    code, chunk = request(au)
    if code != 200:
        die(f"{au}: HTTP {code}", EXIT_PARTIAL)
    query = list_query(chunk)
    if not query:
        die(f"{au}: 200 and no `elasticJobs` query in the page's script — the page changed how it lists; not an empty market", EXIT_PARTIAL)
    first = elastic_jobs(query, PAGE)   # as the page's first load asks
    total = first["pageResults"].get("available")
    if not isinstance(total, int):
        die(f"{API}: the answer states no `available` — not an empty market", EXIT_PARTIAL)
    want = min(total, a.limit) if a.limit else total
    e = first if want <= len(first.get("jobs") or []) else elastic_jobs(query, want)
    rows, seen = [], set()
    for j in (e.get("jobs") or []):
        if not isinstance(j, dict) or not j.get("id") or j["id"] in seen:
            continue
        seen.add(j["id"])
        rows.append(row(j))
        if a.limit and len(rows) >= a.limit:
            break
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    n = len(rows)
    if a.limit and a.limit < total:
        note(f"{th(n)} emitted of the {th(total)} the site states (the page's own elasticJobs query, `available`) — walked by request (--limit), not a shortfall.")
    else:
        verdict = "equal" if n == total else (f"{th(total - n)} short" if n < total else f"{th(n - total)} more emitted")
        note(f"{th(n)} emitted, the site states {th(total)} (the page's own elasticJobs query, `available`) — {verdict}.")
    note(f"the list is the page's own query replayed with its own variables, its text read from the page's script this run; the client's name withheld on {th(sum(1 for r in rows if r['company_hidden']))} where the site hides it; the recruiter on the ad is never emitted.")


def advert_of(body):
    m = NEXT_RE.search(body or "")
    if not m:
        return None
    try:
        d = json.loads(m.group(1))
    except ValueError:
        return None
    ad = ((d.get("props") or {}).get("pageProps") or {}).get("jobAdvert")
    return ad if isinstance(ad, dict) and ad.get("id") else None


def record(ad, url):
    desc = ad.get("description") or ad.get("descriptionPlain") or ""
    return {
        "source": "eezy", "country": "FI", "ledger_id": f"eezy:{ad['id']}", "id": ad["id"], "url": url,
        "title": (ad.get("name") or "").strip() or None, "work_title": (ad.get("worktitle") or "").strip() or None,
        "company": company(ad), "company_hidden": bool(ad.get("hideCustomer")), "company_text": scrub(text(ad.get("customerDescription") or "")), "agency": "Eezy",
        "employment_type": ad.get("typeOfWorkRelationship") or None, "work_mode": ad.get("workRelationshipMode") or None,
        "place": ad.get("locationCity") or None, "address": ad.get("locationAddress") or None,
        "places": [l.get("name") for l in (ad.get("workLocations") or []) if isinstance(l, dict) and l.get("name")] or None,
        "fields": [f for f in (ad.get("fieldOfWorks") or []) if f] or None,
        "posted": (ad.get("startTime") or "")[:10] or None, "valid_through": (ad.get("endTime") or "")[:10] or None,
        "feed": ad.get("source"), "deleted": bool(ad.get("isDeleted")),
        "apply_host": urllib.parse.urlsplit(ad.get("applyLink") or "").netloc or None,   # the ATS the site sends to — never followed
        "description": scrub(text(desc)),
        # `recruitmentPerson` — first and last name, photo, e-mail, telephone — is on the ad and is never emitted
        "language": "fi", "contacts_withheld": True,
    }


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc != HOST or not m:
        die(f"{a.url}: not a job address (https://{HOST}/fi/tyopaikat/<id>)")
    url = f"https://{HOST}/{m.group(1)}/tyopaikat/{m.group(2)}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    ad = advert_of(body)
    if ad is None:
        die(f"{url}: 200 without `jobAdvert` in the page's state — the template changed, or the ad is gone behind a 200", EXIT_PARTIAL)
    rec = record(ad, url)
    print(json.dumps(rec, ensure_ascii=False))
    note(f"{url}: read from the page's own `jobAdvert`; the recruiter withheld; the text scrubbed; the application ({rec['apply_host'] or 'no link'}) never followed.")


def main():
    p = argparse.ArgumentParser(description="Eezy — the page's own list query replayed as the page makes it, its count beside every walk; the recruiter never emitted. Issue #379.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the site's list — 3 requests")
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
