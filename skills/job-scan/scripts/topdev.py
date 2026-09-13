#!/usr/bin/env python3
"""TopDev (`topdev.vn`) — Vietnam's IT board, read through its paged job sitemaps and the JobPosting every advertisement carries.

  topdev.py sitemap [--lang en|vi] [--pages N] [--limit N] [--no-site-total]
  topdev.py ad --url <advertisement URL>

THE JOB SITEMAPS ARE THE ROUTE, THE SEARCH PAGE'S COUNT IS THE SECOND SOURCE

`/sitemap.xml` names seven children; `/sitemap-jobs.xml` is itself an index
of **249 `jobs_desc_en_page_<n>.xml` and 249 `jobs_desc_vi_page_<n>.xml`**
(plus the skills file) — 20 `<loc>` a page on 2026-09-13, the same ids in
both languages (`/detail-jobs/<slug>-<id>` in `en`, `/viec-lam/<slug>-<id>`
in `vi`; page 1 checked, 20 = 20). The adapter reads one language (`en` by
default: 249 requests at 2 s, ~9 min), takes the trailing number of each
URL as the id, dedups, and prints the distinct count beside what the search
page states — `/viec-lam/tim-kiem` says «Tuyển dụng 4942 việc làm lương cao
[Update 13/9/2026]», with the site's own update date: «n emitted, site
states N — equal / k short». `--pages` bounds the walk and says so; the
figure is then a lower bound, not compared. **Every `<lastmod>` in the
sitemap is the day of the read — a rebuild stamp, not a date; no `--since`.**

EVERY ADVERTISEMENT CARRIES A JobPosting IN JSON-LD — `title`, `description`
(HTML), `datePosted`, `validThrough`, `employmentType` (a list — `["OTHER"]`
on the page read), `industry`, `skills` (a comma-joined string),
`jobBenefits` (HTML), `hiringOrganization` (`name`, `sameAs` = the company
page, `logo`), `identifier.value` (**the EMPLOYER's id — 94346 for MBBANK —
not the advertisement's; the advertisement's id is the URL's tail**),
`jobLocation.address` (`addressLocality`, `addressRegion`, `addressCountry`
as ISO-2 — `VN`), `baseSalary` (`currency: VND`, min / max / `unitText`
MONTH, and a `value` sentence «9.000.000 VND to 55.000.000 VND»). The
country is read from the advertisement; the language of the page is the
URL's (`/detail-jobs/` → `en` shell, `/viec-lam/` → `vi`), the text is what
the employer wrote, in either.

THE RULES: Cloudflare's managed block (`ClaudeBot` named and refused, `*`
open — `identity()` answers `claude-user`, `verdict()` sweeps since #230)
plus the operator's: `*` refused `/job-seeker/login`, `/employers/search`,
`/partners/`, `/job/getApply`, `/affiliate/`, `/challenge/`, `/topdemy/`,
`/socket.io`; `Sitemap: https://topdev.vn/sitemap.xml`; no `Crawl-delay`
(2 s is ours); `certain: True`. Measured 2026-09-13 10:22–10:35 UTC (#233,
lot 8 → this adapter).
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
from _ldjson import absent_reason, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _sitemap import locs as sitemap_locs, maybe_gunzip
from _ua import UA
from _zero import empty_first_page

HOST = "topdev.vn"
BASE = "https://" + HOST
INDEX = BASE + "/sitemap.xml"
JOBS_INDEX = BASE + "/sitemap-jobs.xml"
SEARCH = BASE + "/viec-lam/tim-kiem"
PAGE_RE = {"en": re.compile(r"/sitemap/jobs_desc_en_page_(\d+)\.xml$"),
           "vi": re.compile(r"/sitemap/jobs_desc_vi_page_(\d+)\.xml$")}
AD_RE = re.compile(r"^https://topdev\.vn/(?:detail-jobs|viec-lam)/[^/?#]*-(\d+)/?(?:\?.*)?$")
# «Tuyển dụng 4942 việc làm lương cao [Update 13/9/2026]»
SITE_COUNT_RE = re.compile(r"Tuyển dụng\s*([\d.,]+)\s*việc làm")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[topdev] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # no Crawl-delay declared; 2 s is ours


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.5",
        "Accept-Language": "vi,en;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = maybe_gunzip(r.read())
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"[ \t]+", " ", htmlmod.unescape(markup)).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def site_count(body):
    m = SITE_COUNT_RE.search(text(body))
    return int(re.sub(r"\D", "", m.group(1))) if m else None


def cmd_sitemap(a):
    code, body = get(JOBS_INDEX)
    if code != 200:
        die(f"{JOBS_INDEX}: HTTP {code}", EXIT_PARTIAL)
    pages = []
    for u in sitemap_locs(body):
        m = PAGE_RE[a.lang].search(u.strip())
        if m:
            pages.append((int(m.group(1)), u.strip()))
    pages.sort()
    if not pages:
        die(f"{JOBS_INDEX} names {len(sitemap_locs(body))} children and none of the shape jobs_desc_{a.lang}_page_<n>.xml — the enumeration moved; nothing here says the board is empty.", EXIT_PARTIAL)
    rows, seen, raw, unmatched, read = [], set(), 0, 0, 0
    for n, u in pages:
        if a.pages and read >= a.pages:
            break
        code, xml = get(u)
        if code != 200:
            die(f"{u}: HTTP {code} — page {n} of {len(pages)}; the count below would be short and is not printed.", EXIT_PARTIAL)
        read += 1
        for loc in sitemap_locs(xml):
            raw += 1
            m = AD_RE.match(loc.strip())
            if not m:
                unmatched += 1
                continue
            ident = m.group(1)
            if ident in seen:
                continue
            seen.add(ident)
            rows.append({"source": "topdev", "country": "VN", "ledger_id": f"topdev:{ident}", "id": ident, "url": loc.strip()})
        if a.limit and len(rows) >= a.limit:
            break
    if raw == 0:
        die(empty_first_page("topdev", "", "<loc>", where=pages[0][1]), EXIT_PARTIAL)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    bounded = read < len(pages)
    note(f"{read} of {len(pages)} {a.lang} sitemap page(s) read; {raw} <loc>, {raw - unmatched} of the advertisement shape, "
         f"{unmatched} not; **{th(len(rows))} distinct advertisement id(s)**"
         + (f" ({a.limit} printed under --limit)" if a.limit and len(rows) > a.limit else "")
         + (f" — the walk stopped at page {read}, so the count is a lower bound" if bounded else "")
         + ". Every <lastmod> is the day of the read — a rebuild stamp, not a date.")
    if a.no_site_total:
        return
    code, page = get(SEARCH)
    stated = site_count(page) if code == 200 else None
    if stated is None:
        note(f"{SEARCH} states no count this run (HTTP {code}) — no second source.")
    elif bounded:
        note(f"site states {th(stated)} on {SEARCH}; {th(len(rows))} emitted from a bounded walk — not compared.")
    elif stated == len(rows):
        note(f"{th(len(rows))} emitted, site states {th(stated)} on {SEARCH} — equal.")
    else:
        note(f"{th(len(rows))} emitted, site states {th(stated)} on {SEARCH} — {th(abs(stated - len(rows)))} "
             + ("short" if stated > len(rows) else "more in the sitemap than the site states")
             + "; the sitemap and the search index are two views of one store.")


def _money(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/detail-jobs/<slug>-<id> or /viec-lam/<slug>-<id>")
    ident = m.group(1)
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    found = postings(body)
    if not found:
        why = absent_reason(body)
        if getattr(why, "our_fault", False):
            die(f"{a.url}: {why} **The page announces a JobPosting and this read none.**")
        die(f"{a.url}: {why}", EXIT_PARTIAL)
    d = found[0]
    org = d.get("hiringOrganization") or {}
    idv = d.get("identifier") or {}
    loc = d.get("jobLocation") or {}
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
    sal = d.get("baseSalary") or {}
    val = sal.get("value") if isinstance(sal, dict) else None
    if not isinstance(val, dict):
        val = sal if isinstance(sal, dict) else {}
    et = d.get("employmentType")
    skills = d.get("skills")
    print(json.dumps({
        "source": "topdev",
        "country": (addr.get("addressCountry") or "").strip() or "VN" if isinstance(addr, dict) else "VN",
        "ledger_id": f"topdev:{ident}", "id": ident, "url": a.url,
        "title": text(d.get("title")),
        "employer": org.get("name") if isinstance(org, dict) else None,
        "employer_page": org.get("sameAs") if isinstance(org, dict) else None,
        # the site's `identifier.value` is the EMPLOYER's id, not the advertisement's — kept apart
        "employer_id": str(idv.get("value")) if isinstance(idv, dict) and idv.get("value") is not None else None,
        "employment_type": ", ".join(et) if isinstance(et, list) else et,
        "industry": d.get("industry"),
        "skills": [s.strip() for s in skills.split(",") if s.strip()] if isinstance(skills, str) else (skills or []),
        "city": text(addr.get("addressLocality")) or None if isinstance(addr, dict) else None,
        "region": text(addr.get("addressRegion")) or None if isinstance(addr, dict) else None,
        "posted": d.get("datePosted"), "valid_through": d.get("validThrough"),
        "salary_currency": sal.get("currency") if isinstance(sal, dict) else None,
        "salary_min": _money(val.get("minValue")), "salary_max": _money(val.get("maxValue")),
        "salary_unit": (val.get("unitText") or "").strip() or None,
        "salary_as_published": val.get("value") if isinstance(val.get("value"), str) else None,
        "direct_apply": d.get("directApply"),
        "benefits": text(d.get("jobBenefits"))[:4000] or None,
        "description": text(d.get("description"))[:20000],
        "page_language": "en" if "/detail-jobs/" in a.url else "vi",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="TopDev — Vietnam's IT board, through its paged job sitemaps and the JSON-LD its pages carry.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="distinct advertisement ids — 1 + 249 requests at 2 s on 2026-09-13, + the search page's count")
    s.add_argument("--lang", choices=("en", "vi"), default="en")
    s.add_argument("--pages", type=int)
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one advertisement, from its JSON-LD")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
