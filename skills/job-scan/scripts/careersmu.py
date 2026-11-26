#!/usr/bin/env python3
"""Careers.mu (`careers.mu`, Mauritius) — a WP Job Board Pro site whose whole
list is one page, whose count is STATED by that page, and whose employer lives
only in each ad's JSON-LD (#699).

**THE LIST IS ONE REQUEST.** `/browse-jobs/` paginates 14 a page, and its own
«Per Page» selector offers «All» (`jobs_ppp=-1`). Measured 2026-11-26 20:5x UTC:
`/browse-jobs/?jobs_ppp=-1&filter-orderby=newest` renders **31 cards** and the
line «Showing all 31 results»; the paged form says «Showing 1 – 14 of 31
results». *That line is the host's own count, not our extraction*, and it is
what the end line prints beside ours.

**THREE ENUMERATORS, THE SAME 31 MEMBERS, compared member by member:** that
page (by `post-<id>`), the REST collection `/wp-json/wp/v2/job_listing` (31,
one page) and the `/job/` entries of the All in One SEO sitemap (31).

**WHAT LIVES WHERE.** The card carries the title, the category, the location
term and the contract type — and NOT the employer (its employer block is
empty). The REST record carries `date_gmt` and an empty `meta`. The employer,
the region and `validThrough` are in the ad page's `JobPosting`. So `jobs`
costs 2 requests plus one per ad (`--no-details` stops at 2), paced at one
second.

**THE HOST DECLARES EVERY LISTED AD CLOSED, AND THIS TOOL DOES NOT JUDGE IT.**
On 2026-11-26 all 31 ad pages carried, in their own deadline block,
`<div class="deadline-closed">Application deadline closed.</div>`, beside a
`job-deadline` date that is in the past (on the newest ad it is its posting
day). *An earlier sentence of this docstring said the phrase marked only 4 ads;
it was a substring test, and the phrase is on all 31 — the contingent on the
OPEN-looking ads is what refuted it.* So both are emitted as the host states
them, `deadline_stated` and `deadline_closed_stated`, and nothing here reads
them as liveness: the board still lists the ads, and whether it means it is
NOT established. Four of the 31 carried no `JobPosting` at all, so their
`company` is null; why those four is not established either.

**`validThrough` IS NOT A DEADLINE HERE.** On the first ad measured it is
exactly one year after `datePosted` (2026-11-07 -> 2027-11-07) — a plugin
default, not an employer's closing date. It is emitted as
`valid_through_stated`, and nothing in this tool reads it as liveness.

**THIS HOST ALSO PUBLISHES PEOPLE.** Its REST types include `candidate` and
`job_applicant`, and its sitemap lists candidate pages. This tool requests
exactly three path shapes — the list, `job_listing`, and `/job/<slug>/` — and
`fetch()` refuses any other path before a byte is sent.

Rules: `User-Agent: *` / `Disallow:` (nothing refused), no `Crawl-delay`, so
the cadence is ours.
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

HOST = "careers.mu"
LIST = f"https://{HOST}/browse-jobs/?jobs_ppp=-1&filter-orderby=newest"
REST = f"https://{HOST}/wp-json/wp/v2/job_listing"
TAG = "careersmu"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# the only path shapes this tool may ask for — anything else is refused locally
ALLOWED_PATHS = (re.compile(r"^/browse-jobs/$"),
                 re.compile(r"^/wp-json/wp/v2/job_listing(/\d+)?$"),
                 re.compile(r"^/job/[a-z0-9-]+/?$"))

ART_RE = re.compile(r'(?s)<article id="post-(\d+)" class="map-item layout-job[^"]*".*?</article>')
TITLE_RE = re.compile(r'(?s)<h2 class="job-title"><a href="([^"]+)"[^>]*>(.*?)</a>')
CAT_RE = re.compile(r'(?s)<div class="job-category[^"]*">(.*?)</div>')
LOC_RE = re.compile(r'(?s)<div class="job-location">(.*?)</div>')
TYPE_RE = re.compile(r'(?s)<a class="type-job"[^>]*>(.*?)</a>')
COUNT_RE = re.compile(r'(?s)results-count">\s*Showing\s+(?:all\s+(\d+)|.*?of\s+(\d+))\s+results')
CLOSED = "Application deadline closed."
CLOSED_RE = re.compile(r'<div class="deadline-closed">\s*Application deadline closed\.')
DEADLINE_RE = re.compile(r'(?s)class="job-deadline with-icon">(?:<i[^>]*></i>)?\s*([^<]+?)\s*</div>')
LD_RE = re.compile(r'(?s)<script[^>]*application/ld\+json[^>]*>(.*?)</script>')
TAG_RE = re.compile(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
TEL_RE = re.compile(r"\+\s*230[\d\s().\-]{6,}\d|(?<!\d)[2-9]\d{2,3}[\s.\-]?\d{4}(?!\d)")

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
    # AFTER the rules and BEFORE the request: an open rule is not our consent.
    # This host publishes candidates, so only three path shapes ever leave.
    if parts.netloc != HOST or not any(p.match(parts.path) for p in ALLOWED_PATHS):
        die(f"{url}: not one of the three path shapes this tool asks for — never sent",
            EXIT_REFUSED)


def get(url, accept="text/html"):
    gate(url)
    _PACE.setdefault(HOST, Pace(HOST, own=1.0)).wait()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
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
    if not m:
        return None
    return int(m.group(1) or m.group(2))


def cards(body):
    """Every card of the list page -> records, and the cards seen without a
    title link (counted, never emitted)."""
    rows, bad, seen = [], 0, set()
    for m in ART_RE.finditer(body or ""):
        pid, raw = m.group(1), m.group(0)
        if pid in seen:
            continue
        seen.add(pid)
        t = TITLE_RE.search(raw)
        if not t:
            bad += 1
            continue
        c, lo, ty = CAT_RE.search(raw), LOC_RE.search(raw), TYPE_RE.search(raw)
        rows.append({
            "id": pid,
            "ledger_id": f"{TAG}:{pid}",
            "url": html.unescape(t.group(1)),
            "title": text(t.group(2)) or None,
            "company": None,
            "category": text(c.group(1)) if c else None,
            "location_text": (text(lo.group(1)) or None) if lo else None,
            "country": "MU",
            "type": text(ty.group(1)) if ty else None,
            "posted": None,
            "valid_through_stated": None,
            "deadline_stated": None,
            "deadline_closed_stated": None,
            "salary_stated": False,
        })
    return rows, bad


def posting(body):
    """The ad page's JobPosting as a dict, or None."""
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
    """The fields this board puts ONLY in the JobPosting."""
    org = jp.get("hiringOrganization") or {}
    addr = ((jp.get("jobLocation") or {}).get("address") or {})
    region = addr.get("addressRegion") if isinstance(addr, dict) else None
    return {"company": (org.get("name") or None) if isinstance(org, dict) else None,
            "region_stated": region or None,
            "valid_through_stated": jp.get("validThrough") or None}


