#!/usr/bin/env python3
"""Fetch Philippine ads from PhilJobNet — where `?page=2` is accepted, ignored,
and answers 200.

The Philippines' public employment portal, run by the Department of Labor and
Employment. **No key, no cookie prompt, no browser** — but the pagination is
an ASP.NET WebForms postback, and the obvious shortcut is a trap.

  GET  /job-vacancies/                 → 200, ten ads, `__VIEWSTATE` and
                                         `__EVENTVALIDATION` in the form
  POST /job-vacancies/                 → the next ten, with those two fields
       __EVENTTARGET=ctl00$BodyContentPlaceHolder$GridView1
       __EVENTARGUMENT=Page$<n>
  GET  /job-vacancies/job/<slug>-<id>  → one ad

`?page=2` ANSWERS 200 WITH PAGE ONE. Measured 2026-09-02: the ten ad ids it
returns are **the same ten**, in the same order. Nothing errors, nothing
warns, and an adapter written on it **paginates for ever over the same ten
ads while reporting a complete sweep** — the purest form of the failure
`shared/never-fail-silently.md` exists to prevent.

The postback works: `Page$2` returned ten ads with **zero overlap** with page
one.

**So the check that matters is not that a page answered 200 — it is that its
ids do not intersect the previous page's.** This script does that on every
page and stops with a named reason if they do, rather than trusting the
mechanism it just used.

TWO THINGS ABOUT THE HOST, BOTH MEASURED BEFORE ANYTHING ELSE:

- **`www.philjobnet.gov.ph` presents Azure's default certificate**
  (`CN=*.azurewebsites.net`), so every client that verifies refuses it, and
  over plain HTTP it answers 404. **The apex is the service**:
  `philjobnet.gov.ph` answers 200. That is `shared/robots-policy.md`'s TLS
  case — a certificate that does not cover the name stops every client while
  the service underneath is alive, and a plain request separates the two.
- **`philjobnet.gov.ph/robots.txt` is a 404** — no file published. Absent is
  not a refusal, and `_robots.py` treats it that way.

Verified against the live site on **2026-09-02**.
"""

import argparse
import html as html_mod
import http.cookiejar
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _zero import zero_note

from _robots import verdict as robots_verdict

BASE = "https://philjobnet.gov.ph"
LIST = BASE + "/job-vacancies/"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

GRID = "ctl00$BodyContentPlaceHolder$GridView1"
CARD = re.compile(r'<div class="jobcard".*?(?=<div class="jobcard"|\Z)', re.S)
ADLINK = re.compile(r'href="(/job-vacancies/job/([a-z0-9-]+-(\d+)))"')
HIDDEN = re.compile(r'<input[^>]*type="hidden"[^>]*>', re.I)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[philjobnet] {msg}", file=sys.stderr)


def text_of(fragment):
    t = re.sub(r"(?is)<(script|style|svg)[^>]*>.*?</\1>", " ", fragment)
    t = re.sub(r"<[^>]+>", "\n", t)
    return [x.strip() for x in html_mod.unescape(t).split("\n") if x.strip()]


