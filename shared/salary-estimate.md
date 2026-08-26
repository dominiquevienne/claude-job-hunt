# Estimating the compensation range

Used by `cover-letter` at the go/no-go gate. The user is deciding whether to
spend an evening on an application; what the job pays is part of that decision,
and finding out at the offer stage is finding out too late.

**This is an estimate, and it must always look like one.** A confident figure
the user repeats in a negotiation, sourced from nothing, is worse than no figure
at all — it anchors them low, or prices them out, and they will never know which.

## Three tiers, and you must say which one you used

Work down the list. Stop at the first tier that applies.

### Tier A — the ad states it

Use it. Quote it as written, then normalise it (see *Basis* below) so it is
comparable with everything else the user has seen.

State whether the ad's range is a **band for the role** or "up to X" — the
latter is a ceiling advertised as a range, and the real offer sits below it.

### Tier B — the board publishes an estimate

Some boards attach their own model's estimate to the ad; jobup.ch does, as
`info-salary_estimate`, labelled *Estimation salariale de jobup.ch*.

Use it, and **name it for what it is**: the board's estimate, not the
employer's. Never let it read as though the company published a range. Where
both a Tier A and a Tier B figure exist and they disagree, give both and say so
— the gap is itself information.

### Tier C — derived

Nothing published. Now you reason, and the honesty burden is highest.

**Inputs that actually move the number:**

| Input | Effect |
| :-- | :-- |
| **Market** — country, and city within it | Dominant. A Swiss, German and Portuguese posting of the same role are not comparable |
| **Seniority the ad asks for** | Junior / senior / lead / head are different pay grades, not adjectives |
| **The candidate's own seniority and depth** | See *Where the candidate lands*, below |
| **Employer type** | Public sector and universities run published grids and pay under private market; agencies and consultancies take a margin; funded startups trade cash for equity; product companies pay above services companies |
| **Company size** | A 20-person shop and a 5000-person group price the same title differently |
| **Workload** | An 80% role pays 80%. Always normalise to full time before comparing, then state the actual figure |
| **Contract type** | Fixed-term, temporary and contract rates are not comparable with a permanent salary — a daily rate is not a salary divided by 220 |
| **Remote from a cheaper location** | Many employers index pay to the employee's location, not the head office's. Say so as a risk, not a certainty |

**Source discipline — the part that matters:**

- **Prefer something you actually checked.** If a public salary reference for
  that market and role is reachable, fetch it and cite it.
- **If you are reasoning from general knowledge, say exactly that**, in those
  words, and **widen the range** to match your real uncertainty.
- **Never cite a source you did not read.** A named report with a plausible
  figure is the most damaging thing this whole document exists to prevent.
- When you genuinely cannot estimate — an unfamiliar market, a role with no
  comparable — **say so and stop.** "I can't put a credible number on this
  market" is a valid, useful answer. Do not produce a range to avoid an empty
  space.

## Where the candidate lands in the range

The user asked what *they* would be paid, not what the role pays in the
abstract. The fit score from `shared/scoring-rubric.md` already did the work:

| Fit | Position in the range | Why |
| :-- | :-- | :-- |
| **≥ 75 %** | Upper half, and the top third when the seniority is met or exceeded | They meet the requirements the range was written for |
| **55–74 %** | Middle | Genuine gaps get priced in |
| **40–54 %** | Lower half, if an offer comes at all | The employer is taking a ramp-up risk and will price it |

Adjust for what the record shows beyond the ad's asks: years above the ad's
requirement, leadership history where the role is hands-on, a rare part of the
stack. And adjust **down** honestly for a missing must-have — a gap does not
disappear because the rest is strong.

**Never inflate this to make the opportunity look better.** The user is deciding
where to spend their week.

## Basis — state it every time

A number without its basis is unusable. Give all of it, in one line:

- **Gross or net** — say gross, and say so explicitly.
- **Period** — per year, per month, per day. Never leave it implied.
- **Instalments** — some markets pay 13 or 14 monthly instalments; a "monthly
  salary" there is not the annual figure over 12. Say which convention you used.
- **Workload** — the ad's percentage, and the full-time equivalent.
- **Currency** — the ad's own. If you convert, say the rate is indicative and
  moves.
- **What is excluded** — bonus, equity, pension contributions, allowances.
  Variable pay is not salary; present it separately or not at all.

## What to tell the user, at the gate

Three lines, no more. It sits next to the fit ratio, not in place of it:

> **Compensation** — CHF 115 000–135 000 gross/year at 100 % (Tier C, derived:
> senior Laravel role, Vaud, ~50-person product company; general market
> knowledge, no source checked). With an 82 % fit and 15 years' experience,
> the upper half is realistic — call it 125 000–135 000.
> The ad states no range; expect the question at first contact.

Then, only if it is decision-relevant:

- **Below the user's `compensation.floor`** → say it plainly, once. Do **not**
  turn it into a recommendation against applying unless they asked for that;
  `candidate.md` may record a posture where income now outranks the figure.
- **Foreign employer** → flag that which social-security system applies changes
  both take-home pay and entitlements, and that it is a question to ask before
  signing, never a reason not to apply.
- **Agency posting** → the advertised range is the agency's, and the client's
  budget is what actually pays.

## Where it goes, and where it must never go

**Record it** in the dossier's `job-ad.md`, under `## Compensation`, with its
tier, its basis and its date. That is what makes it re-readable in three weeks,
when an interview reaches the money conversation.

**And in the ledger's `Pay` column**, compact and with the tier letter —
`CHF 115–135k (C)`. The dossier holds the reasoning; the ledger holds the figure
in a form that makes a month of applications comparable at a glance, and shows
which numbers came from an employer and which were derived. Never overwrite a
better tier with a worse one, and leave `—` rather than invent. See
`shared/pipeline-format.md`.

**Say it again at the moment of submission.** At the Easy Apply gate the range
is repeated with its basis, together with the exact figure the user gave if the
form asked for one. A salary typed into an application anchors every
conversation that follows and cannot be withdrawn — that gate is the last place
it can be corrected.

**Never put a figure in the resume or the cover letter.** Not the estimate, not
the user's expectation. That number is the user's to disclose, at a moment of
their choosing, and a letter that opens with a price has made the choice for
them.

**Never auto-fill a salary-expectation field on a form.** The estimate is
material for the user's decision, not a substitute for it: show them the range,
say what it is based on, and **ask them for their number**. The rule in
`cover-letter` step 8.3 stands unchanged — an unanswerable question is left
blank and handed over. An estimate you produced does not make it answerable.

## When it does not apply

Skip the estimate entirely — and **say you skipped it, per
`shared/never-fail-silently.md`** — when the ad is a volunteer, internship or
equity-only posting, when the market is one you cannot assess, or when the user
has turned it off with `compensation.estimate: false`.
