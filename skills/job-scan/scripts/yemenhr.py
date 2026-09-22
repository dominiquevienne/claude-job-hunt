#!/usr/bin/env python3
"""Yemen HR (`yemenhr.com`), «Yemen's Premier Jobs & Tenders Platform»: two server-rendered tables of the same system — the jobs and the tenders — walked by `?page=N`, **with the site's own per-location counts checked against ours line by line**. Issue #646.

  yemenhr.py jobs    [--location-id N] [--since YYYY-MM-DD] [--details] [--country-code YE]   50 on 2026-09-22, 1 page
  yemenhr.py tenders [--location-id N] [--since YYYY-MM-DD] [--details] [--country-code YE]   23 on 2026-09-22, 1 page

WHAT IT IS. Yemen's generalist for the NGO and private sectors, run by Yemen HR Consulting: the
organisations that recruit in the country file both their vacancies and their **tenders** there, and
the board is the same table twice. Yemen's other named boards are #647 (Yemen Young Platform) and
`yemenjobs-org.md`. **Until this adapter Yemen had no route at all.**

THE RULES. `yemenhr.com/robots.txt` is read: open on `/`, on `/jobs/`, on `/tenders` and on the
pager, `certain: True` — **and it writes `Crawl-delay: 3`**. *That delay was absent from the card's
2026-09-17 reading and is recovered here: an instruction of the host missing from a card is a breach
waiting to happen.* It is applied, and it is what makes reading fifty adverts a choice rather than a
default.

THE LIST. `GET /jobs/` (200; 748 022 B) renders the table server-side: **Posted · Organization ·
Title · Location · Deadline · Tools**, one `<tr>` a row, the advert's own address in the title's
`<a>`. `/tenders` (200; 372 064 B) renders **the same header and rows of five cells** — no «Tools»,
because the account actions («Login to mark», «Login to save») exist only for jobs.

**THE CELLS ARE READ BY HEADER LABEL, AND THE DATES ARE CHECKED AS DATES.** Today the column the
tenders table lacks is the LAST one, so a positional read would land correctly **by luck**; the day
a column is inserted in the middle it would silently put an organisation where a date belongs. So
the two date columns must HAVE the shape of a date — `22 Sep, 26` — and **a row whose Posted or
Deadline does not is refused and counted**, never emitted askew.

THE COUNT, AND A BETTER WITNESS THAN THE COUNT. The page states `Total: 50` (three times, and the
run checks the three agree). But **a total cannot see a partial loss**: an extraction that drops
five rows and doubles five others still states fifty. The footer states the board's own counts **per
location** — «Jobs in Multiple Cities (11)», «Sana'a (10)», «Aden (10)», «Hodiedah (5)», «Lahij
(4)» — and the location is in every row, so the run compares them **place by place** and says how
many agree on how many. *That is the «N emitted, board states M» discriminant carried one step
further: it catches what no total can.*

**And it earned itself on the first run.** It said «Jobs in Lahij (4)» where the rows gave **2**:
the location cell can name more than one place («Lahij , Al-Kokhah», «Lahij , Abyan») and the site
counts such a row under **each**. Fifty were emitted against a stated fifty the whole time — *the
total was right and a field was modelled wrong, and only the per-place count could see it.*

**Then it disagreed the other way, and the site settled it.** On the tenders the footer says «Aden
(3)» where the rows give 4. Asking the site's own filter — `/tenders?location_id=6` — returns
**4 rows and states «Total: 4»**, the fourth being «Aden , Taiz». So the split is right and the
footer's figure is the odd one out. **A disagreement between two counts a site states about itself
is a question, not a verdict against our reading**, and the run says so and names the third reading
that settles it.

The footer names only its largest locations, so the check is partial and says so, and it is only run
on an unfiltered walk — a filter moves our side of the comparison and not the site's.

THE WALK. `?page=N` is a plain GET and it answers: page 2 on 2026-09-22 returns the table with its
header and **one cell saying «No jobs available.»** — the board's own words, and the walk's end. *A
one-cell row is the board SPEAKING, not a row we failed to read*, so it is told apart from a shifted
table and printed rather than counted as a refusal. The page holds fifty, which is why the card read
«1 of 2 pages» for 51 on 2026-09-17 and one page for 50 today. A page repeating the previous page's
addresses ends it too (exit 6).

THE ADVERT IS READ ONLY IF ASKED. `--details` fetches each advert and reads its three labelled
sections — «Job Description», «How to Apply», «Important Notes» — by their headings, not by their
order. **It is not the default**: fifty adverts at the three seconds the host asked for is a choice,
not something to take on its behalf. `detail_read` says which was done.

**And «Important Notes» is not carried.** It is word for word the same on every advert read — the
site's standing advice to applicants («Following the instructions on How to apply will always
increase your chances…»), not a property of the post. A value true of every advert separates
nothing, so it is **counted and dropped**; an advert whose notes are its own keeps them, because
the day one differs, that difference is the information.

**WITHHELD:** e-mail addresses and telephone numbers in anything emitted («[e-mail withheld]» /
«[telephone withheld]»), `contacts_withheld` on every record. A run of **nine digits or more** is a
number (Yemeni mobiles are `7xxxxxxxx`, nine, and `+967` forms longer); a date is spared, and the
run says how many shorter runs it left. The account actions are never touched and no account is ever
created.

`--location-id` filters through the site's own `?location_id=N`, the ids being read from the footer
the site itself writes. `--since` keeps what was posted on or after a date. `--country-code` STAMPS
(the board is Yemen's; the record does not invent a field the table does not carry).

**AND «Search Total» IS NOT THE PAGE'S STRING.** The card and the issue both record «Search Total:
51» from 2026-09-17; the markup says `<span class="font-bold">Total:</span> 50`, and «Search» is the
label of the search box just above it, glued on by flattening the page to text. *The figure was
right and the name of the thing was not* — the adapter reads `Total:`.

Measured 2026-09-22 13:29–13:4x UTC by the declared client, the guard on the exact path, two reads
of the list: `/jobs/` 200 ×2, **748 022 B both**, md5 a3056277bc00 / 255909805933 — and the two
bodies differ **only** in the CSRF token, the Livewire snapshot and the script's `data-csrf`, three
lines of diff, **so the fingerprint is mute by a named cause and the fifty rows are identical**;
`?page=2` 200 (81 789 B) with no row; `/tenders` 200 (372 064 B), 23 rows, `Total: 23`; one advert
200 (104 726 B). **50 jobs emitted against the stated 50, and — once a multi-place cell counts for
each of its places — the five location counts the footer states are the five the rows give.** The
tenders: 23 emitted against the stated 23, four of the five footer counts matching, the fifth
settled by the site's own filter in our favour. Exercised: `jobs --country-code YE` → 50 · `tenders
--country-code YE` → 23 · `jobs --location-id 11 --details` → 4, three sections read on each, the
notes identical on 4 of 4 and dropped.
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

HOST = "yemenhr.com"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

KINDS = {"jobs": ("job", "/jobs/", "Jobs"), "tenders": ("tender", "/tenders", "Tenders")}
ROW_RE = re.compile(r"(?s)<tr[^>]*>(.*?)</tr>")
CELL_RE = re.compile(r"(?s)<t[dh][^>]*>(.*?)</t[dh]>")
LINK_RE = re.compile(r'(?s)<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>')
TOTAL_RE = re.compile(r'<span class="font-(?:bold|medium)">Total:</span>\s*(?:<br[^>]*>)?\s*([\d,]+)')
FOOT_RE = re.compile(r'(?s)<a[^>]*href="[^"]*/(jobs|tenders)\?location_id=(\d+)"[^>]*>(.*?)</a>')
FOOT_TEXT_RE = re.compile(r"^(?:Jobs|Tenders) in (.+?)\s*\((\d[\d,]*)\)$")
DATE_CELL_RE = re.compile(r"^(\d{1,2})\s+([A-Za-z]{3})[a-z]*,?\s*(\d{2}|\d{4})$")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
RUN_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{5,}\d(?!\w)")
DATE_TEXT_RE = re.compile(r"\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}|\d{4}-\d{2}-\d{2}")
DIGITS_FOR_A_PHONE = 9
SECTIONS = (("description", "Job Description"), ("how_to_apply", "How to Apply"),
            ("important_notes", "Important Notes"))
MONTHS = {m.lower(): i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[yemenhr] {msg}", file=sys.stderr)


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
    if re.search(r"/(?:login|register|sign-?in|join)\b", parts.path, re.I):
        die(f"{url}: an account path is never requested", EXIT_REFUSED)
    a = gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=a.get("crawl_delay") or 3.0)).wait()   # the host writes Crawl-delay: 3
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml",
                                                         "Accept-Language": "en, ar"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>|</h[1-6]>", "\n", markup or "")
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


def when(cell):
    """«22 Sep, 26» → `2026-09-22`. Returns None when the cell is not a date at all."""
    m = DATE_CELL_RE.match((cell or "").strip())
    if not m or m.group(2).lower() not in MONTHS:
        return None
    y = int(m.group(3))
    return f"{2000 + y if y < 100 else y:04d}-{MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"


def stated_total(markup):
    """The page's own `Total:`, and only when its occurrences agree."""
    seen = {int(x.replace(",", "")) for x in TOTAL_RE.findall(markup or "")}
    if len(seen) == 1:
        return seen.pop(), True
    return (sorted(seen)[0] if seen else None), False


