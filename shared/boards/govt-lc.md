# Board measurement — Government of Saint Lucia web portal (`www.govt.lc`, Saint Lucia): its «Job Opportunities» (`/jobs`) and «Vacancies» (`/vacancies`) pages — the public-sector vacancies — answer HTTP 500 to the declared client and to curl on 2026-09-18 (an ASP.NET database error, 11 182 B identical four times) while the root is served; indeterminate, a measure to redo; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: www.govt.lc -->
<!-- script: none -->
<!-- countries: LC -->
<!-- content: indeterminate · **`/vacancies` and `/jobs` answer 500 on two reads each (07:01:24–07:01:50 UTC; 11 182 B, md5 1482eca8b4d2 all four times — an ASP.NET error page «ExecuteReader requires an open and available Connection. The connection's current state is closed.»), the same 500 to curl; the root `/` answers 200 to curl (42 711 B) — the portal is up, its vacancy pages' database is not; nothing of the lists was read; `_robots.allowed('www.govt.lc', '/vacancies')` → open, `certain: False` (the rules file did not answer as one)** · 2026-09-18 -->
<!-- witness: none — nothing was read · 2026-09-18 -->
<!-- route: none · non faisable — décision du propriétaire du 18.09.2026 (un hôte muet reçoit un ticket adapter+blocked qui dit pourquoi et ce qui lèverait), #746 · 2026-09-19 -->

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
