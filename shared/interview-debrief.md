# After the meeting: the debrief

<!-- verified: 2026-09-02 -->

**The plugin used to stop at `applied`.** A letter was drafted, the user sent
it, the ledger recorded it — and then a phone screen happened and **there was
nowhere to put any of it.** Issue #69.

The case that produced this page, in shape rather than content: six questions
had been prepared. **Four were answered, two were never addressed**, a decision
deadline was given, and a further internal step was promised with no date. The
only place any of it existed was a chat transcript, and by the following week
the deadline would have passed with nothing to know it.

## The rule before the mechanics: the candidate's read is theirs

**This is the one part of a debrief that exists nowhere else.** Not in the ad,
not in `profile/`, not on the employer's site: *did this feel like somewhere I
want to work, and did they seem serious about me.* It is also, usually, what
decides a later go/no-go.

**So it is collected, not inferred.** Ask for it and write down what is said.
**Do not read a tone of voice into a summary, do not soften a bad impression
into a balanced one, and do not talk somebody out of a good one.** The plugin
does not know what the room was like. It knows what it was told.

**And nothing here is a verdict on the person.** A debrief records what
happened, not how well they did.

## What to ask, in this order

**1. The meeting.** When, how long, who was in the room and in what role. A
name and a role, not an assessment.

**2. Against the questions that were prepared** — the column that only exists
if the same object holds both halves:

| Prepared | Outcome |
| :-- | :-- |
| *Who is the end client* | answered, with what |
| *Length of the assignment* | answered, with what |
| *On-call duty* | **not addressed** |
| *Team composition* | **not addressed** |

**The unanswered ones are the point.** They are the agenda for the next
conversation, and they vanish first from memory.

**3. What they asked** — and specifically **anything that could not be
answered**.

> **An interview question the candidate could not answer is not a gap in their
> profile.** Issue #63 exists because that confusion produced a false negative
> once: a briefing told somebody a skill was "not documented in the file", they
> use it daily, and it was in `profile/skills.pdf` with eight experiences
> behind it. **Before recording anything as a gap, prove it there** — and a gap
> that is disproved becomes an **evidence line**, which is exactly what the
> next interview needs.

**4. The next step, and its date.** *"They will reply by the end of next
week"*, *"my file goes to a senior manager"*. **A step with no date is
recorded as a step with no date** — do not invent one, and do not let it pass
as though it had been settled.

**5. The candidate's own read**, in their words. Ask for three things and keep
them separate, because they move independently: **the work** (would this be
interesting), **the people** (would this be bearable), **their apparent
interest** (did they seem serious). A single "how did it go" collapses all
three and is unreadable a month later.

**6. Anything the candidate wants to remember**, unprompted and unedited.

## Where it goes

**The application folder**, as `debrief-<YYYY-MM-DD>.md`, next to the letter
and the CV that produced the meeting. That is where somebody looks before the
second conversation.

**And two marks on the ledger row**, which are the part that has to survive
without being read:

```
`IV:2026-09-02 phone` `FU:2026-09-11` réponse promise · présentation interne, sans date
```

`` `IV:<date> <kind>` `` records **that the meeting happened** — repeatable,
one per meeting, the qualifier short. It is what makes an application countable
as one that *landed*, and `job-report --interviews` is where it is read.
**Neither marker changes the status**: the row stays `applied`, and a later
`rejected` carrying an `IV:` says *refused after an interview*, which is worth
keeping.

`` `FU:<date>` `` records **what was promised**, which is the other half.

`shared/pipeline-format.md` records `` `FU:` `` as a marker no run strips.
**`ledger.py due` lists the rows whose date has arrived**, so a promise made in
a phone call is still visible a week later.

```bash
python3 "$S/ledger.py" due --within 3
```

## What this deliberately does not do

**It does not change the row's status**, and that is now a settled decision
rather than a deferral. Issue #52 chose the marker over a new status word: a
row carrying `IV:` or `FU:` is still `applied`, **because an application that
reached an interview must never stop counting as an application sent.** The
markers add facts to a row; they never replace the one it already carries.

**It does not interpret.** It asks, it records, and it puts a date somewhere a
week from now can find it.
