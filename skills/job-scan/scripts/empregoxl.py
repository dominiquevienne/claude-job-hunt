#!/usr/bin/env python3
"""Emprego XL (`www.empregoxl.com`) — a Portuguese board whose sitemap and footer both count the whole archive; the live inventory is read from the dated listing.

  empregoxl.py recent [--days N] [--max-pages N] [--limit N]
  empregoxl.py sitemap [--limit N] [--no-site-total]
  empregoxl.py ad --url <advertisement URL> | --id <n>

THE SITEMAP IS THE ARCHIVE, AND THE SITE COUNTS THE ARCHIVE TOO

`sitemap.xml` held 84 875 `/emprego/<id>/<slug>` addresses on 2026-09-12
(ids 486 946 → 580 783, no `<lastmod>`), and the footer of every page states
«84875 Ofertas de Emprego» — **equal, and both count everything ever
published**: id 520 128 (published 10-11-2022) is still served, with the
site's own label «Este anúncio de emprego tem mais de 90 dias». So `sitemap`
prints the two figures side by side and says what they count; it is not the
live inventory.

THE LIVE INVENTORY IS THE LISTING — `/empregos?p=N`, 20 cards a page, newest
first, each card dated «12 Sep» (day and month, no year). `recent --days N`
walks the pages until a card is older than the window and emits every card
newer than it. The year is inferred for the STOP rule only (the current year,
or the previous one when the month is ahead of today's); the row carries the
label as printed and no derived date — the advertisement page carries the
full `datePosted`. On 2026-09-12 page 7 was still on 09 Sep: the board posts
tens of advertisements a day, most of them from a handful of real-estate
recruiters.

THE ADVERTISEMENT is schema.org microdata (`itemscope itemtype=JobPosting`,
not JSON-LD): title, hiringOrganization/name (with the employer's site as the
link), jobLocation/addressLocality, datePosted (dd-mm-yyyy), description
(HTML). Employer e-mail addresses in the body are Cloudflare-obfuscated
(`data-cfemail`) and are decoded — the employer published them for
candidates to use. An advertisement over 90 days old carries the site's
own label and the adapter emits it as `over_90_days: true`.

`/rss/all/` answered HTTP 500 with an empty body on 2026-09-12 — no feed
route here. The rules refuse eight tooling paths (`/_includes`, `/admin`,
`/uploads`…) to `*` and everything to seven SEO crawlers by name; nothing this
adapter reads is refused; no `Crawl-delay`; this adapter spaces 2 s. Behind
Cloudflare, 200 to the declared identity on every page read.
"""

import argparse
import datetime as dt
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
from _sitemap import locs as sitemap_locs
from _ua import UA
from _zero import empty_first_page

HOST = "www.empregoxl.com"
BASE = "https://" + HOST
SITEMAP = BASE + "/sitemap.xml"
LISTING = BASE + "/empregos"
AD_RE = re.compile(r"^https://(?:www\.)?empregoxl\.com/emprego/(\d+)/([^/?#]*)/?$")
# <div id="stats"><strong>84875 Ofertas de Emprego</strong>
SITE_COUNT_RE = re.compile(r'id="stats">\s*<strong>\s*([\d .,]+)\s*Ofertas de Emprego')
CARD_RE = re.compile(
    r'<li>\s*<a href="(https://www\.empregoxl\.com/emprego/(\d+)/[^"]*)"[^>]*>(.*?)</a>\s*</li>', re.S)
MONTHS = {m: i for i, m in enumerate(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), 1)}
OVER_90 = "tem mais de 90 dias"
PAGE_SIZE = 20

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[empregoxl] {msg}", file=sys.stderr)


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
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "pt,en;q=0.5"})
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


def cf_decode(hexstr):
    """Cloudflare's e-mail obfuscation: first byte is the key, the rest XOR it."""
    try:
        b = bytes.fromhex(hexstr)
        return bytes(x ^ b[0] for x in b[1:]).decode("utf-8")
    except (ValueError, IndexError):
        return None


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    # the employer's published address, obfuscated by the CDN — decoded, because the employer put it there for candidates
    markup = re.sub(r'<a[^>]*class="__cf_email__"[^>]*data-cfemail="([0-9a-f]+)"[^>]*>.*?</a>',
                    lambda m: cf_decode(m.group(1)) or "[e-mail]", markup, flags=re.S)
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    """Thousands with a space — the repo's figure style."""
    return f"{n:,}".replace(",", " ")


