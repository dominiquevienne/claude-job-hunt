# The workspace — where the user's data lives

Both skills read the same workspace. It sits **outside the plugin**, so
updating, reinstalling or deleting the plugin never touches the user's data.

## Resolving it — and saying where, before writing there

```bash
JOB_HUNT_HOME="$(python3 "${CLAUDE_PLUGIN_ROOT:-.}/bin/workspace-path.py")"
```

**`$HOME` is not the user's folder outside a terminal.** In CoWork it belongs
to a container, so a resume, a letter, a PDF and the ledger land somewhere the
person will never find in their file manager.

**And the expensive failure is not a crash, it is a silent success.** The scan
runs, the letters are written, the ledger fills, nothing errors — and
`README.md`'s *"Plain files. Read them, edit them, back them up"* has quietly
become false. Issue #109.

**The cascade, and each step is evidence rather than a guess:**

| | |
| :-- | :-- |
| `--prefer <path>` | A folder the user named or connected. **The caller passes it; nothing invents one** |
| `JOB_HUNT_HOME` | The explicit override, unchanged — **the terminal path works exactly as before** |
| `<home>/Documents/job_applications` | Only if `<home>/Documents` **exists and is writable**. On a Mac or a Linux desktop it does, which is why nothing changes there |
| **nothing** | **No fallback is invented.** Exit `3`, and one question to the person |

**That last row is the point.** The old line defaulted into
`$HOME/Documents/job_applications` whether or not `Documents` existed —
**creating a directory in a container and reporting success.** Refusing to
guess turns an invisible failure into one sentence:

> *"I'll put your job-search files in `<path>`. Is that where you want them?"*

**A sentence, not an environment variable.** `export JOB_HUNT_HOME` in a shell
profile is exactly what a CoWork user will not do.

**Say where the files go before writing any**, and never hardcode a path or
write into the plugin directory — a plugin update replaces it.

*(`--json` gives `{path, source, ask}` for a caller that wants to phrase the
question itself.)*

## What is in it

| File | Required | What it holds | Written by |
| :-- | :-- | :-- | :-- |
| `config.yml` | **yes** | Machine-readable settings: identity, geography, languages, search sweep, thresholds, modules. **Written by the setup conversation, not by hand** — see below | `/job-setup`, or just saying what changed |
| `candidate.md` | **yes** | Prose the config cannot hold: target role families, hard blockers, contact block, standing resume content, corrections to the exports | `/job-setup`, then edited by hand |
| `profile/` | **yes** | The user's source documents (LinkedIn exports or a CV). The factual record every claim is checked against | `sync-sources.sh` |
| `profile/.text/` | built | Every `profile/` PDF as plain text, written by `sync-sources.sh`. **This is what makes a skill check cheap enough to actually run** — `grep -ril '<term>' profile/.text/`. Rebuilt when an export is newer; delete it and re-run to force it |
| `job-pipeline.md` | created on first scan | The shared ledger: one row per ad, the memory of the whole workflow | `job-scan`, updated by `cover-letter` |
| `commute.md` | optional | Travel times from the home base, validated by the user | `/job-setup` |
| `repos.md` | optional | Technologies verified in the user's own repositories, with their real depth and an explicit "never claim these" list | `/job-setup` |
| `employers.md` | optional | **What is true of an employer rather than of an ad** — legal name, address as a declaration expects it, standing decisions with their lifting dates, whether the user favours or excludes them, which ATS they run. **References ledger rows, never copies them** | `/job-setup`, then edited by hand |
| `signature.png` | optional | Handwritten signature, transparent background | `make-signature.sh` |
| `YYYYMMDD_Company-Role/` | per application | One dossier per application: `job-ad.md`, `resume.md`, `cover-letter.md`, the PDFs | `cover-letter` |

## Loading it, at the start of every run

```bash
JOB_HUNT_HOME="${JOB_HUNT_HOME:-$HOME/Documents/job_applications}"
test -f "$JOB_HUNT_HOME/config.yml" && cat "$JOB_HUNT_HOME/config.yml"
```

