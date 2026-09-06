---
name: job-setup
description: Set up or change the job-hunt workspace — where the files live, the profile, what the person is looking for, the boards, geography, languages, thresholds, credentials. Use when the user says "set up my job search", "configure le plugin", "I've moved", "j'ai déménagé", "I'm changing career", "je change de métier", "je me reconvertis", "add a job board", "ajoute un site d'emploi", "remove that board", "widen my search", "élargis ma recherche", "change my commute limit", "update my CV sources", "where are my files?", "mes fichiers sont où ?", "I want to look for something else", or asks to redo, revisit or correct any part of the configuration.
---

# Setting up, and changing, the workspace

**This is a skill and not only a command, because reconfiguration is what
people ask for in words.** `/job-setup` still works and is unchanged; but *"I've
moved"*, *"I'm changing career"* and *"add a job board"* are the sentences that
actually arrive, and a slash command is never reached by any of them. It was the
only door to reconfiguration and it opened from one side. Issue #112.

Run the setup procedure in `${JOB_HUNT_ROOT}/shared/setup.md`. **Read that
file in full first** — it is the procedure, including the rule that **every
input you ask for must come with the exact URL or command that produces it, and
every rejected input must come with the reason and the fix.**

## Which part to run

**Resolve the workspace first**, and if it cannot be resolved, ask before
creating anything — `shared/workspace.md` has the cascade:

```bash
JOB_HUNT_HOME="$(python3 "${JOB_HUNT_ROOT}/bin/workspace-path.py")"
```

- **Nothing named** → full setup. **If `config.yml` already exists, show the
  current configuration first and ask which sections to revisit** rather than
  re-asking everything. Somebody who says *"reconfigure"* rarely means *all of
  it*.
- **A section named** — `profile`, `contact`, `orientation`, `commute`,
  `languages`, `boards`, `searches`, `thresholds`, `modules`, `signature`,
  `repos` → jump to that step, change only it, leave the rest untouched.
- **`boards`** also runs section **5d** when the geography reaches Austria: AMS
  is the one board that asks the user to take a position rather than supply a
  value, and it is raised there rather than buried in a list.
- **`orientation`** is the one to reach for when *what the person is looking
  for* has changed rather than a single value — a wider geography, a
  reconversion, opening up to agency work. It re-derives the profile from their
  documents, asks the four orientation questions, and re-picks the board
  shortlist from the answers. **It keeps every board's own settings**, so a
  board dropped from the shortlist comes back with one line.

## Mapping what people say to what to run

| They say | Run |
| :-- | :-- |
| *"I've moved"*, *"j'ai déménagé"* | `commute`, then `boards` — a new region changes which boards carry anything |
| *"I'm changing career"*, *"je me reconvertis"* | `orientation` — it is the whole point of that section |
| *"add / remove a board"* | `boards` |
| *"widen my search"* | `orientation`, not `searches`: widening is a decision before it is a value |
| *"my CV changed"* | `profile` |
| *"where are my files?"* | Answer from `workspace-path.py`, and offer to move them rather than creating a second workspace |
| *"the France Travail / Adzuna key"* | Sections **5c** and **5e**. **Never ask for a secret in the conversation** — see below |

## Credentials are named, never typed

A key goes in the environment **or** in `<workspace>/credentials.env` — both are
read, the environment wins, and `shared/setup.md` §5c and §5e have the click
paths. **Never ask the user to paste a secret into the conversation, and never
write one into `config.yml`**: that file is read aloud, pasted into issues and
backed up.

## Finish the way the procedure says

**Show what changed, file by file, and give one concrete next step.** A setup
that ends without a next step ends in the user wondering whether it worked.
