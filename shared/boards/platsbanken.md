# Board adapter — Platsbanken (Sweden)

<!-- hosts: arbetsformedlingen.se, jobsearch.api.jobtechdev.se -->

**39 865 live ads offering 67 109 posts**, from Arbetsförmedlingen — Sweden's
public employment service — through the JobTech Dev open API. The **sixth
national public employment service** here after `job-room.md` (CH),
`france-travail.md` (FR), `empleate.md` (ES), `arbeitsagentur.md` (DE) and
`jobsireland.md` (IE), and **the first Swedish adapter**.

**It carries the richest record of any board in this repository** — and the
tightest window onto it.

**Everything here was verified against the live API on 2026-09-01.**

## Access

```
GET https://jobsearch.api.jobtechdev.se/search?limit=100&offset=0
    &q=&municipality=&region=&occupation-field=&published-after=
https://arbetsformedlingen.se/platsbanken/annonser/<id>   → the ad, for a human
```

**No browser, no account, no key, no header.** Not "a key that happens to be
published" as on `arbeitsagentur.md` — there is nothing to send at all. It is
an open-data product of the Swedish state, published as such at
`jobtechdev.se`.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/platsbanken.py" \
  search --kommun 0180 --sedan 2026-09-01T00:00:00
```

## Two numbers in one response, and they mean different things

```json
{"total": {"value": 39865}, "positions": 67109, …}
```

`total` counts **advertisements**; `positions` counts **posts**. Across 300 ads
measured, `number_of_vacancies` summed to **413**, one ad offering ten.

Neither figure is wrong and neither is "the size of the board". `empleate.md`
has the same split — 1 558 announcements, ~3 438 plazas — but there it took two
endpoints and an arithmetic check to see it. **Here they sit side by side in
every response**, which is the honest way to publish it. Both are printed on
every run.

## The window is 2 100, and almost nothing fits in it

```
limit=100 & offset=2000  →  200, 100 ads
limit=100 & offset=2001  →  400
limit=101                →  400
```

`offset` stops at 2 000 and `limit` at 100, so **one query reaches 2 100 ads
out of 39 865** — a fifth of `arbeitsagentur.md`'s ceiling, on a board a
twenty-fifth the size.

**Unlike the German API, this one refuses honestly.** A request past the
ceiling is an HTTP 400 with a `tracking_id` and a stated cause, not a silent
truncation. That is the better failure and it is worth saying which board does
which: Germany hands you 10 000 of 45 901 and reports 45 901; Sweden hands you
an error. The adapter still checks before paging, so a run says *why* it
stopped rather than surfacing a 400.

### Measured, and it is unforgiving

| Query | Ads | |
| :-- | --: | :-- |
| *(no filter)* | 39 865 | unreachable |
| `municipality` = Stockholm | 6 371 | unreachable |
| `region` = Stockholm | 10 452 | unreachable |
| `occupation-field` = IT | 2 610 | unreachable |
| `published-after` = 12 hours ago | 2 399 | unreachable |
| Stockholm **+** `published-after` 1 day | **751** | fits |
| Stockholm **+** `published-after` 3 days | **819** | fits |
| IT **+** `published-after` 7 days | **843** | fits |
| region Stockholm **+** field IT | **1 137** | fits |

**A place alone overflows. A field alone overflows. A twelve-hour window
overflows.** It takes two filters, and the working recipe is *a place or a
field, plus a publication window*.

That last row is the one to hold on to: **Sweden posts about 2 400 ads in
twelve hours.** On a board of 39 865 that is a complete turnover in roughly a
week, so `--sedan` is a freshness control as much as a size one.

## Configuration

```yaml
boards:
  platsbanken:
    enabled: true
    searches:
      - { kommun: "0180", sedan: "2026-09-01T00:00:00" }
      - { region: "01", omrade: "apaJ_2ja_LuF" }
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `kommun` | recommended | Municipality **code** — `0180` is Stockholm |
| `region` | no | Region code — `01` is Stockholms län |
| `omrade` | no | `occupation-field` concept id |
| `sedan` | **effectively yes** | ISO 8601. The filter that makes a place fit |
| `q` | no | Free text. A narrow term fits on its own — `utvecklare` is 578 |

