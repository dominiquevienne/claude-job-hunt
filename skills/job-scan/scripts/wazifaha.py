#!/usr/bin/env python3
"""Wazifaha (`www.wazifaha.org`), Afghanistan: a generalist that states its own total — «Showing 272 active jobs» — and whose pager bounds the walk, **because asking past the last page returns the last page again rather than an empty one**. Issue #642.

  wazifaha.py jobs [--location SLUG] [--since-days N] [--details] [--country-code AF] [--max-pages N]
  wazifaha.py locations        the site's own province pages (1 request)

WHAT IT IS. Afghanistan's second route and its **first generalist**: `acbar.py` reads the NGO
coordination body's board (268 posts), which is the humanitarian market. This one carries private
employers beside the NGOs — a different market, not a second helping of the same one.

THE RULES. `www.wazifaha.org` opens on `/`, `/jobs/` and the pager, `certain: True`, **no
Crawl-delay**; 2 s is ours. The guard is taken on the exact path.

**THE SITE CLAMPS PAST ITS LAST PAGE, SO «WALK UNTIL EMPTY» NEVER TERMINATES HERE.** Page 16 is the
last the pager names; `?page=17` answers 200 with **the same two adverts, the same ids** (a different
md5 — see below — but the same board). *A walk that stops on an empty page would ask for ever, and a
walk that stops on «a round without novelty» is right here for the wrong reason: it would also stop
on a cache or a filter lost in flight.* So the walk is bounded by the pager's largest number, read
on page 1, **and** a page repeating the one before it ends it — the two are not the same statement
and the run says which fired.

**THREE FIGURES, AND THE THIRD IS THE ONE THAT VERIFIES.** The list states **272**; the pager names
**16**; eighteen cards a page puts the last page at **272 − 15 × 18 = 2**. *It carried 2* — tested
before a line of this adapter was written, as on MyJobs the same day.

**THE CARDS ARE COUNTED BY CONTAINER, NEVER BY LINK.** Page 1 carries **eighteen** cards and
**forty-eight distinct advert addresses**: the sidebar links adverts too. *Counting hrefs would have
given a page of 48 against a stated 272 and a pager of 16, and the three figures would have
disagreed for a reason that has nothing to do with the board.* Each card also prints its title and
its employer **twice** — a mobile copy and a desktop one — which is read once.

**THE SALARY IS A LABELLED FIELD AND THE TELEPHONE RULE NEVER TOUCHES IT.** *Not because the afghani
is small* — on the advert read it says «Competitive», and whether any advert prints a figure is not
established — **but because the lesson of `myjobsmm.py` the same day is that a rule for free text
does not belong on a field whose meaning is known.** There the nine-digit threshold destroyed 113 of
115 salaries, and the fix that generalises is this one, applied here before it could cost anything.

**GENDER IS NEVER CARRIED, AND THE LIST DECLARES IT TOO — BECAUSE HALF THE CARDS PRINT IT.** The
advert prints «Male/Female» as a hiring criterion, and so does the card: **nine of the eighteen on
page 1**. The repository serves the advert and does not propagate the criterion (#183), and
`criteria_withheld: ["gender"]` appears **only where the object read carried one**, `[]` where it
did not (#885). *The first draft of this adapter asserted that the card printed none — it does, on
half of them, and the claim was made from the two cards I had looked at.*

**WITHHELD:** e-mail addresses everywhere, telephone numbers in free text at nine digits,
`contacts_withheld` on every record. `--details` reads each advert (one request each); it is not the
default — 272 adverts is nine minutes at our own pace, and that is a choice.

Measured 2026-09-23 17:0x–17:2x UTC by the declared client, the guard on the exact path, two reads of
the list: `/jobs/` 200 ×2, **168 540 B both**, 18 cards, «Showing 272 active jobs», pager to 16;
`?page=16` 200 (112 438 B) **2 cards**; `?page=17` 200 — the same two ids; one advert 200 (95 175 B).
*The two reads of a page give different md5 at identical length, as on MyJobs; the cause is not
established here and the figures that held twice are the ones carried.*
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

HOST = "www.wazifaha.org"
PAGE_SIZE = 18
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

CARD_RE = re.compile(r'<div class="wz-job-body">')
LINK_RE = re.compile(r'href="/jobs/(\d+)/([a-z0-9\-]+)"')
COMPANY_RE = re.compile(r'href="(/companies/[a-z0-9\-]+)"')
STATED_RE = re.compile(r"Showing\s+([\d,]+)\s+active jobs", re.I)
PAGER_RE = re.compile(r"[?&]page=(\d+)")
LOC_RE = re.compile(r'href="(/jobs-by-location/([a-z0-9\-]+))"')
AGE_RE = re.compile(r"^(?:about\s+)?(\d+|an?)\s+(minute|hour|day|week|month)s?\s+ago$", re.I)
VAC_RE = re.compile(r"^(\d[\d,]*)\s+Vacanc(?:y|ies)$", re.I)
FIELD_RE = re.compile(r'<div class="wz-grid-label">(.*?)</div>\s*<div class="wz-grid-value">(.*?)</div>', re.S)
META_RE = re.compile(r'<span class="wz-job-meta-item">(.*?)</span>', re.S)
COMPANY_TEXT_RE = re.compile(r'<a href="/companies/[a-z0-9\-]+"[^>]*>(.*?)</a>', re.S)
TITLE_RE = re.compile(r'<a href="/jobs/\d+/[a-z0-9\-]+" class="wz-job-name[^"]*"[^>]*>(.*?)</a>', re.S)
GENDER_RE = re.compile(r'>\s*(?:Male/Female|Male|Female)\s*<')
GENDER_WORDS = ("Male", "Female", "Male/Female", "Any")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
RUN_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{5,}\d(?!\w)")
DATE_TEXT_RE = re.compile(r"\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}|\d{4}-\d{2}-\d{2}")
DIGITS_FOR_A_PHONE = 9
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[wazifaha] {msg}", file=sys.stderr)


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
    if re.search(r"/(?:accounts|login|register|top-?up)\b", parts.path, re.I):
        die(f"{url}: an account path is never requested", EXIT_REFUSED)
    a = gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=a.get("crawl_delay") or 2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml",
                                                         "Accept-Language": "en, fa, ps"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def pieces(markup):
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", markup or "")   # one (?s), at the start
    t = re.sub(r"(?s)<i [^>]*></i>", "", t)
    return [htmlmod.unescape(x).strip() for x in re.sub(r"<[^>]+>", "\x01", t).split("\x01") if x.strip()]


def scrub(s):
    """Free text: an address goes, and so does a run of nine digits or more."""
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


def labelled(s):
    """A field whose MEANING IS KNOWN — a salary, a contract, a closing date.

    **The telephone rule does not apply here**, and not because this board's currency is small:
    on `myjobsmm.py` the same day a nine-digit threshold destroyed 113 of 115 salaries because a
    Myanmar range is twelve digits. *The lesson that generalises is not «check the currency» but
    «a rule written for free text does not belong on a labelled field».* The address scrub stays;
    it costs nothing.
    """
    return MAIL_RE.sub("[e-mail withheld]", s).strip() or None if s else None


def days_of(age):
    m = AGE_RE.match((age or "").strip())
    if not m:
        return None
    n = 1 if m.group(1).lower() in ("a", "an") else int(m.group(1))
    return {"minute": 0, "hour": 0, "day": n, "week": n * 7, "month": n * 30}[m.group(2).lower()]


def stated_of(markup):
    m = STATED_RE.search(re.sub(r"<[^>]+>", " ", markup or ""))
    return int(m.group(1).replace(",", "")) if m else None


def cards_of(markup):
    """The page's advert cards.

    **Counted by CONTAINER, never by link.** Page 1 carries eighteen cards and forty-eight
    distinct advert addresses — the sidebar links adverts too — so a count of hrefs would have
    disagreed with the board's own figures for a reason that has nothing to do with the board.

    **And every field is taken from what the site MARKS, not from where it falls.** Each card
    prints its employer twice, *with two different truncations* — «Rahmanzai Logistic, Trading,
    …» for the narrow screen and «Rahmanzai Logistic, Trading, Construction, A…» for the wide
    one. A positional read after de-duplication therefore slid the province one place along and
    put a truncated organisation where «Kabul» belonged, on 24 of 272 rows. *The location is the
    meta item bearing `fa-location-dot`; the employer is the company link's longest text.*
    """
    out = []
    for block in CARD_RE.split(markup or "")[1:]:
        link = LINK_RE.search(block)
        if not link:
            continue
        strings = pieces(block)
        age = next((s for s in strings if AGE_RE.match(s)), None)
        vac = next((s for s in strings if VAC_RE.match(s)), None)
        place = None
        for item in META_RE.findall(block):
            if "fa-location-dot" in item:
                place = " ".join(pieces(item)) or None
                break
        company = COMPANY_RE.search(block)
        names = [" ".join(pieces(x)) for x in COMPANY_TEXT_RE.findall(block)]
        employer = max(names, key=len) if names else None
        title = None
        for t in TITLE_RE.findall(block):
            title = " ".join(pieces(t)) or None
            if title:
                break
        # **The gender the card prints is a criterion, and half the cards print one.**
        gender = bool(GENDER_RE.search(block))
        out.append({"id": link.group(1), "path": f"/jobs/{link.group(1)}/{link.group(2)}",
                    "title": title, "employer": employer, "place": place,
                    "company_path": company.group(1) if company else None,
                    "gender_on_card": gender,
                    "age": age, "vacancies": int(VAC_RE.match(vac).group(1).replace(",", "")) if vac else None})
    return out


def detail_of(markup):
    """The advert's labelled grid, plus the criterion that is never carried."""
    fields, criteria = {}, []
    for label, value in FIELD_RE.findall(markup or ""):
        k = " ".join(pieces(label)) or ""
        v = " ".join(pieces(value)) or ""
        if not k:
            continue
        if v in GENDER_WORDS or k.lower() == "gender":
            criteria.append("gender")
            continue
        fields[k.lower()] = v
    return fields, criteria


