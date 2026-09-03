#!/usr/bin/env python3
"""Fetch Trinidad and Tobago's national vacancies from EmployTT — where a
missing advertisement answers **200 with the listing page**.

The Ministry of Labour's national employment service. **No key, no cookie, no
browser, and no endpoint**: every advertisement is in the served HTML of one
page, and `robots.txt` is 26 bytes that close nothing.

  GET /jobs/list        → 200 text/html; every live advertisement, in the
                          markup. jPList paginates in the browser, so the
                          "10 per page" control is not a server limit
  GET /jobs/view/<id>   → one advertisement

**AN ID THAT DOES NOT EXIST IS NOT AN ERROR HERE.** Measured 2026-09-03:
`/jobs/view/2604`, `2606`, `2609`, `2617`, `2632`, `2500` and `2000` all
answer **HTTP 200 with 175 396 bytes — byte for byte the listing page.** No
redirect status, no 404, nothing in the body that announces itself as a
substitution.

**So the status code cannot be the check.** A real advertisement page carries
**zero** `/jobs/view/` links; the listing carries one per advertisement, and
its `<h1>` reads *Jobs Listing* rather than a job title. `ad` tests that and
exits 3 rather than emitting a card built from the listing — which would have
carried the *first* advertisement's title under the id that was asked for.

THE FILTER LINKS ARE CLIENT-SIDE, AND THEY ALL RETURN THE SAME PAGE.
`/jobs/list/category-cbx-1`, `/jobs/list/city-cbx-PortofSpain` and
`/jobs/list/employmentStatus-cbx-fulltime` each returned **the same 21
advertisements** as `/jobs/list`. Two readings fit that — *the server sends
everything and jPList filters it*, or *the path segment is ignored* — and
**they are indistinguishable from the counts alone**, so this script does not
paginate or filter by URL. One request is the sweep.

**LISTING MEMBERSHIP TRACKS NEITHER EXPIRY NOR RECENCY.** Measured
2026-09-03, and each step corrected the one before it.

`/jobs/view/2618` renders a complete advertisement — *Driver/Messenger*,
Barataria — and is **absent from the listing**. The first reading was that the
listing is the unexpired set. The advertisement pages carry an `Expires:`
field, and it refutes that:

    /jobs/view/2603   Expires: 03 September 2026   listed
    /jobs/view/2618   Expires: 04 September 2026   NOT listed

**The one expiring today is listed; the one expiring tomorrow is not.** And
the listing itself carries the other half of the contradiction: **two of its
twenty-one advertisements expired on 02 September** — `2607` and `2615` — and
were still being served on the third. Those two, and only those two, print no
"expires <date>" sentence on their card, which is how the board itself marks a
deadline already past. **Two expired advertisements in, one unexpired
advertisement out.**

Scanning ids 2590-2640: **22 render an advertisement** — the listing's 21 plus
2618 — and the other 29 answer with the listing page. There is no archive
either; ids below the live range are gone rather than kept.

**Nothing visible from outside explains which of the twenty-two is listed.**
`search` returns what the listing serves and says so; **it does not claim to be
the board**, and the count it prints is the listing's, not a total. *A listing
that looks complete* is what this repository keeps finding, and here the gap
is small, real and unexplained rather than argued away.

THE DESCRIPTION IS ESCAPED TWICE. The stored field is HTML and the template
escapes it again, so the page literally contains `&lt;div&gt;` and `&#47;`.
`--with-text` unescapes twice and then strips tags; unescaping once leaves
markup as visible text in the ledger.

Verified against the live site on **2026-09-03**.
"""

import argparse
import html as html_mod
import json
import re
import sys
import urllib.error
import urllib.request

from _decode import decode_body
from _robots import verdict as robots_verdict
from _zero import zero_note

BASE = "https://employtt.gov.tt"
LIST = BASE + "/jobs/list"
from _ua import UA

EXIT_BROKEN, EXIT_GONE, EXIT_REFUSED, EXIT_UNKNOWN = 2, 3, 7, 8

CARD = re.compile(r'(?=<div class="col-lg-12 mb-20 filter-item)')
ADLINK = re.compile(r"/jobs/view/(\d+)")
DATE = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b")
EXPIRES = re.compile(r"expires\s+(\d{1,2}\s+\w+\s+\d{4})", re.I)
H1 = re.compile(r"(?is)<h1[^>]*>(.*?)</h1>")

MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"], start=1)}


def _today():
    import datetime
    return datetime.date.today().isoformat()


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[employtt] {msg}", file=sys.stderr)


def gate():
    v = robots_verdict("employtt.gov.tt")
    if not v["sweep"]:
        die(f"employtt.gov.tt: {v['reason']}",
            EXIT_UNKNOWN if v["sweep"] is None else EXIT_REFUSED)
    return v


def get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


ENTITY = re.compile(r"&(?:#\d+|#x[0-9a-fA-F]+|[a-zA-Z][a-zA-Z0-9]*);")


def unescape_fully(value):
    """**This site escapes twice, so one pass is not the inverse.**

    A title came out `Driver&#47;Messenger` and a description came out full of
    `&lt;div&gt;`. Unescaping blindly twice would be wrong on a value that
    legitimately contains `&amp;amp;`, so the second pass runs **only while an
    entity is still there** — a fixed point rather than a fixed count.
    """
    for _ in range(3):
        if not ENTITY.search(value):
            break
        after = html_mod.unescape(value)
        if after == value:
            break
        value = after
    return value


def text_of(fragment):
    t = re.sub(r"(?is)<(script|style|svg)[^>]*>.*?</\1>", " ", fragment)
    t = unescape_fully(re.sub(r"<[^>]+>", "\n", t))
    return [re.sub(r"\s+", " ", x).strip()
            for x in t.split("\n") if x.strip()]


def is_the_listing(body):
    """**The substitution check, and it is not the status code.**

    A missing id answers 200 with this page. A real advertisement page has no
    `/jobs/view/` link in it at all; the listing has one per advertisement.
    """
    return len(set(ADLINK.findall(body))) > 1


def us_date_to_iso(value):
    m, d, y = value.split("/")
    return f"{y}-{m}-{d}"


def spelled_date_to_iso(value):
    d, mon, y = value.split()
    month = MONTHS.get(mon.lower())
    return f"{y}-{month:02d}-{int(d):02d}" if month else None


FIELD = {
    "employment_status": "employmentStatus",
    "created": "creationDateSort",
    "published": "publishDateSort",
    "deadline": "deadlineDateSort",
    "title": "title decode",
    "company": "employerfilter decode",
    "location_text": "locationfilter decode",
    "category": "categoryfilter decode",
}


def field(block, cls):
    """The value of one named field, or `None`.

    **Read by the class the page gives it, not by position.** The first draft
    counted text nodes: title at index 0, employer at 1, category at -1. It
    worked on twenty cards and put **"Forgot your password?"** in the category
    of the twenty-first, because that block runs to the end of the document
    and swallows the login modal. Positions are an accident of layout; these
    names are the page's own.
    """
    m = re.search(r'class="[^"]*\b' + re.escape(cls) +
                  r'\b[^"]*"[^>]*>(.*?)</', block, re.S)
    if not m:
        return None
    value = unescape_fully(re.sub(r"<[^>]+>", " ", m.group(1)))
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def card(block):
    ident = ADLINK.search(block)
    if not ident:
        return None
    ident = ident.group(1)
    got = {k: field(block, cls) for k, cls in FIELD.items()}
    deadline = got["deadline"]
    spelled = EXPIRES.search(" ".join(text_of(block[:6000])))
    spelled_iso = spelled_date_to_iso(spelled.group(1)) if spelled else None
    expires = us_date_to_iso(deadline) if deadline else None
    salary = field(block, "field-salary_from")
    # The label sits in `field-salary_from` and the value follows it; on every
    # card measured the value is the board's own word "Concealed".
    lines = text_of(block[:6000])
    value = None
    if "salary" in lines:
        i = lines.index("salary")
        value = lines[i + 1] if i + 1 < len(lines) else None
    shown = (value or salary or "").strip().lower()
    return {
        "id": ident,
        "ledger_id": f"employtt:{ident}",
        "url": f"{BASE}/jobs/view/{ident}",
        "title": got["title"],
        "company": got["company"],
        "location_text": got["location_text"],
        "category": got["category"],
        "employment_status": got["employment_status"],
        "created": us_date_to_iso(got["created"]) if got["created"] else None,
        "published": (us_date_to_iso(got["published"])
                      if got["published"] else None),
        "expires": expires,
        # The card also prints the deadline in words. Where it does, the two
        # are compared; `null` means the card printed no such sentence, which
        # is what an already-expired advertisement does.
        "expiry_agrees_with_the_words": (
            None if spelled_iso is None else spelled_iso == expires),
        "salary_text": value or salary,
        # **Count on the value, not on the field being present.** Every card
        # carries the salary line; "Concealed" is the board's own word for a
        # figure it was not given, not a parse failure.
        "salary_stated": bool(shown) and shown not in ("concealed", "salary"),
    }


