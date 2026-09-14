#!/usr/bin/env python3
"""kode24 jobs — kodejobb.no (`kodejobb.no`, Norway): the developers' newspaper's board, one list page of every open ad under the menu's own «Alle stillinger N»; the ad page's JobPosting and its prose. Issue #367.

  kode24.py list [--limit N]
  kode24.py ad --url <https://kodejobb.no/stillinger/<employer-slug>/<uuid>>

THE BOARD IS NOT ON kode24.no. The newspaper (`www.kode24.no`, 708 KB
of front page) links its job menu to `www.kodejobb.no/stillinger`, and
`/jobb` on the newspaper redirects to `https://kodejobb.no/`. **The board
is `kodejobb.no`**, a Next.js site on a Sanity back end: `/stillinger`
serves every open ad server-rendered in `ul#job-list` — 16 cards on
2026-09-14 — and its menu states **«Alle stillinger 16»**: the count the
site states, printed beside the emitted count. No pager: the list is the
inventory. No key, no cookie, no browser.

THE CARD: `/stillinger/<employer-slug>/<uuid>`, the employer's own title
(`job-title-from-customer`), the employer, a one-line subtitle
(`job-title`), the locations (`job-location`, one span each), the
deadline as the site writes it («Frist: om 13 dager»), a «Ny» badge.

THE AD PAGE carries a `JobPosting` in JSON-LD (title, a one-line
description, datePosted, validThrough, employmentType,
hiringOrganization, jobLocation) and the prose — «Firma», «Stillingstittel»,
«Arbeidssted», «Frist: 27.9.2026» (d.m.yyyy, emitted ISO) and the body.
The apply button leads off-site; nothing behind it is read.

THE RULES. `www.kode24.no/robots.txt`: `User-agent: * / Disallow:` (24 B,
nothing refused); `kodejobb.no/robots.txt`: **404** (a Next.js 404 page)
— no rules, `certain: True`. 3 s own spacing.

WHAT IS WITHHELD. Addresses and phone numbers in the prose are replaced
(`[e-mail withheld]`, `[phone withheld]` — eight digits or more, Norwegian
numbers are eight). The board's own `kode24@hsmedia.no` sits in its
footer, in no field this file emits.
"""

import argparse
import html
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

HOST = "kodejobb.no"
BASE = f"https://{HOST}"
LIST = f"{BASE}/stillinger"
AD_RE = re.compile(r"^https?://(?:www\.)?kodejobb\.no/stillinger/([^/?#]+)/([0-9a-f-]{36})/?$")
CARD_RE = re.compile(r'<li class="job-list-item.*?</li>', re.S)
LINK_RE = re.compile(r'href="/stillinger/([^/"]+)/([0-9a-f-]{36})"')
TITLE_RE = re.compile(r'class="job-title-from-customer[^"]*">(.*?)</div>', re.S)
EMP_RE = re.compile(r'class="job-company-name[^"]*">(.*?)</div>', re.S)
SUB_RE = re.compile(r'class="job-title [^"]*">(.*?)</div>', re.S)
LOC_RE = re.compile(r'class="job-location[^"]*">(.*?)<div class="[^"]*job-due-date', re.S)
DUE_RE = re.compile(r'class="[^"]*job-due-date[^"]*">(.*?)</div>', re.S)
STATED_RE = re.compile(r"Alle stillinger<div[^>]*>(\d+)</div>")
LD_RE = re.compile(r"<script[^>]*ld\+json[^>]*>(.*?)</script>", re.S)
FIELD_RE = re.compile(r'<div class="font-semibold">\s*(.*?):\s*</div>\s*<div>(.*?)</div>', re.S)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\d[\d\s().-]{5,}\d(?!\w)")
FIELDS = {"firma": "employer", "stillingstittel": "title", "arbeidssted": "location", "frist": "valid_through"}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACE = Pace(HOST, own=3.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[kode24] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def clean(s):
    s = re.sub(r"<(script|style|svg)\b.*?</\1>", "", s or "", flags=re.S | re.I)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<br\s*/?>|</p>|</li>|</div>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def redact(s):
    s = EMAIL_RE.sub("[e-mail withheld]", s or "")
    return PHONE_RE.sub(lambda m: "[phone withheld]" if sum(c.isdigit() for c in m.group(0)) >= 8 else m.group(0), s)


def iso(dmy):
    m = re.match(r"\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s*$", dmy or "")
    return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}" if m else (clean(dmy) or None)


