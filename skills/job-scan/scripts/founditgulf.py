#!/usr/bin/env python3
"""foundit Gulf (`www.founditgulf.com`, formerly Monster Gulf) — the Gulf + Egypt board, read through its active-jobs sitemaps and the JobPosting every advertisement carries.

  founditgulf.py sitemap [--host www.founditgulf.com|www.foundit.com.ph] [--limit N] [--no-site-total]
  founditgulf.py ad --url <advertisement URL>            # the host is read from the URL

TWO HOSTS, ONE STACK — 2026-09-13 (#233, lot 8): `www.foundit.com.ph`, the
Philippine franchise, publishes the same hand-written group closing `/jobs/`
and `/search/` and the same `/xmlsitemap/` index (37 children, two
`active-jobs` files, a `todays` file); the adapter takes it as a second host,
never reads those two paths on it either, and keys its rows `foundit-ph:`.

THE ACTIVE-JOBS SITEMAPS ARE THE ROUTE — AND `/jobs/`, `/search/` ARE NEVER TOUCHED

The rules carry a group written by hand — `GPTBot`, `ClaudeBot`, `CCBot`,
`Bytespider`, `Meta-ExternalAgent`, `Google-Extended`: `Allow: /`,
`Disallow: /jobs/`, `/search/`. `Claude-User` is not in it and falls under
`*` (owner's decision of 2026-09-07: the group naming ClaudeBot does not
bind Claude-User), **and this adapter still reads neither `/jobs/` nor
`/search/`** — the pilot's condition (#233, lot 4): the enumeration is the
sitemap index, the advertisement is its own page. The line «refusal written
by hand naming ClaudeBot» stays on the card for the owner.

`/xmlsitemap/sitemap-index.xml` names 49 children; the ones matching
`active-jobs-sitemap<n>.xml.gz` hold the advertisements — three files,
24 975 + 24 954 + 9 001 = **58 930 `<loc>` of the shape `/job/<slug>-<id>`,
58 930 distinct ids** on 2026-09-12 11:23 UTC. The `<lastmod>` are a
rebuild stamped by the second (36 values, all 2026-09-11 13:06–13:07): not
a date, no `--since`. `todays-jobs-sitemap.xml` (1 041 that day) is read as
the second document — every one of its ids is expected among the active ones,
and the adapter says how many are not. The root's «Over 800,000+ jobs to
explore» is a network slogan, printed and named as such, never compared.
`expired-jobs-sitemap*` is refused to `*` and never asked for.

EVERY ADVERTISEMENT CARRIES A JobPosting IN JSON-LD — `title`, `description`
(HTML), `identifier.value` (the id, an integer), `datePosted` and
`validThrough` **as `DD-MM-YYYY`** (emitted as published in `*_as_published`
and as ISO beside), `employmentType` («Full time»), `hiringOrganization`
(`sameAs` is the name again, not a URL), `jobLocation.address` with
**`addressCountry` as an ISO-2 code** — the country is read from the
advertisement, EG on a fifth of the board — `experienceRequirements.monthsOfExperience`,
`occupationalCategory`, `industry` (a list), `skills` (a list).

THE RULES for `*` refuse dashboards, middleware, `/pwa/`, `/trex/*/` and the
expired-jobs sitemaps; no `Crawl-delay` (2 s is ours); `certain: True`;
`identity()` answers `claude-user`, `verdict()` sweeps. Measured 2026-09-12
11:18–11:41 UTC (#233, lot 4).
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
from _ldjson import absent_reason, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _sitemap import locs as sitemap_locs, maybe_gunzip
from _ua import UA
from _zero import empty_first_page

# **Two hosts, one stack, one hand-written refusal each** (#233, lot 8: the
# Philippine franchise publishes the same six-agent group closing /jobs/ and
# /search/, and the same /xmlsitemap/ index). The source key names the host.
HOSTS = {"www.founditgulf.com": "founditgulf", "www.foundit.com.ph": "foundit-ph"}
HOST = "www.founditgulf.com"                 # the default; `--host` chooses, `ad` reads it from the URL
ACTIVE_RE = re.compile(r"/xmlsitemap/active-jobs-sitemap\d+\.xml(?:\.gz)?$")
AD_RE = re.compile(r"^https://(www\.founditgulf\.com|www\.foundit\.com\.ph)/job/[^/?#]*-(\d+)/?$")
DMY_RE = re.compile(r"^(\d{2})-(\d{2})-(\d{4})$")
# «Over 800,000+ jobs to explore» on the Gulf root, «100,000+ Jobs in Philippines» on the Philippine one — slogans both
SLOGAN_RE = re.compile(r"(?:Over\s+)?([\d,]+)\+\s+jobs", re.I)


def urls(host):
    base = "https://" + host
    return base, base + "/xmlsitemap/sitemap-index.xml", base + "/xmlsitemap/todays-jobs-sitemap.xml"


BASE, INDEX, TODAY = urls(HOST)
NEVER = ("/jobs/", "/search/")   # the hand-written refusal's paths — not read by this adapter, under any token

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[founditgulf] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    path = full_path(parts)
    if parts.netloc in HOSTS and any(path.startswith(p) for p in NEVER):
        # **Not a rules verdict — a promise.** The rules permit these to
        # claude-user; the adapter declines them so that the hand-written
        # refusal is honoured in substance while the owner decides.
        die(f"{url}: this adapter does not read {path.split('/')[1]}/ — the paths the operator closed by hand", EXIT_REFUSED)
    a = robots_allowed(parts.netloc, path)
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACES = {}


def get(url, binary=False):
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()   # no Crawl-delay declared on either host; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.5",
        "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            raw = maybe_gunzip(r.read())
            return r.getcode(), (raw if binary else decode_body(raw, r.headers)[0])
    except urllib.error.HTTPError as e:
        return e.code, (b"" if binary else "")
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"[ \t]+", " ", htmlmod.unescape(markup)).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def iso(dmy):
    """`10-09-2026` → `2026-09-10`; anything else comes back unchanged."""
    m = DMY_RE.match((dmy or "").strip())
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else dmy


def ids_of(xml):
    out, unmatched = [], 0
    for loc in sitemap_locs(xml):
        m = AD_RE.match(loc.strip())
        if m:
            out.append((m.group(2), loc.strip()))
        else:
            unmatched += 1
    return out, unmatched


def cmd_sitemap(a):
    host = getattr(a, "host", None) or HOST
    if host not in HOSTS:
        die(f"{host}: not a foundit host this adapter knows — one of {', '.join(HOSTS)}")
    src = HOSTS[host]
    BASE, INDEX, TODAY = urls(host)
    code, index = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}", EXIT_PARTIAL)
    children = sitemap_locs(index)
    active = [u for u in children if ACTIVE_RE.search(u.strip())]
    if not active:
        die(f"{INDEX} names {len(children)} children and none matches active-jobs-sitemap<n>.xml.gz — the enumeration moved; nothing here says the board is empty.", EXIT_PARTIAL)
    rows, seen, raw, unmatched = [], set(), 0, 0
    for u in active:
        code, xml = get(u.strip())
        if code != 200:
            die(f"{u}: HTTP {code} — one of {len(active)} active files; the count below would be short and is not printed.", EXIT_PARTIAL)
        pairs, un = ids_of(xml)
        raw += len(pairs) + un
        unmatched += un
        for ident, loc in pairs:
            if ident in seen:
                continue
            seen.add(ident)
            rows.append({"source": src, "ledger_id": f"{src}:{ident}", "id": ident, "url": loc})
    if raw == 0:
        die(empty_first_page("founditgulf", "", "<loc>", where=active[0]), EXIT_PARTIAL)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{len(active)} active-jobs file(s) of {len(children)} index children; {raw} <loc>, {raw - unmatched} of the "
         f"advertisement shape, {unmatched} not; **{th(len(rows))} distinct advertisement id(s)**"
         + (f" ({a.limit} printed under --limit)" if a.limit else "")
         + ". The <lastmod> is a rebuild stamp, not a date; `country` is read per advertisement by `ad`.")
    if a.no_site_total:
        return
    code, xml = get(TODAY)
    if code != 200:
        note(f"{TODAY}: HTTP {code} — no second document this run.")
        return
    today, _ = ids_of(xml)
    tid = {i for i, _u in today}
    missing = tid - seen
    if not tid:
        note(f"{TODAY} lists no advertisement this run — no second document.")
    elif not missing:
        note(f"today's sitemap lists {th(len(tid))}, {th(len(tid))} of them among the {th(len(rows))} active — consistent.")
    else:
        note(f"today's sitemap lists {th(len(tid))} and **{th(len(missing))} of them are NOT among the {th(len(rows))} active** — "
             f"the two files disagree; the active count may be short.")
    code, page = get(BASE + "/")
    m = SLOGAN_RE.search(page or "") if code == 200 else None
    if m:
        note(f"the root says «{m.group(1)}+ jobs» — a slogan, not this board's count; "
             f"the sitemaps hold {th(len(rows))}.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected https://<host>/job/<slug>-<id> on one of {', '.join(HOSTS)}")
    host, ident = m.group(1), m.group(2)
    src = HOSTS[host]
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    found = postings(body)
    if not found:
        why = absent_reason(body)
        if getattr(why, "our_fault", False):
            die(f"{a.url}: {why} **The page announces a JobPosting and this read none.**")
        die(f"{a.url}: {why}", EXIT_PARTIAL)
    d = found[0]
    org = d.get("hiringOrganization") or {}
    loc = d.get("jobLocation") or {}
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
    exp = d.get("experienceRequirements") or {}
    months = exp.get("monthsOfExperience") if isinstance(exp, dict) else None
    ind = d.get("industry")
    skills = d.get("skills")
    country = (addr.get("addressCountry") or "").strip() if isinstance(addr, dict) else ""
    print(json.dumps({
        "source": src,
        # the ISO-2 the advertisement carries — AE, SA, QA, KW, BH, OM, EG on the Gulf host on 2026-09-12 — never assumed from the board
        "country": country or None,
        "ledger_id": f"{src}:{ident}", "id": ident, "url": a.url,
        "title": text(d.get("title")),
        "employer": (org.get("name") if isinstance(org, dict) else None),
        "employment_type": d.get("employmentType") or None,
        "city": (text(addr.get("addressLocality")) or None) if isinstance(addr, dict) else None,
        "region": (text(addr.get("addressRegion")) or None) if isinstance(addr, dict) else None,
        "posted": iso(d.get("datePosted")),
        "posted_as_published": d.get("datePosted"),            # DD-MM-YYYY on the site
        "valid_through": iso(d.get("validThrough")),
        "valid_through_as_published": d.get("validThrough"),
        "months_of_experience": months if isinstance(months, int) else None,
        "category": d.get("occupationalCategory") or None,
        "industries": ind if isinstance(ind, list) else ([ind] if ind else []),
        "skills": skills if isinstance(skills, list) else ([skills] if skills else []),
        "direct_apply": d.get("directApply"),
        "description": text(d.get("description"))[:20000], "language": "en",
    }, ensure_ascii=False))
    note("dates are the site's `DD-MM-YYYY` in `*_as_published` and ISO beside; `country` is the advertisement's own `addressCountry`.")


def main():
    p = argparse.ArgumentParser(description="foundit Gulf — the Gulf + Egypt board, through its active-jobs sitemaps and the JSON-LD its pages carry; /jobs/ and /search/ are never read.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="distinct advertisement ids — the index + its active files (4 on 2026-09-12), + today's file and the root for the second document")
    s.add_argument("--host", default=HOST, help="www.founditgulf.com (default) or www.foundit.com.ph")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one advertisement, from its JSON-LD — the country from the advertisement")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
