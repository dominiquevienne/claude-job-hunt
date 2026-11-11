#!/usr/bin/env python3
"""Jwennjob (`jwennjob.com`, Haiti): «Plateforme de recherche d'emploi en
Haïti». #778.

**THE CARD CALLED IT A SHELL AND THAT WAS TRUE OF THE PAGE AND NEVER OF THE
BOARD.** `/jobs/` is served to the declared client as 60 378 bytes of Next.js
markup that renders «Chargement», with no advertisement, no count and no API
host in its markup — re-measured 2026-11-11, fifty-two days after the card,
and still exactly so. *The list is fetched by the application, and the issue's
«ce qui bloque: l'appel n'est pas encore lu» was the whole of the work.*

**THE CALL IS NOT THE ONE THE BUNDLE'S BASE URL NAMES, AND READING THAT BASE
WOULD HAVE CLOSED THIS BOARD.** The bundle declares
`NEXT_PUBLIC_API_URL || "https://api.jwennjob.com/api/v1"`, and that host
answers **HTTP 401 in 36 bytes** to a plain client. But the client that the
page actually builds is `new O({baseURL:"/api/proxy", requiresServerApiKey:
true})`: **the page talks to its OWN Next route, which holds a server-side key
and forwards.** So the 401 is a technical entry condition on an upstream we
never call (owner's decision of 2026-09-04, #100) and not a refusal that aims
at us — and `api.jwennjob.com` has its own rules file, 404, which is why the
guard is taken per HOST and never per brand (§3 bis).

**AND `requiresServerApiKey` PUTS A FLAG ON THE WIRE, NEVER A KEY: measured in
both directions rather than assumed.** `requestConfig()` returns
`{headers:{"x-proxy-api-key-required":"true"}}`, a boolean marker; the key
itself appears nowhere in any chunk. The route answers **200, 80 289 bytes,
`md5 eb00d4bcf068` — IDENTICAL with the header and without it** — so nothing
here sends a header it does not need.

**THE BOARD PRINTS ITS OWN TOTAL, AND THE WALK IS RECOUPED AGAINST IT.** The
envelope is Laravel's: `data` plus `meta` with
`current_page · from · to · per_page · last_page · total · path`, plus `links`.
On 2026-11-11 it declared **238 advertisements over 20 pages of 12**, and the
walk closed on `19 × 12 + 10 = 238` — a witness that does NOT come from our own
extraction, so a short read is nameable instead of looking like a smaller
board.

**THE ADVERTISEMENT IS READ BY `id` AND THE SLUG IS DECORATION.**
`/api/proxy/jobs/fonctions-generales-de-linfirmierere` is a **404**;
`/api/proxy/jobs/348` is a 200. And the page builds its own link the same way —
`href={`/jobs/${e.id}`}` — so the human URL carries the id too. *The record
still carries the slug, because the board publishes it.*

**THE DETAIL ROUTE ADDS EXACTLY TWO FIELDS**, measured by differencing the key
sets rather than by reading the page: `languages` and `skills`. Everything else
the advertisement holds is already in the list, so `list` is the enumerator and
`ad` exists for those two.

**«Pas de donnée» IS A SENTINEL IN FRENCH, AND A LIST OF REFUSALS WOULD NOT
HAVE CAUGHT IT.** It occurs **47 times on page 1 alone**. So the floor here is
POSITIVE — a string is a value when it passes a test — and the divergence is
not cosmetic. Measured on a SPREAD sample of 34 records (pages 1, 10 and 20,
never the first three):

```
champ                        `if x`   positive floor
recruiter.telephone            28  ->   8     <- twenty records
recruiter.social_links.*       22  ->   3        each
recruiter.lien_website         34  ->  24
experience_level.title         34  ->  33
```

**A naive reader would have declared a withheld telephone on TWENTY records
where nobody deposited one** — the `withheld_fields` lie of §4, which does not
mislead about the board but about OUR discretion, and whose output is identical
either way.

**WHAT REACHES A PERSON, AND IT IS IN THE LIST ITSELF.** `recruiter.email` is a
real address on **34 of 34**, `recruiter.telephone` on 8 of 34 under the floor,
and **3 of 34 descriptions carry a mail in prose**. *The issue recorded «ce
qu'il ne donnera jamais: les contacts recruteur»; the route gives them on every
record.* They are withheld, and the witness is DERIVED from what the redaction
took.

**NO PUBLICATION DATE EXISTS ANYWHERE ON THIS ROUTE.** Neither the list nor the
detail carries one: the only dates are the advertisement's `deadline` and
`recruiter.created_at`, which dates a COMPANY. So `posted` is `None` and the
record says why — a date is not derived from today, and an absent field is not
filled with a plausible one.

**THE RULES ARE ABSENT ON BOTH HOSTS AND THE CADENCE IS THEREFORE OURS.**
`jwennjob.com/robots.txt` → 404 (14 368 bytes of Next.js 404 page, `md5
bb0d206c26b4`) and `api.jwennjob.com/robots.txt` → 404 (6 663 bytes, Laravel's
«Non trouvé», `md5 ef700435156b`) — so `state: absent`, `certain: True`, open
by the owner's decision of 2026-09-13 (#283), and no `Crawl-delay`, no `Host:`,
no `Sitemap:` and no `Allow:` is written anywhere. 3 s is ours. *A threshold
nobody states is learned only by crossing it, so it is not learned.*

    jwennjob.py list
    jwennjob.py ad --id 348

*Measured 2026-11-11 19:19–19:23 UTC by the declared client, the guard taken on
each exact path — both hosts — in a turn of its own, `bin/fetch-body.py`
throughout.*
"""

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA
from _withheld import withheld_a_contact
from _zero import EXIT_INDETERMINATE, empty_first_page

