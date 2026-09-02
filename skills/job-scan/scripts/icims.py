#!/usr/bin/env python3
"""Read one employer's iCIMS careers site — where the default URL is not the ad.

iCIMS is an ATS: one employer per site, no search across employers. It earns
an adapter because four country surveys named it as the most common family
with no adapter here — Ireland 10 cards of 240, Singapore 15 of 240,
Philippines 12 of 240, Indonesia 5 of 120 — and one ATS family serves every
country at once.

  GET https://<host>/robots.txt            → read it. Per HOST, never per family
  GET https://<host>/sitemap.xml           → this employer's ads, one <loc> each
  GET https://<host>/jobs/<id>/<slug>/job?in_iframe=1
                                           → **the ad**
  GET https://<host>/jobs/<id>/<slug>/job  → 90 KB of the employer's portal,
                                             HTTP 200, and no ad in it

THE DEFAULT URL IS NOT THE AD, AND THE SITEMAP LISTS THE DEFAULT ONE. Measured
2026-09-02 on `careers-sunrise.icims.com/jobs/8179/nurse/job`:

    without ?in_iframe=1 → 200, 90 117 bytes, no JobPosting, no job title
    with    ?in_iframe=1 → 200, 37 509 bytes, JobPosting, "Nurse", 4 637 chars

**So this is an instruction and not a warning: append `?in_iframe=1` to every
URL the sitemap gives you.** Enumerate 14 000 ads the obvious way and you
collect 14 000 plausible pages containing nothing, in HTTP 200, and conclude
the board is empty.

THE SAME ID IS A DIFFERENT VACANCY ON EVERY HOST, AND THE WRONG HOST ANSWERS
200. `/jobs/8179` is a nurse at Sunrise and something else entirely at MV
Transportation; the shared `careers.icims.com` 404s it. So the ledger key is
`icims:<host>:<id>` and the host is not optional. This is the mirror of the
Workday defect found the same day: there, one vacancy under two keys, which
duplicates; here, two vacancies under one key, which **makes an ad disappear**.

THREE HOST SHAPES, AND THE PLATFORM HOST IS NEVER CONSTRUCTED. `careers-<t>`,
`<t>` bare, and the employer's own domain — `careers.montenidoaffiliates.com`,
`jobs.lutheranseniorlife.org`. A branded page names its platform host in its
own markup, so `resolve` reads it rather than guessing: the prefix has been
seen as `careers-`, `apply-`, `field-` and nothing at all, and a constructed
host 404s while the employer looks like it has no vacancies.

ROBOTS IS READ PER HOST. Two of six iCIMS hosts sampled served
`User-agent: * / Disallow: /`. Three rules, in order:

1. **The host given governs.** Its file is read and its answer is obeyed.
2. **No host is ever substituted to escape a refusal.** If the host given
   refuses, that is the answer — `resolve` does not become a way around it.
3. **If a sibling host refuses while the given host permits, say so**, and
   leave the decision with the person. Not silence in either direction.

Verified against the live platform on **2026-09-02**.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _robots import verdict as robots_verdict

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

LOC = re.compile(r"<loc>([^<]+)</loc>")
JOB = re.compile(r"/jobs/(\d+)(?:/([^/?#]*))?")
LD = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
                re.S)
# A branded page names its platform host in its own markup — the only reliable
# way to get it, because the prefix is not guessable.
PLATFORM = re.compile(r"https?://([a-z0-9][a-z0-9-]*\.icims\.com)", re.I)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[icims] {msg}", file=sys.stderr)


def get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html,application/xml,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.getcode(), r.headers.get("Content-Type", ""), \
                r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), \
            e.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def check_host(host, sibling=None):
    """Rule 1, and rule 3 when a sibling is known."""
    v = robots_verdict(host)
    if not v["sweep"]:
        die(f"{host}: {v['reason']}\n"
            f"This adapter does not resolve to another host to get around a "
            f"refusal. If this employer publishes the same board on a domain "
            f"of its own that permits reading, that is the person's call to "
            f"make with that URL, not this script's to make silently.", 7)
    if sibling:
        sv = robots_verdict(sibling)
        if not sv["sweep"]:
            note(f"the host you gave ({host}) permits reading, and this "
                 f"employer's other host ({sibling}) refuses: {sv['reason']} "
                 f"Both serve the same board. Reading {host} obeys the origin "
                 f"you asked for — robots.txt is per origin — but you are "
                 f"being told, because choosing the host that says yes is not "
                 f"something this script will do quietly on your behalf.")
    return v


def ad_url(host, ident, slug=None, iframe=True):
    path = f"/jobs/{ident}/{slug}/job" if slug else f"/jobs/{ident}"
    return f"https://{host}{path}" + ("?in_iframe=1" if iframe else "")


def posting(html):
    for m in LD.finditer(html):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            continue
        for o in (d if isinstance(d, list) else [d]):
            if isinstance(o, dict) and o.get("@type") == "JobPosting":
                return o
    return None


def cmd_resolve(a):
    """Recover the platform host from an employer's own careers domain."""
    code, ctype, body = get(a.url)
    hosts = sorted({h.lower() for h in PLATFORM.findall(body)})
    marks = [m for m in ("iCIMS System ID", "ICIMS-LINK", "iCIMS ATS Hiring "
                         "Flow") if m.lower() in body.lower()]
    if not hosts and not marks:
        die(f"{a.url}: nothing in this page names iCIMS. It answered "
            f"HTTP {code}; either it is a different ATS or the markup moved.",
            3)
    # The job hosts, not the corporate ones (www.icims.com carries their legal
    # pages and appears on every branded site).
    tenants = [h for h in hosts if not h.startswith("www.")]
    print(json.dumps({
        "url": a.url,
        "platform_hosts": tenants,
        "markers": marks,
        "note": "the prefix is not guessable — careers-, apply-, field- and "
                "bare have all been seen, so this is read and never built",
    }, ensure_ascii=False))
    if tenants:
        note(f"before sweeping either host, run `list --host <host>`: this "
             f"script reads each host's own robots.txt, and on 2026-09-02 two "
             f"of six iCIMS platform hosts refused everything while the "
             f"employer's own domain permitted.")


