#!/usr/bin/env python3
"""StaffPoint (`www.staffpoint.fi`) — the Finnish staffing group's own board, a Next.js site whose job list is filled by the page's own server action (`fetchJobs`) and never rendered on the server: the adapter replays that call exactly as the page makes it — the action's id read from the page's own script on every run — and prints emitted against the `totalCount` the call states; the ad page's JobPosting read for the rest; **`applicationContact` — the consultant's e-mail — on every ad and never emitted**. Issue #378.

  staffpoint.py list [--limit N] [--lang fi|en]    the site's list: 3 requests (the page, its script, the call) — 153 rows on 2026-09-14
  staffpoint.py ad --url <https://www.staffpoint.fi/tyopaikat/<slug>-<id>>

THE RULES (823 B): `*` reads `Disallow: /search` only; SEO crawlers and scanners named and
refused; `Sitemap: /sitemap.xml`. No Crawl-delay; 2 s is ours. `/search` is never asked —
the site's search lives at `/haku` and is a site-wide text search, not the job list.

THE LIST IS NOT ON THE SERVER, AND NOT IN THE SITEMAP. `/sitemap.xml` (648 rows) names the
site's pages, 323 articles and the English twins — not one job. `/tyopaikat` (200, ~383 KB) is a
React Server Components page whose flight data carries only the 15 «open applications»
(`openApplications.jobs`, `totalCount` 15) — the standing invitations, not the advertisements;
its job list starts as `{}` and is filled on the client by `fetchJobs`, a Next.js server action:
a POST to `/tyopaikat` itself with the header `Next-Action: <id>` and the body
`[{"sortBy":"startDate","sortOrder":"desc","openApplications":"false","size":"<9×page>"}]`,
answered as `text/x-component` whose line `1:` is `{"jobs":[…],"totalCount":N}`. The id is
bound to the build — it changes at every deploy — so it is read on every run from the page's
own `app/[locale]/jobs/page-*.js`, exactly as the browser does. **This is the page's own call
to its own address, replayed with the page's own parameters; nothing is guessed and no other
host is asked.** The pager is «load more» (`size` grows by 9), so the whole list is one call
with `size` = `totalCount`.

THE ROW. `id` (4 chars), `name`, `validFrom`/`validUntil` (dd.mm.yyyy, or «Jatkuva haku» —
continuous), `isNew`, `isExpiring`, `employmentType` («Määräaikainen», «Toistaiseksi voimassa
oleva», «Keikkatyö», «Permanent», «Temporary»), `locations[]` (region → cities), `fields[]`,
`language`, `jobAdBaseUrl`. THE AD. `/tyopaikat/<slug>-<id>` (200, ~290 KB) carries a
JobPosting JSON-LD (twice, identical): `identifier`, `title`, `description` (plain text),
`datePosted`, `validThrough`, `employerOverview` (the employment type), `industry`,
`occupationalCategory`, `jobLocation[]` (region as `name`, town as `addressLocality`),
`hiringOrganization` (the client when named, «StaffPoint Oy» otherwise), `baseSalary`
min/max when the ad states one (EUR, no unit written — the text says «€/h»), and
**`applicationContact.email` — a named consultant on most ads — never emitted; the
description scrubbed of e-mail addresses and Finnish telephone numbers; the application
(`my.staffpoint.fi`, a login) never touched.**

Measured 2026-09-14 03:5x–04:0x UTC by the declared client, the guard on the exact path:
robots 823 B; `/sitemap.xml` 648 rows, 0 jobs; `/tyopaikat` 383 421 B, 15 open applications;
the call: `totalCount` 153 in four readings (9, 153 and 300 asked — 9, 153, 153 returned) and
**176 in one reading between them, at 06:00 local — the count moved, or a variant was served;
the adapter prints what it reads each run**; the ad 290 274 B with its JobPosting.
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
from _ldjson import one, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "www.staffpoint.fi"
LIST = f"https://{HOST}/tyopaikat"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+358[\s ]?|0)(?:\d[\s -]?){6,10}\d(?!\d)")
AD_RE = re.compile(r"^/tyopaikat/([a-z0-9\-]+)-([A-Za-z0-9]{4,8})/?$")
CHUNK_RE = re.compile(r"static/chunks/app/%5Blocale%5D/jobs/page-[a-f0-9]+\.js")
ACTION_RE = re.compile(r'createServerReference\)\("([0-9a-f]+)",[^)]*?"fetchJobs"\)')
FLIGHT_RE = re.compile(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', re.S)

_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written; 2 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[staffpoint] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, data=None, headers=None):
    """GET, or — with `data` — the page's own POST; the guard on the exact path either way."""
    if urllib.parse.urlsplit(url).path.startswith("/search"):
        die(f"{url}: /search is refused in writing — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
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


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def fi_date(s):
    """«11.09.2026» → 2026-09-11; «Jatkuva haku» (continuous) and anything else stay as printed."""
    m = re.match(r"^\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s*$", s or "")
    return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}" if m else ((s or "").strip() or None)


