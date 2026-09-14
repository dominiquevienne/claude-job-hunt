#!/usr/bin/env python3
"""Avature — the careers portal an employer runs on Avature, read by tenant through the `SearchJobs` list its own page pages with `jobOffset`; the portal's «of N» when it states one, and an honest «states no count» when it does not. Issue #450.

  avature.py list --host <tenant>.avature.net [--path /en_US/careers] [--pages N | --all] [--limit N]
  avature.py ad --url <https://<tenant>.avature.net/<locale>/careers/JobDetail/<slug>/<id>>

ONE EMPLOYER PER PORTAL, THE TENANT NAMED BY THE USER (`--host`, as for
`icims.py` and `eightfold.py`). An Avature portal lives at
`https://<tenant>.avature.net/<locale>/careers` (Koch: `/en_US/careers`,
read from the redirect of `/careers` when `--path` is not given); its list
is **`<path>/SearchJobs/?jobRecordsPerPage=<n>&jobOffset=<o>`** — HTML,
`article.article--result` cards (the title's link `JobDetail/<slug>/<id>`,
a subtitle that is the company, labelled fields «Location», «Job Number»)
and a pager whose only forward control is a «Next >>» link
(`paginationNextLink`). The adapter follows that link until it is gone
and dedups on the id. **`jobRecordsPerPage` is not honoured on the tenant
read** (50 asked, 6 served); the page size is the portal's.

THE PAGER IS CAPPED. On Koch, «Next» after «Next» reached
`jobOffset=2004` and the portal answered **HTTP 406** (03:43–04:03 UTC,
2 002 distinct jobs over 334 pages): the list stops at 2 000 by the
portal's rule, the inventory beyond it is not reachable by this route,
and the adapter says so and exits 6 — a bound, not an end.

THE WITNESS, WHEN THERE IS ONE. Some portals fill `list-controls__text`
with «Showing 1-6 of N results»: then N is the count the portal states,
printed beside the emitted count and compared. **Koch's portal leaves it
empty** (measured 2026-09-14 03:4x UTC): the walk then prints «N emitted
over P page(s), the portal states no count — not compared» and exits 0
having reached the end of the pager, 6 only when the end was not reached.
The portal's RSS (`SearchJobs/feed/`) answered 20 items on Koch — a
capped feed, not a count, and not read by this file.

THE JOB PAGE (`JobDetail/<slug>/<id>`): `article.article--details` with
labelled fields («Location(s)», «Company», «Career Field», «Job Number»)
then the body's headed sections («Your Job», «What You Will Do», …). The
«Apply now» route (`/careers/Login`, an account) is never followed.

THE RULES, PER TENANT. `koch.avature.net/robots.txt`: `/*/careers` is
allowed in writing, `certain: True`; each tenant's file is its own and is
read on the exact path. The editor's `www.avature.com` is not a board.
3 s own spacing per host. `careers.ibm.com` (IBM's tenant, `ibmglobal`)
answered 202 with 0 bytes to the declared client on 2026-09-14 — a
different front door, not read here.

WHAT IS WITHHELD. Addresses and phone numbers in the prose are replaced
(`[e-mail withheld]`, `[phone withheld]` — nine digits or more).
"""

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
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

