#!/usr/bin/env python3
"""Vrabotuvanje (`vrabotuvanje.com.mk`) — North Macedonia's board on the MojPosao / Alma Career platform, read through the same-origin JSON proxy its own pages call.

  vrabotuvanje.py search [--query Q ...] [--location L ...] [--sort adtype|relevance] [--limit N] [--pages N]
  vrabotuvanje.py ad --id <uuid> | --url <advertisement URL>

THE ROUTE IS `/api/proxy/jobs/search`, AND THE `x-app` HEADER IS THE BOARD

The site is a Nuxt app whose listing page is chrome — the results come from
`GET /api/proxy/jobs/search?<params>` on the same host, 100 advertisements a
page, `total` and `totalPages` in the envelope. **The proxy serves several
Alma Career boards, and the `x-app` request header selects which**: on
2026-09-12 11:1x UTC the same URL without it answered `total: 2006` with
Croatian advertisements («Voditelj smjene, Rijeka»), and with
`x-app: vrabotuvanje.com.mk` answered `total: 698`, all Macedonian. **A count
taken without the header is a plausible number about another country**, so
this adapter always sends it, and prints the `x-app` it sent beside the count.

THE RULES open everything to `*` except nine `?source=…` tracking variants
and `?utm_source` — none of which this adapter ever appends (the site's own
cards carry `?source=jobs_page`; the canonical address is rebuilt from the id
and slug without it). `Crawl-delay: 1` sits at the foot of the file, after
the `Amazonbot` group; this adapter spaces 2 s regardless. `certain: True`.

THE SITEMAP IS AN ARCHIVE, NOT AN INVENTORY: `sitemap-job-1.xml` and `-2`
hold 81 360 `/rabota/<uuid>/<slug>` URLs with `<lastmod>` from 2025-02 to
2026-09 — 116 times the live count. Not the route.

THE ADVERTISEMENT is `GET /api/proxy/jobs/<uuid>` — title, employer,
organization, position and root position (the site's own taxonomy),
location (`summary` and address items), employment types, work types,
salary (`from`/`to`/`currency` when the employer gave one, else null),
`publishedAt`/`startsAt`/`endsAt`, `isActive`, and the body as `html` (a
designed advertisement) or `description` (plain). **`description` on a
designed advertisement is the title repeated — the body is in `html`**, and
the adapter emits the text of whichever is longer, saying which.
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
from _ua import UA
from _zero import empty_first_page

HOST = "vrabotuvanje.com.mk"
BASE = "https://" + HOST
API = BASE + "/api/proxy"
X_APP = HOST          # the header that selects this board on the shared proxy
PAGE_SIZE = 100       # what the proxy returned on every page read, 2026-09-12
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
AD_URL_RE = re.compile(r"^https://(?:www\.)?vrabotuvanje\.com\.mk/rabota/([0-9a-f-]{36})(?:/[^?#]*)?")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[vrabotuvanje] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # the file's Crawl-delay: 1 sits after the Amazonbot group; 2 s is ours


def get_json(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "application/json",
        "x-app": X_APP, "Accept-Language": "mk"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            body = decode_body(raw, r.headers)[0]
            try:
                return r.getcode(), json.loads(body)
            except ValueError:
                return r.getcode(), body
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</tr>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t]+", " ", htmlmod.unescape(markup))
    out = re.sub(r"(?:\s*\r?\n\s*)+", "\n", out)   # a designed advertisement is a table: collapse its empty cells
    return out.strip()


def th(n):
    """Thousands with a space — the repo's figure style."""
    return f"{n:,}".replace(",", " ")


def ad_url(ident, slug):
    """The canonical address, from the id — never the `?source=` variant the cards carry."""
    return f"{BASE}/rabota/{ident}/{slug}" if slug else f"{BASE}/rabota/{ident}"


