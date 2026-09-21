#!/usr/bin/env python3
"""BLMIS — Bhutan Labour Market Information System, the public employment service of the Ministry of Industry, Commerce and Employment: its jobseeker page ships every vacancy in the page itself, as the Livewire component's `wire:initial-data` (three groupings of one board — by company, by category, by location — 471 distinct on 2026-09-21); no POST is replayed, nothing is composed. The ministry's internal audit fields and the personal criteria a vacancy may carry never leave. Issue #680.

  blmis.py jobs [--country-code BT] [--dzongkhag Thimphu]     the whole board (1 request)
  blmis.py jobs --json-only                                   the records, no note

WHAT IT IS. `www.blmis.gov.bt` is Bhutan's labour-market information system: employers file their
vacancies with the ministry, jobseekers register, and `/jobseeker_page/mispage` is the public
side. **It is the country's official route to work** — Bhutan's other named boards are a civil
service system and two community sites (#681–#683).

THE RULES. `www.blmis.gov.bt/robots.txt` read and open on `/`, on `/jobseeker_page/mispage` and
on `/livewire/…`, no Crawl-delay; 2 s is ours. The guard is taken on the exact path.

THE LIST, IN THE PAGE. `/jobseeker_page/mispage` (200; 2 331 252 B) renders a Livewire component
(`frontpage.jobseeker`) whose `wire:initial-data` — HTML-escaped JSON in the markup — carries
`serverMemo.data` with **three lists of vacancies**: `job_by_company` (401), `job_by_categories`
(176), `job_by_location` (17) — **three groupings of one board**, their union **471 distinct
`application_no`** on 2026-09-21. The markup itself shows no vacancy (the component renders them
after boot), and **the page states no total anywhere**: the union is the board, and the run
prints its size. The Livewire POST route (`/livewire/message/<component>`) exists for the site's
own filtering and **is not replayed** — everything the list holds is already in the page.

Each vacancy: `application_no` (the key), `designation` (the title), `business_name` (the
employer as the ministry registered it), `job_category`, `qualification`, `field_of_study`,
`dzongkhag_name` and `gewog_name` and `placement` (district, block, place as written),
`starting_salary` (Ngultrum a month, `"15000.00"`), `slot` (posts on this vacancy),
`employment_type` (Regular 398 · Contract 65 · Training and Employment 5 · Intern 2 ·
Casual/Freelance 1), `last_date_registration` (the deadline — some reach 2049), `job_description`,
`remarks`, and the ministry's own bookkeeping.

**WITHHELD.** The ministry's **internal audit fields** — `created_by`, `updated_by`, `edited_by`,
`deleted_by`, `action_remarks`, `is_deleted`, `is_completed` — are user ids and case notes of the
people who keyed the record in: never emitted. The vacancy's **`gender`** field is a personal
criterion: null on all 471 today, and **withheld by name when a record carries one** (#183, as
Brunei's age range is — the advert is served, the criterion is not carried), the record saying
which fields it withheld. E-mail addresses and telephone numbers in the description and the
remarks (23 of 471 carry one) are replaced by «[e-mail withheld]» / «[telephone withheld]»;
`contacts_withheld` on every record. The jobseeker area (a login) is never touched.

`--country-code` STAMPS (the board is Bhutan's and states no country) and the run says so;
`--dzongkhag` keeps one district, matched as the page writes it.

Measured 2026-09-21 13:25–13:26 UTC by the declared client, the guard on the exact path, two
reads: `/jobseeker_page/mispage` 200 ×2, 2 331 252 B both times (md5 4d80c27ccfd3 / 81aa1a8c944f
— the Livewire id and checksum move), 471 distinct vacancies in the page, no total stated;
Thimphu 192, Sarpang 103, Paro 64.
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

HOST = "www.blmis.gov.bt"
PATH = "/jobseeker_page/mispage"
LISTS = ("job_by_company", "job_by_categories", "job_by_location")   # three groupings of one board
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")   # «+975 17 12 34 56», «17123456»: 8+ digits with separators
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b")
INITIAL_RE = re.compile(r'wire:initial-data="([^"]+)"')
AUDIT = ("created_by", "updated_by", "edited_by", "deleted_by", "action_remarks",
         "is_deleted", "is_completed", "deleted_at", "edited_at")     # the ministry's bookkeeping, not the vacancy
CRITERIA = ("gender",)                                                # #183: the vacancy is served, the criterion is not carried
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[blmis] {msg}", file=sys.stderr)


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
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(s):
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", s or "")).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def when(s):
    s = (str(s) or "").strip()
    return s[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", s) else (s or None)


def vacancies_of(markup):
    """The page's own Livewire data → (the three lists' union keyed by application_no, the sizes)."""
    m = INITIAL_RE.search(markup or "")
    if not m:
        return None, {}
    try:
        data = (json.loads(htmlmod.unescape(m.group(1))).get("serverMemo") or {}).get("data") or {}
    except ValueError:
        return None, {}
    if not any(isinstance(data.get(k), list) for k in LISTS):
        return None, {}
    out, sizes = {}, {}
    for k in LISTS:
        v = data.get(k)
        sizes[k] = len(v) if isinstance(v, list) else 0
        for x in (v or []):
            if isinstance(x, dict) and x.get("application_no") is not None:
                out.setdefault(str(x["application_no"]), x)
    return out, sizes


def record(v, stamp):
    withheld = [k for k in CRITERIA if v.get(k) not in (None, "", [])]
    place = " · ".join(x for x in (v.get("dzongkhag_name"), v.get("gewog_name"), v.get("placement")) if x)
    return {
        "source": "blmis", "country": stamp,
        "ledger_id": f"blmis:{v.get('application_no')}", "id": str(v.get("application_no")),
        "url": f"https://{HOST}{PATH}",                     # the board has no per-vacancy address: the list is the page
        "title": text(v.get("designation")), "employer": text(v.get("business_name")),
        "category": v.get("job_category") or None, "qualification": v.get("qualification") or None,
        "place": place or None, "dzongkhag": v.get("dzongkhag_name") or None,
        "salary_month_nu": v.get("starting_salary") or None,          # Ngultrum, as the ministry recorded it
        "posts": v.get("slot") if isinstance(v.get("slot"), int) else None,
        "employment_type": v.get("employment_type") or None,
        "closes": when(v.get("last_date_registration")),
        "posted": when((v.get("created_at") or "")[:10]),
        "description": scrub(text(v.get("job_description"))),
        "remarks": scrub(text(v.get("remarks"))),
        "withheld_fields": withheld or None,
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    url = f"https://{HOST}{PATH}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the jobseeker page is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    found, sizes = vacancies_of(body)
    if found is None:
        die(f"{url}: 200 without the page's `wire:initial-data` vacancy lists — the page changed; not an empty board", EXIT_PARTIAL)
    rows = [record(v, stamp) for v in found.values()]
    if a.dzongkhag:
        want = a.dzongkhag.strip().lower()
        rows = [r for r in rows if (r["dzongkhag"] or "").strip().lower() == want]
    withheld = sorted({k for r in rows for k in (r["withheld_fields"] or ())})
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    total = len(found)
    if not total:
        note("0 vacancies — the page's lists are empty (200); not an error.")
    else:
        grouping = ", ".join(f"{k.replace('job_by_', '')} {th(n)}" for k, n in sizes.items())
        note(f"{th(len(rows))} emitted of the {th(total)} distinct vacancies the page carries ({grouping} — three groupings of one board); the site states no total, the union is the board.")
    if a.dzongkhag:
        note(f"--dzongkhag {a.dzongkhag}: kept {th(len(rows))} of {th(total)}.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the board is Bhutan's and states no country.")
    note("the ministry's audit fields never emitted" + (f"; {', '.join(withheld)} withheld where a vacancy carried it (#183)" if withheld else "; no personal criterion on any vacancy today") + "; contacts scrubbed.")


def main(argv=None):
    p = argparse.ArgumentParser(description="BLMIS — Bhutan's public employment service: every vacancy the jobseeker page already carries, read from the page's own Livewire data; the ministry's audit fields and any personal criterion never emitted. Issue #680.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the whole board (1 request)")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the board states none)")
    j.add_argument("--dzongkhag", help="keep one district, as the page writes it (Thimphu, Sarpang, Paro…)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