def footer_counts(markup, kind_word):
    """The site's own per-location counts, `{name: (location_id, count)}`."""
    out = {}
    for word, ident, inner in FOOT_RE.findall(markup or ""):
        if word != kind_word.lower():
            continue
        m = FOOT_TEXT_RE.match(text(inner) or "")
        if m:
            out[m.group(1).strip()] = (ident, int(m.group(2).replace(",", "")))
    return out


def rows_of(markup):
    """(rows, header, refused, messages) — cells by header LABEL, the two date columns checked as
    dates, and **the board's own one-cell message row told apart from a shifted table**: «No jobs
    available.» is the end of the walk, not a row we failed to read."""
    blocks = ROW_RE.findall(markup or "")
    if not blocks:
        return [], [], 0, []
    header = [text(c) or "" for c in CELL_RE.findall(blocks[0])]
    if "Posted" not in header or "Title" not in header:
        return [], header, 0, []
    out, refused, messages = [], 0, []
    for block in blocks[1:]:
        cells = CELL_RE.findall(block)
        if not cells:
            continue
        if len(cells) < 3:                          # one cell spanning the table: the board is SPEAKING
            messages.append(text(cells[0]))
            continue
        row = {}
        for label, cell in zip(header, cells):      # by LABEL; a short row keeps the labels it has
            row[label] = cell
        title_cell = row.get("Title", "")
        link = LINK_RE.search(title_cell)
        posted, deadline = when(text(row.get("Posted"))), when(text(row.get("Deadline")))
        if not link or posted is None or deadline is None:
            refused += 1                            # the columns shifted: a date column that is not a date
            continue
        places = places_of(text(row.get("Location")))
        out.append({"url": htmlmod.unescape(link.group(1)), "title": text(link.group(2)),
                    "organization": text(row.get("Organization")),
                    "location": ", ".join(places) if places else None, "locations": places,
                    "posted": posted, "deadline": deadline,
                    "is_new": "new" in (text(title_cell) or "").split()})
    return out, header, refused, messages