def record(c, stamp, detail=None, criteria=None):
    rec = {
        "source": "wazifaha", "country": stamp,
        "ledger_id": f"wazifaha:{c['id']}", "id": c["id"],
        "url": f"https://{HOST}{c['path']}",
        "title": scrub(c["title"]), "employer": scrub(c["employer"]),
        "company_url": f"https://{HOST}{c['company_path']}" if c["company_path"] else None,
        "place": c["place"], "vacancies": c["vacancies"],
        # **The name is the site's own truncation**, and both copies it prints are cut — the full
        # one is recoverable from the company slug, which the record carries. Saying the name is
        # cut is cheaper than pretending it is whole.
        "employer_truncated": bool(c["employer"] and c["employer"].rstrip().endswith("…")),
        # **#885 applied to what this board actually prints**: half the cards DO carry the
        # criterion, so the list row declares it when the card carried one and `[]` when not.
        # *The first draft of this adapter said «the card prints none» — nine of eighteen do.*
        "criteria_withheld": ["gender"] if c.get("gender_on_card") else [],
        "posted_as_written": c["age"], "posted_days_ago": days_of(c["age"]),
        "detail_read": bool(detail is not None),
        "contacts_withheld": True,
    }
    if detail is not None:
        for key, label in (("employment_type", "contract type"), ("salary", "salary"),
                           ("closes", "closing date"), ("vacancy_number", "vacancy number")):
            if label in detail:
                rec[key] = labelled(detail[label])
        # **#885: declared only when the page READ carried one** — `[]` is «read, and none».
        rec["criteria_withheld"] = sorted(set((criteria or []) + rec["criteria_withheld"]))
    return rec


