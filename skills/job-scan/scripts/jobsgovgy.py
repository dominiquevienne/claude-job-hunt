#!/usr/bin/env python3
"""National Job Bank (`jobs.gov.gy`, Guyana's Ministry of Labour): the search its own «See all jobs» button submits states the count («187 Jobs Found») and shows twenty; its pager is a script the rules refuse to read, so the board is walked by the site's own categories — each below twenty — and the union compared to the stated count; the advert page carries a JobPosting. Issue #314.

  jobsgovgy.py list [--category ID …] [--no-categories]
  jobsgovgy.py ad --url https://jobs.gov.gy/<id>/<slug>.html

THE RULES (1 181 B, read 2026-09-21): `User-agent: *` refuses the
application's own directories — `/language/`, `/jscript/`, `/css/`,
`/uploads/`, `/resume/`… — and a few files; `/job_search.php`,
`/job_search_by_industry.php`, `/<id>/<slug>.html` and `/rss/` are open.
**The pager lives in `/language/english/jscript/page.js`** —
`jobsearch_pagination(20, …)` on the list — **and `/language/` is refused
in writing: the script is not read, its parameter is not guessed** (twelve
plausible names were tried as form fields on 2026-09-21 and every one
answered page 1). No Crawl-delay; 2 s between requests are ours, and the
server itself answers a search in five to seven seconds.

THE ROUTE, MEASURED 2026-09-21 07:02–07:19 UTC, the declared client. The
form the home page's «See all jobs» button submits — `POST
/job_search.php`, `action=search`, nothing else — answers **«187 Jobs
Found»** and twenty cards (`div.previewBox#<id>`: title, employer, region,
type, salary in GYD, experience bracket, a teaser, «Posted: 18th Sep, 2026
— Ends : 01st Nov, 2026»); the cards carry no link — the advert's address
is `/<id>/<slug>.html`, the `<id>` being the box's, any slug served. The
site's «By Category» page (`/job_search_by_industry.php`) lists 89
categories with their live counts (57 non-empty, the largest 20 — Drivers),
each a form `job_category[]=<id>` to the same search: **57 searches,
187 distinct ids, equal to the stated 187** (a job carries several
categories: the counts sum to 214). A category above twenty would be
truncated by the pager this adapter cannot follow — its «Jobs Found»
against its cards is checked on every search and any shortfall named.
The RSS (`/rss/all_jobs.xml` 30 items, `/rss/<n>.xml` ten at most, 89
feeds → 162 distinct) links `/<id>/<slug>.html` with ids of another
numbering that answer the home page: not the route.

THE ADVERT (`/<id>/<slug>.html`, 200, ~35 KB): a `JobPosting` — `title`,
`hiringOrganization.name` (and its logo), `datePosted`, `baseSalary.value`,
`employmentType`, `jobLocation.address.addressCountry: GY`,
`description` (HTML, entity-escaped inside the JSON) and
`disambiguatingDescription` (text) — and the page's labelled fields:
the location line («Georgetown, Guyana»), Experience, Job category,
Salary («220000 GYD»), «Apply before», Job Type, Posted Date. **An id the
site does not have answers 200 with the home page** — no JobPosting, exit 3.

WITHHELD: the description scrubbed of e-mail addresses and telephone
numbers; the employer's logo never emitted; the application
(`apply_now.php`, an account) never touched; `contacts_withheld` on every
record. The country is GY on every row.
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
from _ldjson import label, one, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD, HOST, COUNTRY = "jobsgovgy", "jobs.gov.gy", "GY"
BASE = f"https://{HOST}"
SEARCH = BASE + "/job_search.php"
BY_INDUSTRY = BASE + "/job_search_by_industry.php"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE = 20

FOUND_RE = re.compile(r"(\d[\d,]*)\s+Jobs Found")
BOX_RE = re.compile(r'<div class="previewBox[^"]*" id="(?P<id>\d+)">(?P<body>.*?)(?=<div class="previewBox|<div class="card-footer)', re.S)
H5_RE = re.compile(r"<h5[^>]*>(.*?)</h5>", re.S)
SPAN_RE = re.compile(r'<span class="\s*text-muted[^"]*">(.*?)</span>', re.S)
TEASER_RE = re.compile(r'<div class="text-muted mt-1">(.*?)</div>', re.S)
POSTED_RE = re.compile(r"Posted:\s*([^<]+?)\s*</span>", re.S)
ENDS_RE = re.compile(r"Ends\s*:\s*([^<]+?)\s*</span>", re.S)
CAT_FORM_RE = re.compile(r'<form name="search"[^>]*>(.*?)</form>', re.S)
CAT_ID_RE = re.compile(r'name="job_category\[\]" value="(\d+)"')
CAT_COUNT_RE = re.compile(r"\((\d+)\)")
DL_RE = re.compile(r"(Experience|Job category|Salary|Apply before|Job Type|Posted Date)\s*:?\s*</[^>]+>\s*(?:<[^>]+>\s*)*([^<]+)", re.S)
LOC_RE = re.compile(r">\s*([^<>]{2,80}?,\s*Guyana)\s*<", re.S)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
_PACE = Pace(HOST, own=2.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobsgovgy] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, data=None):
    """(status, body) — this host only, the guard first, 2 s apart; `data` makes it the form POST the site's own buttons send."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc.lower() != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    headers = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en"}
    body = urllib.parse.urlencode(data, doseq=True).encode("utf-8") if data is not None else None
    if body is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(wire_url(url), data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
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


def status_of(st, url):
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)


