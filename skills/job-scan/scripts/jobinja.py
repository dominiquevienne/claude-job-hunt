#!/usr/bin/env python3
"""Jobinja (`jobinja.ir`, «جابینجا», Iran): the generalist's own list — `/jobs?page=N`, twenty cards a page, the page STATING its own «۱۶,۲۰۱ فرصت ‌شغلی فعال» in Persian digits — and the advert's JobPosting; **the gender the board prints beside each advert is never carried** (#183: the advert is served, the criterion is not). Issue #627.

  jobinja.py jobs [--pages N | --all] [--from FILE]
  jobinja.py ad --url https://jobinja.ir/companies/<company>/jobs/<id>/<slug>

THE RULES (read 2026-09-22 07:49 UTC): `User-agent: *` — `Disallow:` (an
empty directive: nothing is refused) then `Disallow: /style_guide/`. **A
query string is permitted here** (unlike `jobvision.ir`, whose rules refuse
`*?*`), so the list's own `?page=N` is the route; `/style_guide/` is never
asked.

THE ROUTE, MEASURED 2026-09-22 07:49–07:55 UTC, the declared client.
`/jobs` (200, 250 680 B) prints **«۱۶,۲۰۱ فرصت ‌شغلی» + «فعال»** — sixteen
thousand two hundred and one ACTIVE opportunities, in Persian digits — and
twenty `li.o-listView__item` cards: the title and its address
(`/companies/<company>/jobs/<id>/<persian slug>`, with `_ref`/`_t` tracking
parameters **dropped from what is emitted**), the employer, the city, and a
relative age («امروز» — today). The pager names its last page, 811 on
2026-09-22 (811 × 20 = 16 220, the stated 16 201 plus a partial page). The
advert (101 193 B): a `JobPosting` — `title`, `hiringOrganization.name`,
`datePosted`, `baseSalary` (currency IRT, value, unitText), `employmentType`,
`jobLocation`, `jobLocationType` — beside the page's labelled fields
(«موقعیت مکانی», «نوع همکاری», «حداقل سابقه کار», «حقوق», «حداقل مدرک
تحصیلی»).

**THE GENDER IS NOT CARRIED, AND THE RECORD ONLY SAYS SO WHEN IT WAS THERE.**
The ADVERT page prints «جنسیت: زن» (gender: woman) as a hiring criterion. The
repository serves the advert and does NOT propagate the criterion (#183, and
`jobcentrebrunei.py` does the same with an age range): the field is never
emitted, and the advert's record names what was left behind —
`criteria_withheld: ["gender"]` **when the page carried one**, `[]` when it did
not.

**The LIST row carries no such field at all, and that is a correction (#885).**
It used to declare `criteria_withheld: ["gender"]` on every card — but *the
card does not print a gender*, only the advert does. The row was therefore
claiming to have withheld something the object it describes never held: an
assertion about the BOARD written into a field that reads as an assertion about
the ADVERT, and the two are indistinguishable once a record is read. **The fact
about the board is true and it belongs on the card, once** —
`shared/boards/jobinja.md` says it. *Same family as «declaring you withheld a
number nobody filed», one step further: there the field was present and empty,
here the field was never on the object at all.*

THE KEY IS THE SITE'S ID, NEVER THE SLUG. The slug is the Persian title; an
ASCII fold of it is empty, and an empty key collides — measured on Jobvision
the same week: 50 097 of 56 095 slugs fold to nothing. Here the key is the
short identifier the site puts in its own address (`tou2`).

WITHHELD: e-mail addresses and telephone numbers in every text (Persian
digits included), the employer's logo, the application route; the gender
criterion above; `contacts_withheld` on every record. Country IR.
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

BOARD, HOST, COUNTRY = "jobinja", "jobinja.ir", "IR"
BASE = f"https://{HOST}"
LISTING = BASE + "/jobs"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE = 20
MAX_PAGES = 2000
FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
STATED_RE = re.compile(r'class="c-jobSearchState__numberOfResultsEcho">\s*([\d۰-۹٠-٩,،\.]+)\s*([^<]*)<')
# The card's own <li> contains nested <li> (its meta items), so a `<li …>(.*?)</li>` cut stops at the FIRST
# inner close and loses the city and the contract — the cards are split on their own opening tag instead.
ITEM_SPLIT_RE = re.compile(r'<li class="o-listView__item ')
LINK_RE = re.compile(r'<a class="c-jobListView__titleLink"[^>]*href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>', re.S)
AGE_RE = re.compile(r'class="c-jobListView__passedDays">\s*\(?([^)<]+?)\)?\s*</span>', re.S)
META_RE = re.compile(r'<li class="c-jobListView__metaItem">.*?<span>\s*(.*?)\s*</span>', re.S)
AD_PATH_RE = re.compile(r"^/companies/([^/]+)/jobs/([A-Za-z0-9_-]+)(?:/(.*))?$")
PAGER_RE = re.compile(r"[?&]page=(\d+)")
GENDER_RE = re.compile(r"جنسیت\s*</?[^>]*>?\s*([^<]{1,20})")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?[\d۰-۹][\d۰-۹\s().\-]{7,}[\d۰-۹](?!\w)")
_PACE = Pace(HOST, own=2.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobinja] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def fa_int(s):
    """A count the site writes in Persian digits with its own separators — «۱۶,۲۰۱» is 16 201."""
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


def clean_url(u):
    """The address without the board's own tracking parameters (`_ref`, `_t`) — what is emitted is a link, not a trail."""
    p = urllib.parse.urlsplit(htmlmod.unescape(u))
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if not k.startswith("_")]
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, urllib.parse.urlencode(q), ""))


