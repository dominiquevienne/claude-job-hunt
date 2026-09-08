#!/usr/bin/env python3
"""UzJobs (`uzjobs.uz`) — Uzbekistan's first adapter, and the country page said
it was unreadable.

  uzjobs.py list [--since 2026-09-01] [--limit 10]
  uzjobs.py ad --id 33951

**One request to the feed the site links returns 21 advertisements complete** —
identifier, title, employer, both ends of the posting period, region and
salary — with no page fetched at all.

THE «GIBBERISH» IS GONE, AND THE REASON MATTERS

Uzbekistan's country page recorded, on 2026-09-04: *«le site répond 200 et rend
du charabia»*, with a redirect chain declaring `iso-8859-1`, then nothing, then
`windows-1251`, and **no charset in the HTML**.

Measured 2026-09-08:

    GET /             200 · no redirect · Content-Type: text/html; charset=windows-1251
    charset_of()      'windows-1251', from the header
    decode_body()     windows-1251 → clean XHTML, <title>UzJobs …</title>

**There is no chain today: the requested URL is the final URL, and the one
declaration is right.** *Whether the site changed or the earlier reading
followed a hop that no longer happens, this card cannot say* — it reports what
one request returns now, and the country page's verdict is retired rather than
contradicted.

**Everything on this host is `windows-1251`** — the HTML, and the feed, which
declares it in its XML prologue. `_decode.decode_body` is given the headers and
picks it up; nothing here is decoded by hand.

THE FEED IS THE INVENTORY THIS MODULE READS, AND IT IS NOT THE BOARD

`/rss_vak.cgi` is linked from the home page and from the vacancy list. It
returns **21 items**, and every field this adapter emits comes from them:

    <guid>/<link>   https://uzjobs.uz/r/vakansy_view-33951.html
    <title>         Вакансия: Руководитель инфраструктурных проектов
    <pubDate>       Mon, 07 Sep 2026 10:51:52 +0500
    <description>   Компания: …<br><br>Период размещения: 07.09.2026 - 06.10.2026
                    <br><br>Регион: Ташкент<br><br>Предлагаемая зарплата: …

**21 is the feed's window, not the board's size.** The vacancy list shows ten
per page with identifiers running to 33951, and its pagination goes through a
form `POST`ing to `/vakansy.cgi` with `raz`, `lan`, `search`, `keyword`, `go`
and the selects `sfera1`, `sfera2`, `pol`, `obraz`, `zanyat`, `region`.

*That form was not exercised.* **Those names are written down here so the next
session does not rediscover them**, and so that nobody mistakes 21 for a count
of anything but the feed.

THE DATE IS THE SITE'S OWN, AND THERE ARE TWO OF THEM

`Период размещения: 07.09.2026 - 06.10.2026` — **the posting period carries
both ends**, so `posted` and `expires` come from the advertisement rather than
from a file's timestamp. `pubDate` agrees with the first on every item
measured, and is parsed with `email.utils` rather than sliced: *an RFC-822 date
compared as a string sorts «Fri 04 Sep» after «Wed 02 Sep», which is how a
first probe of this feed reported its range backwards.*

THIS BOARD PUBLISHES AGE AND GENDER REQUIREMENTS, AND THIS MODULE DOES NOT

An advertisement page carries `Возраст: 30-45 лет`, and the site's own search
form offers `pol` — gender — beside education and employment type.

**Neither is emitted, and no filter is offered on either** — issue #183,
2026-09-08. *Uzbekistan's Labour Code, new edition, law No. ZRU-798 of
2022-10-28 in force since 2023-04-01, admits no employment restriction founded
on age or sex.* **So the criterion does not travel through this module.**

**The advertisement is still served.** *Dropping the advertisements that carry
such a requirement would deny a candidate a real vacancy — the opposite of the
point.* **It is the criterion that does not propagate, not the vacancy.**

**The Code reserves factors «&nbsp;related to the exercise of the
occupation&nbsp;», so a requirement CAN be lawful in narrow cases** — and this
module cannot decide, advertisement by advertisement, whether a given one falls
inside that reserve. *Faced with that, not propagating is the safe conduct.*

**`Возраст` is still known to the parser**, moved to `OTHER_LABELS`: a label
this module does not emit must still be known, so that the value before it is
cut at the right place.

**The claim first written here was that dropping the label would append the age
to `category`. That was not measured, and it is not true of the pages read.**
*Removing `Возраст` from every label set and re-reading four advertisements
changed **zero fields** — the pages put `Возраст` where no emitted value is cut
by it.* **The label is kept as a precaution against a page order we have not
seen, and that is a weaker reason than the one first given here** — written
down because a docstring that overstates its own mechanism is how the next
reader is misled.

**This is per jurisdiction.** *The Uzbek Code says nothing about anywhere else,
and this change is not a template for other adapters.*

Verified against the live site on 2026-09-08.
"""

