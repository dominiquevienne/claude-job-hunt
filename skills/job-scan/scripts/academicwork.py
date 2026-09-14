#!/usr/bin/env python3
"""Academic Work Norway (`www.academicwork.no`) — the Nordic staffing and recruitment network's Norwegian front, a Next.js site (Payload CMS, tenant `NO`): the listing states its count on the server («40 treff», `totalItems`) but pages by a server action, so the jobs sitemap is the inventory and each ad page is read for the `advert` object the page ships in its React flight data; **`owningCm` — the consultant's name and e-mail — on every advert and never emitted**. Issue #370.

  academicwork.py sitemap [--host no] [--limit N]     every /ledige-stillinger/j/<slug>/<id> row of sitemap.xml, with lastmod (1 request)
  academicwork.py list [--host no] [--limit N]        the listing's stated count, then the sitemap's ads read from their pages (2 s apart)
  academicwork.py ad --url <https://www.academicwork.no/ledige-stillinger/j/<slug>/<id>>

THE RULES (319 B): `*` reads `Allow: /`, `Disallow: /api/`, `/admin/`, `/auth/`, `*/auth/`,
`/_next/`, `/public/` and the seven `/<lang>/auth/`; `Sitemap: /sitemap.xml`. No Crawl-delay; 2 s
is ours. `/api/` is refused in writing — the CMS's own routes — and `request()` refuses any
`/api/` path before the gate.

THE COUNT IS STATED, THE PAGES ARE NOT ADDRESSABLE. `/ledige-stillinger` (200, ~365 KB) is a
React Server Components page: its flight data carries «Søk blant 40 ledige stillinger», «40
treff» and the pager's props `{"currentPage":1,"pageSize":10,"totalItems":40,"setPage":"$h4f"}`
— `setPage` is a server action, not a link, and `?page=2` serves page 1 again (the same ten
cards). The ten cards are rendered markup (title, town, «Fulltid», «Rekruttering», «for 7 døgn
siden»), not objects. So the adapter reads the count from the listing and takes `/sitemap.xml`
(159 rows, 40 of them `/ledige-stillinger/j/<slug>/<id>` with lastmod) as the inventory, then
prints emitted against the site's `totalItems`.

THE AD. `/ledige-stillinger/j/<slug>/<id>` (200, ~256 KB) ships, in the same flight data, the
props of its header component: `"advert":{…}` — `shortAdvertId`, `advertId`, `country`,
`language` (`nb`), `publishTimestamp`, `unpublishTimestamp`, `advertTitle`, `startDate` and its
description («Snarest, etter avtale»), `locations[]` (city, country, coordinates),
`locationCity`, `businessArea`, `jobCategory`, `role`, `jobType` (`recruitment` «Rekruttering»
— the client hires — or staffing), `workExtent`, `isAcademyAdvert`, a labelled `summary`
(company, town, start, extent, type, «Andre»: hybrid), `companyName` when `showCompanyName`,
`companySiteUrl`, `externalApplicationUrl`, and `advertText` {leadIn, yourNewWorkplace,
workTasks, requirements, clientInformation} whose long texts are `$<id>` references to `T`
chunks of the same flight (Markdown). No JSON-LD, no salary field. **`owningCm` {employeeRef,
name, email} is on every advert — the consultant manager — and is never emitted; the texts are
scrubbed of e-mail addresses and Norwegian telephone numbers; `contacts_withheld` on every
record; the application form (`/auth/`, refused in writing anyway) is never touched.**

Other Academic Work fronts (`.se`, `.fi`, `.dk`, `.de`, `.ch`) are the same stack under another
tenant; `BOARDS` is the shape, each with its own `adapter` issue first — only `no` is measured.

Measured 2026-09-14 03:4x UTC by the declared client, the guard on the exact path: robots.txt
319 B; `/sitemap.xml` 159 rows / 40 job rows (lastmod 2026-05-08 … 2026-09-11);
`/ledige-stillinger` 365 554 B, «40 treff», `totalItems` 40, 10 cards; `?page=2` the same ten;
the ad 255 963 B with its `advert`.
"""

