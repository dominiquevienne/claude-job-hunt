# Candidate — the record that overrides everything else

Lives at `$JOB_HUNT_HOME/candidate.md`. Written by `/job-setup`, then edited by
hand whenever something changes. Read in full on every run.

This file holds what `config.yml` cannot: the decisions the user does not want
re-litigated every week, and the corrections that override a stale export.

*The example below describes a fictional person. Replace all of it.*

---

## Identity

- **Full name:** Ada Lovelace
- **Filename form:** `Lovelace_Ada_<Company>` — e.g. `Lovelace_Ada_Acme.pdf`
  and `Lovelace_Ada_Acme_CoverLetter.pdf`.

  **Why the company is in the filename.** Without it every application produces
  the same two names, and a job board's "previously uploaded" list shows several
  identical entries with no path and no way to tell them apart — which is how a
  cover letter ends up submitted in the resume slot, or a resume tailored to a
  different employer goes out. The company suffix makes each file identifiable.

  Dossiers already sent keep their original filenames: they record what the
  recipient actually received.
- **Default job title line:** `Senior Full Stack Developer · Laravel / PHP ·
  Engineering Lead` — tailor the wording to each ad, keeping it truthful.

## Target roles — what counts as on-profile

State every role family that is a valid target, and say so explicitly, because
scoring must not penalise any of them.

1. **Hands-on senior engineering** — senior or lead backend / full-stack
   developer.
2. **Lead and management roles** — team lead, engineering manager, project
   manager, head of engineering, CTO. **A role with no hands-on development is
   explicitly fine.**

> Do not treat "this role has no coding" as a gap, a downgrade, or a reason to
> recommend against applying.

**Practical consequence for drafting:** a management ad needs a *differently
framed* resume and letter — leadership, team building, process, delivery and
stakeholder work in front, stack depth as supporting evidence. It is a different
document, not a reworded one.

## Hard blockers — the rules that stop an application

List them here so no run has to rediscover them.

### The ad's primary backend language

**A primary backend language with no production experience behind it is a hard
blocker, and "or willingness to learn" does not soften it.** Score it `0`, name
it in the go/no-go headline, and recommend not applying — even when every other
line scores near 1.

That clause describes the *employer's* flexibility, not the candidate's
interest. A role that writes Go daily is a Go role.

- **The language, not the framework.** The same language with an unfamiliar
  framework is a partial gap, not a blocker.
- **Never draft first and ask later.** If the role looks otherwise excellent,
  ask at the gate whether that specific language interests the candidate
  *before* writing a line.

### Others

- Certifications the ad requires and the candidate does not hold.
- A working language the candidate does not have (see below).
- A commute beyond `location.max_commute_minutes` — filtered before scoring.

## Search posture — how selective to be right now

Circumstances change what a good application is. Record the current posture and
**the date it was set**, so a later run knows whether it still applies.

> *Set 2026-01-15.* Normal posture: apply above 70 %, prefer fit over volume.
>
> When time or income is short, lower the bar to ~50 % and say so here: speed
> and volume then beat perfect fit, a 55 % application sent this week is worth
> more than a 90 % one found in three months. **A hard blocker still stops an
> application** — those waste time rather than saving it.

## Compensation — context a number cannot hold

`config.yml` holds the floor and the currency. This is where the *posture* goes,
and it is what stops a figure from being read mechanically.

> *Example, set 2026-01-15.* A range below the floor is worth reporting, not
> worth refusing over: a role that pays under market but starts in three weeks
> can beat one that pays well and starts in five months. Report the figure
> plainly and let me decide.
>
> Equity is not salary. Report it separately and do not fold it into the range.
>
> For a foreign employer, the question to raise before signing is which
> social-security system applies — it changes both take-home pay and what the
> contributions build toward. Never a reason not to apply.

Whatever is written here **overrides the default reading of the number**. If it
says income now outranks the figure, a low range is information, not a blocker.

## Standing resume content

Anything that must appear on **every** resume, with the exact wording, in each
language used. Keep it to what the factual record supports.

> *Example.* Every resume carries a Skills line on AI-assisted development:
>
> **AI-assisted development:** working with AI coding agents under written
> engineering standards — architecture and testing conventions the agent must
> satisfy, enforced by static analysis and coverage gates in continuous
> integration rather than by review alone.
>
> Never claim employer-level AI rollout or policy ownership unless the record
> supports it.

## Contact

- **Email:** ada@example.com
- **Phone:** +44 7700 900000
- **Address:** 12 Analytical Street, Bristol BS1 4XX, United Kingdom
- **City used in the letter's date line:** Bristol
- **LinkedIn:** https://www.linkedin.com/in/adalovelace
- **GitHub:** https://github.com/adalovelace

**Contact line (EN):**

```
ada@example.com  ·  +44 7700 900000  ·  Bristol, United Kingdom  ·  linkedin.com/in/adalovelace  ·  github.com/adalovelace
```

## Languages

- English — native
- French — full professional
- German — **A2, schoolroom level and rusty.** Understands and gets by; does
  **not** write, negotiate or interview in German. Score `0` on any ad requiring
  professional German, and **never list it in a resume or letter** — the level
  is below what an employer means by the word.

> Note the trap: years spent living in a country does not imply proficiency in
> its language. Do not infer one from the other.

## Corrections to the exports

The documents in `profile/` are snapshots and can lag reality. **The entries
below override them.** Keep the list short and factual, and clear an entry once
the export itself has been refreshed.

- *Example.* **Acme — framework version:** the platform runs on Laravel 13, not
  Laravel 11 as stated in `experience.pdf` (confirmed 2026-01-10). The rest of
  the stack is unchanged.

## Signature

`$JOB_HUNT_HOME/signature.png` — the handwritten signature, keyed out of its
paper background. It is near-square, so **size it by height**; a width-based
`\includegraphics` blows it out of proportion.

In `cover-letter.md`, replace the `\vspace{45pt}` placeholder with:

```latex
\vspace{10pt}

\hfill\includegraphics[height=2.2cm]{<absolute path to signature.png>}\hspace{2cm}

\vspace{-6pt}

\hfill Ada Lovelace\hspace{1.5cm}
```

`height=2.2cm` is a good default — adjust between 1.8 cm and 2.6 cm. The
signature's wider trailing `\hspace` puts it slightly left of the typed name,
which reads more naturally than strict alignment. With no signature file, keep
the original `\vspace{45pt}` and sign the printed page by hand.

Regenerate from a fresh scan with `make-signature.sh`.
