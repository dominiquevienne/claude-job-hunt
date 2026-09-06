---
name: interview-prep
description: Prepare a booked interview from an application already in the ledger, then debrief it afterwards. Builds a briefing sheet from what the employer actually received — the tailored resume and letter, the archived ad, the scoring gaps, the red lines — and after the meeting records what was answered, what was not, the next step and its date. Use when the user says "prepare my interview", "j'ai un entretien pour X", "fiche de préparation", "I have a call with <company> tomorrow", or reports back on a meeting that has happened.
---

# Interview: prepare, then debrief

**One skill, two phases, and they are one object on purpose.** The questions are
written before the meeting and answered after it, and **the most useful column
of a debrief is which prepared questions came back unanswered** — which exists
only if the same object holds both halves. Two skills sharing state are one
skill. Issues #50 and #69.

**Shared references:**

| File | When |
| :-- | :-- |
| `shared/never-fail-silently.md` | **Always.** Nothing skipped, partial or guessed goes unsaid |
| `shared/workspace.md` | Phase 1 step 0 — locating the user's data |
| `shared/interview-debrief.md` | **Phase 2 in full** — the format, and the rule that the candidate's read is collected and never inferred |
| `shared/pipeline-format.md` | The `IV:` and `FU:` markers, and the statuses this skill never touches |
| `shared/plausible-and-false.md` | Before quoting any figure from the file back to the user |

---

## Phase 1 — before the meeting

### 0 — Load the workspace

```bash
JOB_HUNT_HOME="${JOB_HUNT_HOME:-$HOME/Documents/job_applications}"
S="${JOB_HUNT_ROOT}/skills/job-scan/scripts"
test -f "$JOB_HUNT_HOME/config.yml" && cat "$JOB_HUNT_HOME/config.yml"
python3 "$S/ledger.py" index --excluded-only
```

**Then make the record searchable, once** — phase 1 cannot do its job without
it:

```bash
test -d "$JOB_HUNT_HOME/profile/.text" || \
  "${JOB_HUNT_ROOT}/skills/cover-letter/sync-sources.sh" "<Full Name>"
```

### 1 — Which application, and what to do when there is none

Match the company, the pipeline id or the ad URL against the ledger. The
application folder is `<YYYYMMDD>_<Company>-<Role>/` and holds **what the
employer actually received** — that is what they will ask about.

**No application in the ledger is not a refusal.** Build the sheet from the ad
URL and `candidate.md`, and **say at the top that it is thinner**: no tailored
resume, no archived ad, no scoring rationale. A user who has an interview
tomorrow for something they applied to by hand still needs the sheet. **What
they must not get is a thin sheet presented as a full one.**

### 2 — Ask about the meeting, in one batch

**One `question` call, with sensible defaults — never one question per
turn.** These are not the point of the skill; they are what it needs to stop
guessing:

| | Default |
| :-- | :-- |
| When | the next working day, to be corrected |
| How long | 30–45 min |
| Format | phone / video / on-site |
| Who is in the room, and in what role | unknown, and the sheet says so |
| Which round | first |

**Where the employer is an agency or a consultancy, add one question and only
one: is the end client named?** It is the most valuable unknown in that
configuration — it decides what the work actually is, where it happens, and who
the candidate would be reporting to.

### 3 — Build the sheet

From the folder: the tailored **resume** and **letter** (what they received),
the archived **ad** with its must-haves and its pay estimate and reserves, the
ledger **`Note`** with the scoring rationale, and `candidate.md` for
availability, mobility, language levels and **the things that must not be
said**.

#### 3a — Every gap is proven against `profile/` before it reaches the sheet

**This is the hardest requirement here and the one that has already cost
something.** A sheet told a candidate that Confluence was *"not documented in
the file"* and handed them a sentence to deflect it with. It is in
`profile/skills.pdf` with **eight experiences** behind it, and the ad named it.
**The sheet took the strongest tool match in the whole ad and turned it into
something to apologise for.**

```bash
grep -ril "confluence" "$JOB_HUNT_HOME/profile/.text/"
```

- **No gap reaches the sheet on the `Note`'s authority alone.** A `Note` is a
  scoring artefact written at one moment by one run, possibly against sources
  that did not include the inventory. It is **a lead, not a proof**.
- **Not found is not not there.** Where a requirement is unattested, the honest
  output is **a question to the candidate** — *"not attested in `profile/`; do
  you have it?"* — never an assertion of absence.
- **A `Note` gap that turns out to be attested becomes an evidence line, and
  the sheet says so** rather than quietly dropping it. The candidate needs to
  know they can answer that question well.
- **Where the search cannot be run at all** — no `pdftotext`, no `profile/` —
  say so and assert nothing.

**Why this matters more here than anywhere else.** A wrong *positive* claim is
caught in the room, by the interviewer. **A wrong *negative* claim is never
caught**: the candidate has no reason to doubt their own file, concedes a
requirement they meet, and spends on an apology the answer that would have
landed. The plugin's promise is that it never invents a skill the user lacks;
**the mirror of that promise is never denying one they have.**

#### 3b — What the candidate should ask

Turn the ad's own reserves into questions. On the case that produced this
skill: the ad was **not on the employer's own careers site**, which listed 49
other posts, and **the end client was not named** — both are first questions,
not curiosities.

**Every prepared question is written down as a question**, because phase 2 will
report which ones came back unanswered, and that column cannot exist otherwise.

#### 3c — Pay, and the red lines

The archived ad carries the estimate **with its tier and its reserves** — an
agency's advertised range is the agency's, not the client's budget. Quote it
with the reserve attached, per `shared/plausible-and-false.md`.

And `candidate.md`'s red lines are reproduced **as red lines**: what must not
be mentioned, and what must not be overstated.

### 4 — The calendar event: proposed, confirmed, never silent

**Offer to add it. Never add it silently, and never fail silently.** The user
may have no calendar connected; a skill that quietly does nothing is worse than
one that says it cannot. If it cannot be created, **say so and give the
details** so the user can add it in five seconds.

---

## Phase 2 — after the meeting

**Follow `shared/interview-debrief.md` in full.** It is the format, and two of
its rules outrank convenience:

- **The candidate's own read is collected, never inferred.** Do not read a tone
  of voice into a summary, do not soften a bad impression into a balanced one,
  and **do not talk somebody out of a good one.** Asked in three parts kept
  separate — the work, the people, their apparent interest.
- **An interview question the candidate could not answer is not a gap in their
  profile.** Prove it against `profile/.text/` before recording it as one — the
  same rule as 3a, arriving from the other direction.

**And the column that justifies one object rather than two**: the prepared
questions from step 3b, against what came back, **with the unanswered ones
named.** They are the agenda for the next conversation and the first thing to
vanish from memory.

## Writing to the ledger, and what this skill never does

**Only markers in the `Note`, never the `Status`:**

```
`IV:2026-09-02 phone` `FU:2026-09-11` réponse promise · présentation interne, sans date
```

`IV:` records that the meeting happened, `FU:` what was promised.
`shared/pipeline-format.md` has both, and **neither changes the status** — a
row that reached an interview must never stop counting as an application sent.

**And the plugin does not lift a decision it did not take.** If a debrief
reveals that a row marked `no-go` or `discarded` is in fact open, **say so and
leave the re-opening to the candidate.** Those statuses record their decision,
not ours.

**This skill never**: writes a claim about the candidate that `profile/` does
not support, invents an interviewer's name, files a calendar event without
confirmation, or reports a sheet built in degraded mode as a full one.
