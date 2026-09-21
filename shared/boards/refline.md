# Board adapter — Refline (a Swiss ATS, one tenant at a time): the tenant's list on `apply.refline.ch/<tenant>/search.html?form.buttons.listAll=1` is one table whose cells are named by their class, «Es liegen N Angebote vor.» its stated count; each ad carries one JobPosting and a contact block; `refline.py`, the block, the street and the postal code never emitted

<!-- verified: 2026-09-21 -->

<!-- hosts: apply.refline.ch -->
<!-- host-forms: apply.refline.ch -->
<!-- host-forms-basis: read — `refline.py:61` names the one host as a literal; `tenant_of` (`refline.py:97`) takes the six-digit tenant from `--tenant` or from an address on that host, and `request()` refuses any other host before the gate; the mobile mirror `m.refline.ch` is not sent to · 2026-09-21 -->
<!-- script: refline.py -->
<!-- countries: * -->
<!-- content: measured · **three tenants with positions and an unknown number, 2026-09-21 07:30–07:32 UTC, the declared client, the guard on the exact path, two reads each (identical bodies). Rules: one file (1 117 B) — `*` allowed `/`, refused `/rec01/1/` and `/rec03/1/` («demo, no indexing»), eighteen sitemaps declared, no Crawl-delay. The list `/<tenant>/search.html?form.buttons.listAll=1` (200) is one table, no pager, its cells named by their class — `position` (the title's link to `/<tenant>/<id>/pub/<n>[/index.html]`), `workload`, `workplace`, `published` dd.mm.yyyy, `operationArea`, `segment`, `locale`, `department` — the columns the tenant's choice; «Es liegen N Angebote vor.» printed by some tenants: **Empa `673276` 23 stated / 23 rows (13 149 B), FHNW `655298` 16 / 16 (11 259 B), ZKB `792841` none stated / 49 rows (41 280 B)**; no JobPosting on the list. `000001` answers 200 with the vendor's own landing page («Refline - Applicant Tracking System» / «… Bewerbermanagement Software» by the Accept-Language, 63 712 B, no table) — not a tenant, exit 3, never an empty board. The ad `/673276/2176/pub/1/index.html` (200 ×2, 24 058 B) carries one JobPosting — title, description HTML, datePosted ISO with microseconds, validThrough, employmentType `["FULL_TIME", "TEMPORARY"]`, hiringOrganization with a logo, jobLocation with streetAddress, postalCode, locality, region, addressCountry «CH», identifier `refline-673276-master` — and a `contactInfo` block (a name, a telephone, an e-mail); the ZKB ad (13 145 B) writes «Dein Kontakt … Telefon: …» inside the description itself. Exercised: `jobs --tenant https://apply.refline.ch/792841/search.html --country-code ch` → 49 emitted, no count stated, the stamp said; the Empa ad → the posting, its telephone and e-mail withheld; `000001` → exit 3** · 2026-09-21 -->
<!-- witness: the page's own «Es liegen N Angebote vor.» where a tenant prints it (Empa 23, FHNW 16), printed beside the emitted count; where it does not (ZKB) the run says the table is the board · 2026-09-21 -->
<!-- route: http · 49 · 2026-09-21 -->

**Issue #483 (opened under #406, the ATS families; named by `umantis.md`,
present in the job-room feed). Measured 2026-09-21 07:30–07:32 UTC by the
declared client, the guard on the exact path, on three tenants named by the
family's signature (`apply.refline.ch` in a search engine): the Zürcher
Kantonalbank (49), Empa (23), the FHNW (16).** Rank: the pilot's order of
2026-09-21 06:13 UTC — #479 → #488 after the dated controls.

## What Refline is, and where its tenants live

Refline (Zürich) is the applicant-tracking system of Swiss public bodies,
universities, research institutes and banks. Every tenant lives on the one
host `apply.refline.ch` under a six-digit number (`/673276/`); the mobile
mirror `m.refline.ch/<tenant>/` is the same board and not this route.
**The user names the tenant** by its number, or by any `apply.refline.ch`
address that carries it (the search page, an ad).

## The route — one table, one request

```
GET https://apply.refline.ch/673276/search.html?form.buttons.listAll=1   200 — «Es liegen 23 Angebote vor.», 23 rows
GET https://apply.refline.ch/792841/search.html?form.buttons.listAll=1   200 — 49 rows, no count printed
GET https://apply.refline.ch/673276/2176/pub/1                            200 — one JobPosting (the `ad` command)
GET https://apply.refline.ch/000001/search.html?form.buttons.listAll=1   200 — the vendor's landing page: not a tenant, exit 3
```

`form.buttons.listAll=1` is the page's own «list everything» button, sent
as the page sends it. The table's cells are read by their class; a link to
another tenant's ad is not this board's; a duplicated id is one position.
The stated count, when printed, is compared to the emitted one («N emitted,
the page states M — K short»); when not, the run says the table is the
board. `--country-code` **stamps** on the list (it states no country) and
says so; on the ad it filters on the posting's own `addressCountry`.

## What the adapter emits, and withholds

`jobs --tenant <tenant> [--country-code ISO2]`: id, url (`/pub/<n>`,
without `index.html`), title, workload, place (`workplace`), area
(`operationArea`), segment, language (`locale`), published. `ad --url`:
the page's JobPosting — title, company, place, region, country,
employment_type, published, expires, description (text, scrubbed).

**Withheld:** the `contactInfo` block (a name, a telephone, an e-mail)
never read into a record; the JobPosting's `streetAddress`, `postalCode`
and `logo` never emitted; every e-mail address and telephone in the
description replaced by «[e-mail withheld]» / «[telephone withheld]» — a
date («per 01.01.2027») is left alone; `contacts_withheld` on every
record; the application (`/pub/<n>/apply`) never touched.

## Tests and mutations

`AnATSWhoseListIsATableNamedByItsCellsAndWhoseUnknownTenantIsTheVendorsLandingPage`,
both ways on fixtures (the table against a stated count one short, another
tenant's link and a duplicated id dropped, the ZKB columns with no count
and the stamp said, a stated zero, the vendor's landing page, a page
without the list, a 404, malformed tenants, the mirror host refused, the
ad with its contact block, street and logo, the ad's country filter, the
ad gone or changed). Mutation bench on a detached copy, `python3 -B` — see
the PR.
