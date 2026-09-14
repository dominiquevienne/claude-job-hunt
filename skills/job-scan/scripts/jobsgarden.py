#!/usr/bin/env python3
"""Jobsgarden (`www.jobsgarden.hu`, Hungary — a recruitment agency's own board): its WordPress posts of the «jobs-hu» category through the REST API the site publishes, `X-WP-Total` as the count it states; the ad page's own header line for the place. Issue #364.

  jobsgarden.py list [--pages N | --all] [--limit N]
  jobsgarden.py ad --url <https://www.jobsgarden.hu/<slug>/>

THE ROUTE IS THE SITE'S OWN REST API. The board is a WordPress category:
every ad is a post in «jobs-hu» (id 8, `count` 77 on 2026-09-14), with a
sub-category per practice (industry 4, IT 5, SSC 6, corporate 7).
`GET /wp-json/wp/v2/posts?categories=8&per_page=100&page=<p>&_fields=…`
answers the posts as JSON and **`X-WP-Total` / `X-WP-TotalPages` in the
headers** — the count the site states, printed beside the emitted count:
«77 emitted over 1 page(s), site states 77 — equal» (2026-09-14). The HTML
list `/allasajanlatok/` (7 pages of the theme's grid) is the same
inventory and is not walked. No key, no cookie, no browser; `robots.txt`
(66 B) is an empty `*` group and a sitemap line — open, `certain: True`;
3 s own spacing.

THE POST: `id`, `link` (`/<slug>/`, an opaque slug), `title.rendered`
(«Staff Software Engineer (VB-12683)» — the reference in brackets is
emitted as `reference`), `date`, `modified`, `excerpt.rendered` (the one
sentence that names the client's sector), `categories` (mapped to the
practice). The place is **not** in the REST answer: it is in the ad page's
header line «2026-08-25 • Budapest • IT» (`div.jg-job-attributes`), which
`ad` reads together with `content.rendered` from the API.

WHAT IS WITHHELD. The agency's own office, phones and e-mail sit in the
page footer — in no field this file emits; addresses and phone numbers in
the prose are replaced (`[e-mail withheld]`, `[phone withheld]` — nine
digits or more, Hungarian numbers are nine). The client is not named on
the ads (the agency writes «partnerünk»), and that is the board's choice.
"""

import argparse
import html
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

