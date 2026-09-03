#!/usr/bin/env python3
"""Read a page's `application/ld+json`, and say which half failed when it
does not work.

**Eighteen scripts here extract `ld+json`. Four passed `strict=False`. Two
boards need it.** Issue #76.

WHAT WAS MEASURED, 2026-09-02, ON 27 LIVE AD PAGES ACROSS NINE BOARDS:

    michaelpage.ch     0/3 parsed with a bare json.loads, 3/3 with strict=False
    a Chilean service  0/5 bare, 5/5 with strict=False
    adecco, crit, hays, infoempleo, randstad.fr    30/30 blocks parsed bare
    persigo, randstad.ch, sozialinfo               21/21 blocks parsed bare

So the deviation is **real and not universal**: two boards of ten need the
argument, and three of the four scripts that already pass it do not need it
today. That is the honest shape of it, and it is still worth doing everywhere:

**the flag costs nothing, and its absence costs the whole ad, silently.**
Every call site sits inside `try: … except: continue`, so an unparseable block
is skipped and the script goes on to report a board with no structured data.
Same asymmetry as `_robots.py`: between inventing a permission and inventing a
refusal, only one of the two errors announces itself.

THE OTHER DEVIATION IS NOT IN THE PARSER AT ALL, AND IT IS THE COMMONER ONE.

`randstadfr.py` documents a site that writes `<script type='application/ld+json'>`
with **single quotes**. Nothing reaches the parser: the extraction pattern
matches nothing, and the adapter reports `json_ld: false` on every ad — a total
failure wearing the face of "this board publishes no structured data".

**Ten of the eighteen patterns in this repository demand `type="` with double
quotes** (adecco, batiactu, digitalrecruiters, hellowork, icims, jobbkk,
jobology, meteojob, stepstone, taleez) and three of the tolerant eight lack
`re.I`. Each one is that same outage waiting for a board to change its
punctuation. **Quote style is not a contract. Match the attribute, not the
punctuation around it.**

AND THE THIRD FAILURE IS A SENTENCE. When a page contains "JobPosting" and no
block parsed, the fact is **a failure to read, here**. `crit.py` and
`randstadfr.py` say so; `hays.py` said only "contains 'JobPosting' but no
ld+json block parsed", which reads as the board's fault. `absent_reason()`
exists so the difference is a value, not a habit.

Usage:

    from _ldjson import postings, absent_reason

    jp = next(iter(postings(page)), None)
    if jp is None:
        reason = absent_reason(page)
        if reason.our_fault:
            die(f"{url}: {reason.text}")
        return {"json_ld": False, ...}
"""

import json
import re

__all__ = ["LD", "blocks", "objects", "postings", "absent_reason", "Absence",
           "one", "label"]

# **Attribute-agnostic, quote-agnostic, case-insensitive**, in that order of
# importance. It matches `type="application/ld+json"`, `type='…'`, an unquoted
# attribute, `LD+JSON`, and the attribute appearing after others on the tag.
LD = re.compile(r"<script[^>]*application/ld\+json[^>]*>(.*?)</script>",
                re.S | re.I)


def one(value):
    """The first object of a schema.org field, whatever shape it arrived in.

    **schema.org permits a value to be an object, a list of objects, or a bare
    string, and boards use all three for the same field.** A reader that writes
    `(d.get("jobLocation") or {}).get("address")` is correct until the day an
    ad has two sites, and then it raises — or worse, on a string, it raises on
    a field nobody was watching.

    Measured 2026-09-01 on HelloWork: `experienceRequirements` arrives as a
    plain string on some ads and `educationRequirements` as a **list**, and
    `--with-detail` aborted the whole sweep with
    `AttributeError: 'str' object has no attribute 'get'` (issue #57). The same
    shape had already been fixed in `icims.py`, privately, when `jobLocation`
    turned out to be a list — **the second time is what makes it a helper.**

    Returns `{}` for a string, for `None`, and for a list with no object in it,
    so `one(x).get("name")` is always legal. **A string is not silently turned
    into a name**: use `label()` when the field may legitimately be text.
    """
    if isinstance(value, list):
        value = next((x for x in value if isinstance(x, dict)), None)
    return value if isinstance(value, dict) else {}


