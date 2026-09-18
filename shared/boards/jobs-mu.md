# Board measurement — Jobs.mu (`www.jobs.mu`, Mauritius): «Jobs Mauritius | Vacancies in Mauritius» — a board («2,700+ employers» by its description) whose root is served to the declared client (83 KB, identical twice) with `/jobs/` and per-category «N Jobs» counters, rules open; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: www.jobs.mu -->
<!-- script: none -->
<!-- countries: MU -->
<!-- content: measured · **the root (200, 82 882 B, md5 3c59c90be4b6 identical on two reads) is the board's front — `/jobs/`, category blocks with small counters («2 Jobs»); no total, no JobPosting; `_robots.allowed('www.jobs.mu','/')` → open, certain; the list and the ad not read** · 2026-09-18 -->
<!-- witness: none — the root states category counters, no total · 2026-09-18 -->

**Found by the Mauritius search of #618 (a country never searched),
measured 2026-09-18 06:45–06:47 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #618: one search naming the National Employment Department's portal
and the private boards, no composed host names. *A measurement, not an
adapter.*

```
_robots.allowed('www.jobs.mu', '/')   open
GET https://www.jobs.mu/   200 ×2 — see the content line
```

The list, its pager and the ad are the adapter's first line (its `adapter` issue).
