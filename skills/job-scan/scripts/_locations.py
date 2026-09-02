#!/usr/bin/env python3
"""One city, three labels — the shared comparison every adapter needs.

Boards write the same city several ways in the same result set. Measured
2026-09-02, issue #65:

    Kuala Lumpur, Kuala Lumpur                          58 cards
    Kuala Lumpur, Federal Territory of Kuala Lumpur     16
    Kuala Lumpur, Wilayah Persekutuan Kuala Lumpur      12   → one city, 86

    Hanoi, Hanoi                                        19
    Hanoi, Ha Noi                                        3
    Hanoi, Hà Nội                                        2   → one city, 24

Comparing the whole string by equality loses **between a fifth and a third of
a capital's volume**, silently, with a plausible count and no error. And the
Vietnamese case adds a dimension Malaysia's did not: `Ha Noi` and `Hà Nội` are
the same city and are not the same string.

Bogotá is the sharpest measurement of the two conditions together. On 103
cards:

| Test | Recovered |
| :-- | --: |
| whole string, exact | 17% |
| first segment only | 51% |
| **first segment, diacritics folded** | **100%** |

**Neither condition works without the other.** Hence one helper, imported
rather than copied — `stepstone.py` had the right implementation and a private
copy of it, which is how a rule becomes a habit in one file and a bug in ten.

Usage from a sibling script in this directory:

    from _locations import city_key, matches_city, drop_report
"""

import re
import unicodedata

__all__ = ["fold", "city_key", "matches_city", "drop_report"]


def fold(text):
    """Casefold, strip diacritics, squeeze punctuation to single spaces.

    `Hà Nội` → `ha noi`; `Zürich` → `zurich`; `Bogotá, D.C.` → `bogota d c`.
    """
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^0-9a-z]+", " ", text.casefold()).strip()


def city_key(location_text):
    """The part of a location string that identifies the city.

    The first comma-separated segment. Everything after it is an
    administrative suffix that varies by language and by feed — *Kuala
    Lumpur* is the city; *Wilayah Persekutuan Kuala Lumpur* is one of three
    ways this board spells the territory around it.
    """
    first = (location_text or "").split(",")[0]
    return fold(first)


def matches_city(location_text, wanted):
    """Does this row's location name the city asked for?

    Both sides are reduced to `city_key`, and a containment test in either
    direction catches *Ho Chi Minh City* against *Ho Chi Minh*. It is
    deliberately generous: on this data the failure that costs is the missed
    match, not the extra one, and the extra one is visible to a reader while
    the missed one is not.
    """
    if not wanted:
        return True
    got, want = city_key(location_text), fold(wanted)
    if not got or not want:
        return False
    return got == want or want in got or got in want


def drop_report(rows, wanted, location_of=lambda r: r.get("location_text")):
    """Filter by city and return (kept, dropped, the labels that were dropped).

    **Point 4 of the rule: where a city filter drops rows, say how many.** A
    count of what was excluded turns a silent loss into a visible one, and the
    distinct labels are what reveal a variant nobody had seen.
    """
    kept, dropped, labels = [], 0, {}
    for row in rows:
        where = location_of(row)
        if matches_city(where, wanted):
            kept.append(row)
        else:
            dropped += 1
            labels[where] = labels.get(where, 0) + 1
    return kept, dropped, labels
