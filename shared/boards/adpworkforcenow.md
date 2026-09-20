# Board adapter — ADP Workforce Now (an ATS, one tenant at a time): the tenant's Career Center on `workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=<guid>` is a 19 KB shell identical for every tenant, and the app fills its list by `GET …/careercenter/public/events/staffing/v1/job-requisitions?cid=…` — replayed with the page's parameters, `$top` capped at 20 by the service and a one-based `$skip`, to the stated `totalNumber`; `adpworkforcenow.py`

<!-- verified: 2026-09-20 -->

<!-- hosts: workforcenow.adp.com -->
<!-- host-forms: workforcenow.adp.com -->
<!-- host-forms-basis: read — `adpworkforcenow.py` names the one host as a literal (`HOST`) and refuses any other before the gate (exit 7); the tenant is a `cid` GUID in the query, never a host, so the form is closed · 2026-09-20 -->
<!-- script: adpworkforcenow.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants and one requisition, 2026-09-20 12:36–12:4x UTC, the declared client, the guard on the exact path, 2 s between requests. Rules: `workforcenow.adp.com/robots.txt` answers 200 with a page that is not a rules file — an absence since #283, certain False. The Career Center page (200, 19 449 B, md5 a38e11298f9d — the same bytes for both tenants, on two reads each) is ADP's MDF shell («Please switch to a supported browser…» to a client without JavaScript); the calls its app makes, read in a connected tab (`performance.getEntries`, the query strings redacted by the tool, the paths read): `client-features`, `allow-login`, `content-links/career-center`, `job-requisitions/getSearchFilters` and `job-requisitions?cid&ccId&lang&locale&$top` — replayed by the declared client without token or cookie: tenant `4f8b9ec0-…` (a Kauai employer) `meta.totalNumber 11`, 11 requisitions (itemID, requisitionTitle, postDate, clientRequisitionID, workLevelCode, requisitionLocations[{address{cityName, countrySubdivisionLevel1, postalCode}, nameCode.shortName «Kalaheo, HI, US»}], customFieldGroup with ExternalJobID, JobClass, InternalPostingFlag…); tenant `89da4960-…` `totalNumber 85` — `$top=100` answers 20 (the service's cap), `$skip` is one-based (`$skip=0` and `1` both start at the first item; the page asks 1, 21, 41…), five pages of 20 walked, 85 distinct; `job-requisitions/606158` (the ExternalJobID, the id the Career Center's own ad URL carries as `jobId` — a tab with `jobId=606158` fetches exactly that path) answers the same fields plus `requisitionDescription` (HTML, 10 474 B); the address carries no `countryCode` — the country is the last token of the location's name** · 2026-09-20 -->
<!-- witness: the service's own `meta.totalNumber` — `adpworkforcenow.py jobs` prints it beside the emitted count (11 and 85 on 2026-09-20, equal) · 2026-09-20 -->
<!-- route: http · 96 · 2026-09-20 -->

**Issue #462 (opened under #406, the ATS families). Tenants found by the
signature `workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=…`
on 2026-09-20 (a Kauai employer, a US retailer with 85 postings, others on the
search engine's page), measured by the declared client after the page's
calls were read in the user's Chrome, two tenants with requisitions as the
README's two-tenant rule asks.** Rank: the pilot's order of 2026-09-18 —
the ATS families in number order after the country searches of 2026-09-20.

## What ADP Workforce Now is, and where its tenants live

ADP Workforce Now is a US payroll and HR suite whose recruiting module hosts
the employer's «Career Center». **The hosted page is
`https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=<guid>&ccId=<id>&lang=<xx_XX>`** —
`cid` names the tenant, `ccId` the career center (`19000101_000001` for
every tenant seen), `lang` the language; an ad is the same page with
`&jobId=<ExternalJobID>`. The user names the tenant by the GUID or pastes
the URL; the GUID is read, never composed.

## The route — the call the page makes, with its own parameters

```
GET …/careercenter/public/events/staffing/v1/job-requisitions?cid=4f8b9ec0-…&ccId=19000101_000001&lang=en_US&locale=en_US&$top=20&$skip=1    200 — totalNumber 11, 11
GET …/job-requisitions?cid=89da4960-…&$top=20&$skip=1 · 21 · 41 · 61 · 81                                                                 200 — totalNumber 85, 20+20+20+20+5
GET …/job-requisitions/606158?cid=4f8b9ec0-…                                                                                              200 — requisitionDescription
```

No token, no cookie: the service answers the client with the page's own
parameters (a `timeStamp` the page adds, sent too). **`$top` above 20 is
answered with 20 and `$skip` is one-based** — a pager mis-read as zero-based
drops the first item of every page after the first; the guard walks both.
The adapter stops on a page that repeats (exit 6) and at the stated
count's last page; internal-only postings (`InternalPostingFlag`) are
skipped and the count line says so when they make the total differ.

## What the adapter emits, and withholds

`jobs --tenant <guid> [--cc-id X] [--lang xx_XX] [--country-code ISO2]
[--max-pages N]`: id (itemID), ref (the client's requisition id),
external_id (the `jobId` of the ad page), url, title, country (from the
location's name), place, region, location, work_level, job_class, posted,
and «N emitted — the service states M: equal / k short (internal postings
are skipped) / walked N page(s) by request». `ad --url`: the same fields
and description (text, scrubbed).

**Withheld:** postal codes never emitted; descriptions scrubbed of e-mail
addresses and telephone numbers; `screeningRequirements`,
`sponsoredVisaTypeCodes` and the tracking fields not emitted;
`contacts_withheld` on every record; the application (an ADP account)
never touched.

## Tests and mutations

`AnATSWhoseCareerCenterListsRequisitionsByAOneBasedSkipCappedAtTwentyAndStatesTheTotal`,
both ways on fixtures (`$top=20` and `$skip` 1 then 21 to the stated total,
the country from the location's name, no postal code, internal postings
skipped and said, the empty tenant, the country filter, the bounded walk,
the repeating pager, the ad by its ExternalJobID scrubbed, other hosts
refused, bad tenants and a malformed `ccId` refused before any request).
Mutation bench on a detached copy (`bin/mutation-bench.py`, `python3 -B`),
7 / 7 red: `$skip` made zero-based · internal postings emitted · the postal
code emitted · the country from the name dropped · the description not
scrubbed · the repeat guard dropped · the country filter dropped.
