# Board measurement — Georgetown Chamber of Commerce & Industry (`gcci.gy`, Guyana): the Chamber's «Career Opportunities» category — members' vacancy notices as WordPress posts, an archive of 42 (2019-10-11 to 2026-09-14) whose category states its own count; adapter `gcci.py`

<!-- verified: 2026-11-27 -->

<!-- hosts: gcci.gy -->
<!-- script: gcci.py -->
<!-- countries: GY -->
<!-- content: measured · **ADAPTER DELIVERED 2026-11-27 (#709): the list is the REST collection of the category resolved by its slug — `wp/v2/categories?slug=career-opportunities` (id 22, `count` 42) then `wp/v2/posts?categories=22`, 42 records, `X-WP-Total` 42; the HTML pager (10, 10, 10, 10, 2; page 6 is 404) holds the same 42 posts, compared member by member. An ARCHIVE: newest 2026-09-14, 41 older than a year, no expiry stated, nothing dropped by age; the newest post is a vendor-forum announcement and the oldest a consultancy EOI, emitted as posted. 19 bodies carry no text, 17 of them only a flyer (`notice_is_an_image`). Contacts in the body (e-mail on 12, telephone on 1) are taken out and named. Only the three REST paths are asked; `_robots.allowed` open, certain** · 2026-11-27 -->
<!-- content: measured · **`/category/career-opportunities/` (200, 233 330 B, md5 40c0eb36a988 / 7df3750b57de — a rendered element moves) is a WordPress 7.1.1 category: 6 distinct `/vacancy-<slug>/` posts on page 1 («Finance Clerk», «Trade and Investment Officer», «Office Assistant», «Electrician — Guyana Electric»), a pager `/category/career-opportunities/page/2/` … `/page/5/`, dates September 14, 2026 then November 21, 2025 — a thin, irregular flow; no count stated, no JobPosting; `_robots.allowed('gcci.gy','/category/career-opportunities/')` → open, certain** · 2026-09-18 -->
<!-- witness: 42 · **the category's own `count` on `wp/v2/categories?slug=career-opportunities`, read by `gcci.py` on its own request; 42 emitted against 42 stated on 2026-11-27** · 2026-11-27 -->
<!-- witness: none — the category states no count · 2026-09-18 -->
**Found by the Guyana search of #621 (a country never searched), measured
2026-09-18 06:54–06:56 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #621:
three searches naming the public sources and the private boards, no
composed host names. *A measurement, not an adapter.*

A Chamber's notice board, not a job board: members' vacancies as posts, a few a year.

```
_robots.allowed('gcci.gy', '/category/career-opportunities/')   open
GET https://gcci.gy/category/career-opportunities/   200 ×2 — see the content line
```

The adapter's first line: the WordPress REST `wp/v2/posts?categories=<id>` with `X-WP-Total`, the post as the ad.
