#!/usr/bin/env python3
"""Fetch Thai ads from JOBBKK — where page 5 000 answers 200 with page 5's ads.

Thailand's largest board by volume. **No key, no cookie, no browser**:
`robots.txt` is 275 bytes of `text/plain`, identical on the apex and on `www`,
and closes résumés, uploads, mail, captchas and `/jobs/apply/` — **nothing on
the listings, and no AI agent named**.

  GET /jobs/lists/<page>/หางาน,<keyword>,<province>,<category>.html
      → 200 text/html, ~1.2 MB, 25 result cards
  GET /jobs/detail/<company_id>/<jobpost_id>
      → 200 text/html, the ad, with an `application/ld+json` JobPosting

THE LISTING IS THE PAYLOAD. The page is a Next.js app and its flight data
carries **the whole record for each of the 25 cards** — `jobpost_id`,
`company_id`, `company_name`, `position`, the duties text, province, district,
`gmap_la`/`gmap_lo`, `salary_start`/`salary_end`, `job_format_type`,
`employment_type`, `created_at`, `updated_at`. One request buys 25 ads, so a
sweep costs one request per 25, not 26.

PAST THE END, THE BOARD REPEATS THE LAST PAGE FOR EVER. Measured on
*โปรแกรมเมอร์* (programmer) 2026-09-02:

    page 4     25 cards, distinct
    page 5     25 cards, distinct  ← the last real page
    page 200   the same 25 cards as page 5
    page 500   the same 25
    page 5000  the same 25

**No 404, no empty list, no error.** A sweep that pages until it gets nothing
back never stops, and every extra page adds 25 duplicates it has already seen.
This script compares each page's ids with the previous page's and stops when
they repeat — that is the only end-of-results signal this board gives.

The wall is **per search, not global**: *บัญชี* (accounting) and the unfiltered
listing were still returning distinct pages at page 20.

THE PAYLOAD SENDS A SALARY THE EMPLOYER ASKED TO HIDE. `salary_not_show` is
`"1"` on 18 ads of 133, and **17 of those 18 also carry `salary_start` and
`salary_end`**. The site does not display them. This adapter does not emit
them either — `salary_withheld: true`, and no figure. Reading a field the
operator sends is fair; publishing one it was asked to hide is not.

AND THE PAGE CARRIES A "NO RESULTS" MESSAGE WHILE SHOWING RESULTS. The Thai
string *ขออภัยไม่พบตำแหน่งงานที่คุณค้นหา* — "sorry, no position found" — is in
the served HTML of a page with 25 ads, in a hidden template. **Never decide
emptiness by searching for it**; count the cards.

Everything here was verified against the live site on **2026-09-02**.
"""

import argparse
import json
import re

from _decode import decode_body
from _ldjson import absent_reason, one, postings
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _robots import allowed as robots_allowed

from _zero import zero_note

BASE = "https://www.jobbkk.com"
LIST = "/jobs/lists/{page}/หางาน,{keyword},{province},{category}.html"
AD = "/jobs/detail/{company}/{job}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

ALL_PROVINCES = "ทุกจังหวัด"
ALL_CATEGORIES = "ทั้งหมด"

