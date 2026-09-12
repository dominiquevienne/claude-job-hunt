#!/usr/bin/env python3
"""Albania Jobs (`albaniajobs.al`) — a WordPress job board read through its REST collection, with the job sitemap as the second document.

  albaniajobs.py list [--limit N] [--no-terms] [--no-site-total]
  albaniajobs.py ad --url <advertisement URL>

THE REST COLLECTION IS THE ROUTE, THE JOB SITEMAP IS THE SECOND SOURCE

`/wp-json/wp/v2/job-listings?per_page=100&page=N` returns every published
listing with its post id, link, title, date, rendered content and excerpt,
the WP Job Manager meta and the taxonomy term ids — **123 listings in two
pages on 2026-09-12 11:33 UTC, 123 distinct ids.** `job_listing-sitemap.xml`
(AIOSEO) lists the same advertisements by URL — 123 `<loc>` the same
minute — and the adapter prints the two side by side: «n emitted, sitemap
lists N — equal», or «k short». *Neither document carries a count of its
own; the agreement of two enumerations is the check.*

**THE HOST ASKS FOR `Crawl-delay: 10` AND IT IS HONOURED** — `_pace.Pace`
reads it from the rules; a full `list` is five requests (two REST pages,
three term taxonomies), fifty seconds. `--no-terms` skips the three and emits
term ids instead of names.

THE URL CARRIES NO ID — `/job/13-truck-driver-poland/`: the leading number
is the same `13` on most entries, not a key. The key is the WordPress post
id from the REST `id`, and `ad` reads it back from the page's `JobPosting`
JSON-LD (`identifier.value` = `…?post_type=job_listing&p=<id>`).

WHAT THE REST META HOLDS, MEASURED ON THE 123 (2026-09-12): `_company_name`
filled on 2, `_job_salary` / `_currency` / `_unit` on 0, `_remote_position`
on 1, `_filled` on 2 — **the employer is not in the collection**; the page's
JSON-LD `hiringOrganization.name` has it, so `ad` is where the employer
comes from. Regions: Tiranë 91, Shqipëri 11, Vlorë 11, Durrës 2, Kavajë 2,
Kosovë 1 (term counts sum to 123, a third agreement). Types: «Kohë e Plotë»
118. **The board is bilingual (Albanian / English) and says nothing per
listing; no `language` is emitted.**

THE RULES refuse `anthropic-ai` — a name no request from here carries
(#233, fourth form) — and for `*` the WordPress paths and `/*?s=*`,
`Crawl-delay: 10`; `identity()` answers `claude-user`, `verdict()` sweeps.
Measured 2026-09-12 11:18–11:35 UTC (#233, lot 4).
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
from _ldjson import absent_reason, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _sitemap import locs as sitemap_locs
from _ua import UA
from _zero import empty_first_page

HOST = "albaniajobs.al"
BASE = "https://albaniajobs.al"
REST = BASE + "/wp-json/wp/v2/job-listings?per_page=100&page={page}"
TERMS = {"job_listing_region": BASE + "/wp-json/wp/v2/job_listing_region?per_page=100",
         "job-types": BASE + "/wp-json/wp/v2/job-types?per_page=100",
         "job-categories": BASE + "/wp-json/wp/v2/job-categories?per_page=100"}
SITEMAP = BASE + "/job_listing-sitemap.xml"
AD_RE = re.compile(r"^https://albaniajobs\.al/job/[^/]+/?$")
POST_ID_RE = re.compile(r"[?&](?:amp;)?(?:#038;)?p=(\d+)")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[albaniajobs] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # the host declares Crawl-delay: 10 — Pace reads it; 2 s is only the floor


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "application/json,text/html,application/xml;q=0.9",
        "Accept-Language": "sq,en;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"[ \t]+", " ", htmlmod.unescape(markup)).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def rest_page(page):
    """One page of the collection: (status, list) — a JSON error object is
    returned as an empty list with its code, and the caller decides."""
    code, body = get(REST.format(page=page))
    if code != 200:
        return code, []
    try:
        d = json.loads(body)
    except ValueError:
        die(f"page {page}: HTTP 200 and not JSON — {body[:120]!r}", EXIT_PARTIAL)
    if isinstance(d, dict):
        # WordPress answers 400 `rest_post_invalid_page_number` past the end;
        # a 200 with an object is something else and is said out loud
        die(f"page {page}: an object, not a list — {d.get('code')}: {d.get('message')}", EXIT_PARTIAL)
    return code, d


def load_terms():
    names = {}
    for tax, url in TERMS.items():
        code, body = get(url)
        if code != 200:
            note(f"{tax}: HTTP {code} — ids emitted for this taxonomy this run")
            continue
        try:
            names[tax] = {t["id"]: htmlmod.unescape(t["name"]) for t in json.loads(body)}
        except (ValueError, TypeError, KeyError):
            note(f"{tax}: unreadable — ids emitted for this taxonomy this run")
    return names


def cmd_list(a):
    rows, seen, page, raw = [], set(), 1, 0
    while True:
        code, items = rest_page(page)
        if code == 400 and page > 1:
            break                              # past the last page — WordPress' way of saying so
        if code != 200:
            die(f"{REST.format(page=page)}: HTTP {code}", EXIT_PARTIAL)
        if not items and page == 1:
            die(empty_first_page("albaniajobs", "", "listing", where=REST.format(page=1)), EXIT_PARTIAL)
        raw += len(items)
        for it in items:
            ident = str(it.get("id") or "")
            if not ident or ident in seen:
                continue
            seen.add(ident)
            rows.append(it)
        if len(items) < 100:
            break
        page += 1
    names = {} if a.no_terms else load_terms()

    def named(tax, ids):
        table = names.get(tax)
        return [table.get(i, i) if table else i for i in (ids or [])]
    out = []
    for it in rows:
        meta = it.get("meta") or {}
        out.append({
            "source": "albaniajobs", "country": "AL", "ledger_id": f"albaniajobs:{it['id']}",
            "id": str(it["id"]), "url": it.get("link"),
            "title": text((it.get("title") or {}).get("rendered")),
            # 2 of 123 filled on 2026-09-12 — the employer lives on the page (see `ad`)
            "employer": (meta.get("_company_name") or "").strip() or None,
            # WordPress writes `date_gmt` without a zone marker; it is UTC, and the Z says so
            "posted": (it["date_gmt"] + "Z") if it.get("date_gmt") else it.get("date"),
            "modified": (it["modified_gmt"] + "Z") if it.get("modified_gmt") else it.get("modified"),
            "regions": named("job_listing_region", it.get("job_listing_region")),
            "types": named("job-types", it.get("job-types")),
            "categories": named("job-categories", it.get("job-categories")),
            "remote": bool(meta.get("_remote_position")),
            "filled": bool(meta.get("_filled")),
            "salary": (meta.get("_job_salary") or "").strip() or None,
            "salary_currency": (meta.get("_job_salary_currency") or "").strip() or None,
            "salary_unit": (meta.get("_job_salary_unit") or "").strip() or None,
            "excerpt": text((it.get("excerpt") or {}).get("rendered"))[:600],
        })
    for r in out[:a.limit] if a.limit else out:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{raw} listing(s) over {page} REST page(s); **{len(out)} distinct post id(s)**"
         + (f" ({a.limit} printed under --limit)" if a.limit else "") + "."
         + ("" if names else " Term ids emitted, not names."))
    if a.no_site_total:
        return
    code, xml = get(SITEMAP)
    if code != 200:
        note(f"{SITEMAP}: HTTP {code} — no second source this run.")
        return
    listed = {u.strip() for u in sitemap_locs(xml) if "/job/" in u}
    n, m = len(out), len(listed)
    if n == m:
        note(f"{th(n)} emitted, sitemap lists {th(m)} — equal.")
    else:
        note(f"{th(n)} emitted, sitemap lists {th(m)} — {th(abs(m - n))} "
             + ("short" if m > n else "more in the collection than the sitemap lists")
             + "; two enumerations of one store, and they part.")


def cmd_ad(a):
    if not AD_RE.match(a.url.strip()):
        die(f"{a.url}: not an advertisement address — expected {BASE}/job/<slug>/")
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    found = postings(body)
    if not found:
        why = absent_reason(body)
        if getattr(why, "our_fault", False):
            die(f"{a.url}: {why} **The page announces a JobPosting and this read none.**")
        die(f"{a.url}: {why}", EXIT_PARTIAL)
    d = found[0]
    org = d.get("hiringOrganization") or {}
    idv = d.get("identifier") or {}
    m = POST_ID_RE.search(htmlmod.unescape(str(idv.get("value") or "")) if isinstance(idv, dict) else "")
    ident = m.group(1) if m else None
    loc = d.get("jobLocation") or {}
    addr = loc.get("address") if isinstance(loc, dict) else loc
    place = text(addr) if isinstance(addr, str) else text((addr or {}).get("addressLocality")) if isinstance(addr, dict) else None
    print(json.dumps({
        "source": "albaniajobs", "country": "AL",
        "ledger_id": f"albaniajobs:{ident}" if ident else None, "id": ident, "url": a.url,
        "title": text(d.get("title")),
        "employer": org.get("name") if isinstance(org, dict) else None,
        "place": place or None,                      # «Shqipëri» as a string, not an address object
        "remote": d.get("jobLocationType") == "TELECOMMUTE",
        "posted": d.get("datePosted"),
        "direct_apply": d.get("directApply"),
        "description": text(htmlmod.unescape(d.get("description") or ""))[:20000],
    }, ensure_ascii=False))
    if not ident:
        note("the page's JobPosting carries no `identifier` with a post id — `id` is null this run.")


def main():
    p = argparse.ArgumentParser(description="Albania Jobs — a WordPress board through its REST collection, the job sitemap as the second source; Crawl-delay 10 honoured.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every published listing — 2 REST pages + 3 taxonomies + the sitemap, ten seconds apart")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-terms", action="store_true", help="skip the three taxonomy requests; emit term ids")
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advertisement, from the page's JobPosting JSON-LD")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