HOST = "www.jobsgarden.hu"
BASE = f"https://{HOST}"
API = f"{BASE}/wp-json/wp/v2/posts"
JOBS_CATEGORY = 8
PRACTICES = {4: "industry", 5: "it", 6: "ssc", 7: "corporate"}
FIELDS = "id,link,title,date,modified,excerpt,categories"
PAGE_SIZE = 100
DEFAULT_PAGES = 10
AD_RE = re.compile(r"^https?://(?:www\.)?jobsgarden\.hu/([a-z0-9-]+)/?$")
REF_RE = re.compile(r"\(([A-Z]{1,4}-\d{3,7})\)\s*$")
ATTR_RE = re.compile(r'<div class="jg-job-attributes">\s*(.*?)\s*</div>', re.S)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+|\w+\[kukac\]\w+(?:\.\w+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\d[\d\s().-]{6,}\d(?!\w)")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACE = Pace(HOST, own=3.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobsgarden] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    """One GET — `(code, body, headers)`; the headers carry the API's own total."""
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "application/json, text/html"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, "", dict(e.headers or {})
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def clean(s):
    s = re.sub(r"<(script|style)\b.*?</\1>", "", s or "", flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h\d>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def redact(s):
    s = EMAIL_RE.sub("[e-mail withheld]", s or "")
    return PHONE_RE.sub(lambda m: "[phone withheld]" if sum(c.isdigit() for c in m.group(0)) >= 9 else m.group(0), s)


def hdr(headers, name):
    for k, v in (headers or {}).items():
        if k.lower() == name.lower():
            try:
                return int(v)
            except (TypeError, ValueError):
                return None
    return None


def record(p):
    title = clean((p.get("title") or {}).get("rendered") or "")
    ref = REF_RE.search(title)
    cats = p.get("categories") or []
    return {
        "source": "jobsgarden", "country": "HU", "ledger_id": f"jobsgarden:{p.get('id')}", "id": str(p.get("id")), "url": p.get("link"),
        "title": redact(REF_RE.sub("", title).strip()) or None, "reference": ref.group(1) if ref else None,
        "practice": next((PRACTICES[c] for c in cats if c in PRACTICES), None),
        "posted": (p.get("date") or "")[:10] or None, "modified": (p.get("modified") or "")[:10] or None,
        "summary": redact(clean((p.get("excerpt") or {}).get("rendered") or "")) or None,
    }


def cmd_list(a):
    if a.pages is not None and a.pages < 1:
        die("--pages must be at least 1 (or use --all).")
    limit_pages = None if a.all else (a.pages or DEFAULT_PAGES)
    seen, emitted, page, site, total_pages = set(), 0, 0, None, None
    while True:
        page += 1
        url = f"{API}?" + urllib.parse.urlencode({"categories": JOBS_CATEGORY, "per_page": PAGE_SIZE, "page": page, "_fields": FIELDS})
        code, body, headers = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        try:
            posts = json.loads(body)
        except ValueError:
            die(f"{url}: not JSON ({len(body)} characters).", EXIT_PARTIAL)
        if not isinstance(posts, list):
            die(f"{url}: the answer is not a list of posts.", EXIT_PARTIAL)
        if site is None:
            site, total_pages = hdr(headers, "X-WP-Total"), hdr(headers, "X-WP-TotalPages")
            if site is None:
                die(f"{url}: the API states no X-WP-Total.", EXIT_PARTIAL)
        new = 0
        for p in posts:
            r = record(p)
            if not r["id"] or r["id"] in seen:
                continue
            seen.add(r["id"])
            print(json.dumps(r, ensure_ascii=False))
            emitted += 1
            new += 1
            if a.limit and emitted >= a.limit:
                break
        if a.limit and emitted >= a.limit:
            note(f"{emitted} emitted over {page} page(s), site states {site} — walk bounded by request (--limit), not compared.")
            return
        if not posts or new == 0 or emitted >= site or (total_pages and page >= total_pages):
            break
        if limit_pages is not None and page >= limit_pages:
            note(f"{emitted} emitted over {page} page(s), site states {site} — walk bounded by request (--pages {limit_pages}; --all walks to the count), not compared.")
            return
    if emitted == site:
        note(f"{emitted} emitted over {page} page(s), site states {site} (X-WP-Total) — equal.")
    else:
        note(f"{emitted} emitted over {page} page(s), site states {site} (X-WP-Total) — {abs(site - emitted)} {'short' if emitted < site else 'over'}.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an ad URL of this board (https://www.jobsgarden.hu/<slug>/).")
    slug = m.group(1)
    url = f"{API}?" + urllib.parse.urlencode({"slug": slug, "_fields": FIELDS + ",content"})
    code, body, _ = request(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    try:
        posts = json.loads(body)
    except ValueError:
        die(f"{url}: not JSON.", EXIT_PARTIAL)
    if not posts:
        die(f"{a.url}: the API knows no post with this slug — gone, or never a post.", EXIT_GONE)
    p = posts[0]
    if JOBS_CATEGORY not in (p.get("categories") or []):
        die(f"{a.url}: a post, not an ad (categories {p.get('categories')}).", EXIT_GONE)
    r = record(p)
    r["description"] = redact(clean((p.get("content") or {}).get("rendered") or "")) or None
    code, page, _ = request(a.url.strip())
    if code == 200:
        attr = ATTR_RE.search(page)
        if attr:
            parts = [x.strip() for x in clean(attr.group(1)).split("•")]
            r["header_line"] = " • ".join(parts)
            if len(parts) >= 2:
                r["location"] = parts[1] or None
            if len(parts) >= 3:
                r["sector"] = parts[2] or None
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="every ad of the jobs category through the REST API")
    g = l.add_mutually_exclusive_group()
    g.add_argument("--pages", type=int, default=None, help=f"pages of {PAGE_SIZE} to read (default {DEFAULT_PAGES}, bounded and said so)")
    g.add_argument("--all", action="store_true", help="walk to the count the API states, and compare")
    l.add_argument("--limit", type=int, default=0)
    l.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one ad by its public URL — the API's post, and the page's header line for the place")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
