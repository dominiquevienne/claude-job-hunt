#!/usr/bin/env python3
"""Jobslin (`ph.jobslin.com` and its 20 sibling sub-hosts) — the Philippine board of a 21-country operator, through the listing its pages render; «a - b of N Job Vacancies» printed beside every walk; the host's `Crawl-delay: 2` honoured. Issue #299.

  jobslin.py search [--host ph] [--pages N] [--limit N]
  jobslin.py ad --url <https://ph.jobslin.com/job/<id>/<slug>>

THE ROUTE IS THE LISTING — one sub-host per country (`www.jobslin.com` is the country
chooser and has no advertisement):

  GET https://ph.jobslin.com/job-offers            -> «1 - 12 of 16,072 Job Vacancies», 12 cards, a pager ?t=16072&page=2 … (the `t` is the count carried along, not a token)
  GET https://ph.jobslin.com/job-offers?page=N     -> «13 - 24 of 16,072», the next 12
  GET https://ph.jobslin.com/job/<id>/<slug>       -> a JobPosting in JSON-LD (title, hiringOrganization, jobLocation, datePosted, validThrough, employmentType, totalJobOpenings, the description)

**`--host` is the sub-host's country code as the operator names it** (`ph` by default;
`my`, `sg`, `au`, `ke`, `gh` … appear on the hub's chooser) — the same template on every
host read so far, and every host is measured before its card claims it: this adapter was
exercised on `ph` only. The rules on `ph.jobslin.com`: the Cloudflare managed block —
`ClaudeBot` and eight others refused by name, `*` Allow: / with a Content-Signal, and
`Crawl-delay: 2` — the doctrine of 2026-09-07 (a refusal of `ClaudeBot` does not bind
`Claude-User`) opens it, and `_pace` applies the two seconds.

THE CARD carries the title, the employer, a summary, the tags (Full Time / Remote / Part
Time …, the experience asked), «City, Region», the date (DD/MM/YYYY), and the salary as
the card prints it — «₱17,000.00 / Monthly» — emitted with its amount, its currency read
from the sign, and its period, `salary_unit_stated` true only when the card prints a period.
«Premium» cards are the operator's paid placements, kept and flagged. THE AD is the
JobPosting. No contact is on either page on the day; the description is still scrubbed of
e-mail addresses, and the application («Apply») is the site's own form, never touched.

Measured 2026-09-14 00:0x UTC by the declared client: «1 - 12 of 16,072» stated, 12 a
page, 1 340 pages; `--pages` defaults to 10 (120 rows) and the note says the walk was
bounded by request; 1 340 pages at 2 s is a choice, not the default.
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

DOMAIN = "jobslin.com"
PAGE_SIZE = 12
COUNT_RE = re.compile(r"(\d[\d,]*)\s*-\s*(\d[\d,]*)\s+of\s+(\d[\d,]*)\s+Job Vacancies")
CARD_RE = re.compile(r'<a href="(/job/(\d+)/[^"]*)"\s+data-enlace-oferta="1"[^>]*>(.*?)</a>', re.S)
DETAIL_RE = re.compile(r"^https?://([a-z]{2})\.jobslin\.com/job/(\d+)/([A-Za-z0-9._-]*)/?$")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
CURRENCIES = {"₱": "PHP", "RM": "MYR", "S$": "SGD", "$": "USD", "€": "EUR", "£": "GBP", "KSh": "KES", "GH₵": "GHS", "R": "ZAR", "A$": "AUD", "NZ$": "NZD", "MX$": "MXN", "N": "NGN", "Rp": "IDR", "฿": "THB", "₫": "VND"}
_PACES = {}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobslin] {msg}", file=sys.stderr)


def host_of(cc):
    cc = (cc or "ph").strip().lower()
    if not re.fullmatch(r"[a-z]{2}", cc):
        die(f"--host {cc!r}: a two-letter sub-host as the operator names them (ph, my, sg …)")
    return f"{cc}.{DOMAIN}"


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def pace_for(host):
    if host not in _PACES:
        _PACES[host] = Pace(host, own=2.0)   # ph.jobslin.com writes Crawl-delay: 2; the longer of the two wins on every host
    return _PACES[host]


def request(url):
    gate(url)
    pace_for(urllib.parse.urlsplit(url).netloc).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</span>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t ]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def stated(body):
    m = COUNT_RE.search(htmlmod.unescape(body or ""))
    return (int(m.group(1).replace(",", "")), int(m.group(2).replace(",", "")), int(m.group(3).replace(",", ""))) if m else None


def salary(card):
    """«₱17,000.00 / Monthly» as the card prints it — amount, currency from the sign, period when printed."""
    m = re.search(r'texto_celeste"[^>]*>\s*([^<]+?)\s*</span>\s*(?:&nbsp;|\s)*/?\s*([A-Za-z]+)?', card or "")
    if not m:
        return None, None, None, False
    amount_s = htmlmod.unescape(m.group(1)).strip()
    num = re.search(r"\d[\d,]*(?:\.\d+)?", amount_s)
    amount = float(num.group(0).replace(",", "")) if num else None
    sign = amount_s[:num.start()].strip() if num else amount_s
    cur = CURRENCIES.get(sign) if sign else None
    period = {"monthly": "MONTH", "weekly": "WEEK", "daily": "DAY", "hourly": "HOUR", "yearly": "YEAR", "annually": "YEAR"}.get((m.group(2) or "").lower())
    return amount, cur, period, bool(period)


def cards(body, host):
    out = []
    for m in CARD_RE.finditer(body or ""):
        path, ident, card = m.group(1), m.group(2), m.group(3)
        title = re.search(r'class="fw-bold text-primary mb-0 font_2"[^>]*>(.*?)</', card, re.S)
        emp = re.search(r'class="text-secondary opacity-75 mb-0 small"[^>]*>(.*?)</', card, re.S)
        summ = re.search(r'class="pt-1 pb-xl-0 mb-0 mb-xl-1 text-dark fw-lighter font_4"[^>]*>(.*?)</', card, re.S)
        lines = text(card).split("\n")
        premium = lines[:1] == ["Premium"]
        # the place and the date are the spans the card's own icons label — bi-geo-alt, bi-calendar — never a guess from the text
        loc = re.search(r'bi-geo-alt[^>]*>.*?</svg>\s*<span[^>]*>(.*?)</span>', card, re.S)
        loc = text(loc.group(1)) or None if loc else None
        date = re.search(r'bi-calendar[^>]*>.*?</svg>\s*<span[^>]*>(.*?)</span>', card, re.S)
        date = text(date.group(1)) or None if date else None
        tags = [l for l in lines if l in ("Full Time", "Part Time", "Remote", "Half Time", "Internship", "Contract", "Freelance", "Temporary") or l.endswith("Experience") or re.fullmatch(r"\d+\+? years?", l)]
        amount, cur, period, unit = salary(card)
        out.append({
            "source": "jobslin", "country": host.split(".")[0].upper(), "ledger_id": f"jobslin:{host.split('.')[0]}:{ident}", "id": ident,
            "url": f"https://{host}{htmlmod.unescape(path)}",
            "title": text(title.group(1)) if title else None,
            "employer": text(emp.group(1)) if emp else None,
            "summary": MAIL_RE.sub("[e-mail withheld]", text(summ.group(1))) if summ else None,
            "tags": tags,
            "workplace": loc,
            "posted": date,                                   # DD/MM/YYYY as printed
            "salary": amount, "salary_currency": cur, "salary_period": period, "salary_unit_stated": unit,
            "premium": premium,                               # the operator's paid placement — kept, flagged
            "language": "en",
        })
    return out


def cmd_search(a):
    host = host_of(a.host)
    base = f"https://{host}/job-offers"
    out, seen, pageno, total = [], set(), 0, None
    while True:
        pageno += 1
        url = base if pageno == 1 else f"{base}?page={pageno}"
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        s = stated(body)
        rows = cards(body, host)
        if pageno == 1:
            if s is None:
                if not rows:
                    note(f"{host}: no «a - b of N Job Vacancies» and no card — the board lists nothing.")
                    return
                die(f"{url}: cards on the page and no «a - b of N Job Vacancies» — the count line changed; a walk without it is not compared.", EXIT_PARTIAL)
            total = s[2]
        elif s is None or s[0] != (pageno - 1) * PAGE_SIZE + 1:
            die(f"{url}: asked for page {pageno} (rows from {(pageno - 1) * PAGE_SIZE + 1}), the heading says {s!r} — the page did not turn.", EXIT_PARTIAL)
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
        note(f"{th(n)} emitted of the {th(total)} {host} states — {pageno} page(s) of {PAGE_SIZE} walked by request (--pages/--limit) at the host's 2 s, not a shortfall.")
    elif n == total:
        note(f"{th(n)} emitted over {pageno} page(s), {host} states {th(total)} — equal.")
    else:
        note(f"{th(n)} emitted over {pageno} page(s), {host} states {th(total)} — {th(abs(total - n))} " + ("short" if total > n else "more emitted than the site states") + ".")


def jobposting(body):
    for m in re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', body or ""):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            continue
        for e in (d.get("@graph", [d]) if isinstance(d, dict) else d):
            if isinstance(e, dict) and e.get("@type") == "JobPosting":
                return e
    return None


def cmd_ad(a):
    m = DETAIL_RE.match((a.url or "").strip())
    if not m:
        die(f"{a.url}: not a posting address — expected https://<cc>.jobslin.com/job/<id>/<slug>")
    cc, ident = m.group(1), m.group(2)
    code, body = request(a.url)
    if code in (404, 410):
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    d = jobposting(body)
    if not d:
        die(f"{a.url}: no JobPosting on the page ({len(body)} characters) — not a posting, or the site changed.", EXIT_PARTIAL)
    org = d.get("hiringOrganization") if isinstance(d.get("hiringOrganization"), dict) else {"name": d.get("hiringOrganization")}
    loc = d.get("jobLocation") if isinstance(d.get("jobLocation"), dict) else {}
    addr = loc.get("address") if isinstance(loc.get("address"), dict) else {}
    print(json.dumps({
        "source": "jobslin", "country": cc.upper(), "ledger_id": f"jobslin:{cc}:{ident}", "id": ident, "url": a.url,
        "title": d.get("title"), "employer": org.get("name"),
        "workplace": ", ".join(x for x in (addr.get("addressLocality"), addr.get("addressRegion")) if x) or None,
        "posted": d.get("datePosted"), "application_deadline": d.get("validThrough"),
        "employment_type": d.get("employmentType"), "openings": d.get("totalJobOpenings"),
        "description": MAIL_RE.sub("[e-mail withheld]", text(d.get("description") or ""))[:20000] or None,
        "language": "en",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Jobslin — one sub-host per country; the listing's «a - b of N Job Vacancies» beside every walk; the host's Crawl-delay honoured. Issue #299.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="the listing, 12 a page, 2 s apart, 10 pages unless told otherwise; --host is the sub-host's country code (ph by default)")
    s.add_argument("--host", default="ph")
    s.add_argument("--pages", type=int, default=10)
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_search)
    d = sub.add_parser("ad", help="one posting — its JobPosting")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
