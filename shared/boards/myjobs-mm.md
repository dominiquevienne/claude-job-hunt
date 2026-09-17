# Board measurement — MyJobs (`myjobs.com.mm`, Myanmar): «Myanmar's Pioneer Job Portal» — the root served to the declared client (844 KB) with category counts («34 Jobs», «32 Jobs», «22 Jobs», «16 Jobs»), rules open; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: myjobs.com.mm -->
<!-- script: none -->
<!-- countries: MM -->
<!-- content: measured · **the root (200, 844 126 B, md5 f0bed62919be / b085d7c9c953) prints per-category counts («34 Jobs», «32 Jobs», «22 Jobs», «16 Jobs» …) and no total; no JobPosting; `_robots.allowed('myjobs.com.mm','/')` → open, certain; the list and the ad not read** · 2026-09-17 -->
<!-- witness: the root's category counts (34, 32, 22, 16 …); no total · 2026-09-17 -->

**Found by the Myanmar search of #601 (a country never searched), measured
2026-09-17 09:35–09:39 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads of the root, two public resolvers on
a DNS negative.** The method is written on #601: one search for the
country's boards (a recruiting vendor's ranking of ten, cross-read with
the engine's own results) and one for the public employment service (the
Ministry of Labour's Labour Exchange Office system, named by the national
portal). *A measurement, not an adapter.*

```
_robots.allowed('myjobs.com.mm', '/')     open, certain
GET https://myjobs.com.mm/                 200 twice — see the content line
```

Nothing past the root was read: the list route, the pager, the ad page
and what it carries are the first line of the adapter, as its `adapter`
issue says.
