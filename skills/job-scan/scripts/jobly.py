#!/usr/bin/env python3
"""Jobly (`www.jobly.fi`, Alma Media, Finland) — the private generalist left beside Duunitori now that Oikotie Työpaikat has closed; a Drupal site whose rules ask `Crawl-delay: 10` — honoured as written; the listing's own «12 737 avointa työpaikkaa» printed beside every walk; the sitemap's two files as the whole inventory; the ad's JobPosting and body read, the body scrubbed of the recruiters' addresses and numbers it carries. Issue #376.

  jobly.py sitemap [--host jobly|cvonline-hu] [--limit N]           the sitemap files — every advertisement, with lastmod; 3 requests + 1 for the stated count
  jobly.py list [--host jobly|cvonline-hu] [--pages N] [--limit N]  the listing walked, 20 a page, 10 s a page
  jobly.py ad --url <https://www.jobly.fi/tyopaikka/<slug>-<id> | https://www.cvonline.hu/hu/allas/<slug>-<id>>

THE SAME TEMPLATE ON A SECOND BOARD — `--host cvonline-hu` (#362). CVOnline Hungary
(`www.cvonline.hu`, Alma Career) is the same Jobiqo/Drupal recruiter template: the same
rules file (Drupal's default, `Crawl-delay: 10`), the same `<article id="node-<id>">` card,
the same panes, the same sitemap index in two files; what differs is named per board — the
listing `/hu/allashirdetesek` («5 681 ÁLLÁS VÁR, JELENTKEZZ MÉG MA!» in its `<h1>`), the ad
`/hu/allas/<slug>-<id>` (and `/hu/<tier>/allas/…` — premium, lite, freemium …), the sitemap
`/hu/sitemap.xml`, the body in `recruiter_job_template` rather than `field--name-body`,
«Frissítés dátuma:» for the date. `source` and `ledger_id` carry the board's key; `ad --url`
reads the board off the address; an unknown host is refused before any request.

THE RULES (2 281 B, Drupal's default under `*`) ask `Crawl-delay: 10` and refuse `/search/`,
the account pages, and **`/node/*/apply-external` — the «Hae paikkaa» link — never followed**;
`/tyopaikat`, its `?page=N` pager, `/tyopaikka/<slug>-<id>` and `/sitemap.xml` are open. **Ten
seconds between requests is the host's own asking and the adapter's pace** (`_pace.Pace`,
the longer of the host's and ours); a full walk of the listing (637 pages on the day) is not
what `list` is for — `sitemap` gives the whole inventory in three requests.

THE STATED COUNT. `/tyopaikat` («Avoimet työpaikat Joblyssa») says «Tällä hetkellä meillä on
**12 737** avointa työpaikkaa» — printed beside every walk and beside the sitemap's rows. The
sitemap index names two files (`?page=1`, `?page=2`; 10 000 and 4 511 rows) with **13 813
`/tyopaikka/` rows, 13 636 distinct ids (177 repeated across the files), lastmod from 2023-04
to the day, 831 other rows (articles, pages) set aside — 899 more than stated: the sitemap
keeps expired advertisements, and the two witnesses are never merged**.

THE LIST. 20 cards a page, **`?page=N` counted from zero — `?page=1` is the SECOND page** (the
AfricaWork lesson: an index the page counts from zero); a card is `<article id="node-<id>"
about="/tyopaikka/…">` with title, «13.09.2026,» and the employer, the location line
(«95900 Kolari, Lappi»). The cards are the site's, in its order; `--pages` 5 unless told, and
the note says «walked by request».

THE AD. A JSON-LD JobPosting — title, `datePosted`, `validThrough`, `hiringOrganization`,
`employmentType` (a list), `jobLocation` (a list of places — a town with its postcode, then
the region), `occupationalCategory`, `baseSalary` (empty on the day: `salary_unit_stated`
only when a `unitText` is printed) — and the page's panes (region items, the employment-type
term, «Julkaistu 13.09.2026»). **The body carries an AI summary («Tämä tiivistelmä on luotu
tekoälyn avulla») that names the recruitment consultant with telephone and e-mail, and a
«Lisätietoja työpaikasta» block that does the same: the text is emitted scrubbed of e-mail
addresses (including Cloudflare's «[email protected]» placeholder) and Finnish telephone
numbers; `contacts_withheld` on every record.** Observed on the day: one node whose slug and
AI summary describe a waiter's post and whose body describes a ski-shop post — the node is
the site's, the record carries its title and its body as served.

Measured 2026-09-14 02:0x UTC by the declared client, the guard on the exact path, 10 s apart.
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

BOARDS = {
    "jobly": {"host": "www.jobly.fi", "country": "FI", "lang": "fi", "list": "/tyopaikat", "sitemap": "/sitemap.xml",
              "ad": re.compile(r"^/tyopaikka/[^/]+-(\d+)/?$"),
              "count": re.compile(r"meillä on\s*(\d[\d\s  ]*)\s*avointa työpaikkaa"),
              "published": re.compile(r"Julkaistu\s+(\d{2}\.\d{2}\.\d{4})")},
    "cvonline-hu": {"host": "www.cvonline.hu", "country": "HU", "lang": "hu", "list": "/hu/allashirdetesek", "sitemap": "/hu/sitemap.xml",
                    "ad": re.compile(r"^/hu/(?:[a-z]+/)?allas/[^/]+-(\d+)/?$"),
                    "count": re.compile(r"(\d[\d\s  ]*)\s*ÁLLÁS VÁR"),
                    "published": re.compile(r"Frissítés dátuma:\s*(\d{2}\.\d{2}\.\d{4})")},
}
DEFAULT = "jobly"
PAGE_SIZE = 20

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+|\[email(?:\s| |&#160;)*protected\]")
# Finnish 044-7866005 · 040 123 4567 · +358 40 123 4567 — and Hungarian +36 1 808 8376 · 06 30 123 4567 · 06-30-123-4567 · 0630/1234567
PHONE_RE = re.compile(r"(?<![\d+])(?:(?:\+36|06)[\s /-]?\(?\d{1,2}\)?[\s /-]?\d{3}[\s /-]?\d{3,4}|(?:\+358[\s ]?\(?0?\)?[\s ]?|0)\d{1,3}[\s -]?\)?\d{2,4}[\s -]?\d{2,4}(?:[\s -]?\d{1,3})?)(?!\d)")
CARD_RE = re.compile(r'<article id="node-(\d+)"\s+about="(/[^"]+)"(.*?)</article>', re.S)
TITLE_RE = re.compile(r'<h2 class="node__title">\s*<a[^>]*>(.*?)</a>', re.S)
DATE_RE = re.compile(r'<span class="date">\s*(\d{2}\.\d{2}\.\d{4})')
ORG_RE = re.compile(r'<span class="recruiter-company-profile-job-organization">(.*?)</span>', re.S)
LOC_RE = re.compile(r'<div class="location">\s*<span>(.*?)</span>', re.S)
PAGER_RE = re.compile(r'href="[^"?]*\?page=(\d+)"')
LOC_XML_RE = re.compile(r"<url>\s*<loc>([^<]+)</loc>(?:\s*<lastmod>([^<]+)</lastmod>)?", re.S)
BODY_RES = (re.compile(r'<div class="field field--name-body[^"]*">(.*?)</div>\s*</div>\s*</div>', re.S),           # Jobly: the node's body field
            re.compile(r'<div class="recruiter_job_template">\s*<div class="markup">(.*?)</div>\s*</div>\s*</div>', re.S))   # CVOnline: the employer's template
PANE_RE = re.compile(r'<div class="field field--name-field-job-(region|employment-type-term)[^"]*">(.*?)</div>\s*</div>\s*</div>', re.S)
ITEM_RE = re.compile(r'<div class="field__item [^"]*">([^<]*)')   # the items are plain text (`field__items` is the wrapper); the pane's last closing tag is eaten by PANE_RE


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobly] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACES = {}


def pace_for(host):
    if host not in _PACES:
        _PACES[host] = Pace(host, own=2.0)   # both hosts write Crawl-delay: 10 — the longer wins, and it is the host's
    return _PACES[host]


def board_of(host):
    """`--host jobly` / `cvonline-hu` or a hostname → the board; an unknown one is refused before any request."""
    if host is None:
        return dict(BOARDS[DEFAULT], key=DEFAULT)
    h = host.strip().lower()
    for k, b in BOARDS.items():
        if h == k or h == b["host"] or h == b["host"].replace("www.", ""):
            return dict(b, key=k)
    known = ", ".join(f"{k} ({b['host']})" for k, b in BOARDS.items())
    die(f"--host {host!r}: not a board of this template — {known}")


def request(url):
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    pace_for(host).wait()
    lang = next((b["lang"] for b in BOARDS.values() if b["host"] == host), "en")
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9", "Accept-Language": lang})
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
    return int(re.sub(r"[\s  ]", "", s))


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def iso(d):
    """«13.09.2026» → 2026-09-13."""
    m = re.match(r"\s*(\d{2})\.(\d{2})\.(\d{4})", d or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def stated(body, b):
    m = b["count"].search(text(body))
    return num(m.group(1)) if m else None


def cards(body, b):
    out = []
    for nid, path, block in CARD_RE.findall(body):
        if not b["ad"].match(path):
            continue   # a card of another shape is not this board's advertisement
        t = TITLE_RE.search(block)
        d = DATE_RE.search(block)
        o = ORG_RE.search(block)
        loc = LOC_RE.search(block)
        out.append({
            "source": b["key"], "country": b["country"], "ledger_id": f"{b['key']}:{nid}", "id": nid,
            "url": f"https://{b['host']}{path}", "title": text(t.group(1)) if t else None,
            "employer": text(o.group(1)) if o else None,
            "posted": iso(d.group(1)) if d else None,
            "location": text(loc.group(1)) if loc else None,   # «95900 Kolari, Lappi» — the towns, then the region
            "contacts_withheld": True, "language": b["lang"],
        })
    return out


def cmd_list(a):
    b = board_of(getattr(a, "host", None))
    LIST = f"https://{b['host']}{b['list']}"
    rows, seen, pageno, total, first = [], set(), 0, None, None
    while True:
        url = LIST + (f"?page={pageno}" if pageno else "")   # the site counts its pages from zero
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_GONE if code == 404 and pageno == 0 else EXIT_PARTIAL)
        if total is None:
            total = stated(body, b)
        page = cards(body, b)
        if not page:
            die(f"{url}: 200 and not one card — the template changed; not an empty market", EXIT_PARTIAL)
        if first is None:
            first = [r["id"] for r in page]
        elif [r["id"] for r in page] == first:
            die(f"{url}: the same cards as page 1 — the pager is not paging; not counted twice", EXIT_PARTIAL)
        new = 0
        for r in page:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            rows.append(r)
            new += 1
        pageno += 1
        more = {int(n) for n in PAGER_RE.findall(body)}
        if new == 0 or pageno not in more:
            break
        if a.pages and pageno >= a.pages:
            break
        if a.limit and len(rows) >= a.limit:
            break
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    if total is None:
        note(f"{th(n)} emitted over {pageno} page(s) — the listing's own count («… avointa työpaikkaa») was not found; not compared.")
    elif n < total:
        note(f"{th(n)} emitted over {pageno} page(s) of {PAGE_SIZE}, the listing states {th(total)} — walked by request (--pages/--limit), 10 s a page as the host asks; not a shortfall.")
    else:
        note(f"{th(n)} emitted over {pageno} page(s), the listing states {th(total)} — " + ("equal." if n == total else f"{th(n - total)} more emitted than stated."))
    note("the «Hae paikkaa» link (/node/*/apply-external) is refused in writing and never followed; the ad's text is scrubbed of the recruiters' addresses and numbers.")


def cmd_sitemap(a):
    b = board_of(getattr(a, "host", None))
    LIST, SITEMAP = f"https://{b['host']}{b['list']}", f"https://{b['host']}{b['sitemap']}"
    code, body = request(LIST)
    total = stated(body, b) if code == 200 else None
    code, body = request(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    files = re.findall(r"<sitemap>\s*<loc>([^<]+)</loc>", body)
    if not files:
        die(f"{SITEMAP}: no <sitemap> entry — the index's shape changed", EXIT_PARTIAL)
    rows, seen, other = [], set(), 0
    for f in files:
        code, body = request(f)
        if code != 200:
            die(f"{f}: HTTP {code}", EXIT_PARTIAL)
        for loc, lastmod in LOC_XML_RE.findall(body):
            m = b["ad"].match(urllib.parse.urlsplit(loc).path)
            if not m:
                other += 1
                continue
            if m.group(1) in seen:
                continue
            seen.add(m.group(1))
            rows.append({"source": b["key"], "country": b["country"], "ledger_id": f"{b['key']}:{m.group(1)}", "id": m.group(1), "url": loc, "lastmod": lastmod or None, "contacts_withheld": True, "language": b["lang"]})
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(rows)
    lm = sorted(r["lastmod"] for r in rows if r["lastmod"])
    span = f"lastmod {lm[0][:10]} … {lm[-1][:10]}" if lm else "no lastmod"
    if total is None:
        note(f"{th(n)} advertisement id(s) in {len(files)} file(s) ({span}; {th(other)} other rows set aside) — the listing's count was not read; not compared.")
    else:
        diff = n - total
        note(f"{th(n)} advertisement id(s) in {len(files)} file(s) ({span}; {th(other)} other rows set aside), the listing states {th(total)} — "
             + ("equal." if diff == 0 else (f"{th(diff)} more in the sitemap than the listing states: the sitemap keeps expired advertisements; the two witnesses are never merged." if diff > 0 else f"{th(-diff)} short.")))
    if a.limit and a.limit < n:
        note(f"{th(len(emitted))} emitted of the {th(n)} — bounded by --limit.")


def ldjson(body):
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S):
        try:
            d = json.loads(m, strict=False)
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("@type") == "JobPosting":
            return d
    return None


def place(p):
    ad = (p or {}).get("address") or {}
    if isinstance(ad, list):
        ad = ad[0] if ad else {}
    parts = [x for x in (ad.get("postalCode"), ad.get("addressLocality")) if x]
    s = " ".join(parts)
    if ad.get("addressRegion") and ad["addressRegion"] != ad.get("addressLocality"):
        s = f"{s}, {ad['addressRegion']}" if s else ad["addressRegion"]
    return s or None


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    b = next((dict(v, key=k) for k, v in BOARDS.items() if v["host"] == parts.netloc), None)   # the board is read off the address
    m = b["ad"].match(parts.path) if b else None
    if not b or not m:
        die(f"{a.url}: not an advertisement address on one of the boards — " + ", ".join(f"https://{v['host']}{v['list']}" for v in BOARDS.values()))
    url = f"https://{b['host']}{parts.path.rstrip('/')}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    ld = ldjson(body)
    bd = next((x for x in (r.search(body) for r in BODY_RES) if x), None)
    if not ld and not bd:
        die(f"{url}: 200 without a JobPosting or a body — the template changed", EXIT_PARTIAL)
    ld = ld or {}
    panes = {k: [text(i) for i in ITEM_RE.findall(v) if text(i)] for k, v in PANE_RE.findall(body)}
    locs = ld.get("jobLocation") or []
    locs = locs if isinstance(locs, list) else [locs]
    sal = (ld.get("baseSalary") or {}).get("value") or {}
    smin = num(str(sal.get("minValue"))) if str(sal.get("minValue") or "").strip().isdigit() else None
    smax = num(str(sal.get("maxValue"))) if str(sal.get("maxValue") or "").strip().isdigit() else None
    unit = (sal.get("unitText") or "").strip().lower() or None
    pub = b["published"].search(text(body))
    et = ld.get("employmentType")
    print(json.dumps({
        "source": b["key"], "country": b["country"], "ledger_id": f"{b['key']}:{m.group(1)}", "id": m.group(1), "url": url,
        "title": htmlmod.unescape(ld.get("title") or "").strip() or None,
        "employer": htmlmod.unescape(((ld.get("hiringOrganization") or {}).get("name")) or "").strip() or None,
        "employment_type": et if isinstance(et, list) else ([et] if et else None),
        "employment_type_term": (panes.get("employment-type-term") or [None])[0],
        "locations": [x for x in (place(p) for p in locs) if x] or (panes.get("region") or None),
        "region_items": panes.get("region") or None,
        "category": ld.get("occupationalCategory") or None,
        "salary_min": smin, "salary_max": smax, "salary_currency": ((ld.get("baseSalary") or {}).get("currency") or None) if (smin is not None or smax is not None) else None,
        "salary_unit": unit if (smin is not None or smax is not None) else None, "salary_unit_stated": bool(unit) and (smin is not None or smax is not None),
        "posted": (ld.get("datePosted") or "")[:10] or (iso(pub.group(1)) if pub else None),
        "valid_through": (ld.get("validThrough") or "")[:10] or None,
        "direct_apply": ld.get("directApply"),
        "description": scrub(text(bd.group(1))) if bd else scrub(text(htmlmod.unescape(ld.get("description") or ""))),
        # the «Hae paikkaa» link is /node/<id>/apply-external — refused in writing, never followed; the recruiters' addresses and numbers in the text are scrubbed
        "contacts_withheld": True, "language": b["lang"],
    }, ensure_ascii=False))
    note(f"{url}: read; the text is scrubbed of e-mail addresses and telephone numbers; the apply link is never followed.")


def main():
    p = argparse.ArgumentParser(description="Jobly — Finland's private generalist beside Duunitori; Crawl-delay 10 honoured; the listing's own count beside every walk; the sitemap as the inventory; the ad scrubbed of the recruiters' contacts. Issue #376.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s_ = sub.add_parser("sitemap", help="every advertisement id the two sitemap files carry, against the listing's count")
    s_.add_argument("--host", help="jobly (default) · cvonline-hu — or the hostname")
    s_.add_argument("--limit", type=int)
    s_.set_defaults(fn=cmd_sitemap)
    l_ = sub.add_parser("list", help="the listing, 20 a page, 10 s a page, 5 pages unless told")
    l_.add_argument("--host", help="jobly (default) · cvonline-hu — or the hostname")
    l_.add_argument("--pages", type=int, default=5)
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
