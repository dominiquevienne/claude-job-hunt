#!/usr/bin/env python3
"""ITJobs (`itjobs.pt`) — Portugal's IT board, through its public read-only API; a key is required on every call and is never printed.

  itjobs.py list   [--limit N] [--pages N] [--type ID,…] [--contract ID,…]
  itjobs.py search --query Q [--limit N] [--pages N]
  itjobs.py ad     --id <job id>

THE ROUTE IS THE API THE SITE DOCUMENTS — `https://api.itjobs.pt/job/*.json`
— and the doctrine of 2026-09-04 (#100) applies: on an API host the access
control is the key, not `robots.txt`; the identity is still sent.

  /job/list.json     api_key · limit · page · company · type · contract     -> {total, page, limit, results[]}
  /job/search.json   api_key · q (comma-separated) · limit · page · …       -> {total, page, limit, query, results[]}
  /job/get.json      api_key · id                                            -> the job, or {error: {message}}

THE KEY. `ITJOBS_API_KEY`, from the environment first and then from the
workspace `credentials.env` or `~/.itjobs.env` (`_secrets.get`). **Without it
the adapter says so and exits 7 — it does not ask for one, and it never
prints one.** The site issues read-only keys against an e-mail address at
https://www.itjobs.pt/api ; the key is the user's to obtain.

THE COUNT. Every envelope carries `total` — the site's own figure — and the
adapter prints «n emitted, site states total — equal / k short» after the
walk. On a page the site says «Job not found.» in a 200 body: the adapter
reads `error.message` before anything else, and a readable body is never a
success by itself.

THE RECORD, from the documentation and to be confirmed on the first keyed
run: id · title · body (HTML) · ref · company{id, name, url, slug, address,
phone, email} · salaryMin · salaryMax · workModel · types[] · contracts[] ·
locations[] · country · publishedAt · updatedAt · slug. The advertisement
address is rebuilt from the id and slug. **Written and exercised against a
stub of the documented envelope on 2026-09-13; no live call was made — the
key is absent on this machine, by design.**
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
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _secrets import get as secret_get, missing_note
from _ua import UA

API = "https://api.itjobs.pt"
SITE = "https://www.itjobs.pt"
KEY_VAR = "ITJOBS_API_KEY"
PAGE_SIZE = 50

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[itjobs] {msg}", file=sys.stderr)


def api_key():
    """The key, or a clean exit that says where one goes — never a prompt, never an echo."""
    k = secret_get(KEY_VAR, "itjobs")
    if not k:
        die(missing_note([KEY_VAR], "itjobs", "ITJobs", "www.itjobs.pt/api — a read-only key against an e-mail address"),
            EXIT_REFUSED)
    return k


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace("api.itjobs.pt", own=1.0)


def call(method, params):
    """One API call. The key travels in the request and appears in no message."""
    url = f"{API}/job/{method}.json"
    gate(url)
    _PACE.wait()
    body = urllib.parse.urlencode({**params, "api_key": api_key()}).encode()
    req = urllib.request.Request(wire_url(url), data=body, method="POST", headers={
        "User-Agent": UA, "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def envelope(method, params):
    code, text_ = call(method, params)
    if code != 200:
        die(f"/job/{method}.json: HTTP {code}", EXIT_PARTIAL)
    try:
        d = json.loads(text_)
    except ValueError:
        die(f"/job/{method}.json: not JSON ({len(text_)} characters)", EXIT_PARTIAL)
    if isinstance(d, dict) and isinstance(d.get("error"), dict):
        msg = d["error"].get("message") or "error"
        # the site says «Job not found.» in a 200 body — read before anything else
        die(f"/job/{method}.json: the site says «{msg}»", EXIT_GONE if "not found" in msg.lower() else EXIT_PARTIAL)
    return d


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    """Thousands with a space — the repo's figure style."""
    return f"{n:,}".replace(",", " ")


def ad_url(ident, slug):
    """Rebuilt from the id and slug. **The shape is not confirmed**: the site's
    listing renders its links client-side and no keyed run has been made — the
    first one checks a `url` against the page and corrects this line if needed."""
    return f"{SITE}/oferta/{ident}/{slug}" if slug else f"{SITE}/oferta/{ident}"


def names(items):
    return [x.get("name") for x in (items or []) if isinstance(x, dict) and x.get("name")]


