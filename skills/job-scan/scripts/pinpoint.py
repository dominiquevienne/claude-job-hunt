#!/usr/bin/env python3
"""Read one employer's board from Pinpoint — two endpoints, two entities, two
id spaces.

Pinpoint is a UK-origin ATS. Each tenant publishes its board as public JSON,
with no key and no browser:

  GET https://<tenant>.pinpointhq.com/postings.json   → the publications
  GET https://<tenant>.pinpointhq.com/jobs.json       → the requisitions
  https://<tenant>.pinpointhq.com/en/postings/<uuid>  → the ad, for a human

**Measured on 684 postings across five tenants on 2026-09-01.**

`robots.txt` closes `/mydata`, `/admin` and `/companies`; neither JSON path is
disallowed and no crawler or AI agent is named. *(`/api/v1/jobs` also exists
and answers `401 — X-API-KEY header not provided`. That is the tenant's own
admin API and it is not this adapter's door.)*

THE TRAP THAT OUTLIVES THE BOARD: **the two endpoints are two different
things, and their ids never overlap.**

    menzies    52 postings    43 jobs     0 ids in common
    davies    276 postings   251 jobs     0 ids in common
    nfamily   281 postings   281 jobs     1 id  in common

A `posting` is a *publication*; a `job` is the *requisition* behind it. Each
posting carries `job.id`, and all 52 of menzies' resolve into `jobs.json`.
**Fifteen jobs across the five tenants carry more than one posting, one of them
seven.** So the two counts differ — and on `nfamilyclub` they are *equal*
while still being disjoint, which is the case that would convince someone the
endpoints are two views of one list.

They are not. A ledger keyed on `jobs.json` ids and an ad URL built from
`postings.json` describe different objects, and nothing in either response says
so. **This adapter reads `postings.json`**, because a candidate applies to a
posting: the URL, the location and the compensation all hang off it.

*(There are three identifiers per ad, which is one more than it looks. `id` is
numeric — `389422`. The public URL carries a **UUID** —
`/en/postings/68f11550-…`. And `job.id` is a fourth number belonging to the
requisition. All three are emitted; the numeric posting id is the ledger key.)*

`province` IS NOT A PROVINCE. Across 684 postings the field holds, verbatim:

    London 149 · United Kingdom 96 · Maharashtra 68 · Bolton 44 ·
    England 38 · Surrey 32 · uk

A city, a country, an Indian state, a town, a nation, a county, and a lowercase
country code — in one field, across five tenants. It is `hays-fr.md`'s
`addressLocality == addressRegion` problem with the levels mixed as well as the
granularity. It is emitted as `province_freetext` and is never a key; `city`
(680 of 684) and `postal_code` (548) are the fields that mean what they say.

WHERE THIS BOARD GETS IT RIGHT, and it is worth recording because so few do:

- **`compensation_visible` actually tracks the figure.** True on 337 of 684,
  a figure on 333, and only **4** visible-with-no-amount. `turijobs.md` has 27
  visible and 2 figures; `platsbanken.md` states the pay *type* on 300 of 300
  and the amount on none. Here the flag means what it says.
- **`workplace_type` is a real three-value enum** — onsite 366, hybrid 259,
  remote 59 — where `recruitee.md` has three overlapping booleans and
  `empleate.md` has one constant.

FINDING TENANTS, AND A LESSON ABOUT DOING IT BY URL. There is no directory.
`pinpoint.py tenants --country GB` reads HiringCafe's cards — but through the
`ats` / `ats_tenant` fields the HiringCafe adapter already extracts, **not** by
matching `pinpointhq.com` in the apply URL.

The difference is not cosmetic: on one draw of 120 cards the URL pattern found
**5** tenants and `ats_tenant` found **23**. Some Pinpoint tenants serve their
board on their own domain, so the apply URL never says `pinpointhq` —
`mountainwarehouse` (187 postings), `breedongroup` (97) and `blackpooltransport`
(3) are all real boards a URL matcher misses. **Re-deriving what an upstream
adapter already labelled is how you under-count a family by four fifths.**

Usage:
  pinpoint.py jobs --tenant menzies
  pinpoint.py jobs --tenant davies --paid-only
  pinpoint.py tenants --country GB

Output: one JSON object per line.
"""

import argparse
import collections
import html as html_mod
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
TENANT_RE = re.compile(r"https?://([a-z0-9][a-z0-9-]*)\.pinpointhq\.com", re.I)
UUID_RE = re.compile(r"/postings/([0-9a-f-]{36})", re.I)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[pinpoint] {msg}", file=sys.stderr)


