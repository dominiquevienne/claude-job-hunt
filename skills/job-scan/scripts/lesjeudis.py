#!/usr/bin/env python3
"""Les Jeudis (`lesjeudis.com`) — the French IT board whose operator wrote our
own distinction into his rules: `ClaudeBot` is closed BY NAME and `Claude-User`
is opened BY NAME, one line apart. #1128.

**The enumerator is the SITEMAP and not the list's pagination, and that is a
MEASURE and not a preference.** `/offers/` serves a React Server Components
shell: 96 016 bytes, twelve advert links, **zero** `application/ld+json` and
**zero** `JobPosting`. The advert PAGE, by contrast, is rendered server-side.
A verdict taken on the list would have described neither.

**ONE served `ld+json` block carries the advert, and the string
`application/ld+json` occurs TWICE on the page.** The second occurrence is the
same JSON-LD re-queued inside a `self.__next_f` fragment for hydration, as an
ESCAPED JavaScript string literal. So the block is matched by its real TAG —
`<script type="application/ld+json">` — which the escaped copy cannot satisfy:
measured 1 tag against 2 occurrences of the string, on BOTH witnesses. A
page-wide motif for `JobPosting` finds two and would DOUBLE every advert.

**Deduplication is by the identifier and NEVER by the title.** Measured on the
17 269 advert URLs the sitemap declared on 2026-10-31: 17 269 distinct slugs
for **14 129 distinct titles**, so **3 140 advertisements share their title
with another** — one in six. The 8-hex suffix is present on 17 269 of 17 269
and is **unique: zero collisions**; the advert page shows why, its
`identifier.value` being a UUID whose first eight characters ARE that suffix.
So both commands key on it and their rows join.

**No total is declared by the site, and that was measured rather than
assumed**: five motifs of different FORMS, over the raw HTML *and* over the
de-escaped RSC stream, on the list page. So a walk here has **no external
witness**, and this adapter never claims one — a count that comes from our own
extraction is not a witness, and `N short` built on a cap is a figure we
fabricated ourselves.

**The pace is OURS, because nothing targets us.** The rules carry no
`Crawl-delay` for our token, and a file silent on rate promises no absence of
a limit — nine requests in two and a half minutes once raised an interstitial
on another host. This adapter therefore sets its own, and `bin/fetch-body.py`
applies a host's figure whenever a host writes one.

What this adapter does NOT touch: `/offers/*/postuler`, the apply button, the
single refusal that fires on us. It reads as an intention, not as a gap.
"""

import argparse
import datetime
import html
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _robots  # noqa: E402
import _console  # noqa: F401,E402  (patches argparse's writer -- see #1166)

EXIT_BROKEN = 2
EXIT_REFUSED = 7
EXIT_PACED = 9        # the host rate-limited us; NOT a verdict on the board

# The rules live on `www`; the enumerator is declared WITHOUT it, so it is
# another host and it received its own guard (§3 bis). Both were answered by
# `lesjeudis.com` when the guard ran, and that is what `allowed()` reports --
# never assumed from the brand.
HOST = "lesjeudis.com"
ENUM = f"https://{HOST}/sitemap/offre.xml"
LIST = f"https://{HOST}/offers/"

# Our own pace, in seconds, between two requests of one walk. The host writes
# none for us; this is the only figure, so there are not two to disagree.
PACE = 10.0

# `<loc>` in BOTH forms. This file carried no CDATA on 2026-10-31 -- measured,
# zero occurrences -- and a bare `<loc>([^<]+)</loc>` once returned 0 of 467 on
# another board for exactly that reason, so the form is not narrowed to today's
# shape.
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?\s*(.*?)\s*(?:\]\]>)?\s*</loc>",
                 re.S)
LASTMOD = re.compile(r"<lastmod>\s*([^<]+?)\s*</lastmod>")
ENTRY = re.compile(r"<url>(.*?)</url>", re.S)

# The advert's identity. The suffix is unique over the declared set and the
# page's own `identifier.value` is the UUID it truncates.
SLUG_ID = re.compile(r"-([0-9a-f]{8})$")
AD_URL = re.compile(r"^https?://(?:www\.)?lesjeudis\.com/offers/[^/?#]+/?$")

