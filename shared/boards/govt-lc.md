# Board measurement — Government of Saint Lucia web portal (`www.govt.lc`, Saint Lucia): its «Job Opportunities» (`/jobs`) — **14 public-sector vacancies inlined in the page and 14 stated by the portal itself on 2026-09-22**, after the HTTP 500 of 2026-09-18 that had the issue opened `blocked`; `govtlc.py` — the page's visible «No Vacancies to display. 0» is a template branch and never a count, and the coordinates every item carries are never emitted

<!-- verified: 2026-09-22 -->

<!-- hosts: www.govt.lc -->
<!-- script: govtlc.py -->
<!-- countries: LC -->
<!-- content: measured · **14 inlined, 14 stated: they agree**; the HTTP 500 of 2026-09-18 keeps its own exit, never «no vacancy»; its visible «No Vacancies to display» is a template branch, never a count. Read by the declared client, 2026-09-22 09:0x–09:1x UTC, the guard on the exact path: `/jobs` 200 (438 854 B, md5 943c903b455f — a ViewState moves between reads, so the md5 is NOT a stable witness here and the COUNT is) initialises the page's own `new ResourceSummaryList('Resource', {"ResourceTypeNames":"jobs"…}, [ …items… ], 'm_summaries_container', {"TotalRecords":14})`, the items dated 2024-05-02 to 2026-09-18 (the portal keeps its existing vacancies listed). The items array is read by BALANCING brackets outside strings: a description carries «[see schedule]» and lone «]», and a read that stopped at the first one would cut the list in the middle. Each item: Title, Url (`/jobs/<slug>`), Date, LastUpdatedDate, ResourceSubTypeName, and **Latitude/Longitude — never emitted**. A notice (`/jobs/senior-crown-counsel-…` 200, 214 946 B) carries its title, «Published:» and the whole «Description:»; the postal address it tells an applicant to write to is withheld and named. Exercised: `jobs --country-code LC` → **14 emitted, «14 inlined, the portal states 14 — they agree» said**; `ad --url …` → «withheld: email, postal_address» · 2026-09-22 -->
<!-- content-2026-09-18: indeterminate · **`/vacancies` and `/jobs` answer 500 on two reads each (07:01:24–07:01:50 UTC; 11 182 B, md5 1482eca8b4d2 all four times — an ASP.NET error page «ExecuteReader requires an open and available Connection. The connection's current state is closed.»), the same 500 to curl; the root `/` answers 200 to curl (42 711 B) — the portal is up, its vacancy pages' database is not; nothing of the lists was read; `_robots.allowed('www.govt.lc', '/vacancies')` → open, `certain: False` (the rules file did not answer as one)** · 2026-09-18 -->
<!-- witness: the page's own `TotalRecords`, printed beside the items read on every run · 2026-09-22 -->
<!-- route: http · 14 · 2026-09-22 -->
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

## The adapter — `govtlc.py` (#746, 2026-09-22)

```
GET /jobs                     200 — new ResourceSummaryList('Resource', {…}, [14 items], …, {"TotalRecords":14})
GET /jobs/<slug>              200 — the notice: <h1>, «Published:», the whole «Description:»
```

**The issue was blocked on a page that now answers.** On 2026-09-18 `/jobs`
and `/vacancies` returned **HTTP 500** to every client (an ASP.NET
«ExecuteReader requires an open and available Connection») and #746 was
opened `blocked` on that measurement, with a dated control and what would
lift it. The control found them served. *A dated failure is not a verdict* —
and the adapter keeps the 500 its own exit, so the day it returns the run
says «the database is down again», never «no vacancies».

**The visible «No Vacancies to display. 0» is a template branch.** It is
Knockout's `ko if: Items().length == 0`, present in the markup whatever the
list holds. **A reader who trusted the visible text would have published ZERO
on a page carrying fourteen** — and zero is the one result whose honest and
broken forms look alike.

**The items array is read by balancing brackets OUTSIDE strings.** A
description carries «[see schedule]» and, often enough, a lone «]»: a read
that stopped at the first `]` would cut the list in the middle and emit
whatever survived, silently.

**Coordinates are never emitted.** Every item carries `Latitude` and
`Longitude`; the record names them in `withheld_fields` so the absence is
declared rather than silent. A notice's text is the editor's, minus what it
tells an applicant to write to — an e-mail, a number, and a **postal
address** («P.O. Box 709», «3 Manoel Street») — each named.

*`/vacancies` is the wider archive (2 718 records on 2026-09-21: jobs,
scholarships, consultancies and tenders together), paged through a POST web
method this adapter does not replay — the jobs page is the job route.*

**Tests and mutations.**
`APortalWhoseVisibleZeroIsATemplateBranchAndWhoseListIsInItsOwnCall`, both
ways on fixtures (a list read against its stated total, a lone `]` inside a
description, a total that disagrees, no total at all, a 200 without the call,
a 500 with its own message, a 404, a notice whose banner would answer in its
place, `ad` on a query string and on a non-`/jobs/` path, the apex host
refused). Mutation bench on a detached copy, `python3 -B`, **10 / 10 red**:
the array read without balancing · the stated count ignored · the «short»
branch removed · coordinates not declared withheld · the postal-address scrub
dropped · the e-mail scrub dropped · the 500's own exit removed · the
Knockout note dropped · the notice's block not scoped · the host check
dropped.
