# Board measurement — JobsDZ (`jobsdz.com`, Algeria): «المنصة الرائدة للوظيف العمومي والتوظيف في الجزائر» — an Arabic WordPress board (WP Job Manager: `job_listings`, `search_jobs`) stating «2,400+ وظيفة» on its front on 2026-09-20; the list `/ar/wadifa/` is served as the plugin's shell (filters by category and wilaya, the listings loaded by its AJAX route); public-sector and private-sector sections; served to the declared client (247 KB), rules open; no adapter yet

<!-- verified: 2026-09-20 -->

<!-- hosts: jobsdz.com -->
<!-- script: none -->
<!-- countries: DZ -->
<!-- content: measured · **the root redirects to `/ar/` (200, 247 279 B, md5 2042c5a57298 / f4cc269e4ac3 — a rendered element moves): WordPress 7.1.1, «JobsDZ — المنصة الرائدة للوظيف العمومي والتوظيف في الجزائر», a stat «💼 2,400+ وظيفة», sections الوظيف العمومي (public sector) and القطاع الخاص (private sector), `/ar/add-job/`, `/ar/submit-resume/`, `/job-alert`; `/ar/wadifa/` (200, 204 145 B, 12:29 UTC) is WP Job Manager's list shell — `job_listings`, `search_jobs`, `showing_jobs`, filters by category and «كل الولايات» (wilaya) — with the listings fetched by the plugin's AJAX route, no ad in the markup; no JobPosting; `_robots.allowed('jobsdz.com','/ar/wadifa/')` → open, certain** · 2026-09-20 -->
<!-- witness: the front's own «2,400+ وظيفة» (a rounded claim) · 2026-09-20 -->

**Named in the Atlas inventory of 2026-09-04 (#147), never carded; measured
for #770 on 2026-09-20 12:28–12:29 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** *A measurement, not an
adapter.*

```
_robots.allowed('jobsdz.com', '/')   open
GET https://jobsdz.com/            200 ×2 → /ar/ — «2,400+ وظيفة»
GET https://jobsdz.com/ar/wadifa/  200 — WP Job Manager's shell, filters by wilaya
```

The adapter's first line: WP Job Manager's `admin-ajax.php?action=job_manager_get_listings` (the route the shell calls, with its own parameters — page, per_page, the wilaya filter) and its `found_jobs` total against the front's «2,400+», the ad `/ar/<post>/`.
