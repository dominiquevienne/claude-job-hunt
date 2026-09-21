# Board measurement — National Job Bank (`jobs.gov.gy`, Guyana): the Ministry of Labour's free national board, served to the declared client — the list is behind the form its own «See all jobs» button submits, «187 Jobs Found» on 2026-09-21 against 2 564 all time; no adapter yet, a script is the next step (#314)

<!-- verified: 2026-09-21 -->

<!-- hosts: jobs.gov.gy -->
<!-- hosts-source: the one outbound link of the ministry's `/jobs-bank/` page («View National Job Bank Portal», `labour-gov-gy.md`), read 2026-09-21 06:33 UTC · 2026-09-21 -->
<!-- script: none -->
<!-- countries: GY -->
<!-- content: measured · **2026-09-21 06:33–06:35 UTC, the declared client, the guard on each path (rules read, `*` open, certain, no Crawl-delay; the name on 1.1.1.1 and 8.8.8.8 — 104.18.18.199 / 104.18.19.199, Cloudflare, no challenge): the root 200 ×2 (06:33:38, 06:33:43 UTC; 31 693 B) — five recent jobs as `/<id>/<slug>.html`, the site's own counters «14090 Job Seekers — 890 Employers — 2564 Jobs»; `/job_search.php` GET 200 ×2 (06:34:16, 06:34:21 UTC) is the search form (POST; keyword, state = region, area, job_category[], experience); the form the site's own «See all jobs» button submits — `action=search`, nothing else — replayed twice (06:34:57, 06:35:05 UTC; 105 150 B, md5 moving): **«187 Jobs Found»**, a pager «of 10», cards with title, employer, region, type, salary in GYD, experience bracket, skills, «Posted: 18th Sep, 2026 — Ends : 01st Nov, 2026»; facets Posted last 24 h 3 / 7 d 21 / 14 d 34 / 30 d 69 / All Time 2 564, Job Type Full-time 1 780 / Permanent 200 / Contract 133 / Part-time 26 / Internship 18 / Temporary 17; no JobPosting; `industry_rss.php` linked, not read; ad pages not read in this control** · 2026-09-21 -->
<!-- witness: the site's own «187 Jobs Found» on the list its button requests (read twice) and the footer's «2564 Jobs» (all time); the facet totals sum to the same 2 564 — the 187 is the live count, the pager «of 10» bounds the walk · 2026-09-21 -->

**Found behind the Ministry of Labour's site during the 2026-09-21 control
of `labour-gov-gy.md` (#314): the ministry's «Jobs Bank» page links to this
host and nothing else.** Measured by the declared client, the guard on the
exact path, two reads per URL; the POST is the page's own form with the
page's own single parameter.

## What it is

The «National Job Bank» of the Government of Guyana — free to job seekers
and employers, presented as the online expansion of the Central Recruitment
and Manpower Agency (founded 1944). A PHP job-board product (`post_job.php`,
`job_alert_agent.php`, `search_resume.php`, `industry_rss.php`), employers
post themselves: on the first page The Guyana Oil Company Limited, Smart
Solutions Inc., CROWN MINING SUPPLIES.

## The route — the page's own form, replayed

```
dig @1.1.1.1 / @8.8.8.8 jobs.gov.gy      NOERROR — 104.18.18.199, 104.18.19.199
GET https://jobs.gov.gy/                 200 ×2 — five recent jobs, «2564 Jobs» in the footer
GET https://jobs.gov.gy/job_search.php   200 ×2 — the search form; the home's «See all jobs» is <form method="post" action="/job_search.php"><input type="hidden" name="action" value="search">
POST https://jobs.gov.gy/job_search.php  action=search   200 ×2 — «187 Jobs Found», pager «of 10», the cards
```

**What a script does:** POST `action=search` (the button's own request), read
«N Jobs Found» as the stated count, walk the pager to its stated last page
(the pager's parameter is to be read from the response's own links — not
inspected in this control), key on the ad id in `/<id>/<slug>.html`, emit
title, employer, region, type, salary (GYD, as the site prints it), the
posting and closing dates, skills; print «N emitted, site states 187». The
list carries no recruiter name; the ad pages — whether they carry a contact
— were not read here, and a script scrubs their text of e-mail addresses
and telephones as every adapter does. No JobPosting anywhere read.

## What this card does not establish

The pager's request shape (page 2 not read); whether the ad page is served
to the client; whether the 187 are all live (the «Ends» date on each card
is what a reader would check). A measurement, not a script — #314 carries
the adapter, lifted from `blocked` on this reading.
