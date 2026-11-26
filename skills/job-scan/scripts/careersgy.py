#!/usr/bin/env python3
"""Careers.gy (`careers.gy`, Guyana) — an Angular shell whose list lives on a
DIFFERENT host, `api.careers.gy`, and whose public collection still serves the
ads its own `expires_at` has closed (#706).

**THE ROUTE WAS FOUND WHERE THE CLIENT IS BUILT, NOT IN A CONSTANT.** Every
path of `careers.gy` returns the same 79 442-byte shell (`<app-root></app-root>`,
nothing rendered). The environment object in `main-*.js` names
`apiUrl: https://api.careers.gy/public/`; an HTTP interceptor prefixes it to
every relative URL; the generic service composes `api/${baseUrl}`; and the
jobs service is `super(http, "jobs")`, in a chunk reached by walking the
import graph (39 chunks). So the list is
`https://api.careers.gy/public/api/jobs?page=N` — 25 a page, `per_page`
ignored, Laravel paginator fields (`total`, `last_page`).

**THE SAME OBJECT CARRIES A CLIENT SECRET FOR A PASSWORD GRANT, AND IT IS
NEVER USED.** The public collection answers with no credential at all; this
tool sends none, and an `Authorization` header is never built here. The
application form needs a Google account and stays out of scope.

**BOTH HOSTS WRITE NO RULE.** `careers.gy/robots.txt` is the SPA shell (byte
for byte the root) and `api.careers.gy/robots.txt` is Laravel's welcome page:
`_robots` reads both as `state: unrecognised`, an absence of rules — open by
the owner's decision of 13.09.2026, `certain: False`, and the guard is still
taken on the API host itself, never on the front's.

**THE HOST STILL SERVES CLOSED ADS, AND THIS TOOL SAYS SO RATHER THAN FILTER
IN SILENCE.** Measured 2026-11-26 21:5x UTC on all 30 pages: **748 records,
748 distinct, all `status_id` 2, none deleted — and 652 have an `expires_at`
in the past** (created 2021-08-03 to 2026-11-24). The public page's own query
(`salary_from=0&salary_to=1000000&sort_by=created_at|desc`) returns 735, so
the site lists them too; the 13 of difference are records whose salary the
range filter excludes, not closed ones. By default only the records whose
`expires_at` has not passed are emitted — the host's own field, not a guess —
and the end line counts the rest; `--include-expired` emits them flagged.

**CONTACTS.** The description is employer prose; 7 of the 96 live records
carry an `@` and 5 an address the scrub recognises. It is scrubbed and what was taken is named.
"""
import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import datetime
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path
from _robots import verdict as robots_verdict
from _ua import UA
from _withheld import withheld_a_contact

API_HOST = "api.careers.gy"
FRONT = "https://careers.gy"
LIST = f"https://{API_HOST}/public/api/jobs"
TAG = "careersgy"
GUYANA = 1        # `country_id` of 736 of the 748 records; the other 12 all expired in 2022

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ALLOWED_PATHS = (re.compile(r"^/public/api/jobs$"),)

TAG_RE = re.compile(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
TEL_RE = re.compile(r"\+\s*592[\d\s().\-]{6,}\d|(?<!\d)[2-7]\d{2}[\s.\-]?\d{4}(?!\d)")

_PACE = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[{TAG}] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts), agents=("claude-user",))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    if parts.netloc != API_HOST or not any(p.match(parts.path) for p in ALLOWED_PATHS):
        die(f"{url}: not the one path this tool asks for — never sent", EXIT_REFUSED)


def get(url):
    gate(url)
    _PACE.setdefault(API_HOST, Pace(API_HOST, own=1.0)).wait()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, decode_body(e.read(), e.headers)[0]
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(raw):
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub(" ", raw or ""))).strip()


