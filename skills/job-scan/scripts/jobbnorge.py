#!/usr/bin/env python3
"""Jobbnorge (`www.jobbnorge.no`) — Norway's public-sector and academic board (universities, municipalities, counties, the State), through the public API its search page calls itself; the site's own position count printed beside every walk; the contact persons the ad's data carries never leave. Issue #366.

  jobbnorge.py search [--language 1|2] [--limit N]
  jobbnorge.py ad --url <https://www.jobbnorge.no/ledige-stillinger/stilling/<id>[/<slug>]>

THE ROUTE IS THE API THE PAGES CALL — the search page (`/search`) sets `apiUrl =
'https://publicapi.jobbnorge.no/'` and fetches:

  GET https://publicapi.jobbnorge.no/v1/jobs/count            -> 2321   (a bare integer: the site's «treff», which is a count of POSITIONS)
  GET https://publicapi.jobbnorge.no/v3/jobs?language=1       -> {"jobs": [1 078 …]}  — every open posting in ONE answer, no paging

The page prints `#hits` from the count, then overwrites it with the sum of every job's
`positionCount` — and on the day the two agreed: **2 321 positions across 1 078 postings**.
This adapter emits one record per POSTING with its `positionCount`, and prints both figures:
postings emitted, positions summed, positions the site counts — «equal» when the sum is the
count. The rules on `www.jobbnorge.no` (60 B) refuse the PDF of a posting and nothing else;
`publicapi.jobbnorge.no` and `id.jobbnorge.no` write no rule (an absence, certain, open); no
Crawl-delay — 2 s is ours, and a full list is two requests.

THE RECORD (the API's own names): id, title, employer, department (`regardDepartmentAsEmployer`
says which the site shows), summary, publicationDate / deadline (DD.MM.YYYY), jobScope (Heltid /
Deltid / Fast prosent), jobDuration (Fast / Vikariat/Midlertidig / Åremål), jobType, positionCount,
promoted, locations (municipality, county, area, zipCode, isDomestic; the primary one first), link.

THE AD is the posting page's own data — the page is an Angular shell («Laster...») whose client
calls `https://id.jobbnorge.no/api/joblisting?jobId=<id>&languageId=<n>`: `components` (heading,
text, images) and `jobGapComponents` (titled sections: «Om stillingen», «Kvalifikasjoner» …) — the
text; **and `contacts` — name, telephone, title of the persons to call — which is never emitted**;
the text is scrubbed of e-mail addresses and Norwegian telephone numbers all the same.

Measured 2026-09-14 00:5x UTC by the declared client: count 2 321, jobs 1 078 (sum of
positionCount 2 321 — equal), one ad read. `--language 1` is Norwegian (bokmål), 2 English.
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

SITE = "www.jobbnorge.no"
API = "https://publicapi.jobbnorge.no"
DETAIL_API = "https://id.jobbnorge.no/api/joblisting"
DETAIL_RE = re.compile(r"^https?://(?:www\.)?jobbnorge\.no/ledige-stillinger/stilling/(\d+)(?:/[^?#]*)?/?(?:\?.*)?$")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+47[\s ]?)?(?:\d{2}[\s ]?\d{2}[\s ]?\d{2}[\s ]?\d{2}|\d{3}[\s ]?\d{2}[\s ]?\d{3})(?!\d)")
_PACES = {}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobbnorge] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def pace_for(host):
    if host not in _PACES:
        _PACES[host] = Pace(host, own=2.0)   # no Crawl-delay on any of the three hosts; 2 s is ours
    return _PACES[host]


def request(url):
    gate(url)
    pace_for(urllib.parse.urlsplit(url).netloc).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "application/json, text/html;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t ]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def scrub(s):
    if not s:
        return s
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s)


def json_of(url, what):
    code, body = request(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    try:
        return json.loads(body)
    except ValueError:
        die(f"{url}: not JSON ({len(body)} characters) — not the {what}.", EXIT_PARTIAL)


def stated():
    """The site's own «treff» — `/v1/jobs/count`, a bare integer, a count of positions."""
    d = json_of(f"{API}/v1/jobs/count", "count")
    return d if isinstance(d, int) else None