def label(value, key="name"):
    """The readable text of a field that may be a string, an object, or a list.

    `employmentType` is `"FULL_TIME"` on one board and `{"name": "CDI"}` on the
    next; `educationRequirements` is a sentence here and a credential object
    there. **Returning the string when there is one is not a fallback, it is
    the common case** — and it is the half `one()` deliberately drops.
    """
    if isinstance(value, list):
        parts = [label(v, key) for v in value]
        return ", ".join(p for p in parts if p) or None
    if isinstance(value, dict):
        v = value.get(key)
        return v if isinstance(v, str) else (str(v) if v is not None else None)
    if isinstance(value, str):
        return value.strip() or None
    return str(value) if value is not None else None


def blocks(html):
    """Every `ld+json` block's raw text, in page order."""
    return [m.group(1) for m in LD.finditer(html or "")]


def objects(html):
    """Every JSON value in the page's `ld+json`, flattened.

    `strict=False` is passed on the one call site this repository has, so a
    literal newline inside a string — invalid JSON, and what Michael Page and
    the Chilean service both publish — parses instead of losing the ad.
    `@graph` is unwrapped, because a board that uses it is not a board without
    a JobPosting.
    """
    out = []
    for b in blocks(html):
        try:
            d = json.loads(b, strict=False)
        except ValueError:
            # **`strict=False` covers literal control characters and nothing
            # else.** A lone backslash is a different malformation, and it
            # needs its own repair. Issue #127.
            try:
                d = json.loads(_repair(b), strict=False)
            except ValueError:
                continue
        for obj in (d if isinstance(d, list) else [d]):
            out += _unwrap(obj)
    return out


# A backslash that does not begin a valid JSON escape. The specimen:
# `jobivoire.ci` publishes `d\&#039;Atelier` — an apostrophe HTML-escaped
# **after** being JSON-escaped, so the JSON carries `\&`, which is not an
# escape sequence and which `strict=False` does not forgive.
_BAD_ESCAPE = re.compile(r'\\(?!["\\/bfnrtu])')


def _repair(text):
    """Make a lone backslash literal so the block parses. Issue #127.

    **One malformation, named, with the site it was measured on** — not a
    general attempt to fix JSON. Anything this does not repair still fails,
    still reaches `absent_reason()`, and is still reported as `our_fault`.

    **Two occurrences on two continents suggest a class rather than an
    accident**: a publisher that escapes once too often. Michael Page and the
    Chilean service put a literal newline inside a string, which is why
    `strict=False` is passed at all; `jobivoire.ci` puts an HTML entity behind
    a backslash. **Both are one escaping layer too many**, and the next one
    will be seen faster for having a name.

    **This does not silence anything.** A block recovered here is still a
    block that arrived broken, and `repairs()` says how many so a caller can
    report it. The guard that caught this — `absent_reason()` with
    `our_fault=True` — did its job on two independent sessions the same
    evening, and **a fix that recovered the twelve advertisements by turning
    that warning off would be a regression, not a repair.**
    """
    return _BAD_ESCAPE.sub(r"\\\\", text)


def repairs(html):
    """How many `ld+json` blocks parsed only after repair.

    For a caller that wants to say so. **A page whose structured data needs
    mending is a page to watch**, and the number belongs in the run's output
    rather than in this module's silence.
    """
    n = 0
    for b in blocks(html):
        try:
            json.loads(b, strict=False)
        except ValueError:
            try:
                json.loads(_repair(b), strict=False)
                n += 1
            except ValueError:
                pass
    return n


