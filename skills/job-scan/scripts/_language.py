#!/usr/bin/env python3
"""Which language to ask a market in — from measurements, never from a
dictionary.

**The case (issue #70).** On Adzuna's Swiss index, 2026-09-02: `Entwickler`
returns 12 691 and `développeur` returns **0**. `job-scan` builds its search
terms from the user's own profile, so a French-speaking user is served French
terms, and a French term on a German-leaning index returns an empty market
that has twelve thousand jobs in it — HTTP 200, no error.

`_zero.py` makes that zero speak. **This module is what it can say next.**

THREE RULES, AND EACH ONE IS A REFUSAL TO GUESS.

**1. The market's languages come from a map; the user's come from the user.**
Measuring the language of the ads already read cannot help here — *the search
returned nothing, so there is nothing to measure*. The map has to be primary
because the fallback is circular exactly where it is needed.

But the market's languages are not the answer on their own. **A German search
on a Swiss board returns German ads, which mostly require German.** Handing
12 691 of them to somebody who does not speak German replaces a misleading zero
with a misleading flood, and they sort it out by hand. So the third source is
the person: `languages.working` in their config, which setup already collects.

**The rule is therefore: search the market's languages THAT THE PERSON WORKS
IN, and *say* what the others return.** Not hide the German market, not pour it
out. On this case that is one sentence — *your French search returns 0; the
same market returns 12 691 in German, which you have not declared* — and the
person decides. Giving somebody what they need to steer is the whole point of
a person-driven agent (issue #48).

**2. The table records measurements, not translations.** "This term returned N
on this market on this date" is checkable and refutable. "`développeur`
translates to `Entwickler`" is neither, and it ages without saying so (issue
#72).

*How to read a measurement:* **an entry is worth its order of magnitude and its
zero, and nothing finer.** 138 this morning and 129 this afternoon are the same
measurement — the index moves during a day. 12 691 and 0 are not. **Do not
refresh an entry for a 7% drift**; refresh it when a term that returned
thousands returns none, or the reverse.

**3. A term that is not in the table produces silence.** Not a guessed
translation. A guessed translation that also returns zero manufactures a second
zero, and two zeros read as a certainty — one that was invented here. **Finding
no equivalent is information; inventing one is not.**

WHAT THIS MODULE DOES NOT COVER, said plainly because the gap is real:

- **A thin result is as misleading as an empty one, and nothing here fires on
  it.** `informaticien` returns **129 of the Swiss index's 81 516 ads** — 1% of
  the market, and not zero, so `_zero.py` stays quiet and this module is never
  reached. The trigger is strict on purpose (issue #70 is about not lying, not
  about recall), but the step is there and this is where it is.
- **The category route does not fix it either.** Adzuna's 30 tags are shared
  across countries and do return every language of the market — but **70.7% of
  the Swiss index is `category=unknown`**, and `category=it-jobs` returns 1 150
  ads where `what=Entwickler` alone returns 12 691. Measured 2026-09-02.

Everything above was measured against the live API on **2026-09-02**.
"""

__all__ = ["MARKET_LANGUAGES", "MEASURED", "market_languages", "speaks_codes",
           "alternatives", "language_note"]

# The markets whose job ads are genuinely published in more than one language.
# **Short on purpose.** A country absent from this map is not a monolingual
# country — it is a country nobody has measured here, and inventing a row would
# be the guess this module exists to refuse.
#
# The order inside a row is by weight of speakers, and it is **not** a ranking
# of job-ad volume: on Adzuna's Swiss index German outweighs French by about
# a hundred to one for developer ads, which is far past any population ratio.
MARKET_LANGUAGES = {
    "be": ("nl", "fr", "de"),
    "ca": ("en", "fr"),
    "ch": ("de", "fr", "it"),   # Romansh is official and carries no job ads
    "es": ("es", "ca", "eu", "gl"),
    "fi": ("fi", "sv"),
    "lu": ("fr", "de", "lb"),
}

# Language names as a person writes them in `languages.working`, mapped to the
# codes used above. A value the map does not recognise is dropped and named by
# the caller rather than guessed at.
NAMES = {
    "en": ("english", "anglais", "englisch"),
    "fr": ("french", "français", "francais", "französisch"),
    "de": ("german", "allemand", "deutsch", "swiss german", "suisse allemand"),
    "it": ("italian", "italien", "italiano", "italienisch"),
    "nl": ("dutch", "néerlandais", "neerlandais", "nederlands", "flemish",
           "flamand"),
    "es": ("spanish", "espagnol", "español", "espanol", "castilian",
           "castellano"),
    "ca": ("catalan", "català"),
    "eu": ("basque", "euskara"),
    "gl": ("galician", "galego", "galicien"),
    "fi": ("finnish", "finnois", "suomi"),
    "sv": ("swedish", "suédois", "suedois", "svenska"),
    "lb": ("luxembourgish", "luxembourgeois", "lëtzebuergesch"),
    "pt": ("portuguese", "portugais", "português"),
}


