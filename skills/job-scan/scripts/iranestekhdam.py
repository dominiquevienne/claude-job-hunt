#!/usr/bin/env python3
"""Iran Estekhdam (`iranestekhdam.ir`, «ایران استخدام», Iran): the search list — `/search?page=N`, thirty-six cards a page — of a site that is a NEWSPAPER of recruitment notices and not a board of one card per post. Issue #630.

  iranestekhdam.py jobs [--pages N | --all] [--from FILE]
  iranestekhdam.py ad --url https://iranestekhdam.ir/<persian-slug>

**THIS LIST STATES NO COUNT, AND THAT IS THE FINDING.** Every other Iranian
board of this week prints its own total — Jobinja «۱۶,۲۰۱ فرصت شغلی», Jobvision,
IranTalent «۱۷۴۴ نتیجه», Karboom «۳۹۳ آگهی استخدام» — so the habit is to look
for one and compare. Here there is none: no `#search-result-count`, no
`"total"`, no «N نتیجه» anywhere in 341 719 bytes. The figures the page DOES
print in Persian digits are per-EMPLOYER («۲ آگهی فعال», «۱۰۰+ آگهی فعال» on
the company carousel) and one of them is capped with a `+`. **Reading any of
them as the list's total would produce a witness that is specific, plausible
and false.** So the adapter says «the site states no count» and prints the
pager's own bound beside what it emitted; it never manufactures a total.

THE BOUND, AND WHY IT IS A BOUND AND NOT A COUNT. The pager names page 121 on
every page of the walk. Page 1 and page 2 carry 36 cards; page 121 carries 32.
So the list holds **120 × 36 + 32 = 4 352 cards** if no page in between is
short — and nothing on the site says none is. That arithmetic is printed as a
BOUND, in those words.

THE KEY IS THE SITE'S `data-id`, NEVER THE SLUG. Each card is a
`li.search-post-item` carrying `data-id="3118112"` — the site's own advert
number. The address is a Persian title at the ROOT path
(`/استخدام-کارپرداز-برای-شرکت-…`), and an ASCII fold of it is empty: 50 097 of
56 095 such slugs folded to nothing on Jobvision the same week, and an empty
key collides. Each card also holds the SAME link twice (one for the mobile
layout, one for the desktop), so a walk that keys on the address counts 28
where there are 36.

THE FOUR `detail` SPANS ARE POSITIONAL. Title, employer, city, then contract
and salary together in one span — «تمام وقت (حقوق توافقی)», full time
(salary negotiable). They are read by position, and a missing one keeps its
place: a card without a city must not slide its contract into the city's
field. The salary is taken as the site writes it, inside the parentheses,
and is never converted.

THE ADVERT PAGE CARRIES NO `JobPosting`. Its only `application/ld+json` is a
`BreadcrumbList`; the fields are the page's own markup. **An absent JobPosting
is not an absent advert** — the title, the employer, the city and the age are
on the page, and the record says where they came from.

THE RULES (read 2026-09-22 13:06 UTC): `User-agent: *` then `Disallow:` — an
EMPTY directive, which refuses nothing — and ten `Sitemap:` lines.
`allowed('iranestekhdam.ir', '/search')` → open, `certain: True`, no
`Crawl-delay`. The sitemaps are not the route: `sitemap-ads-2026-9.xml` holds
2 390 `<loc>` for the month, with duplicates, and *a count of `<loc>` is not a
count of adverts*.

WITHHELD: e-mail addresses and telephone numbers in every text (Persian digits
included), the employer's logo, the application route; **the gender criterion**
the notices print (#183 — the advert is served, the criterion is not), named on
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
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD, HOST, COUNTRY = "iranestekhdam", "iranestekhdam.ir", "IR"
BASE = f"https://{HOST}"
LISTING = BASE + "/search"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE = 36
MAX_PAGES = 2000
FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
CARD_SPLIT_RE = re.compile(r'<li class="search-post-item')
ID_RE = re.compile(r'data-id="(\d+)"')
HREF_RE = re.compile(r'<a href="(https://iranestekhdam\.ir/[^"]+)"[^>]*class="d-flex w-100"')
ANY_HREF_RE = re.compile(r'href="(https://iranestekhdam\.ir/%[^"?#]+)"')
TITLE_RE = re.compile(r'<strong class="detail title"[^>]*>(.*?)</strong>', re.S)
DETAIL_RE = re.compile(r'<span class="detail"[^>]*>(.*?)</span>', re.S)
DATE_RE = re.compile(r'<span class="date"[^>]*>(.*?)</span>', re.S)
BADGE_RE = re.compile(r'<span class="badge[^"]*"[^>]*>(.*?)</span>', re.S)
PAY_RE = re.compile(r"^(?P<contract>[^()]*?)\s*\((?P<salary>.*)\)\s*$", re.S)
PAGER_RE = re.compile(r"[?&]page=(\d+)")
GENDER_RE = re.compile(r"جنسیت")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?[\d۰-۹][\d۰-۹\s().\-]{7,}[\d۰-۹](?!\w)")
_PACE = Pace(HOST, own=2.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[iranestekhdam] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def fa_int(s):
    """A number the site writes in Persian digits — «۳۶» is 36. A «+» is a CAP, not a number: «۱۰۰+»
    means at least a hundred, so it is refused rather than read as 100."""
    if not s or "+" in s:
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
    return f"{LISTING}?page={n}"


def split_pay(s):
    """«تمام وقت (حقوق توافقی)» is TWO fields in one span: the contract, then the salary in parentheses,
    as written. A span with no parentheses is a contract and no salary — not a salary of nothing."""
    if not s:
        return None, None
    m = PAY_RE.match(s)
    if not m:
        return s.strip() or None, None
    return (m.group("contract").strip() or None), (m.group("salary").strip() or None)


def parse_listing(body):
    """(stated, last_page, cards). `stated` is ALWAYS None here and the caller says so: this list prints no
    total of its own, and the per-employer figures beside it are another question (one is capped «۱۰۰+»)."""
    body = body or ""
    pages = [int(x) for x in PAGER_RE.findall(body)]
    cards = []
    for seg in CARD_SPLIT_RE.split(body)[1:]:
        i = ID_RE.search(seg)
        if not i:
            continue
        h = HREF_RE.search(seg) or ANY_HREF_RE.search(seg)
        t = TITLE_RE.search(seg)
        # **The site OMITS the span rather than emitting an empty one**, so padding the list at the END
        # slides the contract into the city: measured on the first full walk, 87 of 4 352 rows carried
        # «تمام وقت (حقوق توافقی)» as their CITY and 107 carried no contract at all. The employer is
        # always FIRST and the contract-and-salary span always LAST; the city exists only when there
        # are three. *A missing field in the middle is not a missing field at the end.*
        det = [text(x) for x in DETAIL_RE.findall(seg)]
        company = det[0] if det else None
        pay = det[-1] if len(det) > 1 else None
        place = det[1] if len(det) > 2 else None
        contract, salary = split_pay(pay)
        d = DATE_RE.search(seg)
        b = BADGE_RE.search(seg)
        cards.append({"id": i.group(1),
                      "url": urllib.parse.urlsplit(htmlmod.unescape(h.group(1)))._replace(query="", fragment="").geturl() if h else None,
                      "title": text(t.group(1)) if t else None,
                      "company": company, "place": place,
                      "contract_as_written": contract, "salary_as_written": salary,
                      "posted_as_written": text(d.group(1)) if d else None,
                      "badge_as_written": text(b.group(1)) if b else None})
    return None, (max(pages) if pages else None), cards


def row(c):
    return {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{c['id']}", "id": c["id"], "url": c["url"],
            "title": scrub(c["title"]), "company": scrub(c["company"]), "place": scrub(c["place"]),
            "contract_as_written": c["contract_as_written"], "salary_as_written": c["salary_as_written"],
            "posted_as_written": c["posted_as_written"], "badge_as_written": c["badge_as_written"],
            # **No `criteria_withheld` here (#885).** The gender is in the NOTICE, not on the card: measured
            # 2026-09-22, ZERO of thirty-six cards carried «جنسیت» while 4 352 of 4 352 rows declared one.
            # A claim about the board does not belong in a field that reads as a claim about the advert.
            "contacts_withheld": True}


def cmd_jobs(a):
    if a.from_file:
        with open(a.from_file, "rb") as f:
            body = decode_body(f.read())[0]
        stated, last, cards = parse_listing(body)
        if not cards:
            die(f"{a.from_file}: no `li.search-post-item` in this copy — not a list page, or the page changed shape.", EXIT_PARTIAL)
        seen, out = set(), []
        for c in cards:
            if c["id"] not in seen:
                seen.add(c["id"])
                out.append(row(c))
        pages_read = 1
    else:
        seen, out, last, page = set(), [], None, 1
        while page <= MAX_PAGES:
            url = page_url(page)
            st, body = request(url)
            status_of(st, url)
            _s, lp, cards = parse_listing(body)
            if page == 1:
                last = lp
                if not cards:
                    die(f"{url}: no advert card in the answer — not the list, or the page changed shape.", EXIT_PARTIAL)
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
    bounded = bool(a.from_file) or (not a.all_pages and (a.pages or 3) < (last or 0))
    # **No total is invented.** The bound is arithmetic on the pager and is called a bound.
    # **The bound is ASSERTED, not merely printed.** A walk that stops early prints a smaller number and
    # nothing contradicts it — the site states no count, so there is no other witness. Measured on
    # `mellikar.com` the same week (#631): a WebForms list RESET itself twice in eight rounds, and a stop
    # on «no new row» would have emitted 18 of 5 358 with exit 0. `talacom.py` already does this; this
    # adapter printed the interval and checked nothing.
    lo, hi = (max(1, (last - 1) * PAGE + 1), last * PAGE) if last else (None, None)
    bound = f"; its pager ends at page {th(last)}, so the walk must land in {th(lo)}–{th(hi)} ({th(last)} × {PAGE}) — a BOUND, not a count" if last else ""
    short = bool(last) and not bounded and not (lo <= n <= hi)
    note(f"{th(n)} emitted over {th(pages_read)} page(s) of {PAGE} — **the site states no count**{bound}"
         + (f"; a BOUNDED read ({'one saved page' if a.from_file else '--pages'}), not the board" if bounded
            else (f"; **OUTSIDE the pager's bound — the walk stopped early or the list moved**" if short else "; inside the bound.")))
    note("the notices print a gender criterion and it is never carried (#183). The list cards do not carry "
         "one, so no row claims to have withheld one — a claim about the board does not belong in a field "
         "that reads as a claim about the advert (#885).")
    if short:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    if parts.netloc.lower() != HOST or not parts.path or parts.path == "/":
        die(f"{a.url!r}: not an Iran Estekhdam advert address (https://{HOST}/<persian-slug>)")
    url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    st, body = request(url)
    status_of(st, url)
    head = re.search(r'<div class="single-contacts-box"[^>]*>(.*?)</section>', body or "", re.S)
    if not head:
        die(f"{url}: no advert header in the page — gone, or the page changed shape.", EXIT_PARTIAL)
    # **Read by the site's own class names, not by line position.** The fields happen to fall on separate
    # lines because `h1`, `div.company-title` and `div.state` are block elements — an incidental fact of
    # this template, and a reader that depends on it breaks the day one of them becomes a span.
    blk = head.group(1)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", blk, re.S)
    co = re.search(r'<div class="company-title[^"]*"[^>]*>(.*?)</div>', blk, re.S)
    st = re.search(r'<div class="state"[^>]*>(.*?)</div>', blk, re.S)
    ag = re.search(r'<(?:span|div) class="(?:date|time)[^"]*"[^>]*>(.*?)</(?:span|div)>', blk, re.S)
    lines = [text(m.group(1)) if m else None for m in (h1, co, st, ag)]
    og = re.search(r'<meta property="og:description" content="([^"]*)"', body or "")
    rec = {"source": BOARD, "country": COUNTRY,
           "ledger_id": f"{BOARD}:{urllib.parse.unquote(parts.path.strip('/'))[:120]}",
           "url": url,
           "title": scrub(lines[0]), "company": scrub(lines[1]), "place": scrub(lines[2]),
           "posted_as_written": lines[3],
           "description": (scrub(text(htmlmod.unescape(og.group(1)))) if og else None),
           # the page carries no JobPosting — only a BreadcrumbList — and that is said rather than left blank
           "structured_data": "none — the page's only ld+json is a BreadcrumbList",
           "criteria_withheld": ["gender"] if GENDER_RE.search(body or "") else [],
           "contacts_withheld": True}
    print(json.dumps(rec, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Iran Estekhdam (Iran) — the search list of a site that states no count, and says so; the pager's bound printed as a bound; the gender criterion never carried (#183), contacts withheld. Issue #630.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="/search?page=N — thirty-six a page; «N emitted … the site states no count»")
    s.add_argument("--pages", type=int, help="how many pages to read (default 3 — a bounded read, said in the output)")
    s.add_argument("--all", dest="all_pages", action="store_true", help="walk to the pager's last page")
    s.add_argument("--from", dest="from_file", metavar="FILE", help="a saved copy of one list page")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its address; the page's own fields — there is no JobPosting")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
