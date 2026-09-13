#!/usr/bin/env python3
"""GulfTalent (`www.gulftalent.com`) — the Gulf's board, one country edition at a time, through its paginated listing and the JobPosting every advertisement carries.

  gulftalent.py list [--country uae] [--pages N] [--limit N]
  gulftalent.py ad --url <advertisement URL>

THE ROUTE IS THE LISTING, AND THE PAGE STATES ITS OWN COUNT — TWICE

`/<country>/jobs` and `/<country>/jobs/<page>` are server-rendered, 25 rows
a page (`<a class="… job-results-item" data-ga-label="<id>" href=…>` with
the title, `company-name`, `location` and a dated `date` div); past the last
page the site answers **404** (`/uae/jobs/9999`) — or, one past the last
full page, 200 with rows already seen (page 629 on 2026-09-13); the walk
stops on either. The page states its count twice: the visible
`<div class="job-count">15,681 Jobs found</div>` and a `panel-data`
attribute `{"job_count":15680,…}` — **they differed by one on 2026-09-13
14:57 UTC** (page 2 read six minutes after page 1, one advertisement posted
in between, and the panel is a cached figure for `/uae/jobs`). The adapter
prints both beside the walk and corrects neither. The JSON-LD `ItemList`
lives on page 1 ONLY (0 on page 2) — the rows are the route, not the list.

TWO ADDRESS SHAPES, the same advertisement: `…-632616` and `…_632494` —
hyphen or underscore before the id, 4 rows of 25 on the page read with the
underscore. A pattern written for the hyphen alone emits 21 and no
symptom; the id is read from `data-ga-label`, the address as written.

THE WITNESS at the end of a full walk is the pager closing under the reader
— «page M+1 answered 404, pager closes at M» — never a figure copied from
the page; with `--pages` the note says the walk was bounded by request,
never «short». The browser's pager closed at 627 × 25 = 15 675 the same
morning (12:35 UTC); the full walk at 15:01–15:22 UTC printed «15 681
emitted over 628 page(s), site states 15 681 («Jobs found», uae) — equal».

THE RULES name two of this project's tokens under «Blocked — AI training
crawlers» (`ClaudeBot`, `anthropic-ai`: `Disallow: /`) and keep a separate
group «Allowed — AI search and retrieval» (ChatGPT-User, OAI-SearchBot,
PerplexityBot…); `Claude-User` is named in neither and falls under `*`,
`Allow: /` — the decision of 2026-09-07, and here the operator's own
taxonomy says the same thing: the agent acting for a person is the class it
allows. No `Crawl-delay` for `*` (30 s for five SEO crawlers by name); this
adapter spaces 2 s.

THE ADVERTISEMENT PAGE carries the same labelled fields on both shapes —
«Job Type», «Job Location», «Nationality», «Salary: 1000 - 2000 AED», «Job
Function», «Company Industry» — with the employer and «Posted on: 12 Sep
2026» in the header and the description under `#text-container`. **Only the
hyphen shape carries a JobPosting** (datePosted, validThrough, baseSalary
with `unitText MONTH`, directApply); the underscore shape carries a
BreadcrumbList and nothing else (`632494`, 2026-09-13 14:59 UTC). So `ad`
reads the page first and the JSON-LD as a supplement, and says which it had
(`jsonld`). The labelled salary states no period — `salary_unit_stated` is
false unless the JobPosting gave one. Measured 2026-09-13 12:35 UTC (a tab)
and 13:27–14:59 UTC (the declared client, served on every path read).
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
from _ua import UA
from _zero import empty_first_page

BASE = "https://www.gulftalent.com"
COUNTRIES = ("uae", "saudi-arabia", "qatar", "kuwait", "bahrain", "oman")
COUNTRY_ISO = {"uae": "AE", "saudi-arabia": "SA", "qatar": "QA", "kuwait": "KW", "bahrain": "BH", "oman": "OM"}
# two shapes on one page: `…-632616` and `…_632494` — hyphen OR underscore before the id
AD_RE = re.compile(r"^https://www\.gulftalent\.com/([a-z-]+)/jobs/([a-z0-9][a-z0-9-]*?)[-_](\d+)/?$")
ROW_RE = re.compile(r'<a class="[^"]*\bjob-results-item\b[^"]*"(?P<attrs>[^>]*)>(?P<body>.*?)</a>', re.S)
# <div class="job-count"> 15,681 Jobs found </div>   <- the visible figure
FOUND_RE = re.compile(r'class="job-count"[^>]*>\s*([\d,\.\s]+?)\s*Jobs? found', re.I)
# panel-data='{"job_count":15680,"this_page":…}'     <- the panel's figure, cached for the edition's first page
COUNT_RE = re.compile(r"panel-data='(\{.*?\})'", re.S)
PAGE_SIZE = 25

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[gulftalent] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace("www.gulftalent.com", own=2.0)   # no Crawl-delay for `*`; 2 s is ours


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    """Thousands with a space — the repo's figure style."""
    return f"{n:,}".replace(",", " ")


