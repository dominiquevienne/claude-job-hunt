# Board adapter — National Job Bank (`jobs.gov.gy`, Guyana): the Ministry of Labour's free national board, served to the declared client — the search its own «See all jobs» button submits states «187 Jobs Found» and shows twenty, its pager is a script under a written refusal, so `jobsgovgy.py` walks the site's own categories (57 searches, 187 distinct = 187 stated, 2026-09-21) and reads the advert's JobPosting

<!-- verified: 2026-09-21 -->

<!-- hosts: jobs.gov.gy -->
<!-- hosts-source: the one outbound link of the ministry's `/jobs-bank/` page («View National Job Bank Portal», `labour-gov-gy.md`), read 2026-09-21 06:33 UTC · 2026-09-21 -->
<!-- script: jobsgovgy.py -->
<!-- countries: GY -->
<!-- content: measured · **2026-09-21 06:33–07:28 UTC, the declared client, the guard on each path. Rules (1 181 B, `User-agent: *`): the application's directories refused — `/language/`, `/jscript/`, `/css/`, `/uploads/`, `/resume/`… — `/job_search.php`, `/job_search_by_industry.php`, `/<id>/<slug>.html`, `/rss/` open; no Crawl-delay (the name on 1.1.1.1 and 8.8.8.8 — 104.18.18.199 / 104.18.19.199, Cloudflare, no challenge). The root 200 ×2 (31 693 B) — five recent jobs, «14090 Job Seekers — 890 Employers — 2564 Jobs»; the form its «See all jobs» button submits — `POST /job_search.php`, `action=search`, nothing else — **«187 Jobs Found»**, twenty `div.previewBox#<id>` cards (title, employer, region, type, salary in GYD as the site prints it — «000 GYD» and «1 GYD» are the site's own text, 15 and 18 of 187 —, experience bracket, teaser, «Posted: 18th Sep, 2026 — Ends : 01st Nov, 2026»; two of twenty print an empty type span), a pager «of 10». **The pager is `jobsearch_pagination(20, …)` in `/language/english/jscript/page.js` — under `Disallow: /language/`: the script was not read, its parameter not guessed** (twelve plausible field names posted 07:02–07:10 UTC all answered page 1). The «By Category» page (`/job_search_by_industry.php`, 200) lists 89 categories with live counts, 57 non-empty, the largest 20 (Drivers), each a form `job_category[]=<id>` to the same search — `jobsgovgy.py list` live 07:21:57–07:27 UTC: **the first page then 57 category searches, 187 distinct ids — «187 emitted — the site states 187: equal»**, the counts summing to 214 (a job carries several categories); no category above twenty, so no shortfall named. The RSS (`/rss/all_jobs.xml` 30 items; `/rss/<n>.xml` ten at most, 89 feeds → 162 distinct) links `/<id>/<slug>.html` with ids of another numbering that answer the home page — not the route. The advert (`/2591/Assistant.html`, 200, ~35 KB): a `JobPosting` — title, `hiringOrganization.name` + logo, `datePosted`, `baseSalary.value`, `employmentType`, `addressCountry: GY`, `description` HTML entity-escaped inside the JSON — and the page's labelled fields (location «Georgetown, Guyana», Experience, Job category, Salary, Apply before, Job Type, Posted Date); **an id the site does not have answers 200 with the home page** — no JobPosting, exit 3 (`/563/Facilities-Support-Engineer.html`, an RSS id)** · 2026-09-21 -->
<!-- witness: the site's own «187 Jobs Found» on the search its button submits — `jobsgovgy.py list` prints it beside the union of its category walk («187 emitted — the site states 187: equal»; «short» with the categories beyond one page named when the pager would have been needed) · 2026-09-21 -->
<!-- route: http · 187 · 2026-09-21 -->

**Found behind the Ministry of Labour's site during the 2026-09-21 control
of `labour-gov-gy.md` (#314): the ministry's «Jobs Bank» page links to this
host and nothing else.** Measured by the declared client, the guard on the
exact path, two reads per URL; the POSTs are the page's own forms with the
page's own parameters.

## What it is

The «National Job Bank» of the Government of Guyana — free to job seekers
and employers, presented as the online expansion of the Central Recruitment
and Manpower Agency (founded 1944). A PHP job-board product (`post_job.php`,
`job_alert_agent.php`, `search_resume.php`, `industry_rss.php`), employers
post themselves: The Guyana Oil Company Limited, Demerara Distillers,
CROWN MINING SUPPLIES, Hong Da Lian Shao Guyana Construction. Georgetown
98 of 187, East Bank Demerara 44, East Coast Demerara 21 (2026-09-21).

## The route — the page's own forms, and a pager the rules refuse

```
POST https://jobs.gov.gy/job_search.php  action=search              «187 Jobs Found», twenty cards, pager «of 10»
GET  https://jobs.gov.gy/job_search_by_industry.php                  89 category forms with live counts (57 non-empty, max 20)
POST https://jobs.gov.gy/job_search.php  action=search&job_category[]=<id>   ×57 — the union: 187 distinct
GET  https://jobs.gov.gy/<id>/<slug>.html                            the advert: JobPosting + labelled fields; a gone id → the home page (3)
```

```
jobsgovgy.py list                          # the first page, then every non-empty category; «N emitted — the site states M: equal/short»
jobsgovgy.py list --category 33 --category 1   # a filtered walk, not compared to the board's count
jobsgovgy.py list --no-categories          # the first twenty only, «167 short (--no-categories: the first page only)»
jobsgovgy.py ad --url https://jobs.gov.gy/2591/Assistant.html
```

**Why categories and not the pager.** The list's pager is a script under
`/language/`, which the rules refuse in writing — a written `Disallow` is
honoured by every route, so the script is not read and its parameter is not
guessed. The site's own «By Category» page gives the same search a second
axis with live counts, each below the twenty a page shows; the adapter
walks them, unions the ids, and stops when the union reaches the stated
count (58 requests, ~6 min at the server's five-to-seven seconds a search).
A category above twenty would be truncated by the pager the adapter cannot
follow: each search's own «Jobs Found» is compared to its cards and any
shortfall is named beside the final count.

## What is withheld

The description scrubbed of e-mail addresses and telephone numbers; the
employer's logo never emitted; the application (`apply_now.php`, an
account) never touched; `contacts_withheld` on every record.

## The guard

`ANationalJobBankWhosePagerIsBehindAWrittenRefusalAndWhoseCategoriesEachFitOnePage`
in `tests/test_core.py`: the first page then the categories, the union
against the stated count, a repeated id once, a category beyond one page
named, `--no-categories`, `--category`, an empty result, a page without the
search (6), the empty type span leaving the salary in its place, the
advert's JobPosting and fields with the description scrubbed and the logo
and apply link absent, the home page for a gone id (3), bad addresses
refused before any request, another host refused before the gate (7).
Mutation bench 2026-09-21: 9 mutations, 9 red.
