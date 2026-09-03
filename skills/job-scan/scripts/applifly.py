#!/usr/bin/env python3
"""Fetch ads from an Applifly tenant — where a query parameter you would strip
as tracking is the one that renders the page.

Applifly is a Swiss ATS. **Employers front it with their own vanity domain**
(`jobs.<employer>.ch`), so **the host never says Applifly; the path does** —
`/job/view-job.php` and `/jobs.php`, with `source=` in the query. That is the
same topology `shared/modules/ats-open-check.md` records for SuccessFactors,
and it is why this adapter takes `--host`.

  GET /jobs.php?language=<xx>&source=<any>              → the listing
  GET /job/view-job.php?id=<n>&language=<xx>&source=<any>  → one ad
  GET /sitemap.xml                                      → four landing pages
                                                          (no ad URLs)

**`source=` IS LOAD-BEARING, AND IT LOOKS EXACTLY LIKE TRACKING.** Measured on
`jobs.meanquest.ch`, 2026-09-03, on one ad id:

    ?id=1453                                  200      718 bytes   no ad
    ?id=1453&language=fr                      200      718 bytes   no ad
    ?id=1453&source=applifly                  200       99 bytes   no ad
    ?id=1453&language=fr&source=applifly      200  204 739 bytes   THE AD
    ?id=1453&language=fr&source=zzz           200  204 486 bytes   THE AD
    ?id=9999999&language=fr&source=applifly   302                  gone

**The value is irrelevant; the presence is not.** And the 718-byte body is not
an error page — it is a script that reads `document.referrer` and reloads the
same URL with `?source=<referrer>` appended. **A browser therefore always
sees the ad and a script never does**, while the status line says `200` every
time.

**So this is not client-side rendering and it does not need a browser** — which
is what it looks like, and what the first reading concluded. It needs one query
parameter. `shared/robots-policy.md`'s *decide by layer* is the rule: a browser
would fix it, so it appears to be a browser-layer problem, and the cause is one
layer above.

**AND THE ADVICE THAT WOULD BREAK IT IS ALREADY IN THIS REPOSITORY.**
`shared/boards/job-room.md` says of an `externalUrl`: *"Strip the query string
before storing or comparing."* Right for a dedup key, **fatal for a fetch**:
here the id lives in the query, and dropping the parameter that looks like
attribution turns a 204 KB ad into a 718-byte shell that answers `200`.

THE AD IS MICRODATA, NOT JSON-LD. `itemscope itemtype=".../JobPosting"` with
twenty `itemprop`s including coordinates — and **zero `ld+json` describing the
job**. A `grep JobPosting` says yes and a JSON-LD parser says no, on the same
complete posting. `_microdata.py` exists for this.

**The title comes from `<title>`, not from the microdata.** The page's
`<h1 itemprop="title">` wraps a hidden `Organization` block and a submit
button, so the spec-correct value reads *"Meanquest SA Cheffe / Chef de projet
IT Envoyer"*. Measured, not assumed.

ONE TENANT MEASURED. A web search for the template on other hosts returned
nothing, which **establishes nothing about how many exist** (#72): it is one
deployment, said as one deployment. Everything here that could be tenant-local
is marked.

Verified against the live site on **2026-09-03**.
"""

import argparse
import html as html_mod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _microdata import items as md_items
from _robots import verdict as robots_verdict
from _zero import zero_note

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

# The value never mattered on the measured tenant; the presence did. This one
# is honest about who is asking rather than impersonating a referrer.
SOURCE = "applifly"

EXIT_BROKEN, EXIT_GONE, EXIT_REFUSED = 2, 3, 7

