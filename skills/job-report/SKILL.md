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

### Applications that reached an interview

```bash
python3 "<this skill's folder>/scripts/list_applications.py" --interviews
```

**Volume sent is an effort metric; interviews obtained is the outcome one** —
and it is the answer to a question the unemployment office asks and the
candidate asks themselves. A row carries `` `IV:YYYY-MM-DD` `` per meeting and
**keeps its status**, so an application that reached an interview never stops
counting as an application sent.

**Report both numbers with their denominators, never a conversion rate.**
Meetings *held* in the window can belong to applications sent months earlier,
and applications *sent* in the window have had less time the later they went
out. The script prints both and says so; pass that on rather than dividing one
by the other.

**And when nothing comes back, say which silence it is** — no row carries a
marker, or none falls in the window. A meeting nobody recorded looks exactly
like a meeting that did not happen.

### Follow-ups whose date has arrived

**Run this whenever a report is produced**, and put the result at the top:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/ledger.py" due --within 3
```

A `` `FU:YYYY-MM-DD` `` marker is a date **somebody promised in a conversation**
— *"we will reply by the end of next week"*, *"relance le 14.09"* — and it is
the one thing a chat transcript cannot keep. An overdue row is the most
actionable line a report can carry.

**When nothing comes back, say which of the two it is**: no row carries a
follow-up date, or none has arrived. `ledger.py` prints that distinction
itself; pass it on rather than reporting a clean sheet. `shared/interview-debrief.md`
is where the marker gets written in the first place. Issue #69.

### It does not offer to enable a board, and that is deliberate

`cover-letter` offers to switch on an unconfigured board when the user pastes a
URL from one (issue #80). **This skill does not, and should not be given the
ability.** The offer's rule is that it rides in a question already being asked
— and this skill asks none: it has no gate, and `AskUserQuestion` is not in its
`allowed-tools`. A report on a past period is also the wrong moment: the ad is
weeks old and the interest has cooled, where a pasted URL is interest proved a
minute ago.

## When an unemployment-declaration module is enabled

If `config.yml` sets `modules.unemployment_declaration`, read that module and
**always surface the undeclared applications**: the script counts rows carrying
a `JR:missing` marker and reports it as `jr_missing` in `meta`.

A period report is the moment the user is thinking about their declaration, so
naming the gap there is worth more than any total. List those rows explicitly —
company, role, date — and repeat the module's responsibility line: the
declaration is theirs to check and submit.

**`jr_missing` is half the picture, and the visible half.** A row already
declared whose employer has since answered no still reads *En suspens* in
job-room: it misses nothing, so it is counted nowhere, and only a comparison
between the status date and the `JR:` date finds it. When the user is heading
for a declaration session, hand them both lists:

```bash
python3 "<this skill's folder>/scripts/jobroom_sync.py" plan
```

The same script carries the **duplicate gate** that any writing into job-room
must pass — `check`, fed `get_page_text` and never `read_page`. See the
`job-room-ch` module for the rule and for why the distinction matters.
