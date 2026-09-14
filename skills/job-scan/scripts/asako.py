#!/usr/bin/env python3
"""Asako.mg (`www.asako.mg`) — Madagascar's job board on Vercel (Next.js): the listing prints its count on the server («253 offres disponibles») and loads its cards by a client action, the sitemap names every advertisement, and each ad page carries a JobPosting; the count printed beside every walk; the texts scrubbed. Issue #338.

  asako.py sitemap [--limit N]        every /annonces/<slug>-<hex> row of sitemap.xml, with lastmod (1 request)
  asako.py list [--limit N]           the listing's stated count, then the sitemap's ads read from their pages (N pages, 20 unless told, 2 s apart)
  asako.py ad --url <https://www.asako.mg/annonces/<slug>-<hex>>

THE RULES. `Claude-User` is named with its own group — `Allow: /`, `Disallow: /api/`, `/admin/`,
`/recruteur/`, `/candidat/`, `/dashboard/`, `/go/` — the same lines as `*`; no Crawl-delay, 2 s is
ours; `/api/` (the app's routes) and `/go/` (outbound redirects) are refused before the gate.

THE COUNT IS ON THE SERVER, THE CARDS ARE NOT. `/emploi` (200, ~133 KB) is a React Server
Components page whose markup carries «<strong>253</strong> offres disponibles» and «Vous voyez
20 offres sur 253»; twenty cards, then «Charger plus d'offres» — a client action (a tab pressed it
twelve times on 2026-09-14 and reached 253 of 253). So the count is read from the page and the
inventory is `/sitemap.xml` (582 rows on the day: 253 `/annonces/<slug>-<hex>` with lastmod,
229 `/emploi/…` facets, 87 employer profiles, pages); `list` prints emitted against the stated
count. THE AD. `/annonces/<slug>-<hex>` (200, ~160 KB) carries a JobPosting JSON-LD — title,
description, identifier (a UUID), datePosted, validThrough, employmentType, hiringOrganization
(name, url, sameAs), jobLocation or `jobLocationType: TELECOMMUTE` with
`applicantLocationRequirements`, responsibilities, qualifications, skills, industry,
occupationalCategory — beside a BreadcrumbList. **The description, responsibilities and
qualifications are scrubbed of e-mail addresses and Malagasy telephone numbers;
`contacts_withheld` on every record; the application («Postuler», a candidate account) never
touched.**

Measured 2026-09-14 09:48–09:5x UTC by the declared client, the guard on the exact path: the name
resolves again on 1.1.1.1 and 8.8.8.8 (76.76.21.21; NXDOMAIN on 2026-09-13); robots 200;
`/emploi` 132 972 B, «253»; `sitemap.xml` 582 rows / 253 ads (lastmod 2026-09-01 … 2026-09-14);
the ad 161 167 B with its JobPosting; a tab: «Vous voyez 253 offres sur 253».
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

HOST = "www.asako.mg"
LIST = f"https://{HOST}/emploi"
SITEMAP = f"https://{HOST}/sitemap.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+261[\s ]?|0)(?:\d[\s ]?){8,9}\d(?!\d)")
AD_RE = re.compile(r"^/annonces/([a-z0-9\-]+)-([0-9a-f]{4,12})/?$")
REFUSED_RE = re.compile(r"^/(?:api|admin|recruteur|candidat|dashboard|go)(?:/|$)")
ROW_RE = re.compile(r"<url>\s*<loc>([^<]+)</loc>(?:\s*<lastmod>([^<]+)</lastmod>)?", re.S)
COUNT_RE = re.compile(r"<strong[^>]*>\s*(\d[\d  ]*)\s*</strong>\s*(?:<!--\s*-->)?\s*offres? disponibles")

_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written; 2 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[asako] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    if REFUSED_RE.search(urllib.parse.urlsplit(url).path):
        die(f"{url}: refused in writing to Claude-User by name (the app's routes, the accounts, the redirects) — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9", "Accept-Language": "fr"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", htmlmod.unescape(s))
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def stated(body):
    """The count the listing prints on the server — «<strong>253</strong> offres disponibles» — or `None`."""
    m = COUNT_RE.search(body or "")
    return int(re.sub(r"\D", "", m.group(1))) if m else None


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
        if m.group(2) in seen:
            continue
        seen.add(m.group(2))
        rows.append({"source": "asako", "country": "MG", "ledger_id": f"asako:{m.group(2)}", "id": m.group(2), "url": loc, "slug": m.group(1), "lastmod": (lastmod or "")[:10] or None, "contacts_withheld": True, "language": "fr"})
    if not rows:
        die(f"{SITEMAP}: 200 and not one /annonces/<slug>-<hex> row among {th(other)} — the sitemap's shape changed", EXIT_PARTIAL)
    return rows, other


def cmd_sitemap(a):
    rows, other = sitemap_rows()
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{th(len(rows))} ad row(s) in the sitemap ({th(other)} other rows set aside — facets, employer profiles, pages); `list` prints the listing's stated count beside them.")
    if a.limit and a.limit < len(rows):
        note(f"{th(len(emitted))} emitted of the {th(len(rows))} — bounded by --limit.")


MONTHS_FR = {m: i for i, m in enumerate(("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"), 1)}
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
PUBLISHED_RE = re.compile(r"Publiée? le\s*(\d{1,2})\s+([a-zéû]+)\s+(\d{4})")
PLACE_RE = re.compile(r"Lieu de travail\s*(?:</[^>]+>\s*)*(?:<[^>]+>\s*)*([^<]{1,80})<")
SECTION_RE = re.compile(r'<h2[^>]*>(.*?)</h2>\s*</div>\s*<div class="prose[^"]*">(.*?)</div>', re.S)   # «Missions principales», «Profil recherché», «Description …»: an <h2> then the prose block


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t ]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def legacy_record(body, jid, url):
    """An ad page without a JobPosting — the older ads (a numeric tail) — read from its own markup: the `<h1>`, the employer from the `<title>` («… chez MADIXY | Asako.mg»), «Publiée le», «Lieu de travail», the prose sections; `None` when even the heading is absent."""
    h1 = H1_RE.search(body or "")
    if not h1:
        return None
    t = TITLE_RE.search(body or "")
    mt = re.search(r"\schez\s+(.+?)\s*\|", htmlmod.unescape(t.group(1))) if t else None
    pub = PUBLISHED_RE.search(text(body))
    posted = f"{pub.group(3)}-{MONTHS_FR[pub.group(2)]:02d}-{int(pub.group(1)):02d}" if pub and pub.group(2) in MONTHS_FR else None
    place = PLACE_RE.search(body or "")
    secs = {re.sub(r"\s+", " ", text(k)).strip().lower(): scrub(text(v)) for k, v in SECTION_RE.findall(body or "")}
    return {
        "source": "asako", "country": "MG", "ledger_id": f"asako:{jid}", "id": jid, "url": url, "uuid": None,
        "title": text(h1.group(1)) or None, "company": (mt.group(1).strip() if mt else None), "company_profile": None, "company_site": None,
        "employment_type": None, "place": text(place.group(1)) if place else None, "region": None, "remote": False, "applicant_country": None,
        "industry": None, "category": None, "skills": None, "posted": posted, "valid_through": None, "direct_apply": None,
        "description": next((v for k, v in secs.items() if k.startswith("description")), None), "responsibilities": secs.get("missions principales"), "qualifications": secs.get("profil recherché"),
        "contacts_withheld": True, "language": "fr", "no_jobposting": True,   # the page's own markup, read because the ad carries no JobPosting
    }


def record(body, jid, url):
    jp = (postings(body) or [None])[-1]
    if jp is None:
        return legacy_record(body, jid, url)
    org = one(jp.get("hiringOrganization"))
    addr = one(one(jp.get("jobLocation")).get("address"))
    alr = one(jp.get("applicantLocationRequirements"))
    ident = jp.get("identifier") if isinstance(jp.get("identifier"), str) else one(jp.get("identifier")).get("value")
    return {
        "source": "asako", "country": "MG", "ledger_id": f"asako:{jid}", "id": jid, "url": url, "uuid": ident or None,
        "title": htmlmod.unescape(jp.get("title") or "").strip() or None,
        "company": (org.get("name") or "").strip() or None, "company_profile": org.get("url") or None, "company_site": org.get("sameAs") or None,
        "employment_type": jp.get("employmentType") or None,
        "place": addr.get("addressLocality") or None, "region": addr.get("addressRegion") or None,
        "remote": (jp.get("jobLocationType") or "").upper() == "TELECOMMUTE", "applicant_country": alr.get("name") or None,
        "industry": jp.get("industry") or None, "category": jp.get("occupationalCategory") or None,
        "skills": [s for s in (jp.get("skills") or []) if isinstance(s, str)] or None if isinstance(jp.get("skills"), list) else None,
        "posted": (jp.get("datePosted") or "")[:10] or None, "valid_through": (jp.get("validThrough") or "")[:10] or None,
        "direct_apply": jp.get("directApply"),
        "description": scrub(jp.get("description")), "responsibilities": scrub(jp.get("responsibilities")), "qualifications": scrub(jp.get("qualifications")),
        "contacts_withheld": True, "language": "fr",
    }


def cmd_list(a):
    code, body = request(LIST)
    if code != 200:
        die(f"{LIST}: HTTP {code}", EXIT_PARTIAL)
    total = stated(body)
    if total is None:
        die(f"{LIST}: 200 and no «N offres disponibles» in the page — the template changed; not an empty market", EXIT_PARTIAL)
    rows, other = sitemap_rows()
    limit = a.limit if a.limit else 20
    out, gone = [], 0
    for r in rows[:limit]:
        code, page = request(r["url"])
        if code == 404:
            gone += 1
            continue
        if code != 200:
            die(f"{r['url']}: HTTP {code}", EXIT_PARTIAL)
        rec = record(page, r["id"], r["url"])
        if rec is None:
            die(f"{r['url']}: 200 without a JobPosting and without the ad's heading — the template changed; not an empty job", EXIT_PARTIAL)
        rec["lastmod"] = r["lastmod"]
        out.append(rec)
    for rec in out:
        print(json.dumps(rec, ensure_ascii=False))
    n = len(out)
    if limit < len(rows):
        note(f"{th(n)} emitted of the {th(total)} the site states on {LIST} ({th(len(rows))} in the sitemap, {th(gone)} gone) — {th(min(limit, len(rows)))} read by request (--limit), not a shortfall.")
    else:
        verdict = "equal" if n == total else (f"{th(total - n)} short" if n < total else f"{th(n - total)} more emitted")
        note(f"{th(n)} emitted ({th(len(rows))} in the sitemap, {th(gone)} gone), the site states {th(total)} — {verdict}.")
    note("texts scrubbed; the application never touched.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc not in (HOST, "asako.mg") or not m:
        die(f"{a.url}: not a job address (https://{HOST}/annonces/<slug>-<hex>)")
    url = f"https://{HOST}{parts.path.rstrip('/')}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    rec = record(body, m.group(2), url)
    if rec is None:
        die(f"{url}: 200 without a JobPosting and without the ad's heading — the template changed", EXIT_PARTIAL)
    print(json.dumps(rec, ensure_ascii=False))
    note(f"{url}: read from its JobPosting; texts scrubbed; the application never touched.")


def main():
    p = argparse.ArgumentParser(description="Asako.mg — the listing's stated count beside the sitemap's inventory, each ad read from its JobPosting; texts scrubbed. Issue #338.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s_ = sub.add_parser("sitemap", help="every /annonces/ row of sitemap.xml (1 request)")
    s_.add_argument("--limit", type=int)
    s_.set_defaults(fn=cmd_sitemap)
    l_ = sub.add_parser("list", help="the stated count, then the sitemap's ads read from their pages — 20 unless --limit")
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
