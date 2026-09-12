#!/usr/bin/env python3
"""CVbankas (`www.cvbankas.lt`) — Lithuania's board, read through its paged front page; the sitemap is never asked for.

  cvbankas.py list [--pages N] [--limit N] [--no-site-total]
  cvbankas.py ad --url <advertisement URL>

THE FRONT PAGE IS THE LISTING, AND THE PAGES SUM TO THE STATED COUNT

`/` is page 1 — the VIP advertisements, 142 of them on 2026-09-12 — and
`/?page=2` … `/?page=181` follow at 50 a page (21 on the last): 142 + 179 ×
50 + 21 = **9 113, exactly the «Rodoma 9 113 skelbimų» every page states.**
The adapter reads that figure on each page and prints «n emitted, site
states N — equal / k short» at the end; `--pages` bounds the walk and says
so («the walk stopped at page p»), and the figure is then a bound, not a
check. Every card carries the id (`job_ad_<id>`, also the tail of the URL
`/<slug>/<n>-<id>`), title, employer, salary (amount, period, net «į
rankas» or gross), city and an age («prieš 1 d.»). No `Crawl-delay` in the
rules; 1 s between pages is ours, 181 requests for the whole board.

**`/sitemap.xml` IS NEVER ASKED FOR**: it answers a Cloudflare challenge
(403 «Attention Required!», moving md5, twice on 2026-09-12 12:25 UTC) where
the listing answers 200 to the same client — a WAF rule on one path, and a
path that answers a challenge is not the route (borne 2).

THE ADVERTISEMENT PAGE carries **microdata, not JSON-LD**: `itemtype
JobPosting` with `title`, `datePosted` (a `content=` date), `validThrough`
(a `datetime=`), `hiringOrganization/name`, `jobLocation/addressLocality`
(«Užsienis : Danija» for abroad, the city otherwise), `description`, and
sections «Darbo pobūdis», «Reikalavimai darbuotojui», «Ką siūlome»,
«Atlyginimas». **The salary digits on the page are interleaved with U+200C
(zero-width non-joiner) — `2‌2‌0‌0‌-3‌0‌0‌0‌` — an anti-scraping
obfuscation the listing does not apply; the adapter strips it and says so.**
Nothing of a recruiter's contacts is read: the only `mailto:` on the page
is the board's own, and the adapter emits none.

THE RULES: Cloudflare's managed block (`ClaudeBot` named and refused, `*`
open) plus the operator's — ten account and social paths refused to `*`,
and `anthropic-ai` and `Claude-Web` refused everything: **two names no
request from here carries** (#233, the fourth form). `identity()` answers
`claude-user`, `verdict()` sweeps; `certain: True`. Measured 2026-09-12
12:22–12:32 UTC (#233, lot 6 → this adapter).
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
from _zero import empty_first_page

HOST = "www.cvbankas.lt"
BASE = "https://" + HOST
NEVER = ("/sitemap.xml",)                 # answers a challenge; not the route, under any token
AD_RE = re.compile(r"^https://www\.cvbankas\.lt/[a-z0-9-]+/\d+-(\d+)/?$")
ARTICLE_RE = re.compile(r'<article class="list_article[^"]*" id="job_ad_(\d+)">(.*?)</article>', re.S)
STATED_RE = re.compile(r"Rodoma\s*([\d\s ]+?)\s*skelbim")
LAST_PAGE_RE = re.compile(r"\?page=(\d+)")
ZWNJ = "‌"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[cvbankas] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    path = full_path(parts)
    if parts.netloc == HOST and path.split("?")[0] in NEVER:
        die(f"{url}: this adapter does not read {path} — it answers a challenge, and a path that does is not the route", EXIT_REFUSED)
    a = robots_allowed(parts.netloc, path)
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=1.0)   # no Crawl-delay declared; 1 s between pages is ours


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5", "Accept-Language": "lt,en;q=0.5"})
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


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"[ \t]+", " ", htmlmod.unescape(markup).replace(ZWNJ, "")).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def stated(page):
    m = STATED_RE.search(text(page))
    return int(re.sub(r"\D", "", m.group(1))) if m else None


def salary(fragment):
    """«2200-3000», «nuo 1500», «1200» + a period and net/gross — from a
    listing card or the page's salary component. Returns a dict of what was
    there, `None` for what was not."""
    t = text(fragment)
    nums = [int(x.replace(" ", "")) for x in re.findall(r"\d[\d ]*\d|\d", t)]
    # a page is Lithuanian or English per advertisement («€/mėn. į rankas» / «€/mon. net»);
    # the class on the block — salary_bl_net / salary_bl_gross — says net or gross in either
    period = "MONTH" if re.search(r"mėn|mon", t) else ("HOUR" if re.search(r"\bval|/h\b|hour", t) else None)
    net = True if "salary_bl_net" in (fragment or "") else (False if "salary_bl_gross" in (fragment or "") else None)
    lo, hi = (nums[0], nums[1]) if len(nums) >= 2 else ((nums[0], None) if nums else (None, None))
    return {"salary_min": lo, "salary_max": hi, "salary_period": period, "salary_net": net, "salary_currency": "EUR" if nums else None}


def card(ident, body):
    m = re.search(r'href="(https://www\.cvbankas\.lt/[a-z0-9-]+/\d+-' + ident + r')"', body)
    title = re.search(r'<h3 class="list_h3"[^>]*>(.*?)</h3>', body, re.S)
    emp = re.search(r'<span class="heading_secondary">\s*<span[^>]*>(.*?)</span>', body, re.S)
    sal = re.search(r'<span class="salary_c">(.*?)</span>\s*</div>', body, re.S)
    city = re.search(r'<span class="list_city">(.*?)</span>', body, re.S)
    age = re.search(r'<span class="txt_list_2">(.*?)</span>', body, re.S)
    r = {"source": "cvbankas", "country": "LT", "ledger_id": f"cvbankas:{ident}", "id": ident,
         "url": m.group(1) if m else None,
         "title": text(title.group(1)) if title else None,
         "employer": text(emp.group(1)) if emp else None,
         "city": text(city.group(1)) if city else None,
         "vip": "jobadlist_article_vip_icon" in body,   # the VIP badge inside the card; page 1 is all VIP
         "age": text(age.group(1)) if age else None}
    r.update(salary(sal.group(1)) if sal else salary(""))
    return r


def cmd_list(a):
    rows, seen, page, last, stated_n = [], set(), 1, None, None
    while True:
        url = BASE + "/" if page == 1 else f"{BASE}/?page={page}"
        code, body = get(url)
        if code != 200:
            die(f"{url}: HTTP {code} — page {page} of {last or '?'}; the count below would be short and is not printed.", EXIT_PARTIAL)
        arts = ARTICLE_RE.findall(body)
        if page == 1 and not arts:
            die(empty_first_page("cvbankas", body, "<article class=\"list_article\">", where=url), EXIT_PARTIAL)
        if stated_n is None:
            stated_n = stated(body)
        pages = [int(x) for x in LAST_PAGE_RE.findall(body)]
        last = max(pages + [last or 1])
        for ident, frag in arts:
            if ident in seen:
                continue
            seen.add(ident)
            rows.append(card(ident, frag))
        if not arts or page >= last or (a.pages and page >= a.pages) or (a.limit and len(rows) >= a.limit):
            break
        page += 1
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    bounded = (a.pages and page < last) or (a.limit and len(rows) >= a.limit and page < last)
    note(f"{page} page(s) read of {last}; **{th(len(rows))} distinct advertisement id(s)**"
         + (f" ({a.limit} printed under --limit)" if a.limit and len(rows) > a.limit else "")
         + (f" — the walk stopped at page {page}, so the count is a lower bound" if bounded else "") + ".")
    if a.no_site_total:
        return
    if stated_n is None:
        note("the page states no «Rodoma N skelbimų» this run — no second source.")
    elif bounded:
        note(f"site states {th(stated_n)}; {th(len(rows))} emitted from a bounded walk — not compared.")
    elif stated_n == len(rows):
        note(f"{th(len(rows))} emitted, site states {th(stated_n)} — equal.")
    else:
        note(f"{th(len(rows))} emitted, site states {th(stated_n)} — {th(abs(stated_n - len(rows)))} "
             + ("short" if stated_n > len(rows) else "more emitted than the site states") + ".")


def prop(body, name, attr=None):
    m = re.search(r'itemprop="' + name + r'"([^>]*)>', body)
    if not m:
        return None
    if attr:
        v = re.search(attr + r'="([^"]*)"', m.group(1))
        return htmlmod.unescape(v.group(1)) if v else None
    return text(body[m.end():m.end() + 600].split("</", 1)[0])


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/<slug>/<n>-<id>")
    ident = m.group(1)
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    if 'itemtype="http://schema.org/JobPosting"' not in body:
        die(f"{a.url}: no JobPosting microdata on the page — the markup changed, or this is not an advertisement.", EXIT_PARTIAL)
    h1 = re.search(r'<h1[^>]*itemprop="title"[^>]*>(.*?)</h1>', body, re.S)
    org = re.search(r'itemprop="hiringOrganization".*?itemprop="name" content="([^"]*)"', body, re.S)
    # the whole PostalAddress span: «Užsienis : Danija» for abroad (the country is a second link), the city otherwise
    loc = re.search(r'itemprop="jobLocation".*?<span itemprop="address"[^>]*>(.*?)</span>\s*-', body, re.S)
    desc = re.search(r'itemprop="description"[^>]*>(.*?)</section>', body, re.S)
    sal = re.search(r'<div class="salary_component">(.*?)</div>\s*</span>\s*</span>\s*</div>', body, re.S)
    wt = re.search(r'<div class="job_ad_work_types">(.*?)</div>\s*</span>\s*</span>\s*</div>', body, re.S)
    sections = {}
    for sec in re.findall(r"<section[^>]*>(.*?)</section>", body, re.S):
        h = re.search(r"<h[23][^>]*>(.*?)</h[23]>", sec, re.S)
        t = re.search(r'class="jobad_txt"[^>]*>(.*?)$', sec, re.S)
        if h and t:
            sections[text(h.group(1))] = text(t.group(1))[:20000]
    r = {"source": "cvbankas", "country": "LT", "ledger_id": f"cvbankas:{ident}", "id": ident, "url": a.url,
         "title": text(h1.group(1)) if h1 else None,
         "employer": htmlmod.unescape(org.group(1)) if org else None,
         "location": text(loc.group(1)) if loc else None,      # «Užsienis : Danija» for abroad, the city otherwise
         "posted": prop(body, "datePosted", "content"),
         "valid_through": (prop(body, "validThrough", "datetime") or "")[:10] or None,
         "work_type": text(wt.group(1)) if wt else None,
         "description": text(desc.group(1))[:20000] if desc else None,
         "sections": sections}
    r.update(salary(sal.group(1)) if sal else salary(""))
    print(json.dumps(r, ensure_ascii=False))
    if sal and (ZWNJ in sal.group(1) or "&#8204;" in sal.group(1)):
        note("the salary digits on the page are interleaved with U+200C; stripped before parsing — the listing shows the same figure plain.")


def main():
    p = argparse.ArgumentParser(description="CVbankas — Lithuania's board through its paged front page; the stated «Rodoma N skelbimų» as the check; /sitemap.xml never read.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every advertisement card — 181 pages at 1 s on 2026-09-12; --pages bounds the walk")
    s.add_argument("--pages", type=int)
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advertisement, from the page's JobPosting microdata — no contacts")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