# The block that is SERVED. Anchored on the real tag: the hydration copy is an
# escaped JS string and cannot match this.
SERVED_LD = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)

# A third party's coordinates inside the advert's PROSE. **Only the address
# motif decides here.** A digit rule run on prose fires on an ISO date, a
# European date, a time and an md5 -- and a nine-digit rule once destroyed 113
# of 115 salaries on another board. The description is prose, so no digit rule
# runs on it at all.
ADDRESS = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


def die(msg, code=EXIT_BROKEN):
    print(f"[lesjeudis] {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[lesjeudis] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    v = _robots.allowed(parts.netloc, _robots.full_path(parts))
    if v.get("allowed") is False:
        die(f"refused by the rules of {parts.netloc}: {v.get('rule')!r}",
            EXIT_REFUSED)
    if v.get("allowed") is None:
        die(f"the rules of {parts.netloc} could not be read — INDETERMINATE, "
            f"and an indeterminate is not probed", EXIT_REFUSED)
    return v


def fetch(url):
    """The body, or `(None, error)`, through `bin/fetch-body.py`: it takes the
    guard on the exact URL, declares our identity, tests the HTTP code and
    writes the provenance beside the body."""
    import subprocess
    import tempfile
    gate(url)
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    tool = os.path.join(root, "bin", "fetch-body.py")
    fd, tmp = tempfile.mkstemp(suffix=".body")
    os.close(fd)
    try:
        p = subprocess.run([sys.executable, tool, url, "-o", tmp],
                           capture_output=True, text=True)
        if p.returncode != 0:
            err = (p.stderr or p.stdout).strip()
            # the STATUS comes from the record the tool WRITES, never parsed
            # out of its prose: a message is a property of the run
            status = None
            prov = tmp + ".provenance.json"
            if os.path.exists(prov):
                try:
                    with open(prov, encoding="utf-8") as fh:
                        status = json.load(fh).get("status")
                except ValueError:
                    status = None
            return None, {"status": status, "error": err[:300]}
        with open(tmp, encoding="utf-8", errors="replace") as fh:
            return fh.read(), None
    finally:
        for q in (tmp, tmp + ".provenance.json"):
            if os.path.exists(q):
                os.unlink(q)


def plain(markup):
    """Markup as a reader sees it. Scripts go first: their contents are not
    text, and this board's advert carries eleven RSC fragments."""
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup)
    s = html.unescape(re.sub(r"(?s)<[^>]+>", " ", s))
    return re.sub(r"[\s ]+", " ", s).strip()


def iso_day(value):
    """The HOST's timestamp cut back to its day — never a date we compute.
    `None` when it is absent or does not parse, and the caller NAMES the field
    rather than emitting a null that reads as «this advert has no date»."""
    if not isinstance(value, str):
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", value)
    if not m:
        return None
    try:
        datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None
    return m.group(0)


def entries_of(xml):
    """`(url, lastmod)` per `<url>` of the sitemap, and the pairing is read
    INSIDE each entry: a page-wide zip of two page-wide motifs pairs the Nth
    `<loc>` with the Nth `<lastmod>` and is silently wrong the moment one
    entry omits its date."""
    out = []
    for block in ENTRY.findall(xml):
        loc = LOC.search(block)
        if not loc:
            continue
        lm = LASTMOD.search(block)
        out.append((loc.group(1), lm.group(1) if lm else None))
    return out


def served_ld(markup):
    """`(objects, count_of_served_blocks, count_of_the_string)`.

    The two counts are returned TOGETHER on purpose: their difference is the
    whole mechanism of this board, and a caller that sees only the first
    cannot tell a served advert from a hydration copy."""
    blocks = SERVED_LD.findall(markup)
    objs = []
    for raw in blocks:
        try:
            d = json.loads(raw)
        except ValueError:
            continue
        objs.extend(d if isinstance(d, list) else [d])
    return objs, len(blocks), markup.count("application/ld+json")


