# Board adapter — Paylocity (an ATS, one tenant at a time): the module's careers page on `recruiting.paylocity.com/recruiting/jobs/All/<guid>` carries every open job in its own `window.pageData.Jobs` — no API, no token, no page; the job page is server-rendered; `paylocity.py`, countries in three letters turned into ISO2 by `_iso3.py`

<!-- verified: 2026-09-20 -->

<!-- hosts: recruiting.paylocity.com, 2000recruiting.paylocity.com -->
<!-- host-forms: recruiting.paylocity.com, {n}recruiting.paylocity.com -->
<!-- host-forms-basis: read — `paylocity.py` admits a host by `HOST_RE` (`recruiting.paylocity.com` and its numbered twins `<n>recruiting.paylocity.com`, the form the search engine returns for older modules) and refuses any other before the gate (exit 7); the tenant is a GUID in the path, so the forms are closed · 2026-09-20 -->
<!-- script: paylocity.py -->
<!-- countries: * -->
<!-- content: measured · **two modules and one job, 2026-09-19 22:1x UTC, the declared client, the guard on the exact path, 2 s between requests. Rules: `recruiting.paylocity.com/robots.txt` answers 404 — an absence of rules, certain. The module page `/recruiting/jobs/All/<guid>` (200; 36 582 B for Peak Support LLC `67c76e24-…`, 67 242 B for Louisiana Machinery's «ALL JOB POSTINGS» `ff517f63-…` — identical on two reads each) is an ASP.NET page whose inline `window.pageData = {…}` carries the whole module — `ModuleTitle`, `ModuleId`, `Departments`, `Locations`, and `Jobs[]`: every open job with `JobId`, `JobTitle`, `LocationName`, `PublishedDate`, `Description` (a ~100-character summary), `IsInternal`, `HiringDepartment`, `IsRemote`, `JobLocation{Name, Address, Address2, City, State, Zip, Country (alpha-3: «PHL», «USA», «CAN»), County, SmartyAddressId}`. No count is stated and nothing pages: the list is the board — Peak Support 17 (PH 12, US 4, CA 1; 16 remote), Louisiana Machinery 62 (all USA). The job page `/Recruiting/Jobs/Details/<JobId>` (200, 26 432 B ×2) is server-rendered: `pageData = {jobTitle, moduleName}`, a `job-preview-header` (title, «Fully Remote • Remote - Philippines, PHL») and a `job-preview-details` block with the description as HTML under «Description»; no JobPosting; the apply link `/Recruiting/Jobs/Apply/<id>`** · 2026-09-20 -->
<!-- witness: none — no count is stated; `paylocity.py jobs` prints the number of jobs pageData carries and says so · 2026-09-20 -->
<!-- route: http · 79 · 2026-09-20 -->

**Issue #460 (opened under #406, the ATS families). Tenants found by the
signature `recruiting.paylocity.com/recruiting/jobs/All/<guid>` on
2026-09-19 (Peak Support LLC, Louisiana Machinery's NAPA stores, Paylocity's
own on the numbered twin `2000recruiting`), measured by the declared client,
the guard on the exact path, two modules with jobs as the README's
two-tenant rule asks.** Rank: the pilot's order of 2026-09-18 — #456 to
#459, then #460.

## What Paylocity is, and where its tenants live

Paylocity is a US payroll and HR suite whose recruiting module hosts the
employer's «Job Opportunities» page. **The hosted page is
`https://recruiting.paylocity.com/recruiting/jobs/All/<guid>/<slug>`** — the
GUID names the module, the slug is decorative («Peak-Support-LLC», «ALL JOB
POSTINGS») — and a job `…/Recruiting/Jobs/Details/<JobId>`. The user names
the tenant by the GUID or pastes the page URL; the GUID is read from the
URL, never composed.

## The route — one page, the list in its markup

```
GET https://recruiting.paylocity.com/recruiting/jobs/All/67c76e24-da8b-4733-a8b3-9c1fe859c5b9   200 — pageData.Jobs: 17
GET https://recruiting.paylocity.com/recruiting/jobs/All/ff517f63-c379-48fb-acc8-8d66e8d5b076   200 — pageData.Jobs: 62
GET https://recruiting.paylocity.com/Recruiting/Jobs/Details/4517495                            200 — the description, server-rendered
```

No API, no token, no cookie, no pager: the module's page carries its whole
list. Internal jobs (`IsInternal`) are skipped. The adapter dies with 6 on
a 200 without `pageData` or without its `Jobs` list — a changed page, never
an empty board; a module answering 404 is gone (exit 3).

## What the adapter emits, and withholds

`jobs --tenant <guid> [--country-code ISO2]`: id, url, title, company (the
module's title), country (ISO2, from the board's alpha-3 through
`_iso3.alpha2` — `PHL` → `PH`, never guessed from a prefix) with
`country_alpha3` beside it, place, region, location (the location's name),
remote, department, posted, summary (the ~100-character text the list
carries, scrubbed), and «N emitted of the M jobs pageData carries — no
count is stated anywhere and nothing pages». `ad --url`: title, company,
the header's location line, description (text, scrubbed).

**Withheld:** the location's street, `Address2`, `Zip`, `County` and
`SmartyAddressId` never emitted; summaries and descriptions scrubbed of
e-mail addresses and telephone numbers; `TrackingPixels`, logos and the
lead-join form not emitted; `contacts_withheld` on every record; the
application (`/Recruiting/Jobs/Apply/<id>`) never touched.

## Tests and mutations

`AnATSWhoseCareersPageCarriesEveryJobInItsOwnPageDataAndWritesCountriesInThreeLetters`,
both ways on fixtures (the list with ISO2 countries and no street, internal
jobs skipped, the country filter by ISO2 on an alpha-3 board, the empty
module, the gone module (3), the changed page (6), the ad's description and
header line, the numbered twin host admitted, other hosts refused, bad
tenants refused, `_iso3.alpha2` on the prefix traps `MEX`, `IRL`, `CHN`).
Mutation bench on a detached copy (`bin/mutation-bench.py`, `python3 -B`),
7 / 7 red: the pageData regex broken · internal jobs emitted · the street
emitted · the summary not scrubbed · the country filter dropped · the alpha-3
guessed from a prefix · the gone module made a 6.