def scrub(s):
    """Take contacts out, and say which kinds were ACTUALLY taken."""
    taken, out = [], s or ""
    if MAIL_RE.search(out):
        taken.append("email")
        out = MAIL_RE.sub("[e-mail withheld]", out)
    if TEL_RE.search(out):
        taken.append("telephone")
        out = TEL_RE.sub("[telephone withheld]", out)
    return out, taken


def expired(rec, today):
    """True when the record's OWN `expires_at` is before today, None when it
    states none — an absent date is never read as open or as closed."""
    e = (rec.get("expires_at") or "")[:10]
    return None if not e else e < today


def record(rec, today):
    desc, taken = scrub(text(rec.get("description")))
    hid = rec.get("hash_id")
    r = {"id": str(rec.get("id")), "ledger_id": f"{TAG}:{rec.get('id')}",
         "url": f"{FRONT}/job-post/{hid}" if hid else None,
         "title": text(rec.get("title")) or None,
         "company": text(rec.get("company_name")) or None,
         "country": "GY" if rec.get("country_id") == GUYANA else None,
         "country_id_stated": rec.get("country_id"),
         "type": rec.get("employment_type") or None,
         "remote_stated": bool(rec.get("is_remote_position")),
         "vacancies_stated": rec.get("no_of_vacancies"),
         "posted": rec.get("created_at") or None,
         "expires_stated": rec.get("expires_at") or None,
         "expired_by_stated_date": expired(rec, today),
         "salary_from": rec.get("salary_from"), "salary_to": rec.get("salary_to"),
         "salary_stated": bool(rec.get("salary_from") or rec.get("salary_to")),
         "description": desc, "description_chars": len(desc),
         "withheld_fields": taken or None}
    if withheld_a_contact(taken):
        r["contacts_withheld"] = True
    return r


def cmd_jobs(a):
    v = robots_verdict(API_HOST)
    if not v["sweep"]:
        die(f"{API_HOST}: {v['reason']}",
            EXIT_UNKNOWN if v["sweep"] is None else EXIT_REFUSED)
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    seen, rows, total, last, pages, ended = set(), [], None, None, 0, False
    for n in range(1, a.max_pages + 1):
        url = f"{LIST}?page={n}"
        status, body = get(url)
        if status != 200:
            die(f"{url}: HTTP {status} — the status decides.",
                EXIT_GONE if status in (404, 410) else EXIT_BROKEN)
        try:
            d = json.loads(body)
        except ValueError as e:
            die(f"{url}: our parser did not read JSON there ({e})")
        if total is None:
            total, last = d.get("total"), d.get("last_page")
        data = d.get("data") or []
        pages = n
        new = [x for x in data if x.get("id") not in seen]
        if not new:
            ended = True
            break
        for x in new:
            seen.add(x.get("id"))
            rows.append(record(x, today))
        if last and n >= last:
            ended = True
            break
    closed = sum(1 for r in rows if r["expired_by_stated_date"])
    out = rows if a.include_expired else [r for r in rows if not r["expired_by_stated_date"]]
    for r in out[:a.limit] if a.limit else out:
        print(json.dumps(r, ensure_ascii=False))
    withheld = sum(1 for r in out if r["withheld_fields"])
    note(f"{len(rows)} record(s) read over {pages} page(s) of {LIST}; the host "
         f"states total {total} — a count our extraction did not make. "
         f"{closed} are past their own `expires_at` and are "
         + ("emitted flagged (--include-expired)" if a.include_expired else
            "NOT emitted (--include-expired emits them flagged)")
         + f"; {len(out)} emitted; contacts taken out of {withheld} description(s).")
    if (total is not None and len(rows) < total) or not ended:
        note("short of the stated total, or the walk did not end on its own — "
             "partial, and the exit code says so.")
        sys.exit(EXIT_PARTIAL)


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the live records of the public collection")
    s.add_argument("--limit", type=int)
    s.add_argument("--max-pages", type=int, default=60, dest="max_pages")
    s.add_argument("--include-expired", action="store_true", dest="include_expired",
                   help="also emit the records past their own `expires_at`, flagged")
    s.set_defaults(func=cmd_jobs)
    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
