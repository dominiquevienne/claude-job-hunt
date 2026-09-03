#!/usr/bin/env python3
"""Read randstad.ch, the staffing agency's Swiss board.

An AGENCY board, like michaelpage.md, fachkraft.md and persigo.md:
`hiringOrganization` is Randstad on every ad and **the client employer is never
named**.

**Pagination is a PATH segment, not a query parameter** — `/jobs/page-2/`, not
`/jobs/?page=2`. That distinction is the whole reason this board went unbuilt
until now: `?page=2` returns page 1 verbatim, which reads as "there is no
pagination" rather than "wrong mechanism".

And there is no end marker. Past the last page the site **silently serves page 1
again** — no 404, no empty page. The stop condition is therefore "this page is
page 1", which is what `list` uses.

Usage:
  randstad.py list  [--max-pages 40] [--search serrurier] [--place Genf]
                    [--with-detail]
  randstad.py ad    --id aefa6056-8e23-4d6d-b22e-d2b4c9ef9047
  randstad.py check --id aefa6056-8e23-4d6d-b22e-d2b4c9ef9047
"""

import argparse
import html as htmlmod
import json
import re

from _ldjson import one, postings
import sys
import urllib.error
import urllib.parse
import urllib.request

from _robots import allowed as robots_allowed

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
BASE = "https://www.randstad.ch"
# <slug>_<city>_<uuid>. The links are RELATIVE; the id is a UUID, not a number.
CARD = re.compile(r'<a href="/jobs/([^"/]+_([0-9a-f]{8}-[0-9a-f-]{27,}))/"')
# The ad body, for the ads that carry no JobPosting block.
# Bounded by the next locator: an unbounded slice runs into the neighbouring
# sections and returns 17 000 characters of page furniture as "the ad".
DESC = re.compile(r'data-locator-id="jobdetails_description_jobdescription"[^>]*>'
                  r'(.*?)data-locator-id="jobdetails_description_'
                  r'jobdetailsaccordions"', re.S)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def _robots_gate(url, tag, exit_code=7):
    """Ask before fetching — per host and **per path**. Issues #100, #101.

    `verdict()` answers *is this host closed in one block*. **A site that
    refuses its ad path while leaving its root open passes that and refuses
    every advertisement** — `empleate.gob.hn` does exactly that, closing
    `/Vacantes/` to `User-agent: *` with `/` absent.

    It sits **inside the fetch function**, so every request is covered rather
    than the first one, and a refusal **stops the command** with exit 7 and the
    module's own words. **This adapter decides nothing about what a refusal
    means** — deciding is what turns a check into a decoration.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return None
    a = robots_allowed(parts.netloc, parts.path or "/")
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", exit_code)
    if a.get("requested_host") and a["host"] != a["requested_host"]:
        print(f"[randstad] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts. A platform that has "
              f"been renamed reaches an adapter this way before it reaches it "
              f"as a rename.", file=__import__("sys").stderr)
    return a



def get(url):
    _robots_gate(url, 'randstad')
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90)
        return r.getcode(), r.read().decode("utf8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach www.randstad.ch: {e}")


def to_text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?s)<[^>]+>", "|", markup)
    return re.sub(r"\s+", " ", htmlmod.unescape(markup)).strip()


def job_posting(body):
    # One reader for every board's ld+json: tolerant of the quote style
    # on the script tag, and strict=False on the parse. Issue #76.
    return next(iter(postings(body)), None)


def page_url(n):
    return f"{BASE}/jobs/" if n == 1 else f"{BASE}/jobs/page-{n}/"


def cards(body):
    """One card per ad link; the fields follow it as plain text."""
    hits = list(CARD.finditer(body))
    out = []
    for i, m in enumerate(hits):
        # m.end() is still INSIDE the <a> tag — slicing there makes the tag's
        # own class attribute the first "field" and shifts every one after it.
        start = body.find(">", m.end())
        start = m.end() if start < 0 else start + 1
        end = hits[i + 1].start() if i + 1 < len(hits) else start + 4000
        parts = [p.strip() for p in to_text(body[start:end]).split("|")
                 if p.strip()]
        out.append({
            "id": m.group(2),
            "path": m.group(1),
            "title": parts[0] if parts else None,
            "location": parts[1] if len(parts) > 1 else None,
            "contract": parts[2] if len(parts) > 2 else None,
            "teaser": parts[3][:600] if len(parts) > 3 else None,
        })
    # The same ad appears twice per card (title link and button link).
    seen, uniq = set(), []
    for c in out:
        if c["id"] in seen:
            continue
        seen.add(c["id"])
        uniq.append(c)
    return uniq


def row(c, posting=None):
    out = {
        # The UUID alone rebuilds the URL: /jobs/<uuid>/ answers 200.
        "id": c["id"],
        "ledger_id": f"randstad:{c['id']}",
        "url": f"{BASE}/jobs/{c['id']}/",
        "title": c.get("title"),
        # The agency, never the client.
        "company": None,
        "employer_named": False,
        "agency": "Randstad",
        "provider": "randstad",
        "location": c.get("location"),
        "contract": c.get("contract"),
        "teaser": c.get("teaser"),
    }
    if posting is not None:
        out["published"] = posting.get("datePosted")
        out["valid_through"] = posting.get("validThrough")
        out["description"] = re.sub(r"\|+", " ",
                                    to_text(posting.get("description"))).strip()
    return out


# ---------------------------------------------------------------- commands --

def cmd_list(a):
    first = None
    seen, kept, pages_read = set(), 0, 0
    for n in range(1, a.max_pages + 1):
        status, body = get(page_url(n))
        if status != 200:
            die(f"randstad answered HTTP {status} on {page_url(n)}", code=4)
        rows = cards(body)
        ids = {c["id"] for c in rows}
        if not rows:
            break
        if first is None:
            first = ids
        elif ids == first:
            # Past the last page the site serves page 1 again — silently, with
            # HTTP 200 and a full set of cards. This is the only end marker.
            break
        pages_read = n
        for c in rows:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            hay = " ".join(str(c.get(k) or "") for k in
                           ("title", "teaser", "contract")).lower()
            if a.search and a.search.lower() not in hay:
                continue
            if a.place and a.place.lower() not in (c.get("location") or "").lower():
                continue
            posting = None
            if a.with_detail:
                st, b = get(f"{BASE}/jobs/{c['id']}/")
                posting = job_posting(b) if st == 200 else None
            print(json.dumps(row(c, posting), ensure_ascii=False))
            kept += 1
    print(f"[randstad] {kept} emitted, {len(seen)} ads over {pages_read} page(s)"
          + (f"; stopped at --max-pages {a.max_pages}, the board may be larger"
             if pages_read == a.max_pages else ""), file=sys.stderr)
    if (a.search or a.place) and not kept:
        print(f"[randstad] the board is not empty — all {len(seen)} ads were "
              f"filtered out.", file=sys.stderr)


def cmd_ad(a):
    status, body = get(f"{BASE}/jobs/{a.id}/")
    if status == 410:
        die(f"ad {a.id} is gone (HTTP 410 — this board uses 410, not 404). "
            f"Record it as discarded.", code=3)
    if status != 200:
        die(f"randstad answered HTTP {status} for {a.id}", code=4)
    # A JobPosting block is present on some ads and ABSENT on others, and the
    # split follows the region: 8 of 8 German-region ads carried one, 4 of 4
    # Geneva-area ads did not. So its absence is normal, never a verdict.
    j = job_posting(body) or {}
    addr = one(j.get("jobLocation")).get("address") or {}
    description = re.sub(r"\|+", " ", to_text(j.get("description"))).strip()
    if not description:
        # Same container on every ad, and the only route on the ones without
        # structured data.
        m = DESC.search(body)
        description = re.sub(r"\|+", " ", to_text(m.group(1))).strip() if m else ""
    title = j.get("title")
    if not title:
        m = re.search(r"(?is)<title>(.*?)</title>", body)
        # "<Job title> Job in <City>, <Canton> | randstad"
        title = re.split(r"\s+Job in\s+", htmlmod.unescape(m.group(1)).strip())[0] \
            if m else None
    print(json.dumps({
        "id": a.id,
        "ledger_id": f"randstad:{a.id}",
        "url": f"{BASE}/jobs/{a.id}/",
        "title": title,
        "has_jobposting": bool(j),
        "company": None, "employer_named": False, "agency": "Randstad",
        "provider": "randstad",
        "location": " ".join(x for x in (addr.get("postalCode"),
                                         addr.get("addressLocality")) if x) or None,
        "region": addr.get("addressRegion"),
        "published": j.get("datePosted"),
        "valid_through": j.get("validThrough"),
        "employment_type": j.get("employmentType"),
        "description": description or None,
    }, ensure_ascii=False, indent=1))


def cmd_check(a):
    status, body = get(f"{BASE}/jobs/{a.id}/")
    j = job_posting(body) if status == 200 else None
    if status == 410:
        verdict, why = "closed", "HTTP 410 Gone — this board says so explicitly"
    elif status == 200:
        # The 410 is the test. A missing JobPosting block is NOT a signal here:
        # it is absent on every Geneva-area ad sampled and present on every
        # German-region one, so it tracks the region, not the ad's state.
        verdict, why = "open", ("HTTP 200"
                                + (" with a JobPosting block" if j else
                                   " (no JobPosting block — normal on this "
                                   "board's Romandie ads, not a signal)"))
    else:
        verdict, why = "unverified", f"HTTP {status}"
    print(json.dumps({"id": a.id, "verdict": verdict, "why": why,
                      "has_jobposting": bool(j),
                      "title": (j or {}).get("title"),
                      "valid_through": (j or {}).get("validThrough"),
                      "url": f"{BASE}/jobs/{a.id}/"}, ensure_ascii=False))
    sys.exit(0 if verdict == "open" else 1)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="walk /jobs/page-N/ until it repeats page 1")
    li.add_argument("--max-pages", type=int, default=40,
                    help="a safety budget, not the board size: the walk stops "
                         "when a page repeats page 1. 33 pages when measured")
    li.add_argument("--search", help="matched on title, teaser and contract")
    li.add_argument("--place", help="substring of the card's 'City, Canton'")
    li.add_argument("--with-detail", action="store_true",
                    help="fetch each kept ad for its dates and full text — one "
                         "request per ad")
    li.set_defaults(fn=cmd_list)

    ad = sub.add_parser("ad", help="read one ad in full")
    ad.add_argument("--id", required=True, help="the UUID from the ad URL")
    ad.set_defaults(fn=cmd_ad)

    ck = sub.add_parser("check", help="is this ad still open? (step 1b)")
    ck.add_argument("--id", required=True)
    ck.set_defaults(fn=cmd_check)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
