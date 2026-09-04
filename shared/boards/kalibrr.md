# Board adapter — Kalibrr (Indonesia and the Philippines)

<!-- verified: 2026-09-02 -->

<!-- hosts: www.kalibrr.com -->
<!-- script: kalibrr.py -->
<!-- countries: ID PH -->
South-East Asia's private board, and **one adapter for two countries**: 1 045
Indonesian and 778 Philippine ads on 2026-09-02. Public JSON, **no key, no
cookie, no account, no browser**.

`www.kalibrr.com/robots.txt` is **59 bytes of `text/plain`** — checked as a
MIME type, not only as a status — and closes exactly two paths, `/root` and
`/candidate/profile`. No job path is refused and **no AI agent is named**,
neither to allow nor to ban.

**Everything below was verified against the live service on 2026-09-02.**

## The finding that decides how this adapter works

**A search that matches nothing is answered with somebody else's ads, and the
only sign is one boolean.**

| Call | `count` | `from_alternative` |
| :-- | --: | :-- |
| `?country=Indonesia` | 1 045 | `false` |
| `?country=Philippines` | 778 | `false` |
| `?country=Singapore` | **818** | **`true`** |
| `?text=zzzzqqqq` | **818** | **`true`** |
| no country at all | **818** | `false` |

Kalibrr does not operate in Singapore, and no ad matches `zzzzqqqq`. Both
return **the same 818 ads, headed by the same employer**, with a complete
payload, HTTP 200 and no error field. A client that scores what it is handed
scores 818 unrelated ads as Singaporean vacancies.

And read the last row again: **the unfiltered call returns that same 818, and
818 is smaller than either country on its own.** The default is not the
board — it is the fallback set. This is the anomaly that made the board worth
investigating: a sweep with no country reads a curated remainder, gets a
plausible number, and concludes the board is small.

So `kalibrr.py` **requires `--country`**, and **refuses any response carrying
`from_alternative`** — it exits 3 with the substituted count rather than
scoring a single row of it. `from_correction` and `correction_text_search`
get a warning by the same logic: the results answer a term the board chose.

## Two endpoints, and they do not agree

| | `/kjs/job_board/search` | `/api/job_board/search` |
| :-- | --: | --: |
| no country | 818 (the fallback) | **1 830** |
| Indonesia | **1 045** | 1 011 |
| Philippines | **778** | 674 |
| `country=Singapore` | 818, `from_alternative` | **0 — an honest zero** |
| `text=zzzzqqqq` | 818, `from_alternative` | **0** |
| fields per ad | **38** | 37 |

`/api` is the older one: it tells the truth about emptiness and carries
`converted_salary` and `salary_currency_orig`, but it is less complete and it
lacks `is_hybrid`, `is_open_to_fresh_grads` and `job_sds_skills`. `/kjs` is
what the site calls today: fuller, richer, and the one that substitutes.

The adapter builds on `/kjs` **with the `from_alternative` guard**, and this
file records `/api` as the second opinion to reach for when a count looks
wrong — or when you need the currency `/kjs` drops.

## The salary is converted to pesos and the label does not say so

Every salaried ad on `/kjs` carries `salary_currency: "PHP"`. Including the
Indonesian ones:

```
Indonesia, /kjs   PHP 22962.742977478316 – 32803.91853925474  month
                  "Senior Corporate Finance Accounting & Tax"
Indonesia, /api   salary_currency "PHP", salary_currency_orig "IDR",
                  converted_salary true, base 12718.172940574614
Philippines,/kjs  PHP 17000 – 18000 month
```

The Philippine amounts are round numbers an employer typed. The Indonesian
ones are twelve-decimal floats, which is what a conversion looks like, and
`/api` names it outright: **the original currency is IDR and the figure has
been converted**. `/kjs` drops both fields.

Read an Indonesian `base_salary` as pesos and you are wrong by a factor of
roughly 250. **So this adapter never emits `salary_min`.** It emits
`salary_php_min`, `salary_php_max` and `salary_converted`, and
`shared/scoring-rubric.md` cannot mistake one for the other. If a real local
figure is needed, `/api` is where the original currency lives.

## The salary flag is not the salary

| | Indonesia | Philippines |
| :-- | --: | --: |
| Ads read | 999 | 778 (the whole board) |
| **Carrying a figure** | **217 (21.7%)** | **130 (16.7%)** |
| `salary_shown: true` | 880 (88.1%) | 680 (87.4%) |
| **`salary_shown: true` and no figure** | **663** | **550** |

`salary_shown` is true on nearly nine ads in ten, and four out of five of
those carry no salary at all. It is not a disclosure flag, whatever it is —
and a parser that trusts it reads 88% coverage on a board that discloses 20%.
The card carries it as `salary_shown_flag`, named so nobody uses it by
accident.

This is `irishjobs`' `€ Not Disclosed` in another costume: a field that is
filled, and a field that is meaningful, are not the same field.

## What a record gives

1 139 unique ads across both countries:

| Field | Filled |
| :-- | --: |
| Company name | **1 139/1 139** — no anonymous ads on this board |
| Description | 1 139/1 139 |
| `activation_date` | 1 139/1 139 |
| **`application_end_date`** — a real closing date | **1 139/1 139** |
| Structured location (city, region, country) | 1 139/1 139 |
| `is_open_to_fresh_grads` | 199/1 139 |
| `job_sds_skills` | 168/1 139 |
| `is_work_from_home` | 89/1 139 — 31 in Indonesia, **104 of 778 in the Philippines** |
| `apply_redirect_url` | 58/1 139 (~5%) — an external ATS |
| A salary figure | 347/1 139 (~20%) |