def cmd_search(a):
    gate()
    code, body = get(LIST)
    if code != 200:
        die(f"{LIST}: HTTP {code}")
    blocks = [b for b in CARD.split(body) if "/jobs/view/" in b]
    rows, kept, salaried = [], 0, 0
    for b in blocks:
        row = card(b)
        if not row:
            continue
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False))
        kept += 1
        salaried += bool(row["salary_stated"])
        if a.limit and kept >= a.limit:
            break
    if kept == 0:
        note(zero_note("employtt"))
        return
    stale = sum(1 for r in rows if r.get("expires") and
                r["expires"] < _today())
    note(f"{kept} advertisement(s) from one request — **what the listing "
         f"serves, which is not what the board serves.** {stale} of them have "
         f"a deadline already past, and `/jobs/view/2618` renders a complete "
         f"advertisement that is **not listed and expires later than ones "
         f"that are**. Membership tracks neither expiry nor recency, and "
         f"nothing on the site explains it. The board publishes no total, so "
         f"{kept} is the listing's count and nothing further is claimed.")
    note(f"salary: {salaried} of {kept} state a figure; the rest print "
         f"'Concealed', which is the board's own word and not a missing "
         f"field.")


def cmd_ad(a):
    gate()
    url = a.url or f"{BASE}/jobs/view/{a.id}"
    code, body = get(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE)
    if is_the_listing(body):
        die(f"{url}: the server answered **200 with the listing page**, which "
            f"is what it does for an advertisement that does not exist. "
            f"Nothing is emitted, because a card built from this body would "
            f"carry the first advertisement's title under the id you asked "
            f"for.", EXIT_GONE)
    h1 = H1.search(body)
    title = text_of(h1.group(1))[0] if h1 else None
    lines = text_of(body[body.find("Job Information"):])
    # **`Expires:` sits above the Job Information block**, so the slice that
    # reads the specification fields threw away the one field that refuted the
    # obvious reading of why 2618 is unlisted. Read the whole page for it.
    whole = text_of(body)

    def after(label, where=None):
        source = where if where is not None else lines
        try:
            return source[source.index(label) + 1]
        except (ValueError, IndexError):
            return None
    row = {
        "id": ADLINK.search(url).group(1) if ADLINK.search(url) else a.id,
        "url": url,
        "title": title,
        "category": after("Category:"),
        "location_text": after("Work Location:"),
        "salary_text": after("Salary (Monthly)"),
        "employment_type": after("Type"),
        # **The field that refuted the obvious explanation.** 2603 expires
        # today and is listed; 2618 expires tomorrow and is not.
        "expires_text": after("Expires:", whole),
    }
    row["ledger_id"] = f"employtt:{row['id']}"
    salary = (row["salary_text"] or "").strip().lower()
    row["salary_stated"] = bool(salary) and salary != "concealed"
    if a.with_text:
        i = body.find("Job Description")
        # The stored field is HTML and the template escapes it again, so one
        # pass leaves `<div>` sitting in the ledger as text. `unescape_fully`
        # runs to a fixed point rather than a fixed count.
        row["description"] = "\n".join(text_of(unescape_fully(
            body[i:i + 40000])))
    print(json.dumps(row, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="every live advertisement, one request")
    s.add_argument("--limit", type=int)
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="read one advertisement")
    d.add_argument("--url")
    d.add_argument("--id")
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    if a.cmd == "ad" and not (a.url or a.id):
        p.error("give --url or --id")
    a.func(a)


if __name__ == "__main__":
    main()
