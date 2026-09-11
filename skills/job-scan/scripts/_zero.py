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


EXIT_INDETERMINATE = 6


def empty_first_page(board, body, what="card", candidates=None, where=None,
                     what_asked=None):
    """The sentence for a FIRST page that yielded nothing — and it goes in a
    `die(…, 6)`, never in a `note()` followed by `return`. #181.

    **The finding behind it.** Sixteen adapters, read one by one in the re-pass
    of #181, printed `zero_note()` on an empty first page and exited 0 with
    nothing on stdout. *`zero_note` is right about what a zero cannot
    distinguish — and an exit 0 with an empty stdout is exactly what a caller
    reads as «this board is empty».* The admission was on stderr; the verdict
    was on the exit code, and the exit code said fine.

    **The second figure is the size of the body.** A page of tens of kilobytes
    with nothing extracted is one of two things — a reading fault (the markup
    moved, the pattern reads nothing) or a search that matched nothing on a
    board that still serves its chrome — and from here they look alike. So the
    size is printed beside the zero, `candidates` (the blocks a coarse split
    found before parsing) when the adapter has one, and the exit is 6:
    INDETERMINATE, not a count. *The page-1 case only: past the first page an
    empty page is the end of a listing, and the adapters say so themselves.*

    `jobbkk` is the case that opened #181 — 1 239 956 bytes, 25 advertisement
    links, «page 1 carried no result card», exit 0.
    """
    n = len(body or "")
    where = f" at {where}" if where else ""
    asked = f" for {what_asked}" if what_asked else ""
    s = (f"[{board}] page 1 yielded no {what}{asked}{where} — from {n:,} "
         f"characters".replace(",", chr(32)))
    if candidates is not None:
        s += f", {candidates} candidate block(s) before parsing"
    s += (". **A page this size with nothing extracted is not an empty "
          "board**: a reading fault and a search that matched nothing look "
          "alike from here. INDETERMINATE — read the page before believing "
          "the zero, and do not record one.")
    return s
