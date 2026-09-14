#!/usr/bin/env python3
"""Prace.cz (`www.prace.cz`, Alma Career) — the second Czech generalist, through the job cards its listing renders; «Našli jsme N nabídek» printed beside every walk; the contact block on every ad never leaves. Issue #353.

  pracecz.py search [--pages N] [--limit N]
  pracecz.py ad --url <https://www.prace.cz/nabidka/<uuid>/>

THE ROUTE IS THE LISTING — `/nabidky/`, served from page 1 with its cards (the rules refuse
`/search/` and `/hledat/`, the query forms; `/nabidky/` is the site's own «Nabídky práce» page):

  GET /nabidky/              -> «Našli jsme 19 005 nabídek», 40 <article class="JobCard…"> cards, a pager ?page=2 …
  GET /nabidky/?page=N       -> the next 40
  GET /nabidka/<uuid>/       -> one ad: a JobPosting in JSON-LD (title, hiringOrganization, jobLocation, datePosted, validThrough, employmentType, baseSalary with its unit), the text, the benefits — and a «Kontaktní údaje» block

THE CARD names its fields itself, with hidden labels: «Lokalita:», «Název firmy:», «Typ
úvazku:», «Plat:» («35 000 – 45 000 Kč/měsíc» — a range in CZK with its period, so
`salary_unit_stated` is true when «/měsíc» or «/hod» is printed). **Its link is one of three
shapes** — `/nabidka/<uuid>/`, `/firma/<slug>/nabidka/<uuid>/`, or an employer's own host with
`originJobAdUuid=<uuid>` — and the UUID is the id in all three; the address emitted is the site's
`/nabidka/<uuid>/`. **For an employer-hosted ad (13 of 40 on the first page: `o2.jobs.cz`,
`albert.jobs.cz`, `kaufland.jobs.cz` …) that address redirects to the employer's own career
host, a client-rendered page with no JobPosting — the card says `hosted_by_employer`, and `ad`
stops at the redirect (exit 6) rather than read another host.** The `?rps=` token is stripped. THE AD is its JobPosting: `baseSalary.value` is a `QuantitativeValue` with `unitText`
(MONTH), so the unit is the page's own. **The «Kontaktní údaje» block (a company, an address,
sometimes a person and a telephone) is not read, and the description is scrubbed of e-mail
addresses and Czech telephone numbers.** The «Odpovědět» application is the site's own form.

Not the same build as `jobs.cz` (`jobscz.py`): a different template (CSS-module cards, UUID
addresses, the first page served) on the same group's second board — its own script, its own
measurement. The rules: `*` refuses `/auth/`, `/search/`, `/hledat/`, `/muj/`, `/asmt/` and two
form paths — nothing this adapter touches; a sitemap index on CloudFront that holds facets and no
ads (2026-09-01); no Crawl-delay — 2 s is ours.

Measured 2026-09-14 00:1x UTC by the declared client: «19 005» stated, 40 cards on pages 1 and
2 with no overlap; one ad read. **`--pages` defaults to 10** (400 rows) and the note says the walk
was bounded by request.
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

HOST = "www.prace.cz"
BASE = f"https://{HOST}"
LIST = f"{BASE}/nabidky/"
PAGE_SIZE = 40
UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
COUNT_RE = re.compile(r"Našli jsme\s+([\d\s  ]+)\s*nabíd")
CARD_RE = re.compile(r'<article[^>]*class="[^"]*JobCard[^"]*"[^>]*>(.*?)</article>', re.S)
ID_RE = re.compile(r"nabidka/(%s)|originJobAdUuid=(%s)" % (UUID, UUID))
DETAIL_RE = re.compile(r"^https?://www\.prace\.cz/(?:firma/[^/]+/)?nabidka/(%s)/?(?:\?.*)?$" % UUID)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<!\d)(?:\+420[\s ]?)?\d{3}[\s ]?\d{3}[\s ]?\d{3}(?!\d)")
SALARY_RE = re.compile(r"^\s*(\d[\d\s  ]*)\s*(?:[–-]\s*(\d[\d\s  ]*))?\s*Kč(?:\s*/\s*(měsíc|hod\w*|rok|den|týden))?")
PERIODS = {"měsíc": "MONTH", "hod": "HOUR", "rok": "YEAR", "den": "DAY", "týden": "WEEK"}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[pracecz] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # no Crawl-delay in the rules; 2 s is ours


def request(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "cs"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, "", url
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"<!--.*?-->", "", markup, flags=re.S)
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</dd>|</dt>|</tr>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t  ‍]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def num(s):
    return int(re.sub(r"[\s  ]", "", s))


def scrub(s):
    if not s:
        return s
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s)


def stated(body):
    m = COUNT_RE.search(text(body))
    return num(m.group(1)) if m else None


def salary(s):
    """«35 000 – 45 000 Kč/měsíc» → (min, max, period); a figure without a printed period has none."""
    m = SALARY_RE.match(s or "")
    if not m:
        return None, None, None
    lo = num(m.group(1))
    hi = num(m.group(2)) if m.group(2) else lo
    p = m.group(3)
    period = next((v for k, v in PERIODS.items() if p and p.startswith(k)), None) if p else None
    return lo, hi, period


def labelled(card):
    """The card's own hidden labels — «Lokalita:», «Název firmy:», «Typ úvazku:», «Plat:» — and the text beside each."""
    out = {}
    for m in re.finditer(r'<span class="accessibility-hidden">(.*?)</span>\s*(?:<span[^>]*>)?(.*?)(?=<span class="accessibility-hidden">|</li>)', card, re.S):
        label = text(m.group(1)).rstrip(":").strip()
        out[label] = text(m.group(2)) or None
    return out