## What the record carries — the best in the repository

Measured on 300 ads.

| Field | Coverage | Note |
| :-- | --: | :-- |
| `headline`, `description.text` | 300/300 | Median **3 110 characters** |
| `employer.name` | 300/300 | |
| **`employer.organization_number`** | **293/300** | The Swedish company registration number |
| `application_deadline` | **300/300** | Every ad states when applications close |
| `publication_date` | 300/300 | |
| `number_of_vacancies` | 300/300 | Posts per ad — see above |
| `workplace_address.municipality` / `region` | 291/300 | |
| `postcode` | 269/300 | |
| `street_address` | 200/300 | |
| coordinates | **269/300** | Real lon/lat; the field is present on 300 but empty on 31 |
| `occupation` / `_group` / `_field` | 300/300 | A three-level national taxonomy |
| `employment_type`, `duration`, `working_hours_type` | 300/300 | |
| `employer.url` | 190/300 | |
| `application_contacts` | 41/300 | |

**`employer.organization_number` is the field to notice.** No other board here
publishes a legal identifier. It survives a rename, it is unique, and it is the
dedup key the ledger has never had — `michaelpage.md` and the agency boards are
documented as having *no* key that crosses to an employer's own ATS, and this
one would.

### The salary states its type and never its amount

```
salary_type          300/300     "Fast månads- vecko- eller timlön"
salary_description     0/300
```

Every ad says **how** it pays — fixed monthly/weekly/hourly on 281, fixed plus
variable on 17, commission on 2 — and **none of the 300 says how much**.

A presence check on `salary_type` reports 100% salary coverage of nothing. It
is the same shape as `turijobs.md`'s three readings and `infoempleo.md`'s
`value: 0.0`, in its cleanest form yet: two adjacent fields, one always full
and one always empty, and the full one is the one that sounds like an answer.
The card carries `salary_amount_stated` so the distinction cannot be lost.

### A requirement schema no other board has, and it is mostly empty

`must_have` and `nice_to_have` each carry `skills`, `languages`,
`work_experiences`, `education` and `education_level` as **taxonomy concepts
with weights** — a structured, machine-readable statement of what the job
needs. Nothing else in this repository comes close.

Then you count it:

| | `must_have` | `nice_to_have` |
| :-- | --: | --: |
| `skills` | **5/300** | 8/300 |
| `languages` | 43/300 | 18/300 |
| `work_experiences` | 33/300 | 52/300 |
| `education` | 10/300 | 8/300 |

**A rich schema is not rich data.** Structured requirements of any kind appear
on well under a fifth of ads; the requirements are in the prose, like
everywhere else. The card emits the concepts when they exist and the run
reports how many ads had any, so the schema is never mistaken for coverage.

### Fields that exist and are never filled

`description` offers `company_information`, `conditions`, `needs` and
`requirements` beside `text` — a pre-split description like `join.md`'s. All
four are **0 of 300**. Only `text` and `text_formatted` carry anything.

And `workplace_model` — the remote/on-site field — reads **"Arbete på plats"
on 300 of 300**. It did not distinguish anything in the sample, so it is
carried and not relied on, exactly as `empleate.md`'s `modality` is.

## Verification

```bash
S=skills/job-scan/scripts/platsbanken.py
python3 $S count                                   # 39 865 ads / 67 109 posts
python3 $S count --kommun 0180                     # 6 371, fits_in_window false
python3 $S count --kommun 0180 --sedan 2026-09-01T00:00:00   # 751, true
python3 $S search --kommun 0180 --sedan 2026-09-01T00:00:00 --limit 120
```

The refusal is the behaviour to re-check, because the alternative is a 400
surfacing from the middle of a sweep:

```bash
python3 $S search --kommun 0180     # → must ERROR before paging, not mid-run
```

## This adapter now calls the guard

It was one of six network readers that never did (#100). **It is the only one
of the six with no question of principle attached:**

```
jobsearch.api.jobtechdev.se   404 — no robots.txt published, which is an
                              absence and therefore knowledge
arbetsformedlingen.se         permits
```

So the call costs nothing and closes a real gap, rather than deciding an
arbitration. It asks per host **and per path**, and exits 7 on a refusal or 8
on an unknown, with the guard's own words.
