# Board measurement — Zhiyog Recruitment System (`jobs.rcsc.gov.bt`, Bhutan): the Royal Civil Service Commission's recruitment system — «Vacancy Announcement» page served to the declared client (57 KB), its list filled by a POST route `/Application/GetVacancyAnnouncement` (405 on GET), rules open; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: jobs.rcsc.gov.bt -->
<!-- script: none -->
<!-- countries: BT -->
<!-- content: measured · **the root (200, 40 518 B, md5 32b4134380b4 identical on two reads) and `/Application/Vacancy` (200, 56 569 B) — «Vacancy Announcement», a search by field, type, category, location, agency, title and salary, a card template (Position Level, Employment Type, Pay Scale, Closing Date, Applicant(s)) with no vacancy in the markup; the page's script calls `/Application/GetVacancyAnnouncement` and `/Application/GetVacancyCondition` — GET answers 405, the page POSTs; no count stated, no JobPosting; `_robots.allowed('jobs.rcsc.gov.bt','/')` → open, certain** · 2026-09-17 -->
<!-- witness: none — no count stated · 2026-09-17 -->

**Found by the Bhutan search of #605 (a country never searched), measured
2026-09-17 16:57–17:31 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #605: two
searches — the public services (the Ministry's BLMIS, the Royal Civil
Service Commission's ZRS and vacancy pages) and the private portals the
engine names, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('jobs.rcsc.gov.bt', '/')             open, certain
GET https://jobs.rcsc.gov.bt/Application/Vacancy       200 — the search and the card template, no vacancy in the markup
GET https://jobs.rcsc.gov.bt/Application/GetVacancyAnnouncement   405 — the page POSTs it
```

**The civil service's vacancies — a public source.** The POST the page
makes, replayed with the page's own parameters, is the adapter's first
line.
