---
name: interview-rehearsal
description: Rehearse an interview in writing. The agent plays the people on the other side of the table — with drawn facets the candidate does not see: technical depth, managerial and commercial skill, warmth or hostility, and fear of being replaced by the candidate. Three optional parameters (the ad URL, the resume sent, the facets); with none, it starts from the candidate's own profile and draws the rest. Ends in a mandatory debrief where the agent drops the character, reveals the sealed draw and scores the rehearsal against named bases. Use when the user says "fais-moi passer un entretien", "simulate an interview", "répète l'entretien avec moi", "mock interview", or asks to practise before a booked meeting.
---

# Rehearse the interview, then drop the character

**Three phases, and the middle one is blind.** The facets are drawn and sealed,
the interview is played without them being named, and the debrief opens the
seal. **A rehearsal where the candidate knows they face someone afraid of being
replaced is a different exercise entirely** — they would answer the fear, not
the question.

| where | what |
| :-- | :-- |
| `rehearse.py` | the draw, the seal and the reveal. **Not the judging.** |
| `skills/interview-prep/SKILL.md` | the briefing sheet this consumes when one exists |
| `shared/interview-debrief.md` | the format of a **real** debrief — related, and not this |
| `shared/pipeline-format.md` | the ledger, and the markers this skill must not forge |

---

## Phase 0 — where the context comes from

**Two entry points, and the second is richer.**

**With an application in the ledger**, run `interview-prep` first, or read the
sheet it produced. It already holds the archived ad, the resume actually sent,
the scoring gaps and the red lines. **The rehearsal does not reinvent a
context that exists and is sourceable.**

**With nothing**, start from `$JOB_HUNT_HOME/candidate.md` and `profile/`.
Ask nothing first — the request is explicit that the profile is enough to
start. Resolve the workspace, never hardcode it:

```bash
JOB_HUNT_HOME="$(python3 "${JOB_HUNT_ROOT}/bin/workspace-path.py")"
```

Three parameters, **all optional**: the ad URL, the resume sent, and the
facets. Anything not given is drawn.

---

## Phase 1 — the draw, and why it is sealed

```bash
S="${JOB_HUNT_ROOT}/skills/interview-rehearsal"
python3 "$S/rehearse.py" draw \
  --out "$JOB_HUNT_HOME/rehearsals/2026-09-04-acme.json" --interviewers 2
```

**The facets are recorded at the moment they are drawn, and the transcript gets
a digest, not the facets.** That is the whole mechanism, and it exists for one
reason:

> **A debrief that reveals facets chosen after the interview reads exactly like
> one that reveals facets chosen before it.**

Nobody can tell the difference — not the candidate, not a reader of the
transcript, and **not the agent itself**, which is the part that matters. An
agent that reconstructs a plausible draw at debrief time will believe it
remembered one. The digest printed at draw time cannot be matched by a
reconstruction, so the honest failure becomes visible instead of invisible.

**Never print the facets between the draw and the debrief.** Not to explain a
question, not to justify a reaction, not in a summary. The seal is the design.

**Fixing a facet is not cheating and is recorded as such.** `--facet
fear_of_replacement=acute` is a legitimate way to rehearse one situation on
purpose; the file records what was given and what was drawn, and the debrief
says which was which. Same for `--seed`.

**The facet list is open.** `--facet nepotism=strong` is kept verbatim. The
request's "…" is part of the request: **a facet nobody anticipated must not be
lost in silence.**

---

## Phase 2 — the interview

**Play the people, not an examiner.** The facets change what is asked *and how
a good answer lands*. A manager who fears replacement does not stop asking
technical questions — **they stop enjoying the answers.** Someone who read
nothing asks what is already on the CV. Someone under time pressure interrupts.

**Keep the turn and the content of a turn distinct.** One interviewer speaks
per turn, named. This costs nothing in text and is the one choice here that
would be expensive to undo later.

**The candidate is never told the facets, and never told they are being
evaluated on a particular axis.** If they ask, say the debrief will answer —
and mean it.

**Draw questions from the sourceable context first**: the prepared questions
from `interview-prep`, the scoring gaps, the red lines. **Invented questions
are allowed; invented *criteria* are not** — see red line 2.

---

## Phase 3 — the debrief, and the role change

**This is the risk of the whole design.** The same agent played hostility and
must now be honest, and *nothing separates the two unless something is written
down.* A debrief coloured by the character returns a verdict rather than an
evaluation, and the candidate cannot tell.

**So the separation is structural, not an intention:**

1. **Say the rehearsal is over, in one plain line, before anything else.**
2. **Open the seal with the tool, and paste what it prints.** The reveal is
   machine output, not the character's voice — the debrief begins with
   something the character did not write.
   ```bash
   python3 "$S/rehearse.py" reveal --file "$JOB_HUNT_HOME/rehearsals/2026-09-04-acme.json"
   ```
3. **Compare the digest with the line printed at draw time.** If they differ,
   say so and stop treating the file as the draw. If there is no file at all,
   **say that the facets cannot be revealed honestly** — do not describe them
   from memory.
4. **Reveal the facets that were drawn, not the ones that would best explain
   what happened.** This is red line 3, and it is the exact temptation of the
   moment.

---

## The percentage, and it carries its base

**A percentage without a base is a fabricated number.** It looks like a
measurement and it is produced by whoever announces it. This repository has
spent a week on exactly that species.

**So report the bases separately, and never fuse them into one figure without
saying so:**

| base | what it counts | kind |
| :-- | :-- | :-- |
| prepared questions | asked, and answered / unanswered | **fact** |
| scoring gaps | which were probed, which were closed | **fact** |
| red lines | raised, and how they were handled | **fact** |
| the interviewer's judgement | with the drawn facets as context | **avowed opinion** |

**Give each its own number with its own denominator** — *"7 of 9 prepared
questions answered"*, not *"78 %"*. The fourth is a sentence, not a
percentage, and **it is labelled as the simulated interviewer's opinion**, not
as an assessment of the candidate.

**If a single headline figure is asked for, it comes from the three factual
bases and says so in the same breath**, naming what it excludes.

**The unanswered prepared questions are the most valuable output.**
`shared/interview-debrief.md` says that column is the useful one after a real
meeting; a rehearsal produces it without waiting for one.

---

## Three red lines

1. **A rehearsal is not an interview, and the ledger must never confuse them.**
   Never write an `IV:` marker for a rehearsal — that marker records a meeting
   that happened, and forging one corrupts the only record that counts. **If a
   trace is left at all, it must be distinguishable by reading, not by
   intention.** The sealed file lives in `$JOB_HUNT_HOME/rehearsals/` and its
   first field is `"kind": "rehearsal"`.

2. **Do not judge the candidate on criteria invented here.** The gaps already
   exist: the scoring, the red lines, the prepared questions left unanswered.
   An evaluation that departs from them manufactures a verdict.

3. **Produce nothing that could be taken for a real record.** No transcript
   presented as one, no employer feedback, no invented interviewer name
   attached to a real company. And **the revealed facets are the drawn ones.**

---

## This skill never

Writes a status change to the ledger; forges an `IV:` or `FU:` marker; claims
about the candidate what `profile/` does not support; reveals a facet before
the debrief; presents a reconstructed draw as a sealed one; or returns a
percentage without the base it was computed on.
