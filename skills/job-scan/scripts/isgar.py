#!/usr/bin/env python3
"""ISGAR (`isgar.com.tm`) — a Turkmen job board that publishes its own pager, and whose contacts sit in NAMED fields AND in free text at once.

  isgar.py list [--limit N] [--max-pages N] [--no-sitemap]
  isgar.py page --n <page number>

THE HOST PUBLISHES ITS PAGER, SO THE WITNESS IS NOT OUR EXTRACTION

`/vacancies?page=N` is a Next.js server-component page whose RSC payload carries
`{"data": [...], "meta": {"page": N, "limit": 18, "total": T, "totalPages": 23}}`
— **four numbers in EVERY response** (measured 2026-10-06 03:17–03:2x UTC). Page 1
returned 18 advertisements, page 23 returned 16, and page 99 — outside the
declared 23 — returned an honestly EMPTY list rather than a 404 or a silent fall
back to page one. Page 2 is **0 of 18 in common** with page 1.

    page 1    18 adverts   meta.total 406
    page 23   16 adverts   meta.total 412     <- moved by six in three minutes
    page 99    0 adverts   meta.total 406

**So `total` carries its minute, and the walk prints the value it actually read
rather than one remembered from the first page.** *A prediction computed on a
denominator that has already moved accuses a healthy board: 412 − 22×18 = 16 is
exact, and my own «10» came from 406.*

THE DECLARED SITEMAP IS AN INDEPENDENT SECOND ENUMERATION — 2 534 `<loc>`, of
which **407 under `/vacancies`** for the 406 the payload declares, the list page
making the 407th. *This repository had not yet seen a declared sitemap confirm an
API count, so `list` prints the two side by side.* The locale multiplier there is
×2 and not ×4 (812 `/vacancies/<uuid>` URLs, each advert under `/vacancies/` and
`/ru/vacancies/`) and it dedups by UUID.

THE DESCRIPTIONS ARE RSC REFERENCES, AND ONLY SOME RESOLVE IN THE BODY SERVED.
`description` and `descriptionTm` do not hold text in the `data` objects: they hold
`"$3e"`, `"$3f"` — references to chunks the stream defines elsewhere as
`3e:T4eb,<the text>`, where `T<hex>,` is the chunk's kind and length. **Measured on
page 1: 21 distinct references, of which 8 are defined in the same body and 13 are
not** (`3f`, `40`, … `46`).

  -> so a reference is RESOLVED only when the body defines it **as a TEXT chunk**,
     and the field is OMITTED otherwise. *A table built from every `^<id>:` line
     resolved one description to a slab of the payload's own JSON and leaked a
     `latitude`/`longitude` pair into a record. **The floor is positive twice
     over: a value enters the table only if it carries the `T<hex>,` prefix, AND
     only the DECLARED number of characters is taken** — the stream puts
     everything on one line, so «to end of line» read 77 434 characters for a
     chunk declaring 1 259.* **Emitting `"$3f"` as a description would publish a wire
     reference as prose** — the same fabrication as emitting a placeholder as an
     employer — and `list` prints how many resolved against how many did not, so
     the gap is declared rather than silent.

CONTACTS ARE IN NAMED FIELDS **AND** IN FREE TEXT, AND THIS IS THE FIRST BOARD OF
ITS CLUSTER WHERE BOTH ARE TRUE. Measured on the 18 of page 1:

    company.phone        +993 on 18 of 18      a NAMED field, every advert
    company.email        an e-mail on 10 of 18 a NAMED field
    contactPhones        key present on 13     a NAMED field, conditional
    description          +993 on 6 of 18       FREE TEXT
    descriptionTm        +993 on 6 of 18       FREE TEXT

**So the named fields are DROPPED and the free text is SCRUBBED — two different
remedies, because a field whose MEANING is known is removed rather than filtered,
and prose cannot be removed without removing the advertisement.**

`showContacts` IS THE POSTER'S CONSENT AND NEVER A PERMISSION FOR US. It is true
on 13 of 18 and the `contactPhones` key is present on 13 of 18, **the two
agreeing on 18 of 18** — so it predicts exactly where a contact exists. It is
carried as a fact and it decides nothing: a phone is withheld whether or not the
poster agreed to display it.

AND `withheld_fields` IS DERIVED FROM WHAT WAS ACTUALLY FOUND AND IS ABSENT WHEN
NOTHING WAS. Five of the 18 carry no `contactPhones` key at all; a record naming
it as withheld there would lie about our own discretion in the one direction no
guard outside this file can check.

THE DIGIT RULE TOUCHES ONLY THE NAMED TEXT FIELDS, AND THAT IS NOT A DETAIL.
`company.brandBannerUrl` and `company.userId` both match «eight anchored digits»
— the shape of a Turkmen number — while one is a URL path fragment and the other
the first block of a UUID. *Applying the rule to them would destroy the
identifier, exactly as a non-anchored rule destroyed 314 of 314 advert ids on a
Madrid board.* So `SCRUBBED` is a POSITIVE list of fields to pass through the
scrubber, never a blanket pass over the record, and `ids`, `number`, `userId`,
`logoUrl`, `brandBannerUrl` and the five dates are not in it.

COORDINATES ARE DROPPED. `latitude` and `longitude` are present on 1 of the 18;
the record carries the location's NAME and its region and never a coordinate.

WHAT THE 41 FIELDS HOLD, measured one at a time on the 18 (present / non-empty /
real): `id` `number` `headline` `headlineTm` `description` `descriptionTm`
`salaryType` `showSalary` `employmentType` `workSchedule` `status` `viewsCount`
`expiresAt` `publishedAt` `createdAt` `updatedAt` at 18/18/18; `salaryFrom`
18/13/13 and `salaryTo` 18/10/10, so ranges and single values both; `labels`
present on 18 and **never filled**; `location` present on **17** and not 18;
`languageRequirements` on 4; `isPremium` and `isRemotePossible` real on **0**.
*Three MODERATION fields travel in the public payload — `rejectedAt`,
`rejectionReasonCode`, `rejectionReasonText`, None on all 18 — so the board ships
its internal schema; they are not emitted.*

THE RULES: 580 bytes, `Allow: /`, one `Disallow: /api/`, one sitemap, no
`Crawl-delay` — so our own 2 s floor applies. `/api/` is refused in writing and
the refusal costs only images: the 15 `/api/` paths the page references are all
`/api/v1/uploads/files/…`, logos and thumbnails, so the DATA route is not there.
**And the rules file argues its own reasoning in Russian, naming `middleware.ts`:
`/applicant`, `/employer`, `/login`, `/register` and `/forgot-password` are
deliberately NOT blocked but serve `X-Robots-Tag: noindex`, because blocking in
robots.txt would leave the URL in results without content.** *So this host
distinguishes, in writing, «do not index» from «do not fetch» — and this adapter
fetches none of those paths anyway.* Guard taken on every exact path in turns
distinct from the retrievals and exercised both ways: five open with `rule=None`,
three refused by `/api/`. Measured 2026-10-06 (#669).
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
from _sitemap import locs as sitemap_locs
from _ua import UA
from _zero import empty_first_page

HOST = "isgar.com.tm"
BASE = "https://isgar.com.tm"
LIST = BASE + "/vacancies?page={page}"
SITEMAP = BASE + "/sitemap.xml"

# NAMED contact fields. **Dropped, not scrubbed** — a field whose meaning is known
# is removed rather than filtered. `company.*` are reached through the sub-object.
CONTACT_FIELDS = ("contactPhones",)
CONTACT_FIELDS_COMPANY = ("phone", "email")

# The POSITIVE list of fields the scrubber may touch. Everything else — ids,
# numbers, UUIDs, URLs, dates — is never passed through it, because
# `company.userId` and `company.brandBannerUrl` both match an eight-digit run.
SCRUBBED = ("description", "descriptionTm")
SCRUBBED_COMPANY = ("description", "descriptionTm")

# Never emitted: a coordinate is not a place name.
COORDS = ("latitude", "longitude")

# Turkmen numbers are eight digits; the run is ANCHORED so that a UUID block or a
# URL fragment of the same length cannot be mistaken for one.
MAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TEL_RE = re.compile(r"(?:\+\s?993[\s\-()]*)?(?<!\d)\d{8}(?!\d)|\+\s?993[\s\-()\d]{4,}")
MSG_RE = re.compile(r"(?i)\b(?:whats?app|telegram|viber|imo)\b[\s:：]*[+\d][\d\s\-()]{5,}")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[isgar] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # the host writes no Crawl-delay — our own floor


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xml;q=0.9",
        "Accept-Language": "tk,ru;q=0.8,en;q=0.5"})
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


PUSH_RE = re.compile(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', re.S)


def payload(body):
    """The RSC payload, **decoding each push on its own and concatenating after**.

    *Concatenating the literals first and decoding once fails on this host with
    `Invalid \\escape`: an escape sequence straddles two pushes. Decoding per
    push costs one line and the other way loses the whole payload.*
    """
    out = []
    for lit in PUSH_RE.findall(body):
        try:
            out.append(json.loads('"' + lit + '"'))
        except ValueError:
            continue                      # one unreadable chunk is not the document
    return "".join(out)


def envelope(pl):
    """`{"data": [...], "meta": {...}}` found by walking BACK from `"meta":{"page"`
    to the enclosing balanced object.

    *The anchor is the STRUCTURE and not a key name: `"showContacts"` matched the
    page's i18n help dictionary, and `"total"` holds the WORD «Umumy iş
    tejribesi: {duration}» in that same dictionary. On a fully localised site a
    key name is as likely to belong to the translation table as to the data.*
    """
    m = re.search(r'"meta":\s*\{"page":\s*\d+', pl)
    if not m:
        return None
    depth = 0
    for d in range(m.start(), -1, -1):
        if pl[d] == "}":
            depth += 1
        elif pl[d] == "{":
            if depth == 0:
                inner = 0
                for j in range(d, len(pl)):
                    if pl[j] == "{":
                        inner += 1
                    elif pl[j] == "}":
                        inner -= 1
                        if inner == 0:
                            try:
                                return json.loads(pl[d:j + 1])
                            except ValueError:
                                return None
                return None
            depth -= 1
    return None


CHUNK_RE = re.compile(r"(?m)^([0-9a-f]{1,4}):(.*)$")
REF_RE = re.compile(r"^\$([0-9a-f]{1,4})$")
# `T<hex>,` — the kind and the DECLARED LENGTH of a text chunk, in characters.
TEXT_CHUNK_RE = re.compile(r"^T([0-9a-f]+),")


def chunks(pl):
    """The payload's TEXT chunks only: `{id: text}`.

    **The floor is POSITIVE.** An RSC text chunk is written `<id>:T<hex>,<text>`;
    a DATA chunk is written `<id>:[…]` or `<id>:{…}`. A table built from every
    `^<id>:<value>` line resolved a description to a slab of the payload's own
    JSON — `"isActive":true,…,"latitude":37.96665317634351,…` — and that leaked a
    COORDINATE into a record. *The bug was introduced by the fix that resolved
    references at all: before it the field held `"$3e"`, which was wrong and
    harmless.*

    So only a value carrying the `T<hex>,` prefix enters, and a reference that
    points at anything else comes back UNRESOLVED rather than as prose.
    """
    out = {}
    for ident, value in CHUNK_RE.findall(pl):
        m = TEXT_CHUNK_RE.match(value)
        if not m:
            continue
        want = int(m.group(1), 16)
        body = value[m.end():][:want]
        # **The chunk declares its own length, so the length decides where it
        # ends — not the end of the line.** The stream puts everything on ONE
        # line, so «to end of line» took 77 434 characters for a chunk declaring
        # 1 259 and published a slab of the payload's own JSON as a description,
        # coordinates included. A slice that does not reach the declared length
        # is a truncated stream and is refused.
        if len(body) == want:
            out.setdefault(ident, body)
    return out


def resolve(value, table):
    """`(text, status)` where status is one of `plain`, `resolved`, `unresolved`.

    **A `$<id>` is a wire REFERENCE and not text.** When the body served defines
    it, the text comes back; when it does not — 13 of 21 on page 1 — the caller
    omits the field rather than publishing the reference. *Emitting `"$3f"` as a
    description would be the placeholder-as-employer fabrication in a new place.*
    """
    if not isinstance(value, str) or not value.strip():
        return None, "plain"
    m = REF_RE.match(value.strip())
    if not m:
        return value, "plain"
    got = table.get(m.group(1))
    return (got, "resolved") if got else (None, "unresolved")


def scrub(s):
    """Free text with its contacts replaced. **Only the fields in `SCRUBBED` and
    `SCRUBBED_COMPANY` ever reach this.**"""
    if not isinstance(s, str) or not s.strip():
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    s = MSG_RE.sub("[messaging contact withheld]", s)
    s = TEL_RE.sub("[telephone withheld]", s)
    return re.sub(r"[ \t]+", " ", htmlmod.unescape(s)).strip() or None


def held(value):
    """**A field PRESENT is not a field FILLED, and `if x` cannot tell them
    apart.** A list counts only if it holds something non-blank; a string only if
    it is not blank and not a wire sentinel."""
    if value is None:
        return False
    if isinstance(value, str):
        v = value.strip()
        return bool(v) and v.lower() not in ("undefined", "null", "none") and not v.startswith("$")
    if isinstance(value, (list, tuple)):
        return any(held(x) for x in value)
    if isinstance(value, dict):
        return any(held(x) for x in value.values())
    if isinstance(value, bool):
        return value
    return bool(value)


def place(loc):
    """The location's NAME and region — never a coordinate, and never the
    administrative tree's internal ids."""
    if not isinstance(loc, dict):
        return None, None
    return (loc.get("name") or None), (loc.get("region") or None)


