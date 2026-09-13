#!/usr/bin/env python3
"""Tecnoempleo (`www.tecnoempleo.com`) — Spain's IT board, read through its one sitemap and the JobPosting every offer carries; the listing's stated count as the second source.

  tecnoempleo.py sitemap [--limit N] [--no-site-total]
  tecnoempleo.py ad --url <offer URL>

THE RULES NAME SIX ANTHROPIC AGENTS AND CLOSE EVERYTHING TO THEM — AND NOT THIS ONE

`robots.txt` (953 B, written by hand) refuses the whole site to `AnthropicBot`,
`Claude`, `ClaudeBot`, `anthropic-ai`, `Claude-Web` and `Claude-SearchBot`
— and to `yacybot`, `emsi_bot`, `GPTBot`. **`Claude-User`, the token a
request from here carries, is not among them and falls under `*`**, which
refuses seventeen paths of its own (statistics, images, policies, the
candidate area, ajax, matomo, the RSS alert, `/accesoempresa.php`) and
nothing of the offers. Under the owner's decision of 2026-09-07 (a group
that names one token does not bind the other; #233: the hand-written
files are measured like the others) this adapter reads under
`Claude-User` — **and the card records the six names, with the reservation
that a file listing six Anthropic agents reads as an intention toward
Anthropic, for the owner to weigh.** The `*` refusals are honoured by the
guard on every URL; the adapter asks for nothing under them.

THE SITEMAP IS THE ROUTE, THE LISTING'S COUNT IS THE SECOND SOURCE

`/sitemap.xml` is one `urlset` of 30 891 `<loc>` on 2026-09-13 10:52 UTC,
of which **2 146 are offers** — `/<slug>/<skills>/rf-<hash>`, 2 146 distinct
hashes, real `<lastmod>` (1 584 distinct dates; 1 066 on the day of the
read) — the rest company pages and site pages. `/ofertas-trabajo/` states
«2.592 Ofertas de Trabajo en Informática y Telecomunicaciones» and «1-30 de
2.592»; the adapter prints the two side by side — «n emitted, site states N
— equal / k short» — and on the day it was written they were 446 apart:
two views of one store, neither copied as the board's size.

EVERY OFFER CARRIES A JobPosting IN JSON-LD — `title`, `description`,
`datePosted`, `employmentType`, `directApply`, `hiringOrganization.name`,
`jobLocation.address` (`addressLocality`, `addressRegion`,
`addressCountry: ES`), and `identifier.value` — **the EMPLOYER's id (the
number of its logo file), not the offer's, whose key is the `rf-` hash in
the URL**; no `baseSalary`, no `validThrough` on the page read. The only
`tel:` on the page is the board's own; nothing of a recruiter's contacts is
read.

Measured 2026-09-13 10:22–10:53 UTC (#233, lot 8 → this adapter).
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
from _sitemap import locs as sitemap_locs, maybe_gunzip
from _ua import UA
from _zero import empty_first_page

HOST = "www.tecnoempleo.com"
BASE = "https://" + HOST
SITEMAP = BASE + "/sitemap.xml"
LISTING = BASE + "/ofertas-trabajo/"
AD_RE = re.compile(r"^https://www\.tecnoempleo\.com/[^/?#]+/[^/?#]+/rf-([a-z0-9]+)/?$")
# «2.592 Ofertas de Trabajo en Informática…» — a Spanish thousands dot
SITE_COUNT_RE = re.compile(r"([\d]{1,3}(?:\.\d{3})*|\d+)\s+Ofertas de (?:Trabajo|Empleo)", re.I)

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[tecnoempleo] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # no Crawl-delay for us (Bingbot gets 5); 2 s is ours


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.5",
        "Accept-Language": "es,en;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            raw = maybe_gunzip(r.read())
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


def site_count(body):
    m = SITE_COUNT_RE.search(text(body))
    return int(m.group(1).replace(".", "")) if m else None


def cmd_sitemap(a):
    code, xml = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_PARTIAL)
    raw, unmatched, rows, seen = 0, 0, [], set()
    stamps = set()
    for m in re.finditer(r"<loc>\s*([^<]+?)\s*</loc>\s*(?:<lastmod>\s*([^<]+?)\s*</lastmod>)?", xml):
        if AD_RE.match(m.group(1)) and m.group(2):
            stamps.add(m.group(2)[:10])
    for loc in sitemap_locs(xml):
        raw += 1
        m = AD_RE.match(loc.strip())
        if not m:
            unmatched += 1
            continue
        ident = m.group(1)
        if ident in seen:
            continue
        seen.add(ident)
        rows.append({"source": "tecnoempleo", "country": "ES", "ledger_id": f"tecnoempleo:{ident}", "id": ident, "url": loc.strip()})
    if raw == 0:
        die(empty_first_page("tecnoempleo", xml, "<loc>", where=SITEMAP), EXIT_PARTIAL)
    if not rows:
        die(f"{SITEMAP}: {raw} <loc> and not one of the shape /<slug>/<skills>/rf-<hash> — the offer addresses moved; nothing here says the board is empty.", EXIT_PARTIAL)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{raw} <loc> in the sitemap; {raw - unmatched} of the offer shape, {unmatched} not (company and site pages); "
         f"**{th(len(rows))} distinct offer(s)**" + (f" ({a.limit} printed under --limit)" if a.limit and len(rows) > a.limit else "")
         + f"; {len(stamps)} distinct <lastmod> date(s) on them" + (" — real dates, not a rebuild stamp." if len(stamps) > 1 else " — a single value, a rebuild stamp."))
    if a.no_site_total:
        return
    code, page = get(LISTING)
    stated = site_count(page) if code == 200 else None
    if stated is None:
        note(f"{LISTING} states no count this run (HTTP {code}) — no second source.")
    elif stated == len(rows):
        note(f"{th(len(rows))} emitted, site states {th(stated)} on {LISTING} — equal.")
    else:
        note(f"{th(len(rows))} emitted, site states {th(stated)} on {LISTING} — {th(abs(stated - len(rows)))} "
             + ("short" if stated > len(rows) else "more in the sitemap than the site states")
             + "; the sitemap and the listing are two views of one store.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an offer address — expected {BASE}/<slug>/<skills>/rf-<hash>")
    ident = m.group(1)
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
    loc = d.get("jobLocation") or {}
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
    et = d.get("employmentType")
    print(json.dumps({
        "source": "tecnoempleo",
        "country": ((addr.get("addressCountry") or "").strip() or "ES") if isinstance(addr, dict) else "ES",
        "ledger_id": f"tecnoempleo:{ident}", "id": ident, "url": a.url,
        "title": text(d.get("title")),
        "employer": org.get("name") if isinstance(org, dict) else None,
        # the site's `identifier.value` is the EMPLOYER's id (its logo file's number), not the offer's — kept apart
        "employer_id": str(idv.get("value")) if isinstance(idv, dict) and idv.get("value") is not None else None,
        "employment_type": ", ".join(et) if isinstance(et, list) else et,
        "city": (text(addr.get("addressLocality")) or None) if isinstance(addr, dict) else None,
        "region": (text(addr.get("addressRegion")) or None) if isinstance(addr, dict) else None,
        "posted": d.get("datePosted"), "valid_through": d.get("validThrough"),
        "direct_apply": d.get("directApply"),
        "description": text(d.get("description"))[:20000], "language": "es",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Tecnoempleo — Spain's IT board, through its sitemap and the JSON-LD its offers carry; the listing's stated count as the check.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="distinct offer ids — 1 request (2.9 MB), 2 with the listing's count")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one offer, from its JSON-LD")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
