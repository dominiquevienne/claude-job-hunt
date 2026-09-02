#!/usr/bin/env python3
"""A zero result on a board that is not empty is a finding, not an answer.

**The case this exists for, measured 2026-09-02 (issue #70).** On Adzuna's
Swiss index:

    what=Entwickler     → 12 666
    what=developer      →  3 162
    what=informaticien  →    138
    what=développeur    →      0

Zero. HTTP 200, an empty list, no error and no warning. And `job-scan` builds
its search terms from the user's own profile — so **a French-speaking user
searching in French on a Swiss board gets nothing, and the natural reading of
an empty result is "there are no jobs"**, which is wrong by twelve thousand.

This is the worst failure mode in this repository's taxonomy: a clean finish
carrying a plausible number that is not the board. **Naming it does not find
the ads — it stops the sweep concluding they do not exist**, which is where
the damage is.

A corollary the same measurement produced, worth carrying wherever fill rates
are quoted: on 50 German Adzuna ads, **a salary appeared on 0 and
`contract_type` on 0**. "This board is poor in salaries" may therefore be an
artefact of the language queried. **A fill rate measured in one language is
not the board's fill rate.**

Usage, at the end of any command that reports a count:

    from _zero import zero_note
    if kept == 0:
        note(zero_note("adzuna", what=a.what, where=a.where,
                       market=a.country, speaks=a.speaks))

`market` and `speaks` are optional and turn the general warning into a
specific one: `_language.py` holds what has actually been measured on a
market, and who the person is. Without them the sentence still says what a
zero cannot distinguish; with them it can name the term that works and the
market the person cannot see. **Adapters do not read the config** — the skill
passes `--speaks` from `languages.working`.
"""

__all__ = ["zero_note"]

try:
    from _language import language_note
except ImportError:      # the module is optional; the general warning is not
    language_note = None


def zero_note(board, what=None, where=None, extra=None, market=None,
              speaks=()):
    """The sentence a sweep prints when it found nothing.

    It never claims the board is empty and never claims it is not: it says
    which of the two the run cannot distinguish, and what to change to find
    out.
    """
    asked = []
    if what:
        asked.append(f"keywords {what!r}")
    if where:
        asked.append(f"location {where!r}")
    asked = " and ".join(asked) if asked else "this search"

    lines = [
        f"ZERO RESULTS for {asked}. **This is a finding, not an answer**: a "
        f"search that matches nothing and a market that has nothing look "
        f"identical from here — HTTP 200, an empty list, no error.",
        "Before reading it as 'nobody is hiring', change one thing and run "
        "again: the language of the keywords first. On Adzuna's Swiss index "
        "`Entwickler` returns 12 666 and `développeur` returns 0 — the same "
        "market, asked in two languages (issue #70).",
        "Then the place, then the filters. A board's own category or "
        "occupation codes, where it has them, are language-independent — "
        "**but check how much of the index they actually classify before "
        "trusting one**: on Adzuna's Swiss index 70.7% of ads are "
        "`category=unknown`, so `it-jobs` returns 1 150 where the keyword "
        "returns 12 691.",
    ]
    # What has actually been measured on this market, for this person. It
    # replaces the generic advice with a term and a number where one exists,
    # and stays quiet where none does — see `_language.py`, which refuses to
    # guess a translation on purpose.
    if language_note and what and market:
        specific = language_note(what, market, speaks)
        if specific:
            lines.append(specific)
    if extra:
        lines.append(extra)
    return " ".join(lines)
