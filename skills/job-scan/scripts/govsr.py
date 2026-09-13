#!/usr/bin/env python3
"""Vacatures bij de Overheid van Suriname (`gov.sr/vacatures/`) — the State's own vacancy list, one card per posting from the ministries, read from the WordPress pages the site serves at the 60 s the site asks; the register's own count (`X-WP-Total`) printed beside every walk. Issue #443.

  govsr.py list [--pages N] [--limit N]
  govsr.py ad --url <https://gov.sr/vacature/<slug>/>

THE ROUTE IS THE LIST PAGE — and the host's `Crawl-delay: 60` rules the design:

  robots.txt                             user-agent: * / disallow: (nothing) / crawl-delay: 60
  GET /wp-json/wp/v2/vacature?per_page=1  -> the header `X-WP-Total: 133` — the register's own count, one request
  GET /vacatures/  /vacatures/2/  …       -> 6 cards a page; each card carries what the posting says
  GET /vacature/<slug>/                   -> the posting's own page: the title and the ministry — AND NOTHING ELSE

**The card is where the posting lives.** The WordPress REST route lists every
`vacature` (id, date, slug, link, title, ministry as a category) but exposes no
deadline, location or text — those are custom fields Elementor renders on the list
card only: «Categorie: Ministerie van …», a summary, «Locatie: …», «Gepubliceerd:
DD/MM/YYYY», «Inleverdatum tot: DD/MM/YYYY», and a «Meer info» link to the
ministry's PDF (the terms of reference). The posting's own page renders the title and
the ministry and an empty content widget. So `list` walks the LIST PAGES and reads the
cards; the API is asked once, for its count, which is the witness.

**Sixty seconds between requests, because the host says so** — `_pace` reads the
Crawl-delay and applies it. A page is 6 cards, so **`--pages` defaults to 5** (30
cards, five minutes) and the note says the walk was bounded by request; the whole
register (133 on the day → 23 pages) is `--pages 23`, twenty-three minutes, and is a
choice, not the default.

Measured 2026-09-13 23:39–23:5x UTC by the declared client: `X-WP-Total: 133`; the
list `/vacatures/` 6 cards, dated 07/09/2026 back to 24/07/2026 on page 1, the
pager to `/vacatures/5/` in view; the posting page `/vacature/energy-consultant/`
bare. No contact is emitted: a card's «Locatie» is a ministry's street address and
is kept as the workplace; an e-mail in a card's text is dropped from the summary.
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

HOST = "gov.sr"
BASE = f"https://{HOST}"
LIST = f"{BASE}/vacatures/"
API = f"{BASE}/wp-json/wp/v2/vacature?per_page=1"
PAGE_SIZE = 6
DETAIL_RE = re.compile(r"^https?://gov\.sr/vacature/([A-Za-z0-9._-]+)/?$")
CARD_RE = re.compile(r'<div data-elementor-type="loop"[^>]*class="[^"]*\bpost-(\d+)\b[^"]*\btype-vacature\b[^"]*"[^>]*>(.*?)(?=<div data-elementor-type="loop"|<nav\b|<div class="e-load-more-anchor|$)', re.S)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[govsr] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=3.0)   # the rules say `crawl-delay: 60` — the longer wins, and it is the host's


def request(url):
    """One GET — (code, body, headers). `X-WP-Total` is read off the headers of the API answer."""
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/json;q=0.9", "Accept-Language": "nl"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, "", dict(e.headers or {})
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t​‍]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def stated(headers):
    """The register's own count, from the API's `X-WP-Total` header."""
    for k, v in (headers or {}).items():
        if k.lower() == "x-wp-total" and str(v).strip().isdigit():
            return int(v)
    return None


def cards(body):
    """One record per Elementor loop item of type `vacature` — the card's icon-list lines are the posting's fields."""
    out = []
    for m in CARD_RE.finditer(body or ""):
        pid, seg = m.group(1), m.group(2)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", seg, re.S)
        lines = [re.sub(r"\s+", " ", htmlmod.unescape(x)).strip() for x in re.findall(r'elementor-icon-list-text[^>]*>\s*([^<]{2,2000})', seg)]
        f = {"summary": None, "workplace": None, "published": None, "deadline": None, "ministry": None}
        for l in lines:
            if l.startswith("Categorie:"):
                f["ministry"] = l[len("Categorie:"):].strip() or None
            elif l.startswith("Locatie:"):
                f["workplace"] = f["workplace"] or (l[len("Locatie:"):].strip() or None)
            elif l.startswith("Gepubliceerd:"):
                f["published"] = l[len("Gepubliceerd:"):].strip() or None
            elif l.startswith("Inleverdatum tot:"):
                f["deadline"] = l[len("Inleverdatum tot:"):].strip() or None
            elif f["summary"] is None:
                f["summary"] = MAIL_RE.sub("[e-mail withheld]", l)
        link = re.search(r'href="(https://gov\.sr/vacature/[^"]+)"', seg)
        pdf = re.search(r'href="(https://gov\.sr/wp-content/uploads/[^"]+\.pdf)"', seg, re.I)
        out.append({
            "source": "govsr", "country": "SR", "ledger_id": f"govsr:{pid}", "id": pid,
            "url": htmlmod.unescape(link.group(1)) if link else f"{BASE}/?p={pid}",
            "title": text(h1.group(1)) if h1 else None,
            "employer": f["ministry"],                      # the ministry — the State's own service is the employer
            "workplace": f["workplace"],                    # «Locatie: …» — the ministry's address as the card prints it
            "published": f["published"],                    # DD/MM/YYYY as printed
            "application_deadline": f["deadline"],          # «Inleverdatum tot: DD/MM/YYYY», or null when the card gives none
            "summary": f["summary"],
            "terms_of_reference": htmlmod.unescape(pdf.group(1)) if pdf else None,   # the «Meer info» PDF — a link, never fetched
            "language": "nl",
        })
    return out


def cmd_list(a):
    code, _, headers = request(API)
    total = stated(headers) if code == 200 else None
    if code != 200:
        note(f"{API}: HTTP {code} — the register's count is not read; the walk goes on without a witness.")
    out, seen, pageno = [], set(), 0
    while True:
        pageno += 1
        url = LIST if pageno == 1 else f"{LIST}{pageno}/"
        code, body, _ = request(url)
        if code == 404 and pageno > 1:
            pageno -= 1
            break
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        rows = cards(body)
        if pageno == 1 and not rows:
            if (total or 0) > 0:
                die(f"{LIST}: the register states {total} and the first page carries no card — a reading fault, not an empty list.", EXIT_PARTIAL)
            note("no card on the first page and no count from the register — the State lists nothing.")
            return
        new = 0
        for r in rows:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            out.append(r)
            new += 1
        if new == 0 or len(rows) < PAGE_SIZE or (total and len(out) >= total):
            break
        if a.pages and pageno >= a.pages:
            break
        if a.limit and len(out) >= a.limit:
            break
    emitted = out[:a.limit] if a.limit else out
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    if total is None:
        note(f"{th(n)} emitted over {pageno} page(s) of {PAGE_SIZE} at 60 s; no count from the register.")
        return
    bounded = (a.pages and pageno >= a.pages and total > pageno * PAGE_SIZE) or (a.limit and a.limit < total)
    if bounded:
        note(f"{th(n)} emitted of the {th(total)} the register states — {pageno} page(s) of {PAGE_SIZE} walked by request (--pages/--limit) at the 60 s the host asks, not a shortfall; the whole register is --pages {-(-total // PAGE_SIZE)}.")
    elif n == total:
        note(f"{th(n)} emitted over {pageno} page(s), register states {th(total)} — equal.")
    else:
        note(f"{th(n)} emitted over {pageno} page(s), register states {th(total)} — {th(abs(total - n))} " + ("short" if total > n else "more emitted than the register states") + ".")


def cmd_ad(a):
    m = DETAIL_RE.match((a.url or "").strip())
    if not m:
        die(f"{a.url}: not a vacature address — expected {BASE}/vacature/<slug>/")
    slug = m.group(1)
    code, body, _ = request(a.url)
    if code in (404, 410):
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    h1 = re.search(r'<h1 class="elementor-heading-title[^"]*"[^>]*>(.*?)</h1>', body, re.S)
    if not h1 or "type-vacature" not in body:
        die(f"{a.url}: not a vacature page ({len(body)} characters) — a redirect or the site's 404 template.", EXIT_PARTIAL)
    pid = re.search(r'class="[^"]*\bpost-(\d+)\b[^"]*\btype-vacature\b', body)   # the vacature's own element — the template wrapper carries a `post-N` of its own (308 on the day)
    ministry = None
    mm = re.search(r'class="[^"]*\bcategory-([a-z0-9-]+)\b', body)
    if mm:
        # the name as the page's own menu writes it: the anchor whose address ends in the category's slug
        an = re.search(r'href="https://gov\.sr/(?:ministeries|kabinetten)/[^"]*%s/"[^>]*>(?:\s*<[^>]+>)*\s*([^<]{3,160})' % re.escape(mm.group(1)), body)
        ministry = htmlmod.unescape(an.group(1)).strip() if an else None
    print(json.dumps({
        "source": "govsr", "country": "SR", "ledger_id": f"govsr:{pid.group(1) if pid else slug}", "id": pid.group(1) if pid else slug, "url": a.url,
        "title": text(h1.group(1)) or None,
        "employer": ministry,                     # from the post's category slug — the page prints the name in a heading above the title too
        "employer_slug": mm.group(1) if mm else None,
        # the posting's own page renders the title and the ministry and an empty content widget:
        # the deadline, the location, the summary and the terms-of-reference PDF are on the LIST card — `list` reads them
        "detail_is_bare": True,
        "language": "nl",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Vacatures bij de Overheid van Suriname — the State's vacancy cards, read at the 60 s the host asks; the register's X-WP-Total beside every walk. Issue #443.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the vacancy cards, 6 a page, 60 s apart, 5 pages unless told otherwise (the whole register is --pages 23 on the day)")
    l_.add_argument("--pages", type=int, default=5)
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one posting's own page — bare: the title and the ministry; the fields are on the list card")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
