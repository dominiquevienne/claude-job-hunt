#!/usr/bin/env python3
"""Keejob — Tunisia (`www.keejob.com`).

  keejob.py list [--since 2026-08-05] [--limit 20] [--search comptable] [--fetch]
  keejob.py ad   --id 246110

**The only readable board of the eight Tunisian ranks measured on 2026-09-04**
— rank 1 is a public service whose rules could not be read, rank 3 answers 403
to its own `robots.txt`. So this adapter does not add a board to a covered
country; **it is the Tunisian market as far as this tool can see it.**

`/sitemap.xml` names its children honestly — `sitemap-jobs.xml` beside
`-companies`, `-professions`, `-static` and three blog files — so the
advertisements are reachable without counting anything else.

*Three of the seven children are declared over `http`, not `https`. This
adapter only follows `sitemap-jobs.xml`, which is one of the four on `https`;
the mixed scheme is recorded because it is the kind of thing that bites a
caller who follows the index blindly.*

WHAT WAS MEASURED, 2026-09-05

    sitemap-jobs.xml    827 <loc>, 827 distinct — no duplicates
    dates               28 distinct, 2026-08-05 → 2026-09-04
                        all 827 within thirty days; busiest day 184 (22 %)

**827 with no duplicates is worth stating**, because it is not the usual case:
`onape.td` listed one advertisement three times and `caglobalint.com` listed
its own index page among its advertisements.

THE `ld+json` DOES NOT ALWAYS PARSE, AND `strict=False` IS NOT OPTIONAL

Each page carries one `JobPosting`. **Three of eight blocks sampled hold a raw
control character inside a string**, which `json.loads` refuses outright.
`strict=False` read all eight. A reader that does not pass it loses about a
third of the board and loses it *silently*, because a `JSONDecodeError` on one
advertisement looks like a broken advertisement rather than a broken reader.

WHAT THE FIELDS ARE WORTH, MEASURED ON TWELVE TO FOURTEEN ADVERTISEMENTS

    title · datePosted · validThrough · employer · jobLocation    12/12
    baseSalary                                                     7/12
    employmentType                                                14/14 — and useless

**`employmentType` is `"OTHER"` on every advertisement measured.** Present,
well-formed, and carrying no information. **It is not emitted**: a field whose
only value is a placeholder does not become useful by being passed on, and a
caller filtering on contract type would filter on a constant. The card says so;
the JSON does not carry it.

**`baseSalary` is real where it exists** — `TND`, `minValue`/`maxValue`,
`unitText: MONTH`. It is emitted with its currency in the field name, never as
a bare number: `salary_tnd_min`, `salary_tnd_max`. The `kalibrr.md` rule —
*a field whose meaning depends on a caveat gets a name that carries the
caveat*.

**Three employers of twelve read `Entreprise Anonyme`.** That is the site's own
placeholder for an employer who chose not to be named, not a missing value.
It is emitted as-is with `employer_anonymous: true`, because *"anonymous by the
employer's choice"* and *"we could not find it"* are different facts and a
`None` would merge them.

Verified against the live site on **2026-09-05**.
"""

import argparse
import html as html_mod
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _robots import allowed as robots_allowed
from _ua import UA

BASE = "https://www.keejob.com"
SITEMAP = BASE + "/sitemap-jobs.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)
AD_ID = re.compile(r"/offres-emploi/(\d+)/")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[keejob] {msg}", file=sys.stderr)


def gate(url):
    """Per path, never per host."""
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, parts.path or "/")
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)


def get(url):
    gate(url)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "fr-TN,fr;q=0.9,ar;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def entries():
    code, body = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    rows, seen = [], set()
    for block in ENTRY.findall(body):
        loc = LOC.search(block)
        if not loc:
            continue
        u = html_mod.unescape(loc.group(1).strip())
        if u in seen:
            continue
        seen.add(u)
        d = LASTMOD.search(block)
        rows.append((u, d.group(1) if d else None))
    if not rows:
        die(f"{SITEMAP} parsed to zero entries from {len(body)} characters — "
            f"read the bytes before believing the zero.")
    return rows, len(ENTRY.findall(body))


def posting_on(page):
    """The `JobPosting`, read with `strict=False`.

    **Not a nicety.** Three of eight blocks sampled on 2026-09-05 carry a raw
    control character inside a string; strict parsing refuses them and the loss
    is silent, because one unreadable advertisement looks like a bad
    advertisement and not like a bad reader.
    """
    blocks = LDJSON.findall(page)
    for b in blocks:
        for strict in (True, False):
            try:
                d = json.loads(b.strip(), strict=strict)
            except ValueError:
                continue
            for cand in (d if isinstance(d, list) else [d]):
                if isinstance(cand, dict) and cand.get("@type") == "JobPosting":
                    return cand, None
            break
    return None, f"no readable JobPosting in {len(blocks)} ld+json block(s)"


