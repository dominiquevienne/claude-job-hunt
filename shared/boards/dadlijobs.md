# Board measurement — Dadli Jobs (`dadlijobs.com`, Antigua and Barbuda): the only enumerator a plain client can see is the sitemap, which carried **100** vacancies on 2026-11-10 and is NOT truncated — the paginated form redirects to the canonical one and both carry the same 100 addresses; the board states no total (both «Displayed Here» strings are page ranges) and the job post type is absent from `/wp-json/wp/v2/types`; the employer IS published and varies (10/10, 7 distinct); `dadlijobs.py` ships

<!-- verified: 2026-11-10 -->

<!-- hosts: dadlijobs.com -->
<!-- script: dadlijobs.py -->
<!-- countries: AG -->
<!-- content: measured · the sitemap index is real and `job-sitemap.xml` carried 100 distinct `/job/<slug>/` addresses; `job-sitemap1.xml` returns 200 whose `final_url` is `job-sitemap.xml`, so the paginated form redirects to the canonical one and the two bodies hold the SAME 100 addresses (difference empty both ways, `md5` differing only by the generation timestamp each states in its own comment); every `<loc>` is CDATA-wrapped so `<loc>([^<]+)</loc>` returns ZERO; `/` says «Displayed Here: 1 - 25 Jobs» and `/jobs-listing/` says «1 - 15 Jobs», both page RANGES, 15 vacancies behind 31 hrefs and no pager because pagination is `jobsearch_job_pagenation_ajax` on `admin-ajax.php`; `/wp-json/wp/v2/types` lists fifteen types and the job type is NOT among them; ten ads sampled by rank (0, 11 … 99) give employer 10/10 and 7 distinct, Job ID 10/10 and 10 distinct, description 10/10 (436–2 739 chars, read by BALANCING the `div` — a non-greedy close truncates it to 317 and hides the contact), one `html.unescape` pass sufficient (zero doubled `&amp;<entity>;`, zero residual over twenty fields), apply route split 10/10 between a `mailto:` button whose `data-id` equals the Job ID and an `N Application(s)` counter, and ALL TEN deposit at least one contact form so `withheld_fields` is non-empty on 10/10 · 2026-11-10 -->
<!-- witness: none — the board states NO count. Both «Displayed Here» strings are page ranges, the job post type is absent from the REST type list, and the 100 is this adapter's own extraction, corroborated only as UNTRUNCATED by the `job-sitemap1.xml` redirect · 2026-11-10 -->
<!-- route: http · 100 · 2026-11-10 -->
<!-- content: measured · **the root (200, 510 932 / 510 931 B, md5 c7c79c92cb4f / 3395af5e0732 — a rendered element moves) is WordPress with the Careerfy job-board theme (`careerfy-framework`, `addon-jobsearch-chat`): «Displayed Here: 1 – 25 Jobs», 25 distinct `/job/<slug>/` links, dates «September 17, 2026», «September 25, 2026» (a posting and a closing date); no total stated beyond the page's range, no JobPosting on the front; `_robots.allowed('dadlijobs.com','/')` → open, certain** · 2026-09-18 -->
<!-- witness: the front's own «Displayed Here: 1 – 25 Jobs» — a range, not a total · 2026-09-18 -->

**Found by the Antigua and Barbuda search of #620 (a country never
searched), measured 2026-09-18 07:29–07:34 UTC by the declared client, the guard
on the exact path first, `bin/fetch-body.py`, two reads.** The method is
written on #620: four searches naming the Government, the Labour
Department's One Stop Employment Centre and the private boards, no composed
host names. *A measurement, not an adapter.*

The board that carries the One Stop Employment Centre's notices (the search found OSEC's «Labourer», «Event Crew», «Sales Clerk» posts here).

```
_robots.allowed('dadlijobs.com', '/')   open
GET https://dadlijobs.com/   200 ×2 — «Displayed Here: 1 – 25 Jobs», 25 ads
```

The adapter's first line: the Careerfy list (`/jobs/` or the theme's AJAX search with its `total`), the ad `/job/<slug>/`, the stated total if the list states one beside the emitted count.
