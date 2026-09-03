---
name: board-request
description: Report a board problem upstream so the fix reaches every user, not just this machine. Three modes — a board with no adapter yet (records what an adapter would need), an adapter that has stopped working (records the symptom, what changed and the evidence), and a finding that is not a board failure at all (an adapter that answered with the wrong data, a trap in a site's behaviour, a defect in one of the scripts, a method that turned out wrong). Invoked automatically by cover-letter when an ad URL comes from an unknown board, by job-scan when a board's sweep fails, whenever a run learns something that would be true for another user of this plugin, or directly when the user says "add support for <board>", "this board isn't supported", "the LinkedIn scan is broken", "jobup stopped working", "submit jobs.ch as a board".
user-invocable: true
allowed-tools: Bash(*), Read, Write, Edit, WebFetch, AskUserQuestion, ToolSearch, mcp__claude-in-chrome__*
---

# Reporting upstream

**The skill is called `board-request` and two of its three modes are not about a
board.** The name is historical and kept because it is referenced from the other
skills; what it does is take anything one user learned that would be true for
another and turn it into an issue.

Read `shared/never-fail-silently.md` first — it governs this skill more than any
other, because a request that quietly goes nowhere is exactly the failure it
forbids.

**And when a report quotes a board's terms, read them through
`shared/reading-terms.md`.** A sweep is one candidate's own search, so a clause
against commercial harvesting does not describe it — while a clause forbidding
automated access *as such*, a rate limit, a login wall or a `robots.txt`
refusal all bind regardless. **Quote the clause before concluding from it**, so
the maintainer can disagree with the reading without re-finding the document.

`job-scan` can only sweep boards that have an adapter in `shared/boards/`. This
skill captures what a maintainer needs to fix that — and, crucially, **does not
stop the user's work**: they can apply to an ad from any board today through
`cover-letter <URL>`.

## Why this goes upstream at all

Both modes below end in the same place: an issue on the plugin repository.

**That is the whole point, and it is worth being explicit about.** A board that
cannot be swept, or an adapter that has stopped working, is almost never one
user's problem — the site changed for everybody. **And neither is a board that
swept perfectly and returned the wrong ads**, which is the same fact with the
warning removed. Fixing it locally helps the
person in front of you and nobody else, and the next plugin update overwrites
the fix. **The issue is the only route by which one user's broken scan becomes
every user's working scan.**

So: work around it locally *and* report it. Never treat the local workaround as
the resolution — say both happened, and give the issue URL as proof.

**Then, once, quietly:**

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-.}/bin/version-check.py"
```

**It prints nothing when the workspace is current**, which is the normal case
— no version line, no reassurance. When a newer release exists it prints one
short block naming it and the host commands that fetch it. **Pass it on as it
is and carry on**: updating is the host's action, the plugin changes nothing,
and the user's task is not interrupted for a version number. Cached for a day;
every failure is silence. Issue #79.

## Which mode are you in?

| Situation | Mode | Section |
| :-- | :-- | :-- |
| The board has **no adapter** in `shared/boards/` — a URL from a site `job-scan` cannot sweep | **New board** | 1 → 2 → 3 → 4 |
| The board **has** an adapter and it **no longer works** — the sweep returns nothing, the selectors miss, the site redesigned, a login appeared, anti-bot escalated | **Broken adapter** | **2b** → 3 → 4 |
| **Nothing failed** — the sweep finished and you learned something anyway: the adapter answered with the **wrong** data, a site behaves in a way that will fool the next reader, a script has a defect, a method turned out to be wrong | **Finding** | **2c** → 3 → 4 |

A broken adapter **skips section 1 entirely**: whether the site is a board was
settled when the adapter was written. Do not re-litigate it.

**So does a finding.** Section 1 asks whether a *site* deserves an adapter; a
finding is often not about a site at all.

## 1 — Is this actually a board?

A **job board** aggregates ads from many employers and has a search. That is
what an adapter is for.

These are **not** boards, and an adapter would be wasted on them:

| Not a board | Tell it apart by | What to do instead |
| :-- | :-- | :-- |
| A single company's careers page | One employer throughout; the domain is the employer's | Nothing — `cover-letter <URL>` handles it |
| An applicant tracking system (Greenhouse, Workday, Lever, SmartRecruiters, Taleo, Personio, Recruitee…) | The URL contains the ATS name, or the page is one employer's branded portal | Nothing. ATSs need accounts and ask bespoke questions; the skill already declines to drive them |
| A recruitment agency's own site | One agency posting client roles | Nothing |
| An aggregator that only redirects | Every ad bounces to another site | Say so — an adapter would scrape a middleman |

Decide from the URL and, if it is ambiguous, one `WebFetch` of the home page.
When it is not a board, **say so plainly and move on** — do not file a request
nobody can act on, and do not make the user feel their URL was a mistake.

## 2 — Capture what a maintainer would need

Whatever you can establish without a lot of clicking. Everything is optional
except the first two lines: an incomplete report is still useful, a wrong one
is not.

```markdown
# Board request — <name>