def card(j):
    co = j.get("company") if isinstance(j.get("company"), dict) else {}
    return {"source": "itjobs", "country": j.get("country") or "PT", "ledger_id": f"itjobs:{j.get('id')}",
            "id": j.get("id"), "url": ad_url(j.get("id"), j.get("slug")), "url_shape_confirmed": False,
            "title": (j.get("title") or "").strip() or None, "employer": co.get("name"), "employer_id": j.get("companyId") or co.get("id"),
            "employer_site": co.get("url"), "ref": (j.get("ref") or "").strip() or None,
            "locations": names(j.get("locations")), "types": names(j.get("types")), "contracts": names(j.get("contracts")),
            "work_model": j.get("workModel"),
            # the API states no currency and no period for salaryMin/Max — the documentation's 11000–17000 on
            # a Lisbon job read as EUR a year, and «read as» is not «stated»: the unit is emitted as not stated
            "salary_min": j.get("salaryMin") or None, "salary_max": j.get("salaryMax") or None,
            "salary_currency": None, "salary_unit_stated": False,
            "posted": j.get("publishedAt"), "updated": j.get("updatedAt")}


def walk(method, params, a):
    rows, seen, stated, page = [], set(), None, 1
    while True:
        env = envelope(method, {**params, "limit": PAGE_SIZE, "page": page})
        if stated is None:
            stated = env.get("total")
        results = env.get("results") or []
        if page == 1 and not results:
            if (stated or 0) > 0:
                die(f"/job/{method}.json: the envelope states total {stated} and page 1 carried no result — a reading fault, not a market.", EXIT_PARTIAL)
            note(f"/job/{method}.json: total 0 and no result on page 1 — the site states nothing for this query.")
            break
        new = 0
        for j in results:
            if not j.get("id") or j["id"] in seen:
                continue
            seen.add(j["id"])
            rows.append(card(j))
            new += 1
        if not results or new == 0 or len(results) < PAGE_SIZE:
            break
        if a.pages and page >= a.pages:
            break
        if a.limit and len(rows) >= a.limit:
            break
        page += 1
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    if stated is None:
        note(f"{th(n)} emitted over {page} page(s); the envelope carries no `total` — no second source.")
        return
    truncated = (a.pages and stated > page * PAGE_SIZE) or (a.limit and a.limit < stated)
    if n == stated:
        note(f"{th(n)} emitted, site states {th(stated)} over {page} page(s) — equal.")
    elif truncated:
        note(f"{th(n)} emitted of the {th(stated)} the site states — {page} page(s) walked by request (--pages/--limit), not a shortfall.")
    else:
        note(f"{th(n)} emitted, site states {th(stated)} over {page} page(s) — {th(abs(stated - n))} "
             + ("short" if stated > n else "more emitted than the site states") + ".")


def cmd_list(a):
    params = {}
    if a.type:
        params["type"] = a.type
    if a.contract:
        params["contract"] = a.contract
    walk("list", params, a)


def cmd_search(a):
    walk("search", {"q": a.query}, a)


def cmd_ad(a):
    if not str(a.id).isdigit():
        die(f"{a.id!r}: not a job id")
    d = envelope("get", {"id": a.id})
    if not d.get("id"):
        die("/job/get.json: a JSON body with no `id` — not a job record.", EXIT_PARTIAL)
    c = card(d)
    c.update({"description": text(d.get("body"))[:20000], "language": "pt"})
    print(json.dumps(c, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="ITJobs — Portugal's IT board through its documented read-only API; the key is read, never printed, never asked for.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="every job the API lists — 50 a page, the site's total printed beside the count")
    l_.add_argument("--limit", type=int)
    l_.add_argument("--pages", type=int)
    l_.add_argument("--type", help="comma-separated type ids (the site's appendix)")
    l_.add_argument("--contract", help="comma-separated contract ids")
    l_.set_defaults(fn=cmd_list)
    s = sub.add_parser("search", help="the site's search — q is comma-separated")
    s.add_argument("--query", required=True)
    s.add_argument("--limit", type=int)
    s.add_argument("--pages", type=int)
    s.set_defaults(fn=cmd_search)
    d = sub.add_parser("ad", help="one job in full, by id")
    d.add_argument("--id", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
