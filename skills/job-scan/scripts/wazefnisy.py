#!/usr/bin/env python3
"""Wazefni Syria (`www.wazefnisy.com/jobs/`), «وظفني سوريا — منصة الوظائف وفرص العمل في سوريا»: the page renders nothing by itself — **one request to its own `api.php` returns the entire board as JSON**, and a second reads the site's own Arabic labels out of its script. Issue #650.

  wazefnisy.py jobs [--city ID] [--category ID] [--type ID] [--since YYYY-MM-DD] [--country-code SY]   the whole board (2 requests)
  wazefnisy.py labels                                                                                  the site's own city / category / type ids

WHAT IT IS. A Syrian general board with a freelancer marketplace beside it: employers file a
vacancy through `index.html?action=open_add_job`, the site sells «featured» and «urgent» badges for
it, and the jobs page lists what was filed. Syria's other named boards are #649 (Syria Jobs Network,
whose own API answers HTTP 500 — `blocked`), `tanqeeb.md` and `hirefromsyria.md`. **Until this
adapter Syria had no route at all.**

THE RULES. `www.wazefnisy.com` answers HTTP 404 on `/robots.txt`: a 404 is knowledge — there is no
file, so there are no rules — open, `certain: True`, on `/`, on `/jobs/`, on the script and on the
API; no Crawl-delay, 2 s is ours. The guard is taken on the exact path.

THE BOARD IN ONE REQUEST. `/jobs/` (200; 95 446 B, identical twice) is a shell: it carries **no
advert**, only the filters and a «تحميل المزيد» button. Its `script.js` builds
`API_URL = <the page's directory>/api.php` and asks it **once** —
`GET /jobs/api.php?action=get_jobs` (200; 1 671 442 B) returns `{"success": true, "jobs": [ … ]}`
with **every advert of the board**, filtering and paging being done in the browser afterwards. So
there is no pager to walk and no count to chase: **the array's own length is the board**, and the
run prints what the server sent beside what it emitted, `N short` if they differ.

THE LABELS ARE THE SITE'S, NOT OURS. The API speaks in tokens (`sales_marketing`, `rif_dimashq`,
`remote`); the Arabic names live in the site's own `script.js` as three lists (`categories`,
`cities`, `jobTypes`). The run reads them from the site and maps what it emits — **a token the site
does not name is emitted raw and counted**, never guessed. If the script cannot be read or a list
cannot be parsed, every record keeps its raw token, `labels_read: false` says so, and nothing dies:
a label is a decoration, the token is the datum.

**WITHHELD, AND NAMED.** The record carries **no contact**: `phone` (**622** of the 888 adverts
filed a number — the field carries something on 734, but on 112 of those it is a stub, «0» on 92
and the country code «963» on 14, and `withheld_fields` names what was THERE rather than what the
field was called), `application_email` (476),
and any application link that opens a conversation with a person are dropped, and `withheld_fields`
says for each advert which of them was there — a silent filter must not look like a clean board.
*`has_whatsapp` and `has_phone_call` are not carried either: they qualify a number we never
emit, and a channel without its address tells the reader nothing he can act on.* The free text the
employer wrote (title, employer name, description) is scrubbed the same way: e-mail addresses to
«[e-mail withheld]», and **runs of 9 digits or more** to «[telephone withheld]».

*The threshold is 9 and it is a choice.* Syrian numbers are ten digits (`09xxxxxxxx`) and the
international forms longer; at 9 the scrub takes every number in the corpus and leaves every salary
(`1.725.000`, `300 - 1000`, `0.30 - 1.00`) and every date (`31/12/2026`) as written — measured on
the 888 adverts of 2026-09-22: of **180** digit runs, **158 withheld and 22 left, and each of the
22 was read** — five of them carry seven or eight digits (`1.725.000` twice, `300 - 1000`,
`1.800.000`, `1.925.000`), which is exactly what the threshold costs, and **the run prints that
five** rather than hiding it. Arabic-Indic digits are covered — Python's `\\d` matches them, and
`٢٠ - ٥٠` is among the 22 read.

**An application form is not a contact.** `application_link` (115 adverts) is mostly an employer's
form — `forms.gle` 76, `tally.so` 9, `docs.google.com` 4 — and those are emitted as `apply_url`.
The test is **whether the address opens a conversation with a person**: `wa.me/963…` and `t.me/…`
go, a form or a profile page stays. And an address that is not one — `hodnk:iskr/isvwk/fe.com`,
`http://www. homs`, both typed by employers — is dropped too and named in `withheld_fields`, because
emitting a link nobody can follow is worse than saying there was one: **106 emitted of the 115
filed on 2026-09-22.**

**Two fields the board sells and nobody bought:** `is_premium` and `is_urgent` were **false on
888 of 888** on 2026-09-22. A value true of nothing is worth no more than a value true of
everything: the record carries the flag **only when it is set**, and the run prints the count it
saw. *The badges exist — the site prices them — so the day one is sold the record will say so.*

`--city`, `--category` and `--type` filter on the site's own ids **after** the one request, and an
id the site does not know is refused with the list of the ones it does (a filter that fails toward
everything is indistinguishable from a successful one). `--since` keeps the adverts filed on or
after a date. `--country-code` STAMPS: the board names Syria in its own title and its cities are the
fourteen Syrian governorates, but the record does not invent a field the API does not carry.

THE ADVERT PAGE IS NOT READ. `job_details.php?id=N` is the site's own address for an advert — its
`og:url` is `https://wazefnisy.com/jobs/job_details.php?id=1047`, without the title its script
appends — and the API already carries the description, so the run emits the address and never
fetches it. `detail_read: false`.

Measured 2026-09-22 13:09–13:11 UTC by the declared client, the guard on the exact path, two reads
of each: `/jobs/` 200 ×2, 95 446 B, md5 76df6e248848 both; `api.php?action=get_jobs` 200 ×2,
**1 671 442 B, md5 717704ff3382 both**, `success: true`, **888 adverts, 888 distinct ids**, filed
between 2025-07-15 and 2026-09-22; 23 categories / 15 cities / 5 types read from `script.js`,
**every token the adverts use is named by the site**.
"""

