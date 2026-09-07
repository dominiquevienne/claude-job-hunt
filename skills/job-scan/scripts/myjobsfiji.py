#!/usr/bin/env python3
"""MyJobsFiji (`myjobsfiji.com`) — Fiji's first adapter.

  myjobsfiji.py list [--limit 20]
  myjobsfiji.py list --fetch [--since 2026-09-01] [--live] [--limit 50]
  myjobsfiji.py ad --id 50866 --slug heavy-psv-driver

**190 advertisements inside a sitemap of 3 152 URLs.** The other 2 962 are
company pages, blog posts, categories, cities, states and countries.

    /company/…   2 790      /categories/…   37      /countries/…   11
    /job/…         190      /jobs/…         34      /cities/…      23
    /blog/…         45      /states/…       14      other            8

**Counting the file would report this board 3 152 against 190 — 16.6 times
larger** — the widest such gap this repository has measured. *`jobsbotswana` was
368-against-367 and `ihararejobs` 6 503-against-6 295; here it is
3 152-against-190, and the excess is not noise, it is a directory of
employers.*

THE SITEMAP'S `lastmod` IS A SINGLE VALUE, AND IT IS TODAY

**All 3 152 entries carry `2026-09-07`.** One distinct value across the whole
file: it is the timestamp of the file's regeneration, not of anything's
publication. *Fiji's country page recorded this on 2026-09-04 and it is
unchanged.*

**So `--since` is refused on the sitemap** and offered only with `--fetch`,
where it filters `datePosted` from the advertisement's own schema. Those dates
are real and spread — eight distinct days across ten sampled, 2026-08-16 to
2026-09-05.

*This is the second board measured on 2026-09-07 whose sitemap date says
nothing, and the two say nothing for different reasons: `ihararejobs` moves
its dates when a page is read, this one stamps every row with one rebuild.*
**A `lastmod` is not evidence of anything until it has been looked at.**

THE SCHEMA IS COMPLETE AND ONE OF ITS FIELDS IS NOT

Each advertisement carries a full `JobPosting`, and `strict` JSON parsed all
ten sampled — no lax pass needed here, unlike `ihararejobs` at six of eight.

    datePosted      10/10      validThrough   10/10
    employmentType  10/10      hiringOrganization.name  10/10
    baseSalary.value.minValue   1/10

**`baseSalary` is present on every advertisement and empty on nine of ten**:
`{"currency": "FJD", "value": {"minValue": "", "maxValue": "", "unitText":
"YEAR"}}`. *A reader that emitted the object would hand a consumer a salary
structure with nothing in it.*

**The empty ones carry `unitText: "YEAR"` — a default, sitting beside no
value at all.** *A reader that emitted the object would hand a consumer a
yearly salary structure containing nothing, which is worse than absence
because it looks like a schema that was filled in.*

**The one filled example is correct**: `minValue: "6.10"` with
`unitText: "HOUR"`, a Fijian hourly wage. So this module emits
`salary_fjd_min` and `salary_fjd_max` **only when non-empty**, and carries
`salary_unit_text` beside them so the reader never has to assume the period.

*An earlier draft of this docstring said the filled row read `6.10` against
`YEAR` and called it an hourly rate under a yearly label. That was wrong: the
`YEAR` came from an empty record and the `6.10` from a different
advertisement.* **Two records, one conclusion, and it took exercising the
branch rather than re-reading it to see.**

THE BOARD IS FIJIAN AND SOME ADVERTISEMENTS ARE NOT

One of ten sampled is a UNICEF post in **Honiara, `addressCountry: "Solomon
Islands"`**. *A country taken from the board rather than from the
advertisement would file it under Fiji.*

So `countries` is read from the advertisement when `--fetch` supplies it, and
`country_name` travels verbatim beside it. **A country name this module has no
code for yields an empty `countries` and says so** — an empty list is honest,
a wrong ISO code is not.

*Without `--fetch` there is no country in hand at all, and the rows carry the
board's own jurisdiction with `country_basis` saying exactly that.*

Verified against the live site on 2026-09-07.
"""

import argparse
import datetime
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path
from _ua import UA

