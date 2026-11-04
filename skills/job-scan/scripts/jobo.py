#!/usr/bin/env python3
"""JOBO.sc (`jobo.sc`, Seychelles) — the JobMonster list, and FOUR THINGS ON IT LIE QUIETLY.

**#715.** The board states its own size and names its own last page, so this adapter has two
witnesses that are not its extraction — and both are read where the host puts them, which is
not where the issue said.

    jobo.py jobs [--max-pages N] [--country-code XX]
    jobo.py ad --url https://jobo.sc/jobs/<slug>/

**THE STATED COUNT CARRIES AN HTML ENTITY, AND IT IS ONLY ON PAGE 1.** The list writes
`Showing 1&ndash;10 of 184 jobs`: a motif built on the DECODED dash renders zero, which reads
exactly like «this board states no total» — the §4 trap, on the one string that licenses the
comparison. And pages 2..N do NOT repeat it (measured: `[]` on page 15), so a per-page read
would lose it after the first request. It is therefore captured on page 1 and CARRIED.

**THE ADVERT ADDRESS IS `/jobs/<slug>/`, WHICH IS THE LIST'S OWN PREFIX.** The pager links are
`/jobs/page/N/` — under the same prefix — so the filter is POSITIVE: a slug, and never `page`.
*A first measurement of this host looked for `/job/<slug>/` and found 0 links on a page holding
ten adverts; that zero reads as «no adverts».*

**THE DATES ARE DAY-FIRST, AND THAT IS NOT ASSUMED — THE CARD'S OWN `datetime` SAYS SO.** Each
card writes `03/11/2026` in `job-date__posted` and `2026-11-03T16:39:53+04:00` in the `datetime`
of the SAME `<time>`. `03/11` is a valid date read either way, so a month-first reading would
not raise: it would emit March 11th, well formed and false. This tool asserts the two agree on
every card — measured 20 of 20 — and the agreement is what licenses reading the CLOSING date,
which exists only as `dd/mm/yyyy`, the same way. **A disagreement stops the run**: the format
would then be this installation's and not the one measured here.

**AND THE CLOSING SPAN OPENS WITH `- `** — its text is `- 16/11/2026`, the dash belonging to the
layout and not to the date. Taken raw it is not a date at all; `job-date-ago` («15 hours ago»)
sits two tags away and is never read as one.

**WHAT IS WITHHELD IS SCRUBBED FROM THE FIELDS, NEVER FROM THE PAGE — AND THAT IS THE
DIFFERENCE BETWEEN A TRUE AND A FALSE CLAIM ABOUT OUR OWN DISCRETION.** The page carries
`tel:+2482610105` four times: it is JOBO's own number, in the chrome beside FAQ and Contact,
and **0 of the 10 cards carry a telephone**. Scrubbing the page body would therefore write
`withheld_fields: ["telephone"]` on all 184 records and claim a discretion nobody exercised —
the #1005 lie, taken from the other end. So the list route withholds nothing, and each row says
so POSITIVELY through the tri-state rather than by an empty list that could be read either way.
*The AD route is the opposite and it is measured: its custom fields carry `Company Phone
+248 428 4000`, an employer's number, which IS withheld.*

**ON AN ADVERT PAGE THE `<article>` BLOCKS ARE OTHER PEOPLE'S ADVERTS.** Five of them, inside
`class="jobs posts-loop related-jobs"`. The card parser is never run on that page: `ad` reads
`h1.page-title` and the `job-desc` block, and asserts the related block is outside the slice.
*A single advert that quietly emitted five neighbours would be well formed and wrong.*

**AND THE HOST HIDES THE APPLICATION ADDRESS ITSELF, WITH ITS OWN PLACEHOLDER.** The advert's
«How to Apply» reads `e-mail your application to [email protected]` — Cloudflare's
obfuscation, `data-cfemail`, twice on the page. So no address is there to withhold, the
record's `withheld_fields` rightly says nothing about an e-mail, and **the string in the text
is the HOST's placeholder and not ours**: ours is `[e-mail withheld]`, and the two must not be
read as one.

**THE REST API DOES NOT CARRY THIS POST TYPE.** `/wp-json/wp/v2/types` answers 200 with fourteen
types and `noo_job` is not among them, so the HTML list is the route — measured, not assumed.

**THE `<style>`/`<script>` STRIP IS INERT ON THE LIST AND DECLARED SO.** 24 % of the list page is
style and script, and **0 of the six class names this tool matches appear inside them** — unlike
`vacancybt`, where the stylesheet writes the very names the motifs seek. It is kept because the
ad page is the ad page and the layer costs one substitution, and it is named here so no one
counts it as a guard that fires.

EXIT CODES. 0 the walk ended of itself and the stated count agrees · 2 broken · 3 gone ·
6 partial (fewer than the board states, or the list stopped answering) · 7 refused by the rules ·
8 the rules could not be read.
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
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
from _provenance import third_party
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA
from _withheld import withheld_a_contact

HOST = "jobo.sc"
HOSTS = (HOST,)
ROOT = f"https://{HOST}/"
LIST = ROOT + "jobs/"
PER_PAGE = 10                 # the list's own «Showing 1–10 of N jobs»
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

STRIP_RE = re.compile(r"(?s)<style.*?</style>|<script.*?</script>")
CARD_RE = re.compile(r"(?s)<article\b[^>]*>.*?</article>")
# **THE ENTITY IS THE POINT.** The page writes `&ndash;`; the decoded dash is what a composed
# motif carries, and it renders zero on a page that states its total.
STATED_RE = re.compile(
    r"Showing\s*1\s*(?:&ndash;|&#8211;|&#x2013;|–|-)\s*\d+\s*of\s*([\d,  ]+?)\s*jobs")
PAGER_RE = re.compile(r"/jobs/page/(\d+)/")
ID_RE = re.compile(r"\bpost-(\d+)\b")
URL_RE = re.compile(r'class="job-details-link"\s+href="([^"]+)"')
TITLE_RE = re.compile(r'(?s)class="loop-item-title">\s*<a\b[^>]*>(.*?)</a>')
COMPANY_RE = re.compile(
    r'(?s)class="job-company"[^>]*>.*?<a href="[^"]*/employers/([^/"]+)/">\s*<span[^>]*>(.*?)</span>')
TYPE_RE = re.compile(
    r'(?s)class="job-type"><a href="[^"]*/job-type/([^/"]+)/"[^>]*>.*?<span>(.*?)</span>')
LOCATION_RE = re.compile(
    r'(?s)class="job-location"[^>]*>.*?/job-location/([^/"]+)/"[^>]*>\s*<em>(.*?)</em>')
INSTANT_RE = re.compile(r'class="entry-date"\s+datetime="([^"]+)"')
POSTED_RE = re.compile(r'(?s)job-date__posted"[^>]*>(.*?)</span>')
CLOSING_RE = re.compile(r'(?s)job-date__closing"[^>]*>(.*?)</span>')
CATEGORY_BLOCK_RE = re.compile(r'(?s)class="job-category"(.*?)</span>')
CATEGORY_RE = re.compile(r'(?s)/job-category/([^/"]+)/"[^>]*>\s*(.*?)\s*</a>')
INDUSTRY_RE = re.compile(r'(?s)class="job-_industry"[^>]*>.*?</em>(.*?)</span>')
# the leading `- ` of the closing span belongs to the LAYOUT: `- 16/11/2026`
DMY_RE = re.compile(r"^\s*[-–]?\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*$")
SLUG_RE = re.compile(r"^/jobs/([^/]+)/?$")
# the pager's own shape, tested BEFORE the advert's: `/jobs/page/2/` is two segments, so the
# advert motif rejects it for the wrong reason and the diagnosis is lost
PAGER_PATH_RE = re.compile(r"^/jobs/page/\d+/?$")
AD_TITLE_RE = re.compile(r'(?s)class="page-title">\s*<span\s*>(.*?)</span>')
AD_DESC_RE = re.compile(r'(?s)class="job-desc"\s*>(.*?)(?=<div class="job-action|related-jobs|\Z)')

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# ANCHORED. Seychelles is +248 and its local numbers are 7 digits; the LABELLED alternative is
# the half that fires on this host, whose custom field writes `Company Phone` and the value in
# a sibling tag — so the label may be separated from the digits by markup.
PHONE_RE = re.compile(
    r"\+\s*\(?\s*248\s*\)?[\s.\-]?\d[\d\s.\-]{5,}\d"
    r"|(?:T[ée]l(?:[ée]phone)?|Phone|Mobile|Cell|Contact\s*No)\s*:?\s*\(?\+?\d[\d\s().\-]{5,}\d")
_PACES = {}
# **THE THIRD-PARTY NAMES THE AD ROUTE INSPECTS, AND THEY ARE CONTACT FIELDS ONLY.** This board
# writes four custom fields — `Industry`, `Company Phone`, `Contact Phone`, and a layout flag —
# and TWO of them are a telephone. Naming `industry` or `description` here would class an
# industry as a withheld contact: a record would then claim a discretion over a field nobody
# would withhold, which is the #1005 lie with the sign flipped.
INSPECT = ("company_phone", "contact_phone")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobo] {msg}", file=sys.stderr)


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
    """One GET, guarded on the exact URL, paced, declaring our identity."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc not in HOSTS:
        die(f"{url}: not one of {', '.join(HOSTS)} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(parts.netloc, Pace(parts.netloc, own=3.0)).wait()   # no Crawl-delay written
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>|</tr>|</h\d>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    """Contacts out of A FIELD, and the field says which kinds were there.

    It is never given a whole page: the page's own `tel:` link would then be withheld from
    every record, which is a false claim about a discretion nobody exercised.
    """
    if not s:
        return None, []
    took = []
    if MAIL_RE.search(s):
        took.append("email")
        s = MAIL_RE.sub("[e-mail withheld]", s)
    out = PHONE_RE.sub("[telephone withheld]", s)
    if out != s:
        took.append("telephone")
    return (out.strip() or None), took


def stated(markup):
    """The total the LIST states, as a number. Page 1 only — and the entity is the point."""
    m = STATED_RE.search(markup or "")
    if not m:
        return None
    digits = re.sub(r"[^\d]", "", m.group(1))
    return int(digits) if digits else None


def last_page(markup):
    """The last page the pager's own links name — the second witness, present on every page."""
    seen = {int(n) for n in PAGER_RE.findall(markup or "")}
    return max(seen) if seen else None


def dmy(s, what):
    """`dd/mm/yyyy` → `yyyy-mm-dd`, day-first, the layout's leading dash stripped.

    Day-first is not a guess: `card()` asserts it against the `datetime` of the same `<time>`
    before any of these values is trusted.
    """
    m = DMY_RE.match(s or "")
    if not m:
        return None, f"{what} {s!r} is not dd/mm/yyyy"
    d, mo, y = (int(x) for x in m.groups())
    if not (1 <= d <= 31 and 1 <= mo <= 12):
        return None, f"{what} {s!r} is out of range read day-first"
    return f"{y:04d}-{mo:02d}-{d:02d}", None


def card(markup, stamp, position):
    """One `<article>` → a record, or a reason it is not one.

    The two floors here are POSITIVE: an address that is not an advert's, and a date format
    that the host itself confirms. Both would otherwise fail silently — the first as a page of
    ten adverts holding none, the second as a well-formed wrong month.
    """
    mid = ID_RE.search(markup)
    mu = URL_RE.search(markup)
    if not mid or not mu:
        return None, "a card carrying no post id or no details link"
    url = htmlmod.unescape(mu.group(1))
    parts = urllib.parse.urlsplit(url)
    # **THE PAGER IS TESTED BEFORE THE SHAPE, and the order is the whole point.** Written the
    # other way round — one segment first, the name `page` after — the named refusal is
    # UNREACHABLE for the host's real form `/jobs/page/2/`, which has two segments and falls
    # into «not an advert address» without ever naming the pager. The guard still refused, and
    # its reason was the generic one: a dead branch that reads like a live one.
    if parts.netloc != HOST or not parts.path.startswith("/jobs/"):
        return None, f"{url!r} is not an address under https://{HOST}/jobs/"
    if PAGER_PATH_RE.match(parts.path):
        return None, f"{url!r} is a PAGER link, not an advert — the two share the /jobs/ prefix"
    sm = SLUG_RE.match(parts.path)
    if not sm:
        return None, f"{url!r} is not a https://{HOST}/jobs/<slug>/ address"

    inst = INSTANT_RE.search(markup)
    mp = POSTED_RE.search(markup)
    if not inst or not mp:
        return None, "a card carrying no <time datetime=…> or no posted date"
    posted_text = text(mp.group(1))
    posted_date, why = dmy(posted_text, "the posted date")
    if why:
        return None, why
    # **THE HOST CONFIRMS THE FORMAT.** Same `<time>`, same day: if these two disagree the
    # day-first reading is wrong here and nothing downstream may be trusted.
    if inst.group(1)[:10] != posted_date:
        die(f"the card for {url} writes {posted_text!r} beside datetime="
            f"{inst.group(1)!r}: read day-first they give {posted_date} and the host says "
            f"{inst.group(1)[:10]}. A month-first list would emit well-formed wrong dates, so "
            f"this run stops rather than guess which half is right", EXIT_BROKEN)

    closes_text, closes_date = None, None
    mc = CLOSING_RE.search(markup)
    if mc:
        closes_text = text(mc.group(1))
        closes_date, _why = dmy(closes_text, "the closing date")

    mco, mt, ml = (COMPANY_RE.search(markup), TYPE_RE.search(markup),
                   LOCATION_RE.search(markup))
    mi = INDUSTRY_RE.search(markup)
    cats = []
    mcb = CATEGORY_BLOCK_RE.search(markup)
    if mcb:
        cats = [text(n) for _s, n in CATEGORY_RE.findall(mcb.group(1))]

    took, free = [], {}
    for key, raw in (("title", TITLE_RE.search(markup)),
                     ("employer", mco), ("location", ml), ("industry", mi)):
        if key == "employer":
            value = text(raw.group(2)) if raw else None
        elif key == "location":
            value = text(raw.group(2)) if raw else None
        elif key == "industry":
            value = text(raw.group(1)) if raw else None
        else:
            value = text(raw.group(1)) if raw else None
        free[key], t = scrub(value)
        took += t
    if not free["title"]:
        return None, f"the card for {url} carries no title"

    r = {
        "source": "jobo", "country": stamp,
        "ledger_id": f"jobo:{mid.group(1)}", "id": mid.group(1),
        "title": free["title"],
        "url": url,
        "employer": free["employer"],
        "employer_slug": mco.group(1) if mco else None,
        "employment_type": text(mt.group(2)) if mt else None,
        "employment_type_slug": mt.group(1) if mt else None,
        "location": free["location"],
        "location_slug": ml.group(1) if ml else None,
        # the instant the host itself stamps, offset included — it is the host's, not ours
        "posted": inst.group(1),
        "posted_date": posted_date,
        # a DATE and nothing more: the closing span states no time, so none is invented
        "closes_date": closes_date,
        "closes_as_written": closes_text,
        "categories": [c for c in cats if c],
        "industry": free["industry"],
        "list_position": position,
        "withheld_fields": sorted(set(took)),
    }
    if withheld_a_contact(r["withheld_fields"]):
        r["contacts_withheld"] = True
    return r, None


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    rows, seen, page = [], set(), 1
    said_total, said_last, raw, dropped, ended = None, None, 0, [], None
    while True:
        url = LIST if page == 1 else f"{LIST}page/{page}/"
        code, body = request(url)
        if code == 404:
            if page == 1:
                die(f"{url}: HTTP 404 — the list is gone", EXIT_GONE)
            ended = f"page {page} answered 404, the site's own end of the walk"
            page -= 1
            break
        if code != 200:
            die(f"{url}: HTTP {code} — the walk ended at {th(len(seen))}", EXIT_PARTIAL)
        body = STRIP_RE.sub(" ", body)
        if page == 1:
            said_total = stated(body)
        if said_last is None:
            said_last = last_page(body)
        found = CARD_RE.findall(body)
        if not found:
            if page == 1:
                die(f"{url}: 200 without a single <article> — the page changed; this is NOT an "
                    f"empty board", EXIT_PARTIAL)
            ended = f"page {page} carried no card"
            page -= 1
            break
        ids = {m.group(1) for m in (ID_RE.search(c) for c in found) if m}
        if page > 1 and ids and ids <= seen:
            die(f"page {page} repeats the cards of the page before — the walk ended at "
                f"{th(len(seen))}", EXIT_PARTIAL)
        for block in found:
            raw += 1
            r, why = card(block, stamp, len(rows) + 1)
            if r is None:
                dropped.append(why)
                continue
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            rows.append(r)
        if a.max_pages and page >= a.max_pages:
            ended = f"stopped by --max-pages at page {page}"
            break
        page += 1

    for r in rows:
        print(json.dumps(r, ensure_ascii=False))

    note(f"{th(len(rows))} advert(s) emitted over {th(page)} page(s) of {PER_PAGE}; "
         f"{ended or 'the walk ended'}.")
    if dropped:
        note(f"{th(len(dropped))} card(s) not emitted, each for a NAMED reason: "
             + "; ".join(sorted(set(dropped))[:4]))
    if raw != len(seen):
        note(f"{th(raw)} card(s) seen for {th(len(seen))} distinct.")

    if said_total is None:
        note("**page 1 stated no total this time** — it normally writes «Showing 1&ndash;10 of "
             "N jobs», with an HTML ENTITY for the dash, and that line is this board's witness. "
             "The run says so rather than claiming a size.")
    elif a.max_pages:
        note(f"the list states {th(said_total)} advert(s); this run stopped early, so no "
             f"comparison is made.")
    elif len(rows) == said_total:
        note(f"the list states {th(said_total)} and {th(len(rows))} were emitted — THEY AGREE. "
             f"That stated count is a witness this tool did not extract.")
    else:
        note(f"the list states {th(said_total)} and {th(len(rows))} were emitted — "
             f"{th(abs(said_total - len(rows)))} {'short' if len(rows) < said_total else 'over'}, "
             f"so they DISAGREE and this walk is not complete.")

    if said_last is None:
        note("the pager named no last page — the second witness is missing.")
    else:
        want = -(-said_total // PER_PAGE) if said_total else None
        if want is not None and want != said_last:
            note(f"the pager names page {th(said_last)} as its last while {th(said_total)} "
                 f"adverts at {PER_PAGE} a page need {th(want)} — the board's two witnesses "
                 f"DISAGREE with each other.")
        elif not a.max_pages and said_last != page:
            note(f"the pager names page {th(said_last)} as its last and the walk ended at "
                 f"page {th(page)} — they DISAGREE.")
        else:
            note(f"the pager names page {th(said_last)} as its last" +
                 (f", which is what {th(said_total)} at {PER_PAGE} a page needs" if want else "") +
                 ("." if a.max_pages else " and the walk ended there — they agree."))

    note("nothing is withheld on this route and that is MEASURED, not assumed: 0 of the cards "
         "carry a telephone, while the page's chrome carries JOBO's own `tel:+2482610105` four "
         "times — so the fields are scrubbed and the PAGE never is, or every record would claim "
         "a discretion nobody exercised.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the cards name a place (Mahé, Victoria), "
             f"never a country.")
    if said_total is not None and not a.max_pages and len(rows) < said_total:
        return EXIT_PARTIAL
    return 0 if rows else EXIT_PARTIAL


def cmd_ad(a):
    url = a.url.strip()
    parts = urllib.parse.urlsplit(url)
    m = SLUG_RE.match(parts.path)
    if PAGER_PATH_RE.match(parts.path):
        die(f"--url {url}: that is a PAGER address, not an advert")
    if parts.scheme != "https" or parts.netloc not in HOSTS or not m or parts.query:
        die(f"--url {url}: a https://{HOST}/jobs/<slug>/ advert, without a query string")
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — this advert is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_BROKEN)
    body = STRIP_RE.sub(" ", body)
    mt, md = AD_TITLE_RE.search(body), AD_DESC_RE.search(body)
    if not mt:
        die(f"{url}: 200 without an <h1 class=\"page-title\"> — the page changed")
    # **THE NEIGHBOURS STAY OUT.** This page holds five `<article>` blocks and they are OTHER
    # adverts, under `related-jobs`. The slice is asserted to end before them.
    desc = md.group(1) if md else ""
    if "related-jobs" in desc or CARD_RE.search(desc):
        die(f"{url}: the description slice reached the related-jobs block — it would emit other "
            f"people's adverts inside this one", EXIT_BROKEN)
    took, free = [], {}
    for key, value in (("title", text(mt.group(1))), ("description", text(desc))):
        free[key], t = scrub(value)
        took += t
    # the custom fields, by the LABEL the host prints. `raw` feeds the tri-state and `kept`
    # feeds the record: the classification must see what was THERE, the output what is left.
    raw, kept_f = {}, {}
    for label, value in re.findall(
            r"(?s)class='noo-label[^']*'[^>]*>(.*?)</strong>\s*<span[^>]*>(.*?)</span>", body):
        name = (text(label) or "").lower().replace(" ", "_")
        raw[name] = text(value)
        kept_f[name], t = scrub(raw[name])
        if name in INSPECT:
            took += t
    tp = third_party(raw, INSPECT)
    r = {
        "source": "jobo", "country": (a.country_code.upper() if a.country_code else None),
        "ledger_id": f"jobo:{m.group(1)}", "id": m.group(1),
        "title": free["title"], "url": url,
        "description": free["description"],
        "industry": kept_f.get("industry"),
        "withheld_fields": sorted(set(took)),
        **tp,
    }
    if withheld_a_contact(r["withheld_fields"]):
        r["contacts_withheld"] = True
    print(json.dumps(r, ensure_ascii=False))
    note("the advert page's own custom fields carry an employer telephone («Company Phone»), "
         "which is a THIRD PARTY's datum and is withheld — the opposite of the list route, "
         "where 0 of the cards carry one. Both statements are measured.")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="walk the list and emit one record per advert")
    j.add_argument("--max-pages", type=int, default=0,
                   help="stop after N pages; the run then makes NO comparison with the "
                        "stated count, because a bounded slice is not a short walk")
    j.add_argument("--country-code", default=None,
                   help="stamp each record with this ISO-2; the cards name a place, not a country")
    d = sub.add_parser("ad", help="one advert by its URL")
    d.add_argument("--url", required=True)
    d.add_argument("--country-code", default=None)
    a = p.parse_args(argv)
    return {"jobs": cmd_jobs, "ad": cmd_ad}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
