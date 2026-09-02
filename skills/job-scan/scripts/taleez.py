#!/usr/bin/env python3
"""Fetch job ads from a Taleez careers site — the French SME/ETI ATS.

Taleez is a Toulouse-built ATS used by French SMEs and mid-sized companies. Its
careers sites are the French counterpart of `umantis.md`: employers no
meta-board indexes, one tenant at a time, and **no tenant directory exists** —
the user supplies the careers URL.

Two endpoints, both unauthenticated and neither needing a browser:

  GET https://<tenant>.taleez.com/api/careez   → the whole careers site as JSON,
                                                  jobs included, in ONE request
  GET https://taleez.com/apply/<job slug>      → the ad, server-rendered, with a
                                                  JobPosting block

The listing carries no description, so `--with-detail` reads the ad page. It
also carries the tenant's own property referential, which is what turns opaque
ids into "Domaine métier: Commerce / Ventes" — see `decode_properties`.

Usage:
  taleez.py jobs --tenant bertintechnologies
  taleez.py jobs --url https://ufcv-emploi.taleez.com/ --with-detail
  taleez.py ad <job slug>

Output: one JSON object per line (jobs), or one JSON object (ad).
"""

import argparse
import gzip
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request

CAREEZ = "https://{}.taleez.com/api/careez"
AD_URL = "https://taleez.com/apply/{}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

TENANT_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")
HOST_RE = re.compile(r"https?://([a-z0-9-]+)\.taleez\.com", re.I)
LD_RE = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)

# `lockedType` on a property definition says what the tenant's own free-form
# field actually means, so these map to stable keys instead of French labels
# that each tenant is free to rename.
LOCKED = {"DEPARTMENT": "department", "XP": "experience",
          "REMOTE": "remote_type", "APPRENTICESHIP": "apprenticeship"}


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def fetch(url, as_json=False):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json" if as_json else "text/html",
        "Accept-Language": "fr-FR,fr;q=0.9",
        # Taleez compresses whatever you ask for: `Accept-Encoding: identity`
        # is ignored and the body still comes back compressed, which silently
        # turns every regex search into a miss rather than an error. So ask
        # for the one encoding the standard library can undo, and undo it.
        "Accept-Encoding": "gzip",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
            if r.headers.get("Content-Encoding", "").lower() == "gzip":
                body = gzip.decompress(body)
            raw = body.decode("utf-8", errors="replace")
            return json.loads(raw) if as_json else raw
    except urllib.error.HTTPError as e:
        if e.code == 404:
            die("nothing at that URL (HTTP 404). For a tenant, check the slug "
                "against the careers URL the user gave — there is no tenant "
                "directory, so a wrong slug is the likeliest cause. For an ad, "
                "record it as discarded.", code=3)
        if e.code in (401, 403):
            die(f"HTTP {e.code}. Note this is NOT the recruiter API: "
                "`api.taleez.com` needs a key, `<tenant>.taleez.com/api/careez` "
                "does not. Check the host.")
        die(f"Taleez returned HTTP {e.code}")
    except json.JSONDecodeError:
        die("that endpoint did not return JSON. `/api/careez` on a tenant host "
            "does; the marketing site at taleez.com does not.")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach Taleez: {e}")


def tenant_of(a):
    if a.url:
        m = HOST_RE.search(a.url)
        if not m:
            die(f"could not read a tenant out of {a.url!r}. It should look "
                "like https://<tenant>.taleez.com/. A careers site on the "
                "employer's own domain does not expose the tenant in its URL "
                "— ask the user to open it and read the taleez.com address "
                "off a job's apply link.")
        return m.group(1).lower()
    if not a.tenant:
        die("give --tenant or --url. **There is no tenant directory** — no "
            "search, no list, and no way to resolve an employer name to a "
            "tenant. The careers URL comes from the user, exactly as for "
            "umantis.")
    if not TENANT_RE.match(a.tenant):
        die(f"{a.tenant!r} is not a tenant slug. It is the first label of the "
            "host: `bertintechnologies` in bertintechnologies.taleez.com.")
    return a.tenant.lower()


def to_text(markup):
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", markup or "")
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", txt)
    txt = re.sub(r"(?i)<li[^>]*>", "- ", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt).replace(" ", " ")
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", txt).strip()


def ms_to_iso(ms):
    if not ms:
        return None
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ms / 1000))


def decode_properties(job, defs):
    """Turn `[{id, choices:[id]}]` into readable values.

    The choice label lives in `value`, not in any of the `*Name` fields the
    definition itself uses — reading it from `publicName` yields None on every
    choice, which looks like an ad with no data rather than a bug.
    """
    out = {}
    for pr in job.get("properties") or []:
        d = defs.get(pr.get("id"))
        if not d:
            continue
        labels = {c.get("id"): c.get("value") for c in (d.get("choices") or [])}
        vals = [labels.get(c) for c in (pr.get("choices") or [])]
        vals = [v for v in vals if v]
        if not vals:
            continue
        key = LOCKED.get(d.get("lockedType")) or (
            d.get("publicName") or d.get("internalName"))
        out[key] = vals[0] if len(vals) == 1 else vals
    return out


