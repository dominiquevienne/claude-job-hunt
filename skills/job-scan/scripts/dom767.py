#!/usr/bin/env python3
"""DOM767 — Jobs, Vacancies in Dominica (`www.dom767.com`): the jobs section
of «Dominica's #1 Online Community». #735.

**THE BOARD STATES ITS OWN SIZE AND THE CARD SAID IT DID NOT.** The list page
embeds FacetWP's own configuration, and its pager block declares
`page · per_page · total_rows · total_rows_unfiltered · total_pages` —
**2 468 rows over 494 pages of 5** when read on 2026-10-31. *The card and the
issue both recorded «no count stated»; that was true of the visible page and
false of the page's own payload.*

**AND THAT TOTAL IS NOT THE DOMINICA COUNT.** The page carries a facet whose
label is literally «Hide Jobs Not In Dominica», implemented as a checkbox list
of LOCATIONS (`data-value="roseau"`, ten choices). `total_rows` equals
`total_rows_unfiltered`, so no facet is applied: the figure counts every job
the site holds, wherever it is. *A count names a SIZE and never a NATURE —
this one is emitted as `declared_unfiltered` and never as the board's size.*

**THE WALK STOPS AT THE FIRST PAGE, AND THE REASON IS MEASURED RATHER THAN
ASSUMED.** Two routes were tried:

```
?_paged=2         200, the pager reports "page":2 — and the five rows OVERLAP
                  page 1 by THREE of five. Page 1 re-read two minutes later is
                  byte-stable in its rows, so the order is not unstable: the
                  parameter reaches FacetWP without advancing the template's
                  own query. **It is not an enumerator.**
/api-json/facetwp/v1/refresh   the endpoint FacetWP itself declares (the site
                  rewrites `wp-json` to `api-json`, which is why a motif for
                  the usual path finds nothing). POST with the page's nonce →
                  **403 `rest_cookie_invalid_nonce`, «Cookie check failed»**:
                  the nonce is bound to a cookie set when the page is served.
```

*A 403 on an API is a technical entry condition and not a verdict on the board
(owner's decision of 2026-09-04, #100), and neither of these is a refusal by
the publisher: they are limits of ROUTE (§2 sexies).* **So `list` emits the
five rows it can read and NAMES the ending — `capped`, with what sits behind
it — because without that word a capped read looks like a smaller board.**

**THE ADVERTISEMENT PAGE IS WHERE THIS BOARD IS RICH, AND ALSO WHERE IT
EXPOSES A PERSON.** 204 371 bytes of markup render 5 568 characters of text
carrying a labelled block: `Company:`, `LOCATION:`, `DEADLINE:`,
`Qualification:`, `EXPERIENCE:`, `Career Level:`, `Number of Vacancies:`,
`Monthly Salary Range:`, `Contract Length:`, `Company Type:`,
`Job Role/Speciality:` — **and `Contact Person Name:` and
`Contact Person Email:`, inside the advertisement's own block.** *The sibling
Malawi board measured zero contacts inside its block; this one puts one there,
so «the block is clean» is a fact about a board and never about a family.*

**THE AMBIGUITY TWO LABELS SHOWED WAS A PROPERTY OF THE MEASUREMENT'S
SCOPE AND NEVER OF THE BOARD, AND THAT IS WHY THIS READS THE CONTAINER.** On
the whole page `Posted:` and `Industry:` occur FOUR times each, so neither
could bound anything; **inside the advertisement's own container all SEVENTEEN
labels occur EXACTLY ONCE** — the repetitions belong to the sibling cards
outside it. *The container is not inferred either: the markup names its end
itself, `<!-- .entry-header /-->`, and the region is 4 916 characters where the
page is 204 371.*

**And label and value share an element pair, in TWO forms — measured, because a
form read on one member is not the form of the family.** `<h4>L</h4><p>V</p>`
for fifteen of them, `<strong>L</strong><span>V</span>` for the header row's
`Posted:`, `Company:` and `Industry:`. *A single form generalised from
`Company:` would have rendered nothing on fourteen labels.* **`Posted:` is
emitted as what it is: «20 Hours ago», a RELATIVE stamp and not a date.**

**AGE AND GENDER ARE READ AND NEVER EMITTED.** The block carries `Age:` and
`Gender:` as selection criteria. #183 settled the shape: we keep serving the
advertisement and we do not propagate the criterion. *They are listed in
`page_dropped_criteria` so that the silence is declared rather than looking
like a board that does not publish them.*

**THE DEADLINE IS AN EXPIRY AND IT HAD ALREADY PASSED ON THE SPECIMEN.**
`DEADLINE: 30 th OCT, 2026`, read 2026-10-31 — yesterday — on an advertisement
served on page 1. *The row is EMITTED with its date and never dropped
(`shared/never-fail-silently.md`, #1226): the consumer cannot un-drop what it
never received.* **Second board in two days where the collection is not
filtered on expiry, measured independently.**

**THE PACE IS THE HOST'S, NOT OURS: it writes `Crawl-delay: 3`.** Nothing here
sets a pace of its own — `bin/fetch-body.py` reads the host's and applies it,
and inventing a second one beside it is how two numbers come to describe one
quantity.

    dom767.py list
    dom767.py ad --url https://www.dom767.com/job/<slug>/

*Measured 2026-10-31 09:09–09:14 UTC by the declared client, the guard taken
on each exact path in a turn of its own, `bin/fetch-body.py` throughout.*
"""

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _robots  # noqa: E402
import _console  # noqa: F401,E402  (patches argparse's writer -- see #1166)

