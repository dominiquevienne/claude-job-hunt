#!/usr/bin/env python3
"""Werkstraat (`werkstraat.com`) — «De vacaturesite van Suriname», a WordPress job board (a Noo JobMonster theme): the list `/jobs/page/N/` serves ten cards a page on the server with the site's own count («Showing 1–10 of 341 jobs»), and each ad is a page with the same meta block and a «Functieomschrijving» body, no JobPosting JSON-LD; the count printed beside every walk; the texts scrubbed — and a free-posting board is polluted, so the employer field is scrubbed too. Issue #445.

  werkstraat.py list [--pages N]     the cards of /jobs/ … /jobs/page/N/ until the pager's last page (35 pages on the day, 2 s apart), the stated count beside them
  werkstraat.py ad --url <https://werkstraat.com/jobs/<slug>/>

THE RULES. `User-agent: *` — `Disallow: /wp-admin/`, `Allow: /wp-admin/admin-ajax.php`; nothing
else. `/wp-admin/`, `/wp-json/`, `/member/`, `/xmlrpc.php` are never sent (refused before the
gate); no Crawl-delay, 2 s is ours.

THE LIST. `/jobs/` (200, ~211 KB) prints «Showing 1–10 of 341 jobs» and ten `<article class="…
noo_job … post-<id>">` cards: the title, the employer (`company-name`, a link to `/companies/
<slug>/`), microdata `hiringOrganization`, `job-location` links (several: «Paramaribo, Suriname»,
«Remote, vanuit Suriname»), `job-category` links («Communicatie - Klantenservice/Callcenter -
Media»), `job-type` («Freelance», «Full-time»), a `<time datetime>`; the pager `/jobs/page/2/ …
/jobs/page/35/` (the last page read from the pager's largest number). THE AD. `/jobs/<slug>/` (200,
~129 KB): `<h1 class="job-title">`, the same meta block with the expiry beside the date («september
15, 2026 - oktober 5, 2026»), `<div class="job-desc">` with «Functieomschrijving»; no JobPosting.
**A FREE-POSTING BOARD, POLLUTED: on the day nine of the ten newest cards were spam (supplement
«reviews», essay mills), posted under an e-mail address as the employer's name.** The adapter emits
what the site lists and does not judge it — the categories, the type and the locations are the
site's own labels, a reader filters on them; **the employer's name is scrubbed like a text (an
e-mail address as a name becomes «[e-mail withheld]»), the body is scrubbed of e-mail addresses and
Surinamese telephone numbers; `contacts_withheld` on every record; the application («Solliciteer»,
a member account) never touched.**

Measured 2026-09-16 12:10–12:12 UTC by the declared client, the guard on the exact path: robots 200
(67 B); `/` 140 088 B; `/jobs/` 210 774 B, «341», 10 cards, pager to 35; `/jobs/page/2/` 211 210 B,
«Showing 11–20 of 341»; the ad 128 520 B.
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

HOST = "werkstraat.com"
LIST = f"https://{HOST}/jobs/"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+?597[\s\-]?)?(?:[678]\d{2}[\s\-]?\d{4}|[2345]\d{2}[\s\-]?\d{3})(?!\d)")   # Surinamese 7-digit mobiles (6/7/8…) and 6-digit landlines, with or without +597
AD_RE = re.compile(r"^/jobs/([a-z0-9\-]+)/?$")
REFUSED_RE = re.compile(r"^/(?:wp-admin|wp-json|member|xmlrpc\.php|wp-login\.php)(?:/|$)")
CARD_RE = re.compile(r'<article class="[^"]*\bnoo_job\b[^"]*\bpost-(\d+)\b[^"]*"[^>]*>(.*?)</article>', re.S)
TITLE_RE = re.compile(r'<h5 class="[^"]*loop-job-title[^"]*">\s*<a href="(https://werkstraat\.com/jobs/[^"]+)"[^>]*>(.*?)</a>', re.S)
COMPANY_RE = re.compile(r'<a href="https://werkstraat\.com/companies/([^"/]+)/"\s*>\s*<span class="company-name">(.*?)</span>', re.S)
COMPANY_META_RE = re.compile(r'<meta content="([^"]*)" itemprop="name">')
COMPANY_LINK_RE = re.compile(r'href="https://werkstraat\.com/companies/([^"/]+)/"')
LOC_RE = re.compile(r'<span class="job-location"[^>]*>(.*?)(?=<span class="job-(?:category|type|date)"|<div class="job-tools)', re.S)
CAT_RE = re.compile(r'<span class="job-category">(.*?)(?=<span class="job-(?:type|date)"|<div class="job-tools)', re.S)
TYPE_RE = re.compile(r'<span class="job-type">.*?<span>(.*?)</span>', re.S)
TIME_RE = re.compile(r'<time class="entry-date" datetime="([^"]+)"[^>]*>(.*?)</time>', re.S)
LINKS_RE = re.compile(r'<a [^>]*>\s*<span[^>]*>(.*?)</span>\s*</a>|<a [^>]*>(.*?)</a>', re.S)
COUNT_RE = re.compile(r"Showing\s+\d+(?:&ndash;|–|-)\d+\s+of\s+(\d[\d,\.]*)\s+jobs")
PAGE_RE = re.compile(r'href="https://werkstraat\.com/jobs/page/(\d+)/"')
H1_RE = re.compile(r'<h1 class="[^"]*job-title[^"]*"[^>]*>(.*?)</h1>', re.S)
DESC_RE = re.compile(r'<div class="job-desc"\s*>(.*?)</div>\s*(?:<div class="job-tools|<div class="noo-job-attachments|<div id="apply|<div class="apply)', re.S)
MONTHS_NL = {m: i for i, m in enumerate(("januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"), 1)}
EXPIRY_RE = re.compile(r"-\s*([a-z]+)\s+(\d{1,2}),\s*(\d{4})")

_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written; 2 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[werkstraat] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    if REFUSED_RE.search(urllib.parse.urlsplit(url).path):
        die(f"{url}: the admin, the REST API and the member area — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "nl"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def links(markup):
    out = []
    for a, b in LINKS_RE.findall(markup or ""):
        v = text(a or b)
        if v:
            out.append(v)
    return out


def stated(body):
    """The count the list prints — «Showing 1–10 of 341 jobs» — or `None`."""
    m = COUNT_RE.search(htmlmod.unescape(body or ""))
    return int(re.sub(r"\D", "", m.group(1))) if m else None


def meta(inner):
    """The meta block a card and an ad share: company, locations, categories, type, dates."""
    comp = COMPANY_RE.search(inner)
    cm = COMPANY_META_RE.search(inner)
    loc = LOC_RE.search(inner)
    cat = CAT_RE.search(inner)
    ty = TYPE_RE.search(inner)
    tm = TIME_RE.search(inner)
    exp = EXPIRY_RE.search(text(tm.group(2)) or "") if tm else None
    valid = None
    if exp and exp.group(1).lower() in MONTHS_NL:
        valid = f"{exp.group(3)}-{MONTHS_NL[exp.group(1).lower()]:02d}-{int(exp.group(2)):02d}"
    name = text(comp.group(2)) if comp else (htmlmod.unescape(cm.group(1)).strip() if cm else None)
    return {
        "company": scrub(name), "company_profile": (f"https://{HOST}/companies/{comp.group(1)}/" if comp else (f"https://{HOST}/companies/{cl.group(1)}/" if (cl := COMPANY_LINK_RE.search(inner)) else None)),
        "locations": links(loc.group(1)) or None if loc else None, "categories": links(cat.group(1)) or None if cat else None,
        "job_type": text(ty.group(1)) if ty else None,
        "posted": (tm.group(1) or "")[:10] or None if tm else None, "valid_through": valid,
    }


def cards(body):
    out = []
    for nid, inner in CARD_RE.findall(body):
        t = TITLE_RE.search(inner)
        if not t:
            continue
        m = AD_RE.match(urllib.parse.urlsplit(t.group(1)).path)
        rec = {"source": "werkstraat", "country": "SR", "ledger_id": f"werkstraat:{nid}", "id": nid, "url": t.group(1), "slug": m.group(1) if m else None, "title": text(t.group(2))}
        rec.update(meta(inner))
        rec.update({"contacts_withheld": True, "language": "nl"})
        out.append(rec)
    return out


def cmd_list(a):
    out, seen, first_ids, pages, last, total = [], set(), None, 0, 0, None
    n = 1
    while True:
        url = LIST if n == 1 else f"{LIST}page/{n}/"
        code, body = request(url)
        if code == 404:
            break
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if n == 1:
            total = stated(body)
            if total is None:
                die(f"{url}: 200 and no «Showing … of N jobs» in the page — the template changed; not an empty market", EXIT_PARTIAL)
            last = max((int(x) for x in PAGE_RE.findall(body)), default=1)
        cs = cards(body)
        if not cs:
            die(f"{url}: 200 and no card — the template changed; not an empty page", EXIT_PARTIAL)
        ids = [c["id"] for c in cs]
        if first_ids is None:
            first_ids = ids
        elif ids == first_ids:
            die(f"{url}: the same cards as page 1 — the pager is not honoured; stopped", EXIT_PARTIAL)
        new = 0
        for c in cs:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            out.append(c)
            new += 1
        pages += 1
        if new == 0 or n >= last or (a.pages and pages >= a.pages):
            break
        n += 1
    for c in out:
        print(json.dumps(c, ensure_ascii=False))
    emitted = len(out)
    if a.pages and pages >= a.pages and n < last:
        note(f"{th(emitted)} emitted from {pages} page(s) of the {last} the pager names; the site states {th(total)} — walked by request (--pages), not a shortfall.")
    else:
        verdict = "equal" if emitted == total else (f"{th(total - emitted)} short" if emitted < total else f"{th(emitted - total)} more emitted")
        note(f"{th(emitted)} emitted from {pages} page(s), the site states {th(total)} — {verdict}.")
    note("cards only, as the site lists them (a free-posting board carries spam among its cards — the categories and the type are the site's labels); the employer's name scrubbed; the member area never touched.")


def record(body, slug, url):
    h1 = H1_RE.search(body)
    d = DESC_RE.search(body)
    if not h1 or not d:
        return None
    rec = {"source": "werkstraat", "country": "SR", "ledger_id": f"werkstraat:{slug}", "id": slug, "url": url, "title": text(h1.group(1))}
    rec.update(meta(body))
    rec.update({"description": scrub(text(re.sub(r"<h2>\s*Functieomschrijving\s*</h2>", "", d.group(1)))), "contacts_withheld": True, "language": "nl"})
    return rec


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc not in (HOST, "www." + HOST) or not m:
        die(f"{a.url}: not a job address (https://{HOST}/jobs/<slug>/)")
    url = f"https://{HOST}/jobs/{m.group(1)}/"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    rec = record(body, m.group(1), url)
    if rec is None:
        die(f"{url}: 200 without the ad's heading and its «Functieomschrijving» — the template changed", EXIT_PARTIAL)
    print(json.dumps(rec, ensure_ascii=False))
    note(f"{url}: read from its page; employer and description scrubbed; the application never touched.")


def main():
    p = argparse.ArgumentParser(description="Werkstraat — the list's cards with the site's stated count beside them, each ad from its page; employer and texts scrubbed. Issue #445.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="/jobs/ … /jobs/page/N/ until the pager's last page, 2 s apart")
    l_.add_argument("--pages", type=int, help="stop after N pages (a bound, printed as such)")
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
