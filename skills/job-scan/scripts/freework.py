#!/usr/bin/env python3
"""Read free-work.com — French IT roles, permanent and contract, with pay.

A real multi-employer board: one public JSON API, no key, no cookie, no browser.

    GET https://www.free-work.com/api/job_postings

`robots.txt` is among the most permissive this plugin reads: it disallows only
/login, /logout and /fw-deals, and explicitly allows OAI-SearchBot.

Two things make it worth sweeping:

  * **pay on a large share of ads**, in two shapes — `minAnnualSalary`/`max`
    for permanent roles and `minDailySalary`/`max` for contract work. Free-Work
    is the ex-Freelance-Info, so the daily rate is first-class here, and no
    other adapter in this plugin carries one at all;
  * **`expiredAt` on every ad** — a real expiry date, which `cover-letter`
    step 1b has to infer almost everywhere else.

Usage:
  freework.py list [--search laravel] [--contract permanent|contractor|fixed-term]
                   [--remote] [--locality Paris] [--posted-within-days 30]
                   [--pages 5] [--with-description]
  freework.py ad    --slug <slug>
  freework.py check --slug <slug>
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _robots import allowed as robots_allowed

from _ua import UA
API = "https://www.free-work.com/api/job_postings"
SITE = "https://www.free-work.com"
PAGE_SIZE = 30
CONTRACTS = ("permanent", "contractor", "fixed-term", "apprenticeship", "internship")


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
        print(f"[freework] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts. A platform that has "
              f"been renamed reaches an adapter this way before it reaches it "
              f"as a rename.", file=__import__("sys").stderr)
    return a



def get_json(url):
    _robots_gate(url, 'freework')
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={
                "User-Agent": UA, "Accept": "application/json"}), timeout=60)
        return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        die(f"{url} returned HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach {urllib.parse.urlparse(url).netloc}: {e}")


def fold(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def to_text(markup):
    if not markup:
        return None
    t = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    t = re.sub(r"(?i)</p>", "\n\n", t)
    t = re.sub(r"(?i)</li>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    return "\n".join(l.rstrip() for l in t.splitlines()).strip()


def fetch_page(params: dict) -> list:
    d = get_json(f"{API}?{urllib.parse.urlencode(params)}")
    if d is None:
        die("the endpoint answered 404 — its shape changed", code=2)
    if not isinstance(d, list):
        # An error is returned as a JSON object, not a list. The one seen in
        # practice: passing contracts as an array (`contracts[]=permanent`)
        # answers "Input value contracts contains a non-scalar value".
        detail = d.get("detail") if isinstance(d, dict) else str(d)[:200]
        die(f"the API refused the request: {detail}", code=2)
    return d


def sweep(params: dict, max_pages: int) -> list:
    """Page until the board stops giving anything new.

    **The page number cannot be trusted to run out.** Past a ceiling the API
    keeps answering 200 with the *same* final page forever — pages 400 and 800
    were measured returning an identical set of 13 ads. An adapter that stops
    only on an empty page never stops.

    So the loop ends on the first page that adds no unseen id, and dedupes on
    the way.
    """
    seen, out = set(), []
    for page in range(1, max_pages + 1):
        rows = fetch_page({**params, "page": page})
        fresh = [j for j in rows if j.get("id") not in seen]
        if not fresh:
            break
        seen.update(j["id"] for j in fresh)
        out.extend(fresh)
        if len(rows) < PAGE_SIZE:
            break
    return out


def row(j, with_description=False):
    loc = j.get("location") or {}
    company = j.get("company") or {}
    where = [loc.get("postalCode"), loc.get("locality")]
    out = {
        "id": j.get("slug"),
        "ledger_id": f"freework:{j.get('slug')}",
        # The slug is the key: /api/job_postings/<numeric id> answers 404, only
        # the slug resolves. The numeric id is kept for reference, not for use.
        "numeric_id": j.get("id"),
        "url": f"{SITE}/fr/tech-it/jobs/{j.get('slug')}",
        "apply_url": j.get("applicationUrl") or f"{SITE}/fr/tech-it/jobs/{j.get('slug')}",
        "title": j.get("title"),
        "company": company.get("name"),
        "location": " ".join(x for x in where if x) or None,
        # Street, postcode and town when the employer filled them — the fields
        # the job-room-ch module records as most often missing from a PRE.
        "address": {k: v for k, v in (("street", loc.get("street")),
                                      ("postal_code", loc.get("postalCode")),
                                      ("locality", loc.get("locality")),
                                      ("region", loc.get("adminLevel1"))) if v} or None,
        "published": j.get("publishedAt"),
        "updated": j.get("updatedAt"),
        # A real expiry date, on every ad. cover-letter step 1b can read it
        # instead of inferring staleness from age.
        "expires": j.get("expiredAt"),
        "contracts": j.get("contracts") or [],
        "remote_mode": j.get("remoteMode"),
        "remote": j.get("remoteMode") == "full",
        "experience_level": j.get("experienceLevel"),
        "starts_at": j.get("startsAt"),
        "duration": (f"{j['durationValue']} {j['durationPeriod']}"
                     if j.get("durationValue") and j.get("durationPeriod") else None),
        "currency": j.get("currency"),
        # Two pay shapes, and they mean different things. An annual figure is a
        # salary; a daily figure is a contractor rate billed by the day. Never
        # compare or merge them.
        "annual_salary_min": j.get("minAnnualSalary"),
        "annual_salary_max": j.get("maxAnnualSalary"),
        "daily_rate_min": j.get("minDailySalary"),
        "daily_rate_max": j.get("maxDailySalary"),
        "skills": [s.get("name") for s in (j.get("skills") or []) if isinstance(s, dict)],
        # An ad the board itself republished from elsewhere. Worth knowing
        # before treating it as a first-hand posting.
        "external": bool(j.get("external")),
        "external_source": j.get("externalSource"),
    }
    if with_description:
        out["description"] = to_text(j.get("description"))
    return out


def keep(j, a):
    if a.remote and j.get("remoteMode") != "full":
        return False
    if a.locality and fold(a.locality) not in fold((j.get("location") or {}).get("locality")):
        return False
    if a.posted_within_days:
        raw = (j.get("publishedAt") or "")[:10]
        try:
            age = (dt.date.today() - dt.date.fromisoformat(raw)).days
        except ValueError:
            return False
        if age > a.posted_within_days:
            return False
    return True


def cmd_list(a):
    params = {}
    if a.search:
        # `searchKeywords` is the ONLY keyword parameter that filters. `query`,
        # `search`, `q` and `skills` are accepted and silently ignored — the
        # board answers 200 with the unfiltered feed, which reads exactly like
        # a search that matched everything.
        params["searchKeywords"] = a.search
    if a.contract:
        # Scalar, never an array: `contracts[]=permanent` is rejected outright.
        params["contracts"] = a.contract

    rows = sweep(params, a.pages)
    kept = [j for j in rows if keep(j, a)]

    print(f"[free-work] {len(kept)} of {len(rows)} postings kept "
          f"({a.pages} page(s) requested, {PAGE_SIZE}/page)", file=sys.stderr)
    if len(rows) >= a.pages * PAGE_SIZE:
        print("  that is the page budget, not the end of the board — raise "
              "--pages or narrow --search rather than reading this as the "
              "whole market.", file=sys.stderr)
    for j in kept:
        print(json.dumps(row(j, a.with_description), ensure_ascii=False))
    return 0


def cmd_ad(a):
    j = get_json(f"{API}/{urllib.parse.quote(a.slug)}")
    if j is None:
        die(f"no posting with slug {a.slug!r} — it was filled or pulled. "
            "Record it as discarded.", code=3)
    print(json.dumps(row(j, with_description=True), ensure_ascii=False, indent=1))
    return 0


def cmd_check(a):
    j = get_json(f"{API}/{urllib.parse.quote(a.slug)}")
    if j is None:
        verdict, why = "closed", "the API answers 404 for this slug"
    elif not j.get("published") or j.get("status") != "published":
        verdict, why = "unpublished", f"status={j.get('status')!r}, published={j.get('published')!r}"
    else:
        exp = (j.get("expiredAt") or "")[:10]
        try:
            gone = exp and dt.date.fromisoformat(exp) < dt.date.today()
        except ValueError:
            gone = False
        verdict = "expired" if gone else "open"
        why = (f"expiredAt {exp} is in the past" if gone
               else f"published, expiredAt {exp or 'not set'}")
    print(json.dumps({"slug": a.slug, "verdict": verdict, "why": why,
                      "url": f"{SITE}/fr/tech-it/jobs/{a.slug}"}, ensure_ascii=False))
    return 0 if verdict == "open" else 3


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="sweep the board")
    li.add_argument("--search", help="keywords (maps to searchKeywords)")
    li.add_argument("--contract", choices=CONTRACTS)
    li.add_argument("--remote", action="store_true", help="keep remoteMode=full only")
    li.add_argument("--locality", help="substring of the town")
    li.add_argument("--posted-within-days", type=int)
    li.add_argument("--pages", type=int, default=5,
                    help="page budget (default 5 = up to 150 ads)")
    li.add_argument("--with-description", action="store_true")

    ad = sub.add_parser("ad", help="one posting in full")
    ad.add_argument("--slug", required=True)

    ck = sub.add_parser("check", help="is this posting still live?")
    ck.add_argument("--slug", required=True)

    a = p.parse_args()
    return {"list": cmd_list, "ad": cmd_ad, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
