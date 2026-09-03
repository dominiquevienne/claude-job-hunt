#!/usr/bin/env python3
"""Read the HR.ge platform — six Georgian brands on one API, and only four of
them have any ads.

**No key, no cookie, no browser.** Every brand's `robots.txt` is 109 bytes,
`Allow: /`, and declares a sitemap **on the platform's API host**:

    Sitemap: https://api.p.hr.ge/public-portal/tenant/<n>/api/v3/seo/sitemap

**The tenant number in that line is the whole discovery.** It names the
platform, and the ad page names the rest: `tenant/1`, `/2`, `/4`, `/5` appear
in one ad's own markup.

MEASURED 2026-09-03 — six tenants, and `7` upward answer `500`:

    tenant  host              <loc>    announcements
      1     www.hr.ge        39 247        1 062
      2     www.cv.ge        39 247        1 062
      3     www.career.ge    38 185            0
      4     www.doctor.ge    38 249           64
      5     www.chefs.ge     38 345          160
      6     www.bankers.ge   38 185            0

**Three corrections to what this repository recorded, all in the same
direction — the sitemap is not the ad count:**

- **1 062 ads, not 39 247.** Of tenant 1's `<loc>` elements, **36 593 are
  `/customer/` employer pages** and 1 505 are search landing pages. Counting
  the file reports a board thirty-seven times its size — the arithmetic that
  would have inflated Jobstore and Vieclam24h.
- **`career.ge` has no ads at all**, and it was recorded here as sharing
  hr.ge's corpus. **It does share it — because its own `robots.txt` declares
  `tenant/1`, which is hr.ge's sitemap, while career.ge is tenant 3.** A brand
  pointing at another brand's file, and a conclusion drawn from the file
  rather than from the brand.
- **`doctor.ge` and `chefs.ge` were not known here** — vertical boards,
  medical and culinary, 64 and 160 ads.

`hr.ge` and `cv.ge` are genuinely one corpus: **identical `<loc>` counts and
identical byte counts, 5 377 511**, differing only in the host they name.

THE LISTING COUNTS LINKS, NOT ADS. `/jobs/today?p=<n>` returns **100 links a
page over 8 pages — 800 links, 281 distinct ads. A factor of 2.85**, and
**page 4 added zero new ones** while answering with a full hundred. A sweep
that counts what it fetched reports three times the board. This file
deduplicates and prints both numbers, because only their difference exposes
the padding.

**The end of the listing is honest**, which is worth saying next to
`encuentra24.md`: page 50 returns **0 ads**, not page 1 again.

THE PAYLOAD CARRIES CONTACT DETAILS THE AD ITSELF ASKS TO HIDE. On the
measured ad, **`hideContactPerson: true`** — and `contactName`,
`contactEmail` and `contactMobilePhoneNumber` are all populated. **So the
allow-list here is not tidiness, it is the publisher's own instruction**: 150
keys, of which about forty are Google Ads slot configuration, and `KEEP` names
the eighteen a ledger has any use for.

**And `similarAnnouncements` embeds other ads inside an ad.** A reader that
harvests every `announcementId` in the payload collects the neighbours — the
LinkedIn suggestion-block trap, in JSON.

THE SEARCH ENDPOINT EXISTS AND ITS REQUEST SHAPE IS NOT ESTABLISHED.
`POST …/api/v3/announcement-search` answers `500` — *"Attempted to divide by
zero"* — to `{"page","pageSize"}`, `{"pageNumber","pageSize"}`,
`{"page","size"}` and `{"paging":{…}}` alike, **all four with an identical
279-byte body**, which is agreement produced by nothing having parsed. Guessing
further would be #72's fault; the listing works and is used instead.

Verified against the live platform on **2026-09-03**.
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _robots import verdict as robots_verdict
from _sitemap import count_says, locs as sitemap_locs
from _zero import zero_note

API = "https://api.p.hr.ge/public-portal/tenant/{tenant}/api/v3"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# tenant → (host, announcements measured 2026-09-03). Dated measurements, not
# properties: `tenants --check` re-counts them.
TENANTS = {
    1: ("www.hr.ge", 1062),
    2: ("www.cv.ge", 1062),
    3: ("www.career.ge", 0),
    4: ("www.doctor.ge", 64),
    5: ("www.chefs.ge", 160),
    6: ("www.bankers.ge", 0),
}

ANN_RE = re.compile(r"/announcement/(\d+)")

# **The allow-list.** The payload has 150 keys, about forty of them Google Ads
# slot configuration, and it carries a contact name, email and phone on an ad
# whose own `hideContactPerson` is true. Nothing outside this tuple is copied,
# so a field added tomorrow cannot leak through.
KEEP = ("announcementId", "title", "customerId", "customerName", "addresses",
        "dates", "deadlineDate", "publishDate", "expired", "isPriority",
        "isWorkFromHome", "isSuitableForStudent", "isAnonymous",
        "employmentFormTypeName", "languages", "drivingLicenses",
        "salaryFrom", "salaryTo", "showSalary", "totalApplicationsOnWebsite")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[hr.ge] {msg}", file=sys.stderr)


def get(url, timeout=90, as_json=False):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json" if as_json else "text/html,*/*;q=0.8",
        "Accept-Language": "ka-GE,ka;q=0.9,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if as_json:
                return r.getcode(), json.loads(raw.decode("utf-8", "replace"))
            return r.getcode(), raw
    except urllib.error.HTTPError as e:
        return e.code, (None if as_json else b"")
    except (urllib.error.URLError, OSError, ValueError) as e:
        die(f"{url}: {e}")


def tenant_of(n):
    n = int(n)
    if n not in TENANTS:
        die(f"tenant {n} is not one this platform serves. Known: "
            f"{', '.join(str(k) for k in sorted(TENANTS))} — and 7 upward "
            f"answer 500. Run `tenants` to re-read them.")
    return n


def check_robots(host):
    v = robots_verdict(host)
    if not v["sweep"]:
        die(f"{host}: {v['reason']}",
            EXIT_UNKNOWN if v["sweep"] is None else EXIT_REFUSED)
    return v


def ad_urls(body):
    """The `/announcement/` URLs of a sitemap, and the rest counted, not lost."""
    urls = sitemap_locs(body)
    ads = [u for u in urls if "/announcement/" in u]
    return urls, ads


def cmd_tenants(a):
    for n, (host, ads) in sorted(TENANTS.items()):
        row = {"tenant": n, "host": host, "announcements_2026_09_03": ads}
        if a.check:
            code, body = get(f"{API.format(tenant=n)}/seo/sitemap")
            if code != 200:
                row["live"] = None
                row["note"] = f"HTTP {code}"
            else:
                urls, live = ad_urls(body)
                row.update(live=len(live), locs=len(urls),
                           drift=len(live) - ads)
                if not live:
                    row["says"] = ("no `/announcement/` URL in a sitemap of "
                                   f"{len(urls)} — this brand publishes "
                                   f"employer pages and no ads.")
        print(json.dumps(row, ensure_ascii=False))
    note("`career.ge` declares tenant/1 in its own robots.txt — hr.ge's "
         "sitemap — while being tenant 3. A brand pointing at another "
         "brand's file is how it came to be recorded as sharing hr.ge's "
         "corpus; its own tenant has no ads.")
    if not a.check:
        note("these are dated measurements. `tenants --check` re-counts them.")


def cmd_sitemap(a):
    n = tenant_of(a.tenant)
    host, _ = TENANTS[n]
    check_robots(host)
    code, body = get(f"{API.format(tenant=n)}/seo/sitemap")
    if code != 200:
        die(f"tenant {n} sitemap: HTTP {code}")
    urls, ads = ad_urls(body)
    if not urls:
        die(f"tenant {n} sitemap: {count_says(body)}")
    other = len(urls) - len(ads)
    for u in (ads[:a.limit] if a.limit else ads):
        m = ANN_RE.search(u)
        print(json.dumps({"id": m.group(1) if m else None,
                          "ledger_id": f"hr.ge:{n}:{m.group(1)}" if m else None,
                          "url": u, "tenant": n, "host": host},
                         ensure_ascii=False))
    note(f"{len(ads)} advertisement URL(s) out of {len(urls)} `<loc>` — "
         f"**{other} of them are employer and search pages, not ads.** "
         f"Counting the file reports a board many times its size.")
    if not ads:
        note(zero_note("hr.ge", where=host, extra=(
            f"The sitemap answered with {len(urls)} URLs and none of them is "
            f"an advertisement. On this platform that is a real state — "
            f"career.ge and bankers.ge publish employer pages and no ads — "
            f"and not a parse failure.")))


def cmd_search(a):
    n = tenant_of(a.tenant)
    host, _ = TENANTS[n]
    check_robots(host)
    seen, links, page = set(), 0, 1
    while True:
        code, raw = get(f"https://{host}/jobs/today?p={page}", timeout=60)
        if code != 200:
            note(f"page {page}: HTTP {code} — stopping.")
            break
        html = raw.decode("utf-8", "replace")
        ids = set(ANN_RE.findall(html))
        if not ids:
            note(f"page {page} carried no advertisement link — that is this "
                 f"listing's end, and it says so honestly rather than "
                 f"serving page one again.")
            break
        links += len(ids)
        new = ids - seen
        for ident in sorted(new):
            print(json.dumps({
                "id": ident,
                "ledger_id": f"hr.ge:{n}:{ident}",
                "url": f"https://{host}/announcement/{ident}",
                "tenant": n, "host": host, "page": page,
            }, ensure_ascii=False))
        seen |= ids
        if a.limit and len(seen) >= a.limit:
            break
        if a.pages and page >= a.pages:
            break
        page += 1
        time.sleep(a.delay)
    if not seen:
        note(zero_note("hr.ge", where=host))
        return
    # **Both numbers, because only their difference exposes the padding.**
    # Measured on tenant 1: 800 links over 8 pages against 281 distinct ads,
    # and page 4 added none at all while answering with a full hundred.
    note(f"{len(seen)} distinct advertisement(s) from {links} link(s) over "
         f"{page} page(s) — a factor of {links / max(len(seen), 1):.2f}. "
         f"**The listing repeats ads across pages**: report what you counted, "
         f"never what you fetched.")


def card(ann, tenant, host):
    """Only what KEEP names. Never a copy of the record — see the header."""
    out = {k: ann.get(k) for k in KEEP}
    ident = out.get("announcementId")
    out["ledger_id"] = f"hr.ge:{tenant}:{ident}"
    out["url"] = f"https://{host}/announcement/{ident}"
    out["tenant"] = tenant
    # Values, not keys: `showSalary` is false and both bounds are null on the
    # measured ad, so a "salary field present" count would report 100%.
    out["salary_stated"] = bool(out.get("salaryFrom") or out.get("salaryTo"))
    return out


def cmd_ad(a):
    if a.url:
        m = ANN_RE.search(a.url)
        if not m:
            die(f"{a.url}: no `/announcement/<id>` in it.")
        ident = m.group(1)
        netloc = urllib.parse.urlsplit(a.url).netloc
        n = next((k for k, v in TENANTS.items() if v[0] == netloc), a.tenant)
    else:
        ident, n = a.id, a.tenant
    if not ident:
        die("give --url or --id.")
    n = tenant_of(n)
    host, _ = TENANTS[n]
    check_robots(host)
    code, d = get(f"{API.format(tenant=n)}/announcement/{ident}",
                  timeout=45, as_json=True)
    if code != 200 or not d:
        die(f"announcement {ident} on tenant {n}: HTTP {code}", EXIT_GONE)
    ann = ((d.get("data") or {}).get("announcement")) or {}
    if not ann:
        die(f"announcement {ident}: the payload has no `announcement` object "
            f"— the API answered 200 and said nothing about this ad.",
            EXIT_PARTIAL)
    out = card(ann, n, host)
    if a.with_text:
        out["description"] = ann.get("description")
    out["description_chars"] = len(ann.get("description") or "")
    print(json.dumps(out, ensure_ascii=False))
    if ann.get("hideContactPerson"):
        note("this ad sets `hideContactPerson: true` **and the payload still "
             "carries the contact's name, email and phone**. The card emits "
             "none of them: the allow-list here is the publisher's own "
             "instruction, not housekeeping.")
    note("`similarAnnouncements` in the payload lists other ads. It is not "
         "read: harvesting every id in a payload collects the neighbours.")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("tenants", help="the six brands and their ad counts")
    t.add_argument("--check", action="store_true", help="re-count live")
    t.set_defaults(func=cmd_tenants)

    m = sub.add_parser("sitemap", help="every ad URL a tenant publishes")
    m.add_argument("--tenant", type=int, default=1)
    m.add_argument("--limit", type=int)
    m.set_defaults(func=cmd_sitemap)

    s = sub.add_parser("search", help="the live listing, deduplicated")
    s.add_argument("--tenant", type=int, default=1)
    s.add_argument("--pages", type=int)
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=0.8)
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="one ad from the API, allow-listed")
    d.add_argument("--url")
    d.add_argument("--id")
    d.add_argument("--tenant", type=int, default=1)
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
