#!/usr/bin/env python3
r"""DziSeldra (Bhutan) -- the vacancies of a community classifieds platform.

**One enumerator, and it was established by inclusion and not by two counts.**
`/jobs` renders nine advertisement links server-side and `/api/getjobs/?page=1`
returns sixteen records; the nine are a STRICT SUBSET of the sixteen -- measured
on 2026-11-10, `page - api` empty, inclusion true. So the page is a featured
subset and the route is the enumerator. *Two cardinals would not have said
that: 9 and 16 are consistent with two sets that only overlap, which is the
jobsdz case of the day before, where 1 571 sitemap addresses and 2 551-2 560
board records contained neither one another.*

**The route is bounded to the vacancy nature, and the discriminant was a page of
ANOTHER nature.** `/cars` calls no API route at all -- zero call verbs, zero
api-ish paths, by three motifs of different shapes -- and carries its sixteen
listings as server-rendered `/seldra/<id>` links. That is a POSITIVE finding and
not a silent zero: the links are there. And `category_id` is CONSTANT across the
sixteen records and reads `2` on the advertisement page, so this route serves one
category.

**The advertisement page adds nothing, which is why this adapter never fetches
one.** `/seldra/59505` returns HTTP 200 and 93 373 bytes titled with the
advertisement's own title, and 8 of 8 of the long words of the JSON `content`
appear in it. The address form was ESTABLISHED by retrieving it, never composed
from the `posturl` the Vue component names -- `url` is `null` on 16/16 records,
so the JSON does not give it.

**Four column names LIE, and an adapter built on name matching would emit voids
and discard the real dates.** Measured over the sixteen records of page 1:

    vacancy_salary          1/16 non-empty      tender_opening_date     16/16, 14 distinct
    vacancy_job_type        1/16                tender_submission_date  16/16, 14 distinct
    vacancy_experience      1/16                car_manufacturer        16/16, CONSTANT
    vacancy_qualification   2/16                dzongkhag               16/16, CONSTANT

The columns whose name says `vacancy` are the least filled; the columns whose
name says `tender` carry the real datetimes. And a POSITIVE floor alone called
`car_manufacturer` and `dzongkhag` REAL -- they are the integer 1 on every
record. *A floor that excludes None, '' and 0 does not establish that a column
means what its name says; what showed it is the count of DISTINCT values beside
the fill rate, and the card promises `dzongkhag` as a field.*

**The contact is in the PROSE as well as in the columns, so withholding the
columns alone would leave it.** `content` carries a mail address on 10/16 and a
telephone on 10/16, and on 10/16 the digits of `contact_mobile` itself reappear
inside `content`. Withholding `contact_email`/`contact_mobile` and emitting the
description untouched would have published the same contact it had just removed.

**The telephone motif is the strict one, and the kyat is why.** A loose
`[2-8]\d{6}` reaches seven bare digits, and the ngultrum is pegged to the rupee,
so a contract value of 2 500 000 matches it. On a fabricated control where the
two motifs MUST differ the loose one takes two spans and the strict one takes
one; on the real corpus they agree exactly -- 18 spans each, ZERO taken by the
loose motif alone. So the strict motif loses nothing measured and removes the
risk that destroyed 113 of 115 Burmese salaries. *Declared residue: a Bhutanese
landline of seven digits written without its +975 prefix escapes it, and none
exists on this corpus of 16 -- a dated reading, not a property.*

**`likers` is never read beyond its scale and never emitted.** The route serves,
beside each advertisement, the people who merely LIKED it: 28 fields per person
including name, email, mobile, address, birthday, gender and an `api_token`.
Scale on page 1 is one person over sixteen records. The path filter is a
SECURITY CONDITION and not an optimisation -- the lesson of the Tajik board's
34 894 curricula, obtained on a COLUMN instead of a path.

Rules file: `User-agent: *` and a single empty `Disallow:`, 24 bytes, HTTP 200,
read 2026-11-10T12:08:08Z. It refuses nothing -- and `group_for` returns the
empty string INSIDE the disallow list, so `if disallows:` is TRUTHY and would
conclude the host refuses something. No `Crawl-delay`, no `Sitemap:`, no `Allow`.
So the cadence is OURS, and this host answers in 60 to 108 seconds.

Board size is NOT established unless the walk ends of itself: the response is a
BARE LIST with no envelope, no `meta` and no `links`, so nothing declares a
total. `?page=2` is honoured -- sixteen records, intersection ZERO with page 1.
"""

