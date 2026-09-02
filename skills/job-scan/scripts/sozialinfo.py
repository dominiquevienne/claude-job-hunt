#!/usr/bin/env python3
"""Read sozialinfo.ch, Switzerland's job portal for the social sector.

**A real multi-employer board, and the only one here that names the employer.**
26 distinct employers across 27 ads sampled, and every ad's JobPosting block
carries the hiring organisation with a `sameAs` link to its own website — so the
ledger's employer dedup actually works on this board, unlike every agency board
in `shared/boards/`.

Server-rendered HTML. **No key, no cookie, no browser.**

Pagination is CUMULATIVE: `?page=N` returns pages 1..N in one response, so the
whole board arrives in a single request — `--pages 24` returned all 708 ads the
site states, in one fetch.

Usage:
  sozialinfo.py list  [--pages 24] [--search sozialpädagog] [--place Zürich]
  sozialinfo.py ad    --token TA94iHqG
  sozialinfo.py check --token TA94iHqG
"""

import argparse
import html as htmlmod
import json
import re

from _ldjson import one, postings
import sys
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
BASE = "https://www.sozialinfo.ch/arbeitsmarkt/stellenportal"
# The links are RELATIVE and the trailing token is MIXED CASE. A lowercase-only
# pattern finds nothing and reads as an empty board.
LINK = re.compile(r'href="/arbeitsmarkt/stellenportal/([A-Za-z0-9-]+)/"')
ARTICLE = re.compile(r'<article class="h-full @container">(.*?)</article>', re.S)
TOKEN = re.compile(r"-([A-Za-z0-9]{6,})$")
STATED = re.compile(r"(\d[\d' ]{0,6})\s*(?:Stellen|Angebote)", re.I)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def get(url):
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120)
        return r.getcode(), r.read().decode("utf8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach www.sozialinfo.ch: {e}")


def to_text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", htmlmod.unescape(markup)).strip()


def job_posting(body):
    """The ad's own JobPosting block, or None. Also the open/closed test."""
    # One reader for every board's ld+json: tolerant of the quote style
    # on the script tag, and strict=False on the parse. Issue #76.
    return next(iter(postings(body)), None)


def cards(body):
    """The listing card carries everything needed to score, in order:
    date, title, employer, postcode + town, workload, category."""
    out = []
    clean = re.sub(r"<!--\[?\]?-->", "", body)
    for chunk in ARTICLE.findall(clean):
        slugs = LINK.findall(chunk)
        if not slugs:
            continue
        slug = slugs[0]
        m = TOKEN.search(slug)
        parts = [p for p in re.sub(r"(?s)<[^>]+>", "|", chunk).split("|")
                 if p.strip()]
        parts = [re.sub(r"\s+", " ", htmlmod.unescape(p)).strip()
                 for p in parts]
        out.append({
            "token": m.group(1) if m else slug,
            "slug": slug,
            "published": parts[0] if parts else None,
            "title": parts[1] if len(parts) > 1 else None,
            # The employer, named. This is what makes the board worth having.
            "company": parts[2] if len(parts) > 2 else None,
            "location": parts[3] if len(parts) > 3 else None,
            "workload": parts[4] if len(parts) > 4 else None,
            "category": parts[5] if len(parts) > 5 else None,
        })
    return out


def row(c, description=None):
    out = {
        # The token alone rebuilds the URL — /stellenportal/<token>/ answers 200.
        "id": c["token"],
        "ledger_id": f"sozialinfo:{c['token']}",
        "url": f"{BASE}/{c['token']}/",
        "title": c.get("title"),
        "company": c.get("company"),
        "employer_named": bool(c.get("company")),
        "provider": "sozialinfo",
        "location": c.get("location"),
        "workload": c.get("workload"),
        "category": c.get("category"),
        "published": c.get("published"),
    }
    if description is not None:
        out["description"] = description
    return out


# ---------------------------------------------------------------- commands --

