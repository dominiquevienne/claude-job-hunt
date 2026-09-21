#!/usr/bin/env python3
"""Government of Timor-Leste — the portal's «Recruitment» category (`timor-leste.gov.tl/?cat=44`): each entry is a dated document the government publishes (a PDF, sometimes an image) with its own summary; the category states no count, so the walk follows the pager until a page carries no entry, and prints what it read. Issue #685.

  timorlestegov.py jobs [--lang en] [--country-code TL] [--max-pages N]     the category (1 request a page, 3 pages on 2026-09-21)

WHAT IT IS. `timor-leste.gov.tl` is the Government of Timor-Leste's portal (WordPress, a theme of
its own); its **Recruitment** category is where ministries, courts and state projects publish their
calls for applications. Timor-Leste's other named boards are two community sites and a vacancy
portal (#686–#688); this is the state's own. *The application the portal cites,
`timorleste-jobs.tenderwell.app`, answers 404 at its root (2026-09-18) — not a route.*

THE RULES. `timor-leste.gov.tl` answers no rules file (`robots.txt` absent — open, certain, on
`/`, on the category and on `/wp-json/`), no Crawl-delay; 2 s is ours. The guard is taken on the
exact path.

THE LIST. `/?cat=44&lang=en&page=N` (200; 33 435 B for 10 entries, 31 657 for 10, 25 137 for 5,
19 110 for none) renders the category server-side: each entry is a `div.docs_img` (the icon) plus a
`div.docs_details` carrying `span.date` («01 of July of 2026»), `a.title` (the **document's own
address** — 24 of 25 are PDFs under `/wp-content/uploads/`, one is a JPEG), the summary paragraphs
the editor wrote, and `#file_size`. **No count is stated anywhere** and the pager only names the
next pages, so the walk asks page after page **until one carries no entry** (page 4 on
2026-09-21) — the run prints the entries read and the pages walked, and a page repeating the
previous page's addresses ends it (exit 6).

**What the category holds is what the government filed under it**: calls for applications for
judges, consultants and project staff, and occasionally a tender or a contest. The adapter does
not second-guess the ministry's filing — it emits the entries and says the category is the
board's own.

**WITHHELD:** e-mail addresses and telephone numbers in the summaries («[e-mail withheld]» /
«[telephone withheld]»), the editor's file-size string kept as read; `contacts_withheld` on every
record. The documents themselves are never downloaded — the record points at the address the
category publishes.

`--lang` picks the portal's language (`en`, `pt`, `tt` — the entries are often Portuguese whatever
the interface says, and the run does not translate). `--country-code` STAMPS (the category states
no country) and the run says so.

Measured 2026-09-21 13:38–13:40 UTC by the declared client, the guard on the exact path, two reads
of page 1 and one of each other page: page 1 200 ×2 (33 435 B, md5 d20470a82dd2 / f5bdc419f9d7 —
an agenda block moves), **10 entries**; page 2 200 (31 657 B) 10; page 3 200 (25 137 B) 5; page 4
200 (19 110 B) **0 — the walk's end**. **25 entries, no count stated**; the oldest is dated 2022,
the newest 2026-07-01.
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

HOST = "timor-leste.gov.tl"
CAT = "44"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")   # «+670 333 1234»: 8+ digits with separators
DATE_RE = re.compile(r"\b\d{1,2}\s+of\s+\w+\s+of\s+\d{4}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b")
DOC_RE = re.compile(r'<div class="docs_img">.*?<div class="docs_details">(.*?)(?=<div class="docs_img">|</ul>)', re.S)
TITLE_RE = re.compile(r'<a class="title"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S)
DATE_SPAN_RE = re.compile(r'<span class="date">(.*?)</span>', re.S)
SIZE_RE = re.compile(r'<div id="file_size">(.*?)</div>', re.S)
MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}
MONTHS.update({m.lower(): i for i, m in enumerate(        # the portal dates some entries in Portuguese whatever `lang` says
    ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
     "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"], 1)})
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[timorlestegov] {msg}", file=sys.stderr)


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
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en, pt"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", markup or "")
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span)\b[^>]*>", "", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def when(s):
    """«01 of July of 2026» → `2026-07-01`; anything else as read."""
    s = (s or "").strip()
    m = re.match(r"^(\d{1,2})\s+of\s+([^\s\d]+)\s+of\s+(\d{4})$", s)
    if m and MONTHS.get(m.group(2).lower()):
        return f"{m.group(3)}-{MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    return s or None


def key_of(url):
    """The entry's key: the document's own file name, which the portal does not repeat."""
    path = urllib.parse.urlsplit(htmlmod.unescape(url or "")).path
    return urllib.parse.unquote(path.rsplit("/", 1)[-1]) or None


def entries_of(markup):
    """The category page → [(key, fields)], one per `docs_details` block that names a document."""
    out = []
    for block in DOC_RE.findall(markup or ""):
        t = TITLE_RE.search(block)
        if not t:
            continue
        url = htmlmod.unescape(t.group(1))
        d = DATE_SPAN_RE.search(block)
        size = SIZE_RE.search(block)
        body = TITLE_RE.sub("", block)
        body = DATE_SPAN_RE.sub("", body)
        body = SIZE_RE.sub("", body)
        out.append((key_of(url), {"url": url, "title": text(t.group(2)), "date": text(d.group(1)) if d else None,
                                  "file_size": text(size.group(1)) if size else None, "summary": text(body)}))
    return out


def record(key, f, stamp):
    return {
        "source": "timorlestegov", "country": stamp,
        "ledger_id": f"timorlestegov:{key}", "id": key,
        "url": f.get("url"), "title": scrub(f.get("title")),
        "published": when(f.get("date")),
        "document_size": f.get("file_size"),
        "summary": scrub(f.get("summary")),
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    lang = (a.lang or "en").strip().lower()
    if not re.match(r"^[a-z]{2}$", lang):
        die(f"--lang {a.lang}: two letters (en, pt, tt)")
    stamp = a.country_code.upper() if a.country_code else None
    rows, seen, page, empty_at = [], set(), 0, None
    while True:
        page += 1
        q = {"cat": CAT, "lang": lang}
        if page > 1:
            q["page"] = str(page)
        url = f"https://{HOST}/?" + urllib.parse.urlencode(q)
        code, body = request(url)
        if code == 404:
            die(f"{url}: HTTP 404 — no such category", EXIT_GONE)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if page == 1 and "docs_details" not in body and "cat=44" not in body:
            die(f"{url}: 200 without the category's entries — the page changed; not an empty category", EXIT_PARTIAL)
        found = entries_of(body)
        keys = {k for k, _f in found}
        if not found:
            empty_at = page
            break                                   # the walk's end: a page the category does not fill
        if page > 1 and keys and keys <= seen:
            die(f"page {page} repeats the previous page's documents — the walk ended at {th(len(rows))}", EXIT_PARTIAL)
        for k, f in found:
            if not k or k in seen:
                continue
            seen.add(k)
            rows.append(record(k, f, stamp))
        if a.max_pages and page >= a.max_pages:
            break
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if not rows:
        note("0 entries — the category's first page carries none (200); not an error.")
    else:
        end = f"page {empty_at} carried none — the walk's end" if empty_at else f"stopped by --max-pages at page {page}"
        note(f"{th(len(rows))} entries emitted over {th(page - (1 if empty_at else 0))} page(s); {end}. The category states no count: what it lists is the board.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the category states no country.")
    note("the documents themselves are never downloaded; contacts in the summaries scrubbed.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Government of Timor-Leste — the portal's Recruitment category, walked until a page carries no entry; the documents are named, never downloaded. Issue #685.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the category (1 request a page)")
    j.add_argument("--lang", default="en", help="the portal's language (en, pt, tt) — default en")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the category states none)")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0, help="stop after N pages (0 = until a page carries no entry)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
