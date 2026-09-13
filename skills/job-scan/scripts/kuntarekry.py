#!/usr/bin/env python3
"""Kuntarekry (`kuntarekry.fi`) — the recruitment service of Finland's municipalities and wellbeing-services counties, through the server-rendered job cards its own pages carry; the site's own «count» printed beside every walk; the contact person on every ad never leaves. Issue #373.

  kuntarekry.py search [--filter <slug>] [--pages N] [--limit N]
  kuntarekry.py ad --url <https://kuntarekry.fi/fi/tyopaikat/<slug>-<key>/>

THE ROUTE IS THE PAGE — a Lit web-components site whose LIST is rendered by the server:

  GET /fi/tyopaikat/?view=count&format=json     -> {"count": 1356}   — the site's own counter (what its `<job-counter>` asks)
  GET /fi/tyopaikat/                             -> 28 <job-card …> elements: 24 postings + 4 «Mainostetut» (is-promoted="true", repeated on every page); <ip-pagination current="1" total="57" next="/fi/tyopaikat/sivu2/">
  GET /fi/tyopaikat/sivu2/ … /sivuN/             -> the next pages
  GET /fi/tyopaikat/<slug>-<key>/                -> one posting: a JobPosting in JSON-LD, the text, and the contact person

A filter is a path segment the site itself links (`/fi/tyopaikat/espoo`, `/fi/tyopaikat/pirkanmaa`,
`/fi/tyopaikat/sairaanhoitajat-ja-terveydenhoitajat`, an organisation's slug…): `--filter espoo`
walks `/fi/tyopaikat/espoo/` and asks the counter for the same path. **The four promoted cards are
skipped by their own attribute** and every id is emitted once.

Measured 2026-09-13 23:5x UTC by the declared client: count 1 356, 57 pages of 24 (the last
short), page 2 answered `current="2"`; the rules (113 B) `*` Allow: /, two sitemaps that are HTML
pages, no Crawl-delay — 2 s is ours. **`--pages` defaults to 10** (240 rows) and the note says
the walk was bounded by request; 57 pages is a choice.

THE CARD carries the title, `profit-center` (the hiring unit — «Espoon kaupunki», «Saimaan
Tukipalvelut Oy»), `organisation-title` when the site sets one, the publication date and time,
the application deadline (`publication-end` + time, DD.M.YYYY), the site's own key (`job-key`,
e.g. ESPOO-03-1327-26) and id, the address. THE AD carries a JobPosting (title, hiringOrganization,
jobLocation, datePosted, validThrough, employmentType, baseSalary as free text in EUR — «Palkkaus
määräytyy KVTES … 2 312,36 e» — emitted as `salary_text`, never parsed into a number, unit not
stated) and the text. **The contact person — name, e-mail, telephone — is on every ad, in its
own block and often inside the text; the block is dropped and the text is scrubbed of e-mail
addresses and Finnish telephone numbers before it is emitted.** The «Hae työpaikkaa» application
is the site's own form and is never touched.
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

HOST = "kuntarekry.fi"
BASE = f"https://{HOST}"
LIST = f"{BASE}/fi/tyopaikat/"
PAGE_SIZE = 24
CARD_RE = re.compile(r"<job-card\b([^>]*)>", re.S)
PAGER_RE = re.compile(r'<ip-pagination\b([^>]*)>', re.S)
DETAIL_RE = re.compile(r"^https?://(?:www\.)?kuntarekry\.fi/fi/tyopaikat/([a-z0-9][a-z0-9.-]*-[a-z0-9-]+)/?$", re.I)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d.])(?:\+358|0)\s?\d{1,3}(?:[ -]?\d{2,4}){2,3}(?!\d)")   # a Finnish number in any of its spacings; a date (1.10.2026) never starts with 0 after a dot

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[kuntarekry] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # no Crawl-delay in the rules; 2 s is ours


def request(url, accept="text/html,application/xhtml+xml"):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": accept, "Accept-Language": "fi"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</dd>|</dt>|</tr>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t  ]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def attrs(s):
    return {k: htmlmod.unescape(v) for k, v in re.findall(r'\s([a-z-]+)="([^"]*)"', s or "")}


def scrub(s):
    """No contact leaves: e-mail addresses and Finnish telephone numbers are struck from a text."""
    if not s:
        return s
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s)


def list_url(flt, page):
    base = LIST + (flt.strip("/") + "/" if flt else "")
    return base if page == 1 else f"{base}sivu{page}/"


def stated(flt):
    """The site's own counter — the JSON its `<job-counter>` asks for, on the same path as the walk."""
    code, body = request(list_url(flt, 1) + "?view=count&format=json", accept="application/json")
    if code != 200:
        return None
    try:
        d = json.loads(body)
    except ValueError:
        return None
    c = d.get("count") if isinstance(d, dict) else None
    return c if isinstance(c, int) else None


def pager(body):
    m = PAGER_RE.search(body or "")
    if not m:
        return None
    a = attrs(m.group(1))
    try:
        return int(a.get("current") or 0), int(a.get("total") or 0)
    except ValueError:
        return None


