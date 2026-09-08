#!/usr/bin/env python3
"""Jobartis (`www.jobartis.com`) — Angola's largest archive and smallest flow.

  jobartis.py list [--since 2026-08-01] [--form bare] [--limit 20]
  jobartis.py ad --slug emprego-abreu-cabondela-lameira-adao-agricultura
  jobartis.py ad --slug adding-talent-contabilista

**40 882 advertisements in one gzipped sitemap**, and 216 of them published
since 1 August 2026. `angoemprego` holds 1 434 and published 924 in the same
window: *this board is an archive, and the two other Angolan cards already
say so.* What this adapter adds is that the archive is bigger than the
repository recorded, and why.

TWO URL FORMS, AND ONLY ONE OF THEM HAD EVER BEEN COUNTED

    /emprego-<slug>    38 588   2 528 distinct dates   2018-01-15 .. 2026-09-06
    /<slug>             2 294      60 distinct dates   2018-01-17 .. 2026-07-30
    neither               212   the home page, sign-up, help, search
                       ------
                       41 094   = every <loc> in the file

**`angoemprego.md` and `angolaemprego.md` both record 38 547 for this board.**
That is the `/emprego-` form alone — my count of the same form today is 38 588,
which is 41 more after two days. **The 2 294 bare-slug advertisements are in
neither figure**, and they are advertisements: `/anonimo-caixeiro-de-pecas`
serves a vacancy, closed, *«&nbsp;Oferta aberta até 30/09/2014&nbsp;»*.

**They are not the same advertisements under a second URL.** 113 slugs appear
in both forms, and the pair that was fetched — `adding-talent-contabilista`
under each — is **two different vacancies from the same employer**: reference
`Con_2015` closing 22/01/2015 against one closing 04/09/2014. *Same employer,
same job title, different years.* So the two forms are distinct URL spaces and
the counts add.

*A pattern that matched one form returned 94 % of the board and looked
complete — a narrow extractor does not return less, it returns false.*

THE ARCHIVE IS ONE IMPORT AND A TRICKLE

    /emprego-  busiest day  2018-01-26   7 138   18.5 %
    /<slug>    busiest day  2018-01-24     956   41.7 %

**A high count of distinct dates does not protect against a single import**:
2 528 distinct dates, and one January day carries a fifth of the file. The
bare-slug corpus is worse and also frozen — its most recent entry is
2026-07-30, so it takes no new advertisements at all.

**`--since` is therefore the flag that makes this board usable**, and it costs
one request: `lastmod` is present on 40 882 of 40 882.

ONE SECOND BETWEEN REQUESTS IS TOO FAST FOR THIS HOST

Seven requests at roughly one second apart drew **alternating 503s** — the
same URL that failed succeeded twenty seconds later, and a different URL
failed in its place. *That is a rate, not a property of any URL.* This module
paces itself at five seconds and `list` needs exactly one request.

**A zero, or a refusal, produced by our own request rate is ours and not the
site's** — which is why the pace is here and not in a comment.

WHAT AN ADVERTISEMENT PAGE CARRIES

`data-job-id="59272"` is the board's own identifier, and it is the ledger key.
There is no `ld+json` and no `JobPosting` anywhere: the fields are `data-label`
pairs, in Portuguese — contract type, closing date, role, industry, number of
posts, minimum education, years of experience, nationality, languages,
functional area.

**The state is read from two markers and never inferred from one.** An open
advertisement carries *«&nbsp;Enviar candidatura&nbsp;»*; a closed one carries
*«&nbsp;Vaga fechada&nbsp;»*. A page with neither reports `None` rather than
being called open by default.

Verified against the live site on 2026-09-07.
"""

import argparse
import gzip
import html as html_mod
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BASE = "https://www.jobartis.com"
SITEMAP = BASE + "/sitemap.xml.gz"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)
JOBID = re.compile(r'data-job-id="(\d+)"')
FIELD = re.compile(r'<div class="data-label[^"]*">\s*([^<]{2,40}?)\s*</div>\s*'
                   r'<div class="[^"]*">\s*(.*?)\s*</div>', re.S)