def _unwrap(obj):
    """One block may hold many objects, in three standard containers.

    `@graph` is the usual one. **`ItemList` / `itemListElement` is the one a
    listing page uses** — jobup's search results carry twenty `JobPosting`
    objects that way, and a reader that only unwrapped `@graph` saw **zero**
    on a page holding twenty. Both are schema.org containers, so unwrapping
    them belongs here rather than in whichever adapter meets them first.
    """
    if not isinstance(obj, dict):
        return []
    if isinstance(obj.get("@graph"), list):
        out = []
        for x in obj["@graph"]:
            out += _unwrap(x)
        return out
    # **`mainEntity` is the third container, and it nests.** `jobivoire.ci`
    # publishes a `CollectionPage` whose `mainEntity` is an `ItemList` of
    # twelve `JobPosting`s — so a reader that unwraps `itemListElement` only
    # at the top level sees **one** object on a page holding twelve. Issue
    # #127, and the same shape as the `ItemList` case one level down.
    if isinstance(obj.get("mainEntity"), (dict, list)):
        inner = obj["mainEntity"]
        out = []
        for x in (inner if isinstance(inner, list) else [inner]):
            out += _unwrap(x)
        return out
    if isinstance(obj.get("itemListElement"), list):
        out = []
        for entry in obj["itemListElement"]:
            if isinstance(entry, dict):
                out += _unwrap(entry.get("item") if "item" in entry else entry)
        return out
    return [obj]


def postings(html):
    """Just the schema.org JobPostings."""
    return [o for o in objects(html) if o.get("@type") == "JobPosting"]


class Absence:
    """Why there is no JobPosting, and whose problem it is.

    `our_fault` is the whole point: a page that says JobPosting and yields
    none has been misread **here**, and that deserves a loud exit rather than
    a row saying the board publishes nothing.
    """

    __slots__ = ("kind", "text", "our_fault")

    def __init__(self, kind, text, our_fault):
        self.kind, self.text, self.our_fault = kind, text, our_fault

    def __repr__(self):
        return f"<Absence {self.kind} our_fault={self.our_fault}>"


def absent_reason(html):
    """Called only when `postings()` came back empty."""
    html = html or ""
    raw = blocks(html)
    unreadable, mended = [], 0
    for b in raw:
        try:
            json.loads(b, strict=False)
        except ValueError as e:
            # **The same two attempts `objects()` makes, in the same order.**
            # A diagnosis that parsed differently from the reader would
            # report a page unreadable while the reader was reading it — the
            # two must agree about the same block. Issue #127.
            try:
                json.loads(_repair(b), strict=False)
                mended += 1
            except ValueError:
                unreadable.append(str(e))
    if unreadable:
        return Absence(
            "unparseable",
            f"{len(unreadable)} of {len(raw)} ld+json block(s) did not parse "
            f"even with strict=False ({unreadable[0][:80]}). **This is a "
            f"failure to read the page, not a board without structured "
            f"data** — do not trust any count from this run.",
            True)
    if raw:
        mend = (f" {mended} of them parsed only after repairing an invalid "
                f"escape (#127), which is worth knowing about this page even "
                f"though it did not stop the reading." if mended else "")
        return Absence(
            "no-jobposting",
            f"{len(raw)} ld+json block(s) parsed and none is a JobPosting. "
            f"That is a real answer about this page, not a reading "
            f"failure.{mend}",
            False)
    if "JobPosting" in html:
        return Absence(
            "extraction",
            "the page contains 'JobPosting' and no ld+json block was "
            "extracted at all. **The markup changed and the reader missed "
            "it** — check the script tag's attributes and its quote style "
            "before believing any count from this run.",
            True)
    if len(html) < 2000:
        return Absence(
            "short-page",
            f"no ld+json, and the page is only {len(html)} characters — too "
            f"short to be an ad. A wall or a redirect is likelier than an "
            f"empty board.",
            True)
    return Absence(
        "absent",
        "no ld+json block and no mention of JobPosting: this page carries no "
        "structured data.",
        False)
