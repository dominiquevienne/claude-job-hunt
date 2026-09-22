#!/usr/bin/env python3
"""ACBAR Jobs (`www.acbar.org/en/jobs`, Afghanistan): the Agency Coordinating Body for Afghan Relief and Development publishes the NGO and UN posts — the first Afghan job portal, and the one `jobs.af` came out of. Issue #641.

  acbar.py jobs [--country-code AF] [--max-pages N]              the list (20 a page, 14 pages on 2026-09-22)
  acbar.py ad --url https://www.acbar.org/en/jobs/details/<id>/<slug>    one advert, its text and what is NOT carried

WHAT IT IS. ACBAR is the coordination body of the NGOs working in Afghanistan; its board carries the
posts of the agencies (IOM, UNOPS, Islamic Relief, DACAAR), of banks and of private employers.
**For a country whose other routes are thin — one board behind a JavaScript shell, one refusing at
403, one with a broken TLS chain — this is the live one.**

THE RULES. `www.acbar.org` answers its rules file and allows both paths: open, `certain: True`, no
Crawl-delay; 2 s is ours. The guard is taken on the exact path.

THE LIST. `/en/jobs` (200; 84 972 B) states its own count — **«268 jobs found»** — and carries 20
`div.job-card` a page, each with the advert's address (`/en/jobs/details/<id>/<slug>`), its title,
the employer, the contract type, the province, how long ago it was posted (**relative — «34 minutes
ago» — and kept as the site writes it**, because a relative age is not a date) and the closing date.
The pager is `?page=N`, read from the page's own links. The walk stops when the emitted count
reaches the stated total, on a page with no card, or on a page repeating the one before (6).

**The key is the site's own numeric id**, never the slug: the titles are often Dari or Pashto
(«teller به نمایندگی های ولایت پکتیکا»), and a slug folded to ASCII letters is empty.

THE ADVERT. `ad` reads one page: the four blocks the site writes («About the Company», «Job
Summary», «Job Requirements», «Submission Guideline») and its ten information rows.

**WITHHELD, AND NAMED — the advert carries personal criteria.** `Gender` («Male») and `Nationality`
(«Afghan») are read **so they can be dropped by name**: the advert is served, the criterion is not
carried (#183, as Bhutan's `gender` and Brunei's age range). E-mail addresses and telephone numbers
anywhere in the text go the same way — the submission guideline is written around an address to
write to. `withheld_fields` names each one, on every record, so a silence is never read as an
absence.

`--country-code` STAMPS (the list states no country — every post is Afghanistan's by ACBAR's own
scope, and a stamp is still the user's) and the run says so.

Measured 2026-09-22 09:2x–09:4x UTC by the declared client, the guard on the exact path: `/en/jobs`
200 (84 972 B, md5 6ae74824df7a), **«268 jobs found» stated, 20 cards on page 1, a pager to page
14**; one advert read at `/en/jobs/details/145755/haul-truck-operator` (200, 96 600 B) — ten
information rows, four blocks, `Gender: Male` and `Nationality: Afghan` among them.
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

HOST = "www.acbar.org"
LIST = f"https://{HOST}/en/jobs"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\(?\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")
STRIP_RE = re.compile(r"(?s)<style.*?</style>|<script.*?</script>")
STATED_RE = re.compile(r'jobs-toolbar__count"[^>]*>\s*([\d,]+)\s*jobs found', re.I)
CARD_RE = re.compile(r'<div class="job-card">(.*?)(?=<div class="job-card">|<ul class="pagination"|\Z)', re.S)
TITLE_RE = re.compile(r'<a href="([^"]+)"[^>]*class="job-card__title"[^>]*>(.*?)</a>', re.S)
COMPANY_RE = re.compile(r'<div class="job-card__company[^"]*"[^>]*>(.*?)(?:<span class="job-dot">|</div>)', re.S)
PILL_RE = re.compile(r'<span class="job-pill"[^>]*>(.*?)</span>', re.S)
DETAILS_RE = re.compile(r"/en/jobs/details/(\d+)/")
INFO_RE = re.compile(r'acbar-jd__info-term"[^>]*>(.*?)</\w+>\s*<\w+ class="acbar-jd__info-desc"[^>]*>(.*?)</\w+>', re.S)
# the four blocks the site writes; the LAST one ends on the e-mail paragraph, not on `</article>`,
# and matching the tidy shape alone lost exactly the block that carries the address to write to
CARD_TITLE_RE = re.compile(r'acbar-jd__card-title">(.*?)</h2>.*?<div class="acbar-jd__rich[^"]*">(.*?)</div>\s*(?=<p class="acbar-jd__email"|</article>|<article)', re.S)
EMAIL_BLOCK_RE = re.compile(r'<p class="acbar-jd__email">(.*?)</p>', re.S)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
# the criteria the advert states about a PERSON: read so they can be dropped BY NAME (#183)
CRITERIA = {"gender": "gender", "nationality": "nationality", "age": "age"}
FIELDS = {"type": "contract_type", "location": "location", "category": "category",
          "published": "published", "salary": "salary", "contract duration": "contract_duration",
          "vacancy number": "vacancy_number", "no of job": "openings", "years of experience": "experience",
          "education": "education", "close date": "closing_date", "closing date": "closing_date"}
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[acbar] {msg}", file=sys.stderr)


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
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>|</tr>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    """Contacts out, and the record says which kinds were there."""
    if not s:
        return None, []
    took = []
    if MAIL_RE.search(s):
        took.append("email")
        s = MAIL_RE.sub("[e-mail withheld]", s)
    out = PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s)
    if out != s:
        took.append("telephone")
    return (out.strip() or None), took


def stated(markup):
    m = STATED_RE.search(markup or "")
    return int(m.group(1).replace(",", "")) if m else None


def cards_of(markup):
    """The list page → [(id, fields)]; the pills are the site's own, in its own order."""
    out = []
    for block in CARD_RE.findall(STRIP_RE.sub("", markup or "")):
        t = TITLE_RE.search(block)
        if not t:
            continue
        url = htmlmod.unescape(t.group(1))
        ident = DETAILS_RE.search(url)
        if not ident:
            continue
        company = COMPANY_RE.search(block)
        pills = [text(p) for p in PILL_RE.findall(block)]
        pills = [p for p in pills if p]
        closing = next((p for p in pills if re.match(r"^\d{4}-\d{2}-\d{2}$", p)), None)
        posted = next((p for p in pills if re.search(r"\bago\b", p)), None)
        rest = [p for p in pills if p not in (closing, posted)]
        out.append((ident.group(1), {
            "url": url, "title": text(t.group(2)),
            "employer": text(company.group(1)) if company else None,
            "contract_type": rest[0] if rest else None,
            "location": rest[1] if len(rest) > 1 else None,
            "posted_relative": posted, "closing_date": closing,
        }))
    return out