import argparse
import email.utils
import html as html_mod
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BASE = "https://uzjobs.uz"
FEED = BASE + "/rss_vak.cgi"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ITEM = re.compile(r"<item>(.*?)</item>", re.S)
TAG = {t: re.compile(rf"<{t}>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</{t}>", re.S)
       for t in ("title", "link", "pubDate", "description")}
AD_ID = re.compile(r"vakansy_view-(\d+)\.html")
PERIOD = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})\s*-\s*(\d{2})\.(\d{2})\.(\d{4})")

# The labels the feed's `description` uses, and the page repeats.
LABELS = {"employer": "Компания", "period": "Период размещения",
          "region": "Регион", "salary": "Предлагаемая зарплата"}
# Labels that appear only on the advertisement page.
PAGE_LABELS = {"employer": "Работодатель", "period": "Период размещения",
               "category": "категория должности"}
# **Labels this module does not emit but must know, to cut values at.** A
# first version knew only the four above, so `age` came back as
# `30-45 лет Пол: … Местожительство: … Образование: …` — every following
# field, in one string that looks full rather than wrong.
# `Возраст` moved here from PAGE_LABELS by #183: known, never emitted.
OTHER_LABELS = ("Информация о вакансии", "Обязанности", "Пол", "Возраст",
                "Местожительство", "Образование", "Опыт работы",
                "Требования к кандидату", "Занятость", "Сфера деятельности",
                "Знание языков", "Контактное лицо", "Телефон")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[uzjobs] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# The host declares no `Crawl-delay`; this spacing is ours and declared as ours.
_PACE = Pace("uzjobs.uz", own=1.5)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/rss+xml;q=0.9",
        "Accept-Language": "ru-UZ,ru;q=0.9,uz;q=0.8,en;q=0.7",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            # **Never decoded by hand.** Everything here is `windows-1251`,
            # declared in the header and in the feed's XML prologue.
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def clean(s):
    return " ".join(html_mod.unescape(re.sub(r"<[^>]+>", " ", s or "")).split())


def rfc822(value):
    """`Mon, 07 Sep 2026 10:51:52 +0500` -> `2026-09-07`, or `None`.

    **Parsed, never sliced.** An RFC-822 date compared as a string sorts
    `Fri, 04 Sep` after `Wed, 02 Sep`, and a first probe of this feed reported
    its range backwards for exactly that reason.
    """
    try:
        dt = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    return dt.date().isoformat() if dt else None


# Every label this module knows, so a value can be cut at the next one.
ALL_LABELS = tuple(set(LABELS.values()) | set(PAGE_LABELS.values())
                   | set(OTHER_LABELS))


def labelled(text, label):
    """The value the site prints after `<label>:`, **cut at the next label**.

    *A first version matched `[^<\n]{1,160}` on the cleaned text and swallowed
    every following field*: the feed separates them with `<br><br>`, and
    stripping tags removes exactly the boundary the pattern relied on. So
    `employer` came back as the company **plus** the period, the region and the
    salary — a value that is wrong and looks full rather than empty.
    """
    m = re.search(rf"{re.escape(label)}\s*:\s*(.{{1,400}})", text, re.S)
    if not m:
        return None
    value = m.group(1)
    # **Cut at the next label with OR without its colon.** `Информация о
    # вакансии` is printed as a heading with no colon, and a cut that required
    # one left it glued to the employer's name.
    cuts = []
    for other in ALL_LABELS:
        if other == label:
            continue
        for probe in (other + ":", other):
            i = value.find(probe)
            if i > 0:
                cuts.append(i)
    if cuts:
        value = value[: min(cuts)]
    return clean(value) or None


def from_feed(raw_description, label):
    """The same, but on the feed's description **before** its tags are
    stripped: the `<br>` runs are the field separators."""
    for part in re.split(r"(?:<br\s*/?>\s*)+", raw_description):
        got = labelled(clean(part), label)
        if got:
            return got
    return None