def parse_listing(body):
    """(stated, active_word, last_page, cards) — the count the page states, the word beside it, the pager's last page."""
    m = STATED_RE.search(body or "")
    stated, word = (fa_int(m.group(1)), text(m.group(2))) if m else (None, None)
    pages = [int(x) for x in PAGER_RE.findall(body or "")]
    cards = []
    for seg in ITEM_SPLIT_RE.split(body or "")[1:]:
        link = LINK_RE.search(seg)
        if not link:
            continue
        url = clean_url(link.group("url"))
        am = AD_PATH_RE.match(urllib.parse.unquote(urllib.parse.urlsplit(url).path))
        if not am:
            continue
        metas = [text(x) for x in META_RE.findall(seg)]
        age = AGE_RE.search(seg)
        cards.append({"id": am.group(2), "company_slug": am.group(1), "url": url, "title": text(link.group("title")),
                      "company": metas[0] if metas else None, "place": metas[1] if len(metas) > 1 else None,
                      "contract_as_written": metas[2] if len(metas) > 2 else None,
                      "posted_as_written": text(age.group(1)) if age else None})
    return stated, word, (max(pages) if pages else None), cards


def row(c):
    return {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{c['id']}", "id": c["id"], "url": c["url"],
            "title": scrub(c["title"]), "company": scrub(c["company"]), "place": scrub(c["place"]),
            "posted_as_written": c["posted_as_written"], "contract_as_written": c.get("contract_as_written"),
            "contacts_withheld": True}      # no `criteria_withheld`: the CARD prints no criterion (#885)


def cmd_jobs(a):
    if a.from_file:
        with open(a.from_file, "rb") as f:
            bodies = [decode_body(f.read())[0]]
        pages_read, stated, word, last = 1, None, None, None
        seen, out = set(), []
        for body in bodies:
            stated, word, last, cards = parse_listing(body)
            for c in cards:
                if c["id"] not in seen:
                    seen.add(c["id"])
                    out.append(row(c))
    else:
        seen, out, stated, word, last, page = set(), [], None, None, None, 1
        while page <= MAX_PAGES:
            url = LISTING if page == 1 else f"{LISTING}?page={page}"
            st, body = request(url)
            status_of(st, url)
            s, w, lp, cards = parse_listing(body)
            if page == 1:
                stated, word, last = s, w, lp
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
    bounded = not a.all_pages and not a.from_file and (a.pages or 3) < (last or 0)
    note(f"{th(n)} emitted over {th(pages_read)} page(s) of {PAGE} — the site states {th(stated) if stated is not None else 'no total'}"
         + (f" «{word}»" if word else "") + (f", its pager ending at page {th(last)}" if last else "")
         + ("; a BOUNDED read (--pages), not the board" if bounded else (": equal." if stated == n else f": {th(abs(stated - n))} short." if stated is not None else ".")))
    note("the gender is printed on the ADVERT page, not on these cards: the list rows declare no "
         "criterion (#885), and `ad` says `criteria_withheld: [\"gender\"]` only when the advert "
         "it read carried one (#183). That the board prints the criterion at all is a fact about "
         "the board, and the card says it once.")
    if stated is not None and not bounded and stated != n:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_PATH_RE.match(urllib.parse.unquote(parts.path or ""))
    if parts.netloc.lower() != HOST or not m:
        die(f"{a.url!r}: not a Jobinja advert address (https://{HOST}/companies/<company>/jobs/<id>/<slug>)")
    url = clean_url(a.url)
    st, body = request(url)
    status_of(st, url)
    found = postings(body)
    if not found:
        die(f"{url}: no JobPosting in the page — gone, or the page changed shape.", EXIT_PARTIAL)
    p = found[0]
    sal = one(p.get("baseSalary"))
    addr = one(one(p.get("jobLocation")).get("address"))
    rec = {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{m.group(2)}", "id": m.group(2), "url": url,
           "title": scrub(label(p.get("title"))), "company": scrub(label(p.get("hiringOrganization"))),
           "place": scrub(label(addr.get("addressLocality")) or label(addr.get("addressRegion"))),
           "employment_type": label(p.get("employmentType")), "remote": label(p.get("jobLocationType")),
           "salary_currency": label(sal.get("currency")), "salary_value": sal.get("value") if not isinstance(sal.get("value"), (dict, list)) else label(one(sal.get("value")).get("value")),
           "posted": label(p.get("datePosted")),
           "description": (scrub(text(label(p.get("description")) or "")) or "")[:20000] or None,
           # **conditional on what THIS page carried** — an empty list is «read, and there was none»
           "criteria_withheld": ["gender"] if GENDER_RE.search(body) else [],
           "contacts_withheld": True}
    print(json.dumps(rec, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Jobinja (Iran) — the site's own list against its own stated count; the advert's JobPosting; the gender criterion never carried (#183), contacts withheld. Issue #627.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="/jobs?page=N — twenty a page; «N emitted … the site states M «فعال»»")
    s.add_argument("--pages", type=int, help="how many pages to read (default 3 — a bounded read, said in the output)")
    s.add_argument("--all", dest="all_pages", action="store_true", help="walk to the pager's last page")
    s.add_argument("--from", dest="from_file", metavar="FILE", help="a saved copy of one list page")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its address; JobPosting + page fields, gender never emitted")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
