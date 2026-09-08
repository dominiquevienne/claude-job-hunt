#!/usr/bin/env python3
"""JobWeb Rwanda (`jobwebrwanda.com`) — Rwanda's first adapter, and it has stopped.

  jobwebrwanda.py list [--since 2026-01-01] [--limit 20]
  jobwebrwanda.py list --fetch --limit 5      # 30 s PER advertisement
  jobwebrwanda.py ad --slug funding-and-reporting-officer-at-akagera-management-company

**558 advertisements, and nothing published since 2026-06-24** — two and a
half months at the time of writing, and zero dated on or after 1 August.

    558 advertisements   167 distinct dates   2019-05-08 → 2026-06-24
    busiest day            8, which is 1.4 %
    since 2026-06-01      66
    since 2026-08-01       0

*This is the most evenly spread board this repository has measured* — 1.4 % on
the busiest day, against 18.5 % for `jobartis` and 60.5 % for `ihararejobs`.
**A clean distribution and a dead board are not contradictory**: the site
published steadily for seven years and then stopped.

THE HOST ASKS FOR THIRTY SECONDS, AND IT GETS THEM

`robots.txt` is two lines: `User-agent: *` and **`Crawl-delay: 30`**. *That is
a directive, not a remark* — `ejob.az` taught this repository the same lesson
with a delay of 5.

**`list` costs one request. `--fetch` costs 30 s per advertisement**, so
reading the whole board would take four and a half hours. The flag says so
before it starts.

THE ROOT DEMANDS A LOGIN AND THE ADVERTISEMENTS DO NOT

    GET /                       302 → /login/?redirect_to=…/login/?redirect_to=…
    GET /sitemap.xml            200 → /sitemap_index.xml
    GET /job_listing-sitemap…   200
    GET /jobs/<slug>/           200, a complete JobPosting

**A redirect loop into a login page**, and the inventory behind it is public
anyway. *A reader that took the root as the board's answer would have filed
Rwanda as closed;* **the verdict is taken where the advertisements are, and
this module never requests `/`.**

*No account is created and none is needed. If the advertisements ever move
behind that login, this adapter stops and says so — it does not authenticate.*

THE SITEMAP'S DATE IS THE POSTING DATE HERE — CHECKED, NOT ASSUMED

`lastmod` equals `datePosted` on **3 of 3** sampled, including the most recent.
**So `--since` works on one request**, which is worth stating because the two
boards measured immediately before it could not:

    ihararejobs   the date MOVES when the page is read     our own crawl
    myjobsfiji    ONE value for 3 152 entries              a rebuild stamp
    jobwebrwanda  lastmod == datePosted, 3 of 3            the posting date

**A `lastmod` is worth nothing until it has been looked at, and there are at
least three ways for it to be worthless.**

NOTHING HERE IS LIKELY TO BE LIVE, AND THIS MODULE DOES NOT CLAIM A CENSUS

The most recent advertisement is dated 2026-06-24 and its own `validThrough`
is **2026-07-04** — already past. On the three sampled, `validThrough` falls
ten to eleven days after `datePosted`.

*If that interval holds, nothing on this board is live.* **It is an inference
from three, not a count**: liveness is per advertisement and costs one request
each at thirty seconds. `--live` exists, requires `--fetch`, and is honest
about what it just spent.

*Rwanda's country page recorded «201 offres vivantes» on 2026-09-04. This
module cannot reproduce that at a reasonable cost and does not contradict it —
it reports what the sitemap says and what three advertisements said.*

ONE SITEMAP BY NAME, NEVER A WILDCARD

`/job_listing-sitemap.xml`. **The index also offers `job_loc-`, `job_cat-` and
`job_type-`, which a `job_listing*` glob would sweep in** — they are
taxonomies, not advertisements, and this repository has paid for that mistake
before. The name is written out.

`/jobs/` itself appears among the entries and is not an advertisement: 559
`<loc>`, 558 advertisements.

Verified against the live site on 2026-09-08.
"""