def cards(body):
    """One record per `<job-card>` that is not promoted — the site marks its four «Mainostetut» cards itself."""
    out = []
    for m in CARD_RE.finditer(body or ""):
        a = attrs(m.group(1))
        if a.get("is-promoted") == "true":
            continue
        ident = a.get("job-id")
        if not ident:
            continue
        out.append({
            "source": "kuntarekry", "country": "FI", "ledger_id": f"kuntarekry:{ident}", "id": ident,
            "key": a.get("job-key") or None,                          # the site's own key — ESPOO-03-1327-26
            "url": BASE + a["url"] if a.get("url", "").startswith("/") else (a.get("url") or None),
            "title": a.get("title") or None,
            "employer": a.get("profit-center") or a.get("organisation-title") or None,   # the hiring unit as the card names it
            "organisation": a.get("organisation-title") or None,
            "posted": a.get("publication-date") or None,                                  # DD.M.YYYY as printed
            "application_deadline": (a.get("publication-end") + (" " + a["publication-end-time"] if a.get("publication-end-time") else "")).strip() if a.get("publication-end") else None,
            "language": "fi",
        })
    return out


def cmd_search(a):
    total = stated(a.filter)
    where = f"({a.filter})" if a.filter else "(the whole site)"
    if total is None:
        note(f"the site's counter did not answer for {where} — the walk goes on without a witness.")
    out, seen, pageno = [], set(), 0
    pages_total = None
    while True:
        pageno += 1
        url = list_url(a.filter, pageno)
        code, body = request(url)
        if code == 404 and pageno > 1:
            pageno -= 1
            break
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        pg = pager(body)
        if pg and pg[0] != pageno:
            die(f"{url}: asked for page {pageno}, the pager says current={pg[0]} — the page did not turn.", EXIT_PARTIAL)
        if pg:
            pages_total = pg[1]
        rows = cards(body)
        if pageno == 1 and not rows:
            if (total or 0) > 0:
                die(f"{url}: the site counts {total} and the first page carries no card — a reading fault, not an empty list.", EXIT_PARTIAL)
            note(f"no card on the first page and the site counts nothing {where}.")
            return
        new = 0
        for r in rows:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            out.append(r)
            new += 1
        if new == 0 or (pages_total and pageno >= pages_total) or (total and len(out) >= total):
            break
        if a.pages and pageno >= a.pages:
            break
        if a.limit and len(out) >= a.limit:
            break
    emitted = out[:a.limit] if a.limit else out
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    if total is None:
        note(f"{th(n)} emitted over {pageno} page(s){' of ' + str(pages_total) if pages_total else ''}; no count from the site.")
        return
    bounded = (a.pages and pageno >= a.pages and (pages_total or 0) > pageno) or (a.limit and a.limit < total)
    if bounded:
        note(f"{th(n)} emitted of the {th(total)} the site counts {where} — {pageno} of {pages_total or '?'} page(s) walked by request (--pages/--limit), not a shortfall.")
    elif n == total:
        note(f"{th(n)} emitted over {pageno} page(s), site counts {th(total)} {where} — equal.")
    else:
        note(f"{th(n)} emitted over {pageno} page(s), site counts {th(total)} {where} — {th(abs(total - n))} " + ("short" if total > n else "more emitted than the site counts") + ".")


def jsonld(body):
    for m in re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', body or ""):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("@type") == "JobPosting":
            return d
    return None


def cmd_ad(a):
    m = DETAIL_RE.match((a.url or "").strip())
    if not m:
        die(f"{a.url}: not a posting address — expected {LIST}<slug>-<key>/")
    code, body = request(a.url)
    if code in (404, 410):
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    d = jsonld(body)
    jv = attrs((re.search(r"<job-view\b([^>]*)>", body) or [None, ""])[1])
    if not d and not jv.get("job-ext-id"):
        die(f"{a.url}: no JobPosting and no <job-view> on the page ({len(body)} characters) — not a posting, or the site changed.", EXIT_PARTIAL)
    d = d or {}
    loc = d.get("jobLocation") if isinstance(d.get("jobLocation"), dict) else {}
    addr = loc.get("address") if isinstance(loc.get("address"), dict) else {}
    sal = d.get("baseSalary") if isinstance(d.get("baseSalary"), dict) else {}
    key = jv.get("job-ext-id") or m.group(1).rsplit("-", 1)[-1]
    print(json.dumps({
        "source": "kuntarekry", "country": "FI", "ledger_id": f"kuntarekry:key:{key}", "key": key, "url": a.url,
        "title": d.get("title") or jv.get("job-title") or None,
        "employer": d.get("hiringOrganization") if isinstance(d.get("hiringOrganization"), str) else (d.get("hiringOrganization") or {}).get("name"),
        "workplace": ", ".join(x for x in (addr.get("addressLocality"), addr.get("addressRegion")) if x) or None,
        "postal_code": str(addr["postalCode"]) if addr.get("postalCode") is not None else None,
        "posted": d.get("datePosted"), "application_deadline": d.get("validThrough"),
        "employment_type": d.get("employmentType"),
        "salary_text": scrub(sal.get("value")) if isinstance(sal.get("value"), str) else None,   # free text — «Palkkaus määräytyy KVTES …» — never parsed into a number
        "salary_currency": sal.get("currency") or None, "salary_unit_stated": False,
        "description": scrub(text(d.get("description") or ""))[:20000] or None,
        "contacts_withheld": True,   # the contact person's block (name, e-mail, telephone) is not read; the text is scrubbed
        "language": "fi",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Kuntarekry — Finland's municipal recruitment service through the job cards its pages render; the site's own count beside every walk; no contact ever leaves. Issue #373.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="the open postings, 24 a page, 2 s apart, 10 pages unless told otherwise; --filter is a path segment the site itself links (espoo, pirkanmaa, sosiaaliala, an organisation's slug)")
    s.add_argument("--filter")
    s.add_argument("--pages", type=int, default=10)
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_search)
    d = sub.add_parser("ad", help="one posting — the JobPosting and the text, the contact person withheld")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
