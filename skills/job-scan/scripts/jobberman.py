#!/usr/bin/env python3
"""Jobberman / BrighterMonday (ROAM Africa) — one file, three hosts: `www.jobberman.com` (Nigeria), `www.brightermonday.co.ke` (Kenya), `www.brightermonday.co.ug` (Uganda); the listings sitemap the rules declare, the listing's own «N Jobs Found» beside every walk, the ten pages the rules allow. Issue #390.

  jobberman.py sitemap [--host www.brightermonday.co.ke] [--limit N] [--since YYYY-MM-DD]
  jobberman.py recent  [--host …] [--pages N] [--limit N]
  jobberman.py ad --url <https://www.jobberman.com/listings/<slug>-<id>>

ONE TEMPLATE, THREE RULES FILES THAT SAY THE SAME THING (2026-09-13
17:50 UTC): `*` refuses `/job/`, `/api/`, `/ajax/` and every facet query
(`/*q=*`, `/*industry=*`, `/*sort=*`, `/*page=*` …) and **allows
`page=2` … `page=10` by name** — so the listing walk stops at page 10
(160 cards) by the rules, not by choice, and says so. The four declared
sitemaps include `/sitemap-listings-index-en.xml`, an index of **27
category files** of `/listings/<slug>-<id>` with a `<lastmod>` each; an
advertisement filed under two categories appears in two files and is
keyed by its trailing id (six characters, `-x8gn9q`).

THE COUNT IS THE LISTING'S: `/jobs` (open) states «4,194 Jobs Found» on
Nigeria, «1,895» Kenya, «1,025» Uganda on the day, 16 cards a page, a
pager to 263 / 119 / 65. `sitemap` reads it once and prints it beside
the file's distinct count; `recent` reads it on every page.

THE CARD: title, employer, location, job type, salary («NGN 70,000 -
150,000» — a range with a currency and **no period on the card**; emitted
with `salary_unit_stated: false`), function, «2 days ago» as printed, a
numeric id in the card's `aria-labelledby` beside the slug id. THE
ADVERTISEMENT PAGE carries no JobPosting (a WebPage/Organization/Person
JSON-LD — the site's own, not the job's): the fields are read from the
page — the breadcrumbs (function, industry, location, type), the salary
line, «Job summary», the labelled facts (Min Qualification, Experience
Level/Length, Language Requirement, Working Hours, Applicant Location)
and «Job descriptions & requirements». Applications are «Log In and
Apply»; no contact is on the page and none is read.
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

HOSTS = {
    "www.jobberman.com": ("jobberman", "NG", "NGN"),
    "www.brightermonday.co.ke": ("brightermonday-ke", "KE", "KES"),
    "www.brightermonday.co.ug": ("brightermonday-ug", "UG", "UGX"),
}
DEFAULT_HOST = "www.jobberman.com"
AD_RE = re.compile(r"^https://(www\.(?:jobberman\.com|brightermonday\.co\.(?:ke|ug)))/listings/([a-z0-9][a-z0-9-]*?)-([a-z0-9]{6})/?$")
FOUND_RE = re.compile(r"(\d[\d,]*)\s*Jobs?\s+Found", re.I)
CARD_RE = re.compile(r'aria-labelledby="job-(\d+)-title"(.*?)(?=aria-labelledby="job-\d+-title"|data-cy="pagination|</main>)', re.S)
PAGES_ALLOWED = 10        # the rules allow page=2 … page=10 by name and refuse /*page=* otherwise
PAGE_SIZE = 16

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobberman] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def get(url):
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()   # no Crawl-delay in the rules; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9", "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h\d>|</span>|</a>|</strong>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def host_of(a):
    h = getattr(a, "host", None) or DEFAULT_HOST
    if h not in HOSTS:
        die(f"{h}: not one of this family's hosts — {', '.join(HOSTS)}")
    return h


def jobs_found(body):
    m = FOUND_RE.search(htmlmod.unescape(re.sub(r"<[^>]+>", " ", body or "")))
    return int(m.group(1).replace(",", "")) if m else None


def salary(s):
    """«NGN 400,000 - 600,000» → (currency, min, max); a single figure → (currency, n, n)."""
    m = re.search(r"\b([A-Z]{3})\s*(\d[\d,]*)(?:\s*-\s*(\d[\d,]*))?", s or "")
    if not m:
        return None, None, None
    lo = int(m.group(2).replace(",", ""))
    return m.group(1), lo, int(m.group(3).replace(",", "")) if m.group(3) else lo


def cards(body, host):
    """The listing's cards, by their structure: the title link, then the employer <p>, then a row of <span>
    (location, type, «CUR <span>range</span>»), then the function <p>, then «N days ago» — as the card is built."""
    out = []
    for m in CARD_RE.finditer(body or ""):
        num, inner = m.group(1), m.group(2)
        link = re.search(r'<a\s+href="(https://%s/listings/[^"?#]+)"[^>]*data-cy="listing-title-link"[^>]*>(.*?)</a>' % re.escape(host), inner, re.S)
        if not link:
            continue
        mm = AD_RE.match(link.group(1))
        if not mm:
            continue
        after = inner[link.end():]
        ps = [text(x) for x in re.findall(r"<p[^>]*>(.*?)</p>", after, re.S)]
        spans = [text(x) for x in re.findall(r"<span[^>]*>(.*?)</span>", after[:after.find("</p>", after.find("</p>") + 1)] if after.count("</p>") > 1 else after, re.S)]
        spans = [x for x in spans if x and not re.fullmatch(r"[\d,]+(?:\s*-\s*[\d,]+)?", x)]
        sal_line = next((x for x in spans if re.search(r"\b[A-Z]{3}\b", x)), "")
        cur, lo, hi = salary(text(re.sub(r"</?span[^>]*>", " ", (re.search(r"<span[^>]*>\s*([A-Z]{3}\s*<span[^>]*>[^<]*</span>)", after) or [None, sal_line])[1])))
        age = next((x for x in ps if re.search(r"\b(ago|today|yesterday)\b", x, re.I)), None)
        out.append({"id": mm.group(3), "numeric_id": num, "url": link.group(1),
                    "title": text(link.group(2)) or None, "employer": ps[0] if ps else None,
                    "location": spans[0] if spans else None, "job_type": spans[1] if len(spans) > 1 else None,
                    "function": ps[1] if len(ps) > 1 and not re.search(r"\bago\b", ps[1]) else None,
                    "salary_currency": cur, "salary_min": lo, "salary_max": hi, "posted_label": age,
                    "excerpt": next((x for x in ps if len(x) > 80), None)})
    return out


def row(host, c):
    source, iso, _ = HOSTS[host]
    return {"source": source, "country": iso, "ledger_id": f"{source}:{c['id']}", "id": c["id"], "numeric_id": c.get("numeric_id"),
            "url": c["url"], "title": c.get("title"), "employer": c.get("employer"), "location": c.get("location"), "job_type": c.get("job_type"), "function": c.get("function"),
            "salary_currency": c.get("salary_currency"), "salary_min": c.get("salary_min"), "salary_max": c.get("salary_max"),
            # a range with a currency and no period on the card: «read as monthly» is not «stated»
            "salary_unit": None, "salary_unit_stated": False, "posted_label": c.get("posted_label"), "excerpt": c.get("excerpt"), "language": "en"}


def cmd_sitemap(a):
    host = host_of(a)
    source, iso, _ = HOSTS[host]
    code, body = get(f"https://{host}/sitemap-listings-index-en.xml")
    if code != 200:
        die(f"https://{host}/sitemap-listings-index-en.xml: HTTP {code}", EXIT_PARTIAL)
    files = [htmlmod.unescape(u) for u in re.findall(r"<loc>\s*([^<]+?)\s*</loc>", body)]
    if not files:
        die(f"https://{host}/sitemap-listings-index-en.xml: no file in the index ({len(body)} characters)", EXIT_PARTIAL)
    rows, seen, twice, per_file = [], {}, 0, []
    for f in files:
        code, xml = get(f)
        if code != 200:
            die(f"{f}: HTTP {code} — {th(len(rows))} read before it; a partial walk is not a count.", EXIT_PARTIAL)
        n_here = 0
        for m in re.finditer(r"<url>\s*<loc>\s*([^<]+?)\s*</loc>(.*?)</url>", xml, re.S):
            u = htmlmod.unescape(m.group(1))
            mm = AD_RE.match(u)
            if not mm:
                continue
            n_here += 1
            if mm.group(3) in seen:
                twice += 1
                continue
            lm = re.search(r"<lastmod>\s*([^<]+?)\s*</lastmod>", m.group(2))
            seen[mm.group(3)] = True
            if a.since and lm and lm.group(1)[:10] < a.since:
                continue
            rows.append({"source": source, "country": iso, "ledger_id": f"{source}:{mm.group(3)}", "id": mm.group(3), "url": u,
                         "lastmod": lm.group(1) if lm else None, "category_file": f.rsplit("/", 1)[-1]})
        per_file.append(n_here)
    if not seen:
        die(f"{len(files)} file(s) and no advertisement address matched — a reading fault, not an empty board.", EXIT_PARTIAL)
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    note(f"**{th(len(seen))} distinct advertisement id(s)** over {len(files)} category file(s) ({th(sum(per_file))} entries, {th(twice)} filed under a second category); "
         f"{th(len(emitted))} emitted" + (f" dated on or after {a.since}" if a.since else "") + (f" (--limit {a.limit})" if a.limit else "") + ".")
    code, page = get(f"https://{host}/jobs")
    stated = jobs_found(page) if code == 200 else None
    if stated is None:
        note(f"/jobs answered HTTP {code} without «Jobs Found» — no second source this run.")
    elif stated == len(seen):
        note(f"{th(len(seen))} in the sitemap, the listing states {th(stated)} «Jobs Found» — equal.")
    else:
        note(f"{th(len(seen))} in the sitemap, the listing states {th(stated)} «Jobs Found» — {th(abs(stated - len(seen)))} " + ("more in the listing" if stated > len(seen) else "more in the sitemap") + "; the files are rebuilt hourly (their lastmod), the listing is live.")


def cmd_recent(a):
    host = host_of(a)
    rows, seen, stated, page = [], set(), None, 1
    limit_pages = min(a.pages or PAGES_ALLOWED, PAGES_ALLOWED)
    while True:
        url = f"https://{host}/jobs" + (f"?page={page}" if page > 1 else "")
        code, body = get(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if stated is None:
            stated = jobs_found(body)
        found = cards(body, host)
        if page == 1 and not found:
            die(f"{url}: no card read on the first page ({len(body)} characters, {body.count('listing-cards-components')} card component(s)) — a reading fault, not an empty board.", EXIT_PARTIAL)
        new = 0
        for c in found:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            rows.append(row(host, c))
            new += 1
        if not found or new == 0:
            break
        if page >= limit_pages or (a.limit and len(rows) >= a.limit):
            break
        page += 1
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    if stated is None:
        note(f"{th(n)} emitted over {page} page(s); the listing states no «Jobs Found» this run — no second source.")
    elif n >= stated:
        note(f"{th(n)} emitted over {page} page(s), the listing states {th(stated)} «Jobs Found» — " + ("equal" if n == stated else "more emitted than stated") + ".")
    else:
        note(f"{th(n)} emitted of the {th(stated)} the listing states «Jobs Found» — {page} page(s) of {PAGE_SIZE}; the rules allow page=2…{PAGES_ALLOWED} by name and refuse the rest, so the listing walk ends here by the rules; `sitemap` is the whole.")


def cmd_ad(a):
    m = AD_RE.match((a.url or "").strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected https://<host>/listings/<slug>-<id> on one of {', '.join(HOSTS)}")
    host, ident = m.group(1), m.group(3)
    source, iso, _ = HOSTS[host]
    code, body = get(a.url)
    if code in (404, 410):
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    i = body.find('data-cy="breadcrumbs"')
    if i < 0:
        die(f"{a.url}: no breadcrumbs on the page ({len(body)} characters) — not an advertisement page as read.", EXIT_PARTIAL)
    t = text(body[i:])
    lines = [l for l in t.split("\n") if l.strip()]
    # the breadcrumbs are anchors: function, industry (?industry=), location, type — the home link is a glyph
    crumbs = [text(x) for h, x in re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', body[i:i + 8000], re.S) if "/jobs" in h]
    title = text((re.search(r'data-cy="title-job"[^>]*>(.*?)</', body, re.S) or re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S) or [None, ""])[1]) or None
    employer = text((re.search(r"<h2[^>]*>(.*?)</h2>", body[i:], re.S) or [None, ""])[1]) or None
    cur, lo, hi = salary(next((l for l in lines if re.search(r"\b[A-Z]{3}\s*\d[\d,]*", l)), "") or " ".join(lines[:40]))
    facts = {}
    for k in ("Min Qualification", "Experience Level", "Experience Length", "Language Requirement", "Working Hours", "Applicant Location"):
        fm = re.search(re.escape(k) + r":\s*\n\s*([^\n]+)", t)
        if fm:
            facts[k] = fm.group(1).strip()
    summ = re.search(r"Job summary\s*\n(.*?)\n(?:Min Qualification|Experience Level|Job descriptions)", t, re.S)
    desc = re.search(r"Job descriptions & requirements\s*\n(.*?)(?:\nLog In and Apply|\nImportant safety tips|$)", t, re.S)
    age = next((l for l in lines[:30] if re.search(r"\b(ago|today|yesterday)\b", l, re.I)), None)
    print(json.dumps({
        "source": source, "country": iso, "ledger_id": f"{source}:{ident}", "id": ident, "url": a.url,
        "title": title, "employer": employer, "breadcrumbs": crumbs[:5],
        "function": crumbs[0] if crumbs else None, "industry": crumbs[1] if len(crumbs) > 1 else None,
        "location": crumbs[2] if len(crumbs) > 2 else None, "job_type": crumbs[3] if len(crumbs) > 3 else None,
        "salary_currency": cur, "salary_min": lo, "salary_max": hi, "salary_unit": None, "salary_unit_stated": False,
        "posted_label": age, "facts": facts,
        "summary": summ.group(1).strip() if summ else None,
        "description": (desc.group(1).strip() if desc else "")[:20000] or None, "language": "en",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Jobberman / BrighterMonday (ROAM Africa) — three hosts, one file: the declared listings sitemap (27 category files, ids deduped), the listing's «N Jobs Found» beside every walk, the ten pages the rules allow, the advertisement page's own fields. Issue #390.")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, help_ in (("sitemap", cmd_sitemap, "every advertisement id with its lastmod and category file — 28 requests; the listing's «Jobs Found» beside the count"),
                            ("recent", cmd_recent, "the listing, 16 a page, pages 1–10 as the rules allow; the count beside it")):
        s = sub.add_parser(name, help=help_)
        s.add_argument("--host", default=DEFAULT_HOST, choices=sorted(HOSTS))
        s.add_argument("--limit", type=int)
        if name == "sitemap":
            s.add_argument("--since")
        else:
            s.add_argument("--pages", type=int)
        s.set_defaults(fn=fn)
    d = sub.add_parser("ad", help="one advertisement page — fields read from the page; no JobPosting on it, no contact on it")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
