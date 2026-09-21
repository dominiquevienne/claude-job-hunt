# Board measurement — Government of Saint Lucia web portal (`www.govt.lc`, Saint Lucia): its «Job Opportunities» (`/jobs`) and «Vacancies» (`/vacancies`) pages — the public-sector vacancies — answered HTTP 500 on 2026-09-18 and are served on 2026-09-21: `/jobs` states **14** jobs and inlines all 14, `/vacancies` states 2 718 records of every type (jobs, scholarships, consultancies, tenders); the list is a JSON array in the page, the «No Vacancies to display.» text is a Knockout template branch, not a count; no adapter yet

<!-- verified: 2026-09-21 -->

<!-- hosts: www.govt.lc -->
<!-- script: none -->
<!-- countries: LC -->
<!-- content: measured · **2026-09-21 06:15:02–06:15:06 UTC, two reads each by the declared client: `/jobs` 200 (438 854 B, md5 moving between reads — a ViewState), `/vacancies` 200 (355 812 B, md5 moving); the page initialises `new ResourceSummaryList('Resource', {query}, [items], 'm_summaries_container', {"TotalRecords": N})` — `/jobs`: query `ResourceTypeNames: "jobs"`, 14 items inlined, `TotalRecords: 14` (UrlFolder `jobs` ×14, dates 2024-05-02 → 2026-09-18 — the list is «existing vacancies», some old); `/vacancies`: `ResourceTypeNames: "vacancies"`, 15 items inlined of `TotalRecords: 2 718` (jobs 8, scholarships 4, consultancies 2, tenders 1 on the first page — every resource type, an archive), pager 15 a page through the web method `GetResourceSummaries` on `/admin/resourceapi.asmx/` (POST JSON `{query, cursor: {StartRowIndex, PageSize}}`, read in `Scripts/project/resourceapi.js`, not replayed); each item: Title, Url (`/jobs/<slug>`), Date, LastUpdatedDate, Description (HTML), ResourceSubTypeName, Tags, Latitude/Longitude (never to be emitted); no JobPosting; the visible «No Vacancies to display. 0» is the Knockout `ko if: Items().length == 0` branch of the template, present in the markup whatever the count; `_robots.allowed('www.govt.lc', '/vacancies')` → open, `certain: False` (the rules file answers something that is not a rules file, state `unrecognised`)** · 2026-09-21 -->
<!-- content-2026-09-18: indeterminate · **`/vacancies` and `/jobs` answer 500 on two reads each (07:01:24–07:01:50 UTC; 11 182 B, md5 1482eca8b4d2 all four times — an ASP.NET error page «ExecuteReader requires an open and available Connection. The connection's current state is closed.»), the same 500 to curl; the root `/` answers 200 to curl (42 711 B) — the portal is up, its vacancy pages' database is not; nothing of the lists was read; `_robots.allowed('www.govt.lc', '/vacancies')` → open, `certain: False` (the rules file did not answer as one)** · 2026-09-18 -->
<!-- witness: the page's own `TotalRecords` — 14 on `/jobs`, 2 718 on `/vacancies` (all resource types) — read twice on 2026-09-21 06:15 UTC; the 14 are inlined in full, so `emitted == stated` is the check · 2026-09-21 -->
<!-- no `route:` line since 2026-09-21: the host answers and lists 14 — a script is due (#746 lifted from `blocked`), and until it exists the card is «measured, to build», not a route -->
<!-- route-2026-09-19: none · non faisable — décision du propriétaire du 18.09.2026, #746 · lifted 2026-09-21 -->

**Found by the Saint Lucia search of #619 (a country never searched),
measured 2026-09-18 07:01–07:06 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #619: two searches naming the Government's portal and the private boards,
no composed host names. *A measurement, not an adapter.*

The Government's portal is the public source of public-sector vacancies («Apply to work with Government of Saint Lucia» is one of its services); the country page cited it on 2026-09-03 and no card carried it until this one.

```
_robots.allowed('www.govt.lc', '/vacancies')   open, certain False
GET https://www.govt.lc/vacancies   500 ×2 — 11 182 B, md5 1482eca8b4d2, ASP.NET «ExecuteReader requires an open and available Connection»
GET https://www.govt.lc/jobs        500 ×2 — the same bytes
GET https://www.govt.lc/            200 (curl, 42 711 B) — the portal itself is served
```

**A server error is neither a refusal nor a permission.** The vacancy pages fail in the portal's database layer today, to every client; whether they list vacancies when they answer is unknown. Not «closed»: the next control is 2026-09-21 (a deferred task of the session that measured).

## The control three days on — the database is back, and the list is in the page

```
GET https://www.govt.lc/jobs        200 ×2 (06:15:04, 06:15:06 UTC) — 438 854 B; ResourceSummaryList: ResourceTypeNames "jobs", 14 items, TotalRecords 14
GET https://www.govt.lc/vacancies   200 ×2 (06:15:02, 06:15:03 UTC) — 355 812 B; ResourceTypeNames "vacancies", 15 items of TotalRecords 2 718 (jobs, scholarships, consultancies, tenders)
GET https://www.govt.lc/Scripts/project/resourceapi.js   200 (24 566 B) — the pager POSTs `/admin/resourceapi.asmx/GetResourceSummaries` with {query, cursor}
```

**The 500 of 2026-09-18 was the database behind these pages; three days later
they answer, and the first page of each list is a JSON array in the markup**
— no web-service call is needed for `/jobs`, whose 14 records are all
inlined and whose `TotalRecords` says 14. The visible «No Vacancies to
display. 0» is a Knockout template branch (`<!-- ko if: Items().length == 0
-->`) that the markup carries whatever the count: **it is not a reading of
the board, and a reader that trusted it would publish a false zero.**

**What a script does:** `GET /jobs`, decode the `ResourceSummaryList`
arguments (`json.JSONDecoder.raw_decode` at the `[` after the query
object), emit id (`Id`), url (`/jobs/<slug>`), title, published (`Date`),
updated, description scrubbed of e-mail addresses and telephones, type
(`ResourceSubTypeName`), tags; print «14 emitted, page states 14». Never
emit `Latitude` / `Longitude`, `Permissions`, `MenuId`. `/vacancies` is the
archive of every resource type — a filter, not the board. Issue #746 lifted
from `blocked` on this reading.
