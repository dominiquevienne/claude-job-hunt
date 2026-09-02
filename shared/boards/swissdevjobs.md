# Board adapter — swissdevjobs.ch

<!-- verified: 2026-09-02 -->

**Re-verified 2026-09-02**: **177 of 177 postings kept**, against 172 recorded earlier.

Swiss tech and software roles. **A real multi-employer board**, unlike the
per-tenant ATS family in `ats.py`: one request returns every live vacancy, and
the employer is named on each. **No browser, no account, no cookie.**

**Everything here was measured against the live API on 2026-08-31.**

## Configuration

```yaml
boards:
  swissdevjobs:
    enabled: true
```

No settings. There is nothing to scope: the endpoint returns the whole board.

## Usage

```bash
swissdevjobs.py list --tech PHP --tech Laravel
swissdevjobs.py list --near 46.52,6.63 --radius-km 60
swissdevjobs.py list --salary-min 120000 --seniority Senior
swissdevjobs.py ad    --slug <jobUrl>
swissdevjobs.py check --slug <jobUrl>
```

## The endpoint

```
GET https://swissdevjobs.ch/api/jobsLight
```

HTTP 200, JSON array, unauthenticated. **No paging** — 170 ads, 218 kB, one
request for the entire board.

`robots.txt` disallows `/api/` for **`Meta-ExternalAgent` by name** and for
nobody else; search and listing are not disallowed at all.

**The old `/api/jobs` is dead but answers 200.** It returns the plain text
*"ENDPOINT Deprecated - contact hello@swissdevjobs.ch if you are using it"*, so
a caller that only checks the status code sees success and parses nothing. The
adapter fails loudly if the payload is not a list.

## Two fields that no other board here provides

**A salary on 169 of 170 ads.** `annualSalaryFrom` / `annualSalaryTo`, in CHF,
the employer's own figure — **tier (A)** in `shared/salary-estimate.md`, not an
estimate. For comparison, Michael Page populates its salary block on 3 ads of 39,
and most boards publish none at all. This is the only board in the plugin where
the money is known before applying, on essentially every ad.

**Coordinates on 170 of 170.** `latitude` / `longitude`, which is why `--near`
exists: distance is computed, not guessed from a place name. It removes the
weakest link in the commute rule of `shared/scoring-rubric.md`, which elsewhere
has to interpret strings like *"Lausanne Region"*.

**But read the caveat.** `--near` filters on what the employer geocoded, not on
the town it printed. Measured: **3 ads of 170 carry coordinates more than 25 km
from their own `actualCity`**, the worst 96 km out — an ad labelled *8001 Zürich*
sitting on Bern's coordinates. All three were multi-site IT-consulting firms.
Distance is also straight-line, never travel time.

## Also on every ad

`address` + `postalCode` + `actualCity` — **street, postcode and town**, the
fields `job-room-ch` records as the ones most often missing from a PRE.

`expLevel` (Junior / Regular / Senior / Lead), `jobType` (Full-Time / Part-Time /
Contract / Internship), `workplace` (office / hybrid / remote), `technologies`
(a tag array, present on 158 of 170), `companySize`, `companyType`, `activeFrom`.

## What it does NOT carry

**No description.** The endpoint is called `jobsLight` and it means it: there is
no body text, and the ad page is client-rendered, so there is no no-browser route
to it. `--with-description` returns an explicit note saying so rather than an
empty string. To score an ad properly, open the URL or paste the text into
`cover-letter`.

**`hasVisaSponsorship` is a string, not a boolean** — `"Yes"` or `"No"`, and
`"Yes"` is rare: **2 ads of 170**. Testing whether the key exists reads every ad
as sponsoring, which overstates it by two orders of magnitude.

`contractRateFrom` / `contractRateTo` exist but are populated on 2 ads of 170.

## Honest limit — this is German-speaking Switzerland

On a full board of 170:

| | |
| :-- | --: |
| Zürich | 77 |
| Bern | 18 |
| Luzern | 10 |
| **Suisse romande, all of it** | **2** |
| `workplace: remote` | **4** |

Anyone switching this on expecting Geneva or Lausanne coverage gets an empty
pipeline **and no error**. `list` prints that figure on stderr whenever a run
returns nothing, so an empty result reads as the board and not as the market.

## Closure signal

`check` treats the listing as the authority: present and not `isPaused` → open.
When an ad is absent it confirms with the ad page, which is usable here because
**a wrong slug really does return 404** rather than the SPA shell. `isPaused` was
`false` or absent on all 170 measured, so the flag is untested against a live
paused ad — `check` reports it as `paused` rather than guessing what it means.

| Code | Meaning |
| :-- | :-- |
| `3` | `ad` or `check` on a slug no longer listed — record it `discarded` |
| `2` | the endpoint did not return a list — shape changed, do not fall back to `/api/jobs` |

## Possible future — two sibling boards

The site's bundle links **germantechjobs.de** and **devjob.ro**, run by the same
team with what looks like the same front end. If they expose an equivalent
`jobsLight`, this adapter's shape would cover three countries. **Not verified.**
