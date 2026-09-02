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
            continue
        for obj in (d if isinstance(d, list) else [d]):
            if isinstance(obj, dict) and isinstance(obj.get("@graph"), list):
                out += [x for x in obj["@graph"] if isinstance(x, dict)]
            elif isinstance(obj, dict):
                out.append(obj)
    return out


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
    unreadable = []
    for b in raw:
        try:
            json.loads(b, strict=False)
        except ValueError as e:
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
        return Absence(
            "no-jobposting",
            f"{len(raw)} ld+json block(s) parsed and none is a JobPosting. "
            f"That is a real answer about this page, not a reading failure.",
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
