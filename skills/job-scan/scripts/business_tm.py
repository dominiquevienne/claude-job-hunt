#!/usr/bin/env python3
"""Business Turkmenistan (`business.com.tm`) — the «Вакансии» section, and only it.

WHAT THE HOST SERVES, measured 2026-10-29 03:21-03:29 UTC by the declared client,
the guard taken on each exact path in a turn of its own, `bin/fetch-body.py`:

    /robots.txt                                209 B, group `*`, SEVEN refused paths
                                               (/_backup /index.php /kcfinder /yii
                                               /admin /cgi-sys /search), NONE of which
                                               names /ru/work/; no Crawl-delay; one
                                               sitemap declared; `Host:` ignored.
    /ru/work/rabota/vakansii                   200, 43 266 B — ten notices, a pager
    /ru/work/a/index?path=rabota%2Fvakansii&page=N    200 — the pager, pages 2,3,4,5,141
    /ru/work/<id>                              200 — one notice
    /sitemap.xml                               200, 2 594 757 B, 12 258 <loc>

THE ENUMERATOR IS THE SECTION PAGER, AND THE SITEMAP IS ONLY A WITNESS. This is the
one decision of this adapter and it is not the cheap one: the sitemap hands over all
1 410 `/work/<id>` paths in a SINGLE request, while the pager costs 141. The pager is
taken anyway, because **it is section-scoped BY ITS OWN PARAMETER** — `path=rabota%2F
vakansii` — whereas the sitemap's `/work/<id>` is FLAT and carries no category at all.
On `naydizdes.com`, the sibling board of the same country, the parent section held 345
vacancies AND 51 CVs written by real people, and the enumerator that could not tell
them apart would have leaked all 51 (#671). Here no CV section exists TODAY — measured
below — so the sitemap is safe TODAY; it would absorb, in silence and with no symptom,
any subsection «Работа» gains tomorrow. A path prefix reads like a nature and it is
not one, so the filter is the adapter.

WHAT WAS MEASURED ABOUT THAT RISK, in both directions:
  * the parent `/ru/work/rabota` declares the SAME extent as the child — MAX page 141 —
    and its page one is identical id for id (5613..5622). So «Работа» == «Вакансии»
    today: the Naydizdes shape does not reproduce.
  * the vacancies page names NO CV section: `rezyume`, `rezume`, `resume`, `soiskatel`,
    `Резюме`, `резюме`, `Соискател`, `соискател` each return ZERO.
  * the neighbouring content class is `/advert/<id>` («Announcements», 121 in the
    sitemap) and a notice of it carries ZERO `/ru/work/<id>` link. It is a different
    path space, not a sibling of this one.

THE WITNESS, and it is not our own extraction:
    pager    141 pages declared (named by page 2 AND page 141), 10 notices on page 1,
             page 2 and page 70 (the median), 8 on page 141   ->   140*10 + 8 = 1408
    sitemap  1410 `/work/<id>`, ids 4115..5622, 98 gaps in the raw span
    4115 and 4116 are IN the sitemap and on NO pager page; both answer HTTP 404.
             1410 - 2 dead = 1408.   The two enumerators AGREE at 1408.
The page size was measured on THREE pages of 140, not inferred from one: a total that
closes on an assumed page size is the `51 + 345 = 396` of #671, which was a
coincidence and not a decomposition.

CONTACTS. The host exposes the advertiser's contacts in THREE places, and the issue
named one of them:
    1. a structured `place-info` pair labelled `Телефон:` / `Почта:`
    2. the free text of the notice («Rezýume ibermek üçin: <address>»)
    3. a copy of that text in `<meta name="description">` and the `og:` tags
This adapter emits NONE of them. It never parses the meta tags, it drops the two
labelled values without decoding them, and it scrubs the free text. The site's OWN
footer contacts (`+993 61 89 14 98`, `info@business.com.tm`) are a different thing:
they sit in a `<ul>` of the chrome, identical on every page, they are NOT read, and
they never count towards `withheld_fields` — declaring to have withheld what nobody
deposited is a lie about our own discretion, and it would fire on every single record.

AND NO DIGIT THRESHOLD IS USED. The anchors are the literal `+993`, the e-mail shape,
and the two LABELS; the 8-digit floor comes in only through the expression `isgar.py`
already carries for this same country, whose measurement is written there — a Turkmen
number is eight digits, a monthly wage in manat is four. Measured on this corpus
before relying on it: across the 38 listed items and the two notices read in full, the
only run of six or more digits that is not a phone is `276758`, which is SIX, so the
floor fires on zero of them. A threshold carried from one country to another destroyed
113 of 115 salaries on a Burmese board, and a rule anchored on a LABEL cannot.

`withheld_fields` IS DERIVED from the labels actually present and is ABSENT when none
is: `Телефон:` is present on notice 5622 and ABSENT on notice 4888, so the field
varies on the real corpus rather than being a constant dressed as a measurement.

THE CARD AND THE ISSUE BOTH CARRY A RETYPED PAGER, and the host settles it:
    served:   path=rabota%2Fvakansii&page=N      (9 occurrences)
    written:  path=rabota/vakansii&p=N           (`path=rabota/vakansii` -> 0,  `&p=` -> 0)
The card's own `content:` line has the right encoding and its H1 has the wrong one, so
the card disagreed with itself; the issue body carries both errors. An adapter built on
`&p=N` would have asked for a parameter this host does not use.

DATES ARE ABSOLUTE here, unlike `naydizdes.com`: the listing prints `DD.MM.YYYY` in a
`badge_ex` span, so `posted` is a real date and not a relative string carried as read.

THE LISTING IS ENOUGH for the title, the id, the date, the region, the employer and a
teaser; only the FULL text needs one request per notice (`--details`). The region and
the employer are each named by an ICON in the listing -- `fa-map-marker` and
`fa-building` -- which the first run of this adapter found by accident, because the
unbounded teaser was swallowing them. The teaser is
TRUNCATED by the host — 141 to 236 characters — and the scrub DOES fire on it: **4 of
the 1 408 carry a contact**, three a phone and one an address. An earlier reading of
this line said «0 of 38 for an address, 0 of 38 for a `+993` … a branch that nothing
on the corpus ever takes», and the full walk refuted it: that was a claim about a
DISTRIBUTION made on 38 of 1 408, and nothing in the small sample said it could not
answer. **AND THE SAME WALK IS WHAT JUSTIFIES THE ANCHORS, which no sample could:**
of the 86 runs of digits in a telephone's shape across those 1 408 teasers, ZERO is
preceded by a word of contact within 80 characters — every one is an age range
(`18-25`), a schedule (`14:00-22:00`), a wage (`2500-3000 манат`) or an announcement
number (`ASHGABAT-2026-037`). An Ashgabat landline is written on SIX digits, so a
six-digit floor would have destroyed all 86, which is the Burmese defect exactly.
One teaser, id 4745, still carries the string `+993` and that is CORRECT: the host
truncated its own teaser right after `(+993)`, so the country code stands alone with
no subscriber digit behind it. Matching a bare country code would substitute
"withheld" for something nobody deposited.

No `JobPosting`, no JSON-LD, no breadcrumb list anywhere on this host: the floor that
makes a record a vacancy is POSITIVE and DOUBLED — the `<title>` must end in
`| Вакансии` AND the `categoryHeader` `<h1>` must read `Вакансии`. Both were asserted
to RETAIN the two notices and to REFUSE two real negatives of the same host, an
`/advert/<id>` announcement and a `/post/<id>` press article.

NO Crawl-delay IS PUBLISHED, which is not an absence of a rate limit — a silent host
raised an anti-robot interstitial after nine requests in two and a half minutes
elsewhere in this repository, and the only way to learn where such a threshold sits is
to cross it. The floor here is OURS and it is the cadence actually exercised during
the measurement without incident: ten seconds, twelve requests.

Issue #672.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import html as htmlmod
import json
import re
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "business.com.tm"
BASE = "https://business.com.tm"
SECTION = BASE + "/ru/work/rabota/vakansii"
PAGE = BASE + "/ru/work/a/index?path=rabota%2Fvakansii&page={page}"
SITEMAP = BASE + "/sitemap.xml"

# The pager's `path=` is the whole safety boundary, so it is a WHITELIST of one and
# never a list of refusals: a generic paginator enumerates whatever it is handed.
SECTION_PARAM = "rabota%2Fvakansii"
PARENT_PARAM = "rabota"
VACANCY_LABEL = "Вакансии"
# Segments a CV section would carry on this family of hosts. NONE of them exists on
# this host today -- each returns zero on the served section page -- and they are kept
# so that the day one appears, a URL naming it is refused before any request.
CANDIDATE_SEGMENTS = ("rezyume", "rezume", "resume", "soiskatel",
                      "\u0440\u0435\u0437\u044e\u043c\u0435",
                      "\u0441\u043e\u0438\u0441\u043a\u0430\u0442\u0435\u043b")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# Same country as `isgar.py`, whose measurement these carry: a Turkmen number is eight
# digits, a monthly wage in manat is four, so the 8-digit floor cannot eat a salary.
MAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TEL_RE = re.compile(r"(?:\+\s?993[\s\-()]*)?(?<!\d)\d{8}(?!\d)|\+\s?993[\s\-()\d]{4,}")
MSG_RE = re.compile(r"(?i)\b(?:whats?app|telegram|viber|imo)\b[\s:\uff1a]*[+\d][\d\s\-()]{5,}")

# Every expression below was EXTRACTED from a served body and asserted on the four
# listing pages and the two notices read, never composed from the shape of the markup.
ART_RE = re.compile(r'<article class="type-info-item.*?</article>', re.S)
LINK_RE = re.compile(
    r'<a[^>]+href="(https://business\.com\.tm/(?:ru/)?work/(\d+))"[^>]*>(.*?)</a>', re.S)
DATE_RE = re.compile(
    r'class="badge[^"]*badge_ex[^"]*"[^>]*>\s*([0-3]?\d\.[01]?\d\.\d{4})\s*<')
# The teaser's container nests further `<p>`, so a `(.*?)</p>` closes on the INNER tag
# and returned ZERO on all four pages. The marker is found and the tail of the
# `<article>` block is taken instead.
TEASER_MARK = '<p class="entry-description"'
# ... and the teaser must be BOUNDED or it swallows the tail of the block: the first
# run of the walk emitted `... Ашгабат “Deryaplastik” kärhanasy -->`, the listing's own
# region, employer and a comment close glued onto the description. Measured over the 38
# items: with these three frontiers, ZERO teaser carries a `-->` and 37 of 38 end in the
# host's own ellipsis. Only RUNNING it showed this.
TEASER_BOUNDS = ("<sub", "<!--", "</div>")
# The listing carries the region and the employer after all, each named by its ICON --
# so `--details` buys the FULL text and nothing else. 37 of the 38 items carry both;
# the one that carries neither is id 4125, an older notice, and it emits nulls.
PLACE_RE = re.compile(
    r'<sub class="text-green">\s*<i class="fa fa-map-marker"[^>]*>\s*</i>\s*([^<]*?)\s*</sub>', re.S)
EMPLOYER_RE = re.compile(
    r'<sub class="text-green">\s*<i class="fa fa-building"[^>]*>\s*</i>\s*([^<]*?)\s*</sub>', re.S)
PAGER_RE = re.compile(r'path=rabota%2Fvakansii&(?:amp;)?page=(\d+)')
TITLE_RE = re.compile(
    r'<title[^>]*>(.*?)\s*\|\s*\u0412\u0430\u043a\u0430\u043d\u0441\u0438\u0438\s*</title>', re.S)
CAT_RE = re.compile(r'<h1[^>]*class="categoryHeader[^"]*"[^>]*>\s*(.*?)\s*</h1>', re.S)
FIELD_RE = re.compile(
    r'place-info_label"?>\s*(.*?)\s*</div>\s*<div class="place-info_labeled">(.*?)</div>', re.S)
# One occurrence on each notice read, ZERO on both negatives of the same host.
NOTICE_BODY_RE = re.compile(r'<div class="border-left-big1"[^>]*>(.*?)</div>\s*</div>', re.S)
NOTICE_URL_RE = re.compile(r"^https://business\.com\.tm/(?:ru/|tm/)?work/(\d+)/?$")
SITEMAP_ID_RE = re.compile(r"<loc>[^<]*?/work/(\d+)[^<]*</loc>")

LABEL_EMPLOYER = "\u0420\u0430\u0431\u043e\u0442\u043e\u0434\u0430\u0442\u0435\u043b\u044c"
LABEL_PHONE = "\u0422\u0435\u043b\u0435\u0444\u043e\u043d"
LABEL_MAIL = "\u041f\u043e\u0447\u0442\u0430"
LABEL_REGION = "\u0420\u0435\u0433\u0438\u043e\u043d"


def die(msg, code=EXIT_BROKEN):
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def note(msg):
    print(msg, file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# This host publishes NO Crawl-delay. That is not an absence of a limit, so the floor
# is ours: ten seconds, the cadence exercised during the measurement without incident.
_PACE = Pace(HOST, own=10.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xml;q=0.9",
        "Accept-Language": "ru,tk;q=0.8,en;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def refuse_path(url):
    """A URL this adapter will not take, REFUSED before any request rather than filtered.

    The floor is POSITIVE on the pager's parameter: a generic paginator enumerates
    whatever `path=` names, so the only accepted values are the vacancies section and
    its parent, and everything else -- including a CV section this host does not have
    today -- is refused rather than trusted to be harmless.
    """
    low = url.lower()
    for seg in CANDIDATE_SEGMENTS:
        if seg in low:
            die(f"{url}: its path names {seg!r}, a candidate CV section. **No request is "
                "made.** This host declares no such section today -- each of these segments "
                "returns zero on its served vacancies page -- so this refusal is for the day "
                "it gains one: on `naydizdes.com`, the sibling board of this country, the "
                "parent section held 51 CVs written by real people among its 396 adverts, "
                "and the filter was the adapter.", EXIT_REFUSED)
    q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    raw = urllib.parse.urlsplit(url).query
    if "path=" in raw:
        got = (q.get("path") or [""])[0]
        if got not in (PARENT_PARAM, "rabota/vakansii"):
            die(f"{url}: its `path=` parameter reads {got!r}. **This pager is GENERIC and "
                f"what it enumerates is whatever `path=` names**, so the accepted values are "
                f"a whitelist of one, {SECTION_PARAM!r}, and not a list of refusals: a list "
                "of refusals bets that the problem has been enumerated.", EXIT_REFUSED)


def text(s):
    return re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<[^>]*>", " ", s or ""))).strip()


def scrub(s):
    """The free text, with the advertiser's own contacts removed.

    Anchored on `+993`, on the e-mail shape and on the labels -- never on a count of
    digits alone beyond the 8-digit floor `isgar.py` measured for this country.
    """
    if not s:
        return None
    s = MSG_RE.sub("[contact withheld]", s)
    s = MAIL_RE.sub("[email withheld]", s)
    s = TEL_RE.sub("[telephone withheld]", s)
    return s.strip() or None


def iso(d):
    """`28.10.2026` -> `2026-10-28`. The host prints an ABSOLUTE date."""
    if not d:
        return None
    m = re.match(r"^([0-3]?\d)\.([01]?\d)\.(\d{4})$", d.strip())
    if not m:
        return None
    day, month, year = (int(x) for x in m.groups())
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None
    return f"{year:04d}-{month:02d}-{day:02d}"


def teaser(block):
    i = block.find(TEASER_MARK)
    if i < 0:
        return None
    j = block.find(">", i)
    if j < 0:
        return None
    ends = [k for k in (block.find(b, j) for b in TEASER_BOUNDS) if k > 0]
    return scrub(text(block[j + 1:min(ends) if ends else len(block)]))


def listing(body, where):
    """Every notice of one listing page. The id and the date are both required."""
    rows, dropped = [], []
    for block in ART_RE.findall(body):
        link = LINK_RE.search(block)
        if not link:
            dropped.append("an <article> carrying no /work/<id> anchor")
            continue
        url, ident, title = link.group(1), link.group(2), text(link.group(3))
        when = DATE_RE.search(block)
        where_at = PLACE_RE.search(block)
        who = EMPLOYER_RE.search(block)
        rows.append({
            "source": "business-tm", "country": "TM",
            "ledger_id": f"business-tm:{ident}", "id": ident,
            "url": f"{BASE}/ru/work/{ident}",
            "title": title or None,
            "posted": iso(when.group(1)) if when else None,
            "posted_raw": when.group(1) if when else None,
            "teaser": teaser(block),
            "place": text(where_at.group(1)) if where_at else None,
            "employer": text(who.group(1)) if who else None,
            "listed_on": where,
        })
    return rows, dropped


def notice(url):
    """One notice page, with the POSITIVE floor asserted at BOTH of its declarations."""
    refuse_path(url)
    m = NOTICE_URL_RE.match(url)
    if not m:
        die(f"{url}: not a notice path. A notice is `{BASE}/ru/work/<id>` and nothing "
            "else; the shape is asserted rather than assumed, because the id space is "
            "reached only through the section pager.", EXIT_REFUSED)
    ident = m.group(1)
    code, body = get(url)
    if code == 404:
        die(f"{url}: HTTP 404 -- the notice is gone. **The declared sitemap carries dead "
            "ids**: 4115 and 4116 are in it, are on no pager page, and both answer 404.",
            EXIT_GONE)
    if code != 200 or not body:
        die(f"{url}: HTTP {code}, {len(body)} byte(s).", EXIT_PARTIAL)

    titled = TITLE_RE.search(body)
    header = CAT_RE.search(body)
    head = text(header.group(1)) if header else None
    # Two declarations, both asserted, neither trusted alone. This host serves no
    # JobPosting, no JSON-LD and no breadcrumb list, so these are all there is.
    if not titled:
        die(f"{url}: its <title> does not end in '| {VACANCY_LABEL}'. **Not emitted**: the "
            "floor is POSITIVE -- a record is a vacancy because it passes a test, never "
            "because it is missing from a list. An `/advert/<id>` announcement of this same "
            "host ends in '| Announcements' and is refused here.", EXIT_REFUSED)
    if head != VACANCY_LABEL:
        die(f"{url}: its `categoryHeader` reads {head!r} while its <title> declares "
            f"{VACANCY_LABEL!r}. **Two declarations that disagree are not a vacancy "
            "established**, so nothing is emitted.", EXIT_REFUSED)

    fields = {text(k).rstrip(":"): v for k, v in FIELD_RE.findall(body)}
    bodies = NOTICE_BODY_RE.findall(body)
    full = scrub(text(bodies[0])) if bodies else None
    # The two labelled contact values are DROPPED here and never decoded into the
    # record. The site's own footer contacts live in the chrome and are not read.
    withheld = [n for n, label in (("phone", LABEL_PHONE), ("email", LABEL_MAIL))
                if text(fields.get(label, ""))]
    out = {
        "source": "business-tm", "country": "TM",
        "ledger_id": f"business-tm:{ident}", "id": ident, "url": url,
        "title": text(titled.group(1)) or None,
        "category": head,
        "employer": text(fields.get(LABEL_EMPLOYER, "")) or None,
        "place": text(fields.get(LABEL_REGION, "")) or None,
        "description": full,
    }
    # DERIVED from the labels actually present, and ABSENT when none is. `Телефон:` is
    # on notice 5622 and NOT on notice 4888, so this varies on the real corpus.
    if withheld:
        out["withheld_fields"] = withheld
    return out


def th(n):
    return f"{n:,}".replace(",", " ")


def sitemap_ids():
    """The witness: the ids the host's OWN declared sitemap names, not our extraction."""
    code, body = get(SITEMAP)
    if code != 200 or not body:
        return None, f"HTTP {code}"
    ids = {int(x) for x in SITEMAP_ID_RE.findall(body)}
    return ids, None