def postings_of(markup):
    """The `JobPosting` objects of the SERVED blocks, with the two counts."""
    objs, served, occurrences = served_ld(markup)
    return ([o for o in objs if isinstance(o, dict)
             and o.get("@type") == "JobPosting"], served, occurrences)


def address_of(posting):
    """`jobLocation.address`, whichever of the two shapes the host uses. A
    reader inherited from a neighbouring board returns `None` instead of an
    error, so both shapes are named here rather than one being assumed."""
    jl = posting.get("jobLocation")
    if isinstance(jl, list):
        jl = jl[0] if jl else None
    if not isinstance(jl, dict):
        return {}
    a = jl.get("address")
    return a if isinstance(a, dict) else {}


def board_id_of(posting):
    """The board's own identifier, when it gives one in the shape it used on
    both witnesses. Returns `None` rather than reaching into a string."""
    ident = posting.get("identifier")
    if isinstance(ident, dict) and isinstance(ident.get("value"), str):
        return ident["value"]
    if isinstance(ident, str):
        return ident
    return None


def ledger_id(url, posting=None):
    """`lesjeudis:<8 hex>` — the key BOTH commands emit, so a row from the
    sitemap and a row from the advert page join.

    The title is never part of it: 3 140 of the 17 269 declared adverts share
    their title with another, so a title key collapses one advert in six."""
    m = SLUG_ID.search(url.rstrip("/").rsplit("/", 1)[-1])
    if m:
        return "lesjeudis:" + m.group(1)
    bid = board_id_of(posting or {})
    if bid and re.match(r"^[0-9a-f]{8}", bid):
        return "lesjeudis:" + bid[:8]
    return None


def cmd_list(a):
    body, err = fetch(ENUM)
    if body is None:
        if err.get("status") == 429:
            die("HTTP 429 — rate-limited; not re-probed", EXIT_PACED)
        die(f"{ENUM}: {err.get('error')}")

    entries = entries_of(body)
    if not entries:
        die(f"{ENUM}: no `<url>` entry was read — this says what was NOT read "
            f"and makes no claim about the board")

    rows, seen, offsite, keyless = [], set(), 0, 0
    for url, lastmod in entries:
        if not AD_URL.match(url):
            offsite += 1
            continue
        key = ledger_id(url)
        if key is None:
            keyless += 1
            continue
        if key in seen:
            continue
        seen.add(key)
        rows.append({"source": "lesjeudis", "country": "FR",
                     "ledger_id": key, "url": url,
                     # the sitemap's OWN declaration, kept under its own name:
                     # reading a board moves this field on some hosts, so it
                     # is never promoted to `posted_on_page`
                     "sitemap_lastmod": iso_day(lastmod),
                     # the labelled fields live on the advert's page
                     "body_source": "page"})
        if a.max and len(rows) >= a.max:
            break

    for r in rows:
        print(json.dumps(r, ensure_ascii=False, sort_keys=True))

    note(f"{len(entries)} `<url>` entr(ies) in the enumerator the board "
         f"DECLARES, {len(rows)} row(s) emitted")
    if offsite:
        note(f"{offsite} entr(y/ies) were not advert addresses and were not "
             f"emitted — a path prefix reads as a nature and is not one")
    if keyless:
        note(f"{keyless} entr(y/ies) carried no 8-hex identifier: NAMED, not "
             f"silently dropped, and no title was used in their place")
    note("**this count is the SITEMAP's and it is NOT the board's size.** No "
         "total is declared by the site: five motifs of different forms, over "
         "the raw HTML and over the de-escaped RSC stream of `/offers/`, "
         "returned none on 2026-10-31. So this walk has NO external witness, "
         "and a count that comes from our own extraction is not one. The "
         "figure also MOVES: the same file declared 17 420 entries on "
         "2026-10-12 and 17 269 on 2026-10-31.")
    if a.max and len(rows) >= a.max:
        note(f"the walk ends **capped at --max {a.max}**, not exhausted — and "
             f"no shortfall is reported against the declared figure, because "
             f"the cap is ours and a witness built on it would be one we "
             f"fabricated")
    else:
        note("the walk ends **of its own accord**: every declared entry was "
             "read")
    return 0 if rows else EXIT_BROKEN


