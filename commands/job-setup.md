---
description: Configure (or reconfigure) your job-hunt workspace — profile, geography, languages, search sweep, thresholds, optional modules.
argument-hint: "[section to change, e.g. 'commute' or 'searches']"
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
- **A section named** (`profile`, `contact`, `commute`, `languages`, `boards`,
  `searches`, `thresholds`, `modules`, `signature`, `repos`) → jump straight to
  that step of the procedure, change only it, and leave the rest untouched.

Finish by showing what changed, file by file, and one concrete next step.