DEFAULT_PAGES = 10
AD_RE = re.compile(r"^https?://([a-z0-9.-]+)(/[A-Za-z_-]+/careers)/JobDetail/([^/?#]+)/(\d+)/?$")
CARD_RE = re.compile(r'<article class="article article--result">(.*?)</article>', re.S)
TITLE_RE = re.compile(r'class="article__header__text__title[^"]*"[^>]*>\s*<a href="([^"]*?/JobDetail/[^"/]+/(\d+))"[^>]*>(.*?)</a>', re.S)
SUB_RE = re.compile(r'class="article__header__text__subtitle">(.*?)</h\d>', re.S)
FIELD_RE = re.compile(r'class="article__content__field__label">\s*(.*?)\s*</div>\s*<div class="article__content__field__value">\s*(.*?)\s*</div>', re.S)
VFIELD_RE = re.compile(r'class="article__content__view__field__label">\s*(.*?)\s*</div>\s*<div class="article__content__view__field__value">\s*(.*?)\s*</div>', re.S)
NEXT_RE = re.compile(r'class="[^"]*paginationNextLink[^"]*"\s+href="([^"]+)"')
STATED_RE = re.compile(r'class="list-controls__text">\s*(.*?)\s*</div>', re.S)
OF_RE = re.compile(r"\bof\s+([\d,.]+)")
H1_RE = re.compile(r'class="banner__text__title[^"]*"[^>]*>(.*?)</h\d>', re.S)   # the page's <h1> is the portal's name; the job's title is the banner's
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\d[\d\s().-]{6,}\d(?!\w)")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[avature] {msg}", file=sys.stderr)


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


