#!/usr/bin/env python3
"""Prospective — a Swiss multi-employer ATS, one career center at a time: `ohws.prospective.ch/public/v1/careercenter/<id>/` fills its list by POSTing its own form (`offset`, `limit`, `lang`, the filters) back to itself, and the answer's `#jobs` holds `.job` items whose link ends in the ad's UUID — the adapter replays that POST, walks `offset` until a page brings no new UUID, and reads each ad's JobPosting on `/public/v1/jobs/<uuid>` (recognised by `shared/ats-open-check.md`); the street and the postal code never emitted. Issue #485.

  prospective.py jobs --tenant 1003036 [--lang de] [--country-code CH] [--max-pages N]     the center's positions (ceil(N/limit) requests)
  prospective.py jobs --tenant https://ohws.prospective.ch/public/v1/careercenter/1000981/?lang=de
  prospective.py ad --url https://ohws.prospective.ch/public/v1/jobs/892e45e0-1fec-4b5f-ae5f-d379d5fe0e89

WHAT IT IS. Prospective Media Services (Zürich) runs the «Online Hosting Web Service» behind the
career centers of Swiss employers — CSS, EKZ, the ZHAW, the Universitätsspital Basel, Raiffeisen,
Coop, the Swiss Army, cantons. Its signature: `ohws.prospective.ch/public/v1/careercenter/<id>/`
(the list) and `ohws.prospective.ch/public/v1/jobs/<uuid>` (an ad — which `ats-open-check.md`
already reads for its `validThrough`). **One adapter covers every employer that uses it; the user
names the center** by its number or by any address on the host that carries it. The centers'
links point at the tenant's own domain (`jobs.ekz.ch/offene-stellen/<slug>/<uuid>`, `jobs.css.ch/
…`); the adapter keys on the UUID and reads the ad on `ohws.prospective.ch` — the tenant's host is
never sent to.

THE RULES. One host, one file (5 592 B): `*` — `Disallow:` empty — and a list of `Allow:` lines for
share images on the vendor's S3; no Crawl-delay, 2 s is ours. The guard is taken on the exact path.

THE LIST. GET `/public/v1/careercenter/<id>/` (200; 42–56 KB, or 664 B for a center still on the
«project template») renders the tenant's own template around a `#careercenter-form` (POST to
itself: `offset`, `limit` — 12 by default —, `lang`, `query`, `place`, `radius`, `viewport`, the
`filter_NN` selects) and fills `#jobListAndPagination` by that POST on load (jQuery, 500 ms). The
POST's answer holds `#jobs` with `.job` items — a link whose `href` ends in `/<uuid>`, a `.job-title`
(or the link's `title`), a `.job-city` / `.place-of-work` — and a pager (`sendPagination(<offset>)`);
some templates print the total (`.jobs-total .total`: CSS «42 Jobs»), most do not. **A `limit` of
100 is honoured** (EKZ: 64 items in one answer). The walk adds `limit` to `offset` until an answer
brings no new UUID; the stated total, when printed, is compared to the emitted count.

THE AD. `/public/v1/jobs/<uuid>` (200) carries one JobPosting — title, description, datePosted,
validThrough (every ad), employmentType, hiringOrganization (the real employer), jobLocation with
streetAddress and postalCode; a 404 titled «Fehlermeldung» is «not listed».

**WITHHELD:** `streetAddress` and `postalCode`; e-mail addresses and telephones in the texts replaced
(«[e-mail withheld]» / «[telephone withheld]»), dates left alone; `contacts_withheld` on every
record; the application (`/public/v1/application/<uuid>`) never touched. `--country-code` STAMPS on
the list (it states no country) and says so; on the ad it filters on the posting's own country.

Measured 2026-09-21 07:50–07:52 UTC by the declared client, the guard on the exact path: CSS
`1000981` (GET 42 331 B ×2; the POST 44 923 B, «42 Jobs» stated, 12 a page), EKZ `1003036` (GET
55 946 B ×2; the POST 55 940 B with 12 items and a pager to offset 60, `limit=100` 99 146 B with 64
items — the whole board), ZHAW `1002929` (664 B — «Career Center project template», no form: not a
board today, exit 6 with that sentence).
"""

import argparse
import html as htmlmod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