def record(j):
    locs = j.get("locations") if isinstance(j.get("locations"), list) else []
    locs = sorted(locs, key=lambda l: not l.get("isPrimary"))          # the primary first, as the page shows it
    prim = locs[0] if locs else {}
    ident = str(j.get("id") or "").strip()
    return {
        "source": "jobbnorge", "country": "NO", "ledger_id": f"jobbnorge:{ident}", "id": ident,
        "url": j.get("link") or f"https://{SITE}/ledige-stillinger/stilling/{ident}",
        "title": (j.get("title") or "").strip() or None,
        "employer": (j.get("department") if j.get("regardDepartmentAsEmployer") else j.get("employer")) or None,   # what the site shows as the employer
        "employer_parent": j.get("employer") if j.get("regardDepartmentAsEmployer") else None,
        "department": j.get("department") or None,
        "summary": scrub((j.get("summary") or "").strip()) or None,
        "workplace": ", ".join(x for x in (prim.get("area"), prim.get("municipality"), prim.get("county")) if x) or None,
        "postal_code": prim.get("zipCode") or None,
        "locations": [", ".join(x for x in (l.get("municipality"), l.get("county")) if x) for l in locs] or None,
        "abroad": (not prim.get("isDomestic", True)) if prim else None,
        "job_scope": j.get("jobScope") or None, "job_duration": j.get("jobDuration") or None,
        "job_type": (j.get("jobType") or {}).get("name") if isinstance(j.get("jobType"), dict) else None,
        "positions": j.get("positionCount"),
        "promoted": bool(j.get("promoted")),
        "posted": j.get("publicationDate") or None,                     # DD.MM.YYYY as the API prints it
        "application_deadline": j.get("deadline") or None,
        "language": "no",
    }


def cmd_search(a):
    total = stated()
    d = json_of(f"{API}/v3/jobs?language={a.language}", "job list")
    jobs = d.get("jobs") if isinstance(d, dict) else None
    if not isinstance(jobs, list):
        die(f"{API}/v3/jobs: no `jobs` list in the answer — the shape changed.", EXIT_PARTIAL)
    rows, seen = [], set()
    for j in jobs:
        r = record(j)
        if not r["id"] or r["id"] in seen:
            continue
        seen.add(r["id"])
        rows.append(r)
    if not rows:
        if (total or 0) > 0:
            die(f"{API}/v3/jobs: the site counts {total} positions and the list carried no posting — a reading fault, not an empty board.", EXIT_PARTIAL)
        note("no posting in the list and the site counts none.")
        return
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    positions = sum(r["positions"] or 0 for r in rows)
    if total is None:
        note(f"{th(len(emitted))} posting(s) emitted of {th(len(rows))} listed, {th(positions)} position(s) summed; the site's count did not answer — no witness.")
        return
    if a.limit and a.limit < len(rows):
        note(f"{th(len(emitted))} posting(s) emitted of the {th(len(rows))} the list carries (--limit), {th(positions)} position(s) summed, site counts {th(total)} — bounded by request, not a shortfall.")
    elif positions == total:
        note(f"{th(len(rows))} posting(s) emitted, {th(positions)} position(s) summed, site counts {th(total)} positions — equal.")
    else:
        note(f"{th(len(rows))} posting(s) emitted, {th(positions)} position(s) summed, site counts {th(total)} positions — {th(abs(total - positions))} " + ("short" if total > positions else "more summed than the site counts") + ".")


def cmd_ad(a):
    m = DETAIL_RE.match((a.url or "").strip())
    if not m:
        die(f"{a.url}: not a posting address — expected https://{SITE}/ledige-stillinger/stilling/<id>")
    ident = m.group(1)
    url = f"{DETAIL_API}?jobId={ident}&languageId={a.language}"
    code, body = request(url)
    if code in (404, 410):
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    try:
        d = json.loads(body)
    except ValueError:
        die(f"{url}: not JSON ({len(body)} characters) — not the posting's data.", EXIT_PARTIAL)
    if not isinstance(d, dict) or not (d.get("components") or d.get("jobGapComponents")):
        die(f"{url}: no components in the answer — not a posting, or the site changed.", EXIT_PARTIAL)
    comps = [c for c in (d.get("components") or []) if isinstance(c, dict)]
    gaps = [g for g in (d.get("jobGapComponents") or []) if isinstance(g, dict)]
    title = next((c.get("heading") for c in comps if c.get("heading")), None)
    sections = [{"title": text(g.get("title") or "") or None, "text": scrub(text(g.get("content") or "")) or None} for g in gaps]
    body_text = "\n\n".join(x for x in (scrub(text(c.get("text") or "")) for c in comps) if x)
    # `contacts` — the persons to call, with their telephone — is never read
    print(json.dumps({
        "source": "jobbnorge", "country": "NO", "ledger_id": f"jobbnorge:{ident}", "id": ident, "url": f"https://{SITE}/ledige-stillinger/stilling/{ident}",
        "title": text(title) if title else None,
        "positions": d.get("positionCount"),
        "published": d.get("isPublished"),
        "sections": sections,
        "description": (body_text or "\n\n".join(f"{s['title']}\n{s['text']}" for s in sections if s["text"]))[:20000] or None,
        "contacts_withheld": True,
        "language": "no" if str(a.language) == "1" else "en",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Jobbnorge — Norway's public and academic board through the API its pages call; the site's position count beside every walk; the contact persons never emitted. Issue #366.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="every open posting — two requests: the site's count, then the whole list")
    s.add_argument("--language", default="1", help="1 = bokmål (default), 2 = English — the API's own codes")
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_search)
    d = sub.add_parser("ad", help="one posting — its sections and text from the page's own data route; the contact persons withheld")
    d.add_argument("--url", required=True)
    d.add_argument("--language", default="1")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
