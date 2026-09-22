#!/usr/bin/env python3
"""Service Commissions Department (Saint Vincent and the Grenadines, `psc.gov.vc`): the public service's own recruiter publishes its open posts on one Joomla page — a ministry heading, then its posts, each a link to the advertisement and a deadline. Issue #732.

  pscgovvc.py jobs [--open-on 2026-09-22] [--country-code VC]      the page (1 request)

WHAT IT IS. The **Service Commissions Department** (the Personnel Department) recruits for the
public service of Saint Vincent and the Grenadines: the Public Service Commission, the Police
Service Commission and the Judicial and Legal Services Commission sit under it. **This page is the
country's live public route**: its two private boards answer a Cloudflare 522 (#751, #752, both
`blocked`), and the national portal `www.gov.vc` mirrors this page with a post that expired in 2025.

THE RULES. `psc.gov.vc` answers **404** to `/robots.txt` — a knowledge, not an ignorance: the host
looked and there is no file, so there is no rule to obey (open, `certain: True`), and no
Crawl-delay; 2 s is ours. The guard is taken on the exact path.

THE LIST. `/psc/index.php/vacancies` (200; 21 397 B) carries everything inside
`div[itemprop=articleBody]`, and the structure IS the grouping:

```
<p><strong>Ministry of Higher Education, Grenadines Affairs, Airports and Seaports</strong></p>
<ul><li><a href="/psc/images/PDF/Vacancies/423_-_Procurement_Officer_I_-_Urban.pdf">Post of Procurement Officer I</a>
        <strong><em>(Deadline: September 28, 2026)</em></strong></li></ul>
```

**The ministry is a heading, not a field of the post** — so it is carried forward to every post that
follows it until the next heading, and a post that appears before any heading gets `None` rather
than the previous page's ministry. **Nothing states a count**: the run prints what it read.

**The advertisement is a PDF** under `/psc/images/PDF/Vacancies/`, and it is **named, never
downloaded** — what the Department publishes is the document, and the page gives the post's title
and its deadline beside it.

**Only the article body is read.** The page's footer carries the Department's street address and its
office hours; **a street is never emitted** and the parse does not reach it — that is by
construction, not by scrubbing.

`--open-on` keeps the posts whose deadline is on or after a day (by default nothing is filtered, and
a closed post is emitted with its date rather than dropped in silence). `--country-code` STAMPS (the
page states no country) and the run says so.

Measured 2026-09-22 08:4x UTC by the declared client, the guard on the exact path, two reads:
200 ×2, 21 397 B both, md5 b9fda0a5f3f9 both — **2 posts under 2 ministries**, deadlines
2026-09-28 and 2026-10-05, each a PDF. *A thin flow, and it is the public service's own.*
"""

