#!/usr/bin/env python3
"""JobNet (`www.jobnet.com.mm`, Myanmar): the country's largest private generalist, «2,077 Jobs Found» stated on its own list. Issue #635.

  jobnetmm.py jobs [--country-code MM] [--max-pages N]     the list (30 a page, 70 pages on 2026-09-22)

WHAT IT IS. A national generalist — banks, manufacturers, NGOs and the agencies advertise there.
**What it changes for Myanmar is the country's coverage, not a count**: the only other route measured
is the State's own portal (`myanmargov.py`, 182 notices of which 181 already closed), so a live
private board is the difference between a market observed and a market inferred.

THE RULES. `www.jobnet.com.mm` answers its rules file and allows both paths: open, `certain: True`,
no Crawl-delay; 2 s is ours. The guard is taken on the exact path.

THE LIST. `/jobs` and `/jobs-in-myanmar` render the same list server-side: **30 `div.serp-item` a
page**, each an `a.search__job-title` to `/job/<slug>/<id>`, a second title line the site prints in
brackets, the employer (`p.search__job-subtitle`), the number of posts («1 Post»), the location, a
«Verified» badge the site awards itself, and excerpts it labels Benefits and Highlights.

**The page prints NO pager link** — and `?page=N` answers anyway: page 2 carries thirty other
adverts, **no id in common with page 1**. *The same shape as Guyana's DPI: the absence of a «next»
link is not the end of the list*, and the walk follows the count the site states — **«2,077 Jobs
Found»**, printed beside what was read on every run.

**THE SALARY IS BEHIND A LOGIN, AND THE RECORD SAYS SO.** Every card shows «Login to view Salary»
pointing at `/login?redirect=…`. The plugin never creates an account and never logs in, so
`salary_behind_login: true` is on every record — *a field that is absent because a site hides it is
not the same as a field the site does not have, and only the record can tell them apart.*

**THE «VERIFIED» BADGE IS NOT CARRIED, AND THE REASON IS A MEASUREMENT.** It appears on **every
card read** (30 of 30 on page 1, 60 of 60 over two pages): *a value that is true of everything
separates nothing*, and a field that never varies reads like information while carrying none. The
run counts it and says so; the record does not hold it.

**WITHHELD:** e-mail addresses and telephone numbers in a title, an employer name or an excerpt;
`contacts_withheld` on every record. `--country-code` STAMPS (the list states no country — every
advert is Myanmar's by the board's own scope, and a stamp is still the user's) and the run says so.

Measured 2026-09-22 12:5x UTC by the declared client, the guard on the exact path: `/jobs` 200
(493 307 B, md5 45e0116c3a21), **«2,077 Jobs Found» stated, 30 cards**; `/jobs-in-myanmar?page=2`
200 (490 433 B), **30 cards, zero shared with page 1**, the same total stated.
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

HOST = "www.jobnet.com.mm"
LIST = f"https://{HOST}/jobs-in-myanmar"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\(?\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
DATE_RE = re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")
STRIP_RE = re.compile(r"(?s)<style.*?</style>|<script.*?</script>")
STATED_RE = re.compile(r"number'>([\d,]+)</span>\s*Jobs Found", re.I)
ITEM_RE = re.compile(r'<div class="serp-item">(.*?)(?=<div class="serp-item">|<div class="search__pagination|\Z)', re.S)
TITLE_RE = re.compile(r'<a[^>]+class="search__job-title[^"]*"[^>]*href="(/job/[^"]+)"[^>]*>(.*?)</a>', re.S)
TITLE2_RE = re.compile(r'<a[^>]+class="search__job-title2[^"]*"[^>]*>(.*?)</a>', re.S)
EMPLOYER_RE = re.compile(r'<p class="search__job-subtitle">(.*?)</p>', re.S)
LOC_RE = re.compile(r'<p class="search__job-location"[^>]*>(.*?)</p>', re.S)
EXCERPT_RE = re.compile(r'<p class="(benefit|highlights)[^"]*">\s*<strong>[^<]*</strong>(.*?)</p>', re.S | re.I)
ID_RE = re.compile(r"/job/[^/]+/(\d+)")
POSTS_RE = re.compile(r"^\s*(\d[\d,]*)\s*Post", re.I)
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobnetmm] {msg}", file=sys.stderr)


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
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    if parts.path.startswith("/login"):
        die(f"{url}: the login page — never requested; the plugin creates no account", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return " ".join(t.split()) or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def stated(markup):
    m = STATED_RE.search(markup or "")
    return int(m.group(1).replace(",", "")) if m else None


def cards_of(markup):
    """The list → [(id, fields)]. The location and the «N Post» share one class, so they are told
    apart by what they SAY — «1 Post» is a count, and a place is not."""
    out = []
    for block in ITEM_RE.findall(STRIP_RE.sub("", markup or "")):
        t = TITLE_RE.search(block)
        if not t:
            continue
        href = htmlmod.unescape(t.group(1))
        ident = ID_RE.search(href)
        if not ident:
            continue
        posts, place = None, None
        for chunk in LOC_RE.findall(block):
            value = text(chunk)
            if not value:
                continue
            m = POSTS_RE.match(value)
            if m and posts is None:
                posts = m.group(1).replace(",", "")
            elif place is None:
                place = value.rstrip(".")
        t2 = TITLE2_RE.search(block)
        emp = EMPLOYER_RE.search(block)
        excerpts = {("benefits" if k.lower().startswith("benefit") else "highlights"): text(v)
                    for k, v in EXCERPT_RE.findall(block)}
        out.append((ident.group(1), {
            "url": urllib.parse.urljoin(LIST, href), "title": text(t.group(2)),
            "title_second": text(t2.group(1)) if t2 else None,
            "employer": text(emp.group(1)) if emp else None,
            "openings": posts, "location": place,
            "verified": "divverified" in block,   # counted, NOT emitted — see below
            "benefits": excerpts.get("benefits"), "highlights": excerpts.get("highlights"),
        }))
    return out


def record(ident, f, stamp):
    return {
        "source": "jobnetmm", "country": stamp,
        "ledger_id": f"jobnetmm:{ident}", "id": ident,
        "title": scrub(f.get("title")), "title_second": scrub(f.get("title_second")),
        "employer": scrub(f.get("employer")),
        "location": f.get("location"), "openings": f.get("openings"),
        "benefits": scrub(f.get("benefits")), "highlights": scrub(f.get("highlights")),
        "url": f.get("url"),
        "salary_behind_login": True,   # «Login to view Salary» on every card; no account is ever created
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    rows, seen, page, said, ended, verified = [], set(), 1, None, None, 0
    while True:
        url = LIST if page == 1 else f"{LIST}?page={page}"
        code, body = request(url)
        if code == 404:
            die(f"{url}: HTTP 404 — the list is gone", EXIT_GONE)
        if code != 200:
            die(f"{url}: HTTP {code} — the walk ended at {th(len(seen))}", EXIT_PARTIAL)
        if page == 1:
            said = stated(body)
        found = cards_of(body)
        if not found:
            if page == 1:
                die(f"{url}: 200 without a single advert card — the page changed; not an empty board", EXIT_PARTIAL)
            ended = f"page {page} carried no card"
            page -= 1
            break
        keys = {i for i, _f in found}
        if page > 1 and keys <= seen:
            die(f"page {page} repeats the adverts of the page before — the walk ended at {th(len(seen))}", EXIT_PARTIAL)
        for ident, f in found:
            if ident in seen:
                continue
            seen.add(ident)
            verified += 1 if f.get("verified") else 0
            rows.append(record(ident, f, stamp))
        if said is not None and len(seen) >= said:
            ended = f"the {th(said)} the board states were read"
            break
        if a.max_pages and page >= a.max_pages:
            ended = f"stopped by --max-pages at page {page}"
            break
        page += 1
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if said is None:
        note(f"{th(len(rows))} emitted over {th(page)} page(s); **the board stated no count this time** — it usually prints «N Jobs Found», and the run says so rather than claiming one. {ended or ''}")
    elif said != len(seen):
        note(f"{th(len(seen))} read over {th(page)} page(s), the board states {th(said)} — {th(abs(said - len(seen)))} {'short' if said > len(seen) else 'more'}; {ended}.")
    else:
        note(f"{th(len(seen))} read over {th(page)} page(s), and the board states {th(said)} — they agree; {ended}.")
    note("the board prints NO pager link and `?page=N` answers anyway — a walk that trusted the markup would stop at the first 30.")
    note(f"the board's «Verified» badge is on {th(verified)} of the {th(len(seen))} adverts read — **it separates nothing**, so it is counted here and NOT carried as a field: a value that is true of everything measures nothing.")
    note("the salary is behind a login on every card: `salary_behind_login: true`, and no account is ever created — a field hidden by a site is not a field the site lacks.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the list states no country.")


def main(argv=None):
    p = argparse.ArgumentParser(description="JobNet (Myanmar) — the national generalist, walked against the count it states. Issue #635.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the list (30 a page)")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the list states none)")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0, help="stop after N pages (0 = until the stated count is read)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
