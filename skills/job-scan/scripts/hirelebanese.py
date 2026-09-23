#!/usr/bin/env python3
"""HireLebanese (`www.hirelebanese.com`), Lebanon's generalist since 2000: the browse route is a plain GET, the results page states **its total AND its window** on every page, and the site's own 44 location facets **sum exactly to that total** — so the count can be checked at each step and place by place. Issue #657.

  hirelebanese.py jobs [--country-id N] [--since YYYY-MM-DD] [--country-code LB] [--max-pages N]
  hirelebanese.py locations        the site's own facets: id, name, count (1 request)

WHAT IT IS. The Lebanese generalist — employers file vacancies and jobseekers apply through it — and
it carries postings from outside Lebanon too: its own facets name Iraq (30), Congo (29), Ghana (26),
Ivory Coast (12), Angola (7) and thirty more. **Until this adapter Lebanon had no route at all.**

THE RULES. `www.hirelebanese.com` opens on `/`, on `/jobsearch.aspx`, on `/jseeker/findjobhome.aspx`
and on the browse route, `certain: True`, **no Crawl-delay written**; 2 s is ours. The guard is taken
on the exact path.

THE ROUTE IS A GET, AND THE CARD'S FIRST READING SAID OTHERWISE. `/jobsearch.aspx` is an ASP.NET
WebForms **search form** with a `__VIEWSTATE` and a POST — and it is *not* the road to the board.
What the browse page's own «Next» and «Last» links carry is
`searchresults.aspx?order=date&keywords=&category=&type=&duration=&country=&state=&city=&emp=&pg=N`:
**50 adverts a page, 65 pages, no POST and no ViewState.** Every facet link is a plain GET too
(`searchresults.aspx?resume=1&top=0&category=&company=&country=N`).

TWO WITNESSES, AND THE SECOND IS THE ONE A TOTAL CANNOT BE.

* **Every page states «Job Posts A - B of T Results Found».** So the walk is checked at *each* page
  and not once at the end: `A` must be `50 × (page − 1) + 1`, `B − A + 1` must be what the page
  actually carried, and `T` must not move. A total that shifts mid-walk is a board that changed
  under us, and the run says so rather than averaging it away.
* **The browse page states a count per location, and the 44 of them sum to 3 210 — the stated total
  to the unit** (measured 2026-09-22). *That settles a question this card had left open and warned
  about*: «Lebanon (1951)» and «Lebanon - Beirut (901)» are **siblings, not parent and child**, and
  the facets partition the board. Had they nested, the sum would have exceeded the total by the
  1 010 of the four Lebanese sub-entries. **The arithmetic was free — the numbers were already
  held — and it turned a caution into a usable witness.**

THE LOCATION IS READ BY THE SITE'S OWN VOCABULARY, NOT BY A SEPARATOR. A row prints
«employer - location», and the location itself may contain the separator: «shareQ - Lebanon -
Beirut». Splitting on the last « - » yields «Beirut», which **is not a facet name** and would never
match the counts. So the run takes the **longest facet name the string ends with** — the site's own
44 labels decide — and a row whose tail matches none keeps its whole string as the employer, with
the location left null **and counted**.

**AND THE LABELS ARE CUT AT TWENTY CHARACTERS.** Eight of the 44 are exactly that long while the
rows print the full names — «United Arab Emirates - Dubai», «Democratic Republic of the Congo»,
«United States - Wyoming». *Measured on the first full walk: fourteen rows ended in a place the site
does name, and three of its facets read zero.* So a label of exactly twenty characters matches a
tail that **begins** with it. **And three different ids collapse onto the single label «United Arab
Emirates»**, so the site's counts are **summed per label**: our rows carry the label and not the id,
and telling the three apart would invent a distinction the page does not expose. *The record keeps
the row's own words; the label is only what buckets it for the count — the two are not conflated.*

**A FEATURED ADVERT IS READ AND FLAGGED.** The board sells the placement and marks it
(`panel-heading featured-job-color`), putting a star image **between `<h4>` and the link**. A parser
requiring the two adjacent dropped one panel on eighteen pages of the first full walk — **3 199 read
against a stated 3 232** — and the page's own per-page window is what said so. *The thing that hid
the adverts turned out to name a field worth carrying*: `featured` is emitted only when set, and the
run prints how many there were (33 of 3 232 on 2026-09-23).

**WITHHELD:** e-mail addresses and telephone numbers in anything emitted, at a threshold of nine
digits (a date is spared, and the run says how many shorter runs it left). `contacts_withheld` on
every record. **The advert page is never fetched** — the panel carries the excerpt the board itself
shows, `detail_read: false` — and `/jseeker/login.aspx` is refused before the gate: no account is
ever created.

`--country-id` walks the site's own facet instead of the whole board (`locations` lists them).
`--since` keeps what was posted on or after a date. `--country-code` STAMPS: **the board is not only
Lebanese**, so the country a record carries is the one its row prints, and the stamp stays the
user's.

Measured 2026-09-22 and 2026-09-23 by the declared client, the guard on the exact path, two reads of
each route: `/jseeker/findjobhome.aspx` 200 ×2, **110 865 B, md5 25e3856878b4 both**;
`searchresults.aspx?resume=1&top=0&category=&company=&country=` 200 ×2, **39 583 B, md5 5dab6fb7a558
both**, **50 adverts and «Job Posts 1 - 50 of 3210 Results Found»**, its own Last link at **pg=65**
(50 × 65 = 3 250 ≥ 3 210); 44 location facets summing to **3 210**.
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

HOST = "www.hirelebanese.com"
BROWSE = "/jseeker/findjobhome.aspx"
RESULTS = "/searchresults.aspx"
PAGE_SIZE = 50
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

PANEL_RE = re.compile(r'<div class="panel panel-default jobs-margin">')
# **Anything may sit between `<h4>` and the link** — a FEATURED advert carries a star image
# there, and requiring the two to be adjacent lost one panel in eighteen pages of the first
# full walk: 3 199 read against a stated 3 232. The page's own per-page window said so.
TITLE_RE = re.compile(r'<h4>(?:(?!</h4>).)*?<a href="\.\./jobdetails\.aspx\?id=(\d+)">(.*?)</a>', re.S)
FEATURED_RE = re.compile(r'panel-heading[^"]*featured-job-color')
WHO_RE = re.compile(r'<div class=col-xs-9>(.*?)</div>', re.S)
WHEN_RE = re.compile(r'style="color: gray[^"]*">(.*?)</div>', re.S)
EXCERPT_RE = re.compile(r'<div class=col-xs-12>(.*?)</div>', re.S)
STATED_RE = re.compile(r"Job Posts\s*(\d[\d,]*)\s*-\s*(\d[\d,]*)\s*of\s*(\d[\d,]*)\s*Results Found", re.I)
# **The pattern must NOT trim the label**: the page cuts at twenty characters and one label's
# twentieth is a space, so `\s*([^<]+?)\s*` — trimming inside the regex — measured nineteen and
# the label stopped looking truncated. The capture is raw; the trimming happens after the length
# is taken. *The instrument was doing the normalisation that hid the thing being measured.*
FACET_RE = re.compile(r'<a href="\.\./searchresults\.aspx\?([^"]+)"[^>]*>(?:<img[^>]*>)?([^<]*)</a>\s*\((\d+)\)')
POSTED_RE = re.compile(r"Posted at\s+([A-Za-z]{3})\w*\s+(\d{1,2}),\s*(\d{4})")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
RUN_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{5,}\d(?!\w)")
DATE_TEXT_RE = re.compile(r"\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}|\d{4}-\d{2}-\d{2}")
DIGITS_FOR_A_PHONE = 9
MONTHS = {m.lower(): i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[hirelebanese] {msg}", file=sys.stderr)


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
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    if re.search(r"/(?:login|register|signup)\b", parts.path, re.I):
        die(f"{url}: an account path is never requested", EXIT_REFUSED)
    a = gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=a.get("crawl_delay") or 2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml",
                                                         "Accept-Language": "en, ar, fr"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)

    def one(m):
        run = m.group(0)
        if DATE_TEXT_RE.fullmatch(run.strip()):
            return run
        if sum(1 for c in run if c.isdigit()) < DIGITS_FOR_A_PHONE:
            return run
        return "[telephone withheld]"

    return RUN_RE.sub(one, s).strip() or None


def shortish(s):
    n = 0
    for run in RUN_RE.findall(s or ""):
        d = sum(1 for c in run if c.isdigit())
        if 7 <= d < DIGITS_FOR_A_PHONE and not DATE_TEXT_RE.fullmatch(run.strip()):
            n += 1
    return n


def when(s):
    """«Posted at Sep 22, 2026» → `2026-09-22`; anything else as read."""
    m = POSTED_RE.search(s or "")
    if not m or m.group(1).lower() not in MONTHS:
        return None
    return f"{int(m.group(3)):04d}-{MONTHS[m.group(1).lower()]:02d}-{int(m.group(2)):02d}"


def facets_of(markup):
    """The site's own location facets: `[(name, id, count, cut)]`, page order.

    **`cut` is measured on the label AS WRITTEN, before stripping** — and that matters, because
    the page cuts at twenty characters and one label's twentieth character is a space:
    `'Democratic Republic '`. Stripping first turns it into nineteen characters and it stops
    looking truncated, which is exactly how it survived one round of this fix — *our own
    normalisation hid the thing we were measuring.* So the length is taken before `.strip()`,
    and only the leading indentation of the markup is removed.
    """
    out = []
    for query, name, count in FACET_RE.findall(markup or ""):
        m = re.search(r"country=(\d+)", query)
        if m:
            written = htmlmod.unescape(name).lstrip()
            out.append((written.strip(), m.group(1), int(count), len(written) >= LABEL_CAP))
    return out


LABEL_CAP = 20          # the browse page truncates its facet labels at twenty characters


def split_who(who, facets):
    """«shareQ - Lebanon - Beirut» → («shareQ», «Lebanon - Beirut», «Lebanon - Beirut»).

    Returns `(employer, the place AS THE ROW PRINTS IT, the site's label for it)`.

    **The site's own labels decide where the employer ends**, not the last separator: the place
    itself carries « - », so a positional split yields «Beirut», which is no facet's name.

    **And the labels are TRUNCATED at twenty characters** — eight of the 44 are exactly that long,
    and the rows print the full names: «United Arab Emirates - Dubai», «Democratic Republic of the
    Congo», «United States - Wyoming». So a label of exactly twenty characters matches a tail that
    BEGINS with it. *Measured: without this, fourteen rows ended in a place the site does name,
    and three of its facets read zero.*

    The record keeps the row's own words; the label is only what buckets it for the count. **The
    two are not the same thing and are not conflated**: «United Arab Emirates» is the label of
    THREE different ids whose full names differ, so a row can be placed in the bucket without
    pretending to know which of the three it came from.
    """
    who = (who or "").strip()
    if not who:
        return None, None, None
    exact = {n for n, _i, _c, _t in facets}
    cut = [n for n, _i, _c, t in facets if t]
    parts = who.split(" - ")
    for k in range(0 if who in exact else 1, len(parts)):
        tail = " - ".join(parts[k:])
        if tail in exact:
            return (" - ".join(parts[:k]).strip() or None), tail, tail
        for n in sorted(cut, key=len, reverse=True):
            if tail.startswith(n):
                return (" - ".join(parts[:k]).strip() or None), tail, n
    return who, None, None


def rows_of(markup, facets):
    """The page's advert panels → `[dict]`, plus how many rows named a place the site does not."""
    out, unnamed = [], 0
    for block in PANEL_RE.split(markup or "")[1:]:
        t = TITLE_RE.search(block)
        if not t:
            continue
        who = WHO_RE.search(block)
        employer, place, label = split_who(text(who.group(1)) if who else None, facets)
        if who and place is None:
            unnamed += 1
        w = WHEN_RE.search(block)
        excerpts = [text(x) for x in EXCERPT_RE.findall(block)]
        excerpts = [x for x in excerpts if x and not POSTED_RE.search(x)]
        out.append({"id": t.group(1), "title": text(t.group(2)), "employer": employer,
                    "place": place, "label": label, "posted": when(text(w.group(1)) if w else None),
                    "excerpt": excerpts[-1] if excerpts else None,
                    "featured": bool(FEATURED_RE.search(block))})
    return out, unnamed