def company(raw, table=None):
    """The employer, with its NAMED contact fields removed and its prose
    scrubbed. Returns `(dict, withheld)` where `withheld` names only the fields
    that actually HELD a value."""
    if not isinstance(raw, dict):
        return None, []
    withheld = [f"company.{k}" for k in CONTACT_FIELDS_COMPANY if held(raw.get(k))]
    out = {"name": raw.get("name") or None,
           "verified": bool(raw.get("isVerified")),
           "anonymous": bool(raw.get("isAnonymous")),
           "website": raw.get("website") or None}
    for k in SCRUBBED_COMPANY:
        txt, _ = resolve(raw.get(k), table or {})
        v = scrub(txt)
        if v:
            out[k] = v
    return out, withheld


def record(ad, table=None):
    table = table if table is not None else {}
    co, withheld = company(ad.get("company"), table)
    withheld += [k for k in CONTACT_FIELDS if held(ad.get(k))]
    name, region = place(ad.get("location"))
    ident = str(ad.get("id") or "").strip() or None
    out = {
        "source": "isgar", "country": "TM",
        "ledger_id": f"isgar:{ident}" if ident else None, "id": ident,
        "number": ad.get("number"),
        "url": f"{BASE}/vacancies/{ident}" if ident else None,
        "title": (ad.get("headline") or None), "title_tm": (ad.get("headlineTm") or None),
        "employer": co,
        "place": name, "region": region,
        # 13 of 18 filled, 10 of 18 with an upper bound — both carried as read
        "salary_from": ad.get("salaryFrom") or None,
        "salary_to": ad.get("salaryTo") or None,
        "salary_type": ad.get("salaryType") or None,
        "salary_shown": bool(ad.get("showSalary")),
        "employment_type": ad.get("employmentType") or None,
        "work_schedule": ad.get("workSchedule") or None,
        "experience_level": ad.get("experienceLevel") or None,
        "languages": ad.get("languageRequirements") or None,
        "remote": bool(ad.get("isRemotePossible")),
        "nationwide": bool(ad.get("isNationwide")),
        "status": ad.get("status") or None,
        "views": ad.get("viewsCount"), "applications": ad.get("applicationsCount"),
        "posted": ad.get("publishedAt") or None,
        "expires": ad.get("expiresAt") or None,
        "updated": ad.get("updatedAt") or None,
        # the POSTER's consent, carried as a fact and deciding nothing here
        "poster_shows_contacts": bool(ad.get("showContacts")),
    }
    unresolved = []
    for k in SCRUBBED:
        txt, status = resolve(ad.get(k), table)
        if status == "unresolved":
            unresolved.append(k)
            continue                     # never publish a wire reference as prose
        v = scrub(txt)
        if v:
            out[k if k == "description" else "description_tm"] = v
    if unresolved:
        # **Declared, not silent**: the body served did not define these chunks.
        out["unresolved_fields"] = sorted(unresolved)
    # **Derived, and ABSENT when the set is empty** — see the module docstring.
    if withheld:
        out["withheld_fields"] = sorted(set(withheld))
    return out


