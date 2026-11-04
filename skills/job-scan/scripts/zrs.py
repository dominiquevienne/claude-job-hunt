#!/usr/bin/env python3
"""ZRS / RCSC (`jobs.rcsc.gov.bt`, Bhutan): the Royal Civil Service Commission's Zhiyog Recruitment System — and the first board in this corpus where an EMPTY filter means «no value matches» instead of «no filter». Issue #681.

  zrs.py jobs [--max-pages N] [--country-code BT]   the search, paged by the page's own skip/take
  zrs.py lists                                      the four filter sets, as the host declares them

WHAT IT IS. The recruitment system of Bhutan's Royal Civil Service Commission: the vacancies of
the royal civil service, with their position level, pay scale, agency, qualification, slot count
and application window. A public source, and the only route to those vacancies — `rcsc.gov.bt`'s
own announcements page says so itself.

THE RULES. `jobs.rcsc.gov.bt` serves **no `robots.txt` at all** — 404, so `state: absent` and
`certain: True`: an absence of rules is a KNOWLEDGE and not an ignorance (#283). No `Crawl-delay`
is written, so 3 s is ours. The guard is taken on the exact path, host included, for every one of
the five endpoints below.

**THE BLOCKING QUESTION THIS FILE WAS WRITTEN AGAINST WAS POSED ON THE WRONG OBJECT, and the
answer was in the page all along — no request was needed to find it.** `/Application/Vacancy`'s
script was read as making `GetVacancyCondition` the carrier of the four filter lists, so the
adapter was declared to depend on it and it answers `null` (4 B, `md5 37a6259c…`) to a plain
client, twice, with and without `X-Requested-With`. **It is not the carrier. It is the
restoration of a PREVIOUSLY SAVED search, and the page guards against its own `null`:**

    if (IsClear) { btnSearch_Click(false); }  else { GetSearchCondition(); }
    function SetSearchCondition(ret) { if (ret != null && ret != "") { ...

*So `null` is the normal answer for a client that has saved nothing, the search runs without it,
and «why does it answer `null`» had no bearing on the route. A measurement aimed at the wrong
object is not a failed measurement — it answers, and its answer is about something else.*

THE FOUR LISTS LIVE ON FOUR OTHER ENDPOINTS, which the page's own dropdown descriptors name
(`var dd1 … dd7`, each with its `Controller` and `Action`). Measured 2026-11-04:

    /AgencyCommon/GetSuperStructureData    6 services     -> Condition02   default: all checked
    /AgencyCommon/GetEmploymentTypeData    2 types        -> Condition03   default: all checked
    /AgencyCommon/GetCategoryData          5 categories   -> Condition04   default: all checked
    /AgencyCommon/GetDzongkhagData        20 dzongkhags   -> Condition05   default: all checked

**AND `default: true` IS THE WHOLE DIFFICULTY: the multi-selects open FULLY CHECKED, so an empty
`ConditionNN` does not mean «do not filter on this» — it means «no value matches», and the search
answers `[]`.** That `[]` is a well-formed empty list from a board that holds vacancies, which is
why this file's floor is POSITIVE: a list that comes back empty is a BROKEN run, never a board
with nothing in it. *Publishing one of those `[]` as «the board is empty» was avoided by a hair.*

THE SERIALISATION IS THE PAGE'S, to the trailing comma. `GetCondition()` appends `value + ","`
per checked item, so each field ends in a comma, and `$.ajax({data: {Condition: data}})` sends it
form-encoded as `Condition[ConditionNN]`. `Condition10` (the order, `D`/`C`/`A`) is REQUIRED — the
page refuses its own search without it. `Condition11`/`Condition12` are skip/take, and the page's
own page size is 10.

THE WITNESS IS THE BOARD'S OWN AND IT IS NOT OUR EXTRACTION: every row carries
`totaL_ROW_COUNT`, read by the page itself as `ret[0].totaL_ROW_COUNT`. Measured 2026-11-04:
**16 declared, 10 + 6 emitted over two pages, 16 distinct, zero overlap** — and the browser's
own header read «16 Jobs» the day before. *So the count is stated, compared, and reported; and
what is stated is the result of the full-set search, never «the size of the board».*

**THE LOCATION IS TWENTY BOOLEANS, AND DERIVING THEIR NAMES NAIVELY IS WRONG ON EXACTLY ONE OF
THE TWENTY.** Each row carries `locBumthang`, `locChukha` … one per dzongkhag. The obvious
derivation — `"loc" + name.replace(" ", "")` — is faithful on 19 and FAILS on `Pema Gatshel`,
whose field is `locPemagatshel` with a lowercase `g`. It would not raise: the vacancy would
simply come out with no location, which is well formed and false. So the mapping is built
**case-insensitively from the host's own list** and asserted a TOTAL BIJECTION — 20 names against
20 fields, no collision, nothing unclaimed — or the run stops. *A list whose members are derived
cannot omit one; a list composed by hand omits one without leaving a trace.*

THE DATES ARE WRITTEN WITHOUT AN OFFSET — `2026-11-09T00:00:00` — so they are recorded AS WRITTEN
and no timezone is invented for them. Bhutan is `+06:00`; the host does not say so, and a stamped
offset would be ours and not its.

REDACTION. The 64 fields of a row are structural — title, agency, level, pay scale, dates, counts.
**Measured on all 16 rows: zero e-mail and zero telephone**, so `withheld_fields` comes out empty
and the record says nothing about a discretion it did not exercise. The free-text fields are
scrubbed anyway, because the floor must exist before the first row that needs it.

EXIT CODES. 0 all rows emitted and the count agrees · 2 broken · 6 partial (fewer rows than the
board declares) · 7 refused by the rules · 8 the rules could not be read.
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
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
from _withheld import withheld_a_contact

HOST = "jobs.rcsc.gov.bt"
HOSTS = (HOST,)
ROOT = f"https://{HOST}/"
PAGE_SIZE = 10                      # the page's own `PageCount = Number("10")`
ORDER_DEFAULT = "D"                 # the page's own initial value; D/C/A are the only three
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# The four filter sets, named by the page's own dropdown descriptors (`var dd1 … dd7`), each
# with the Condition field it feeds and the key its rows carry. These four are the ones the
# page opens FULLY CHECKED (`default: true`), which is why all four must be sent in full.
FILTERS = (
    ("Condition02", "GetSuperStructureData", "superStructureID"),
    ("Condition03", "GetEmploymentTypeData", "employmentTypeCD"),
    ("Condition04", "GetCategoryData", "categoryCD"),
    ("Condition05", "GetDzongkhagData", "dzongkhagName"),   # the VALUE is the name, not an id
)
DZONGKHAG_ENDPOINT = "GetDzongkhagData"
SEARCH_PATH = "/Application/GetVacancyAnnouncement"
LIST_PATH = "/AgencyCommon/%s"

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# ANCHORED. Bhutan's code is +975 and its local numbers are 8 digits; the labelled alternative
# is what fires on a board that writes `Tel: 17940918` without any code, as `vacancybt` does.
PHONE_RE = re.compile(
    r"\+\s*\(?\s*975\s*\)?[\s.\-]?\d[\d\s.\-]{5,}\d"
    r"|(?:T[ée]l(?:[ée]phone)?|Phone|Mobile|Cell|Contact\s*No)\s*:?\s*\(?\+?\d[\d\s().\-]{5,}\d")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[zrs] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def post(url, form):
    """One POST, guarded on the exact URL, paced, and declaring our identity."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc not in HOSTS:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(parts.netloc, Pace(parts.netloc, own=3.0)).wait()   # no Crawl-delay written
    body = urllib.parse.urlencode(form).encode("utf-8")
    req = urllib.request.Request(wire_url(url), data=body, headers={
        "User-Agent": UA,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def as_json(url, code, raw, what):
    if code != 200:
        die(f"{what}: HTTP {code} from {url}", EXIT_GONE if code == 404 else EXIT_BROKEN)
    try:
        return json.loads(raw)
    except ValueError as e:
        die(f"{what}: {url} answered {len(raw or '')} characters that are not JSON: {e}")


def filter_sets():
    """The four sets, from the host. A set that comes back EMPTY stops the run.

    This floor is POSITIVE and it is the one guard this board cannot do without: the
    multi-selects open fully checked, so an empty `ConditionNN` is read by the search as
    «no value matches» and answers `[]` — a well-formed empty list from a board that holds
    vacancies. An empty set here would therefore publish a false zero about the host.
    """
    out = {}
    for field, action, key in FILTERS:
        url = ROOT.rstrip("/") + LIST_PATH % action
        rows = as_json(url, *post(url, {}), what=action)
        if not isinstance(rows, list) or not rows:
            die(f"{action} answered {rows!r}: an empty filter set means «no value matches», "
                f"so the search would answer [] and that [] would be a false zero about "
                f"this board — refusing to search", EXIT_BROKEN)
        vals = [str(r[key]) for r in rows if r.get(key) not in (None, "")]
        if len(vals) != len(rows):
            die(f"{action}: {len(rows) - len(vals)} of {len(rows)} rows carry no {key!r}")
        out[field] = (vals, rows)
    return out


def dzongkhag_map(rows, row):
    """{field in a vacancy row -> dzongkhag name}, derived and asserted a TOTAL BIJECTION.

    `"loc" + name.replace(" ", "")` is faithful on 19 of the 20 and wrong on `Pema Gatshel`,
    whose field is `locPemagatshel` with a lowercase `g`. That mismatch does not raise — the
    vacancy simply comes out with no location, which is well formed and false. So the match is
    case-insensitive and the result must claim every name AND every field, or the run stops.
    """
    fields = [k for k in row if k.startswith("loc")]
    lower = {k.lower(): k for k in fields}
    if len(lower) != len(fields):
        die(f"two `loc*` fields differ only in case: {sorted(fields)}")
    out, missing = {}, []
    for r in rows:
        name = r.get("dzongkhagName")
        key = lower.get(("loc" + str(name).replace(" ", "")).lower())
        if key is None:
            missing.append(name)
        else:
            out[key] = name
    unclaimed = sorted(set(fields) - set(out))
    if missing or unclaimed or len(out) != len(rows):
        die(f"the dzongkhag mapping is not a bijection: {len(out)} of {len(rows)} names matched, "
            f"unmatched {missing}, `loc*` fields nothing claimed {unclaimed}")
    return out


def text(s):
    if s is None:
        return None
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", str(s))).replace("\xa0", " ")
    return " ".join(t.split()) or None


def scrub(s):
    """Contacts out, and the record says which kinds were there."""
    if not s:
        return None, []
    took = []
    if MAIL_RE.search(s):
        took.append("email")
        s = MAIL_RE.sub("[e-mail withheld]", s)
    out = PHONE_RE.sub("[telephone withheld]", s)
    if out != s:
        took.append("telephone")
    return (out.strip() or None), took


def record(row, locmap, stamp, position):
    took = []
    free = {}
    for k in ("positionTitle", "recruitmentName", "qualificationName", "agencyName"):
        free[k], t = scrub(text(row.get(k)))
        took += t
    rid, pid = row.get("recruitmentID"), row.get("positionID")
    key = f"{rid}-{pid}"
    r = {
        "source": "zrs", "country": stamp,
        "ledger_id": f"zrs:{key}", "id": key,
        "title": free["positionTitle"],
        "recruitment": free["recruitmentName"],
        "employer": free["agencyName"],
        "qualification": free["qualificationName"],
        "service": text(row.get("superStructureName")),
        "employment_type": text(row.get("employmentTypeName")),
        "category": text(row.get("categoryName")),
        "position_level": text(row.get("positionLevelName")),
        # the dzongkhags this vacancy is open in, from the twenty booleans the row carries
        "locations": sorted(n for k, n in locmap.items() if row.get(k)),
        "pay_scale_min": row.get("minPayScale"),
        "pay_scale_max": row.get("maxPayScale"),
        "slots": row.get("slots"),
        "applicants_count": row.get("applicantsCount"),
        # AS WRITTEN: the host states no offset, and Bhutan's +06:00 would be ours, not its
        "posted_as_written": row.get("vaPublishDate"),
        "closes_as_written": row.get("vaEndDate"),
        "application_from_as_written": row.get("applicationFrom"),
        "application_to_as_written": row.get("applicationTo"),
        "url": ROOT + "Application/Vacancy",     # the board has no per-vacancy address
        "list_position": position,
        "withheld_fields": sorted(set(took)),
    }
    if withheld_a_contact(r["withheld_fields"]):
        r["contacts_withheld"] = True
    return r


def search(sets, skip, take):
    form = {
        "Condition[IsSearch]": "true",
        "Condition[Condition01]": "",            # the free-text search box, empty
        "Condition[Condition06]": "",            # agency
        "Condition[Condition07]": "",            # position title
        "Condition[Condition08]": "",            # salary
        "Condition[Condition09]": "false",       # bookmark — a signed-in notion
        "Condition[Condition10]": ORDER_DEFAULT,  # REQUIRED: the page refuses its own search
        "Condition[Condition11]": str(skip),
        "Condition[Condition12]": str(take),
    }
    for field, _, _ in FILTERS:
        # the page appends `value + ","` per checked item, so the field ENDS in a comma
        form["Condition[%s]" % field] = "".join(v + "," for v in sets[field][0])
    url = ROOT.rstrip("/") + SEARCH_PATH
    rows = as_json(url, *post(url, form), what="GetVacancyAnnouncement")
    if not isinstance(rows, list):
        die(f"GetVacancyAnnouncement answered {type(rows).__name__}, not a list")
    return rows


def cmd_lists(a):
    sets = filter_sets()
    for field, action, key in FILTERS:
        vals, rows = sets[field]
        print(f"{field}  {action}  {len(vals)} value(s)")
        for r in rows:
            print(f"    {r[key]}")
    note("these four sets are sent IN FULL: the page opens them fully checked, so an empty "
         "field means «no value matches» and not «no filter».")


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    sets = filter_sets()
    note(f"filter sets, from the host: " + ", ".join(
        f"{action} {len(sets[field][0])}" for field, action, _ in FILTERS))

    rows, seen, skip, pages, stated = [], set(), 0, 0, None
    locmap = None
    while True:
        batch = search(sets, skip, PAGE_SIZE)
        pages += 1
        if not batch:
            break
        if locmap is None:
            locmap = dzongkhag_map(sets["Condition05"][1], batch[0])
        if stated is None:
            stated = batch[0].get("totaL_ROW_COUNT")
        for row in batch:
            key = f"{row.get('recruitmentID')}-{row.get('positionID')}"
            if key in seen:
                continue
            seen.add(key)
            rows.append(record(row, locmap, stamp, len(rows) + 1))
        skip += PAGE_SIZE
        if a.max_pages and pages >= a.max_pages:
            note(f"stopped at --max-pages {a.max_pages}: this is OUR bound, not the board's")
            break
        if stated is not None and skip >= stated:
            break

    json.dump(rows, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")

    # the count is the BOARD's own field, read by the page itself as ret[0].totaL_ROW_COUNT —
    # it is not derived from anything we extracted, which is what makes the comparison worth
    # printing at all
    short = None if stated is None else stated - len(rows)
    if stated is None:
        note(f"{len(rows)} vacancy/vacancies emitted over {pages} page(s); the board stated no "
             f"count on this run, so the conclusion rests on a short page and not on a witness.")
    elif short:
        note(f"{len(rows)} emitted, board states {stated} — {short} SHORT over {pages} page(s).")
        sys.exit(EXIT_PARTIAL)
    else:
        note(f"{len(rows)} emitted over {pages} page(s), board states {stated} — they agree. "
             f"That is the full-set search, never «the size of the board».")
    if stamp:
        note(f"country {stamp} is the user's stamp — a row states its dzongkhags, not its country.")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="ZRS / RCSC (Bhutan) — the royal civil service's vacancies, searched with "
                    "the four filter sets IN FULL. Issue #681.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the search, paged by the page's own skip/take")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0,
                   help="stop after N pages (0 = until the stated count is reached)")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on every record")
    j.set_defaults(fn=cmd_jobs)
    l = sub.add_parser("lists", help="the four filter sets, as the host declares them")
    l.set_defaults(fn=cmd_lists)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
