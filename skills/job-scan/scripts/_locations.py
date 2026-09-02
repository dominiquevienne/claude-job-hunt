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

WHAT THIS CANNOT DO, AND WILL NOT BE MADE TO DO. Folding reconciles *Zürich*
with *Zurich*. **It will never reconcile `Tel Aviv` with `Tel Aviv-Yafo`,
because that is not a variation on a name — it is a different name for the
same place.** Measured on 239 Israeli cards, 2026-09-02: Tel Aviv appears **78
times under eight labels and three names** — the usual name, the municipality's
official one, and an anglicised one — so a count grouped by label reads **45%**
where the city's real share is 90%.

**No character rule reaches it.** Knowing that two names denote one city is
not computed, it is declared — and a declaration table is not written here, on
purpose:

- **It never stops growing**, and an incomplete one looks complete. That is
  the class `shared/plausible-and-false.md` exists for: corrected in the
  entries somebody thought of, uncorrected elsewhere, and indistinguishable
  from the outside.
- **The obvious cheap rule is wrong in a direction that destroys
  information.** `X City → X` would cover the Philippine cases (*Makati City*,
  *Taguig City*, *Pasig City*) in three lines — and it would fold **Quebec City
  into a province, Mexico City and Panama City and Guatemala City and Kuwait
  City into countries.** *(Reasoned from place names, not measured in this
  corpus — but the counter-examples have to be excluded before the rule is
  written, and they are not hard to find.)*
- **And nothing here is a search problem.** A candidate searching Tel Aviv
  receives all 78 cards, because the query is compared against the label and
  not normalised into one. **Only a measurement is affected, and the honest fix
  for a measurement is to say what it measures.**

So a share computed over these labels is a **label concentration**, not the
city's — and **which of the two naive divisions you used decides whether it is
a bound at all.** Nothing in this repository computes one; this is the rule for
whoever publishes it:

| Divide the dominant label by | Error |
| :-- | :-- |
| **every card of the market** | **always low — an honest lower bound.** Taipei reads 24% where the city holds 58% |
| the cards *sharing its first segment* | **no bound in either direction.** Tel Aviv reads **90%** where the city's share is **45%** — 35 of 39, because the other 39 cards of the same city were dropped from the denominator too |

**The second one amputates the denominator as well as the numerator**, which is
exactly how it climbs above the truth. **Only the first may be called a lower
bound**, and the caveat belongs in the name rather than a footnote (#67, #85).

*(The Taipei and Tel Aviv figures come from the country surveys of 2026-09-02
and are recorded here, not measured here.)*

AND THE PROBLEM IS BOUNDED MORE NARROWLY THAN IT LOOKS. Across **38 country
samples and 13 750 city labels**, covering ten writing systems — Arabic,
Cyrillic, Han, Hangul, Thai, Hebrew, Bengali, Georgian, Sinhala and Tamil,
Urdu — there is **not one non-Latin alphabetic character**. Seoul is never
서울; Moscow is never Москва.

**That is a property of the field, not a pattern of some countries:
romanisation is applied upstream, to the whole corpus.** *(Method note: Unicode
classes `á`, `ü` and `ḩ` as Latin, so the test measures the writing system and
not the diacritics — which is what makes the result usable.)*

**That is true of the aggregated corpus and false of this tool**, and the
difference is the whole point:

> A normalisation whose only input is the international corpus will never have
> to transliterate — it will only have to reconcile **Latin variants of a
> romanisation somebody else already did, and did several ways**: `Zhubei`
> against `Jhubei`, `Tel Aviv` against `Tel Aviv-Yafo`. **The moment a national
> board feeds the same table, transliteration is the problem again, because
> national sources keep their own script.**

**The native characters exist; they simply never reach the aggregator's
field.** `104.com.tw` shows `新北市中和區`; Taiwan's public service shows
`高雄市 / 前鎮區`; `ikman.lk` publishes in English, Sinhala and Tamil. An
adapter reading those boards receives Han, Sinhala and Tamil. **Carrying the
aggregated population's property over to the source population is the same
faulty join this repository keeps catching, in the other direction.**

**And the two halves of the tool have opposite problems**, which is more
interesting than either:

- **The international corpus**: the romanisation was done for us, across
  everything, **and we do not know how.** Taipei's five region labels, Doha's
  five spellings, `Zhubei` against `Jhubei` are **the scars of that invisible
  work** — we inherit the result without the procedure, and it cannot be
  redone, because the original is gone.
- **A national board**: the original is right there. The native script and its
  administrative hierarchy — 市, 區 — are intact, **so it is deduplicable
  properly**, and a transliteration remains to be done.

**The day two adapters feed one place table, the two meet**: a damaged
romanisation whose original has disappeared, and an intact original that has to
be romanised.

*(Recorded from the country surveys of 2026-09-02. The first version of this
paragraph said transliteration would never be needed; that was measured on the
aggregator's labels and stated of the tool.)*

**One more reason this helper does not audit itself.** The metric that found
the Israeli case had also *missed* it for weeks, because it grouped labels by
first segment — **the same way this file compares them.** A check that shares
its object's blind spot agrees with it by construction; see *blind agreement*
in `shared/never-fail-silently.md`.

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