def cmd_list(a):
    url = f"{BASE}?page={a.pages}" if a.pages > 1 else BASE
    status, body = get(url)
    if status != 200:
        die(f"sozialinfo answered HTTP {status} on the job portal", code=4)
    rows = cards(body)
    if not rows:
        die("the portal served no cards. The listing ships every ad in its "
            "markup, so zero cards is a page-shape change, not an empty board "
            "— report it with the board-request skill.", code=5)
    m = STATED.search(to_text(body))
    stated = int(re.sub(r"\D", "", m.group(1))) if m else None
    kept = 0
    for c in rows:
        hay = " ".join(str(c.get(k) or "") for k in
                       ("title", "company", "category")).lower()
        if a.search and a.search.lower() not in hay:
            continue
        if a.place and a.place.lower() not in (c.get("location") or "").lower():
            continue
        desc = None
        if a.with_description:
            st, b = get(f"{BASE}/{c['token']}/")
            j = job_posting(b) if st == 200 else None
            desc = to_text((j or {}).get("description"))
        print(json.dumps(row(c, desc), ensure_ascii=False))
        kept += 1
    note = f"[sozialinfo] {kept} emitted, {len(rows)} read"
    if stated:
        note += f", board states {stated}"
        if len(rows) < stated:
            note += (f" — {stated - len(rows)} short. Pagination is cumulative: "
                     f"raise --pages until the two agree (24 covered the whole "
                     f"board when this was written) and never report this count "
                     f"as the size of the board while they differ")
        else:
            note += " (complete)"
    print(note, file=sys.stderr)
    if (a.search or a.place) and not kept:
        print(f"[sozialinfo] the board is not empty — all {len(rows)} ads were "
              f"filtered out.", file=sys.stderr)


def cmd_ad(a):
    status, body = get(f"{BASE}/{a.token}/")
    if status != 200:
        die(f"sozialinfo answered HTTP {status} for {a.token}", code=4)
    j = job_posting(body)
    if not j:
        die(f"ad {a.token} answered 200 but carries no JobPosting block — an "
            f"unknown token answers exactly this way, with an empty <title>. "
            f"Record it as discarded.", code=3)
    org = j.get("hiringOrganization") or {}
    addr = one(j.get("jobLocation")).get("address") or {}
    print(json.dumps({
        "id": a.token,
        "ledger_id": f"sozialinfo:{a.token}",
        "url": f"{BASE}/{a.token}/",
        "title": j.get("title"),
        "company": org.get("name"),
        "employer_named": bool(org.get("name")),
        "employer_site": org.get("sameAs"),
        "provider": "sozialinfo",
        # "8006 Zürich", the shape the ORP form wants — not "8006, Zürich".
        "location": " ".join(x for x in (addr.get("postalCode"),
                                         addr.get("addressLocality")) if x) or None,
        "region": addr.get("addressRegion"),
        "published": j.get("datePosted"),
        "valid_through": j.get("validThrough"),
        "employment_type": j.get("employmentType"),
        "description": to_text(j.get("description")),
    }, ensure_ascii=False, indent=1))


def cmd_check(a):
    """Answer step 1b. An unknown token answers 200, so the status is no test."""
    status, body = get(f"{BASE}/{a.token}/")
    j = job_posting(body) if status == 200 else None
    if status != 200:
        verdict, why = "unverified", f"HTTP {status}"
    elif j:
        verdict, why = "open", "HTTP 200 with a JobPosting block"
    else:
        verdict, why = ("closed",
                        "HTTP 200 but no JobPosting block and an empty <title> "
                        "— this token does not resolve. The status code is not "
                        "a test on this board: an unknown token answers 200 too")
    print(json.dumps({"token": a.token, "verdict": verdict, "why": why,
                      "title": (j or {}).get("title"),
                      "valid_through": (j or {}).get("validThrough"),
                      "url": f"{BASE}/{a.token}/"}, ensure_ascii=False))
    sys.exit(0 if verdict == "open" else 1)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="the board; pagination is cumulative")
    li.add_argument("--pages", type=int, default=24,
                    help="?page=N returns pages 1..N in ONE response. 24 covers "
                         "the whole board; 1 gives the newest 30")
    li.add_argument("--search", help="matched on title, employer and category")
    li.add_argument("--place", help="substring of the '<postcode> <town>' field")
    li.add_argument("--with-description", action="store_true",
                    help="costs one extra request per kept ad")
    li.set_defaults(fn=cmd_list)

    ad = sub.add_parser("ad", help="read one ad in full")
    ad.add_argument("--token", required=True, help="e.g. TA94iHqG")
    ad.set_defaults(fn=cmd_ad)

    ck = sub.add_parser("check", help="is this ad still open? (step 1b)")
    ck.add_argument("--token", required=True)
    ck.set_defaults(fn=cmd_check)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
