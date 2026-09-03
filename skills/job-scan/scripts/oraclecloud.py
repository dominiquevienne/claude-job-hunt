#!/usr/bin/env python3
"""Read one employer's board from Oracle Recruiting Cloud — the biggest ATS
family this repository did not cover.

Measured across twelve countries by a sibling session: `oraclecloud` is the
**largest provider with no adapter** — 164 cards of 2 838, and the only family
besides `icims2`, `eightfold` and `taleo_careersection` present in **all twelve
markets sampled**. That is what the *reach* criterion in
`shared/boards/README.md` is for.

  GET /hcmRestApi/resources/latest/recruitingCESites          → the career sites
  GET /hcmRestApi/resources/latest/recruitingCEJobRequisitions → the board
  GET /hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails → the text
  https://<host>/hcmUI/CandidateExperience/en/sites/<site>/requisitions/job/<id>

**No browser, no account, no key.** `robots.txt` on a tenant host is a 404 —
none published. The host is the tenant: `ecwl.fa.us2.oraclecloud.com`,
`fa-etjg-saasfaprod1.fa.ocs.oraclecloud.com`.

Verified against two live tenants on 2026-09-02.

THE TRAP THAT OUTLIVES THE BOARD: **without `expand=requisitionList` the
endpoint reports 1 428 jobs and returns none of them.**

    …&finder=findReqs;siteNumber=CX_1,limit=5
        → 200, TotalJobsCount 1428, requisitionList: []

    …&expand=requisitionList&finder=findReqs;siteNumber=CX_1,limit=5
        → 200, TotalJobsCount 1428, requisitionList: 5 items

Valid JSON, HTTP 200, and **a large confident count attached to an empty
list**. A caller who trusts `TotalJobsCount` reports a board of 1 428; one who
trusts the list reports zero; neither is told which they got. The adapter
always sends the expand and treats *a non-zero count with an empty list* as a
hard error naming the parameter.

`siteNumber` DOES NOTHING, AND NEVER SAYS SO. It looks like the parameter that
picks which career site to read. On the tenant measured:

    siteNumber=CX            1428 jobs, first id 238677
    siteNumber=CX_1          1428 jobs, first id 238677
    siteNumber=CX_2001       1428 jobs, first id 238677
    siteNumber=TOTALLY_BOGUS 1428 jobs, first id 238677
    siteNumber=              1428 jobs, first id 238677

**A value that does not exist returns the same board as the right one.** So
this adapter does not claim site scoping: it reports the tenant's
requisitions, and `sites` lists what the tenant declares only so the ad URL can
be built. `recruitingCESites` is a real directory — `ecwl` declares *ClubCorp*
(`CX`) and a copy of its old site — but the number is not a filter.

`Distance` IS THE POSTING DATE. On 100 of 100 requisitions the field named
`Distance` held `1788220800000.0`, which is `PostedDate` as a millisecond
epoch — **the same value, on every row**. It is not a distance, there is no
location search in the query, and a reader who takes it for one gets a number
that grows by 86 400 000 a day. Emitted only as
`distance_field_is_the_posted_date`, never as a distance.

AND THE LISTING HAS NO DESCRIPTION. `ShortDescriptionStr` **equals the title on
88 of 100**. The real text is `ExternalDescriptionStr` in the details resource
— 7 731 characters on the first ad — at one request per job. `search` does not
fetch it and says so; `read` does.

Usage:
  oraclecloud.py sites --host ecwl.fa.us2.oraclecloud.com
  oraclecloud.py search --host ecwl.fa.us2.oraclecloud.com --limit 50
  oraclecloud.py read --host ecwl.fa.us2.oraclecloud.com --limit 10

Output: one JSON object per line.
"""

import argparse
import collections
import datetime
import html as html_mod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _robots import verdict as robots_verdict

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

REST = "/hcmRestApi/resources/latest/"
# limit=200 was served in full; the whole board is reachable — offset 1 425 of
# 1 428 returned the last 3 and 1 430 returned none. No window here.
PAGE = 200

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[oraclecloud] {msg}", file=sys.stderr)


def host_of(h):
    return re.sub(r"^https?://", "", h).split("/")[0]


def get(host, resource, query, retries=2):
    url = f"https://{host_of(host)}{REST}{resource}?{query}"
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read().decode("utf-8", "replace")
            try:
                return json.loads(body), url
            except ValueError:
                die(f"{url} did not return JSON ({len(body)} characters). A "
                    "host that is not an Oracle Recruiting tenant answers the "
                    "Fusion login page, not an error.")
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                die(f"{url} answered {exc.code}. The candidate-experience "
                    "resources are public; this reads like the wrong host or "
                    "a tenant that has closed its external site.")
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