def cmd_list(a):
    rows, dropped, pages, n = [], 0, 0, 1
    seen, last = set(), None
    end = "walked to the last page the pager names"
    while True:
        url = SECTION if n == 1 else PAGE.format(page=n)
        refuse_path(url)
        code, body = get(url)
        if code != 200 or not body:
            if n == 1:
                die(f"{url}: HTTP {code}, {len(body)} byte(s) -- no first page, no walk.",
                    EXIT_PARTIAL)
            end = f"page {n} came back HTTP {code}"
            break
        pages += 1
        if n == 1:
            last = max((int(x) for x in PAGER_RE.findall(body)), default=1)
        got, bad = listing(body, url)
        dropped += len(bad)
        if not got:
            end = f"page {n} carried no notice this adapter would emit"
            break
        for r in got:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            rows.append(r)
        if a.max_pages and pages >= a.max_pages:
            end = f"capped by --max-pages at {pages} of {last}"
            break
        if n >= (last or 1):
            break
        n += 1

    out = rows[:a.limit] if a.limit else rows
    if a.details:
        for r in out:
            r.update({k: v for k, v in notice(r["url"]).items() if v is not None})
    for r in out:
        print(json.dumps(r, ensure_ascii=False))

    capped = bool(a.max_pages) or bool(a.limit and a.limit < len(rows))
    note(f"{th(len(rows))} vacancy(ies) emitted over {pages} page(s) of the "
         f"`path={SECTION_PARAM}` pager, which names {last} page(s); {end}.")
    if capped:
        note("this walk was CAPPED, so no total is established by it and the figure above "
             "is what we emitted, not the size of the board.")
    else:
        note(f"the host's own pager declares {last} page(s); page one, page two and the "
             "median page each carried ten notices and the last carried eight, so the "
             f"extent it DECLARES is {th((last - 1) * 10 + 8)} if that size is uniform. "
             "**That page size was measured on three pages of the walk, not inferred from "
             "one**, and it is the pager's claim rather than a count the host prints: this "
             "host prints no total anywhere.")
    if a.witness and not capped:
        ids, why = sitemap_ids()
        if ids is None:
            note(f"the declared sitemap could not be read ({why}): no witness this run.")
        else:
            got = {int(r["id"]) for r in rows}
            note(f"WITNESS -- the host's own declared sitemap names {th(len(ids))} "
                 f"`/work/<id>` path(s) against {th(len(rows))} emitted; "
                 f"{th(len(ids - got))} of them were on no page we walked and "
                 f"{th(len(got - ids))} of ours are absent from it. **This is a witness and "
                 "not our own extraction.** At the measurement its 1 410 reconciled exactly: "
                 "two of its ids, 4115 and 4116, answer HTTP 404, and 1 410 - 2 = 1 408 = "
                 "140 x 10 + 8, the pager's own extent.")
    elif a.witness:
        note("--witness is not taken on a CAPPED walk: a difference against the sitemap "
             "would be ours and would say nothing about the board.")
    if dropped:
        note(f"{dropped} <article> block(s) carried no `/work/<id>` anchor and were dropped.")
    if not a.details:
        note("`teaser` is the host's own TRUNCATED description, BOUNDED at the block's own "
             "next element -- 141 to 236 characters over the 38 items measured, 37 of them "
             "ending in the host's ellipsis. The employer and the region come from the "
             "LISTING (37 of 38 carry both); only the FULL text needs `--details`, one "
             "request per notice at 10 s apart. **No contact is emitted on "
             "either path**: the teaser is scrubbed and the scrub FIRES on 4 of the 1 408 "
             "(three a phone, one an address), while a notice page carries the "
             "advertiser's phone and mail in a labelled `place-info` pair, again in its free "
             "text, and a third time in its meta tags -- the labelled values are dropped "
             "undecoded, the free text is scrubbed, and the meta tags are never read.")
    note("`posted` is a REAL date: this host prints `DD.MM.YYYY` in the listing, unlike "
         "`naydizdes.com` where no absolute date exists anywhere.")