def read_list(url):
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the list is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    return body


def cmd_locations(a):
    body = read_list(f"https://{HOST}/jobs/")
    seen = {}
    for href, slug in LOC_RE.findall(body):
        seen.setdefault(slug, href)
    for slug, href in sorted(seen.items()):
        print(json.dumps({"slug": slug, "path": href}, ensure_ascii=False))
    note(f"{th(len(seen))} province page(s) named by the list; the site states no count per province.")


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    base = f"https://{HOST}/jobs-by-location/{a.location}" if a.location else f"https://{HOST}/jobs/"
    rows, seen, page, bound, stated, ended = [], set(), 0, None, None, "the bound"
    previous = None
    while True:
        page += 1
        body = read_list(base + (f"?page={page}" if page > 1 else ""))
        if page == 1:
            bound = max((int(x) for x in PAGER_RE.findall(body)), default=1)
            stated = stated_of(body)
        found = cards_of(body)
        if page == 1 and not found:
            die(f"{base}: 200 and no card — the template changed; this is not an empty board", EXIT_PARTIAL)
        ids = {c["id"] for c in found}
        # **The site clamps**: past the last page it re-serves the last. A repeat is therefore the
        # NORMAL way past the end, and it is told apart from the bound so the run says which fired.
        if previous is not None and ids and ids == previous:
            ended = "a repeated page"
            page -= 1
            break
        previous = ids
        for c in found:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            rows.append(c)
        if not found:
            ended = "an empty page"
            page -= 1
            break
        if a.max_pages and page >= a.max_pages:
            ended = "--max-pages"
            break
        if bound and page >= bound:
            ended = "the bound"
            break

    kept = []
    for c in rows:
        if a.since_days and (days_of(c["age"]) is None or days_of(c["age"]) > a.since_days):
            continue
        detail, criteria = None, None
        if a.details:
            code, body = request(f"https://{HOST}{c['path']}")
            if code != 200:
                note(f"{c['path']}: HTTP {code} — the advert was not read; the row is emitted without it.")
            else:
                detail, criteria = detail_of(body)
        kept.append(record(c, stamp, detail, criteria))
    for rec in kept:
        print(json.dumps(rec, ensure_ascii=False))

    dropped = len(rows) - len(kept)
    last = len(rows) - PAGE_SIZE * (page - 1) if page else 0
    note(f"{th(len(kept))} emitted over {th(page)} page(s) of {PAGE_SIZE}"
         + (f", {th(dropped)} left out by --since-days" if dropped else "")
         + (f"; the list states {th(stated)}" if stated is not None else "; the list states no total")
         + (f" — {'they agree' if stated == len(rows) else f'{th(abs(stated - len(rows)))} apart'}"
            if stated is not None and not (a.location or a.max_pages) else "")
         + f"; the walk ended on {ended}.")
    if bound and not (a.location or a.max_pages):
        note(f"the pager named {th(bound)} on page 1, so {th(bound)} × {PAGE_SIZE} = {th(bound * PAGE_SIZE)} "
             f"bounds the walk, and the last page carried {th(last)}"
             + (f" — {th(stated)} = {th(bound - 1)} × {PAGE_SIZE} + {th(last)}, so the total, the pager and "
                f"the fill agree" if stated is not None and stated == PAGE_SIZE * (page - 1) + last else "")
             + ". Asking past the last page returns the last page again, so an empty page is not how "
               "this board ends.")
    if a.details:
        withheld = sum(1 for r in kept if r.get("criteria_withheld"))
        note(f"advert pages read one by one; the gender the advert prints is NEVER carried and "
             f"{th(withheld)} of {th(len(kept))} record(s) name it as withheld — the others read an "
             f"advert that carried none (#183, #885).")
    else:
        note("the advert pages were NOT read (`--details` reads them, one request each): the list "
             "row carries no criterion because the card prints none, and `detail_read: false` says so.")
    note("the salary is a labelled field and the telephone rule never touches it; free text keeps "
         "both scrubs.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the cards state a province, not a country.")
    if not kept:
        note("0 emitted — check the filters before reading this as an empty board.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Wazifaha (Afghanistan) — the list walked to the pager's bound, checked against the board's own «Showing N active jobs»; the site clamps past its last page. Issue #642.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the board (1 request a page of 18)")
    j.add_argument("--location", help="walk one of the site's own province pages (see `locations`)")
    j.add_argument("--since-days", dest="since_days", type=int, help="keep cards the board dates within N days")
    j.add_argument("--details", action="store_true", help="read each advert (1 request each)")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0, help="stop after N pages (0 = the bound)")
    j.set_defaults(fn=cmd_jobs)
    l = sub.add_parser("locations", help="the site's own province pages (1 request)")
    l.set_defaults(fn=cmd_locations)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