EXIT_BROKEN = 2
EXIT_REFUSED = 7
EXIT_PACED = 9        # the host rate-limited us; NOT a verdict on the board

HOST = "www.dom767.com"
LIST = f"https://{HOST}/jobs-dominica/all-vacancies-jobs-dominica/"

# The pager's own figures, embedded in FacetWP's configuration. The anchor
# carries the START OF THE VALUE and not just the name: this page also *talks*
# about its facets, and a bare `pager` matches in several places.
PAGER = re.compile(r'"pager":\s*(\{[^}]*\})')

# The rows of the pager, by the anchor of their CONTAINER. A page-wide motif
# for `/job/<slug>/` finds each row TWICE — the title and the «View Details»
# link — so a count taken on it is a count of links and not of advertisements.
ROW = re.compile(r'<a class="job-single-view" href="([^"]+)"')

# The advertisement's own container, bounded by the comment the markup writes
# itself. Everything below is read INSIDE it: the page carries sibling job
# cards with the same labels, and a count taken on the page is a count of the
# page's cards and not of this advertisement's fields.
HEADER = re.compile(r'class="entry-header(.*?)\.entry-header /-->', re.S)

# Label and value share an element pair, in TWO forms. Both are closed by a
# real tag, so neither needs a terminator invented for it.
PAIR = re.compile(r"<(strong|h4)>\s*([^<]+?)\s*</\1>\s*<(span|p)>(.*?)</\3>",
                  re.S)

# Every label the container carries, VERBATIM as the page writes them, mixed
# case included.
AD_LABELS = ("Posted:", "Company:", "Industry:", "Qualification:",
             "Company Type:", "LOCATION:", "Job Role/Speciality:",
             "EXPERIENCE:", "Career Level:", "DEADLINE:",
             "Number of Vacancies:", "Monthly Salary Range:", "Age:",
             "Contract Length:", "Gender:", "Contact Person Name:",
             "Contact Person Email:")

# What is read and deliberately NOT emitted — #183: we keep serving the
# advertisement, we do not propagate the criterion.
DROPPED = ("Age:", "Gender:")

# What is withheld as a third party's: an address is unambiguous, and a name
# given as a contact is a person. The digit motif never runs on a field whose
# sense is a DATE or a SALARY — a nine-digit rule once destroyed 113 of 115
# salaries on another board, and this block carries `Monthly Salary Range:`.
ADDRESS = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"\+?\d[\d\s().-]{6,}\d")
CONTACT_LABELS = ("Contact Person Name:", "Contact Person Email:")
SENSE_KNOWN = ("DEADLINE:", "Monthly Salary Range:", "Number of Vacancies:",
               "EXPERIENCE:", "Posted:", "Age:")

MONTHS = {m: i for i, m in enumerate(
    ("jan feb mar apr may jun jul aug sep oct nov dec").split(), 1)}
# `30 th OCT, 2026` — the ordinal suffix is a separate word on this board.
DEADLINE = re.compile(r"(\d{1,2})\s*(?:st|nd|rd|th)?\s*([A-Za-z]{3,9})[,.]?\s*(\d{4})")


def die(msg, code=EXIT_BROKEN):
    print(f"[dom767] {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[dom767] {msg}", file=sys.stderr)


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
    """The body, or `(None, error)`. The host writes `Crawl-delay: 3` and
    `bin/fetch-body.py` applies it: no pace is set here, because two numbers
    describing one quantity is how they come to disagree."""
    import subprocess
    import tempfile
    gate(url)
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    tool = os.path.join(root, "bin", "fetch-body.py")
    fd, tmp = tempfile.mkstemp(suffix=".html")
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
    """The page as the READER sees it — 204 371 bytes of an advertisement
    render 5 568 characters of text, so the block is matched in the TEXT.
    Scripts go first: their contents are not text, and leaving them in puts
    two hundred kilobytes of code between a label and its value."""
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup)
    s = html.unescape(re.sub(r"(?s)<[^>]+>", " ", s))
    return re.sub(r"[\s ]+", " ", s).strip()


