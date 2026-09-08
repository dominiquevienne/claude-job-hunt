#!/usr/bin/env python3
"""Emplois Congo (`www.emploiscongo.com`) — a Jobartis site, and a closed archive.

  emploiscongo.py list [--since 2026-01-01] [--limit 20]
  emploiscongo.py ad --slug emploi-unops-engineer-intern

**446 advertisements, and 7 of 7 sampled are closed — including the three most
recent.** This board is not dormant, it is an archive: the newest posting,
2026-08-19, already carries *«&nbsp;Offre d'emploi fermée&nbsp;»*.

    446 advertisements   92 distinct dates   2019-02-20 → 2026-08-19
    since 2026-01-01      23
    since 2026-07-01       2
    since 2026-08-01       1        <- and it is closed

*Useful for what an employer has recruited for and when. Not useful for
applying, and this module says so rather than returning 446 rows that look
live.*

IT IS THE SAME OPERATOR AS `jobartis`, AND THE RULES FILE PROVES IT

`www.emploiscongo.com/robots.txt` and `www.jobartis.com/robots.txt` are
**identical once the first-party host is normalised** — same eleven
`Disallow`, same `Allow: //info.jobartis.com`, and the Congolese file declares
`https://info.jobartis.com/…` as its second sitemap **by name**. The
advertisement page even carries a `m.jobartis.com` button.

*So `jobartis.py` transposes — which had been recorded on 2026-09-07 as
«&nbsp;probably, to be verified&nbsp;».* **It was worth verifying, because one
half of it is false.**

WHAT TRANSPOSED, AND THE ONE THING THAT DID NOT

    same   /sitemap.xml.gz, gzipped, flat urlset
    same   /<prefix>-<slug> advertisements, one segment
    same   data-job-id on the advertisement page
    same   data-label pairs for the fields
    NOT    the second, bare-slug URL form

**`jobartis` serves 2 294 advertisements under a bare `/<slug>` beside its
38 588 prefixed ones, and counting only the prefix form under-reported it by
6 %.** *Here there are **zero** bare-slug advertisements* — checked, not
assumed. **The template is shared; the defect is not.**

*That is the whole reason the earlier note said «to be verified, not to be
supposed»: a finding carried across on the strength of a shared template
would have had this module hunting a form that does not exist, and reporting
its absence as a change.*

THE SLUG IS NOT CANONICAL, AND THE ID IS

Several strings reach one advertisement. `emploi-unops-engineer-intern` and
`emploi-unops-engineer-intern-121ff0dd-…-7e24d3e245c1` both return **id
58850**, and a genuinely absent slug returns a real 404.

*So a ledger keyed on the URL would file one vacancy under as many identities
as there are ways to spell it.* **`data-job-id` is the key**, and the slug is
only how we got there. *This was found by expecting a truncated slug to be
gone and being wrong: the code was right and the expectation was not.*

THE LABELS ARE FRENCH AND CARRY HTML ENTITIES

`Secteur d&#39;activité`, and the closed marker itself is
`Offre d&#39;emploi fermée`. **Both the key and the value pass through
`html.unescape`** — matching on the raw form would miss every label containing
an apostrophe, which in French is most of the interesting ones.

NO STATE IS EVER REPORTED AS «OPEN», AND THAT IS DELIBERATE

The closed marker is measured. **An open marker has never been seen on this
host**, because no sampled advertisement was open. `jobartis` uses
*«&nbsp;Enviar candidatura&nbsp;»* and the French template would plausibly say
*«&nbsp;Envoyer candidature&nbsp;»* — **plausibly is not measured, and this
module does not guess a string it has never observed.**

So `state` is `"closed"` or `None`, and `state_basis` says which. The deadline
travels separately as `deadline`, unparsed into a state: *inferring «open»
from a future date would manufacture exactly the claim this section refuses.*

Verified against the live site on 2026-09-08.
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

BASE = "https://www.emploiscongo.com"
SITEMAP = BASE + "/sitemap.xml.gz"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(\d{4}-\d{2}-\d{2})", re.S)
JOBID = re.compile(r'data-job-id="(\d+)"')
FIELD = re.compile(r'<div class="data-label[^"]*">\s*([^<]{2,44}?)\s*</div>\s*'
                   r'<div class="[^"]*">\s*(.*?)\s*</div>', re.S)

# **Measured, not translated.** The Portuguese sibling's closed marker is
# `Vaga fechada`; this host's is below, and it carries an entity.
CLOSED = "Offre d'emploi fermée"

# Single-segment paths that are not advertisements.
NOT_AN_AD = {"", "emplois", "search-job-offers", "ajuda", "aide", "sitemap"}

FIELDS = {
    "contract": "type de contrat", "deadline": "delai de candidature",
    "role": "bureau", "industry": "secteur d'activite",
    "posts": "postes a pourvoir", "description": "la description",
    "education": "education minimum", "experience": "experience requise",
    "nationality": "nationalite", "languages": "les langues",
}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[emploiscongo] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# Five seconds, carried over from `jobartis.py` where one second drew
# alternating 503s. **Same operator, so the limit is assumed shared** — and
# that assumption errs towards slower, which is the safe direction.
_PACE = Pace("www.emploiscongo.com", own=5.0)


def get(url, binary=False):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "fr-CD,fr;q=0.9,en;q=0.8",
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
    """Magic bytes decide, not the file extension; and the decompressed bytes
    go through `decode_body` rather than a hand-rolled UTF-8 decode."""
    was_gz = raw[:2] == b"\x1f\x8b"
    return decode_body(gzip.decompress(raw) if was_gz else raw, headers)[0], was_gz


def clean(s):
    return " ".join(html_mod.unescape(re.sub(r"<[^>]+>", " ", s or "")).split())


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def iso(d):
    """`18/08/2026` -> `2026-08-18`, or `None` — never a guess."""
    m = re.search(r"\b(\d{2})/(\d{2})/(\d{4})\b", d or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def classify(url):
    if not url.startswith(BASE + "/"):
        return None
    tail = url[len(BASE) + 1:]
    if "/" in tail or tail in NOT_AN_AD:
        return None
    # **One prefix, and no second form.** `jobartis` has a bare-slug form
    # beside its prefixed one; this host has none, checked on the whole file.
    return "emploi" if tail.startswith("emploi-") else "bare"


def entries():
    code, raw, headers = get(SITEMAP, binary=True)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    body, was_gz = ungzip(raw, headers)
    rows, counts = [], {"emploi": 0, "bare": 0, "not-an-ad": 0}
    for block in ENTRY.findall(body):
        loc = LOC.search(block)
        if not loc:
            continue
        url = html_mod.unescape(loc.group(1).strip())
        form = classify(url)
        if form is None:
            counts["not-an-ad"] += 1
            continue
        counts[form] += 1
        d = LASTMOD.search(block)
        rows.append({"source": "emploiscongo", "url": url,
                     "slug": url[len(BASE) + 1:], "form": form,
                     "lastmod": d.group(1) if d else None,
                     "countries": ["CD"]})
    if not rows:
        die(f"{SITEMAP} parsed to zero advertisements from {len(body)} "
            f"characters (gzip={was_gz}) — read the bytes before believing "
            f"the zero.")
    rows.sort(key=lambda r: (r["lastmod"] or ""), reverse=True)
    return rows, counts, was_gz


def read_ad(url):
    code, page = get(url)
    if code in (404, 410):
        return None, f"gone — HTTP {code}"
    if code != 200:
        return None, f"HTTP {code}"
    text = html_mod.unescape(page)
    ident = JOBID.search(page)
    fields = {}
    for m in FIELD.finditer(page):
        fields[fold(clean(m.group(1)))] = clean(m.group(2)) or None
    closed = CLOSED in text
    out = {
        "id": ident.group(1) if ident else None,
        "ledger_id": f"emploiscongo:{ident.group(1) if ident else url.rsplit('/', 1)[-1]}",
        # **`closed` or `None`, never `open`.** No open marker has been
        # observed on this host; guessing the French of the sibling's string
        # would be inventing a measurement.
        "state": "closed" if closed else None,
        "state_basis": ("«Offre d'emploi fermée» on the page" if closed else
                        "no closed marker, and no open marker is known for "
                        "this host — 7 of 7 sampled on 2026-09-08 were closed"),
        "labels_read": len(fields),
    }
    for name, key in FIELDS.items():
        out[name] = fields.get(key)
    out["deadline"] = iso(out.get("deadline"))
    return out, None


def cmd_list(a):
    rows, counts, was_gz = entries()
    if not rows:
        die(f"{sum(counts.values())} sitemap entr(y|ies) and **0 "
            f"advertisement(s) parsed** ({counts}). The file was read and "
            f"yielded no advertisement — a reading that failed, not an empty "
            f"board. #181", EXIT_PARTIAL)
    note(f"{counts['emploi']} advertisement(s) under `/emploi-` and "
         f"**{counts['bare']} under a bare slug** (gzip={was_gz}); "
         f"{counts['not-an-ad']} entr(y|ies) are not advertisements. "
         f"*`jobartis`, the same operator, has 2 294 bare-slug "
         f"advertisements — this host has none, and that was checked.*")
    newest = max((r["lastmod"] or "") for r in rows)
    note(f"most recent: {newest}. **This board is a closed archive** — 7 of 7 "
         f"sampled were closed, the three most recent included.")
    if a.since:
        rows = [r for r in rows if r["lastmod"] and r["lastmod"] >= a.since]
        note(f"{len(rows)} dated {a.since} or later.")
    if a.search:
        rows = [r for r in rows if fold(a.search) in fold(r["slug"])]
    if a.limit:
        rows = rows[: a.limit]
    if not a.fetch:
        print(json.dumps({"source": "emploiscongo", "country": "CD",
                          "advertisements": counts["emploi"],
                          "bare_slug_advertisements": counts["bare"],
                          "not_advertisements": counts["not-an-ad"],
                          "returned": len(rows), "ads": rows},
                         ensure_ascii=False, indent=1))
        return
    note(f"opening {len(rows)} page(s) at {_PACE.source()}.")
    kept, broken = [], []
    for row in rows:
        rec, why = read_ad(row["url"])
        if rec is None:
            broken.append((row["slug"][:40], why))
            continue
        kept.append(dict(row, **rec))
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{s} ({w})" for s, w in broken[:5]))
    closed = sum(1 for k in kept if k["state"] == "closed")
    note(f"{closed} of {len(kept)} carry the closed marker.")
    print(json.dumps({"source": "emploiscongo", "country": "CD",
                      "advertisements": counts["emploi"], "read": len(rows),
                      "kept": len(kept), "unreadable": len(broken),
                      "closed": closed, "ads": kept},
                     ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}/{a.slug.strip('/')}"
    rec, why = read_ad(url)
    if rec is None:
        die(f"{a.slug}: {why}",
            EXIT_GONE if (why or "").startswith("gone") else EXIT_BROKEN)
    print(json.dumps(dict({"source": "emploiscongo", "url": url,
                           "slug": a.slug.strip("/"), "countries": ["CD"]},
                          **rec), ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="every advertisement, from one request")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for its fields and its state")
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="the sitemap's `lastmod`. **23 advertisements are "
                         "dated 2026 or later, and 1 since 1 August**")
    li.add_argument("--search", help="match the slug; folds accents")
    li.add_argument("--limit", type=int)
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True,
                    help="the whole tail, `emploi-` included")
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
