# Board measurement — the Myanmar National Portal's «Jobs & Vacancies» (`myanmar.gov.mm/vacancies`, Myanmar): the government's own vacancy notices on a Liferay portal, served to the declared client with rules open; no count stated; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: myanmar.gov.mm -->
<!-- script: none -->
<!-- countries: MM -->
<!-- content: measured · **`/vacancies` (200, 222 321 B, md5 cc12bee36161 / 3e39ad6b3ee4 — a Liferay portlet id moves) is the National Portal's «Jobs & Vacancies» page — an asset publisher of government vacancy notices with per-ministry facets (`/health/vacancy`, `/education-research/vacancy`, `/view-all/vacancy`), Burmese and English; no count stated, no JobPosting; `_robots.allowed('myanmar.gov.mm','/vacancies')` → open, certain; the notices themselves not read** · 2026-09-17 -->
<!-- witness: none — the page states no count · 2026-09-17 -->

**Found by the Myanmar search of #601 (a country never searched), measured
2026-09-17 09:35–09:39 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads of the root, two public resolvers on
a DNS negative.** The method is written on #601: one search for the
country's boards (a recruiting vendor's ranking of ten, cross-read with
the engine's own results) and one for the public employment service (the
Ministry of Labour's Labour Exchange Office system, named by the national
portal). *A measurement, not an adapter.*

```
_robots.allowed('myanmar.gov.mm', '/vacancies')   open, certain
GET https://myanmar.gov.mm/vacancies              200 ×2 — Liferay, «Jobs & Vacancies», facets by ministry
```

The public sector's own notices, on the portal that also names the Labour
Exchange Office system (unreachable from here today, see
`myanmarjob-gov.md`). What a notice carries, how the publisher pages, and
whether a list route serves the client are the first line of the adapter.
