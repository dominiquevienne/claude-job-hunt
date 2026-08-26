# Never fail silently

**This is the plugin's first rule, and it outranks every convenience.** It
applies to both skills, every module, every adapter, every script — and to any
contribution added later.

A job search is invisible work with delayed feedback: the user finds out weeks
later, from a silence, that something did not happen. **They cannot audit what
you did not tell them.** A scan that quietly covered half its searches, a resume
quietly missing two jobs, an application quietly never sent — each looks exactly
like success until it is far too late to fix.

So: **anything that did not happen, happened partially, or happened on a guess
must appear in the run's own output.** Not in a log file. Not on request. In
what the user reads when the run ends.

## The five failures this rule exists to prevent

| Silent failure | What it looks like to the user | What you do instead |
| :-- | :-- | :-- |
| **A skipped step** | Everything seemed fine | Name it, say why, say what it costs, give the fix |
| **A partial result presented as complete** | "8 new ads" — from 3 of 8 searches | Report *n of m*, always. `Ran 3 of 8 searches (LinkedIn throttled after the third)` |
| **A guess dressed as a fact** | A confident postcode, a score on an unread ad, a claimed skill | Mark it: `~` for a provisional score, "to be established" for a missing field, and never claim a skill the record does not carry |
| **An unconfirmed action reported as done** | "Applied" for an application nobody saw land | `applied` requires a confirmation you *saw*. Otherwise `todo` + `send not confirmed` |
| **A silent cap** | Top-10 results from 40 found | Say what was dropped and why: `read 12 of 26 descriptions — stopped to stay under the board's rate limit` |

## What every run owes the user at the end

When **anything** was skipped, degraded, guessed or capped, close with a short
block that says so. Not an apology — an inventory:

> **Not done this run**
> - jobup: skipped — `enabled: true` but no `language` set. Fix: `/job-setup boards`
> - 3 of 18 descriptions unread — the list re-ordered; their scores are marked `~`
> - No `repos.md`, so scoring saw only what your exports declare

When nothing was skipped, **say that too**, in one clause. "All 8 searches ran,
all 12 descriptions read" is information. Its absence is what makes users
wonder.

## Empty is a result, not a silence

Zero new ads, zero matches above threshold, zero pending rows — **report the
zero and why it happened**: how many ads were seen, how many were already in the
ledger, how many were discarded and on what grounds. A run that ends with
nothing to show and says nothing is indistinguishable from a run that broke.

## Errors

- **Never swallow a tool error.** If a call fails, say which one and what it
  means for the result.
- **Never retry the same failing action in a loop.** Two attempts, then stop and
  tell the user what you tried, what happened, and what you need from them.
- **Never route around a blocker that exists for a reason** — a login wall, a
  file picker, a modal that is not in the accessibility tree. Those are dead
  ends by design. Hand them over explicitly; do not improvise a workaround and
  report success.
- **A missing prerequisite is not an error, it is a task** — see
  `shared/prerequisites.md`. Name it, offer the fix, take the fallback.

## Degrading is allowed. Degrading quietly is not

The plugin is *built* to keep working with less: no browser, no LaTeX, no
`repos.md`, no board enabled. Every one of those paths is legitimate and should
be taken rather than stopping the user's work.

**The only thing that is forbidden is taking one without saying so.**
