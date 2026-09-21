# Board adapter — Factorial (an ATS, one tenant at a time): the tenant's career page on `<tenant>.factorial.es` / `<tenant>.factorialhr.com` renders its whole job list as `li.job-offer-item` cards next to a team section full of employee names — the cards read, the team never; each ad on `/job_posting/<slug>-<id>` carries one JobPosting; `factorial.py`, the street and the postal code never emitted

<!-- verified: 2026-09-21 -->

<!-- hosts: careers.factorialhr.com, kampaoh.factorial.es, vegenat.factorial.es, diaconia.factorial.es -->
<!-- host-forms: {tenant}.factorial.es, {tenant}.factorialhr.com -->
<!-- host-forms-basis: read — `factorial.py:95` (`host_of`: `--tenant` is REQUIRED, a subdomain, a host or an address on it, resolved to `<tenant>.factorial.es` unless a host under one of the vendor's domains is given, `factorial.py:61`; the vendor's own subdomains refused, `factorial.py:62`; `request()` refuses any other host before the gate) · 2026-09-21 -->
<!-- script: factorial.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants with positions and two without, 2026-09-21 08:03–08:05 UTC, the declared client, the guard on the exact path, two reads each (identical bodies). Rules: every tenant's file read and open, no Crawl-delay. The career page `/` (200) renders values, benefits, offices, **a team section with employee names, roles and portraits** (Vegenat: dozens of names), and the jobs as `li.job-offer-item` cards — `data-job-postings-url='https://<tenant>/job_posting/<slug>-<id>'`, `data-contract-type`, `data-is-remote`, `data-location-id`, `data-team-id`, three text cells (title, team, workplace mode «Onsite» / «Presencial»); a spontaneous-application card carries no posting url and is not a position: **Factorial's own `careers.factorialhr.com` 135 cards (263 310 B), Kampaoh 1 + the spontaneous card (57 320 B), Vegenat 0 (181 390 B), DIACONÍA 0 (70 909 B)**; no count stated anywhere, no JobPosting on the list. The ad `careers.factorialhr.com/job_posting/it-systems-engineer-323635` (200 ×2, 44 496 B) carries one JobPosting — title, description, datePosted, identifier (the id), hiringOrganization, jobLocation with a **full street address in `streetAddress`** («Calle Anade Real, 11 - Perillo, 15173 - Oleiros, A Coruña»), postalCode, locality, addressCountry «ES»; the page prints the contract, the schedule and a salary band («€30,000 - €42,800 Annual»). Exercised offline on the held bodies (135 / 1 / 0 cards) and on the ad; the live `jobs` and `ad` runs are the measurement above (the same requests)** · 2026-09-21 -->
<!-- witness: none — no count is stated anywhere; `factorial.py jobs` prints the cards the page carries beside the emitted count · 2026-09-21 -->
<!-- route: http · 135 · 2026-09-21 -->

**Issue #486 (opened under #406, the ATS families; 15 cards on 239 in
Portugal). Measured 2026-09-21 08:03–08:05 UTC by the declared client, the
guard on the exact path, on four tenants named by the family's signature
(«Ofertas de empleo, oficinas y equipo» on `factorial.es` in a search
engine, and the vendor's own careers host): Factorial (135), Kampaoh (1),
Vegenat (0), DIACONÍA (0).** Rank: the pilot's order of 2026-09-21 06:13
UTC — #479 → #488 after the dated controls.

## What Factorial is, and where its tenants live

Factorial (Barcelona) is an HR suite for SMEs; its recruiting module hosts
one «career page» per employer on `<tenant>.factorial.es` (Spain, the
default), `<tenant>.factorialhr.com` (Factorial's own on `careers.`), and
the vendor's other country domains. **The user names the tenant** by its
subdomain, its host, or any address on it.

## The route — the page, whole

```
GET https://careers.factorialhr.com/                                        200 — 135 li.job-offer-item cards
GET https://kampaoh.factorial.es/                                           200 — 1 card + the spontaneous-application card (no posting url)
GET https://vegenat.factorial.es/                                           200 — 0 cards: «0 positions», not an error
GET https://careers.factorialhr.com/job_posting/it-systems-engineer-323635  200 — one JobPosting (the `ad` command)
```

One request for the whole board: every card is in the page, no pager, no
count stated. A card whose posting url is on another host is not this
board's; a duplicated id is one position. **The team section is never
read**: its names, roles and portraits are the employer's people, not the
board. `--country-code` **stamps** on the list (the cards state no
country) and says so; on the ad it filters on the posting's own country.

## What the adapter emits, and withholds

`jobs --tenant <tenant> [--country-code ISO2]`: id, url, title, team,
workplace (the card's mode label), contract (`data-contract-type`),
remote (`data-is-remote`), location_id, team_id. `ad --url`: the page's
JobPosting — title, company, reference, place, region, country,
employment_type, published, expires, description (text, scrubbed).

**Withheld:** the team section (names, roles, portraits); the JobPosting's
`streetAddress` (a full postal address) and `postalCode`; every e-mail
address and telephone in the description replaced by «[e-mail withheld]»
/ «[telephone withheld]» — a date («01/11/2026») is left alone;
`contacts_withheld` on every record; the application never touched.

## Tests and mutations

`AnATSWhoseCareerPageRendersItsJobCardsNextToItsTeamsNames`, both ways on
fixtures (the cards with a remote one, another tenant's card, a duplicated
id and the spontaneous card next to a team section — the names never in
the output; the stamp said; a page without cards; a page without the
module; a 404; the vendor's hosts and another host refused; the ad with
its full street and contact, the ad's country filter, the ad gone or
changed). Mutation bench on a detached copy, `python3 -B` — see the PR.