- **No `config.yml`** → the workspace is not configured. Run the setup procedure
  in `shared/setup.md`, then resume what the user asked for. Say in one line
  what is happening and why — *"first run: I need about five minutes to set up
  your profile, then I'll run the scan"* — never launch into an interview with
  no explanation.
- **`config.yml` present but a required file missing** (`profile/` empty,
  `candidate.md` absent) → do not silently degrade. Name the missing file, say
  what it costs (*"without `profile/` I have no factual record and cannot write
  a resume"*), and offer the single step that fixes it.
- **`version:` higher than this plugin knows** → the workspace was written by a
  newer plugin. Say so and continue on a best-effort basis; do not rewrite it.

Read `candidate.md` in full, every run. It is where the user records decisions
that must not be re-litigated — role families that are on-profile, blockers that
are real, corrections that override the exports.

## `config.yml` is generated, not authored

**It is three hundred lines of YAML with distinctions that bite.**
`driving_licence: []` means *declared none* and a missing key means *never
asked* — the same shape as `work_authorization`, and neither is guessable from
looking at the file. Issue #113.

**So the announced route is the conversation**: *"I've moved"*, *"add that
board"*, *"raise my commute limit"* all reach `job-setup`, which changes the
one thing and leaves the rest alone. **Editing it by hand still works** and
nothing rejects a hand-edited file — but it is the fallback, and a reader
should not be told otherwise.

*(`templates/config.example.yml` is the reference for what a key means. Read it
to understand a value, not as a form to fill in.)*

## Two files, two subjects, and which one wins

**The ledger is authoritative about advertisements. `employers.md` is
authoritative about the employer. They never speak about the same thing.**

That rule is written down rather than hoped for, because a file that adds a
second place to look must say which one wins **before** they contradict each
other. In practice it means: no score, no application status and no ad title in
`employers.md`; no standing decision about a company recorded only on one ad's
row.

**The incident it comes from.** A freeze on an employer was declared on
2026-08-19 and lifted on 2026-08-27, each on a different ad's row, eighteen
rows apart. On 2026-09-02 a scan discarded three of that employer's ads citing
*"the freeze of 2026-08-19, a standing decision in force"*; **two of them were
live, and the decision no longer existed.**

`job-scan` already said to read a row's notes before proposing it, **and that
was done — one note was read.** The fact that cancelled it lived elsewhere and
nothing said to go and look. **A fact that holds for the employer, filed on an
ad's row, is found only by luck.** Issue #94.

**So read the directory before the row's notes**, mechanically:

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-.}/skills/job-scan/scripts/employers.py" \
  lookup --name "<the employer>"
```

It returns every standing decision **with its lifting date beside it**, so a
lifted freeze cannot be read as a live one. **No file is not an error** — it is
an absence of record, which is not an absence of decisions, and it is said in
those words rather than treated as a clean bill.

**One field is not a decision and must not sit among them: the preference.**
`preferred`, `excluded`, or the line absent — which means **never asked**, not
neutral. Everything in the standing-decisions table carries a lifting date, and
**a preference is not lifted**; filed there it would read as a decision nobody
ended. **A freeze is bounded and goes in the table; "I do not want to work
there" is stable and goes in the field.** An employer can be `preferred` and
frozen at the same moment — two facts, one lifting date. And **a preference
never touches a score**: `shared/scoring-rubric.md` holds that line.

**And what belongs there is the user's data, not the plugin's.** Which ATS a
company runs is theirs; **how that ATS behaves is `shared/ats-open-check.md`**,
indexed by host and true for every user. `jobs.sicpa.com` answers `401` to
everybody — that is not one candidate's fact. The *ATS* field is the bridge
between the two and carries only the tenant's name.

## Precedence when sources disagree

1. **`candidate.md` corrections** — the user's explicit override of a stale
   export. Highest authority.
2. **`profile/` documents** — the factual record.
3. **`repos.md`** — completes the record where the exports understate it, and
   caps what may be claimed. It never *raises* a claim above the depth it
   states.
4. **A public web profile** — supplementary only, and often gated.

Anything present in none of these **does not exist**. Do not infer a skill from
an adjacent one, a job title, or the mere fact that an ad asks for it.