def rows_on(body):
    """The listing rows of one page — id from `data-ga-label`, address as written, title, employer, location, date label."""
    out = []
    for m in ROW_RE.finditer(body or ""):
        attrs, inner = m.group("attrs"), m.group("body")
        ident = (re.search(r'data-ga-label="(\d+)"', attrs) or [None, None])[1]
        href = (re.search(r'href="([^"]+)"', attrs) or [None, None])[1]
        if not ident or not href:
            continue

        def div(cls):
            d = re.search(r'<(?:div|p) class="[^"]*\b%s\b[^"]*"[^>]*>(.*?)</(?:div|p)>' % cls, inner, re.S)
            return text(d.group(1)) if d else None
        out.append({"id": ident, "href": href, "title": div("title"), "employer": div("company-name"),
                    "location": div("location"), "posted_label": div("date"),
                    "edition": (re.search(r'data-ga-dimension-three="([a-z-]+)"', attrs) or [None, None])[1]})
    return out


def jobs_found(body):
    """The visible «N Jobs found» of the page, or None."""
    m = FOUND_RE.search(body or "")
    if not m:
        return None
    digits = re.sub(r"\D", "", m.group(1))
    return int(digits) if digits else None


def site_count(body):
    """`job_count` from the page's own panel-data — the panel's cached figure — or None."""
    m = COUNT_RE.search(body or "")
    if not m:
        return None
    try:
        v = json.loads(htmlmod.unescape(m.group(1))).get("job_count")
    except ValueError:
        return None
    return int(v) if isinstance(v, int) else None


def listing_url(country, page):
    return f"{BASE}/{country}/jobs" + (f"/{page}" if page > 1 else "")


def cmd_list(a):
    country = a.country
    rows, seen, found, panel, page, closed = [], set(), None, None, 1, None
    while True:
        url = listing_url(country, page)
        code, body = get(url)
        if code == 404 and page > 1:
            closed = f"page {page} answered 404, pager closes at {page - 1}"
            page -= 1
            break
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if found is None:
            found, panel = jobs_found(body), site_count(body)
        items = rows_on(body)
        anchors = body.count("job-results-item")
        if page == 1 and not items:
            die(empty_first_page("gulftalent", body, "listing row", where=url,
                                 candidates=anchors), EXIT_PARTIAL)
        if len(items) < anchors:
            # the hyphen-only pattern read 21 of 25 with no symptom (2026-09-13); a bounded walk cannot see a per-page
            # shortfall from the stated count, so the page's own anchors are the second source here
            die(f"{url}: {anchors} listing anchor(s) on the page, {len(items)} read — a partial read of a page is a reader fault, not a count.", EXIT_PARTIAL)
        new = 0
        for r in items:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            href = r["href"] if r["href"].startswith("http") else BASE + r["href"]
            edition = r["edition"] or country
            rows.append({"source": "gulftalent", "country": COUNTRY_ISO.get(edition, edition.upper()),
                         "edition": edition, "ledger_id": f"gulftalent:{r['id']}", "id": r["id"], "url": href,
                         "title": r["title"], "employer": r["employer"], "location": r["location"],
                         "posted_label": r["posted_label"]})
            new += 1
        if not items or new == 0:
            closed = f"page {page} carried {'no row' if not items else 'no new row'}, pager closes at {page - 1}"
            page -= 1
            break
        if a.pages and page >= a.pages:
            break
        if a.limit and len(rows) >= a.limit:
            break
        page += 1
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    stated = found if found is not None else panel
    second = "" if panel is None or panel == found else f"; panel `job_count` {th(panel)}" + ("" if found is None else f" — {th(abs(panel - found))} apart, neither corrected")
    if stated is None:
        note(f"{th(n)} emitted over {page} page(s) of {PAGE_SIZE}; the page states no «Jobs found» and no `job_count` this run — no second source.")
        return
    bounded = (a.pages and page >= a.pages and stated > page * PAGE_SIZE) or (a.limit and a.limit < stated)
    if bounded:
        note(f"{th(n)} emitted of the {th(stated)} the site states («Jobs found», {country}) — {page} page(s) walked by request (--pages/--limit), not a shortfall{second}.")
    elif n == stated:
        note(f"{th(n)} emitted over {page} page(s), site states {th(stated)} («Jobs found», {country}) — equal; {closed}{second}.")
    else:
        note(f"{th(n)} emitted over {page} page(s), site states {th(stated)} («Jobs found», {country}) — {th(abs(stated - n))} "
             + ("short" if stated > n else "more emitted than the site states") + f"; {closed}{second}; a live board moves between the first page and the last.")