def cmd_list(a):
    code, body = get(FEED)
    if code != 200:
        die(f"{FEED}: HTTP {code}")
    items = ITEM.findall(body)
    if not items:
        die(f"{FEED} parsed to zero items from {len(body)} characters — read "
            f"the bytes before believing the zero.")
    rows = []
    for it in items:
        link = TAG["link"].search(it)
        url = clean(link.group(1)) if link else None
        ident = AD_ID.search(url or "")
        desc = TAG["description"].search(it)
        raw_desc = desc.group(1) if desc else ""
        text = clean(raw_desc)
        title = TAG["title"].search(it)
        pub = TAG["pubDate"].search(it)
        period = PERIOD.search(text)
        rows.append({
            "source": "uzjobs", "url": url,
            "id": ident.group(1) if ident else None,
            "ledger_id": f"uzjobs:{ident.group(1) if ident else url}",
            # The feed prefixes every title with «Вакансия: ».
            "title": re.sub(r"^Вакансия\s*:\s*", "",
                            clean(title.group(1)) if title else "") or None,
            "employer": from_feed(raw_desc, LABELS["employer"]),
            "region": from_feed(raw_desc, LABELS["region"]),
            "salary_text": from_feed(raw_desc, LABELS["salary"]),
            # **Both ends, from the advertisement's own posting period.**
            "posted": (f"{period.group(3)}-{period.group(2)}-{period.group(1)}"
                       if period else None),
            "expires": (f"{period.group(6)}-{period.group(5)}-{period.group(4)}"
                        if period else None),
            "pub_date": rfc822(clean(pub.group(1))) if pub else None,
            "countries": ["UZ"],
        })
    disagree = [r for r in rows if r["posted"] and r["pub_date"]
                and r["posted"] != r["pub_date"]]
    note(f"{len(rows)} advertisement(s) from one request to the feed. "
         f"**This is the feed's window, not the board** — the vacancy list "
         f"paginates through a form and was not exercised.")
    note(f"{len(disagree)} item(s) where `pubDate` and the posting period "
         f"disagree; they agreed on every item when this was written.")
    if a.since:
        rows = [r for r in rows if r["posted"] and r["posted"] >= a.since]
        note(f"{len(rows)} posted {a.since} or later.")
    if a.search:
        rows = [r for r in rows if fold(a.search) in fold(r["title"] or "")]
    if a.limit:
        rows = rows[: a.limit]
    print(json.dumps({"source": "uzjobs", "country": "UZ",
                      "feed_items": len(items), "returned": len(rows),
                      "date_disagreements": len(disagree),
                      "note": "21 is the feed's window; the board is larger "
                              "and its pagination was not exercised",
                      "ads": rows}, ensure_ascii=False, indent=1))


def cmd_ad(a):
    url = f"{BASE}/r/vakansy_view-{a.id}.html"
    code, page = get(url)
    if code in (404, 410):
        die(f"{a.id} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    text = clean(page)
    # **The `<h1>` is a section heading — `Вакансии (8)` on every page** — so
    # it is neither the job title nor evidence the advertisement exists.
    #
    # The title is the last non-empty line before `Работодатель:`, and it has
    # to be taken from the page split into LINES: `clean()` collapses the
    # document to one string, and a first version reading it that way returned
    # the navigation bar.
    lines = [clean(x) for x in re.split(r"<[^>]+>", page)]
    lines = [x for x in lines if x]
    title = None
    for i, line in enumerate(lines):
        if line.startswith("Работодатель"):
            title = lines[i - 1] if i else None
            break
    period = PERIOD.search(text)
    out = {"source": "uzjobs", "url": url, "id": a.id,
           "ledger_id": f"uzjobs:{a.id}",
           "title": title,
           "employer": labelled(text, PAGE_LABELS["employer"]),
           "category": labelled(text, PAGE_LABELS["category"]),
           "posted": (f"{period.group(3)}-{period.group(2)}-{period.group(1)}"
                      if period else None),
           "expires": (f"{period.group(6)}-{period.group(5)}-{period.group(4)}"
                       if period else None),
           # **No age and no gender field — #183.** The board prints
           # `Возраст:` and offers a `pol` filter; neither leaves this module.
           # *The advertisement is still emitted: it is the criterion that does
           # not propagate, not the vacancy.*
           "countries": ["UZ"]}
    # **The employer label is the discriminator, not the title.** This host
    # answers an unknown id with 200 and a page that has no `Работодатель:` at
    # all; a first version tested the `<h1>`, which every page carries, and
    # returned exit 0 on an invented id.
    if not out["employer"] and not out["posted"]:
        die(f"{a.id} is gone: this host answers an unknown advertisement with "
            f"HTTP 200 and a page carrying no `Работодатель:`. Record it as "
            f"discarded.", EXIT_GONE)
    print(json.dumps(out, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="the feed, in one request")
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="the start of the advertisement's own posting period")
    li.add_argument("--search", help="match the title; folds accents")
    li.add_argument("--limit", type=int)
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by numeric id")
    ad.add_argument("--id", required=True)
    ad.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
