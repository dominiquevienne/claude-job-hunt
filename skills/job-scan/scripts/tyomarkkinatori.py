#!/usr/bin/env python3
"""Työmarkkinatori (`tyomarkkinatori.fi`) — Finland's public employment service, through the search API its own widget calls — a route the site REFUSES IN WRITING, taken only under the user's own `boards.tyomarkkinatori.override_robots: true`. Issue #371.

  tyomarkkinatori.py search [--q TEXT] [--pages N] [--limit N]
  tyomarkkinatori.py ad --id <uuid>

THE ROUTE IS REFUSED, AND THAT IS THE FIRST THING THIS ADAPTER SAYS.
`tyomarkkinatori.fi/robots.txt` writes `Disallow: /api/` and `/*/api/` to
`User-agent: *` (639 B, read 2026-09-13), and every data route of the board
is under `/api/`: the widget `TmtTyopaikkaHakuV2` (1 500 919 B, permitted,
read once) builds `qU = axios.create({baseURL: "/api"})` and POSTs
`/jobpostingfulltext/search/v2/search` with `{query, filters, paging:
{pageNumber, pageSize}, sorting}`, and GETs `/jobposting-new/v1/public
/jobpostings/<id>` for a posting. The pages carry no advertisement.

**Without the key this adapter requests nothing and exits 7**, naming the
rule, the key and the file it consulted. **With the key** — the owner's
decision of 2026-09-13 (#403), «l'utilisateur doit pouvoir émettre une
dérogation en son âme et conscience», the user's line in the user's
workspace — the guard flips the written «no» for this board, prints the
banner (what is crossed before what it costs), and the adapter reads one
page at a time, 3 s apart, and stops on the first block. The response's
`totalElements` is the witness, printed beside every walk.

**Written and exercised on a stub of the widget's own schemas on
2026-09-13; no request was made under `/api/`** — the key was absent on
this machine, by design, and it is not the developer's to set. The first
keyed run is the first measurement.

THE HIT (schema `Z$` in the widget): `id` (uuid), `title` {fi, en, sv},
`publishDate`, `applicationPeriodEndDate`, `employer` {name, businessId[],
ownerName}, `employerType` (Organization / International / Household),
`location` {address {streetAddress, postalCode, postOffice}, municipalities
[{value, region, label}], regions [], countries []}, `employmentRelationships`,
`continuityOfWork[]`, `workTime`, `tags[]`, `applicationUrl`. The street
address is a premises' address and is not emitted; the municipality and
region are. No contact field is in the schema, and none is read.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD = "tyomarkkinatori"
HOST = "tyomarkkinatori.fi"
BASE = f"https://{HOST}"
SEARCH = f"{BASE}/api/jobpostingfulltext/search/v2/search"
POSTING = f"{BASE}/api/jobposting-new/v1/public/jobpostings/"
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
PAGE_SIZE = 30            # the widget's own default (aN.pageSize)

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[tyomarkkinatori] {msg}", file=sys.stderr)


def gate(url):
    """The guard on the exact path, with this board's name — so the user's key, and only it, can turn the written «no».

    `_robots.allowed()` prints the banner itself when it crosses (#403); this
    function adds the refusal's own words when it does not, and the sentence
    to write — `boards.tyomarkkinatori.override_robots: true` — never only a
    path."""
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts), board=BOARD)
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: refused in writing — {a.get('host', HOST)} writes `Disallow: {a.get('rule')}` to `User-agent: *`, and every data route of this "
            f"board is under it. **This adapter requests nothing.** The one exit is yours to take, in your own name: "
            f"{a.get('override_available', 'boards.' + BOARD + '.override_robots: true in config.yml')} — see shared/setup.md 5h and shared/robots-policy.md; "
            f"the address that would get blocked is yours.", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=3.0)   # no Crawl-delay in the rules; 3 s is ours — «pace as if you were welcome»


def request(url, payload=None):
    gate(url)
    _PACE.wait()
    headers = {"User-Agent": UA, "Accept": "application/json", "Accept-Language": "fi,en"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()
    req = urllib.request.Request(wire_url(url), data=data, headers=headers, method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def lang(obj, order=("fi", "en", "sv")):
    """A {fi, en, sv} object as one string — the first language present, and which."""
    if isinstance(obj, str):
        return obj, None
    if not isinstance(obj, dict):
        return None, None
    for k in order:
        v = obj.get(k)
        if v:
            return v, k
    return None, None


def row(h):
    title, tl = lang(h.get("title"))
    emp = h.get("employer") if isinstance(h.get("employer"), dict) else {}
    loc = h.get("location") if isinstance(h.get("location"), dict) else {}
    muns = [m for m in (loc.get("municipalities") or []) if isinstance(m, dict)]
    regs = [r for r in (loc.get("regions") or []) if isinstance(r, dict)]
    app = h.get("applicationUrl") if isinstance(h.get("applicationUrl"), dict) else {}
    return {
        "source": BOARD, "country": "FI", "ledger_id": f"{BOARD}:{h.get('id')}", "id": h.get("id"),
        "url": f"{BASE}/henkiloasiakkaat/avoimet-tyopaikat/{h.get('id')}",
        "title": title, "title_language": tl,
        "employer": emp.get("name"), "employer_type": h.get("employerType"),
        # the street address in `location.address` is a premises' address and is not emitted
        "municipality": lang(muns[0].get("label"))[0] if muns else None,
        "region": lang(regs[0].get("label"))[0] if regs else (muns[0].get("region") if muns else None),
        "post_office": (loc.get("address") or {}).get("postOffice") if isinstance(loc.get("address"), dict) else None,
        "published": h.get("publishDate"), "application_deadline": h.get("applicationPeriodEndDate"),
        "employment": h.get("employmentRelationships"), "continuity": h.get("continuityOfWork"), "work_time": h.get("workTime"),
        "tags": h.get("tags"), "application_url": app.get("value"),
        "language": tl or "fi",
    }


def page(query, number):
    payload = {"query": query or "", "filters": {}, "paging": {"pageNumber": number, "pageSize": PAGE_SIZE}, "sorting": "LATEST"}
    code, body = request(SEARCH, payload)
    if code in (403, 429):
        die(f"{SEARCH}: HTTP {code} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if code != 200:
        die(f"{SEARCH}: HTTP {code}", EXIT_PARTIAL)
    try:
        j = json.loads(body)
    except ValueError:
        die(f"{SEARCH}: not JSON ({len(body)} characters)", EXIT_PARTIAL)
    if not isinstance(j, dict) or "totalElements" not in j:
        die(f"{SEARCH}: no `totalElements` in the answer — not the widget's response shape.", EXIT_PARTIAL)
    return j.get("totalElements"), [h for h in (j.get("content") or []) if isinstance(h, dict)], j.get("totalPages")


def cmd_search(a):
    total, hits, pages = page(a.q, 0)
    rows, seen, n_page = [], set(), 0
    while True:
        new = 0
        for h in hits:
            if not h.get("id") or h["id"] in seen:
                continue
            seen.add(h["id"])
            rows.append(row(h))
            new += 1
        if not hits or new == 0 or len(rows) >= (total or 0):
            break
        if a.pages and n_page + 1 >= a.pages:
            break
        if a.limit and len(rows) >= a.limit:
            break
        n_page += 1
        _t, hits, _p = page(a.q, n_page)
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    where = f"(q={a.q!r})" if a.q else "(no filter)"
    walked = n_page + 1
    bounded = (a.pages and walked >= a.pages and (total or 0) > walked * PAGE_SIZE) or (a.limit and a.limit < (total or 0))
    if bounded:
        note(f"{th(n)} emitted of the {th(total)} the site states {where} — {walked} page(s) of {PAGE_SIZE} walked by request (--pages/--limit), not a shortfall.")
    elif n == total:
        note(f"{th(n)} emitted over {walked} page(s), site states {th(total)} {where} — equal.")
    else:
        note(f"{th(n)} emitted over {walked} page(s), site states {th(total)} {where} — {th(abs((total or 0) - n))} " + ("short" if (total or 0) > n else "more emitted than the site states") + ".")


def cmd_ad(a):
    ident = (a.id or "").strip().lower()
    if not UUID_RE.match(ident):
        die(f"{a.id!r}: not a posting id (a uuid)")
    code, body = request(POSTING + ident)
    if code == 404:
        die(f"{POSTING}{ident}: HTTP 404", EXIT_GONE)
    if code in (403, 429):
        die(f"{POSTING}{ident}: HTTP {code} — the operator answering directly; stopped.", EXIT_REFUSED)
    if code != 200:
        die(f"{POSTING}{ident}: HTTP {code}", EXIT_PARTIAL)
    try:
        j = json.loads(body)
    except ValueError:
        die(f"{POSTING}{ident}: not JSON ({len(body)} characters)", EXIT_PARTIAL)
    r = row(j if isinstance(j, dict) else {})
    r["id"] = r["id"] or ident
    desc, dl = lang(j.get("description") if isinstance(j, dict) else None)
    # any contact block the posting carries — the widget's schema has none in the hit; the posting may — is not emitted
    dropped = sorted(k for k in (j.keys() if isinstance(j, dict) else []) if re.search(r"contact|phone|email|yhteys", k, re.I))
    r.update({"description": (desc or "")[:20000] or None, "description_language": dl, "contact_dropped": dropped})
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Työmarkkinatori — Finland's public employment service through the API its widget calls, a route refused in writing and taken only under the user's own boards.tyomarkkinatori.override_robots; totalElements beside every walk; no contact. Issue #371.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="the widget's search, 30 a page, 3 s apart, LATEST first; without the key: nothing requested, exit 7")
    s.add_argument("--q", help="free text, as the widget's query")
    s.add_argument("--pages", type=int)
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_search)
    d = sub.add_parser("ad", help="one posting by uuid, from the same API; contact keys dropped")
    d.add_argument("--id", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