def record(ident, f, stamp):
    title, took_t = scrub(f.get("title"))
    employer, took_e = scrub(f.get("employer"))
    return {
        "source": "acbar", "country": stamp,
        "ledger_id": f"acbar:{ident}", "id": ident,
        "title": title, "employer": employer,
        "contract_type": f.get("contract_type"), "location": f.get("location"),
        "posted_relative": f.get("posted_relative"),    # «34 minutes ago» as the site writes it
        "closing_date": f.get("closing_date"),
        "url": f.get("url"),
        "withheld_fields": sorted(set(took_t + took_e)),
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    rows, seen, page, said, ended = [], set(), 1, None, None
    while True:
        url = LIST if page == 1 else f"{LIST}?page={page}"
        code, body = request(url)
        if code == 404:
            die(f"{url}: HTTP 404 — the list is gone", EXIT_GONE)
        if code != 200:
            die(f"{url}: HTTP {code} — the walk ended at {th(len(seen))}", EXIT_PARTIAL)
        if page == 1:
            said = stated(body)
        found = cards_of(body)
        if not found:
            if page == 1:
                die(f"{url}: 200 without a single job card — the page changed; not an empty board", EXIT_PARTIAL)
            ended = f"page {page} carried no card"
            page -= 1
            break
        keys = {i for i, _f in found}
        if page > 1 and keys <= seen:
            die(f"page {page} repeats the cards of the page before — the walk ended at {th(len(seen))}", EXIT_PARTIAL)
        for ident, f in found:
            if ident in seen:
                continue
            seen.add(ident)
            rows.append(record(ident, f, stamp))
        if said is not None and len(seen) >= said:
            ended = f"the {th(said)} the board states were read"
            break
        if a.max_pages and page >= a.max_pages:
            ended = f"stopped by --max-pages at page {page}"
            break
        page += 1
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if said is None:
        note(f"{th(len(rows))} emitted over {th(page)} page(s); **the board stated no count this time** — it usually prints «N jobs found», and the run says so rather than claiming one. {ended or ''}")
    elif said != len(seen):
        note(f"{th(len(seen))} read over {th(page)} page(s), the board states {th(said)} — {th(abs(said - len(seen)))} {'short' if said > len(seen) else 'more'}; {ended}.")
    else:
        note(f"{th(len(seen))} read over {th(page)} page(s), and the board states {th(said)} — they agree; {ended}.")
    note("the key is the board's own numeric id, never the slug: the titles are often Dari or Pashto, and an ASCII fold of them is empty.")
    note("the posted age is relative («34 minutes ago») and is kept as the board writes it — a relative age is not a date.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the list states no country.")


def cmd_ad(a):
    url = a.url.strip()
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST or not DETAILS_RE.search(parts.path) or parts.query:
        die(f"--url {url}: a https://{HOST}/en/jobs/details/<id>/<slug> advert, without a query string")
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the advert is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    clean = STRIP_RE.sub("", body)
    h1 = H1_RE.search(clean)
    rows = INFO_RE.findall(clean)
    blocks = CARD_TITLE_RE.findall(clean)
    if not h1 or not rows:
        die(f"{url}: 200 without the advert's title or its information rows — the page changed", EXIT_PARTIAL)
    out, withheld, took = {}, [], []
    for term, desc in rows:
        key = (text(term) or "").strip().lower().rstrip(":")
        value = text(desc)
        if key in CRITERIA:
            withheld.append(CRITERIA[key])      # READ so it can be dropped BY NAME — never emitted
            continue
        if key in FIELDS:
            out[FIELDS[key]] = value
    body_out = {}
    for title, rich in blocks:
        key = re.sub(r"[^a-z]+", "_", (text(title) or "").lower()).strip("_")
        value, t = scrub(text(rich))
        took += t
        body_out[key] = value
    # the address to write to sits OUTSIDE the blocks, in its own paragraph: read so it is scrubbed
    for block in EMAIL_BLOCK_RE.findall(clean):
        _v, t = scrub(text(block))
        took += t
    title, t = scrub(text(h1.group(1)))
    took += t
    r = {
        "source": "acbar", "country": a.country_code.upper() if a.country_code else None,
        "ledger_id": f"acbar:{DETAILS_RE.search(parts.path).group(1)}",
        "id": DETAILS_RE.search(parts.path).group(1),
        "title": title, "url": url,
    }
    r.update(out)
    r.update(body_out)
    r["withheld_fields"] = sorted(set(withheld + took))
    r["contacts_withheld"] = True
    print(json.dumps(r, ensure_ascii=False))
    if withheld:
        note(f"criteria the advert states about a person and this record does NOT carry: {', '.join(sorted(set(withheld)))} — #183, named so a silence is not read as an absence.")
    else:
        note("this advert states no personal criterion; `withheld_fields` says only what was scrubbed.")


def main(argv=None):
    p = argparse.ArgumentParser(description="ACBAR Jobs (Afghanistan) — the coordination body's board, walked against the count it states. Issue #641.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the list (20 a page)")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the list states none)")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0, help="stop after N pages (0 = until the stated count is read)")
    j.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert, its blocks, and what it states about a person and we do not carry")
    d.add_argument("--url", required=True, help="the advert's own address")
    d.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on the record")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
