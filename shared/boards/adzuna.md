# Board adapter — Adzuna

<!-- verified: 2026-09-02 -->

<!-- hosts: api.adzuna.com -->
<!-- script: adzuna.py -->
An aggregator with **one API for nineteen countries**, where the country is a
path segment. One adapter reaches Switzerland, France, Germany, Austria,
Belgium, the Netherlands, Italy, Spain, Poland, the United Kingdom, the United
States, Canada, Australia, New Zealand, India, Singapore, South Africa, Brazil
and Mexico.

**It needs a key**, and it is the second adapter here that does, after
`france-travail.md`. It is also the one with the smallest budget in the
repository: **250 calls a day for everything together.**

**Everything below was verified against the live API on 2026-09-02**, with the
user's own credentials.

## The nineteen, from the API itself

```
gb us at au be br ca ch de es fr in it mx nl nz pl sg za
```

Not guessed: it is the `country` enum of the OpenAPI the portal serves at
`developer.adzuna.com/swagger/spec/test2.json`, **and the API repeats it in an
error**. `/jobs/ie/search/1` answers **HTTP 404 with a JSON body naming every
supported code** — an honest, self-documenting refusal, and the reason
`jobsireland.md` says Adzuna does not cover Ireland.

## The budget is the design

Published in the terms: **25 calls a minute, 250 a day, 1 000 a week, 2 500 a
month**, for every search and every country together. And a page holds at most
50 ads:

> `results_per_page=100` and `results_per_page=101` both answer **HTTP 200 with
> 50 rows** and no complaint.

**The cap is silent.** Code that asks for 100 and assumes it received 100 will
page twice as often as it believes, on an allowance that small.

So a day is 12 500 ads at the absolute maximum, and a sweep of nineteen
countries does not fit. `adzuna.py` asks for 50 every time, reads **one page
per search by default**, and stops at `--max-calls` (default 10) so a loop
cannot spend the day's allowance by accident. Every run prints what it spent.

Deep paging does work — page 200 of a GB search returned 50 rows — but it is
almost always the wrong way to use this board. Narrow the search instead.

## The description is a 500-character teaser

The spec says *"truncated to 500 characters"*, and the measurement agrees: on
GB, FR, CH and DE, **the median description length and the maximum are both
exactly 500**.

**This is a discovery board, not a scoring board.** The full text lives with
the advertiser, behind `redirect_url` — which is also where Adzuna's terms
require the user to be sent. The card carries `description_teaser`,
`description_chars` and `teaser_truncated`, so nothing downstream mistakes a
teaser for an ad.

## The salary may be Adzuna's guess

`salary_is_predicted == '1'` means the figure came from Adzuna's *Jobsworth*
estimator, **not from the advert**. Measured on 50 ads per country:

| Country | With a salary | Of those, predicted | Advertiser's own |
| :-- | --: | --: | --: |
| gb | 16/50 | **6** | 10 |
| fr | 7/50 | 0 | 7 |
| ch | 2/50 | 0 | 2 |
| de | **0/50** | 0 | 0 |

