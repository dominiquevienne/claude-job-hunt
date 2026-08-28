#!/usr/bin/env python3
"""Read Michael Page, the recruitment agency's own board.

Unlike the ATS adapters, this IS a board: one search across many employers. But
it is an agency board, and that changes what comes back — the hiring employer is
described and never named. See --help of `list`.

Country-scoped, like Indeed: www.michaelpage.ch, .fr, .de, .co.uk … A job
reference is served ONLY by the domain that published it, so the domain is part
of the ledger key.

Server-rendered HTML, and every ad carries a schema.org JobPosting block, so the
extraction does not depend on CSS selectors.

Usage:
  michaelpage.py list  --domain www.michaelpage.ch [--search developer]
                       [--location Lausanne] [--pages 3] [--with-description]
  michaelpage.py ad    --domain www.michaelpage.ch --ref jn-072026-7075230
  michaelpage.py check --domain www.michaelpage.ch --ref jn-072026-7075230
"""

import argparse
import html as htmlmod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

REF = re.compile(r'/ref/(jn-\d{6}-\d+)', re.I)
LD = re.compile(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', re.S | re.I)
PAGE_HINT = 30      # observed on .ch and .de; .fr served 20 and .co.uk 17


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def fetch(url):
    """Return (status, body). 404 is an answer here: end of results, or a dead ad."""
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=45)
        return r.getcode(), r.read().decode("utf8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach {urllib.parse.urlsplit(url).netloc}: {e}")


def to_text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", htmlmod.unescape(markup)).strip()


def job_posting(body):
    """The schema.org JobPosting, or None.

    strict=False is REQUIRED, not defensive: every ad sampled embeds literal
    newlines inside JSON strings, which is invalid JSON. A strict parser — the
    default in most languages — rejects the whole block and sees no ad at all.
    """
    for block in LD.findall(body):
        try:
            data = json.loads(block, strict=False)
        except ValueError:
            continue
        for obj in (data if isinstance(data, list) else [data]):
            if isinstance(obj, dict) and obj.get("@type") == "JobPosting":
                return obj
    return None


def card(domain, ref, posting, title_hint=None, with_description=False):
    addr = ((posting or {}).get("jobLocation") or {}).get("address") or {}
    salary = (posting or {}).get("baseSalary") or {}
    value = salary.get("value") or {}
    # baseSalary is present on every ad and hollow on every ad sampled:
    # currency "" and min/max "". Emit a figure only if one is actually there.
    has_salary = bool(salary.get("currency")) and bool(
        value.get("minValue") or value.get("maxValue"))
    out = {
        "id": ref,
        "ledger_id": f"michaelpage:{domain}:{ref}",
        "url": f"https://{domain}/job-detail/ref/{ref}",
        "title": (posting or {}).get("title") or title_hint,
        # The agency is the hiringOrganization on every ad. The employer is
        # DESCRIBED in the body ("About Our Client") and never named.
        "company": None,
        "employer_named": False,
        "agency": "Michael Page",
        "domain": domain,
        "provider": "michaelpage",
        "location": addr.get("addressLocality"),
        "region": addr.get("addressRegion"),
        "country": addr.get("addressCountry"),
        "published": (posting or {}).get("datePosted"),
        "employment_type": (posting or {}).get("employmentType"),
        "industry": (posting or {}).get("industry"),
        "remote": (posting or {}).get("jobLocationType") == "TELECOMMUTE",
        "salary": (f"{value.get('minValue')}-{value.get('maxValue')} "
                   f"{salary.get('currency')}" if has_salary else None),
    }
    if with_description:
        out["description"] = to_text((posting or {}).get("description"))
    return out


def read_ad(domain, ref):
    status, body = fetch(f"https://{domain}/job-detail/ref/{ref}")
    return status, (job_posting(body) if status == 200 else None)


# ---------------------------------------------------------------- commands --

