# Board measurement — MyanmarJobLink (`www.myanmarjoblink.com`, Myanmar): «Find Jobs & Job Vacancies in Myanmar» — the root served to the declared client (127 KB) with industry and category facets on `/find-jobs` and 57 employer profiles, no count stated, rules open; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: www.myanmarjoblink.com -->
<!-- script: none -->
<!-- countries: MM -->
<!-- content: measured · **the root (200, 126 681 B, md5 decf94462dd4 / 7ea004f5bb2f) links `/find-jobs?emp_post_job_main_industry[]=N` and `…_cat[]=N` facets and 57 `/companies/detail/<id>` profiles; no count stated, no JobPosting; `_robots.allowed('www.myanmarjoblink.com','/')` → open, certain; the list and the ad not read** · 2026-09-17 -->
<!-- witness: none — the root states no count · 2026-09-17 -->

**Found by the Myanmar search of #601 (a country never searched), measured
2026-09-17 09:35–09:39 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads of the root, two public resolvers on
a DNS negative.** The method is written on #601: one search for the
country's boards (a recruiting vendor's ranking of ten, cross-read with
the engine's own results) and one for the public employment service (the
Ministry of Labour's Labour Exchange Office system, named by the national
portal). *A measurement, not an adapter.*

```
_robots.allowed('www.myanmarjoblink.com', '/')     open, certain
GET https://www.myanmarjoblink.com/                 200 twice — see the content line
```

Nothing past the root was read: the list route, the pager, the ad page
and what it carries are the first line of the adapter, as its `adapter`
issue says.
