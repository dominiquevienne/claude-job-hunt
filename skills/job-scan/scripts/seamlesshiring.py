#!/usr/bin/env python3
"""SeamlessHiring (SeamlessHR's ATS, Nigeria and Southern Africa), one tenant at a time: the careers portal `<tenant>.seamlesshiring.com` is a login shell, but its own job API answers the declared client without a session — `GET /v2/jobs/job-list?page=N` (Laravel pagination: `total` stated, twenty a page) and `GET /v2/jobs/find/<id>`; the public advert is `/job/view/<id>`. Issue #494.

  seamlesshiring.py jobs --tenant <name | host | url> [--country-code CC]
  seamlesshiring.py ad --url https://<tenant>.seamlesshiring.com/job/view/<id> [--country-code CC]

THE HOSTS. The issue named `<entreprise>.seamlesshr.com/careers`; the product's
careers portals live on `<tenant>.seamlesshiring.com` (coronationgroup,
letshego, goldenoiltd, mgas, seamlesshr itself — found 2026-09-21). One
host per run — the tenant's; every other host refused before the gate (7).
Rules (`<tenant>.seamlesshiring.com/robots.txt`, 2026-09-21): `User-agent: *
/ Disallow:` — nothing refused, no Crawl-delay; 2 s between requests are
ours.

THE ROUTE, READ IN THE PORTAL'S OWN BUNDLE (`cdn.seamlesshiring.com/js/app.js`,
`JobModel.viewJobsListing` → `$http.get("/v2/jobs/job-list", {params})`,
`getJob` → `v2/jobs/find/<id>`, axios base `/`), MEASURED 2026-09-21 07:49–07:50
UTC, the declared client, no cookie, no token: `job-list` answers
`{status_code: 200, data: {jobs: {current_page, data: [...], last_page,
per_page: 20, total}, subsidiaries: [...]}}` — **Letshego 15 (total 15),
Golden Oil 6 (6), Coronation 0 (0), M-Gas 0 (0)**; `find/<id>` the same
record; an id the tenant does not have `{"message": {"message": "Job not
found", "status_code": 404}}` (exit 3); an unknown tenant is a name that does
not resolve (exit 3, «not a tenant»). The record: `title`, `summary`,
`details` (HTML), `experience` (HTML), `location` / `city` /
`location_details.name`, `country_id` (a number — the API names no country:
`--country-code` stamps it), `post_date`, `expiry_date`, `closing_date`,
`job_type`, `work_style`, `position`, `job_level`, `qualification`,
`minimum_remuneration` / `maximum_remuneration` / `currency_id` shown only
when `show_remuneration` is 1, `is_private`, `status`, `company.name`,
`specializations[].name`. The public advert `/job/view/<id>` (200, 71 KB,
the title in `<title>`) is the address emitted; the SPA's `/jobs/view/<id>`
redirects there.

WITHHELD — and the API gives far more than the page shows: the `company`
block carries the recruiter's telephone, e-mail, street address and the
tenant's own API key; `users` the recruiters' names and e-mails; `fields`
and `form_structure` the application form; `scoring_criteria`,
`auto_screening_json`, `sentiment_analysis` the employer's screening.
**None of it is emitted** — the record keeps the advert and its dates; the
texts are scrubbed of e-mail addresses and telephones; the logo never
emitted; `contacts_withheld` on every record.
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

BOARD = "seamlesshiring"
DOMAIN = "seamlesshiring.com"
VENDOR = {"seamlesshiring.com", "www.seamlesshiring.com", "cdn.seamlesshiring.com", "seamlesshr.com", "www.seamlesshr.com"}
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE = 20
MAX_PAGES = 500
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
_HOST = {"name": None}
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[seamlesshiring] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def tenant_of(s):
    """The tenant's host from a name, a host or an address — the vendor's own hosts are not tenants."""
    s = (s or "").strip()
    if "://" in s or "/" in s:
        s = urllib.parse.urlsplit(s if "://" in s else "https://" + s).netloc
    s = s.lower().rstrip(".")
    if not s:
        die("--tenant: empty")
    host = s if s.endswith("." + DOMAIN) else f"{s}.{DOMAIN}"
    if host in VENDOR or host.count(".") != 2 or not re.fullmatch(r"[a-z0-9-]+\." + re.escape(DOMAIN), host):
        die(f"{s!r}: not a tenant of {DOMAIN} (the vendor's own hosts are not tenants)")
    return host


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    """(status, body) — the run's tenant only, the guard first, 2 s apart."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc.lower() != _HOST["name"]:
        die(f"{url}: not the run's tenant {_HOST['name']} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(parts.netloc, Pace(parts.netloc, own=2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "application/json, text/html", "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        try:
            return e.code, decode_body(e.read(), e.headers)[0]
        except Exception:
            return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        if "nodename nor servname" in str(e) or "Name or service not known" in str(e) or "getaddrinfo" in str(e):
            die(f"{url}: the name does not resolve — not a tenant of {DOMAIN}.", EXIT_GONE)
        die(f"{url}: {type(e).__name__}: {e}")


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


def status_of(st, url, body=""):
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)


def parse_json(body, url):
    try:
        d = json.loads(body or "")
    except ValueError:
        die(f"{url}: not JSON — the tenant's API did not answer (a login shell, or not a tenant).", EXIT_PARTIAL)
    return d


def none_if_blank(v):
    if v is None:
        return None
    v = str(v).strip()
    return v or None


