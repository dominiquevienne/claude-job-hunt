#!/usr/bin/env python3
"""Dept of Labour Online Skills Bank (`jobseekers.bahamas.gov.bs`) — the Bahamas' public employment service, through the PCRecruiter job board its own page posts; «1-24 of N» printed beside every walk; the employer is not on the board and stays that way. Issue #447.

  jobseekers_bs.py search [--island "New Providence"] [--keyword Q] [--pages N] [--limit N]
  jobseekers_bs.py ad --url <https://jobseekers.bahamas.gov.bs/pcrbin/jobboard.aspx?action=detail&recordid=<digits>&pcr-id=...>

THE ROUTE IS THE FORM — `/pcrbin/jobboard.aspx`, a PCRecruiter board (Main Sequence
Technologies) behind the Department of Labour's site:

  GET  /pcrbin/jobboard.aspx?uid=labour%20database.txt          -> «1-24 of 221», 24 rows, the pager form `googlePage`
  POST /pcrbin/jobboard.aspx  action= · showjobs=Y · pcr-id · morecount=<offset>$$<page-1> · sortorder · unifiedsearch
                                                                  -> the page asked («25-48 of 221» checked after every turn)
  POST /pcrbin/jobboard.aspx  action=search · Keyword · Island/State · pcr-id · locale   -> a filtered first page
  GET  /pcrbin/jobboard.aspx?action=detail&recordid=<id>&pcr-id=<token>                  -> one posting

`pcr-id` is a token the list page hands out; the detail page served WITHOUT it is a
4 302-byte shell with no posting in it, so the adapter reads the token off the list
and the `ad` command wants the address as the list wrote it. `goToPage(p)` on the page
sets `morecount` to `(p-1)*24 + "$$" + (p-1)` and submits `googlePage` — this adapter
does exactly that, and reads the «a-b of N» heading back to check the page turned.

Measured 2026-09-13 23:1x UTC by the declared client: «1-24 of 221» stated, 24 rows a
page, 25 `<tr>` on the page (one header row); page 2 answers «25-48 of 221». The rules:
`/robots.txt` is 404 — an absence, certain, open; no Crawl-delay — 3 s is ours.
**`--pages` defaults to 10** (240 rows) and the note says when the walk was bounded by
request; 221 is under that, so the default walks the whole board.

THE ROW: position (the link text), island (Abaco · Berry Islands · Eleuthera · Exuma ·
Grand Bahama · New Providence), type («Full-Time Regular» …), date posted (M/D/YYYY),
the record id and the detail address. THE DETAIL PAGE: the title, a location line
(«Location: National Airport, New Providence, Bahamas»), the description, and a
«Job Brief» block — Location · Job Type · Salary («$0.00 — $0.00» when the employer
stated none: emitted as null, never as zero) · Industry · Benefits · Vacation · Degree ·
Years Experience · «Posted N Hours ago». **The employer's name is on neither page — the
Department mediates, and the board shows the posting without the employer**; `employer`
is null and `employer_hidden` says why. No contact is on either page; the «APPLY» goes
to the Department's own form, which this adapter never touches.
"""

import argparse
import html as htmlmod
import http.cookiejar
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

HOST = "jobseekers.bahamas.gov.bs"
BASE = f"https://{HOST}"
BOARD = f"{BASE}/pcrbin/jobboard.aspx"
LIST_URL = f"{BOARD}?uid=labour%20database.txt"
PAGE_SIZE = 24
COUNT_RE = re.compile(r'id="resultcount"[^>]*>\s*(\d+)\s*-\s*(\d+)\s+of\s+(\d+)\s*<')
ROW_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
DETAIL_RE = re.compile(r"^https?://jobseekers\.bahamas\.gov\.bs/pcrbin/jobboard\.aspx\?action=detail&recordid=(\d+)&pcr-id=([^&\s]+)$")
NO_EMPLOYER = "the board shows the posting without the employer — the Department of Labour mediates; no name on the list or the detail page"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobseekers_bs] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=3.0)   # /robots.txt is 404 — no Crawl-delay to honour; 3 s is ours
_JAR = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_JAR))


