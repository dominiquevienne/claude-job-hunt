# Board measurement — DziSeldra (`dziseldra.com/jobs`, Bhutan): «Bhutan's No.1 Job Portal» by its own description — a community platform (feed, jobs, scholarships, tenders, properties, cars) whose jobs page is served to the declared client (128 KB) with no job link in its markup, rules open; the list is client-rendered; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: dziseldra.com -->
<!-- script: none -->
<!-- countries: BT -->
<!-- content: measured · **`/jobs` (200, 128 440 B, md5 04c83742bd0a / 6966d12da983 — a rendered element moves; the host answers slowly, minutes for a read) is a community app's front — a navigation (Job Vacancies, Scholarships, Training, Tenders, Announcements, Properties, Cars, Companies) and one `/jobs` link, no card, no count, no JobPosting in the markup; `_robots.allowed('dziseldra.com','/jobs')` → open, certain; whether the route the page calls serves the client is the adapter's first line** · 2026-09-17 -->
<!-- witness: none — the page is client-rendered · 2026-09-17 -->

**Found by the Bhutan search of #605 (a country never searched), measured
2026-09-17 16:57–17:31 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #605: two
searches — the public services (the Ministry's BLMIS, the Royal Civil
Service Commission's ZRS and vacancy pages) and the private portals the
engine names, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('dziseldra.com', '/jobs')   open, certain
GET https://dziseldra.com/jobs               200 ×2 (each read took minutes) — a community app's front, no card in the markup
```