def stated(body):
    m = STATED_RE.search(body or "")
    return int(m.group(1)) if m else None


def cards(body):
    out = []
    for blk in CARD_RE.findall(body or ""):
        link = LINK_RE.search(blk)
        if not link:
            continue
        slug, ident = link.groups()
        t, e, sub, loc, due = TITLE_RE.search(blk), EMP_RE.search(blk), SUB_RE.search(blk), LOC_RE.search(blk), DUE_RE.search(blk)
        locs = [clean(x) for x in re.findall(r'<span class="p-2[^"]*">(.*?)</span>\s*(?=<span class="p-2|</div>)', re.sub(r"<svg.*?</svg>", "", loc.group(1), flags=re.S), re.S)] if loc else []
        locs = [x for x in dict.fromkeys(locs) if x]   # each place is rendered twice (light / dark theme); once here
        out.append({
            "source": "kode24", "country": "NO", "ledger_id": f"kode24:{ident}", "id": ident, "url": f"{LIST}/{slug}/{ident}",
            "title": redact(clean(t.group(1))) or None if t else None, "employer": redact(clean(e.group(1))) or None if e else None,
            "employer_slug": slug, "subtitle": redact(clean(sub.group(1))) or None if sub else None,
            "locations": locs or None, "deadline_text": clean(due.group(1)).replace("Frist:", "").strip() or None if due else None,
            "new": True if ">Ny<" in blk else None,
        })
    return out


def cmd_list(a):
    code, body = request(LIST)
    if code != 200:
        die(f"{LIST}: HTTP {code}", EXIT_PARTIAL)
    site = stated(body)
    if site is None:
        die(f"{LIST}: the menu states no «Alle stillinger N» ({len(body)} characters).", EXIT_PARTIAL)
    rows = cards(body)
    seen, emitted = set(), 0
    for r in rows:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        print(json.dumps(r, ensure_ascii=False))
        emitted += 1
        if a.limit and emitted >= a.limit:
            note(f"{emitted} emitted, site states {site} — bounded by request (--limit), not compared.")
            return
    if emitted == site:
        note(f"{emitted} emitted over 1 page, site states {site} («Alle stillinger») — equal.")
    else:
        note(f"{emitted} emitted over 1 page, site states {site} («Alle stillinger») — {abs(site - emitted)} {'short' if emitted < site else 'over'}.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an ad URL of this board (https://kodejobb.no/stillinger/<employer-slug>/<uuid>).")
    slug, ident = m.groups()
    code, body = request(a.url.strip())
    if code == 404:
        die(f"{a.url}: HTTP 404 — the ad is gone.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_PARTIAL)
    ld = None
    for blob in LD_RE.findall(body):
        try:
            j = json.loads(blob)
        except ValueError:
            continue
        if isinstance(j, dict) and j.get("@type") == "JobPosting":
            ld = j
            break
    if not ld:
        die(f"{a.url}: no JobPosting on the page — gone, or not the template this file reads.", EXIT_GONE)
    org = ld.get("hiringOrganization") or {}
    addr = (ld.get("jobLocation") or {}).get("address") or {}
    r = {"source": "kode24", "country": "NO", "ledger_id": f"kode24:{ident}", "id": ident, "url": a.url.strip(), "employer_slug": slug,
         "title": redact(clean(ld.get("title") or "")) or None, "employer": redact(clean(org.get("name") or "")) or None,
         "subtitle": redact(clean(ld.get("description") or "")) or None,
         "location": clean(addr.get("addressLocality") or "") or None,
         "posted": (ld.get("datePosted") or "")[:10] or None, "valid_through": (ld.get("validThrough") or "")[:10] or None,
         "employment_type": ld.get("employmentType") or None}
    for label, value in FIELD_RE.findall(body):
        key = FIELDS.get(clean(label).lower())
        if key == "valid_through" and not r.get("valid_through"):
            r["valid_through"] = iso(value)
        elif key == "location" and not r.get("location"):
            r["location"] = clean(value) or None
    tail = body.split("Frist:", 1)[1] if "Frist:" in body else body
    prose = re.search(r'<div class="p-4 lg:p-0">(.*?)</div>\s*(?:<div class="[^"]*sticky|<footer|<aside)', tail, re.S)
    r["description"] = redact(clean(prose.group(1))) or None if prose else None
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="every open ad, one page, compared to «Alle stillinger N»")
    l.add_argument("--limit", type=int, default=0)
    l.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one ad by its public URL")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