def request(url, data=None):
    """One request in the session — GET, or POST of an ordered field list."""
    gate(url)
    _PACE.wait()
    headers = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en"}
    body = None
    if data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(wire_url(url), data=body, headers=headers)
    try:
        with _OPENER.open(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</td>|</th>|</tr>|</li>|</h\d>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def form_fields(body, form_id):
    """The hidden fields of one form on the page, in document order — the pager form
    `googlePage` carries the token, the search key and the sort; nothing else is posted."""
    m = re.search(r'<form[^>]*id="%s"[^>]*>(.*?)</form>' % re.escape(form_id), body or "", re.S)
    if not m:
        return None
    out = []
    for i in re.finditer(r"<input([^>]*)>", m.group(1)):
        a = i.group(1)
        n = re.search(r'name="([^"]+)"', a)
        if not n:
            continue
        v = re.search(r'value="([^"]*)"', a)
        out.append((n.group(1), htmlmod.unescape(v.group(1)) if v else ""))
    return out


def stated(body):
    """(first, last, total) from the page's own «a-b of N» heading, or None when it is not there."""
    m = COUNT_RE.search(body or "")
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def rows(body):
    """One row per table line that carries a detail link — position, island, type, date."""
    out = []
    for m in ROW_RE.finditer(body or ""):
        r = m.group(1)
        link = re.search(r'href="(/pcrbin/jobboard\.aspx\?action=detail&(?:amp;)?recordid=(\d+)&(?:amp;)?pcr-id=[^"]+)"', r)
        if not link:
            continue
        cells = [text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        if len(cells) < 4:
            continue
        ident = link.group(2)
        out.append({
            "source": "jobseekers_bs", "country": "BS", "ledger_id": f"jobseekers_bs:{ident}", "id": ident,
            "url": BASE + htmlmod.unescape(link.group(1)),
            "title": cells[0] or None,
            "employer": None, "employer_hidden": NO_EMPLOYER,
            "island": cells[1] or None,
            "job_type": cells[2] or None,
            "posted": cells[3] or None,                 # M/D/YYYY as the board prints it
            "language": "en",
        })
    return out


def turn(body, pageno):
    """Page `pageno` of the results, by the pager form the page itself submits."""
    fields = form_fields(body, "googlePage")
    if not fields:
        die(f"{BOARD}: the page carries no `googlePage` form — not the results page ({len(body or '')} characters).", EXIT_PARTIAL)
    fields = [(k, ("%d$$%d" % ((pageno - 1) * PAGE_SIZE, pageno - 1)) if k == "morecount" else v) for k, v in fields]
    code, out = request(BOARD, fields)
    if code != 200:
        die(f"{BOARD} (page {pageno}): HTTP {code}", EXIT_PARTIAL)
    s = stated(out)
    if s is None:
        die(f"{BOARD} (page {pageno}): the answer carries no «a-b of N» heading ({len(out)} characters) — not the results page.", EXIT_PARTIAL)
    if s[0] != (pageno - 1) * PAGE_SIZE + 1:
        die(f"{BOARD}: asked for page {pageno} (rows from {(pageno - 1) * PAGE_SIZE + 1}), the heading says «{s[0]}-{s[1]} of {s[2]}» — the page did not turn.", EXIT_PARTIAL)
    return out


def first_page(a):
    """The unfiltered list by GET, or the search form posted when an island or a keyword is asked."""
    code, page = request(LIST_URL)
    if code != 200:
        die(f"{LIST_URL}: HTTP {code}", EXIT_PARTIAL)
    if not (a.island or a.keyword):
        return page
    fields = form_fields(page, "searchForm")
    if fields is None:
        die(f"{LIST_URL}: no `searchForm` on the page ({len(page)} characters).", EXIT_PARTIAL)
    fields = [(k, v) for k, v in fields if k not in ("Keyword", "Island/State")]
    fields = [("Keyword", a.keyword or ""), ("Island/State", a.island or "")] + fields
    code, out = request(BOARD, fields)
    if code != 200:
        die(f"{BOARD} (search): HTTP {code}", EXIT_PARTIAL)
    return out


def cmd_search(a):
    body = first_page(a)
    s = stated(body)
    where = " · ".join(x for x in (f"island {a.island}" if a.island else "", f"keyword {a.keyword!r}" if a.keyword else "") if x) or "the whole board"
    if s is None:
        if not rows(body):
            note(f"no «a-b of N» heading and no row ({where}) — the site says nothing matched.")
            return
        die(f"{BOARD}: rows on the page and no «a-b of N» heading — the count line changed; a walk without it is not compared.", EXIT_PARTIAL)
    total = s[2]
    out, seen, pageno = [], set(), 1
    while True:
        new = 0
        for r in rows(body):
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            out.append(r)
            new += 1
        if new == 0 or len(out) >= total:
            break
        if a.pages and pageno >= a.pages:
            break
        if a.limit and len(out) >= a.limit:
            break
        pageno += 1
        body = turn(body, pageno)
    emitted = out[:a.limit] if a.limit else out
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    bounded = (a.pages and pageno >= a.pages and total > pageno * PAGE_SIZE) or (a.limit and a.limit < total)
    if bounded:
        note(f"{th(n)} emitted of the {th(total)} the site states ({where}) — {pageno} page(s) of {PAGE_SIZE} walked by request (--pages/--limit), not a shortfall.")
    elif n == total:
        note(f"{th(n)} emitted over {pageno} page(s), site states {th(total)} ({where}) — equal.")
    else:
        note(f"{th(n)} emitted over {pageno} page(s), site states {th(total)} ({where}) — {th(abs(total - n))} " + ("short" if total > n else "more emitted than the site states") + ".")
    note(f"the employer is on no row — {NO_EMPLOYER}; `employer` is null on all {th(n)}.")


def brief(body):
    """The «Job Brief» / «Requirements» pairs — `detail_title` beside `detail_data`, as the page lays them out."""
    out = {}
    for m in re.finditer(r'<span class="detail_title">([^<]+)</span>\s*<span[^>]*class="detail_data"[^>]*>(.*?)</span>', body or "", re.S):
        out[text(m.group(1)).rstrip(":").strip()] = text(m.group(2)) or None
    return out


def salary(s):
    """«$0.00 — $0.00» is the board's blank: emitted as no salary, never as zero. A real range gives (min, max)."""
    if not s:
        return None, None
    nums = [float(x.replace(",", "")) for x in re.findall(r"\$\s*([\d,]+(?:\.\d+)?)", s)]
    nums = [x for x in nums if x > 0]
    if not nums:
        return None, None
    return min(nums), max(nums)


def cmd_ad(a):
    m = DETAIL_RE.match((a.url or "").strip())
    if not m:
        die(f"{a.url}: not a detail address as the list writes it — expected {BOARD}?action=detail&recordid=<digits>&pcr-id=<token> (the token is the list's; without it the site serves an empty shell)")
    ident = m.group(1)
    code, body = request(a.url)
    if code in (404, 410):
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    title = re.search(r'<h1 class="litejobtitle"[^>]*>(.*?)</h1>', body, re.S)
    if not title or "detail_title" not in body:
        die(f"{a.url}: not a posting page ({len(body)} characters) — the shell the site serves without the list's token, or a redirect.", EXIT_PARTIAL)
    b = brief(body)
    # the description is the page's own `jd-description-text` block — the employer's text as posted
    dm = re.search(r'<div class="jd-description-text">(.*?)</div>\s*</div>\s*</div>', body, re.S) or re.search(r'<div class="jd-description-text">(.*?)Click here to apply', body, re.S)
    desc = text(dm.group(1)) if dm else ""
    desc = re.sub(r"\n?Click here to apply online.*$", "", desc, flags=re.S).strip()
    loc_line = next((l[len("Location:"):].strip() for l in desc.split("\n") if l.startswith("Location:") and "," in l), None)
    smin, smax = salary(b.get("Salary"))
    posted = re.search(r'class="date_posted">([^<]+)<', body)
    print(json.dumps({
        "source": "jobseekers_bs", "country": "BS", "ledger_id": f"jobseekers_bs:{ident}", "id": ident, "url": a.url,
        "title": text(title.group(1)) or None,
        "employer": None, "employer_hidden": NO_EMPLOYER,
        "island": b.get("Location"),
        "workplace": loc_line,                        # the page's own «Location: <place>, <island>, Bahamas» line, when it gives one
        "job_type": b.get("Job Type"),
        "industry": b.get("Industry"),
        "salary_min": smin, "salary_max": smax,
        "salary_currency": "BSD" if smin else None,  # the board prints «$» on a Bahamian board; the dollar is at par and the page names no code
        "salary_unit_stated": False,                 # no period is printed beside the amount
        "benefits": b.get("Benefits"), "vacation": b.get("Vacation"),
        "degree": b.get("Degree"), "years_experience": b.get("Years Experience"),
        "posted_relative": text(posted.group(1)) if posted else None,   # «Posted 4 Hours ago» — the page gives no date on the detail
        "description": desc[:20000] or None,
        "language": "en",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Dept of Labour Online Skills Bank (Bahamas) — the public employment service's PCRecruiter board, paged by the form its page posts; «a-b of N» beside every walk; the employer is on neither page. Issue #447.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="the open postings, 24 a page, 3 s apart, 10 pages unless told otherwise; --island narrows to one island as the site names it")
    s.add_argument("--island", help="Abaco · Berry Islands · Eleuthera · Exuma · Grand Bahama · New Providence — as the site's select names them")
    s.add_argument("--keyword")
    s.add_argument("--pages", type=int, default=10)
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_search)
    d = sub.add_parser("ad", help="one posting, by the address the list wrote (the pcr-id token included)")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
