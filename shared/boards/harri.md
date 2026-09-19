# Board adapter — Harri (a hospitality ATS, one tenant at a time): the tenant's career portal on `harri.com/<slug>` is a shell whose app asks `gateway.harri.com` for the brand behind the slug, its `basic_info` (the stated `active_jobs_count`) and its jobs (`POST harri_search/search_jobs`) — replayed with the page's own parameters; `harri.py`, the ad from the page's JobPosting

<!-- verified: 2026-09-19 -->

<!-- hosts: harri.com, gateway.harri.com -->
<!-- host-forms: harri.com, gateway.harri.com -->
<!-- host-forms-basis: read — `harri.py` names both hosts as literals (`PAGE_HOST`, `API_HOST`) and refuses any other before the gate (exit 7); the tenant is a path (`/<slug>`), never a subdomain, so the host forms are closed · 2026-09-19 -->
<!-- script: harri.py -->
<!-- countries: * -->
<!-- content: measured · **seven tenants, 2026-09-19 14:1x–14:3x UTC, the declared client, the guard on the exact path; the page's calls read once in a connected tab (a standalone navigate, an XHR hook) and replayed by the client the same hour. Rules: `harri.com/robots.txt` is a `*` group refusing `/employee-records` and three tenant paths (`/subway-783-0-1`, `/subway-883-1-1`, one of its ads), nothing else, no Crawl-delay; `gateway.harri.com` answers its rules path 403 — an absence since #283, certain False, and it serves. The portal `/<slug>` (200; 58 734 / 58 846 B for Hogsalt — a token moves) is an Angular shell with `data-brand-id` and no job in its markup; the app calls `GET gateway.harri.com/core/api/v1/profile/slug/<slug>` (200, 252 B: `id`, `career_portal_enabled`), `GET …/core/api/v2/career_portal/brands/<id>/basic_info` (name, type, `location_count`, `active_jobs_count`) and `POST …/core/api/v1/harri_search/search_jobs` with headers `FORCE-CSRF: true`, `X-REFERRER-PAGE: <portal URL>` and the body `{size: 30, source: web, brand_level_ids: [<id>], search_phrase: "", sort: [publish_date], sort_type: desc, flow: CAREER_PORTAL}` → `data.hits`, `data.results[]` (id, brand{id, name, slug}, position{name}, aliasPosition, locations[{city, state, country, country_code, formatted_address}], publishTime, compensation{name, plus_tips…}, brand_media). No `from` / `page` / `offset` moves the page (each answers page 1 on an 11-job tenant); `size` is honoured to 500. A tenant answers `hits: 0` when it has none. The ad `/<brand slug>/job/<id>-<slug>` (200, 75 964 B) carries a schema.org JobPosting (title, description HTML, datePosted, hiringOrganization, jobLocation, employmentType). Hogsalt (`HHospitality`, GP-1, 29 locations): basic_info 6, hits 6, 6 emitted — equal; `careers_us` 11 / 11 / 11; `Harri-Restaurant`, `The-Restaurant-Group` (enterprise, 22 locations), `crg-jobs` (GP-2, 119 locations), `radissoncareersuk`, `careers_uk`: 0 / 0 — no tenant longer than a page was found on 2026-09-19, so the `size = hits` second call is exercised on fixtures only** · 2026-09-19 -->
<!-- witness: two stated counts — basic_info's `active_jobs_count` and the search's `hits` — both printed beside the emitted count by `harri.py jobs` (6 · 6 · 6 for Hogsalt on 2026-09-19) · 2026-09-19 -->
<!-- route: http · 17 · 2026-09-19 -->

**Issue #457 (opened under #406, the ATS families). Tenants found by the
signature `harri.com/<slug>` on 2026-09-19 (Hogsalt, Harri's own, UK groups),
measured by the declared client, the guard on the exact path, two tenants
with jobs (Hogsalt 6, Harri US 11) and five without.** Rank: the pilot's
order of 2026-09-18 — #456 Cornerstone then #457.

## What Harri is, and where its tenants live

Harri is the hiring and workforce software of restaurants, hotels and bars.
**The hosted career portal is `https://harri.com/<slug>`** (Hogsalt is
`/HHospitality`, the group's venues `/HHILTT`, `/HHILCM`…), an ad
`https://harri.com/<brand slug>/job/<id>-<slug>`; the user names the tenant
by its slug or pastes the portal URL. `harri.com/jobs` is Harri's own
cross-tenant search (server-rendered, 25 ads a page) — not a tenant, refused
as one.

## The route — the three calls the page makes

```
GET  https://gateway.harri.com/core/api/v1/profile/slug/HHospitality                 200 — id 7746910, career_portal_enabled true
GET  https://gateway.harri.com/core/api/v2/career_portal/brands/7746910/basic_info   200 — Hogsalt, GP-1, 29 locations, active_jobs_count 6
POST https://gateway.harri.com/core/api/v1/harri_search/search_jobs                  200 — hits 6, 6 results (FORCE-CSRF, X-REFERRER-PAGE, the page's body)
GET  https://harri.com/HHILTT/job/2757301-server-assistant-earn-up-to-1-000-wk-       200 — a JobPosting
GET  https://gateway.harri.com/core/api/v1/profile/slug/Harri-Restaurant → search    200 — hits 0: «0 jobs», not an error
```

The headers and the body are the page's own (the 14.09 judgment on
StaffPoint, Eezy, SparkHire, Cornerstone: a route the page calls, replayed
with its parameters); no token, no cookie is needed. The search's page cannot
be moved, so a list longer than 30 is asked once more with `size = hits`
(to 500) — the cap is printed when it bites, and a tenant beyond 500 is a
measurement to make on the day one is found.

## What the adapter emits, and withholds

`jobs --tenant <slug> [--country-code ISO2]`: id, url (the ad), title (the
posted alias), position, company (the venue's brand), country / countries,
place, region, location, posted, compensation (the label) and plus_tips; and
«N emitted — the search states H hits — basic_info states S: equal / k short».
`ad --url`: the page's JobPosting — title, company, place, region, country,
posted, employment_type, salary, description (text, scrubbed).

**Withheld:** descriptions scrubbed of e-mail addresses and telephone
numbers; brand media and image ids not emitted; `contacts_withheld` on every
record; the application (Harri's form, «Multiple apply», the talent pool)
never touched.

## Tests and mutations

`AHospitalityATSWhosePortalAsksTheGatewayForItsBrandThenItsJobsAndStatesTheCountTwice`,
both ways on fixtures (the three calls and their headers and body, the two
stated counts, the second call at `size = hits`, the 500 cap printed, the
empty tenant, the country filter, a short list, the ad scrubbed, other hosts
refused, bad tenants refused before any request). Mutation bench on a
detached copy (`bin/mutation-bench.py`, `python3 -B`), 7 / 7 red: the
referrer header dropped · the second call never made · the cap note dropped ·
the description not scrubbed · the country filter dropped · brand media
emitted · the stated count not read.
