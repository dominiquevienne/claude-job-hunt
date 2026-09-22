#!/usr/bin/env python3
"""IranTalent (`www.irantalent.com`, Iran): «Recruitment & Jobs for Professionals» — the board's own pager lives behind a query string its rules refuse in writing (`Disallow: *?*`), so the walk goes through the 6 726 FILTER pages the site publishes as plain paths in its own sitemap, and the union is compared to the «آگهی استخدام 1744 نتیجه» the list states. Issue #628.

  irantalent.py jobs [--filters N | --all-filters] [--from FILE]
  irantalent.py ad --url https://www.irantalent.com/job/<slug>/<id>

THE RULES (read 2026-09-22 08:09 UTC). Three named agents (LinkedInBot,
TelegramBot, WhatsAppBot) are ALLOWED `*?*`; the `*` group — ours — is
refused it: `Disallow: *?*`, `*utm_*`, `/jobs-search/`, `/jobs-search*`,
`/*result`, `/*?keyword=`, `/*job-fair`, `/admin-panel/`. **Being named and
allowed elsewhere changes nothing for us: the group that applies to
`Claude-User` is `*`, and no query string is ever sent.** `/jobs`, the
filter paths `/jobs/<filter>-jobs` and `/job/<slug>/<id>` carry none.

THE ROUTE, MEASURED 2026-09-22 08:09–08:20 UTC, the declared client.
`/jobs` (200, 929 874 B) states **«آگهی استخدام 1744 نتیجه»** — 1 744
results — and renders 32 advert links; **no pager link exists in the HTML**
(an Angular front) and `/jobs/page/2`, `/jobs/2` answer a page with no
advert: the rest is behind the query string the rules refuse. The site's own
sitemap index (`/sitemap.xml`) declares `fa|en/sitemap.xml` (pages),
`company/sitemap.xml` and **`fa/job-filter/sitemap.xml` — 6 726 filter
pages, all plain paths under `/jobs/`** (banking-investment-jobs,
agriculture-…-jobs …), each rendering its own adverts (22 and 4 on the two
read). The walk unions those pages' advert ids and prints the union beside
the stated 1 744; **a bounded walk says so and is not compared** («a BOUNDED
walk of N filter pages of 6 726»). The advert (`/job/<slug>/<id>`, 397 901 B)
carries a `JobPosting` — `title`, `identifier.value`, `datePosted`,
`employmentType`, `hiringOrganization.name` (+ logo, `sameAs`),
`jobLocation.address` (region, country — **and a street, withheld**),
`baseSalary` — with **`description: null` in the JSON-LD**: the advert's text lives in the
Angular transferred state under `role_description` (a `null` there is an
empty FIELD, not an advert without a text), and that is what is read.

WITHHELD: the street address, the employer's logo, the application route;
e-mail addresses and telephone numbers in every text (Persian digits
included); `contacts_withheld` on every record. **The key is the id the site
puts at the end of its own address**, never the slug: an ASCII fold of a
Persian title is empty and collides (50 097 of 56 095 measured on Jobvision
the same week). Country IR.
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
from _ldjson import label, one, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD, HOST, COUNTRY = "irantalent", "www.irantalent.com", "IR"
BASE = f"https://{HOST}"
LISTING = BASE + "/jobs"
FILTER_SITEMAP = BASE + "/fa/job-filter/sitemap.xml"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
STATED_RE = re.compile(r"آگهی استخدام\s+([\d,۰-۹،]+)\s+نتیجه")
AD_HREF_RE = re.compile(r'href="(/job/([^"/?#]+)/(\d+))"')
LOC_RE = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")
AD_PATH_RE = re.compile(r"^/job/([^/]+)/(\d+)/?$")
FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?[\d۰-۹][\d۰-۹\s().\-]{7,}[\d۰-۹](?!\w)")
_PACE = Pace(HOST, own=2.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[irantalent] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def fa_int(s):
    if not s:
        return None
    d = re.sub(r"[^0-9]", "", s.translate(FA_DIGITS))
    return int(d) if d else None


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    """(status, text) — this host only, NEVER a query string (`Disallow: *?*` for the `*` group, which is ours), the guard first, 2 s apart."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc.lower() != HOST or parts.query:
        die(f"{url}: not {HOST}, or a query string (the `*` group is refused `*?*` — being named elsewhere is not our group) — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml", "Accept-Language": "fa,en"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", markup or "", flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ").replace("‌", " ")
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


def ads_of(body):
    """[(id, slug, url)] — the advert links of a rendered page, each one once, in order."""
    out, seen = [], set()
    for href, slug, jid in AD_HREF_RE.findall(body or ""):
        if jid in seen:
            continue
        seen.add(jid)
        out.append((jid, slug, BASE + href))
    return out


def row(jid, slug, url, via):
    return {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{jid}", "id": jid, "url": url,
            "slug": slug, "title_from_slug": " ".join(slug.replace("-", " ").split()) or None,
            "seen_on": via, "contacts_withheld": True}


