#!/usr/bin/env python3
"""Asako.mg (`www.asako.mg`) — Madagascar's job board on Vercel (Next.js): the listing states its count on the server, the ads are named by the sitemap the HOST DECLARES, and each ad page carries a JobPosting; the count printed beside every walk with the witness it came from; the texts scrubbed. Issues #338, #1239.

  asako.py sitemap [--limit N]        every /annonces/<slug>-<hex> row of the ads' sitemap, with lastmod (1 request)
  asako.py list [--limit N]           the count the page states, then that sitemap's ads read from their pages (N pages, 20 unless told, 2 s apart)
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

**2026-11-02 03:14–03:17Z (#1239) — TWO THINGS MOVED AND THE ADAPTER'S GUARD CAUGHT BOTH.** Every
line above is kept as the dated record it is; what follows corrects it. The guard at `cmd_list`
exited 6 on «200 and no «N offres disponibles»», and that was the right verdict — the phrase HAS
gone from `/emploi`. It had NOT gone from the board:

  /emploi            200, 353 739 B (md5 f47bce8f0a80, identical twice) — REDESIGNED. No «offres
                     disponibles» anywhere; the count is there three times otherwise («479 offres
                     d'emploi» twice, «Vous voyez <strong>20</strong> offres sur <strong>479</strong>»)
                     and in the RSC flight as `totalCount`. **And the 20 cards are now real
                     `<a href="/annonces/...">` links, where the 2026-09 card recorded ZERO**, with
                     «Charger plus» now a server link `/emploi/page/2`, not a client action.
  /emploi/page/2     200, 204 801 B — the OLD template, «<strong>479</strong> offres disponibles»
                     intact, `totalCount` and `resultCount` both 479, 20 more ad links, `/page/3`.
                     So the template changed on PAGE 1 ONLY, and the reader was pointed at the one
                     page that stopped carrying its phrase.
  /sitemap.xml       200, 31 202 B, 361 rows, **not one advertisement** (234 /emploi/ facets, 112
                     employer profiles, 15 pages) — where 582 rows / 253 ads were on 2026-09-14.
  /sitemap-jobs.xml  200, 72 329 B, 479 rows, 478 ads (lastmod 2026-09-18 … 2026-11-01) — DECLARED
                     in robots.txt beside the root sitemap, and never read until today.
  the ad             200, 153 074 B — `record()` unchanged: JobPosting, UUID, employer, dates,
                     TELECOMMUTE, industry, category, the texts scrubbed.
  robots.txt         200, 1 877 B, md5 ba46383a2cc3 — the SAME md5 as 2026-09-14. `Claude-User` keeps
                     its own group, `Allow: /`, no Crawl-delay; 2 s is still ours.

THE TWO ENUMERATORS AGREE, which is the favourable case and had to be checked rather than assumed:
the 40 ad links of pages 1–2 are ALL in `sitemap-jobs.xml` (0 outside), its 479 rows match the 479
the page states. So the sitemap is a WITNESS and not a second population, and `/emploi/page/N` is a
measured fallback route if it ever stops being one. ONE row of the 479 is not emitted and says so:
`/annonces/sdr-b2b-freelance7d468b86`, hex glued to the slug.
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
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
HOST_FORMS = (HOST, "asako.mg")
LIST = f"https://{HOST}/emploi"
SITEMAP_JOBS = f"https://{HOST}/sitemap-jobs.xml"   # where the ads are, measured 2026-11-02: 479 rows, 478 ads
SITEMAP_ROOT = f"https://{HOST}/sitemap.xml"        # where they were on 2026-09-14 (582 rows, 253 ads) -- a candidate now, not the address
JOBS_HINT_RE = re.compile(r"job|emploi|annonce", re.I)

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+261[\s ]?|0)(?:\d[\s ]?){8,9}\d(?!\d)")
AD_RE = re.compile(r"^/annonces/([a-z0-9\-]+)-([0-9a-f]{4,12})/?$")
REFUSED_RE = re.compile(r"^/(?:api|admin|recruteur|candidat|dashboard|go)(?:/|$)")
ROW_RE = re.compile(r"<url>\s*<loc>([^<]+)</loc>(?:\s*<lastmod>([^<]+)</lastmod>)?", re.S)
COUNT_RE = re.compile(r"<strong[^>]*>\s*(\d[\d  ]*)\s*</strong>\s*(?:<!--\s*-->)?\s*offres? disponibles")
SEEN_OF_RE = re.compile(r"offres? sur\s*(?:<!--\s*-->)?\s*<strong[^>]*>\s*(\d[\d  ]*)\s*</strong>")
TOTAL_RE = re.compile(r'\\?"totalCount\\?"\s*:\s*(\d+)')

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
    """The count the listing states on the server, and WHICH witness answered — `(None, None)` when none does.

    THE STRUCTURE FIRST, THE PROSE AFTER, and that order IS the measurement of
    2026-11-02 rather than a preference: `/emploi` was redesigned and no longer
    carries «N offres disponibles» anywhere, while `/emploi/page/2` still carries
    it unchanged — so in seven weeks the PROSE moved and the KEY did not.
    `totalCount` is in the RSC flight of both pages and in no ad page.

    The prose form is kept as a fallback and not dropped: page 2 proves it is
    still served, and a witness that still answers is not a witness to retire.
    «… offres sur <strong>N</strong>» requires the `<strong>`, because the FAQ prose
    of the same page writes «340 offres sur 479» without it — measured in both
    directions, and without that requirement the reader would return 340.
    """
    b = body or ""
    m = TOTAL_RE.search(b)
    if m:
        return int(m.group(1)), "`totalCount` in the page's RSC flight"
    for name, rx in (("«N offres disponibles»", COUNT_RE), ("«… offres sur <strong>N</strong>»", SEEN_OF_RE)):
        m = rx.search(b)
        if m:
            return int(re.sub(r"\D", "", m.group(1))), name
    return None, None


def jobs_first(declared):
    """The sitemaps to try, in order: the host's own `Sitemap:` declarations whose
    address hints at jobs, then its other declarations in file order, then the two
    paths this adapter has measured — deduplicated, order preserved.

    THE ADS MOVED, AND THE HOST SAID SO ALL ALONG. On 2026-09-14 they were the
    253 `/annonces/` rows of `/sitemap.xml`; on 2026-11-02 that file carries 361
    rows and NOT ONE advertisement (234 `/emploi/` facets, 112 employer profiles,
    15 pages), while `/sitemap-jobs.xml` — declared in `robots.txt` beside it —
    carries 479 rows of which 478 are ads. A constant would have died on a host
    that was publishing the address; `_robots.sitemaps_for` reads the declaration,
    and its own docstring documents this trap.

    Only `www.asako.mg` and `asako.mg`: a row from a third host would carry that
    host into every record's `url`, and this adapter names its host as a literal
    (its card's `host-forms-basis`). A sitemap that moves off the host is a
    measurement to take, never a redirection to follow in silence.
    """
    ours = [u for u in declared if urllib.parse.urlsplit(u).netloc in HOST_FORMS]
    hinted = [u for u in ours if JOBS_HINT_RE.search(urllib.parse.urlsplit(u).path)]
    rest = [u for u in ours if u not in hinted]
    return list(dict.fromkeys(hinted + rest + [SITEMAP_JOBS, SITEMAP_ROOT]))


def sitemap_candidates():
    return jobs_first(gate(LIST).get("sitemaps") or [])


def sitemap_rows():
    """The ads from the first declared sitemap that carries one, with the URL that
    answered, the non-ad rows, and the `/annonces/` rows the ADDRESS pattern refused.

    A `/annonces/` row that `AD_RE` refuses is NOT filed under «other»: no identifier
    can be read from it, so it is not emitted, and an ad dropped in silence is the one
    thing a row count cannot show. Measured 2026-11-02: exactly ONE of the 479 rows —
    `/annonces/sdr-b2b-freelance7d468b86`, whose hex is glued to the slug with no
    hyphen. Emitting it would need a guess at where the slug ends, which is a decision
    and not a fix; the pattern stays as it is and the loss is DECLARED, and `list`
    already reports emitted against the stated count, so the arithmetic says it too.

    Trying the next candidate on a 404 means no path here renders EXIT_GONE any more:
    «every declared sitemap refuses» is the inventory having moved, never a dead board,
    and declaring a board dead is not ours to do.
    """
    tried = []
    for url in sitemap_candidates():
        code, body = request(url)
        if code != 200:
            tried.append(f"{url}: HTTP {code}")
            continue
        all_rows = ROW_RE.findall(body)
        rows, seen, other, refused = [], set(), 0, []
        for loc, lastmod in all_rows:
            path = urllib.parse.urlsplit(loc).path
            m = AD_RE.match(path)
            if not m:
                if path.startswith("/annonces/"):
                    refused.append(loc)
                else:
                    other += 1
                continue
            if m.group(2) in seen:
                continue
            seen.add(m.group(2))
            rows.append({"source": "asako", "country": "MG", "ledger_id": f"asako:{m.group(2)}", "id": m.group(2), "url": loc, "slug": m.group(1), "lastmod": (lastmod or "")[:10] or None,"language": "fr"})
        if rows:
            return rows, other, refused, url
        tried.append(f"{url}: 200, {th(len(all_rows))} row(s) and not one /annonces/<slug>-<hex>")
    die(f"not one of the sitemaps {HOST} declares carries an advertisement ({'; '.join(tried)}) — the inventory moved; not an empty market", EXIT_PARTIAL)


def cmd_sitemap(a):
    rows, other, refused, url = sitemap_rows()
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{th(len(rows))} ad row(s) in {url} ({th(other)} other rows set aside — facets, employer profiles, pages); `list` prints the listing's stated count beside them.")
    if refused:
        shown = ", ".join(refused[:3]) + (" …" if len(refused) > 3 else "")
        note(f"{th(len(refused))} /annonces/ row(s) NOT emitted — the address pattern refuses them, so no identifier can be read: {shown}")
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
    total, witness = stated(body)
    if total is None:
        die(f"{LIST}: 200 and no count stated on the server — neither `totalCount` in its RSC flight, nor «N offres disponibles», nor «… offres sur <strong>N</strong>» — the template changed; not an empty market", EXIT_PARTIAL)
    rows, other, refused, smap = sitemap_rows()
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
    note(f"the count comes from {witness} on {LIST}; the inventory from {smap}.")
    if refused:
        shown = ", ".join(refused[:3]) + (" …" if len(refused) > 3 else "")
        note(f"{th(len(refused))} /annonces/ row(s) NOT emitted — the address pattern refuses them, so no identifier can be read: {shown}")
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
    s_ = sub.add_parser("sitemap", help="every /annonces/ row of the ads' sitemap, derived from the host's own declarations (1 request)")
    s_.add_argument("--limit", type=int)
    s_.set_defaults(fn=cmd_sitemap)
    l_ = sub.add_parser("list", help="the count the page states, then the declared sitemap's ads read from their pages — 20 unless --limit")
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
