---
name: board-request
description: Report a board problem upstream so the fix reaches every user, not just this machine. Two modes — a board with no adapter yet (records what an adapter would need), and an adapter that has stopped working (records the symptom, what changed and the evidence). Invoked automatically by cover-letter when an ad URL comes from an unknown board, by job-scan when a board's sweep fails, or directly when the user says "add support for <board>", "this board isn't supported", "the LinkedIn scan is broken", "jobup stopped working", "submit jobs.ch as a board".
user-invocable: true
allowed-tools: Bash(*), Read, Write, Edit, WebFetch, AskUserQuestion, ToolSearch, mcp__claude-in-chrome__*
---

# Reporting a board problem upstream

Read `shared/never-fail-silently.md` first — it governs this skill more than any
other, because a request that quietly goes nowhere is exactly the failure it
forbids.

`job-scan` can only sweep boards that have an adapter in `shared/boards/`. This
skill captures what a maintainer needs to fix that — and, crucially, **does not
stop the user's work**: they can apply to an ad from any board today through
`cover-letter <URL>`.

## Why this goes upstream at all

Both modes below end in the same place: an issue on the plugin repository.

**That is the whole point, and it is worth being explicit about.** A board that
cannot be swept, or an adapter that has stopped working, is almost never one
user's problem — the site changed for everybody. Fixing it locally helps the
person in front of you and nobody else, and the next plugin update overwrites
the fix. **The issue is the only route by which one user's broken scan becomes
every user's working scan.**

So: work around it locally *and* report it. Never treat the local workaround as
the resolution — say both happened, and give the issue URL as proof.

## Which mode are you in?

| Situation | Mode | Section |
| :-- | :-- | :-- |
| The board has **no adapter** in `shared/boards/` — a URL from a site `job-scan` cannot sweep | **New board** | 1 → 2 → 3 → 4 |
| The board **has** an adapter and it **no longer works** — the sweep returns nothing, the selectors miss, the site redesigned, a login appeared, anti-bot escalated | **Broken adapter** | **2b** → 3 → 4 |

A broken adapter **skips section 1 entirely**: whether the site is a board was
settled when the adapter was written. Do not re-litigate it.

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
| Adapter broken | **Anti-bot challenge** (`indeed.md` documents this as expected behaviour) | A challenge page. This is the *user's* to solve, and the adapter already says so — not an issue unless the challenge is new or now unsolvable |

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

## 3 — Save it locally

```bash
JOB_HUNT_HOME="${JOB_HUNT_HOME:-$HOME/Documents/job_applications}"
mkdir -p "$JOB_HUNT_HOME/board-requests"
```

Write it to `$JOB_HUNT_HOME/board-requests/<board-slug>.md` for a **new board**,
or `$JOB_HUNT_HOME/board-requests/<board-slug>-broken-<YYYY-MM-DD>.md` for a
**broken adapter**. The date is in the filename because a board can break more
than once, and each break is its own event with its own window — collapsing them
into one file destroys the *last known working* evidence that makes them fixable.

If a report for that board already exists, update it rather than adding a second
— and tell the user it was already recorded. **Two exceptions:** a dated
broken-adapter report is never overwritten, and a broken-adapter report never
overwrites a new-board one.

**Check for an already-open issue before writing a second report for the same
break.** If the user has `gh`:

```bash
gh issue list --repo dominiquevienne/claude-job-hunt \
  --state open --search "<board> in:title" 2>/dev/null
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
```

**Keep the title prefixes exact** — `Board request:` and `Board broken:`. They
are what the duplicate search in step 3 matches on, and what lets a maintainer
tell a missing adapter from a regression at a glance.

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
