#!/usr/bin/env python3
"""Mauritius Jobs (`mauritiusjobs.govmu.org`), the National Employment Department's portal (Ministry of Labour and Industrial Relations): its search is a POST the page makes on itself, and **one request returns the whole board — every row AND every advert, unfolded in the page**. Issue #696.

  mauritiusjobs.py jobs [--district NAME] [--country-code MU] [--local|--international]

WHAT IT IS. The **public employment service of Mauritius**: employers file their vacancies with the
Department and jobseekers apply through it (the apply button leads to its login — the plugin never
creates an account and never logs in). The project is co-funded by the EU, Italy's Ministry of
Labour and the IOM, which is why the board carries international postings beside the Mauritian ones.

THE RULES. `mauritiusjobs.govmu.org` does not answer `/robots.txt` as a rules file: no rule is read,
so there is none to obey — open, `certain: False`, no Crawl-delay; 2 s is ours. The guard is taken on
the exact path.

THE LIST. `GET /jobsearch` (200; 138 641 B) is the **form only** — it lists no vacancy. The form
POSTs to `/index.php/jobsearch` with its own fields (`search_by_local`, `search_by_international`,
`search_by_district`, `search_by_keyword`, `search_by_jobtitle`, `search_by_qualification`,
`search_by_sector`) and **no token of any kind**, so the empty search is replayed exactly as the page
sends it. The answer (200; 2 209 039 B) carries:

  * **its own count** — «Total Jobs Available : 587 jobs», printed beside the emitted count, and the
    run says «N short» if they differ (a board that states a total is the one witness worth having);
  * **587 rows** `<tr onclick="jobdetails('56320')">` — # · Job Title · Economic Sector · Company ·
    Country · Closing Date;
  * **587 advert blocks** `<div class="show_details" id="56320">`, each a `table.job_details` of
    **label / value** pairs — Employer, Economic Sector, District in Mauritius, Country, Job Summary,
    Duties of Job, and, when the employer filed them, Qualifications Required (363), Skills (340),
    State / Province (251), Experience Required (81), Salary Proposed (395), a website link (69).
    **The labels are read as labels**, never by position: they are not all present on every advert,
    and a positional read would put a district where a summary is.

**AGE RANGE IS NEVER EMITTED, AND THE RECORD SAYS SO — 464 of the 587 adverts carry one** («18 -
39»). #183: the advert is served, the criterion is not carried, and `withheld_fields: ["age_range"]`
names what was dropped so a silent filter cannot look like a clean board. *Salary Proposed is a
range the employer offers, not a criterion about a person: it is emitted as written.*

**THREE STATED FIGURES, THREE DATES, none of them corrected into the others**: the search states
**587** (2026-09-21), the portal's own root says «More Than **575** Jobs Available» the same day, and
the card's first reading recorded «**650** Jobs» on 2026-09-18. The adapter prints the one it read.

`--district` filters the emitted rows **on the district the advert states**, and the filtering is
OURS, done after the one request — the portal's own district codes are never composed. `--local` and
`--international` split on the advert's own Country field the same way. `--country-code` STAMPS (the
board is Mauritius's but carries postings abroad, so the stamp stays the user's) and the run says so.

Measured 2026-09-21 14:0x–14:1x UTC by the declared client, the guard on the exact path, two POSTs:
200 ×2, 2 209 039 B both, md5 d51540fa42a8 / b66cc5275b2e (a rendered element moves), **587 rows
both times, the same ids in the same order, «587 jobs» stated both times**.
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

HOST = "mauritiusjobs.govmu.org"
SEARCH = f"https://{HOST}/index.php/jobsearch"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\(?\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
DATE_RE = re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")
TOTAL_RE = re.compile(r"Total Jobs Available\s*:\s*([\d\s,]+?)\s*jobs", re.I)
ROW_RE = re.compile(r"<tr onclick=\"jobdetails\('(\d+)'\)\"[^>]*>(.*?)</tr>", re.S)
TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
DETAIL_SPLIT = '<div class="show_details" id="'
PAIR_RE = re.compile(r"<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>", re.S)
ROW_CELLS = 7
AGE_LABEL = "age range"          # #183: read so it can be withheld BY NAME, never so it can be emitted
FIELDS = {
    "employer": "employer",
    "economic sector": "sector",
    "district in mauritius": "district",
    "state / province": "state_province",
    "country": "country",
    "job summary": "summary",
    "duties of job": "duties",
    "qualifications required": "qualifications",
    "skills/competencies": "skills",
    "experience required": "experience",
    "salary proposed": "salary_proposed",
    "youtube/website link": "link",
}
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[mauritiusjobs] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, data=None):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    headers = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"}
    if data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(wire_url(url), data=data.encode("utf-8") if data is not None else None, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
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
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def when(s):
    """«21/09/2026» → `2026-09-21`; anything else as read."""
    s = (s or "").strip()
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}" if m else (s or None)


def stated(markup):
    m = TOTAL_RE.search(markup or "")
    return int(re.sub(r"\D", "", m.group(1))) if m else None


def details_of(markup):
    """The page's advert blocks → {id: {field: value}}, read by LABEL — they are not all present."""
    out = {}
    for chunk in (markup or "").split(DETAIL_SPLIT)[1:]:
        m = re.match(r"(\d+)\"\s*>", chunk)
        if not m:
            continue
        block = chunk[: chunk.find(DETAIL_SPLIT)] if DETAIL_SPLIT in chunk else chunk
        table = re.search(r'<table class="job_details"[^>]*>(.*?)</table>', block, re.S)
        got = {}
        for label, value in PAIR_RE.findall(table.group(1) if table else ""):
            key = (text(label) or "").strip().lower().rstrip(":")
            if key == AGE_LABEL:
                got["_age"] = True                      # noted so the withholding can DECLARE itself
            elif key in FIELDS:
                got[FIELDS[key]] = text(value)
        out[m.group(1)] = got
    return out


