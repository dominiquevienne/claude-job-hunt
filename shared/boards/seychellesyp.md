# Board measurement — Seychelles YP jobs (`www.seychellesyp.com/jobs`, Seychelles): «Jobs in Seychelles, Current Jobs in Seychelles» — the jobs section of a directory, the same template as `guyanaindex.md` and `yemenyp.md`: `/jobs` lists 8 latest ads (`/job/<id>/<slug>` — «Assistant Production Manager», «Public Area Supervisor», «Kitchen Steward»), `/jobs/all` and a city filter, served to the declared client (12 KB, identical twice), rules open; no count stated; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: www.seychellesyp.com -->
<!-- script: none -->
<!-- countries: SC -->
<!-- content: measured · **`/jobs` (200, 11 942 B, md5 33d2ab47736c identical on two reads) lists 8 «Latest Job Vacancies» as `/job/<id>/<slug>` with `/jobs/all` and `/jobs/all/city:Mahe`; here the cards are in the served markup (on `www.yemenyp.com` the same template served an empty shell); no count stated, no JobPosting; `_robots.allowed('www.seychellesyp.com', '/jobs')` → open, certain** · 2026-09-18 -->
<!-- witness: none — no count stated; `/jobs/all` and its pager bound the list · 2026-09-18 -->

**Found by the Seychelles search of #617 (a country never searched),
measured 2026-09-18 07:10–07:17 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #617: one search naming the Ministry and the private boards, no
composed host names. *A measurement, not an adapter.*

```
_robots.allowed('www.seychellesyp.com', '/jobs')   open
GET https://www.seychellesyp.com/jobs   200 ×2 — 8 ads, /jobs/all
```

The adapter's first line: `/jobs/all` and its pager (on `www.guyanaindex.com` the same template pages 20 an page), the ad by id.
