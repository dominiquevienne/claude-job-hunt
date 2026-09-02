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
