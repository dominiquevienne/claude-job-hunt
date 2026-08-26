---
name: job-report
description: List the job applications recorded in the pipeline ledger between two dates, and count what was actually sent. Defaults to the current month (1st → today). Use when the user asks "how many applications this month?", "list my applications between X and Y", "combien de candidatures ce mois-ci ?", "récap de mes candidatures", or wants the volume of applications sent over a period — including for an unemployment-office declaration.
user-invocable: true
allowed-tools: Bash(*), Read
---

# Applications report

Reads the ledger that `job-scan` and `cover-letter` maintain, and lists the
applications whose status date falls inside a period.

**Shared references:**

| File | When |
| :-- | :-- |
| `shared/never-fail-silently.md` | **Always.** A count is the one output where a silent omission is invisible |
| `shared/workspace.md` | Locating the ledger |
| `shared/pipeline-format.md` | What each status means |
| `shared/modules/*.md` | Only those enabled in `config.yml` |

## Run it

```bash
JOB_HUNT_HOME="${JOB_HUNT_HOME:-$HOME/Documents/job_applications}"
python3 "<this skill's folder>/scripts/list_applications.py" [options]
```

With **no options**: applications **actually sent** — statuses `applied` *and*
`rejected` — from the **1st of the current month** to **today**. That is the
default the user almost always means; pass `--from`/`--to` only when they name
a different period.

| Option | Default | Meaning |
| :-- | :-- | :-- |
| `--from YYYY-MM-DD` | 1st of current month | inclusive start |
| `--to YYYY-MM-DD` | today | inclusive end |
| `--status` | `applied,rejected` | comma-separated kinds, or `all` (`applied`, `rejected`, `no-go`, `todo`, `discarded`) |
| `--format` | `table` | `table` (terminal), `md` (markdown), `json` |
| `--file` | `$JOB_HUNT_HOME/job-pipeline.md` | another ledger |

```bash
# this month (default)
python3 scripts/list_applications.py

# July 2026
python3 scripts/list_applications.py --from 2026-07-01 --to 2026-07-31

# everything with a date, as a markdown table
python3 scripts/list_applications.py --from 2026-01-01 --status all --format md
```

## Resolving the period from what the user said

Compute the dates yourself and pass them explicitly — the script does no
natural-language parsing:

- "this month" / nothing said → omit both flags.
- "last month" → 1st to last day of the previous month.
- "this week" → Monday → today.
- "since the 15th" → `--from` the 15th of the current month, no `--to`.
- A single date mentioned → treat it as `--from`.

Take today's date from the environment, never a guess. **Say which period you
used**, so a wrong interpretation is visible immediately rather than silently
producing a plausible number.

## What counts as an application

The ledger's `Status` column carries the date: `applied YYYY-MM-DD`,
`rejected YYYY-MM-DD`, `no-go YYYY-MM-DD`. Rows that are `todo` or `discarded`
have no date and are never counted.

**`rejected` counts as an application, and this is not negotiable.** It means
the application went out and the employer answered no. It is a real
application: it belongs in the volume the candidate reports, and it is exactly
the population that gets forgotten. Counting `applied` alone is a known,
documented way to under-report — see `shared/pipeline-format.md`. Hence the
default filter `applied,rejected`.

So the number is **applications actually sent**, not ads scanned. If the user
seems to want the scanned volume instead, say so and use `--status all`, or
read the ledger's `## Log` section.

## Legacy ledgers

The script also accepts the older French status vocabulary
(`postulé le <date>`, `refusé le <date>`) so a ledger that has not been migrated
still reports correctly. It reads column names **from the table header** rather
than by position, so a ledger with or without the `Pay` column both work.

If it finds French statuses, **say so** and offer to migrate the file — running
two vocabularies indefinitely is how one of them silently stops matching.

## Reporting back

Give the **count first**, then one line per application (date · company ·
role), plus the status when it is not a plain `applied`. Keep the note column
out unless it explains something — an application sent through an external ATS,
say. Report in the user's `languages.interface`; the script's own output is
English.

**Then the omissions, per `shared/never-fail-silently.md`.** The script reports
them in `meta`; pass them on rather than presenting a clean number:

- rows whose status could not be parsed,
- rows counted but with no reconstructible ad URL (an id of `—`, or a board
  with no URL template),
- the total row count the number was drawn from, as *n of m*.

If **zero** applications fall in the range, say so plainly **and give the date
of the most recent one outside it** — that is usually the real question behind
an empty result, and an unexplained zero is indistinguishable from a broken
filter.

## When an unemployment-declaration module is enabled

If `config.yml` sets `modules.unemployment_declaration`, read that module and
**always surface the undeclared applications**: the script counts rows carrying
a `JR:missing` marker and reports it as `jr_missing` in `meta`.

A period report is the moment the user is thinking about their declaration, so
naming the gap there is worth more than any total. List those rows explicitly —
company, role, date — and repeat the module's responsibility line: the
declaration is theirs to check and submit.
