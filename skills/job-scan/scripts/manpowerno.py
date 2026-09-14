#!/usr/bin/env python3
"""Manpower Norway (`www.manpower.no`) — the staffing network's Norwegian front on ManpowerGroup's Sitecore platform: the sitemap's `/nb/jobb/<id>/<slug>` rows as the inventory (the site's search is client-side and states no count a client reads), each job page read for its JobPosting, its labelled list and its body; the agency as employer on every ad; the text scrubbed. Issue #368.

  manpowerno.py sitemap [--limit N]        every /nb/jobb/<id>/<slug> row of sitemap.xml, with lastmod (1 request)
  manpowerno.py list [--limit N]           the sitemap's jobs read from their pages (N pages, 20 unless told, 2 s apart)
  manpowerno.py ad --url <https://www.manpower.no/nb/jobb/<id>/<slug>>

THE RULES (2 406 B): thirty named crawlers get their own groups; `*` (with
`facebookexternalhit`) reads `Allow: /`, `Disallow: /candidate`; `Sitemap: /sitemap.xml`. No
Crawl-delay; 2 s is ours.

THE INVENTORY IS THE SITEMAP. `/sitemap.xml` (588 rows) carries 96 `/nb/jobb/<id>/<slug>` rows
(and their `/en/job/` twins, set aside) with a per-row lastmod (94 distinct for 96), beside
`/sok/…` facet pages (place, trade, sector — server-rendered with at most 7 cards each) and the
site's pages. **The search `/nb/sok` renders no result and no count on the server** (a React
app; the count lives in its own calls) — so no count is stated a client reads: the sitemap's
rows are printed as the inventory, never as the site's statement.

THE AD. `/nb/jobb/<id>/<slug>` (200, ~120 KB) carries a JSON-LD graph with a JobPosting —
`identifier.value` (the reference), `title`, a one-line `description` (the teaser),
`datePosted` and `validThrough` in the site's compact form (`20260910T125613`), `employmentType`
(«Vikariat/ engasjement», «Fast»), `workHours` («Heltid»), `industry` as ids, `jobLocation`
with the county and the town **in the fields the site chose (`addressLocality` Vestland,
`addressRegion` Bergen — emitted as written, and named `place_text` from the page's own
«Arbeidssted» when printed)**, an empty `baseSalary` — and the page's labelled list
(«Referansenummer», «Publisert: 10 september, 2026», «Ansettelsesform», «Bransje» as names,
«Søknadsfrist», «Antall stillinger», «Heltid/deltid») and the body in `details-rich-text`.
**`hiringOrganization` is Manpower on every ad — an agency board, the client employer never
named; the body is scrubbed of e-mail addresses and Norwegian telephone numbers;
`contacts_withheld` on every record; «SØK PÅ STILLINGEN» is a form, never touched.**

Measured 2026-09-14 03:2x UTC by the declared client, the guard on the exact path: the sitemap
235 496 B / 96 job rows; `/nb/sok` 116 023 B without a card; `/sok/ledig-stilling-bergen` 7
cards; the ad 123 092 B with its JobPosting.
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
from _ldjson import one, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "www.manpower.no"
SITEMAP = f"https://{HOST}/sitemap.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+47[\s ]?)?(?:\d{2}[\s ]?\d{2}[\s ]?\d{2}[\s ]?\d{2}|\d{3}[\s ]?\d{2}[\s ]?\d{3})(?!\d)")
AD_RE = re.compile(r"^/nb/jobb/(\d+)/([^/]+)/?$")
ROW_RE = re.compile(r"<url>\s*<loc>([^<]+)</loc>(?:\s*<lastmod>([^<]+)</lastmod>)?", re.S)
DETAIL_RE = re.compile(r'<div class="job-details-text">(.*?)</div>', re.S)
BODY_RE = re.compile(r'<div class="details-rich-text">(.*?)</div>\s*</div>\s*</article>', re.S)
MONTHS_NB = {m: i for i, m in enumerate(("januar", "februar", "mars", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "desember"), 1)}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[manpowerno] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written; 2 s is ours


def request(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9", "Accept-Language": "nb"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"<!--.*?-->", "", markup or "", flags=re.S)
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup)
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t ​]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def compact_date(s):
    """`20260910T125613` / `20260917T215959Z` → 2026-09-10; an ISO string passes; anything else stays as printed."""
    m = re.match(r"^(\d{4})(\d{2})(\d{2})(?:T|$)", (s or "").strip())
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", (s or "").strip())
    return m.group(1) if m else ((s or "").strip() or None)


def nb_date(s):
    """«10 september, 2026» → 2026-09-10."""
    m = re.match(r"\s*(\d{1,2})\s+([a-zæøå]+),?\s*(\d{4})", (s or "").lower())
    if m and m.group(2) in MONTHS_NB:
        return f"{m.group(3)}-{MONTHS_NB[m.group(2)]:02d}-{int(m.group(1)):02d}"
    return (s or "").strip() or None


def sitemap_rows():
    code, body = request(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    rows, seen, other = [], set(), 0
    for loc, lastmod in ROW_RE.findall(body):
        m = AD_RE.match(urllib.parse.urlsplit(loc).path)
        if not m:
            other += 1
            continue
        if m.group(1) in seen:
            continue
        seen.add(m.group(1))
        rows.append({"source": "manpower-no", "country": "NO", "ledger_id": f"manpower-no:{m.group(1)}", "id": m.group(1), "url": loc, "slug": m.group(2), "lastmod": lastmod or None, "contacts_withheld": True, "language": "nb"})
    if not rows:
        die(f"{SITEMAP}: 200 and not one /nb/jobb/<id>/ row among {th(other)} — the sitemap's shape changed", EXIT_PARTIAL)
    return rows, other


def cmd_sitemap(a):
    rows, other = sitemap_rows()
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{th(len(rows))} job row(s) in the sitemap ({th(other)} other rows set aside — pages, facets, the English twins) — the site's search renders no count a client reads: the sitemap is the inventory, not the site's statement.")
    if a.limit and a.limit < len(rows):
        note(f"{th(len(emitted))} emitted of the {th(len(rows))} — bounded by --limit.")


def details(body):
    out = {}
    for d in DETAIL_RE.findall(body):
        t = text(d)
        if ":" in t:
            k, v = t.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def record(body, jid, url):
    jp = (postings(body) or [None])[-1]
    dl = details(body)
    bd = BODY_RE.search(body)
    if jp is None and not bd:
        return None
    jp = jp or {}
    addr = one(jp.get("jobLocation")).get("address") or {}
    sal = one(jp.get("baseSalary")).get("value") or {}
    val = (sal.get("value") or "").strip() if isinstance(sal.get("value"), str) else sal.get("value")
    body_text = text(bd.group(1)) if bd else ""
    place = re.search(r"Arbeidssted:\s*([^\n]+)", body_text)
    positions = dl.get("Antall stillinger")
    return {
        "source": "manpower-no", "country": "NO", "ledger_id": f"manpower-no:{jid}", "id": jid, "url": url,
        "reference": one(jp.get("identifier")).get("value") or dl.get("Referansenummer") or jid,
        "title": htmlmod.unescape(jp.get("title") or "").strip() or None,
        "teaser": scrub(htmlmod.unescape(jp.get("description") or "").strip()) or None,
        "company": "Manpower", "employer_is_the_agency": True,   # the client is described in the body and never named
        "locality_as_written": addr.get("addressLocality") or None, "region_as_written": addr.get("addressRegion") or None,   # the site's own fields — county in the locality, town in the region on the ad read
        "postal_code": addr.get("postalCode") or None, "country_as_written": addr.get("addressCountry") or None,
        "place_text": place.group(1).strip() if place else None,   # «Arbeidssted: Bergen» from the body, when printed
        "employment_type": jp.get("employmentType") or dl.get("Ansettelsesform"),
        "work_hours": jp.get("workHours") or dl.get("Heltid/deltid"),
        "sector": dl.get("Bransje"),
        "positions": int(positions) if positions and positions.isdigit() else positions,
        "salary_min": None, "salary_max": None, "salary_unit_stated": False, "salary_text": val or None,   # empty on every ad read
        "posted": compact_date(jp.get("datePosted")) or nb_date(dl.get("Publisert")),
        "posted_on_page": nb_date(dl.get("Publisert")),
        "valid_through": compact_date(jp.get("validThrough")), "deadline_on_page": nb_date(dl.get("Søknadsfrist")),
        "description": scrub(body_text) or None,
        "contacts_withheld": True, "language": "nb",
    }


def cmd_list(a):
    rows, other = sitemap_rows()
    limit = a.limit if a.limit else 20
    out, gone = [], 0
    for r in rows[:limit]:
        code, body = request(r["url"])
        if code == 404:
            gone += 1
            continue
        if code != 200:
            die(f"{r['url']}: HTTP {code}", EXIT_PARTIAL)
        rec = record(body, r["id"], r["url"])
        if rec is None:
            die(f"{r['url']}: 200 without a JobPosting or a body — the template changed; not an empty job", EXIT_PARTIAL)
        rec["lastmod"] = r["lastmod"]
        out.append(rec)
    for rec in out:
        print(json.dumps(rec, ensure_ascii=False))
    note(f"{th(len(out))} job(s) read from their pages, {th(gone)} gone since the sitemap, of the {th(len(rows))} the sitemap names — {th(min(limit, len(rows)))} read by request (--limit), not a shortfall; the site states no count a client reads.")
    note("the agency is the employer on every ad, the client never named; the body is scrubbed; the application form is never touched.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc not in (HOST, "manpower.no") or not m:
        die(f"{a.url}: not a job address (https://{HOST}/nb/jobb/<id>/<slug>)")
    url = f"https://{HOST}{parts.path.rstrip('/')}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    rec = record(body, m.group(1), url)
    if rec is None:
        die(f"{url}: 200 without a JobPosting or a body — the template changed", EXIT_PARTIAL)
    print(json.dumps(rec, ensure_ascii=False))
    note(f"{url}: read; the agency is the employer; the body is scrubbed; the application form is never touched.")


def main():
    p = argparse.ArgumentParser(description="Manpower Norway — the sitemap's jobs as the inventory, each page read; the agency as employer; the text scrubbed. Issue #368.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s_ = sub.add_parser("sitemap", help="every /nb/jobb/ row of sitemap.xml (1 request)")
    s_.add_argument("--limit", type=int)
    s_.set_defaults(fn=cmd_sitemap)
    l_ = sub.add_parser("list", help="the sitemap's jobs read from their pages — 20 unless --limit")
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
