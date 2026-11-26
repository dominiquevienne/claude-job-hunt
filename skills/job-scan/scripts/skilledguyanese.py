#!/usr/bin/env python3
"""SkilledGuyanese (`skilledguyanese.com`, Guyana) — a Nuxt board rendered on
the server, 50 cards a page, whose count is stated on the page (#704).

**THE COUNT IS STATED AND THE WALK REACHES IT.** The list page carries
«<N> Jobs» in its header. Measured 2026-11-26 21:2x UTC: «206 Jobs», and
`/?page=1` to `/?page=5` render 50 · 50 · 50 · 50 · 6 cards — **206 distinct
`/job/<opaque id>`** — while `/?page=6` renders none. The walk stops on the
first page that adds no new id, and the end line prints the stated count
beside ours.

**IT IS NOT A MIRROR OF GUYANAINDEX, measured member by member.** The issue
noted that «the first titles are those of `guyanaindex.com/jobs`». The same
evening GuyanaIndex's `/jobs/all/<n>` carried 48 ads over 3 pages, and the two
inventories share **3 normalised titles out of 167 and 42** — «accountant»,
«executive assistant», «sales representative» — whose SkilledGuyanese
employers are three distinct companies. Two boards, not two enumerators of
one inventory; the September observation was true of its two first titles
and is not true of the inventories today.

**THE CARD CARRIES THE FIELDS.** Title (`text-lg font-bold`), employer
(`/company/<id>` link), place (the italic «- Town, Guyana»), contract type (the
first uppercase pill) and «Expire <d> <Mon>, <yyyy>». `ad <id>` reads the ad's
`JobPosting` for its body, contacts taken out and named.

Rules: `User-agent: *` / `Allow: /`, sitemap declared, no `Crawl-delay`; the
cadence is ours. Only `/` (with `?page=N`) and `/job/<id>` are ever asked for.
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

HOST = "skilledguyanese.com"
TAG = "skilledguyanese"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ALLOWED_PATHS = (re.compile(r"^/$"), re.compile(r"^/job/[A-Za-z0-9_-]+$"))

CARD_RE = re.compile(r'(?s)<div class="job-list__item p-3 sm:p-4">(.*?)</a></div></div></div></div>')
TITLE_RE = re.compile(r'(?s)<a href="/job/([A-Za-z0-9_-]+)" class="text-lg font-bold[^"]*">(.*?)</a>')
COMPANY_RE = re.compile(r'(?s)<a href="/company/([A-Za-z0-9_-]+)"[^>]*>\s*<small class="font-semibold"[^>]*>(.*?)</small>')
PLACE_RE = re.compile(r'(?s)<small class="italic text-gray-400">(.*?)</small>')
TYPE_RE = re.compile(r'(?s)<div class="flex items-center uppercase"[^>]*>\s*<div class="[^"]*rounded-sm p-1[^"]*">(.*?)</div>')
EXPIRE_RE = re.compile(r"Expire\s+(\d{1,2})\s+([A-Z][a-z]{2}),\s*(\d{4})")
COUNT_RE = re.compile(r'(?s)<div class="text-gray-900">\s*(\d+)\s*<strong[^>]*>\s*</strong>\s*Jobs\s*</div>')
LD_RE = re.compile(r'(?s)<script[^>]*application/ld\+json[^>]*>(.*?)</script>')
TAG_RE = re.compile(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
TEL_RE = re.compile(r"\+\s*592[\d\s().\-]{6,}\d|(?<!\d)[2-7]\d{2}[\s.\-]?\d{4}(?!\d)")
MONTHS = {m: i for i, m in enumerate(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",
                                      "Aug", "Sep", "Oct", "Nov", "Dec"), 1)}

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


def card(raw):
    t = TITLE_RE.search(raw)
    if not t:
        return None
    jid = t.group(1)
    co, pl, ty, ex = (COMPANY_RE.search(raw), PLACE_RE.search(raw),
                      TYPE_RE.search(raw), EXPIRE_RE.search(raw))
    place = text(pl.group(1)).lstrip("-").strip() if pl else None
    expires = None
    if ex and ex.group(2) in MONTHS:
        try:
            expires = datetime.date(int(ex.group(3)), MONTHS[ex.group(2)],
                                    int(ex.group(1))).isoformat()
        except ValueError:
            pass
    return {"id": jid, "ledger_id": f"{TAG}:{jid}", "url": f"https://{HOST}/job/{jid}",
            "title": text(t.group(2)) or None,
            "company": text(co.group(2)) if co else None,
            "company_id": co.group(1) if co else None,
            "location_text": place or None, "country": "GY",
            "type": text(ty.group(1)) if ty else None,
            "expires_stated": expires, "salary_stated": False}


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


def cmd_jobs(a):
    v = robots_verdict(HOST)
    if not v["sweep"]:
        die(f"{HOST}: {v['reason']}",
            EXIT_UNKNOWN if v["sweep"] is None else EXIT_REFUSED)
    seen, rows, bad, stated, pages, ended = set(), [], 0, None, 0, False
    for page in range(1, a.max_pages + 1):
        url = f"https://{HOST}/?page={page}"
        status, body = get(url)
        if status != 200:
            die(f"{url}: HTTP {status} — the status decides.",
                EXIT_GONE if status in (404, 410) else EXIT_BROKEN)
        if stated is None:
            stated = stated_count(body)
        got, b = cards(body)
        bad += b
        pages = page
        new = [r for r in got if r["id"] not in seen]
        if not new:
            ended = True
            break
        for r in new:
            seen.add(r["id"])
            rows.append(r)
    if not rows and stated != 0:
        die(f"https://{HOST}/: no card of the expected shape (`job-list__item`) — "
            f"OUR pattern found nothing; this says nothing about the board.")
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    end = ("the walk ended on a page that added no new ad" if ended
           else f"stopped at the --max-pages ceiling of {a.max_pages}")
    note(f"{len(rows)} card(s) emitted over {pages} page(s) — {end}"
         + (f"; {bad} card(s) seen without a title link and NOT emitted" if bad else "")
         + ". " + (f"The page states {stated} job(s), a count our extraction did "
                   f"not make" if stated is not None else
                   "The page stated NO count this run, so completeness is not established"))
    if (stated is not None and len(rows) < stated) or not ended:
        note("short of the stated count, or the walk did not end on its own — "
             "partial, and the exit code says so.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    jid = a.id.rstrip("/").split("/")[-1]
    url = f"https://{HOST}/job/{jid}"
    status, body = get(url)
    if status != 200:
        die(f"{url}: HTTP {status}", EXIT_GONE if status in (404, 410) else EXIT_BROKEN)
    jp = posting(body)
    if jp is None:
        die(f"{url}: no JobPosting on the page — OUR reader found none.")
    org = jp.get("hiringOrganization") or {}
    desc, taken = scrub(text(jp.get("description")))
    r = {"id": jid, "url": url, "title": text(jp.get("title")) or None,
         "company": org.get("name") if isinstance(org, dict) else None,
         "posted": jp.get("datePosted") or None,
         "valid_through_stated": jp.get("validThrough") or None,
         "description": desc, "description_chars": len(desc),
         "withheld_fields": taken or None}
    if withheld_a_contact(taken):
        r["contacts_withheld"] = True
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="every card, page by page, newest first")
    s.add_argument("--limit", type=int)
    s.add_argument("--max-pages", type=int, default=12, dest="max_pages")
    s.set_defaults(func=cmd_jobs)
    s = sub.add_parser("ad", help="one ad's JobPosting, contacts taken out")
    s.add_argument("id", help="the opaque id or the ad's URL")
    s.set_defaults(func=cmd_ad)
    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
