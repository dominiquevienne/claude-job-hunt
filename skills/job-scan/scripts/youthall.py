#!/usr/bin/env python3
"""Youthall (`www.youthall.com`, Turkey — internships, young-graduate programmes and entry jobs): the listing `/tr/is-ilanlari/?page=N` walked to its empty page, the job sitemap as the second enumeration, the advert's own JobPosting. Issue #387.

  youthall.py jobs [--no-sitemap] [--max-pages N]
  youthall.py ad --url https://www.youthall.com/tr/<company>/<slug>_<n>/

THE RULES NAME THIS PROJECT ON BOTH SIDES. `www.youthall.com/robots.txt`
(3 626 B, 2026-09-20): `Claude-User` and `Claude-SearchBot` `Allow: /` by
name, `ClaudeBot` and `anthropic-ai` `Disallow: /` by name, `*` `Allow: /`
with three query strings closed (`?v331`, `?trk`, `?hl`) and two paths
(`/youth/login/`, `/crm-sales`); no Crawl-delay. The site wrote the
distinction the plugin declares — the route is plain HTTP under
`Claude-User`, and `?page=` is not among the closed queries. 2 s between
requests are ours.

THE LISTING, MEASURED 2026-09-20 14:42 UTC (each page twice; page 1 286 751 B,
md5 moving — a rendered element). `/tr/is-ilanlari/` carries three blocks
of `div.jobs` cards: «Öne Çıkan İlanlar» (featured, a subset of the list),
**«Tüm İlanlar» (the list: 15 on page 1, 13 on `?page=2`, 0 on `?page=3`)**
and «Yetenek Programları» (talent programmes, cards without a job link).
Only the «Tüm İlanlar» block is read, page after page, until a page holds
no card; **28 distinct advertisements** on 2026-09-20 (27 on 2026-09-13).
A card: `<a href="https://www.youthall.com/tr/<company>/<slug>_<n>/">`, the
employer's logo `alt="<Employer> logo"`, `<h5>` title, then three
`jobs-tag`s — the type (Stajyer, Tam Zamanlı, …), the closing date
(`27.09.2026`, the clock icon; the ad's `<title>` calls it «Son Başvuru»)
and the city. **The page states no count**: the second enumeration is
`sitemap.tr-jobs.xml` (28 `<loc>`, one `lastmod` each), printed beside the
emitted number — «28 emitted, the sitemap lists 28 — equal» — the
agreement of two enumerations being the check, as on `albaniajobs`.
`sitemap.tr-talent_programs.xml` (328 programme pages and their review
pages) is a catalogue of employers' programmes, not advertisements: named
here, never counted.

THE KEY IS THE ADDRESS. `/tr/toyotaturkiye/…_4/` — `_4` is the employer's
own sequence, not a site-wide id (the ad page's `identifier.value` is
`8262`), so the ledger key is `youthall:<company>:<n>` and `ad` adds the
site's `identifier` as `site_id`.

THE ADVERT (4.2 MB pages — two images inlined in base64) carries a full
`JobPosting`: title, description (HTML), `datePosted`, `validThrough`,
`employmentType` (INTERN, FULL_TIME …), `hiringOrganization` (name and the
employer's Youthall page), `identifier`, `jobLocation[]` (locality, region,
`addressCountry: TR`). `ad` reads it through `_ldjson.postings` and dies
with 6 when the page has none (a company page, a programme page).

WITHHELD: the description scrubbed of e-mail addresses and telephone
numbers; the employer's logo and cover images not emitted; the application
(`directApply` on the site, an account) never touched; `contacts_withheld`
on every record.
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

BOARD, HOST, COUNTRY = "youthall", "www.youthall.com", "TR"
BASE = f"https://{HOST}"
LIST = BASE + "/tr/is-ilanlari/"
SITEMAP = BASE + "/sitemap.tr-jobs.xml"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

AD_RE = re.compile(r"^/tr/(?P<company>[A-Za-z0-9_.-]+)/(?P<slug>[A-Za-z0-9_.-]+?)_(?P<n>\d+)/?$")
BLOCK_RE = re.compile(r"<h2[^>]*>\s*Tüm İlanlar\s*</h2>(.*?)(?:<h2[^>]*>|$)", re.S)
CARD_RE = re.compile(r'<div class="jobs">\s*<a href="(?P<url>https://www\.youthall\.com/tr/[^"]+)">(?P<body>.*?)</a>\s*</div>', re.S)
LOGO_RE = re.compile(r'class="jobs-content-logo"\s+alt="([^"]*?)\s*logo"')
H5_RE = re.compile(r"<h5>(.*?)</h5>", re.S)
TAG_RE = re.compile(r'<div class="jobs-tag">\s*<i class="(?P<icon>[^"]*)"></i>\s*(?P<text>.*?)\s*</div>', re.S)
LOC_RE = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
_PACE = Pace(HOST, own=2.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[youthall] {msg}", file=sys.stderr)


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
    parts = urllib.parse.urlsplit(url)
    if parts.netloc.lower() != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml", "Accept-Language": "tr,en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", markup or "", flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def key_of(url):
    """`https://www.youthall.com/tr/toyotaturkiye/gelecek-…_4/` → (company, n, canonical url); None when it is not an advert address."""
    parts = urllib.parse.urlsplit((url or "").strip())
    if parts.netloc.lower() != HOST:
        return None
    m = AD_RE.match(parts.path)
    if not m:
        return None
    return m.group("company"), m.group("n"), f"{BASE}/tr/{m.group('company')}/{m.group('slug')}_{m.group('n')}/"


def status_of(code, url):
    if code == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if code in (403, 429):
        die(f"{url}: HTTP {code} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)


def parse_cards(body):
    """The «Tüm İlanlar» block's cards → rows; None when the page has no such block (not the listing)."""
    m = BLOCK_RE.search(body or "")
    if not m:
        return None
    rows = []
    for c in CARD_RE.finditer(m.group(1)):
        k = key_of(c.group("url"))
        if not k:
            continue
        company, n, url = k
        b = c.group("body")
        logo = LOGO_RE.search(b)
        h5 = H5_RE.search(b)
        tags = [(t.group("icon"), text(t.group("text"))) for t in TAG_RE.finditer(b)]
        kind = next((v for i, v in tags if "briefcase" in i), None)
        closes = next((v for i, v in tags if "clock" in i), None)
        city = next((v for i, v in tags if "map-marker" in i), None)
        rows.append({
            "source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{company}:{n}", "id": f"{company}:{n}", "url": url,
            "title": text(h5.group(1)) if h5 else None, "company": htmlmod.unescape(logo.group(1)).strip() if logo else None,
            "kind": kind, "closes": closes, "place": city, "contacts_withheld": True,
        })
    return rows


