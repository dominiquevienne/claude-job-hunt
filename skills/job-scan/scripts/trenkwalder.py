#!/usr/bin/env python3
"""Trenkwalder Slovakia (`sk.trenkwalder.com`) — the staffing network's Slovak front, a Next.js site whose rules name `Claude-User` and open everything but `/api/*` at `Crawl-delay: 10`; the listing server-rendered with its search state — the site's own «Našli sme pre Vás N možných výsledkov» printed beside every walk — and the jobs sitemap for what the first page does not carry; **every record carries a `recruiter` object (name, e-mail, telephone) — never emitted**. Issue #349.

  trenkwalder.py list [--host sk] [--limit N]      /jobs (30 hits in the page's state) + the sitemap's other ids read from their pages, 10 s apart
  trenkwalder.py sitemap [--host sk]                /sitemap-jobs — every /jobs/<id>, with lastmod
  trenkwalder.py ad --url <https://sk.trenkwalder.com/jobs/<id>>

THE RULES (878 B) name `Claude-User` and `Claude-SearchBot` beside `OAI-SearchBot`,
`PerplexityBot` and `*`, each with `Allow: /` and `Disallow: /api/*`, `/_next/*`, `/admin/*`;
`Semrushbot` and `Dotbot` refused; **`Crawl-delay: 10` — honoured as written** (the longer of
the host's ten and our two). Four sitemaps named; `sitemap-jobs` carries every `/jobs/<id>`.

THE LIST. `/jobs` («Všetky práce») is server-rendered with its search state in `__NEXT_DATA__`
(`serverState.initialResults[<index>].results[0]`): `nbHits` — **the site's own count, 32 on the
day, the number the page prints as «Našli sme pre Vás 32 možných výsledkov»** — and up to 30
`hits`, the full records. `?page=2` serves page 1 again (the pager is client-side), so the
adapter reads the sitemap for the ids the first page does not carry and fetches those pages
(10 s each), then prints emitted against `nbHits`. Each page's `__NEXT_DATA__` carries the same
record as `pageProps.job`.

THE RECORD (the site's own object): `objectID` (the reference), `jobObject` (title, subtitle,
category and industry in the national language, `jobType` blue/white collar,
`typeOfPlacement` Leasing / Permanent …), `jobLocation` (town, zip, region, country — abroad
postings are common, «Rakúsko»), `jobInfo` (`hoursPerWeek`, `workSchedule`, `salaryMin`/`Max`,
`currency`, `salaryPeriod` — **read only when `publishSalary` is true; a period, so
`salary_unit_stated`**), `jobParams` (start/end of the posting, `lastChange`), `web.tags`
(«Hot-job», «Zahraničie», «Ubytovanie»), `jobBranch` (the agency's office), `jobContent`
(company information, description, requirements, benefits — HTML, scrubbed). **`recruiter`
— name, e-mail, mobile, photo, quote — is never emitted; the `applicationUrl` is a form,
never touched; the client employer is described and never named (`account.logoShow` false,
«No permission for account logo publishing»); `contacts_withheld` on every record.**

Measured 2026-09-14 03:3x UTC by the declared client, the guard on the exact path, ten seconds
apart: `/jobs` 620 647 B, 30 hits, `nbHits` 32; `/sitemap-jobs` 6 694 B, 32 rows with lastmod
(2026-06-24 … 2026-09-11); the ad 195 440 B with its JobPosting and its `job` object.
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

BOARDS = {"sk": {"host": "sk.trenkwalder.com", "country": "SK", "lang": "sk", "key": "trenkwalder-sk"}}
DEFAULT = "sk"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+42[01][\s ]?|0042[01][\s ]?|0)?\d{3}[\s ]?\d{3}[\s ]?\d{3}(?!\d)")
NEXT_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)
AD_RE = re.compile(r"^/jobs/([A-Za-z0-9]{15,18})/?$")
ROW_RE = re.compile(r"<url>\s*<loc>([^<]+)</loc>(?:\s*<lastmod>([^<]+)</lastmod>)?", re.S)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[trenkwalder] {msg}", file=sys.stderr)


def board_of(host):
    if host is None:
        return dict(BOARDS[DEFAULT], code=DEFAULT)
    h = host.strip().lower()
    for k, b in BOARDS.items():
        if h == k or h == b["host"]:
            return dict(b, code=k)
    die(f"--host {host!r}: not a front this adapter reads — " + ", ".join(f"{k} ({b['host']})" for k, b in BOARDS.items()))


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACES = {}


def pace_for(host):
    if host not in _PACES:
        _PACES[host] = Pace(host, own=2.0)   # the host writes Crawl-delay: 10 — the longer wins, and it is the host's
    return _PACES[host]


def request(url):
    if "/api/" in urllib.parse.urlsplit(url).path:
        die(f"{url}: /api/* is refused in writing to Claude-User by name — never sent", EXIT_REFUSED)
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    pace_for(host).wait()
    lang = next((b["lang"] for b in BOARDS.values() if b["host"] == host), "sk")
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9", "Accept-Language": lang})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t ​]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def next_props(body):
    m = NEXT_RE.search(body)
    if not m:
        return None
    try:
        return (json.loads(m.group(1)).get("props") or {}).get("pageProps") or {}
    except ValueError:
        return None


def nat(v):
    """A `{en, national}` pair → the national text (the English when the national is empty); a string passes."""
    if isinstance(v, dict):
        return (v.get("national") or v.get("en") or "").strip() or None
    return (v or "").strip() or None if isinstance(v, str) else None


def record(h, b):
    jo = h.get("jobObject") or {}
    jl = h.get("jobLocation") or {}
    ji = h.get("jobInfo") or {}
    jp = h.get("jobParams") or {}
    jc = h.get("jobContent") or {}
    web = h.get("web") or {}
    br = h.get("jobBranch") or {}
    oid = h.get("objectID") or ""
    publish = bool(ji.get("publishSalary"))
    smin = ji.get("salaryMin") if publish else None
    smax = ji.get("salaryMax") if publish else None
    unit = nat(ji.get("salaryPeriod")) if publish else None
    return {
        "source": b["key"], "country": b["country"], "ledger_id": f"{b['key']}:{oid}", "id": oid,
        "url": web.get("jobUrl") or f"https://{b['host']}/jobs/{oid}",
        "title": (jo.get("title") or "").strip() or None, "subtitle": (jo.get("subtitle") or "").strip() or None,
        "company": "Trenkwalder", "employer_is_the_agency": True,   # the client is described in the text and never named
        "place": jl.get("location") or None, "postal_code": jl.get("zipCode") or None, "region": nat(jl.get("region")), "job_country": nat(jl.get("country")),
        "category": nat(jo.get("mainJobCategory")) or nat((jo.get("jobCategory") or [None])[0]),
        "industry": nat(jo.get("mainIndustry")) or nat((jo.get("industry") or [None])[0]),
        "job_type": jo.get("jobType") or None, "placement": nat(jo.get("typeOfPlacement")),
        "work_schedule": nat(ji.get("workSchedule")), "hours_per_week": ji.get("hoursPerWeek"),
        "salary_min": smin, "salary_max": smax, "salary_currency": (ji.get("currency") or None) if publish else None,
        "salary_unit": unit, "salary_unit_stated": bool(unit) and (smin is not None or smax is not None),
        "tags": [nat(t) for t in (web.get("tags") or []) if nat(t)] or None,
        "office": br.get("name") or None, "office_city": br.get("city") or None,
        "posted": (jp.get("startDate") or web.get("jobAdDate") or "")[:10] or None, "valid_through": (jp.get("endDate") or "")[:10] or None,
        "changed": (jp.get("lastChange") or "")[:10] or None,
        "status": h.get("publishingStatus") or None, "language": (h.get("language") or b["lang"]).lower(),
        "company_text": scrub(text(jc.get("companyInformation") or "")),
        "description": scrub(text(jc.get("jobDescription") or "")),
        "requirements": scrub(text(jc.get("jobRequirements") or "")),
        "benefits": scrub(text(jc.get("compensationBenefits") or "")),
        # `recruiter` — name, e-mail, mobile, photo, quote — is on every record and is never emitted; `applicationUrl` is a form, never touched
        "contacts_withheld": True,
    }


def hits_of(body):
    pp = next_props(body)
    ir = ((pp or {}).get("serverState") or {}).get("initialResults") or {}
    for idx in ir.values():
        for res in (idx.get("results") or []):
            if isinstance(res, dict) and "hits" in res:
                return res.get("hits") or [], res.get("nbHits")
    return None, None


def sitemap_rows(b):
    url = f"https://{b['host']}/sitemap-jobs"
    code, body = request(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    rows, seen = [], set()
    for loc, lastmod in ROW_RE.findall(body):
        m = AD_RE.match(urllib.parse.urlsplit(loc).path)
        if not m or m.group(1) in seen:
            continue
        seen.add(m.group(1))
        rows.append({"source": b["key"], "country": b["country"], "ledger_id": f"{b['key']}:{m.group(1)}", "id": m.group(1), "url": loc, "lastmod": lastmod or None, "contacts_withheld": True, "language": b["lang"]})
    if not rows:
        die(f"{url}: 200 and not one /jobs/<id> row — the sitemap's shape changed", EXIT_PARTIAL)
    return rows


def cmd_sitemap(a):
    b = board_of(getattr(a, "host", None))
    rows = sitemap_rows(b)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{th(len(rows))} job id(s) in {b['host']}/sitemap-jobs — the listing's own count is read by `list`; not compared here.")


def cmd_list(a):
    b = board_of(getattr(a, "host", None))
    url = f"https://{b['host']}/jobs"
    code, body = request(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    hits, total = hits_of(body)
    if hits is None:
        die(f"{url}: 200 and no search state in the page — the template changed; not an empty market", EXIT_PARTIAL)
    rows, seen = [], set()
    for h in hits:
        r = record(h, b)
        if r["id"] and r["id"] not in seen:
            seen.add(r["id"])
            rows.append(r)
    fetched, gone = 0, 0
    if total is not None and len(seen) < total and (not a.limit or len(rows) < a.limit):
        for s in sitemap_rows(b):
            if s["id"] in seen:
                continue
            if a.limit and len(rows) >= a.limit:
                break
            code, page = request(s["url"])
            if code == 404:
                gone += 1
                continue
            if code != 200:
                die(f"{s['url']}: HTTP {code}", EXIT_PARTIAL)
            job = (next_props(page) or {}).get("job")
            if not isinstance(job, dict) or not job.get("objectID"):
                die(f"{s['url']}: 200 and no `job` in the page's state — the template changed", EXIT_PARTIAL)
            seen.add(job["objectID"])
            rows.append(record(job, b))
            fetched += 1
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    if total is None:
        note(f"{th(n)} emitted from the listing's state ({th(fetched)} read from their pages) — the site's `nbHits` was not found; not compared.")
    elif a.limit and a.limit < len(rows) + (total - len(seen)):
        note(f"{th(n)} emitted of the {th(total)} the site states («Našli sme pre Vás {th(total)} možných výsledkov») — {th(len(hits))} from the listing's first page, {th(fetched)} read from their pages; bounded by --limit, not a shortfall.")
    else:
        diff = n - total
        note(f"{th(n)} emitted ({th(len(hits))} from the listing's first page, {th(fetched)} read from their pages, {th(gone)} gone), the site states {th(total)} — " + ("equal." if diff == 0 else (f"{th(diff)} more emitted than stated." if diff > 0 else f"{th(-diff)} short.")))
    note("the `recruiter` object on every record (name, e-mail, telephone) is never emitted; texts scrubbed; the application form never touched; the client employer never named.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    b = next((dict(v, code=k) for k, v in BOARDS.items() if v["host"] == parts.netloc), None)
    m = AD_RE.match(parts.path) if b else None
    if not b or not m:
        die(f"{a.url}: not a job address on a front this adapter reads (https://sk.trenkwalder.com/jobs/<id>)")
    url = f"https://{b['host']}/jobs/{m.group(1)}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    job = (next_props(body) or {}).get("job")
    if not isinstance(job, dict) or not job.get("objectID"):
        die(f"{url}: 200 and no `job` in the page's state — the template changed", EXIT_PARTIAL)
    print(json.dumps(record(job, b), ensure_ascii=False))
    note(f"{url}: read from the page's own state; `recruiter` withheld; texts scrubbed; the application form never touched.")


def main():
    p = argparse.ArgumentParser(description="Trenkwalder Slovakia — the listing's own count beside every walk, the sitemap for the rest, ten seconds apart as the rules ask; the recruiter never emitted. Issue #349.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the listing's state (30) and the sitemap's other jobs read from their pages")
    l_.add_argument("--host", help="sk (default) — or the hostname")
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    s_ = sub.add_parser("sitemap", help="every /jobs/<id> of sitemap-jobs")
    s_.add_argument("--host")
    s_.set_defaults(fn=cmd_sitemap)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