import argparse
import html as htmlmod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "psc.gov.vc"
PAGE = f"https://{HOST}/psc/index.php/vacancies"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\(?\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
DATE_RE = re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")
STRIP_RE = re.compile(r"(?s)<style.*?</style>|<script.*?</script>")
BODY_RE = re.compile(r'<div itemprop="articleBody"[^>]*>(.*?)</div>\s*</div>', re.S)
BLOCK_RE = re.compile(r"<p[^>]*>(?P<heading>.*?)</p>|<li[^>]*>(?P<post>.*?)</li>", re.S)
LINK_RE = re.compile(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
DEADLINE_RE = re.compile(r"Deadline\s*:?\s*([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})", re.I)
MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[pscgovvc] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # no rules file at all; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return " ".join(t.split()) or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def when(s):
    """«September 28, 2026» → `2026-09-28`."""
    m = DEADLINE_RE.search(s or "")
    if not m or not MONTHS.get(m.group(1).lower()):
        return None
    return f"{m.group(3)}-{MONTHS[m.group(1).lower()]:02d}-{int(m.group(2)):02d}"


def slug(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (s or "").lower())).strip("-")


def entries_of(markup):
    """The article body → [(ministry, title, document, deadline)].

    The ministry is a HEADING that precedes its posts, so it is carried forward until the next one —
    and a post before any heading carries `None`, never the ministry of another page's reading.
    """
    body = BODY_RE.search(STRIP_RE.sub("", markup or ""))
    if not body:
        return None
    ministry, out = None, []
    for m in BLOCK_RE.finditer(body.group(1)):
        if m.group("heading") is not None:
            head = text(m.group("heading"))
            if head and not LINK_RE.search(m.group("heading")):
                ministry = head          # a paragraph that is a link is not a heading
            continue
        block = m.group("post")
        link = LINK_RE.search(block)
        if not link:
            continue
        out.append((ministry, text(link.group(2)), htmlmod.unescape(link.group(1)), when(text(block))))
    return out


def record(ministry, title, doc, deadline, stamp):
    doc_url = urllib.parse.urljoin(PAGE, doc) if doc else None
    name = urllib.parse.unquote((urllib.parse.urlsplit(doc_url or "").path or "").rsplit("/", 1)[-1])
    key = slug(name) or f"{slug(ministry)}-{slug(title)}"
    return {
        "source": "pscgovvc", "country": stamp,
        "ledger_id": f"pscgovvc:{key}", "id": key,
        "title": scrub(title), "ministry": scrub(ministry),
        "deadline": deadline,
        "document_url": doc_url, "document_downloaded": False,
        "employer": "Service Commissions Department (public service)",
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    on = (a.open_on or "").strip()
    if on and not re.match(r"^\d{4}-\d{2}-\d{2}$", on):
        die(f"--open-on {a.open_on}: a date, YYYY-MM-DD")
    stamp = a.country_code.upper() if a.country_code else None
    code, body = request(PAGE)
    if code == 404:
        die(f"{PAGE}: HTTP 404 — the page is gone", EXIT_GONE)
    if code != 200:
        die(f"{PAGE}: HTTP {code}", EXIT_PARTIAL)
    found = entries_of(body)
    if found is None:
        die(f"{PAGE}: 200 without the article body — the page changed; not an empty list", EXIT_PARTIAL)
    rows, seen, dropped, undated = [], set(), 0, 0
    for ministry, title, doc, deadline in found:
        r = record(ministry, title, doc, deadline, stamp)
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        if not r["deadline"]:
            undated += 1
        if on and r["deadline"] and r["deadline"] < on:
            dropped += 1
            continue
        rows.append(r)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    today = time.strftime("%Y-%m-%d", time.gmtime())
    closed = sum(1 for r in rows if r["deadline"] and r["deadline"] < today)
    ministries = len({r["ministry"] for r in rows if r["ministry"]})
    if not rows:
        note(f"0 posts emitted ({th(len(seen))} read); **the page states no count** — what it lists is the board, and today it lists this.")
    else:
        note(f"{th(len(rows))} post(s) emitted under {th(ministries)} ministry(ies) ({th(len(seen))} read); **the page states no count** — what it lists is the board.")
    if dropped:
        note(f"{th(dropped)} post(s) whose deadline is before {on} not emitted — OUR filter, on the date the page states.")
    if undated:
        note(f"{th(undated)} post(s) state no deadline; they are emitted with `deadline: null` rather than dropped.")
    if closed:
        note(f"{th(closed)} emitted post(s) state a deadline already past on {today} (UTC) — the Department's own filing, never dropped in silence.")
    note("the advertisement is a PDF the Department publishes: it is NAMED, never downloaded; the page's footer (its street address and hours) is not read at all.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the page states no country.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Service Commissions Department (Saint Vincent and the Grenadines) — the public service's open posts, one page, the ministry read as the heading it is. Issue #732.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the page (1 request)")
    j.add_argument("--open-on", dest="open_on", metavar="YYYY-MM-DD", help="keep only the posts whose stated deadline is on or after this day (OUR filter)")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the page states none)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
