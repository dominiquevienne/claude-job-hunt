# Board measurement — Worklinkcy (`www.worklinkcy.com`, Northern Cyprus): «Kuzey Kıbrıs'ta İş Bul» — a bilingual board whose `/tr/jobs` is served with ads (`/tr/jobs/<slug>`: «Laravel Full Stack Developer», «Okul Öncesi Öğretmeni», «Bar Staff»), a `?page=N` pager and a `/tr/feed/jobs` feed, no count stated, served to the declared client (357 KB), rules open; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: www.worklinkcy.com -->
<!-- script: none -->
<!-- countries: CYN -->
<!-- content: measured · **`/tr/jobs` (200, 357 323 B, md5 bd546ef2f6ab / 1faa6d672fd0 — a rendered element moves) lists ads as `/tr/jobs/<slug>` (10 distinct on the first page), a pager `?page=2`, `?page=3`, and a feed `/tr/feed/jobs`; no count stated, no JobPosting; `_robots.allowed('www.worklinkcy.com','/tr/jobs')` → open, certain** · 2026-09-18 -->
<!-- witness: none — the list states no count · 2026-09-18 -->

**Found by the Northern Cyprus search of #606 (a country never searched),
measured 2026-09-18 07:20–07:22 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #606: two searches in Turkish naming the Labour Department and the
private boards, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('www.worklinkcy.com', '/tr/jobs')   open
GET https://www.worklinkcy.com/tr/jobs   200 ×2 — see the content line
```

The adapter's first line: `/tr/feed/jobs` (a feed is the inventory if it is whole) against the paged list, the ad's fields.
