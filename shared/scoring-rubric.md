# Scoring an ad against the candidate

One rubric, used by **both** skills, so the numbers stay comparable end to end:
`job-scan` scores fast and shallow from the ad, `cover-letter` re-scores deeply
before drafting. A score that means something different in each skill is worse
than no score at all.

## Method

Take the ad's requirements, one line each. Score each line against the
**factual record** — `profile/`, `candidate.md`, `repos.md` (see
`shared/workspace.md` for precedence):

- **`1`** — genuinely met, with production experience behind it.
- **`0.5`** — partially met, adjacent, or non-professional only (a side project,
  a prototype, a language at passive level).
- **`0`** — absent.

`repos.md` decides the borderline calls: it states which technologies are
professional-depth, which are prototype-level, and which must stay at `0` no
matter how tempting the adjacency. **Scoring a line above what the record
supports is the single easiest way to make this whole exercise worthless.**

Then weight each line by how central it is **to this specific role**, totalling
100. For a hands-on developer role the stack *is* the job, so the core technical
requirements carry the bulk of the weight:

| Block | Typical weight |
| :-- | :-- |
| Backend language / runtime the ad names | 25–30 |
| Frontend framework + language the ad names | 15–20 |
| Other role-critical tech (data, ML, mobile…) | 10 |
| Database | 10 |
| Cloud / infrastructure platform | 10 |
| Containerization / tooling | 5 |
| Years of experience / seniority | 5 |
| Engineering practice (review, testing, pipelines) | 5 |
| Domain or industry knowledge | 5 |

Reweight for a role that is not hands-on: for a lead or management ad, team
size, delivery ownership, process and stakeholder work carry the weight, and
stack depth becomes supporting evidence.

Sum to a **fit ratio in percent**.

## Bands

| Ratio | Reading |
| :-- | :-- |
| **≥ 75 %** | Strong fit — apply |
| **55–74 %** | Good fit — apply, foreground the matches |
| **40–54 %** | Moderate — worth it only with a genuinely strong angle |
| **25–39 %** | Low — likely filtered out before a human reads it |
| **< 25 %** | Very low — recommend not applying |

The user's own `thresholds.apply_from` in `config.yml` overrides where the
"apply" line sits. The bands still describe what the number *means*.

## What overrides the number

**Before scoring on a number, ask where it came from.** A salary may be a
conversion whose label did not travel with it, an estimator's output wearing
the employer's name, or minor units read as whole ones — wrong by 100 or by
250, and plausible either way. `shared/plausible-and-false.md` lists the
mechanisms; the short form is that a figure this rubric weighs must be one the
advertiser stated, and the adapter's field name says which it is.

## Before a score is written: both directions, against `profile/`

**Every must-have the ad names is matched against `profile/`, and every gap
asserted is proven there.** Two halves, and the rule needs both — they are the
same omission running in opposite directions, and both were measured in one
session on 2026-09-02:

| | What went wrong | Cost |
| :-- | :-- | --: |
| **A gap asserted that is false** | GraphQL called missing; `profile/skills.pdf` contradicts it | **65% → 80%** |
| **A must-have never checked** | CMS experience stated by the ad, simply absent from the scoring — and a strong point of the record | **63% → 72%** |

**One error cost the candidate and the other flattered the ad, and both come
from scoring against the ad's description without opening the record.** A
requirement the ad states and the scorer never checks is the same failure as a
false gap, and it is the quieter of the two.

### The record is `profile/`, and it is now greppable

`candidate.md` and `repos.md` are not a skills inventory. The inventory is in
the `profile/` PDFs — which is why the wrong answer used to be cheaper than the
right one, and why the cheap one won. **`sync-sources.sh` now extracts every
PDF to `profile/.text/`**, so the check is one command:

```bash
grep -ril "confluence" "$JOB_HUNT_HOME/profile/.text/"
```

**Not finding a term there is evidence. Not having looked is not.** Where the
search cannot be run at all — no `pdftotext`, no `profile/` — **the honest
output is a question to the user, never an assertion of absence.**

### A gap in a ledger `Note` is a lead, not a proof

It was written by an earlier run, possibly against sources that did not include
the inventory. Re-prove it or drop it.

