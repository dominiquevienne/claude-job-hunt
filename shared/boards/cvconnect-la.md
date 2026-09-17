# Board measurement — CVConnect (`cvconnect.la`, Laos): «the largest CV database and job site in Laos» by its own description — the root served to the declared client (31 KB, identical twice) lists «Show 1 - 7 jobs of all 7 jobs» on 2026-09-17, Lao-language cards, a `search_jobs.php` pager, rules open; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: cvconnect.la -->
<!-- script: none -->
<!-- countries: LA -->
<!-- content: measured · **the root (200, 30 765 B, md5 df69b22dfc1e identical on two reads) prints «Show 1 - 7 jobs of all 7 jobs» and seven cards — a Lao title, the employer, a location, an age, a date range («08/09/2026 to 30/09/2026») — with `/jobs/<id>/` links, province filters and a `search_jobs.php?page=N` pager; no JobPosting; `_robots.allowed('cvconnect.la','/')` → open, certain; the ad not read** · 2026-09-17 -->
<!-- witness: the root's own «all 7 jobs» · 2026-09-17 -->

**Found by the Laos search of #602 (a country never searched), measured
2026-09-17 13:49–13:51 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads, two public resolvers on a DNS
negative.** The method is written on #602: one search naming the country's
boards and agencies (the UN aggregators left aside), no composed host
names. *A measurement, not an adapter.*

```
_robots.allowed('cvconnect.la', '/')   open, certain
GET https://cvconnect.la/               200 ×2, identical — «Show 1 - 7 jobs of all 7 jobs», seven cards, /jobs/<id>/
```

**Seven live ads on the day** — a small board whose count is honest; the
ad page and what it carries are the adapter's first line.
