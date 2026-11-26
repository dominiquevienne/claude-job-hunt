#!/usr/bin/env python3
"""GuyanaIndex Jobs (`www.guyanaindex.com`, Guyana) — the jobs section of a
business directory, paged by PATH and not by query, whose count is stated on
the list (#708).

**THE PAGER IS `/jobs/all/<n>`, AND `?page=N` IS SILENTLY IGNORED.** Measured
2026-11-26 21:2x UTC: `/jobs/all?page=2` … `?page=7` returned the SAME 36 617
bytes, the same md5, six times — page one again. `/jobs/all/2` and `/3` are
distinct, and `/4` onwards carry no ad at all. *A walk on `?page=` would loop
on page one, and a dedup by id would hide it as «one page of 20»: this tool
walks the path form and stops on the first page that adds no new id.*

**THE COUNT IS STATED.** The list says «We found <b>48</b> job offers», and the
three pages carry 20 · 20 · 8 = **48 distinct `/job/<id>/<slug>`**. The end line
prints the stated count beside ours.

**IT IS NOT A MIRROR OF SKILLEDGUYANESE**, measured member by member the same
evening (#704): the two inventories share 3 normalised titles out of 42 and
167, whose SkilledGuyanese employers are three distinct companies.

**THE CARD, AND WHAT IT LACKS.** The card carries the title, the employer
(`/company/<id>/<slug>`), an excerpt, a RELATIVE date («1 day ago») and two
fields named by their icons — `fa-suitcase` (the kind, «Employee») and
`fa-clock-o` (the schedule, «Full Time»). It carries no place and no absolute
date: those are in the ad's `JobPosting` (`datePosted`, `jobLocation`,
`validThrough`), one request per ad; `--no-details` stops at the list pages.
The excerpt is prose an employer typed, so it goes through the same scrub as
the ad body, and what is taken is named.

Rules: `User-agent: *` with a list of refused paths (`/user/*`, `/redir/*`,
`/admin/`, …) none of which this tool asks for; only `/jobs/all`,
`/jobs/all/<n>` and `/job/<id>/<slug>` ever leave.
"""
import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
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

HOST = "www.guyanaindex.com"
TAG = "guyanaindex"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ALLOWED_PATHS = (re.compile(r"^/jobs/all(/\d+)?$"), re.compile(r"^/job/\d+/[a-z0-9-]+$"))

