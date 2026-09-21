#!/usr/bin/env python3
"""PageUp (an Australian ATS — universities, the public sector, Compass Group; also in the US), one tenant at a time, on its classic careers site: `careers.pageuppeople.com/<id>/cw/<lang>/listing/` — or the same `/cw/<lang>/listing/` on the employer's own host — is a server-rendered table paged by the page's own «More Jobs» link (`?page=N&page-items=M`), whose count is the jobs REMAINING after the page: shown + remaining is the site's stated total; the advert page carries the labelled fields and the dates. Issue #495.

  pageup.py jobs --tenant <id | listing address> [--page-items 100] [--country-code CC]
  pageup.py ad --url https://careers.pageuppeople.com/<id>/cw/<lang>/job/<no>/<slug>

THE HOSTS. The issue named `<entreprise>.pageuppeople.com`; the classic
careers sites live on `careers.pageuppeople.com/<id>/cw/<lang>/` (Compass
Group 541, SA Power Networks 511, Virginia Tech 968 `en-us`), sometimes on
the employer's own host with the same `/cw/<lang>/` paths. **A second,
newer product exists — the «careersite» (`<hash>.careersite.pageuppeople.com`
and employers' hosts such as `careers.sapowernetworks.com.au/jobs/search`,
where tenant 511 redirects): Rails cards, ten a page, no stated count read —
NOT this adapter** (measured 2026-09-21, named in the card). One host per
run; every other host refused before the gate (7); the application gateway
`secure.pageuppeople.com` / `secure.dc2.pageuppeople.com` never touched.
Rules (`careers.pageuppeople.com/robots.txt`, 1 B BOM + 33 lines,
2026-09-21): `*` refuses the test and admin paths (`/admin`, `/awake`,
`/*/uat/`, `/*/staging/`…) and nothing of `/<id>/cw/`; no Crawl-delay; 2 s
between requests are ours.

THE ROUTE, MEASURED 2026-09-21 09:05–09:07 UTC, the declared client (the
issue's 403 was the VENDOR's marketing root, `www.pageuppeople.com` — the
careers host answers 200). `/541/cw/en/listing/` (200, 89 670 B): the
`#search-results-content` table — `a.job-link` (`/541/cw/en/job/<no>/<slug>`),
`span.location`, `span.close-date time[datetime]`, a `tr.summary` teaser —
fifteen rows, then `<a class="more-link" href="…?page=2&page-items=15">More
Jobs <span class="count">636</span></a>`: **the count is what REMAINS —
15 + 636 = 651; page 2 shows 15 and says 621 (30 + 621 = 651); `page-items=100`
shows 100 and says 551 (100 + 551 = 651)** — the page's own parameters, the
value ours (100, said in the output). Virginia Tech (`en-us`) 20 a page,
20 + 277 = 297. An unknown tenant id answers 404 (exit 3); an unknown job
number answers 200 with «Sorry, we can't provide additional information about
this job right now» and an empty `#job-content` (exit 3). The advert (24 KB):
`#job-content` — `h2` title, `.job-externalJobNo`, `.work-type`, `.location`,
`.categories`, `#job-details` (HTML), «Advertised:» `.open-date time` and
«Applications close:» `.close-date time`, `og:site_name` the employer; no
JobPosting; the apply link is the gateway (never emitted).

WITHHELD: the apply and employee-referral gateway links; texts scrubbed of
e-mail addresses and telephones; `contacts_withheld` on every record; the
country stamped from `--country-code` (the site names none).
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

BOARD = "pageup"
VENDOR_HOST = "careers.pageuppeople.com"
NEVER = {"secure.pageuppeople.com", "secure.dc2.pageuppeople.com", "www.pageuppeople.com", "pageuppeople.com", "static.pageuppeople.com"}
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
MAX_PAGES = 400
LISTING_RE = re.compile(r"^(?P<prefix>(?:/\d+)?)/cw/(?P<lang>[a-z]{2}(?:-[a-z]{2})?)/listing/?$", re.I)
AD_RE = re.compile(r"^(?P<prefix>(?:/\d+)?)/cw/(?P<lang>[a-z]{2}(?:-[a-z]{2})?)/job/(?P<no>\d+)(?:/(?P<slug>[^/]*))?/?$", re.I)
TR_RE = re.compile(r'<tr(?P<attrs>[^>]*)>(?P<body>.*?)</tr>', re.S)
LINK_RE = re.compile(r'<a class="job-link" href="(?P<href>[^"]+)">(?P<title>.*?)</a>', re.S)
LOC_RE = re.compile(r'<span class="location">(.*?)</span>', re.S)
MORE_RE = re.compile(r'<a href="[^"]*"\s+class="more-link[^"]*"[^>]*data-page="(?P<page>\d+)"\s+data-page-items="(?P<items>\d+)"\s*>\s*More Jobs\s*<span class="count">(?P<count>\d+)</span>', re.S)
TIME_RE = re.compile(r'<time datetime="([^"]+)"')
FIELD_RE = re.compile(r'<span class="(?P<cls>job-externalJobNo|work-type[^"]*|location|categories)">(?P<v>.*?)</span>', re.S)
OPEN_RE = re.compile(r'<span class="open-date"><time datetime="([^"]+)"')
CLOSE_RE = re.compile(r'<span class="close-date"><time datetime="([^"]+)"')
DETAILS_RE = re.compile(r'<div id="job-details">(?P<body>.*?)</div>\s*<p>\s*<b>Advertised:', re.S)
DETAILS_LOOSE_RE = re.compile(r'<div id="job-details">(?P<body>.*?)<p>\s*<a class="back-link', re.S)
H2_RE = re.compile(r'<div id="job-content">\s*<h2>(.*?)</h2>', re.S)
SITE_RE = re.compile(r'<meta property="og:site_name" content="([^"]*)"')
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
_HOST = {"name": None}
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[pageup] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def tenant_of(s):
    """(host, prefix, lang) — a bare id is `careers.pageuppeople.com/<id>/cw/en/`; an address on any host with `/cw/<lang>/listing/` is its own tenant."""
    s = (s or "").strip()
    if re.fullmatch(r"\d+", s):
        return VENDOR_HOST, f"/{s}", "en"
    parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
    host = parts.netloc.lower()
    m = LISTING_RE.match(parts.path or "/")
    if not host or host in NEVER or not m:
        die(f"{s!r}: not a PageUp careers listing (an id, or https://<host>[/<id>]/cw/<lang>/listing/)")
    return host, m.group("prefix"), m.group("lang")


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    """(status, body) — the run's host only, never the application gateway, the guard first, 2 s apart."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc.lower() != _HOST["name"] or parts.netloc.lower() in NEVER:
        die(f"{url}: not the run's host {_HOST['name']} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(parts.netloc, Pace(parts.netloc, own=2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en"})
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
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span|font|time)\b[^>]*>", "", t)
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
    """(rows, more) — rows of the #search-results-content table, whatever columns the tenant shows (a row is a <tr> with a job link; the <tr class="summary"> after it is its teaser); more = (next_page, page_items, remaining) or None."""
    i = (body or "").find('id="search-results-content"')
    if i < 0:
        return None, None
    end = body.find("</tbody>", i)
    seg = body[i:end if end > 0 else None]
    rows = []
    for m in TR_RE.finditer(seg):
        attrs, tr = m.group("attrs"), m.group("body")
        if "summary" in attrs:
            if rows and rows[-1]["summary"] is None:
                rows[-1]["summary"] = text(re.sub(r"</?td[^>]*>", " ", tr))
            continue
        link = LINK_RE.search(tr)
        if not link:
            continue
        am = AD_RE.match(urllib.parse.urlsplit(link.group("href")).path)
        loc, close = LOC_RE.search(tr), TIME_RE.search(tr)
        rows.append({"href": link.group("href"), "no": am.group("no") if am else None, "title": text(link.group("title")),
                     "place": text(loc.group(1)) if loc else None, "closes": close.group(1) if close else None, "summary": None})
    mm = MORE_RE.search(body[i:])
    more = (int(mm.group("page")), int(mm.group("items")), int(mm.group("count"))) if mm else None
    return rows, more