def stated(markup):
    """(first, last, total) as the page states them, or None."""
    m = STATED_RE.search(re.sub(r"<[^>]+>", " ", markup or ""))
    if not m:
        return None
    return tuple(int(x.replace(",", "")) for x in m.groups())


def record(r, stamp):
    return {
        "source": "hirelebanese", "country": stamp,
        "ledger_id": f"hirelebanese:{r['id']}", "id": r["id"],
        "url": f"https://{HOST}/jobdetails.aspx?id={r['id']}",
        "title": scrub(r["title"]), "employer": scrub(r["employer"]),
        "place": r["place"], "published": r["posted"],
        "excerpt": scrub(r["excerpt"]),
        "detail_read": False, "contacts_withheld": True,
    }


def with_badge(rec, r):
    if r.get("featured"):
        rec["featured"] = True
    return rec


def page_url(country_id, page):
    q = [("order", "date"), ("keywords", ""), ("category", ""), ("type", ""), ("duration", ""),
         ("country", country_id or ""), ("state", ""), ("city", ""), ("emp", "")]
    if page > 1:
        q.append(("pg", str(page)))
    return f"https://{HOST}{RESULTS}?" + urllib.parse.urlencode(q)


def read_facets():
    code, body = request(f"https://{HOST}{BROWSE}")
    if code != 200:
        note(f"the browse page answered HTTP {code} — the site's own location counts were not read; "
             f"places are left null and nothing is checked against them.")
        return []
    return facets_of(body)