import _ldjson
from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "ohws.prospective.ch"
PAGE_SIZE = 100
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")   # «+41 58 277 11 11», «058 277 11 11»: 8+ digits with separators
DATE_RE = re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b")                       # «per 01.01.2027» is a date, not a telephone — it stays
UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
TENANT_RE = re.compile(r"^\d{3,8}$")
JOB_RE = re.compile(r'<div class="job(?:\s[^"]*)?">(.*?)(?=<div class="job(?:\s[^"]*)?">|<div class="paging|<div id="jobs-pagination|</div>\s*</div>\s*<div class="paging|<button|</section>|</body>)', re.S)
LINK_RE = re.compile(r'<a\b([^>]*)href="([^"]*/(' + UUID + r'))"([^>]*)>(.*?)</a>', re.S)
TOTAL_RE = re.compile(r'class="(?:[^"]*\s)?total(?:\s[^"]*)?"[^>]*>\s*(\d[\d\s \']*)\s*<', re.S)
TITLE_RE = re.compile(r'class="(?:[^"]*\s)?job-title(?:\s[^"]*)?"[^>]*>(.*?)</', re.S)
PLACE_RE = re.compile(r'class="(?:[^"]*\s)?(?:job-city|place-of-work|job-location|job-place)(?:\s[^"]*)?"[^>]*>(.*?)</', re.S)
FORM_RE = re.compile(r'<form[^>]*id="careercenter-form"')
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[prospective] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def tenant_of(arg):
    """`1003036`, or any ohws.prospective.ch address carrying `/careercenter/<id>/` → the id."""
    s = arg.strip()
    if TENANT_RE.match(s):
        return s
    parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
    m = re.match(r"^/public/v1/careercenter/(\d{3,8})(?:/|$)", parts.path)
    if parts.netloc.lower() != HOST or not m:
        die(f"{arg}: a tenant is its career center number (1003036) or an address https://{HOST}/public/v1/careercenter/<id>/")
    return m.group(1)


def request(url, data=None, accept="text/html,application/xhtml+xml,*/*;q=0.8"):
    """One GET, or one POST of the page's own form, under the declared identity — to the one host."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    headers = {"User-Agent": UA, "Accept": accept}
    if data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(wire_url(url), data=data, headers=headers)
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
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", markup or "")
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span)\b[^>]*>", "", t)   # inline tags leave no space behind
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def when(s):
    s = (s or "").strip()
    return s[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", s) else (s or None)


def items_of(markup):
    """The answer's `.job` items → [(uuid, fields)]: the link's UUID, the title, the place — whatever the tenant's template shows."""
    out = []
    for body in JOB_RE.findall(markup or ""):
        lk = LINK_RE.search(body)
        if not lk:
            continue
        attrs = lk.group(1) + lk.group(4)
        tm = re.search(r'\btitle="([^"]*)"', attrs)
        t = TITLE_RE.search(body)
        title = text(t.group(1)) if t else (htmlmod.unescape(tm.group(1)).strip() if tm else text(lk.group(5)))
        p = PLACE_RE.search(body)
        out.append((lk.group(3), {"title": title or None, "place": text(p.group(1)) if p else None, "employer_url": htmlmod.unescape(lk.group(2))}))
    return out


def stated_of(markup):
    m = TOTAL_RE.search(markup or "")
    return int(re.sub(r"\D", "", m.group(1))) if m else None


