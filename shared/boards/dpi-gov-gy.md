# Board measurement — Department of Public Information (`dpi.gov.gy`, Guyana): the Government's «Vacancies» category of its government adverts — public-sector vacancies (GuySuCo, Bureau of Statistics, Guyana Marketing Corporation, Defence Force) as WordPress posts, served to the declared client (312 KB), rules open; no count stated; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: dpi.gov.gy -->
<!-- script: none -->
<!-- countries: GY -->
<!-- content: measured · **`/category/government-adverts/vacancies/` (200, 311 736 B, md5 b13c4ce89263 / 8a482da3cf7f — a rendered element moves) is a WordPress 7.0.5 category of government vacancy notices: 7 distinct posts on the first page («Guyana Sugar Corporation Inc vacancy N», «Bureau of Statistics vacancy — Human Resources Clerk», «Guyana Defence Force vacancies»), the newest dated September 15, 2026; no pager link on page 1, no count stated, no JobPosting; `_robots.allowed('dpi.gov.gy', '/category/government-adverts/vacancies/')` → open, certain** · 2026-09-18 -->
<!-- witness: none — the category states no count · 2026-09-18 -->
<!-- route: none · no route measured — the list and the ad are the adapter's first line · 2026-09-18 -->

**Found by the Guyana search of #621 (a country never searched), measured
2026-09-18 06:54–06:56 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #621:
three searches naming the public sources and the private boards, no
composed host names. *A measurement, not an adapter.*

A public source, not a board: the Government's information department republishes the vacancy notices of state bodies. The National Job Bank of the Ministry of Labour (CRMA) lives on `labour.gov.gy/jobs-bank` — its card (`labour-gov-gy.md`) carries its own measurement and control date, and this search did not remeasure it.

```
_robots.allowed('dpi.gov.gy', '/category/government-adverts/vacancies/')   open
GET https://dpi.gov.gy/category/government-adverts/vacancies/   200 ×2 — see the content line
```

The adapter's first line: whether `/page/2/` exists (WordPress serves it if there are more posts), the WordPress REST `wp/v2/posts?categories=…` as a list with `X-WP-Total`, and the post as the ad.
