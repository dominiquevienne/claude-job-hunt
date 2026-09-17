# Board measurement — MyWorld Careers Laos (`laos.myworld-careers.com`, Laos): a recruitment agency's board (Vientiane) — the root served to the declared client (80 KB, identical twice) with `/jobs/` and `/submit-vacancy` links, no count stated, rules open; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: laos.myworld-careers.com -->
<!-- script: none -->
<!-- countries: LA -->
<!-- content: measured · **the root (200, 80 392 B, md5 4c49ad1ef141 identical on two reads) is the agency's front («Recruitment, Staffing & Employment Agency in Laos») with `/jobs/` and `/submit-vacancy`; no count stated, no JobPosting; `_robots.allowed('laos.myworld-careers.com','/')` → open, certain; the list and the ad not read — the same agency as `myworld-mm.md` (Myanmar), a separate host per country** · 2026-09-17 -->
<!-- witness: none — the root states no count · 2026-09-17 -->

**Found by the Laos search of #602 (a country never searched), measured
2026-09-17 13:49–13:51 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads, two public resolvers on a DNS
negative.** The method is written on #602: one search naming the country's
boards and agencies (the UN aggregators left aside), no composed host
names. *A measurement, not an adapter.*

```
_robots.allowed('laos.myworld-careers.com', '/')   open, certain
GET https://laos.myworld-careers.com/               200 ×2, identical — the agency's front, /jobs/
```