def request(url):
    """One GET — `(code, body, final_url)`; the portal redirects `/careers` to its locale path."""
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    _PACES.setdefault(host, Pace(host, own=3.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, "", url
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def clean(s):
    s = re.sub(r"<(script|style|svg)\b.*?</\1>", "", s or "", flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h\d>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def redact(s):
    s = EMAIL_RE.sub("[e-mail withheld]", s or "")
    return PHONE_RE.sub(lambda m: "[phone withheld]" if sum(c.isdigit() for c in m.group(0)) >= 9 else m.group(0), s)


def norm_host(h):
    h = re.sub(r"^https?://", "", (h or "").strip().lower()).split("/")[0]
    if not h:
        die("--host is required: the tenant, e.g. koch.avature.net.")
    return h


def portal_path(host, given):
    """`/en_US/careers` — given, or read from where the portal sends `/careers`."""
    if given:
        return "/" + given.strip("/")
    code, body, final = request(f"https://{host}/careers")
    if code != 200:
        die(f"https://{host}/careers: HTTP {code} — not a portal this file can read; pass --path if you know it.", EXIT_PARTIAL)
    p = urllib.parse.urlsplit(final).path.rstrip("/")
    if not p.endswith("/careers"):
        die(f"https://{host}/careers landed on {final} — not an Avature careers path; pass --path.", EXIT_PARTIAL)
    return p


def stated(body):
    m = STATED_RE.search(body or "")
    if not m:
        return None
    t = clean(m.group(1))
    n = OF_RE.search(t)
    return int(re.sub(r"[^\d]", "", n.group(1))) if n else None


def cards(body, host):
    out = []
    for blk in CARD_RE.findall(body or ""):
        t = TITLE_RE.search(blk)
        if not t:
            continue
        url, ident, title = t.groups()
        sub = SUB_RE.search(blk)
        fields = {clean(k).rstrip(":").lower(): clean(v) for k, v in FIELD_RE.findall(blk)}
        out.append({
            "source": "avature", "country": None, "tenant": host, "ledger_id": f"avature:{host}:{ident}", "id": ident,
            "url": url if url.startswith("http") else f"https://{host}{url}",
            "title": redact(clean(title)) or None, "company": redact(clean(sub.group(1))) or None if sub else None,
            "location": redact(re.sub(r"\s+", " ", fields.get("location", ""))) or None,
            "job_number": fields.get("job number") or None,
        })
    return out


def cmd_list(a):
    host = norm_host(a.host)
    if a.pages is not None and a.pages < 1:
        die("--pages must be at least 1 (or use --all).")
    limit_pages = None if a.all else (a.pages or DEFAULT_PAGES)
    path = portal_path(host, a.path)
    url = f"https://{host}{path}/SearchJobs/"
    seen, emitted, page, site, ended = set(), 0, 0, None, False
    while True:
        page += 1
        code, body, _ = request(url)
        if code == 406 and page > 1:
            note(f"{th(emitted)} emitted over {page - 1} page(s) ({host}{path}) — the portal answers HTTP 406 at {url.split('?')[-1]}: its pager is capped there, the inventory beyond is not reachable by this route"
                 + (f"; the portal states {th(site)}." if site is not None else "; the portal states no count."))
            sys.exit(EXIT_PARTIAL)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if page == 1:
            if "article--result" not in body and "SearchJobs" not in body:
                die(f"{url}: not an Avature list page ({len(body)} characters).", EXIT_PARTIAL)
            site = stated(body)
        rows = cards(body, host)
        new = 0
        for r in rows:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            print(json.dumps(r, ensure_ascii=False))
            emitted += 1
            new += 1
            if a.limit and emitted >= a.limit:
                break
        nxt = NEXT_RE.search(body)
        if a.limit and emitted >= a.limit:
            note(f"{th(emitted)} emitted over {page} page(s) ({host}{path}) — walk bounded by request (--limit), not compared.")
            return
        if not rows or new == 0 or not nxt:
            ended = True
            break
        if limit_pages is not None and page >= limit_pages:
            note(f"{th(emitted)} emitted over {page} page(s) ({host}{path}), portal states {th(site) if site is not None else 'no count'} — walk bounded by request (--pages {limit_pages}; --all follows «Next» to the end), not compared.")
            return
        url = html.unescape(nxt.group(1))
        if url.startswith("/"):
            url = f"https://{host}{url}"
    if site is None:
        note(f"{th(emitted)} emitted over {page} page(s) ({host}{path}) — the portal states no count; the pager's end was {'reached' if ended else 'NOT reached'}, not compared.")
        return
    if emitted == site:
        note(f"{th(emitted)} emitted over {page} page(s), portal states {th(site)} ({host}{path}) — equal.")
    else:
        note(f"{th(emitted)} emitted over {page} page(s), portal states {th(site)} ({host}{path}) — {th(abs(site - emitted))} {'short' if emitted < site else 'over'}.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an Avature job URL (https://<tenant>/<locale>/careers/JobDetail/<slug>/<id>).")
    host, path, slug, ident = m.groups()
    host = norm_host(host)
    code, body, _ = request(a.url.strip())
    if code == 404:
        die(f"{a.url}: HTTP 404 — the job is gone.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_PARTIAL)
    if "article--details" not in body:
        die(f"{a.url}: no `article--details` on the page — gone, or not the template this file reads.", EXIT_GONE)
    fields = {clean(k).rstrip(":").lower(): re.sub(r"\s+", " ", clean(v)) for k, v in VFIELD_RE.findall(body)}
    h1 = H1_RE.search(body)
    # the body: the unlabelled field of the details article — the employer's own HTML, up to the article's end
    unl = re.findall(r'<div class="article__content__view__field\s*">\s*<div class="article__content__view__field__value">(.*?)(?=<div class="article__content__view__field\b|</article>)', body, re.S)
    body_text = "\n".join(clean(x) for x in unl if clean(x))
    r = {"source": "avature", "country": None, "tenant": host, "ledger_id": f"avature:{host}:{ident}", "id": ident, "url": a.url.strip(),
         "title": redact(clean(h1.group(1))) or None if h1 else None,
         "location": redact(fields.get("location(s)") or fields.get("location") or "") or None,
         "company": redact(fields.get("company") or "") or None, "career_field": fields.get("career field") or None,
         "job_number": fields.get("job number") or None,
         "description": redact(body_text) or None}
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="one tenant's SearchJobs list, «Next» after «Next»")
    l.add_argument("--host", required=True, help="the tenant, e.g. koch.avature.net")
    l.add_argument("--path", default="", help="the portal's locale path, e.g. /en_US/careers (read from the redirect of /careers when omitted)")
    g = l.add_mutually_exclusive_group()
    g.add_argument("--pages", type=int, default=None, help=f"pages to read (default {DEFAULT_PAGES}, bounded and said so)")
    g.add_argument("--all", action="store_true", help="follow «Next» to the end, and compare when the portal states a count")
    l.add_argument("--limit", type=int, default=0)
    l.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one job by its public URL")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
