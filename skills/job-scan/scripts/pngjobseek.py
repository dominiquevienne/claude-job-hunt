#!/usr/bin/env python3
"""PNG JobSeek (`www.pngjobseek.com`) — Papua New Guinea's board, read from its server-rendered listing pages; the page's own «N jobs found» as the check.

  pngjobseek.py list [--limit N] [--no-site-total]
  pngjobseek.py ad --url <advertisement URL>

THE LISTING IS SERVER-RENDERED, PAGED, AND STATES ITS COUNT

`/jobs` is a React Router app rendered on the server (Mantine cards): 25
cards a page, `?page=2` the next, and a header «31 jobs found — Showing 1 –
25 of 31» on 2026-09-13. **There is no JSON-LD on any page** — the card is
read from its rendered text: title (the `<h4>` of the `/jobs/<id>` link),
employer (the logo's `alt`), «City, Province», the work type, a date, a
snippet, a category. The adapter walks the pages until one comes back
without a card, dedups on the id, and prints «n emitted, site states N —
equal / k short». The advertisement page repeats the head fields (title,
employer, city, category, salary or «Not Disclosed», date) and carries a
«Job Description» and a «Requirements» block in text; `ad` reads those.
No contacts of a recruiter are read. 2 s between requests, no `Crawl-delay`.

THE RULES: Cloudflare's managed block (`ClaudeBot` named and refused, `*`
open — `identity()` answers `claude-user`, `verdict()` sweeps since #230)
plus the operator's lines (3 695 B); `certain: True`. Measured 2026-09-12
15:28 and 2026-09-13 11:35 UTC (#233, lot 7 → this adapter).
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

HOST = "www.pngjobseek.com"
BASE = "https://" + HOST
LISTING = BASE + "/jobs"
AD_RE = re.compile(r"^https://www\.pngjobseek\.com/jobs/(\d+)/?(?:\?.*)?$")
CARD_SPLIT = re.compile(r'(?=<div[^>]*class="_card_)')
CARD_TAG = re.compile(r'<div[^>]*class="_card_')
STATED_RE = re.compile(r"([\d,]+)\s+jobs? found")
DATE_RE = re.compile(r"^\d{1,2} [A-Z][a-z]+ \d{4}$")
MONTHS = {m: i for i, m in enumerate(("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"), 1)}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[pngjobseek] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # no Crawl-delay declared; 2 s is ours


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


def cells(markup):
    """The rendered text of a fragment as a list of non-empty cells, styles
    dropped — the shape the server renders the cards and the head in."""
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    parts = re.split(r"<[^>]+>", markup)
    return [htmlmod.unescape(re.sub(r"\s+", " ", p)).strip() for p in parts if p and p.strip()]


def iso(d):
    """«11 September 2026» → «2026-09-11»; anything else comes back unchanged."""
    m = re.match(r"^(\d{1,2}) ([A-Z][a-z]+) (\d{4})$", d or "")
    if not m or m.group(2) not in MONTHS:
        return d
    return f"{m.group(3)}-{MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}"


def th(n):
    return f"{n:,}".replace(",", " ")


def card(fragment):
    m = re.search(r'href="/jobs/(\d+)"', fragment)
    if not m:
        return None
    ident = m.group(1)
    c = cells(fragment)
    title = re.search(r"<h4[^>]*>(.*?)</h4>", fragment, re.S)
    alt = re.search(r'alt="([^"]*)"', fragment)
    employer = htmlmod.unescape(alt.group(1)) if alt else None
    # after the employer: «City, Province» · work type · date · snippet · category — by position, dated cells recognised by shape
    after = c[c.index(employer) + 1:] if employer in c else c
    date = next((x for x in after if DATE_RE.match(x)), None)
    k = after.index(date) if date in after else -1
    place = after[k - 2] if k >= 2 else None
    wtype = after[k - 1] if k >= 1 else None
    snippet = after[k + 1] if 0 <= k < len(after) - 1 else None
    category = after[k + 2] if 0 <= k < len(after) - 2 else None
    return {"source": "pngjobseek", "country": "PG", "ledger_id": f"pngjobseek:{ident}", "id": ident,
            "url": f"{BASE}/jobs/{ident}",
            "title": htmlmod.unescape(re.sub(r"<[^>]+>", "", title.group(1))).strip() if title else None,
            "employer": employer, "place": place, "work_type": wtype,
            "posted": iso(date), "posted_as_published": date,
            "category": category, "snippet": (snippet or "")[:600] or None}


def cmd_list(a):
    rows, seen, page, stated_n = [], set(), 1, None
    while True:
        url = LISTING if page == 1 else f"{LISTING}?page={page}"
        code, body = get(url)
        if code != 200:
            die(f"{url}: HTTP {code} — page {page}; the count below would be short and is not printed.", EXIT_PARTIAL)
        # the card's opening tag carries a long style attribute before its class — test the TAG, not a byte window
        frags = [f for f in CARD_SPLIT.split(body) if CARD_TAG.match(f)]
        if page == 1 and not frags:
            die(empty_first_page("pngjobseek", body, '<div class="_card_">', where=url), EXIT_PARTIAL)
        if stated_n is None:
            m = STATED_RE.search(" ".join(cells(body)))
            stated_n = int(m.group(1).replace(",", "")) if m else None
        new = 0
        for f in frags:
            c = card(f)
            if not c or c["id"] in seen:
                continue
            seen.add(c["id"])
            rows.append(c)
            new += 1
        if not frags or new == 0 or (a.limit and len(rows) >= a.limit):
            break
        page += 1
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{page} page(s) read; **{th(len(rows))} distinct advertisement id(s)**"
         + (f" ({a.limit} printed under --limit, the walk stopped there)" if a.limit and len(rows) >= a.limit else "") + ".")
    if a.no_site_total or a.limit:
        return
    if stated_n is None:
        note("the page states no «N jobs found» this run — no second source.")
    elif stated_n == len(rows):
        note(f"{th(len(rows))} emitted, site states {th(stated_n)} — equal.")
    else:
        note(f"{th(len(rows))} emitted, site states {th(stated_n)} — {th(abs(stated_n - len(rows)))} "
             + ("short" if stated_n > len(rows) else "more emitted than the site states") + ".")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/jobs/<id>")
    ident = m.group(1)
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    c = cells(body)
    if "Back to Jobs" not in c:
        die(f"{a.url}: no «Back to Jobs» head on the page — the markup changed, or this is not an advertisement.", EXIT_PARTIAL)
    head = c[c.index("Back to Jobs") + 1:]
    # title · employer · city · category · salary («Not Disclosed» or a figure) · date · «Job Description» · text … «Requirements» · text
    try:
        jd = head.index("Job Description")
    except ValueError:
        jd = None
    fields = head[:jd] if jd is not None else head[:6]
    date = next((x for x in fields if DATE_RE.match(x)), None)
    title, employer, city, category, salary = (fields + [None] * 5)[:5]
    body_cells = head[jd + 1:] if jd is not None else []
    req = body_cells.index("Requirements") if "Requirements" in body_cells else None
    stop = next((i for i, x in enumerate(body_cells) if x in ("Apply Now", "Apply", "Share", "Save", "Similar Jobs", "Related Jobs")), len(body_cells))
    description = "\n".join(body_cells[:req if req is not None else stop])
    requirements = "\n".join(body_cells[req + 1:stop]) if req is not None else None
    print(json.dumps({
        "source": "pngjobseek", "country": "PG", "ledger_id": f"pngjobseek:{ident}", "id": ident, "url": a.url,
        "title": title, "employer": employer, "city": city, "category": category,
        "salary_as_published": salary,                      # «Not Disclosed» on the page read; a figure when the employer gives one
        "posted": iso(date), "posted_as_published": date,
        "description": description[:20000] or None, "requirements": (requirements or "")[:8000] or None, "language": "en",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="PNG JobSeek — the paged server-rendered listing, the page's «N jobs found» as the check; no JSON-LD anywhere.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every advertisement card — 25 a page, 2 s apart")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advertisement, from the page's rendered head and description")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
