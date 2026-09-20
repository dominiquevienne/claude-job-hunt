#!/usr/bin/env python3
"""SeeMeHired (`seemehired.com`, a Belfast ATS whose employers' vacancies are published on one board for the UK and Ireland): the list `/jobs?page=N` is server-rendered, 12 cards a page, with the count stated in the page («1639 jobs found. Showing page 1 of 137»); the job page carries a JobPosting. Issue #475.

  seemehired.py jobs [--country-code GB|IE] [--max-pages N]
  seemehired.py ad --url https://seemehired.com/jobs/<id>

ONE BOARD, NOT ONE TENANT: the issue named `<company>.seemehired.com`;
measured 2026-09-20, the employers' vacancies live on the vendor's own
board, and the per-company filter (`?company=<slug>`) is ignored by the
permitted list — the filtered list is `/jobs/filtered`, refused in writing
to `*`. So this adapter walks the whole board (137 pages of 12 on
2026-09-20) and `--max-pages` bounds it; the user filters at home. Rules:
`User-agent: *` / `Allow: /` / `Disallow: /jobs/filtered`, `/internal-
opportunities/`, `/healthz`, `/api/`, `/public/indexing/`; `Bytespider`
refused; no Crawl-delay; 2 s between requests are ours.

THE LIST: `<p class="sr-only" role="status">1639 jobs found. Showing page 1
of 137.</p>` (the witness), cards `<a href="/jobs/<id>" aria-label="View
job: <title> at <company> in <place>" posteddate="7 hours ago" status="Full
time">` with tag spans (the schedule, the salary text). THE JOB PAGE: a
schema.org JobPosting — title, identifier (the employer), datePosted,
validThrough, employmentType, hiringOrganization, jobLocation (streetAddress
with the premises' address — not emitted —, addressLocality, addressRegion,
postalCode — not emitted —, addressCountry «GB»), directApply, description.

WITHHELD: the street and the postal code; e-mail addresses and telephone
numbers in the description; the application (a form on the job page);
`contacts_withheld` on every record. The list states no country: the
board is UK & Ireland, the job page says which; `--country-code` on
`jobs` stamps the rows and says so.
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
from _ldjson import postings as ld_postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD = "seemehired"
HOST = "seemehired.com"
BASE = f"https://{HOST}"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE_SIZE = 12

STATUS_RE = re.compile(r"(\d[\d,]*)\s+jobs? found\.\s*Showing page (\d+) of (\d+)", re.I)
NO_JOBS_RE = re.compile(r"\b0 jobs found|No jobs found", re.I)
CARD_RE = re.compile(r'<a href="/jobs/(\d+)"([^>]*)>(.*?)</a>', re.S)
ATTR_RE = re.compile(r'\b(aria-label|posteddate|status)="([^"]*)"')
LABEL_RE = re.compile(r"^View job:\s*(.*?)\s+at\s+(.*?)(?:\s+in\s+(.*?))?\s*$", re.S)
TAG_RE = re.compile(r'<span class="inline-block[^"]*">(.*?)</span>', re.S)
AD_PATH_RE = re.compile(r"^/jobs/(\d+)/?$")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$£€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
_PACE = Pace(HOST, own=2.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[seemehired] {msg}", file=sys.stderr)


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
    if parts.netloc.lower() != HOST:
        die(f"{url}: not the SeeMeHired host — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en-GB,en"})
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


def cards_of(body):
    out = []
    for jid, attrs, inner in CARD_RE.findall(body or ""):
        at = dict(ATTR_RE.findall(attrs))
        m = LABEL_RE.match(htmlmod.unescape(at.get("aria-label", "")))
        tags = [t for t in (text(x) for x in TAG_RE.findall(inner)) if t]
        out.append((jid, {"title": (m.group(1) if m else None), "company": (m.group(2) if m else None), "place": (m.group(3) if m else None),
                          "posted_ago": at.get("posteddate") or None, "schedule": at.get("status") or None,
                          "salary": next((t for t in tags if t != at.get("status") and re.search(r"[£€$]|\d", t)), None), "tags": tags}))
    return out


def row(jid, c, country):
    return {
        "source": BOARD, "ledger_id": f"{BOARD}:{jid}", "id": jid, "url": f"{BASE}/jobs/{jid}",
        "title": c["title"], "company": c["company"], "place": c["place"], "country": country,
        "schedule": c["schedule"], "salary": c["salary"], "posted_ago": c["posted_ago"], "tags": c["tags"],
        "contacts_withheld": True,
    }


def page(number):
    url = f"{BASE}/jobs" + (f"?page={number}" if number > 1 else "")
    st, body = request(url)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    m = STATUS_RE.search(body)
    if not m and not NO_JOBS_RE.search(body):
        die(f"{url}: no «N jobs found. Showing page x of y» in the page — not the board's list, or its shape changed.", EXIT_PARTIAL)
    total = int(m.group(1).replace(",", "")) if m else 0
    current = int(m.group(2)) if m else number
    pages = int(m.group(3)) if m else 1
    return total, current, pages, cards_of(body)


def cmd_jobs(a):
    country = (a.country_code or "").strip().upper() or None
    total, current, pages, cards = page(1)
    rows, seen, walked = [], set(), 1
    while True:
        new = 0
        for jid, c in cards:
            if jid in seen:
                continue
            seen.add(jid)
            rows.append(row(jid, c, country))
            new += 1
        if cards and new == 0:
            die(f"{BASE}/jobs?page={walked}: the page repeated the previous one — the pager is not advancing; {th(len(rows))} kept of the {th(total)} stated.", EXIT_PARTIAL)
        if current != walked:
            die(f"{BASE}/jobs?page={walked}: the page says it is page {current} — the pager is not advancing; {th(len(rows))} kept of the {th(total)} stated.", EXIT_PARTIAL)
        if not cards or walked >= pages or len(rows) >= total or (a.max_pages and walked >= a.max_pages):
            break
        walked += 1
        _t, current, _p, cards = page(walked)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    n = len(rows)
    stamp = f"; country {country} stamped from --country-code (the list states none — the board is UK & Ireland, the job page says which)" if country else ""
    if a.max_pages and walked >= a.max_pages and total > n:
        note(f"{th(n)} emitted of the {th(total)} the board states — {walked} page(s) of {PAGE_SIZE} walked by request (--max-pages) out of {pages}, not a shortfall{stamp}.")
    elif n == total:
        note(f"{th(n)} emitted over {walked} page(s) — the board states {th(total)}: equal{stamp}.")
    else:
        note(f"{th(n)} emitted over {walked} page(s) — the board states {th(total)}: {th(abs(total - n))} " + ("short" if total > n else "more emitted than stated") + f"{stamp}.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    m = AD_PATH_RE.match(parts.path)
    if parts.netloc.lower() != HOST or not m:
        die(f"{a.url!r}: not a SeeMeHired job address ({BASE}/jobs/<id>)")
    url = f"{BASE}/jobs/{m.group(1)}"                       # `?company=…&jobtitle=…` and the like dropped
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped.", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    ps = ld_postings(body)
    if not ps:
        die(f"{url}: no JobPosting in the page — a SeeMeHired job page carries one; the shape changed, or the job is gone.", EXIT_PARTIAL)
    p = ps[0]
    org = p.get("hiringOrganization") if isinstance(p.get("hiringOrganization"), dict) else {}
    loc = p.get("jobLocation") if isinstance(p.get("jobLocation"), dict) else {}
    addr = loc.get("address") if isinstance(loc.get("address"), dict) else {}
    cc = addr.get("addressCountry")
    r = {
        "source": BOARD, "ledger_id": f"{BOARD}:{m.group(1)}", "id": m.group(1), "url": url,
        "title": (p.get("title") or "").strip() or None, "company": (org.get("name") or "").strip() or None,
        "place": (addr.get("addressLocality") or "").strip() or None, "region": (addr.get("addressRegion") or "").strip() or None,
        "country": cc.strip().upper() if isinstance(cc, str) and len(cc.strip()) == 2 else None,
        # streetAddress and postalCode are the premises' address and are not emitted
        "employment_type": p.get("employmentType"), "posted": p.get("datePosted"), "closes": p.get("validThrough"),
        "description": (scrub(text(p.get("description"))) or "")[:20000] or None,
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="SeeMeHired — the vendor's UK & Ireland board: the server-rendered list 12 a page with its count stated, the job page's JobPosting; street and postal code withheld, no contact. Issue #475.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the board's list, 12 a page, 2 s apart, to the stated count (137 pages on 2026-09-20 — bound it)")
    s.add_argument("--country-code", help="GB or IE to stamp the rows with — the list states no country")
    s.add_argument("--max-pages", type=int)
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one job by its page's JobPosting; street and postal code withheld, description scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