FIELD_RE = re.compile(r'<span style="color: #6c757d">([^<]+?):?\s*</span>\s*<span>\s*(.*?)</span>', re.S)
HEAD_RE = re.compile(r'<h2[^>]*>(.*?)</h2>\s*</a>\s*<p>(.*?)</p>\s*<p>Posted on:\s*([^<]+)</p>', re.S)
DESC_RE = re.compile(r'id="text-container"[^>]*>(.*?)</span>\s*</div>', re.S)
SAL_RE = re.compile(r"^\s*([\d,\.]+)\s*-\s*([\d,\.]+)\s*([A-Z]{3})\s*$")


def page_fields(body):
    """The labelled pairs every advertisement page carries — «Job Type», «Job Location», «Salary», «Job Function», «Company Industry»… — plus the header's employer, place and «Posted on»."""
    f = {text(k): text(v) for k, v in FIELD_RE.findall(body or "")}
    h = HEAD_RE.search(body or "")
    if h:
        f["_employer"], f["_place"], f["_posted"] = text(h.group(1)), text(h.group(2)), h.group(3).strip()
    d = DESC_RE.search(body or "")
    f["_description"] = text(d.group(1)) if d else None
    return f


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/<country>/jobs/<slug>-<id> (or _<id>)")
    edition, ident = m.group(1), m.group(3)
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    f = page_fields(body)
    title = re.search(r'data-cy="job-title"[^>]*>(.*?)</h1>', body, re.S)
    if not title and not f.get("_employer"):
        die(f"{a.url}: neither a job title nor the header this page shape carries — not an advertisement page as read ({len(body)} characters).", EXIT_PARTIAL)
    # the labelled «Salary: 1000 - 2000 AED» states no period; the JobPosting (hyphen shape only) states MONTH
    sal = SAL_RE.match(f.get("Salary") or "")
    money = lambda v: int(float(v.replace(",", ""))) if v else None
    row = {
        "source": "gulftalent", "country": COUNTRY_ISO.get(edition, edition.upper()), "edition": edition,
        "ledger_id": f"gulftalent:{ident}", "id": ident, "url": a.url,
        "title": text(title.group(1)) if title else None,
        "employer": f.get("_employer"),
        "employment_type": [f["Job Type"]] if f.get("Job Type") else [],
        "location": f.get("Job Location") or f.get("_place"),
        "job_function": f.get("Job Function"), "industry": f.get("Company Industry"),
        "nationality": f.get("Nationality"),
        "posted_label": f.get("_posted"), "posted": None, "valid_through": None,
        "salary_currency": sal.group(3) if sal else None,
        "salary_min": money(sal.group(1)) if sal else None, "salary_max": money(sal.group(2)) if sal else None,
        "salary_unit": None, "salary_unit_stated": False,
        "direct_apply": None, "jsonld": False,
        "description": (f.get("_description") or "")[:20000] or None, "language": "en",
    }
    found = postings(body)
    if found:
        d = found[0]
        bs = d.get("baseSalary") or {}
        val = bs.get("value") if isinstance(bs, dict) and isinstance(bs.get("value"), dict) else (bs if isinstance(bs, dict) else {})
        unit = (val.get("unitText") or "").strip() or None
        row.update({"jsonld": True, "posted": d.get("datePosted"), "valid_through": d.get("validThrough"),
                    "direct_apply": d.get("directApply"),
                    "salary_unit": unit, "salary_unit_stated": bool(unit)})
        if not row["employer"] and isinstance(d.get("hiringOrganization"), dict):
            row["employer"] = d["hiringOrganization"].get("name")
    else:
        why = absent_reason(body)
        if getattr(why, "our_fault", False):
            die(f"{a.url}: {why.text} **The page announces a JobPosting and this read none.**")
        # the underscore shape carries no JSON-LD at all (2026-09-13); the page fields above are the record
        note(f"{a.url}: no JobPosting on this page ({why.kind}) — page fields only, no datePosted/validThrough.")
    print(json.dumps(row, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="GulfTalent — one country edition through its paginated listing rows and the JobPosting every advertisement carries; the page's own figures printed beside the count, the pager closing under the reader as the witness.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="every advertisement of one edition — 25 a page, 2 s apart, until the pager closes (404); the page's «Jobs found» and panel job_count beside the count")
    l_.add_argument("--country", choices=COUNTRIES, default="uae")
    l_.add_argument("--pages", type=int)
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advertisement, from its JSON-LD")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
