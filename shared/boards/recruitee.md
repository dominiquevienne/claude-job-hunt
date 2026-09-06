# Board adapter — Recruitee (European ATS)

**Recruitee is Tellent, and the tenant hosts have not moved with it.**
Measured 2026-09-03: `jobs.recruitee.com/robots.txt` answers from
**`careers.tellent.com`** — 81 bytes, `Disallow: /v/`, one sitemap — while a
tenant host such as `tellent.recruitee.com` **still serves its own 31-byte
file under `recruitee.com`**, with the same `Disallow: /v/`.

**So the rebrand has reached the generic entry point and not the tenants**,
which is the half that matters here: this adapter reads
`<tenant>.recruitee.com/api/offers/`, and that address answers for itself.
Nothing in either file refuses it.

<!-- hosts: jobs.recruitee.com, tellent.recruitee.com -->
<!-- script: recruitee.py -->
<!-- countries: * -->

One employer at a time, by tenant. Recruitee is a Dutch-origin ATS, now part of
Tellent, used across the Netherlands, Belgium, Germany, Poland and beyond. Each
tenant publishes its **whole board as public JSON**.

**Measured on 238 offers across six tenants on 2026-09-01.**

## Access

```
GET https://<tenant>.recruitee.com/api/offers/   → every published offer
https://<tenant>.recruitee.com/o/<slug>          → the ad, for a human
```

**No browser, no account, no key.** One request returns the employer's entire
board **with descriptions** — 145 offers in a single 454 KB response on the
largest tenant measured. No pagination, no window, no second call per ad; the
same shape as `workable.md` and `flatchr.md`.

`robots.txt` is two lines — `User-Agent: *`, `Disallow: /v/` — so the API path
is not disallowed, and no crawler or AI agent is named.

```bash
python3 "${JOB_HUNT_ROOT}/skills/job-scan/scripts/recruitee.py" \
  jobs --tenant gmk
```

## Configuration

```yaml
boards:
  recruitee:
    enabled: true
    tenants:
      - "gmk"
      - "ballastnedam.recruitee.com"
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `tenants` | yes | Tenant name or careers hostname |
| `country_code` | no | ISO-2. **Filter on the code, never on the label** — trap 2 |
| `city` | no | Substring of the city |

**A tenant that does not exist answers JSON**, `{"error":"Not Found"}` with a
404 — which is better than most of this family: `smartrecruiters.md` records
that a wrong tenant there is indistinguishable from an employer with nothing
open. Here the two are distinguishable, and the adapter says which it got.

### Finding tenants

Recruitee publishes no directory and no cross-tenant search. `recruitee.py
tenants --country NL` reads HiringCafe's cards and extracts the Recruitee hosts
from their apply URLs — which is how the six tenants measured for this adapter
were found, 22 in two pages of Dutch cards.

**It is a hint, not a census.** HiringCafe indexes a fraction of Recruitee, so
an employer missing from that list is not an employer without a board. Ask the
user for the careers URL when they have one.

## Traps

**1. The salary object is always there, the figure often is, and the unit is
the thing that will hurt you.**

| | |
| :-- | --: |
| `salary` object present | **238/238** |
| …with an actual figure | **133/238** |

The first line is the shape `platsbanken.md` and `turijobs.md` both punish — a
presence check reports total coverage. **But unlike those two, this board
mostly means it**: 56% carry real numbers, which is better than every national
board here except `swissdevjobs.md`.

```json
"salary": {"min": "2990", "max": "3992", "period": "month", "currency": "EUR"}
```

**`period` is `month` on 124 of the 133**, `hour` on 6, `year` on 1, and absent
on 2. A Dutch monthly salary read as an annual one is **wrong by a factor of
twelve** — the same class of error as `join.md`'s minor units, where `2035`
means `20.35`, and `arbeitsagentur.md`'s hourly rates. `salary_period` sits
beside every figure and is never assumed.

*(A detail found by fixing the adapter's own counter: some offers carry a
`period` with no amount. Counting periods and figures together reported more
units than salaries — 50 periods against 39 figures on one tenant. The period
is now counted only where there is an amount to attach it to, and the orphans
are reported separately.)*

**2. The country is written in the tenant's own language, and the values mix.**

Across one sweep of six tenants:

```
Nederland 231 · Frankrijk 2 · Duitsland 2 · Switzerland 1 ·
Oostenrijk 1 · Denemarken 1
```

**Five Dutch names and one English one, in the same result set.** A filter
written `country == "Germany"` matches nothing; so does `country ==
"Netherlands"`. The label is whatever the tenant configured, and two tenants in
one sweep will not agree.

`country_code` is on **238 of 238** and is the only reliable one. The localised
string is carried beside it as `country_label` so it cannot be mistaken for a
key, and `--country-code` filters on the code.

*(This is `crit.md`'s `addressCountry: "France"` problem generalised: there one
board wrote the country's name where every other wrote `FR`. Here the *same*
field varies by tenant within one provider.)*

**3. `remote`, `hybrid` and `on_site` are three booleans and they overlap.**

| Combination | Offers |
| :-- | --: |
| `on_site` only | 120 |
| `hybrid` only | 67 |
| **`hybrid` and `on_site`** | **49** |
| `remote` and `on_site` | 1 |
| `remote`, `hybrid` and `on_site` | 1 |

They are not an enum. Reading `remote` alone misses the 49 that are
hybrid-and-on-site; **treating them as mutually exclusive misclassifies 51 of
238**. All three are emitted, plus a `work_model` list, and never a single
value.

## What the record carries

| Field | Coverage | Note |
| :-- | --: | :-- |
| `title`, `description` | 238/238 | Description median **1 829 characters** |
| `requirements` | 178/238 | **A separate field** from the description, empty on 60 |
| `company_name`, `department` | 238/238 | |
| `city`, `state_name`, `country_code` | 238/238 | |
| `postal_code` | 82/238 | |
| `locations` | 238/238 | More than one on **29** |
| `employment_type_code`, `experience_code`, `education_code` | 238/238 | |
| `published_at`, `updated_at` | 238/238 | Real per-ad timestamps |
| `careers_url`, `careers_apply_url` | 238/238 | The ad and the application form |
| `min_hours_per_week` / `max_` | most | Part-time hours, stated |

**`requirements` being separate is worth using.** `shared/scoring-rubric.md`
reads requirements rather than the whole ad, and only `join.md` and
`personio.md` also hand them over pre-separated.

**Two fields that promise and do not deliver.** `close_at` exists in the
payload and is set on **0 of 238** — there is no closing date on this board.
And `status` is `published` on **238 of 238**, because the endpoint serves
nothing else; it distinguishes nothing and is carried only so nobody
rediscovers that.

## Verification

```bash
S=skills/job-scan/scripts/recruitee.py
python3 $S tenants --country NL --pages 2 --plugin-root .
python3 $S jobs --tenant gmk
python3 $S jobs --tenant ballastnedam        # → reports the country and overlap warnings
python3 $S jobs --tenant notarealtenantxyz   # → must name the wrong tenant, not report zero
```
