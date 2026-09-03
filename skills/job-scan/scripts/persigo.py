#!/usr/bin/env python3
"""Read persigo.ch, a Swiss staffing agency's board.

An AGENCY board, like michaelpage.md and fachkraft.md: `hiringOrganization` is
Persigo AG on every ad and **the client employer is never named**.

The whole board — 890 ads — arrives in one request, and each listing card
carries the title, town, sector and contract type. **It carries no date**, and
that matters more here than on most boards: see "Age is the only staleness
signal" below.

Server-rendered HTML with a `JobPosting` block on every ad. **No key, no cookie,
no browser.**

Usage:
  persigo.py list  [--search monteur] [--place Horw] [--type Festanstellung]
                   [--with-detail]
  persigo.py ad    --token 00G6LE
  persigo.py check --token 00G6LE
"""

import argparse
import html as htmlmod
import json
import re

from _decode import decode_body
from _ldjson import one, postings
import sys
import urllib.error
import urllib.parse
import urllib.request

from _robots import allowed as robots_allowed

from _ua import UA
BASE = "https://www.persigo.ch/stelle-finden"
ITEM = re.compile(r'<div class="row listitem listitem-([A-Za-z0-9]+)">(.*?)'
                  r'(?=<div class="row listitem |</section|\Z)', re.S)
SHOW = re.compile(r'<a class="show"[^>]*>(.*?)</a>', re.S)
TYPE = re.compile(r'<p class="selectedType">(.*?)</p>', re.S)
STATED = re.compile(r"(\d[\d' ]{0,6})\s*(?:Stellen|Jobs)", re.I)


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
    _robots_gate(url, "persigo")
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90)
        return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach www.persigo.ch: {e}")


def to_text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", htmlmod.unescape(markup)).strip()


def job_posting(body):
    # One reader for every board's ld+json: tolerant of the quote style
    # on the script tag, and strict=False on the parse. Issue #76.
    return next(iter(postings(body)), None)


def cards(body):
    """Each listitem gives: token, title, town, sector, contract type."""
    out = []
    for token, chunk in ITEM.findall(body):
        m = SHOW.search(chunk)
        title = town = None
        if m:
            # <strong>TITLE</strong><br>TOWN
            inner = m.group(1)
            st = re.search(r"<strong>(.*?)</strong>", inner, re.S)
            title = to_text(st.group(1)) if st else None
            town = to_text(re.sub(r"(?s)<strong>.*?</strong>", "", inner)) or None
        t = TYPE.search(chunk)
        # The sector sits in the second column, before selectedType.
        rest = TYPE.sub("", chunk)
        cols = [to_text(c) for c in re.findall(r"<p>(.*?)</p>", rest, re.S)]
        sector = next((c for c in cols[1:] if c), None)
        out.append({"token": token, "title": title, "location": town,
                    "sector": sector,
                    "contract": to_text(t.group(1)) if t else None})
    return out


def row(c, posting=None):
    out = {
        "id": c["token"],
        "ledger_id": f"persigo:{c['token']}",
        "url": f"{BASE}/stelle/{c['token']}/",
        "title": c.get("title"),
        # The agency, never the client. The employer is not named on this board.
        "company": None,
        "employer_named": False,
        "agency": "Persigo AG",
        "provider": "persigo",
        "location": c.get("location"),
        "sector": c.get("sector"),
        "contract": c.get("contract"),
    }
    if posting is not None:
        out["published"] = posting.get("datePosted")
        out["region"] = (one(posting.get("jobLocation"))
                         .get("address") or {}).get("addressRegion")
        out["description"] = to_text(posting.get("description"))
    return out


# ---------------------------------------------------------------- commands --