def parse_search(body):
    """(stated, cards) — stated None when the page prints no «Jobs Found»; cards [] on an empty result."""
    m = FOUND_RE.search(body or "")
    stated = int(m.group(1).replace(",", "")) if m else None
    cards = []
    for b in BOX_RE.finditer(body or ""):
        seg = re.sub(r"<form.*?</form>", " ", b.group("body"), flags=re.S)   # the skill-tag forms and the apply form
        h5 = H5_RE.search(seg)
        spans = [text(x) for x in SPAN_RE.findall(seg)]   # positional — an empty span (no job type) stays None so the salary keeps its place
        teaser = TEASER_RE.search(seg)
        posted, ends = POSTED_RE.search(seg), ENDS_RE.search(seg)
        cards.append({"id": b.group("id"), "title": text(h5.group(1)) if h5 else None,
                      "company": spans[0] if len(spans) > 0 else None, "place": spans[1] if len(spans) > 1 else None,
                      "kind": spans[2] if len(spans) > 2 else None, "salary": spans[3] if len(spans) > 3 else None, "experience": spans[4] if len(spans) > 4 else None,
                      "teaser": text(teaser.group(1)) if teaser else None,
                      "posted": text(posted.group(1)) if posted else None, "closes": text(ends.group(1)) if ends else None})
    return stated, cards


def parse_categories(body):
    """[(id, label, count)] from the «By Category» page — the forms it carries, each with its live count in brackets."""
    out = []
    for f in CAT_FORM_RE.findall(body or ""):
        cid = CAT_ID_RE.search(f)
        if not cid:
            continue
        lab = " ".join(htmlmod.unescape(re.sub(r"<[^>]+>", " ", f)).split())
        cnt = CAT_COUNT_RE.search(lab)
        out.append((cid.group(1), CAT_COUNT_RE.sub("", lab).strip(), int(cnt.group(1)) if cnt else 0))
    return out


def row(c):
    return {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{c['id']}", "id": c["id"], "url": f"{BASE}/{c['id']}/{re.sub(r'[^A-Za-z0-9]+', '-', c['title'] or 'job').strip('-') or 'job'}.html",
            "title": c["title"], "company": c["company"], "place": c["place"], "kind": c["kind"], "salary": c["salary"], "experience": c["experience"],
            "posted": c["posted"], "closes": c["closes"], "teaser": scrub(c["teaser"]), "contacts_withheld": True}


