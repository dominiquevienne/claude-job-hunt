#!/usr/bin/env python3
"""Állásportál (`allasportal.hu`, Hungary) — the generalist of manual trades and agency work, at the THIRTY seconds its rules ask (`Crawl-Delay: 30`, honoured as written); the list's own «8661 állás» printed beside every walk; the job sitemap as the inventory in one request; two kinds of card — hosted ads read, redirected ads (whose only address the rules refuse) carried as the card and never followed; the contact block the hosted ad's body carries, scrubbed. Issue #360.

  allasportal.py sitemap [--limit N]          sitemap_job.xml — every /munka-<slug>/ (2 requests, 60 s: the list for its count, then the file)
  allasportal.py list [--pages N] [--limit N] /munka/list, 15 cards a page, 30 s a page, 3 pages unless told
  allasportal.py ad --url <https://allasportal.hu/munka-<slug>/>

THE RULES (741 B, `*`): `Crawl-Delay: 30`, five sitemaps named, and `Disallow` on
`/munka/redirect/`, `/munka/sendmail/`, `/munka/statclick/`, `/munka/statapply/`,
`/munka/track/` (and the same under `/job/` and `/allas/`), `/munka/add`, `/favorite/`,
`/user/new`. **Thirty seconds between requests is the host's own asking and the adapter's pace**
— `_pace.Pace` takes the longer of the host's and ours. `/munka/list`, its `?page=N` pager,
`/munka-<slug>/` and the sitemaps are open.

TWO KINDS OF CARD. `/munka/list` («8661 állás - összegyűjtöttük a nagy állásoldalak összes
találatát» — the count stated, and the site says it gathers the big boards' results) prints
15 cards a page over 722 pages: a card is an employer, a title, a snippet, a county, an age
(«3 napja», «tegnapi», «még aktuális», «3 hónapja - még aktuális») and a link that is either
`data-jobtype="jobshow"` — an ad hosted at `/munka-<slug>/` — or `data-jobtype="redirect"` —
an ad on another board whose only address here is `/munka/redirect/<id>`, **refused in
writing: the record carries the card's fields and `url` null with the reason; nothing is
followed**. The id is the card's `data-job`.

THE SITEMAP. `sitemap_job.xml` carries every hosted ad — 8 670 `/munka-<slug>/` on the day, no
lastmod, no id (the slug is the key) — against the list's 8 661 (which counts both kinds):
printed side by side, never merged.

THE AD (hosted). No JSON-LD: the `<h1>`, the employer (`card-head`), the county (`.loc`), the
categories (`jobad-categs`), the body (the `order-1` column) — **which carries the employer's
«Kapcsolati adatok» block (telephone, e-mail): scrubbed of Hungarian telephone numbers and
e-mail addresses, Cloudflare's «[email protected]» included; `contacts_withheld` on every
record** — and the employer's own apply address (`apply_url`, another host, never fetched);
the statistics beacons (`/munka/statclick/`) are refused and never sent.

Measured 2026-09-14 02:13–02:2x UTC by the declared client, the guard on the exact path, 30 s
apart: the sitemap 1 167 855 B / 8 670 rows; the list 135 251 B, 15 cards, «8661 állás», 722
pages; one hosted ad 98 485 B with its contact block.
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

HOST = "allasportal.hu"
LIST = f"https://{HOST}/munka/list"
SITEMAP = f"https://{HOST}/sitemap_job.xml"
PAGE_SIZE = 15
REDIRECT_REASON = "the ad is on another board and its only address here is /munka/redirect/<id>, refused in writing (Disallow: /munka/redirect/) — the card is the record, nothing is followed"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+|\[email(?:\s| |&#160;)*protected\]")
# +36 1 808 8376 · +36 30 123 4567 · 06 30 123 4567 · 06-30-123-4567 · 0630/1234567
PHONE_RE = re.compile(r"(?<![\d+])(?:\+36|06)[\s /-]?\(?\d{1,2}\)?[\s /-]?\d{3}[\s /-]?\d{3,4}(?!\d)")
COUNT_RE = re.compile(r"<span class=\"res\">\s*<strong>\s*(\d[\d\s  .]*?)\s*állás", re.S)
CARD_RE = re.compile(r'<div class="card"[^>]*>(.*?)<div class="col-lg-7 jobad-cta">', re.S)
AGE_RE = re.compile(r'<span class="date-info">([^<]*)</span>')
EMPLOYER_RE = re.compile(r'class="card-head"[^>]*>\s*<h2><span>(.*?)</span></h2>', re.S)
POS_RE = re.compile(r'<a href="([^"]+)"[^>]*data-job="(\d+)"[^>]*data-jobtype="(jobshow|redirect)"[^>]*class="pos"[^>]*>(.*?)</a>', re.S)
SNIPPET_RE = re.compile(r"<hr>\s*<p>(.*?)</p>", re.S)
LOC_RE = re.compile(r'class="loc">(.*?)</a>', re.S)
PAGER_RE = re.compile(r'href="/munka/list\?page=(\d+)"')
XML_LOC_RE = re.compile(r"<loc>([^<]+)</loc>")
H1_RE = re.compile(r"<h1>(.*?)</h1>", re.S)
CATEG_RE = re.compile(r'<div class="jobad-categs">(.*?)</div>', re.S)
BODY_RE = re.compile(r'<div class="col-12 col-lg-9 order-1">(.*?)(?:<p><a [^>]*class="btn-fill-orange"|<div class="col-12 col-lg-3 order-3">|<div class="jobad-cta">)', re.S)   # the column ends at the apply button or the sidebar
STAT_ID_RE = re.compile(r'send_statistic\("/munka/statclick/JOBID",\s*"(\d+)"')
APPLY_RE = re.compile(r'<a href="([^"]+)"[^>]*data-jobapply="1"')


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[allasportal] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # the host writes Crawl-Delay: 30 — the longer wins, and it is the host's


def request(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9", "Accept-Language": "hu"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>|<hr\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t ​]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def num(s):
    return int(re.sub(r"[\s  .]", "", s))


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def stated(body):
    m = COUNT_RE.search(body)
    return num(m.group(1)) if m else None


def slug_of(url):
    m = re.search(r"/munka-([^/]+)/?$", urllib.parse.urlsplit(url).path)
    return m.group(1) if m else None


def cards(body):
    out = []
    for block in CARD_RE.findall(body):
        p = POS_RE.search(block)
        if not p:
            continue
        href, jid, kind, title = p.groups()
        emp = EMPLOYER_RE.search(block)
        age = AGE_RE.search(block)
        sn = SNIPPET_RE.search(block)
        loc = LOC_RE.search(block)
        hosted = kind == "jobshow"
        out.append({
            "source": "allasportal", "country": "HU", "ledger_id": f"allasportal:{jid}", "id": jid,
            "kind": "hosted" if hosted else "redirect",
            "url": href if hosted else None,
            "url_withheld": None if hosted else REDIRECT_REASON,
            "title": text(title), "employer": text(emp.group(1)) if emp else None,   # a private advertiser has no card-head
            "county": text(loc.group(1)) if loc else None,
            "age": text(age.group(1)) if age else None,   # «3 napja», «tegnapi», «még aktuális» — the site's own words
            "summary": scrub(text(sn.group(1))) if sn else None,
            "contacts_withheld": True, "language": "hu",
        })
    return out


def cmd_list(a):
    rows, seen, pageno, total, first = [], set(), 0, None, None
    while True:
        pageno += 1
        url = LIST + (f"?page={pageno}" if pageno > 1 else "")
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_GONE if code == 404 and pageno == 1 else EXIT_PARTIAL)
        if total is None:
            total = stated(body)
        page = cards(body)
        if not page:
            die(f"{url}: 200 and not one card — the template changed; not an empty market", EXIT_PARTIAL)
        ids = [r["id"] for r in page]
        if first is None:
            first = ids
        elif ids == first:
            die(f"{url}: the same cards as page 1 — the pager is not paging; not counted twice", EXIT_PARTIAL)
        new = 0
        for r in page:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            rows.append(r)
            new += 1
        more = {int(n) for n in PAGER_RE.findall(body)}
        if new == 0 or (pageno + 1) not in more:
            break
        if a.pages and pageno >= a.pages:
            break
        if a.limit and len(rows) >= a.limit:
            break
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    redirected = sum(1 for r in emitted if r["kind"] == "redirect")
    if total is None:
        note(f"{th(n)} emitted over {pageno} page(s) — the list's own count («N állás») was not found; not compared.")
    elif n < total:
        note(f"{th(n)} emitted over {pageno} page(s) of {PAGE_SIZE}, the list states {th(total)} — walked by request (--pages/--limit), 30 s a page as the host asks; not a shortfall.")
    else:
        note(f"{th(n)} emitted over {pageno} page(s), the list states {th(total)} — " + ("equal." if n == total else f"{th(n - total)} more emitted than stated."))
    note(f"{th(redirected)} of the {th(n)} are ads on other boards whose only address here is refused in writing — carried as the card, url null, never followed; the hosted ads' contact block is scrubbed by `ad`.")


def cmd_sitemap(a):
    code, body = request(LIST)
    total = stated(body) if code == 200 else None
    code, body = request(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    rows, seen, other = [], set(), 0
    for loc in XML_LOC_RE.findall(body):
        slug = slug_of(loc)
        if not slug:
            other += 1
            continue
        if slug in seen:
            continue
        seen.add(slug)
        rows.append({"source": "allasportal", "country": "HU", "ledger_id": f"allasportal:slug:{slug}", "id": slug, "url": loc, "kind": "hosted", "contacts_withheld": True, "language": "hu"})
    if not rows:
        die(f"{SITEMAP}: 200 and not one /munka-<slug>/ row — the file's shape changed", EXIT_PARTIAL)
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(rows)
    if total is None:
        note(f"{th(n)} hosted advertisement(s) in the job sitemap ({th(other)} other rows set aside) — the list's count was not read; not compared.")
    else:
        diff = n - total
        note(f"{th(n)} hosted advertisement(s) in the job sitemap ({th(other)} other rows set aside), the list states {th(total)} (hosted and redirected together) — "
             + ("equal." if diff == 0 else (f"{th(diff)} more in the sitemap than the list states." if diff > 0 else f"{th(-diff)} fewer than the list states, which counts the redirected ads too.")) + " The two witnesses are never merged.")
    if a.limit and a.limit < n:
        note(f"{th(len(emitted))} emitted of the {th(n)} — bounded by --limit.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    slug = slug_of(a.url)
    if parts.netloc not in (HOST, f"www.{HOST}") or not slug:
        die(f"{a.url}: not a hosted advertisement address (https://{HOST}/munka-<slug>/) — a redirected ad has no readable address here")
    url = f"https://{HOST}/munka-{slug}/"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    h1 = H1_RE.search(body)
    bd = BODY_RE.search(body)
    if not h1 or not bd:
        die(f"{url}: 200 without a title or a body column — the template changed", EXIT_PARTIAL)
    jid = STAT_ID_RE.search(body)
    emp = EMPLOYER_RE.search(body)
    loc = LOC_RE.search(body)
    cat = CATEG_RE.search(body)
    apply_ = APPLY_RE.search(body)
    print(json.dumps({
        "source": "allasportal", "country": "HU", "ledger_id": f"allasportal:{jid.group(1) if jid else 'slug:' + slug}", "id": jid.group(1) if jid else slug, "url": url,
        "title": text(h1.group(1)), "employer": text(emp.group(1)) if emp else None,
        "county": text(loc.group(1)) if loc else None,
        "categories": [re.sub(r"\s+", " ", text(c)) for c in re.findall(r"<a[^>]*>(.*?)</a>", cat.group(1), re.S)] if cat else None,
        "apply_url": apply_.group(1) if apply_ and apply_.group(1).startswith("http") and HOST not in apply_.group(1) else None,   # the employer's own page on another host — never fetched
        "description": scrub(text(bd.group(1))),   # the «Kapcsolati adatok» block the employer writes is in the body — scrubbed
        "contacts_withheld": True, "language": "hu",
    }, ensure_ascii=False))
    note(f"{url}: read; the body is scrubbed of telephone numbers and e-mail addresses; the statistics beacons and the mail form are refused in writing and never sent.")


def main():
    p = argparse.ArgumentParser(description="Állásportál — Hungary's generalist of manual trades at the thirty seconds its rules ask; the list's own count beside every walk; hosted ads read, redirected ads carried as the card and never followed; the contact block scrubbed. Issue #360.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s_ = sub.add_parser("sitemap", help="every hosted advertisement in sitemap_job.xml, against the list's count")
    s_.add_argument("--limit", type=int)
    s_.set_defaults(fn=cmd_sitemap)
    l_ = sub.add_parser("list", help="the list, 15 a page, 30 s a page, 3 pages unless told")
    l_.add_argument("--pages", type=int, default=3)
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