def ad_url(ident, slug=""):
    return f"{BASE}/emprego/{ident}/{slug}" if slug else f"{BASE}/emprego/{ident}/"


def site_count(body):
    m = SITE_COUNT_RE.search(body or "")
    return int(re.sub(r"[^\d]", "", m.group(1))) if m else None


def cmd_sitemap(a):
    code, xml = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_PARTIAL)
    raw, rows, seen, other = 0, [], set(), 0
    for loc in sitemap_locs(xml):
        raw += 1
        m = AD_RE.match(loc.strip())
        if not m:
            other += 1
            continue
        if m.group(1) in seen:
            continue
        seen.add(m.group(1))
        rows.append({"source": "empregoxl", "country": "PT", "ledger_id": f"empregoxl:{m.group(1)}",
                     "id": m.group(1), "url": loc.strip()})
    if raw == 0:
        die(empty_first_page("empregoxl", xml, "<loc>", where=SITEMAP), EXIT_PARTIAL)
    if not rows:
        die(f"{SITEMAP}: {th(raw)} <loc> and none of the shape /emprego/<id>/<slug> — the address shape moved, or the board has nothing; from here they look alike.", EXIT_PARTIAL)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    ids = sorted(int(r["id"]) for r in rows)
    note(f"{th(raw)} <loc> in sitemap.xml: **{th(len(rows))} distinct advertisement id(s)** ({th(ids[0])} → {th(ids[-1])}), "
         f"{th(other)} other addresses. No <lastmod>. **This is the archive, not the live inventory** — "
         "advertisements from 2022 are still listed and served; use `recent` for what is current.")
    if a.no_site_total:
        return
    code, page = get(BASE + "/")
    stated = site_count(page) if code == 200 else None
    if stated is None:
        note(f"{BASE}/ states no count this run (HTTP {code}) — no second source.")
        return
    n, gap = th(len(rows)), th(abs(stated - len(rows)))
    if stated == len(rows):
        note(f"{n} emitted, site states {th(stated)} «Ofertas de Emprego» in its footer — equal; both count the archive.")
    else:
        note(f"{n} emitted, site states {th(stated)} «Ofertas de Emprego» in its footer — {gap} "
             + ("short" if stated > len(rows) else "more in the sitemap than the site states") + "; both count the archive.")


def card_date(label, today):
    """«12 Sep» → a date, for the stop rule only: this year, or last year when the month is ahead of today's."""
    m = re.match(r"\s*(\d{1,2})\s+([A-Z][a-z]{2})\s*$", label or "")
    if not m or m.group(2) not in MONTHS:
        return None
    day, month = int(m.group(1)), MONTHS[m.group(2)]
    year = today.year - 1 if month > today.month else today.year
    try:
        return dt.date(year, month, day)
    except ValueError:
        return None


def parse_cards(body):
    out = []
    for url, ident, inner in CARD_RE.findall(body):
        def field(cls):
            m = re.search(r'<span class="%s">(.*?)</span>' % cls, inner, re.S)
            return text(m.group(1)) if m else None
        kind = re.search(r'<img[^>]*alt="([^"]*)"', inner)
        company_loc = field("company_name") or ""
        company, _, city = company_loc.rpartition(",")
        out.append({"source": "empregoxl", "country": "PT", "ledger_id": f"empregoxl:{ident}", "id": ident,
                    "url": url, "title": field("jobtitle"),
                    "employer": company.strip() or None, "city": city.strip() or None,
                    "job_type": kind.group(1) if kind else None,
                    # the card's date as printed — day and month, no year; the page carries the full datePosted
                    "posted_label": field("date"), "posted": None})
    return out


