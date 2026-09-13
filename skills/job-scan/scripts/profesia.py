#!/usr/bin/env python3
"""Profesia — Alma Career's Slovak board (and its Czech front on the same stack), enumerated by one 7 MB sitemap sorted by URL form; the listing's own `count` as the witness.

  profesia.py list [--host www.profesia.sk|www.profesia.cz] [--limit N] [--no-site-total]
  profesia.py ad --url <advertisement URL>

ONE SITEMAP, TWO URL FORMS — AND ONLY ONE IS AN ADVERTISEMENT

`/sitemap.php` is generated on the fly (7 264 199 B on `.sk`, 645 638 B on
`.cz`, 2026-09-13 17:09 UTC) and mixes two things: **advertisements**, of
the form `/praca/<employer-slug>/O<id>` (`/prace/…` on `.cz`), and
**facets** — `/praca/bratislava/`, `/praca/nitriansky-kraj/`, `/praca/
inzinier-kvality/` — with nothing but the URL's shape to tell them apart.
On 2026-09-13: 20 409 `<loc>` on `.sk`, **14 751** advertisements; 1 844
on `.cz`, **1 094**. The adapter keeps the `O<id>` form only, dedups on
the id, and prints the facets it set aside. *The employer is in the URL —
rare and precious — and the id space is shared by the two hosts (5.3 M).*

THE WITNESS is the listing page's own search payload: `/praca/` (or
`/prace/`) embeds `"count":14773 … "scenario":"standard"` — the board's
count of live advertisements at that moment (1 095 on `.cz`). The visible
«Vybraným kritériám vyhovuje 10000 pracovných ponúk» is a capped popup,
not the count, and it is never read. The adapter prints «n emitted, site
states N — equal / k short» and never corrects one by the other.

THE ADVERTISEMENT PAGE has no JSON-LD. It carries microdata in one of two
layouts (the board's own, and the one used for advertisements «prevzatá
z inej stránky», taken over from another site): `itemprop="datePosted"`
(ISO) on both; `<h1>` as the title; «ID: N»; «lokalita: <a>PLACE</a>»;
«Spoločnosť: <a href="…/C<employerId>">NAME</a>» (the EMPLOYER's id, kept
apart from the advertisement's); `salary-range` for «Mzdové podmienky
(brutto)» when published; «Druh pracovného pomeru», «Termín nástupu» read
by their label. `.cz` labels are read in both languages, since the Czech
front serves Slovak-written advertisements too (a Malý Cetín position on
`.cz`, 2026-09-13): `country` is the HOST's (SK / CZ) and `place` is the
text, which names the country when it is not the host's. No `mailto:`,
no `tel:` — nothing of the kind is read.

THE RULES: 2 204 B on `.sk` / 2 201 B on `.cz`, the same file to a few
lines — `*` refused 44 paths (facets by language, forms, CV routes,
`search_offers*form=`), no AI agent named, `sweep: True`, `certain: True`,
no `Crawl-delay` (1 s is ours); `Sitemap: /sitemap.php`. Measured
2026-09-13 17:09 UTC (#343; page Slovaquie of 2026-09-01: 14 040).
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
from _sitemap import count as sitemap_count, count_says, locs as sitemap_locs
from _ua import UA

HOSTS = {"www.profesia.sk": ("SK", "praca", "profesia"), "www.profesia.cz": ("CZ", "prace", "profesia-cz")}
AD_RE = re.compile(r"^https://(www\.profesia\.(?:sk|cz))/(praca|prace)/([a-z0-9-]+)/O(\d+)/?$")
COUNT_RE = re.compile(r'"count":(\d+),"criteria":\{"sort":"[a-z._]+"\},"scenario":"standard"')
EMPLOYER_RE = re.compile(r"(?:Spoločnosť|Společnost):\s*</strong>\s*<a href=\"([^\"]*?C(\d+))\">(.*?)</a>", re.S)
PLACE_RE = re.compile(r"lokalita:\s*</strong>\s*<a[^>]*>(.*?)</a>", re.S)
LABELS = {"type": ("Druh pracovného pomeru", "Druh pracovního poměru"), "start": ("Termín nástupu",),
          "salary": ("Mzdové podmienky (brutto)", "Mzdové podmínky (brutto)", "Mzdové podmienky", "Mzdové podmínky"),
          "desc": ("Informácie o pracovnom mieste", "Informace o pracovním místě")}
STOP = ("Základná zložka mzdy", "Spodní hranice mzdy", "Reagovať na ponuku", "Reagovat na nabídku", "Odporučiť ponuku", "Doporučit nabídku")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[profesia] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACES = {}


def get(url):
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    _PACES.setdefault(host, Pace(host, own=1.0)).wait()   # no Crawl-delay declared; 1 s is ours
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.5", "Accept-Language": "sk,cs;q=0.8,en;q=0.5"})
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


def host_of(a):
    if a.host not in HOSTS:
        die(f"--host must be one of {', '.join(HOSTS)}")
    return a.host, HOSTS[a.host]


def entry(url, lastmod, host):
    m = AD_RE.match(url)
    if not m or m.group(1) != host:
        return None
    country, _, source = HOSTS[host]
    return {"source": source, "country": country, "ledger_id": f"profesia:{m.group(4)}", "id": m.group(4), "url": url,
            "employer_slug": m.group(3), "lastmod": lastmod}


def cmd_list(a):
    host, (country, path, source) = host_of(a)
    smap = f"https://{host}/sitemap.php"
    code, body = get(smap)
    if code == 404:
        die(f"{smap}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{smap}: HTTP {code}", EXIT_PARTIAL)
    c = sitemap_count(body)
    if c["locs"] != c["urls"]:
        die(f"{smap}: {c['locs']} <loc> against {c['urls']} <url> — the file does not agree with itself, and no count is printed.", EXIT_PARTIAL)
    rows, seen, facets = [], set(), 0
    for block in re.findall(r"<url>(.*?)</url>", body, re.S):
        m = re.search(r"<loc>\s*(.*?)\s*</loc>", block, re.S)
        if not m:
            continue
        lm = re.search(r"<lastmod>\s*(.*?)\s*</lastmod>", block, re.S)
        e = entry(htmlmod.unescape(m.group(1)), lm.group(1) if lm else None, host)
        if not e:
            facets += 1   # `/praca/<place>/`, `/praca/<position>/` — the same file, the same tag, another shape
            continue
        if e["id"] in seen:
            continue
        seen.add(e["id"])
        rows.append(e)
    if not rows:
        die(f"{smap}: {c['locs']} <loc>, none of the shape /{path}/<employer>/O<id> — {count_says(body)}", EXIT_PARTIAL)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{host}: {c['locs']} <loc>, {c['urls']} <url>; **{th(len(rows))} distinct advertisement id(s)** of the shape /{path}/<employer>/O<id>, "
         f"{th(facets)} facet URL(s) set aside by their shape" + (f" ({a.limit} printed under --limit)" if a.limit and len(rows) > a.limit else "") + ".")
    if a.no_site_total:
        return
    code, body = get(f"https://{host}/{path}/")
    m = COUNT_RE.search(body) if code == 200 else None
    if not m:
        note(f"the listing /{path}/ answers HTTP {code} and states no `count` this run — no stated figure to print beside the {th(len(rows))}.")
        return
    stated = int(m.group(1))
    if stated == len(rows):
        note(f"{th(len(rows))} emitted, site states {th(stated)} — equal.")
    else:
        note(f"{th(len(rows))} emitted, site states {th(stated)} — {th(abs(stated - len(rows)))} " + ("short" if stated > len(rows) else "more emitted than the site states")
             + "; the sitemap and the listing's own count are two witnesses, and neither corrects the other.")


def after(t, labels, stop):
    """The text after the first label found, up to the next stop word — the page's two layouts share the labels, not the markup."""
    for lab in labels:
        i = t.find(lab)
        if i >= 0:
            seg = t[i + len(lab):]
            cut = min([seg.find(s) for s in stop if seg.find(s) >= 0] or [len(seg)])
            return seg[:cut].strip(" :") or None
    return None


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected https://www.profesia.sk/praca/<employer>/O<id> (or .cz/prace/)")
    host, ident = m.group(1), m.group(4)
    country, _, source = HOSTS[host]
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    t = text(body)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    if not h1 or "ID: " not in t:
        die(f"{a.url}: HTTP 200 but no <h1> and no «ID:» — not an advertisement page as this adapter knows it ({len(body)} B).", EXIT_PARTIAL)
    emp = EMPLOYER_RE.search(body)
    pl = PLACE_RE.search(body)
    dp = re.search(r'itemprop=["\']datePosted["\'][^>]*>\s*([\d-]+)\s*<', body)
    sal = re.search(r'class="salary-range[^"]*">(.*?)</span>', body, re.S)
    et = re.search(r'itemprop=["\']employmentType["\'][^>]*>(.*?)<', body, re.S)
    other_labels = LABELS["start"] + LABELS["salary"] + LABELS["desc"] + ("Miesto práce", "Místo práce")
    print(json.dumps({
        "source": source, "country": country, "ledger_id": f"profesia:{ident}", "id": ident, "url": a.url,
        "title": text(h1.group(1)),
        "employer": text(emp.group(3)) if emp else None,
        # the C<id> of the employer's page, kept apart from the advertisement's O<id>
        "employer_id": emp.group(2) if emp else None,
        "place": text(pl.group(1)) if pl else None,
        "employment_type": text(et.group(1)) if et else after(t, LABELS["type"], other_labels + STOP),
        "start": after(t, LABELS["start"], LABELS["salary"] + LABELS["desc"] + LABELS["type"] + ("Miesto práce", "Místo práce") + STOP),
        "salary": text(sal.group(1)) if sal else None,
        "posted": dp.group(1) if dp else None,
        "description": (after(t, LABELS["desc"], STOP) or "")[:20000] or None,
        "language": "sk" if country == "SK" else "cs",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Profesia (.sk, and .cz on the same stack) — one generated sitemap sorted by URL shape, the listing's own count as the witness; microdata and labels on the advertisement.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every advertisement in /sitemap.php — 14 751 on .sk, 1 094 on .cz on 2026-09-13; one 7 MB request, then the listing for its count")
    s.add_argument("--host", default="www.profesia.sk", choices=sorted(HOSTS))
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advertisement, from its page's microdata and labels")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