HOST = "jwennjob.com"
BASE = f"https://{HOST}"
#  The site's OWN proxy, which is what its page calls. `api.jwennjob.com/api/v1`
#  is the upstream the bundle names and it answers 401 to a plain client: the key
#  that opens it lives on the Next server and is none of our business.
API = BASE + "/api/proxy/jobs"
AD = BASE + "/jobs/"
COUNTRY = "HT"

#  A route this host NAMES and that we do not interrogate. `/api/proxy/filters`
#  serves the taxonomies behind the search form (62 617 bytes); nothing here needs
#  them, and "the guard permits" is not "it is ours to take".
UNINTERROGATED = ("/api/proxy/filters",)

#  The sentinel this board writes where a field is empty, and the forms a
#  neighbouring one might. **The floor is POSITIVE: a string is a value when it
#  passes this test, never because it is missing from a list of refusals.** The
#  first alternative is the one measured here -- 47 occurrences on page 1 -- and
#  the others are declared INERT on this corpus: they exist because the next
#  sentinel arrives spelled differently, not because they protect anything we saw.
SENTINEL = re.compile(
    r"^\s*(?:pas\s+de\s+donn[ée]es?|n/?a|aucune?|-{1,3}|null|none|undefined"
    r"|\$undefined)\s*$", re.I)

MAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
#  Haiti is +509 and its numbers are EIGHT digits beginning 2, 3 or 4. The form is
#  anchored on an explicit +509, or on eight digits that are not part of a longer
#  run -- a salary line here reads «40,001 - 50,000 HTG», so a looser form would
#  reach a contract value, which is the kyat trap of §4.
TEL_RE = re.compile(
    r"(?<![\d+])(?:\+\s?509[\s.\-]?[2-4]\d{3}[\s.\-]?\d{4}"
    r"|[2-4]\d{3}[\s.\-]\d{4})(?![\d])")
TAG_RE = re.compile(r"(?s)<[^>]+>")

EXIT_BROKEN, EXIT_GONE = 2, 3
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

#  `delay_for()` has nothing to return on a 404 rules file, so the cadence is ours.
_PACE = Pace(HOST, own=3.0)

TIMEOUT = 60


class ShapeMoved(Exception):
    """The response is not the shape every reader below assumes."""


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jwennjob] {msg}", file=sys.stderr)


def gate(url):
    """The guard on the EXACT url, host included -- this board has two hosts."""
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "application/json",
        "Accept-Language": "fr"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0], r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, "", url
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


# ---------------------------------------------------------------- pure readers