def search_url(query, locations, sort, page):
    params = []
    for q in query or []:
        params.append(("query", q))
    for loc in locations or []:
        params.append(("locations", loc))
    if sort:
        params.append(("sortBy", sort))
    if page and page > 1:
        params.append(("page", str(page)))
    qs = urllib.parse.urlencode(params, safe="")
    return API + "/jobs/search" + (f"?{qs}" if qs else "")


INCOGNITO = "incognito"   # the proxy's `organization` for an employer who chose not to be named — 10 of 698 on 2026-09-12


def as_dict(v, key="name"):
    """The proxy writes some sub-objects as a bare string — `organization:
    "incognito"` for a hidden employer — and this reads both shapes."""
    if isinstance(v, dict):
        return v
    return {key: v} if isinstance(v, str) and v else {}


def employer_of(org):
    """(name, hidden) — a hidden employer is `None, True`, never the word the proxy uses as a placeholder."""
    name = org.get("name")
    if isinstance(name, str) and name.strip().lower() == INCOGNITO:
        return None, True
    return name, False


def card(j):
    org = as_dict(j.get("organization"))
    sal = as_dict(j.get("salary"), "from")
    return {"source": "vrabotuvanje", "country": "MK", "ledger_id": f"vrabotuvanje:{j.get('id')}",
            "id": j.get("id"), "url": ad_url(j.get("id"), j.get("slug")),
            "title": j.get("title"), "employer": employer_of(org)[0], "employer_hidden": employer_of(org)[1],
            "organization_id": org.get("id"), "location": j.get("location"),
            "posted": j.get("publishedAt"), "ends": j.get("endsAt"), "is_active": j.get("isActive"),
            "format": (j.get("format") or {}).get("name"),
            "salary_min": sal.get("from") or None, "salary_max": sal.get("to") or None,
            "salary_currency": sal.get("currency") if (sal.get("from") or sal.get("to")) else None,
            "snippet": j.get("description")}


def jobs_of(envelope):
    """The proxy groups advertisements by employer block — `items[].jobs[]`."""
    out = []
    for it in envelope.get("items") or []:
        out.extend(it.get("jobs") or [])
    return out


def cmd_search(a):
    rows, seen, stated, pages_declared = [], set(), None, None
    page = 1
    while True:
        url = search_url(a.query, a.location, a.sort, page)
        code, env = get_json(url)
        if code != 200 or not isinstance(env, dict):
            die(f"{url}: HTTP {code}" + ("" if isinstance(env, dict) else " — not a JSON envelope"), EXIT_PARTIAL)
        if stated is None:
            stated = env.get("total")
            pages_declared = env.get("totalPages")
        jobs = jobs_of(env)
        if page == 1 and not jobs:
            if (stated or 0) > 0:
                die(f"{url}: the envelope states total {stated} and page 1 carried no advertisement — a reading fault, not a market.", EXIT_PARTIAL)
            die(empty_first_page("vrabotuvanje", json.dumps(env), "advertisement", where=url,
                                 what_asked=" ".join(a.query or []) or None), EXIT_PARTIAL)
        new = 0
        for j in jobs:
            if not j.get("id") or j["id"] in seen:
                continue
            seen.add(j["id"])
            rows.append(card(j))
            new += 1
        if not jobs or new == 0:
            break
        if pages_declared and page >= pages_declared:
            break
        if a.pages and page >= a.pages:
            break
        if a.limit and len(rows) >= a.limit:
            break
        page += 1
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)   # the count printed is the count written to stdout, never the count collected
    walked = f"{page} page(s) of {pages_declared} declared" if pages_declared else f"{page} page(s)"
    if stated is None:
        note(f"{th(n)} distinct advertisement id(s) over {walked}; the envelope states no `total` this run — no second source.")
        return
    truncated = (a.pages and pages_declared and a.pages < pages_declared) or (a.limit and a.limit < stated)
    if n == stated:
        note(f"{th(n)} emitted, board states {th(stated)} (x-app: {X_APP}) over {walked} — equal.")
    elif truncated:
        note(f"{th(n)} emitted of the {th(stated)} the board states (x-app: {X_APP}) — {walked} walked by request (--pages/--limit), not a shortfall.")
    else:
        gap = th(abs(stated - n))
        note(f"{th(n)} emitted, board states {th(stated)} (x-app: {X_APP}) over {walked} — {gap} "
             + ("short" if stated > n else "more emitted than the board states") + ".")