import argparse
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

BASE = "https://dziseldra.com"
API = BASE + "/api/getjobs/"
AD = BASE + "/seldra/"
COUNTRY = "BT"

#  A route this host NAMES and that we do not interrogate: `/api/posts/` appears
#  in the advertisement page's scripts. It is not bounded to a nature by anything
#  we have read, and `likers` showed what an unbounded route here serves. "The
#  guard permits" is not "it is ours to take".
UNINTERROGATED = ("/api/posts/", "/api/save_post/", "/api/unsave_post/")

#  Columns of the vacancy nature. The four misleading names are placed by what
#  they CARRY, measured, and never by what they say.
VACANCY_DATES = ("tender_opening_date", "tender_submission_date",
                 "vacancy_submission_date")

#  CONSTANT on 16/16 and therefore discriminating nothing. Kept as a literal so
#  that a future reader does not re-measure them, and so that nothing emits them
#  as if they were fields.
CONSTANT_ON_PAGE_1 = (
    "author_id", "car_manufacturer", "category", "category_id", "comment_count",
    "dzongkhag", "editor_id", "is_editors_pick", "is_featured",
    "is_visible_to_all", "liked", "saved", "status", "type",
)

#  Natures this platform also serves, whose columns ride in the SAME flat schema.
#  Nothing of them is emitted on a vacancy.
OTHER_NATURE = re.compile(
    r"^(car_|property_|housing_|service_type|no_of_|area_in_decimal)")

MAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
#  STRICT: an explicit +975 and eight digits, or a Bhutanese mobile prefix (17 or
#  77) and six more. See the docstring -- the loose form reaches a contract value.
TEL_RE = re.compile(r"(?<![\d])(?:\+?975[\s.\-]?\d{8}|(?:17|77)\d{6})(?![\d])")
TAG_RE = re.compile(r"(?s)<[^>]+>")
ENTITY_RE = re.compile(r"&(?:[a-zA-Z][a-zA-Z0-9]{1,30}|#\d{1,6}|#x[0-9a-fA-F]{1,6});")

EXIT_BROKEN, EXIT_GONE = 2, 3
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

#  `delay_for()` returns None on this host's 24-byte rules file, so the cadence is
#  ours; 3 s against a host that answers in 60-108 s. A threshold nobody states is
#  learned only by crossing it, so it is not learned.
_PACE = Pace("dziseldra.com", own=3.0)

#  This host answers in 60 to 108 seconds, measured. The house default of 60 would
#  time out on a body that is arriving.
TIMEOUT = 180


class ShapeMoved(Exception):
    """The response is not the shape every reader below assumes."""


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[dziseldra] {msg}", file=sys.stderr)


def gate(url):
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
        "Accept": "application/json,text/html;q=0.9",
        "Accept-Language": "en"})
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

def records_of(body):
    """The BARE LIST this route returns.

    There is no envelope: no `data`, no `meta`, no `links`. A reader that walks
    looking for a `data` key finds one nowhere and would report an empty page on
    a response carrying sixteen records, so the shape is asserted instead of
    searched.
    """
    try:
        d = json.loads(body)
    except ValueError as e:
        raise ShapeMoved(f"the response is not JSON: {e}")
    if not isinstance(d, list):
        raise ShapeMoved(
            "the response is %s and not the bare list this route served on "
            "2026-11-10 -- an envelope would have appeared, and every reader "
            "below assumes the list" % type(d).__name__)
    bad = [type(x).__name__ for x in d if not isinstance(x, dict)]
    if bad:
        raise ShapeMoved(f"the list carries {bad[0]} beside its records")
    return d


def text_of(markup):
    """Visible text, and `None` for present-but-empty is the CALLER's business."""
    if markup is None:
        return None
    s = TAG_RE.sub(" ", str(markup))
    s = ENTITY_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s or None


