#!/usr/bin/env python3
"""Read one employer's Haufe/Abacus umantis career site.

umantis is an ATS, not a board: each employer runs its own site, either at
recruitingapp-<n>.umantis.com or behind a vanity domain of their own
(jobs.<employer>.com). There is no search across employers, so this script
targets one employer at a time — the same shape as workday.py and ats.py.

Two paths carry everything, and both answer unauthenticated even when the site
root is gated by SSO:

  /Jobs                                  the listing
  /Vacancies/<id>/Description/<segment>  one vacancy, full text

The segment is NOT a constant. It varies per vacancy inside a single tenant,
so it is read from the listing and never guessed. See --help of `ad`.

There is deliberately no `resolve` command: HiringCafe indexes no umantis ad
(0 of 771 Swiss ads), so the trick that finds tenants for Workday, Greenhouse,
Lever and Ashby does not work here. The user supplies the careers URL, or it
arrives as the externalUrl of a jobup / job-room / jobs.ch row.

Usage:
  umantis.py list  --host jobs.bobst.com [--search product]
  umantis.py ad    --host jobs.bobst.com --id 9151 [--segment 2]
  umantis.py check --host jobs.bobst.com --id 9151     # open / not open
"""

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _robots import verdict as robots_verdict

from _ua import UA
# A vacancy link in the listing, with the segment the tenant actually serves.
VACANCY = re.compile(r'/Vacancies/(\d+)/Description/(\d+)')
# The vendor's own marketing site, served with HTTP 200 on an unallocated tenant.
VENDOR = re.compile(r'Abacus\s+Umantis|HR-Suite', re.I)
# The listing widget used by tenants that render their rows client-side.
CONNECTOR = re.compile(r'connectortable|PageName:\s*"Overview"', re.I)
# Segments probed when the listing cannot supply one.
PROBE = (1, 2, 3, 4, 5)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def fetch(url):
    """Return (status, body). A 403 is an answer here, not a failure."""
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=45)
        return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach {urllib.parse.urlsplit(url).netloc}: {e}")


def page_title(markup):
    m = re.search(r"(?is)<title>(.*?)</title>", markup)
    return html.unescape(m.group(1)).strip() if m else ""


def is_shell(title):
    """True when the vacancy slot of the title is empty.

    A wrong segment answers 200 with the tenant's chrome and nothing in front
    of the separator — '  | Applicant Management' on one tenant, '  |
    eRecruiting Swiss TPH' on another. What follows the pipe is per-tenant and
    localised; what is stable is that nothing precedes it.
    """
    return not title or title.startswith("|")


def to_text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", html.unescape(markup)).strip()


def listing(host):
    url = f"https://{host}/Jobs"
    status, body = fetch(url)
    if status != 200:
        die(f"{host} answered HTTP {status} on /Jobs. Check the host: umantis "
            f"sites live at recruitingapp-<n>.umantis.com or on the employer's "
            f"own domain.", code=4)
    if VENDOR.search(page_title(body)):
        die(f"{host} served the umantis vendor's own marketing page, not an "
            f"employer board. An unallocated tenant number answers HTTP 200 "
            f"with that page — this is a wrong host, not an employer with no "
            f"openings.", code=4)
    return url, body


def vacancies(body):
    """[(id, segment)] in listing order, de-duplicated, first segment wins."""
    seen, out = set(), []
    for vid, seg in VACANCY.findall(body):
        if vid not in seen:
            seen.add(vid)
            out.append((vid, seg))
    return out


def title_near(body, vid):
    """The anchor text of the link to <vid>, which is the vacancy title."""
    m = re.search(
        r'(?is)<a[^>]+/Vacancies/%s/Description/\d+[^>]*>(.*?)</a>' % vid, body)
    return to_text(m.group(1)) if m else None


def row(host, vid, seg, title):
    return {
        "id": vid,
        "ledger_id": f"umantis:{host}:{vid}",
        "url": f"https://{host}/Vacancies/{vid}/Description/{seg}",
        "segment": seg,
        "title": title,
        "host": host,
        "provider": "umantis",
    }


# ---------------------------------------------------------------- commands --

def cmd_list(a):
    _v = robots_verdict(a.host)
    if not _v["sweep"]:
        die(f"{_v['host']}: {_v['reason']} On umantis the host belongs to the employer, so this is that employer's "
            f"answer and not the platform's. Issue #73.",
                8 if _v["sweep"] is None else 7)
    url, body = listing(a.host)
    found = vacancies(body)
    if not found:
        if CONNECTOR.search(body):
            die(f"{a.host} renders its listing client-side — the rows arrive "
                f"from a widget, and /Jobs carries none of them in its HTML. "
                f"This is NOT an empty board: read it in the browser, or reach "
                f"a vacancy directly if you already have its id.", code=5)
        die(f"{a.host} served /Jobs with no vacancy links and no sign of a "
            f"client-rendered widget. Report the board rather than concluding "
            f"they are not hiring.", code=5)
    kept = 0
    for vid, seg in found:
        title = title_near(body, vid) or ""
        if a.search and a.search.lower() not in title.lower():
            continue
        print(json.dumps(row(a.host, vid, seg, title), ensure_ascii=False))
        kept += 1
    note = f"[umantis] {kept} of {len(found)} vacancies on {a.host}"
    if a.search and not kept:
        note += (f" — the board is not empty; every vacancy was filtered out by "
                 f"--search {a.search!r}. Titles only: this board carries no "
                 f"server-side search.")
    print(note, file=sys.stderr)


