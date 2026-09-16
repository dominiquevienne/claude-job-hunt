#!/usr/bin/env python3
"""Trabajito (`www.trabajito.com.bo`) — Bolivia's generalist on Next.js: the department page states its count on the server («736 ofertas de empleo en Bolivia» in its meta), the list is filled by a client route the rules refuse (`/api/`), the sitemap names every advertisement with its department, and each ad page carries a JobPosting; the count printed beside every walk; the description scrubbed. Issue #429.

  trabajito.py sitemap [--dept santa-cruz] [--limit N]   every /trabajo/<dept>/<slug>-<CODE> row of sitemap.xml, with lastmod (1 request)
  trabajito.py list [--dept santa-cruz] [--limit N]      the stated count, then the sitemap's ads read from their pages (N pages, 20 unless told, 2 s apart)
  trabajito.py ad --url <https://trabajito.com.bo/trabajo/<dept>/<slug>-<CODE>>

THE RULES. `User-Agent: *` — `Allow: /`, then the app's routes and the accounts refused (`/api/`,
`/user/`, `/dashboard`, `/login`, `/register`, `/candidato/`, `/manage-jobs`, `/crud-job`,
`/company-profile`, `/applicants` …); `ClaudeBot` and `anthropic-ai` are named with `Allow: /`
(the AI crawlers' block — GPTBot, PerplexityBot, CCBot); no Crawl-delay, 2 s is ours; `Sitemap:`
declared. `/api/` and the accounts are refused before the gate.

THE COUNT IS ON THE SERVER, THE CARDS ARE NOT. `/trabajo` (200, ~124 KB) is a Next.js page whose
markup names not one advertisement — the list is a client fetch to `/api/…`, refused in writing.
`/empleos/bolivia` (200, ~145 KB) carries «736 ofertas de empleo en Bolivia» in its meta
description and one hundred ad links in its flight data; `/empleos/<departamento>` the same for a
department. So the count is read from the department page and the inventory is `/sitemap.xml`
(967 rows on the day: 728 `/trabajo/<departamento>/<slug>-<CODE>` — santa-cruz 502, la-paz 99,
cochabamba 67, tarija 13, chuquisaca 13, oruro 11, remoto 7, beni 6, potosi 6, pando 4 — and 239
facets and pages); `list` prints emitted against the stated count («8 short» on the day — the
sitemap and the counter are two clocks). THE AD. `/trabajo/<dept>/<slug>-<CODE>` (200, ~114 KB)
carries a JobPosting JSON-LD — title, description, identifier (name = the employer, value = the
CODE), employmentType, hiringOrganization (name, sameAs, logo), jobLocation (locality, region,
country), datePosted, validThrough — beside a FAQPage. **The description is scrubbed of e-mail
addresses and Bolivian telephone numbers (a mobile travelled in the page's flight data on the ad
read); `contacts_withheld` on every record; the application (a candidate account) never touched.**

Measured 2026-09-16 06:00–06:01 UTC by the declared client, the guard on the exact path: robots
200 (993 B); `/` 106 641 B; `/trabajo` 123 787 B, no ad link; `sitemap.xml` 147 005 B, 967 rows /
728 ads, distinct; `/empleos/bolivia` 144 581 B, «736 ofertas»; the ad 114 236 B with its JobPosting.
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

HOST = "www.trabajito.com.bo"
APEX = "trabajito.com.bo"
SITEMAP = f"https://{HOST}/sitemap.xml"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+?591[\s\-]?)?(?:[67]\d{7}|[2-4][\s\-]?\d{6,7})(?!\d)")   # mobiles 6xxxxxxx / 7xxxxxxx, landlines 2/3/4 + 6–7 digits, with or without +591
AD_RE = re.compile(r"^/trabajo/([a-z0-9\-]+)/([a-z0-9\-]+)-([A-Z0-9]{3,8})/?$")
REFUSED_RE = re.compile(r"^/(?:api|user|dashboard|employer-dashboard|candidato|login|register|employer-login|employer-register|candidate-register|password|cart|checkout|orders|manage-jobs?|crud-job|company-profile|applicants|applied-jobs|blocked-candidates|webhook-config)(?:[/\-]|$)")
ROW_RE = re.compile(r"<url>\s*<loc>([^<]+)</loc>(?:\s*<lastmod>([^<]+)</lastmod>)?", re.S)
COUNT_RE = re.compile(r"(\d[\d\.,]*)\s*ofertas de empleo en ")

_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written; 2 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[trabajito] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    if REFUSED_RE.search(urllib.parse.urlsplit(url).path):
        die(f"{url}: refused in writing to `*` (the app's routes, the accounts) — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9", "Accept-Language": "es"})
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
    s = MAIL_RE.sub("[e-mail withheld]", htmlmod.unescape(s))
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def dept_url(dept):
    return f"https://{HOST}/empleos/{dept or 'bolivia'}"


def stated(body):
    """The count the department page prints on the server — «736 ofertas de empleo en Bolivia» — or `None`."""
    m = COUNT_RE.search(body or "")
    return int(re.sub(r"\D", "", m.group(1))) if m else None


def sitemap_rows(dept=None):
    code, body = request(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    rows, seen, other, elsewhere = [], set(), 0, 0
    for loc, lastmod in ROW_RE.findall(body):
        m = AD_RE.match(urllib.parse.urlsplit(loc).path)
        if not m:
            other += 1
            continue
        if dept and m.group(1) != dept:
            elsewhere += 1
            continue
        if m.group(3) in seen:
            continue
        seen.add(m.group(3))
        rows.append({"source": "trabajito", "country": "BO", "ledger_id": f"trabajito:{m.group(3)}", "id": m.group(3), "url": loc, "department": m.group(1), "slug": m.group(2), "lastmod": (lastmod or "")[:10] or None, "contacts_withheld": True, "language": "es"})
    if not rows and not elsewhere:
        die(f"{SITEMAP}: 200 and not one /trabajo/<dept>/<slug>-<CODE> row among {th(other)} — the sitemap's shape changed", EXIT_PARTIAL)
    return rows, other, elsewhere


def cmd_sitemap(a):
    rows, other, elsewhere = sitemap_rows(a.dept)
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{th(len(rows))} ad row(s) in the sitemap" + (f" for {a.dept} ({th(elsewhere)} in other departments)" if a.dept else "") + f" ({th(other)} other rows set aside — facets, pages); `list` prints the department page's stated count beside them.")
    if a.limit and a.limit < len(rows):
        note(f"{th(len(emitted))} emitted of the {th(len(rows))} — bounded by --limit.")


def record(body, jid, url, dept):
    jp = (postings(body) or [None])[-1]
    if jp is None:
        return None
    org = one(jp.get("hiringOrganization"))
    addr = one(one(jp.get("jobLocation")).get("address"))
    ident = jp.get("identifier") if isinstance(jp.get("identifier"), str) else one(jp.get("identifier")).get("value")
    return {
        "source": "trabajito", "country": "BO", "ledger_id": f"trabajito:{jid}", "id": jid, "url": url, "code": ident or None,
        "title": htmlmod.unescape(jp.get("title") or "").strip() or None,
        "company": (org.get("name") or "").strip() or None, "company_site": org.get("sameAs") or None,
        "employment_type": jp.get("employmentType") or None,
        "department": dept, "place": addr.get("addressLocality") or None, "region": addr.get("addressRegion") or None, "address_country": addr.get("addressCountry") or None,
        "posted": (jp.get("datePosted") or "")[:10] or None, "valid_through": (jp.get("validThrough") or "")[:10] or None,
        "description": scrub(jp.get("description")),
        "contacts_withheld": True, "language": "es",
    }


def cmd_list(a):
    code, body = request(dept_url(a.dept))
    if code != 200:
        die(f"{dept_url(a.dept)}: HTTP {code}", EXIT_PARTIAL)
    total = stated(body)
    if total is None:
        die(f"{dept_url(a.dept)}: 200 and no «N ofertas de empleo en …» in the page — the template changed; not an empty market", EXIT_PARTIAL)
    rows, other, elsewhere = sitemap_rows(a.dept)
    limit = a.limit if a.limit else 20
    out, gone = [], 0
    for r in rows[:limit]:
        code, page = request(r["url"])
        if code == 404:
            gone += 1
            continue
        if code != 200:
            die(f"{r['url']}: HTTP {code}", EXIT_PARTIAL)
        rec = record(page, r["id"], r["url"], r["department"])
        if rec is None:
            die(f"{r['url']}: 200 without a JobPosting — the template changed; not an empty job", EXIT_PARTIAL)
        rec["lastmod"] = r["lastmod"]
        out.append(rec)
    for rec in out:
        print(json.dumps(rec, ensure_ascii=False))
    n = len(out)
    where = dept_url(a.dept)
    if limit < len(rows):
        note(f"{th(n)} emitted of the {th(total)} the site states on {where} ({th(len(rows))} in the sitemap, {th(gone)} gone) — {th(min(limit, len(rows)))} read by request (--limit), not a shortfall.")
    else:
        verdict = "equal" if n == total else (f"{th(total - n)} short" if n < total else f"{th(n - total)} more emitted")
        note(f"{th(n)} emitted ({th(len(rows))} in the sitemap, {th(gone)} gone), the site states {th(total)} — {verdict}.")
    note("descriptions scrubbed; the application never touched.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc not in (HOST, APEX) or not m:
        die(f"{a.url}: not a job address (https://{APEX}/trabajo/<dept>/<slug>-<CODE>)")
    url = f"https://{APEX}{parts.path.rstrip('/')}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    rec = record(body, m.group(3), url, m.group(1))
    if rec is None:
        die(f"{url}: 200 without a JobPosting — the template changed", EXIT_PARTIAL)
    print(json.dumps(rec, ensure_ascii=False))
    note(f"{url}: read from its JobPosting; description scrubbed; the application never touched.")


def main():
    p = argparse.ArgumentParser(description="Trabajito — the department page's stated count beside the sitemap's inventory, each ad read from its JobPosting; descriptions scrubbed. Issue #429.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s_ = sub.add_parser("sitemap", help="every /trabajo/<dept>/<slug>-<CODE> row of sitemap.xml (1 request)")
    s_.add_argument("--dept", help="a department slug as the site writes it — santa-cruz, la-paz, cochabamba, remoto …")
    s_.add_argument("--limit", type=int)
    s_.set_defaults(fn=cmd_sitemap)
    l_ = sub.add_parser("list", help="the stated count, then the sitemap's ads read from their pages — 20 unless --limit")
    l_.add_argument("--dept", help="a department slug; the count is then the department page's")
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
