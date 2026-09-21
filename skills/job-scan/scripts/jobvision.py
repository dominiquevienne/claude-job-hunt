#!/usr/bin/env python3
"""Jobvision (`jobvision.ir`, «بزرگترین سایت کاریابی ایران», Iran): an Angular site whose lists live behind query strings its rules refuse in writing — so the inventory is read where the site publishes it without one, its own job sitemap (`/sitemap/jobposts.xml`, UTF-16, 56 095 entries on 2026-09-21), and each advert page carries a JobPosting. Issue #626.

  jobvision.py jobs [--since YYYY-MM-DD] [--limit N] [--from <saved sitemap>]
  jobvision.py ad --url https://jobvision.ir/jobs/<id>/<slug>

THE RULES (read 2026-09-21): `user-agent: *` — `disallow: *?*` (**every URL
with a query string**), `*utm_*`, `*/Login/*`; `Allow: *.js`, `Allow: *.css`;
two sitemaps declared. **No query string is ever sent** — not one: the
adapter refuses to build a URL with one, before the gate. That is why the
search API is not used, although the bundle names its hosts
(`candidateapi.jobvision.ir`, `basedataapi.`, `web.`): a search there takes
its parameters in a query string.

THE ROUTE, MEASURED 2026-09-21 14:12–14:16 UTC, the declared client.
`/sitemap.xml` (UTF-16) declares four sitemaps; `/sitemap/jobposts.xml`
(23 009 777 B, UTF-16) is the advert inventory — **56 095 `<url>` entries**,
each with `<loc> https://jobvision.ir/jobs/<id>/<slug>` and two image `<loc>`
(the company logo and a generated card, never emitted), `<lastmod>` from
2026-07-23 to 2026-09-21. `/sitemap.jobs.xml.gz` (34 KB) is NOT the adverts:
5 271 category pages. The advert (`/jobs/1468042/…`, 169 113 B): a
`JobPosting` — `title`, `hiringOrganization.name` (+ logo, `sameAs`),
`jobLocation.address` (locality, region, country — **and a street and postal
code, withheld**), `baseSalary`, `industry`, `employmentType`,
`directApply`, `datePosted`, `description`.

THE COUNT, AND WHAT IT IS NOT. The sitemap is the SOURCE, so its 56 095 is
not an independent witness of itself — «a sum that matches its source is not
a check». The only outside anchors the site gives are its own rounded
«۴۸ هزار آگهی شغلی» (48 thousand) in the root's meta description on
2026-09-21 and the «56,781 آگهی» its root printed on 2026-09-17 (#600). The
run prints the emitted count, the sitemap's own entry count, the window of
`lastmod` it covers, and says which of the three is rounded.

WITHHELD: the street address and postal code of the advert, the employer's
logo and website, the apply route; texts scrubbed of e-mail addresses and
telephone numbers; `contacts_withheld` on every record. Country IR.
"""