def row(j, host, cc):
    jid = str(j.get("id"))
    loc = j.get("location_details") if isinstance(j.get("location_details"), dict) else {}
    place = none_if_blank(j.get("location")) or none_if_blank(j.get("city")) or none_if_blank(loc.get("name"))
    company = j.get("company") if isinstance(j.get("company"), dict) else {}
    specs = [s.get("name") for s in (j.get("specializations") or []) if isinstance(s, dict) and s.get("name")]
    show_pay = str(j.get("show_remuneration") or "0") == "1"
    rec = {"source": BOARD, "country": cc, "ledger_id": f"{BOARD}:{host}:{jid}", "id": jid,
           "url": f"https://{host}/job/view/{jid}",
           "title": none_if_blank(j.get("title")), "company": none_if_blank(company.get("name")),
           "place": place, "country_id": j.get("country_id"),
           "job_type": none_if_blank(j.get("job_type")), "work_style": none_if_blank(j.get("work_style")),
           "position": none_if_blank(j.get("position")), "job_level": none_if_blank(j.get("job_level")),
           "qualification": scrub(text(j.get("qualification"))),
           "salary_min": none_if_blank(j.get("minimum_remuneration")) if show_pay else None,
           "salary_max": none_if_blank(j.get("maximum_remuneration")) if show_pay else None,
           "currency_id": j.get("currency_id") if show_pay else None,
           "posted": none_if_blank(j.get("post_date")), "expires": none_if_blank(j.get("expiry_date")),
           "closes": (none_if_blank(j.get("closing_date")) or "")[:10] or None,
           "status": none_if_blank(j.get("status")), "private": str(j.get("is_private") or "0") == "1",
           "specializations": specs or None,
           "summary": scrub(text(j.get("summary"))),
           "description": (scrub(text(j.get("details"))) or "")[:20000] or None,
           "experience": (scrub(text(j.get("experience"))) or "")[:5000] or None,
           "contacts_withheld": True}
    return rec


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    _HOST["name"] = host
    cc = (a.country_code or "").upper() or None
    seen, out, stated, page = set(), [], None, 1
    while page <= MAX_PAGES:
        url = f"https://{host}/v2/jobs/job-list" + (f"?page={page}" if page > 1 else "")
        st, body = request(url)
        if st == 404 and page == 1:
            die(f"{url}: HTTP 404 — not a tenant of {DOMAIN}, or the API moved.", EXIT_GONE)
        status_of(st, url)
        d = parse_json(body, url)
        jobs = (d.get("data") or {}).get("jobs") if isinstance(d.get("data"), dict) else None
        if not isinstance(jobs, dict) or "data" not in jobs:
            die(f"{url}: no data.jobs in the answer ({str(d)[:120]!r}) — not a tenant, or the API changed shape.", EXIT_PARTIAL)
        if stated is None:
            stated = jobs.get("total")
            stated = int(stated) if isinstance(stated, (int, str)) and str(stated).isdigit() else None
        new = 0
        for j in jobs.get("data") or []:
            if not isinstance(j, dict) or j.get("id") is None or str(j["id"]) in seen:
                continue
            seen.add(str(j["id"]))
            out.append(row(j, host, cc))
            new += 1
        last = jobs.get("last_page")
        last = int(last) if isinstance(last, (int, str)) and str(last).isdigit() else page
        if page > 1 and new == 0:
            note(f"page {page} of {last}: only repeats — stopped.")
            break
        if page >= last or not jobs.get("next_page_url"):
            break
        page += 1
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    if cc:
        note(f"country {cc} stamped from --country-code — the API names no country (country_id only).")
    if stated is None:
        note(f"{th(n)} emitted from {host} — the API stated no total.")
    elif stated == n:
        note(f"{th(n)} emitted from {host} — the site states {th(stated)}: equal.")
    else:
        note(f"{th(n)} emitted from {host} — the site states {th(stated)}: {th(abs(stated - n))} " + ("short" if stated > n else "more emitted than stated") + ".")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = re.fullmatch(r"/job/view/(\d+)/?", parts.path or "")
    host = parts.netloc.lower()
    if not m or not re.fullmatch(r"[a-z0-9-]+\." + re.escape(DOMAIN), host) or host in VENDOR:
        die(f"{a.url!r}: not a SeamlessHiring advert address (https://<tenant>.{DOMAIN}/job/view/<id>)")
    _HOST["name"] = host
    jid = m.group(1)
    url = f"https://{host}/v2/jobs/find/{jid}"
    st, body = request(url)
    if st == 404:
        die(f"https://{host}/job/view/{jid}: the tenant answers «Job not found» — gone, or never this tenant's.", EXIT_GONE)
    status_of(st, url)
    d = parse_json(body, url)
    j = d.get("data") if isinstance(d.get("data"), dict) else None
    if not j or j.get("id") is None:
        die(f"{url}: no job record in the answer ({str(d)[:120]!r}).", EXIT_PARTIAL)
    print(json.dumps(row(j, host, (a.country_code or "").upper() or None), ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="SeamlessHiring (SeamlessHR's ATS) — one tenant's job API walked to its stated total; the advert record; the recruiters' contacts, the form and the screening never emitted. Issue #494.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="/v2/jobs/job-list?page=N to last_page; «N emitted — the site states M: equal/short»")
    s.add_argument("--tenant", required=True, help="the tenant: a name (letshego), a host or an address on it")
    s.add_argument("--country-code", help="ISO-3166 alpha-2 to stamp on every row (the API names no country)")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its public address /job/view/<id>")
    d.add_argument("--url", required=True)
    d.add_argument("--country-code")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
