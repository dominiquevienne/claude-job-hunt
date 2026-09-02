#!/usr/bin/env python3
"""Read one employer's Workday career site.

Workday is an ATS, not a board: each employer runs its own career site at
<tenant>.wdN.myworkdayjobs.com/<site>, and that site is backed by a public JSON
endpoint (`/wday/cxs/...`) needing no key, no cookie and no browser.

Three coordinates identify a board — host, tenant, site — and `resolve` finds
them from the employer's name.

Usage:
  workday.py resolve "Swisscom"
  workday.py facets --host swisscom.wd103.myworkdayjobs.com --tenant swisscom \\
                    --site SwisscomExternalCareers [--like Lausanne]
  workday.py list   --host … --tenant … --site … [--location Switzerland]
                    [--search engineer] [--pages 3] [--with-description]
  workday.py ad     --host … --tenant … --site … (--path /job/… | --req-id R-123)
"""

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _robots import verdict as robots_verdict

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
PAGE = 20  # a limit above 20 is answered with HTTP 400


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def cxs(a, suffix=""):
    return f"https://{a.host}/wday/cxs/{a.tenant}/{a.site}{suffix}"


def post(url, body):
    try:
        r = urllib.request.urlopen(urllib.request.Request(
            url, data=json.dumps(body).encode(),
            headers={"User-Agent": UA, "content-type": "application/json"}),
            timeout=60)
        return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            die("no Workday board at those coordinates (HTTP 404). Host, tenant "
                "and site must all match — find them with: workday.py resolve "
                "\"<employer name>\"", code=4)
        if e.code == 400:
            die("Workday refused the query (HTTP 400). The page size is capped "
                "at 20; a larger --limit is rejected outright.")
        die(f"Workday returned HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach {a_host_of(url)}: {e}")


def a_host_of(url):
    return urllib.parse.urlparse(url).netloc


def get(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(
            url, headers={"User-Agent": UA, "accept": "application/json"}),
            timeout=60)
        return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            die("that posting is gone (HTTP 404) — it was filled or pulled. "
                "Record it as discarded, do not retry.", code=3)
        die(f"Workday returned HTTP {e.code} for that posting")
    except Exception as e:  # noqa: BLE001
        die(f"could not reach {a_host_of(url)}: {e}")