def declared(value):
    """A POSITIVE floor: `(value, state)`, and the sentinel is a STATE.

    It runs on the RAW value, because normalising first collapses «present but
    empty» into «absent» and makes the floor inert. Three states and not two:
    `if x` conflates all three, and the one that costs is `sentinel` -- a board
    that writes «Pas de donnée» into a telephone column has deposited nothing,
    and reading it as a number is how a record comes to declare a discretion
    nobody exercised.
    """
    if value is None:
        return None, "absent"
    if isinstance(value, str):
        if not value.strip():
            return None, "present but empty"
        if SENTINEL.match(value):
            return None, "sentinel"
    return value, "declared"


def text_of(markup):
    """Visible text of an HTML description, entities resolved AFTER the tags.

    The order is not indifferent: `html.unescape` first would turn `&lt;p&gt;`
    into a tag that `TAG_RE` then eats, so a description that quotes markup would
    lose the quoted part. And it runs BEFORE the redaction on purpose -- an
    address written `nom&#64;exemple.ht` is a contact, and a motif on the raw
    markup does not see it.
    """
    if markup is None:
        return None
    s = TAG_RE.sub(" ", str(markup))
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s or None


def envelope_of(body):
    """`(rows, meta)` -- and the shape is ASSERTED, never searched for.

    A reader that walks looking for a list would find `meta.links` and report a
    page of pagination widgets as advertisements.
    """
    try:
        d = json.loads(body)
    except ValueError as e:
        raise ShapeMoved(f"the response is not JSON: {e}")
    if not isinstance(d, dict):
        raise ShapeMoved(
            "the response is %s and not the `data`/`meta` envelope this route "
            "served on 2026-11-11" % type(d).__name__)
    rows = d.get("data")
    if not isinstance(rows, list):
        raise ShapeMoved(f"`data` is {type(rows).__name__} and not a list")
    bad = [type(x).__name__ for x in rows if not isinstance(x, dict)]
    if bad:
        raise ShapeMoved(f"`data` carries {bad[0]} beside its records")
    meta = d.get("meta")
    return rows, (meta if isinstance(meta, dict) else {})


def total_of(meta):
    """The total the BOARD states, or `None`. Never a count of our own.

    It is only believed as an integer: `meta.total` is 238 and `meta.last_page`
    20, and a string there would make the shortfall arithmetic below compare a
    number with text.
    """
    t = meta.get("total")
    return t if isinstance(t, int) else None


def scrub(prose):
    """Remove what reaches a person from the description, and say WHAT was taken.

    The witness is DERIVED from the substitutions this function actually made --
    never from whether a column was non-empty. A name in `withheld_fields` that
    nobody deposited lies about OUR discretion, and the output is identical
    either way.
    """
    if not prose:
        return prose, ()
    taken = []
    out, n = MAIL_RE.subn("[email withheld]", prose)
    if n:
        taken.append("email")
    out, n = TEL_RE.subn("[telephone withheld]", out)
    if n:
        taken.append("telephone")
    return out, tuple(taken)


def label_of(record, key):
    """`{"id": n, "title": s}` -> the title, under the floor.

    Eight fields of this route have that shape, and on some records the whole
    object is `null` -- `salary` is absent on 18 of 34 and `commune` on 3 -- so
    the object's presence is tested before its title. An `id` with no lookup
    table is a foreign key and is not emitted as if it were a name.
    """
    o = record.get(key)
    if not isinstance(o, dict):
        return None
    v, _state = declared(o.get("title"))
    return text_of(v) if v is not None else None


def titles_of(record, key):
    """A list of `{"id","title"}` -> its titles. `languages` and `skills` only."""
    xs = record.get(key)
    if not isinstance(xs, list):
        return None
    out = []
    for x in xs:
        if not isinstance(x, dict):
            continue
        v, _state = declared(x.get("title"))
        if v is not None:
            out.append(text_of(v))
    return out or None