**And a gap that is disproved does not simply vanish — it becomes an evidence
line.** The candidate needs to know they can answer that question well, which
is the opposite of what a false gap does to them: a briefing once told somebody
Confluence was *"not documented in the file"* and handed them a sentence to
deflect it with. They use it daily, it is in `skills.pdf` with eight
experiences behind it, and they concluded their own record was incomplete.

**A false positive gets caught in the room; a false negative never does.**
Claim an experience the candidate lacks and the interviewer probes it. Concede
a requirement they meet, and nobody present knows to correct it. Issue #63.

**A `0` on a stated must-have caps the score, whatever the total.** Say so in
the headline. In practice these are automatic filters, and no amount of
tailoring writes around them:

- A **spoken language** the candidate does not have at working level. An ad
  written in a language they cannot interview in is a blocker, whatever the
  stack. Passive knowledge is not working knowledge — see `config.yml`.
- **Work authorization** the candidate lacks — **and this one is not a
  discard**, see below. It caps the score for a *local employment contract*
  and says so; it never removes the ad.
- A **required certification** the candidate does not hold.
- A **commute that cannot be made** — see below. This one is not scored at all.
- Whatever `candidate.md` records as a **hard blocker** for this user. That file
  is where they wrote down the rules they do not want re-litigated every run;
  a rule stated there is not a preference to weigh, it is a stop.

## A preference is not a score, and it must never enter the ratio

**The plugin knows how well an ad *fits*. It knows nothing about what the user
*wants*** — and `employers.md` now carries one field for it: `preferred`,
`excluded`, or absent, which means **never asked** and not neutral.

**The red line: a preference never adds a point.** This file already forbids
inflating a line to reach a threshold and softening a bad ratio. **A favoured
employer that quietly raises a score stops the score measuring fit** and turns
it into a blend of fit and appetite — unreadable three weeks later, when the
candidate rereads their own ledger and cannot tell which of the two they are
looking at.

> *"55%, and this is an employer you favour"* is information.
> *"68%"* for the same ad is a lie.

**What a favoured employer actually changes is the cadence, not the ranking**,
and that is the counter-intuitive half. Measured on the case that produced the
field: four ads open at one employer on the same day, and the candidate
**froze** them — *not because the interest was low, because it was high enough
not to spray*. Then lifted the freeze eight days later on a dated argument.
Neither decision was a ranking.

So a preference acts on:

1. **Cadence** — how many applications run at once there, and what to wait
   between them.
2. **Effort** — deeper research, a more worked letter, and a threshold lowered
   **knowingly**, which is not the same as a score raised silently.
3. **The memory of the relationship** — former employer, earlier refusal,
   application in flight.

**And `excluded` does not silently drop anything.** Ads from an excluded
employer are not proposed, **and the run says how many it withheld and why** —
*"3 ads from Acme not proposed: employer excluded 2026-09-03"*. A filter with
no counter is the silent cap `shared/never-fail-silently.md` forbids, and this
one would hide exactly the ad that makes somebody change their mind.

**A refusal is not a freeze.** A freeze is bounded and lives in the standing
decisions with its lifting date; *"I do not want to work there"* is stable and
lives in the preference field. **Confusing them reproduces the error of
2026-09-02 in either direction** — a permanent refusal treated as temporary, or
a freeze nobody ever lifts. Issues #94 and #95.

## A country list is not a workplace

**A card carrying a list of countries and no city is "remote, open to your
country" — never "a job in your country".** Some boards publish the
jurisdictions an employer will hire from: **6.5 of them on average on a remote
ad**, against 1.9 elsewhere, and on 200 measured cards **63% carried no city at
all**. See `shared/boards/hiringcafe.md`.

**Score it as what it is.** Such an ad is worth finding — a remote role open to
Switzerland is exactly what this plugin should surface — but **the commute rule
has nothing to apply to**, and ranking it beside a local ad misrepresents it.
Say *remote, open to your country* in the row, and let the user weigh it.

## The right to work is not shaped like the commute, and must not be filtered like it

`location.work_authorization` in `config.yml` lists the countries and zones
where the user needs no sponsorship. When an ad's **employer** sits outside it,
the run says one thing and removes nothing:

> **A local employment contract there needs sponsorship you have not declared —
> that is a stop on the employed route, not on the ad.** Invoicing that country
> from where you are is a different legal object and may well be open.

**Score the ad, show the score, then say it.** The score is what tells somebody
the job was worth wanting, and the B2B route stays open without any permit —
so a silent drop would destroy real opportunities invisibly, which is the
failure `shared/never-fail-silently.md` forbids. That is the difference from
the commute below: a body cannot be in two places, but a contract can take two
forms.