# **Single-segment paths that are not advertisements.** Everything else with no
# slash is one — checked by fetching two of them, not assumed from the shape.
NOT_AN_AD = {"", "ajuda", "search-job-offers", "vagas-emprego", "sitemap",
             "aviso-legal", "politica-de-privacidade", "contacto"}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobartis] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    # An unknown is not a refusal: `not None` is `True` for both.
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# **Five seconds, measured rather than chosen.** At one second this host
# returned alternating 503s from the seventh request on; the URL that failed
# succeeded twenty seconds later. The host declares no `Crawl-delay`, so this
# figure is ours and is declared as ours.
_PACE = Pace("www.jobartis.com", own=5.0)


def get(url, binary=False):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "pt-AO,pt;q=0.9,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            raw = r.read()
            if binary:
                return r.getcode(), raw, r.headers
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return (e.code, b"", e.headers) if binary else (e.code, "")
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def ungzip(raw, headers):
    """**The magic bytes decide, not the file extension.**

    `.gz` in a URL is a name; a host that stops compressing keeps the name and
    starts serving XML. Decompressing on the extension would raise, and
    trusting the extension the other way would hand XML to gzip.

    **The decompressed bytes go through `decode_body`, not through
    `.decode("utf-8")`.** Decompressing recovers bytes, not text, and the
    declaration that says which encoding they are is inside them — a hand-rolled
    UTF-8 decode with `errors="replace"` would turn a Portuguese `ç` into a
    replacement character and report success. The repository's guard caught
    exactly that here.
    """
    was_gz = raw[:2] == b"\x1f\x8b"
    return decode_body(gzip.decompress(raw) if was_gz else raw, headers)[0], was_gz


