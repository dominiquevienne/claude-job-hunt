#!/usr/bin/env python3
"""Eightfold — the careers site an employer runs on Eightfold AI, read by tenant through the JSON route its own page calls; `count` as the count the tenant states; the employer's contact never emitted. Issue #451.

  eightfold.py list --host <tenant>.eightfold.ai [--domain employer.com] [--q TEXT] [--pages N | --all] [--limit N]
  eightfold.py ad --host <tenant>.eightfold.ai --id <position id> [--domain employer.com]
  eightfold.py ad --url <https://<tenant>.eightfold.ai/careers/job/<id>>

ONE EMPLOYER PER SITE, ONE ROUTE FOR ALL OF THEM. An employer on Eightfold
serves `https://<tenant>.eightfold.ai/careers` (often under a vanity name
too — `talent.bayer.com` is `bayer.eightfold.ai`), and that page fills its
list from **`GET /api/apply/v2/jobs?domain=<employer domain>&start=<n>&num=10`**
— JSON with **`count`** (the count the tenant states) and `positions[]`
(id, name, location(s), department, business_unit, t_create, t_update,
ats_job_id, work_location_option, canonicalPositionUrl). **`num` is capped
at 10 by the server** (100 asked, 10 answered — measured on
`bayer.eightfold.ai` 2026-09-14 03:2x UTC, `count` 602). One position is
**`GET /api/apply/v2/jobs/<id>?domain=…`** — the same record plus
`job_description` (HTML, the employer's own), `apply_redirect_url`. The
`domain` the routes need is the employer's own (`bayer.com`), read from the
careers page (`?domain=` in its config) when `--domain` is not given.

TWO SHAPES OF TENANT, ONE READ HERE. `micron.eightfold.ai/careers` is
served (254 KB, «Careers at Micron Technology») and the same v2 route
answers **403 `{"message": "Not authorized for PCSX"}`** — the tenant runs
the PCSX variant, whose data route the page does not name in clear (its
list is drawn by the bundle). This file says so and exits 7: a second
shape to measure, not a closed employer.

**The tenant is named by the user, never guessed** (`--host`, as for
`icims.py`): a family adapter reads the employers you name. The guard and
the pace are per host — each tenant's `robots.txt` is its own (Bayer's
refuses nothing under `/careers` or `/api/apply`; another tenant's may).

WHAT IS WITHHELD. Addresses and phone numbers in the description are
replaced (`[e-mail withheld]`, `[phone withheld]`, nine digits or more);
the description's HTML is reduced to text. The apply route
(`apply_redirect_url`, the tenant's own form) is never followed.
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

PAGE_SIZE = 10
DEFAULT_PAGES = 10
AD_RE = re.compile(r"^https?://([a-z0-9.-]+)/careers/job/(\d+)")
DOMAIN_RE = re.compile(r"[?&]domain=([a-z0-9.-]+)")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().-]{6,}\d(?!\w)")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[eightfold] {msg}", file=sys.stderr)


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


def request(url, accept="application/json"):
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    _PACES.setdefault(host, Pace(host, own=3.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        try:
            body = decode_body(e.read(), e.headers)[0]
        except Exception:
            body = ""
        return e.code, body
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def clean(s):
    s = re.sub(r"<(script|style)\b.*?</\1>", "", s or "", flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</tr>|</h\d>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def redact(s):
    s = EMAIL_RE.sub("[e-mail withheld]", s or "")
    return PHONE_RE.sub(lambda m: "[phone withheld]" if sum(c.isdigit() for c in m.group(0)) >= 9 else m.group(0), s)


def norm_host(h):
    h = (h or "").strip().lower()
    h = re.sub(r"^https?://", "", h).split("/")[0]
    if not h:
        die("--host is required: the tenant, e.g. bayer.eightfold.ai (or its vanity name).")
    return h


def domain_of(host, given):
    """The employer's `domain` the routes need — given, or read from the careers page's own config."""
    if given:
        return given.strip().lower()
    code, body = request(f"https://{host}/careers", accept="text/html")
    if code != 200:
        die(f"https://{host}/careers: HTTP {code} — not a careers site this file can read; pass --domain if you know it.", EXIT_PARTIAL)
    m = DOMAIN_RE.search(body)
    if not m:
        die(f"https://{host}/careers: the page names no `domain=` — not an Eightfold careers page, or its config moved; pass --domain.", EXIT_PARTIAL)
    return m.group(1)


def api(host, domain, **q):
    return f"https://{host}/api/apply/v2/jobs?" + urllib.parse.urlencode({"domain": domain, **q})


def parse(body, url):
    try:
        j = json.loads(body)
    except ValueError:
        die(f"{url}: not JSON ({len(body or '')} characters).", EXIT_PARTIAL)
    if not isinstance(j, dict):
        die(f"{url}: the answer is not an object.", EXIT_PARTIAL)
    return j


def ts(t):
    import datetime
    try:
        return datetime.datetime.fromtimestamp(int(t), datetime.timezone.utc).strftime("%Y-%m-%d") if t else None
    except (TypeError, ValueError, OverflowError):
        return None


def record(p, host, domain):
    ident = str(p.get("id") or "").strip()
    return {
        "source": "eightfold", "country": None, "tenant": host, "employer_domain": domain,
        "ledger_id": f"eightfold:{host}:{ident}", "id": ident, "ats_job_id": p.get("ats_job_id") or p.get("display_job_id") or None,
        "url": p.get("canonicalPositionUrl") or f"https://{host}/careers/job/{ident}",
        "title": redact(clean(p.get("name") or p.get("posting_name") or "")) or None,
        "locations": [clean(x) for x in (p.get("locations") or ([p.get("location")] if p.get("location") else [])) if clean(x)] or None,
        "department": p.get("department") or None, "business_unit": p.get("business_unit") or None,
        "work_location": p.get("work_location_option") or None, "locale": p.get("locale") or None,
        "posted": ts(p.get("t_create")), "updated": ts(p.get("t_update")),
    }


def cmd_list(a):
    host = norm_host(a.host)
    if a.pages is not None and a.pages < 1:
        die("--pages must be at least 1 (or use --all).")
    limit_pages = None if a.all else (a.pages or DEFAULT_PAGES)
    domain = domain_of(host, a.domain)
    seen, emitted, page, site = set(), 0, 0, None
    while True:
        q = {"start": page * PAGE_SIZE, "num": PAGE_SIZE}
        if a.q:
            q["query"] = a.q
        url = api(host, domain, **q)
        code, body = request(url)
        if code == 403 and "PCSX" in (body or ""):
            die(f"{url}: HTTP 403 {body.strip()[:60]} — this tenant runs the PCSX variant of Eightfold, whose data route is not the v2 one this file reads "
                f"(measured 2026-09-14 on micron.eightfold.ai); a second shape to measure, not a closed employer.", EXIT_REFUSED)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        j = parse(body, url)
        if site is None:
            try:
                site = int(j.get("count"))
            except (TypeError, ValueError):
                die(f"{url}: the answer states no `count` (keys {sorted(j)[:12]}).", EXIT_PARTIAL)
        page += 1
        rows = j.get("positions") or []
        new = 0
        for p in rows:
            r = record(p, host, domain)
            if not r["id"] or r["id"] in seen:
                continue
            seen.add(r["id"])
            print(json.dumps(r, ensure_ascii=False))
            emitted += 1
            new += 1
            if a.limit and emitted >= a.limit:
                break
        label = f"{host}, domain {domain}" + (f", query {a.q!r}" if a.q else "")
        if a.limit and emitted >= a.limit:
            note(f"{th(emitted)} emitted over {page} page(s), tenant states {th(site)} ({label}) — walk bounded by request (--limit), not compared.")
            return
        if not rows or new == 0 or emitted >= site:
            break
        if limit_pages is not None and page >= limit_pages:
            note(f"{th(emitted)} emitted over {page} page(s), tenant states {th(site)} ({label}) — walk bounded by request (--pages {limit_pages}; --all walks to the count), not compared.")
            return
    if emitted == site:
        note(f"{th(emitted)} emitted over {page} page(s), tenant states {th(site)} ({label}) — equal.")
    else:
        note(f"{th(emitted)} emitted over {page} page(s), tenant states {th(site)} ({label}) — {th(abs(site - emitted))} {'short' if emitted < site else 'over'}.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    host, ident = (norm_host(a.host) if a.host else None), (str(a.id).strip() if a.id else None)
    if a.url:
        m = AD_RE.match(a.url.strip())
        if not m:
            die(f"{a.url}: not an Eightfold position URL (https://<tenant>/careers/job/<id>).")
        host, ident = norm_host(m.group(1)), m.group(2)
    if not host or not ident:
        die("ad needs --host and --id, or --url.")
    domain = domain_of(host, a.domain)
    url = f"https://{host}/api/apply/v2/jobs/{ident}?" + urllib.parse.urlencode({"domain": domain})
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the position is gone.", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    p = parse(body, url)
    if not p.get("id"):
        die(f"{url}: no position in the answer — gone, or never public.", EXIT_GONE)
    r = record(p, host, domain)
    r["description"] = redact(clean(p.get("job_description") or "")) or None
    r["apply_is_external"] = bool(p.get("apply_redirect_url")) or None
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="one tenant's positions through its own JSON route")
    l.add_argument("--host", required=True, help="the tenant, e.g. bayer.eightfold.ai — or its vanity name")
    l.add_argument("--domain", default="", help="the employer's domain the route needs (read from the careers page when omitted)")
    l.add_argument("--q", default="", help="free text (the route's `query`)")
    g = l.add_mutually_exclusive_group()
    g.add_argument("--pages", type=int, default=None, help=f"pages of {PAGE_SIZE} to read (default {DEFAULT_PAGES}, bounded and said so)")
    g.add_argument("--all", action="store_true", help="walk to the count the tenant states, and compare")
    l.add_argument("--limit", type=int, default=0)
    l.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one position by tenant and id, or by URL")
    d.add_argument("--host")
    d.add_argument("--id")
    d.add_argument("--url")
    d.add_argument("--domain", default="")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
