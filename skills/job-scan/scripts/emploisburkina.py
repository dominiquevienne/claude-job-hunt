#!/usr/bin/env python3
"""Emplois Burkina (`emploisburkina.bf`) — the Afrique Emplois network's Burkinabè front: the root and each category page state their count and carry fifteen cards, of which the open ones link `/post/<id>` and the «EXCLUSIF» ones open a subscription; the rest of the list is behind `/api/load-more`, refused in writing. The adapter reads only what the site serves without exception — the open cards of the root and of the five category pages, the open post pages — and prints the shortfall against the stated count. Issue #300; the pilot's reading of 2026-09-14 («ça compte») applies.

  emploisburkina.py list [--limit N]         the open cards of the root and of the category pages, 3 s apart (6 requests)
  emploisburkina.py ad --url <https://emploisburkina.bf/post/<id>>

THE RULES (2026-09-14): `*` `Allow: /`, `Disallow: /api/`, `/login`, `/register`, `/forgot-password`,
`/profile`, `/subscription`, `/talents/create`; `Crawl-delay: 1` (3 s is ours — the host refused
connections after the eleventh request on 2026-09-08); `Sitemap: https://afriqueemplois.com/sitemap.xml`
(the network's per-country job sitemaps, `sitemap-jobs-BF.xml` among them — 500 on the day, twice).

WHAT IS SERVED, AND WHAT IS NOT. The root (200, ~299 KB) prints «2305 offres» beside «Offres
d'emploi» and a `CollectionPage` JSON-LD with `numberOfItems: 2305`; `#posts-container` holds
fifteen `<article>` cards: an open card links `https://emploisburkina.bf/post/<id>` (the title in
`<h3>`, an excerpt in `<p>`, a level badge — «Niveau BAC+3», «Multiple», «Autres» —, a date «14
sept. 2026», a comment count), an «EXCLUSIF» card carries `data-exclusive-offer` and opens
`showSubscriptionModal()` — **never opened**. The rest of the list loads by
`fetch('/api/load-more?page=…&category=…')` — **`/api/` is refused in writing, never sent**. The
five category pages (`/category/12` BAC, 13 BAC+2, 14 BAC+3, 16 BAC+5, 25 Multiple) are the same
shape with their own count («165 offres d'emploi dans la catégorie», `numberOfItems: 165`).
The post page (200, ~93 KB) carries the `<h1>`, «Date limite: 14 sept. 2026», the body (an
e-mail address in it on the ad read — scrubbed), «Postuler»; WebSite / Organization /
BreadcrumbList JSON-LD and no JobPosting (there was one on 2026-09-08).

**So `list` prints «N emitted (M exclusive set aside), the site states 2 305 — short» on every
run, and says why: the pager is a refused route, the exclusives a subscription.** Measured
2026-09-14 10:47–11:1x UTC by the declared client, the guard on the exact path, 3 s apart.
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

HOST = "emploisburkina.bf"
ROOT = f"https://{HOST}/"
CATEGORIES = ("12", "13", "14", "16", "25")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+226[\s ]?)?(?:\d{2}[\s ]?){3}\d{2}(?!\d)")
REFUSED_RE = re.compile(r"^/(?:api|login|register|forgot-password|profile|subscription)(?:/|$)|^/talents/create")
AD_RE = re.compile(r"^/post/(\d+)/?$")
COUNT_RE = re.compile(r"(\d[\d  ]*)\s*offres")
ARTICLE_RE = re.compile(r"<article[^>]*>(.*?)</article>", re.S)
LINK_RE = re.compile(r'href="https://emploisburkina\.bf/post/(\d+)"')
H3_RE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
P_RE = re.compile(r'<p class="text-gray-600[^"]*">(.*?)</p>', re.S)
BADGE_RE = re.compile(r'<span class="inline-flex[^"]*">(.*?)</span>', re.S)
DATE_RE = re.compile(r'data-lucide="calendar"[^>]*></i>\s*([^<]+)')
MONTHS_FR = {"janv.": 1, "févr.": 2, "mars": 3, "avr.": 4, "mai": 5, "juin": 6, "juil.": 7, "août": 8, "sept.": 9, "oct.": 10, "nov.": 11, "déc.": 12}

_PACE = Pace(HOST, own=3.0)   # Crawl-delay 1 written; 3 s is ours — the host refused connections after the eleventh request on 2026-09-08


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[emploisburkina] {msg}", file=sys.stderr)


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
        die(f"{url}: refused in writing (the app's routes, the accounts, the subscription) — never sent", EXIT_REFUSED)
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


def text(markup):
    markup = re.sub(r"<!--.*?-->", "", markup or "", flags=re.S)
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup)
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t ]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def fr_date(s):
    """«14 sept. 2026» → 2026-09-14; anything else stays as printed."""
    m = re.match(r"\s*(\d{1,2})\s+([a-zéû.]+)\s+(\d{4})", s or "")
    if m and m.group(2) in MONTHS_FR:
        return f"{m.group(3)}-{MONTHS_FR[m.group(2)]:02d}-{int(m.group(1)):02d}"
    return (s or "").strip() or None


def stated(body):
    """The page's own «N offres» — or `None`."""
    m = COUNT_RE.search(text(body or "")[:20000])
    return int(re.sub(r"\D", "", m.group(1))) if m else None


