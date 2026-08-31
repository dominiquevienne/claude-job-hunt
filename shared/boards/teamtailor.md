# Board adapter — Teamtailor

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

`robots.txt` disallows `/app/`, `/messages/`, `/messenger/` and `/jobs/internal/`.
**`/jobs.json` is not disallowed**, and the file carries
`Content-Signal: search=yes, ai-train=no, ai-input=yes`.

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