def cmd_list(a):
    check_host(a.host, sibling=a.sibling)
    code, ctype, body = get(f"https://{a.host}/sitemap.xml")
    if code != 200:
        die(f"https://{a.host}/sitemap.xml: HTTP {code}. Two of six hosts "
            f"sampled answered 403 here while their robots.txt also refused; "
            f"a 404 more likely means this host does not publish one.", 3)
    if "xml" not in ctype:
        die(f"the sitemap answered {ctype!r}, not XML — a sitemap that is not "
            f"XML is not a sitemap. See shared/robots-policy.md.")
    rows, seen = [], set()
    for loc in LOC.findall(body):
        m = JOB.search(loc)
        if not m:
            continue          # /jobs/intro and other furniture
        ident, slug = m.group(1), (m.group(2) or None)
        if ident in seen:
            continue
        seen.add(ident)
        rows.append({
            "id": ident,
            "ledger_id": f"icims:{a.host}:{ident}",
            # **The host is part of the key**: /jobs/8179 is a different
            # vacancy on every host and the wrong host answers 200.
            "host": a.host,
            "slug": slug,
            # The URL a person opens, as the sitemap gives it.
            "url": ad_url(a.host, ident, slug, iframe=False),
            # The URL that actually carries the ad.
            "read_url": ad_url(a.host, ident, slug, iframe=True),
        })
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{len(rows)} ad(s) in this host's sitemap. **The sitemap lists the "
         f"URL without `?in_iframe=1`** — `read_url` is the one that carries "
         f"the ad; the bare one answers 200 with the employer's portal and no "
         f"posting in it.")


def cmd_ad(a):
    check_host(a.host)
    code, ctype, body = get(ad_url(a.host, a.id, a.slug, iframe=True))
    if code == 404:
        die(f"{a.host}/jobs/{a.id}: 404 — gone, or never on this host. "
            f"Remember that the id is host-scoped: the same number is another "
            f"employer's vacancy elsewhere, and that host would answer 200.",
            3)
    p = posting(body)
    if p is None:
        die(f"{a.host}/jobs/{a.id}: HTTP {code}, {len(body)} bytes, and no "
            f"JobPosting. If this is about 90 KB, `?in_iframe=1` did not take "
            f"effect and you are holding the employer's portal page.", 3)
    org = p.get("hiringOrganization") or {}
    # `jobLocation` is sometimes an object and sometimes a list of them —
    # a multi-site vacancy. Take the first and say how many there were.
    jl = p.get("jobLocation") or {}
    places = jl if isinstance(jl, list) else [jl]
    loc = (places[0] or {}).get("address") or {} if places else {}
    print(json.dumps({
        "id": str(a.id),
        "ledger_id": f"icims:{a.host}:{a.id}",
        "host": a.host,
        "url": ad_url(a.host, a.id, a.slug, iframe=False),
        "title": p.get("title"),
        "company": org.get("name"),
        "posted": (p.get("datePosted") or "")[:10] or None,
        "expires": (p.get("validThrough") or "")[:10] or None,
        "employment_type": p.get("employmentType"),
        "city": loc.get("addressLocality"),
        "region": loc.get("addressRegion"),
        "country": loc.get("addressCountry"),
        # More than one means the same vacancy is posted for several sites.
        "locations_listed": len(places),
        "description_chars": len(p.get("description") or ""),
        "description": p.get("description") if a.with_text else None,
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("resolve",
                       help="platform host from an employer's own careers URL")
    r.add_argument("--url", required=True)
    r.set_defaults(func=cmd_resolve)

    li = sub.add_parser("list", help="this employer's ads, from its sitemap")
    li.add_argument("--host", required=True,
                    help="the host to read. Given, never constructed")
    li.add_argument("--sibling",
                    help="another host of the same employer, if known — its "
                         "robots.txt is reported, never used to override")
    li.add_argument("--limit", type=int)
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="read one ad")
    ad.add_argument("--host", required=True)
    ad.add_argument("--id", required=True)
    ad.add_argument("--slug")
    ad.add_argument("--with-text", action="store_true", dest="with_text")
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