def cards(body):
    out = []
    for m in CARD_RE.finditer(body or ""):
        c = m.group(1)
        idm = ID_RE.search(htmlmod.unescape(c))
        if not idm:
            continue
        ident = idm.group(1) or idm.group(2)
        ext = re.search(r'href="https?://((?!www\.prace\.cz)[^"/]+)[^"]*originJobAdUuid=', c)   # the employer's own career host, when the card links out
        title = re.search(r'data-testid="job-card-title"[^>]*>\s*<a[^>]*>(.*?)</a>', c, re.S)
        f = labelled(c)
        smin, smax, period = salary(f.get("Plat") or "")
        out.append({
            "source": "pracecz", "country": "CZ", "ledger_id": f"pracecz:{ident}", "id": ident,
            "url": f"{BASE}/nabidka/{ident}/",                           # the site's own address for every card, the ?rps= token dropped
            "hosted_by_employer": htmlmod.unescape(ext.group(1)) if ext else None,   # «o2.jobs.cz» … — the site's address redirects there, and `ad` will not follow
            "title": text(title.group(1)) if title else None,
            "employer": f.get("Název firmy"),
            "workplace": f.get("Lokalita"),                              # as the card prints it — «Praha-Horní Počernice», or a list of towns
            "employment": f.get("Typ úvazku"),
            "salary_text": f.get("Plat"),
            "salary_min": smin, "salary_max": smax, "salary_currency": "CZK" if smin is not None else None,
            "salary_period": period, "salary_unit_stated": bool(period),
            "language": "cs",
        })
    return out


