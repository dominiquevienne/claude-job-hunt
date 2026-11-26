#!/usr/bin/env python3
"""Motravay (`motravay.mu`, Mauritius) — a front that LOOKS client-rendered at
its root and whose `/jobs` is rendered by the SERVER, cards and count
included (#700).

**THE PREMISE OF THE ISSUE WAS THE ROOT, NOT THE LIST.** The card of
2026-09-18 read the root: «a front with `/jobs` and no card». `/jobs` itself,
read 2026-11-26 21:1x UTC (HTTP 200, 62 427 B), carries **8 cards**
(`<a data-testid="job-card-<uuid>" href="/jobs/<CODE>/<n>-<slug>">`) and the
line «8 results». No API had to be replayed and no browser is needed.

**THE LIST IS THE LIVE INVENTORY, THE SITEMAP IS AN ARCHIVE.** The sitemap the
rules declare (`/api/sitemap.xml`) names **115** `/jobs/<uuid>` pages whose
`lastmod` runs 2026-05-24 to 2026-11-25; the 8 cards of the list are a strict
subset of them, compared MEMBER BY MEMBER by uuid. So the sitemap is not
walked: it would emit 107 pages the list no longer shows. The count printed
beside ours is the list's own «N results» — the host's count, not our
extraction.

**EACH FIELD IS READ BY ITS ICON, NEVER BY ITS POSITION.** The card's meta
spans carry a `lucide-map-pin` (place), a `lucide-briefcase` (category) and,
when present, a `lucide-banknote` (salary, 1 card of 8); the contract type is
the pill, the date the right-hand span in `M/D/YYYY`. *On the 8 cards of
2026-11-26 the spans always come in that order, so a positional read gives
the SAME result today — measured by mutation, which stayed green on the real
cards. The icon read is chosen because it does not depend on an order nothing
guarantees; whether the order ever varies on this board is NOT established.*

**THE EMPLOYER IS IN THE AD, AND IT IS SOMETIMES THE BOARD.** The card names
no employer; the ad's `JobPosting` does, as `hiringOrganization`. On
2026-11-26 the ad of code `MAD` named «MADO Parfums & Co.ltd» and the ad of
code `MOT` measured named «Motravay.mu», the board itself. *An earlier
sentence here said the employer was never stated; it was read on one `MOT` ad
and was false of the `MAD` one.* So `jobs` reads each ad (one request each,
`--no-details` stops at one request in all) and emits the name AS STATED in
`company`; whether a `MOT` ad is the board's own vacancy or a client's is NOT
established.

Rules: `Allow: /`, refused in writing: `/admin`, `/employer`, `/candidate`,
`/inbox`, `/login`, `/register`. This tool asks for exactly two path shapes,
`/jobs` and `/jobs/<CODE>/<slug>`, and refuses any other after the rules and
before a byte leaves.
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

HOST = "motravay.mu"
LIST = f"https://{HOST}/jobs"
TAG = "motravay"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ALLOWED_PATHS = (re.compile(r"^/jobs$"), re.compile(r"^/jobs/[A-Z]+/[A-Za-z0-9-]+$"))

CARD_RE = re.compile(r'(?s)<a data-testid="job-card-([0-9a-f-]{36})" class="[^"]*" '
                     r'href="(/jobs/[A-Z]+/[A-Za-z0-9-]+)"[^>]*>(.*?)</a>')
TITLE_RE = re.compile(r"(?s)<h3[^>]*>(.*?)</h3>")
PILL_RE = re.compile(r'(?s)<span class="shrink-0 [^"]*rounded-full[^"]*">(.*?)</span>')
META_RE = re.compile(r'(?s)<span class="inline-flex items-center gap-1\.5">\s*'
                     r'<svg[^>]*class="[^"]*lucide-([a-z-]+)[^"]*"[^>]*>.*?</svg>(.*?)</span>')
DATE_RE = re.compile(r'<span class="ml-auto">\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*</span>')
COUNT_RE = re.compile(r">\s*(\d+)\s+results?\s*<")
LD_RE = re.compile(r'(?s)<script[^>]*application/ld\+json[^>]*>(.*?)</script>')
TAG_RE = re.compile(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
TEL_RE = re.compile(r"\+\s*230[\d\s().\-]{6,}\d|(?<!\d)[2-9]\d{2,3}[\s.\-]?\d{4}(?!\d)")
ICON = {"map-pin": "location_text", "briefcase": "category", "banknote": "salary_text"}

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
    if parts.netloc != HOST or not any(p.match(parts.path) for p in ALLOWED_PATHS):
        die(f"{url}: not one of the two path shapes this tool asks for — never sent",
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


def card(uuid, href, raw):
    t = TITLE_RE.search(raw)
    pill = PILL_RE.search(raw)
    r = {"id": uuid, "ledger_id": f"{TAG}:{uuid}", "url": f"https://{HOST}{href}",
         "title": text(t.group(1)) if t else None, "company": None,
         "location_text": None, "category": None, "salary_text": None,
         "country": "MU", "type": text(pill.group(1)) if pill else None,
         "posted": None}
    for icon, val in META_RE.findall(raw):
        key = ICON.get(icon)
        if key and r[key] is None:
            r[key] = text(val) or None
    d = DATE_RE.search(raw)
    if d:
        mo, dy, yr = map(int, d.groups())
        try:
            r["posted"] = datetime.date(yr, mo, dy).isoformat()
        except ValueError:
            pass
    r["salary_stated"] = r["salary_text"] is not None
    return r


def cards(body):
    rows, seen = [], set()
    for uuid, href, raw in CARD_RE.findall(body or ""):
        if uuid in seen:
            continue
        seen.add(uuid)
        rows.append(card(uuid, href, raw))
    return rows


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


def cmd_jobs(a):
    v = robots_verdict(HOST)
    if not v["sweep"]:
        die(f"{HOST}: {v['reason']}",
            EXIT_UNKNOWN if v["sweep"] is None else EXIT_REFUSED)
    status, body = get(LIST)
    if status != 200:
        die(f"{LIST}: HTTP {status} — the status decides, not whether the body "
            f"reads.", EXIT_GONE if status in (404, 410) else EXIT_BROKEN)
    rows = cards(body)
    stated = stated_count(body)
    if not rows and stated != 0:
        die(f"{LIST}: no card of the expected shape (`data-testid=\"job-card-…\"`) — "
            f"OUR pattern found nothing; this says nothing about the board.")
    misses = 0
    todo = rows[:a.limit] if a.limit else rows
    if a.details:
        for r in todo:
            st, ad = get(r["url"])
            jp = posting(ad) if st == 200 else None
            org = (jp or {}).get("hiringOrganization") or {}
            name = org.get("name") if isinstance(org, dict) else None
            if not name:
                misses += 1
                continue
            r["company"] = name
            r["valid_through_stated"] = jp.get("validThrough") or None
    for r in todo:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{len(rows)} card(s) emitted from one page, {LIST}"
         + (f"; {misses} ad(s) named no employer, `company` stays null" if misses else "")
         + ". "
         + (f"The page itself states {stated} result(s), a count our extraction "
            f"did not make" if stated is not None else
            "The page stated NO count this run, so completeness is not established")
         + ". The sitemap is an ARCHIVE of past ads and is not walked.")
    if stated is not None and len(rows) < stated:
        note(f"{stated - len(rows)} short of the stated count — a pager this tool "
             f"has never seen may have appeared; partial, and the exit code says so.")
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
    loc = ((jp.get("jobLocation") or {}).get("address") or {})
    desc, taken = scrub(text(jp.get("description")))
    r = {"url": url, "title": text(jp.get("title")) or None,
         "posted_by_stated": org.get("name") if isinstance(org, dict) else None,
         "locality_stated": loc.get("addressLocality") if isinstance(loc, dict) else None,
         "posted": jp.get("datePosted") or None,
         "valid_through_stated": jp.get("validThrough") or None,
         "type": jp.get("employmentType") or None,
         "description": desc, "description_chars": len(desc),
         "withheld_fields": taken or None}
    if withheld_a_contact(taken):
        r["contacts_withheld"] = True
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="every card of the live list")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-details", dest="details", action="store_false",
                   help="skip the ad pages: no employer, one request in all")
    s.set_defaults(func=cmd_jobs)
    s = sub.add_parser("ad", help="one ad's JobPosting, contacts taken out")
    s.add_argument("url", help="the ad's URL or its /jobs/<CODE>/<slug> path")
    s.set_defaults(func=cmd_ad)
    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
