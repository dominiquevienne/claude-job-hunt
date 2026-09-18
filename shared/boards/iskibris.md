# Board measurement — İş Kıbrıs (`www.iskibris.com`, Northern Cyprus): «Kıbrıs'ın İş Arama Portalı» — a Next.js board whose server-rendered front states 12 sector counters («Satış Münhalleri 40 iş ilanı», «Muhasebe/Finans 43», … — sum 315) and links `/jobs`, `/jobs/<id>` and six district quick-links, served to the declared client (113 KB, identical twice), rules open; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: www.iskibris.com -->
<!-- script: none -->
<!-- countries: CYN -->
<!-- content: measured · **the root (200, 112 950 B, md5 cbd1b1e54d58 identical on two reads) is a Next.js app rendered on the server (`/_next/static`, MUI): 12 sector cards each with «N iş ilanı» (40, 9, 43, 43, 44, 33, 24, 16, 2, 55, 2, 4 — sum 315, a sum of sector counters and not a stated total), `/jobs`, one `/jobs/25824`, quick-links `/quick-links/jobs-in-nicosia|kyrenia|magusa|iskele|guzelyurt|lefke`; no JobPosting; `_robots.allowed('www.iskibris.com','/')` → open, certain** · 2026-09-18 -->
<!-- witness: the front's own sector counters, summing to 315 (a sum, not the site's total) · 2026-09-18 -->

**Found by the Northern Cyprus search of #606 (a country never searched),
measured 2026-09-18 07:20–07:22 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #606: two searches in Turkish naming the Labour Department and the
private boards, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('www.iskibris.com', '/')   open
GET https://www.iskibris.com/   200 ×2 — see the content line
```

The adapter's first line: `/jobs` and its pager (server-rendered or the Next data route), the ad `/jobs/<id>`, the stated total if `/jobs` states one beside the emitted count.