def resolve_segment(host, vid, given):
    """Return (segment, status, title, body) for the vacancy's real page."""
    if given:
        status, body = fetch(f"https://{host}/Vacancies/{vid}/Description/{given}")
        return given, status, page_title(body), body
    # The listing is authoritative and costs one request.
    try:
        _, jobs = listing(host)
        for lid, seg in vacancies(jobs):
            if lid == vid:
                status, body = fetch(
                    f"https://{host}/Vacancies/{vid}/Description/{seg}")
                if status == 200 and not is_shell(page_title(body)):
                    return seg, status, page_title(body), body
    except SystemExit:
        pass  # a client-rendered listing is not a reason to give up on one ad
    last = (None, None, "", "")
    for seg in PROBE:
        status, body = fetch(f"https://{host}/Vacancies/{vid}/Description/{seg}")
        title = page_title(body)
        if status == 403:
            return str(seg), 403, "", ""
        if status == 200 and not is_shell(title):
            return str(seg), 200, title, body
        last = (str(seg), status, title, body)
    return last


def cmd_ad(a):
    _v = robots_verdict(a.host)
    if not _v["sweep"]:
        die(f"{_v['host']}: {_v['reason']} On umantis the host belongs to the employer, so this is that employer's "
            f"answer and not the platform's — and it refuses the content, not just the sweep. Issue #73.",
                8 if _v["sweep"] is None else 7)
    seg, status, title, body = resolve_segment(a.host, a.id, a.segment)
    if status == 403:
        die(f"vacancy {a.id} on {a.host} answers HTTP 403 — closed, withdrawn, "
            f"or never existed. That is an answer, not a network problem.",
            code=3)
    if status != 200:
        die(f"vacancy {a.id} on {a.host} answered HTTP {status}", code=4)
    if is_shell(title):
        die(f"vacancy {a.id} answered 200 but with the tenant's chrome and an "
            f"empty title slot, on every segment tried "
            f"({', '.join(str(s) for s in PROBE)}). The segment is per-vacancy: "
            f"run `list` and use the one the listing publishes.", code=5)
    out = row(a.host, a.id, seg, title)
    out["description"] = to_text(body)
    print(json.dumps(out, ensure_ascii=False))


def cmd_check(a):
    """Answer step 1b: is this ad still open?"""
    _v = robots_verdict(a.host)
    if not _v["sweep"]:
        die(f"{_v['host']}: {_v['reason']} On umantis the host belongs to the employer, so this is that employer's "
            f"answer and not the platform's — and it refuses the content, not just the sweep. Issue #73.",
                8 if _v["sweep"] is None else 7)
    seg, status, title, _ = resolve_segment(a.host, a.id, a.segment)
    if status == 403:
        verdict, why = "closed", "HTTP 403 — the ATS stopped serving it"
    elif status == 200 and not is_shell(title):
        verdict, why = "open", f"HTTP 200 with the job title in <title>"
    elif status == 200:
        verdict, why = ("unverified",
                        "HTTP 200 but the title slot is empty on every segment "
                        "tried — the segment is per-vacancy, so this is a "
                        "wrong URL, not evidence the ad closed")
    else:
        verdict, why = "unverified", f"HTTP {status}"
    print(json.dumps({"id": a.id, "host": a.host, "segment": seg,
                      "verdict": verdict, "title": title, "why": why,
                      "url": f"https://{a.host}/Vacancies/{a.id}/Description/{seg}"},
                     ensure_ascii=False))
    sys.exit(0 if verdict == "open" else 1)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def host_arg(sp):
        sp.add_argument("--host", required=True,
                        help="recruitingapp-<n>.umantis.com, or the employer's "
                             "own domain (jobs.<employer>.com)")

    li = sub.add_parser("list", help="list this employer's open vacancies")
    host_arg(li)
    li.add_argument("--search", help="filter on the title, locally — this board "
                                     "has no server-side search")
    li.set_defaults(fn=cmd_list)

    ad = sub.add_parser("ad", help="read one vacancy in full")
    host_arg(ad)
    ad.add_argument("--id", required=True, help="the numeric vacancy id")
    ad.add_argument("--segment", help="the trailing Description segment. Omit "
                                      "it and the listing is consulted; it is "
                                      "per-vacancy and must never be guessed")
    ad.set_defaults(fn=cmd_ad)

    ck = sub.add_parser("check", help="is this vacancy still open? (step 1b)")
    host_arg(ck)
    ck.add_argument("--id", required=True)
    ck.add_argument("--segment")
    ck.set_defaults(fn=cmd_check)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