def host(tenant):
    if "." in tenant:
        h = re.sub(r"^https?://", "", tenant).split("/")[0]
        m = TENANT_RE.match("https://" + h)
        return m.group(1) if m else h.split(".")[0]
    return tenant


def api(tenant, path, retries=2):
    url = f"https://{host(tenant)}.pinpointhq.com{path}"
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8")), url
        except urllib.error.HTTPError as exc:
            if exc.code == 401:
                die(f"{url} answered 401. That is the tenant's own admin API, "
                    "which wants an X-API-KEY. The public board is "
                    "/postings.json and needs nothing.")
            if exc.code in (403, 404):
                die(f"{url} answered {exc.code}. Check the tenant — there is "
                    "no directory, see `pinpoint.py tenants`.")
            if attempt == retries:
                die(f"{url}: HTTP {exc.code}")
            time.sleep(1.5 * (attempt + 1))
        except (urllib.error.URLError, OSError) as exc:
            if attempt == retries:
                die(f"{url}: {exc}")
            time.sleep(1.5 * (attempt + 1))
    return {}, url


def text_of(raw):
    if not isinstance(raw, str):
        return None
    return WS_RE.sub(" ", TAG_RE.sub(" ", html_mod.unescape(raw))).strip() or None


def money(x):
    """The figures, and whether they are a range or a single point.

    299 of the 333 that state an amount are a real range; 34 have min == max,
    which is a point salary written into a range's shape. `compensation` is
    the same value as free text and is formatted inconsistently — '32,000',
    '£26,230 / year' — so the structured fields are the ones used.
    """
    lo, hi = x.get("compensation_minimum"), x.get("compensation_maximum")
    if lo is None and hi is None:
        return None, None, None, None, None
    point = lo is not None and lo == hi
    return lo, hi, x.get("compensation_frequency"), \
        x.get("compensation_currency"), point


def card(tenant, p):
    loc = p.get("location") or {}
    job = p.get("job") or {}
    lo, hi, freq, cur, point = money(p)
    url = p.get("url")
    uuid = (UUID_RE.search(url or "") or [None, None])[1] if url else None
    parts = {
        "description": text_of(p.get("description")),
        "key_responsibilities": text_of(p.get("key_responsibilities")),
        "skills_knowledge_expertise": text_of(
            p.get("skills_knowledge_expertise")),
        "benefits": text_of(p.get("benefits")),
    }
    return {
        # The numeric posting id — the ledger key. See the module docstring:
        # there are three identifiers per ad and they belong to two entities.
        "id": p.get("id"),
        "ledger_id": "pinpoint:{}:{}".format(host(tenant), p.get("id")),
        "url": url,
        "posting_uuid": uuid,
        # The requisition behind this publication. Fifteen jobs in 684
        # postings carry more than one, one of them seven — so this is NOT a
        # unique key for an ad.
        "job_id": job.get("id"),
        "requisition": job.get("requisition_id"),
        "title": p.get("title"),
        "tenant": host(tenant),
        "department": (job.get("department") or {}).get("name"),
        "division": (job.get("division") or {}).get("name"),
        "reporting_to": p.get("reporting_to") or None,
        "city": loc.get("city"),
        "postcode": loc.get("postal_code"),
        "street": loc.get("street_address"),
        "site_name": loc.get("name"),
        # NOT a province. London, United Kingdom, Maharashtra, Bolton,
        # England, Surrey and "uk" all appear in it. Never a key.
        "province_freetext": loc.get("province"),
        "employment_type": p.get("employment_type"),
        "employment_type_text": p.get("employment_type_text"),
        # A real three-value enum: onsite / hybrid / remote.
        "workplace_type": p.get("workplace_type"),
        "salary_min": lo,
        "salary_max": hi,
        "salary_is_a_point": point,
        "salary_frequency": freq,
        "salary_currency": cur,
        # On this board the flag tracks the figure — 337 true, 333 figures,
        # 4 visible with no amount. That is unusual and worth trusting here.
        "salary_marked_visible": bool(p.get("compensation_visible")),
        "salary_freetext": p.get("compensation") or None,
        "closes": p.get("deadline_at"),
        "description": " ".join(v for v in parts.values() if v) or None,
        "description_parts": {k: v for k, v in parts.items() if v} or None,
    }