def th(n):
    return f"{n:,}".replace(",", " ")


def one_page(n):
    code, body = get(LIST.format(page=n))
    if code != 200:
        die(f"{LIST.format(page=n)}: HTTP {code}", EXIT_PARTIAL)
    pl = payload(body)
    env = envelope(pl)
    if env is None:
        die(f"page {n}: the RSC payload carries no `meta` envelope. "
            "**This says what THIS tool did not find, not what the host does not serve.**",
            EXIT_PARTIAL)
    data = env.get("data")
    if not isinstance(data, list):
        die(f"page {n}: `data` is {type(data).__name__}, not a list", EXIT_PARTIAL)
    return data, (env.get("meta") or {}), chunks(pl)


def cmd_list(a):
    rows, seen, pages, meta = [], set(), 0, {}
    n = 1
    while True:
        data, meta, table = one_page(n)
        pages += 1
        if not data and n == 1:
            die(empty_first_page("isgar", "", "advertisement", where=LIST.format(page=1)),
                EXIT_PARTIAL)
        for ad in data:
            r = record(ad, table)
            if r["id"] and r["id"] in seen:
                continue
            if r["id"]:
                seen.add(r["id"])
            rows.append(r)
        total_pages = meta.get("totalPages") or 1
        if a.max_pages and pages >= a.max_pages:
            end = f"capped by --max-pages at {pages} of {total_pages}"
            break
        if n >= total_pages or not data:
            end = "walked to the last page the host declares" if n >= total_pages else "a page came back empty"
            break
        n += 1
    for r in (rows[:a.limit] if a.limit else rows):
        print(json.dumps(r, ensure_ascii=False))
    total = meta.get("total")
    note(f"{th(len(rows))} emitted over {pages} page(s) of {meta.get('limit')} — "
         f"the host declares total {th(total) if isinstance(total, int) else total} "
         f"and totalPages {meta.get('totalPages')}; {end}.")
    if isinstance(total, int) and len(rows) != total and not a.max_pages:
        note(f"{th(len(rows))} emitted against {th(total)} declared — "
             f"{th(abs(total - len(rows)))} apart. **`total` moved by six in three minutes when "
             "this was measured, so a gap of a few is the board changing under the walk and a "
             "large one is ours.**")
    unres = sum(1 for r in rows if r.get("unresolved_fields"))
    note(f"{th(len(rows)) if False else len(rows) - unres} record(s) carry a resolved description and "
         f"{unres} do not: their `description` is an RSC REFERENCE the body served does not define, "
         "and the field is OMITTED rather than filled with `$<id>`. **8 of 21 references resolved "
         "when this was measured.**")
    held_count = sum(1 for r in rows if r.get("withheld_fields"))
    note(f"{held_count} of {th(len(rows))} record(s) name a withheld field; the rest held none, "
         "and say nothing. **`showContacts` is the poster's consent and decides nothing here.**")
    if a.no_sitemap:
        return
    code, xml = get(SITEMAP)
    if code != 200:
        note(f"{SITEMAP}: HTTP {code} — no second enumeration this run.")
        return
    listed = {u.strip() for u in sitemap_locs(xml, contains="/vacancies/")}
    note(f"the declared sitemap lists {th(len(listed))} `/vacancies/<uuid>` URL(s) — "
         "**a ×2 locale multiplier, each advert under `/vacancies/` and `/ru/vacancies/`**, so "
         f"it dedups to about {th(len(listed) // 2)} and that is a SECOND enumeration of the "
         "same store, not a confirmation of this one.")


def cmd_page(a):
    data, meta, table = one_page(a.n)
    for ad in data:
        print(json.dumps(record(ad, table), ensure_ascii=False))
    note(f"page {a.n}: {len(data)} advertisement(s); the host says {meta}.")
    if not data:
        note("an empty list on a page the host still answers 200 for: outside the declared "
             "`totalPages` this board returns an honestly EMPTY page rather than a 404.")


def main():
    p = argparse.ArgumentParser(
        description="ISGAR (Turkmenistan) — the host publishes {page, limit, total, totalPages} "
                    "in every response and honours ?page=N; contacts live in NAMED fields AND in "
                    "free text, so the first are dropped and the second scrubbed.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every advertisement the host's pager declares, 2 s apart")
    s.add_argument("--limit", type=int)
    s.add_argument("--max-pages", type=int, help="stop after N pages")
    s.add_argument("--no-sitemap", action="store_true", help="skip the second enumeration")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("page", help="one page, as the host serves it")
    d.add_argument("--n", type=int, required=True)
    d.set_defaults(fn=cmd_page)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
