# Board measurement — BLMIS (`www.blmis.gov.bt`, Bhutan): the Ministry of Industry, Commerce and Employment's Labour Market Information System — the public employment service where employers post vacancies and job seekers search them; served to the declared client (the jobseeker page 2.4 MB), a Livewire application whose «Search Job» is a form, rules open; no adapter yet, the list route to measure

<!-- verified: 2026-09-17 -->

<!-- hosts: www.blmis.gov.bt -->
<!-- script: none -->
<!-- countries: BT -->
<!-- content: measured · **the root (200, 42 773 B, md5 78cb3f09b246 / f0c8248e99cc — a rendered element moves) is a Livewire front («Vacancies & Trainings», «Career Information», Login, Register); `/jobseeker_page/mispage` (200, 2 439 212 B) carries «Search Job» and «Search Training» forms with a 253-option occupation list and no vacancy in its markup — the list is filled by Livewire calls (POST); no count stated, no JobPosting; `_robots.allowed('www.blmis.gov.bt','/')` → open, certain** · 2026-09-17 -->
<!-- witness: none — no count stated · 2026-09-17 -->

**Found by the Bhutan search of #605 (a country never searched), measured
2026-09-17 16:57–17:31 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #605: two
searches — the public services (the Ministry's BLMIS, the Royal Civil
Service Commission's ZRS and vacancy pages) and the private portals the
engine names, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('www.blmis.gov.bt', '/')            open, certain
GET https://www.blmis.gov.bt/                       200 ×2 — a Livewire front
GET https://www.blmis.gov.bt/jobseeker_page/mispage  200, 2 439 212 B — «Search Job», 253 occupations, no vacancy in the markup
```

**The public employment service, at the top of Bhutan's list.** Its list
arrives by Livewire calls the page makes (a POST with the component's
state) — whether that call replays as the page makes it (the 14.09
judgment) or needs a tab is the adapter's first line (its `adapter`
issue).