def record(uuid, f, tenant, stamp):
    return {
        "source": "prospective", "tenant": tenant, "country": stamp,
        "ledger_id": f"prospective:{uuid}", "id": uuid,
        "url": f"https://{HOST}/public/v1/jobs/{uuid}", "employer_url": f.get("employer_url"),
        "title": f.get("title"), "place": f.get("place"),
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    tenant = tenant_of(a.tenant)
    lang = (a.lang or "de").strip().lower()
    if not re.match(r"^[a-z]{2}$", lang):
        die(f"--lang {a.lang}: two letters (de, fr, it, en)")
    stamp = a.country_code.upper() if a.country_code else None
    url = f"https://{HOST}/public/v1/careercenter/{tenant}/"
    code, page = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — no such career center", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    if not FORM_RE.search(page):
        if "Career Center project template" in page:
            die(f"{url}: 200 — «Career Center project template», no form: the center is not built today; not an empty board", EXIT_PARTIAL)
        die(f"{url}: 200 without `#careercenter-form` — not a Prospective career center, or the page changed", EXIT_PARTIAL)
    rows, seen, offset, pages, stated = [], set(), 0, 0, None
    while True:
        pages += 1
        data = urllib.parse.urlencode({"offset": offset, "limit": PAGE_SIZE, "lang": lang, "query": "", "place": "", "radius": "", "viewport": ""}).encode()
        code, body = request(url, data=data)
        if code != 200:
            die(f"POST {url} offset={offset}: HTTP {code}", EXIT_PARTIAL)
        if stated is None:
            stated = stated_of(body)
        found = items_of(body)
        new = [(u, f) for u, f in found if u not in seen]
        if pages > 1 and found and not new:
            break                                   # the same items again: the pager's end
        for u, f in new:
            seen.add(u)
            rows.append(record(u, f, tenant, stamp))
        if not found or len(found) < PAGE_SIZE or (a.max_pages and pages >= a.max_pages):
            break
        offset += PAGE_SIZE
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if stated is not None:
        note(f"{th(len(rows))} emitted, the page states {th(stated)} for center {tenant}" + (f" — {th(stated - len(rows))} short" if len(rows) < stated else "") + f" ({pages} answer(s) of {PAGE_SIZE}).")
    elif not rows:
        note(f"center {tenant}: 0 positions — the list answered none and states no count (200); not an error.")
    else:
        note(f"{th(len(rows))} emitted for center {tenant} over {pages} answer(s) of {PAGE_SIZE} — no count is stated, the list is the board.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the list states no country.")
    note("the ad's street and postal code never emitted; texts scrubbed; the tenant's own domain never sent to.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = re.match(r"^/public/v1/jobs/(" + UUID + r")/?$", parts.path)
    if parts.scheme != "https" or parts.netloc.lower() != HOST or not m:
        die(f"{a.url}: not a Prospective ad address (https://{HOST}/public/v1/jobs/<uuid>)")
    uuid = m.group(1)
    url = f"https://{HOST}/public/v1/jobs/{uuid}"                    # any `track=` token dropped
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — not listed (unknown or withdrawn)", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    posts = _ldjson.postings(body)
    if not posts:
        die(f"{url}: 200 without a JobPosting — the page changed", EXIT_PARTIAL)
    p = posts[0]
    org = p.get("hiringOrganization") if isinstance(p.get("hiringOrganization"), dict) else {}
    jl = p.get("jobLocation")
    jl = jl[0] if isinstance(jl, list) and jl else (jl if isinstance(jl, dict) else {})
    addr = jl.get("address") if isinstance(jl.get("address"), dict) else {}
    cc = (addr.get("addressCountry") or "").strip()
    et = p.get("employmentType")
    row = {
        "source": "prospective", "tenant": None,
        "country": cc.upper() if len(cc) == 2 else None, "country_name": cc if cc and len(cc) != 2 else None,
        "ledger_id": f"prospective:{uuid}", "id": uuid, "url": url,
        "title": scrub(text(p.get("title") or "")), "company": org.get("name") or None,
        "place": addr.get("addressLocality") or None, "region": addr.get("addressRegion") or None,
        "employment_type": et if isinstance(et, list) else ([et] if et else None),
        "published": when(p.get("datePosted")), "expires": when(p.get("validThrough")),
        "description": scrub(text(p.get("description") or "")),
        "contacts_withheld": True,
    }
    if a.country_code and row["country"] and row["country"] != a.country_code.upper():
        note(f"{url}: the ad is in {row['country']}, not {a.country_code.upper()} — 0 emitted.")
        return
    print(json.dumps(row, ensure_ascii=False))
    note(f"{url}: read from the page's JobPosting; the street and the postal code never emitted; text scrubbed.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Prospective — one career center's list by the POST its own form makes, walked by offset; the ad's JobPosting with its street withheld. Issue #485.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="one career center's whole board")
    j.add_argument("--tenant", required=True, help="the career center number (1003036) or its address on ohws.prospective.ch")
    j.add_argument("--lang", default="de", help="the form's lang (de, fr, it, en) — default de")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the list states none)")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0, help="stop after N answers of 100 (0 = to the end)")
    j.set_defaults(fn=cmd_jobs)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.add_argument("--country-code", dest="country_code", metavar="ISO2", help="emit only if the ad's own country is this one")
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