def iso_deadline(value):
    """The HOST's date, reformatted — never computed by us. `None` when it
    does not parse, and the caller NAMES the field rather than emitting a null
    that reads as «this advertisement has no deadline»."""
    m = DEADLINE.search(value or "")
    month = MONTHS.get(m.group(2)[:3].lower()) if m else None
    if not month:
        return None
    return "%04d-%02d-%02d" % (int(m.group(3)), month, int(m.group(1)))


def pairs_of(markup):
    """The container's label/value pairs, and THREE distinct silences, each
    named apart.

    **A label is read only where it occurs exactly ONCE inside the
    container.** Measured on this board: seventeen labels, seventeen pairs,
    every count one — and on the whole page two of them occur four times,
    which is why the container is the unit and not the document.

    *The three silences are disjoint by construction, and collapsing any two
    of them would put a different fact under one name:* **absent** — the
    container does not carry the label at all, which is what a redesign looks
    like; **ambiguous** — it carries it several times, so it bounds nothing
    and resolving it by picking an occurrence is how a field comes to carry
    the card next to it; **unpaired** — the label is there once and its value
    is not in the element pair we read, which says the markup moved.
    """
    m = HEADER.search(markup)
    if not m:
        return None, [], [], []
    region = m.group(1)
    once, absent, ambiguous = {}, [], []
    for lab in AD_LABELS:
        n = len(re.findall(re.escape(lab), region))
        if n == 0:
            absent.append(lab)
        elif n > 1:
            ambiguous.append("%s x%d" % (lab.rstrip(":"), n))
        else:
            once[lab] = True
    got = {}
    for _tag, lab, _vtag, value in PAIR.findall(region):
        lab = lab.strip()
        if once.get(lab):
            got[lab] = plain(value)
    unpaired = sorted(l for l in once if l not in got)
    return got, ambiguous, sorted(absent), unpaired


def declared_pager(markup):
    """FacetWP's own pager figures, or `None`.

    *The page embeds its configuration with the quotes escaped, so the blob is
    read on the UNESCAPED text — a motif written for the rendered form finds
    nothing here, and its zero would read as «the board states no count».*
    """
    m = PAGER.search(markup.replace('\\"', '"'))
    if not m:
        return None
    try:
        p = json.loads(m.group(1))
    except ValueError:
        return None
    return {k: p.get(k) for k in
            ("page", "per_page", "total_rows", "total_rows_unfiltered",
             "total_pages")}


def cmd_list(a):
    body, err = fetch(LIST)
    if body is None:
        if err.get("status") == 429:
            die("HTTP 429 — rate-limited; not re-probed", EXIT_PACED)
        die(f"{LIST}: {err.get('error')}")
    rows = []
    seen = set()
    for url in ROW.findall(body):
        if url not in seen:
            seen.add(url)
            rows.append({"source": "dom767", "country": "DM",
                         "ledger_id": "dom767:" + url.rstrip("/").rsplit("/", 1)[-1],
                         "url": url,
                         # the list card carries a title and a type; the
                         # LABELLED fields live on the advertisement's page,
                         # and this says so rather than emitting empties
                         "body_source": "page"})
    pager = declared_pager(body)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False, sort_keys=True))
    if pager:
        note(f"the board DECLARES {pager['total_rows']} row(s) over "
             f"{pager['total_pages']} page(s) of {pager['per_page']} in its "
             f"own pager — **and that figure is UNFILTERED**: the page carries "
             f"a «Hide Jobs Not In Dominica» facet over locations, and "
             f"`total_rows` equals `total_rows_unfiltered`, so it counts every "
             f"job the site holds wherever it is. It is NOT this board's size.")
    else:
        note("the page states no pager figures — a count that is ABSENT, not a "
             "count of zero")
    note(f"{len(rows)} row(s) emitted, and the walk ends **capped**: "
         f"`?_paged=2` reports page 2 and returns five rows OVERLAPPING page 1 "
         f"by three, so it does not advance the query and is not an "
         f"enumerator; the route FacetWP declares "
         f"(`/api-json/facetwp/v1/refresh`) answers 403 "
         f"`rest_cookie_invalid_nonce` to a nonce not accompanied by its "
         f"cookie. Neither is a refusal by the publisher — both are limits of "
         f"ROUTE, and this adapter follows neither.")
    return 0 if rows else EXIT_BROKEN