def sections_of(markup):
    """The advert's three labelled sections, read by their heading and not by their order."""
    out = {}
    heads = [(m.start(), text(m.group(1)) or "", m.end()) for m in re.finditer(r"(?s)<h[23][^>]*>(.*?)</h[23]>", markup or "")]
    for i, (_start, label, end) in enumerate(heads):
        for key, want in SECTIONS:
            if label.split("/")[0].strip().lower() == want.lower():
                stop = heads[i + 1][0] if i + 1 < len(heads) else len(markup)
                out[key] = scrub(text(markup[end:stop]))
    return out


def places_of(cell):
    """«Lahij , Al-Kokhah» is TWO places, and the site's own filter counts it under each.

    Found by the footer's own figures on the first run: it stated «Jobs in Lahij (4)» where the
    rows gave 2, and the two missing ones were «Lahij , Al-Kokhah» and «Lahij , Abyan». *A total
    would never have shown it — 50 emitted against 50 stated, and a field modelled wrong.*

    **And the same witness then disagreed the other way, which is how it was settled.** On the
    tenders the footer states «Aden (3)» where the split gives 4; asking the site's own filter,
    `/tenders?location_id=6`, returns **4 and states «Total: 4»** — the fourth being «Aden ,
    Taiz». *So the split is right and the footer's figure is the odd one out: a disagreement
    between two counts the site states about itself is a question, not our defect.*
    """
    return [p for p in (x.strip() for x in re.split(r"[,\u060c]|\n", cell or "")) if p.strip()] or None