def cmd_ad(a):
    if not AD_URL.match(a.url):
        die(f"{a.url}: not a Les Jeudis advert address "
            f"(https://{HOST}/offers/<slug>)")
    body, err = fetch(a.url)
    if body is None:
        if err.get("status") == 429:
            die("HTTP 429 — rate-limited; not re-probed", EXIT_PACED)
        die(f"{a.url}: {err.get('error')}")

    postings, served, occurrences = postings_of(body)
    if served == 0:
        die(f"{a.url}: no `ld+json` block is SERVED in the body — the string "
            f"occurs {occurrences} time(s), which is the hydration copy and "
            f"not an advert. This says what was not read and makes no claim "
            f"about the advert.")
    if not postings:
        die(f"{a.url}: {served} served `ld+json` block(s), none of `@type` "
            f"JobPosting")
    if len(postings) > 1:
        die(f"{a.url}: {len(postings)} served JobPosting objects — the two "
            f"witnesses carried exactly one each, so this shape is unmeasured "
            f"and is not guessed at")

    p = postings[0]
    key = ledger_id(a.url, p)
    addr = address_of(p)
    org = p.get("hiringOrganization")
    org = org.get("name") if isinstance(org, dict) else org
    posted = iso_day(p.get("datePosted"))
    through = iso_day(p.get("validThrough"))
    today = datetime.date.today().isoformat()

    # the advert's PROSE. The address motif decides here, and nothing else
    # does: a withheld field is named only when something was really found.
    desc = p.get("description") if isinstance(p.get("description"), str) else ""
    found = sorted(set(ADDRESS.findall(desc)))
    withheld = ["description.email"] if found else []

    row = {
        "source": "lesjeudis", "country": "FR", "ledger_id": key,
        "url": p.get("url") if isinstance(p.get("url"), str) else a.url,
        "title": p.get("title") if isinstance(p.get("title"), str) else None,
        "organisation": org if isinstance(org, str) else None,
        "locality": addr.get("addressLocality"),
        "postal_code": addr.get("postalCode"),
        "country_code": addr.get("addressCountry"),
        "posted_on_page": posted,
        "valid_through": through,
        "board_id": board_id_of(p),
        "direct_apply": p.get("directApply"),
        "description_chars": len(plain(desc)),
        "withheld_fields": withheld,
        # the mechanism, carried in the row so a reader can see it was obeyed
        "page_served_ld_blocks": served,
        "page_ld_string_occurrences": occurrences,
    }
    if through:
        row["expired"] = through < today
        row["expired_against"] = today
    else:
        row["expired"] = None
        row["expired_against"] = None

    print(json.dumps(row, ensure_ascii=False, sort_keys=True))

    if occurrences > served:
        note(f"the string `application/ld+json` occurs {occurrences} time(s) "
             f"for {served} block(s) actually SERVED: the surplus is the same "
             f"JSON-LD re-queued in a `self.__next_f` fragment for hydration. "
             f"A page-wide motif would have emitted this advert twice.")
    if withheld:
        note(f"{len(found)} address(es) found in the advert's prose and "
             f"WITHHELD — the field is named because something was really "
             f"found, and the name disappears when nothing is")
    if row["expired"]:
        note(f"this advert's `validThrough` is {through} and the enumerator "
             f"still declares it: the row is emitted WITH its date, never "
             f"dropped")
    if row["expired"] is None:
        note("`validThrough` is absent or unparsable: `expired` is null and "
             "NAMED, never a false `false`")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    li = sub.add_parser("list", help="the adverts the declared sitemap carries")
    li.add_argument("--max", type=int, default=0,
                    help="stop after N rows; the cap is OURS and no shortfall "
                         "is reported against it")
    d = sub.add_parser("ad", help="one advert by its URL")
    d.add_argument("--url", required=True)
    a = p.parse_args()
    return {"list": cmd_list, "ad": cmd_ad}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
