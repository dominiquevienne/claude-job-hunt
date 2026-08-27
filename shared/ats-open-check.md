# Is the ad still open? Asking the employer's ATS directly

Used by `cover-letter` **step 1b**, when an ad is in the at-risk band and the
question *"is anyone still reading applications?"* has to be answered before a
dossier is written.

This file is **not** a board adapter and never will be. `shared/boards/*.md`
exists so `job-scan` can **sweep** a board. This exists so step 1b can **ask one
question about one ad**. The two needs look similar and are not: a host can be
useless for sweeping and excellent as an oracle, which is exactly the case for
every entry below.

## Why a direct request beats every other route

The board is the least reliable place to ask. A board will happily serve the
full description of a dead ad — the *"no longer accepting applications"* banner
is rendered client-side and never reaches fetched markdown. **The employer's own
applicant tracking system has no reason to lie**: when the requisition closes,
the ATS stops serving it, usually with a status code.

So when an ad's *apply* link points at a host below, **one request settles what
a careers-page search only suggests.**

## The hosts, and exactly what they answer

Match on **status code first, page title second, body text last** — bodies are
localised and get rewritten; status codes do not.

### Haufe / Abacus umantis — a strong, status-code signal

- **Recognise it by the path**, not the host: `/Vacancies/<numeric id>/Description/2`.
  Employers front it either with `recruitingapp-<n>.umantis.com` or a vanity
  domain of their own (`jobs.<employer>.com`), so **the host tells you nothing
  and the path tells you everything.**
- **The trailing `2` is required.** It is *not* a language or view index.

| Response | Reading |
| :-- | :-- |
| **`200`** + a real job title in `<title>` | **Open.** |
| **`403`** | **Not open** — closed, withdrawn, or never existed. Body is localised (*"Invalid permission"* / *"Fehlende Berechtigung"*); **match the 403, not the words.** |
| `404` | Malformed path — you got the URL shape wrong, not an answer about the ad. |
| `200` + `<title>` is `Applicant Management` | **Wrong trailing segment** (`/1`, `/99`…). The ATS shell, not a description. **Not an answer** — retry with `/2`. |

**Verified 2026-08-27 on two unrelated tenants, in two locales.** The decisive
case: a vacancy on `recruitingapp-2698.umantis.com` that a search engine had
indexed — so it was open when crawled — answered **403** when requested. That is
a genuinely closed vacancy returning 403, not merely an unknown id.

**The site root is usually gated by SSO. That does not matter** — the direct
vacancy URL answers unauthenticated, which is the whole value.

### Jobvite — a weak, title-only signal. Affirmative use only.

- Path: `jobs.jobvite.com/<employer>/job/<opaque token>`
- **Jobvite never returns an error status.** Every request below answered `200`.

| Response | Reading |
| :-- | :-- |
| `200` + `<title>` = `<Employer> Careers - <Job Title>` | **Listed.** |
| `200` + `<title>` = `<Employer> Careers` (bare) | Token is unknown or malformed. **Not proof the ad closed.** |
| `200` + Jobvite's own support page | The employer segment is wrong. |

> **What a genuinely *closed* Jobvite vacancy returns is UNVERIFIED.** Only the
> bogus-token state was tested. It may well keep serving the description.
> **So Jobvite is trustworthy in one direction only:** a real job title means
> listed; anything else means *ask another way*, never *the ad is dead*.

### The ones already named in step 1b

Factorial, Workday, Greenhouse, Lever and SmartRecruiters close a requisition
with unambiguous prose — *"This job opening doesn't exist anymore"*. Step 1b has
always said so; no table needed, because the page tells you in words.

## Rules

- **Never infer closure from a signal not verified for closure.** An unverified
  host earns *"could not verify"*, which is a reportable outcome under
  `shared/never-fail-silently.md` — not a silent assumption either way.
- **Never guess a vacancy id or a URL shape** to manufacture an answer. Probing
  ids to learn a host's *behaviour* is fine and is how this file was written;
  probing them to decide a specific ad's fate is not.
- **Report the route at the gate**, naming host and response: *"verified live —
  employer's umantis posting answers 200 with the job title"* is a finding a
  user can weigh. *"Looks open"* is not.
- **A host that is not listed here is not a failure.** Say you could not verify
  and why, then carry on. Adding a host means testing its **closed** state, not
  just its open one — that is the whole difference between the two entries above.

## Adding a host

One entry costs a handful of requests, and the closed state is the only part
that is hard:

1. Fetch a **known-open** vacancy. Record status and `<title>`.
2. Find a **known-closed** one — the reliable trick is a search engine's index:
   anything indexed was open when crawled, so a stale result is a closed-vacancy
   candidate. Record status and `<title>`.
3. Fetch a **malformed** id and a **wrong tenant**, to learn what "you asked
   wrong" looks like versus "the ad is gone".
4. Repeat on a **second, unrelated tenant** — one employer's configuration is
   not a vendor's behaviour.
5. Write down what you observed and **only** what you observed. A guessed row
   here produces a confident, wrong "this ad is closed" — which costs the user a
   real opportunity, the most expensive mistake this plugin can make.
