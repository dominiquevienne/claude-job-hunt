# Board measurement — Careers Malawi (`careersmw.com`, Malawi): «No One Knows Better» — a WordPress job board whose root is served to the declared client (78 KB, identical twice) with `/job/<slug>/` ads and `/post-a-job/`, rules open; no count stated; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: careersmw.com -->
<!-- script: none -->
<!-- countries: MW -->
<!-- content: measured · **the root (200, 78 095 B, md5 7d48132b905b identical on two reads) links ads as `/job/<slug>/` («project-manager-debottlenecking», «project-engineer-N») and `/post-a-job/`; no count stated, no JobPosting on the root; `_robots.allowed('careersmw.com','/')` → open, certain; the list and the ad not read** · 2026-09-17 -->
<!-- witness: none — the root states no count · 2026-09-17 -->

**Found by the Malawi search of #622 (a country never searched), measured
2026-09-17 16:49–16:52 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #622: one
search naming the national boards and aggregators, no composed host
names; no public employment service found online by that search. *A
measurement, not an adapter.*

```
_robots.allowed('careersmw.com', '/')   open, certain
GET https://careersmw.com/   200 ×2 — see the content line
```

The list, its pager and the ad are the adapter's first line (its `adapter` issue).