BASE = "https://myjobsfiji.com"
SITEMAP = BASE + "/sitemap.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(\d{4}-\d{2}-\d{2})", re.S)
JOB_URL = re.compile(r"^https://myjobsfiji\.com/job/(\d+)/([^/]+)/?$")
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)

# **Written out, and short on purpose.** Only the country names this module has
# actually seen in this board's schema are mapped; anything else yields an
# empty `countries` rather than a guess. A name-to-ISO table that grows by
# guessing is how a row ends up filed under the wrong jurisdiction.
COUNTRY_CODE = {"fiji": "FJ", "solomon islands": "SB"}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[myjobsfiji] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# The host declares no `Crawl-delay`; this spacing is ours and declared as ours.
_PACE = Pace("myjobsfiji.com", own=1.5)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-FJ,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def entries():
    code, body = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}")
    ads, other, stamps = [], 0, set()
    for block in ENTRY.findall(body):
        loc = LOC.search(block)
        if not loc:
            continue
        url = loc.group(1).strip()
        d = LASTMOD.search(block)
        if d:
            stamps.add(d.group(1))
        m = JOB_URL.match(url)
        if not m:
            other += 1
            continue
        ads.append({"source": "myjobsfiji", "url": url,
                    "id": m.group(1), "slug": m.group(2),
                    "ledger_id": f"myjobsfiji:{m.group(1)}"})
    if not ads:
        die(f"{SITEMAP} parsed to zero advertisements from {len(body)} "
            f"characters — read the bytes before believing the zero.")
    ads.sort(key=lambda r: int(r["id"]), reverse=True)
    return ads, other, sorted(stamps)


def posting_on(page):
    for block in LDJSON.findall(page):
        for strict in (True, False):
            try:
                d = json.loads(block.strip(), strict=strict)
            except ValueError:
                continue
            for it in (d if isinstance(d, list) else [d]):
                if isinstance(it, dict) and it.get("@type") == "JobPosting":
                    return it, None, "strict" if strict else "lax"
            break
    return None, "no readable JobPosting on the page", None


def card(row, post, mode):
    org = post.get("hiringOrganization") or {}
    place = post.get("jobLocation") or {}
    addr = (place.get("address") or {}) if isinstance(place, dict) else {}
    cname = (addr.get("addressCountry") or "").strip()
    code = COUNTRY_CODE.get(fold(cname))
    bs = post.get("baseSalary") or {}
    val = (bs.get("value") or {}) if isinstance(bs, dict) else {}
    lo, hi = str(val.get("minValue") or ""), str(val.get("maxValue") or "")
    out = dict(row)
    out.update({
        "title": (post.get("title") or "").strip() or None,
        "employer": ((org.get("name") or "").strip() or None
                     if isinstance(org, dict) else None),
        "employer_site": org.get("sameAs") if isinstance(org, dict) else None,
        "city": (addr.get("addressLocality") or "").strip() or None,
        "region": (addr.get("addressRegion") or "").strip() or None,
        # **From the advertisement, not from the board.** One of ten sampled
        # is in Honiara, `addressCountry: "Solomon Islands"`.
        "country_name": cname or None,
        "countries": [code] if code else [],
        "country_basis": ("read from the advertisement" if code else
                          f"the advertisement names `{cname}`, which this "
                          f"module has no code for — an empty list rather "
                          f"than a guess" if cname else
                          "the advertisement names no country"),
        "employment_type": post.get("employmentType"),
        "posted": (post.get("datePosted") or "")[:10] or None,
        "valid_through": (post.get("validThrough") or "")[:10] or None,
        "json_pass": mode,
    })
    # **Emitted only when filled.** Present and empty on 9 of 10 sampled, and
    # the tenth reads `6.10` against `unitText: "YEAR"` — an hourly rate under
    # a yearly label. The unit travels unchanged because it is the wrong part.
    if lo or hi:
        out["salary_fjd_min"] = lo or None
        out["salary_fjd_max"] = hi or None
        out["salary_unit_text"] = val.get("unitText")
    return out