def card(url, lastmod, posting):
    org = posting.get("hiringOrganization") or {}
    name = (org.get("name") or "").strip() if isinstance(org, dict) else ""
    place = posting.get("jobLocation") or {}
    addr = (place.get("address") or {}) if isinstance(place, dict) else {}
    sal = posting.get("baseSalary") or {}
    val = (sal.get("value") or {}) if isinstance(sal, dict) else {}
    cur = (sal.get("currency") or "").strip().lower() if isinstance(sal, dict) else ""
    out = {
        "source": "keejob",
        "url": url,
        "id": (AD_ID.search(url).group(1) if AD_ID.search(url) else None),
        "title": html_mod.unescape(posting.get("title") or "").strip() or None,
        "employer": name or None,
        # **"anonymous by the employer's choice" and "we could not find it" are
        # different facts.** A `None` would merge them.
        "employer_anonymous": bool(name) and "anonyme" in name.lower(),
        "city": (addr.get("addressLocality") or "").strip() or None,
        "region": (addr.get("addressRegion") or "").strip() or None,
        "country_code": (addr.get("addressCountry") or "").strip() or None,
        "posted": (posting.get("datePosted") or "")[:10] or lastmod,
        "valid_through": (posting.get("validThrough") or "")[:10] or None,
        "countries": ["TN"],
    }
    # The currency travels in the name, never beside the number.
    if cur and (val.get("minValue") is not None
                or val.get("maxValue") is not None):
        out[f"salary_{cur}_min"] = val.get("minValue")
        out[f"salary_{cur}_max"] = val.get("maxValue")
        out["salary_period"] = val.get("unitText")
    # `employmentType` is deliberately absent — "OTHER" on 14 of 14 measured.
    return out


def cmd_list(a):
    rows, raw = entries()
    note(f"{raw} <url> in {SITEMAP.rsplit('/', 1)[-1]}, {len(rows)} distinct")
    if a.since:
        rows = [r for r in rows if r[1] and r[1] >= a.since]
        note(f"{len(rows)} dated {a.since} or later")
    if a.limit:
        rows = rows[: a.limit]
    if not a.fetch and not a.search:
        print(json.dumps({"source": "keejob", "country": "TN",
                          "sitemap_entries": raw, "distinct": len(rows),
                          "ads": [{"url": u, "posted": d,
                                   "id": (AD_ID.search(u).group(1)
                                          if AD_ID.search(u) else None)}
                                  for u, d in rows]},
                         ensure_ascii=False, indent=1))
        return
    kept, broken = [], []
    needle = fold(a.search) if a.search else None
    for u, d in rows:
        code, page = get(u)
        if code in (404, 410):
            broken.append((u, f"HTTP {code}"))
            continue
        if code != 200:
            broken.append((u, f"HTTP {code}"))
            continue
        posting, why = posting_on(page)
        if posting is None:
            broken.append((u, why))
            continue
        c = card(u, d, posting)
        if needle and needle not in fold(c["title"] or ""):
            continue
        kept.append(c)
    if broken:
        note(f"{len(broken)} advertisement(s) unreadable: "
             + "; ".join(f"{u.rsplit('/', 2)[-2]} ({w})" for u, w in broken[:5]))
    print(json.dumps({"source": "keejob", "country": "TN",
                      "sitemap_entries": raw, "read": len(kept) + len(broken),
                      "kept": len(kept), "unreadable": len(broken), "ads": kept},
                     ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    rows, _raw = entries()
    match = [u for u, _d in rows if f"/offres-emploi/{a.id}/" in u]
    if not match:
        die(f"no advertisement {a.id} in the sitemap. It may have expired — "
            f"the sitemap holds only what is live.", EXIT_GONE)
    url = match[0]
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.id} is gone (HTTP {code}). Record it as discarded.", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    posting, why = posting_on(page)
    if posting is None:
        die(f"{url}: {why}")
    print(json.dumps(card(url, None, posting), ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="advertisements from the sitemap")
    li.add_argument("--since", metavar="YYYY-MM-DD")
    li.add_argument("--limit", type=int)
    li.add_argument("--search", help="match the title; folds accents")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for its fields; without it the listing "
                         "is the sitemap alone — one request instead of 827")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by numeric id")
    ad.add_argument("--id", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
