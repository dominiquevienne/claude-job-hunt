# The workspace — where the user's data lives

Both skills read the same workspace. It sits **outside the plugin**, so
updating, reinstalling or deleting the plugin never touches the user's data.

## Resolving it

```bash
JOB_HUNT_HOME="${JOB_HUNT_HOME:-$HOME/Documents/job_applications}"
```

Use that line in every snippet. Never hardcode a path, and never write anything
into the plugin directory — a plugin update replaces it.

## What is in it

| File | Required | What it holds | Written by |
| :-- | :-- | :-- | :-- |
| `config.yml` | **yes** | Machine-readable settings: identity, geography, languages, search sweep, thresholds, modules | `/job-setup` |
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