class Session:
    def __init__(self, delay=1.5):
        self.jar = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar))
        self.op.addheaders = [
            ("User-Agent", UA),
            ("Accept", "text/html,application/xhtml+xml"),
            ("Accept-Language", "en-US,en;q=0.9"),
        ]
        self.delay = delay
        self.last_html = ""

    def get(self, url):
        try:
            with self.op.open(url, timeout=45) as r:
                self.last_html = decode_body(r.read(), r.headers)[0]
                return r.getcode(), self.last_html
        except urllib.error.HTTPError as e:
            return e.code, ""
        except (urllib.error.URLError, OSError) as e:
            die(f"{url}: {e}")

    def post_page(self, n):
        """Replay the form with the GridView's own postback arguments.

        `__VIEWSTATE` and `__EVENTVALIDATION` are per-response: they must come
        from the page just received, not from the first one. Reusing a stale
        pair is how a WebForms sweep silently returns to page one.
        """
        fields = {}
        for m in HIDDEN.finditer(self.last_html):
            tag = m.group(0)
            name = re.search(r'name="([^"]+)"', tag)
            val = re.search(r'value="([^"]*)"', tag)
            if name:
                fields[name.group(1)] = html_mod.unescape(
                    val.group(1)) if val else ""
        fields["__EVENTTARGET"] = GRID
        fields["__EVENTARGUMENT"] = f"Page${n}"
        req = urllib.request.Request(
            LIST, data=urllib.parse.urlencode(fields).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with self.op.open(req, timeout=45) as r:
                self.last_html = decode_body(r.read(), r.headers)[0]
                return r.getcode(), self.last_html
        except urllib.error.HTTPError as e:
            return e.code, ""
        except (urllib.error.URLError, OSError) as e:
            die(f"POST Page${n}: {e}")


def cards(html):
    """Pair each card with the link that sits **before** it, not inside it.

    **The anchor precedes the block it belongs to.** On the grid, the link for
    `stockman-1460624` sits at byte 18 835 and the first `<div class="jobcard">`
    starts at 18 942 — so a parser that takes the link *inside* a block gets
    the **next** card's id. Every row would carry the right title against the
    wrong id, and nothing would say so: measured while writing this, by
    checking a slug against a title. `sales-clerk-1460623` came back titled
    "STOCKMAN"; the ad page says "SALES CLERK".

    The slug encodes the title, so the pairing is self-checking, and the card
    carries `slug_matches_title` for the next reader.
    """
    out = []
    starts = [m.start() for m in re.finditer(r'<div class="jobcard"', html)]
    links = [(m.start(), m.group(1), m.group(3), m.group(2))
             for m in ADLINK.finditer(html)]
    blocks = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(html)
        before = [l for l in links if l[0] < start]
        blocks.append((html[start:end], before[-1] if before else None))
    for block, link in blocks:
        if link is None:
            continue
        _pos, href, ident, slug = link
        lines = text_of(block)
        salary = next((x for x in lines if x.startswith("₱")), None)
        posted = next((x for x in lines if x.lower().startswith("posted on")),
                      None)
        # The card's own order: title, salary, employer, location, education,
        # employment type, posted. Anything absent is simply not printed by
        # the site, so positions are read by content rather than by index.
        educ = next((x for x in lines if "Educ" in x or "GRADUATE" in x.upper()
                     or "LEVEL" in x.upper()), None)
        kind = next((x for x in lines
                     if x in ("Permanent", "Contractual", "Part-time",
                              "Probationary", "Project-based", "Seasonal")),
                    None)
        body = [x for x in lines
                if x not in (salary, posted, educ, kind) and len(x) > 2]
        title = body[0] if body else None
        employer = body[1] if len(body) > 1 else None
        where = body[2] if len(body) > 2 else None
        want = re.sub(r"-\d+$", "", slug).replace("-", " ").lower()
        out.append({
            "id": ident,
            "ledger_id": f"philjobnet:{ident}",
            "url": BASE + href,
            # The slug carries the title, so the pairing checks itself. False
            # here means the anchor and the block drifted apart again.
            "slug_matches_title": bool(title) and want == (title or "").lower(),
            "title": title,
            "company": employer,
            "location_text": where,
            # "Salary not specified" is printed as text and never as ₱, so a
            # missing key here is the board's own silence, not a parse failure.
            "salary_text": salary,
            "education": educ,
            "employment_type": kind,
            "posted_text": posted,
        })
    return out


def cmd_search(a):
    v = robots_verdict("philjobnet.gov.ph")
    if not v["sweep"]:
        die(f"philjobnet.gov.ph: {v['reason']}",
            8 if v["sweep"] is None else 7)
    if v["state"] != "read":
        note(f"robots.txt: {v['reason']} — absent is not a refusal, so the "
             f"sweep proceeds at a human pace.")
    s = Session(a.delay)
    code, html = s.get(LIST)
    if code != 200:
        die(f"{LIST}: HTTP {code}")
    seen, kept, previous = set(), 0, None
    page = 1
    while True:
        rows = cards(html)
        ids = [r["id"] for r in rows]
        if not ids:
            note(f"page {page} carried no job card — stopping.")
            break
        # **The check that matters.** `?page=2` answers 200 with page one's
        # ten ads; so does a postback with a stale __VIEWSTATE. A page that
        # repeats the previous one has not advanced, whatever it answered.
        if previous is not None and set(ids) & set(previous):
            overlap = len(set(ids) & set(previous))
            note(f"page {page} repeats {overlap} of page {page - 1}'s "
                 f"{len(previous)} ads — the pagination did not advance. "
                 f"Stopping rather than looping. {kept} ad(s) returned so far "
                 f"and they are good.")
            print(json.dumps({"partial": True, "pages_read": page - 1,
                              "reason": "pagination stopped advancing"}),
                  file=sys.stderr)
            sys.exit(6)
        previous = ids
        for r in rows:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            print(json.dumps(r, ensure_ascii=False))
            kept += 1
            if a.limit and kept >= a.limit:
                note(f"{kept} ad(s) over {page} page(s).")
                return
        if a.pages and page >= a.pages:
            break
        page += 1
        time.sleep(a.delay)
        code, html = s.post_page(page)
        if code != 200:
            note(f"POST for page {page}: HTTP {code} — stopping.")
            break
    if kept == 0:
        note(zero_note("philjobnet"))
    note(f"{kept} ad(s) over {page} page(s) of ten.")


def cmd_ad(a):
    v = robots_verdict("philjobnet.gov.ph")
    if not v["sweep"]:
        die(f"philjobnet.gov.ph: {v['reason']}",
            8 if v["sweep"] is None else 7)
    s = Session()
    code, html = s.get(a.url)
    if code != 200:
        die(f"{a.url}: HTTP {code}", 3)
    lines = text_of(html)
    try:
        start = lines.index("Job details") + 1
    except ValueError:
        start = 0
    body = lines[start:]
    posted = next((body[i + 1] for i, x in enumerate(body)
                   if x.lower() == "posted on" and i + 1 < len(body)), None)
    print(json.dumps({
        "url": a.url,
        "id": (re.search(r"-(\d+)$", a.url) or [None, None])[1],
        "title": body[3] if len(body) > 3 else None,
        "salary_text": body[4] if len(body) > 4 else None,
        "company": body[5] if len(body) > 5 else None,
        "posted_text": posted,
        "lines": len(body),
        "description": "\n".join(body) if a.with_text else None,
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="read the vacancy grid")
    s.add_argument("--pages", type=int, default=3)
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=1.5)
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="read one ad by URL")
    d.add_argument("--url", required=True)
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
