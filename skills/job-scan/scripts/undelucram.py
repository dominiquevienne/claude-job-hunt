#!/usr/bin/env python3
"""Undelucram.ro — Romania's employer-review site with a job board attached, read through its paged listing; the listing's own «N rezultate» and its closed pager as two witnesses, never corrected by each other.

  undelucram.py list [--pages N] [--limit N] [--no-site-total]
  undelucram.py ad --url <advertisement URL>

THE LISTING IS PAGED AND STATES ITS COUNT — AND THE PAGER CLOSES

`/ro/locuri-de-munca` carries 10 `jobs-item` cards a page and `?page=2` …
`?page=146` on 2026-09-13; every page states «1.468 rezultate» (a Romanian
thousands dot) in its filter panel and «1-10 din 1468» in its pager line.
The adapter walks the pages at 1 s until one comes back without a card,
dedups on the id (the URL's tail), and prints two things it never merges:
«n emitted, site states N — equal / k short», and «the pager closes at page
P — P × 10 = M». *146 × 10 = 1 460 against 1 468 stated on the day: the
listing had a partial last page or moved during the walk; both numbers are
printed, neither corrects the other.* `--pages` bounds the walk and says so.

THE CARD carries the title (an `<h4>`), the date («12.09.2026»), the
employer (an `<h5>`, with the site's own rating and its review count), the
place («Hybrid (Pantelimon)», «Timișoara»), the work type («Full-time»).
THE ADVERTISEMENT PAGE carries a `JobPosting` in JSON-LD — `title`,
`description` (HTML), `datePosted`, `validThrough`, `employmentType`,
`hiringOrganization` (`name`, `sameAs` = the employer's review page),
`jobLocation` (a list, `addressLocality`, `addressCountry: RO`) — and
`identifier.value` is **the EMPLOYER's id** (278 for Henkel Romania, the
number of its review page), not the advertisement's, whose key is the URL's
tail; the two are kept apart. No salary field. No contacts read.

THE RULES: a short file (231 B) naming `ClaudeBot` to refuse it, `*` open —
`identity()` answers `claude-user`, `verdict()` sweeps since #230; no
`Crawl-delay` (1 s is ours); `certain: True`. Measured 2026-09-12 15:28 and
2026-09-13 15:54 UTC (#233, lot 7 → this adapter).
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
from _ldjson import absent_reason, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA
from _zero import empty_first_page

HOST = "www.undelucram.ro"
BASE = "https://" + HOST
LISTING = BASE + "/ro/locuri-de-munca"
AD_RE = re.compile(r"^https://www\.undelucram\.ro/ro/locuri-de-munca/[a-z0-9-]+/(\d+)/?$")
ITEM_RE = re.compile(r'<div class="jobs-item[^"]*"[^>]*>(.*?)(?=<div class="jobs-item|<div class="pagination|</main>|</body>)', re.S)
STATED_RE = re.compile(r"([\d]{1,3}(?:\.\d{3})*|\d+)\s+rezultate")
LAST_PAGE_RE = re.compile(r"[?&]page=(\d+)")
DMY_RE = re.compile(r"^(\d{2})\.(\d{2})\.(\d{4})$")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[undelucram] {msg}", file=sys.stderr)


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
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5", "Accept-Language": "ro,en;q=0.5"})
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
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", htmlmod.unescape(markup)).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def iso(dmy):
    m = DMY_RE.match((dmy or "").strip())
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else dmy


def card(fragment):
    m = re.search(r'href="(https://www\.undelucram\.ro/ro/locuri-de-munca/[a-z0-9-]+/(\d+))"', fragment)
    if not m:
        return None
    url, ident = m.group(1), m.group(2)
    title = re.search(r"<h4[^>]*>(.*?)</h4>", fragment, re.S)
    date = re.search(r'<p class="text-gray[^"]*">\s*(\d{2}\.\d{2}\.\d{4})\s*</p>', fragment)
    emp = re.search(r"<h5[^>]*>(.*?)</h5>", fragment, re.S)
    rating = re.search(r'fw-bolder fs-5">([\d,]+)</span>', fragment)
    reviews = re.search(r"(\d+)\s+evalu", fragment)
    # each label is an svg with an aria-label naming the field, then a <span> with the value — the aria-label picks, not the order
    labels = {k: text(v) for k, v in re.findall(r'<div class="other-info-label[^"]*">\s*<svg[^>]*aria-label="([^"]+)".*?</svg>\s*<span[^>]*>(.*?)</span>', fragment, re.S)}
    return {"source": "undelucram", "country": "RO", "ledger_id": f"undelucram:{ident}", "id": ident, "url": url,
            "title": text(title.group(1)) if title else None,
            "employer": text(emp.group(1)) if emp else None,
            "employer_rating": float(rating.group(1).replace(",", ".")) if rating else None,
            "employer_reviews": int(reviews.group(1)) if reviews else None,
            "place": labels.get("Location"), "work_type": labels.get("Job Type"),
            "posted": iso(date.group(1)) if date else None, "posted_as_published": date.group(1) if date else None}


def cmd_list(a):
    rows, seen, page, last, stated_n = [], set(), 1, None, None
    while True:
        url = LISTING if page == 1 else f"{LISTING}?page={page}"
        code, body = get(url)
        if code != 200:
            die(f"{url}: HTTP {code} — page {page} of {last or '?'}; the count below would be short and is not printed.", EXIT_PARTIAL)
        frags = ITEM_RE.findall(body)
        if page == 1 and not frags:
            die(empty_first_page("undelucram", body, '<div class="jobs-item">', where=url), EXIT_PARTIAL)
        if stated_n is None:
            m = STATED_RE.search(text(body))
            stated_n = int(m.group(1).replace(".", "")) if m else None
        last = max([int(x) for x in LAST_PAGE_RE.findall(body)] + [last or 1])
        new = 0
        for f in frags:
            c = card(f)
            if not c or c["id"] in seen:
                continue
            seen.add(c["id"])
            rows.append(c)
            new += 1
        if not frags or new == 0 or page >= last or (a.pages and page >= a.pages) or (a.limit and len(rows) >= a.limit):
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
    # two witnesses, printed apart and never merged: the stated figure, and the closed pager
    if bounded:
        note(f"site states {th(stated_n) if stated_n else 'no figure'}; the pager closes at page {last} — {th(len(rows))} emitted from a bounded walk, not compared.")
        return
    note(f"the pager closes at page {last} — {last} × 10 = {th(last * 10)}; {th(len(rows))} emitted over the walk.")
    if stated_n is None:
        note("the page states no «N rezultate» this run — no stated figure to print beside the count.")
    elif stated_n == len(rows):
        note(f"{th(len(rows))} emitted, site states {th(stated_n)} — equal.")
    else:
        note(f"{th(len(rows))} emitted, site states {th(stated_n)} — {th(abs(stated_n - len(rows)))} "
             + ("short" if stated_n > len(rows) else "more emitted than the site states")
             + "; the stated figure and the pager are two witnesses, and neither corrects the other.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/ro/locuri-de-munca/<slug>/<id>")
    ident = m.group(1)
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
    idv = d.get("identifier") or {}
    loc = d.get("jobLocation") or {}
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
    et = d.get("employmentType")
    print(json.dumps({
        "source": "undelucram",
        "country": ((addr.get("addressCountry") or "").strip() or "RO") if isinstance(addr, dict) else "RO",
        "ledger_id": f"undelucram:{ident}", "id": ident, "url": a.url,
        "title": text(d.get("title")),
        "employer": org.get("name") if isinstance(org, dict) else None,
        "employer_page": org.get("sameAs") if isinstance(org, dict) else None,
        # the site's `identifier.value` is the EMPLOYER's id (its review page's number), not the advertisement's — kept apart
        "employer_id": str(idv.get("value")) if isinstance(idv, dict) and idv.get("value") is not None else None,
        "employment_type": ", ".join(et) if isinstance(et, list) else et,
        "city": (text(addr.get("addressLocality")) or None) if isinstance(addr, dict) else None,
        "posted": d.get("datePosted"), "valid_through": d.get("validThrough"),
        "description": text(d.get("description"))[:20000], "language": "ro",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Undelucram.ro — the paged listing at 1 s, the stated «N rezultate» and the closed pager as two witnesses; JSON-LD on the advertisement.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every advertisement card — 10 a page, 146 pages on 2026-09-13, 1 s apart; --pages bounds the walk")
    s.add_argument("--pages", type=int)
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advertisement, from its JSON-LD")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
