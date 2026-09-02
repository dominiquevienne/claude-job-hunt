#!/usr/bin/env python3
"""Which rows in a result page actually match what was asked?

**Issue #62.** A board's reported total is not a match count, and a full page
of cards is not a page of matches. Measured 2026-09-02 across nine StepStone
domains, from the platform's own decomposition of its own total:

    stepstone.nl  "software developer"        26 reported —   1 main,  25 semantic
    stepstone.be  "software developer"       607 reported — 110 main, 497 semantic
    totaljobs     "software developer" London 1862 reported — 796 regional

**`stepstone.nl` holds one Dutch "software developer" ad and still serves a
full page of 25 cards.** Nothing in the markup distinguishes the other 24 —
same component, same position, same feed. **The padding is heaviest exactly
where the board is thinnest**, which is the worst possible place for it.

LinkedIn does the same thing on a *zero-result* search, with suggestion cards
(#46). Neither board marks the padding. Assume more do and have not been
caught.

WHY THIS LIVES HERE AND NOT IN ONE ADAPTER. `stepstone.py` had the only
implementation, and its own comment says why that is a problem: keeping a rule
private "is how a rule becomes a habit in one script and a bug in ten" (#65,
the city-folding lesson). The test needs nothing but the card's own title and
town, so any adapter that knows what was searched for can apply it.

**IT IS A LITERAL TEST AND IT IS WRONG IN KNOWN WAYS.** Only `literal` is
asserted; the other two keep their question marks:

- **Another language.** A Dutch title under an English search reads as padding
  even when it is the job — *Medewerker Klantenservice* against "customer
  service" is a real match this rejects.
- **The keyword in the description, not the title.** Common, and it reads as
  padding.
- **A location field naming the region rather than the town.** Reads as
  regional.

So the marker is a *lead for the reader*, never a filter: nothing is dropped on
its verdict, and `shared/plausible-and-false.md` is why — a test that is wrong
in three known directions must not silently remove rows.

    from _match import classify, share
    row["match"], row["match_reason"] = classify(row.get("title"),
                                                 row.get("location_text"),
                                                 keyword, location)
    …
    note(share(rows))
"""

from _locations import fold, matches_city

__all__ = ["classify", "share"]


def flatten(text):
    """Padded and folded, so ` term ` matches a whole word and not a prefix."""
    return " " + fold(text) + " "


def classify(title, location_text, keyword, location):
    """Mark ONE card from the card's own words. Returns `(match, reason)`.

    `literal` is the only assertion. `regional?` and `semantic?` are questions,
    because the test above is wrong in three known ways.
    """
    t = flatten(title)
    where = flatten(location_text)
    if location:
        # `matches_city` compares the first segment with diacritics folded, so
        # "Zürich, Zurich, CH" and "Zurich, Zurich, CH" — both live on one page
        # of results — do not land on opposite sides of the test (#65).
        if not matches_city(location_text, location) and fold(location) not in where:
            return "regional?", (f"the card's location does not contain "
                                 f"'{location}'")
    if keyword:
        terms = [x for x in flatten(keyword).split() if len(x) > 2] \
            or flatten(keyword).split()
        missing = [x for x in terms if f" {x} " not in t]
        if missing:
            return "semantic?", ("the title does not contain "
                                 + ", ".join(missing))
    return "literal", None


def share(rows, key="match"):
    """The sentence a sweep prints when part of its page was padding.

    **A run that produced mostly padding should say so while it is happening**,
    not leave it for whoever reads the ledger next week.
    """
    total = len(rows)
    if not total:
        return None
    counts = {}
    for r in rows:
        counts[r.get(key)] = counts.get(r.get(key), 0) + 1
    literal = counts.get("literal", 0)
    if literal == total:
        return None                     # nothing to say, so nothing is said
    parts = ", ".join(f"{n} {k}" for k, n in sorted(counts.items(),
                                                    key=lambda kv: -kv[1]))
    pct = round(100 * (total - literal) / total)
    return (f"{total - literal} of {total} rows ({pct}%) did not literally "
            f"match what was asked — {parts}. **A board's reported total is "
            f"not a match count** (issue #62), and these are marked rather "
            f"than dropped: the test is wrong on another language, on a "
            f"keyword that lives in the description, and on a location field "
            f"naming a region. Read them; do not trust the count.")
