# Board measurement — JOBO.sc (`jobo.sc`, Seychelles): «Job Opportunities in Seychelles» — a WordPress job board stating «Showing 1–10 of 143 jobs» on `/jobs/` on 2026-09-18, paged `/jobs/page/N/` to 15, cards with employer (`/employers/<slug>/`), type, place, posting and closing dates, categories (143 = the sum of the root's category counters), served to the declared client (1.5 MB root, 449 KB list), rules open; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: jobo.sc -->
<!-- script: none -->
<!-- countries: SC -->
<!-- content: measured · **the root (200, 1 518 904 B, md5 a3e9e2d38498 / 0ae428ae5758 — a rendered element moves) is WordPress 7.1.1 with 900 category links each carrying a `job-count` («0 Jobs» on 853, 1 on 30, 2 on 9, 3 on 4, 7 and 9 on 2 each — sum 143); `/jobs/` (200, 448 504 B ×2, md5 d8c7e0117cea / 1469ca655a00, 07:16 UTC) states «Showing 1–10 of 143 jobs», 10 `<article>` cards («Accounts Technician — Hunt, Deltel & Co. Ltd — Full Time — Mahé, Victoria — 18/09/2026 - 28/09/2026 — Accounting, Business Studies — Industry: Shipping»), a pager to `/jobs/page/15/`; no JobPosting; `_robots.allowed('jobo.sc', '/jobs/')` → open, certain** · 2026-09-18 -->
<!-- witness: the list's own «Showing 1–10 of 143 jobs», and the root's category counters sum to 143 · 2026-09-18 -->

**Found by the Seychelles search of #617 (a country never searched),
measured 2026-09-18 07:10–07:17 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #617: one search naming the Ministry and the private boards, no
composed host names. *A measurement, not an adapter.*

```
_robots.allowed('jobo.sc', '/')   open
GET https://jobo.sc/        200 ×2 — the front, 900 categories with counters
GET https://jobo.sc/jobs/   200 ×2 — «Showing 1–10 of 143 jobs», 10 cards, /jobs/page/2/ … /15/
```

The adapter's first line: the 15 pages (10 cards each — 143 = 14 × 10 + 3), the ad behind the card's title, the stated count beside the emitted one.
