# Board adapter — job-room.ch

<!-- verified: 2026-09-02 -->

<!-- hosts: api.job-room.ch, www.job-room.ch -->
<!-- script: jobroom.py -->
<!-- countries: CH -->
<!-- overlap: sozialinfo.md · 27 ads in common · 2026-09-03 -->
<!-- overlap: solique.md · 24 Solique tenants among 2 800 job-room ads FETCHED — **the denominator is a fetched count, not the board's size**, so no share is computed from it · 2026-09-03 -->
**Re-verified 2026-09-02**: a keyword search returned 50 cards on the documented route.

Switzerland's **public employment service portal**, run by SECO. It carries the
vacancies employers must publish under the Swiss vacancy-reporting duty
(*Stellenmeldepflicht* / *obligation d'annonce*), plus a large volume syndicated
from other boards.

**Everything here was verified against the live API on 2026-08-28.**

Not to be confused with `shared/modules/job-room-ch.md`, which is about
*declaring* applications to an ORP. Same site, different job: this file is the
sweep.

## Why it earns a place next to HiringCafe

It reaches the employers the meta-board does not. Of 20 employers sampled from
fresh VD/GE ads, **17 were absent from HiringCafe** — Banque Raiffeisen,
Fidinter, Hotelis, OK Job, Proman, Flexsis, Albedis, Fondation Eben-Hézer,
Fondation des 4 Marronniers, the International Skating Union. Present: Manor,
Hospice général, Siemens. That is the Romandie SME, foundation and staffing
layer, and it is exactly the gap `hiringcafe.md` documents.

## No browser, and a strict API

```
POST https://api.job-room.ch/jobadservice/api/jobAdvertisements/_search?page=0&size=50&sort=date_desc
     content-type: application/json
     {"cantonCodes":["VD"]}
→ ads in the body, the match count in the X-Total-Count header
```

No key, no cookie, no browser. And **an unknown field is refused with HTTP 400**
rather than ignored — the opposite of HiringCafe, and worth knowing: a malformed
query here fails loudly. That does not make every wrong query loud; see the
traps.

Use the script:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/jobroom.py" \
  search --canton VD --canton GE --online-since 7 --pages 3
```

## Configuration

```yaml
boards:
  job-room:
    enabled: true
    cantons: ["VD", "GE"]     # official uppercase codes
    # or, instead of cantons — a radius search:
    lat: 46.5197
    lon: 6.6323
    radius_km: 20             # minimum 10
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `cantons` | one of the two | List of official **uppercase** two-letter codes |
| `lat` / `lon` / `radius_km` | one of the two | `radius_km` ≥ 10 |

No login, no account, no profile URL. Ask for the cantons the user would
actually work in — that, not a keyword, is what bounds this board.

## Building a search

| `search.*` config | Field in the POST body | Verified |
| :-- | :-- | :-- |
| `keywords` | `keywords` (list) | VD + `infirmier` → 187 |
| `location` | `cantonCodes` (list) | VD 2 914, GE 1 495, ZH 17 689, all CH 78 774 |
| `location` (radius) | `radiusSearchRequest` `{geoPoint:{lat,lon}, distance}` | km, **minimum 10** |
| `posted_within` | `onlineSince` (days) | `3` → 9 311 |
| — | `companyName` | `Raiffeisen` → 184 |
| — | `permanent` (bool) | `true` → 66 822 |
| — | `workloadPercentageMin` / `Max` | 80–100 → 74 324 |
| sorting | `?sort=` | `date_desc` or `date_asc` **only** — `relevance_desc` is a 400 |

Radius around Lausanne, measured: 10 km → 1 461, 15 → 1 650, 20 → 1 907,
30 → 2 503, 50 → 3 715, 100 → 16 740. As everywhere, this is a net, not the
commute rule in `shared/scoring-rubric.md`.

## The ad id and its URL

The id is the ad's UUID. Rebuild the canonical page from it:

```
https://www.job-room.ch/job-search/<uuid>
```

In the ledger: `job-room:<uuid>`, the full UUID, never shortened.

**The site is a single-page app that answers 200 for any path**, so a status
code proves nothing about a URL being right. `/job-search/<uuid>` was confirmed
by rendering it and reading the ad back, and by `robots.txt` naming that exact
prefix.

## Reading one ad

```bash
python3 .../jobroom.py ad <uuid>
```

`GET /jobadservice/api/jobAdvertisements/<uuid>` returns the full record. A
deleted ad is a 404, which the script reports as exit 3 — record it `discarded`.

## Traps

**1. A wrong canton code returns 0 ads and no error.** `ZZ` → 0. **`vd` in
lowercase → 0.** The script validates against the 26 official codes and refuses
rather than sweeping into silence.

**2. `communalCodes` is accepted and silently ignored.** Passing a real commune
code (Nyon `5724`, Lausanne `5586`) returned the **unfiltered 78 774**. The
field exists, the API does not reject it, and it does nothing. Use
`radiusSearchRequest` for anything narrower than a canton. The script does not
expose `communalCodes` at all — do not add it back.

**3. A keyword search wraps every hit in `<em>`.** Left alone, the ledger gets
`<em>Infirmier</em>-ère à 100%`. And stripping the tag with a space produces
`Infirmier -ère`, so it is removed with no replacement, before any other tag.

**4. `languageIsoCode` lies.** Of 100 fresh VD/GE ads, **61 were tagged `de`**
while carrying French text. Never pick a description by its language tag; take
the longest one and report the tag as-is.

**5. Descriptions arrive with markdown-style escaping** — `Nyon\-La Vallée`,
`80\%`. Unescape before scoring, or the resume matcher reads backslashes.

**6. `externalUrl` carries affiliate tracking**, a `utm_campaign` blob 200
characters long. **Strip the query string for comparing — never for
fetching**, and keep the two forms apart in whatever you store.

That distinction was added after it broke something. On an Applifly host the
**id is in the query string** and a parameter that reads exactly like
attribution — `source=` — is what renders the page: stripped, the same URL
answers **`200` with 718 bytes** of referrer-capture JavaScript and no ad. So
the stripped form is a **dedup key and not an address**; see
`shared/boards/applifly.md`.

**6b. And it is not always the URL of an ad.** Measured 2026-08-29: **6 of 6**
`okjob.ch` external URLs led to a *category* page — `<title>` = *"Toutes les
offres d'emploi à &lt;slug&gt;"* — and not to the posting. The slug looks like an
ad's, which is exactly what makes it deceptive.

So `externalUrl` is a strong dedup key (trap 7) and a **weak** promise about
what is at the other end. Before treating one as an ad URL, confirm the page is
an ad: a `JobPosting` block, or a title that is not a listing heading. Reporting
"read the employer's posting" from a category page is the silent-failure this
plugin exists to avoid.

**7. This is the board most likely to duplicate the ledger, by construction.**

**The share was measured wrong until 2026-09-03, and by this adapter.**
job-room sends `externalUrl` in two shapes — 100 of 300 Vaud cards carry
`https://www.jobup.ch/...` and **193 carry `www.jobs.ch/de/...` with no
scheme** — and `urlparse("www.jobs.ch/x").netloc` is `""`. So `external_host`
was empty on 193 of 300 and a count made on it reported **`jobs.ch` once where
the sample holds 194**.

Re-measured on 300 Vaud cards after the fix:

```
www.jobs.ch          194   64.7%
www.jobup.ch          89   29.7%
ohws.prospective.ch    9    3.0%
no externalUrl         7    2.3%
live.solique.ch        1    0.3%
```

**jobup and jobs.ch are one platform, so 283 of 300 — 94.3% — of what this
board returns for Vaud comes from a single upstream.** That is not a third,
and it is not two sources: it is one, and reading it as two understates the
concentration by the whole of it.

`duplicate_of` was blind on exactly the same rows: filled on 90 of 300 before
the fix, **283 of 300 after**. Every jobs.ch advertisement already in the
ledger under a jobs.ch id was being recorded again as new.

*(The earlier reading — jobup.ch 32, jobs.ch 3 of 100 fresh VD/GE ads — is
superseded. It was not a sampling difference; the field it counted was
empty on two rows in three.)*

**A wider sweep, 2026-08-29 — 2 800 ads FETCHED across all 25 cantons — adds
two facts the 100-ad sample could not show.**

**2 800 is a count of what was retrieved, not a count of the board.** The
adapter defaults to `--pages 1` at `--size 50`, which is a cost guard and does
its job; a canton-by-canton sweep under it returns fifty rows per canton and
stops. Measured 2026-09-05: **the API reports 16 043 matches for Zurich alone**
— one canton is 5.7 times the national figure published here.

**And the right number was free on every request.** The API returns its own
match count, which the adapter prints, and it was never summed. *This is the
third time in one day that a count of what we read was published as a count of
what exists* — after `jobsbotswana` at 367 against 5 123, and `apec`'s file
named *offres* holding 1 288 search facets.

**No total is published in its place.** A figure exists in a hard-coded string
inside the script and nowhere in any measurement, and a hard-coded population
is exactly what this repository distrusts. The measurement that would settle it
is summing the per-canton match counts the API already returns.

**One agency supplies a third of this board.** `med-ipersonal.ch` accounted for
**872 of the 2 800 fetched** ads, and all 872 come from a **single employer**: MediPersonal,
a healthcare staffing agency. That is not a market signal and not an ATS — it is
one company publishing at scale. **Never read this board's volume as demand
without checking the host distribution**, and expect a healthcare-heavy skew
that has nothing to do with the user's field.

**This board is the route to the Swiss ATS HiringCafe cannot see.** The same
sweep carried **13 Refline** ads and **8 umantis** ads — hosts of which
HiringCafe indexes *zero* across 771 Swiss ads (`hiringcafe.md`). So job-room
earns its place twice: for the SMEs and foundations, and as the only supplier of
`apply.refline.ch` and `recruitingapp-*.umantis.com` URLs, which
`shared/ats-open-check.md` turns into open/closed answers.

The same sweep surfaced two more oracle hosts: **28 `ohws.prospective.ch`** ads
across 15 employers and **24 `live.solique.ch`** ads across 6 tenants. Both are
now in the registry, and Prospective publishes an explicit `validThrough`
expiry date on **every** ad — the only host anywhere here that does.

The good news: the duplicate is **exactly** identifiable, not merely suspected.
The card carries `duplicate_of` — `jobup:<uuid>` or `jobs.ch:<uuid>`, extracted
from the external URL. When it is set and the ledger already has that row, this
is the same posting: record it `discarded` naming the row, and do **not** apply
the fuzzy employer-name check from `skills/job-scan/SKILL.md`, which is for
cases where no such key exists.

**And the duplication is not only against `jobup`'s rows — it is within
job-room itself.** The same vacancy can arrive as **two** job-room
advertisements, under two `job-room:` ids, sharing one `duplicate_of`. Left
alone both enter the ledger as separate rows for one job. See **7b**.

**7b. The same vacancy arrives twice, with a different title on each copy —
and the truncated one is the employer's own.** Measured 2026-09-03 on four
Infomaniak records:

| `duplicate_of` | The employer's API feed | Jobup's syndicated copy |
| :-- | :-- | :-- |
| `jobup:478b69aa` | `Backend Software Engineer` | **`Backend Software Engineer (Hosting)`** |
| `jobup:4302da20` | `Software Engineer PHP` | **`Software Engineer PHP (Médias)`** |

**Two of two: the employer's feed drops the parenthesis and the syndicated
record keeps it.** With `(kDrive)`, `(Hosting)`, `(Médias)` and `(Core DevOps)`
open at one employer, that is the difference between four roles and one string
— **and the ledger's duplicate check reads the title**: *"same company and a
comparable role"*. It came within one read of a second application to a post
already applied for on 19.08.

**The orphan separator is the tell.** `Software Engineer -` keeps the dash the
parenthesis used to follow. The card carries `title_looks_truncated` when a
title ends that way and there is no second record to repair it from.

**And the company is wrong on the other copy.** The syndicated record names
**`Jobup`** — the syndicator — where the API one names the employer. **So the
duplicate check's two halves are broken on opposite records of the same ad**:
the copy with the usable role has the wrong company, and the copy with the
right company has the amputated role. Neither is complete, and joining them is
what makes either half work.

**`duplicate_of` is the join key, and the repair is inside job-room** — no
other board is needed. `jobroom.py`'s `merge()` groups a page's cards by it,
takes the **longest** title and the **non-syndicator** company, and says which
record each came from in `title_source`, `company_source` and `merged_note`.
On the measured page: **12 records → 10 vacancies.**

**Where no pair exists it flags and does not repair.** `company_is_syndicator`
on a record that only reached job-room through Jobup; `title_looks_truncated`
on an unpaired API record ending in a separator. There is no second value to
take, and inventing one is the guess this file exists to prevent.

*(`pick_description` was the suspect and is exonerated: **all four records
carry exactly one `jobDescriptions` entry**, so its `max()` had nothing to
choose between. The truncation is in the feed.)* Issue #97.

**8. Read the detail endpoint before scoring.** One ad returned a 325-character
description from `_search` and 5 185 characters from the detail endpoint; five
others matched exactly. The discrepancy is not systematic and its cause was not
established — which is precisely why the full read is worth one request.

**9. The ORP fields are thinner than they look.** Out of 100 ads: the employer
name is always there, **postcode and city on 39**, **street on 7**, an
`stellennummerAvam` on **2**. So this board helps the `job-room-ch` module, but
it does not fill the PRE form on its own — do not promise the user that it does.

**10. `sourceSystem` says where the ad came from**: `EXTERN` 61, `API` 37,
`JOBROOM` 2. On `EXTERN` ads the site itself displays a disclaimer — SECO
provides the result as an additional service and has *no influence over its
content or quality*. Treat those as you would any repost: the employer's own
page is the authority.

## Applying

There is no in-site apply flow. Hand the user `external_url` when there is one,
the job-room page otherwise, with their documents — as for any external ATS.

## Pace, and the note on access

One request per page of results, one per ad read. A sweep is a few dozen.

`robots.txt` disallows `/job-search/` for crawlers. This adapter does not crawl
that path: it reads the portal's own public API, unauthenticated, a handful of
times, for one user's own job search. These are public vacancy data published by
a public employment service whose stated purpose is getting people back into
work — which is exactly what this use is. Keep the pace human.
