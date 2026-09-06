# What the candidate did since last time

**A dossier ages in silence.** Nothing here ever asked *"have you done anything
new?"*, and that is the only way an achievement that exists in no export ever
reaches the record. Issue #42.

## The case, and it is not a small one

On 2026-08-31 a passing question — *does this plugin appear in `repos.md`?* —
turned up **no**. It was a public MIT repository: 125 commits, 35 adapters,
7 814 lines of dependency-free Python, **written in five days during the job
search**, and the best available evidence for a practice the dossier already
claimed on ten times thinner grounds.

**The file had been reread and enriched several times in those five days.**
Nobody thought to ask.

**A candidate does not spontaneously declare what they have just done.** To
them it is the present, not a CV line. And the cost is exact: the dossier's
Python line read *scripting, stdlib* while the reality was 7 814 lines of
production code — points lost on every ad mentioning Python, for five days of
active applications.

## This is not a developer's problem, and building it as one misses it entirely

`repos.md` is an artefact of a single trade. **The reflex is a reminder that
scans git repositories. That would be useless to most of the people this plugin
is for.**

- a **cabinetmaker** delivered three kitchens and a fitted library;
- a **nurse** qualified in palliative care;
- a **project manager** finished a migration last week;
- a **graphic designer** rebuilt a client's visual identity;
- anyone at all passed a **certification**, did **qualifying voluntary work**,
  or took on a **responsibility in an association**.

**None of it appears in a LinkedIn export until the person puts it there, and
none of it is detectable. Only the question makes it exist.**

So: **never scan the disk for projects.** It is intrusive, and it answers for
one trade out of twenty.

## When to ask

**Monthly, at the end of a `job-scan` — never in the middle of writing an
application.**

**Only `job-scan`, and that is a constraint rather than a preference.**
`job-report` cannot ask: its `allowed-tools` are `Bash(*), Read` and it holds
no `question` on purpose — it has no gate, and the same reasoning that
keeps the board offer out of it keeps this out too. **A skill that cannot ask
must not improvise a question in prose**, so `job-report` says nothing here.
`cover-letter` can ask and must not: a person writing an application is
mid-task, and this question would interrupt it.

```bash
python3 "${JOB_HUNT_ROOT}/skills/job-scan/scripts/achievements.py" due
```

`due: false` → **say nothing at all.** No "I won't ask this time", no mention.

**A question asked too often is ignored, then resented, then switched off.**
The interval exists to keep the question worth answering, and `achievements.py`
holds the schedule so no run has to reason about dates.

## How to ask

**One open question, in the candidate's own vocabulary, and not a
questionnaire:**

> **Depuis un mois : de nouvelles réalisations, formations, certifications,
> responsabilités ?**

Never *"have you pushed any new repositories?"* — that question answers itself
for one trade and excludes everyone else.

**"No" is a complete answer.** Do not probe, do not offer examples to jog the
memory, do not ask again before the next interval:

```bash
python3 …/achievements.py asked --outcome none
```

**And "stop asking" must work.** `--outcome paused` and the question never
returns until the candidate says otherwise. A reminder with no off switch is
the nag this file exists to avoid.

## If the answer is yes — two steps, in this order

### 1. Record it where the trade puts it

```bash
python3 …/achievements.py where
```

That prints **which destinations this workspace actually has**, and it is the
guard against the reflex above:

| Destination | For |
| :-- | :-- |
| `candidate.md` | **The default, for every trade** — a qualification, a responsibility, a delivery, volunteering |
| `repos.md` | Software work with a repository, **and nothing else** |
| `profile/` | A document that speaks for itself — a certificate, a portfolio page, an attestation |

**Do not create a destination in order to have somewhere to put a trade it does
not fit.** A nurse's palliative-care qualification does not belong in a file
about repositories, and inventing one to hold it is how a tool teaches a
candidate that their work is the wrong shape.

**Write nothing without the candidate's approval of the wording.** A badly
phrased achievement propagates into every CV generated afterwards, and it is
the candidate who has to defend it in a room. Show the sentence, get a yes,
then write — and record the outcome:

```bash
python3 …/achievements.py asked --outcome recorded
```

**Phrase it so it survives a question.** What was done, at what scale, over
what period, with what result — not an adjective. *"Three fitted kitchens
delivered between March and August, from measurement to installation"* answers
a follow-up; *"experienced in bespoke joinery"* invites one it cannot survive.

### 2. Offer the LinkedIn version, and never post it

**An enriched local file beside a stale public profile is half the benefit.**
So offer the text, ready to paste, and say where it goes — the *Experience*
entry, *Licences & certifications*, the *About* summary.

**The candidate publishes it themselves.** The plugin does not post on their
behalf, for the same reason it does not send an application or transmit an ORP
declaration: **an action taken in someone's name is theirs to take.**

*(And LinkedIn is read in the user's own browser, never fetched by a script —
`shared/robots-policy.md` records that it refuses this agent by name.)*

## What this never does

- **Scan the disk**, or any repository, looking for work to claim.
- **Turn into a questionnaire.** One open question, once a month.
- **Write to the dossier without validation.** See above: the CV inherits it.
- **Store the answer in its own state file.** `.achievements.json` holds *when*
  the question was asked and *what came of it* — never the content. The content
  belongs in the candidate's files, which are the ones they can read and
  correct.
