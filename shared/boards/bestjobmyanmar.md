# Board measurement — BestJobMyanmar (`www.bestjobmyanmar.com`, Myanmar): «Find a Job in Myanmar — Best Job Listings» — the root served to the declared client (62 KB) with `/find-jobs-in-myanmar/<category>/ad/<slug>-<id>` links, no count stated, rules open; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: www.bestjobmyanmar.com -->
<!-- script: none -->
<!-- countries: MM -->
<!-- content: measured · **the root (200, 61 856 B, md5 750ba62cda9b / 33c3fc8232c6) links ads as `/find-jobs-in-myanmar/<category>/ad/<slug>-<id>` and a list `/jobs`; no count stated, no JobPosting; `_robots.allowed('www.bestjobmyanmar.com','/')` → open, certain; the list and the ad not read** · 2026-09-17 -->
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
_robots.allowed('www.bestjobmyanmar.com', '/')     open, certain
GET https://www.bestjobmyanmar.com/                 200 twice — see the content line
```

Nothing past the root was read: the list route, the pager, the ad page
and what it carries are the first line of the adapter, as its `adapter`
issue says.
