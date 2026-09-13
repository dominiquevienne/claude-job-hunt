#!/usr/bin/env python3
"""The Ugandan Jobline (`theugandanjobline.com`) — a WordPress board whose listing counts its whole archive; the adapter walks the newest pages and reads the closing date on every card.

  ugandanjobline.py list [--pages N] [--limit N] [--no-site-total]
  ugandanjobline.py ad --url <post URL>

THE STATED COUNT IS THE ARCHIVE, AND THE CARD SAYS WHEN IT CLOSES

`/jobs-in-uganda` states «84,248 jobs» and pages to `/page/8425` (10 a
page) on 2026-09-13 — every post since the site began; 85 `post-sitemap`
files of a thousand say the same. **That figure is not the live board.** The
listing is newest first, and every card carries «Posted N days ago» and
«Closes DD Mon»; the adapter walks the first pages (`--pages`, default 20 =
200 posts), emits `closes` on each row, and prints how many of the rows
read still close in the future — the live window of the pages read — beside
the stated archive figure, which it never compares to its count. A full
walk is not offered: 8 425 pages at 1 s is the archive, not the board.

THE POST PAGE carries a `JobPosting` in a JSON-LD `@graph` — `title`,
`description` (HTML), `datePosted` and `validThrough` (with a time, no
zone), `employmentType`, `hiringOrganization` (`name`, `sameAs`),
`jobLocation.address` (`addressLocality`, `addressRegion`, `addressCountry`
as the name «Uganda»), `industry`, `workHours`, `monthsOfExperience`,
`baseSalary` (`currency: UGX`, and an EMPTY `value` on the page read),
`identifier.value` (empty). The country is emitted as `UG` when the name is
Uganda, any other name as published. The page's `mailto:` links are the
site's share buttons; nothing of a recruiter's contacts is read.

THE RULES: Cloudflare's managed block (`ClaudeBot` named and refused, `*`
open — `identity()` answers `claude-user`, `verdict()` sweeps) plus the
operator's: `/wp-admin/`, `/wp-login.php`, `/xmlrpc.php`, `/api`,
`/oauth-check`, `/link`, `/boost/job`, `/*?s=`, `/*&s=` refused to `*`; no
`Crawl-delay` (1 s between pages is ours). #233 recorded on 2026-09-11 a
hand-written motive («crawl cost»); the file read on 2026-09-13 carries no
motive and names `ClaudeBot` only through the managed block. Measured
2026-09-13 10:22–10:59 UTC (#233, lot 8 → this adapter).
"""

import argparse
import html as htmlmod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

from _decode import decode_body
from _ldjson import absent_reason, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA
from _zero import empty_first_page

HOST = "theugandanjobline.com"
BASE = "https://" + HOST
LISTING = BASE + "/jobs-in-uganda"
AD_RE = re.compile(r"^https://theugandanjobline\.com/(\d{4})/(\d{2})/([a-z0-9-]+)\.html$")
CARD_RE = re.compile(r'<article class="jc[^"]*">(.*?)</article>', re.S)
STATED_RE = re.compile(r'<div class="count[^"]*">\s*([\d,]+)\s*jobs\s*</div>')
LAST_PAGE_RE = re.compile(r"/jobs-in-uganda/page/(\d+)")
MONTHS = {m: i for i, m in enumerate(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), 1)}
COUNTRY = {"uganda": "UG"}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[ugandanjobline] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
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
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5", "Accept-Language": "en"})
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
    return re.sub(r"[ \t]+", " ", htmlmod.unescape(markup)).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def closes_on(fragment, today):
    """«Closes 21 Sep» → an ISO date in the current or the next year — the
    card names no year, so the nearest future reading is taken; None when
    the card carries no closing date."""
    m = re.search(r"Closes\s+(\d{1,2})\s+([A-Z][a-z]{2})", fragment)
    if not m:
        return None
    d, mon = int(m.group(1)), MONTHS.get(m.group(2))
    if not mon:
        return None
    try:
        when = date(today.year, mon, d)
    except ValueError:
        return None
    if (today - when).days > 60:          # more than two months past: the card means next year
        when = date(today.year + 1, mon, d)
    return when.isoformat()


def card(fragment, today):
    m = re.search(r'<div class="title"><a href="(https://theugandanjobline\.com/\d{4}/\d{2}/[a-z0-9-]+\.html)">(.*?)</a>', fragment, re.S)
    if not m:
        return None
    url = m.group(1)
    slug = AD_RE.match(url)
    co = re.search(r'<a class="co-link" href="[^"]*">(.*?)</a>', fragment, re.S)
    posted = re.search(r"Posted\s*<b>(.*?)</b>", fragment, re.S)
    pills = re.findall(r'<span class="pill">(.*?)</span>', fragment, re.S)
    return {"source": "ugandanjobline", "country": "UG",
            "ledger_id": f"ugandanjobline:{slug.group(1)}/{slug.group(2)}/{slug.group(3)}" if slug else None,
            "id": f"{slug.group(1)}/{slug.group(2)}/{slug.group(3)}" if slug else None, "url": url,
            "title": text(m.group(2)), "employer": text(co.group(1)) if co else None,
            "posted_ago": text(posted.group(1)) if posted else None,
            "closes": closes_on(fragment, today),
            "categories": [text(p) for p in pills]}