import argparse
import datetime
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

BASE = "https://jobwebrwanda.com"
SITEMAP = BASE + "/job_listing-sitemap.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(\d{4}-\d{2}-\d{2})", re.S)
AD_URL = re.compile(r"^https://jobwebrwanda\.com/jobs/([^/]+)/?$")
LDJSON = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobwebrwanda] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# **No `own` argument.** The host asks for 30 s in its `robots.txt` and that is
# what `Pace` reads; passing a spacing of ours would only be able to make it
# faster, which is the one direction that is not ours to choose.
_PACE = Pace("jobwebrwanda.com")


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-RW,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
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
    ads, other = [], 0
    for block in ENTRY.findall(body):
        loc = LOC.search(block)
        if not loc:
            continue
        url = html_mod.unescape(loc.group(1).strip())
        m = AD_URL.match(url)
        # `/jobs/` itself is in this file and is the listing page.
        if not m or m.group(1) == "jobs":
            other += 1
            continue
        d = LASTMOD.search(block)
        ads.append({"source": "jobwebrwanda", "url": url, "slug": m.group(1),
                    "ledger_id": f"jobwebrwanda:{m.group(1)}",
                    # **The posting date.** `lastmod == datePosted` on 3 of 3
                    # sampled, so this is named for what it is rather than for
                    # where it came from.
                    "posted": d.group(1) if d else None,
                    "posted_source": "sitemap `lastmod`, equal to `datePosted` "
                                     "on 3 of 3 sampled 2026-09-08",
                    "countries": ["RW"]})
    if not ads:
        die(f"{SITEMAP} parsed to zero advertisements from {len(body)} "
            f"characters — read the bytes before believing the zero.")
    ads.sort(key=lambda r: (r["posted"] or ""), reverse=True)
    return ads, other


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
    bs = post.get("baseSalary") or {}
    val = (bs.get("value") or {}) if isinstance(bs, dict) else {}
    lo, hi = str(val.get("minValue") or ""), str(val.get("maxValue") or "")
    out = dict(row)
    out.update({
        "title": html_mod.unescape((post.get("title") or "").strip()) or None,
        "employer": (html_mod.unescape((org.get("name") or "").strip()) or None
                     if isinstance(org, dict) else None),
        "employer_site": org.get("sameAs") if isinstance(org, dict) else None,
        "city": (addr.get("addressLocality") or "").strip() or None,
        "country_name": (addr.get("addressCountry") or "").strip() or None,
        "employment_type": post.get("employmentType"),
        "posted_on_page": (post.get("datePosted") or "")[:10] or None,
        "valid_through": (post.get("validThrough") or "")[:10] or None,
        "json_pass": mode,
    })
    # **Only when filled**, and the currency travels with the number.
    if lo or hi:
        out["salary_min"] = lo or None
        out["salary_max"] = hi or None
        out["salary_currency"] = bs.get("currency") if isinstance(bs, dict) else None
    # **Says when the two dates disagree**, rather than preferring one in
    # silence: the sitemap's date is the reason `--since` costs one request,
    # and a divergence would retire that.
    if out["posted_on_page"] and out["posted"] and out["posted_on_page"] != out["posted"]:
        out["date_conflict"] = (f"sitemap says {out['posted']}, the page says "
                                f"{out['posted_on_page']} — `--since` filters "
                                f"on the sitemap")
    return out


