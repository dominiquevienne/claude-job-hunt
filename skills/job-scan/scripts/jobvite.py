"""Jobvite — one employer's career site on `jobs.jobvite.com/<tenant>`, its search page paged to the end and its «1-50 of N» as the witness.

Jobvite is an ATS: every employer's board lives under one host, `jobs.jobvite.com`,
at `/<tenant>` — the tenant is the path segment of the employer's own careers URL
(`nutanix`, `pragmaticplay`), named by the user, never guessed. One adapter, one
tenant per invocation; the guard is taken on `jobs.jobvite.com` and the exact path.

TWO LISTS, AND ONLY ONE IS COMPLETE. `/<tenant>/jobs` is the «View All» page: jobs
grouped under department headings, no pager, no count — and on the tenant read it
carried 97 rows where the search page states 224. `/<tenant>/search?q=&l=` is the
route: `table.jv-job-list` rows (`td.jv-job-list-name a[href=/<tenant>/job/<id>]`,
`td.jv-job-list-location` — a city or «N Locations»), a footer `jv-pagination-text`
«1-50 of 224» — THE COUNT THE SITE STATES — and a `jv-pagination-next` link
(`/<tenant>/search/?p=1`, zero-based) followed until it is gone; rows deduplicated
on the id. The emitted count is printed beside the stated one, exit 6 on a gap; a
tenant whose search page states no count is said so and not compared.

A tenant that does not exist is not a 404: the host redirects to the editor's
support page (`www.jobvite.com/support/job-seeker-support/?invalid=1`) with HTTP 200 —
`zscaler`, recorded in this repository's notes, lands there on 2026-09-14. The
adapter reads the final URL and exits 3.

The job page (`/<tenant>/job/<id>`): `h2.jv-header` the title,
`p.jv-job-detail-meta` the department, the locations and «Req.Num.: N» separated by
`jv-inline-separator`, `div.jv-job-detail-description` the employer's own HTML —
which may open with an HTML comment holding an older text («<!-- removed ===== …
removed=====--->»): comments are dropped before the text is read. E-mail addresses
and telephone numbers are withheld; `/apply` is never followed.

MEASURED on `jobs.jobvite.com/nutanix`, 2026-09-14 04:28–04:3x UTC: `robots.txt`
404 (no rules, certain); the search page states «1-50 of 224», 5 pages of 50;
`/nutanix/jobs` shows 97 rows and no count; one job read (Systems Sales Engineer,
Req.Num. 32278, Sales, two locations). `pragmaticplay` (ARRISE): 78 rows on
`/jobs`.

    python3 jobvite.py list --tenant nutanix --all
    python3 jobvite.py ad --url https://jobs.jobvite.com/nutanix/job/oxVCAfwo

Exits: 0 read; 2 broken; 3 gone (a tenant the host does not know, a job page
without its header); 6 partial (a walk short of the stated count, HTTP ≠ 200); 7
refused by the rules; 8 the rules could not be read.
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

HOST = "jobs.jobvite.com"
DEFAULT_PAGES = 10
AD_RE = re.compile(r"^https?://jobs\.jobvite\.com/([A-Za-z0-9_-]+)/job/([A-Za-z0-9]+)/?(?:[?#].*)?$")
ROW_RE = re.compile(r'<td class="jv-job-list-name">\s*<a href="(/[A-Za-z0-9_-]+/job/([A-Za-z0-9]+))"[^>]*>(.*?)</a>\s*</td>\s*<td class="jv-job-list-location">(.*?)</td>', re.S)
STATED_RE = re.compile(r'class="jv-pagination-text">\s*[\d,]+\s*-\s*[\d,]+\s+of\s+([\d,]+)')
NEXT_RE = re.compile(r'<a href="([^"]+)" class="jv-pagination-next"')
TITLE_RE = re.compile(r'<h2 class="jv-header">\s*(.*?)\s*</h2>', re.S)
META_RE = re.compile(r'<p class="jv-job-detail-meta">(.*?)</p>', re.S)
DESC_RE = re.compile(r'<div class="jv-job-detail-description"[^>]*>(.*?)<div class="jv-job-detail-bottom-actions|<div class="jv-job-detail-description"[^>]*>(.*?)</article>', re.S)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\d[\d\s().-]{6,}\d(?!\w)")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACE = Pace(HOST, own=3.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobvite] {msg}", file=sys.stderr)


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
    """One GET — `(code, body, final_url)`; an unknown tenant is a 200 on the editor's support page."""
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, "", url
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def clean(s):
    s = re.sub(r"<!--.*?-->", "", s or "", flags=re.S)   # an older text may sit in a comment before the current one
    s = re.sub(r"<(script|style|svg)\b.*?</\1>", "", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h\d>|</tr>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def redact(s):
    s = EMAIL_RE.sub("[e-mail withheld]", s or "")
    return PHONE_RE.sub(lambda m: "[phone withheld]" if sum(c.isdigit() for c in m.group(0)) >= 9 else m.group(0), s)


def norm_tenant(t):
    t = re.sub(r"^https?://jobs\.jobvite\.com/", "", (t or "").strip()).strip("/").split("/")[0]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", t):
        die("--tenant is required: the path segment of the employer's careers URL, e.g. nutanix (jobs.jobvite.com/nutanix).")
    return t


def unknown_tenant(final_url):
    return "jobvite.com/support" in (final_url or "") or "invalid=1" in (final_url or "")


def stated(body):
    m = STATED_RE.search(body or "")
    return int(m.group(1).replace(",", "")) if m else None


def rows(body, tenant):
    out = []
    for path, ident, title, loc in ROW_RE.findall(body or ""):
        loc = re.sub(r"\s+", " ", clean(loc))
        out.append({
            "source": "jobvite", "country": None, "tenant": tenant, "ledger_id": f"jobvite:{tenant}:{ident}", "id": ident,
            "url": f"https://{HOST}{path}", "title": redact(re.sub(r"\s+", " ", clean(title))) or None,
            "location": redact(loc) or None, "locations_count": int(loc.split()[0]) if re.fullmatch(r"\d+ Locations?", loc) else None,
        })
    return out


def cmd_list(a):
    tenant = norm_tenant(a.tenant)
    if a.pages is not None and a.pages < 1:
        die("--pages must be at least 1 (or use --all).")
    limit_pages = None if a.all else (a.pages or DEFAULT_PAGES)
    url = f"https://{HOST}/{tenant}/search?q=&l="
    seen, emitted, page, site, ended = set(), 0, 0, None, False
    while True:
        page += 1
        code, body, final = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}" + (f" — {th(emitted)} emitted over {page - 1} page(s)" if emitted else ""), EXIT_PARTIAL)
        if page == 1:
            if unknown_tenant(final):
                die(f"{url}: the host does not know the tenant «{tenant}» — it lands on {final}.", EXIT_GONE)
            if "jv-job-list" not in body and "jv-page-body" not in body:
                die(f"{url}: not a Jobvite search page ({len(body)} characters).", EXIT_PARTIAL)
            site = stated(body)
        new = 0
        rs = rows(body, tenant)
        for r in rs:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            print(json.dumps(r, ensure_ascii=False))
            emitted += 1
            new += 1
            if a.limit and emitted >= a.limit:
                break
        nxt = NEXT_RE.search(body)
        where = f"{HOST}/{tenant}"
        if a.limit and emitted >= a.limit:
            note(f"{th(emitted)} emitted over {page} page(s) ({where}) — walk bounded by request (--limit), not compared.")
            return
        if not rs or new == 0 or not nxt:
            ended = True
            break
        if limit_pages is not None and page >= limit_pages:
            note(f"{th(emitted)} emitted over {page} page(s) ({where}), site states {th(site) if site is not None else 'no count'} — walk bounded by request (--pages {limit_pages}; --all follows «Next» to the end), not compared.")
            return
        url = html.unescape(nxt.group(1))
        if url.startswith("/"):
            url = f"https://{HOST}{url}"
    if site is None:
        note(f"{th(emitted)} emitted over {page} page(s) ({where}) — the site states no count; the pager's end was {'reached' if ended else 'NOT reached'}, not compared.")
        return
    if emitted == site:
        note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} ({where}) — equal.")
    else:
        note(f"{th(emitted)} emitted over {page} page(s), site states {th(site)} ({where}) — {th(abs(site - emitted))} {'short' if emitted < site else 'over'}.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not a Jobvite job URL (https://jobs.jobvite.com/<tenant>/job/<id>).")
    tenant, ident = m.groups()
    code, body, final = request(a.url.strip())
    if code == 404:
        die(f"{a.url}: HTTP 404 — the job is gone.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_PARTIAL)
    if unknown_tenant(final):
        die(f"{a.url}: the host does not know the tenant «{tenant}» — it lands on {final}.", EXIT_GONE)
    t = TITLE_RE.search(body)
    if not t:
        die(f"{a.url}: no `jv-header` on the page — gone, or not the template this file reads.", EXIT_GONE)
    meta = META_RE.search(body)
    parts = [re.sub(r"\s+", " ", clean(x)) for x in re.split(r"<span class=['\"]jv-inline-separator['\"]>\s*</span>", meta.group(1))] if meta else []
    parts = [p for p in parts if p]
    req = next((p for p in parts if re.match(r"(?i)req\.?\s*num", p)), None)
    rest = [p for p in parts if p != req]
    d = DESC_RE.search(body)
    desc = clean((d.group(1) or d.group(2)) if d else "")
    r = {"source": "jobvite", "country": None, "tenant": tenant, "ledger_id": f"jobvite:{tenant}:{ident}", "id": ident, "url": a.url.strip(),
         "title": redact(re.sub(r"\s+", " ", clean(t.group(1)))) or None,
         "department": redact(rest[0]) if rest else None,
         "location": redact(" | ".join(rest[1:])) or None if len(rest) > 1 else None,
         "req_number": re.sub(r"(?i)^req\.?\s*num\.?\s*:?\s*", "", req).strip() if req else None,
         "description": redact(desc) or None}
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="one tenant's search page, «Next» after «Next»")
    l.add_argument("--tenant", required=True, help="the employer's path on jobs.jobvite.com, e.g. nutanix")
    g = l.add_mutually_exclusive_group()
    g.add_argument("--pages", type=int, default=None, help=f"pages to read (default {DEFAULT_PAGES}, bounded and said so)")
    g.add_argument("--all", action="store_true", help="follow «Next» to the end, and compare with the count the site states")
    l.add_argument("--limit", type=int, default=0)
    l.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one job by its public URL")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
