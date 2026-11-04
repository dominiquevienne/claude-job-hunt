# Board measurement — JOBO.sc (`jobo.sc`, Seychelles): «Job Opportunities in Seychelles», a JobMonster board stating «Showing 1&ndash;10 of 184 jobs» on `/jobs/` and naming `/jobs/page/19/` as its last — **184 of 184 emitted on 2026-11-04 and the two witnesses agree with each other**; the stated line carries an HTML ENTITY and sits on page 1 only, the advert address `/jobs/<slug>/` shares the list's prefix with the pager, and the dates are day-first ONLY because the card's own `datetime` says so; `script: jobo.py`

<!-- verified: 2026-11-04 -->

<!-- hosts: jobo.sc -->
<!-- script: jobo.py -->
<!-- countries: SC -->
<!-- content: measured · **the walk is COMPLETE and WITNESSED TWICE: `jobo.py jobs` emitted 184 of the 184 the list states, over 19 pages of 10, page 20 answering 404 — and 19 is exactly what 184 at 10 a page needs, so the stated count and the pager agree with each other and not only with us.** The stated line is `Showing 1&ndash;10 of 184 jobs`, an HTML ENTITY for the dash and PAGE 1 ONLY (page 15 states none), so a motif on the decoded dash renders zero and that zero reads «this board states no total». Adverts are `/jobs/<slug>/` — the LIST's own prefix, shared with `/jobs/page/N/` — so a first look for `/job/<slug>/` found 0 links on a page of ten. Each card carries `03/11/2026` beside `datetime="2026-11-03T16:39:53+04:00"` in the SAME `<time>`: day-first is the HOST's statement, asserted on 184 of 184, and it licenses the closing date, which exists only as `dd/mm/yyyy` behind a layout `- `. Fields filled on 184/184 for title, url, employer, type, place, both dates and industry; categories on 179/184; 54 distinct employers. `/wp-json/wp/v2/types` answers 200 and does NOT carry `noo_job`, so the HTML list is the route. 0 of the cards carry a telephone while the chrome carries JOBO's own `tel:+2482610105` four times — the fields are scrubbed and the PAGE never is. The AD route is the opposite: its custom fields carry `Company Phone` and `Contact Phone`, both withheld, and the application address is hidden by the HOST itself (`data-cfemail`)** · 2026-11-04 -->
<!-- witness: the list's own «Showing 1&ndash;10 of 184 jobs» AND the pager's own `/jobs/page/19/`, which cross-check: 184 at 10 a page needs 19 pages, and the walk ended on a 404 at page 20 · 2026-11-04 -->
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

**SHIPPED 2026-11-04 as `jobo.py` (#715).** `jobo.py jobs` walks the list and emits one record per card; `jobo.py ad --url …` reads one advert, whose page holds FIVE `<article>` blocks that are OTHER people's adverts, under `related-jobs` — the description slice is asserted to end before them.

*The September line above said «143 jobs on 15 pages». Both numbers moved — 184 on 19 — which is why the adapter reads them at runtime and compares them to each other: a count written into the code would have been wrong within seven weeks.*