def to_text(markup):
    txt = html.unescape(markup or "")
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", txt)
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", txt)
    txt = re.sub(r"(?i)<li[^>]*>", "- ", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", txt).strip()


# ------------------------------------------------------------------ facets --

def location_facets(payload):
    """Yield (facetParameter, descriptor, id) for every location value.

    The parameter name is per-tenant configuration, not a constant: Swisscom
    exposes `locations` holding cities, Hitachi exposes `locationCountry`
    holding countries. Hardcoding either one silently filters nothing.
    """
    for facet in payload.get("facets") or []:
        if facet.get("facetParameter") != "locationMainGroup":
            continue
        for group in facet.get("values") or []:
            param = group.get("facetParameter")
            for v in group.get("values") or []:
                yield param, v.get("descriptor"), v.get("id"), v.get("count")


def resolve_location(a, payload):
    wanted = a.location.strip().lower()
    matches = [(p, d, i, c) for p, d, i, c in location_facets(payload)
               if d and wanted in d.lower()]
    if not matches:
        available = [d for _, d, _, _ in location_facets(payload)]
        die(f"this board has no location facet matching {a.location!r}. It "
            f"offers: {', '.join(available[:20]) or '(none)'}"
            f"{' …' if len(available) > 20 else ''}. Workday filters on the "
            "employer's own list, so the name must be one of theirs.")
    if len(matches) > 1:
        exact = [m for m in matches if m[1].lower() == wanted]
        if len(exact) != 1:
            die(f"{a.location!r} matches several facets: "
                f"{', '.join(m[1] for m in matches[:8])}. Name one exactly.")
        matches = exact
    param, descriptor, fid, count = matches[0]
    print(f"[workday] location facet {param}={descriptor!r} ({count} postings)",
          file=sys.stderr)
    return {param: [fid]}


# ------------------------------------------------------------------- cards --

def card(a, j, detail=None):
    path = j.get("externalPath") or ""
    req = (j.get("bulletFields") or [None])[0]
    if detail:
        req = detail.get("jobReqId") or req
    out = {
        "id": req,
        # **The site name is case-insensitive at the API and case-preserving
        # in the URL, so it must be folded here or the same vacancy gets two
        # ledger keys.** `workday.py resolve "Swisscom"` returns
        # `swisscomexternalcareers`; the configuration example and the
        # employer's own URL say `SwisscomExternalCareers`; both list the same
        # ads. Measured 2026-09-02. The URL below keeps the caller's spelling
        # because that is what the employer publishes; the key does not.
        "ledger_id": f"workday:{a.tenant}:{a.site.lower()}:{req}",
        "url": f"https://{a.host}/{a.site}{path}",
        "path": path,
        "title": j.get("title"),
        "company": a.tenant,
        "tenant": a.tenant,
        "site": a.site,
        "provider": "workday",
        "location": j.get("locationsText"),
        "posted_relative": j.get("postedOn"),
        # remoteType is a free-text field the employer configures. Swisscom
        # fills it with a workload ("80-100%"), not a work mode.
        "remote_type_raw": j.get("remoteType"),
        "published": None,
        "time_type": None,
    }
    if detail:
        out["published"] = detail.get("startDate")
        out["time_type"] = detail.get("timeType")
        out["country"] = (detail.get("country") or {}).get("descriptor")
        out["location"] = detail.get("location") or out["location"]
        out["description"] = to_text(detail.get("jobDescription"))
    return out


# ---------------------------------------------------------------- commands --

def cmd_facets(a):
    payload = post(cxs(a, "/jobs"),
                   {"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": ""})
    print(f"[workday] {payload.get('total')} postings on this board",
          file=sys.stderr)
    for facet in payload.get("facets") or []:
        param = facet.get("facetParameter")
        if param == "locationMainGroup":
            for p, d, i, c in location_facets(payload):
                if not a.like or a.like.lower() in (d or "").lower():
                    print(json.dumps({"facet": p, "value": d, "id": i,
                                      "count": c}, ensure_ascii=False))
        else:
            for v in facet.get("values") or []:
                d = v.get("descriptor")
                if not a.like or a.like.lower() in (d or "").lower():
                    print(json.dumps({"facet": param, "value": d,
                                      "id": v.get("id"), "count": v.get("count")},
                                     ensure_ascii=False))


def cmd_sites(a):
    """The career sites this tenant publishes, from its own robots.txt.

    **Measured 2026-09-02**: every Workday tenant's `robots.txt` carries one
    `Allow:` line per career site it has opened, plus a `Sitemap:` line for
    each. Four tenants — swisscom, novartis, roche, adobe — all had that exact
    shape, differing only in the site names, which is what a per-tenant file
    should differ in.

    So the `site` coordinate does not have to be guessed or looked up
    elsewhere: **the tenant lists it**. Swisscom publishes three —
    `SwisscomExternalCareers`, `cablexExternalCareers`, `FWVFJOBExternal` —
    and `resolve` finds two of them through HiringCafe.
    """
    v = robots_verdict(a.host)
    if not v["sweep"]:
        die(f"{a.host}: {v['reason']}", 7)
    req = urllib.request.Request(f"https://{a.host}/robots.txt",
                                 headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        die(f"https://{a.host}/robots.txt: {exc}")
    allows = re.findall(r"(?im)^\s*Allow:\s*/([^/\s]+)/\s*$", body)
    maps = re.findall(r"(?im)^\s*Sitemap:\s*(\S+)", body)
    print(json.dumps({"host": a.host, "sites": allows, "sitemaps": maps},
                     ensure_ascii=False))
    print(f"[workday] {len(allows)} career site(s) named by this tenant's own "
          f"robots.txt. The `site` coordinate is case-insensitive at the API "
          f"but case-preserving in the URL — use the spelling here.",
          file=sys.stderr)


def cmd_list(a):
    v = robots_verdict(a.host)
    if not v["sweep"]:
        die(f"{a.host}: {v['reason']} A Workday tenant publishes its own "
            f"robots.txt — this is this employer's answer, not Workday's.", 7)
    applied = {}
    if a.location:
        probe = post(cxs(a, "/jobs"),
                     {"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": ""})
        applied = resolve_location(a, probe)
    kept = 0
    total = None
    for page in range(a.pages):
        payload = post(cxs(a, "/jobs"),
                       {"appliedFacets": applied, "limit": PAGE,
                        "offset": page * PAGE, "searchText": a.search or ""})
        if total is None:
            total = payload.get("total")
            print(f"[workday] {total} postings match", file=sys.stderr)
            if not total:
                print("[workday] zero matches — narrow with --search or check "
                      "the location facet name before concluding they are not "
                      "hiring", file=sys.stderr)
        postings = payload.get("jobPostings") or []
        for j in postings:
            detail = None
            if a.with_description:
                detail = (get(cxs(a) + j.get("externalPath", ""))
                          or {}).get("jobPostingInfo")
            print(json.dumps(card(a, j, detail), ensure_ascii=False))
            kept += 1
        if len(postings) < PAGE:
            break
    print(f"[workday] {kept} returned"
          + (f" of {total}; raise --pages to go further" if total and kept < total
             else ""), file=sys.stderr)


def cmd_ad(a):
    path = a.path
    if not path:
        payload = post(cxs(a, "/jobs"),
                       {"appliedFacets": {}, "limit": 5, "offset": 0,
                        "searchText": a.req_id})
        hits = payload.get("jobPostings") or []
        if not hits:
            die(f"no posting {a.req_id!r} on this board — it was filled or "
                "pulled. Record it as discarded.", code=3)
        path = hits[0].get("externalPath")
    d = get(cxs(a) + path)
    info = (d or {}).get("jobPostingInfo")
    if not info:
        die("Workday returned no jobPostingInfo — report with /board-request")
    stub = {"externalPath": path, "title": info.get("title"),
            "locationsText": info.get("location"),
            "postedOn": info.get("postedOn"),
            "remoteType": info.get("remoteType"),
            "bulletFields": [info.get("jobReqId")]}
    print(json.dumps(card(a, stub, info), ensure_ascii=False, indent=1))


def cmd_resolve(a):
    """Find host/tenant/site for an employer, via HiringCafe's index."""
    state = {"companyNames": [a.employer]}
    url = "https://hiringcafe.com/?" + urllib.parse.urlencode(
        {"searchState": json.dumps(state, separators=(",", ":"))})
    try:
        raw = urllib.request.urlopen(urllib.request.Request(
            url, headers={"User-Agent": UA}), timeout=60).read().decode(
            "utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        die(f"could not reach hiringcafe to resolve the board: {e}")
    m = re.search(r'id="__NEXT_DATA__"[^>]*>(.*?)</script>', raw, re.S)
    if not m:
        die("hiringcafe's page shape changed — resolve by hand: open the "
            "employer's Workday careers page and read host, tenant and site "
            "out of the URL.")
    seen = {}
    for h in json.loads(m.group(1))["props"]["pageProps"].get("ssrHits") or []:
        if h.get("source") != "workday":
            continue
        # NOT board_token: for Workday it is lowercased and truncated at 43
        # characters, so it loses the real site name. apply_url is authoritative.
        p = urllib.parse.urlparse(h.get("apply_url") or "")
        if not p.netloc:
            continue
        seg = [s for s in p.path.split("/") if s]
        if seg and re.fullmatch(r"[a-z]{2}-[A-Z]{2}", seg[0]):
            seg = seg[1:]  # a locale prefix, not the site
        if not seg:
            continue
        name = ((h.get("attributed_org") or {}).get("name")
                or (h.get("enriched_company_data") or {}).get("name") or "?")
        seen.setdefault((p.netloc, p.netloc.split(".")[0], seg[0]), name)
    if not seen:
        print(f"No Workday board found for {a.employer!r}. They may use another "
              "ATS, or HiringCafe may not index them — neither is evidence "
              "they are not hiring. Check their careers page by hand.",
              file=sys.stderr)
        sys.exit(1)
    for (host, tenant, site), name in seen.items():
        print(json.dumps({"host": host, "tenant": tenant, "site": site,
                          "company": name}, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def coords(sp):
        sp.add_argument("--host", required=True,
                        help="e.g. swisscom.wd103.myworkdayjobs.com")
        sp.add_argument("--tenant", required=True)
        sp.add_argument("--site", required=True)

    f = sub.add_parser("facets", help="list the filters this board offers")
    coords(f)
    f.add_argument("--like", help="only facet values containing this text")
    f.set_defaults(func=cmd_facets)

    st = sub.add_parser("sites",
                        help="career sites this tenant names in its robots.txt")
    st.add_argument("--host", required=True)
    st.set_defaults(func=cmd_sites)

    li = sub.add_parser("list", help="list postings")
    coords(li)
    li.add_argument("--location", help="a facet value this employer defines")
    li.add_argument("--search", help="Workday's own full-text search")
    li.add_argument("--pages", type=int, default=1, help=f"{PAGE} postings each")
    li.add_argument("--with-description", action="store_true",
                    help="one extra request per posting")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="read one posting in full")
    coords(ad)
    g = ad.add_mutually_exclusive_group(required=True)
    g.add_argument("--path", help="the externalPath from a card")
    g.add_argument("--req-id", help="the requisition id, looked up by search")
    ad.set_defaults(func=cmd_ad)

    rs = sub.add_parser("resolve", help="employer name -> host, tenant, site")
    rs.add_argument("employer")
    rs.set_defaults(func=cmd_resolve)

    a = p.parse_args()
    for f in ("location", "search", "with_description", "path", "req_id", "like"):
        if not hasattr(a, f):
            setattr(a, f, None)
    a.func(a)


if __name__ == "__main__":
    main()
