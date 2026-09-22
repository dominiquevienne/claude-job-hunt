#!/usr/bin/env python3
"""Department of Public Information (Guyana) — the Government's own vacancy notices (`dpi.gov.gy`, category «Vacancies»): the State's agencies file their advertisements here, and each one is a **document** the post embeds. Issue #703.

  dpigovgy.py jobs [--since 2026-01-01] [--country-code GY] [--max-pages N]    the category (1 request a page)
  dpigovgy.py ad --url https://dpi.gov.gy/<slug>/                              one notice, and the document it embeds

WHAT IT IS. The **Department of Public Information** is the Guyanese government's information arm;
its «Government Adverts → Vacancies» category is where GuySuCo, the Bureau of Statistics, the Guyana
Marketing Corporation, the Defence Force and other state bodies publish their recruitment
advertisements. *The Ministry of Labour's own National Job Bank (`labour.gov.gy/jobs-bank`) is a
different host and has its own card.*

THE RULES. `dpi.gov.gy` answers its rules file and allows both paths: open, `certain: True`, no
Crawl-delay; 2 s is ours. The guard is taken on the exact path.

THE LIST. `/category/government-adverts/vacancies/` (200; 307 102 B) renders the archive
server-side: ten `div.item` blocks inside `div.fn-archive-content`, each an `.item-title` link and an
`.item-date` («September 18, 2026»). **The theme prints NO pager link** — `/page/N/` nevertheless
answers (page 2, page 20 and page 60 each carry ten on 2026-09-22) and **the end of the walk is a
404**, which WordPress serves past the last page. *So the absence of a «next» link is not the end of
the list, and a walk that trusted the markup would stop at ten.*

**Nothing states a count**, here or anywhere on the site: the run prints the entries read, the pages
walked, and how the walk ended — never a total it did not read. The archive is deep (page 60 still
carries ten, page 100 answers 404), so `--since` bounds it **on the date each entry states**: the
posts are newest-first, so the walk stops at the first entry older than the date asked for, and the
run says the stop was ours rather than the category's.

**THE REST API IS NOT THE ROUTE, AND THAT IS MEASURED.** `wp/v2/posts?categories=39092` and
`wp/v2/posts?slug=<a post read from the HTML>` both answer **200 with `[]`** (2026-09-21 and
2026-09-22) while the same posts render in the archive — the site's REST returns no post at all. The
HTML is the route; the REST is not «empty», it is closed to this reading, and the difference is the
whole reason the adapter walks pages.

THE NOTICE. A post's body is not text: it is the **advertisement itself**, embedded — a PDF in the
`algori-pdf-viewer` iframe (the address sits in its `?file=` parameter) or the post's image. `ad`
names that address and the post's date; **no document is ever downloaded**.

**WITHHELD:** e-mail addresses and telephone numbers anywhere in a title (the agencies put theirs in
the document, which we do not read), `contacts_withheld` on every record. `--country-code` STAMPS
(the category states no country — every notice is Guyana's by the Department's own scope, and a
stamp is still the user's) and the run says so.

Measured 2026-09-22 08:0x–08:2x UTC by the declared client, the guard on the exact path: page 1 200
(307 102 B, md5 a3a231007eee), 10 entries, the newest 2026-09-18; `/page/2/` 200 (305 664 B) 10;
`/page/20/` 200 10; `/page/60/` 200 10; `/page/100/`, `/page/120/`, `/page/150/` and `/page/300/`
**404 (241 022 B, the theme's own not-found page)** — the end is between page 60 and page 100, and
the run says which page answered it.
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

HOST = "dpi.gov.gy"
CATEGORY = "/category/government-adverts/vacancies/"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\(?\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
DATE_RE = re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")
STRIP_RE = re.compile(r"(?s)<style.*?</style>|<script.*?</script>")
ARCHIVE_RE = re.compile(r'<div class="fn-archive-content">(.*?)</main>', re.S)
ITEM_RE = re.compile(r'<div class="item item-\d+[^"]*">(.*?)(?=<div class="item item-\d+|\Z)', re.S)
TITLE_RE = re.compile(r'class="item-title"[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S)
ITEM_DATE_RE = re.compile(r'item-date[^>]*>\s*-?\s*(.*?)<', re.S)
POST_TITLE_RE = re.compile(r'<h1 class="entry-title post-title"[^>]*>(.*?)</h1>', re.S)
POST_DATE_RE = re.compile(r'<a class="entry-date updated"[^>]*>(.*?)</a>', re.S)
PDF_RE = re.compile(r'algori-pdf-viewer[^"]*-iframe"\s+src="[^"]*\?file=([^"&]+)', re.S)
IMG_RE = re.compile(r'<img[^>]+class="[^"]*wp-post-image[^"]*"[^>]+src="([^"]+)"', re.S)
MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[dpigovgy] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return " ".join(t.split()) or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def when(s):
    """«September 18, 2026» → `2026-09-18`; anything else as read."""
    s = (s or "").strip()
    m = re.match(r"^([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})$", s)
    if m and MONTHS.get(m.group(1).lower()):
        return f"{m.group(3)}-{MONTHS[m.group(1).lower()]:02d}-{int(m.group(2)):02d}"
    return s or None


def slug_of(url):
    path = urllib.parse.urlsplit(url or "").path.strip("/")
    return path.rsplit("/", 1)[-1] or None


def entries_of(markup):
    """The archive region → [(url, title, date)]. Read INSIDE `fn-archive-content`: the sidebar uses
    the same `item item-N` class, and a page-wide read counted 41 blocks where the archive holds 10."""
    body = STRIP_RE.sub("", markup or "")
    region = ARCHIVE_RE.search(body)
    if not region:
        return None
    out = []
    for block in ITEM_RE.findall(region.group(1)):
        t = TITLE_RE.search(block)
        if not t:
            continue
        d = ITEM_DATE_RE.search(block)
        out.append((htmlmod.unescape(t.group(1)), text(t.group(2)), text(d.group(1)) if d else None))
    return out


def record(url, title, date, stamp):
    key = slug_of(url)
    return {
        "source": "dpigovgy", "country": stamp,
        "ledger_id": f"dpigovgy:{key}", "id": key,
        "title": scrub(title), "url": url, "published": when(date),
        "document_downloaded": False,    # the notice IS a document; `ad` names its address, nothing fetches it
        "contacts_withheld": True,
    }


def page_url(page):
    return f"https://{HOST}{CATEGORY}" if page == 1 else f"https://{HOST}{CATEGORY}page/{page}/"


def cmd_jobs(a):
    since = (a.since or "").strip()
    if since and not re.match(r"^\d{4}-\d{2}-\d{2}$", since):
        die(f"--since {a.since}: a date, YYYY-MM-DD")
    stamp = a.country_code.upper() if a.country_code else None
    rows, seen, page, ended, older = [], set(), 1, None, 0
    while True:
        url = page_url(page)
        code, body = request(url)
        if code == 404:
            if page == 1:
                die(f"{url}: HTTP 404 — the category is gone", EXIT_GONE)
            ended = f"page {page} answered 404 — the end of the category"   # WordPress past the last page
            page -= 1
            break
        if code != 200:
            die(f"{url}: HTTP {code} — the walk ended at {th(len(seen))}", EXIT_PARTIAL)
        found = entries_of(body)
        if found is None:
            die(f"{url}: 200 without the archive region — the page changed; not an empty category", EXIT_PARTIAL)
        if not found:
            ended = f"page {page} carried no entry"
            page -= 1
            break
        keys = {u for u, _t, _d in found}
        if page > 1 and keys <= seen:
            die(f"page {page} repeats the entries of the page before — the walk ended at {th(len(seen))}", EXIT_PARTIAL)
        stop = False
        for url_, title, date in found:
            if url_ in seen:
                continue
            seen.add(url_)
            r = record(url_, title, date, stamp)
            if since and r["published"] and re.match(r"^\d{4}-\d{2}-\d{2}$", r["published"]) and r["published"] < since:
                older += 1
                stop = True        # the archive is newest-first, so everything below is older too
                continue
            rows.append(r)
        if stop:
            ended = f"the first entry older than {since} was reached on page {page} — OUR bound, not the category's"
            break
        if a.max_pages and page >= a.max_pages:
            ended = f"stopped by --max-pages at page {page}"
            break
        page += 1
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if not rows:
        note(f"0 entries emitted over {th(page)} page(s); {ended}. Nothing on the site states a count.")
    else:
        note(f"{th(len(rows))} entries emitted over {th(page)} page(s) ({th(len(seen))} read); {ended}. **Nothing states a count** — what the category lists is the board.")
    if older:
        note(f"{th(older)} entry(ies) older than {since} not emitted: the walk stopped there because the archive is newest-first.")
    note("the notice IS a document (a PDF in the post's viewer, or its image): `ad --url <post>` names its address, and nothing is ever downloaded.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the category states no country.")


def cmd_ad(a):
    url = a.url.strip()
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST or not slug_of(url) or parts.query:
        die(f"--url {url}: a https://{HOST}/<slug>/ notice, without a query string")
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the notice is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    clean = STRIP_RE.sub("", body)
    t = POST_TITLE_RE.search(clean)
    if not t:
        die(f"{url}: 200 without the notice's title — the page changed", EXIT_PARTIAL)
    d = POST_DATE_RE.search(clean)
    pdf = PDF_RE.search(clean)
    img = IMG_RE.search(clean)
    doc = urllib.parse.unquote(pdf.group(1)) if pdf else (img.group(1) if img else None)
    r = record(url, text(t.group(1)), text(d.group(1)) if d else None,
               a.country_code.upper() if a.country_code else None)
    r["document_url"] = doc
    r["document_kind"] = "pdf" if pdf else ("image" if img else None)
    print(json.dumps(r, ensure_ascii=False))
    if doc is None:
        note("the notice embeds neither a PDF viewer nor an image — the advertisement is not where it usually is, and the record says so rather than inventing one.")
    else:
        note(f"the advertisement is a {r['document_kind']} at the address above; it is NAMED, never downloaded.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Department of Public Information (Guyana) — the Government's vacancy notices, walked until the category's 404. Issue #703.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the category (1 request a page)")
    j.add_argument("--since", metavar="YYYY-MM-DD", help="stop at the first entry older than this day (the archive is newest-first)")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the category states none)")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0, help="stop after N pages (0 = until the category's 404)")
    j.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one notice, and the address of the document it embeds")
    d.add_argument("--url", required=True, help="the notice's own address")
    d.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on the record")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
