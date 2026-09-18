# Board measurement — RCSC vacancies (`rcsc.gov.bt/vacancies/`, Bhutan): the Royal Civil Service Commission's WordPress announcements page — served to the declared client (488 KB) with category links (general announcements, scholarships) and no vacancy list of its own on the day, rules open; the vacancies themselves live in ZRS

<!-- verified: 2026-09-17 -->

<!-- hosts: rcsc.gov.bt -->
<!-- script: none -->
<!-- countries: BT -->
<!-- content: measured · **`/vacancies/` (200, 488 090 B, md5 aed114603871 / 9384db17da47 — a rendered element moves) is the Commission's WordPress site: category links (`/category/general-announcement/`, scholarships), a `/Login/LoginSelect`, no `/vacancy/<slug>` post on the page read; no count, no JobPosting; `_robots.allowed('rcsc.gov.bt','/vacancies/')` → open, certain — the recruitment list is `jobs.rcsc.gov.bt` (`zrs-rcsc.md`)** · 2026-09-17 -->
<!-- witness: none — an announcements page · 2026-09-17 -->

**Found by the Bhutan search of #605 (a country never searched), measured
2026-09-17 16:57–17:31 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #605: two
searches — the public services (the Ministry's BLMIS, the Royal Civil
Service Commission's ZRS and vacancy pages) and the private portals the
engine names, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('rcsc.gov.bt', '/vacancies/')   open, certain
GET https://rcsc.gov.bt/vacancies/               200 ×2 — WordPress announcements, categories, no vacancy post on the day
```

**No adapter issue of its own**: the Commission's vacancies are in ZRS
(`jobs.rcsc.gov.bt`); this page is its notice board.