def rows_of(markup):
    """The result table → [(id, row fields)]; the row names #, title, sector, company, country, closing."""
    out = []
    for job_id, tr in ROW_RE.findall(markup or ""):
        tds = TD_RE.findall(tr)
        if len(tds) != ROW_CELLS:
            return None, f"a row carries {len(tds)} cell(s), not {ROW_CELLS}"
        out.append((job_id, {"title": text(tds[1]), "sector": text(tds[2]), "employer": text(tds[3]),
                             "country": text(tds[4]), "closing_date": text(tds[5])}))
    return out, None


def record(job_id, row, detail, stamp):
    d = dict(detail or {})
    withheld = ["age_range"] if d.pop("_age", False) else []
    r = {
        "source": "mauritiusjobs", "country_stamp": stamp,
        "ledger_id": f"mauritiusjobs:{job_id}", "id": job_id,
        "title": scrub(row.get("title")),
        "employer": scrub(d.get("employer") or row.get("employer")),
        "sector": d.get("sector") or row.get("sector"),
        "district": d.get("district"), "state_province": d.get("state_province"),
        "country": d.get("country") or row.get("country"),
        "closing_date": when(row.get("closing_date")),
        "summary": scrub(d.get("summary")), "duties": scrub(d.get("duties")),
        "qualifications": scrub(d.get("qualifications")), "skills": scrub(d.get("skills")),
        "experience": scrub(d.get("experience")), "salary_proposed": d.get("salary_proposed"),
        "link": scrub(d.get("link")),
        "advert_read": bool(detail),
        "withheld_fields": withheld,          # #183: what was dropped is NAMED, even when today it is empty
        "contacts_withheld": True,
    }
    return r


def cmd_jobs(a):
    if a.local and a.international:
        die("--local and --international name two halves of the board: pass one, or neither for all of it")
    form = {"search_by_local": "", "search_by_international": "", "search_by_district": "",
            "search_by_keyword": "", "search_by_jobtitle": "", "search_by_qualification": "",
            "search_by_sector": ""}
    code, body = request(SEARCH, urllib.parse.urlencode(form))    # the form's own fields, no token
    if code == 404:
        die(f"{SEARCH}: HTTP 404 — the search route is gone", EXIT_GONE)
    if code != 200:
        die(f"{SEARCH}: HTTP {code}", EXIT_PARTIAL)
    if 'class="job_list"' not in body:
        die(f"{SEARCH}: 200 without the result table — the page changed; not an empty board", EXIT_PARTIAL)
    said = stated(body)
    found, why = rows_of(body)
    if found is None:
        die(f"{SEARCH}: 200 but the result table is not the one measured ({why}) — the page changed", EXIT_PARTIAL)
    details = details_of(body)
    stamp = a.country_code.upper() if a.country_code else None
    want = (a.district or "").strip().lower()
    rows, seen, dropped = [], set(), 0
    for job_id, row in found:
        if job_id in seen:
            continue
        seen.add(job_id)
        r = record(job_id, row, details.get(job_id), stamp)
        if want and (r["district"] or "").strip().lower() != want:
            dropped += 1
            continue
        mauritian = (r["country"] or "").strip().lower() == "mauritius"
        if (a.local and not mauritian) or (a.international and mauritian):
            dropped += 1
            continue
        rows.append(r)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    no_advert = sum(1 for r in rows if not r["advert_read"])
    withheld = sum(1 for r in rows if r["withheld_fields"])
    read = th(len(seen))
    if said is None:
        note(f"{read} row(s) read; **the page stated no total this time** — it usually prints «Total Jobs Available : N jobs», and the run says so rather than claiming one.")
    elif said != len(seen):
        note(f"{read} row(s) read, the board states {th(said)} — {th(abs(said - len(seen)))} {'short' if said > len(seen) else 'more'}; the gap is the page's, not a filter's.")
    else:
        note(f"{read} row(s) read, and the board states {th(said)} — they agree.")
    note(f"{th(len(rows))} emitted{f' ({th(dropped)} dropped by the filters asked for, which are OURS and applied after the one request)' if dropped else ''}.")
    if no_advert:
        note(f"{th(no_advert)} row(s) carried no advert block; what the row itself names is emitted, and `advert_read` says which.")
    note(f"age range never emitted — {th(withheld)} of the emitted records declare it in `withheld_fields` (#183: the advert is served, the criterion is not carried).")
    if stamp:
        note(f"country {stamp} is the user's stamp — the board is Mauritius's and carries postings abroad, which the record's own `country` names.")
    note("applying needs an account on the portal; the plugin creates none and never logs in.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Mauritius Jobs — the National Employment Department's board, returned whole by the search POST the page makes on itself. Issue #696.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the whole board (1 request)")
    j.add_argument("--district", help="keep only the adverts stating this district (OUR filter, after the one request)")
    j.add_argument("--local", action="store_true", help="keep only the adverts whose own Country is Mauritius")
    j.add_argument("--international", action="store_true", help="keep only the adverts posted outside Mauritius")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the board carries postings abroad)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
