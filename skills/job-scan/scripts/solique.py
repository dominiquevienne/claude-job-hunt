#!/usr/bin/env python3
"""Read one employer's Solique job portal.

Solique is an ATS, not a board: one employer per tenant, no search across
employers. Public HTML and JSON, unauthenticated, **no browser**.

The awkward part is that Solique does not have one architecture, it has three,
and which one a tenant uses is invisible until you ask:

  1. <tenant>/<lang>/ajax/           JSON  — complete board  (e.g. iss, 105 ads)
  2. <tenant>/<lang>/api/v1/data/    JSON  — complete board  (e.g. ktzh, 177)
  3. <tenant>/                       HTML  — PARTIAL board, and unpageable
                                            (ottosag serves 25 of a stated 157)

`list` tries them in that order and always says which route answered and how
complete it is. **Route 3 is never a full board** — see --help of `list`.

Usage:
  solique.py list  --tenant iss [--lang de] [--search projet]
  solique.py ad    --tenant iss --id 4061853
  solique.py check --tenant iss --id 4061853
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
from _robots import allowed as robots_allowed
from datetime import datetime, timezone

from _sitemap import locs as sitemap_locs

from _ua import UA
BASE = "https://live.solique.ch"
LINK = re.compile(r"/job/details/(\d+)")
TOTAL = re.compile(r"(\d+)\s*Stellen", re.I)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def _robots_gate(url, tag, exit_code=7):
    """Ask per tenant and per path before fetching. Issues #100 and #101.

    **On a tenant platform the rules file is the employer's, not the vendor's**
    — two Teamtailor tenants declared opposite things while this repository
    recorded the permissive one as platform policy (#73). `icims` and `taleez`
    have asked per tenant for weeks; this adapter did not.

    **And it asks about the path.** `verdict()` answers *is this host closed in
    one block*; a careers site that refuses its ad path while leaving its root
    open passes that check and refuses every advertisement.

    A refusal **stops the command** with exit 7 and the module's own words —
    nothing here decides what a refusal means.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return None
    a = robots_allowed(parts.netloc, parts.path or "/")
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", exit_code)
    if a.get("requested_host") and a["host"] != a["requested_host"]:
        print(f"[{tag}] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts, and a platform that "
              f"has been renamed reaches us this way before it reaches us as "
              f"a rename.", file=sys.stderr)
    return a



def get(url):
    _robots_gate(url, "solique")
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60)
        return r.getcode(), r.headers.get_content_type(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, "", b""
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach live.solique.ch: {e}")


def get_json(url):
    """Return the parsed body, or None when this route is not the tenant's.

    The JSON is served with a UTF-8 BOM, which json.loads rejects outright
    ("Unexpected UTF-8 BOM"). utf-8-sig is required, not defensive.
    """
    status, ctype, raw = get(url)
    if status != 200 or "json" not in ctype:
        return None
    try:
        return json.loads(raw.decode("utf-8-sig"))
    except ValueError:
        return None


def unwrap(v):
    """ktzh wraps most fields as {"value": ..., "id": ...}; iss does not."""
    if isinstance(v, dict):
        return v.get("value")
    return v


def epoch_date(v):
    """iss `startDate` is a unix timestamp, not a date string."""
    try:
        return datetime.fromtimestamp(int(v), tz=timezone.utc).strftime("%d.%m.%Y")
    except (TypeError, ValueError):
        return v or None


def to_text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", htmlmod.unescape(markup)).strip()


def card(tenant, jid, **kw):
    out = {
        "id": str(jid),
        "ledger_id": f"solique:{tenant.lower()}:{jid}",
        "url": f"{BASE}/{tenant}/job/details/{jid}/",
        "company": tenant,
        "tenant": tenant.lower(),
        "provider": "solique",
    }
    out.update({k: v for k, v in kw.items() if v not in (None, "")})
    return out


# ------------------------------------------------------------------ routes --

def route_ajax(tenant, lang):
    """iss-style: jobTitle / publicDate / region / zip / locationFreeText."""
    d = get_json(f"{BASE}/{tenant}/{lang}/ajax/")
    jobs = (d or {}).get("jobs")
    if not isinstance(jobs, list):
        return None
    out = []
    for j in jobs:
        jid = (LINK.search(j.get("link") or "") or [None, None])[1] \
            if LINK.search(j.get("link") or "") else None
        if not jid:
            continue
        out.append(card(tenant, jid,
                        title=j.get("jobTitle"),
                        published=j.get("publicDate"),
                        location=j.get("locationFreeText") or j.get("zip"),
                        region=j.get("region"),
                        employment_type=j.get("employmentType"),
                        category=j.get("jobCategory"),
                        start=epoch_date(j.get("startDate")),
                        description=to_text(j.get("fullTextSearch"))))
    return ("ajax", out, len(out))


def route_api(tenant, lang):
    """ktzh-style: an entirely different field set. title / location / office."""
    d = get_json(f"{BASE}/{tenant}/{lang}/api/v1/data/")
    jobs = (d or {}).get("jobs")
    if not isinstance(jobs, list):
        return None
    out = []
    for j in jobs:
        m = LINK.search(j.get("link") or "")
        if not m:
            continue
        out.append(card(tenant, m.group(1),
                        title=unwrap(j.get("title")),
                        published=unwrap(j.get("dateModified")),
                        location=unwrap(j.get("location")),
                        department=unwrap(j.get("office"))
                        or unwrap(j.get("organization")),
                        category=unwrap(j.get("field")),
                        description=to_text(j.get("htmlContent"))))
    return ("api/v1/data", out, len(out))


def route_html(tenant, _lang):
    """The fallback, and it is PARTIAL. Never present it as a whole board."""
    status, _ctype, raw = get(f"{BASE}/{tenant}/")
    if status != 200:
        return None
    # **No headers to pass**: `get()` returns the content-type as a string,
    # not the header object, and threading it through would change a contract
    # for one call site. `decode_body` without headers still reads the page's
    # own `<meta charset>` — the right declaration for an HTML page — then
    # strict UTF-8, then a total fallback that now says so aloud. #115.
    body = decode_body(raw)[0]
    ids = list(dict.fromkeys(LINK.findall(body)))
    if not ids:
        return None
    m = TOTAL.search(to_text(body))
    stated = int(m.group(1)) if m else None
    return ("html", [card(tenant, i) for i in ids], stated or len(ids))


ROUTES = (route_ajax, route_api, route_html)


# ---------------------------------------------------------------- commands --

def cmd_list(a):
    for route in ROUTES:
        got = route(a.tenant, a.lang)
        if not got:
            continue
        name, rows, total = got
        kept = 0
        for r in rows:
            if a.search and a.search.lower() not in (r.get("title") or "").lower():
                continue
            print(json.dumps(r, ensure_ascii=False))
            kept += 1
        note = (f"[solique:{a.tenant}] route {name!r}: {kept} emitted, "
                f"{len(rows)} read")
        short = total and len(rows) < total
        if short:
            note += f" of {total} stated"
            if name == "html":
                # ottosag serves 25 of a stated 157, and NOTHING pages it:
                # ?page=2 repeats the same rows, every other offset parameter
                # returns an error page. The shortfall is real and permanent.
                note += (" — **this board is TRUNCATED and cannot be paged**: "
                         "every offset and page parameter tried returns the "
                         "same rows or an error page. Do not report this count "
                         "as the size of the board")
        else:
            note += " (complete: the board states no more than this)"
        print(note, file=sys.stderr)
        if a.search and not kept:
            print(f"[solique:{a.tenant}] the board is not empty — every ad was "
                  f"filtered out by --search {a.search!r}. Titles only.",
                  file=sys.stderr)
        return
    die(f"no route answered for tenant {a.tenant!r}. Solique serves three "
        f"architectures and this tenant matched none — either the tenant name "
        f"is wrong (a wrong one answers HTTP 404), or it uses a fourth shape. "
        f"Report it with the board-request skill rather than treating it as an "
        f"employer with nothing open.", code=4)


def read_ad(tenant, jid):
    return get(f"{BASE}/{tenant}/job/details/{jid}/")


def cmd_ad(a):
    status, _ctype, raw = read_ad(a.tenant, a.id)
    if status == 404:
        die(f"no ad {a.id} on tenant {a.tenant} (HTTP 404) — it was filled or "
            f"pulled. Record it as discarded.", code=3)
    if status != 200:
        die(f"tenant {a.tenant} answered HTTP {status} for ad {a.id}", code=4)
    # **No headers to pass**: `get()` returns the content-type as a string,
    # not the header object, and threading it through would change a contract
    # for one call site. `decode_body` without headers still reads the page's
    # own `<meta charset>` — the right declaration for an HTML page — then
    # strict UTF-8, then a total fallback that now says so aloud. #115.
    body = decode_body(raw)[0]
    title = page_title(body)
    # Same control as `check`: not every tenant 404s an unknown id.
    _, _, landing = get(f"{BASE}/{a.tenant}/")
    home = page_title(decode_body(landing)[0] if landing else "")
    if home and title == home:
        die(f"ad {a.id} on tenant {a.tenant} answered HTTP 200 with the "
            f"tenant's own landing page — this id does not resolve. Some "
            f"tenants answer an unknown id with 200 rather than 404. Record it "
            f"as discarded.", code=3)
    print(json.dumps(card(a.tenant, a.id, title=title or None,
                          description=to_text(body)[:20000]),
                     ensure_ascii=False, indent=1))


def page_title(body):
    m = re.search(r"(?is)<title>(.*?)</title>", body or "")
    return htmlmod.unescape(m.group(1)).strip() if m else ""


def cmd_check(a):
    """Answer cover-letter step 1b.

    The 404 is the test on most tenants — and NOT on all of them. ktzh answers
    an unknown id with HTTP 200 and its own landing page (1 112 bytes against
    23 196 for a real ad), so a status-only check reports a non-existent ad as
    open. Comparing the ad's <title> against the tenant's landing page settles
    it without knowing which tenants behave which way.
    """
    status, _ctype, raw = read_ad(a.tenant, a.id)
    # **No headers to pass**: `get()` returns the content-type as a string,
    # not the header object, and threading it through would change a contract
    # for one call site. `decode_body` without headers still reads the page's
    # own `<meta charset>` — the right declaration for an HTML page — then
    # strict UTF-8, then a total fallback that now says so aloud. #115.
    body = decode_body(raw)[0] if raw else ""
    if status == 404:
        verdict, why = "closed", "HTTP 404 — the portal stopped serving it"
    elif status == 200:
        _, _, landing = get(f"{BASE}/{a.tenant}/")
        home = page_title(decode_body(landing)[0] if landing else "")
        if home and page_title(body) == home:
            verdict, why = ("closed",
                            "HTTP 200, but the page is the tenant's own landing "
                            "page — this id does not resolve. Some tenants "
                            "answer an unknown id with 200 rather than 404")
        else:
            verdict, why = "open", "HTTP 200, and the page is not the landing page"
    else:
        verdict, why = "unverified", f"HTTP {status}"
    # A JobPosting block is present on some tenants and absent on others, and
    # never on Microsites pages. It describes the employer's configuration, not
    # the ad — so it is reported, never used as the test.
    print(json.dumps({"id": a.id, "tenant": a.tenant, "verdict": verdict,
                      "why": why, "has_jobposting": "JobPosting" in body,
                      "url": f"{BASE}/{a.tenant}/job/details/{a.id}/"},
                     ensure_ascii=False))
    sys.exit(0 if verdict == "open" else 1)


def cmd_tenants(a):
    """Read the tenant names out of the platform's sitemap index.

    **This file used to say "there is no directory". There is one**, at the
    standard path, under a `robots.txt` of `User-agent: * / Allow: /`, and it
    was found on 2026-09-02 by looking rather than by reasoning.

    It is a directory, not *the* directory: it named 13 tenants of which 6
    carried ads, it listed `vebego` where the live tenant is `vebegoag`, and
    it **missed three tenants this adapter already knew** —
    `vebegoag`, `united-machining`, `ottosag`. So it is a source of names to
    try, and the `list` command is what settles whether a name is a board.
    """
    code, ctype, body = get(f"{BASE}/sitemap.xml")
    if code != 200 or "xml" not in ctype:
        die(f"{BASE}/sitemap.xml answered {code} as {ctype!r} — a sitemap that "
            f"is not XML is not a sitemap. The directory may have moved; fall "
            f"back to job-room, which indexes Solique ads.")
    # The one reader, then the name out of the URL — the old pattern needed
    # `</loc>` on the heels of the filename and missed CDATA entirely.
    names = [m.group(1) for m in
             (re.search(r"/sitemap-([a-z0-9-]+)\.xml$", u)
              for u in sitemap_locs(body)) if m]
    out = sorted(set(names))
    print(f"[solique] {len(out)} tenant name(s) in the sitemap index. This "
          f"lists names, not boards: on 2026-09-02, 7 of 13 answered with zero "
          f"ads and three live tenants were absent from it. Run `list` on each "
          f"before believing either way.", file=sys.stderr)
    print(json.dumps({"source": f"{BASE}/sitemap.xml", "tenants": out},
                     ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--tenant", required=True,
                        help="the path segment, e.g. iss, ktzh, manor, ottosag")

    li = sub.add_parser("list", help="list this employer's ads")
    common(li)
    li.add_argument("--lang", default="de",
                    help="language segment for the JSON routes (default de)")
    li.add_argument("--search", help="filter on the title, locally")
    li.set_defaults(fn=cmd_list)

    ad = sub.add_parser("ad", help="read one ad in full")
    common(ad)
    ad.add_argument("--id", required=True)
    ad.set_defaults(fn=cmd_ad)

    te = sub.add_parser("tenants",
                        help="tenant names from the platform's sitemap index")
    te.set_defaults(fn=cmd_tenants)

    ck = sub.add_parser("check", help="is this ad still open? (step 1b)")
    common(ck)
    ck.add_argument("--id", required=True)
    ck.set_defaults(fn=cmd_check)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
