# Board adapter — Hiring Room (Latin America's ATS, one tenant at a time): the tenant's `/jobs` states its count and fills its list by `POST /jobs/getVacanciesForPortal/<page>` — the call its own script makes — twenty a page to an empty page; the advert page's hero and sections; `hiringroom.py`, the apply link never followed

<!-- verified: 2026-09-21 -->

<!-- hosts: kpmg.hiringroom.com, ecuaquimica.hiringroom.com, fravega.hiringroom.com -->
<!-- host-forms: {tenant}.hiringroom.com -->
<!-- host-forms-basis: read — `hiringroom.py:DOMAIN` with the tenant as its subdomain (`tenant_of`), one per run, every other host refused before the gate; the vendor's `www`, `jobs` (the aggregated portal) and the apex are not tenants · 2026-09-21 -->
<!-- script: hiringroom.py -->
<!-- countries: * -->
<!-- content: measured · **three tenants, 2026-09-21 06:34–06:38 UTC, the declared client, the guard on the exact path first, each list read twice. Rules: `/robots.txt` on a tenant answers HTTP 404 with the application's own page (81 896 B) — no rules, `certain: True`; the vendor's apex publishes 149 B closing a few non-job paths (13.09). `/jobs` (200; KPMG Argentina 220 869 B, Frávega 124 516 B) prints «Ver N vacantes», declares `typePortal = "external"` and renders the first twenty cards; its `main.js` (25 008 B) fills the list by `POST /jobs/getVacanciesForPortal/<page>` (form fields `typePortal`, `selectedPage`, the ticked filters) whose JSON answers `result: success`, `data.total_vacancies`, `data.htmlContent` (the cards), `data.paginationLabel` («21-40 de 49 vacantes»); the page past the last answers no card («61-49 de 49»). `hiringroom.py jobs` live: **KPMG Argentina 49 emitted over 3 pages (20 + 20 + 9), the call states 49 — equal; Ecuaquímica 39 = 39; Frávega 0 = 0 (an empty board that says so)**; one advert read (KPMG «Consultor Data Analyst»: location, area, Full-time / Híbrido / Senior, «Hace 2 meses», three sections). An unknown subdomain answers 404 (exit 3)** · 2026-09-21 -->
<!-- witness: the list call's own `total_vacancies` (the page's «Ver N vacantes» when the call states none) — `hiringroom.py jobs` prints it beside the emitted count after the walk to the empty page: «49 emitted — the list call states 49: equal», «short» when the walk ended before the total (a page of repeats), and says when `--max-pages` cut it · 2026-09-21 -->
<!-- route: http · 49 · 2026-09-21 -->

**Issue #492 (under #406, the ATS families — bloc LATAM). Tenants found by
the family's signature `hiringroom.com/jobs` in a search engine on
2026-09-21: `kpmg` (KPMG Argentina, 49), `ecuaquimica` (Ecuador, 39),
`fravega` (0 today), and `danec`, `lgconsultores`, `empresademo` listed,
not read.** Rank: `votes.sh` read at 06:33 UTC — #492 first `adapter`
issue outside cd's #479–#488 series.

## What Hiring Room is, and where its tenants live

Hiring Room (Buenos Aires) is the ATS many Latin American employers
publish through: each employer's «portal de empleos» is
`<tenant>.hiringroom.com/jobs`, a server-rendered page (jQuery, Bootstrap)
whose list is filled by a POST its own `main.js` makes, twenty cards a
page, with filters (location, area, type, modality, disability) the user
ticks. **The user names the tenant** by its subdomain (`kpmg`), its host
or the `/jobs` URL; the vendor's own hosts are refused before any request.
A «microsite» portal declares `typePortal = "microsite"` and a
`microSiteId` the call carries — read from the page when it is there, not
seen on the three tenants.

## The route — the page's count, then the call its script makes

```
GET  https://kpmg.hiringroom.com/jobs                              200 — «Ver 49 vacantes», typePortal = "external", 20 cards
POST https://kpmg.hiringroom.com/jobs/getVacanciesForPortal/1      200 — JSON: total_vacancies 49, 20 cards, «1-20 de 49 vacantes»
POST …/getVacanciesForPortal/2 · /3                                 200 — 20 · 9 cards
POST …/getVacanciesForPortal/4                                      200 — 0 cards, «61-49 de 49»: the walk ends
GET  https://nao-existe-xyz.hiringroom.com/jobs                     404 — not a tenant (exit 3)
```

A card: `a[href="/jobs/get_vacancy/<24-hex>"]`, `h4.name__vacancy` the
title, the location line («Capital Federal, Buenos Aires (fuera de GBA),
Argentina» — the country is its last element, mapped to ISO2 when this
adapter knows the name, `--country-code` otherwise), the area line
(«Área / Subárea»), three tags (schedule, modality, seniority) and a
relative age («Hace 2 meses» — the site prints no date). The key is the
24-hex id; the ledger key `hiringroom:<host>:<id>`.

## The advert — the hero and the sections, no JobPosting

`/jobs/get_vacancy/<id>` (200, ~140 KB): `div.hero__title h2` the title,
the location and area lines, the three hero tags, the relative age, then
`h6` sections each with a `div.job-description-content` — «Descripción
del puesto», «Requisitos», «Beneficios» (HTML) — `description` being the
first and every section under `sections`; the employer from the page's
`<title>` («… en KPMG Argentina»). «Postularse» links the vendor's form on
`hiringroom.com/jobs/get_vacancy/<id>/candidates/new` — never followed,
never emitted.

## Withheld, and the guard

E-mail addresses and telephone numbers scrubbed from the sections; the
apply link, the banners and logos never emitted; `contacts_withheld` on
every record. Guard in `tests/`: the POST's parameters and pages to the
empty one, the stated total beside the emitted number (equal, short), a
repeated id once and a page of repeats ending the walk, the country from
the location and the stamp, the empty board, a non-success answer (6), a
page without `typePortal` (6), a 404 (3), the advert's fields and scrubbed
sections with the apply link never emitted, bad addresses and tenants
refused before any request, another host never sent (7) — 8 mutations on
the committed file, 8 red (2026-09-21).
