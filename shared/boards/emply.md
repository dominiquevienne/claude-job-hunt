# Board adapter — Emply (a Danish ATS, Paychex since 2026 — one tenant at a time): the employer's career site on `<tenant>.career.emply.com` fills its vacancy section by `POST /api/integration/vacancy/get-page` with the config the page declares, the answer states `count`; the vacancy page is server-rendered; `emply.py`, streets, postcodes and the contact facts never emitted

<!-- verified: 2026-09-20 -->

<!-- hosts: aarhus.career.emply.com, aalborg.career.emply.com, toender.career.emply.com, via.career.emply.com, au.career.emply.com -->
<!-- host-forms: {tenant}.career.emply.com -->
<!-- host-forms-basis: read — `emply.py:DOMAIN` with the tenant as its subdomain (`tenant_of`), one per run, every other host refused before the gate; the vendor's `emply.com` (refused the client on 13.09, 6 478 B) is not a board · 2026-09-20 -->
<!-- script: emply.py -->
<!-- countries: * -->
<!-- content: measured · **three tenants with vacancies and one behind a challenge, 2026-09-20 13:4x–13:5x UTC, the declared client, the guard on the exact path first, each page read twice. Rules (`<tenant>.career.emply.com/robots.txt`, 23 B, the same on four tenants): `User-agent: * / Allow: /`, no Crawl-delay. The list page (200): Aarhus Kommune `/ledige-stillinger` 1 299 595 B ×2 same md5 and `/` 1 299 578 B (the root is the list), Aalborg `/` 358 473 B, Tønder `/ledige-stillinger` 182 027 B, VIA `/ledige-stillinger` 240 230 B — each declares `var languageKey = 'da-DK'` and one or two vacancy sections `var config = { count: N, filters: [], langCode: languageKey, offset: 0, searchText: '', sectionId: '<guid>', sortByProjectDataId: 'deadline', sortAscending: true, light: false, isJobAgent: false, siteId: null }` POSTed as JSON to `/api/integration/vacancy/get-page` (Aarhus: a section of 30 and a widget of 6; Aalborg, Tønder, VIA: 6); the answer `{count, vacancies[]}`, `offset` advancing by the vacancies received — `emply.py jobs` live: Aarhus 35 emitted, states 35, 2 calls of 30; Tønder 31 = 31, 6 calls of 6. The vacancy: id, shortId, titleAsUrl, number, created, published, deadline, department, location («Kingosvej 1-7, 8230, Åbyhøj, Denmark»), talentPool, externalCseAdLink, translations[] (title, content — the whole advert as HTML, 24 e-mail addresses in Aarhus's first 30 —, languageKey, factDatas[] — the tenant's labelled fields: Nummer, Frist, Lokation (the address again), Afdeling, «1. Kontaktperson», Stillingsbetegnelse, Arbejdstid, Ansættelse, Tiltrædelse, banner file names); the vacancy page `/ad/<titleAsUrl>/<shortId>` (200, 71 260 B) is server-rendered — `h1.css_headline`, `div.csa_jobadText` (nested divs), the apply button to `/apply/…` (reCAPTCHA on the page); no JobPosting. Aarhus University `au` answers 403 «Checking search engine crawler…» (6 887 B ×2, same md5) to `bin/fetch-body.py` on `/ledige-stillinger` — a challenge, consigned, not crossed (borne 2)** · 2026-09-20 -->
<!-- witness: the answer's own `count` — `emply.py jobs` prints it beside the emitted number on every walk · 2026-09-20 -->
<!-- route: http · 66 · 2026-09-20 -->

**Issue #468 (opened under #406, the ATS families). The premise of 13.09
(`emply.com` 403, redirecting to `paychex.eu` on 31.08) concerns the
vendor's site; the tenants live on `<tenant>.career.emply.com` and are
open — found by the signature in a search engine on 2026-09-20 (`aarhus`,
`aalborg`, `toender`, `via`, `au`, `hr`, `ase`, `meldgaard`, `collectia`);
three with vacancies measured, as the README's two-tenant rule asks.**
Rank: the pilot's order of 2026-09-20 12:5x, after #467.

## What Emply is, and where its tenants live

Emply (Copenhagen; Paychex Europe since 2026) is a Danish ATS whose career
sites run on `<tenant>.career.emply.com` — municipalities (Aarhus, Aalborg,
Tønder), universities (Aarhus University, VIA), companies. **The user
names the tenant by its subdomain**, its host or the site's URL. The root
of the site is usually the list; when it carries no vacancy section the
adapter tries `/ledige-stillinger` and `/vacancies`, or the page the user
names with `--page`.

## The route — the page's own call, replayed with its own config

```
GET  https://aarhus.career.emply.com/                                   200 — languageKey da-DK, config {count 30, sectionId 687f3e3c-…}
POST https://aarhus.career.emply.com/api/integration/vacancy/get-page   200 — {count: 35, vacancies: [30]}   (offset 0)
POST …/get-page  (offset 30)                                            200 — {count: 35, vacancies: [5]}
GET  https://aarhus.career.emply.com/ad/<titleAsUrl>/wt7hyj             200 — the vacancy page (the `ad` command)
GET  https://au.career.emply.com/                                       403 — «Checking search engine crawler…»: a challenge, exit 7, consigned
```

The adapter reads the page, takes the section with the largest `count`
(the list, not the widget), replays the config with the page's own
`sectionId`, `count`, sort and `langCode`, the page's cookie and a
Referer, and advances `offset` by the vacancies received to the stated
`count`, bounded by that count's last call; a call that repeats dies with
6. Two seconds between requests are ours.

## What the adapter emits, and withholds

`jobs --tenant <name> [--page] [--country-code] [--max-pages]`: id (the
shortId), number, url (the vacancy page, or the tenant's external link),
title, department, place · country (from `location`, its last segments —
«Åbyhøj», Denmark → DK; a location naming no country is stamped with
`--country-code`, said aloud), published, closes, talent_pool, language,
`fields` (the tenant's own labels), description (the advert, scrubbed).
`ad --url`: title and description from the page.

**Withheld:** the street and the postcode of the workplace — in the row
and in the location fact («Kingosvej 1-7, 8230» gone, «Åbyhøj, Denmark»
kept); the facts that name a contact («1. Kontaktperson», telephone,
e-mail, «ansvarlig»); e-mail addresses and telephone numbers in the
advert; the application form never touched; `contacts_withheld` on every
record.

## Tests and mutations

`AnATSWhoseCareerSitePostsItsOwnSectionConfigToGetPageAndWhoseVacancyCarriesTheWholeAdvertAndTheContactInItsFacts`,
both ways on fixtures (the config replayed with the page's section, size,
sort and language, the walk to the stated 35 over two calls, the root
without a section falling to `/ledige-stillinger`, `--page`, the address
trimmed in the row and the fact, the contact fact dropped, the description
scrubbed, the country from the location and the stamp, the bounded walk, a
repeating call, the empty tenant, the challenge, a non-Emply page, the ad
page balanced across nested divs and scrubbed, a gone ad, bad addresses,
other hosts refused, bad tenants). Mutation bench on a detached copy,
`python3 -B`, 10 / 10 red: the section not the page's · the offset not
advancing · a repeat tolerated · the location fact raw · the contact fact
kept · the description not scrubbed · the challenge read as empty · the
country filter dropped · a nested div ending the ad · the address segments
kept. *A postcode rule was found redundant with the digit rule by the
bench and removed.*
