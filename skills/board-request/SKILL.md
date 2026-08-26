---
name: board-request
description: Capture a job board that claude-job-hunt cannot scan yet, and prepare it for submission as a new adapter. Records what the board is, what it looks like, and what an adapter would need. Invoked automatically by cover-letter when an ad URL comes from an unknown board, or directly when the user says "add support for <board>", "this board isn't supported", "submit jobs.ch as a board".
user-invocable: true
allowed-tools: Bash(*), Read, Write, Edit, WebFetch, AskUserQuestion, ToolSearch, mcp__claude-in-chrome__*
---

# Requesting a new board adapter

Read `shared/never-fail-silently.md` first — it governs this skill more than any
other, because a request that quietly goes nowhere is exactly the failure it
forbids.

`job-scan` can only sweep boards that have an adapter in `shared/boards/`. This
skill captures everything a maintainer needs to write one for a board that does
not have it yet — and, crucially, **does not stop the user's work**: they can
apply to an ad from any board today through `cover-letter <URL>`.

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

## 3 — Save it locally

```bash
JOB_HUNT_HOME="${JOB_HUNT_HOME:-$HOME/Documents/job_applications}"
mkdir -p "$JOB_HUNT_HOME/board-requests"
```

Write it to `$JOB_HUNT_HOME/board-requests/<board-slug>.md`. If a report for
that board already exists, update it rather than adding a second — and tell the
user it was already recorded.

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

### Route A — the GitHub CLI, when it is there

```bash
gh auth status
```

Authenticated? Then offer it, naming the account it would post under:

> *"I can open an issue on `dominiquevienne/claude-job-hunt` as **@\<login\>**
> with the report below. Post it?"*

Show the title and the full body first. On an explicit yes:

```bash
gh issue create \
  --repo dominiquevienne/claude-job-hunt \
  --title "Board request: <board name>" \
  --body-file "$JOB_HUNT_HOME/board-requests/<slug>.md" \
  --label board-request
```

If it fails because the label does not exist in the repo, retry once without
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
  "$JOB_HUNT_HOME/board-requests/<slug>.md" "<board name>" <<'PY'
import sys, urllib.parse
body = open(sys.argv[1]).read()
if len(body) > 6000:                     # URLs have limits; do not silently truncate
    body = body[:6000] + "\n\n…truncated — full report attached separately."
q = urllib.parse.urlencode({"title": f"Board request: {sys.argv[2]}", "body": body})
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

Close by returning the user to what they were actually doing:

> *"jobs.example.com isn't a board I can sweep automatically yet — I've noted
> what an adapter would need at `~/Documents/job_applications/board-requests/…`.
> It changes nothing for this ad: give me the URL and I'll score it, and write
> your resume and letter as usual."*

The request is a side effect. The application is the task.
