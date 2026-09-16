#!/usr/bin/env python3
"""Trabajando Bolivia (`trabajando.com.bo`) — the Trabajando.com network's Bolivian front, a Drupal site: the list `/trabajo?page=N` (0-based) serves its cards on the server with the site's own count («encontrarás 344 trabajos y ofertas de empleo en toda Bolivia»), and each ad carries a JobPosting; the count printed beside every walk; the description scrubbed. Issue #430.

  trabajando_bo.py list [--pages N]     the cards of /trabajo?page=0 … until the pager ends (23 pages on the day, 2 s apart), the stated count beside them
  trabajando_bo.py ad --url <https://trabajando.com.bo/trabajo/<city>/<category>/<slug>-<nid>>

THE RULES. Drupal's file for `*`: the engine's directories, `/admin/`, `/search/`, `/search?`,
`/node/add/`, `/user/logout`, and — the lines that matter here — `/*buscar=`, `/*sort=`, `/*f[`:
the keyword search, the sort and the facets are refused in writing; the plain list and its
`?page=` are not. The adapter never sends a search, a sort or a facet (refused before the gate),
and never touches `/user/`. No Crawl-delay; 2 s is ours.

THE LIST. `/trabajo` (200, ~168 KB) is server-rendered: `<article data-nid="N">` cards — an
`<h2><a href="/trabajo/<city>/<category>/<slug>-<nid>">` title, the employer as a link to
`/empresa/<slug>`, a plain name without a profile, or «Empresa confidencial» in italics, a two-line excerpt, the hours («Jornada
completa», «Media jornada»…), the city, a `<time datetime>` — fifteen a page, three «Destacado»
cards on top of page 0 (18 there); the pager `?page=0 … 22` on the day, page 22 with 14: 22 × 15 +
14 = 344, the count the page states in prose («En Trabajando.com.bo encontrarás 344 trabajos y
ofertas de empleo en toda Bolivia»). The walk stops when a page brings no new card, and dies (exit 6)
when a page 200 carries no card at all or repeats page 0. THE AD. `/trabajo/<city>/<category>/
<slug>-<nid>` (200, ~60 KB) carries a JobPosting in an `@graph` — title, employmentType,
datePosted, validThrough, identifier (Trabajando.com.bo, the nid), hiringOrganization (name,
sameAs, logo), jobLocation (locality, region, BO), description (HTML), industry — beside a
BreadcrumbList. **The description is scrubbed of e-mail addresses and Bolivian telephone numbers —
the ad read on the day carried «Enviar CV … al 76469326» in its own text; `contacts_withheld` on
every record; the application (a candidate account) never touched.**

Measured 2026-09-16 06:08–06:09 UTC by the declared client, the guard on the exact path: robots 200
(4 115 B); `/` 124 767 B, «344 ofertas»; `/trabajo` 167 881 B, 18 cards; `?page=1` 15; `?page=22` 14;
the ad 59 996 B with its JobPosting.
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

HOST = "trabajando.com.bo"
LIST = f"https://{HOST}/trabajo"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+?591[\s\-]?)?(?:[67]\d{7}|[2-4][\s\-]?\d{6,7})(?!\d)")   # mobiles 6xxxxxxx / 7xxxxxxx, landlines 2/3/4 + 6–7 digits, with or without +591
AD_RE = re.compile(r"^/trabajo/([a-z0-9\-]+)/([a-z0-9\-]+)/([a-z0-9\-]+)-(\d+)/?$")
REFUSED_RE = re.compile(r"^/(?:admin|search|node/add|user|comment/reply|filter/tips|media/oembed|index\.php)(?:[/?]|$)")
REFUSED_QUERY_RE = re.compile(r"(?:^|[?&])(?:buscar|sort|f(?:%5B|\[))", re.I)
CARD_RE = re.compile(r'<article[^>]*\bdata-nid="(\d+)"[^>]*>(.*?)</article>', re.S)
TITLE_RE = re.compile(r'<h2[^>]*>\s*<a href="(/trabajo/[^"]+)"[^>]*>(.*?)</a>', re.S)
EMPLOYER_RE = re.compile(r'<a href="/empresa/([^"]+)"[^>]*>(.*?)</a>', re.S)
EMPLOYER_PLAIN_RE = re.compile(r'<div class="mt-0.5 flex items-center gap-2 text-sm">\s*<span[^>]*>\s*(.*?)\s*</span>', re.S)   # a named employer without a profile link, or «Empresa confidencial» in italics
BADGE_RE = re.compile(r'<span class="inline-flex items-center gap-1.5">\s*(?:<svg.*?</svg>\s*)?([^<]+?)\s*</span>', re.S)
TIME_RE = re.compile(r'<time datetime="([^"]+)"')
COUNT_RE = re.compile(r"encontrarás\s+(\d[\d\.,]*)\s+trabajos y ofertas de empleo")
PAGE_RE = re.compile(r'href="\?page=(\d+)"')

_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written; 2 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[trabajando_bo] {msg}", file=sys.stderr)


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
    if REFUSED_RE.search(parts.path) or REFUSED_QUERY_RE.search(parts.query):
        die(f"{url}: refused in writing to `*` (the search, the sort, the facets, the accounts) — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "es"})
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
    t = re.sub(r"<br\s*/?>|</p>|</li>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t))
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def stated(body):
    """The count the list prints in prose — «encontrarás 344 trabajos y ofertas de empleo en toda Bolivia» — or `None`."""
    m = COUNT_RE.search(body or "")
    return int(re.sub(r"\D", "", m.group(1))) if m else None


def cards(body):
    out = []
    for nid, inner in CARD_RE.findall(body):
        t = TITLE_RE.search(inner)
        if not t:
            continue
        m = AD_RE.match(t.group(1))
        emp = EMPLOYER_RE.search(inner)
        badges = [b.strip() for b in BADGE_RE.findall(inner)]
        tm = TIME_RE.search(inner)
        out.append({
            "source": "trabajando_bo", "country": "BO", "ledger_id": f"trabajando_bo:{nid}", "id": nid, "url": f"https://{HOST}{t.group(1)}",
            "title": text(t.group(2)), "company": text(emp.group(2)) if emp else text((EMPLOYER_PLAIN_RE.search(inner) or [None, ""])[1]),
            "company_profile": f"https://{HOST}/empresa/{emp.group(1)}" if emp else None,
            "city": m.group(1) if m else None, "category": m.group(2) if m else None,
            "hours": badges[0] if len(badges) > 1 else None, "place": badges[1] if len(badges) > 1 else (badges[0] if badges else None),
            "posted": (tm.group(1) or "")[:10] or None, "featured": "Destacado" in inner,
            "contacts_withheld": True, "language": "es",
        })
    return out


def cmd_list(a):
    out, seen, first_ids, pages, last = [], set(), None, 0, None
    n = 0
    while True:
        url = LIST if n == 0 else f"{LIST}?page={n}"
        code, body = request(url)
        if code == 404:
            break
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if n == 0:
            total = stated(body)
            if total is None:
                die(f"{url}: 200 and no «encontrarás N trabajos y ofertas de empleo» in the page — the template changed; not an empty market", EXIT_PARTIAL)
            last = max((int(x) for x in PAGE_RE.findall(body)), default=0)
        cs = cards(body)
        if not cs:
            die(f"{url}: 200 and no card — the template changed; not an empty page", EXIT_PARTIAL)
        ids = [c["id"] for c in cs]
        if first_ids is None:
            first_ids = ids
        elif ids == first_ids:
            die(f"{url}: the same cards as page 0 — the pager is not honoured; stopped", EXIT_PARTIAL)
        new = 0
        for c in cs:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            out.append(c)
            new += 1
        pages += 1
        if new == 0 or n >= last or (a.pages and pages >= a.pages):
            break
        n += 1
    for c in out:
        print(json.dumps(c, ensure_ascii=False))
    emitted = len(out)
    if a.pages and pages >= a.pages and n < last:
        note(f"{th(emitted)} emitted from {pages} page(s) of the {last + 1} the pager names; the site states {th(total)} — walked by request (--pages), not a shortfall.")
    else:
        verdict = "equal" if emitted == total else (f"{th(total - emitted)} short" if emitted < total else f"{th(emitted - total)} more emitted")
        note(f"{th(emitted)} emitted from {pages} page(s), the site states {th(total)} — {verdict}.")
    note("cards only — `ad --url` reads a JobPosting, scrubbed; the search, the sort and the facets are refused in writing and never sent.")


def record(body, nid, url):
    jp = (postings(body) or [None])[-1]
    if jp is None:
        return None
    org = one(jp.get("hiringOrganization"))
    addr = one(one(jp.get("jobLocation")).get("address"))
    ident = jp.get("identifier") if isinstance(jp.get("identifier"), str) else one(jp.get("identifier")).get("value")
    m = AD_RE.match(urllib.parse.urlsplit(url).path)
    return {
        "source": "trabajando_bo", "country": "BO", "ledger_id": f"trabajando_bo:{nid}", "id": nid, "url": url, "nid": ident or None,
        "title": htmlmod.unescape(jp.get("title") or "").strip() or None,
        "company": (org.get("name") or "").strip() or None, "company_site": org.get("sameAs") if org.get("sameAs") and org.get("sameAs").rstrip("/") != f"https://{HOST}" else None,
        "employment_type": jp.get("employmentType") or None, "industry": jp.get("industry") or None,
        "city": m.group(1) if m else None, "category": m.group(2) if m else None,
        "place": addr.get("addressLocality") or None, "region": addr.get("addressRegion") or None, "address_country": addr.get("addressCountry") or None,
        "posted": (jp.get("datePosted") or "")[:10] or None, "valid_through": (jp.get("validThrough") or "")[:10] or None,
        "description": scrub(text(jp.get("description"))),
        "contacts_withheld": True, "language": "es",
    }


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc not in (HOST, "www." + HOST) or not m:
        die(f"{a.url}: not a job address (https://{HOST}/trabajo/<city>/<category>/<slug>-<nid>)")
    url = f"https://{HOST}{parts.path.rstrip('/')}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    rec = record(body, m.group(4), url)
    if rec is None:
        die(f"{url}: 200 without a JobPosting — the template changed", EXIT_PARTIAL)
    print(json.dumps(rec, ensure_ascii=False))
    note(f"{url}: read from its JobPosting; description scrubbed; the application never touched.")


def main():
    p = argparse.ArgumentParser(description="Trabajando Bolivia — the list's cards with the site's stated count beside them, each ad from its JobPosting; descriptions scrubbed. Issue #430.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="/trabajo?page=0 … until the pager ends, 2 s apart")
    l_.add_argument("--pages", type=int, help="stop after N pages (a bound, printed as such)")
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
