#!/usr/bin/env python3
"""Karboom (`karboom.io`, «کاربوم», Iran): the generalist's own list — `/jobs?page=N`, twenty cards a page, the page STATING its own «۳۹۳ آگهی استخدام» in Persian digits — and the advert's JobPosting; **the gender the board prints beside an advert is never carried** (#183: the advert is served, the criterion is not). Issue #629.

  karboom.py jobs [--pages N | --all] [--from FILE]
  karboom.py ad --url https://karboom.io/jobs/<hashid>/<slug>

`/jobs` AND `/jobs?page=1` ARE TWO DIFFERENT PAGES, AND THE FIRST IS NOT THE
LIST. The bare path is a CATEGORY HUB: seventy-two category tiles, the city
tiles, and **nine featured adverts** — no `#search-result-count` anywhere on
it. The list is `?page=N`, twenty cards and the count. Measured 2026-09-22
09:15–09:17 UTC: the hub 137 062 B / 9 adverts / no count, the list's first
page 275 462 B / 20 adverts / **«۳۹۳»**. *The neighbouring Iranian board
(`jobinja.ir`, #627) has the opposite convention — there the bare `/jobs` IS
page one — so the habit carried over from it reads the hub, emits nine, and
says nothing is wrong.* Every page of this walk carries `?page=`, page one
included; the guard holds it.

THE RULES (read 2026-09-22 09:16 UTC): `User-agent: *` with fourteen
`Disallow` lines — the back office (`/backend/*`, `/employer/*`, `/ats/*`,
`/my/*`), the candidate's own area (`/profile/*`, `/cv/*`), the assessments,
and two that bear on this walk: **`Disallow: /*?q=`** — a query string
carrying `q=` is refused, which the pager's `?page=N` is not — and
**`Disallow: /jobs/sokan_academy`**, one facet refused BY NAME. Neither is
ever asked. `allowed('karboom.io', '/jobs')` → open, `certain: True`.

THE ROUTE, MEASURED 2026-09-22 09:14–09:20 UTC, the declared client, the
guard on each exact path. The root answers 200 at **103 597 bytes on both
reads** while its md5 moves (`c58ffb47f9ae`, then `467583f03e1c`): **the size
is the witness here and the md5 is not** — the page carries an element
rendered at request time, the same one that turns up inside the advert below.
The list states its own total in `span#search-result-count` and names what it
counts in the `<h1>` beside it («آگهی استخدام»); its pager ends at page 20,
and 20 × 20 = 400 ≥ 393. A card gives the advert's address
(`/jobs/<hashid>/<percent-encoded Persian title>`), its employer, its city
and a relative age («امروز» — today); the key is the site's own **hashid**,
never the slug, because an ASCII fold of a Persian title is empty and an
empty key collides (measured on Jobvision the same week: 50 097 of 56 095).

`employmentType` IS NOT A STRING — IT IS THE SITE'S OWN ROW, HTML-ESCAPED.
The advert's JobPosting carries
`{"id":118711,"job_id":48484,"cooperation_type":"FULL_TIME","created_at":…}`
in that field. Emitted whole it would publish the board's internal
identifiers; and **its `created_at` is stamped at the moment of the request**
— it read `2026-09-22T09:15:10` on a fetch made at 09:15:10, for an advert
posted the day before. So the field is parsed, `cooperation_type` is kept,
and the ids and that stamp are dropped: *a value that changes between two
reads is not a measurement.*

WITHHELD: e-mail addresses and telephone numbers in every text (Persian
digits included), the employer's logo, the application route, the board's
internal identifiers; the gender criterion above; `contacts_withheld` on
every record. Country IR.
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

BOARD, HOST, COUNTRY = "karboom", "karboom.io", "IR"
BASE = f"https://{HOST}"
LISTING = BASE + "/jobs"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE = 20
MAX_PAGES = 2000
FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
# The count and the words that name what it counts live in two sibling elements, and only together do they
# say «393 job adverts» rather than «393».
STATED_RE = re.compile(r'id="search-result-count"[^>]*>\s*([\d۰-۹٠-٩,،.\s]+?)\s*<')
STATED_WORD_RE = re.compile(r'id="static-text"[^>]*>\s*([^<]+?)\s*<')
CARD_SPLIT_RE = re.compile(r'<div class="job-position-card ')
HREF_RE = re.compile(r'data-href="([^"]+)"')
TITLE_RE = re.compile(r'<h3[^>]*>\s*<a[^>]*title="([^"]*)"', re.S)
COMPANY_RE = re.compile(r'class="company-name[^"]*"[^>]*>\s*(.*?)\s*</span>', re.S)
PLACE_RE = re.compile(r'class="pull-right"[^>]*>\s*(.*?)\s*</span>', re.S)
DATE_RE = re.compile(r'class="date [^"]*"[^>]*>\s*(.*?)\s*</p>', re.S)
AD_PATH_RE = re.compile(r"^/jobs/([A-Za-z0-9]+)/(.*)$")
PAGER_RE = re.compile(r"[?&]page=(\d+)")
GENDER_RE = re.compile(r"جنسیت")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?[\d۰-۹][\d۰-۹\s().\-]{7,}[\d۰-۹](?!\w)")
_PACE = Pace(HOST, own=2.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[karboom] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def fa_int(s):
    """A count the site writes in Persian digits with its own separators — «۳۹۳» is 393."""
    if not s:
        return None
    digits = re.sub(r"[^0-9]", "", s.translate(FA_DIGITS))
    return int(digits) if digits else None


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    """(status, text) — this host only, the guard first (it reads the rules on the exact path), 2 s apart."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc.lower() != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "fa,en"})
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