def key_of(url):
    return urllib.parse.urlsplit(url).path.rstrip("/").rsplit("/", 1)[-1] or None


def record(kind, r, stamp, detail):
    rec = {
        "source": "yemenhr", "kind": kind, "country": stamp,
        "ledger_id": f"yemenhr:{kind}:{key_of(r['url'])}", "id": key_of(r["url"]),
        "url": r["url"], "title": scrub(r["title"]),
        "organization": scrub(r["organization"]),
        "location": r["location"], "locations": r["locations"],
        "published": r["posted"], "deadline": r["deadline"],
        "newly_posted": r["is_new"],
        "detail_read": bool(detail),
        "contacts_withheld": True,
    }
    for key, _label in SECTIONS:
        if detail and detail.get(key):
            rec[key] = detail[key]
    return rec


def walk(path, kind_word, location_id, max_pages):
    """The table, page after page, until a page carries no row. Returns (rows, pages, first_page)."""
    rows, seen, page, first = [], set(), 0, None
    while True:
        page += 1
        q = {}
        if location_id:
            q["location_id"] = location_id
        if page > 1:
            q["page"] = str(page)
        url = f"https://{HOST}{path}" + (("?" + urllib.parse.urlencode(q)) if q else "")
        code, body = request(url)
        if code == 404:
            die(f"{url}: HTTP 404 — the list is gone", EXIT_GONE)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if first is None:
            first = body
        found, header, refused, messages = rows_of(body)
        if page == 1 and not header:
            die(f"{url}: 200 with no table at all — the page changed; this is not an empty board", EXIT_PARTIAL)
        if refused:
            note(f"page {page}: {th(refused)} row(s) refused — Posted or Deadline was not a date, "
                 f"so the columns are not where the header says. Emitting them would have been worse.")
        if not found:
            if messages:
                note(f"page {page} carries no row, and the board says so itself: "
                     f"«{messages[0]}» — the walk's end.")
            return rows, page - 1, first
        keys = {r["url"] for r in found}
        if page > 1 and keys <= seen:
            die(f"page {page} repeats the previous page's advertisements — the walk ended at {th(len(rows))}", EXIT_PARTIAL)
        for r in found:
            if r["url"] in seen:
                continue
            seen.add(r["url"])
            rows.append(r)
        if max_pages and page >= max_pages:
            return rows, page, first


def drop_the_boilerplate(records, field="important_notes"):
    """**«Important Notes» is the site's standing advice to applicants, repeated word for word.**

    A value true of every advert separates nothing: it reads like information and carries none. So
    the repeated text is COUNTED and not carried, and an advert whose notes are its OWN keeps
    them — the day one differs, that difference is the information.

    Returns `(how many repeated it, how many kept their own, the first line of the repeated text)`.
    """
    seen = {}
    for r in records:
        v = r.get(field)
        if v:
            seen[v] = seen.get(v, 0) + 1
    if not seen:
        return None
    common, n = max(seen.items(), key=lambda kv: (kv[1], len(kv[0])))
    if n < 2:
        return None
    own = sum(seen.values()) - n
    for r in records:
        if r.get(field) == common:
            del r[field]
    return n, own, common.splitlines()[0]