def clean(s):
    return " ".join(html_mod.unescape(re.sub(r"<[^>]+>", " ", s or "")).split())


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def iso(d):
    """`22/01/2015` -> `2015-01-22`, or `None` — never a guess."""
    m = re.search(r"\b(\d{2})/(\d{2})/(\d{4})\b", d or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def classify(url):
    """`"emprego"`, `"bare"` or `None` — and `None` is the answer for a page
    that is not an advertisement, not an error."""
    if not url.startswith(BASE + "/"):
        return None
    tail = url[len(BASE) + 1:]
    if "/" in tail or tail in NOT_AN_AD:
        return None
    return "emprego" if tail.startswith("emprego-") else "bare"


def entries():
    code, raw, headers = get(SITEMAP, binary=True)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    body, was_gz = ungzip(raw, headers)
    rows, counts = [], {"emprego": 0, "bare": 0, "not-an-ad": 0, "no-date": 0}
    for block in ENTRY.findall(body):
        loc = LOC.search(block)
        if not loc:
            continue
        url = html_mod.unescape(loc.group(1).strip())
        form = classify(url)
        if form is None:
            counts["not-an-ad"] += 1
            continue
        d = LASTMOD.search(block)
        if not d:
            counts["no-date"] += 1
        counts[form] += 1
        rows.append({
            "source": "jobartis",
            "url": url,
            "slug": url[len(BASE) + 1:],
            "form": form,
            "lastmod": d.group(1) if d else None,
            "countries": ["AO"],
        })
    if not rows:
        die(f"{SITEMAP} parsed to zero advertisements from {len(body)} "
            f"characters (gzip={was_gz}) — read the bytes before believing "
            f"the zero.")
    rows.sort(key=lambda r: (r["lastmod"] or ""), reverse=True)
    return rows, counts, was_gz


def cmd_list(a):
    rows, counts, was_gz = entries()
    note(f"{len(rows)} advertisement(s) in one request "
         f"(gzip={was_gz}): {counts['emprego']} under `/emprego-` and "
         f"{counts['bare']} under a bare slug. **Both forms are "
         f"advertisements and they are not each other** — 113 slugs appear "
         f"in both, and the pair that was checked is two different vacancies.")
    note(f"{counts['not-an-ad']} entr(y|ies) are not advertisements; "
         f"{counts['no-date']} advertisement(s) carry no `lastmod`.")
    if a.form:
        rows = [r for r in rows if r["form"] == a.form]
        note(f"{len(rows)} in the `{a.form}` form")
    if a.since:
        rows = [r for r in rows if r["lastmod"] and r["lastmod"] >= a.since]
        note(f"{len(rows)} dated {a.since} or later. **This board is an "
             f"archive**: one 2018 day carries 18.5 % of it, so a count "
             f"without a date says almost nothing about the market.")
    if a.search:
        needle = fold(a.search)
        rows = [r for r in rows if needle in fold(r["slug"])]
    if a.limit:
        rows = rows[: a.limit]
    print(json.dumps({"source": "jobartis", "country": "AO",
                      "sitemap_entries": sum(counts.values()) - counts["no-date"],
                      "advertisements": counts["emprego"] + counts["bare"],
                      "by_form": {"emprego": counts["emprego"],
                                  "bare": counts["bare"]},
                      "not_advertisements": counts["not-an-ad"],
                      "returned": len(rows),
                      "ads": rows}, ensure_ascii=False, indent=1))


def cmd_ad(a):
    slug = a.slug.strip("/")
    url = f"{BASE}/{slug}"
    code, page = get(url)
    if code in (404, 410):
        die(f"{slug} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    ident = JOBID.search(page)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    fields = {}
    for m in FIELD.finditer(page):
        key = fold(clean(m.group(1))).replace(" ", "_")
        fields[key] = clean(m.group(2)) or None
    # **Two markers, and neither is assumed from the absence of the other.**
    closed = "Vaga fechada" in page
    open_ = "Enviar candidatura" in page
    state = "closed" if closed else ("open" if open_ else None)
    print(json.dumps({
        "source": "jobartis", "url": url, "slug": slug,
        "form": classify(url),
        "id": ident.group(1) if ident else None,
        "ledger_id": f"jobartis:{ident.group(1) if ident else slug}",
        "id_source": "data-job-id" if ident else "slug — the page carried no id",
        "title": clean(h1.group(1)) if h1 else None,
        "state": state,
        "state_basis": ("«Vaga fechada»" if closed else
                        ("«Enviar candidatura»" if open_ else
                         "neither marker on the page — not called open")),
        "open_until": iso(fields.get("oferta_aberta_ate")),
        "contract_type": fields.get("tipo_contrato"),
        "role": fields.get("cargo"),
        "industry": fields.get("industria"),
        "posts": fields.get("numero_de_vagas"),
        "education": fields.get("titulacao_minima"),
        "experience": fields.get("experiencia_exigida"),
        "nationality": fields.get("nacionalidade"),
        "languages": fields.get("linguas"),
        "functional_area": fields.get("area_funcional"),
        "countries": ["AO"],
        "structured_data": "none — no ld+json and no JobPosting on this site",
    }, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="every advertisement, from one request")
    # **`%` in an argparse help string is a format specifier.** A bare `18.5 %`
    # raises `badly formed help string` at `add_argument`, so the module dies
    # before it parses anything — a percentage written for a reader takes the
    # whole adapter down. It is doubled here and nowhere else in this file.
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="`lastmod`, present on every advertisement. **Use "
                         "it**: one 2018 day carries 18.5 %% of this file")
    li.add_argument("--form", choices=("emprego", "bare"),
                    help="`/emprego-<slug>` or the bare `/<slug>`; both are "
                         "advertisements and only the first had been counted")
    li.add_argument("--search", help="match the slug; folds accents")
    li.add_argument("--limit", type=int)
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by its path tail")
    ad.add_argument("--slug", required=True,
                    help="the whole tail, `emprego-` included when it is there")
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
