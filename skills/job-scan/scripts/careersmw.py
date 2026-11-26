#!/usr/bin/env python3
"""Careers Malawi (`careersmw.com`) — a WordPress job board whose WHOLE list is
one server-rendered page, and whose count is stated by an enumerator that is
not our extraction (#677).

**THE LIST IS ONE REQUEST.** The home page renders 50 cards and a «Load more
jobs» button whose `href` is the no-JavaScript fallback `/?job_all=1`; that URL
renders EVERY card. Measured 2026-11-26 20:03 UTC (HTTP 200, 186 589 B):
**101 cards, 101 distinct `/job/<id>/` links, and no further «load more».**

**THREE ENUMERATORS, THE SAME 101 MEMBERS.** Measured the same hour:

    /?job_all=1                              101 cards
    /wp-json/wp/v2/job_listing (2 pages)     101 records   (100 + 1)
    /wp-sitemap-posts-job_listing-1.xml      101 <loc>

*They were compared MEMBER BY MEMBER, not by size — two sets of the same size
say nothing about which members they hold — and the intersection is 101 on
both sides.* So the count this tool prints beside its own is the REST
collection's `X-WP-Total`, read on its own request: a witness that is NOT our
extraction.

**THE CARD CARRIES WHAT THE AD PAGE DOES NOT.** Each card is
`<article class="cmw-cjm-job-card">` with the title, `cmw-cjm-meta`
(«Employer · City, Malawi»), the contract type, `<time datetime=…>` for the
posting and «Expires <date>». The ad page's own header `job-single-meta` is
EMPTY and carries no JSON-LD, and the REST record's `meta` is `[]` — so the
employer and the place exist ONLY on the card. *Measured on one ad page and on
the 101 REST records; a later theme may move them, and then `company` comes
back null rather than guessed.*

**NOT EVERY CARD IS A JOB, AND NONE IS DROPPED.** The contract type is emitted
as `type`; on 2026-11-26 one card was a supplier prequalification (type
«Other») and one a training. *A filter written from two specimens would be a
guess about the next one; the type is the host's own declaration and the
reader decides.* The end line counts them.

**CONTACTS.** The card carries none. The ad body (`ad <id>`, read from the
REST record's `content`) does — four e-mail addresses on the first record
measured — and they are taken out and NAMED in `withheld_fields`, from what
was actually taken, never from what a field could hold.

Rules: `User-agent: *` / `Disallow: /wp-admin/` / `Allow:
/wp-admin/admin-ajax.php`; no `Crawl-delay`, so the cadence is ours (one
second, and the list is one request anyway).
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

HOST = "careersmw.com"
LIST = f"https://{HOST}/?job_all=1"
REST = f"https://{HOST}/wp-json/wp/v2/job_listing"
TAG = "careersmw"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

CARD_RE = re.compile(r'(?s)<article class="cmw-cjm-job-card[^"]*">(.*?)</article>')
LINK_RE = re.compile(r'(?s)<h3>\s*<a href="([^"]+)"[^>]*>(.*?)</a>')
META_RE = re.compile(r'(?s)<p class="cmw-cjm-meta">(.*?)</p>')
TYPE_RE = re.compile(r'(?s)<span class="cmw-cjm-job-type">(.*?)</span>')
TIME_RE = re.compile(r'<time class="cmw-cjm-posted"[^>]*datetime="([^"]+)"')
EXP_RE = re.compile(r'(?s)<small>\s*Expires\s+(.*?)\s*</small>')
ID_RE = re.compile(r"/job/(\d+)/?$")
TAG_RE = re.compile(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
TEL_RE = re.compile(r"\+\s*\d[\d\s().\-]{7,}\d|(?<!\d)0[189]\d{2}[\s.]?\d{3}[\s.]?\d{3}(?!\d)")
NOT_A_JOB = ("other", "training")

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


def get(url, accept="text/html"):
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    _PACE.setdefault(host, Pace(host, own=1.0)).wait()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], r.headers
    except urllib.error.HTTPError as e:
        return e.code, decode_body(e.read(), e.headers)[0], e.headers
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


def split_meta(meta):
    """«Employer · City, Malawi» -> (employer, place). Without the separator
    the whole text is the employer and the place is null, never guessed."""
    m = text(meta)
    if not m:
        return None, None
    if " · " in m:
        company, place = m.split(" · ", 1)
        return company.strip() or None, place.strip() or None
    return m, None


def card(raw):
    """One list card -> one record. A card without its title link is not a
    record (returns None), and the caller COUNTS those."""
    lk = LINK_RE.search(raw)
    if not lk:
        return None
    url = html.unescape(lk.group(1))
    mid = ID_RE.search(url)
    mm, ty, tm, ex = (META_RE.search(raw), TYPE_RE.search(raw),
                      TIME_RE.search(raw), EXP_RE.search(raw))
    company, place = split_meta(mm.group(1)) if mm else (None, None)
    kind = text(ty.group(1)) if ty else None
    return {
        "id": mid.group(1) if mid else None,
        "ledger_id": f"{TAG}:{mid.group(1)}" if mid else None,
        "url": url,
        "title": text(lk.group(2)) or None,
        "company": company,
        "location_text": place,
        "country": "MW",
        "type": kind,
        "not_a_job_by_type": bool(kind and kind.lower() in NOT_A_JOB),
        "posted": tm.group(1) if tm else None,
        "expires_stated": text(ex.group(1)) if ex else None,
        "salary_stated": False,
    }


def cards(body):
    """Every card of the list page, and how many were seen but unreadable."""
    rows, bad, seen = [], 0, set()
    for raw in CARD_RE.findall(body or ""):
        r = card(raw)
        if r is None:
            bad += 1
            continue
        if r["url"] in seen:
            continue
        seen.add(r["url"])
        rows.append(r)
    return rows, bad


def stated_total():
    """`X-WP-Total` of the REST collection — a count our extraction did not
    produce. None when the host does not state it, and the end line says so."""
    url = f"{REST}?per_page=1&_fields=id"
    status, _, hd = get(url, accept="application/json")
    if status != 200:
        note(f"{url}: HTTP {status} — no stated count this run.")
        return None
    try:
        return int(hd.get("X-WP-Total"))
    except (TypeError, ValueError):
        return None


def cmd_jobs(a):
    v = robots_verdict(HOST)
    if not v["sweep"]:
        die(f"{HOST}: {v['reason']}",
            EXIT_UNKNOWN if v["sweep"] is None else EXIT_REFUSED)
    status, body, _ = get(LIST)
    if status != 200:
        die(f"{LIST}: HTTP {status} — the status decides, not whether the body "
            f"reads.", EXIT_GONE if status in (404, 410) else EXIT_BROKEN)
    rows, bad = cards(body)
    if not rows and "cmw-cjm-job-card" not in (body or ""):
        die(f"{LIST}: no card of the expected shape (`cmw-cjm-job-card`) in "
            f"{len(body or '')} characters — OUR pattern found nothing; this "
            f"says nothing about whether the board has vacancies.")
    total = stated_total()
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    odd = sum(r["not_a_job_by_type"] for r in rows)
    note(f"{len(rows)} card(s) emitted from one page, {LIST}"
         + (f"; {bad} card(s) seen without a title link and NOT emitted" if bad else "")
         + (f"; {odd} of them typed by the host as «Other» or «Training», emitted "
            f"with `not_a_job_by_type: true` and never dropped" if odd else "")
         + ". " + (f"The REST collection states {total} `job_listing` record(s) "
                   f"(`X-WP-Total`), a count our extraction did not make"
                   if total is not None else
                   "The host stated NO count this run, so completeness rests on "
                   "this one page alone and is not established"))
    if total is not None and len(rows) < total:
        note(f"{total - len(rows)} short of the stated count — partial, and the "
             f"exit code says so.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    pid = a.id.strip().rstrip("/").split("/")[-1]
    if not pid.isdigit():
        die(f"{a.id}: an ad is named by its numeric id (`/job/<id>/`).")
    url = f"{REST}/{pid}?_fields=id,link,date_gmt,title,content"
    status, body, _ = get(url, accept="application/json")
    if status != 200:
        die(f"{url}: HTTP {status}", EXIT_GONE if status in (404, 410) else EXIT_BROKEN)
    try:
        post = json.loads(body)
    except ValueError as e:
        die(f"{url}: our parser did not read JSON there ({e})")
    desc, taken = scrub(text((post.get("content") or {}).get("rendered")))
    r = {"id": str(post.get("id")), "ledger_id": f"{TAG}:{post.get('id')}",
         "url": post.get("link"),
         "title": text((post.get("title") or {}).get("rendered")) or None,
         "posted": (post["date_gmt"] + "Z") if post.get("date_gmt") else None,
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
    s.set_defaults(func=cmd_jobs)
    s = sub.add_parser("ad", help="one ad's body, contacts taken out")
    s.add_argument("id", help="the numeric id, or the ad's URL")
    s.set_defaults(func=cmd_ad)
    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