- **Home page:** <URL>
- **Example ad URL:** <the URL the user gave>
- **Country / region:** <where it covers>
- **Language(s):** <of the site>
- **Login required to browse ads?** <yes / no / unknown>
- **Search URL shape:** <if visible, e.g. https://…/jobs/?q=…&location=…>
- **Stable per-ad id?** <what the ad URL looks like — the dedup key depends on it>
- **In-site apply flow?** <does it have its own "quick apply", or does it hand off?>
- **Why it matters:** <one line, in the user's words>

Reported <YYYY-MM-DD> from claude-job-hunt <version>.
```

If the Claude Chrome extension is connected and the user agrees, opening the
board's search page once and noting the result-card structure makes the report
far more actionable. **Ask first, keep it to two or three page views, and never
log in.** If the extension is absent, skip it — the report is still worth
filing.

**Record only what you observed.** A guessed selector is worse than a blank
field: it produces an adapter that looks verified and returns the wrong ads.

## 2b — When an existing adapter has stopped working

You are here because `job-scan` hit a board it is supposed to handle and it did
not work. **The failure is the report.** Capture it while the browser is still
on the page — a symptom reconstructed from memory an hour later is the kind of
guess that produces an adapter fix for the wrong thing.

**Establish first that the adapter is what broke.** Three things look identical
from the outside and need different fixes, or no fix at all:

| Looks like | Actually | Tell it apart by |
| :-- | :-- | :-- |
| Adapter broken | **The search legitimately has no results** | Run one of the user's queries by hand in the browser. Results on screen, none extracted → adapter. Nothing on screen either → not a bug |
| Adapter broken | **The user is logged out**, or the session expired | The adapter's prerequisites block; the logged-out layout is usually obvious in a screenshot |
| Adapter broken | **The run was on stale code** — the fix already shipped | `bin/version-check.py --print-version`, then compare against the closed issues. **See below: this one is not a symptom of the board at all.** |
| Adapter broken | **Anti-bot challenge** (`indeed.md` documents this as expected behaviour) | A challenge page. This is the *user's* to solve, and the adapter already says so — not an issue unless the challenge is new or now unsolvable |
| Adapter broken | **The adapter answered, and the answer was wrong** | Nothing to tell apart — this is not a broken adapter and it is not nothing. It is **worse than a failure, because it does not announce itself**. Go to **2c** |

### A failure observed on stale code is not evidence about the board

**Fill `Plugin version:` from the code that actually ran**, never from the
repository:

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-.}/bin/version-check.py" --print-version
```

**Then check whether the running version is behind**, because the whole report
depends on it:

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-.}/bin/version-check.py"
```

**If it prints anything, stop and say so before filing.** A board that failed
under an old adapter tells you nothing about the board: the fix may have
shipped weeks ago and the symptom would be a closed issue re-opened as a new
one — *the most expensive shape a bug report can take*. Ask the user to update
and run the sweep again, and file only if it still fails.

This is not hypothetical. A `/job-scan` run on 2026-09-02 executed from plugin
cache **1.52.0** while the repository was at **1.85.1** — 53 releases behind —
and reproduced a HiringCafe 403 that had been fixed in v1.72.1 four hours
earlier. **The stale code even reported it with pre-fix semantics**: exit 2
(*broken*) where the fixed version exits 6 (*throttled*), so the skill could
not make the very distinction the fix exists to provide, and it went looking
for a tracker to file against. Issue #78.

**And the duplicate check has to look at closed issues too**, not only open
ones — filtered to fixes that shipped *after* the version that observed the
symptom. An open-issues-only search is what lets a fixed bug be filed twice.

Only when it is genuinely the adapter, write:

```markdown
# Board adapter broken — <board>