DETAIL = re.compile(r'href="/jobs/detail/(\d+)/(\d+)"')


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def _robots_gate(url, tag, exit_code=7):
    """Ask before fetching — per host and **per path**. Issues #100, #101.

    `verdict()` answers *is this host closed in one block*. **A site that
    refuses its ad path while leaving its root open passes that and refuses
    every advertisement** — `empleate.gob.hn` does exactly that, closing
    `/Vacantes/` to `User-agent: *` with `/` absent.

    It sits **inside the fetch function**, so every request is covered rather
    than the first one, and a refusal **stops the command** with exit 7 and the
    module's own words. **This adapter decides nothing about what a refusal
    means** — deciding is what turns a check into a decoration.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return None
    a = robots_allowed(parts.netloc, parts.path or "/")
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", exit_code)
    if a.get("requested_host") and a["host"] != a["requested_host"]:
        print(f"[hellowork] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts. A platform that has "
              f"been renamed reaches an adapter this way before it reaches it "
              f"as a rename.", file=__import__("sys").stderr)
    return a



def note(msg):
    print(f"[jobbkk] {msg}", file=sys.stderr)


def get(path):
    _robots_gate(BASE + path if not path.startswith("http") else path, 'jobbkk')
    url = BASE + urllib.parse.quote(path, safe="/,.?=&")
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html",
        # The pages are 1.2 MB; identity keeps the parse honest and the
        # measurement comparable.
        "Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            ctype = r.headers.get("Content-Type", "")
            body = decode_body(r.read(), r.headers)[0]
            if "text/html" not in ctype:
                die(f"{url}: Content-Type {ctype!r} — this board serves HTML. "
                    f"A different type means a different page.")
            return body
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        die(f"{url}: HTTP {exc.code}")
    except (urllib.error.URLError, OSError) as exc:
        die(f"{url}: {exc}")


def records(page_html):
    """Pull the card objects out of the Next.js flight payload.

    The payload is JSON escaped inside a JavaScript string, so it is unescaped
    once and then matched on `"jobpost_id":`. Brace-balanced rather than
    regex-bounded, because the duties text contains braces.
    """
    text = page_html.replace('\\"', '"').replace("\\\\", "\\")
    out = []
    for m in re.finditer(r'"jobpost_id"\s*:\s*\d+', text):
        start = text.rfind("{", 0, m.start())
        if start < 0:
            continue
        depth, i, n = 0, start, len(text)
        while i < n:
            c = text[i]
            if c == '"':
                i += 1
                while i < n and text[i] != '"':
                    i += 2 if text[i] == "\\" else 1
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        try:
            out.append(json.loads(text[start:i + 1]))
        except ValueError:
            continue
    return out


def card(r):
    job, comp = r.get("jobpost_id"), r.get("company_id")
    lo, hi = r.get("salary_start"), r.get("salary_end")
    withheld = str(r.get("salary_not_show") or "") == "1"
    return {
        "id": f"{comp}/{job}",
        "ledger_id": f"jobbkk:{comp}/{job}",
        "url": BASE + AD.format(company=comp, job=job),
        "title": r.get("position"),
        "company": r.get("company_name"),
        "company_id": comp,
        "province": r.get("province_name"),
        "district": r.get("district_name"),
        "location_text": r.get("location"),
        "latitude": r.get("gmap_la"),
        "longitude": r.get("gmap_lo"),
        "occupation": r.get("occupation_sub_name") or r.get("occupation_name"),
        "industry": r.get("business_name"),
        "job_format": r.get("job_format_type"),
        "employment_note": r.get("employment_type"),
        # `salary_start`/`salary_end` are 0 when the employer stated no
        # figure — a zero, not a null.
        #
        # **`salary_not_show == "1"` is the employer asking for the figure to
        # be hidden, and the payload sends it anyway**: 17 of the 18 ads
        # carrying that flag also carried an amount. This adapter withholds it.
        # The board's own display honours the flag; a plugin that published
        # what the site hides would be reading past a request, not reading a
        # public field.
        "salary_min": None if withheld else (lo or None),
        "salary_max": None if withheld else (hi or None),
        "salary_withheld": withheld,
        # **`created_at` is not the posting age.** Ads created in 2022 and
        # 2024 came back on page 1 of a 2026 search, refreshed the day before.
        # The age the site shows is `date_up` / `updated_at`; a scorer that
        # reads `created` as "posted" ages a live ad by four years.
        "created": (r.get("created_at") or "")[:10] or None,
        "refreshed": (r.get("updated_at") or "")[:10] or None,
        "date_label": r.get("date_up"),
        "welcomes_new_graduates": bool(r.get("is_new_graduated")),
        "open_to_disability": bool(r.get("is_disability")),
        "online": bool(r.get("is_online")),
        # The duties block, which is also what the ad page's JSON-LD carries.
        "duties_chars": len((r.get("detail") or "").strip()),
    }


def list_path(a, page):
    return LIST.format(page=page, keyword=a.keyword or "",
                       province=a.province, category=a.category)


def cmd_search(a):
    seen, kept, previous = set(), 0, None
    page = 1
    while True:
        html = get(list_path(a, page))
        if html is None:
            note(f"page {page} answered 404 — stopping.")
            break
        ids = [f"{c}/{j}" for c, j in DETAIL.findall(html)]
        if not ids:
            note(f"page {page} carried no result card — stopping. (The Thai "
                 f"'no position found' string is in every page's HTML as a "
                 f"hidden template, so the cards are what count.)")
            break
        if previous is not None and ids == previous:
            note(f"page {page} repeats page {page - 1} exactly — that is this "
                 f"board's end of results. It never 404s and never empties; "
                 f"page 5 000 would return these same {len(ids)} ads.")
            break
        previous = ids
        rows = records(html)
        if not rows:
            die(f"page {page}: {len(ids)} ad links but no card records parsed. "
                f"The Next.js payload has moved — re-verify jobbkk.md before "
                f"trusting anything from this board.")
        for r in rows:
            c = card(r)
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            print(json.dumps(c, ensure_ascii=False))
            kept += 1
            if a.limit and kept >= a.limit:
                note(f"{kept} ads returned over {page} page(s).")
                return
        page += 1
        if a.pages and page > a.pages:
            break
        time.sleep(a.delay)
    if kept == 0:
        note(zero_note("jobbkk", what=a.keyword, where=a.province))
    note(f"{kept} ads returned over {page} page(s) read.")


def cmd_ad(a):
    comp, _, job = a.id.partition("/")
    if not job:
        die("--id is <company_id>/<jobpost_id>, as the ledger stores it.")
    html = get(AD.format(company=comp, job=job))
    if html is None:
        die(f"{a.id}: 404 — the ad is gone.", 3)
    # One reader for every board's ld+json: tolerant of the quote style
    # on the script tag, and strict=False on the parse. Issue #76.
    posting = (postings(html) or [None])[-1]
    if posting is None:
        why = absent_reason(html)
        die(f"{a.id}: no JobPosting JSON-LD — {why.text} It was on 12 of 12 "
            f"ads on 2026-09-02, so re-verify jobbkk.md.",
            2 if why.our_fault else 3)
    addr = (one(posting.get("jobLocation")).get("address") or {})
    print(json.dumps({
        "id": a.id,
        "ledger_id": f"jobbkk:{a.id}",
        "url": BASE + AD.format(company=comp, job=job),
        "title": posting.get("title"),
        "company": one(posting.get("hiringOrganization")).get("name"),
        "employment_type": posting.get("employmentType"),
        "occupational_category": posting.get("occupationalCategory"),
        "posted": (posting.get("datePosted") or "")[:10] or None,
        # A date, but a distant one — 2026-12 to 2027-05 across the sample.
        # It is a listing expiry, not an application deadline.
        "expires": (posting.get("validThrough") or "")[:10] or None,
        "street": addr.get("streetAddress"),
        "district": addr.get("addressLocality"),
        "province": addr.get("addressRegion"),
        "postal_code": addr.get("postalCode"),
        # The duties block only — the rendered page carries several more
        # sections. 24 to 942 characters over 12 ads.
        "duties_chars": len(posting.get("description") or ""),
        "duties": posting.get("description") if a.with_text else None,
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="read the result cards")
    s.add_argument("--keyword", required=True,
                   help="Thai or English, as typed on the site")
    s.add_argument("--province", default=ALL_PROVINCES,
                   help=f"Thai province name; default {ALL_PROVINCES} (all)")
    s.add_argument("--category", default=ALL_CATEGORIES,
                   help=f"Thai category name; default {ALL_CATEGORIES} (all)")
    s.add_argument("--limit", type=int)
    s.add_argument("--pages", type=int)
    s.add_argument("--delay", type=float, default=1.5)
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="read one ad by id")
    d.add_argument("--id", required=True, help="<company_id>/<jobpost_id>")
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