def cmd_list(a):
    ads, other = entries()
    newest = max((r["posted"] or "") for r in ads)
    note(f"{len(ads)} advertisement(s) and {other} other entr(y|ies) in "
         f"`job_listing-sitemap.xml`. **Most recent: {newest}** — this board "
         f"has stopped publishing.")
    rows = ads
    if a.since:
        rows = [r for r in rows if r["posted"] and r["posted"] >= a.since]
        note(f"{len(rows)} of {len(ads)} dated {a.since} or later.")
    if a.search:
        rows = [r for r in rows if fold(a.search) in fold(r["slug"])]
    if a.limit:
        rows = rows[: a.limit]
    if not a.fetch:
        if a.live:
            die("`--live` needs `--fetch`: `validThrough` is on the "
                "advertisement page, not in the sitemap. **At "
                f"{_PACE.source()} that is {len(rows)} × 30 s.**")
        print(json.dumps({"source": "jobwebrwanda", "country": "RW",
                          "advertisements": len(ads), "other_entries": other,
                          "newest": newest, "returned": len(rows),
                          "ads": rows}, ensure_ascii=False, indent=1))
        return
    mins = len(rows) * 30 / 60
    note(f"opening {len(rows)} page(s) at {_PACE.source()} — **about "
         f"{mins:.0f} minute(s)**. The host asked for this delay; it is not "
         f"ours to shorten.")
    today = datetime.date.today().isoformat()
    kept, broken, dropped, lax, conflicts = [], [], 0, 0, 0
    for row in rows:
        code, page = get(row["url"])
        if code in (404, 410):
            broken.append((row["slug"][:38], f"gone — HTTP {code}"))
            continue
        if code != 200:
            broken.append((row["slug"][:38], f"HTTP {code}"))
            continue
        post, why, mode = posting_on(page)
        if post is None:
            broken.append((row["slug"][:38], why))
            continue
        if mode == "lax":
            lax += 1
        c = card(row, post, mode)
        if c.get("date_conflict"):
            conflicts += 1
        if a.live and c["valid_through"] and c["valid_through"] < today:
            dropped += 1
            continue
        kept.append(c)
    if conflicts:
        note(f"**{conflicts} advertisement(s) disagree with the sitemap's "
             f"date.** It matched on 3 of 3 when this was written; a rise "
             f"here retires `--since` on one request.")
    if lax:
        note(f"{lax} needed the lax JSON pass (0 of 3 did when measured).")
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{s} ({w})" for s, w in broken[:5]))
    if a.live:
        note(f"{dropped} dropped as expired. **The newest advertisement on "
             f"this board expired 2026-07-04**, so a small number here is the "
             f"board's state and not a filter failing.")
    print(json.dumps({"source": "jobwebrwanda", "country": "RW",
                      "advertisements": len(ads), "read": len(rows),
                      "kept": len(kept), "unreadable": len(broken),
                      "expired_dropped": dropped if a.live else None,
                      "date_conflicts": conflicts, "lax_json": lax,
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    url = f"{BASE}/jobs/{a.slug.strip('/')}/"
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.slug} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code in (301, 302):
        die(f"{url}: HTTP {code}. **The root of this site redirects into a "
            f"login loop**; if the advertisements now do too, this adapter "
            f"stops here rather than authenticating.", EXIT_REFUSED)
    if code != 200:
        die(f"{url}: HTTP {code}")
    post, why, mode = posting_on(page)
    if post is None:
        die(f"{url}: {why}")
    row = {"source": "jobwebrwanda", "url": url, "slug": a.slug.strip("/"),
           "ledger_id": f"jobwebrwanda:{a.slug.strip('/')}",
           "posted": None, "countries": ["RW"]}
    print(json.dumps(card(row, post, mode), ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="advertisements, from one request")
    li.add_argument("--fetch", action="store_true",
                    help="open each page. **The host asks for 30 s between "
                         "requests**, so this is half a minute per "
                         "advertisement and four hours for the board")
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="the sitemap's `lastmod`, which equals `datePosted` "
                         "on 3 of 3 sampled — so this costs one request")
    li.add_argument("--live", action="store_true",
                    help="drop advertisements whose `validThrough` has "
                         "passed. Requires --fetch, and the newest here "
                         "expired 2026-07-04")
    li.add_argument("--search", help="match the slug; folds accents")
    li.add_argument("--limit", type=int)
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by slug")
    ad.add_argument("--slug", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