def sitemap_urls(body):
    return {k[2] for k in (key_of(u) for u in LOC_RE.findall(body or "")) if k}


def cmd_jobs(a):
    seen, out = set(), []
    for page in range(1, a.max_pages + 1):
        url = LIST if page == 1 else f"{LIST}?page={page}"
        st, body = request(url)
        status_of(st, url)
        rows = parse_cards(body)
        if rows is None:
            die(f"{url}: no «Tüm İlanlar» block in the page — not the listing, or the page changed shape.", EXIT_PARTIAL)
        fresh = [r for r in rows if r["url"] not in seen]
        if not rows or not fresh:
            break                       # the empty page ends the walk (page 3 on 2026-09-20); a page of only repeats too
        for r in fresh:
            seen.add(r["url"])
            out.append(r)
    else:
        note(f"{a.max_pages} pages read (--max-pages) and the last still had cards — the walk is truncated.")
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    if a.no_sitemap:
        note(f"{th(n)} emitted — the page states no count; the sitemap not read (--no-sitemap).")
        return
    st, body = request(SITEMAP)
    if st != 200:
        note(f"{th(n)} emitted — the page states no count; {SITEMAP}: HTTP {st}, no second enumeration.")
        return
    sm = sitemap_urls(body)
    missing, extra = sm - seen, seen - sm
    if not missing and not extra:
        note(f"{th(n)} emitted, the sitemap lists {th(len(sm))} — equal.")
    else:
        note(f"{th(n)} emitted, the sitemap lists {th(len(sm))} — {th(len(missing))} in the sitemap not on the pages, {th(len(extra))} on the pages not in the sitemap.")


def cmd_ad(a):
    k = key_of(a.url)
    if not k:
        die(f"{a.url!r}: not a Youthall advert address (https://{HOST}/tr/<company>/<slug>_<n>/)")
    company, n, url = k
    st, body = request(url)
    status_of(st, url)
    found = postings(body)
    if not found:
        die(f"{url}: no JobPosting in the page — a company or programme page, or the advert is gone.", EXIT_PARTIAL)
    p = found[0]
    org = one(p.get("hiringOrganization"))
    place = one(p.get("jobLocation"))
    addr = one(place.get("address")) if place else {}
    ident = one(p.get("identifier"))
    r = {
        "source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{company}:{n}", "id": f"{company}:{n}", "url": url,
        "site_id": label(ident, "value") if ident else None,
        "title": label(p.get("title")), "company": label(org) if org else None, "company_url": label(org, "sameAs") if org else None,
        "posted": label(p.get("datePosted")), "closes": label(p.get("validThrough")),
        "employment_type": label(p.get("employmentType")),
        "place": label(addr, "addressLocality") if addr else None, "region": label(addr, "addressRegion") if addr else None,
        "description": (scrub(text(label(p.get("description")))) or "")[:20000] or None,
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Youthall (Turkey) — the listing walked to its empty page, the job sitemap as the second enumeration, the advert's JobPosting; no contact. Issue #387.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="every card of «Tüm İlanlar», page after page; the sitemap's count beside the emitted number")
    s.add_argument("--no-sitemap", action="store_true", help="skip the sitemap read")
    s.add_argument("--max-pages", type=int, default=20)
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its address; description scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