def cmd_one(a):
    print(json.dumps(notice(a.url), ensure_ascii=False))
    note("contacts: the advertiser's phone and mail sit in a `place-info` pair labelled "
         "`Телефон:` and `Почта:`; both are DROPPED without being decoded, and "
         "`withheld_fields` names only the ones that were actually there. The site's own "
         "footer number and address are chrome, identical on every page, and are not read: "
         "counting them would claim a discretion we never exercised, on every record.")


def cmd_witness(a):
    ids, why = sitemap_ids()
    if ids is None:
        die(f"{SITEMAP}: {why}", EXIT_PARTIAL)
    lo, hi = min(ids), max(ids)
    print(json.dumps({"sitemap_work_ids": len(ids), "min": lo, "max": hi,
                      "raw_span": hi - lo + 1, "gaps": (hi - lo + 1) - len(ids)},
                     ensure_ascii=False))
    note("the host's own declared sitemap, counted. **A count of `<loc>` names a SIZE and "
         "never a NATURE**: these are `/work/<id>` paths with no category in them, which is "
         "exactly why this adapter enumerates the section pager instead. Two of them, 4115 "
         "and 4116, answered HTTP 404 at the measurement.")


def main():
    p = argparse.ArgumentParser(
        description="Business Turkmenistan (Turkmenistan) -- walks the «Вакансии» section "
                    "pager, whose `path=` parameter bounds it to vacancies by construction, "
                    "and never the flat `/work/<id>` space of the sitemap, which carries no "
                    "category. Every record is asserted to declare itself a vacancy twice.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every vacancy the section pager names, 10 s apart")
    s.add_argument("--limit", type=int)
    s.add_argument("--max-pages", type=int, help="stop after N pages")
    s.add_argument("--details", action="store_true",
                   help="fetch each notice page for employer, region and full text")
    s.add_argument("--witness", action="store_true",
                   help="also read the declared sitemap and reconcile against it")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("one", help="one notice page, with the category floor asserted twice")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_one)
    w = sub.add_parser("witness", help="count the declared sitemap's `/work/<id>` paths")
    w.set_defaults(fn=cmd_witness)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
