# Board measurement — MyJobo (`www.myjobo.com`, Malawi): «Malawi's Skills & Talent Ecosystem» — a board and talent platform covering the 28 districts, its front served to the declared client (105 KB) with `/search-jobs?state_id=N` per district and «0 jobs» counters on the front, rules open; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: www.myjobo.com -->
<!-- script: none -->
<!-- countries: MW -->
<!-- content: measured · **the root (200, 105 173 B, md5 b089b655f423 / d3827d740239 — a rendered element moves) links `/search-jobs` and 29 `/search-jobs?state_id=N` district filters and prints «0 jobs» counters on its front blocks; no JobPosting; `_robots.allowed('www.myjobo.com','/')` → open, certain; the search page and the ad not read — whether the district counters are live is the adapter's first line** · 2026-09-17 -->
<!-- witness: the front's «0 jobs» counters — read on the search page before trusting them · 2026-09-17 -->

**Found by the Malawi search of #622 (a country never searched), measured
2026-09-17 16:49–16:52 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #622: one
search naming the national boards and aggregators, no composed host
names; no public employment service found online by that search. *A
measurement, not an adapter.*

```
_robots.allowed('www.myjobo.com', '/')   open, certain
GET https://www.myjobo.com/   200 ×2 — see the content line
```

The list, its pager and the ad are the adapter's first line (its `adapter` issue).