def cmd_jobs(a):
    seen, out = set(), []
    st, body = request(LISTING)
    status_of(st, LISTING)
    # the count and its word sit in two different tags («آگهی استخدام» in an <h1>, «1744 نتیجه» in a <small>),
    # so the page's TEXT is what states it, not its markup — a search on the raw HTML finds nothing (2026-09-22)
    m = STATED_RE.search(text(body) or "")
    stated = fa_int(m.group(1)) if m else None
    first = ads_of(body)
    if not first:
        die(f"{LISTING}: no advert link in the answer — not the list, or the page changed shape.", EXIT_PARTIAL)
    for jid, slug, url in first:
        seen.add(jid)
        out.append(row(jid, slug, url, "/jobs"))
    filters, walked = [], 0
    if a.from_file:
        with open(a.from_file, "rb") as f:
            filters = [l for l in LOC_RE.findall(decode_body(f.read())[0]) if "/jobs/" in l]
    else:
        st, sm = request(FILTER_SITEMAP)
        status_of(st, FILTER_SITEMAP)
        filters = [l for l in LOC_RE.findall(sm) if "/jobs/" in l]
        if not filters:
            die(f"{FILTER_SITEMAP}: no /jobs/ filter address in the sitemap — the walk has no route.", EXIT_PARTIAL)
        limit = len(filters) if a.all_filters else max(0, a.filters if a.filters is not None else 20)
        for url in filters[:limit]:
            st, page = request(url)
            if st == 404:
                continue
            status_of(st, url)
            walked += 1
            for jid, slug, ad in ads_of(page):
                if jid not in seen:
                    seen.add(jid)
                    out.append(row(jid, slug, ad, url[len(BASE):]))
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    bounded = not a.all_filters and walked < len(filters)
    head = f"{th(n)} emitted — the list itself renders {th(len(first))}, and {th(walked)} of {th(len(filters))} filter pages were walked"
    if stated is None:
        note(head + "; the list stated no count.")
        sys.exit(EXIT_PARTIAL)
    if bounded:
        note(head + f"; the site states {th(stated)} — a BOUNDED walk, NOT compared to it (the pager is behind a query string the rules refuse; --all-filters walks the {th(len(filters))}).")
        return
    note(head + f"; the site states {th(stated)}: " + ("equal." if n == stated else f"{th(abs(stated - n))} " + ("short." if stated > n else "more emitted than stated.")))
    if n < stated:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_PATH_RE.match(urllib.parse.unquote(parts.path or ""))
    if parts.netloc.lower() != HOST or not m or parts.query:
        die(f"{a.url!r}: not an IranTalent advert address (https://{HOST}/job/<slug>/<id>, no query string)")
    url = f"{BASE}/job/{m.group(1)}/{m.group(2)}"
    st, body = request(url)
    status_of(st, url)
    found = postings(body)
    if not found:
        die(f"{url}: no JobPosting in the page — gone, or the page changed shape.", EXIT_PARTIAL)
    p = found[0]
    addr = one(one(p.get("jobLocation")).get("address"))
    sal = one(p.get("baseSalary"))
    desc = label(p.get("description"))
    if not desc:
        # **The JSON-LD says `description: null` and the page is an Angular shell: the advert's text lives in the
        # transferred state, under `role_description` (HTML, unicode-escaped). A `null` in the JSON-LD is the
        # board's own field being empty, NOT an advert without a text** — and emitting nothing here would have
        # said the second while measuring the first.
        dm = re.search(r'"role_description":"((?:[^"\\]|\\.)*)"', body)
        desc = text(json.loads('"' + dm.group(1) + '"')) if dm else None
    rec = {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{m.group(2)}", "id": m.group(2), "url": url,
           "title": scrub(label(p.get("title"))), "company": scrub(label(p.get("hiringOrganization"))),
           "place": scrub(label(addr.get("addressRegion")) or label(addr.get("addressLocality"))),
           "country_as_written": label(addr.get("addressCountry")),
           "employment_type": label(p.get("employmentType")), "posted": label(p.get("datePosted")),
           "board_identifier": label(one(p.get("identifier")).get("value")) if p.get("identifier") else None,
           "salary_currency": label(sal.get("currency")), "salary_value": sal.get("value") if not isinstance(sal.get("value"), (dict, list)) else label(one(sal.get("value")).get("value")),
           "description": (scrub(text(desc)) or "")[:20000] or None,
           "contacts_withheld": True}
    print(json.dumps(rec, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="IranTalent (Iran) — the list and the site's own filter pages, no query string ever sent; the union against the stated count; street, logo and apply route withheld. Issue #628.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="/jobs then the filter pages of the site's own sitemap; «N emitted … the site states M»")
    s.add_argument("--filters", type=int, help="how many filter pages to walk (default 20 — a bounded walk, said in the output)")
    s.add_argument("--all-filters", action="store_true", help="walk every filter page the sitemap declares")
    s.add_argument("--from", dest="from_file", metavar="FILE", help="a saved copy of the filter sitemap")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its address; JobPosting + the page's text, scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