def page(host, site, limit, offset):
    q = ("onlyData=true&expand=requisitionList.secondaryLocations"
         f"&finder=findReqs;siteNumber={urllib.parse.quote(site)},"
         f"limit={limit},offset={offset},sortBy=POSTING_DATES_DESC")
    data, url = get(host, "recruitingCEJobRequisitions", q)
    items = data.get("items") or []
    if not items:
        die(f"{url} returned no `items`. That is the only container in this "
            "payload, so its absence is a read failure.")
    it = items[0]
    total = it.get("TotalJobsCount")
    reqs = it.get("requisitionList") or []
    if total and not reqs and offset == 0:
        die(f"the endpoint reports {total} jobs and returned none of them.\n"
            f"  {url}\n"
            "That is what a missing `expand=requisitionList` looks like — 200, "
            "valid JSON, a large count and an empty list. This request does "
            "send the expand, so if you see this the resource has changed.")
    return total, reqs, url


def as_date(ms):
    """`Distance` is PostedDate in milliseconds. Prove it rather than assume."""
    try:
        return datetime.datetime.utcfromtimestamp(float(ms) / 1000).date(
            ).isoformat()
    except Exception:  # noqa: BLE001 - a non-timestamp is the interesting case
        return None


def card(host, site, r, detail=None):
    ident = r.get("Id")
    secondary = [s.get("Name") or s.get("PrimaryLocation")
                 for s in (r.get("secondaryLocations") or [])]
    short = (r.get("ShortDescriptionStr") or "").strip()
    title = (r.get("Title") or "").strip()
    out = {
        "id": ident,
        "ledger_id": f"oraclecloud:{host_of(host)}:{ident}",
        "url": (f"https://{host_of(host)}/hcmUI/CandidateExperience/en/sites/"
                f"{site}/requisitions/job/{ident}"),
        "title": r.get("Title"),
        "tenant_host": host_of(host),
        "location": r.get("PrimaryLocation"),
        "country": r.get("PrimaryLocationCountry"),
        "secondary_locations": [x for x in secondary if x] or None,
        "locations_count": 1 + len([x for x in secondary if x]),
        "published": r.get("PostedDate"),
        "posting_end": r.get("PostingEndDate"),
        "workplace_type": r.get("WorkplaceType") or None,
        "job_family": r.get("JobFamily"),
        "job_function": r.get("JobFunction"),
        "job_schedule": r.get("JobSchedule"),
        "job_type": r.get("JobType"),
        "worker_type": r.get("WorkerType"),
        "legal_employer": r.get("LegalEmployer"),
        "department": r.get("Department"),
        "organization": r.get("Organization"),
        # NOT a description: equal to the title on 88 of 100.
        "short_description_equals_title": bool(short) and short == title,
        # NOT a distance. The same millisecond epoch as PostedDate on 100 of
        # 100, with no location search in the query.
        "distance_field_is_the_posted_date": as_date(r.get("Distance")),
        "detail_read": False,
    }
    if detail:
        out.update({
            "description": text_of(detail.get("ExternalDescriptionStr")),
            "qualifications": text_of(
                detail.get("ExternalQualificationsStr")),
            "responsibilities": text_of(
                detail.get("ExternalResponsibilitiesStr")),
            "corporate_description": text_of(
                detail.get("CorporateDescriptionStr")),
            "category": detail.get("Category"),
            "contact_name": detail.get("ExternalContactName") or None,
            "posted_start": detail.get("ExternalPostedStartDate"),
            "posted_end": detail.get("ExternalPostedEndDate"),
            "detail_read": True,
        })
    return out


def detail_for(host, site, ident):
    q = ("expand=all&onlyData=true&finder=ById;"
         f"Id=%22{urllib.parse.quote(str(ident))}%22,"
         f"siteNumber={urllib.parse.quote(site)}")
    data, _ = get(host, "recruitingCEJobRequisitionDetails", q)
    items = data.get("items") or []
    return items[0] if items else None


def sites_of(host):
    data, _ = get(host, "recruitingCESites", "onlyData=true&limit=50")
    return data.get("items") or []


def url_segment(site):
    """The path a human's ad URL uses.

    It is `SiteURLName` when the tenant has set one and `SiteNumber`
    otherwise — measured: ClubCorp publishes at `/sites/CX/` with
    SiteURLName null, and FMOLHS at `/sites/fmolhs-careers/` from a
    SiteURLName while its SiteNumber is `CX_3001`. Building the URL from
    SiteNumber alone produces a link that does not resolve.
    """
    return site.get("SiteURLName") or site.get("SiteNumber")


