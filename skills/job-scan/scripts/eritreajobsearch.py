#!/usr/bin/env python3
"""Eritrea Job Search (`eritreajobsearch.com`, a node of the `*jobsearch.com` network operated from India): the only host naming Eritrea that publishes a list — «468 Jobs Available» in its own counter — read by the site's own per-page form (`?jobs_ppp=384`, its largest option) and its pager, the advert's JobPosting; and a SUSPICION FLAG on every row, because the adverts bear the marks of fabrication and nobody has established it either way (#549, the owner's decision: «pourquoi les écarter ?»).

  eritreajobsearch.py jobs [--per-page 384]
  eritreajobsearch.py ad --url https://eritreajobsearch.com/job/<slug>/

THE SIGNS, CONSIGNED WITHOUT VERDICT (13.09 and 21.09.2026): titles at one
template «<role> Job Vacancy in <town>, Eritrea – <sector>»; international
employers (Deloitte, Huawei Technologies) placed in border towns (Zalambessa,
Dekemhare); salaries printed in SSP (South Sudanese pound) while the
JobPosting says `currency: Nfk`; a generated «Company Overview» in every
advert; one to six views each; no application route — «Please Register here
as Candidate to apply», a paid «Pricing» page; the network's own contacts
(+91) on every page. **Every row carries `source_signals` with the date and
these marks**; the measurement that would settle it — an employer confirming
or denying one advert — has not been made.

THE RULES (2026-09-21): `User-agent: *` refuses the WooCommerce internals and
`add-to-cart` queries; `/job-vacancy-eritrea/`, `/job/<slug>/` and the
`jobs_ppp` query are open; no Crawl-delay; 2 s between requests are ours.

THE ROUTE, MEASURED 2026-09-21 09:16–09:17 UTC, the declared client:
`/job-vacancy-eritrea/` 200 (230 KB) — ten `article.job-grid.post-<id>` cards
(title, `/job/<slug>/`, `.job-location`, `.type-job`, views), a pager to
`/page/47/`, the site's counter `.job-count-number` **468** («Total Active
Jobs in Eritrea … Jobs Available»; 456 on 2026-09-13); the page's own
per-page form (`GET ?jobs_ppp=12|24|48|96|192|384|-1`): `?jobs_ppp=384` 200
(875 KB), 384 cards, a pager to `/page/2/?jobs_ppp=384`. The advert
(`/job/<slug>/`, 148 KB): a JobPosting — `title`, `datePosted`,
`validThrough`, `hiringOrganization.name`, `jobLocation.address`,
`baseSalary` (currency Nfk, min/max), `description` (entity-escaped) — and
the page's labelled paragraphs; **an unknown slug answers 200 with the
LISTING page** (no JobPosting, the counter present) — exit 3. The same
salary line «SSP 1,500,000 – SSP 2,500,000 per annum» sits in the attorney's
and the network engineer's adverts alike.

WITHHELD: the network's e-mail addresses and telephones (scrubbed wherever
they appear), the registration link; `contacts_withheld` on every record.
Country ER on every row.
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

BOARD, HOST, COUNTRY = "eritreajobsearch", "eritreajobsearch.com", "ER"
BASE = f"https://{HOST}"
LISTING = BASE + "/job-vacancy-eritrea/"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PER_PAGE_OPTIONS = (12, 24, 48, 96, 192, 384)
MAX_PAGES = 200
SIGNALS = ["fabrication-suspected (2026-09-21): titles at one template, international employers in border towns, salaries in a foreign currency (SSP) against a JobPosting in Nfk, a generated company overview in every advert, no application route — consigned in #549, not established"]

COUNT_RE = re.compile(r'class="job-count-number">\s*([\d,]+)\s*<')
CARD_RE = re.compile(r'<article class="map-item job-grid post-(?P<id>\d+)[^"]*"(?P<attrs>[^>]*)>(?P<body>.*?)</article>', re.S)
TITLE_RE = re.compile(r'<h2 class="job-title"><a href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>', re.S)
LOC_RE = re.compile(r'<div class="job-location">(.*?)</div>', re.S)
TYPE_RE = re.compile(r'<a class="type-job"[^>]*>(.*?)</a>', re.S)
VIEWS_RE = re.compile(r'class="job-views">\s*[^\d<]*(\d+)\s*views')
NEXT_RE = re.compile(r'href="(https://eritreajobsearch\.com/job-vacancy-eritrea/page/(\d+)/[^"]*)"')
DESC_RE = re.compile(r'<div class="job-detail-description">\s*<h3 class="title">[^<]*</h3>(?P<body>.*?)(?=<div class="job-detail-(?!description)|<aside|<div class="sidebar)', re.S)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
_PACE = Pace(HOST, own=2.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[eritreajobsearch] {msg}", file=sys.stderr)


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


def request(url):
    """(status, body) — this host only, the guard first, 2 s apart."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc.lower() != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
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