def cmd_recent(a):
    today = dt.date.today()
    floor = today - dt.timedelta(days=a.days)
    rows, seen, page, stopped, oldest = [], set(), 1, None, None
    while True:
        url = LISTING if page == 1 else f"{LISTING}?p={page}"
        code, body = get(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        cards = parse_cards(body)
        if page == 1 and not cards:
            die(empty_first_page("empregoxl", body, "card", where=url, candidates=body.count('class="jobtitle"')), EXIT_PARTIAL)
        if not cards:
            stopped = "the listing ended"
            break
        for c in cards:
            d = card_date(c["posted_label"], today)
            if d is None:
                note(f"card {c['id']}: date label {c['posted_label']!r} not read — kept, not dated.")
            elif d < floor:
                stopped = f"a card dated {c['posted_label']} is older than {a.days} day(s)"
                break
            else:
                oldest = min(oldest, d) if oldest else d
            if c["id"] not in seen:
                seen.add(c["id"])
                rows.append(c)
        if stopped:
            break
        if a.max_pages and page >= a.max_pages:
            stopped = f"--max-pages {a.max_pages} reached — the window may hold more"
            break
        page += 1
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{th(len(emitted))} card(s) emitted from {page} page(s) of {PAGE_SIZE} (newest first, oldest kept {oldest}); "
         f"stopped because {stopped}. **The board states no count for this window** — its only figure counts the archive.")


def cmd_ad(a):
    ident = a.id
    if a.url:
        m = AD_RE.match(a.url.strip())
        if not m:
            die(f"{a.url}: not an advertisement address — expected {BASE}/emprego/<id>/<slug>/")
        ident = m.group(1)
    if not ident or not ident.isdigit():
        die(f"{ident!r}: not a numeric id")
    url = a.url.strip() if a.url else ad_url(ident)
    code, body = get(url)
    if code == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    blk = re.search(r'<div id="job-details" itemscope itemtype="http://schema.org/JobPosting">(.*?)<div class="adsensebottom">', body, re.S)
    if not blk:
        die(f"{url}: no JobPosting microdata block in {th(len(body))} characters — the page shape moved, or this is not an advertisement.", EXIT_PARTIAL)
    b = blk.group(1)

    def prop(name, tag="[a-z0-9]+"):
        # up to the closing tag of the SAME element — the description holds <a> and <br>, and `</` alone would stop at the first of them
        m = re.search(r"<(%s)[^>]*itemprop=['\"]%s['\"][^>]*>(.*?)</\1>" % (tag, name), b, re.S)
        return text(m.group(2)) if m else None
    org = re.search(r'<a itemprop="hiringOrganization"[^>]*href="([^"]*)"[^>]*>.*?<span itemprop="name">(.*?)</span>', b, re.S)
    posted = prop("datePosted")
    pm = re.match(r"(\d{2})-(\d{2})-(\d{4})", posted or "")
    kind = re.search(r'<h2 itemprop="title">.*?<img[^>]*alt="([^"]*)"', b, re.S)
    print(json.dumps({
        "source": "empregoxl", "country": "PT", "ledger_id": f"empregoxl:{ident}", "id": ident, "url": url,
        "title": prop("title"),
        # linked employer: <a itemprop=hiringOrganization href=…><span itemprop=name>; unlinked: <strong itemprop=hiringOrganization>Yupi!</strong>
        "employer": text(org.group(2)) if org else (prop("name") or prop("hiringOrganization")),
        "employer_site": (org.group(1) or None) if org else None,
        "city": prop("addressLocality"),
        "job_type": kind.group(1) if kind else None,
        "posted": f"{pm.group(3)}-{pm.group(2)}-{pm.group(1)}" if pm else None, "posted_as_printed": posted,
        "over_90_days": OVER_90 in b,
        "applications": (lambda m: int(m.group(1)) if m else None)(re.search(r'id="applied-to-job">\s*(\d+)', b)),
        "description": prop("description", "div")[:20000] if prop("description", "div") else None, "language": "pt",
    }, ensure_ascii=False))
    if OVER_90 in b:
        note("the site labels this advertisement «mais de 90 dias» — served, listed in the sitemap, and older than the site's own freshness line.")


def main():
    p = argparse.ArgumentParser(description="Emprego XL — the dated listing for what is live, the sitemap and footer for the archive they both count.")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("recent", help="cards newer than --days from the listing, newest first — 1 request per 20")
    r.add_argument("--days", type=int, default=30)
    r.add_argument("--max-pages", type=int)
    r.add_argument("--limit", type=int)
    r.set_defaults(fn=cmd_recent)
    s = sub.add_parser("sitemap", help="every advertisement ever published — the archive, with the footer's count beside it")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one advertisement, from its microdata")
    g = d.add_mutually_exclusive_group(required=True)
    g.add_argument("--url")
    g.add_argument("--id")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