def row(r, host, cc, company=None):
    href = r["href"] if r["href"].startswith("http") else f"https://{host}{r['href']}"
    rec = {"source": BOARD, "country": cc, "ledger_id": f"{BOARD}:{host}:{r['no']}", "id": r["no"], "url": href,
           "title": r["title"], "company": company, "place": r["place"], "closes": r["closes"],
           "summary": scrub(r.get("summary")), "contacts_withheld": True}
    return rec


def cmd_jobs(a):
    host, prefix, lang = tenant_of(a.tenant)
    _HOST["name"] = host
    cc = (a.country_code or "").upper() or None
    base = f"https://{host}{prefix}/cw/{lang}/listing/"
    seen, out, stated, page, items = set(), [], None, 1, a.page_items
    while page <= MAX_PAGES:
        url = f"{base}?page={page}&page-items={items}"
        st, body = request(url)
        if st == 404 and page == 1:
            die(f"{url}: HTTP 404 — not a PageUp tenant here, or the site moved.", EXIT_GONE)
        status_of(st, url)
        rows, more = parse_listing(body)
        if rows is None:
            die(f"{url}: no #search-results-content table in the answer — not the classic careers site (the newer «careersite» product is not this adapter), or the page changed shape.", EXIT_PARTIAL)
        if stated is None:
            stated = len(rows) + (more[2] if more else 0)
        new = 0
        for r in rows:
            if r["no"] and r["no"] not in seen:
                seen.add(r["no"])
                out.append(row(r, host, cc))
                new += 1
        if page > 1 and new == 0 and rows:
            note(f"page {page}: only repeats — stopped.")
            break
        if not more or more[2] <= 0 or not rows:
            break
        page, items = more[0], more[1]
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    if cc:
        note(f"country {cc} stamped from --country-code — the site names none.")
    note(f"{th(n)} emitted from {host}{prefix} over {page} page(s) of {items} — the site states {th(stated)} (the first page's rows plus its «More Jobs» remainder): " + ("equal." if stated == n else f"{th(abs(stated - n))} " + ("short." if stated > n else "more emitted than stated.")))
    if stated != n:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    host = parts.netloc.lower()
    m = AD_RE.match(parts.path or "")
    if not host or host in NEVER or not m:
        die(f"{a.url!r}: not a PageUp advert address (https://<host>[/<id>]/cw/<lang>/job/<no>/<slug>)")
    _HOST["name"] = host
    url = f"https://{host}{m.group('prefix')}/cw/{m.group('lang')}/job/{m.group('no')}/{m.group('slug') or ''}"
    st, body = request(url)
    status_of(st, url)
    if "can't provide additional information about this job" in body or "jobnotfound=true" in body:
        die(f"{url}: the site answers «Sorry, we can't provide additional information about this job right now» with an empty #job-content — gone, or never this tenant's.", EXIT_GONE)
    h2 = H2_RE.search(body)
    if not h2 or 'id="job-details"' not in body:
        die(f"{url}: no #job-content title or #job-details in the page — not an advert, or the page changed shape.", EXIT_PARTIAL)
    fields = {}
    for fm in FIELD_RE.finditer(body):
        cls = fm.group("cls").split()[0]
        fields.setdefault(cls, text(fm.group("v")))
    dm = DETAILS_RE.search(body) or DETAILS_LOOSE_RE.search(body)
    op, cl, site = OPEN_RE.search(body), CLOSE_RE.search(body), SITE_RE.search(body)
    no = fields.get("job-externalJobNo") or m.group("no")
    rec = {"source": BOARD, "country": (a.country_code or "").upper() or None, "ledger_id": f"{BOARD}:{host}:{no}", "id": no, "url": url,
           "title": text(h2.group(1)), "company": htmlmod.unescape(site.group(1)).strip() if site and site.group(1).strip() else None,
           "place": fields.get("location"), "work_type": fields.get("work-type"),
           "categories": [c.strip() for c in (fields.get("categories") or "").split(",") if c.strip()] or None,
           "posted": op.group(1) if op else None, "closes": cl.group(1) if cl else None,
           "description": (scrub(text(dm.group("body"))) or "")[:20000] or None if dm else None,
           "contacts_withheld": True}
    print(json.dumps(rec, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="PageUp (classic careers site) — one tenant's listing paged by its own «More Jobs» link to the stated total; the advert's fields and dates; the apply gateway never touched. Issue #495.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the listing, ?page=N&page-items=M, to the last «More Jobs»; «N emitted — the site states M: equal/short»")
    s.add_argument("--tenant", required=True, help="a careers.pageuppeople.com id (541), or the listing address on any host (…/cw/en/listing/)")
    s.add_argument("--page-items", type=int, default=100, help="rows a page (the page's own parameter; 100 is ours, the site's default is 15 or 20)")
    s.add_argument("--country-code", help="ISO-3166 alpha-2 to stamp on every row (the site names no country)")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its address")
    d.add_argument("--url", required=True)
    d.add_argument("--country-code")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