def page_url(n):
    """Page one is `?page=1`, NOT the bare path: the bare path is the category hub, and it carries nine
    featured adverts and no count — a walk that started there would emit nine and say nothing was wrong."""
    return f"{LISTING}?page={n}"


def cooperation(raw):
    """`employmentType` is the site's own row, HTML-escaped. Keep what names the contract; drop the internal
    ids and the `created_at` the server stamps AT REQUEST TIME (it read 09:15:10 on a fetch made at 09:15:10)."""
    v = label(raw)
    if not v:
        return None
    s = htmlmod.unescape(v).strip()
    if s.startswith("{"):
        try:
            d = json.loads(s)
        except ValueError:
            return None
        return d.get("cooperation_type") or d.get("title") or None
    return s


def parse_listing(body):
    """(stated, counted_word, last_page, cards) — the count the page states, the words that name what it
    counts, the pager's last page."""
    body = body or ""
    m = STATED_RE.search(body)
    w = STATED_WORD_RE.search(body)
    stated = fa_int(m.group(1)) if m else None
    word = text(w.group(1)) if w else None
    pages = [int(x) for x in PAGER_RE.findall(body)]
    cards = []
    for seg in CARD_SPLIT_RE.split(body)[1:]:
        h = HREF_RE.search(seg)
        if not h:
            continue
        url = htmlmod.unescape(h.group(1))
        parts = urllib.parse.urlsplit(url)
        am = AD_PATH_RE.match(parts.path or "")
        if parts.netloc.lower() != HOST or not am:
            continue
        t = TITLE_RE.search(seg)
        c = COMPANY_RE.search(seg)
        p = PLACE_RE.search(seg)
        d = DATE_RE.search(seg)
        cards.append({"id": am.group(1), "url": urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, "", "")),
                      "title": text(t.group(1)) if t else None, "company": text(c.group(1)) if c else None,
                      "place": text(p.group(1)) if p else None,
                      "posted_as_written": text(d.group(1)) if d else None})
    return stated, word, (max(pages) if pages else None), cards


def row(c):
    return {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{c['id']}", "id": c["id"], "url": c["url"],
            "title": scrub(c["title"]), "company": scrub(c["company"]), "place": scrub(c["place"]),
            "posted_as_written": c["posted_as_written"],
            # **No `criteria_withheld` here (#885).** The gender is printed on the ADVERT page, not on the
            # card: measured 2026-09-22, one card of twenty carried «جنسیت». Declaring it on every list row
            # said we had withheld something the card never held — an affirmation about the BOARD written in
            # a field that reads as an affirmation about the ADVERT. The board fact lives on the card once.
            "contacts_withheld": True}


