# Board measurement — Ntchito Malawi (`ntchito.com`, Malawi): «2026 Job Vacancies, Tenders & Grants in Malawi» — a WordPress aggregator of jobs, internships, tenders and grants, its jobs page served to the declared client (182 KB) with `/jobs/` and job-tag facets, rules open; no count stated; no adapter yet

<!-- verified: 2026-10-06 -->

<!-- hosts: ntchito.com -->
<!-- script: none -->
<!-- countries: MW -->
<!-- content: measured · **THE ROUTE IS THE WORDPRESS REST API, AND NEITHER `/jobs/` NOR `/jobs-in-malawi/` IS A LIST — #674's premise is refuted.** Both answer 200 (118 510 B md5 5ee36cde3e92; 119 551 B md5 532f44ff003a, against 182 497 B on 2026-09-17, so the page lost a third) and each carries exactly ONE `<article>`, which is the page's own prose, with no `JobPosting` in its JSON-LD — only `Place`, `Organization`, `WebSite`, `BreadcrumbList`, `WebPage`, `Person`. `/jobs/` is a PAGE, not an archive: it names itself `wp-json/wp/v2/pages/96`, and its listing sits behind a JavaScript category chooser. **AND COUNTING A KEYWORD MEASURED THE INTERFACE: five matches for «Showing/results» are all UI strings — two menu toggles, a select's `data-no_results_text='No results match'`, a noscript notice.** WHERE THE ADVERTS ARE: the REST discovery root `/wp-json/` (1 383 380 B) registers 795 routes, of which **`/wp/v2/job-listings`** is WP Job Manager's own, publicly readable, alongside `/wp/v2/job-types`, `/wp/v2/job-categories`, `/wp/v2/job_listing_tag` and `/wp/v2/company`. A page of 5 returns records of `type: job_listing`, `status: publish`, each with `id`, `date` (the freshest read was 2026-10-06T05:14:01, the same morning), `link` of the form `/job/<slug>`, `title`, and a `meta` block. **THE HOST STATES ITS OWN COUNTS PER TYPE, AND THAT IS A WITNESS THAT IS NOT OUR EXTRACTION:** `job-types` returns 14 terms with a `count` each — Internationally Recruited 314 ; Job Vacancy in Malawi 202 ; **Tender 192** ; Grants for Individuals 165 ; Grants for NGOs & Institutions 111 ; Trainings, Conferences & Fellowships 79 ; Grants for Businesses 60 ; PhD & Postdoc 53 ; Consultancy 42 ; Opportunity 28 ; Internship 12 ; Masters Scholarship 9 ; VISA Sponsorship Job 4 ; Bachelors Scholarship 1. **SO THE SEPARATION #674 ASKS FOR IS THE HOST'S OWN TAXONOMY AND NOT A CLASSIFICATION WE INVENT: about 532 of these are jobs (202 + 314 + 12 + 4) and about 740 are not — 192 tenders and 336 grants among them. Emitting the post type as «jobs» would inflate the count by more than half, and the first page by date is entirely grants and fellowships.** The sum of the per-type counts is 1 272 and **is NOT the board's size**: a record carries several types (one read showed `[65, 633, 63]`), so the sum double-counts and no total is stated anywhere. **ZERO CONTACT IS EXPOSED ON THIS ROUTE, MEASURED: `_application`, `_company_name` and `_job_location` are EMPTY on 5 of 5, and the payload holds no e-mail address at all.** `_job_salary` is free text on 2 of 5 and one of them is a GRANT amount («Grants of up to EUR 60 000 per organization»), so it is not a salary. **AND THE AVAILABILITY SURFACE IS THE LISTING: `_filled` is present on 5 of 5 — a per-record flag on the API itself, which is the `closure: listing` shape of #1003.** The city pages are named `<city>-jobs-and-tenders` and therefore MIX both in one path, so they cannot separate what the taxonomy can. METHOD: guard on each exact path in the same command as the act, `bin/fetch-body.py` throughout, as `Claude-User` · 2026-10-06 -->
<!-- content: measured · **`/jobs-in-malawi/` (200, 182 497 B, md5 16d2e6bdf36d / 8f6cff7a4c8a — a rendered element moves) is a WordPress page linking `/jobs/`, `/jobs-in-lilongwe/` and `/job-tag/<sector>/` facets; no count stated, no JobPosting on the page; `_robots.allowed('ntchito.com','/jobs-in-malawi/')` → open, certain; the list and the ad not read** · 2026-09-17 -->
<!-- witness: the host's OWN per-type counts from `/wp-json/wp/v2/job-types` — 14 terms each carrying a `count`, so the jobs/tenders/grants split is the host's and not ours; **it is not a board total**, because a record carries several types and the sum of 1 272 double-counts · 2026-10-06 -->
<!-- witness: none — the page states no count · 2026-09-17 -->

**Found by the Malawi search of #622 (a country never searched), measured
2026-09-17 16:49–16:52 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #622: one
search naming the national boards and aggregators, no composed host
names; no public employment service found online by that search. *A
measurement, not an adapter.*

```
_robots.allowed('ntchito.com', '/jobs-in-malawi/')   open, certain
GET https://ntchito.com/jobs-in-malawi/   200 ×2 — see the content line
```

The list, its pager and the ad are the adapter's first line (its `adapter` issue).
