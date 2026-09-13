#!/usr/bin/env python3
"""Služby zamestnanosti — the Slovak public employment service's board (the ÚPSVaR's «Voľné pracovné miesta» sends here), read by the JSON search its own page calls; the state's own store by default, the republished private boards on request.

  sluzbyzamestnanosti.py list [--source VPM|all] [--pages N] [--limit N] [--no-site-total]
  sluzbyzamestnanosti.py ad --url https://www.sluzbyzamestnanosti.gov.sk/pracovne-ponuky/<uuid>

THE ÚPSVaR IS NOT THE BOARD — IT POINTS HERE

`www.upsvr.gov.sk` (24 B of rules: `Disallow:` empty, everything allowed)
publishes the office's own vacancies and a link «Vyhľadávanie pracovných
ponúk - Služby zamestnanosti (gov.sk)»: the public board lives on
**`www.sluzbyzamestnanosti.gov.sk`** (52 B of rules: one refusal,
`/pracovne-ponuky/*/reagovat` — the apply action; no agent named; no
sitemap: `/sitemap.xml` answers a Keycloak login page). The rules of
BOTH hosts are read; nothing under `/reagovat` is ever requested.

ONE JSON SEARCH, TWO STORES, AND THE SITE'S OWN COUNT IN THE ANSWER

`/pracovne-ponuky` is server-rendered (12 cards) and its script calls
**`GET /search/ponuky?pageNr=N&pageSize=…[&zdrojPonuky=VPM]`**, which
answers JSON: `countVPM`, `countZamestnavatelia`, `countPocetVolnychMiest`,
`pageNr`, `pageSize`, and `pracovnePonuky[]` — `uuid`,
`nazovPracovnehoMiesta`, `zamestnavatelObchodneMeno`, `miestoVykonuPrace`,
`zakladnaMzda` + `zakladnaMzdaZaObdobie`, `naposledyZmenene`,
`priznakZdroj` (1 = úrad PSVR, 2 = Portál SZ, 3 = an external portal),
`externyPortal`, `urlExternyPortal`. `pageSize=100` is honoured. On
2026-09-13 18:2x UTC the board states **25 563** advertisements from
8 955 employers for 150 248 positions — of which **12 126 are the state's
own** (`zdrojPonuky=VPM`: entered at an office or on the portal) and the
rest are **republished from profesia.sk, kariera.sk, worki.sk, eures.sk
and the Fajn group**, each card linking out to the portal that holds it.
**The adapter reads the state's store by default** — the inventory nobody
else republishes; `--source all` adds the republished ones, which this
repository already reads at their source (`profesia.py`, …). The witness
is the answer's own `countVPM` for the store asked: «12 126 emitted, site
states 12 126 — equal», printed and never merged; a bounded walk
(`--pages`) is a lower bound and is not compared.

THE ADVERTISEMENT PAGE `/pracovne-ponuky/<uuid>` (the state's own only; an
external one has no page here) is a server-rendered `<dl>`: «Názov
pracovnej pozície», «Profesia (SK ISCO-08)», «Pracovná oblasť», «Počet
voľných miest», «Náplň práce», «Miesto výkonu práce», «Pracovný a
mimopracovný pomer», «Zmennosť», «Základná zložka mzdy v eurách (v
hrubom)», «Dátum nástupu», «Požadovaný stupeň vzdelania», «Cudzí jazyk»;
the employer's «Názov spoločnosti», «IČO», «Internetová adresa», «Počet
zamestnancov». **The page ends with a «Kontaktná osoba» section — a name,
a phone — that is never read.** No JSON-LD. Measured 2026-09-13 18:13–18:2x
UTC (#342; page Slovaquie of 2026-09-01 named the ÚPSVaR and no board).
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

HOST = "www.sluzbyzamestnanosti.gov.sk"
BASE = "https://" + HOST
SEARCH = BASE + "/search/ponuky"
LISTING = BASE + "/pracovne-ponuky"
AD_RE = re.compile(r"^https://www\.sluzbyzamestnanosti\.gov\.sk/pracovne-ponuky/([0-9a-f-]{36})/?(?:\?.*)?$")
PAGE_SIZE = 100
SOURCE_TAG = {1: "úrad PSVR", 2: "Portál SZ", 3: "external"}
FIELDS = {"Názov pracovnej pozície": "title", "Profesia (SK ISCO-08)": "occupation", "Pracovná oblasť": "field", "Počet voľných miest": "positions",
          "Náplň práce": "description", "Pracovný a mimopracovný pomer": "employment_type", "Zmennosť": "shifts",
          "Základná zložka mzdy v eurách (v hrubom)": "salary", "Dátum nástupu na voľné pracovné miesto": "start",
          "Požadovaný stupeň vzdelania": "education", "Cudzí jazyk": "languages", "Dátum a čas vytvorenia": "created", "Naposledy aktualizované": "updated",
          "Id VPM": "vpm_id", "Zdroj": "source_label", "Názov spoločnosti": "employer", "IČO": "employer_ico", "Internetová adresa": "employer_site", "Počet zamestnancov": "employer_size"}
PLACE_LABEL = "Miesto výkonu práce"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[sluzbyzamestnanosti] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=1.0)   # no Crawl-delay declared; 1 s between the 122 pages of the state's store is ours


def get(url, accept="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.5"):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": accept, "Accept-Language": "sk,en;q=0.5"})
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
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", htmlmod.unescape(markup)).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def row(p):
    ext = p.get("priznakZdroj") == 3
    sal = p.get("zakladnaMzda")
    return {"source": "sluzbyzamestnanosti", "country": "SK", "ledger_id": f"sz:{p.get('uuid')}", "id": p.get("uuid"),
            "url": p.get("urlExternyPortal") if ext else f"{LISTING}/{p.get('uuid')}",
            "store": "external" if ext else "own", "entered_via": SOURCE_TAG.get(p.get("priznakZdroj"), str(p.get("priznakZdroj"))),
            "external_portal": p.get("externyPortal") if ext else None,
            "title": p.get("nazovPracovnehoMiesta"), "employer": p.get("zamestnavatelObchodneMeno"), "place": p.get("miestoVykonuPrace"),
            "salary": (f"{sal:g} € / {p.get('zakladnaMzdaZaObdobie', '').lower()}" if isinstance(sal, (int, float)) and sal else None),
            "updated": p.get("naposledyZmenene")}


def cmd_list(a):
    rows, seen, page, stated, stated_extra = [], set(), 1, None, None
    while True:
        q = {"pageNr": page, "pageSize": PAGE_SIZE}
        if a.source == "VPM":
            q["zdrojPonuky"] = "VPM"
        url = SEARCH + "?" + urllib.parse.urlencode(q)
        code, body = get(url, accept="application/json,*/*;q=0.5")
        if code != 200:
            die(f"{url}: HTTP {code} — page {page}: the count below would be short and is not printed.", EXIT_PARTIAL)
        try:
            d = json.loads(body)
        except ValueError:
            die(f"{url}: HTTP 200 but not JSON ({len(body)} B) — a readable body is not an answer.", EXIT_PARTIAL)
        items = d.get("pracovnePonuky")
        if not isinstance(items, list):
            die(f"{url}: no `pracovnePonuky` list in the answer — keys {sorted(d)[:8]}.", EXIT_PARTIAL)
        if stated is None:
            stated = d.get("countVPM")
            stated_extra = (d.get("countZamestnavatelia"), d.get("countPocetVolnychMiest"))
        new = 0
        for p in items:
            r = row(p)
            if not r["id"] or r["id"] in seen:
                continue
            seen.add(r["id"])
            rows.append(r)
            new += 1
        size = d.get("pageSize") or PAGE_SIZE
        last = -(-int(stated or 0) // size) if stated else page
        if not items or new == 0 or page >= last or (a.pages and page >= a.pages) or (a.limit and len(rows) >= a.limit):
            break
        page += 1
    if not rows:
        die(f"{SEARCH}: 0 advertisement(s) in the answer while it states {stated} — the reader is broken, or the store is empty; either way no count is printed.", EXIT_PARTIAL)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    own = sum(1 for r in rows if r["store"] == "own")
    bounded = (a.pages and page < last) or (a.limit and len(rows) >= a.limit and page < last)
    which = "the state's own store, zdrojPonuky=VPM" if a.source == "VPM" else "all sources"
    note(f"{page} page(s) of {size} read ({which}); **{th(len(rows))} distinct advertisement(s)** — "
         f"{th(own)} the state's own, {th(len(rows) - own)} republished from external portals"
         + (f" ({a.limit} printed under --limit)" if a.limit and len(rows) > a.limit else "")
         + (f" — the walk stopped at page {page} of {last}, so the count is a lower bound" if bounded else "") + ".")
    if a.no_site_total or stated is None:
        return
    extra = f" (site also states {th(stated_extra[0] or 0)} employers and {th(stated_extra[1] or 0)} positions — positions, not advertisements, never compared)"
    if bounded:
        note(f"site states {th(stated)}{extra}; {th(len(rows))} emitted from a bounded walk, not compared.")
    elif stated == len(rows):
        note(f"{th(len(rows))} emitted, site states {th(stated)} — equal{extra}.")
    else:
        note(f"{th(len(rows))} emitted, site states {th(stated)} — {th(abs(stated - len(rows)))} " + ("short" if stated > len(rows) else "more emitted than the site states")
             + f"; the walk and the answer's own count are two witnesses, and neither corrects the other{extra}.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not a state advertisement address — expected {LISTING}/<uuid> (a republished one lives on its portal, with no page here)")
    ident = m.group(1)
    code, body = get(f"{LISTING}/{ident}")
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    # the «Kontaktná osoba» section closes the page: nothing at or after it is read
    cut = body.find("Kontaktná osoba")
    head = body[:cut] if cut > 0 else body
    fields, place = {}, None
    for dt, dd in re.findall(r"<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>", head, re.S):
        lab, val = text(dt), text(dd)
        if lab.startswith(PLACE_LABEL) and place is None:
            place = re.sub(r"\s*location_on.*$", "", val).strip(" ,") or None
        key = FIELDS.get(lab)
        if key and key not in fields:
            fields[key] = val or None
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", head, re.S)
    if not h1 or not fields:
        die(f"{a.url}: HTTP 200 but no <h1> or no <dl> fields — not an advertisement page as this adapter knows it ({len(body)} B).", EXIT_PARTIAL)
    out = {"source": "sluzbyzamestnanosti", "country": "SK", "ledger_id": f"sz:{ident}", "id": ident, "url": f"{LISTING}/{ident}", "store": "own",
           "title": fields.get("title") or text(h1.group(1)), "place": place}
    for k in ("employer", "employer_ico", "employer_site", "employer_size", "occupation", "field", "positions", "employment_type", "shifts", "salary", "start", "education", "languages", "created", "updated", "vpm_id", "source_label"):
        out[k] = fields.get(k)
    out["description"] = (fields.get("description") or "")[:20000] or None
    out["language"] = "sk"
    print(json.dumps(out, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Služby zamestnanosti (Slovakia's public employment service) — the JSON search its page calls, the state's own store by default, the answer's own count as the witness; the <dl> of the advertisement page, the contact person never read.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every advertisement of the state's store (12 126 on 2026-09-13, 122 pages of 100 at 1 s) — or of all sources with --source all (25 563)")
    s.add_argument("--source", default="VPM", choices=["VPM", "all"])
    s.add_argument("--pages", type=int)
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one of the state's advertisements, from its page's <dl> — never the contact person")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
