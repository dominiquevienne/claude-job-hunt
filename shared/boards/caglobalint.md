# Board measurement — CA Global (`www.caglobalint.com`): «Africa Recruitment | Africa Jobs» — a pan-African recruitment agency's board, WordPress, `/jobs/` paged 15 a page to `?paged=12` (about 180 ads), each ad `/recruitmentafrica/job/<slug>/` with a region («Southern Africa»), a reference and «Posted N days ago»; page 1 locates ads in South Africa, Nigeria, Guinea, Morocco, Egypt, Congo, Angola, Djibouti, Eritrea, Ethiopia; served to the declared client (438 KB), rules open; no count stated; no adapter yet

<!-- verified: 2026-09-20 -->

<!-- hosts: www.caglobalint.com -->
<!-- script: none -->
<!-- countries: ZA NG GN MA EG CG AO DJ ER ET RW -->
<!-- content: measured · **the root (200, 213 234 B, md5 504e47c5d14c identical on two reads) is the agency's front (Rwanda, Kenya, Botswana, Djibouti, Eritrea among the countries it names, `/banking-africa-recruitment-jobs/`, `/internship-page/`); `/jobs/` (200, 437 960 B, 12:29 UTC) lists 15 distinct `/recruitmentafrica/job/<slug>/` ads with a region, a reference number and «Posted N days ago», and a pager `?paged=2` … `?paged=12` (at most 180, not stated); the ads' places on page 1 — Northern Cape (South Africa), Nigeria, Guinea, Morocco, Egypt, Congo, Angola, Djibouti, Eritrea, Ethiopia — give `countries:` by the measure (Rwanda kept from the front, where the agency names it, and from the country pages that named the host); no JobPosting; `_robots.allowed('www.caglobalint.com','/jobs/')` → open, certain** · 2026-09-20 -->
<!-- witness: none — no count stated; the pager bounds the list (12 pages of 15) · 2026-09-20 -->

**Named in the Atlas inventory of 2026-09-04 (#147), never carded; measured
for #768 on 2026-09-20 12:28–12:29 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** *A measurement, not an
adapter.*

One card for the many pages that name it (Rwanda, Djibouti, Eritrea, Guinea-Bissau, Equatorial Guinea in prose; `jobsbotswana.md` and `keejob.md` in passing): **a pan-African agency board, `countries:` by the ads measured** — a multi-country adapter appears on every page it covers (the 13.09 decision). Guinea-Bissau and Equatorial Guinea are not among the places on page 1; the twelve pages would settle them.

```
_robots.allowed('www.caglobalint.com', '/jobs/')   open
GET https://www.caglobalint.com/        200 ×2 — the agency's front
GET https://www.caglobalint.com/jobs/   200 — 15 ads, ?paged=2 … 12
```

The adapter's first line: the 12 pages, the ad's fields (title, region, reference, posted, the text), the WordPress REST if the job type is exposed with `X-WP-Total`.