def cmd_list(a):
    st, body = request(SEARCH, {"action": "search"})
    status_of(st, SEARCH)
    stated, cards = parse_search(body)
    if stated is None and not cards:
        die(f"{SEARCH}: no «Jobs Found» and no card in the answer — not the search page, or the page changed shape.", EXIT_PARTIAL)
    seen, out, shortfalls = set(), [], []
    for c in cards:
        if c["id"] not in seen:
            seen.add(c["id"])
            out.append(row(c))
    if not a.no_categories and (stated is None or stated > len(out)):
        st, body = request(BY_INDUSTRY)
        status_of(st, BY_INDUSTRY)
        cats = [(i, lab, n) for i, lab, n in parse_categories(body) if n > 0 and (not a.category or i in a.category)]
        if not cats and not a.category:
            die(f"{BY_INDUSTRY}: no category form on the page — the walk has no route.", EXIT_PARTIAL)
        for cid, lab, n in cats:
            st, body = request(SEARCH, {"action": "search", "job_category[]": cid})
            status_of(st, SEARCH)
            cstated, ccards = parse_search(body)
            if cstated is not None and cstated > len(ccards):
                shortfalls.append(f"{lab} ({cid}): {th(cstated)} found, {len(ccards)} shown")
            for c in ccards:
                if c["id"] not in seen:
                    seen.add(c["id"])
                    out.append(row(c))
            if stated is not None and len(out) >= stated and not a.category:
                break
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    if shortfalls:
        note("categories beyond one page — the pager is a script the rules refuse (/language/): " + "; ".join(shortfalls) + ".")
    if a.category:
        note(f"{th(n)} emitted from {len(a.category)} categor{'y' if len(a.category) == 1 else 'ies'} — a filtered walk, not compared to the board's {th(stated) if stated is not None else '?'}.")
    elif stated is None:
        note(f"{th(n)} emitted — the page states no count.")
    elif n == stated:
        note(f"{th(n)} emitted — the site states {th(stated)}: equal.")
    else:
        note(f"{th(n)} emitted — the site states {th(stated)}: {th(abs(stated - n))} " + ("short" if stated > n else "more emitted than stated") + ("" if not a.no_categories else " (--no-categories: the first page only)") + ".")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    m = re.fullmatch(r"/(\d+)/([^/]+)\.html", parts.path or "")
    if parts.netloc.lower() != HOST or not m:
        die(f"{a.url!r}: not a National Job Bank advert address (https://{HOST}/<id>/<slug>.html)")
    jid = m.group(1)
    url = f"{BASE}/{jid}/{m.group(2)}.html"
    st, body = request(url)
    status_of(st, url)
    found = postings(body)
    if not found:
        die(f"{url}: no JobPosting in the page — the site answers its home page for an id it does not have: gone, or never an advert.", EXIT_GONE)
    p = found[0]
    org = one(p.get("hiringOrganization"))
    fields = {k: text(v) for k, v in DL_RE.findall(body)}
    loc = LOC_RE.search(body)
    desc = htmlmod.unescape(label(p.get("description")) or "")
    r = {
        "source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{jid}", "id": jid, "url": url,
        "title": label(p.get("title")), "company": label(org) if org else None,
        "place": text(loc.group(1)) if loc else None,
        "posted": (label(p.get("datePosted")) or "").strip() or None, "posted_as_written": fields.get("Posted Date"), "closes": fields.get("Apply before"),
        "employment_type": label(p.get("employmentType")) or fields.get("Job Type"),
        "salary": fields.get("Salary") or (label(one(p.get("baseSalary")), "value") if one(p.get("baseSalary")) else None),
        "experience": fields.get("Experience"), "category": fields.get("Job category"),
        "description": (scrub(text(desc)) or scrub(htmlmod.unescape(label(p.get("disambiguatingDescription")) or "")) or "")[:20000] or None,
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="National Job Bank (Guyana) — the site's own search and its categories walked to the stated count; the advert's JobPosting; no contact. Issue #314.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="the search the site's button submits, then each non-empty category, the union compared to «N Jobs Found»")
    s.add_argument("--category", action="append", metavar="ID", help="walk this category only (repeatable)")
    s.add_argument("--no-categories", action="store_true", help="the first twenty only")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advert by its address; description scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