class Term:
    """One measurement: this term, on this market, returned this many, then.

    It is not a claim about a language. It is a claim about a request, and it
    can be re-run.
    """

    __slots__ = ("lang", "term", "count", "on", "board")

    def __init__(self, lang, term, count, on, board):
        self.lang, self.term, self.count = lang, term, count
        self.on, self.board = on, board

    def __repr__(self):
        return (f"{self.term!r} ({self.lang}) → {self.count} on {self.board}, "
                f"{self.on}")


# **The table.** One market, one concept, four terms — because that is what has
# been measured. It is meant to grow one measurement at a time, and a row
# nobody ran does not belong in it.
#
# The concept key is a label for grouping, and it is the one human judgement
# here: it says "these terms were tried for the same kind of work", not "these
# words are translations of each other".
MEASURED = {
    ("ch", "software-development"): (
        Term("de", "Entwickler", 12691, "2026-09-02", "adzuna"),
        Term("en", "developer", 3162, "2026-09-02", "adzuna"),
        Term("fr", "informaticien", 129, "2026-09-02", "adzuna"),
        Term("fr", "développeur", 0, "2026-09-02", "adzuna"),
    ),
}


def _fold(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", (s or "").strip().lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def market_languages(market):
    """The languages a market's ads are written in, or () if unmeasured."""
    return MARKET_LANGUAGES.get((market or "").lower(), ())


def speaks_codes(values):
    """`languages.working` as codes, plus whatever could not be read.

    Returns `(codes, unrecognised)`. **Nothing is guessed**: a value that
    matches no name is handed back so the caller can say so.
    """
    codes, unknown = [], []
    for v in values or ():
        f = _fold(v)
        hit = next((c for c, names in NAMES.items()
                    if any(f == n or f.startswith(n + " ") or
                           f.startswith(n + "(") for n in map(_fold, names))),
                   None)
        if hit and hit not in codes:
            codes.append(hit)
        elif not hit:
            unknown.append(v)
    return tuple(codes), tuple(unknown)


def alternatives(term, market, speaks=()):
    """Other measured terms for the same kind of work on the same market.

    Split into what the person can use and what they cannot, because those are
    two different sentences and only one of them is an instruction.
    """
    key = _fold(term)
    speaks = tuple(speaks or ())
    for (mkt, concept), terms in MEASURED.items():
        if mkt != (market or "").lower():
            continue
        if not any(_fold(t.term) == key for t in terms):
            continue
        others = [t for t in terms if _fold(t.term) != key]
        return {
            "concept": concept,
            "reachable": [t for t in others
                          if not speaks or t.lang in speaks],
            "out_of_reach": [t for t in others
                             if speaks and t.lang not in speaks],
        }
    # **Silence, deliberately.** Nobody measured this term on this market, and
    # a guessed translation that also returns zero would manufacture a second
    # zero — two zeros read as a certainty.
    return {"concept": None, "reachable": [], "out_of_reach": []}


def language_note(term, market, speaks=()):
    """What to add to a zero, or None when there is nothing measured to say."""
    langs = market_languages(market)
    alt = alternatives(term, market, speaks)
    if not langs and not alt["concept"]:
        return None
    out = []
    if langs:
        out.append(f"Ads on {market.upper()} are published in "
                   f"{', '.join(langs)}.")
    for t in alt["reachable"]:
        if t.count:
            out.append(f"**Measured: {t.term!r} ({t.lang}) returned "
                       f"{thousands(t.count)} here on {t.on}** — you work in "
                       f"{t.lang}, so try it.")
        else:
            out.append(f"{t.term!r} ({t.lang}) returned 0 here on {t.on} too, "
                       f"so that one is already spent.")
    # **Only a market that is bigger than anything they can reach is worth
    # naming.** Telling somebody about a language they do not work in is
    # useful when it holds twelve thousand ads they cannot see, and noise
    # otherwise — the point is to let them steer, not to list the table.
    best = max([t.count for t in alt["reachable"]] or [0])
    bigger = [t for t in alt["out_of_reach"] if t.count > max(best, 0)]
    if bigger:
        t = max(bigger, key=lambda x: x.count)
        out.append(f"**And {t.term!r} ({t.lang}) returned {thousands(t.count)} "
                   f"on the same index on {t.on} — a language you have not "
                   f"declared as a working one.** Said so you can decide: ads "
                   f"in a language usually want that language, and neither "
                   f"hiding that market nor pouring it out is the sweep's "
                   f"call.")
    if langs and not alt["concept"]:
        out.append("No measured equivalent for this term on this market. "
                   "**This is a table of measurements, not a dictionary: it "
                   "will not guess a translation**, because a guessed term "
                   "that also returns zero would look like proof.")
    return " ".join(out) if out else None


def thousands(n):
    """12691 → '12 691'. A thin space would break a terminal; a comma reads
    as a decimal point on half the markets in the table."""
    return f"{n:,}".replace(",", "\u202f").replace("\u202f", " ")
