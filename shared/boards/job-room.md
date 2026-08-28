# Board adapter — job-room.ch

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
characters long. Strip the query string before storing or comparing.

**7. This is the board most likely to duplicate the ledger, by construction.**
98 of 100 fresh VD/GE ads had an `externalUrl`; the hosts were jobup.ch 32,
carrieres-rolex.com 17, michaelpage.ch 10, successfactors 7, jobs.ch 3,
offres-emploi.vd.ch 2, smartrecruiters 2. So roughly a third of what this board
returns for Romandie is a jobup ad the ledger may already hold.

The good news: the duplicate is **exactly** identifiable, not merely suspected.
The card carries `duplicate_of` — `jobup:<uuid>` or `jobs.ch:<uuid>`, extracted
from the external URL. When it is set and the ledger already has that row, this
is the same posting: record it `discarded` naming the row, and do **not** apply
the fuzzy employer-name check from `skills/job-scan/SKILL.md`, which is for
cases where no such key exists.

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