def parse_record(record):
    """One advertisement, with its contacts withheld and the witness derived."""
    rid = record.get("id")
    if not isinstance(rid, int):
        raise ShapeMoved(f"a record carries id={record.get('id')!r}, not an int")

    title, _ = declared(record.get("title"))
    desc, from_prose = scrub(text_of(declared(record.get("description"))[0]))

    rec = record.get("recruiter")
    rec = rec if isinstance(rec, dict) else {}
    employer, employer_state = declared(rec.get("nom"))

    #  The two contact COLUMNS, each spelled as a LITERAL of the shared
    #  vocabulary. A loop over (column, canonical) pairs appends through a
    #  VARIABLE, and the vocabulary check in `tests/test_core.py` reads LITERALS
    #  only: the conciser form would leave this file silently unchecked.
    #
    #  **And the floor is what decides here, not `if x`.** `recruiter.telephone`
    #  is non-empty on 28 of 34 and a real number on 8: the other twenty say
    #  «Pas de donnée», and naming them would declare a discretion nobody
    #  exercised.
    withheld = []
    if declared(rec.get("email"))[0] is not None:
        withheld.append("employer_email")
    if declared(rec.get("telephone"))[0] is not None:
        withheld.append("employer_phone")
    for name in from_prose:
        if name not in withheld:
            withheld.append(name)
    withheld = sorted(withheld)

    out = {
        "source": "jwennjob",
        "country": COUNTRY,
        "url": AD + str(rid),
        "id": rid,
        "slug": declared(record.get("slug"))[0],
        "title": text_of(title) if title else None,
        "employer": text_of(employer) if employer else None,
        "employer_declared": employer_state,
        "description": desc,
        "description_contacts_withheld": bool(from_prose),
        #  **This route carries NO publication date, on the list or the detail.**
        #  `recruiter.created_at` dates a company and `deadline` is an expiry, so
        #  neither is promoted here: an absent date is emitted as absent.
        "posted": None,
        "posted_absent": "this route declares no publication date",
        "expires": declared(record.get("deadline"))[0],
        "withheld_fields": withheld,
    }

    #  The declaration follows what the redaction ACTUALLY took, and it is only
    #  written when something reaching a PERSON left. On the 34 records held on
    #  2026-11-11 it is true on 34 -- `recruiter.email` is real on every one --
    #  so the branch is not dead here, and the FALSE branch is exercised by the
    #  bench rather than by this corpus.
    if withheld_a_contact(withheld):
        out["contacts_withheld"] = True

    for key, name in (("contract", "contract"), ("sector", "sector"),
                      ("department", "region"), ("commune", "city"),
                      ("education_level", "education_level"),
                      ("experience_level", "experience_level")):
        v = label_of(record, key)
        if v is not None:
            out[name] = v

    #  A RANGE in gourdes, as the board words it («40,001 - 50,000 HTG»): a label
    #  and not a number, so it travels as one and is never parsed into bounds.
    salary = label_of(record, "salary")
    if salary is not None:
        out["salary_declared"] = salary

    site, _ = declared(rec.get("lien_website"))
    if site is not None:
        out["employer_website"] = site

    for key in ("languages", "skills"):
        v = titles_of(record, key)
        if v is not None:
            out[key] = v

    n = record.get("applications_count")
    if isinstance(n, int):
        out["applications_count"] = n

    #  The keys are OURS, so this can only fire while someone is adding one. It is
    #  asserted rather than removed: a constant that reads like a guard and guards
    #  nothing is worse than none.
    leaked = sorted(k for k in out
                    if k.endswith(("_email", "_phone", "_telephone"))
                    and k not in ("employer_email_withheld",))
    if leaked:
        raise ShapeMoved(
            "this record would emit %s -- a raw contact. `recruiter.email` is a "
            "real address on every record this route serves; it is named in "
            "`withheld_fields` and never carried." % ", ".join(leaked))
    return out


# ---------------------------------------------------------------- commands

def merge(pages):
    """The pages' records into one list, each advertisement once.

    The dedup lives HERE and not in the page reader, because that is the only
    place it can fire: a page is twelve distinct records by construction, and an
    advertisement posted BETWEEN two requests shifts the window and pushes the
    twelfth of page 1 onto page 2.
    """
    out, seen, twice = [], set(), 0
    for rows in pages:
        for r in rows:
            rid = r.get("id")
            if rid in seen:
                twice += 1
                continue
            seen.add(rid)
            out.append(r)
    return out, twice