import argparse
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

BOARDS = {
    "no": {"host": "www.academicwork.no", "list": "/ledige-stillinger", "prefix": "/ledige-stillinger/j/", "key": "academicwork-no", "country": "NO", "lang": "nb"},
}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+47[\s ]?)?(?:\d{2}[\s ]?\d{2}[\s ]?\d{2}[\s ]?\d{2}|\d{3}[\s ]?\d{2}[\s ]?\d{3})(?!\d)")
ROW_RE = re.compile(r"<url>\s*<loc>([^<]+)</loc>(?:\s*<lastmod>([^<]+)</lastmod>)?", re.S)
FLIGHT_RE = re.compile(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', re.S)
TOTAL_RE = re.compile(r'"totalItems":(\d+)')
TREFF_RE = re.compile(r'"children":"(\d[\d ]*) treff"')

_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[academicwork] {msg}", file=sys.stderr)


def board_of(host):
    """The board for a code or a hostname — refused before any request when unknown."""
    if host is None:
        return BOARDS["no"]
    h = host.lower().strip()
    if h in BOARDS:
        return BOARDS[h]
    for b in BOARDS.values():
        if h in (b["host"], b["host"].removeprefix("www.")):
            return b
    die(f"--host {host}: not a board this script knows ({', '.join(BOARDS)}) — another front gets its own `adapter` issue first")


def ad_re(b):
    return re.compile(r"^" + re.escape(b["prefix"]) + r"([^/]+)/([A-Z0-9]{6})/?$")


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
    if parts.path.startswith("/api/"):
        die(f"{url}: /api/ is refused in writing — the CMS's own routes are never called", EXIT_REFUSED)
    gate(url)
    if parts.netloc not in _PACES:
        _PACES[parts.netloc] = Pace(parts.netloc, own=2.0)   # no Crawl-delay written; 2 s is ours
    _PACES[parts.netloc].wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9", "Accept-Language": "nb"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def flight(body):
    """The page's React flight chunks, `{id: payload}` — a `T<hex>,` chunk is text of that many bytes (it may hold newlines), any other runs to the line's end."""
    raw = "".join(FLIGHT_RE.findall(body or ""))
    if not raw:
        return {}
    try:
        s = json.loads('"' + raw + '"')
    except ValueError:
        return {}
    b, i, out = s.encode("utf-8"), 0, {}
    while i < len(b):
        m = re.match(rb"([0-9a-f]+):", b[i:])
        if not m:
            j = b.find(b"\n", i)
            if j < 0:
                break
            i = j + 1
            continue
        cid = m.group(1).decode()
        i += m.end()
        if b[i:i + 1] == b"T":
            k = b.find(b",", i)
            n = int(b[i + 1:k], 16)
            out[cid] = b[k + 1:k + 1 + n].decode("utf-8", "replace")
            i = k + 1 + n
        else:
            j = b.find(b"\n", i)
            j = len(b) if j < 0 else j
            out[cid] = b[i:j].decode("utf-8", "replace")
            i = j + 1
    return out


def deref(v, chunks):
    """A `$<id>` reference resolved to its text chunk; a plain string passes."""
    if isinstance(v, str) and re.fullmatch(r"\$[0-9a-f]+", v):
        return chunks.get(v[1:])
    return v


def advert_of(body):
    """The `advert` object the ad page ships in its flight data, its text references resolved — `None` when the page carries none."""
    chunks = flight(body)
    for v in chunks.values():
        i = v.find('"advert":{')
        if i < 0:
            continue
        try:
            obj, _ = json.JSONDecoder().raw_decode(v[i + len('"advert":'):])
        except ValueError:
            continue
        if isinstance(obj, dict) and obj.get("shortAdvertId"):
            at = obj.get("advertText") or {}
            for k, sec in list(at.items()):
                if isinstance(sec, dict):
                    sec["text"] = deref(sec.get("text"), chunks)
                else:
                    at[k] = deref(sec, chunks)
            return obj
    return None


def stated(body):
    """The count the listing states — the pager's `totalItems`, else «N treff» — read in the decoded flight data, or `None`."""
    text = "\n".join(flight(body).values())
    m = TOTAL_RE.search(text)
    if m:
        return int(m.group(1))
    m = TREFF_RE.search(text)
    return int(m.group(1).replace(" ", "")) if m else None


def label(v):
    return (v or {}).get("label") if isinstance(v, dict) else None


def record(ad, b, url=None):
    at = ad.get("advertText") or {}
    sm = ad.get("summary") or {}

    def sec(name):
        s = at.get(name)
        return scrub((s.get("text") if isinstance(s, dict) else s) or "")

    def sm_text(name):
        s = sm.get(name)
        return (s.get("text") or "").strip() or None if isinstance(s, dict) else None

    oid = ad.get("shortAdvertId")
    locs = [l for l in (ad.get("locations") or []) if isinstance(l, dict)]
    jt = ad.get("jobType") or {}
    return {
        "source": b["key"], "country": b["country"], "ledger_id": f"{b['key']}:{oid}", "id": oid, "advert_id": ad.get("advertId"),
        "url": ad.get("absoluteUrl") or url or (f"https://{b['host']}{ad['url']}" if ad.get("url") else None),
        "title": (ad.get("advertTitle") or "").strip() or None,
        "lead_in": scrub(at.get("leadIn") if isinstance(at.get("leadIn"), str) else (at.get("leadIn") or {}).get("text")),
        "company": (ad.get("companyName") or "").strip() or None if ad.get("showCompanyName", True) else None,   # the client, when the site shows it
        "company_site": ad.get("companySiteUrl") or None,
        "agency": "Academic Work", "job_type": label(jt), "job_type_id": jt.get("id"),   # recruitment: the client hires; staffing: the agency does
        "employer_is_the_agency": jt.get("id") == "staffing",
        "place": ad.get("locationCity") or (locs[0].get("city") if locs else None),
        "locations": [{"city": l.get("city"), "country": l.get("country"), "lat": (l.get("coordinates") or {}).get("lat"), "lon": (l.get("coordinates") or {}).get("lon")} for l in locs] or None,
        "business_area": label(ad.get("businessArea")), "category": label(ad.get("jobCategory")), "role": label(ad.get("role")),
        "work_extent": label(ad.get("workExtent")), "work_extent_text": sm_text("workExtent"),
        "start_date": (ad.get("startDate") or "")[:10] or None, "start_text": ad.get("startDateDescription") or sm_text("startDate"),
        "other": sm_text("other"), "green_job": sm.get("greenJob"), "is_academy": bool(ad.get("isAcademyAdvert")),
        "tags": [label(t) or t for t in (ad.get("jobTags") or [])] or None,
        "posted": (ad.get("publishTimestamp") or "")[:10] or None, "valid_through": (ad.get("unpublishTimestamp") or "")[:10] or None,
        "published": ad.get("published"), "language": (ad.get("language") or b["lang"]).lower(),
        "external_application_url": ad.get("externalApplicationUrl") or None,   # the client's own posting, when the site names it — never followed
        "about_the_job": sec("yourNewWorkplace"), "tasks": sec("workTasks"), "requirements": sec("requirements"), "about_the_company": sec("clientInformation"),
        # `owningCm` — the consultant manager's employee reference, name and e-mail — is on every advert and is never emitted
        "contacts_withheld": True,
    }


def sitemap_rows(b):
    url = f"https://{b['host']}/sitemap.xml"
    code, body = request(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    rx, rows, seen, other = ad_re(b), [], set(), 0
    for loc, lastmod in ROW_RE.findall(body):
        m = rx.match(urllib.parse.urlsplit(loc).path)
        if not m:
            other += 1
            continue
        if m.group(2) in seen:
            continue
        seen.add(m.group(2))
        rows.append({"source": b["key"], "country": b["country"], "ledger_id": f"{b['key']}:{m.group(2)}", "id": m.group(2), "url": loc, "slug": m.group(1), "lastmod": lastmod or None, "contacts_withheld": True, "language": b["lang"]})
    if not rows:
        die(f"{url}: 200 and not one {b['prefix']}<slug>/<id> row among {th(other)} — the sitemap's shape changed", EXIT_PARTIAL)
    return rows, other


def cmd_sitemap(a):
    b = board_of(a.host)
    rows, other = sitemap_rows(b)
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{th(len(rows))} job row(s) in {b['host']}'s sitemap ({th(other)} other rows set aside — pages, articles, programmes) — the inventory; the listing states the count, `list` prints both.")
    if a.limit and a.limit < len(rows):
        note(f"{th(len(emitted))} emitted of the {th(len(rows))} — bounded by --limit.")


def cmd_list(a):
    b = board_of(a.host)
    url = f"https://{b['host']}{b['list']}"
    code, body = request(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    total = stated(body)
    if total is None:
        die(f"{url}: 200 and no «N treff» nor `totalItems` in the page — the template changed; not an empty market", EXIT_PARTIAL)
    rows, other = sitemap_rows(b)
    out, gone = [], 0
    for r in rows:
        if a.limit and len(out) >= a.limit:
            break
        code, page = request(r["url"])
        if code == 404:
            gone += 1
            continue
        if code != 200:
            die(f"{r['url']}: HTTP {code}", EXIT_PARTIAL)
        ad = advert_of(page)
        if ad is None:
            die(f"{r['url']}: 200 without an `advert` in the page's flight data — the template changed; not an empty job", EXIT_PARTIAL)
        rec = record(ad, b, r["url"])
        rec["lastmod"] = r["lastmod"]
        out.append(rec)
    for rec in out:
        print(json.dumps(rec, ensure_ascii=False))
    n = len(out)
    if a.limit and a.limit < len(rows):
        note(f"{th(n)} emitted of the {th(total)} the site states on {b['host']}{b['list']} ({th(len(rows))} in the sitemap, {th(gone)} gone) — walked by request (--limit), not a shortfall.")
    else:
        verdict = "equal" if n == total else (f"{th(total - n)} short" if n < total else f"{th(n - total)} more emitted")
        note(f"{th(n)} emitted ({th(len(rows))} in the sitemap, {th(gone)} gone), the site states {th(total)} — {verdict}.")
    note("`owningCm` (the consultant's name and e-mail) is on every advert and never emitted; texts scrubbed; the application form never touched.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    b = next((x for x in BOARDS.values() if parts.netloc in (x["host"], x["host"].removeprefix("www."))), None)
    m = ad_re(b).match(parts.path) if b else None
    if not m:
        die(f"{a.url}: not a job address ({' / '.join('https://' + x['host'] + x['prefix'] + '<slug>/<id>' for x in BOARDS.values())})")
    url = f"https://{b['host']}{parts.path.rstrip('/')}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    ad = advert_of(body)
    if ad is None:
        die(f"{url}: 200 without an `advert` in the page's flight data — the template changed", EXIT_PARTIAL)
    print(json.dumps(record(ad, b, url), ensure_ascii=False))
    note(f"{url}: read from the page's own `advert`; `owningCm` withheld; texts scrubbed; the application form never touched.")


def main():
    p = argparse.ArgumentParser(description="Academic Work Norway — the listing's stated count beside the sitemap's inventory, each ad read from its page's own object; the consultant never emitted. Issue #370.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s_ = sub.add_parser("sitemap", help="every job row of sitemap.xml (1 request)")
    s_.add_argument("--host", help="board code or hostname (no)")
    s_.add_argument("--limit", type=int)
    s_.set_defaults(fn=cmd_sitemap)
    l_ = sub.add_parser("list", help="the listing's count, then the sitemap's ads read from their pages")
    l_.add_argument("--host", help="board code or hostname (no)")
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
