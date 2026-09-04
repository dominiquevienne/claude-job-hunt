# Board adapter — free-work.com

<!-- hosts: www.free-work.com -->
<!-- script: freework.py -->
<!-- countries: FR -->

French **IT** roles, permanent and contract, on one public JSON API.
**No browser, no account, no cookie.**

Free-Work is the former Freelance-Info, which is why the contractor day rate is
first-class here — and why it is the only board in this plugin that carries one
at all.

**Everything below was measured against the live API on 2026-08-31.**

## Configuration

```yaml
boards:
  freework:
    enabled: true
```

No settings. Scope is set per search, not per config.

## Usage

```bash
freework.py list --search laravel
freework.py list --search php --contract permanent --pages 3
freework.py list --remote --posted-within-days 14
freework.py ad    --slug <slug>
freework.py check --slug <slug>
```

## The endpoint

```
GET https://www.free-work.com/api/job_postings?searchKeywords=<terms>&page=<n>
```

HTTP 200, JSON array, unauthenticated, **30 ads per page**.

`robots.txt` is among the most permissive this plugin reads — it disallows only
`/login`, `/logout` and `/fw-deals`, and explicitly **allows `OAI-SearchBot`**.
Nothing about the API or the search is disallowed.

## Three traps, and they are the reason to read this file

**1. `searchKeywords` is the only keyword parameter that filters.**

`query`, `search`, `q` and `skills` are all **accepted and silently ignored**:
the board answers 200 with the unfiltered feed, which is indistinguishable from
a search that matched everything. Measured — `?query=php` returned an ad titled
*"Ingénieur PKI"* as its first result.

**2. The page number never runs out.**

Past a ceiling the API keeps answering 200 with the *same* final page. Pages
**400 and 800 returned an identical set of 13 ads**. An adapter that stops only
on an empty page never stops.

`sweep()` therefore ends on the first page that adds **no unseen id**, and
dedupes as it goes. Measured: `--pages 50` (a 1 500-ad budget) terminates on its
own at **449 unique ads** in about 13 seconds.

**3. The key is the slug. The numeric id 404s.**

Every ad carries both `id` (numeric) and `slug`. Only the slug resolves:

```
/api/job_postings/665332                        → 404
/api/job_postings/fbo-ingenieur-pki-rennes-1828 → 200
```

The ledger row is `freework:<slug>`. `numeric_id` is kept on the card for
reference and is not usable as a key.

Bonus trap: `contracts` must be **scalar**. `contracts[]=permanent` is rejected
with *"Input value contracts contains a non-scalar value"* — a clean error, at
least, unlike the keyword parameters above.

## Two pay shapes, and they must never be merged

| Field | Meaning |
| :-- | :-- |
| `annual_salary_min` / `_max` | a **salary**, €/year — permanent roles |
| `daily_rate_min` / `_max` | a **contractor rate**, €/day — freelance missions |

Measured on one `laravel` search: 32 000–40 000 €/an and 55 000–60 000 €/an on
the permanent ads, 320–420 €/j and 100–470 €/j on the contract ones.

Both are the employer's own figures — **tier (A)** in
`shared/salary-estimate.md`. Do not convert one into the other, and do not
average them: a day rate is turnover for a contractor who carries their own
charges, not take-home pay.

## `expiredAt`, on every ad

A real expiry date, which almost no other board publishes. `check` reads it
directly instead of inferring staleness from age, and `cover-letter` step 1b
should do the same:

```json
{"slug": "...", "verdict": "open", "why": "published, expiredAt 2026-10-18"}
```

## Also on the card

`address` — street, postcode, town and region when the employer filled them,
which is what a `job-room-ch` PRE asks for; `contracts` (an ad can carry several);
`remote_mode` (`full` / `partial` / `none`); `experience_level`; `starts_at` and
`duration` for missions; `skills`; and **`external` / `external_source`**, which
flag an ad Free-Work republished from elsewhere rather than received first-hand.

## Exit codes

| Code | Meaning |
| :-- | :-- |
| `3` | `ad` or `check` on a slug that 404s, or a posting past its `expiredAt` |
| `2` | the API refused the request — the message is passed through verbatim |

`check` distinguishes `open`, `expired`, `unpublished` and `closed` rather than
collapsing them, because they are not the same news: an expired ad was real and
ran out, a closed one is gone from the board entirely.
