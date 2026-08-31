---
description: Configure (or reconfigure) your job-hunt workspace — profile, orientation (what you are looking for, and which boards serve it), geography, languages, search sweep, thresholds, optional modules.
argument-hint: "[section: profile | orientation | commute | languages | searches | boards | thresholds | modules]"
allowed-tools: Bash(*), Read, Write, Edit, AskUserQuestion
---

Run the setup procedure in `${CLAUDE_PLUGIN_ROOT}/shared/setup.md`. Read that
file in full first — it is the procedure, including the rule that **every input
you ask for must come with the exact URL or command that produces it, and every
rejected input must come with the reason and the fix.**

Arguments: `$ARGUMENTS`

- **No argument** → full setup. If `$JOB_HUNT_HOME/config.yml` already exists,
  show the current configuration first and ask which sections to revisit rather
  than re-asking everything.
- **A section named** (`profile`, `contact`, `orientation`, `commute`,
  `languages`, `boards`, `searches`, `thresholds`, `modules`, `signature`,
  `repos`) → jump straight to that step of the procedure, change only it, and
  leave the rest untouched.
- **`boards`** also runs section **5d** when the user's geography reaches
  Austria: AMS is the one board that asks them to take a position rather than
  supply a value, and it is raised there rather than buried in the board list.
- **`orientation`** is the one to reach for when *what the user is looking for*
  has changed rather than a single value — widening the geography, a
  reconversion, opening up to intérim. It re-derives the profile from their
  documents, asks the four orientation questions, and re-picks the board
  shortlist from the answers. It keeps every board's own settings, so a board
  dropped from the shortlist can be switched back on with one line.

Finish by showing what changed, file by file, and one concrete next step.
