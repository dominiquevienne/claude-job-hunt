#!/usr/bin/env python3
"""easy-prace.cz — a Czech board that publishes two stores in two sitemaps, its own and the public employment service's republication, and says which is which; the listing's own «N výsledků» as the witness.

  easyprace.py list [--store easy|up|both] [--limit N] [--no-site-total]
  easyprace.py ad --url <advertisement URL>

TWO STORES, NAMED BY THE SITEMAP THAT HOLDS THEM

`robots.txt` is 90 B — `Allow: /` and one Sitemap line — and the index
`/data/sitemap/easyprace-index.xml` names four files, two of them
advertisements: **`easyprace-aktivni-easy.xml`**, the board's own
advertisements under `/nabidka/<slug>/<id>` (10 121 on 2026-09-13 17:28
UTC), and **`easyprace-aktivni-up.xml`**, the advertisements of the Úřad
práce ČR — the public employment service — republished under
`/volne-misto/<slug>/<id>` (24 546). The two id spaces are separate (two
numbers collide across them), so the ledger key carries the store:
`easyprace:easy:<id>` / `easyprace:up:<id>`. The adapter reads both by
default and prints them apart; `--store` picks one. *The other two files
(`vyhledavani`, `clanky`) are search facets and articles, never read.*

THE WITNESS is the listing `/nabidka-zamestnani`, which states «34 578
výsledků» and pages to `/strana/865` (40 a page). On 2026-09-13: 34 667
`<loc>` over the two files, 34 667 rows keyed by store — «34 667 emitted,
site states 34 575 — 92 more emitted than the site states» at 17:31 UTC
(the listing said 34 578 three minutes earlier), printed and never
merged: a sitemap regenerated on its own clock against a listing counted
on another.

THE ADVERTISEMENT PAGE has no JSON-LD. It is one template for both
stores: the `<h1>` title, the employer in `NabidkaDetail-company`, the
salary in `NabidkaDetail-salary` («33 000 - 44 000 Kč») when published,
label/value pairs `NabidkaDetail-infoLabel` / `-infoValue` («Lokalita»,
«Úvazek», «Vzdělání», «Směnnost», «Pracovní období», «Vhodné pro»,
«Ubytování»), content rows with an `<h2>` each — «Popis pracovní nabídky», «Požadujeme»,
«Nabízíme», «Jiná sdělení» on the board's own advertisements, joined as the
description; «Směnnost», «Pracovní období» on the Úřad práce records, which
carry no description — and an
«Aktualizováno před pár hodinami» that is relative, so the date is the
sitemap's `lastmod`. **The page names a contact person («Kontaktní osoba»,
a name) — it is never read.** No `mailto:`, no `tel:`.

THE RULES: `Allow: /`, no agent named, no `Crawl-delay` (1 s is ours),
`certain: True`. Measured 2026-09-13 17:28 UTC (#352; page Tchéquie of
2026-09-01: 9 862 + 23 620 = 33 482).
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
from _sitemap import count as sitemap_count, count_says
from _ua import UA

HOST = "www.easy-prace.cz"
BASE = "https://" + HOST
LISTING = BASE + "/nabidka-zamestnani"
STORES = {"easy": (BASE + "/data/sitemap/easyprace-aktivni-easy.xml", "nabidka", "the board's own"),
          "up": (BASE + "/data/sitemap/easyprace-aktivni-up.xml", "volne-misto", "Úřad práce ČR, republished")}
AD_RE = re.compile(r"^https://www\.easy-prace\.cz/(nabidka|volne-misto)/([^/]*)/(\d+)/?$")
STATED_RE = re.compile(r"(\d[\d\s\xa0.]{2,9})\s*výsledků")
LABEL_RE = re.compile(r'<p class="NabidkaDetail-infoLabel">(.*?)</p>\s*<div class="NabidkaDetail-infoValue">(.*?)</div>\s*</div>', re.S)
ROW_RE = re.compile(r'<div class="NabidkaDetail-contentRow"[^>]*>(.*?)(?=<div class="NabidkaDetail-contentRow"|<div class="NabidkaDetail-contactPerson")', re.S)
FIELDS = {"Lokalita": "place", "Úvazek": "employment_type", "Vzdělání": "education", "Směnnost": "shifts", "Pracovní období": "period", "Vhodné pro": "suitable_for", "Ubytování": "housing"}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[easyprace] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=1.0)   # no Crawl-delay declared; 1 s is ours


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.5", "Accept-Language": "cs,en;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
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
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", htmlmod.unescape(markup)).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def entry(url, lastmod, store):
    m = AD_RE.match(url)
    if not m or m.group(1) != STORES[store][1]:
        return None
    return {"source": "easyprace", "country": "CZ", "store": store, "ledger_id": f"easyprace:{store}:{m.group(3)}", "id": m.group(3), "url": url,
            "slug": m.group(2), "lastmod": lastmod}


def cmd_list(a):
    stores = ["easy", "up"] if a.store == "both" else [a.store]
    rows, per_store, locs_total = [], {}, 0
    for st in stores:
        smap, path, label = STORES[st]
        code, body = get(smap)
        if code == 404:
            die(f"{smap}: HTTP 404", EXIT_GONE)
        if code != 200:
            die(f"{smap}: HTTP {code} — the {label} store unread: the count below would be short and is not printed.", EXIT_PARTIAL)
        c = sitemap_count(body)
        if c["locs"] != c["urls"]:
            die(f"{smap}: {c['locs']} <loc> against {c['urls']} <url> — the file does not agree with itself, and no count is printed.", EXIT_PARTIAL)
        locs_total += c["locs"]
        seen, n, other = set(), 0, 0
        for block in re.findall(r"<url>(.*?)</url>", body, re.S):
            m = re.search(r"<loc>\s*(.*?)\s*</loc>", block, re.S)
            if not m:
                continue
            lm = re.search(r"<lastmod>\s*(.*?)\s*</lastmod>", block, re.S)
            e = entry(htmlmod.unescape(m.group(1)), lm.group(1) if lm else None, st)
            if not e:
                other += 1   # a URL of the other store's shape, or none — this file is named for one store
                continue
            if e["id"] in seen:
                continue
            seen.add(e["id"])
            rows.append(e)
            n += 1
        per_store[st] = (n, other, c["locs"])
        if not n:
            die(f"{smap}: {c['locs']} <loc>, none of the shape /{path}/<slug>/<id> — {count_says(body)}", EXIT_PARTIAL)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    parts = "; ".join(f"{st} ({STORES[st][2]}): {th(n)} distinct id(s) of {th(l)} <loc>" + (f", {other} of another shape set aside" if other else "") for st, (n, other, l) in per_store.items())
    note(f"{th(locs_total)} <loc> over {len(stores)} store file(s); **{th(len(rows))} row(s)** keyed by store — {parts}" + (f" ({a.limit} printed under --limit)" if a.limit and len(rows) > a.limit else "") + ".")
    if a.no_site_total:
        return
    if a.store != "both":
        note(f"site total not compared: one store read (--store {a.store}), and the listing counts both.")
        return
    code, body = get(LISTING)
    m = STATED_RE.search(text(body)) if code == 200 else None
    if not m:
        note(f"the listing {LISTING} answers HTTP {code} and states no «N výsledků» this run — no stated figure to print beside the {th(len(rows))}.")
        return
    stated = int(re.sub(r"\D", "", m.group(1)))
    if stated == len(rows):
        note(f"{th(len(rows))} emitted, site states {th(stated)} — equal.")
    else:
        note(f"{th(len(rows))} emitted, site states {th(stated)} — {th(abs(stated - len(rows)))} " + ("short" if stated > len(rows) else "more emitted than the site states")
             + "; the two sitemaps and the listing's own count are two witnesses, and neither corrects the other.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected {BASE}/nabidka/<slug>/<id> or /volne-misto/<slug>/<id>")
    store = "easy" if m.group(1) == "nabidka" else "up"
    ident = m.group(3)
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    if not h1 or "NabidkaDetail-infoLabel" not in body:
        die(f"{a.url}: HTTP 200 but no <h1> and no NabidkaDetail labels — not an advertisement page as this adapter knows it ({len(body)} B).", EXIT_PARTIAL)
    fields = {}
    for lab, val in LABEL_RE.findall(body):
        key = FIELDS.get(text(lab))
        if key:
            fields[key] = text(val) or None
    emp = re.search(r'class="NabidkaDetail-company(?:Link|Name)?"[^>]*>(.*?)</(?:a|span|div|p)>', body, re.S)
    sal = re.search(r'class="NabidkaDetail-salary"[^>]*>(.*?)</div>', body, re.S)
    # the content rows: an <h2> label each — «Směnnost», «Pracovní období» are fields on the Úřad práce records;
    # «Popis pracovní nabídky», «Požadujeme», «Nabízíme», «Jiná sdělení» are the description on the board's own
    sections = []
    for row in ROW_RE.findall(body):
        h = re.search(r"<h2[^>]*>(.*?)</h2>", row, re.S)
        label = text(h.group(1)) if h else ""
        value = text(re.sub(r"<h2[^>]*>.*?</h2>", " ", row, count=1, flags=re.S))
        if FIELDS.get(label):
            fields[FIELDS[label]] = value or None
        elif value:
            sections.append(f"{label}: {value}" if label else value)
    # `NabidkaDetail-contactPerson` names a person — never read; the site's apply form is not a field
    print(json.dumps({
        "source": "easyprace", "country": "CZ", "store": store, "ledger_id": f"easyprace:{store}:{ident}", "id": ident, "url": a.url,
        "title": text(h1.group(1)),
        "employer": text(emp.group(1)) or None if emp else None,
        "salary": text(sal.group(1)) or None if sal else None,
        **{k: fields.get(k) for k in ("place", "employment_type", "education", "shifts", "period", "suitable_for", "housing")},
        "description": "\n".join(sections)[:20000] or None,
        "language": "cs",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="easy-prace.cz — two stores in two sitemaps (the board's own, the Úřad práce republication), keyed apart; the listing's own «N výsledků» as the witness.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every advertisement of one or both stores — 10 121 + 24 546 on 2026-09-13, two 2–4 MB requests, then the listing for its count")
    s.add_argument("--store", default="both", choices=["easy", "up", "both"])
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advertisement, from its page's labels — never the contact person")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