def cmd_jobs(a):
    data, url = api(a.tenant, "/postings.json")
    posts = data.get("data")
    if posts is None:
        die(f"{url} returned no `data` key. That is the only container in this "
            "payload, so its absence is a read failure rather than an "
            "employer with nothing open.")
    note(f"{len(posts)} postings — {url}")
    if not posts:
        note("a real zero: the endpoint answered with an empty list.")
        return
    jobs = collections.Counter(str((p.get("job") or {}).get("id"))
                               for p in posts)
    multi = sum(1 for v in jobs.values() if v > 1)
    kept = paid = point = 0
    freqs, places, models = collections.Counter(), collections.Counter(), \
        collections.Counter()
    for p in posts:
        c = card(a.tenant, p)
        if a.paid_only and not (c["salary_min"] or c["salary_max"]):
            continue
        if a.city and a.city.lower() not in (c["city"] or "").lower():
            continue
        if c["salary_min"] or c["salary_max"]:
            paid += 1
            if c["salary_frequency"]:
                freqs[c["salary_frequency"]] += 1
            if c["salary_is_a_point"]:
                point += 1
        places[c["province_freetext"]] += 1
        models[c["workplace_type"]] += 1
        print(json.dumps(c, ensure_ascii=False))
        kept += 1
    note(f"{kept} returned of {len(posts)} postings, which are "
         f"{len(jobs)} distinct requisitions — {multi} of those are published "
         "more than once. The ad key is the posting id, not job_id.")
    note(f"salary: {paid} of {kept} state a figure ({dict(freqs)}); {point} of "
         "those are a single point written into a range's shape.")
    note(f"workplace: {dict(models)}")
    if len(places) > 1:
        note("province holds " + ", ".join(
            f"{k!r}" for k, _ in places.most_common(5))
            + " — a city, a country and a county in one field. Use city and "
              "postcode; province_freetext is not a key.")


def cmd_tenants(a):
    root = a.plugin_root or "."
    cmd = [sys.executable, f"{root}/skills/job-scan/scripts/hiringcafe.py",
           "search", "--country", a.country, "--pages", str(a.pages)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except Exception as exc:  # noqa: BLE001 - report, do not swallow
        die(f"could not run hiringcafe.py: {exc}")
    if r.returncode != 0:
        die(f"hiringcafe.py exited {r.returncode}. Its own message:\n"
            f"  {r.stderr.strip()[:400]}\n"
            "An empty tenant list from a failed sweep would read exactly like "
            "a provider nobody uses.")
    seen, cards, via = collections.Counter(), 0, collections.Counter()
    for line in r.stdout.splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        cards += 1
        # HiringCafe already labels the ATS and its tenant. Use that rather
        # than re-deriving it from the apply URL: some Pinpoint tenants serve
        # on their own domain, so a URL pattern under-counts the family.
        # Measured: 8 tenants via ats_tenant against 5 the URL found, and
        # mountainwarehouse (187 postings), breedongroup (97) and
        # blackpooltransport (3) are all real boards the URL missed.
        if str(d.get("ats") or "").lower() == "pinpoint" and d.get("ats_tenant"):
            seen[str(d["ats_tenant"]).lower()] += 1
            via["ats_tenant"] += 1
            continue
        for k in ("apply_url", "url", "job_url", "source_url"):
            v = d.get(k)
            if isinstance(v, str):
                m = TENANT_RE.match(v)
                if m:
                    seen[m.group(1).lower()] += 1
                    via["url"] += 1
                    break
    for t, n in seen.most_common():
        print(json.dumps({"tenant": t, "ads_seen_on_hiringcafe": n,
                          "board": f"https://{t}.pinpointhq.com/postings.json"},
                         ensure_ascii=False))
    note(f"{len(seen)} tenants in {cards} HiringCafe cards for {a.country} "
         f"(matched {dict(via)}). **A hint, not a directory**: HiringCafe "
         "indexes a fraction of Pinpoint, so an employer missing here is not "
         "an employer without a board.")
    if not seen and cards:
        note(f"{cards} cards were read and none was a Pinpoint ad. That is a "
             "real zero for this draw, not a failed sweep — HiringCafe's "
             "sample rotates, so try more --pages or another country.")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("jobs", help="one employer's whole board")
    c.add_argument("--tenant", required=True,
                   help="tenant name or careers hostname")
    c.add_argument("--city")
    c.add_argument("--paid-only", dest="paid_only", action="store_true",
                   help="keep only postings that state a figure")
    c.set_defaults(func=cmd_jobs)

    c = sub.add_parser("tenants", help="tenants seen in HiringCafe's cards")
    c.add_argument("--country", required=True, metavar="ISO2")
    c.add_argument("--pages", type=int, default=3)
    c.add_argument("--plugin-root", dest="plugin_root")
    c.set_defaults(func=cmd_tenants)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
