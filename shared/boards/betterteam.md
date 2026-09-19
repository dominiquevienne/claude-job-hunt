# Board adapter — Betterteam (a small-business ATS, one tenant at a time): the tenant's hosted careers page on `<slug>.betterteam.com` is rendered on the server with one card per open position, and the position page carries a JobPosting — no API, no token; `betterteam.py`

<!-- verified: 2026-09-20 -->

<!-- hosts: careers.betterteam.com, pandarg-117.betterteam.com, carilionclinic.betterteam.com -->
<!-- host-forms: {slug}.betterteam.com -->
<!-- host-forms-basis: read — `betterteam.py` admits a host by `HOST_RE` (`<slug>.betterteam.com`) and refuses `www`, `app` and `s` (the marketing site, the dashboard, the asset host) before the gate (exit 7); the tenant is the subdomain the careers URL spells, so the form is closed · 2026-09-20 -->
<!-- script: betterteam.py -->
<!-- countries: * -->
<!-- content: measured · **five tenants and one position, 2026-09-19 22:1x UTC, the declared client, the guard on the exact path, 2 s between requests. Rules: `<slug>.betterteam.com/robots.txt` refuses `/resumes/` and `/cdn-cgi/` to `*` and nothing else, no Crawl-delay. The careers page (200; 13 777 B for Betterteam's own `careers`, 12 539 B for Panda Restaurant Group `pandarg-117`, 6 911 B for Carilion Clinic `carilionclinic` — identical on two reads each) is React Router rendered on the server (`ssr: true`; the loader data streams in a turbo-stream the markup does not need): a «Current Positions» section, one card per position — `<a class="font-semibold text-lg …" href="/<slug>">Title</a>` then a `text-sm` line of Remote / a place with a tooltip carrying the full postal address / a country / the employment type, joined by «•». Panda 7 cards (Cleveland, Collegedale, Dalton, Chattanooga, Fort Oglethorpe — Tennessee and Georgia, Part-time and Full-time), Betterteam 2 (Remote • Australia, Remote • Philippines), Carilion Clinic 0 («doesn't have any openings right now»); `nowhospitality` and `hivetalent` answer 404 «Page Not Found» ×2 (4 292 B, one body) — tenants gone. No count is stated anywhere: the cards are the board. The position `/assistant-manager-general-manager` on Panda (200, 31 260 B ×2) carries a schema.org JobPosting — title, description (HTML), datePosted 2024-04-13, employmentType FULL_TIME, hiringOrganization (name, sameAs), jobLocation (a PostalAddress with the street), baseSalary USD 72 000–100 000 a year, identifier (the tenant's name, the position's slug), `directApply: true`** · 2026-09-20 -->
<!-- witness: none — no count is stated; `betterteam.py jobs` prints the number of cards the page carries and says so · 2026-09-20 -->
<!-- route: http · 9 · 2026-09-20 -->

**Issue #459 (opened under #406, the ATS families). Tenants found by the
signature — a subdomain of `betterteam.com` whose page is titled
«<Employer> Careers» (`careers`, `pandarg-117`, `carilionclinic`,
`ptaclinic`, `primarycarechandler`, `completecare`, `geckohospitality-24`,
`selfincorp-3`) — measured by the declared client, the guard on the exact
path, two tenants with positions as the README's two-tenant rule asks, one
without, two gone.** Rank: the pilot's order of 2026-09-18 — #456, #457,
#458, then #459.

## What Betterteam is, and where its tenants live

Betterteam is hiring software for restaurants, clinics, agencies and
family-run companies; it distributes a posting to job boards and hosts the
employer's «Careers» page on **`https://<slug>.betterteam.com/`**, each
position at `/<position-slug>`. The user names the tenant by that
subdomain (`pandarg-117`) or pastes the careers URL. The subdomain is the
employer's choice, sometimes suffixed by a number (`pandarg-117`,
`geckohospitality-24`) — it is read from the URL, never composed.

## The route — one page, read as a browser would see it

```
GET https://pandarg-117.betterteam.com/                                 200 — 7 cards in the markup
GET https://careers.betterteam.com/                                     200 — 2 cards, both Remote
GET https://carilionclinic.betterteam.com/                              200 — «doesn't have any openings right now»
GET https://nowhospitality.betterteam.com/                              404 — «Page Not Found»: no such tenant today (exit 3)
GET https://pandarg-117.betterteam.com/assistant-manager-general-manager 200 — a JobPosting
```

No API, no token, no cookie: the list is in the served markup and the ad in
its JSON-LD. The adapter dies with 6 on a 200 that carries neither a card
nor the «Current Positions» section nor the «no openings» sentence — a
changed page, never an empty board.

## What the adapter emits, and withholds

`jobs --tenant <slug> [--country-code ISO2]`: id (the position's slug), url,
title, company (from the page's title), remote, place, region, country (as
the page names it — «United States», «Australia»; the filter accepts the
ISO2 code or the name), employment_type, location (the card's own line),
and «N emitted of the M cards the page carries — no count is stated
anywhere». `ad --url`: the JobPosting — title, company, employer_url,
place, region, country (ISO2 in the JSON-LD), posted, employment_type,
salary (currency, min, max, unit), description (text, scrubbed).

**Withheld:** the tooltip's street line and the JSON-LD's `streetAddress`
not emitted (the place and region are); descriptions scrubbed of e-mail
addresses and telephone numbers; `contacts_withheld` on every record; the
application (`/apply`, Betterteam's form) never touched.

## Tests and mutations

`ASmallBusinessATSWhoseHostedCareersPageRendersEveryPositionAsACardAndWhosePositionPageCarriesAJobPosting`,
both ways on fixtures (the cards with their place, region, country and type,
the remote card's country, the country filter by code or name, the empty
tenant, the gone tenant (3), the changed page (6), the ad scrubbed with the
street left out, other hosts refused, bad tenants refused before any
request). Mutation bench on a detached copy (`bin/mutation-bench.py`,
`python3 -B`), 7 / 7 red: the card regex broken · the tooltip's street
emitted · the description not scrubbed · the country filter dropped · the
gone tenant made a 6 · the changed-page check dropped · the remote flag
dropped.