def cmd_search(a):
    out, seen, total, pageno = [], set(), None, 0
    while True:
        pageno += 1
        url = LIST if pageno == 1 else f"{LIST}?page={pageno}"
        code, body, _ = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        s = stated(body)
        rows = cards(body)
        if pageno == 1:
            if s is None:
                if not rows:
                    note("no «Našli jsme N nabídek» and no card — the site lists nothing.")
                    return
                die(f"{url}: cards on the page and no «Našli jsme N nabídek» — the count line changed; a walk without it is not compared.", EXIT_PARTIAL)
            total = s
        new = 0
        for r in rows:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            out.append(r)
            new += 1
        if new == 0 or len(out) >= total:
            break
        if a.pages and pageno >= a.pages:
            break
        if a.limit and len(out) >= a.limit:
            break
    emitted = out[:a.limit] if a.limit else out
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    bounded = (a.pages and pageno >= a.pages and total > pageno * PAGE_SIZE) or (a.limit and a.limit < total)
    if bounded:
        note(f"{th(n)} emitted of the {th(total)} the site states — {pageno} page(s) of {PAGE_SIZE} walked by request (--pages/--limit), not a shortfall.")
    elif n == total:
        note(f"{th(n)} emitted over {pageno} page(s), site states {th(total)} — equal.")
    else:
        note(f"{th(n)} emitted over {pageno} page(s), site states {th(total)} — {th(abs(total - n))} " + ("short" if total > n else "more emitted than the site states") + ".")


def jobposting(body):
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
        die(f"{a.url}: not an ad address — expected {BASE}/nabidka/<uuid>/")
    ident = m.group(1)
    code, body, final = request(f"{BASE}/nabidka/{ident}/")
    if code in (404, 410):
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    fhost = urllib.parse.urlsplit(final or "").netloc
    if fhost and fhost != HOST:
        # the site sends employer-hosted ads to the employer's own career site (o2.jobs.cz/detail-pozice?…) — another host, a client-rendered page: not this board's, not read
        die(f"{a.url}: the site redirected to {fhost} — the employer's own career site, not a page of this board; not read (the card's `hosted_by_employer` names it).", EXIT_PARTIAL)
    d = jobposting(body)
    if not d:
        die(f"{a.url}: no JobPosting on the page ({len(body)} characters) — not an ad, or the site changed.", EXIT_PARTIAL)
    org = d.get("hiringOrganization") if isinstance(d.get("hiringOrganization"), dict) else {"name": d.get("hiringOrganization")}
    loc = d.get("jobLocation") if isinstance(d.get("jobLocation"), dict) else {}
    addr = loc.get("address") if isinstance(loc.get("address"), dict) else {}
    sal = d.get("baseSalary") if isinstance(d.get("baseSalary"), dict) else {}
    val = sal.get("value") if isinstance(sal.get("value"), dict) else {}
    et = d.get("employmentType")
    benefits = [text(x) for x in re.findall(r'data-testid="benefit-item-\d+"[^>]*>(.*?)</', body, re.S)]
    # the «Kontaktní údaje» block — a company, an address, sometimes a person and a telephone — is never read
    print(json.dumps({
        "source": "pracecz", "country": "CZ", "ledger_id": f"pracecz:{ident}", "id": ident, "url": f"{BASE}/nabidka/{ident}/",
        "title": d.get("title"), "employer": org.get("name"),
        "workplace": ", ".join(x for x in (addr.get("addressLocality"), addr.get("postalCode")) if x) or None,   # locality and postal code — the street stays with the employer's block
        "posted": d.get("datePosted"), "application_deadline": d.get("validThrough"),
        "employment_type": ", ".join(et) if isinstance(et, list) else et,
        "salary_min": val.get("minValue"), "salary_max": val.get("maxValue"), "salary_currency": sal.get("currency") if val else None,
        "salary_period": val.get("unitText"), "salary_unit_stated": bool(val.get("unitText")),
        "benefits": [b for b in benefits if b],
        "description": scrub(text(d.get("description") or ""))[:20000] or None,
        "contacts_withheld": True,
        "language": "cs",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Prace.cz — the job cards its listing renders; «Našli jsme N nabídek» beside every walk; the contact block never leaves. Issue #353.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="the listing, 40 a page, 2 s apart, 10 pages unless told otherwise")
    s.add_argument("--pages", type=int, default=10)
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_search)
    d = sub.add_parser("ad", help="one ad — its JobPosting, the benefits, the text; the contact block withheld")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