def cmd_ad(a):
    ident = a.id
    if a.url:
        m = AD_URL_RE.match(a.url.strip())
        if not m:
            die(f"{a.url}: not an advertisement address — expected {BASE}/rabota/<uuid>/<slug>")
        ident = m.group(1)
    if not ident or not UUID_RE.match(ident):
        die(f"{ident!r}: not a job uuid")
    url = f"{API}/jobs/{ident}"
    code, d = get_json(url)
    if code == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if code != 200 or not isinstance(d, dict):
        die(f"{url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    if not d.get("id"):
        die(f"{url}: a JSON body with no `id` — not a job record.", EXIT_PARTIAL)
    body_html = text(d.get("html") or "")
    body_plain = (d.get("description") or "").strip()
    body, body_from = (body_html, "html") if len(body_html) >= len(body_plain) else (body_plain, "description")
    loc = as_dict(d.get("location"), "summary")
    sal = as_dict(d.get("salary"), "from")
    pos, root = as_dict(d.get("position")), as_dict(d.get("rootPosition"))
    org, emp = as_dict(d.get("organization")), as_dict(d.get("employer"))
    print(json.dumps({
        "source": "vrabotuvanje", "country": "MK", "ledger_id": f"vrabotuvanje:{d['id']}", "id": d["id"],
        "url": ad_url(d["id"], d.get("slug")),
        "title": d.get("title"), "employer": employer_of(emp)[0] or employer_of(org)[0],
        "employer_hidden": employer_of(emp)[1] or employer_of(org)[1], "organization_id": org.get("id"),
        "location": loc.get("summary"),
        "addresses": [x.get("address") for x in (loc.get("items") or []) if isinstance(x, dict)],
        "position": pos.get("name"), "position_group": root.get("name"),
        "employment_types": d.get("employmentTypes") or [], "work_types": d.get("workTypes") or [],
        "salary_min": sal.get("from") or None, "salary_max": sal.get("to") or None,
        "salary_currency": sal.get("currency") if sal and (sal.get("from") or sal.get("to")) else None,
        "posted": d.get("publishedAt"), "starts": d.get("startsAt"), "ends": d.get("endsAt"),
        "is_active": d.get("isActive"), "external_url": d.get("externalDetailsUrl") or None,
        "description": body[:20000], "description_from": body_from,
        "requirements": text(d.get("requirements")) or None, "benefits": text(d.get("benefits")) or None,
        "language": "mk",
    }, ensure_ascii=False))
    note(f"body read from `{body_from}` ({th(len(body))} characters); on a designed advertisement `description` "
         "is the title repeated and the body lives in `html`.")


def main():
    p = argparse.ArgumentParser(description="Vrabotuvanje — North Macedonia, through the JSON proxy its own pages call, with the x-app header that selects this board.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="every advertisement the board lists — one request per 100, the board's total printed beside the count")
    s.add_argument("--query", action="append")
    s.add_argument("--location", action="append", help="a place name as the site writes it, e.g. Скопје")
    s.add_argument("--sort", choices=("adtype", "relevance"), default=None)
    s.add_argument("--limit", type=int)
    s.add_argument("--pages", type=int)
    s.set_defaults(fn=cmd_search)
    d = sub.add_parser("ad", help="one advertisement, in full, from the proxy")
    g = d.add_mutually_exclusive_group(required=True)
    g.add_argument("--id")
    g.add_argument("--url")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