def action_id(page_body, chunk_body):
    """The `fetchJobs` action id the page's own script carries — `None` when the script is not named or does not carry it."""
    m = ACTION_RE.search(chunk_body or "")
    return m.group(1) if m else None


def chunk_url(page_body):
    m = CHUNK_RE.search(page_body or "")
    return f"https://{HOST}/_next/{m.group(0)}" if m else None


def parse_component(body):
    """The `{"jobs": …, "totalCount": …}` line of a text/x-component answer — `None` when absent."""
    for line in (body or "").splitlines():
        if line.startswith("1:"):
            try:
                d = json.loads(line[2:])
            except ValueError:
                return None
            return d if isinstance(d, dict) and "jobs" in d else None
    return None


def fetch_jobs(aid, size, lang=None):
    params = {"sortBy": "startDate", "sortOrder": "desc", "openApplications": "false", "size": str(size)}
    if lang and lang != "fi":
        params["language"] = lang   # the page adds it only off the default locale
    body = json.dumps([params]).encode("utf-8")
    code, text = request(LIST, data=body, headers={"Accept": "text/x-component", "Content-Type": "text/plain;charset=UTF-8", "Next-Action": aid})
    if code != 200:
        die(f"{LIST} (the page's fetchJobs call): HTTP {code}", EXIT_PARTIAL)
    d = parse_component(text)
    if d is None:
        die(f"{LIST} (the page's fetchJobs call): 200 without the jobs line — the action changed shape", EXIT_PARTIAL)
    return d


def row(j):
    locs = [l for l in (j.get("locations") or []) if isinstance(l, dict)]
    m = AD_RE.match(urllib.parse.urlsplit(j.get("jobAdBaseUrl") or "").path)
    return {
        "source": "staffpoint", "country": "FI", "ledger_id": f"staffpoint:{j.get('id')}", "id": j.get("id"),
        "url": j.get("jobAdBaseUrl") or None, "slug": m.group(1) if m else None,
        "title": (j.get("name") or "").strip() or None,
        "employment_type": (j.get("employmentType") or {}).get("name"),
        "regions": sorted({l.get("name") for l in locs if l.get("name")}) or None,
        "cities": sorted({c.get("name") for l in locs for c in (l.get("cities") or []) if isinstance(c, dict) and c.get("name")}) or None,
        "fields": [f.get("name") for f in (j.get("fields") or []) if isinstance(f, dict) and f.get("name")] or None,
        "posted": fi_date(j.get("validFrom")), "valid_through": fi_date(j.get("validUntil")), "continuous": (j.get("validUntil") or "").strip() == "Jatkuva haku",
        "is_new": j.get("isNew"), "is_expiring": j.get("isExpiring"),
        "language": (j.get("language") or "fi").lower(), "contacts_withheld": True,
    }