def cmd_ad(a):
    if not re.search(r"^https?://(www\.)?dom767\.com/job/[^/]+/?$", a.url):
        die(f"{a.url}: not a DOM767 advert address "
            f"(https://{HOST}/job/<slug>/)")
    body, err = fetch(a.url)
    if body is None:
        if err.get("status") == 429:
            die("HTTP 429 — rate-limited; not re-probed", EXIT_PACED)
        die(f"{a.url}: {err.get('error')}")
    got, ambiguous, absent, unpaired = pairs_of(body)
    if got is None:
        die(f"{a.url}: the advertisement's container was not found "
            f"(`.entry-header`) — this says what was NOT read and makes no "
            f"claim about the advertisement")
    text = plain(body)

    inspected, withheld, dropped, vals = [], [], [], {}
    for lab in sorted(got):
        inspected.append(lab.rstrip(":"))
        # **A contact label is withheld WHATEVER its value**, and before any
        # motif is consulted: `Contact Person Email:` is a person's address by
        # the page's own label, and a motif that happened not to match it
        # would publish it.
        if lab in CONTACT_LABELS:
            withheld.append(lab.rstrip(":"))
            continue
        if lab in DROPPED:
            dropped.append(lab.rstrip(":"))
            continue
        if ADDRESS.search(got[lab]):
            withheld.append(lab.rstrip(":"))
            continue
        if lab not in SENSE_KNOWN and PHONE.search(got[lab]):
            withheld.append(lab.rstrip(":"))
            continue
        vals[lab] = got[lab]

    expiry = iso_deadline(vals.get("DEADLINE:"))
    today = time.strftime("%Y-%m-%d", time.gmtime())
    title = text.split(" – DOM767")[0].strip() or None
    row = {
        "source": "dom767",
        "country": "DM",
        "ledger_id": "dom767:" + a.url.rstrip("/").rsplit("/", 1)[-1],
        "url": a.url,
        "title": title,
        "organisation": vals.get("Company:") or None,
        "employer_kind": vals.get("Company Type:") or None,
        "locality": vals.get("LOCATION:") or None,
        "industry": vals.get("Industry:") or None,
        "role": vals.get("Job Role/Speciality:") or None,
        "qualification": vals.get("Qualification:") or None,
        "experience": vals.get("EXPERIENCE:") or None,
        "career_level": vals.get("Career Level:") or None,
        "vacancies": vals.get("Number of Vacancies:") or None,
        "salary": vals.get("Monthly Salary Range:") or None,
        "contract_length": vals.get("Contract Length:") or None,
        # **Emitted with its date and never dropped** — #1226. `None` when
        # there is nothing to compare, never False.
        "valid_through": expiry,
        "expired": None if expiry is None else expiry < today,
        "expired_against": today if expiry is not None else None,
        # RELATIVE, and said so: «20 Hours ago» is not a date, and calling
        # it `posted` would put a stamp we cannot resolve where consumers
        # expect one we can.
        "posted_relative": vals.get("Posted:") or None,
        "body_source": "page",
        "contacts_exposed": bool(withheld),
        "page_inspected": sorted(inspected),
        "page_withheld": sorted(withheld),
        "page_dropped_criteria": sorted(dropped),
    }
    unparsed = ["DEADLINE"] if "DEADLINE:" in vals and expiry is None else []
    for key, value in (("page_unparsed", unparsed),
                       ("page_labels_absent", absent),
                       ("page_unpaired_labels", unpaired),
                       ("page_ambiguous_labels", ambiguous)):
        if value:
            row[key] = sorted(value)
    print(json.dumps(row, ensure_ascii=False, sort_keys=True))
    if row["page_withheld"]:
        note(f"withheld as a third party's: {', '.join(row['page_withheld'])} "
             f"— this board puts a contact INSIDE the advertisement's block, "
             f"which its Malawi sibling does not")
    if row["page_dropped_criteria"]:
        note(f"read and deliberately NOT emitted: "
             f"{', '.join(row['page_dropped_criteria'])} — #183: we keep "
             f"serving the advertisement and we do not propagate the criterion")
    if row["expired"]:
        note(f"this advertisement EXPIRED on {expiry} and the list still "
             f"serves it: the row is emitted WITH its date, never dropped")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="the advertisements the first page serves")
    d = sub.add_parser("ad", help="one advertisement by its URL")
    d.add_argument("--url", required=True)
    a = p.parse_args()
    return {"list": cmd_list, "ad": cmd_ad}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