**The employer is named on every ad**, which is better than most of this
repository, and the closing date is real rather than a repost of the posting
date. Remote work is a Philippine phenomenon here, not an Indonesian one:
13% against 3%.

## Pagination, and how it ends

`limit=500` was accepted and returned 500 rows; no ceiling was found. 100 is
what the adapter uses, because nothing needs 500 at once.

The end of a result set is a **200 with an empty `jobs` list — and `count`
drops from the country's total back to 818**, the fallback number:

```
offset=1000 → 20 rows, count 1045
offset=1040 →  5 rows, count 1045
offset=1100 →  0 rows, count  818
offset=5000 →  0 rows, count  818
```

Neither is an error. The adapter stops on the empty list and says so when the
count changed underneath it.

## The ad URL is rebuilt from the company code and the id

```
https://www.kalibrr.com/c/first-datacorp-1/jobs/271911            → 200, 73 KB
https://www.kalibrr.com/c/first-datacorp-1/jobs/271911/<slug>     → 200, same
https://www.kalibrr.com/id/c/…                                    → 6 250 B, a shell
```

The slug is decorative; `company.code` and `id` are enough. The locale prefix
`/id/` is not — it serves a 6 250-byte skeleton, so build the plain form.

**There is no per-ad JSON endpoint**, and the ad page carries only a `WebSite`
JSON-LD block, no `JobPosting`. The search payload *is* the ad: it includes
the description, so no second request buys anything. `--with-description`
puts the text on the card.

## What the terms allow

Kalibrr's terms (read 2026-09-02 at `kalibrr.com/terms`, server-rendered):

> "You may download relevant materials from our website bearing sufficient
> reference to its proprietary nature, and solely for your **personal and
> non-commercial use**."

> "You shall not reproduce, copy, distribute, upload, post, transmit, or
> disseminate in any manner … any content, graphics, pictures, or materials
> from our website or Application without written permission from Kalibrr and
> the relevant owners."

So a personal job hunt is inside the licence, including keeping what you
found; **reproducing or disseminating the content is not**. No ad text, no
description and no employer copy from this board goes into anything this
project publishes.

**A measured count is a narrower question, and this file does not settle it
the way `adzuna.md` does.** Adzuna's terms name *aggregation* outright —
"vacancy counts, average salaries etc." — and exclude it without written
consent, which is why no Adzuna figure appears in a published page. Kalibrr's
clause forbids reproducing and disseminating *content*; a number this project
measured is neither the content nor an aggregation the clause names. The
project therefore does publish Kalibrr volumes and fill rates, with that
reasoning stated on the page carrying them so it can be argued with. The two
boards differ because the two documents differ, not because the practice
does.

One honest note on scope: the word *scraping* appears **once** in the
document, in the **Kalibrr Free** section, which governs employer accounts on
that plan and reserves the right to monitor them for "automated extraction,
scraping, fraudulent hiring activity … or excessive usage". It is not a
prohibition addressed to visitors, and it does not name the API — but it is
the operator saying what it thinks of bulk extraction, and it is a reason to
keep the pace conservative rather than a reason to stop.

## Configuration

```yaml
boards:
  kalibrr:
    enabled: true
    countries: ["Indonesia", "Philippines"]   # required; those two only
    searches:
      - keyword: "software engineer"
      - keyword: "accountant"
    pages: 3            # 100 ads a page
    delay: 1.0
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `countries` | **yes** | `Indonesia`, `Philippines`. **Anything else — including omitting it — reads the fallback set**, and any other value is answered with 818 substituted ads |
| `searches` | no | Each `keyword` becomes `text=`; without one the sweep is the country's whole board |
| `pages` | no | 100 ads a page |
| `delay` | no | Seconds between calls, default 1.0 |

No credentials, no login, no browser.

## Zero-shaped answers

**1. `from_alternative: true` — the answer is to a different question.** 818
ads, HTTP 200, full payload. The single most important field in the response.

**2. No country is not "all countries".** It is the same 818, and it is
smaller than either market.

**3. `salary_shown: true` with no salary**, on 1 213 ads of 1 777.

**4. `salary_currency: "PHP"` on an Indonesian ad**, converted, with the
original currency dropped by this endpoint.

**5. Past the end is a 200, an empty list, and a `count` that changes** back
to the fallback total.

**6. The `/id/` locale prefix serves a 6 250-byte shell** with HTTP 200.

**7. The two endpoints disagree by a few hundred ads** in the same minute.
`/kjs` is the fuller one; the gap is not an error to reconcile but a reason to
name which endpoint a number came from.

## Applying

`apply_redirect_url` is present on about 5% of ads and points at the
employer's own ATS; the rest are applied to on Kalibrr, which requires an
account. **The plugin does not create accounts and does not fill credential
fields.** Hand the user the ad URL and their documents.

## Verification

```bash
S=skills/job-scan/scripts/kalibrr.py
python3 $S count  --country Indonesia                        # 1 045
python3 $S count  --country Philippines --keyword "software engineer"
python3 $S count  --country Indonesia --keyword zzzzqqqq     # refuses, exit 3
python3 $S search --country Philippines --limit 2
```