def cmd_jobs(a):
    if a.from_file:
        with open(a.from_file, "rb") as f:
            body = decode_body(f.read())[0]
        stated, word, last, cards = parse_listing(body)
        # The same discriminator as the walk, and it is needed MORE here: a saved copy carries no address,
        # so nothing else in the file says whether it is the list or the category hub — and the hub parses
        # cleanly into nine rows. Without this, `--from <the hub>` emits nine and calls it the board.
        if stated is None:
            die(f"{a.from_file}: no `span#search-result-count` in this copy — it is the category hub "
                f"(`/jobs`, nine featured adverts) and not the list (`/jobs?page=N`), or the page changed shape.",
                EXIT_PARTIAL)
        seen, out = set(), []
        for c in cards:
            if c["id"] not in seen:
                seen.add(c["id"])
                out.append(row(c))
        pages_read = 1
    else:
        seen, out, stated, word, last, page = set(), [], None, None, None, 1
        while page <= MAX_PAGES:
            url = page_url(page)
            st, body = request(url)
            status_of(st, url)
            s, w, lp, cards = parse_listing(body)
            if page == 1:
                stated, word, last = s, w, lp
                if not cards:
                    die(f"{url}: no advert card in the answer — not the list, or the page changed shape.", EXIT_PARTIAL)
                if stated is None:
                    die(f"{url}: the list states no count — `span#search-result-count` is absent. The bare `/jobs` is the "
                        f"category hub and answers 200 with nine featured adverts; this walk asks `?page=`, so a missing "
                        f"count means the page changed shape, not that the route is wrong.", EXIT_PARTIAL)
            new = 0
            for c in cards:
                if c["id"] not in seen:
                    seen.add(c["id"])
                    out.append(row(c))
                    new += 1
            if not cards or new == 0:
                if page > 1:
                    note(f"page {page}: {'no card' if not cards else 'only repeats'} — stopped.")
                break
            if not a.all_pages and page >= (a.pages or 3):
                break
            if last and page >= last:
                break
            page += 1
        pages_read = page
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    # A saved copy is ONE page of the walk, so it is bounded BY CONSTRUCTION: without this it reports
    # «373 short» on a file that was never meant to hold the board, and a bounded read reads as a loss.
    bounded = bool(a.from_file) or (not a.all_pages and (a.pages or 3) < (last or 0))
    note(f"{th(n)} emitted over {th(pages_read)} page(s) of {PAGE} — the site states {th(stated) if stated is not None else 'no total'}"
         + (f" «{word}»" if word else "") + (f", its pager ending at page {th(last)}" if last else "")
         + (f"; a BOUNDED read ({'one saved page' if a.from_file else '--pages'}), not the board" if bounded else (": equal." if stated == n else f": {th(abs(stated - n))} short." if stated is not None else ".")))
    note("the board prints a gender criterion ON ITS ADVERT PAGES and it is never carried (#183). The list "
         "cards do not carry it, so no row claims to have withheld one — a claim about the board does not "
         "belong in a field that reads as a claim about the advert (#885).")
    if stated is not None and not bounded and stated != n:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_PATH_RE.match(parts.path or "")
    if parts.netloc.lower() != HOST or not m:
        die(f"{a.url!r}: not a Karboom advert address (https://{HOST}/jobs/<hashid>/<slug>)")
    url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    st, body = request(url)
    status_of(st, url)
    found = postings(body)
    if not found:
        die(f"{url}: no JobPosting in the page — gone, or the page changed shape.", EXIT_PARTIAL)
    p = found[0]
    addr = one(one(p.get("jobLocation")).get("address"))
    rec = {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{m.group(1)}", "id": m.group(1), "url": url,
           "title": scrub(label(p.get("title"))), "company": scrub(label(p.get("hiringOrganization"))),
           "place": scrub(label(addr.get("addressLocality")) or label(addr.get("addressRegion"))),
           "employment_type": cooperation(p.get("employmentType")),
           "education": scrub(label(p.get("educationRequirements"))),
           "occupational_category": scrub(label(p.get("occupationalCategory"))),
           "posted": label(p.get("datePosted")), "valid_through": label(p.get("validThrough")),
           "description": (scrub(text(label(p.get("description")) or "")) or "")[:20000] or None,
           "criteria_withheld": ["gender"] if GENDER_RE.search(body or "") else [],
           "contacts_withheld": True}
    print(json.dumps(rec, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Karboom (Iran) — the site's own list against its own stated count; the advert's JobPosting; the gender criterion never carried (#183), contacts withheld. Issue #629.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="/jobs?page=N — twenty a page; «N emitted … the site states M «آگهی استخدام»»")
    s.add_argument("--pages", type=int, help="how many pages to read (default 3 — a bounded read, said in the output)")
    s.add_argument("--all", dest="all_pages", action="store_true", help="walk to the pager's last page")
    s.add_argument("--from", dest="from_file", metavar="FILE", help="a saved copy of one list page")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its address; JobPosting, the contract read out of the site's own row, gender never emitted")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
