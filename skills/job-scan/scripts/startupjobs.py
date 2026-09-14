#!/usr/bin/env python3
"""StartupJobs (`www.startupjobs.cz`, Czechia) — the Czech tech and start-up board, read through the offer sitemap and the offer page's own server-rendered state, because the API the page calls lives on a host that refuses everything in writing; no count stated on a page this client may read — the sitemap is the inventory, and the adapter says so; no contact field in the offer, the text scrubbed all the same. Issue #354.

  startupjobs.py sitemap [--limit N]        sitemap_index.xml → sitemap/offers.xml — every /nabidka/<id>/<slug> (2 requests)
  startupjobs.py list [--limit N]           the sitemap's offers, each read from its own page (N pages, 20 unless told, 2 s apart)
  startupjobs.py ad --url <https://www.startupjobs.cz/nabidka/<id>/<slug>>

THE RULES (143 B, `*`): `Allow: /`, `Disallow: /admin/`, `/superadmin/`; five sitemaps. **The
listing (`/nabidky`) is a Nuxt page that renders no offer on the server and fetches its list
from `https://back.startupjobs.cz` — whose rules are `User-agent: * / Disallow: /`, everything
refused in writing: no request ever goes there.** The offer page, on the other hand, is
server-rendered on `www.` with the whole offer object in its `__NUXT_DATA__` payload (the
`apiOffersIdGet` query the page dehydrates) — that is the route: the sitemap for the ids,
the page for the record. No Crawl-delay; 2 s is ours.

NO STATED COUNT THIS CLIENT MAY READ. The listing's count is the API's; the root and the
listing print none. `sitemap/offers.xml` carried 392 `/nabidka/<id>/<slug>` rows on the day
(414 on 2026-09-01), no lastmod — printed as the inventory, never as the site's statement;
a 200 page without one offer block exits 6.

THE RECORD (the offer object's own fields, Czech first): `name`, `company` (name, slug, type
— start/scale/corporate —, areas, verified), `salary` (minimum, maximum, `measure` monthly —
a period, so `salary_unit_stated` is true —, currency), `locations` (place, region, country;
`type` place/remote), `collaborations` (hybrid, onsite, remote, employment, freelance …),
`shifts` (hours a month: 160 is full time), `seniorities`, `skills` (required / nice-to-have),
`languages` (name, level), `benefits`, the field (`breadcrumbs`), `createdAt`, `updatedAt`,
`promotionSince`, `status`, `externalLink` (the employer's own application page — emitted,
never fetched), `description` (HTML → text) and `descriptionShort`. **The object carries no
contact field; the text is scrubbed of e-mail addresses and Czech telephone numbers all the
same; `contacts_withheld` on every record.**

Measured 2026-09-14 02:4x UTC by the declared client, the guard on the exact path: the index
601 B, `offers.xml` 48 488 B / 392 rows; `/nabidky` 150 886 B with no offer; the offer page
152 689 B with its 54 144-character payload.
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

HOST = "www.startupjobs.cz"
INDEX = f"https://{HOST}/sitemap_index.xml"
OFFERS = f"https://{HOST}/sitemap/offers.xml"
REFUSED_HOST = "back.startupjobs.cz"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<!\d)(?:\+420[\s ]?)?\d{3}[\s ]?\d{3}[\s ]?\d{3}(?!\d)")
AD_RE = re.compile(r"^/nabidka/(\d+)/([^/]+)/?$")
LOC_XML_RE = re.compile(r"<loc>([^<]+)</loc>")
WRAPPERS = {"Reactive", "ShallowReactive", "Ref", "ShallowRef", "EmptyRef", "Set", "Map", "Date", "NuxtError", "BigInt", "RegExp"}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[startupjobs] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    if parts.netloc == REFUSED_HOST:
        die(f"{url}: {REFUSED_HOST} publishes `User-agent: * / Disallow: /` — refused in writing, never sent", EXIT_REFUSED)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written; 2 s is ours


def request(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9", "Accept-Language": "cs"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t ​]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def hydrate(arr, i, seen=None):
    """Nuxt's `__NUXT_DATA__` is devalue's flat array — every value an index into it; wrappers (`Reactive`, `Ref` …) unwrapped, negative indices the sentinels."""
    seen = {} if seen is None else seen
    if not isinstance(i, int):
        return i
    if i < 0:
        return None   # -1 undefined, -2 NaN … the sentinels
    if i in seen:
        return seen[i]
    v = arr[i]
    if isinstance(v, list):
        if v and isinstance(v[0], str) and v[0] in WRAPPERS:
            if v[0] == "Map":
                out = {hydrate(arr, v[k], seen): hydrate(arr, v[k + 1], seen) for k in range(1, len(v) - 1, 2)}
            elif v[0] == "Set":
                out = [hydrate(arr, x, seen) for x in v[1:]]
            else:
                out = hydrate(arr, v[1], seen) if len(v) > 1 else None
            seen[i] = out
            return out
        out = []
        seen[i] = out
        for x in v:
            out.append(hydrate(arr, x, seen))
        return out
    if isinstance(v, dict):
        out = {}
        seen[i] = out
        for k, x in v.items():
            out[k] = hydrate(arr, x, seen)
        return out
    seen[i] = v
    return v


def offer_of(body):
    """The `apiOffersIdGet` query the offer page dehydrates — the offer object, or None."""
    m = re.search(r'<script type="application/json"[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', body, re.S)
    if not m:
        return None
    try:
        arr = json.loads(m.group(1))
    except ValueError:
        return None
    try:
        state = hydrate(arr, 0)
    except (IndexError, TypeError, RecursionError):
        return None
    queries = (((state or {}).get("state") or {}).get("$svue-query") or {}).get("queries") or []
    for q in queries:
        key = q.get("queryKey")
        if isinstance(key, list) and key and isinstance(key[0], dict) and key[0].get("_id") == "apiOffersIdGet":
            d = (q.get("state") or {}).get("data")
            if isinstance(d, dict) and d.get("name"):
                return d
    return None


def cs(v):
    """A `{cs, en}` pair → the Czech text, the English one when Czech is empty."""
    if isinstance(v, dict):
        return (v.get("cs") or v.get("en") or "").strip() or None
    return (v or "").strip() or None if isinstance(v, str) else None


def record(o, oid, url):
    comp = o.get("company") or {}
    sal = o.get("salary") or {}
    locs = o.get("locations") or []
    return {
        "source": "startupjobs", "country": "CZ", "ledger_id": f"startupjobs:{oid}", "id": str(oid), "url": url,
        "title": cs(o.get("name")),
        "employer": (comp.get("name") or "").strip() or None, "employer_slug": comp.get("slug") or None, "employer_type": comp.get("type") or None,
        "employer_verified": comp.get("verified"), "employer_areas": [cs(a.get("name")) for a in (comp.get("areas") or []) if cs(a.get("name"))] or None,
        "field": " / ".join(cs(b.get("name")) for b in (o.get("breadcrumbs") or []) if cs(b.get("name"))) or None,
        "locations": [{"name": cs(l.get("name")), "place": cs(l.get("place")), "region": cs(l.get("region")), "country": cs(l.get("country")), "type": l.get("type")} for l in locs if isinstance(l, dict)] or None,
        "collaborations": o.get("collaborations") or None, "shifts_hours_month": o.get("shifts") or None, "seniorities": o.get("seniorities") or None,
        "salary_min": sal.get("minimum"), "salary_max": sal.get("maximum"), "salary_currency": sal.get("currency") if sal else None,
        "salary_unit": sal.get("measure") if sal else None, "salary_unit_stated": bool(sal.get("measure")) and (sal.get("minimum") is not None or sal.get("maximum") is not None),
        "skills": [{"name": s.get("name"), "type": s.get("type")} for s in (o.get("skills") or []) if isinstance(s, dict) and s.get("name")] or None,
        "languages": [{"name": l.get("name"), "level": l.get("level")} for l in ((o.get("languages") or {}).get("cs") or []) if isinstance(l, dict)] or None,
        "benefits": [b.get("name") for b in ((o.get("benefits") or {}).get("cs") or []) if isinstance(b, dict) and b.get("name")] or None,
        "created": (o.get("createdAt") or "")[:10] or None, "updated": (o.get("updatedAt") or "")[:10] or None, "promoted_since": (o.get("promotionSince") or "")[:10] or None,
        "status": o.get("status"), "exclusive": o.get("exclusive"),
        "external_link": o.get("externalLink") or None,   # the employer's own application page — never fetched
        "summary": scrub(cs(o.get("descriptionShort"))),
        "description": scrub(text(cs(o.get("description")))),
        "contacts_withheld": True, "language": "cs",
    }


def sitemap_rows():
    code, body = request(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    if OFFERS not in body:
        die(f"{INDEX}: no offers sitemap named — the index's shape changed", EXIT_PARTIAL)
    code, body = request(OFFERS)
    if code != 200:
        die(f"{OFFERS}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    rows, seen, other = [], set(), 0
    for loc in LOC_XML_RE.findall(body):
        m = AD_RE.match(urllib.parse.urlsplit(loc).path)
        if not m:
            other += 1
            continue
        if m.group(1) in seen:
            continue
        seen.add(m.group(1))
        rows.append({"source": "startupjobs", "country": "CZ", "ledger_id": f"startupjobs:{m.group(1)}", "id": m.group(1), "url": loc, "slug": m.group(2), "contacts_withheld": True, "language": "cs"})
    if not rows:
        die(f"{OFFERS}: 200 and not one /nabidka/<id>/ row — the file's shape changed", EXIT_PARTIAL)
    return rows, other


def cmd_sitemap(a):
    rows, other = sitemap_rows()
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{th(len(rows))} offer id(s) in the offers sitemap ({th(other)} other rows set aside) — the site states no count on a page this client may read (its count is on {REFUSED_HOST}, refused in writing): the sitemap is the inventory, not the site's statement.")
    if a.limit and a.limit < len(rows):
        note(f"{th(len(emitted))} emitted of the {th(len(rows))} — bounded by --limit.")


def read_ad(url):
    code, body = request(url)
    if code == 404:
        return None, "gone"
    if code != 200:
        return None, f"HTTP {code}"
    o = offer_of(body)
    if not o:
        return None, "no offer block"
    return o, None


def cmd_list(a):
    rows, other = sitemap_rows()
    limit = a.limit if a.limit else 20
    out, gone, broken = [], 0, 0
    for r in rows[:limit]:
        o, why = read_ad(r["url"])
        if o is None:
            if why == "gone":
                gone += 1
                continue
            die(f"{r['url']}: {why} — the offer page's shape changed; not an empty offer", EXIT_PARTIAL)
        out.append(record(o, r["id"], r["url"]))
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{th(len(out))} offer(s) read from their pages, {th(gone)} gone since the sitemap, of the {th(len(rows))} the offers sitemap names — {th(min(limit, len(rows)))} read by request (--limit), not a shortfall; the site states no count this client may read.")
    note(f"the list's API on {REFUSED_HOST} is refused in writing and never sent; no contact field in the offer, the text scrubbed all the same; the employer's own application link is emitted and never fetched.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc not in (HOST, "startupjobs.cz") or not m:
        die(f"{a.url}: not an offer address (https://{HOST}/nabidka/<id>/<slug>)")
    url = f"https://{HOST}{parts.path.rstrip('/')}"
    o, why = read_ad(url)
    if why == "gone":
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if o is None:
        die(f"{url}: {why} — the offer page's shape changed", EXIT_PARTIAL)
    print(json.dumps(record(o, m.group(1), url), ensure_ascii=False))
    note(f"{url}: read from the page's own state; the text is scrubbed; the employer's application link is never fetched.")


def main():
    p = argparse.ArgumentParser(description="StartupJobs — the Czech tech board through its offer sitemap and its server-rendered offer pages; the API host refused in writing and never sent; no count stated this client may read. Issue #354.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s_ = sub.add_parser("sitemap", help="every offer id the offers sitemap names (2 requests)")
    s_.add_argument("--limit", type=int)
    s_.set_defaults(fn=cmd_sitemap)
    l_ = sub.add_parser("list", help="the sitemap's offers read from their pages — 20 unless --limit")
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
