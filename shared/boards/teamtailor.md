# Board adapter — Teamtailor

<!-- verified: 2026-09-02 -->

<!-- hosts: teamtailor.com -->
<!-- script: ats.py -->
**Re-verified 2026-09-02 against three tenants for the fetch, and against
nine for the `robots.txt` question — see *There is no platform policy here*** — `investengine`, `polestar`
and `oatly` — all three answering with live postings on the documented route.
The repository's rule is two tenants minimum for an ATS family, because what
does not vary at the first client is not a property of the API.

One employer at a time, by tenant. **No browser, no account, no cookie.** Same
family and same script as `greenhouse.md`, `lever.md`, `ashby.md`,
`smartrecruiters.md` and `workable.md`: `skills/job-scan/scripts/ats.py`.

**Everything here was measured against the live feed on 2026-08-31.**

## Configuration

```yaml
boards:
  teamtailor:
    enabled: true
    employers: ["investengine", "…"]
```

The tenant is the **subdomain**, read off `<tenant>.teamtailor.com`. Most
employers also expose a vanity host — `careers.<company>.com` — and that is
usually the URL you will have in hand. **The tenant is still the subdomain**;
see below for why the vanity host is not what this adapter reads.

## Usage

```bash
ats.py list --provider teamtailor --tenant investengine
ats.py ad   --provider teamtailor --tenant investengine --id 7718928
```

## Read `<tenant>.teamtailor.com`, never `careers.<company>.com`

Both hosts answer `/jobs.json`, both return HTTP 200, and both look like the
employer's board. **They do not serve the same ads.** Measured on one tenant on
the same day, minutes apart:

| | Ads | Only there |
| :-- | --: | --: |
| `<tenant>.teamtailor.com` | **16** | 8 |
| `careers.<company>.com` | 13 | 5 |
| in common | 8 | |

The split is not random. Everything exclusive to the platform host was published
**2026-07-24 → 2026-08-24**; everything exclusive to the vanity host,
**2026-05-07 → 2026-07-13**. The vanity domain is a **stale mirror**: it misses
every recent vacancy and keeps ads the platform has already dropped.

Reading it would produce the two failures this plugin exists to avoid — missing
the new roles entirely, and scoring dead ones as live.

## The feed

```
GET https://<tenant>.teamtailor.com/jobs.json
```

HTTP 200, `application/feed+json` (JSON Feed 1.1), unauthenticated, **no paging**
— the whole board in one request, descriptions included. There is an
`/jobs.rss` alongside it carrying an `xmlns:tt` locations namespace; unexamined,
because the JSON feed answers everything the adapter needs.

## There is no platform policy here — there is a per-tenant answer

**This file used to record one tenant's `Content-Signal` as Teamtailor's.**
That was wrong, and it was wrong in the direction that matters. Measured on
**nine live tenants, 2026-09-02**:

| Tenants | `Content-Signal` |
| :-- | :-- |
| investengine, oatly, anyfin, centiro, firstcamp, brandimpact, ginatricotsverige | `search=yes, ai-train=no, **ai-input=yes**` |
| **polestar, normative** | `search=no, ai-train=no, **ai-input=no**` |

**Seven permit, two refuse.** Teamtailor gives every customer its own
hostname, so each one answers for itself, and `ai-input=no` is an operator
asking that its content not be read into an AI system — which is what a sweep
that scores does. `shared/robots-policy.md` and issue #48 say a person-driven
agent is not a harvester; that answers `ai-train`, and it does not answer
`ai-input`.

**So there is nothing here to quote as the platform's position.** The rule is
the procedure, not the verdict:

> **Read `https://<tenant>.teamtailor.com/robots.txt` before sweeping that
> tenant.** `ats.py` does it now, through
> `skills/job-scan/scripts/_robots.py`, and exits 7 naming the tenant when the
> answer is no. Issue #73.

Two practical notes from taking the measurement:

- **A tenant that does not exist answers `robots.txt` with 1 076 bytes of
  HTML and HTTP 404** — `volvocars`, `aiven`, `kry` and `epidemicsound` all
  did. Counting `Disallow` lines in that reads as "zero rules, everything
  allowed". The helper checks the `Content-Type` first, calls it unreadable,
  and **passes** — a 404 is not a refusal, and inventing one would be the
  symmetric error.
- **Three tenants gave three different md5s** and looked like three policies.
  Removing the `Sitemap:` lines — the rule in `shared/robots-policy.md` —
  leaves two identical to the bit, and the real divergence is **one line**:
  the `Content-Signal`. The hash said "three policies"; the diff said "one
  exception, and which".

Beyond that signal, the file disallows `/app/`, `/messages/`, `/messenger/`
and `/jobs/internal/` on the tenants sampled, and **`/jobs.json` is not
disallowed**.

## The id is in the JobPosting block, not in `id`

Each item carries an `id` that is a **UUID appearing in no URL** — pasting it
into a browser gets you nothing. The usable id is the number in
`_jobposting.identifier.value`, which is also the numeric prefix of the ad slug:

```
https://<tenant>.teamtailor.com/jobs/7718928-senior-engineering-manager
                                     ^^^^^^^
```

The adapter uses that, falling back to the slug when the JobPosting block is
missing. Ledger rows read `teamtailor:<tenant>:<numeric id>`.

## What the feed does NOT publish

Measured across 16 ads on one tenant:

| Field | Present |
| :-- | --: |
| `jobLocation` with a full postal address | **13 / 16** |
| `employmentType` | **0 / 16** |
| `baseSalary` | **0 / 16** |
| `validThrough` | **0 / 16** |
| `jobLocationType` / `applicantLocationRequirements` | **0 / 16** |

So `employment_type` and `remote` are always `null` on the card. **They are not
inferred from the description**, and an ad that says "Fully Remote" in its body
still reports `remote: null` — a guess dressed as a field is worse than an
honest blank.

**No `validThrough` means no expiry signal.** Absence from the listing is the
only closure evidence this board gives — which is reliable, since the endpoint
returns the employer's whole live board every time, but it means step 1b of
`cover-letter` has nothing to read here beyond age.

## What it does publish, and nothing else here does

The 13 ads that carry `jobLocation` give a **complete postal address**:

```json
{"streetAddress": "47-51 Great Suffolk St", "addressLocality": "London",
 "postalCode": "SE1 0BS", "addressCountry": "GB"}
```

The card exposes it as `address`. That is the field the `job-room-ch` module
records as the one that goes missing most often on a PRE — street and postcode,
straight from the employer.

## Exit codes

| Code | Meaning |
| :-- | :-- |
| `4` | no such tenant — `<tenant>.teamtailor.com` answers a clean **404** |
| `3` | `ad` was asked for an id no longer on the board — filled or pulled, record it `discarded` |

**A wrong tenant is unambiguous here**, unlike SmartRecruiters: an unknown
subdomain returns 404 with an empty body rather than an empty board that looks
like an employer with nothing open.