def cards(body):
    """`(open cards, exclusive count)` — an exclusive card carries `data-exclusive-offer` and opens a subscription: counted, never opened."""
    out, excl = [], 0
    for a in ARTICLE_RE.findall(body or ""):
        if "data-exclusive-offer" in a:
            excl += 1
            continue
        m = LINK_RE.search(a)
        if not m:
            continue
        h3 = H3_RE.search(a)
        p = P_RE.search(a)
        badges = [text(b) for b in BADGE_RE.findall(a)]
        d = DATE_RE.search(a)
        out.append({
            "source": "emploisburkina", "country": "BF", "ledger_id": f"emploisburkina:{m.group(1)}", "id": m.group(1), "url": f"https://{HOST}/post/{m.group(1)}",
            "title": text(h3.group(1)) if h3 else None, "excerpt": scrub(text(p.group(1))) if p else None,
            "level": next((b for b in badges if b and b != "EXCLUSIF"), None),
            "posted": fr_date(d.group(1)) if d else None,
            "language": "fr", "contacts_withheld": True,
        })
    return out, excl


def cmd_list(a):
    code, body = request(ROOT)
    if code != 200:
        die(f"{ROOT}: HTTP {code}", EXIT_PARTIAL)
    total = stated(body)
    if total is None:
        die(f"{ROOT}: 200 and no «N offres» on the page — the template changed; not an empty market", EXIT_PARTIAL)
    rows, seen, excl, pages = [], set(), 0, 1
    cs, e = cards(body)
    if not cs and not e:
        die(f"{ROOT}: 200 and not one card in the page — the template changed; not an empty market", EXIT_PARTIAL)
    excl += e
    for c in cs:
        if c["id"] not in seen:
            seen.add(c["id"])
            rows.append(c)
    for cat in CATEGORIES:
        if a.limit and len(rows) >= a.limit:
            break
        url = f"https://{HOST}/category/{cat}"
        code, page = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        pages += 1
        cs, e = cards(page)
        excl += e
        for c in cs:
            if c["id"] not in seen:
                seen.add(c["id"])
                c["category_page"] = cat
                rows.append(c)
    if a.limit:
        rows = rows[:a.limit]
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    n = len(rows)
    verdict = "equal" if n == total else (f"{th(total - n)} short" if n < total else f"{th(n - total)} more emitted")
    note(f"{th(n)} emitted from {pages} page(s) ({th(excl)} exclusive card(s) set aside — behind a subscription, never opened), the site states {th(total)} — {verdict}.")
    note("the rest of the list is behind /api/load-more, refused in writing to every route; the exclusives behind a paid subscription: the shortfall is the site's, printed and not filled.")


def record(body, jid, url):
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body or "", re.S)
    if not h1:
        return None
    dl = re.search(r"Date limite\s*:\s*([^<\n]+)", body or "")   # before the heading, in the page's header block
    after = text(body[h1.end():])   # the page from its heading on, so the <title> is never mistaken for the heading
    j = re.search(r"\n(?:POSTULER|Postuler)\b", after)
    bodytxt = (after[:j.start()] if j else after).strip() or None
    return {
        "source": "emploisburkina", "country": "BF", "ledger_id": f"emploisburkina:{jid}", "id": jid, "url": url,
        "title": text(h1.group(1)) or None,
        "deadline": fr_date(dl.group(1)) if dl else None,
        "description": scrub(bodytxt),
        "language": "fr", "contacts_withheld": True,
    }


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc not in (HOST, "www." + HOST) or not m:
        die(f"{a.url}: not a job address (https://{HOST}/post/<id>)")
    url = f"https://{HOST}/post/{m.group(1)}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    rec = record(body, m.group(1), url)
    if rec is None:
        die(f"{url}: 200 without the ad's heading — the template changed, or an exclusive behind the subscription", EXIT_PARTIAL)
    print(json.dumps(rec, ensure_ascii=False))
    note(f"{url}: read from the page's own markup (no JobPosting on this site today); the text scrubbed; the application never touched.")


def main():
    p = argparse.ArgumentParser(description="Emplois Burkina — the open cards the site serves, the stated count beside them and the shortfall said; nothing refused in writing is asked. Issue #300.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the open cards of the root and the category pages (6 requests)")
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