def cmd_list(a):
    today = date.today()
    rows, seen, page, last, stated_n = [], set(), 1, None, None
    while True:
        url = LISTING if page == 1 else f"{LISTING}/page/{page}"
        code, body = get(url)
        if code != 200:
            die(f"{url}: HTTP {code} — page {page}; the rows below would be short and are not printed.", EXIT_PARTIAL)
        frags = CARD_RE.findall(body)
        if page == 1 and not frags:
            die(empty_first_page("ugandanjobline", body, '<article class="jc">', where=url), EXIT_PARTIAL)
        if stated_n is None:
            m = STATED_RE.search(body)
            stated_n = int(m.group(1).replace(",", "")) if m else None
        last = max([int(x) for x in LAST_PAGE_RE.findall(body)] + [last or 1])
        for f in frags:
            c = card(f, today)
            if not c or not c["id"] or c["id"] in seen:
                continue
            seen.add(c["id"])
            rows.append(c)
        if not frags or page >= last or page >= a.pages or (a.limit and len(rows) >= a.limit):
            break
        page += 1
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    live = sum(1 for r in rows if r["closes"] and r["closes"] >= today.isoformat())
    dated = sum(1 for r in rows if r["closes"])
    note(f"{page} page(s) read of {last}; **{th(len(rows))} distinct post(s)**"
         + (f" ({a.limit} printed under --limit)" if a.limit and len(rows) > a.limit else "")
         + f"; {th(dated)} carry a closing date and **{th(live)} still close on or after {today.isoformat()}** — the live window of the pages read.")
    if a.no_site_total:
        return
    if stated_n is None:
        note("the page states no «N jobs» this run — no archive figure.")
    else:
        note(f"site states {th(stated_n)} jobs — the archive since the site began ({th(last)} pages of 10), not the live board; "
             f"never compared to the {th(len(rows))} read here.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not a post address — expected {BASE}/<yyyy>/<mm>/<slug>.html")
    ident = f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    found = postings(body)
    if not found:
        why = absent_reason(body)
        if getattr(why, "our_fault", False):
            die(f"{a.url}: {why} **The page announces a JobPosting and this read none.**")
        die(f"{a.url}: {why}", EXIT_PARTIAL)
    d = found[0]
    org = d.get("hiringOrganization") or {}
    loc = d.get("jobLocation") or {}
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
    sal = d.get("baseSalary") or {}
    val = sal.get("value") if isinstance(sal, dict) else None
    if not isinstance(val, dict):
        val = sal if isinstance(sal, dict) else {}
    exp = d.get("experienceRequirements") or {}
    cname = (text(addr.get("addressCountry")) if isinstance(addr, dict) else "") or ""

    def money(v):
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return None
    print(json.dumps({
        "source": "ugandanjobline",
        "country": COUNTRY.get(cname.lower(), cname or None),   # «Uganda» → UG; any other name as published
        "ledger_id": f"ugandanjobline:{ident}", "id": ident, "url": a.url,
        "title": text(d.get("title")),
        "employer": org.get("name") if isinstance(org, dict) else None,
        "employer_site": org.get("sameAs") if isinstance(org, dict) else None,
        "employment_type": d.get("employmentType"),
        "industry": d.get("industry") or None,
        "city": (text(addr.get("addressLocality")) or None) if isinstance(addr, dict) else None,
        "region": (text(addr.get("addressRegion")) or None) if isinstance(addr, dict) else None,
        "posted": d.get("datePosted"), "valid_through": d.get("validThrough"),
        "work_hours": d.get("workHours") or None,
        "months_of_experience": money(exp.get("monthsOfExperience")) if isinstance(exp, dict) else None,
        "salary_currency": sal.get("currency") if isinstance(sal, dict) else None,
        "salary": money(val.get("value")), "salary_unit": (val.get("unitText") or "").strip() or None,
        "description": text(d.get("description"))[:20000], "language": "en",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="The Ugandan Jobline — the newest pages of an archive-sized listing, the closing date on every card; the stated 84 248 is the archive and is never compared.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="the newest posts — --pages N of 10 (default 20), 1 s between pages")
    s.add_argument("--pages", type=int, default=20)
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one post, from its JobPosting JSON-LD")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