def cmd_list(a):
    status, body = get(f"{BASE}/")
    if status != 200:
        die(f"persigo answered HTTP {status} on the job list", code=4)
    rows = cards(body)
    if not rows:
        die("persigo served the list with no `listitem` blocks. The whole board "
            "ships in one page, so zero is a page-shape change, not an empty "
            "board — report it with the board-request skill.", code=5)
    m = STATED.search(to_text(body))
    stated = int(re.sub(r"\D", "", m.group(1))) if m else None
    kept = 0
    for c in rows:
        hay = " ".join(str(c.get(k) or "") for k in
                       ("title", "sector")).lower()
        if a.search and a.search.lower() not in hay:
            continue
        if a.place and a.place.lower() not in (c.get("location") or "").lower():
            continue
        if a.type and a.type.lower() not in (c.get("contract") or "").lower():
            continue
        posting = None
        if a.with_detail:
            st, b = get(f"{BASE}/stelle/{c['token']}/")
            posting = job_posting(b) if st == 200 else None
        print(json.dumps(row(c, posting), ensure_ascii=False))
        kept += 1
    note = f"[persigo] {kept} emitted, {len(rows)} read"
    if stated:
        note += f", board states {stated}"
        note += " (complete)" if len(rows) >= stated else f" — {stated - len(rows)} short"
    if not a.with_detail:
        note += (". No posting date: the listing carries none, and this board "
                 "keeps ads a long time — 3 of 14 sampled were over eight "
                 "months old. Use --with-detail before trusting the freshness "
                 "of anything here")
    print(note, file=sys.stderr)
    if (a.search or a.place or a.type) and not kept:
        print(f"[persigo] the board is not empty — all {len(rows)} ads were "
              f"filtered out.", file=sys.stderr)


def cmd_ad(a):
    status, body = get(f"{BASE}/stelle/{a.token}/")
    if status == 404:
        die(f"no ad {a.token} on persigo (HTTP 404) — it was filled or pulled. "
            f"Record it as discarded.", code=3)
    if status != 200:
        die(f"persigo answered HTTP {status} for {a.token}", code=4)
    j = job_posting(body)
    if not j:
        die(f"ad {a.token} answered 200 but carries no JobPosting block. That is "
            f"a page-shape change, not a dead ad — report it with the "
            f"board-request skill rather than treating it as closed.", code=5)
    addr = one(j.get("jobLocation")).get("address") or {}
    print(json.dumps({
        "id": a.token,
        "ledger_id": f"persigo:{a.token}",
        "url": f"{BASE}/stelle/{a.token}/",
        "title": j.get("title"),
        "company": None, "employer_named": False, "agency": "Persigo AG",
        "provider": "persigo",
        # The JSON-LD carries only a region; the LISTING carries the town.
        "region": addr.get("addressRegion"),
        "published": j.get("datePosted"),
        "employment_type": j.get("employmentType"),
        "description": to_text(j.get("description")),
    }, ensure_ascii=False, indent=1))


def cmd_check(a):
    """Answer step 1b. There is no validThrough on this board — age is all."""
    status, body = get(f"{BASE}/stelle/{a.token}/")
    j = job_posting(body) if status == 200 else None
    if status == 404:
        verdict, why = "closed", "HTTP 404 — the board stopped serving it"
    elif j:
        verdict, why = "open", "HTTP 200 with a JobPosting block"
    elif status == 200:
        verdict, why = ("unverified",
                        "HTTP 200 but no JobPosting block — a page-shape change, "
                        "not evidence the ad closed")
    else:
        verdict, why = "unverified", f"HTTP {status}"
    print(json.dumps({
        "token": a.token, "verdict": verdict, "why": why,
        "title": (j or {}).get("title"),
        "published": (j or {}).get("datePosted"),
        # No validThrough anywhere on this board: a listed ad may still be old.
        "valid_through": None,
        "url": f"{BASE}/stelle/{a.token}/"}, ensure_ascii=False))
    sys.exit(0 if verdict == "open" else 1)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="the whole board, in one request")
    li.add_argument("--search", help="matched on title and sector, locally")
    li.add_argument("--place", help="substring of the town on the card")
    li.add_argument("--type", help="e.g. Festanstellung, Temporär")
    li.add_argument("--with-detail", action="store_true",
                    help="fetch each kept ad for its posting date and full text "
                         "— one request per ad, and the only way to know an "
                         "ad's age on this board")
    li.set_defaults(fn=cmd_list)

    ad = sub.add_parser("ad", help="read one ad in full")
    ad.add_argument("--token", required=True, help="e.g. 00G6LE")
    ad.set_defaults(fn=cmd_ad)

    ck = sub.add_parser("check", help="is this ad still open? (step 1b)")
    ck.add_argument("--token", required=True)
    ck.set_defaults(fn=cmd_check)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