def resolve_site(a):
    if a.site:
        return a.site, a.site
    got = sites_of(a.host)
    if not got:
        note("no career site declared; falling back to CX_1 for the ad URL "
             "only.")
        return "CX_1", "CX_1"
    # Prefer an ACTIVE site, then one that declares a URL name. The first
    # site in the list is not necessarily either: `eqtm` lists an INACTIVE
    # "FMOLHS Career Portal" before the live one, and building URLs from it
    # would produce links into a retired site.
    def rank(x):
        return (x.get("StatusCode") == "ORA_ACTIVE", bool(x.get("SiteURLName")))
    pick = sorted(got, key=rank, reverse=True)[0]
    if pick is not got[0]:
        note(f"the first site listed is {got[0].get('SiteNumber')} "
             f"({got[0].get('StatusCode')}); using "
             f"{pick.get('SiteNumber')} ({pick.get('StatusCode')}) instead.")
    seg, num = url_segment(pick), pick.get("SiteNumber") or "CX_1"
    note(f"{len(got)} career site(s) declared — " + ", ".join(
        f"{s.get('SiteNumber')}={s.get('SiteName')!r}" for s in got[:4]))
    note(f"ad URLs use {seg!r} (SiteURLName if the tenant set one, else "
         "SiteNumber).")
    note("siteNumber does NOT filter the board: a bogus value returns the "
         "same jobs and the same first id. What follows is the tenant's "
         "requisitions, not one site's.")
    return seg, num


def collect(a, site):
    total, first, url = page(a.host, site, min(a.limit or PAGE, PAGE), 0)
    note(f"{total} requisitions — {url.split('?')[0]}")
    rows = list(first)
    want = a.limit or total or 0
    off = 0
    while len(rows) < want:
        off += PAGE
        _, more, _ = page(a.host, site, PAGE, off)
        if not more:
            break
        rows.extend(more)
        time.sleep(a.delay)
    return rows[:want], total


def emit(a, site, want_detail):
    seg, num = site
    rows, total = collect(a, num)
    countries = collections.Counter()
    short_eq = multi = read = 0
    for r in rows:
        d = detail_for(a.host, num, r.get("Id")) if want_detail else None
        if d:
            read += 1
        c = card(a.host, seg, r, d)
        countries[c["country"]] += 1
        short_eq += bool(c["short_description_equals_title"])
        multi += c["locations_count"] > 1
        print(json.dumps(c, ensure_ascii=False))
        if want_detail:
            time.sleep(a.delay)
    n = len(rows)
    note(f"{n} returned of {total}; countries {dict(countries.most_common(5))}")
    if multi:
        note(f"{multi} of {n} list a secondary location.")
    if short_eq:
        note(f"ShortDescriptionStr repeats the title on {short_eq} of {n} — "
             "it is not a description on those.")
    if want_detail:
        note(f"{read} of {n} details read, one request each.")
    else:
        note("no descriptions: the listing carries none. Use `read` for the "
             "ad text, at one request per job.")


def cmd_sites(a):
    got = sites_of(a.host)
    for s in got:
        print(json.dumps({"site_number": s.get("SiteNumber"),
                          "url_name": s.get("SiteURLName"),
                          "ad_url_segment": url_segment(s),
                          "name": s.get("SiteName"),
                          "status": s.get("StatusCode")},
                         ensure_ascii=False))
    note(f"{len(got)} site(s). **The number does not filter the board** — a "
         "value that does not exist returns the same jobs. It is only used to "
         "build the ad URL.")


def cmd_search(a):
    _v = robots_verdict(a.host)
    if not _v["sweep"]:
        die(f"{_v['host']}: {_v['reason']} On Oracle Cloud the host belongs to the employer, so this is that employer's "
            f"answer and not the platform's. Issue #73.",
                8 if _v["sweep"] is None else 7)
    emit(a, resolve_site(a), False)


def cmd_read(a):
    _v = robots_verdict(a.host)
    if not _v["sweep"]:
        die(f"{_v['host']}: {_v['reason']} On Oracle Cloud the host belongs to the employer, so this is that employer's "
            f"answer and not the platform's — and it refuses the content, not just the sweep. Issue #73.",
                8 if _v["sweep"] is None else 7)
    emit(a, resolve_site(a), True)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, h in (("sites", cmd_sites, "the career sites a tenant declares"),
                        ("search", cmd_search, "the board, no ad text"),
                        ("read", cmd_read,
                         "the board plus the description, one request per job")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--host", required=True,
                       help="the tenant host — ecwl.fa.us2.oraclecloud.com")
        c.add_argument("--site", help="siteNumber for the ad URL. It does not "
                                      "filter; see `sites`")
        c.add_argument("--limit", type=int)
        c.add_argument("--delay", type=float, default=0.3)
        c.set_defaults(func=fn)
    a = p.parse_args()
    if a.cmd in ("search", "read") and not a.limit:
        note("no --limit: reading the whole board. Some tenants publish over "
             "a thousand requisitions.")
    a.func(a)


if __name__ == "__main__":
    main()