CARD_RE = re.compile(r'(?s)<div class="company">\s*<div class="company_header">(.*?)<div class="company_btns')
TITLE_RE = re.compile(r'(?s)<h3><a href="(/job/(\d+)/[a-z0-9-]+)">(.*?)</a></h3>')
EMP_RE = re.compile(r'(?s)<strong><a href="/company/(\d+)/[^"]*">(.*?)</a></strong>')
DESC_RE = re.compile(r'(?s)<div class="cont desc">(.*?)</div>')
STAT_RE = re.compile(r'(?s)<i class="[^"]*\b(fa-[a-z-]+)"[^>]*></i>\s*<span>(.*?)</span>')
COUNT_RE = re.compile(r"We found\s*<b>\s*(\d+)\s*</b>\s*job offers?")
LD_RE = re.compile(r'(?s)<script[^>]*application/ld\+json[^>]*>(.*?)</script>')
TAG_RE = re.compile(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
TEL_RE = re.compile(r"\+\s*592[\d\s().\-]{6,}\d|(?<!\d)[2-7]\d{2}[\s.\-]?\d{4}(?!\d)")
STATS = {"fa-calendar": "posted_relative_stated", "fa-suitcase": "kind",
         "fa-clock-o": "type"}

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
    if parts.netloc != HOST or parts.query or \
            not any(p.match(parts.path) for p in ALLOWED_PATHS):
        die(f"{url}: not one of the path shapes this tool asks for — never sent",
            EXIT_REFUSED)


def get(url):
    gate(url)
    _PACE.setdefault(HOST, Pace(HOST, own=1.0)).wait()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
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


def stated_count(body):
    m = COUNT_RE.search(body or "")
    return int(m.group(1)) if m else None


def page_url(n):
    return f"https://{HOST}/jobs/all" + ("" if n == 1 else f"/{n}")


def card(raw):
    t = TITLE_RE.search(raw)
    if not t:
        return None
    e, d = EMP_RE.search(raw), DESC_RE.search(raw)
    excerpt, taken = scrub(text(d.group(1))) if d else (None, [])
    r = {"id": t.group(2), "ledger_id": f"{TAG}:{t.group(2)}",
         "url": f"https://{HOST}{t.group(1)}", "title": text(t.group(3)) or None,
         "company": text(e.group(2)) if e else None,
         "company_id": e.group(1) if e else None,
         "location_text": None, "country": "GY",
         "posted_relative_stated": None, "kind": None, "type": None,
         "posted": None, "valid_through_stated": None,
         "excerpt": excerpt or None, "withheld_fields": taken or None,
         "salary_stated": False}
    for icon, val in STAT_RE.findall(raw):
        key = STATS.get(icon)
        if key and r[key] is None:
            r[key] = text(val) or None
    if withheld_a_contact(taken):
        r["contacts_withheld"] = True
    return r


def cards(body):
    rows, bad = [], 0
    for raw in CARD_RE.findall(body or ""):
        r = card(raw)
        if r is None:
            bad += 1
        else:
            rows.append(r)
    return rows, bad


def posting(body):
    for raw in LD_RE.findall(body or ""):
        try:
            d = json.loads(raw)
        except ValueError:
            continue
        for x in (d.get("@graph", [d]) if isinstance(d, dict) else d):
            if isinstance(x, dict) and x.get("@type") == "JobPosting":
                return x
    return None


def details(jp):
    addr = ((jp.get("jobLocation") or {}).get("address") or {})
    return {"posted": jp.get("datePosted") or None,
            "valid_through_stated": jp.get("validThrough") or None,
            "location_text": (addr.get("addressLocality") or None) if isinstance(addr, dict) else None}


def cmd_jobs(a):
    v = robots_verdict(HOST)
    if not v["sweep"]:
        die(f"{HOST}: {v['reason']}",
            EXIT_UNKNOWN if v["sweep"] is None else EXIT_REFUSED)
    seen, rows, bad, stated, pages, ended = set(), [], 0, None, 0, False
    for n in range(1, a.max_pages + 1):
        url = page_url(n)
        status, body = get(url)
        if status != 200:
            die(f"{url}: HTTP {status} — the status decides.",
                EXIT_GONE if status in (404, 410) else EXIT_BROKEN)
        if stated is None:
            stated = stated_count(body)
        got, b = cards(body)
        bad += b
        pages = n
        new = [r for r in got if r["id"] not in seen]
        if not new:
            ended = True
            break
        for r in new:
            seen.add(r["id"])
            rows.append(r)
    if not rows and stated != 0:
        die(f"{page_url(1)}: no card of the expected shape (`company_header`) — OUR "
            f"pattern found nothing; this says nothing about the board.")
    todo = rows[:a.limit] if a.limit else rows
    misses = 0
    if a.details:
        for r in todo:
            st, ad = get(r["url"])
            jp = posting(ad) if st == 200 else None
            if jp is None:
                misses += 1
                continue
            r.update(details(jp))
    for r in todo:
        print(json.dumps(r, ensure_ascii=False))
    withheld = sum(1 for r in rows if r["withheld_fields"])
    end = ("the walk ended on a page that added no new ad" if ended
           else f"stopped at the --max-pages ceiling of {a.max_pages}")
    note(f"{len(rows)} card(s) emitted over {pages} page(s) of `/jobs/all/<n>` — {end}"
         + (f"; {bad} card(s) seen without a title link and NOT emitted" if bad else "")
         + (f"; {misses} ad(s) gave no JobPosting" if misses else "")
         + f"; contacts taken out of {withheld} excerpt(s). "
         + (f"The list states {stated} job offer(s), a count our extraction did "
            f"not make" if stated is not None else
            "The list stated NO count this run, so completeness is not established"))
    if (stated is not None and len(rows) < stated) or not ended:
        note("short of the stated count, or the walk did not end on its own — "
             "partial, and the exit code says so.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = a.url if a.url.startswith("http") else f"https://{HOST}{a.url}"
    status, body = get(url)
    if status != 200:
        die(f"{url}: HTTP {status}", EXIT_GONE if status in (404, 410) else EXIT_BROKEN)
    jp = posting(body)
    if jp is None:
        die(f"{url}: no JobPosting on the page — OUR reader found none.")
    org = jp.get("hiringOrganization") or {}
    desc, taken = scrub(text(jp.get("description")))
    r = {"url": url, "title": text(jp.get("title")) or None,
         "company": org.get("name") if isinstance(org, dict) else None,
         **details(jp), "type": jp.get("employmentType") or None,
         "description": desc, "description_chars": len(desc),
         "withheld_fields": taken or None}
    if withheld_a_contact(taken):
        r["contacts_withheld"] = True
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="every card of /jobs/all/<n>, newest first")
    s.add_argument("--limit", type=int)
    s.add_argument("--max-pages", type=int, default=12, dest="max_pages")
    s.add_argument("--no-details", dest="details", action="store_false",
                   help="skip the ad pages: no place and no absolute date")
    s.set_defaults(func=cmd_jobs)
    s = sub.add_parser("ad", help="one ad's JobPosting, contacts taken out")
    s.add_argument("url", help="the ad's URL or its /job/<id>/<slug> path")
    s.set_defaults(func=cmd_ad)
    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