def run(a, which):
    kind, path, kind_word = KINDS[which]
    stamp = a.country_code.upper() if a.country_code else None
    if a.since and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.since):
        die(f"--since {a.since}: wants YYYY-MM-DD")
    if a.location_id and not re.fullmatch(r"\d+", str(a.location_id)):
        die(f"--location-id {a.location_id}: the site's own numeric id (see the footer of any list page)")
    rows, pages, first = walk(path, kind_word, a.location_id, a.max_pages)
    total, agreed = stated_total(first)
    foot = footer_counts(first, kind_word)

    kept, short_runs = [], 0
    for r in rows:
        if a.since and r["posted"] < a.since:
            continue
        detail = None
        if a.details:
            code, body = request(r["url"])
            if code != 200:
                note(f"{r['url']}: HTTP {code} — the advertisement was not read; the row is emitted without it.")
            else:
                detail = sections_of(body)
                short_runs += sum(shortish(v) for v in detail.values() if v)
        kept.append(record(kind, r, stamp, detail))

    boiler = drop_the_boilerplate(kept) if a.details else None

    for rec in kept:
        print(json.dumps(rec, ensure_ascii=False))

    filtered = len(rows) - len(kept)
    note(f"{th(len(kept))} {kind}(s) emitted over {th(pages)} page(s)"
         + (f", {th(filtered)} left out by --since" if filtered else "")
         + (f"; the page states «Total: {th(total)}»" if total is not None else "; the page states no total")
         + (f" — {'they agree' if total == len(rows) else f'{th(abs(total - len(rows)))} apart, and the difference is not explained'}" if total is not None else "")
         + ".")
    if total is not None and not agreed:
        note("the page prints its own «Total:» more than once and the copies DISAGREE — "
             "the figure above is the lowest of them, and it should not be trusted.")
    # **The witness that a total cannot be**: the site's own count per location, row by row.
    if foot and not (a.location_id or a.since or a.max_pages):
        mine = {}
        for r in rows:
            for place in (r["locations"] or []):
                mine[place] = mine.get(place, 0) + 1
        ok = [n for n, (_i, c) in foot.items() if mine.get(n, 0) == c]
        off = [f"{n}: site {c}, read {mine.get(n, 0)}" for n, (_i, c) in foot.items() if mine.get(n, 0) != c]
        note(f"{th(len(ok))} of {th(len(foot))} location counts the site states are the counts the rows give"
             + (f" — APART: {'; '.join(off)}" if off else "")
             + ". The footer names only its largest locations, so this is a partial witness — "
               "but a total cannot see five rows lost against five doubled, and this can."
             + (" A disagreement is a QUESTION, not a verdict against the rows: ask the site's own "
                "filter with --location-id, which is a third reading. On 2026-09-22 the tenders "
                "footer said «Aden 3», the rows gave 4, and `?location_id=6` returned 4 and stated "
                "«Total: 4»." if off else ""))
    elif foot:
        note(f"the site's per-location counts were not checked: a filter moves our side of the "
             f"comparison and not the site's ({th(len(foot))} counts read and left alone).")
    if boiler:
        n, own, first_line = boiler
        note(f"«Important Notes» is word for word the same on {th(n)} of the {th(len(kept))} "
             f"advertisement(s) read — the site's standing advice to applicants («{first_line[:60]}…»), "
             f"counted and NOT carried" + (f"; {th(own)} carry their own and keep it" if own else "")
             + ". A value true of every advert separates nothing.")
    if a.details:
        note(f"advertisements read one by one at the host's own Crawl-delay; contacts scrubbed"
             + (f"; {th(short_runs)} digit run(s) of 7–8 digits left as written, the threshold being "
                f"{DIGITS_FOR_A_PHONE}" if short_runs else "") + ".")
    else:
        note("the advertisement pages were NOT read (`--details` reads them, one request each at the "
             "host's Crawl-delay of 3 s): `detail_read: false` on every record.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the table states no country.")
    if not kept:
        note(f"0 emitted — the list carried no {kind} the filters kept; that is a state, not a failure.")


def cmd_jobs(a):
    run(a, "jobs")


def cmd_tenders(a):
    run(a, "tenders")


def main(argv=None):
    p = argparse.ArgumentParser(description="Yemen HR — the jobs and the tenders, two tables of one system read by header label, with the site's own per-location counts checked against ours. Issue #646.")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, helptext in (("jobs", cmd_jobs, "the vacancies (1 request a page)"),
                               ("tenders", cmd_tenders, "the tenders (1 request a page)")):
        s = sub.add_parser(name, help=helptext)
        s.add_argument("--location-id", dest="location_id", help="the site's own numeric location id (the footer writes them)")
        s.add_argument("--since", help="keep what was posted on or after YYYY-MM-DD")
        s.add_argument("--details", action="store_true", help="read each advertisement (1 request each, at the host's Crawl-delay)")
        s.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record")
        s.add_argument("--max-pages", dest="max_pages", type=int, default=0, help="stop after N pages (0 = until a page carries no row)")
        s.set_defaults(fn=fn)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