- **Board:** <name> · adapter `shared/boards/<board>.md`
- **Plugin version:** <version>
- **Observed:** <YYYY-MM-DD>
- **Last known working:** <date, or "unknown" — check the ledger's Log for the last successful scan of this board>

## Symptom

<What job-scan did, and what it got. Counts matter: "0 cards extracted from a
search page showing 25 results" is actionable; "the scan didn't work" is not.>

## Where it broke

<Which step of the adapter — building the search URL, loading the page,
extracting cards, opening a description, reading the id. Name the step.>

## What changed on the site

<Only what you observed: a selector that no longer matches, a renamed field, a
new consent or login wall, a changed URL shape, pagination that moved. If you
could not determine it, write "not determined" — never guess a selector.>

## Evidence

<The search URL used. The exact error text if there was one. What a screenshot
or `read_page` showed instead of the expected structure. An example ad URL only
if it is needed to reproduce.>

## Workaround applied for this user

<What was done so their run still produced something — board skipped, ad URL
handled through cover-letter, manual paste. Or "none".>

Reported <YYYY-MM-DD> from claude-job-hunt <version>.
```

**The `Last known working` line earns its place.** It bounds the change to a
window, which is often the difference between a maintainer finding the cause in
ten minutes and not finding it at all.

**Do not fix the adapter file yourself as the answer.** Editing
`shared/boards/<board>.md` in the installed plugin is a local edit in a cache
directory: it is overwritten by the next update, and it reaches nobody else.
If you do patch it to unblock the user, say plainly that it is temporary, and
**put the patch in the issue** — a working fix in the report is the fastest path
to it reaching everyone.

## 2c — When nothing failed and you learned something anyway

**This is the mode that did not exist**, and by count it is the common one. Of
this repository's 46 issues recording a field finding, **10** are "a board did
not sweep" and **36** are this. See
`shared/never-fail-silently.md`, *What you learn belongs to the next user too*,
for the rule and for the measurement.

You are here when the run **succeeded** and produced knowledge that outlives it:

| Shape | Example from this repository |
| :-- | :-- |
| The adapter answered with the **wrong** data | LinkedIn returned seven suggestion-block ads for a search with no results (#46); jobup wrote a re-listing date to the ledger, seven weeks off (#84) |
| A site behaves in a way that will fool the next reader | An expired ad answering `200` with twenty `JobPosting` blocks, none of them the ad (#88) |
| A method is wrong | "A date in the past means the ad is closed" — false against a live BCV vacancy 18 days past its printed deadline (#89) |
| A script carries a defect | `lists[]` dropped, so every requirement of a Lever posting was silently lost (#54) |
| A capability nobody had noticed | jobup and jobs.ch need no browser at all — plain `curl` returns the full payload (#68) |

**Apply the test before writing anything**, because this mode has no failure to
justify it and is therefore the easy one to file noise into:

> Would this still be true on another machine, for another person, tomorrow?

If it turns on this user's config, credentials, profile, or one search that
genuinely had no results, **it is not a finding — it is a line in the run's own
output**, and it stops there.

**And measure before you assert.** A finding filed from one observation is a
guess with a ticket number. Say how many times you saw it, on what, and on which
date — `shared/plausible-and-false.md` on why repetition corroborates only when
the measurements are independent, and #72 on why an assertion of non-existence
must carry the search that established it.

```markdown
# <One line: what is true, not what you did>

- **Kind:** wrong data · site behaviour · method · script defect · capability
- **Where:** <adapter, script, or shared doc that carries the wrong thing — or "nowhere yet">
- **Plugin version:** <version>
- **Observed:** <YYYY-MM-DD>

## What the run did

<The command, the site, the search. What it returned, and that it returned it
cleanly — no error, no warning. This is the point: it looked like a success.>

## What is actually true

<The measurement. Numbers with their denominator: "two of 71", "0 of 300",
"18 days past the printed deadline". Never a number without what it is out of.>

## How it was established