def walk(limit=None, max_pages=40):
    """Pages of the one enumerator, and the ends, NAMED.

    Without the name a walk cut by the transport reads as a smaller board.
    """
    pages, page, end, stated = [], 1, "ended of itself", None
    while page <= max_pages:
        code, body, _ = get(f"{API}?page={page}")
        if code != 200:
            end = f"cut by the transport (HTTP {code} on page {page})"
            break
        try:
            rows, meta = envelope_of(body)
        except ShapeMoved as e:
            if page == 1:
                die(f"{e}", EXIT_BROKEN)
            end = f"cut by the shape on page {page}: {e}"
            break
        if stated is None:
            stated = total_of(meta)
        if not rows:
            end = f"ended of itself (page {page} is empty)"
            break
        pages.append(rows)
        held, _twice = merge(pages)
        if limit and len(held) >= limit:
            end = f"capped at the requested {limit}"
            break
        last = meta.get("last_page")
        if isinstance(last, int) and page >= last:
            end = f"ended of itself (the board declares {last} page(s))"
            break
        page += 1
    else:
        end = f"capped at {max_pages} pages"
    rows, twice = merge(pages)
    if limit:
        rows = rows[:limit]
    return rows, end, page, stated, twice


def cmd_list(a):
    rows, end, pages, stated, twice = walk(limit=a.limit, max_pages=a.max_pages)
    if not rows:
        code, body, _ = get(f"{API}?page=1")
        die(empty_first_page("jwennjob", body, what="advertisement", where=API),
            EXIT_INDETERMINATE)
    out = []
    for r in rows:
        try:
            out.append(parse_record(r))
        except ShapeMoved as e:
            die(f"{e}", EXIT_BROKEN)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    note(f"{len(out)} advertisement(s) over {pages} page(s) -- walk {end}")
    if twice:
        note(f"{twice} record(s) arrived twice across pages and were read once "
             f"-- the window shifts while the walk runs")

    #  The count is RECOUPED against a figure the board states itself, so a short
    #  read is named instead of passing for a smaller board.
    if stated is None:
        note("board size: NOT ESTABLISHED -- this route declared no `meta.total` "
             "on this read")
    elif a.limit:
        note(f"board size: {stated}, as the board states it -- this read is "
             f"capped at {a.limit} and establishes nothing about it")
    elif len(out) == stated:
        note(f"board size: {stated} -- the walk and the board's own `meta.total` "
             f"AGREE")
    else:
        note(f"{len(out)} emitted, board states {stated} -- "
             f"{abs(stated - len(out))} "
             f"{'short' if len(out) < stated else 'over'}")

    withheld = sum(1 for r in out if r.get("contacts_withheld"))
    prose = sum(1 for r in out if r.get("description_contacts_withheld"))
    note(f"{withheld}/{len(out)} record(s) had something reaching a person "
         f"removed, {prose} of them from the description's prose")


def cmd_ad(a):
    """One advertisement by id, from the detail route -- it adds two fields."""
    code, body, _ = get(f"{API}/{a.id}")
    if code == 404:
        die(f"id {a.id}: HTTP 404 -- this route reads by ID and a SLUG is a 404 "
            f"on it", EXIT_GONE)
    if code != 200:
        die(f"id {a.id}: HTTP {code}", EXIT_BROKEN)
    try:
        d = json.loads(body)
    except ValueError as e:
        die(f"the response is not JSON: {e}")
    record = d.get("data") if isinstance(d, dict) else None
    if not isinstance(record, dict):
        die("the detail response is not the `data` envelope this route served "
            "on 2026-11-11", EXIT_BROKEN)
    try:
        json.dump(parse_record(record), sys.stdout, ensure_ascii=False, indent=2)
    except ShapeMoved as e:
        die(f"{e}", EXIT_BROKEN)
    sys.stdout.write("\n")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    s = p.add_subparsers(dest="cmd", required=True)

    pl = s.add_parser("list", help="walk the one enumerator")
    pl.add_argument("--limit", type=int, default=None)
    pl.add_argument("--max-pages", type=int, default=40, dest="max_pages")
    pl.set_defaults(fn=cmd_list)

    pa = s.add_parser("ad", help="one advertisement by id")
    pa.add_argument("--id", type=int, required=True)
    pa.set_defaults(fn=cmd_ad)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
