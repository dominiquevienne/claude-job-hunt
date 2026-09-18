# Board measurement — Ministry of Employment and Social Affairs (`www.employment.gov.sc`, Seychelles): its «National Vacancies» page — the public employment service publishes ONE weekly PDF («Weekly Vacancy List - 15th to 21st September 2026», 387 382 B, served as an attachment) and no HTML list; the page served to the declared client (34 KB), rules open; no count stated; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: www.employment.gov.sc -->
<!-- script: none -->
<!-- countries: SC -->
<!-- content: measured · **`/job-opportunities/national-vacancies` (200, 34 240 B, md5 8d3959a869db / 26d4964b4f6b — a rendered element moves) is a Joomla-style download category with one item, «Weekly Vacancy List - 15th to 21st September 2026 — New! Download», whose `/download` answers 200 `application/pdf`, `Content-Disposition: attachment; filename="Weekly Vacancy List - 15th to 21st September 2026 .pdf"; size=387382`, modified 2026-09-15 08:34 +04 (HEAD, not downloaded); a sibling page `/job-opportunities/ministry-s-vacancies`; no HTML list, no count, no JobPosting; `_robots.allowed('www.employment.gov.sc', '/job-opportunities/national-vacancies')` → open, certain** · 2026-09-18 -->
<!-- witness: none — the list is a PDF whose count is inside the document · 2026-09-18 -->

**Found by the Seychelles search of #617 (a country never searched),
measured 2026-09-18 07:10–07:17 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #617: one search naming the Ministry and the private boards, no
composed host names. *A measurement, not an adapter.*

The public employment service of the Seychelles; the country page cited it on 2026-09-03 and no card carried it until this one.

```
_robots.allowed('www.employment.gov.sc', '/job-opportunities/national-vacancies')   open
GET  …/national-vacancies                                              200 ×2 — one weekly item, see the content line
HEAD …/national-vacancies/weekly-vacancy-list-15th-to-21st-september-2026/download   200 application/pdf, 387 382 B, attachment
```

The adapter's first line: the weekly PDF — its text layer (columns: employer, post, closing date, in the Ministry's format) is the list; the page's single link changes every week and the adapter follows it rather than composing a name.
