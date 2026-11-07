#!/usr/bin/env python3
"""Jobs.mu (`www.jobs.mu`, Mauritius): a board that states NO total of its own, whose size is
established by THREE independent enumerators agreeing on the same members — and whose own RSS
feed publishes links that 404. Issue #698.

  jobsmu.py jobs [--country-code MU] [--no-witness] [--max-pages N]
  jobsmu.py ad --code 139963
  jobsmu.py ad --url https://www.jobs.mu/job/139963/driver/

WHAT IT IS. Jobs.mu is the second Mauritian board this repository walks, after CareerHub (#701),
and it is the opposite shape. CareerHub states `numberOfItems: 158` and serves 24 of them behind a
client-side loader. **Jobs.mu serves everything it has and declares no total at all**: the list is
rendered server-side, the pager carries exactly one page, and nothing on the page says how big the
board is. So the question is not «how much is hidden» but «what can stand in for a total».

THE RULES. `www.jobs.mu/robots.txt` is read: 274 B, three lines — `User-agent: *`, a decorative
comment, and a `Sitemap:` — with **ZERO `Disallow` and ZERO `Allow`**. `_robots` renders
`state: read`, `certain: True`, group `*`, `sweep: True`, and **no `Crawl-delay` is written, so
4 s is ours**. The guard is taken on the exact path, host included, in a turn of its own.

**AND A HOST THAT FORBIDS NOTHING HAS NOT THEREBY CONSENTED TO EVERYTHING IT EXPOSES.** This host
publishes `/registration/`, `/login/`, `/password-recovery/` and `/companies/`, and `allowed()`
permits every one of them exactly as it permits `/jobs/`. What bounds this adapter is therefore
OURS, and it is a **POSITIVE allowlist** — `ALLOWED_PATHS`, three motifs, checked at the single
chokepoint every request passes through — because a list of REFUSALS would bet that we have
enumerated the paths worth refusing. Its default FAILS VISIBLY: an unknown path is refused by
name and the message says the rules permitted it. *The path filter here is a condition of SAFETY
and not an optimisation, which is the lesson of the Tajik board whose open rules covered 34 894
candidate CVs.*

*A first version of this file carried a refusal list instead, and it was INERT — the advert motif
refused anything outside `/job/<id>/` before `request()` was ever reached, so no CLI path could
fire it. Measured by trying it: `ad --url .../registration/` was refused by the WRONG guard, with
the wrong reason. An inert refusal list reads as a protection that was exercised.*

**THE WITNESS THE ISSUE PROPOSED IS FALSE, AND IT OVER-COUNTS. Measured, and the member is
named.** #698 wrote «la somme des compteurs de catégorie comme témoin». The footer of every page
carries «Jobs by Category» with a counter per category; on 2026-11-07 the seven non-empty
categories summed to **9** while the list served **8**. That disagreement is what tested it: *an
agreement on the small case proves nothing, because that is the regime where a page count and a
board count coincide.* The seven category pages were walked and their UNION is **8 distinct ids,
exactly the list's members** — so there is no ninth advert the list withholds. The cause is
MULTI-MEMBERSHIP: advert **139890** («Finance & Payment Reconciliation Officer») is counted by
both `707 accounting-finance` and `703 customer-service-bpo`. **A sum over categories is not a
count of adverts, and on this board it is wrong by exactly the number of adverts filed twice.**

**WHAT STANDS IN FOR THE TOTAL IS THE RSS FEED, BECAUSE IT IS A SECOND ENUMERATOR AND NOT A SECOND
READING OF THE FIRST.** `/rss/` (200, 11 393 B, md5 3d7f4a8f8385) carries 8 `<item>`s, and they
name the same 8 ids as the list. Three instruments then agree on the same members: the list's own
`ItemList` (`numberOfItems: 8`, 8 elements, 16 `href` for 8 distinct — each advert is linked
twice), the feed's 8 items, and the union of the 7 category pages. *That is a real witness. It is
weaker than a board stating its own total, and it is declared weaker.*

**AND THE FEED'S OWN LINKS ARE DEAD — the finding that decides the shape of `ad`.** Its `<link>`
and `<guid>` are CDATA under `/display-job/<id>/<Title-cased-and-accented>.html`;
`/display-job/139963/Driver.html` returns **HTTP 404** (61 187 B of readable body, not kept — a
readable body is not an answer, the code decides). The same advert under the list's form,
`/job/139963/driver/`, returns 200. So the feed enumerates correctly and addresses wrongly, and
this adapter takes its IDS and never its URLS. `ad --url` REFUSES the `/display-job/` form by
name, citing the measurement and its date rather than discovering the 404 at run time.

**WHAT MAKES THE FEED USABLE AT ALL IS THAT THE SLUG IS OPTIONAL.** `/job/139963/` without any
slug returns 200, **71 529 B, md5 09ed83f51bea — identical to the byte** to
`/job/139963/driver/`, and declares `rel="canonical"` on the slugged form. Hence `ad --code`,
which takes the bare identifier: without it, a feed whose links 404 would give ids that nothing
could resolve, since the slug is not reconstructible from a title (`Receptionist - Réceptionniste`
becomes `receptionist-receptionniste`, accents folded and punctuation dropped).

THE ADVERT IS A COMPLETE `JobPosting`. `title`, `description`, `datePosted` and `validThrough` as
ISO dates, `employmentType`, `hiringOrganization` with the employer's own site in `sameAs`,
`jobLocation` as a `PostalAddress` (locality, region, `addressCountry: MU`), `identifier` whose
`value` is the id, `directApply`, and **`baseSalary` in MUR with a min and a max**. Reading the
posting BOUNDS the redaction structurally, as on CareerHub: this site's own telephone lives in the
page footer, outside the posting, so scrubbing the page would declare a withheld contact on every
record for one no employer deposited.

**THE LIST CARRIES SIX FIELDS PER ADVERT, AND THEY ARE CLASSIFIED BY THEIR ICON AND NEVER BY THEIR
POSITION.** Each card's footer is five `<li><i class="icon-…"></i><span>…</span></li>`, and the
icon class NAMES the field — `icon-feather-briefcase` is the employer, `…location-on` the place,
`…awesome-money` the salary, `…access-time` the posting date, `…access-alarm` the closing date.
*An icon class is a DECLARATION; the order of the list items is a motif that would have to be
proved in both directions.* An icon this adapter does not know puts its text in `unclassified` and
**the run says so** — a default that fails visibly rather than one that silently files a stranger
under the last field that matched.

**THE SALARY HAS A POSITIVE FLOOR, NOT A REFUSAL LIST.** The field reads `Rs 12,501 - Rs 25,000`
on one card and `Not disclosed` on another, and a list of sentinels would bet that we have
enumerated the ways a board says «nothing». A value is emitted only when it CONTAINS A DIGIT.
And `salary_text` never reaches `scrub()` at all — it comes through `money()` — so no motif,
anchored or not, can destroy it: structural, not careful, which is the kyat's lesson (113 of
115 Burmese salaries lost to an unanchored nine-digit rule).

**PAGINATION IS NOT ESTABLISHED, AND THIS IS THE RESIDUE THAT MATTERS.** The pager renders exactly
`data-num="1"`, so the board has ONE page today; `?page=2` returns 200 with the SAME 8 ids. **On a
one-page list that reading is indistinguishable from three different mechanisms** — a pager that
clamps out-of-range requests to page 1, a parameter that is ignored, and a board that genuinely
has one page — and the conclusion CareerHub reached («`?page=2` is ignored») does NOT transpose,
because there the pager offered further pages and here it does not. So this adapter follows the
pager's own `data-num` values and makes no claim about the parameter. *And the consequence is that
**its multi-page branch is not exercised by the live board**: the fixtures take it, the corpus
never does, and a run reports which happened rather than leaving a green that reads «covered».*

NOT ESTABLISHED, and declared: that `sitemap-main.xml` (named by `/sitemap.xml`, a sitemapindex of
283 B pointing at it and at the blog's `advice/sitemap_index.xml`) holds nothing the list omits —
it is not walked, because three enumerators already agree on the same members, and «we did not
look» is not «there is nothing there». And the site's «2,700+ employers» and «Hundreds of new jobs
added daily» are its own marketing copy in a `<meta>` description: they are not a total, they are
not dated, and nothing here treats them as a denominator.

Measured 2026-11-07 03:22–03:27 UTC by the declared client, the guard on each exact path in a turn
distinct from retrieval, one token (`claude-user`): `/robots.txt` 200 (274 B, md5 fdf4c951f001),
`/jobs/` 200 (86 405 B, md5 7201332b2d52), `/jobs/?page=2` 200 (86 405 B, md5 6b2a575e2c65 — the
same size and a different digest, so the page carries a render element), `/rss/` 200 (11 393 B,
md5 3d7f4a8f8385, 8 items), `/job/139963/driver/` 200 (71 529 B, md5 09ed83f51bea),
`/job/139963/` 200 (71 529 B, md5 09ed83f51bea, identical), `/display-job/139963/Driver.html`
**404**, `/sitemap.xml` 200 (283 B), and the 7 category pages. The premise of #698 was measured
2026-09-18 and is fifty days old; its «rien de mesuré ; la liste n'est pas encore lue» is
answered, and its proposed witness is refuted.
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import datetime
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

import _ldjson
from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA
from _withheld import withheld_a_contact

HOST = "www.jobs.mu"
LIST = f"https://{HOST}/jobs/"
FEED = f"https://{HOST}/rss/"
DEFAULT_MAX_PAGES = 20

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# **The rules forbid NOTHING on this host, so what bounds this adapter is OURS — and it is a
# POSITIVE allowlist and not a refusal list.** `allowed()` permits `/registration/`, `/login/`,
# `/password-recovery/` and `/companies/` exactly as it permits `/jobs/`: a host that forbids
# nothing has not thereby consented to everything it exposes. A list of REFUSALS would bet that
# we have enumerated the paths worth refusing; this one bets only that we know the three we
# need, and **its default FAILS VISIBLY** — an unknown path is refused, named, and the message
# says the rules permitted it.
#
# *A first version of this file carried the refusal list instead, and it was INERT: the advert
# motif refused anything outside `/job/<id>/` before `request()` was ever reached, so no CLI
# path could fire it. An inert refusal list reads as a protection that was exercised.*
ALLOWED_PATHS = (
    re.compile(r"^/jobs/?$"),
    re.compile(r"^/rss/?$"),
    re.compile(r"^/job/\d+(?:/[^/]*)?/?$"),
)

# the list's form. The id ALONE resolves — measured identical to the byte — so the slug is
# optional in the motif, which is what lets `ad --code` exist.
AD_PATH_RE = re.compile(r"^/job/(\d+)(?:/[^/]*)?/?$")
# the form the FEED publishes, and it returns 404. Refused BY NAME rather than discovered at
# run time, because a 404 after a request is a request we did not need to make.
FEED_PATH_RE = re.compile(r"^/display-job/(\d+)/", re.I)

AD_HREF_RE = re.compile(r'href="https://www\.jobs\.mu/job/(\d+)/[^"]*"')
CARD_RE = re.compile(
    r'<a\s+href="(https://www\.jobs\.mu/job/(\d+)/[^"]*)"\s+class="utf-job-listing"\s*>(.*?)</a\s*>',
    re.S | re.I)
TITLE_RE = re.compile(r'<h3[^>]*class="utf-job-listing-title"[^>]*>(.*?)</h3>', re.S | re.I)
EXCERPT_RE = re.compile(r'<div[^>]*class="listing-item__desc"[^>]*>(.*?)</div>', re.S | re.I)
KIND_RE = re.compile(r'<span[^>]*class="[^"]*utf-job-status-item[^"]*"[^>]*>(.*?)</span>', re.S | re.I)
FOOT_RE = re.compile(r'<li>\s*<i[^>]*class="([^"]*)"[^>]*>\s*</i>\s*<span[^>]*>(.*?)</span>\s*</li>',
                     re.S | re.I)
PAGE_NUM_RE = re.compile(r'data-num="(\d+)"')
TAG_RE = re.compile(r"<[^>]+>")

# the icon class NAMES the field. A declaration, not a position.
BY_ICON = (
    ("briefcase", "employer"),
    ("location-on", "location_text"),
    ("awesome-money", "salary_text"),
    ("access-time", "posted_text"),
    ("access-alarm", "closing_text"),
)

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# ANCHORED on the MAURITIAN dialling code or a written label, and the reason is MEASURED on
# what this adapter emits: unanchored, the motif takes **the sixteen ISO dates** of the eight
# adverts (`2026-11-04`, `2026-12-04`, ...) and, over the whole advert page, the `rgba()`
# numbers of the site's own stylesheet. Anchored, it takes none of them — and nothing at all
# on this board, whose adverts deposit no telephone. *It is NOT the rupee range: `Rs 12,501 -
# Rs 25,000` is not a candidate even unanchored, the `Rs` between the numbers interrupting the
# motif. That claim was written first and measured false.*
PHONE_RE = re.compile(
    r"\+\s*\(?\s*230\s*\)?[\s.\-]?\d[\d\s.\-]{5,}\d"
    r"|(?:T[ée]l(?:[ée]phone)?|Phone|Mobile|Cell|Whatsapp|WhatsApp)\s*:?\s*\(?\+?\d[\d\s().\-]{5,}\d")

MONTHS = {m: i for i, m in enumerate(
    ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1)}
DATE_RE = re.compile(r"([A-Za-z]{3})[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})")

_PACE = None


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobsmu] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ") if isinstance(n, int) else str(n)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    global _PACE
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    if not any(pat.match(parts.path) for pat in ALLOWED_PATHS):
        die(f"{url}: not a path this adapter asks for. **The host's rules permit it** — they "
            f"carry no `Disallow` at all — and what decides is what the object holds, not what "
            f"the rules allow. Allowed here: /jobs/, /rss/, /job/<id>/.", EXIT_REFUSED)
    gate(url)
    if _PACE is None:
        _PACE = Pace(HOST, own=4.0)   # no Crawl-delay written; 4 s is ours
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text_of(markup):
    """Tags out, entities decoded by the LIBRARY and never by hand.

    The first version of this function replaced six named entities itself, and a live run put
    `Vos responsabilit&eacute;s cl&eacute;s` into an `excerpt`: **a hand-rolled decode does not
    raise, it returns TEXT**, and the text it returns is simply wrong in a field a candidate
    reads. `html.unescape` knows the whole table, numeric references included. Found by running
    the adapter against the host, not by reading it.
    """
    s = html.unescape(TAG_RE.sub(" ", markup or ""))
    return " ".join(s.split()).strip() or None


def iso_date(text):
    """`Added: Nov 4, 2026` -> `2026-11-04`. Unparseable text travels AS TEXT, never as a date."""
    if not text:
        return None
    m = DATE_RE.search(text)
    if not m:
        return None
    mon = MONTHS.get(m.group(1).lower())
    if not mon:
        return None
    try:
        return datetime.date(int(m.group(3)), mon, int(m.group(2))).isoformat()
    except ValueError:
        return None


def plain(s):
    """A JSON-LD text field, entities decoded, newlines kept.

    **This is the same defect as `text_of`, one consumer further.** Fixing the LIST's decode did
    not audit the ADVERT, which reads its text from the posting and never passes through
    `text_of`: a live `ad` run emitted `client&rsquo;s representative` and `equivalent.&nbsp;` in
    a `description`. The board HTML-escapes the text it puts inside its own JSON-LD, and
    `_ldjson.label()` rightly hands back the string it was given.
    """
    if not isinstance(s, str):
        return s
    out = html.unescape(s).replace("\u00a0", " ")
    return "\n".join(" ".join(line.split()) for line in out.splitlines()).strip() or None


def money(text):
    """A POSITIVE floor: a salary is a value only if it carries a digit.

    `Not disclosed` is one of the ways this board says «nothing», and a list of sentinels would
    bet that we have enumerated them all.
    """
    if not text:
        return None
    return text if any(c.isdigit() for c in text) else None


def scrub(s):
    """Contacts out of the text we emit, and the record says WHICH kinds were there."""
    if not isinstance(s, str) or not s:
        return s, []
    took = []
    if MAIL_RE.search(s):
        took.append("email")
        s = MAIL_RE.sub("[e-mail withheld]", s)
    out = PHONE_RE.sub("[telephone withheld]", s)
    if out != s:
        took.append("telephone")
    return (out.strip() or None), took


def item_list(html):
    """The `ItemList` CONTAINER, from the RAW blocks.

    Not from `_ldjson.objects()`, which expands the container into its items and loses
    `numberOfItems` with it — the count being the only witness external to our own extraction
    on this page.
    """
    for raw in _ldjson.blocks(html or ""):
        try:
            d = json.loads(raw, strict=False)
        except ValueError:
            continue
        for o in (d if isinstance(d, list) else [d]):
            if isinstance(o, dict) and o.get("@type") == "ItemList":
                return o
    return None


def cards_of(html):
    """One row per advert card, fields classified by their ICON and never by their position."""
    rows, unknown = [], []
    for m in CARD_RE.finditer(html or ""):
        url, ident, inner = m.group(1), m.group(2), m.group(3)
        row = {"id": ident, "url": url,
               "title": text_of((TITLE_RE.search(inner) or [None, ""])[1]
                                if TITLE_RE.search(inner) else ""),
               "employment_type": text_of((KIND_RE.search(inner).group(1))
                                          if KIND_RE.search(inner) else ""),
               "excerpt": text_of((EXCERPT_RE.search(inner).group(1))
                                  if EXCERPT_RE.search(inner) else "")}
        for cls, val in FOOT_RE.findall(inner):
            field = next((f for key, f in BY_ICON if key in cls), None)
            if field is None:
                unknown.append((cls.strip(), text_of(val)))
                continue
            row[field] = text_of(val)
        rows.append(row)
    return rows, unknown


def feed_ids(body):
    """The ids the FEED enumerates — never its URLS, which return 404.

    Its `<link>`/`<guid>` are CDATA, so a motif that assumed bare text would take nothing; the
    ids are read off the path, which is the only part of those URLs that resolves.
    """
    return set(re.findall(r"/display-job/(\d+)/", body or ""))


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    pages, seen_pages = [], set()
    url = LIST
    first_body = None
    announced = None
    for _ in range(max(1, a.max_pages)):
        code, body = request(url)
        if code == 404:
            die(f"{url}: HTTP 404 — the list is gone", EXIT_GONE)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if first_body is None:
            first_body = body
            nums = sorted({int(n) for n in PAGE_NUM_RE.findall(body)}) or [1]
            announced = nums
        pages.append(body)
        seen_pages.add(url)
        nxt = [n for n in (announced or [1]) if f"?page={n}" not in url and n != 1]
        nxt = [n for n in nxt if f"{LIST}?page={n}" not in seen_pages]
        if not nxt:
            break
        url = f"{LIST}?page={min(nxt)}"

    rows, unknown, order = [], [], []
    for body in pages:
        got, unk = cards_of(body)
        unknown.extend(unk)
        order.extend(got)
    by_id = {}
    for r in order:
        by_id.setdefault(r["id"], r)       # raw and distinct must be able to differ
    rows = list(by_id.values())

    lst = item_list(first_body)
    said = lst.get("numberOfItems") if isinstance(lst, dict) else None
    said = said if isinstance(said, int) else None
    hrefs = set(AD_HREF_RE.findall(first_body or ""))

    if not rows:
        die(f"{LIST}: 200 and not one advert card. The page carries "
            f"{th(len(hrefs))} advert link(s) and its `ItemList` states {said!r} — so this is a "
            f"page that CHANGED, not an empty board.", EXIT_PARTIAL)

    today = datetime.date.today().isoformat()
    expired = 0
    for r in rows:
        title, took = scrub(r.get("title"))
        emp, t2 = scrub(r.get("employer"))
        exc, t3 = scrub(r.get("excerpt"))
        took = took + t2 + t3
        closes = iso_date(r.get("closing_text"))
        if closes and closes < today:
            expired += 1
        rec = {
            "source": "jobsmu", "country": stamp,
            "ledger_id": f"jobsmu:{r['id']}", "id": r["id"],
            "title": title, "employer": emp,
            "location_text": r.get("location_text"),
            "employment_type": r.get("employment_type"),
            "salary_text": money(r.get("salary_text")),
            "posted": iso_date(r.get("posted_text")),
            "closes": closes,
            "excerpt": exc,
            "url": r["url"],
            "withheld_fields": sorted(set(took)),
        }
        if closes and closes < today:
            rec["expired"] = True
        if withheld_a_contact(rec["withheld_fields"]):
            rec["contacts_withheld"] = True
        print(json.dumps(rec, ensure_ascii=False))

    note(f"{th(len(rows))} advert(s) emitted from {th(len(pages))} page(s) of the list.")
    if said is not None:
        note(f"the page's own `ItemList` states {th(said)} and this run emitted "
             f"{th(len(rows))}: they {'agree' if said == len(rows) else 'DISAGREE'}. "
             f"**That count is the PAGE's, not the board's** — `numberOfItems` on a list page "
             f"counts what the page carries, and this board states no total of its own.")
    else:
        note("the page carries no `ItemList` total this time; the run says so rather than "
             "claiming one.")
    if hrefs:
        note(f"the markup carries {th(len(hrefs))} distinct advert link(s) for "
             f"{th(len(rows))} card(s) — each advert is linked twice in a card, so the two "
             f"readings of the same page must agree on the DISTINCT set, and they "
             f"{'do' if hrefs == set(by_id) else 'DO NOT'}.")
    note(f"the pager declares page(s) {', '.join(str(n) for n in (announced or [1]))}. "
         f"**No claim is made about `?page=N`**: measured 2026-11-07 the board had ONE page and "
         f"`?page=2` returned the same adverts, which on a one-page list cannot distinguish a "
         f"pager that clamps from a parameter that is ignored. This run followed the pager's own "
         f"`data-num` values"
         + (f" and the multi-page branch was NOT taken — on the live board it never is, so its "
            f"green comes from the fixtures and not from the corpus."
            if len(pages) == 1 else f" and took the multi-page branch for {th(len(pages))} pages."))
    if expired:
        note(f"{th(expired)} of {th(len(rows))} advert(s) have a closing date already past; they "
             f"are emitted and flagged `expired`, not dropped — the board serves them.")
    if unknown:
        note(f"{th(len(unknown))} footer field(s) carried an icon class this adapter does not "
             f"know: {', '.join(sorted({c for c, _ in unknown})[:6])}. Their text is NOT filed "
             f"under a field — a stranger goes to `unclassified` rather than under whichever "
             f"field matched last.")
    if a.witness:
        code, body = request(FEED)
        if code != 200:
            note(f"{FEED}: HTTP {code} — **no witness this run**, and that is said rather than "
                 f"left as a silence that reads like agreement.")
        else:
            ids = feed_ids(body)
            got = set(by_id)
            if not ids:
                note(f"{FEED}: 200 and no `/display-job/<id>/` in it — the feed's shape changed, "
                     f"so there is no witness this run.")
            elif ids == got:
                note(f"**WITNESS: the RSS feed enumerates the same {th(len(ids))} advert(s), by "
                     f"the same ids.** It is a SECOND enumerator and not a second reading of the "
                     f"first, which is what makes it a witness on a board that states no total.")
            else:
                note(f"**WITNESS DISAGREES**: the feed has {th(len(ids))} id(s), the list "
                     f"{th(len(got))}. Only in the feed: "
                     f"{', '.join(sorted(ids - got)[:12]) or 'none'}. Only in the list: "
                     f"{', '.join(sorted(got - ids)[:12]) or 'none'}. Two sets of different "
                     f"sizes do not say WHICH members are missing, so both are reported and "
                     f"neither is taken for the board.")
            note("the feed's own `<link>`s are NOT followed: they address "
                 "`/display-job/<id>/<Title>.html`, and that form returned HTTP 404 on "
                 "2026-11-07 while `/job/<id>/` returned 200. Its IDS are read, its URLS are "
                 "not.")
    else:
        note("`--no-witness` was passed, so this run has NO witness: the counts above are all "
             "readings of the same page, and the board states no total of its own.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the list states none per advert, and the "
             f"ADVERT does (`addressCountry`).")


def cmd_ad(a):
    if a.code:
        ident = a.code.strip()
        if not ident.isdigit():
            die(f"--code {a.code}: the board's identifier is digits (e.g. 139963)")
        url = f"https://{HOST}/job/{ident}/"
    else:
        url = a.url.strip()
        parts = urllib.parse.urlsplit(url)
        if FEED_PATH_RE.match(parts.path):
            m = FEED_PATH_RE.match(parts.path)
            die(f"--url {url}: this is the form the RSS feed publishes, and it returned HTTP 404 "
                f"on 2026-11-07 (measured on `/display-job/139963/Driver.html`). The advert "
                f"lives at `/job/{m.group(1)}/` — try `--code {m.group(1)}`. Refused by name "
                f"rather than by a request we already know the answer to.", EXIT_GONE)
        m = AD_PATH_RE.match(parts.path)
        if parts.scheme != "https" or parts.netloc != HOST or not m:
            die(f"--url {url}: a https://{HOST}/job/<id>/<slug>/ advert, or `--code <id>`")
        ident = m.group(1)
        url = f"https://{HOST}{parts.path}"

    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the advert is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    posts = _ldjson.postings(body)
    if not posts:
        die(f"{url}: 200 without a `JobPosting` block — {_ldjson.absent_reason(body)}",
            EXIT_PARTIAL)
    p = posts[0]
    took = []

    def pris(v):
        out, t = scrub(v)
        took.extend(t)
        return out

    # `one()` HERE, and this is what it is for: `{}` for a string, a list or None, so `.get()`
    # is legal whatever shape the board sent. `label()` is for the fields that are TEXT.
    org = _ldjson.one(p.get("hiringOrganization"))
    addr = _ldjson.one(_ldjson.one(p.get("jobLocation")).get("address"))
    sal = _ldjson.one(p.get("baseSalary"))
    val = _ldjson.one(sal.get("value"))
    canon = re.search(r'<link rel="canonical" href="([^"]+)"', body or "")
    r = {
        "source": "jobsmu", "country": a.country_code.upper() if a.country_code else None,
        "ledger_id": f"jobsmu:{ident}", "id": ident,
        "title": pris(plain(_ldjson.label(p.get("title")))),
        "employer": pris(plain(_ldjson.label(org))),
        "employer_site": _ldjson.label(org, "sameAs"),
        "posted": _ldjson.label(p.get("datePosted")),
        "valid_through": _ldjson.label(p.get("validThrough")),
        "employment_type": _ldjson.label(p.get("employmentType")),
        "city": _ldjson.label(addr.get("addressLocality")),
        "region": _ldjson.label(addr.get("addressRegion")),
        "country_stated": _ldjson.label(addr.get("addressCountry")),
        "salary_currency": _ldjson.label(sal.get("currency")),
        "salary_min": val.get("minValue"),
        "salary_max": val.get("maxValue"),
        "salary_unit": _ldjson.label(val, "unitText"),
        "direct_apply": p.get("directApply") if isinstance(p.get("directApply"), bool) else None,
        "description": pris(plain(_ldjson.label(p.get("description")))),
        "url": canon.group(1) if canon else url,
        "withheld_fields": sorted(set(took)),
    }
    if withheld_a_contact(r["withheld_fields"]):
        r["contacts_withheld"] = True
    vt = r["valid_through"]
    if isinstance(vt, str) and vt[:10] < datetime.date.today().isoformat():
        r["expired"] = True
    print(json.dumps(r, ensure_ascii=False))
    note(f"read from the advert's own `JobPosting`: "
         f"{', '.join(k for k, v in r.items() if v not in (None, [], ''))}.")
    if a.code:
        note(f"requested by identifier at `/job/{ident}/` — the slug is OPTIONAL, measured "
             f"identical to the byte to the slugged form, and that is what lets the RSS feed's "
             f"ids be resolved at all since its own links 404.")
    note("the redaction is BOUNDED to the posting's own fields, and that is structural: this "
         "site's telephone lives in the page footer, OUTSIDE the posting. Scrubbing the page "
         "would declare a withheld contact on every record for one no employer deposited.")
    if not r["withheld_fields"]:
        note("nothing was scrubbed from this advert; `withheld_fields` is empty because the "
             "posting carried no contact, not because none was looked for.")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Jobs.mu (Mauritius) — a board that states no total, whose size is established "
                    "by three agreeing enumerators, and whose own RSS links 404. Issue #698.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the list, with the RSS feed as its witness")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on every record")
    j.add_argument("--no-witness", dest="witness", action="store_false", default=True,
                   help="skip the RSS feed; the run then has NO witness and says so")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=DEFAULT_MAX_PAGES,
                   metavar="N", help=f"bound on pages followed (default {DEFAULT_MAX_PAGES})")
    j.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert, from its own `JobPosting`")
    g = d.add_mutually_exclusive_group(required=True)
    g.add_argument("--code", help="the board's identifier; the slug is optional")
    g.add_argument("--url", help="the advert's own address")
    d.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on the record")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