So this adapter **never emits a field called `salary_min`**. It emits
`salary_min_stated` / `salary_max_stated` — the advertiser's figure, or
nothing — and `salary_min_adzuna_estimate` / `salary_max_adzuna_estimate`
separately. A number the board invented must not be able to look like a number
the employer wrote. (Issue #67, and the same treatment as `kalibrr.md`.)

Note the German column: **a salary on 0 of 50**. Adzuna's coverage of pay is
national, not uniform.

## What else a record carries, and how unevenly

Over the same four samples of 50:

| Field | gb | fr | ch | de |
| :-- | --: | --: | --: | --: |
| `title`, `company.display_name` | 50 | 50 | 50 | 50 |
| `redirect_url`, `adref` | 50 | 50 | 50 | 50 |
| `latitude` / `longitude` | 49 | 50 | 46 | 45 |
| `contract_time` | 42 | 8 | 4 | **0** |
| `contract_type` | 10 | 33 | 1 | **0** |

`location.area` is an array from broad to narrow — 4 to 6 levels, e.g.
`["UK", "South East England", "Surrey", "Staines", "Laleham"]` — and the card
keeps it whole rather than flattening it.

**Volumes on a bare search, the same day:** gb 739 193, fr 967 066, de
1 215 596, ch 81 882.

## Searching, and one warning about language

`what`, `where`, `distance`, `max_days_old`, `salary_min` and `category` all
work; `sort_by=date` is accepted, `sort_by=relevancy` is a **400**. An unknown
place is an **honest zero** — `where=Zzzznotaplace` on CH returns `count: 0`,
not a fallback — which is a decency this repository does not always get (see
`kalibrr.md`).

**But the index is not evenly multilingual.** On Switzerland:

| `what=` | Matches |
| :-- | --: |
| `Entwickler` | **12 666** |
| `developer` | 3 162 |
| `informaticien` | 138 |
| `développeur` | **0** |

Zero. A French-speaking user searching in French on the Swiss board of an
aggregator gets nothing, and the board does not say why. **Search the language
the ads are written in**, and for Switzerland that is mostly German.

**Since 2026-09-02 the adapter says so on every empty result** (`_zero.py`,
issue #70): a zero here is a finding, not an answer, and the run must not read
it as an empty market before the query has been asked in the market's
language. Pass **`--speaks`** and it says more — which of the market's
languages the person actually works in, what a measured term returns in each,
and what the languages they do not work in return. The table of measured terms
is `shared/search-language.md`; it records counts and dates, never
translations.

## The categories are language-independent, and they classify a third of the board

**The obvious escape from the language problem is the taxonomy, and it does not
hold.** Measured 2026-09-02:

| Index | Ads | `category=unknown` | `it-jobs` |
| :-- | --: | --: | --: |
| **ch** | 81 516 | **57 663 — 70.7%** | 1 150 |
| fr | 965 545 | 477 585 — 49.5% | 13 293 |
| de | 1 211 402 | 822 462 — 67.9% | 23 034 |

Two things are true at once, and only one of them is good news.

**The tags are genuinely language-independent.** Thirty of them, and the `ch`
and `fr` sets are **identical**. A sample of `category=it-jobs` on `ch` with no
keyword at all returns *Technicien Service Desk (H/F)*, *Ingénieur Système
Infrastructure H/F* and *Backend Software Engineer* side by side — French,
German and English together. A francophone reaches German-market ads without
knowing a word of German.

**And the classification is mostly empty.** `category=it-jobs` returns **1 150**
on `ch` where `what=Entwickler` alone returns **12 691**. A sweep by category
would report 1 150 IT jobs in Switzerland where there are twelve thousand:
issue #70 again, in better manners, and **it never trips the zero check because
1 150 is not zero**.

So `--category` stays, and **`adzuna.py` now prints those percentages every
time it is used**: the flag narrows a keyword search, it does not sweep a
market. The count it returns is a count of what Adzuna classified.

*(Nor is it clean: a `Lehrstelle Küchenangestellte/r` — a kitchen apprenticeship
— sat in `it-jobs` in the sample.)*

**The same caution applies to the `category` and `category_tag` fields on every
row.** They are present, plausible, and empty on roughly seven Swiss rows in
ten. Read one as *"Adzuna happened to classify this ad"*, never as a trade.

**And the same caution attaches to the fill rates above.** A salary on **0 of
50** German ads and `contract_type` on **0 of 50** were measured through
German-language queries. *A fill rate measured in one language is not the
board's fill rate* — those two zeros are reported as what they are, a
measurement of one slice, not a property of the German market.

## The `ad` endpoint exists, and it is not in the spec

`adref` is documented as usable "with the 'ad' endpoint" — an endpoint the
OpenAPI does not describe. It answers anyway:

```
GET /v1/api/jobs/gb/ad/<adref>   → 200, the same record, same 500-char teaser
                                 → 503 with an HTML page, 1 of 3 tried
```

So it is a **liveness check and nothing more**: it buys no extra text. And it
was flaky under test, so `adzuna.py` treats a failure there as *unknown*, never
as *the ad is gone*.

## Credentials

**`ADZUNA_APP_ID` and `ADZUNA_APP_KEY`, from the environment and from nowhere
else** — the same rule as `france-travail.md`, for the same reason: `config.yml`
is read aloud, pasted into issues and backed up.

They live in **`~/.adzuna.env`, `chmod 600`**. A non-interactive shell does not
read a profile, so every call is prefixed:

```bash
set -a; . ~/.adzuna.env; set +a
python3 skills/job-scan/scripts/adzuna.py count --country ch --what Entwickler
```

Getting a key is **self-service** at `developer.adzuna.com/signup` — username,
email, password, an organisation name and website, and a dropdown where a job
seeker's honest answer is *Personal or academic research*. **The grant is
discretionary**: the terms say *"Adzuna has absolute discretion over granting
access to users"*, and the portal never states whether a key is issued
immediately or after review. **The plugin does not create accounts**; if the
key is missing the board is skipped with that reason named.

## What the terms allow, and the one thing they exclude

- **Permitted uses** are publishing Adzuna listings, publishing Jobsworth
  estimates, and **personal research** — which is what a job hunt is.
- **Attribution** applies when you *publish*: a "Jobs by Adzuna" label,
  116 × 23 px, for displayed adverts; "Adzuna Jobsworth" for estimates; a
  citation of "The Adzuna API" for research. A local ledger is not a
  publication; a page on the internet is.
- **Aggregation is excluded without written consent** — the terms name it:
  vacancy counts, average salaries and the like may not be used "in aggregation
  … to deliver any ongoing work or research". **So no Adzuna figure goes into
  anything this project publishes**, and this adapter is not designed to
  produce publishable counts. (`kalibrr.md` reaches the opposite conclusion
  from a differently worded clause; the documents differ, not the practice.)
- **Multiple accounts for one person is a breach**, and so is contacting a
  third-party content provider. On termination, data acquired from Adzuna must
  be removed.

`api.adzuna.com/robots.txt` is `User-agent: *` / `Disallow: /` — **26 bytes,
`text/plain`, refusing every crawler evenly**. That is not a reason to
override anything: the key *is* the sanctioned door, which is question 2 of
`shared/robots-policy.md`.

**Since 2026-09-04 that is binding rather than advisory.** Question 2 said
*"if one exists the debate is moot"* and left *moot* to the reader; the owner's
decision on #100 says **take the door**, on two cumulative conditions that both
hold here — the refusal is explicit and covers us, and Adzuna publishes a free
self-service API. **So the key is not a convenience: it decides whether this
board lights at all**, and an onboarding that assumes a terminal fails the user
who has none (#131). Measured 2026-09-04: `api.adzuna.com/robots.txt`, HTTP
200, `text/plain`, 26 bytes, unchanged. **The site is never swept**; only the documented
endpoints, under the user's own registered application.

## Configuration

```yaml
boards:
  adzuna:
    enabled: true
    countries: ["ch", "fr"]        # from the nineteen
    searches:
      - what: "Entwickler"
        where: "Zürich"
        distance: 20
      - category: "it-jobs"
    max_days_old: 7
    max_calls: 10                  # per run; the day's allowance is 250
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `countries` | yes | Any of the nineteen. An unknown code is a 404 that lists them |
| `searches` | yes | `what`, `where`, `distance`, `category`, `salary_min` |
| `max_days_old` | no | Days; keeps the sweep inside the budget |
| `max_calls` | no | Hard stop per run, default 10 |

**The credentials are not config keys.** See above.

## Zero-shaped answers

**1. No credentials → HTTP 400 with 1 996 bytes of HTML**, the "Uh oh"
page — not JSON. A client that calls `.json()` on the error crashes instead of
saying "no key". Identical page for a country outside the enum without a key,
and for `/version`.

**2. Bad credentials → HTTP 401 JSON `AUTH_FAIL`**, where the API's own spec
documents **410**. Handle both.

**3. Under load → HTTP 503, the same HTML page as case 1.** The status is the
only thing that separates "you sent no key" from "we are busy". The script
retries a 5xx once, slowly, then stops.

**4. `results_per_page` above 50 is silently 50.**

**5. A predicted salary looks exactly like a real one** unless
`salary_is_predicted` is read.

**6. A 500-character description looks like a short ad**, not a truncation.

**7. An unknown `where` is an honest 0** — worth recording as a *good* shape,
because the same input on other boards returns a full page of unrelated ads.

## Applying

There is no apply flow here and there should not be: the terms require the
user to reach the advertiser through `redirect_url`, and that is what the card
exposes as `url`. Hand it over with their documents.

## Pace

25 calls a minute is the published ceiling; the script sleeps 2.5 s between
calls, which is well under it, and the daily 250 is the real constraint. A
`503` under a burst was seen once at a faster pace — another reason to keep the
default.

## Verification

```bash
set -a; . ~/.adzuna.env; set +a
S=skills/job-scan/scripts/adzuna.py
python3 $S count  --country ch --what Entwickler            # 12 666
python3 $S count  --country ch --what développeur           # 0 — see the language note
python3 $S search --country ch --what développeur --speaks French   # 0, and what to try instead
python3 $S search --country ch --category it-jobs --limit 1 # warns: 70.7% of ch is unclassified
python3 $S search --country gb --what "python developer" --limit 2
python3 $S count  --country ie --what x                     # 404, and it lists the nineteen
```

## Why this adapter does not call the guard — HELD, not decided

`api.adzuna.com` publishes **`User-agent: * / Disallow: /`** on the very host
this adapter reads with the user's own key.

**Whether an issued key is a more specific instrument than a generic file is
in arbitration with the user, and it is not settled.** Wiring the guard would
decide it — and **so would quietly leaving this alone**, which is the defect
met on SmartRecruiters in `ats.py`, where the exception existed nowhere and
was a silence.

So: nothing wired, and the hold written here. The same question covers
`francetravail.md`, `arbeitsagentur.md` and `labonnealternance.md` — **four
boards, one arbitration**, not the two it was first framed on.