import argparse
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

HOST = "www.wazefnisy.com"
BASE = "/jobs/"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
RUN_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{5,}\d(?!\w)")    # a digit run long enough to be a number someone dials
DATE_RE = re.compile(r"\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}|\d{4}-\d{2}-\d{2}")
DIGITS_FOR_A_PHONE = 9                       # 09xxxxxxxx is ten; 1.725.000 is seven — see the docstring
LIST_RE = r"%s\s*=\s*\["                     # the site's own three lists, read where it keeps them
PAIR_RE = re.compile(r"\{\s*id:\s*'([^']+)'\s*,\s*name:\s*'([^']+)'\s*\}")
MESSAGING = ("wa.me", "api.whatsapp.com", "web.whatsapp.com", "whatsapp.com",
             "t.me", "telegram.me", "m.me", "messenger.com")
HOSTNAME_RE = re.compile(r"[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[wazefnisy] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, accept="text/html,application/xhtml+xml"):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": accept,
                                                         "Accept-Language": "ar, en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def bracketed(src, name):
    """The body of `<name> = [ … ]` in the site's script, brackets balanced."""
    m = re.search(LIST_RE % re.escape(name), src or "")
    if not m:
        return ""
    depth, i = 1, m.end()
    while depth and i < len(src):
        if src[i] == "[":
            depth += 1
        elif src[i] == "]":
            depth -= 1
        i += 1
    return src[m.end():i - 1] if not depth else ""


def labels_of(src):
    """The site's three id → Arabic-name maps, `all` (its «any» option) dropped."""
    out = {}
    for field, name in (("category", "categories"), ("city", "cities"), ("type", "jobTypes")):
        pairs = {k: v for k, v in PAIR_RE.findall(bracketed(src, name)) if k != "all"}
        out[field] = pairs
    return out


def read_labels():
    code, body = request(f"https://{HOST}{BASE}script.js", accept="application/javascript, text/javascript")
    if code != 200:
        note(f"script.js: HTTP {code} — the site's own labels were not read; tokens are emitted raw.")
        return {"category": {}, "city": {}, "type": {}}, False
    maps = labels_of(body)
    empty = [f for f in ("category", "city", "type") if not maps[f]]
    if empty:
        note(f"script.js read ({th(len(body))} chars) but {', '.join(empty)} could not be parsed — "
             f"those tokens are emitted raw. The list's shape changed.")
    return maps, not empty


def scrub(s):
    """Free text as the employer wrote it, minus what reaches a person."""
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)

    def one(m):
        run = m.group(0)
        if DATE_RE.fullmatch(run.strip()):
            return run
        if sum(1 for c in run if c.isdigit()) < DIGITS_FOR_A_PHONE:
            return run
        return "[telephone withheld]"

    return RUN_RE.sub(one, s).strip() or None


def shortish(s):
    """How many digit runs this text carries that are too short for the threshold."""
    n = 0
    for run in RUN_RE.findall(s or ""):
        d = sum(1 for c in run if c.isdigit())
        if 7 <= d < DIGITS_FOR_A_PHONE and not DATE_RE.fullmatch(run.strip()):
            n += 1
    return n