def cmd_list(a):
    seen, rows = [], []
    for page in range(a.pages):
        qs = {}
        if a.search:
            qs["search"] = a.search
        if a.location:
            qs["location"] = a.location
        if page:
            qs["page"] = page
        url = f"https://{a.domain}/jobs" + ("?" + urllib.parse.urlencode(qs) if qs else "")
        status, body = fetch(url)
        if status == 404:
            # Paging past the last page is a 404, not an empty page — that is the
            # end-of-results signal. On page 0 it is AMBIGUOUS: a search with no
            # match answers 404 too (?search=zzzqqqxyz, ?location=Zzzqqq). The
            # bare /jobs settles it in one request.
            if page == 0:
                bare, _ = fetch(f"https://{a.domain}/jobs")
                if bare == 200:
                    print(f"[michaelpage:{a.domain}] no ad matched. On this "
                          f"board a zero-result search answers HTTP 404, not an "
                          f"empty page — the domain is fine (bare /jobs answers "
                          f"200), so this is a real zero, not a failure.",
                          file=sys.stderr)
                    return
                die(f"{a.domain} answered HTTP 404 on /jobs, and so did the "
                    f"unfiltered /jobs. Check the domain: Michael Page is "
                    f"country-scoped (www.michaelpage.ch, .fr, .de, .co.uk …).",
                    code=4)
            break
        if status != 200:
            die(f"{a.domain} answered HTTP {status} on /jobs", code=4)
        refs = list(dict.fromkeys(m.lower() for m in REF.findall(body)))
        if not refs:
            break
        fresh = [r for r in refs if r not in seen]
        # Pages overlap: a location=Lausanne run returned 12 refs on page 1 of
        # which only 9 were new. Dedupe on the reference, never on position.
        seen.extend(fresh)
        for ref in fresh:
            posting = None
            if a.with_description or not a.titles_from_listing:
                _, posting = read_ad(a.domain, ref)
            rows.append(card(a.domain, ref, posting,
                             with_description=a.with_description))
        if len(refs) < 5:      # a short page is the last one
            break
    for row in rows:
        print(json.dumps(row, ensure_ascii=False))
    print(f"[michaelpage:{a.domain}] {len(rows)} ads over {a.pages} page(s) at "
          f"most. There is no result total on the page — raise --pages to go "
          f"further, and never report a count as the size of the board.",
          file=sys.stderr)


def cmd_ad(a):
    status, posting = read_ad(a.domain, a.ref)
    if status == 404:
        die(f"no ad {a.ref} on {a.domain} (HTTP 404) — it was filled or pulled, "
            f"or the reference belongs to another country's domain: references "
            f"are NOT shared between them. Record it as discarded.", code=3)
    if status != 200:
        die(f"{a.domain} answered HTTP {status} for {a.ref}", code=4)
    if posting is None:
        die(f"ad {a.ref} answered 200 but carries no schema.org JobPosting. "
            f"That is a page-shape change, not a dead ad — report it with the "
            f"board-request skill rather than treating it as closed.", code=5)
    print(json.dumps(card(a.domain, a.ref, posting, with_description=True),
                     ensure_ascii=False, indent=1))


def cmd_check(a):
    """Answer cover-letter step 1b: is this ad still open?"""
    status, posting = read_ad(a.domain, a.ref)
    if status == 404:
        verdict, why = ("closed",
                        "HTTP 404 — this domain stopped serving it. Confirm the "
                        "domain first: a reference published by another "
                        "country's Michael Page answers 404 here while being "
                        "perfectly alive there, and the two are indistinguishable")
    elif status == 200 and posting:
        verdict, why = "open", "HTTP 200 with a schema.org JobPosting"
    elif status == 200:
        verdict, why = ("unverified",
                        "HTTP 200 but no JobPosting block — a page-shape change, "
                        "not evidence the ad closed")
    else:
        verdict, why = "unverified", f"HTTP {status}"
    print(json.dumps({"ref": a.ref, "domain": a.domain, "verdict": verdict,
                      "why": why, "title": (posting or {}).get("title"),
                      "url": f"https://{a.domain}/job-detail/ref/{a.ref}"},
                     ensure_ascii=False))
    sys.exit(0 if verdict == "open" else 1)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def dom(sp):
        sp.add_argument("--domain", required=True,
                        help="www.michaelpage.ch, .fr, .de, .co.uk … No default: "
                             "guessing the country searches the wrong market")

    li = sub.add_parser("list", help="search the board")
    dom(li)
    li.add_argument("--search", help="free text, matched by the site")
    li.add_argument("--location", help="town or region, as the site spells it")
    li.add_argument("--pages", type=int, default=2,
                    help=f"pages to read, ~{PAGE_HINT} ads each on .ch (fewer on "
                         f"other domains). Default 2")
    li.add_argument("--with-description", action="store_true",
                    help="costs one extra request per ad")
    li.add_argument("--titles-from-listing", action="store_true",
                    help="skip the per-ad request; ids only, no title or location")
    li.set_defaults(fn=cmd_list)

    ad = sub.add_parser("ad", help="read one ad in full")
    dom(ad)
    ad.add_argument("--ref", required=True, help="e.g. jn-072026-7075230")
    ad.set_defaults(fn=cmd_ad)

    ck = sub.add_parser("check", help="is this ad still open? (step 1b)")
    dom(ck)
    ck.add_argument("--ref", required=True)
    ck.set_defaults(fn=cmd_check)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
