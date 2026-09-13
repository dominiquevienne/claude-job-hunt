#!/usr/bin/env python3
"""NAV Arbeidsplassen (`arbeidsplassen.nav.no`) — Norway's public employment service, through the sitemap it declares and the unkeyed search API its own page calls; the API's total printed beside every walk. Issue #365.

  arbeidsplassen.py sitemap [--limit N] [--since YYYY-MM-DD]
  arbeidsplassen.py search [--q TEXT] [--county VESTLAND] [--municipal BERGEN] [--limit N] [--pages N]
  arbeidsplassen.py ad --url <https://arbeidsplassen.nav.no/stillinger/stilling/<uuid>>

TWO ROUTES, BOTH WRITTEN BY THE SITE. `robots.txt` (`*`, `Disallow:` empty
— everything open) declares `/sitemap.xml`, whose `/stillinger/sitemap.xml`
lists every advertisement as `/stillinger/stilling/<uuid>` with a
`<lastmod>` — **13 615 distinct on 2026-09-13 17:33 UTC**. The site's
search page calls `/stillinger/api/search` (Elasticsearch behind it, no
key): `size` up to 100, `from` up to **10 000 — «Pagination depth exceeds
maximum allowed window» past it**, filters `q`, `county`, `municipal`;
`hits.total.value` is the site's count — **13 620 the same minute**, five
more than the file: a live board between two reads. `aggregations
.positioncount.sum` (27 406) is a HEADCOUNT, positions not advertisements
— printed as such, never compared. The country page measured a **429 after
~200 reads** on 2026-08-31: this adapter spaces 1 s and stops on a 429
without a retry (exit 7).

THE HIT carries title, employer (businessName / employer.name), the
locations (county, municipal, city — the street address is dropped),
published, expires, source (**FINN, IMPORTAPI, Stillingsregistrering,
EURES** — half the inventory comes from FINN.no through the door the
State opens), engagementType, positionCount, properties.applicationdue,
jobtitle, remote, education, experience, workLanguage — no engagement
type, extent or position count in the hit (those are on the page). No
description in the list; the advertisement page (Next.js, no JSON-LD) renders it under
«Om jobben», «Hva vi ser etter», «Arbeidsoppgaver», «Vi tilbyr» and a
`<dt>/<dd>` list — `ad` reads those and **drops «Kontaktperson for
stillingen» whole**: the page embeds `contactList` with names, e-mails
and telephones, and none of it leaves this adapter.
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

HOST = "arbeidsplassen.nav.no"
BASE = f"https://{HOST}"
SITEMAP = f"{BASE}/stillinger/sitemap.xml"
API = f"{BASE}/stillinger/api/search"
UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
AD_RE = re.compile(r"^https://arbeidsplassen\.nav\.no/stillinger/stilling/(" + UUID + r")/?$")
PAGE_SIZE = 100
WINDOW = 10000            # the API's own limit on `from` — measured, not chosen

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[arbeidsplassen] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=1.0)   # no Crawl-delay in the rules; 1 s is ours, and a 429 stops the run


def get(url, accept="text/html"):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": accept, "Accept-Language": "nb,no,en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h\d>|</dt>|</dd>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def api_page(params):
    """One API page; a 429 is the host saying slow down and this stops without a retry."""
    url = API + "?" + urllib.parse.urlencode(params)
    code, body = get(url, accept="application/json")
    if code == 429:
        die(f"{url}: HTTP 429 — the host asks to slow down (a 429 after ~200 reads was measured on 2026-08-31); stopped without a retry.", EXIT_REFUSED)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    try:
        j = json.loads(body)
    except ValueError:
        die(f"{url}: not JSON ({len(body)} characters)", EXIT_PARTIAL)
    if isinstance(j, dict) and j.get("error"):
        die(f"{url}: the API says «{j['error']}»", EXIT_PARTIAL)
    hits = (j.get("hits") or {})
    total = ((hits.get("total") or {}).get("value"))
    return total, [h.get("_source") or {} for h in (hits.get("hits") or [])], j.get("aggregations") or {}


def row(src):
    locs = src.get("locationList") or []
    loc = locs[0] if locs and isinstance(locs[0], dict) else {}
    props = src.get("properties") if isinstance(src.get("properties"), dict) else {}
    emp = src.get("employer") if isinstance(src.get("employer"), dict) else {}
    ident = src.get("uuid")
    return {
        "source": "arbeidsplassen", "country": "NO", "ledger_id": f"arbeidsplassen:{ident}", "id": ident,
        "url": f"{BASE}/stillinger/stilling/{ident}",
        "title": src.get("title"), "employer": src.get("businessName") or emp.get("name"),
        # the street address the hit carries is a premises' address and is not emitted
        "city": loc.get("city"), "municipal": loc.get("municipal"), "county": loc.get("county"), "address_country": loc.get("country"),
        "published": src.get("published"), "expires": src.get("expires"),
        "application_due": props.get("applicationdue"),
        # engagement type, extent and position count are on the advertisement page, not in the search hit
        "remote": props.get("remote"),
        "listed_via": src.get("source"),          # FINN · IMPORTAPI · Stillingsregistrering · EURES — the door, not the employer
        "occupations": [f"{o.get('level1')} / {o.get('level2')}" for o in (src.get("occupationList") or []) if isinstance(o, dict)],
        "categories": [c.get("name") for c in (src.get("categoryList") or []) if isinstance(c, dict) and c.get("name")],
        "work_language": props.get("workLanguage"), "education": props.get("education"), "experience": props.get("experience"),
        "language": "no",
    }


def cmd_search(a):
    params = {"size": PAGE_SIZE, "from": 0}
    for k in ("q", "county", "municipal"):
        if getattr(a, k):
            params[k] = getattr(a, k)
    rows, seen, page, total = [], set(), 1, None
    aggs = None
    while True:
        params["from"] = (page - 1) * PAGE_SIZE
        if params["from"] >= WINDOW:
            note(f"the API's window ends at from={WINDOW}: {th(len(rows))} read, the site states {th(total)} — narrow with --county/--municipal/--q to read the rest.")
            break
        t, hits, ag = api_page(params)
        if total is None:
            total, aggs = t, ag
        new = 0
        for h in hits:
            if not h.get("uuid") or h["uuid"] in seen:
                continue
            seen.add(h["uuid"])
            rows.append(row(h))
            new += 1
        if not hits or new == 0 or len(rows) >= (total or 0):
            break
        if a.pages and page >= a.pages:
            break
        if a.limit and len(rows) >= a.limit:
            break
        page += 1
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    head = ((aggs or {}).get("positioncount") or {}).get("sum", {}).get("value")
    where = "(" + ", ".join(f"{k}={params[k]}" for k in ("q", "county", "municipal") if k in params) + ")" if any(k in params for k in ("q", "county", "municipal")) else "(no filter)"
    if total is None:
        die("the API answered without hits.total — no count to compare; the shape changed.", EXIT_PARTIAL)
    bounded = (a.pages and page >= a.pages and total > page * PAGE_SIZE) or (a.limit and a.limit < total)
    if n == total:
        note(f"{th(n)} emitted over {page} page(s), site states {th(total)} {where} — equal.")
    elif bounded:
        note(f"{th(n)} emitted of the {th(total)} the site states {where} — {page} page(s) of {PAGE_SIZE} walked by request (--pages/--limit), not a shortfall.")
    else:
        note(f"{th(n)} emitted over {page} page(s), site states {th(total)} {where} — {th(abs(total - n))} " + ("short" if total > n else "more emitted than the site states") + ".")
    if head:
        note(f"the API also states {th(int(head))} POSITIONS (positioncount.sum) — a headcount, not advertisements; printed, never compared.")


def cmd_sitemap(a):
    code, xml = get(SITEMAP, accept="application/xml")
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_PARTIAL)
    rows, seen, undated = [], set(), 0
    for m in re.finditer(r"<url>\s*<loc>\s*([^<]+?)\s*</loc>(.*?)</url>", xml, re.S):
        u = htmlmod.unescape(m.group(1))
        mm = AD_RE.match(u)
        if not mm or mm.group(1) in seen:
            continue
        seen.add(mm.group(1))
        lm = re.search(r"<lastmod>\s*([^<]+?)\s*</lastmod>", m.group(2))
        if not lm:
            undated += 1
        if a.since and lm and lm.group(1)[:10] < a.since:
            continue
        rows.append({"source": "arbeidsplassen", "country": "NO", "ledger_id": f"arbeidsplassen:{mm.group(1)}", "id": mm.group(1), "url": u,
                     "lastmod": lm.group(1) if lm else None})
    if not seen:
        die(f"{SITEMAP}: {xml.count('<loc>')} <loc> and no advertisement address — a reading fault, not an empty board.", EXIT_PARTIAL)
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    note(f"**{th(len(seen))} distinct advertisement uuid(s)** in the sitemap, {undated} without <lastmod>; {th(len(emitted))} emitted"
         + (f" dated on or after {a.since}" if a.since else "") + (f" (--limit {a.limit})" if a.limit else "") + ".")
    total, _, _ = api_page({"size": 1, "from": 0})
    if total is None:
        note("the API answered without hits.total — no second source this run.")
    elif total == len(seen):
        note(f"{th(len(seen))} in the sitemap, the API states {th(total)} — equal.")
    else:
        note(f"{th(len(seen))} in the sitemap, the API states {th(total)} — {th(abs(total - len(seen)))} " + ("more in the API" if total > len(seen) else "more in the file") + "; a live board between two reads, and the sitemap is rebuilt on its own clock.")


def cmd_ad(a):
    m = AD_RE.match((a.url or "").strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/stillinger/stilling/<uuid>")
    ident = m.group(1)
    code, body = get(a.url)
    if code in (404, 410):
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    main = body[body.find("<main"):body.find("</main>")] if "<main" in body else body
    if "<dt" not in main:
        die(f"{a.url}: no <dt>/<dd> list on the page ({len(body)} characters) — not an advertisement page as read.", EXIT_PARTIAL)
    fields = {}
    for dm in re.finditer(r"<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>", main, re.S):
        fields.setdefault(text(dm.group(1)), text(dm.group(2)))
    # sections by <h2>; «Kontaktperson for stillingen» is dropped whole — names, e-mails, telephones live there
    sections, dropped = {}, []
    parts = re.split(r"<h2[^>]*>(.*?)</h2>", main, flags=re.S)
    for i in range(1, len(parts) - 1, 2):
        name = text(parts[i])
        if "Kontaktperson" in name or "Del annonsen" in name or "Lignende" in name:
            if "Kontaktperson" in name:
                dropped.append(name)
            continue
        sections[name] = text(parts[i + 1])[:20000]
    title = text((re.search(r"<h1[^>]*>(.*?)</h1>", main, re.S) or [None, ""])[1]) or fields.get("Stillingstittel")
    print(json.dumps({
        "source": "arbeidsplassen", "country": "NO", "ledger_id": f"arbeidsplassen:{ident}", "id": ident, "url": a.url,
        "title": title, "job_title": fields.get("Stillingstittel"), "engagement": fields.get("Type ansettelse"),
        "start": fields.get("Oppstart"), "hours": fields.get("Arbeidstid"), "sector": fields.get("Sektor"),
        "last_changed": fields.get("Sist endret"), "listed_via": fields.get("Hentet fra"), "reference": fields.get("Referanse"),
        "fields": {k: v for k, v in fields.items() if k not in ("Nettsted",)},
        "sections": sections, "contact_dropped": dropped, "language": "no",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="NAV Arbeidsplassen — Norway's public employment service: the declared sitemap, the unkeyed search API its page calls (total printed beside the walk, 10 000-deep window, stop on 429), and the advertisement page with its contact section dropped. Issue #365.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="every advertisement uuid with its lastmod, and the API's total beside the count — two requests")
    s.add_argument("--limit", type=int)
    s.add_argument("--since", help="keep entries with lastmod on or after YYYY-MM-DD")
    s.set_defaults(fn=cmd_sitemap)
    q = sub.add_parser("search", help="the API, 100 a page, 1 s apart; --q/--county/--municipal narrow it; the window ends at 10 000")
    q.add_argument("--q")
    q.add_argument("--county", help="e.g. VESTLAND, OSLO — the API's own upper-case names")
    q.add_argument("--municipal", help="e.g. BERGEN")
    q.add_argument("--pages", type=int)
    q.add_argument("--limit", type=int)
    q.set_defaults(fn=cmd_search)
    d = sub.add_parser("ad", help="one advertisement page — the <dt>/<dd> list and the sections; «Kontaktperson» dropped")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