# The shell, identified by what it *is* rather than by its length: a script
# that reloads the page with a `source` parameter taken from the referrer.
SHELL = re.compile(r"document\.referrer[\s\S]{0,400}?location\.href", re.I)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[applifly] {msg}", file=sys.stderr)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Return the redirect instead of following it."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    """Every request carries `language` and `source`. There is no way to
    forget them from here, which is the point."""

    def __init__(self, host, language="fr", delay=1.0):
        self.host = host.replace("https://", "").replace("http://", "").strip("/")
        self.language = language
        self.delay = delay
        # **Do not follow the redirect, because the redirect is the answer.**
        # An unknown id answers `302`; `urllib` follows it by default and
        # lands on a page that serves the referrer shell, so a dead ad comes
        # back looking like a parameter mistake — exit 2 where exit 3 was
        # true. Measured while writing this, and it is the `-L` trap of
        # `shared/plausible-and-false.md` in its silent, no-flag form.
        self._opener = urllib.request.build_opener(_NoRedirect)

    def url(self, path, **params):
        q = {"language": self.language, "source": SOURCE}
        q.update({k: v for k, v in params.items() if v is not None})
        return f"https://{self.host}{path}?" + urllib.parse.urlencode(q)

    def get(self, path, **params):
        u = self.url(path, **params)
        req = urllib.request.Request(u, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": f"{self.language},en;q=0.8",
        })
        try:
            with self._opener.open(req, timeout=45) as r:
                body = r.read().decode("utf-8", "replace")
                return r.getcode(), body, u
        except urllib.error.HTTPError as e:
            return e.code, "", u
        except (urllib.error.URLError, OSError) as e:
            die(f"{u}: {e}")

    def check_robots(self):
        v = robots_verdict(self.host)
        if not v["sweep"]:
            die(f"{self.host}: {v['reason']}", EXIT_REFUSED)
        return v


def guard(body, url):
    """Refuse to read a shell as an empty result.

    **This is the whole reason the adapter exists rather than a `curl`.** The
    shell answers `200`; treating it as "no ads" is the silent failure
    `shared/never-fail-silently.md` forbids.
    """
    if SHELL.search(body) and "view-job.php?id=" not in body:
        die(f"{url}: the referrer shell, not the page — {len(body)} bytes of "
            f"JavaScript that reloads with `?source=`. The request is missing "
            f"`language` or `source`, or this tenant changed the parameter "
            f"names. Nothing about the ads follows from this.")
    if len(body) < 400:
        die(f"{url}: {len(body)} bytes, too short to be a page. The measured "
            f"tenant returns 99 bytes for a `language` it does not know.")


def _og(body, prop):
    m = re.search(rf'<meta[^>]+property=["\']og:{prop}["\'][^>]+'
                  rf'content=["\']([^"\']*)["\']', body, re.I)
    return html_mod.unescape(m.group(1)).strip() if m else None


def _title(body):
    """From `<title>`, then `og:title` — never from the microdata `title`.

    The `<h1 itemprop="title">` wraps a hidden `Organization` and a submit
    button, so schema.org's own answer is *"<Employer> <Job title> Envoyer"*.
    """
    m = re.search(r"<title>(.*?)</title>", body, re.S | re.I)
    if m:
        return re.sub(r"\s+", " ", html_mod.unescape(m.group(1))).strip()
    return _og(body, "title")


def card(cli, ident, body, url, with_text=False):
    posts = md_items(body, "JobPosting")
    p = (posts[0].get("props") if posts else {}) or {}
    direct = (posts[0].get("props_direct") if posts else {}) or {}
    # **The address is on `PostalAddress`, not on `Place`** — `Place` carries
    # only `address` pointing at it — and `GeoCoordinates` is present as a
    # block on ads that have no coordinates in it. Measured on two ads: one
    # carried latitude and longitude, the other an empty block. **Count the
    # values, not the blocks.**
    org = md_items(body, "Organization")
    post = md_items(body, "PostalAddress")
    geo = md_items(body, "GeoCoordinates")
    g = (geo[0].get("props") if geo else {}) or {}
    addr = (post[0].get("props") if post else {}) or {}
    out = {
        "id": ident,
        "ledger_id": f"applifly:{cli.host}:{ident}",
        # The URL as it must be fetched, parameters included. Storing it
        # without them stores something that answers 200 and is not the ad.
        "url": url,
        "host": cli.host,
        "title": _title(body),
        "company": ((org[0].get("props") or {}).get("name") if org
                    else _og(body, "site_name")),
        "location_text": " · ".join(
            x for x in (addr.get("addressLocality"), addr.get("addressRegion"),
                        addr.get("addressCountry")) if x) or None,
        "street_address": addr.get("streetAddress"),
        "latitude": g.get("latitude"),
        "longitude": g.get("longitude"),
        # As printed by the site: `datePosted` is dd/mm/yyyy here while
        # `validThrough` is ISO. Not normalised, because one tenant is not a
        # platform and a wrong date is worse than a raw one.
        "posted_text": direct.get("datePosted") or p.get("datePosted"),
        "valid_through": direct.get("validThrough") or p.get("validThrough"),
        # **The site puts a contract type and a workload in one field.**
        # Measured: `CDI` on one ad and `Temps plein = 100%` on the next.
        # Emitted as printed rather than parsed into two — one tenant is not
        # a platform, and inventing a split here would be a guess.
        "employment_type": direct.get("employmentType"),
        "industry": direct.get("industry"),
        "occupational_category": direct.get("occupationalCategory"),
        "has_microdata": bool(posts),
        "description_chars": len(p.get("description") or ""),
    }
    if with_text:
        out["description"] = p.get("description")
    return out