def declared(value):
    """A POSITIVE floor: present-and-empty is not absent, and `if x` conflates
    them.

    It runs on the RAW value. Normalising first collapses 'present but empty'
    into 'absent' and makes the floor inert -- measured on jobsdz, where the
    third advertisement's `hiringOrganization.name` IS an empty string.

    **Declared: the second branch is DEAD on this host's corpus.** Zero of the 32
    records held on 2026-11-10 carries a present-but-empty string, `companies`
    included. So it is red under mutation, green in any suite, and never taken in
    the world -- kept because the shape moves and the distinction costs nothing,
    not because it protects anything measured here.
    """
    if value is None:
        return None, "absent"
    if isinstance(value, str) and not value.strip():
        return None, "present but empty"
    return value, "declared"


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


def employer_of(record):
    """`companies` is an object on 7/16 and `company_id` is an integer on 16/16.

    The integer is a foreign key with no lookup table in this response, so it is
    not a name and it is not emitted as one.
    """
    c = record.get("companies")
    if not isinstance(c, dict):
        return None, "absent"
    name, state = declared(c.get("company_name"))
    return (text_of(name) if name else None), state


def parse_record(record):
    """One vacancy, emitting ONLY the columns of its own nature."""
    rid = record.get("id")
    if not isinstance(rid, int):
        raise ShapeMoved(f"a record carries id={record.get('id')!r}, not an int")

    title, _ = declared(record.get("title"))
    raw_desc, _ = declared(record.get("content"))
    desc, from_prose = scrub(text_of(raw_desc) if raw_desc else None)

    employer, employer_state = employer_of(record)

    #  The two contact COLUMNS, mapped onto the SHARED vocabulary: `_withheld`
    #  knows `email` and `telephone`, and `contact_email`/`contact_mobile` would
    #  make `withheld_a_contact` RAISE rather than guess. Measured across the
    #  adapters here, `email` is the canonical name 32 times and `telephone` 22.
    #
    #  **Each site spells the canonical name as a LITERAL, and the loop that read
    #  better is what broke it.** A loop over (column, canonical) pairs appends
    #  through a VARIABLE, and the vocabulary check in `tests/test_core.py` reads
    #  LITERALS only: it collected NONE from this file and said so -- "aucun nom
    #  collecte, le controle est inerte". A test of literals is blind to what
    #  passes a variable, so the conciser form silently left the file unchecked.
    withheld = []
    if declared(record.get("contact_email"))[0] is not None:
        withheld.append("email")
    if declared(record.get("contact_mobile"))[0] is not None:
        withheld.append("telephone")
    for name in from_prose:
        if name not in withheld:
            withheld.append(name)
    withheld = sorted(withheld)

    #  `expired` is a boolean and `post_expiry_date` a string, so expiry is
    #  readable from the record and never derived from today's date.
    expired_flag = record.get("expired")

    out = {
        "source": "dziseldra",
        "country": COUNTRY,
        "url": AD + str(rid),
        "id": rid,
        "title": text_of(title) if title else None,
        "employer": employer,
        "employer_declared": employer_state,
        "description": desc,
        "description_contacts_withheld": bool(from_prose),
        "posted": record.get("published_at") or record.get("created_at"),
        "expires": record.get("post_expiry_date"),
        "expired": expired_flag if isinstance(expired_flag, bool) else None,
        "withheld_fields": withheld,
    }

    #  The declaration follows what the redaction ACTUALLY took, and it is only
    #  written when something reaching a PERSON left -- a name does not carry its
    #  class, and this record can also withhold nothing at all. On the 32 records
    #  held on 2026-11-10 it is true on 29, so the branch is not dead here.
    if withheld_a_contact(withheld):
        out["contacts_withheld"] = True

    #  The dates this host really carries, under names that say `tender`.
    for k in VACANCY_DATES:
        v, _ = declared(record.get(k))
        if v is not None:
            out[k] = v

    #  `vacancy_slots` is an integer on 7/16 and means a number of posts.
    slots, _ = declared(record.get("vacancy_slots"))
    if slots is not None:
        out["slots"] = slots

    #  `vacancy_sector` is an integer on 16/16 with SEVEN distinct values and NO
    #  lookup table in this response. An opaque key emitted as a field reads like
    #  a sector; it is recorded as unresolved or not at all.
    sector, _ = declared(record.get("vacancy_sector"))
    if sector is not None:
        out["sector_key_unresolved"] = sector

    #  `OTHER_NATURE` was DEAD CODE until a mutation showed it: neutered to match
    #  nothing, the sweep stayed green, because `parse_record` names its keys one
    #  by one and never filtered. A constant that reads like a guard and guards
    #  nothing is worse than none, so it is asserted here instead of removed --
    #  the keys are OURS, so this can only fire while someone is adding one.
    leaked = sorted(k for k in out
                    if OTHER_NATURE.match(k) or k == "likers"
                    or k.startswith("contact_"))
    if leaked:
        raise ShapeMoved(
            "this record would emit %s -- a column of another nature, the likers "
            "of an advertisement, or a raw contact. This platform shares ONE flat "
            "schema across cars, property, services and vacancies, and `likers` "
            "carries a real person's name, mail, mobile, address and api_token."
            % ", ".join(leaked))
    return out


