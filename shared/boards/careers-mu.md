# Board measurement — Careers.mu (`careers.mu`, Mauritius): «Find Jobs & Top Employers in Mauritius» — a WP Job Board Pro site whose whole list is one page, `/browse-jobs/?jobs_ppp=-1` («Showing all 31 results» on 2026-11-26), rules open; adapter `careersmu.py`

<!-- verified: 2026-11-26 -->

<!-- hosts: careers.mu -->
<!-- script: careersmu.py -->
<!-- countries: MU -->
<!-- content: measured · **ADAPTER DELIVERED 2026-11-26 (#699): `careersmu.py jobs` reads ONE list page, `/browse-jobs/?jobs_ppp=-1&filter-orderby=newest` (the «All» of the site's own «Per Page» selector), 31 cards, and the page STATES «Showing all 31 results». Three enumerators agree MEMBER BY MEMBER: that page, the REST `job_listing` (31) and the `/job/` entries of the All in One SEO sitemap (31). The card carries title, category, location term and contract type, not the employer; the employer and region are in each ad's JobPosting, one request per ad. All 31 ad pages state «Application deadline closed.» in their own deadline block, the deadline date being the posting day, so the host's deadline says nothing about liveness and is emitted as stated, never filtered. 4 of the 31 carry no JobPosting. The host also publishes `candidate` and `job_applicant` types: the tool refuses every path but the list, `job_listing` and `/job/<slug>/` before sending.** · 2026-11-26 -->
<!-- content: measured · **the root (200, 269 120 B, md5 41c04ce6fc0e identical on two reads) is a WordPress job board — `/job-type/full-time/`, `/job-category/<slug>/`, `/job/<slug>/` ads; no count stated, no JobPosting on the root; `_robots.allowed('careers.mu','/')` → open, certain; the list and the ad not read** · 2026-09-18 -->
<!-- witness: 31 · **the list page's own line «Showing all 31 results» (paged form «Showing 1 – 14 of 31 results»), read by `careersmu.py` on the page it extracts from; 31 against 31 emitted on 2026-11-26** · 2026-11-26 -->
<!-- witness: none — the root states no count · 2026-09-18 -->

**Found by the Mauritius search of #618 (a country never searched),
measured 2026-09-18 06:45–06:47 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #618: one search naming the National Employment Department's portal
and the private boards, no composed host names. *A measurement, not an
adapter.*

```
_robots.allowed('careers.mu', '/')   open
GET https://careers.mu/   200 ×2 — see the content line
```

The list, its pager and the ad are the adapter's first line (its `adapter` issue).