**The country that matters is the employer's, not the desk's.** *A remote post
with a British employer is still British employment*, and this is the case that
will keep catching people — the ad that produced this rule advertised "hybrid
and remote working arrangements available".

**With no `work_authorization` configured, nothing is flagged.** The user who
skipped that question gets exactly the previous behaviour. Issue #82, and
`skills/job-scan/scripts/_workauth.py` holds the zone lists.

## A driving licence is a must-have with no second route, and nobody was asked

`location.driving_licence` (the categories held, `[]` for none) and
`location.own_vehicle`. **Two fields, because ads ask for one, the other, or
both** — the capacity to drive and having a car are different things, and the
difference is what decides field roles.

**This is #82's shape on another field: the rule above could always treat a
stated must-have as a capping zero, and nothing ever collected the value.** A
Meanquest ad on 2026-09-03 printed *"Permis de conduire obligatoire"* in a list
where ITIL was explicitly only a plus; `candidate.md`, `repos.md` and five
profile PDFs answered nothing, and the run wrote *"to verify before drafting"*
into the ledger — the right reaction, and one that **turns a stable fact into a
question re-asked at every ad**. Issue #91.

**Three states, and the middle one is why it is never a filter.**

| Config | Ad states it as a must-have | What the run does |
| :-- | :-- | :-- |
| **Key absent** — never asked | — | **Ask at the gate**, and offer to record it once. Never a discard: absent from the file is not a no |
| `driving_licence: []` / `own_vehicle: false` | yes | **Say it before a dossier is spent.** The ad keeps its score and is not removed |
| A category / `true` | yes | Nothing. It is satisfied |

**And the asymmetry is the reason for that middle row.** A false *"they do not
have it"* costs an ad wrongly dropped, silently; a false *"they have it"* costs
an interview. Both are real, they land in different places, and only the first
is invisible.

**Unlike the right to work, there is no second route.** That section splits an
ad into *employment excluded, service provision perhaps open*. **A licence
required is a licence required** — there is no equivalent door, and offering
one would be a comfort rather than an option.

**Do not detect it by searching for `permis`.** In one workspace, 13
`permis <word>` matches broke down as **7 driving licence, 5 work permit and 1
past participle of *permettre***; `permis` is the prefix of *permissions*; and
bare `vehicle` matched this repository's own *employment vehicle* in 5 of 45 ad
files, none of them a car. `skills/job-scan/scripts/_licence.py` is an
allow-list of phrases, and **`permis B` on a Swiss ad is a residence permit** —
it raises a question and never a verdict.

## The commute is a filter, not a score line

An ad requiring regular physical presence beyond `location.max_commute_minutes`
is **discarded before scoring**. Never score it and then discuss it: a strong
stack fit is exactly the case where a good number tempts everyone into
re-proposing something the candidate cannot physically take.

It applies to the **presence requirement**, not the label on the ad:

| Work mode | Treatment |
| :-- | :-- |
| On-site beyond the limit | Discard — the daily commute is impossible |
| Hybrid beyond the limit | Discard — hybrid still means regular days on site |
| Remote with a distant head office | **Keep** — quarterly meetups are not a commute |
| Remote but demanding weekly or monthly on-site days beyond the limit | Discard — usually only visible in the description; downgrade the row when you read it |

Two traps seen in real scans:

- **Job-board geocoding lies.** Boards render odd locations for fully remote
  ads — a village name that has nothing to do with the employer. Never discard
  on a location string alone when the card also says *Remote*; check the
  description's own wording.
- **Multi-site ads.** An ad listing several offices is judged on its *nearest*
  site; discard only if even that one is beyond the limit.

Use `commute.md` for travel times rather than guessing. When a listed place sits
right at the limit, keep the ad and note the commute rather than discarding it.

## Honesty rules

- **Mark a score provisional (`~`)** when it comes from the card alone — title,
  company, location — because the description was not opened. Never present a
  provisional score as if the ad had been read.
- **Never soften a bad ratio** to make an application feel worth writing. The
  honest answer is sometimes "don't apply", and it saves the user more time than
  any tailoring.
- **Never inflate a line to reach a threshold.** If the total lands just under
  the user's `apply_from`, say so and let them decide — that is what the
  go/no-go gate is for.