def parse_listing(body):
    """(stated, cards, next_url) — stated from the site's own counter (None when absent), next_url the pager's next page or None."""
    m = COUNT_RE.search(body or "")
    stated = int(m.group(1).replace(",", "")) if m else None
    cards = []
    for c in CARD_RE.finditer(body or ""):
        t = TITLE_RE.search(c.group("body"))
        if not t:
            continue
        loc, typ, views = LOC_RE.search(c.group("body")), TYPE_RE.search(c.group("body")), VIEWS_RE.search(c.group("body"))
        cards.append({"id": c.group("id"), "url": t.group("url"), "title": text(t.group("title")), "place": text(loc.group(1)) if loc else None,
                      "kind": text(typ.group(1)) if typ else None, "views": int(views.group(1)) if views else None})
    return stated, cards, None


def next_of(body, page):
    for url, n in NEXT_RE.findall(body or ""):
        if int(n) == page + 1:
            return htmlmod.unescape(url)
    return None


def row(c):
    slug = urllib.parse.urlsplit(c["url"]).path.strip("/").split("/")[-1]
    return {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{c['id']}", "id": c["id"], "url": c["url"], "slug": slug,
            "title": c["title"], "place": c["place"], "kind": c["kind"], "views": c["views"],
            "source_signals": list(SIGNALS), "contacts_withheld": True}


def cmd_jobs(a):
    if a.per_page not in PER_PAGE_OPTIONS:
        die(f"--per-page {a.per_page}: not one of the form's own options {PER_PAGE_OPTIONS}")
    seen, out, stated, page = set(), [], None, 1
    url = f"{LISTING}?jobs_ppp={a.per_page}"
    while page <= MAX_PAGES:
        st, body = request(url)
        status_of(st, url)
        s, cards, _ = parse_listing(body)
        if page == 1:
            stated = s
            if not cards and "job-vacancy-eritrea" not in (body or ""):
                die(f"{url}: no card and no listing shell in the answer — not the listing, or the page changed shape.", EXIT_PARTIAL)
        new = 0
        for c in cards:
            if c["id"] not in seen:
                seen.add(c["id"])
                out.append(row(c))
                new += 1
        if page > 1 and new == 0 and cards:
            note(f"page {page}: only repeats — stopped.")
            break
        nxt = next_of(body, page)
        if not nxt or not cards:
            break
        url, page = nxt, page + 1
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    note(f"every row carries source_signals — {SIGNALS[0].split(':')[0]}; see #549.")
    if stated is None:
        note(f"{th(n)} emitted over {page} page(s) of {a.per_page} — the site's counter was not read.")
        sys.exit(EXIT_PARTIAL)
    if stated == n:
        note(f"{th(n)} emitted over {page} page(s) of {a.per_page} — the site states {th(stated)}: equal.")
    else:
        note(f"{th(n)} emitted over {page} page(s) of {a.per_page} — the site states {th(stated)}: {th(abs(stated - n))} " + ("short." if stated > n else "more emitted than stated."))
        if stated > n:
            sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = re.fullmatch(r"/job/([^/]+)/?", parts.path or "")
    if parts.netloc.lower() != HOST or not m or parts.query:
        die(f"{a.url!r}: not an Eritrea Job Search advert address (https://{HOST}/job/<slug>/)")
    slug = m.group(1)
    url = f"{BASE}/job/{slug}/"
    st, body = request(url)
    status_of(st, url)
    found = postings(body)
    if not found:
        if 'class="job-count-number"' in body or "Current Job Vacancies in" in body:
            die(f"{url}: the site answers its listing page (200, no JobPosting) for a slug it does not have — gone, or never an advert.", EXIT_GONE)
        die(f"{url}: no JobPosting in the page — not an advert, or the page changed shape.", EXIT_PARTIAL)
    p = found[0]
    sal = one(p.get("baseSalary"))
    val = one(sal.get("value"))
    addr = one(p.get("jobLocation")).get("address")
    dm = DESC_RE.search(body)
    desc = scrub(text(dm.group("body"))) if dm else scrub(text(htmlmod.unescape(label(p.get("description")) or "")))
    rec = {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{slug}", "id": slug, "url": url,
           "title": label(p.get("title")), "company": label(p.get("hiringOrganization")),
           "place": label(addr, "addressLocality") if isinstance(addr, (dict, list)) else label(addr),
           "posted": label(p.get("datePosted")), "valid_through": label(p.get("validThrough")),
           "employment_type": label(p.get("employmentType")),
           "salary_currency_ldjson": label(sal.get("currency")), "salary_min_ldjson": label(val.get("minValue")), "salary_max_ldjson": label(val.get("maxValue")),
           "salary_as_written": (re.search(r"Salary:\s*([^\n]+)", desc or "") or [None, None])[1] if desc else None,
           "description": (desc or "")[:20000] or None,
           "source_signals": list(SIGNALS), "contacts_withheld": True}
    print(json.dumps(rec, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Eritrea Job Search — the list by the site's own per-page form and pager to its stated counter, the advert's JobPosting, a suspicion flag on every row (#549).")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the listing at ?jobs_ppp=N (the form's own options) and its pager; «N emitted — the site states M: equal/short»")
    s.add_argument("--per-page", type=int, default=384, help="one of the form's own options: 12 24 48 96 192 384")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its address; JobPosting + the page's description, scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