import argparse
import datetime
import gzip
import html as htmlmod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _ldjson import label, one, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD, HOST, COUNTRY = "jobvision", "jobvision.ir", "IR"
BASE = f"https://{HOST}"
SITEMAP = BASE + "/sitemap/jobposts.xml"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
URL_RE = re.compile(r"<url>(.*?)</url>", re.S)
LOC_RE = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")
LASTMOD_RE = re.compile(r"<lastmod>\s*([^<\s]+)\s*</lastmod>")
AD_PATH_RE = re.compile(r"^/jobs/(\d+)/(.+)$")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?[\d۰-۹][\d۰-۹\s().\-]{7,}[\d۰-۹](?!\w)")
_PACE = Pace(HOST, own=2.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobvision] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    """(status, text) — this host only, NEVER a query string (refused in writing: `disallow: *?*`), the guard first, 2 s apart."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc.lower() != HOST or parts.query:
        die(f"{url}: not {HOST}, or a query string (the rules refuse `*?*`) — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml", "Accept-Language": "fa,en"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            raw = r.read()
            if raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            return r.getcode(), decode_text(raw, r.headers)
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def decode_text(raw, headers=None):
    """The sitemaps are UTF-16 WITH A BOM, the pages are UTF-8 — the BOM is read on the bytes, and
    everything else goes through `_decode.decode_body`, which reads the declaration and says when it
    has to fall back (no `errors="replace"` of our own, ever)."""
    if isinstance(raw, str):
        return raw
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    return decode_body(raw, headers)[0]


def text(markup):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", markup or "", flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def status_of(st, url):
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)


def parse_sitemap(body):
    """(entries, n_url) — one entry per <url> whose first advert <loc> is /jobs/<id>/<slug>; image <loc> are skipped, never emitted."""
    entries, n = [], 0
    for m in URL_RE.finditer(body or ""):
        n += 1
        seg = m.group(1)
        ad = None
        for loc in LOC_RE.findall(seg):
            p = urllib.parse.urlsplit(loc)
            am = AD_PATH_RE.match(urllib.parse.unquote(p.path))
            # the image <loc> of an entry are `/company/logo/…` and `/jobpost/image/…`, never `/jobs/<id>/…` —
            # measured on the 2026-09-21 sitemap: 56 095 `/jobs/` addresses, NONE with an image extension. So the
            # shape test below is what excludes them, and no extension filter is added: a filter that cannot fire
            # would be a guard that cannot redden (its mutation stayed green, which is how it was caught).
            if p.netloc.lower() == HOST and am:
                ad = (am.group(1), loc)
                break
        if not ad:
            continue
        lm = LASTMOD_RE.search(seg)
        entries.append({"id": ad[0], "url": ad[1], "lastmod": lm.group(1) if lm else None})
    return entries, n


def row(e):
    slug = urllib.parse.unquote(urllib.parse.urlsplit(e["url"]).path).split("/", 3)[-1]
    # the slug IS the site's own title, dashed — rendered readable, never invented; the real title is on the advert («ad»).
    # **And the KEY is built on what is EMITTED, not on what was read** (#626, 2026-09-21): an employer who writes a
    # telephone or an address in the title would put it in the slug, hence in the url, the id-slug and the rendered
    # title — where no scrub of the description would ever reach it. Measured the same day: 0 of 56 095 slugs carry
    # one. So the case is rare, not impossible: when it happens the slug and the title are scrubbed AND the address
    # emitted is the canonical one, `/jobs/<id>/x`, which the site serves identically (read twice, 169 119 B, the same
    # JobPosting) — the row then says `url_neutralised`, because a link that silently loses its title is a lie of another kind.
    title = " ".join(slug.replace("-", " ").split()) or None
    leaked = bool(MAIL_RE.search(slug) or PHONE_RE.search(slug.replace("-", " ")))
    rec = {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{e['id']}", "id": e["id"],
           "url": f"{BASE}/jobs/{e['id']}/x" if leaked else e["url"],
           "slug": scrub(slug) if leaked else slug, "title_from_slug": scrub(title) if leaked else title,
           "lastmod": e["lastmod"], "contacts_withheld": True}
    if leaked:
        rec["url_neutralised"] = "the site's own slug carried a contact — the canonical address is emitted instead"
    return rec


def cmd_jobs(a):
    if a.from_file:
        with open(a.from_file, "rb") as f:
            body = decode_text(f.read())
        where = f"the saved sitemap {a.from_file}"
    else:
        st, body = request(SITEMAP)
        status_of(st, SITEMAP)
        where = SITEMAP
    entries, n_url = parse_sitemap(body)
    if not entries:
        die(f"{where}: no /jobs/<id>/<slug> entry in the sitemap ({th(n_url)} <url> read) — not the advert inventory, or the sitemap changed shape.", EXIT_PARTIAL)
    kept, seen = [], set()
    for e in entries:
        if e["id"] in seen:
            continue
        if a.since and (not e["lastmod"] or e["lastmod"][:10] < a.since):
            continue
        seen.add(e["id"])
        kept.append(e)
        if a.limit and len(kept) >= a.limit:
            break
    for e in kept:
        print(json.dumps(row(e), ensure_ascii=False))
    lms = sorted(x["lastmod"][:10] for x in kept if x["lastmod"])
    window = f"lastmod {lms[0]} → {lms[-1]}" if lms else "no lastmod"
    note(f"{th(len(kept))} emitted from the site's own job sitemap ({th(len(entries))} advert entries in {th(n_url)} <url>), {window}"
         + (f"; --since {a.since}" if a.since else "") + (f"; --limit {a.limit} — a bounded read, not the inventory" if a.limit and len(kept) >= a.limit else "") + ".")
    note("the sitemap is the SOURCE, so its own count is not a witness of itself; the site's outside figures are its rounded «۴۸ هزار» (48 000) in the root's meta description and the «56,781 آگهی» its root printed on 2026-09-17 — both are the site's, one is rounded.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_PATH_RE.match(urllib.parse.unquote(parts.path or ""))
    if parts.netloc.lower() != HOST or not m or parts.query:
        die(f"{a.url!r}: not a Jobvision advert address (https://{HOST}/jobs/<id>/<slug>, no query string)")
    st, body = request(a.url)
    status_of(st, a.url)
    found = postings(body)
    if not found:
        die(f"{a.url}: no JobPosting in the page — gone, or the page changed shape.", EXIT_PARTIAL)
    p = found[0]
    addr = one(one(p.get("jobLocation")).get("address"))
    rec = {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{m.group(1)}", "id": m.group(1), "url": a.url,
           "title": label(p.get("title")), "company": label(p.get("hiringOrganization")),
           "place": label(addr.get("addressLocality")), "region": label(addr.get("addressRegion")),
           "country_as_written": label(addr.get("addressCountry")),
           "industry": label(p.get("industry")), "employment_type": label(p.get("employmentType")),
           "salary_as_written": p.get("baseSalary") if not isinstance(p.get("baseSalary"), (dict, list)) else label(one(p.get("baseSalary")).get("value")),
           "posted": label(p.get("datePosted")), "valid_through": label(p.get("validThrough")),
           "description": (scrub(text(label(p.get("description")) or "")) or "")[:20000] or None,
           "contacts_withheld": True}
    print(json.dumps(rec, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Jobvision (Iran) — the advert inventory from the site's own job sitemap (no query string is ever sent: the rules refuse `*?*`), the advert's JobPosting; street, postal code, logo and apply route withheld. Issue #626.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="/sitemap/jobposts.xml — one row an advert; «N emitted from the site's own job sitemap …»")
    s.add_argument("--since", metavar="YYYY-MM-DD", help="keep the adverts whose lastmod is on or after this day")
    s.add_argument("--limit", type=int, help="stop after N rows — a bounded read, said in the output")
    s.add_argument("--from", dest="from_file", metavar="FILE", help="a saved copy of the sitemap (23 MB live) instead of a fetch")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its address; JobPosting, description scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