def cmd_list(a):
    ads, other, stamps = entries()
    note(f"{len(ads)} advertisement(s) and {other} other URL(s) in the "
         f"sitemap. **Counting the file would report this board "
         f"{(len(ads) + other) / len(ads):.0f}× larger** — the rest is a "
         f"directory of employers, plus blog, categories and places.")
    note(f"`lastmod` takes {len(stamps)} distinct value(s) across the file"
         + (f" — {stamps[0]}, which is a regeneration stamp and not a "
            f"publication date." if len(stamps) == 1 else "."))
    if a.since and not a.fetch:
        die("`--since` needs `--fetch`. **Every entry in this sitemap carries "
            "the same `lastmod`**, so filtering on it returns either all of "
            "the board or none of it. `datePosted` in the advertisement's "
            "schema is real and spread over weeks.")
    if a.live and not a.fetch:
        die("`--live` needs `--fetch`: `validThrough` is in the "
            "advertisement's schema, not in the sitemap.")
    if not a.fetch:
        rows = [dict(r, countries=["FJ"],
                     country_basis="the board's own jurisdiction — no "
                                   "advertisement was read; use --fetch for "
                                   "the country the advertisement names")
                for r in ads]
        if a.search:
            rows = [r for r in rows if fold(a.search) in fold(r["slug"])]
        if a.limit:
            rows = rows[: a.limit]
        print(json.dumps({"source": "myjobsfiji", "country": "FJ",
                          "sitemap_urls": len(ads) + other,
                          "advertisements": len(ads), "other_urls": other,
                          "lastmod_values": stamps, "returned": len(rows),
                          "ads": rows}, ensure_ascii=False, indent=1))
        return
    todo = ads[: a.limit] if a.limit else ads
    note(f"opening {len(todo)} of {len(ads)} page(s) at {_PACE.source()}.")
    today = datetime.date.today().isoformat()
    kept, broken, dropped, lax = [], [], 0, 0
    for row in todo:
        code, page = get(row["url"])
        if code != 200:
            broken.append((row["id"], f"HTTP {code}"))
            continue
        post, why, mode = posting_on(page)
        if post is None:
            broken.append((row["id"], why))
            continue
        if mode == "lax":
            lax += 1
        c = card(row, post, mode)
        if a.since and (not c["posted"] or c["posted"] < a.since):
            dropped += 1
            continue
        if a.live and c["valid_through"] and c["valid_through"] < today:
            dropped += 1
            continue
        if a.search and fold(a.search) not in fold(c["title"] or ""):
            continue
        kept.append(c)
    if lax:
        note(f"{lax} needed the lax JSON pass — 0 of 10 did when this was "
             f"measured, so a rise here is a change in the board.")
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{i} ({w})" for i, w in broken[:5]))
    outside = [c["id"] for c in kept if c["countries"] and
               c["countries"] != ["FJ"]]
    if outside:
        note(f"{len(outside)} advertisement(s) are not located in Fiji — "
             f"the board is Fijian and its postings are not all Fijian.")
    print(json.dumps({"source": "myjobsfiji", "country": "FJ",
                      "advertisements": len(ads), "read": len(todo),
                      "kept": len(kept), "unreadable": len(broken),
                      "filtered_out": dropped, "lax_json": lax,
                      "outside_fiji": len(outside), "ads": kept},
                     ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}/job/{a.id}/{a.slug.strip('/')}/"
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.id} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    post, why, mode = posting_on(page)
    if post is None:
        die(f"{url}: {why}")
    row = {"source": "myjobsfiji", "url": url, "id": a.id,
           "slug": a.slug.strip("/"), "ledger_id": f"myjobsfiji:{a.id}"}
    print(json.dumps(card(row, post, mode), ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="advertisements from the sitemap")
    li.add_argument("--fetch", action="store_true",
                    help="open each page for `datePosted`, employer, city and "
                         "the country the advertisement names")
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="the advertisement's own `datePosted`. Requires "
                         "--fetch: every sitemap entry shares one `lastmod`")
    li.add_argument("--live", action="store_true",
                    help="drop advertisements whose `validThrough` has "
                         "passed. Requires --fetch")
    li.add_argument("--search", help="matches the slug without --fetch and "
                                     "the title with it; folds accents")
    li.add_argument("--limit", type=int)
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by id and slug")
    ad.add_argument("--id", required=True)
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
