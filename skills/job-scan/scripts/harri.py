#!/usr/bin/env python3
"""Harri — a hospitality ATS, one tenant at a time: the tenant's career portal on `harri.com/<slug>` is an Angular app that asks the gateway for the brand behind the slug and then for its jobs — the adapter replays those calls with the page's own parameters, prints the brand's stated `active_jobs_count` beside the search's `hits` and the emitted count, and reads an ad from the JobPosting its page carries. Issue #457.

  harri.py jobs --tenant HHospitality [--country-code US]     the tenant's jobs (3 requests: the slug, the brand, the search — a 4th when the list is longer than a page)
  harri.py jobs --tenant https://harri.com/HHospitality
  harri.py ad --url https://harri.com/HHILTT/job/2757301-server-assistant-earn-up-to-1-000-wk-

WHAT IT IS. Harri is the hiring and workforce software of restaurants, hotels and bars (Hogsalt,
Harri's own careers, UK pub and hotel groups). **One adapter covers every employer that uses it, in
every country; the user names the tenant** as the slug the career-portal URL spells
(`harri.com/HHospitality` → `HHospitality`), as for Recruitee or SparkHire.

THE RULES. `harri.com/robots.txt` is a `*` group refusing `/employee-records` and a few tenant
paths (the guard is taken per path, so a refused tenant is refused here too); no Crawl-delay, 2 s
is ours. `gateway.harri.com` answers its rules path with 403 — an absence of rules since #283,
`certain: False`, the transport decides, and it serves.

THE PAGE, THE CALLS. `harri.com/<slug>` (200, 58 KB) is a shell with `data-brand-id` and no job in
its markup; the app calls, in this order — read in a connected tab on 2026-09-19 and replayed by
the declared client the same day:

  GET  https://gateway.harri.com/core/api/v1/profile/slug/<slug>                    → data.id, career_portal_enabled
  GET  https://gateway.harri.com/core/api/v2/career_portal/brands/<id>/basic_info    → name, type, location_count, active_jobs_count (THE STATED COUNT)
  POST https://gateway.harri.com/core/api/v1/harri_search/search_jobs                (headers FORCE-CSRF: true, X-REFERRER-PAGE: the portal URL)
       {"size": 30, "source": "web", "brand_level_ids": [<id>], "search_phrase": "", "sort": ["publish_date"], "sort_type": "desc", "flow": "CAREER_PORTAL"}
       → data.hits, data.results[] (id, brand{id, name, slug}, position{name}, aliasPosition, locations[{city, state, country, country_code, formatted_address}], publishTime, createdTime, compensation{name, plus_tips…}, brand_media)

No `from` / `page` / `offset` parameter changes the page (measured on an 11-job tenant: each
answers page 1); **`size` is honoured up to 500** — so a list longer than 30 is asked again with
`size = hits` (capped at 500, and the cap is printed when it bites). A tenant with no job answers
`hits: 0` — printed as «0 jobs», not an error. The ad `harri.com/<brand slug>/job/<id>-<slug>`
(200, 76 KB) carries a schema.org JobPosting: title, description (HTML), datePosted,
hiringOrganization, jobLocation, employmentType, baseSalary.

Measured 2026-09-19 14:1x–14:3x UTC: Hogsalt (`HHospitality`, GP-1, 29 locations) — basic_info
`active_jobs_count` 6, search `hits` 6, 6 emitted, equal; Harri's own `careers_us` 11 / 11;
`Harri-Restaurant`, `The-Restaurant-Group`, `crg-jobs`, `radissoncareersuk`, `careers_uk` — 0 / 0.

**WITHHELD:** the descriptions scrubbed of e-mail addresses and telephone numbers; brand media and
image ids not emitted; `contacts_withheld` on every record; the application (Harri's own form and
«Multiple apply») never touched.
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
from _ldjson import one as ld_one, postings as ld_postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

PAGE_HOST = "harri.com"
API_HOST = "gateway.harri.com"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE_SIZE, SIZE_CAP = 30, 500

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$])\+?\d[\d\s().\-]{7,}\d(?!\w)")   # an international shape: 9+ digits with separators — a «$1,000/wk» has too few digits
SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-&.%]*$")
AD_RE = re.compile(r"^/([^/]+)/job/(\d+)(?:-[^/]*)?/?$")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[harri] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, accept="text/html,application/xhtml+xml", headers=None, data=None):
    parts = urllib.parse.urlsplit(url)
    if parts.netloc not in (PAGE_HOST, API_HOST):
        die(f"{url}: not a Harri host — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(parts.netloc, Pace(parts.netloc, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    h = {"User-Agent": UA, "Accept": accept, "Accept-Language": "en"}
    h.update(headers or {})
    req = urllib.request.Request(wire_url(url), headers=h, data=data, method="POST" if data is not None else "GET")
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
    """`<slug>` or the portal URL → slug."""
    s = arg.strip()
    if "://" in s or s.startswith(PAGE_HOST):
        parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
        m = re.match(r"^/([^/]+)/?$", parts.path)
        if parts.netloc not in (PAGE_HOST, "www." + PAGE_HOST) or not m or m.group(1) in ("jobs", "about-us"):
            die(f"{arg}: not a Harri career-portal address (https://{PAGE_HOST}/<slug>)")
        return m.group(1)
    if not SLUG_RE.match(s) or "/" in s or s in ("jobs", "about-us"):
        die(f"{arg}: a tenant is written as the slug the portal URL spells — HHospitality")
    return s


def api_json(url, data=None, headers=None, what="the gateway"):
    code, body = request(url, accept="application/json", headers=headers, data=data)
    if code == 404:
        die(f"{what}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{what}: HTTP {code}", EXIT_PARTIAL)
    try:
        d = json.loads(body)
    except ValueError:
        die(f"{what}: 200 and not JSON — the route changed", EXIT_PARTIAL)
    if not isinstance(d, dict) or "data" not in d:
        die(f"{what}: 200 without a data field — the route changed", EXIT_PARTIAL)
    return d["data"]


def brand_of(slug):
    d = api_json(f"https://{API_HOST}/core/api/v1/profile/slug/{urllib.parse.quote(slug, safe='')}", what=f"the slug {slug}")
    if not isinstance(d, dict) or not isinstance(d.get("id"), int):
        die(f"the slug {slug}: no brand id behind it — not a tenant", EXIT_GONE)
    if d.get("is_archived"):
        note(f"{slug}: the brand is archived")
    info = api_json(f"https://{API_HOST}/core/api/v2/career_portal/brands/{d['id']}/basic_info", what="basic_info")
    return d["id"], (info if isinstance(info, dict) else {})


def search(slug, brand_id, size):
    body = {"size": size, "source": "web", "brand_level_ids": [brand_id], "search_phrase": "", "sort": ["publish_date"], "sort_type": "desc", "flow": "CAREER_PORTAL"}
    d = api_json(f"https://{API_HOST}/core/api/v1/harri_search/search_jobs", data=json.dumps(body).encode("utf-8"),
                 headers={"Content-Type": "application/json", "FORCE-CSRF": "true", "X-REFERRER-PAGE": f"https://{PAGE_HOST}/{slug}"}, what="search_jobs")
    if not isinstance(d, dict) or not isinstance(d.get("results"), list):
        die("search_jobs: 200 without data.results — the route changed", EXIT_PARTIAL)
    return d


def ad_url(brand_slug, job_id, title):
    s = re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-")
    return f"https://{PAGE_HOST}/{brand_slug}/job/{job_id}-{s}" if s else f"https://{PAGE_HOST}/{brand_slug}/job/{job_id}"


def record(r, slug):
    b = r.get("brand") or {}
    locs = [l for l in (r.get("locations") or []) if isinstance(l, dict)]
    first = locs[0] if locs else {}
    comp = r.get("compensation") or {}
    title = (r.get("aliasPosition") or (r.get("position") or {}).get("name") or "").strip() or None
    return {
        "source": "harri", "tenant": slug, "country": first.get("country_code") or None,
        "countries": sorted({l.get("country_code") for l in locs if l.get("country_code")}) or None,
        "ledger_id": f"harri:{r.get('id')}", "id": r.get("id"),
        "url": ad_url(b.get("slug") or slug, r.get("id"), title),
        "title": title, "position": (r.get("position") or {}).get("name") or None, "company": b.get("name") or None,
        "place": first.get("city") or None, "region": first.get("state") or None, "location": first.get("formatted_address") or None,
        "posted": (r.get("publishTime") or "")[:10] or None,
        "compensation": comp.get("name") or None, "plus_tips": bool(comp.get("plus_tips")) if comp else None,
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    slug = tenant_of(a.tenant)
    brand_id, info = brand_of(slug)
    stated = info.get("active_jobs_count") if isinstance(info.get("active_jobs_count"), int) else None
    d = search(slug, brand_id, PAGE_SIZE)
    hits = d.get("hits") if isinstance(d.get("hits"), int) else None
    capped = False
    if isinstance(hits, int) and hits > PAGE_SIZE:
        d = search(slug, brand_id, min(hits, SIZE_CAP))   # no offset parameter moves the page; `size` is honoured to 500
        capped = hits > SIZE_CAP
    rows, seen = [], set()
    for r in d["results"]:
        if isinstance(r, dict) and r.get("id") not in seen:
            seen.add(r.get("id"))
            rows.append(record(r, slug))
    if a.country_code:
        rows = [x for x in rows if (x["country"] or "").upper() == a.country_code.upper()]
    for x in rows:
        print(json.dumps(x, ensure_ascii=False))
    name = info.get("name") or slug
    where = f" for {a.country_code.upper()}" if a.country_code else ""
    if hits == 0:
        note(f"{name} ({slug}): 0 jobs — the search answered hits 0 and basic_info states {stated!r}; the tenant publishes none today, not an error.")
    elif capped:
        note(f"{th(len(rows))} emitted{where} — the search states {th(hits)} hits and basic_info {th(stated) if stated is not None else 'no count'}; the API's page cap is {SIZE_CAP}: {th(hits - SIZE_CAP)} beyond it are not walked.")
    elif a.country_code:
        note(f"{th(len(rows))} emitted{where} of the {th(len(seen))} the search lists — the search states {th(hits) if hits is not None else 'no'} hits, basic_info {th(stated) if stated is not None else 'no count'}.")
    else:
        parts = [f"{th(len(rows))} emitted", f"the search states {th(hits) if hits is not None else 'no'} hits", f"basic_info states {th(stated) if stated is not None else 'no count'}"]
        verdict = "equal" if hits == len(rows) == (stated if stated is not None else hits) else (f"{th(abs((stated if stated is not None else hits) - len(rows)))} {'short' if len(rows) < (stated if stated is not None else hits) else 'over'}")
        note(" — ".join(parts) + f": {verdict}.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url.strip())
    m = AD_RE.match(parts.path)
    if parts.netloc not in (PAGE_HOST, "www." + PAGE_HOST) or not m:
        die(f"{a.url}: not a Harri job address (https://{PAGE_HOST}/<brand>/job/<id>-<slug>)")
    brand_slug, job_id = m.group(1), int(m.group(2))
    url = f"https://{PAGE_HOST}{parts.path}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — no such job", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    p = next((x for x in ld_postings(body) if isinstance(x, dict)), None)
    if not p:
        die(f"{url}: 200 without a JobPosting — the page changed", EXIT_PARTIAL)
    loc = ld_one(p.get("jobLocation"))
    addr = ld_one(loc.get("address")) if loc else {}
    org = ld_one(p.get("hiringOrganization"))
    sal = ld_one(p.get("baseSalary"))
    val = ld_one(sal.get("value")) if sal else {}
    out = {
        "source": "harri", "tenant": brand_slug, "country": addr.get("addressCountry") or None,
        "ledger_id": f"harri:{job_id}", "id": job_id, "url": url,
        "title": (p.get("title") or "").strip() or None, "company": org.get("name") or None,
        "place": addr.get("addressLocality") or None, "region": addr.get("addressRegion") or None,
        "posted": (p.get("datePosted") or "") or None, "employment_type": p.get("employmentType") or None,
        "salary": {"currency": sal.get("currency"), "min": val.get("minValue"), "max": val.get("maxValue"), "unit": val.get("unitText")} if sal else None,
        "description": scrub(text(p.get("description"))),
        "contacts_withheld": True,
    }
    print(json.dumps(out, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Harri — one tenant's jobs, the calls its portal makes")
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the tenant's jobs")
    j.add_argument("--tenant", required=True, help="the portal slug (HHospitality) or the portal URL")
    j.add_argument("--country-code", help="ISO2 — filters on the job's country_code")
    j.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one job")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