def apply_url(link):
    """(url to emit, what was withheld).

    **The test is whether the address opens a conversation with a person**, not
    whether it is social: `wa.me/963…` and `t.me/…` are how you reach someone, so
    they go; a form, a careers page or a profile page is where the job is
    described, so it stays. And an address we cannot read as an address — a
    scheme of its own, a host with no registrable name («http://www. homs», typed
    by the employer) — is not emitted either, because we would be publishing a
    link nobody can follow.
    """
    link = (link or "").strip()
    if not link:
        return None, None
    parts = urllib.parse.urlsplit(link)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return None, "application_link"          # mailto:, tel:, or not an address at all
    host = parts.netloc.lower().split("@")[-1].split(":")[0]
    if not HOSTNAME_RE.fullmatch(host):
        return None, "application_link"
    if host.startswith("www."):
        host = host[4:]
    if host in MESSAGING:
        return None, "application_link"
    return link, None


def label(maps, field, token):
    token = (token or "").strip() or None
    if not token:
        return None, None
    return maps.get(field, {}).get(token), token


def filed_a_number(v):
    """**`phone` is «0» on 92 of the 888 adverts** — a placeholder the form left, not
    a number. `withheld_fields` must name what was THERE: claiming to have withheld
    a number nobody filed is a second kind of false statement, quieter than the
    first. Six digits is the floor; Syrian numbers are ten."""
    return sum(1 for c in str(v or "") if c.isdigit()) >= 6


def record(j, maps, stamp):
    withheld = []
    if filed_a_number(j.get("phone")):
        withheld.append("phone")
    if j.get("application_email"):
        withheld.append("application_email")
    url, dropped = apply_url(j.get("application_link"))
    if dropped:
        withheld.append(dropped)
    cat, cat_id = label(maps, "category", j.get("category"))
    city, city_id = label(maps, "city", j.get("city"))
    typ, typ_id = label(maps, "type", j.get("job_type"))
    ts = (j.get("timestamp") or "").strip() or None
    salary = j.get("salary") or None
    currency = (str(j.get("currency_type") or "").strip() or None)
    if currency in ("0", "None"):
        currency = None
    r = {
        "source": "wazefnisy", "country": stamp,
        "ledger_id": f"wazefnisy:{j['id']}", "id": j["id"],
        "url": f"https://{HOST}{BASE}job_details.php?id={j['id']}",
        "title": scrub(j.get("job_title")),
        "employer": scrub(j.get("company_name")),
        "city": city, "city_id": city_id,
        "category": cat, "category_id": cat_id,
        "employment_type": typ, "employment_type_id": typ_id,
        "published": ts.split("T")[0] if ts else None,
        "published_at": ts,
        "description": scrub(j.get("description")),
        "views_count": j.get("views_count"),
        "detail_read": False,
        "contacts_withheld": True,
        "withheld_fields": withheld,
    }
    if salary:
        r["salary"] = salary
        r["salary_period"] = (j.get("salary_period") or "").strip() or None
        r["currency"] = currency
    if url:
        r["apply_url"] = url
    if j.get("is_premium"):
        r["featured"] = True
    if j.get("is_urgent"):
        r["urgent"] = True
    return r


