# Board adapter — Cornerstone OnDemand (an ATS, one tenant at a time): the tenant's career site on `<slug>.csod.com` is a shell whose `csod.context` carries an anonymous per-visitor token and the search API's host, and the page fills its list by `POST <cloud>/rec-job-search/external/jobs` — replayed with the page's own parameters, paged to the stated count; `cornerstone.py`, people's ids never emitted

<!-- verified: 2026-09-19 -->

<!-- hosts: henkel.csod.com, laerdal.csod.com, eu-fra.api.csod.com -->
<!-- host-forms: {slug}.csod.com, {region}.api.csod.com -->
<!-- host-forms-basis: read — `cornerstone.py` admits a host by `TENANT_HOST_RE` (`<slug>.csod.com`) or `API_HOST_RE` (`<region>.api.csod.com`) in `is_ours()`, refused before the gate otherwise (exit 7); the API host is the one the page names in `endpoints.cloud`, never composed · 2026-09-19 -->
<!-- script: cornerstone.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants, 2026-09-19 14:0x UTC, the declared client, the guard on the exact path, 10 s between requests to a tenant host (its own Crawl-delay). Rules: `<slug>.csod.com/robots.txt` is `User-agent: *` / `Crawl-delay: 10` behind a byte-order mark — read as «no group» by the guard until #738, fixed the same day; the API host's rules path answers a page that is not a rules file (an absence, certain False). The career site `/ux/ats/careersite/<site>/home?c=<slug>` (200; 5 479 B for Henkel, 5 318 B for Laerdal — a token moves between reads) is `<div id="cs-root">` plus `csod.context` (`corp`, `user: -100`, `cultureID`, `cultureName`, `endpoints.cloud`, `token` — a JWT issued to every visitor, three hours long, listing the services it opens) and it sets session cookies (`ASP.NET_SessionId`, `cscx`). The page's list call `POST https://eu-fra.api.csod.com/rec-job-search/external/jobs` with `Authorization: Bearer <token>` and the page's own body (`careerSiteId`, `pageNumber`, `pageSize: 25`, `cultureId`, `countryCodes`…) answers `data.totalCount` and `data.requisitions[]` (`requisitionId`, `displayJobTitle`, `locations[{city, state, country}]`, `postingEffectiveDate`, `postingExpirationDate`, `externalDescription` as text): Henkel states 1 083 (25 a page; `countryCodes: ["PL"]` → 12, a filter that reduces; 2 pages walked = 50 distinct), Laerdal states 20 (US 18, 2 without a country) — 20 emitted, equal. The requisition's `GET https://<slug>.csod.com/services/x/job-requisition/v2/requisitions/<id>/jobDetails?cultureId=N` answers 200 with the page's cookies and token (401 «Check your credentials» without the cookies): `displayTitle`, `ref`, `externalDescription` (HTML), `primaryLocation`, `additionalLocations`, `openDate`, `allowApply`, `companyApplyUrl`, and `hiringManagerId`, `owners`, `reviewers`, `positionOUId`** · 2026-09-19 -->
<!-- witness: the search API's own `data.totalCount` — `cornerstone.py jobs` prints it beside the emitted count (Henkel 1 083, Laerdal 20 on 2026-09-19) · 2026-09-19 -->
<!-- route: http · 1103 · 2026-09-19 -->

**Issue #456 (opened under #406, the ATS families). Tenants found by the
signature `csod.com/ux/ats/careersite` on 2026-09-18 (Henkel, Laerdal,
Cornerstone's own, universities), measured 2026-09-18 09:25 UTC (the shells)
and 2026-09-19 14:0x UTC (the calls) by the declared client, the guard on the
exact path, two tenants with positions as the README's two-tenant rule asks.**
Rank: the pilot's order of 2026-09-18 — #455 BambooHR (blocked, no tenant by
its signature) then #456.

## What Cornerstone is, and where its tenants live

Cornerstone OnDemand is the software behind an employer's «Careers» page —
Henkel, Laerdal, the College of DuPage, Duquesne, Cornerstone itself. **The
hosted career site is `https://<slug>.csod.com/ux/ats/careersite/<site>/home?c=<slug>`**
and a requisition `…/home/requisition/<id>?c=<slug>`; the user names the tenant
as `<slug>/<site>` — the subdomain and the site number the URL spells
(`henkel/1`, `laerdal/4`) — or pastes the career-site URL.

## The route — two calls the page makes, replayed with the page's own parameters

```
GET  https://henkel.csod.com/ux/ats/careersite/1/home?c=henkel                                  200 — csod.context: corp, cultureID 2, en-GB, endpoints.cloud, token; cookies set
POST https://eu-fra.api.csod.com/rec-job-search/external/jobs   (Bearer token, JSON body)         200 — totalCount 1 083, 25 requisitions a page
POST …  countryCodes: ["PL"]                                                                    200 — totalCount 12: the filter reduces
GET  https://henkel.csod.com/services/x/job-requisition/v2/requisitions/88785/jobDetails?cultureId=2   200 with the page's cookies + token · 401 without the cookies
GET  https://laerdal.csod.com/ux/ats/careersite/4/home?c=laerdal → the API                        200 — totalCount 20, 20 emitted
```

**The token is anonymous and issued to every visitor** (`sub: -100`, three
hours) — the same shape as SparkHire's public careers token and StaffPoint's
`Next-Action` id (the pilot's judgment of 2026-09-14): the plugin replays the
URL the page calls, with the parameters the page carries, and the cookies the
page was given, and nothing else. The adapter checks that the page's `corp` is
the address's slug (exit 6 otherwise), that `endpoints.cloud` is a
`*.api.csod.com` host (exit 6), and refuses any other host before the gate
(exit 7). The tenant host's `Crawl-delay: 10` is read by `Pace` — a walk of
Henkel's 1 083 is 44 pages at 2 s on the API host, plus the page at 10 s.

## What the adapter emits, and withholds

`jobs --tenant <slug>/<site> [--country-code ISO2] [--max-pages N]`: id (the
requisition id), url (the requisition page), title, company (the slug),
country / countries, place, region, posted, expires, description (text,
scrubbed), and «N emitted — the API states M» (equal, k short, or «walked N
page(s) by request, not a shortfall»); an API stating 0 prints «0
requisitions … not an error». `ad --url`: one requisition through
`jobDetails` — title, ref, location, posted, apply_open, description.

**Withheld:** `hiringManagerId`, `owners`, `reviewers`, `positionOUId`
(people's and org units' ids) never emitted, not even as keys; descriptions
scrubbed of e-mail addresses and telephone numbers; the token used for the two
calls and never printed; `contacts_withheld` on every record; the apply
workflow never touched.

## Tests and mutations

`AnATSWhoseTenantPageIssuesAnAnonymousTokenAndWhoseSearchAPIPagesTheRequisitionsWithTheirStatedCount`,
both ways on fixtures (the token in the header and never in the output, the
body's fields, the pager to the stated count, the country filter in the
request, the empty tenant, the bounded walk, the repeating pager, the foreign
`corp`, a foreign cloud host, the ad with a person's ids, other hosts refused,
bad tenants refused before any request). Mutation bench on a detached copy
(`bin/mutation-bench.py`, `python3 -B`), 7 / 7 red: the token not sent · the
hiring manager emitted · the description not scrubbed · the country filter
dropped · the corp check dropped · the repeat guard dropped · the pager stopped
after page one.