def dates():
    url = f"{REST}?per_page=100&_fields=id,date_gmt"
    status, body = get(url, accept="application/json")
    if status != 200:
        note(f"{url}: HTTP {status} — no dates this run; `posted` stays null.")
        return {}
    try:
        return {str(r["id"]): r["date_gmt"] + "Z" for r in json.loads(body)
                if r.get("date_gmt")}
    except (ValueError, KeyError, TypeError):
        note(f"{url}: our parser did not read the records; `posted` stays null.")
        return {}


def cmd_jobs(a):
    v = robots_verdict(HOST)
    if not v["sweep"]:
        die(f"{HOST}: {v['reason']}",
            EXIT_UNKNOWN if v["sweep"] is None else EXIT_REFUSED)
    status, body = get(LIST)
    if status != 200:
        die(f"{LIST}: HTTP {status} — the status decides, not whether the body "
            f"reads.", EXIT_GONE if status in (404, 410) else EXIT_BROKEN)
    rows, bad = cards(body)
    stated = stated_count(body)
    if not rows and stated != 0:
        die(f"{LIST}: no card of the expected shape (`map-item layout-job`) — "
            f"OUR pattern found nothing; this says nothing about the board.")
    when = dates()
    misses, closed = 0, 0
    for r in rows:
        r["posted"] = when.get(r["id"])
    if a.details:
        for r in rows[:a.limit] if a.limit else rows:
            st, ad = get(r["url"])
            if st != 200:
                misses += 1
                continue
            r["deadline_closed_stated"] = bool(CLOSED_RE.search(ad))
            dl = DEADLINE_RE.search(ad)
            r["deadline_stated"] = text(dl.group(1)) if dl else None
            closed += r["deadline_closed_stated"]
            jp = posting(ad)
            if jp is None:
                misses += 1
                continue
            r.update(details(jp))
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{len(rows)} card(s) emitted from one page, {LIST}"
         + (f"; {bad} card(s) seen without a title link and NOT emitted" if bad else "")
         + (f"; {closed} ad page(s) state «{CLOSED}» in their own deadline block "
            f"— still listed by the host, emitted with `deadline_closed_stated: "
            f"true` and never dropped" if closed else "")
         + (f"; {misses} ad page(s) gave no JobPosting, so their `company` stays "
            f"null" if misses else "")
         + ". " + (f"The page itself states {stated} result(s), a count our "
                   f"extraction did not make" if stated is not None else
                   "The page stated NO count this run, so completeness is not "
                   "established"))
    if stated is not None and len(rows) < stated:
        note(f"{stated - len(rows)} short of the stated count — partial, and the "
             f"exit code says so.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = a.url if a.url.startswith("http") else f"https://{HOST}/job/{a.url.strip('/')}/"
    status, body = get(url)
    if status != 200:
        die(f"{url}: HTTP {status}", EXIT_GONE if status in (404, 410) else EXIT_BROKEN)
    jp = posting(body)
    if jp is None:
        die(f"{url}: no JobPosting on the page — OUR reader found none.")
    desc, taken = scrub(text(jp.get("description")))
    r = {"url": url, "title": text(jp.get("title")) or None,
         "posted": jp.get("datePosted") or None, **details(jp),
         "description": desc, "description_chars": len(desc),
         "withheld_fields": taken or None}
    if withheld_a_contact(taken):
        r["contacts_withheld"] = True
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="every card of the list, newest first")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-details", dest="details", action="store_false",
                   help="skip the ad pages: no employer, two requests in all")
    s.set_defaults(func=cmd_jobs)
    s = sub.add_parser("ad", help="one ad's JobPosting, contacts taken out")
    s.add_argument("url", help="the ad's URL or its /job/<slug>/ slug")
    s.set_defaults(func=cmd_ad)
    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
