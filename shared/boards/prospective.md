# Board adapter — Prospective (a Swiss multi-employer ATS, one career center at a time): `ohws.prospective.ch/public/v1/careercenter/<id>/` fills its list by POSTing its own form back to itself, the `.job` items link to the tenant's domain with the ad's UUID, and the ad on `/public/v1/jobs/<uuid>` carries one JobPosting; `prospective.py`, the street and the postal code never emitted, the tenant's domain never sent to

<!-- verified: 2026-09-21 -->

<!-- hosts: ohws.prospective.ch -->
<!-- host-forms: ohws.prospective.ch -->
<!-- host-forms-basis: read — `prospective.py:62` names the one host as a literal; `tenant_of` (`prospective.py:100`) takes the center's number from `--tenant` or from an address on that host; `request()` (`prospective.py:112`) refuses any other host before the gate — the tenant's own domain in the list's links (`jobs.css.ch`, `jobs.ekz.ch`) is kept as `employer_url` and never sent to · 2026-09-21 -->
<!-- script: prospective.py -->
<!-- countries: * -->
<!-- content: measured · **two centers with positions and one on the vendor's template, 2026-09-21 07:50–07:52 UTC, the declared client, the guard on the exact path, two reads each (identical bodies). Rules: one file (5 592 B) — `*` with an empty `Disallow:` and a list of `Allow:` lines for share images on the vendor's S3; no Crawl-delay. GET `/public/v1/careercenter/<id>/` (200; CSS `1000981` 42 331 B, EKZ `1003036` 55 946 B, ZHAW `1002929` 664 B — «Career Center project template», no form) renders the tenant's own template around `#careercenter-form` (POST to itself: `offset`, `limit` 12, `lang`, `query`, `place`, `radius`, `viewport`, the `filter_NN` selects) and fills `#jobListAndPagination` by that POST on load; the POST's answer (CSS 44 923 B, EKZ 55 940 B) holds `#jobs` with `.job` items — a link to the tenant's domain ending in the ad's UUID (`jobs.css.ch/offene-stellen/<slug>/<uuid>`), a `.job-title` or the link's `title`, a `.place-of-work` / `.job-city` — and a pager `sendPagination(<offset>)`; the CSS template prints `.jobs-total .total` **«42 Jobs»**, the EKZ one prints none; **`limit=100` honoured** (EKZ 99 146 B, 64 items — the whole board). The ad `/public/v1/jobs/892e45e0-…` (200) carries one JobPosting — title, description, datePosted, validThrough (2036-09-17 — a far date, as the employer set it), employmentType `["PART_TIME"]`, hiringOrganization «CSS Versicherung», jobLocation with streetAddress, postalCode, locality, region, addressCountry «Schweiz» (a name). Exercised: `jobs --tenant 1000981 --country-code ch` → 42 emitted, 42 stated (2 requests, the stamp said); the CSS ad → the posting, its street and postal code withheld; `1002929` → exit 6 with the template's sentence** · 2026-09-21 -->
<!-- witness: the template's own `.total` where it prints one (CSS 42), compared to the emitted count; where it does not (EKZ) the run says the list is the board · 2026-09-21 -->
<!-- route: http · 42 · 2026-09-21 -->

**Issue #485 (opened under #406, the ATS families; the ad host already read
by `shared/ats-open-check.md` for its `validThrough`). Measured 2026-09-21
07:50–07:52 UTC by the declared client, the guard on the exact path, on
three centers named by the family's signature (`ohws.prospective.ch/public/
v1` in a search engine): CSS (42), EKZ (64), the ZHAW (the vendor's
template — not built).** Rank: the pilot's order of 2026-09-21 06:13 UTC —
#479 → #488 after the dated controls.

## What Prospective is, and where its tenants live

Prospective Media Services (Zürich) hosts the career centers of Swiss
employers — insurers, utilities, hospitals, universities, cantons, the
Swiss Army — on one host under a numeric id; the ads are `/public/v1/jobs/
<uuid>`, multi-employer (the real employer in `hiringOrganization`). **The
user names the center** by its number, or by any `ohws.prospective.ch`
address that carries it (a filtered search page, a job-abo page).

## The route — the page's own form, posted back

```
GET  https://ohws.prospective.ch/public/v1/careercenter/1000981/                 200 — #careercenter-form (offset, limit 12, lang…)
POST https://ohws.prospective.ch/public/v1/careercenter/1000981/  offset=0&limit=100&lang=de   200 — #jobs, 42 .job items, .total 42
POST …/careercenter/1003036/  offset=0&limit=100                                 200 — 64 items, no total (12 a page and a pager to 60 in the page's own default)
GET  https://ohws.prospective.ch/public/v1/jobs/892e45e0-…                       200 — one JobPosting (the `ad` command)
GET  https://ohws.prospective.ch/public/v1/careercenter/1002929/                 200 — «Career Center project template»: not built, exit 6
```

The POST is the form the page sends to itself on load, with the page's
own fields; the adapter asks 100 an answer (the page's default is 12) and
walks `offset` until an answer brings no new UUID or fewer than asked. The
UUID is the key; the list's links name the tenant's own domain, kept as
`employer_url` and never sent to. `--country-code` **stamps** on the list
(it states no country) and says so; on the ad it filters on the posting's
own country.

## What the adapter emits, and withholds

`jobs --tenant <center> [--lang de] [--country-code ISO2] [--max-pages N]`:
id (the UUID), url (`/public/v1/jobs/<uuid>`), employer_url, title, place.
`ad --url`: the page's JobPosting — title, company, place, region, country
(or `country_name` when the posting gives a name), employment_type,
published, expires (`validThrough`, every ad), description (text,
scrubbed); any `track=` token in the address dropped.

**Withheld:** the JobPosting's `streetAddress` and `postalCode`; every
e-mail address and telephone in the description replaced by «[e-mail
withheld]» / «[telephone withheld]» — a date («per 01.01.2027») is left
alone; `contacts_withheld` on every record; the application
(`/public/v1/application/<uuid>`) never touched.

## Tests and mutations

`AMultiEmployerATSWhoseCareerCenterFillsItselfByPostingItsOwnFormAndLinksToTheTenantsDomain`,
both ways on fixtures (the form posted back with offset, limit and lang,
two answers against a stated total, the EKZ template without a total and
the walk's end on a repeated answer, the stamp said, a stated zero, the
vendor's template, a page without the form, a 404, a tenant-domain
address refused; the ad with its street and contact, the `track=` token
dropped, the country filter, the ad gone or changed). Mutation bench on a
detached copy, `python3 -B`, 9 / 9 red: the UUID link regex broken · the
walk's end on «nothing new» dropped · the stated total ignored · the
street emitted · the scrub dropped in the ad · the stamp note dropped ·
the template check dropped · the `track=` token kept · another host sent.