# ---------------------------------------------------------------- commands

def walk(limit=None, max_pages=50):
    """Pages of the one enumerator, and the THREE possible ends, named.

    Without them a walk cut by the transport reads as a smaller board.
    """
    seen, rows = set(), []
    page, end = 1, "ended of itself"
    while page <= max_pages:
        code, body, _ = get(f"{API}?page={page}")
        if code != 200:
            end = f"cut by the transport (HTTP {code} on page {page})"
            break
        try:
            batch = records_of(body)
        except ShapeMoved as e:
            if page == 1:
                die(f"{e}", EXIT_BROKEN)
            end = f"cut by the shape on page {page}: {e}"
            break
        if not batch:
            end = f"ended of itself (page {page} is empty)"
            break
        fresh = [r for r in batch if r.get("id") not in seen]
        if not fresh:
            end = (f"ended of itself (page {page} repeats page {page - 1} -- the "
                   f"`page` parameter stopped advancing)")
            break
        for r in fresh:
            seen.add(r.get("id"))
            rows.append(r)
            if limit and len(rows) >= limit:
                return rows, f"capped at the requested {limit}", page
        page += 1
    else:
        end = f"capped at {max_pages} pages"
    return rows, end, page


def cmd_list(a):
    rows, end, pages = walk(limit=a.limit, max_pages=a.max_pages)
    if not rows:
        code, body, _ = get(f"{API}?page=1")
        die(empty_first_page("dziseldra", body, what="vacancy record",
                             where=API), EXIT_INDETERMINATE)
    out = []
    for r in rows:
        try:
            out.append(parse_record(r))
        except ShapeMoved as e:
            die(f"{e}", EXIT_BROKEN)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    note(f"{len(out)} vacancy record(s) over {pages} page(s) -- walk {end}")
    #  The size of the board is a claim about the WORLD, so it is only made when
    #  the walk ended of itself. Nothing in this response declares a total.
    if end.startswith("ended of itself"):
        note(f"board size: {len(out)} -- the walk ended of itself, and no field "
             f"of this route declares a total")
    else:
        note("board size: NOT ESTABLISHED -- the walk did not end of itself, and "
             "this route declares no total (bare list, no meta, no links)")
    withheld = sum(1 for r in out if r.get("contacts_withheld"))
    note(f"{withheld}/{len(out)} record(s) had something reaching a person "
         f"removed; `likers` is never read beyond its scale and never emitted")


def cmd_ad(a):
    """One record, by id, taken from the enumerator -- NOT from `/seldra/<id>`.

    The advertisement page adds nothing: 8 of 8 of the long words of the JSON
    `content` appear in it, measured on 59505. Fetching it would spend a request
    on this slow host for a body we already hold the substance of.
    """
    rows, end, _ = walk(max_pages=a.max_pages)
    for r in rows:
        if r.get("id") == a.id:
            json.dump(parse_record(r), sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
            return
    die(f"id {a.id} is not among the {len(rows)} record(s) the enumerator served "
        f"-- walk {end}", EXIT_GONE)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    s = p.add_subparsers(dest="cmd", required=True)

    pl = s.add_parser("list", help="walk the one enumerator")
    pl.add_argument("--limit", type=int, default=None)
    pl.add_argument("--max-pages", type=int, default=50, dest="max_pages")
    pl.set_defaults(fn=cmd_list)

    pa = s.add_parser("ad", help="one record by id, from the enumerator")
    pa.add_argument("--id", type=int, required=True)
    pa.add_argument("--max-pages", type=int, default=50, dest="max_pages")
    pa.set_defaults(fn=cmd_ad)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