def card(job, site, defs):
    loc = job.get("location") or {}
    slug = job.get("slug")
    units = {u.get("id"): u.get("name") for u in (site.get("units") or [])}
    return {
        "id": job.get("id"),
        "ledger_id": f"taleez:{job.get('id')}",
        "url": AD_URL.format(slug) if slug else None,
        "slug": slug,
        "title": job.get("label"),
        # Always the tenant: a Taleez careers site belongs to one employer, so
        # unlike an agency board this name is the workplace.
        "company": site.get("name"),
        "unit": units.get(job.get("unitId")),
        "city": loc.get("city"),
        "postal_code": loc.get("postalCode"),
        "country": loc.get("country"),
        "contract": job.get("contract"),
        "remote": job.get("remote"),
        "lang": job.get("lang"),
        "published": ms_to_iso(job.get("publishDate")),
        "created": ms_to_iso(job.get("creationDate")),
        **decode_properties(job, defs),
    }


def ad_fields(slug, page):
    for raw in LD_RE.findall(page):
        try:
            d = json.loads(raw.strip())
        except Exception:  # noqa: BLE001
            continue
        if isinstance(d, dict) and d.get("@type") == "JobPosting":
            emp = d.get("employmentType")
            return {
                "description": to_text(d.get("description")),
                "qualifications": to_text(d.get("qualifications")),
                "employment_type": ", ".join(emp) if isinstance(emp, list)
                else emp,
                "posted": d.get("datePosted"),
            }
    die(f"no JobPosting block on /apply/{slug}. Either the ad closed, or the "
        "markup changed — report it with board-request rather than guessing.",
        code=3)


def cmd_jobs(a):
    tenant = tenant_of(a)
    site = fetch(CAREEZ.format(tenant), as_json=True)
    jobs = site.get("jobs") or []
    defs = {p.get("id"): p for p in (site.get("properties") or [])}
    print(f"[taleez] {site.get('name')} ({tenant}): {len(jobs)} ads",
          file=sys.stderr)
    if not jobs:
        print("[taleez] the tenant is real and has nothing open — that is a "
              "zero, not a failure. A wrong slug is a 404 instead.",
              file=sys.stderr)
    for j in jobs:
        c = card(j, site, defs)
        if a.with_detail and c["slug"]:
            time.sleep(a.delay)
            c.update(ad_fields(c["slug"], fetch(c["url"])))
        print(json.dumps(c, ensure_ascii=False))
    print(f"[taleez] {len(jobs)} cards returned", file=sys.stderr)


def cmd_ad(a):
    print(json.dumps({"slug": a.slug, "url": AD_URL.format(a.slug),
                      **ad_fields(a.slug, fetch(AD_URL.format(a.slug)))},
                     ensure_ascii=False, indent=1))


def cmd_sitemap(a):
    """Every ad on the whole Taleez board, from the platform's own sitemap.

    **This file said "no tenant directory exists" until 2026-09-02.** There is
    one, at `https://taleez.com/sitemap-job.xml`: 14 221 `/apply/<slug>` URLs,
    `application/xml`, 1.8 MB, no key and no tenant needed. And `ad <slug>`
    reads any of them **without knowing which employer it belongs to**, which
    is what makes the sitemap a usable directory rather than a list of links.

    It is the board, not a search: there is no keyword or location filter here,
    so this is for enumerating and then reading, not for targeting.
    """
    raw = fetch("https://taleez.com/sitemap-job.xml")
    # The slug is not always the short opaque id: 296 of the 14 221 look like
    # `fmudc`, and the rest are long descriptive ones ending in the contract
    # type. Both forms answer `ad`. Matching only the short shape found 2% of
    # the board — measured while writing this.
    text = raw if isinstance(raw, str) else raw.decode("utf-8", "replace")
    slugs = re.findall(r"<loc>https://taleez\.com/apply/([^<]+)</loc>", text)
    seen, out = set(), []
    for sl in slugs:
        if sl not in seen:
            seen.add(sl)
            out.append(sl)
    print(f"[taleez] {len(out)} ad slugs in the platform sitemap. Read one "
          f"with `taleez.py ad <slug>` — no tenant needed. This is the whole "
          f"board with no filter, so pick before you fetch.", file=sys.stderr)
    if a.limit:
        out = out[:a.limit]
    for sl in out:
        print(json.dumps({"slug": sl,
                          "url": f"https://taleez.com/apply/{sl}"},
                         ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    j = sub.add_parser("jobs", help="every ad on one tenant, in one request")
    j.add_argument("--tenant", help="the host's first label")
    j.add_argument("--url", help="the careers URL, if that is what you have")
    j.add_argument("--with-detail", action="store_true",
                   help="read each ad page for the description — one request "
                        "per ad")
    j.add_argument("--delay", type=float, default=1.0,
                   help="seconds between ad reads (default 1)")
    j.set_defaults(func=cmd_jobs)

    sm = sub.add_parser("sitemap",
                        help="every ad slug on the platform, no tenant needed")
    sm.add_argument("--limit", type=int)
    sm.set_defaults(func=cmd_sitemap)

    d = sub.add_parser("ad", help="read one ad by slug")
    d.add_argument("slug")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