def cmd_search(a):
    cli = Client(a.host, a.language, a.delay)
    v = cli.check_robots()
    if v["state"] != "read":
        note(f"robots.txt: {v['reason']}")
    code, body, url = cli.get("/jobs.php")
    if code != 200:
        die(f"{url}: HTTP {code}")
    guard(body, url)
    ids, seen = [], set()
    for m in re.finditer(r"view-job\.php\?id=(\d+)(-[a-z0-9-]*)?", body, re.I):
        if m.group(1) not in seen:
            seen.add(m.group(1))
            ids.append(m.group(1))
    if not ids:
        note(zero_note("applifly", extra=(
            "The listing answered 200 and carried no `view-job.php?id=` link. "
            "On this platform that is either an empty board or a shell — "
            "`guard()` ruled out the shell, so it is the board.")))
        return
    kept = 0
    for ident in ids[:a.limit] if a.limit else ids:
        code, ad, u = cli.get("/job/view-job.php", id=ident)
        if code in (301, 302, 303, 307, 308):
            note(f"id {ident}: HTTP {code} — the id no longer resolves. "
                 f"Skipped.")
            continue
        if code != 200:
            note(f"id {ident}: HTTP {code}. Skipped.")
            continue
        guard(ad, u)
        print(json.dumps(card(cli, ident, ad, u, a.with_text),
                         ensure_ascii=False))
        kept += 1
        time.sleep(a.delay)
    note(f"{kept} ad(s) of {len(ids)} linked from the listing.")
    note("every URL emitted carries `language` and `source`: without them the "
         "same URL answers 200 with a referrer shell and no ad.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    q = urllib.parse.parse_qs(parts.query)
    ident = (q.get("id") or [""])[0].split("-")[0]
    if not ident.isdigit():
        die(f"{a.url}: no numeric `id` in the query. On this platform the id "
            f"is in the query string and nowhere else — a URL stripped of its "
            f"parameters is not a shorter URL, it is a different page.")
    cli = Client(parts.netloc, (q.get("language") or [a.language])[0], a.delay)
    cli.check_robots()
    code, body, url = cli.get(parts.path, id=ident)
    if code in (301, 302, 303, 307, 308):
        die(f"{a.url}: HTTP {code} — this id does not resolve. On the measured "
            f"tenant a live id answers 200 and an unknown one redirects, so "
            f"this is a real negative and not a silence.", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE)
    guard(body, url)
    print(json.dumps(card(cli, ident, body, url, a.with_text),
                     ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="the tenant's listing, then each ad")
    s.add_argument("--host", required=True,
                   help="the employer's vanity domain, e.g. jobs.acme.ch")
    s.add_argument("--language", default="fr")
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=1.0)
    s.add_argument("--with-text", action="store_true", dest="with_text")
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="one ad by URL")
    d.add_argument("--url", required=True)
    d.add_argument("--language", default="fr")
    d.add_argument("--delay", type=float, default=1.0)
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
