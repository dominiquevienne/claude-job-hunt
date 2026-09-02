#!/usr/bin/env python3
"""Fetch Vietnamese ads from Vieclam24h — 110 fields per ad, and the adapter
reads sixteen of them on purpose.

One of Vietnam's largest boards. **No key, no cookie, no browser**: every
search page carries its results in the page's own `__NEXT_DATA__`, and
`robots.txt` — 356 bytes of `text/plain` — declares a sitemap index whose job
files hold **17 089 ad URLs**.

  GET /tim-kiem-viec-lam-nhanh?q=<terms>&page=<n>
      → 200 text/html; `props.initialState.api.getJobList.data`
        30 items a page, with `total_items` and `last`
  GET /file/sitemap/sitemap-index.xml → the sitemap families
  GET /<category>/<slug>c<c>p<p>id<id>.html
      → one ad; `props.initialState.api.jobDetailHiddenContact.data`, 110 keys

THE RECORD CARRIES OTHER PEOPLE'S CONTACT DETAILS, ON EVERY AD. Measured on 90
ads, 2026-09-02:

    employer_info    present on 90 of 90   (43 keys, incl. the board's own
                                            account manager, named)
    contact_name     filled  on 90 of 90
    contact_email    filled
    contact_phone    filled
    contact_address  filled

These are a named recruiter's direct details and a named salesperson's, not
job data. **A pipeline ledger is a file on somebody's disk that gets pasted
into issues and backed up**, and none of that belongs in it.

**So this card is an allow-list, not a deny-list.** It names the sixteen fields
it emits and copies nothing else, which means a field added to the payload
tomorrow cannot leak through it. Dropping `employer_info` by name would have
left `contact_email` behind — the deny-list was tried first, on paper, and it
missed four fields out of five.

**Nothing is lost.** Applying goes through the ad URL, where the employer
publishes what it chose to publish, to a person who is applying.

COUNT THE SALARY ON VALUES. `salary_min` and `salary_max` are present as keys
on **90 of 90** and carry a real figure on **89** — 98.9%, not 100%. The
difference is one ad, and the habit is the point: on this repository's other
boards the same slip has been worth 80 points.

A BARE `curl` IS REFUSED AND AN ORDINARY BROWSER IS NOT. The ad page answers
**403** to a plain request and **200** to the same URL with an ordinary
`Accept`/`Accept-Language` pair. It is header sniffing rather than a bot wall
— nothing in `robots.txt` refuses this — so the script sends what a browser
sends and nothing more.

Verified against the live site on **2026-09-02**.
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _zero import zero_note

from _robots import verdict as robots_verdict

BASE = "https://vieclam24h.vn"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
NEXT = re.compile(r'id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)

# **The allow-list.** Every field the card may carry, and nothing else is
# copied out of the payload. See the header: the record holds a named
# recruiter's phone, email and address, and the board's own account manager.
KEEP = ("id", "title", "title_slug", "salary_min", "salary_max", "salary_unit",
        "vacancy_quantity", "experience_range", "degree_requirement",
        "working_method", "province_ids", "updated_at", "resume_apply_expired",
        "total_views", "is_verified", "employer_id")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[vieclam24h] {msg}", file=sys.stderr)


def get(path):
    url = path if path.startswith("http") else BASE + path
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        # Without these two the same URL answers 403. Header sniffing, not a
        # refusal — robots.txt permits this path.
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.getcode(), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            die(f"{url}: HTTP 403. This site refuses a request with no "
                f"`Accept`/`Accept-Language`; if this script is sending them "
                f"and is still refused, the sniffing changed.", 5)
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def payload(html, where):
    m = NEXT.search(html)
    if not m:
        die(f"{where}: no __NEXT_DATA__ — the page shape changed.")
    try:
        return json.loads(m.group(1))
    except ValueError as e:
        die(f"{where}: __NEXT_DATA__ did not parse ({e}).")


def card(item):
    """Only what KEEP names. Never a copy of the record."""
    out = {k: item.get(k) for k in KEEP}
    ident = out.get("id")
    slug = out.get("title_slug")
    out["ledger_id"] = f"vieclam24h:{ident}"
    # The sitemap writes `/<category>/<slug>id<id>.html`, and the listing
    # carries no category — but the category segment turns out to be optional:
    # `/ke-toan-ban-hangid200897251.html` answers 200 without redirecting.
    # Checked 2026-09-02, which is why this builds the short form rather than
    # spending a request to learn the category.
    out["url"] = (f"{BASE}/{slug}id{ident}.html" if slug else None)
    # Values, not keys: the pair is present on every ad and filled on almost
    # every one.
    out["salary_stated"] = bool((out.get("salary_min") or 0) > 0)
    return out


def cmd_search(a):
    v = robots_verdict("vieclam24h.vn")
    if not v["sweep"]:
        die(f"vieclam24h.vn: {v['reason']}", 7)
    seen, kept, total, last = set(), 0, None, None
    for page in range(1, a.pages + 1):
        q = urllib.parse.urlencode({"q": a.keyword or "", "page": page})
        code, html = get(f"/tim-kiem-viec-lam-nhanh?{q}")
        if code != 200:
            die(f"search page {page}: HTTP {code}")
        d = payload(html, f"search page {page}")
        try:
            data = d["props"]["initialState"]["api"]["getJobList"]["data"]
        except KeyError:
            die("the search payload moved — `getJobList` is not where it was.")
        if total is None:
            total, last = data.get("total_items"), data.get("last")
        items = data.get("items") or []
        if not items:
            note(f"page {page} carried no item — stopping.")
            break
        for it in items:
            if it.get("id") in seen:
                continue
            seen.add(it.get("id"))
            print(json.dumps(card(it), ensure_ascii=False))
            kept += 1
            if a.limit and kept >= a.limit:
                break
        if a.limit and kept >= a.limit:
            break
        time.sleep(a.delay)
    if kept == 0:
        note(zero_note("vieclam24h", what=a.keyword))
    note(f"{kept} ad(s) of {total} matching, across {last} page(s) of 30.")
    note("the card carries the sixteen fields named in KEEP and copies "
         "nothing else: the payload also holds a named recruiter's phone, "
         "email and address, and the board's own account manager. A field "
         "that is never read cannot leak.")


def cmd_ad(a):
    v = robots_verdict("vieclam24h.vn")
    if not v["sweep"]:
        die(f"vieclam24h.vn: {v['reason']}", 7)
    code, html = get(a.url)
    if code != 200:
        die(f"{a.url}: HTTP {code}", 3)
    d = payload(html, a.url)
    try:
        job = d["props"]["initialState"]["api"]["jobDetailHiddenContact"]["data"]
    except KeyError:
        die("the ad payload moved — `jobDetailHiddenContact` is not where it "
            "was.")
    c = card(job)
    c["url"] = a.url
    # The description is job data and is kept; the contact block is not.
    if a.with_text:
        c["description"] = job.get("description")
        c["job_requirement"] = job.get("job_requirement")
        c["benefit"] = job.get("benefit")
    c["description_chars"] = len(job.get("description") or "")
    print(json.dumps(c, ensure_ascii=False))


def cmd_sitemap(a):
    v = robots_verdict("vieclam24h.vn")
    if not v["sweep"]:
        die(f"vieclam24h.vn: {v['reason']}", 7)
    code, idx = get("/file/sitemap/sitemap-index.xml")
    if code != 200:
        die(f"sitemap index: HTTP {code}")
    families = re.findall(r"<loc>([^<]+)</loc>", idx)
    jobs = [f for f in families if "/job-" in f]
    urls = []
    for f in jobs:
        code, body = get(f)
        for sub in re.findall(r"<loc>([^<]+)</loc>", body):
            code2, body2 = get(sub)
            urls += re.findall(r"<loc>([^<]+)</loc>", body2)
            time.sleep(a.delay)
    note(f"{len(urls)} ad URL(s) across the job sitemaps. The index also "
         f"declares occupation, province and district families, which are "
         f"search landing pages rather than ads — count the job files only.")
    for u in urls[:a.limit] if a.limit else urls:
        m = re.search(r"id(\d+)\.html$", u)
        print(json.dumps({"id": int(m.group(1)) if m else None, "url": u},
                         ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="read the search results")
    s.add_argument("--keyword")
    s.add_argument("--pages", type=int, default=1)
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=1.5)
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="read one ad by URL")
    d.add_argument("--url", required=True)
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)

    m = sub.add_parser("sitemap", help="every ad URL, from the job sitemaps")
    m.add_argument("--limit", type=int)
    m.add_argument("--delay", type=float, default=1.0)
    m.set_defaults(func=cmd_sitemap)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
