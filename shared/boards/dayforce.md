# Board adapter — Dayforce, ex-Ceridian (an ATS, one tenant at a time): the tenant's candidate portal on `jobs.dayforcehcm.com/<lang>/<slug>/<board>` is a Next.js page whose app posts `/api/geo/<slug>/jobposting/search` with next-auth's CSRF token and the portal's cookies — replayed as the page does, paged 25 at a time to the stated `maxCount`; the ad from the requisition page's own `__NEXT_DATA__`; `dayforce.py`

<!-- verified: 2026-09-20 -->

<!-- hosts: jobs.dayforcehcm.com -->
<!-- host-forms: jobs.dayforcehcm.com -->
<!-- host-forms-basis: read — `dayforce.py` names the one host as a literal (`HOST`) and refuses any other before the gate (exit 7); the tenant is a path segment (`/<lang>/<slug>/<board>`), never a subdomain (the older `<tenant>.dayforcehcm.com/CandidatePortal` form of the issue serves only the tenants' images today), so the host form is closed · 2026-09-20 -->
<!-- script: dayforce.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants and one requisition, 2026-09-19 14:3x and 2026-09-20 14:0x UTC, the declared client, the guard on the exact path, 2 s between requests. Rules: `jobs.dayforcehcm.com` answers its rules path 200 with a page that is not a rules file — an absence since #283, certain False. The portal `/en-US/car/CANDIDATEPORTAL` (200; 433 962 B, a build token moves between reads) is Next.js with `USE_SSR`: `__NEXT_DATA__` dehydrates only `site-info` (`clientId 25775`, `jobBoardId 1`, the board's settings, `candidateCorrespondenceClientName` — and `clientCorrespondanceEmailAddress`, never emitted); the list is fetched by the app. The calls, read in the `_app` chunk (an axios interceptor sets `X-CSRF-TOKEN` from next-auth's `getCsrfToken()` on every POST; the search hook posts the router's query with `paginationStart: (page − 1) × 25`) and replayed by the client: `GET /api/auth/csrf` → `csrfToken`; `POST /api/geo/car/jobposting/search` with the token and the portal's cookies → `maxCount 15`, `offset`, `count`, `jobPostings[]` (jobPostingId, jobReqId, jobTitle, jobDescription as text, posting start/expiry, isEvergreen, hasVirtualLocation, postingLocations[{formattedAddress, cityName, stateCode, isoCountryCode}], postingAppliedStatus, searchScore) — 403 «Forbidden» without the token. Carnegie Museums (`car`): 15 stated, 15 emitted, equal; WoodmenLife (`woodmenlife`): 36 stated, two pages (`paginationStart` 0 and 25), 36 emitted, equal. The requisition `/en-US/car/CANDIDATEPORTAL/jobs/12216` (200, 351 093 B) dehydrates the `jobs` query in its `__NEXT_DATA__`: jobTitle, jobReqId, posting start/expiry, isoCurrencyRegion, jobPostingContent (header, description, footer as HTML), postingLocations, jobPostingAttributes (JobFamily, PayType) — served to the client, no call** · 2026-09-20 -->
<!-- witness: the search API's own `maxCount` — `dayforce.py jobs` prints it beside the emitted count (15 for `car`, 36 for `woodmenlife` on 2026-09-20) · 2026-09-20 -->
<!-- route: http · 51 · 2026-09-20 -->

**Issue #458 (opened under #406, the ATS families). Tenants found by the
signature `dayforcehcm.com/CandidatePortal` on 2026-09-19 — today spelled
`jobs.dayforcehcm.com/<lang>/<slug>/CANDIDATEPORTAL` (Carnegie Museums of
Pittsburgh `car`, WoodmenLife, Progressive AE, Door County, Dayforce's own
`hcmportal`) — measured by the declared client, the guard on the exact
path; the list call read in the page's `_app` chunk after the browser
extension dropped mid-hook, two tenants with postings as the README's
two-tenant rule asks.** Rank: the pilot's order of 2026-09-18 — #456, #457,
then #458.

## What Dayforce is, and where its tenants live

Dayforce is a North-American HR suite whose hiring module publishes the
employer's «Careers» page. **The hosted portal is
`https://jobs.dayforcehcm.com/<lang>/<slug>/<board>`** (`car/CANDIDATEPORTAL`),
a requisition `…/jobs/<id>`; the user names the tenant by its namespace
(`car`), the board (`CANDIDATEPORTAL` by default) and the language
(`en-US` by default), or pastes the portal URL.

## The route — the calls the page makes, replayed with the page's own parameters

```
GET  https://jobs.dayforcehcm.com/en-US/car/CANDIDATEPORTAL              200 — Next.js, site-info dehydrated, next-auth cookies set
GET  https://jobs.dayforcehcm.com/api/auth/csrf                          200 — {"csrfToken": …}
POST https://jobs.dayforcehcm.com/api/geo/car/jobposting/search          200 — maxCount 15, 15 postings   (X-CSRF-TOKEN + the cookies; 403 without)
POST …/api/geo/woodmenlife/jobposting/search  paginationStart 0, then 25  200 — maxCount 36, 25 + 11
GET  https://jobs.dayforcehcm.com/en-US/car/CANDIDATEPORTAL/jobs/12216   200 — the requisition in __NEXT_DATA__
```

The token is next-auth's anonymous CSRF token, issued to every visitor of
the portal, and the cookies are the ones the portal sets — the same shape as
Cornerstone's per-visitor token and Harri's CSRF header (the 14.09 judgment):
the plugin replays the URL the page calls, with the parameters and headers
the page carries. The adapter checks that the page's `clientNamespace` is the
address's (exit 6 otherwise), stops on a pager that repeats (exit 6) and at
the stated count's last page, and refuses any other host before the gate
(exit 7).

## What the adapter emits, and withholds

`jobs --tenant <slug> [--board X] [--lang xx-XX] [--country-code ISO2]
[--max-pages N]`: id, ref (the requisition id), url (the requisition page),
title, company (the board's correspondence client name), country /
countries, place, region, location, remote, posted, expires, evergreen,
description (text, scrubbed), and «N emitted — the search states M: equal /
k short / walked N page(s) by request, not a shortfall»; a `maxCount` of 0
prints «0 postings … not an error». `ad --url`: the page's dehydrated
requisition — title, ref, location, posted, expires, currency, pay_type,
job_family, description (header + body + footer, scrubbed).

**Withheld:** `clientCorrespondanceEmailAddress` (the employer's HR
address in `site-info`) never emitted; `postingAppliedStatus`,
`searchScore`, assessment and application-template ids not emitted;
descriptions scrubbed of e-mail addresses and telephone numbers;
`contacts_withheld` on every record; the application (an account, a form)
never touched.

## Tests and mutations

`AnATSWhosePortalPostsItsSearchWithNextAuthsCSRFTokenAndDehydratesTheRequisitionInItsPage`,
both ways on fixtures (the csrf call then the search with the token — a
search without it answers 403 in the fixture —, `paginationStart` 0 then 25
to the stated count, the empty tenant, the country filter, the bounded walk,
the repeating pager, the foreign namespace, the ad from `__NEXT_DATA__`
without a call, the correspondence address absent, other hosts refused, bad
tenants refused before any request). Mutation bench on a detached copy
(`bin/mutation-bench.py`, `python3 -B`), 7 / 7 red: the CSRF header
dropped · `paginationStart` never moving · the repeat guard dropped · the
namespace check dropped · the description not scrubbed · the correspondence
address emitted · the country filter dropped.