def cmd_list(a):
    code, page = request(LIST)
    if code != 200:
        die(f"{LIST}: HTTP {code}", EXIT_PARTIAL)
    cu = chunk_url(page)
    if not cu:
        die(f"{LIST}: 200 and no jobs script named in the page — the template changed", EXIT_PARTIAL)
    code, chunk = request(cu)
    if code != 200:
        die(f"{cu}: HTTP {code}", EXIT_PARTIAL)
    aid = action_id(page, chunk)
    if not aid:
        die(f"{cu}: 200 and no `fetchJobs` action in the page's script — the page changed how it lists; not an empty market", EXIT_PARTIAL)
    first = fetch_jobs(aid, 9, a.lang)   # as the page's first load asks
    total = first.get("totalCount")
    if not isinstance(total, int):
        die(f"{LIST}: the call states no `totalCount` — not an empty market", EXIT_PARTIAL)
    want = min(total, a.limit) if a.limit else total
    d = first if want <= len(first.get("jobs") or []) else fetch_jobs(aid, want, a.lang)
    rows, seen = [], set()
    for j in (d.get("jobs") or []):
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
        note(f"{th(n)} emitted of the {th(total)} the site states (the page's own fetchJobs call, `totalCount`) — walked by request (--limit), not a shortfall.")
    else:
        verdict = "equal" if n == total else (f"{th(total - n)} short" if n < total else f"{th(n - total)} more emitted")
        note(f"{th(n)} emitted, the site states {th(total)} (the page's own fetchJobs call, `totalCount`) — {verdict}.")
    note("the list is the page's own call replayed with its own parameters, its action id read from the page's script this run; the consultant's e-mail on the ad is never emitted.")


def record(body, tail, url):
    jp = (postings(body) or [None])[-1]
    if jp is None:
        return None
    locs = [one(l) for l in (jp.get("jobLocation") if isinstance(jp.get("jobLocation"), list) else [jp.get("jobLocation")]) if l]
    sal = one(one(jp.get("baseSalary")).get("value"))
    smin, smax = sal.get("minValue"), sal.get("maxValue")
    cur = (one(jp.get("baseSalary")).get("currency") or jp.get("salaryCurrency") or "").upper() or None
    org = one(jp.get("hiringOrganization")).get("name") or None
    ident = jp.get("identifier") if isinstance(jp.get("identifier"), str) else one(jp.get("identifier")).get("value")
    sid = ident or tail   # the site's id (the list's `id`) — the address tail is another code, kept beside it
    return {
        "source": "staffpoint", "country": "FI", "ledger_id": f"staffpoint:{sid}", "id": sid, "url": url, "url_id": tail,
        "title": htmlmod.unescape(jp.get("title") or jp.get("name") or "").strip() or None,
        "company": org, "employer_is_the_agency": org in (None, "StaffPoint Oy", "StaffPoint"), "agency": "StaffPoint",
        "employment_type": jp.get("employerOverview") or jp.get("employmentType"),
        "industry": jp.get("industry") if isinstance(jp.get("industry"), list) else ([jp.get("industry")] if jp.get("industry") else None),
        "regions": sorted({l.get("name") for l in locs if l.get("name")}) or None,
        "cities": sorted({one(l.get("address")).get("addressLocality") for l in locs if one(l.get("address")).get("addressLocality")}) or None,
        "salary_min": smin, "salary_max": smax, "salary_currency": cur if (smin is not None or smax is not None) else None, "salary_unit": None, "salary_unit_stated": False,   # the JSON-LD writes no unit; the text says «€/h» when it says
        "posted": (jp.get("datePosted") or "")[:10] or None, "valid_through": (jp.get("validThrough") or "")[:10] or None,
        "description": scrub(htmlmod.unescape(jp.get("description") or "").strip()),
        # `applicationContact.email` — a named consultant on most ads — is never emitted
        "contacts_withheld": True, "language": "fi",
    }


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc not in (HOST, "staffpoint.fi") or not m:
        die(f"{a.url}: not a job address (https://{HOST}/tyopaikat/<slug>-<id>)")
    url = f"https://{HOST}{parts.path.rstrip('/')}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    rec = record(body, m.group(2), url)
    if rec is None:
        die(f"{url}: 200 without a JobPosting — the template changed", EXIT_PARTIAL)
    print(json.dumps(rec, ensure_ascii=False))
    note(f"{url}: read from its JobPosting; the consultant's e-mail withheld; the description scrubbed; the application never touched.")


def main():
    p = argparse.ArgumentParser(description="StaffPoint — the page's own list call replayed as the page makes it, its count beside every walk; the consultant never emitted. Issue #378.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the site's list — 3 requests")
    l_.add_argument("--limit", type=int)
    l_.add_argument("--lang", choices=("fi", "en"), help="the page's language filter (fi is the default and sends none)")
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
