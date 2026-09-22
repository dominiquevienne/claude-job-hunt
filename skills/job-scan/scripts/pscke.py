#!/usr/bin/env python3
"""Public Service Commission (Kenya) — the recruitment system's own tables (`pscims.publicservice.go.ke`): the civil service's open adverts and its internship programme, each a table whose header names its columns. Issue #802.

  pscke.py jobs [--kind both] [--country-code KE]     the two tables (1 request each)

WHAT IT IS. The **Public Service Commission** advertises the Kenyan civil service's posts: the
competitions open to the public and to serving officers, the **Public Service Internship
Programme**, and the posts of the public universities and independent offices. *The generalists do
not carry these*, which is why the Commission's own system is the route.

**THE HOST WAS SILENT AND CAME BACK.** It answered nothing on 2026-09-12 and 2026-09-13, and
answered again on 2026-09-20 — the issue was opened on that return. *A dated silence is not a
verdict*, and this reading confirms the return.

THE RULES. `pscims.publicservice.go.ke` answers **404** to `/robots.txt`: no file, so no rule to
obey (open, `certain: True`), no Crawl-delay; 2 s is ours. *The Commission's WordPress site
(`www.publicservice.go.ke`) serves a Cloudflare managed `robots.txt` that refuses `ClaudeBot` and
does not name `Claude-User`, so the `*` group applies there (07.09.2026) — but that host is not this
adapter's route; see below.* The guard is taken on the exact path.

THE TABLES. Two pages, two tables, **and their columns are not the same**:

```
/jobs/ActiveJobsAdverts.aspx              ## · Advert Number · Position · Job Scale · Ministry ·
                                          Number of Vacancies · Years of Experience Required ·
                                          Advert Category · Advert Date · Advert Close Date · (details)
/jobs/ActiveAdvertsInternsInternshipExt.aspx   ## · Advert Number · Position ·
                                          Ministry/State Department · Number of Vacancies ·
                                          Advert Date · Advert Close Date · Action
```

**So the cells are read BY THEIR HEADER, never by position**: the **fourth cell is a job scale on
one page and a ministry on the other**, and the two tables have eleven and eight columns. A record
whose `ministry` held «CSG 8» would be wrong in a way nothing downstream could notice.

*A column read by position is also how a reading goes wrong while looking complete: the first
inspection of this table printed its first nine cells and concluded it had no closing date — it has
one, in the tenth.* **What a table does not state, the record leaves null**, and the run says how
many records lack a closing date rather than inventing one. The advert's detail sits behind an
ASP.NET `__doPostBack` — **not replayed**, and the record says the detail was not read.

**The Commission's WordPress site is NOT read, and the reason is not technical.** Its `/jobs/` page
carries 16 PDFs — delegated adverts, re-adverts **and lists of successful candidates**. *A list of
named candidates is personal data about people who did not publish it for us*; the adapter does not
open that page. **Applying needs an account on the system (an ID or passport number); the plugin
never creates one.**

**WITHHELD:** e-mail addresses and telephone numbers in any cell; `contacts_withheld` on every
record. `--country-code` STAMPS (the tables state no country) and the run says so.

Measured 2026-09-22 09:5x UTC by the declared client, the guard on the exact path, two reads of the
adverts table: `ActiveJobsAdverts.aspx` 200 ×2, 14 232 B, **md5 24732dc66ffc both times** — **1
active advert** (D111/2026, Principal Labour Migration Officer, CSG 8, 2 vacancies, «For Serving
Officers Only», 14-09-2026); `ActiveAdvertsInternsInternshipExt.aspx` 200, 14 538 B — **1 advert,
1 000 places** (Public Service Internship — Digital Literacy Programme, close 05-10-2026). *On
2026-09-20 that second table carried its header and no row: **the page was empty, and it is not
empty today** — which is why an empty table is reported, never treated as a failure.*
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

HOST = "pscims.publicservice.go.ke"
PAGES = {"jobs": f"https://{HOST}/jobs/ActiveJobsAdverts.aspx",
         "internships": f"https://{HOST}/jobs/ActiveAdvertsInternsInternshipExt.aspx"}
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\(?\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
DATE_RE = re.compile(r"\b\d{1,2}-\d{1,2}-\d{4}\b")
REF_RE = re.compile(r"^\d{1,4}/\d{4}$")     # «143/2026» is an advert number and has the shape of a phone number
STRIP_RE = re.compile(r"(?s)<style.*?</style>|<script.*?</script>")
ROW_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL_RE = re.compile(r"<t([dh])[^>]*>(.*?)</t[dh]>", re.S)
FIELDS = {"advert number": "advert_number", "position": "position", "job scale": "job_scale",
          "ministry": "ministry", "ministry/state department": "ministry",
          "number of vacancies": "vacancies", "years of experience required": "experience_years",
          "advert category": "category", "advert date": "advert_date",
          "advert close date": "close_date", "close date": "close_date"}
IGNORE = {"##", "#", "action", ""}
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[pscke] {msg}", file=sys.stderr)


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
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # no rules file at all; 2 s is ours
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
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", markup or "")).replace("\xa0", " ")
    return " ".join(t.split()) or None


def scrub(s):
    if not s:
        return None
    if REF_RE.match(s.strip()):              # an advert number, not a number to call
        return s.strip()
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def when(s):
    """«05-10-2026» → `2026-10-05`; anything else as read."""
    s = (s or "").strip()
    m = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{4})$", s)
    return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}" if m else (s or None)


def rows_of(markup):
    """A page → (header labels, [row cells]). The two tables do NOT share their columns."""
    body = STRIP_RE.sub("", markup or "")
    header, rows = None, []
    for block in ROW_RE.findall(body):
        cells = CELL_RE.findall(block)
        if not cells:
            continue
        kinds = {k for k, _v in cells}
        values = [text(v) for _k, v in cells]
        if kinds == {"h"} or (header is None and values and (values[0] or "").strip() in ("##", "#")):
            header = [(v or "").strip().lower() for v in values]
            continue
        if header is None:
            continue
        if len([v for v in values if v]) <= 1:
            continue                       # the pager's «< >» line is not a row
        rows.append(values)
    return header, rows


def record(header, values, kind, stamp):
    got = {}
    for label, value in zip(header, values):
        key = FIELDS.get(label)
        if key and value:
            got[key] = scrub(value)
    number = got.get("advert_number") or ""
    position = got.get("position") or ""
    key = re.sub(r"[^a-z0-9]+", "-", f"{kind}-{number}-{position}".lower()).strip("-")
    return {
        "source": "pscke", "country": stamp, "kind": kind,
        "ledger_id": f"pscke:{key}", "id": key,
        "advert_number": got.get("advert_number"), "title": got.get("position"),
        "ministry": got.get("ministry"), "job_scale": got.get("job_scale"),
        "vacancies": got.get("vacancies"), "experience_years": got.get("experience_years"),
        "category": got.get("category"),
        "advert_date": when(got.get("advert_date")), "close_date": when(got.get("close_date")),
        "url": PAGES[kind],
        "detail_read": False,     # the detail is an ASP.NET __doPostBack; it is not replayed
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    kinds = tuple(PAGES) if a.kind == "both" else (a.kind,)
    stamp = a.country_code.upper() if a.country_code else None
    rows, seen, read, no_close = [], set(), [], 0
    for kind in kinds:
        url = PAGES[kind]
        code, body = request(url)
        if code == 404:
            die(f"{url}: HTTP 404 — the page is gone", EXIT_GONE)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        header, values = rows_of(body)
        if header is None:
            die(f"{url}: 200 without the table's header — the page changed; not an empty table", EXIT_PARTIAL)
        read.append((kind, len(values)))
        for v in values:
            r = record(header, v, kind, stamp)
            if not r["advert_number"] or r["id"] in seen:
                continue
            seen.add(r["id"])
            if not r["close_date"]:
                no_close += 1
            rows.append(r)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    listed = ", ".join(f"{k} {th(n)}" for k, n in read)
    if not rows:
        note(f"0 adverts emitted ({listed}) — **an empty table is a state, not a failure**: the internship table carried its header and no row on 2026-09-20 and carries one today.")
    else:
        note(f"{th(len(rows))} advert(s) emitted ({listed}); **neither table states a count** — what they list is the board.")
    if no_close:
        note(f"{th(no_close)} advert(s) state no closing date: the adverts table has no such column, and the record leaves it null rather than inventing one.")
    note("the cells are read BY THEIR HEADER: the two tables do not share their columns, and the fourth is a job scale on one page and a ministry on the other.")
    note("the advert's detail is an ASP.NET __doPostBack and is NOT replayed (`detail_read: false`); the Commission's WordPress PDFs are not read at all — some of them are lists of successful candidates, which is personal data.")
    note("applying needs an account on the system (an ID or passport number); the plugin creates none.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the tables state no country.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Public Service Commission (Kenya) — the civil service's active adverts and internships, read by the header each table prints. Issue #802.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the two tables (1 request each)")
    j.add_argument("--kind", choices=("jobs", "internships", "both"), default="both", help="which table — default both")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the tables state none)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