<The commands, in full, so a maintainer re-runs them rather than trusting you.
If a convenience flag changed the answer, say which — `--compressed` and `-L`
have each destroyed a finding here (#71).>

## Who else it hits

<Every user of board X · every adapter reading JSON-LD · every run that scores
on a posted date. If the answer is "only this user", you are in the wrong
section.>

## What was done for this user

<Local workaround, or "none — the run was correct once the finding was applied".>

Reported <YYYY-MM-DD> from claude-job-hunt <version>.
```

**Say where the knowledge should live, not only that it is true.** Most of these
end in a `shared/` doctrine file or an adapter's *Zero-shaped answers* section
rather than in code, and naming the destination is half the fix. #46's own
lesson was that `shared/never-fail-silently.md` **already catalogued the trap**
and the LinkedIn adapter did not carry it — a finding recorded in a place the
next run does not read is barely recorded at all.

## 3 — Save it locally

```bash
JOB_HUNT_HOME="${JOB_HUNT_HOME:-$HOME/Documents/job_applications}"
mkdir -p "$JOB_HUNT_HOME/board-requests"
```

Write it to `$JOB_HUNT_HOME/board-requests/<board-slug>.md` for a **new board**,
or `$JOB_HUNT_HOME/board-requests/<board-slug>-broken-<YYYY-MM-DD>.md` for a
**broken adapter**, and
`$JOB_HUNT_HOME/board-requests/finding-<slug>-<YYYY-MM-DD>.md` for a **finding**
— dated for the same reason a break is, and slugged on what is true rather than
on a board, because a finding often spans several. The date is in the filename because a board can break more
than once, and each break is its own event with its own window — collapsing them
into one file destroys the *last known working* evidence that makes them fixable.

If a report for that board already exists, update it rather than adding a second
— and tell the user it was already recorded. **Two exceptions:** a dated
broken-adapter report is never overwritten, and a broken-adapter report never
overwrites a new-board one.

**Check for an already-open issue before writing a second report for the same
break.** If the user has `gh`:

```bash
# A board — the prefix is the match
gh issue list --repo dominiquevienne/claude-job-hunt \
  --state open --search "<board> in:title" 2>/dev/null

# A finding — no prefix to match, so search the claim's own words, and
# **include closed issues**: a finding is usually closed by the fix that
# records it, and filing it twice is filing a solved problem.
gh issue list --repo dominiquevienne/claude-job-hunt \
  --state all --search "<two or three words of the claim>" 2>/dev/null
```

An open issue for the same symptom → **do not file a duplicate.** Say it is
already reported, give that issue URL, and offer to add a comment if this run
saw something the issue does not have. A second identical issue makes the
problem look twice as big and gets fixed no faster.

## 4 — Offer to submit it

**The local file in step 3 is written first, always, and it is the only thing
that happens without asking.** Submission is optional, explicit, and made under
the user's own GitHub identity — never yours, never a service.

### What leaves the machine — say this before asking

The report contains: the board's URL, **one example ad URL** (the one they gave
you), and what you observed about the site's structure. It contains **no part of
their profile, name, contact details or application.**

The example ad URL is the one thing worth flagging: it reveals which job they
were looking at, and a public issue is public forever. **Offer to strip it** —
the board's home page alone is enough to write an adapter. Do not decide for
them, and do not skip the sentence because it is unlikely to matter.

**A broken-adapter report has two more things to check, and they are easier to
leak.** The report was written while the browser was on the user's own
logged-in session:

- **A search URL can carry their query terms**, which describe what they are
  looking for and sometimes their salary or seniority filters. Usually harmless,
  occasionally not — name it, and offer to reduce it to the URL's *shape*.
- **A screenshot, a `read_page` dump or an error trace can carry session
  identifiers, a profile name, or recommended-jobs content keyed to them.**
  Never paste raw page dumps or cookies into an issue. Describe the structure —
  *"the results container no longer has a `data-job-id` attribute"* — rather than
  attaching what you saw.

### Route A — the GitHub CLI, when it is there

```bash
gh auth status
```

Authenticated? Then offer it, naming the account it would post under:

> *"I can open an issue on `dominiquevienne/claude-job-hunt` as **@\<login\>**
> with the report below. Post it?"*

Show the title and the full body first. On an explicit yes:

```bash
# New board
gh issue create \
  --repo dominiquevienne/claude-job-hunt \
  --title "Board request: <board name>" \
  --body-file "$JOB_HUNT_HOME/board-requests/<slug>.md" \
  --label board-request

# Broken adapter — different title prefix, and it is a bug
gh issue create \
  --repo dominiquevienne/claude-job-hunt \
  --title "Board broken: <board name> — <one-line symptom>" \
  --body-file "$JOB_HUNT_HOME/board-requests/<slug>-broken-<YYYY-MM-DD>.md" \
  --label board-request --label bug

# Finding — no prefix, and the title states what is true
gh issue create \
  --repo dominiquevienne/claude-job-hunt \
  --title "<the claim itself, in one line>" \
  --body-file "$JOB_HUNT_HOME/board-requests/finding-<slug>-<YYYY-MM-DD>.md" \
  --label bug
```

**Keep the two board prefixes exact** — `Board request:` and `Board broken:`.
They are what the duplicate search in step 3 matches on, and what lets a
maintainer tell a missing adapter from a regression at a glance.

**A finding takes no prefix, and its title is the claim, not the activity.**
`"A date in the past means the ad is closed" is false — a BCV ad open 18 days
past its printed deadline` tells a maintainer what changed in the world;
*Investigated jobup dates* tells them nothing and is unsearchable six months
later. It is also why a finding's duplicate check cannot match on a board name:
search the **claim's own words** instead, across open **and** closed issues.

If it fails because a label does not exist in the repo, retry once without
`--label`. Any other failure: report it verbatim and fall back to Route B.

**Give the issue URL that `gh` returns.** That URL is the proof; without it,
nothing was submitted.

### Route B — a pre-filled issue URL

No `gh`, not authenticated, or Route A failed. Build a link that opens GitHub's
new-issue form with everything already typed in, so the user reviews it and
presses submit themselves:

```bash
# `python3` does not exist on Windows by default — resolve an interpreter.
PY_BIN="$(for c in python3 python py; do command -v "$c" >/dev/null 2>&1 && { echo "$c"; break; }; done)"
"${PY_BIN:?no Python found — give the user the local report path instead}" - \
  "$JOB_HUNT_HOME/board-requests/<report file>.md" "<board name>" "<request|broken>" <<'PY'
import sys, urllib.parse
body = open(sys.argv[1]).read()
if len(body) > 6000:                     # URLs have limits; do not silently truncate
    body = body[:6000] + "\n\n…truncated — full report attached separately."
prefix = "Board broken" if sys.argv[3] == "broken" else "Board request"
q = urllib.parse.urlencode({"title": f"{prefix}: {sys.argv[2]}", "body": body})
print(f"https://github.com/dominiquevienne/claude-job-hunt/issues/new?{q}")
PY
```

Give the URL and **ask before opening it in a browser.** If the body had to be
truncated, say so and tell them the complete report is at the local path.

### Route C — they decline, or have no GitHub

Fine, and it is a real outcome, not a failure. The report is on their disk; give
the path and the repository URL, and move on.

### Rules that hold in all three routes

- **One submission, one explicit yes.** An approval for this board does not
  carry to the next one, and asking for a board is not itself an approval.
- **Never post under an identity that is not theirs.**
- **Never say "submitted", "filed", "in the queue" or "will be reviewed" unless
  an issue URL came back.** Saved locally is *saved locally* — say those words.
  This is `shared/never-fail-silently.md` at its sharpest: a request the user
  believes was sent, and was not, is the exact shape of failure this plugin
  exists to refuse.

## 5 — Then get out of the way

Close by returning the user to what they were actually doing.

**New board:**

> *"jobs.example.com isn't a board I can sweep automatically yet — I've noted
> what an adapter would need at `~/Documents/job_applications/board-requests/…`.
> It changes nothing for this ad: give me the URL and I'll score it, and write
> your resume and letter as usual."*

**Broken adapter** — say three things, in this order: what still works, where
the report went, and what it does for them:

> *"The jobup sweep is broken — the result cards changed shape and nothing was
> extracted. Filed as `<issue URL>`, so the fix ships to everyone on the next
> plugin update rather than living on this machine. LinkedIn and Indeed swept
> normally and their ads are in the ledger; for jobup, give me an ad URL and
> `cover-letter` handles it with no adapter at all."*

Never end a broken-adapter run on the failure alone. The user came to find jobs,
and **a board being down does not stop that** — the other boards swept, and any
individual URL still works end to end.

The request is a side effect. The application is the task.