def board():
    url = f"https://{HOST}{BASE}api.php?action=get_jobs"
    code, body = request(url, accept="application/json")
    if code == 404:
        die(f"{url}: HTTP 404 — the board's own endpoint is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    try:
        data = json.loads(body)
    except ValueError as e:
        die(f"{url}: 200 with {th(len(body))} chars that are not JSON: {e}", EXIT_PARTIAL)
    if not isinstance(data, dict) or "jobs" not in data:
        die(f"{url}: 200 with JSON that carries no `jobs`: keys {sorted(data)[:6] if isinstance(data, dict) else type(data).__name__}", EXIT_PARTIAL)
    if not data.get("success"):
        die(f"{url}: the API answered `success: false` — it refused the request, it did not say the board is empty", EXIT_PARTIAL)
    jobs = data["jobs"]
    if not isinstance(jobs, list):
        die(f"{url}: `jobs` is {type(jobs).__name__}, not a list", EXIT_PARTIAL)
    return jobs


def cmd_labels(a):
    maps, ok = read_labels()
    for field in ("category", "city", "type"):
        for k, v in sorted(maps[field].items()):
            print(json.dumps({"field": field, "id": k, "name": v}, ensure_ascii=False))
    note(f"{th(len(maps['category']))} categories, {th(len(maps['city']))} cities, "
         f"{th(len(maps['type']))} types — read from the site's own script"
         + ("" if ok else "; at least one list could not be parsed"))


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    since = None
    if a.since:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.since):
            die(f"--since {a.since}: wants YYYY-MM-DD")
        since = a.since
    maps, labels_ok = read_labels()
    for opt, field in (("city", "city"), ("category", "category"), ("type", "type")):
        want = getattr(a, opt)
        if want and maps[field] and want not in maps[field]:
            die(f"--{opt} {want}: the site does not name that id. It names: "
                f"{', '.join(sorted(maps[field]))}", EXIT_BROKEN)
    jobs = board()
    received = len(jobs)
    rows, seen, bad_id, dropped_filter = [], set(), 0, 0
    premium, urgent, no_salary, unmapped, short_runs = 0, 0, 0, set(), 0
    for j in jobs:
        if not isinstance(j, dict) or j.get("id") in (None, ""):
            bad_id += 1
            continue
        if j["id"] in seen:
            continue
        seen.add(j["id"])
        if j.get("is_premium"):
            premium += 1
        if j.get("is_urgent"):
            urgent += 1
        if not j.get("salary"):
            no_salary += 1
        for field, key in (("category", "category"), ("city", "city"), ("type", "job_type")):
            tok = (j.get(key) or "").strip()
            if tok and maps[field] and tok not in maps[field]:
                unmapped.add(f"{field}:{tok}")
        if a.city and j.get("city") != a.city:
            dropped_filter += 1
            continue
        if a.category and j.get("category") != a.category:
            dropped_filter += 1
            continue
        if getattr(a, "type") and j.get("job_type") != getattr(a, "type"):
            dropped_filter += 1
            continue
        if since and (j.get("timestamp") or "")[:10] < since:
            dropped_filter += 1
            continue
        short_runs += sum(shortish(j.get(f)) for f in ("job_title", "company_name", "description"))
        rows.append(record(j, maps, stamp))
        if a.max and len(rows) >= a.max:
            break

    for r in rows:
        print(json.dumps(r, ensure_ascii=False))

    kept = len(seen) - dropped_filter if not a.max else len(rows)
    note(f"{th(len(rows))} emitted, the API sent {th(received)}"
         + (f"; {th(dropped_filter)} left out by the filters given" if dropped_filter else "")
         + (f"; {th(bad_id)} record(s) carried no id and were not emitted — the board sent them, we could not key them" if bad_id else "")
         + (f"; stopped by --max at {th(a.max)}" if a.max and len(rows) >= a.max else "")
         + ". The board states no total of its own: the array the API sends IS the board.")
    if received and len(rows) + dropped_filter + bad_id < received:
        note(f"{th(received - len(rows) - dropped_filter - bad_id)} short — the API sent adverts "
             f"this run neither emitted nor explained; that is a defect, not a filter.")
    note(f"contacts never emitted: phone and application e-mail dropped, messaging links dropped, "
         f"free text scrubbed; `withheld_fields` names them advert by advert.")
    if short_runs:
        note(f"{th(short_runs)} digit run(s) of 7–8 digits were left as written — the threshold is "
             f"{DIGITS_FOR_A_PHONE} digits, and this is what it costs.")
    note(f"featured {th(premium)} of {th(len(seen))}, urgent {th(urgent)} of {th(len(seen))} — "
         f"the site sells both; the record carries the flag only when it is set.")
    if no_salary:
        note(f"{th(no_salary)} of {th(len(seen))} advert(s) state no salary — the field is absent, not zero.")
    if unmapped:
        note(f"{th(len(unmapped))} token(s) the site's own script does not name, emitted raw: "
             f"{', '.join(sorted(unmapped))}")
    if not labels_ok:
        note("labels_read: false — at least one of the site's lists was not parsed; ids are the datum.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the API carries no country field.")
    if not rows:
        note("0 emitted — check the filters before reading this as an empty board.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Wazefni Syria — the whole board in one request to its own api.php, the Arabic labels read from the site's own script. Issue #650.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the whole board (2 requests)")
    j.add_argument("--city", help="the site's own city id (see `labels`)")
    j.add_argument("--category", help="the site's own category id (see `labels`)")
    j.add_argument("--type", help="the site's own employment-type id (see `labels`)")
    j.add_argument("--since", help="keep adverts filed on or after YYYY-MM-DD")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the API carries none)")
    j.add_argument("--max", type=int, default=0, help="stop after N emitted (0 = the board)")
    j.set_defaults(fn=cmd_jobs)
    l = sub.add_parser("labels", help="the site's own ids and their Arabic names (1 request)")
    l.set_defaults(fn=cmd_labels)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