def cmd_locations(a):
    facets = read_facets()
    for name, ident, count, is_cut in facets:
        print(json.dumps({"id": ident, "name": name, "count": count, "label_truncated": is_cut}, ensure_ascii=False))
    note(f"{th(len(facets))} location facet(s) read from the site's own browse page; "
         f"they sum to {th(sum(c for _n, _i, c, _t in facets))}; "
         f"{th(sum(1 for _n, _i, _c, t in facets if t))} of them are cut at {LABEL_CAP} characters.")


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    if a.since and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.since):
        die(f"--since {a.since}: wants YYYY-MM-DD")
    if a.country_id and not re.fullmatch(r"\d+", str(a.country_id)):
        die(f"--country-id {a.country_id}: the site's own numeric id (see `locations`)")
    facets = read_facets()
    if a.country_id and facets and a.country_id not in [i for _n, i, _c, _t in facets]:
        die(f"--country-id {a.country_id}: the site does not name that facet. It names: "
            + ", ".join(f"{i} ({n})" for n, i, _c, _t in facets), EXIT_BROKEN)

    rows, seen, page, total, windows, unnamed, short_runs = [], set(), 0, None, [], 0, 0
    while True:
        page += 1
        url = page_url(a.country_id, page)
        code, body = request(url)
        if code == 404:
            die(f"{url}: HTTP 404 — the results page is gone", EXIT_GONE)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        st = stated(body)
        found, un = rows_of(body, facets)
        unnamed += un
        if page == 1 and st is None and not found:
            die(f"{url}: 200 with neither a stated count nor an advert — the page changed; "
                f"this is not an empty board", EXIT_PARTIAL)
        if not found:
            page -= 1
            break
        if st:
            first, last, tot = st
            windows.append((page, first, last, tot))
            if total is None:
                total = tot
            elif tot != total:
                note(f"page {th(page)}: the board now states {th(tot)} where page 1 stated "
                     f"{th(total)} — it changed under the walk; both figures are printed, neither "
                     f"is averaged.")
                total = tot
            want = PAGE_SIZE * (page - 1) + 1
            if first != want:
                die(f"page {th(page)} states its window starts at {th(first)} where the pager's "
                    f"arithmetic wants {th(want)} — the walk is not where it thinks it is", EXIT_PARTIAL)
            if last - first + 1 != len(found):
                note(f"page {th(page)}: the window says {th(last - first + 1)} advert(s), "
                     f"{th(len(found))} were read.")
        fresh = [r for r in found if r["id"] not in seen]
        if page > 1 and not fresh:
            die(f"page {th(page)} repeats the previous page's advertisements — the walk ended at "
                f"{th(len(rows))}", EXIT_PARTIAL)
        for r in fresh:
            seen.add(r["id"])
            rows.append(r)
        if a.max_pages and page >= a.max_pages:
            break
        if total is not None and len(seen) >= total:
            break

    kept = []
    for r in rows:
        if a.since and (r["posted"] or "") < a.since:
            continue
        short_runs += shortish(r["title"]) + shortish(r["employer"]) + shortish(r["excerpt"])
        kept.append(with_badge(record(r, stamp), r))
    for rec in kept:
        print(json.dumps(rec, ensure_ascii=False))

    featured = sum(1 for r in rows if r.get("featured"))
    filtered = len(rows) - len(kept)
    note(f"{th(len(kept))} emitted over {th(page)} page(s) of {PAGE_SIZE}"
         + (f", {th(filtered)} left out by --since" if filtered else "")
         + (f"; the board states {th(total)}" if total is not None else "; the board stated no total")
         + (f" — {'they agree' if total == len(rows) else f'{th(abs(total - len(rows)))} short'}"
            if total is not None and not (a.country_id or a.max_pages) else "")
         + ".")
    # **The witness a total cannot be**: the site's own count per place, checked place by place.
    if facets and not (a.country_id or a.since or a.max_pages):
        mine = {}
        for r in rows:
            if r["label"]:
                mine[r["label"]] = mine.get(r["label"], 0) + 1
        # **Three facets share the label «United Arab Emirates»** — twenty characters is where the
        # page cuts, and three different ids collapse onto it. Our rows carry the label, not the
        # id, so the site's counts are summed per label: pretending to tell them apart would be
        # inventing a distinction the page does not expose.
        site = {}
        for n, _i, c, _t in facets:
            site[n] = site.get(n, 0) + c
        ok = [n for n, c in site.items() if mine.get(n, 0) == c]
        off = [f"{n}: site {c}, read {mine.get(n, 0)}" for n, c in site.items() if mine.get(n, 0) != c]
        merged = len(facets) - len(site)
        note(f"{th(len(ok))} of {th(len(site))} location counts the site states are the counts the "
             f"rows give" + (f" — APART: {'; '.join(off[:6])}" + ("…" if len(off) > 6 else "") if off else "")
             + f". Those facets sum to {th(sum(c for _n, _i, c, _t in facets))}"
             + (f", the stated total being {th(total)}" if total is not None else "")
             + " — they PARTITION the board, «Lebanon» and «Lebanon - Beirut» being siblings and not "
               "parent and child, which is why the counts may be compared one by one."
             + (f" {th(merged)} facet(s) share a label with another and were summed into it: the page "
                f"cuts its labels at {LABEL_CAP} characters, so several ids collapse onto one name and "
                f"a row can be bucketed without knowing which id it came from." if merged else ""))
    elif facets:
        note(f"the site's per-location counts were not checked: a filter moves our side of the "
             f"comparison and not the site's ({th(len(facets))} facets read and left alone).")
    note(f"{th(featured)} of {th(len(rows))} advert(s) are FEATURED — the board sells the placement "
         f"and marks it on the panel; the record carries the flag only when it is set. *The star "
         f"image is what hid them from the first parser.*")
    if unnamed:
        note(f"{th(unnamed)} row(s) end in a place the site's own facets do not name — the whole "
             f"string is kept as the employer and the place is null, never guessed.")
    if short_runs:
        note(f"{th(short_runs)} digit run(s) of 7–8 digits left as written — the threshold is "
             f"{DIGITS_FOR_A_PHONE}.")
    note("the advertisement pages were NOT read: the panel carries the board's own excerpt, and "
         "`detail_read: false` says so on every record. Contacts scrubbed; no account is ever created.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the board carries postings from outside Lebanon "
             f"and the place a record holds is the one its row prints.")
    if not kept:
        note("0 emitted — check the filters before reading this as an empty board.")


def main(argv=None):
    p = argparse.ArgumentParser(description="HireLebanese — the browse route walked by GET, the board's own window checked at every page and its per-location counts place by place. Issue #657.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the board (1 request a page of 50, plus one for the facets)")
    j.add_argument("--country-id", dest="country_id", help="walk one of the site's own location facets (see `locations`)")
    j.add_argument("--since", help="keep what was posted on or after YYYY-MM-DD")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0, help="stop after N pages (0 = the board)")
    j.set_defaults(fn=cmd_jobs)
    l = sub.add_parser("locations", help="the site's own location facets (1 request)")
    l.set_defaults(fn=cmd_locations)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
