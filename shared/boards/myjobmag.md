# Board adapter — MyJobMag (`www.myjobmag.com` Nigeria, `.co.ke` Kenya, `.co.za` South Africa, `myjobmagghana.com` Ghana, `.co.uk` UK): one generalist on five fronts by `--host`, whose list states no count and is an archive — walked newest-first and bounded by date: 4 464 cards in 30 days on Nigeria, 1 796 Kenya, 1 409 South Africa; Ghana and the UK dormant; one record per position of an advert, the application text scrubbed

<!-- verified: 2026-09-14 -->

<!-- hosts: www.myjobmag.com, www.myjobmag.co.ke, www.myjobmag.co.za, www.myjobmagghana.com, www.myjobmag.co.uk -->
<!-- script: myjobmag.py -->
<!-- host-forms: www.myjobmag.com, www.myjobmag.co.ke, www.myjobmag.co.za, www.myjobmagghana.com, www.myjobmag.co.uk -->
<!-- host-forms-basis: read — `myjobmag.py` names the five hosts as `BOARDS` and builds every address on the host `--host` names; the Nigerian front's header links the four others; all five were exercised on the day · 2026-09-14 -->
<!-- countries: NG KE ZA GH GB -->
<!-- content: measured · **the site states no count on any front** — `/jobs` («Jobs in Nigeria», 123 788 B) prints 35 dated cards a page and a pager without an end (page 1 000 answered 200 with cards of 12 February); the two job sitemaps stop at exactly 45 001 and 45 000 rows, a cap; **so the adapter walks newest-first and stops at the first card older than `--days` (30): Nigeria 4 464 cards over 128 pages (1 439 adverts of several positions) stopped at 2026-08-14; Kenya 1 796 over 72 pages; South Africa 1 409 over 79 pages; Ghana 0 — its first card is dated 18 February 2026 and the rest May–June 2024; UK 0 — first card 16 May 2026** — read by the declared client, the guard on the exact path, 01:34–01:43 UTC; the rules on each front (320–403 B) refuse every query string (`/*?`), the search, the account pages and `/apply-now/`, nothing of the list, the pager or the ads; **the «Method of Application» block carries the address an employer wants a CV sent to — scrubbed on every record, with the description; the contact person never named** · 2026-09-14 -->
<!-- witness: none stated by the site — the adapter prints the pages walked, the cards emitted and the date it stopped at, and exits 6 on a 200 page without one card (a changed template, never an empty market); the card count per page on the day (35 / 25 / 18 / 18 / 20 by front) is the only outside figure · 2026-09-14 -->

**MyJobMag is one Nigerian operator's template on five hosts — Nigeria,
Kenya, South Africa, Ghana, the UK — with 4 464 postings in the last
thirty days on the Nigerian front alone, the second largest inventory
measured for the country after HotNigerianJobs.** Issue #391. Measured
2026-09-14 01:2x–01:43 UTC by the declared client, the guard on the exact
path before each request, on each of the five hosts.

## Rules and the routes

```
www.myjobmag.com/robots.txt        200, 401 B — User-agent: *: Disallow /search/jobs?*, /*?, /profile, /access, /create, /saved-jobs, /signout, /activate, /login, /signup, /user/*, /videos/tag/*, /apply-now/, /&page=, /job-application/, /learn/ ; Sitemap: /sitemapindex.xml
www.myjobmag.co.ke, .co.za         the same file (384 B, 403 B)
www.myjobmagghana.com              352 B — the same without /&page= and /learn/
www.myjobmag.co.uk                 320 B — the same, shorter (a «Disllow:» typo on /signup)
GET https://www.myjobmag.com/jobs                200, 123 788 B — «Jobs in Nigeria», 35 dated cards, pager 1…5 (no last page)
GET https://www.myjobmag.com/jobs/page/1000      200, 128 541 B — 35 cards dated 12 February: the list is an archive
GET https://www.myjobmag.com/sitemapindex.xml    200 — sitemap-main-jobs.xml 45 001 /jobs/<slug> (adverts), sitemap-sub-jobs.xml 45 000 /job/<slug> (positions), no lastmod: a cap, not a count
GET https://www.myjobmag.com/job/<slug>          200, 73 875 B — one position: JSON-LD JobPosting (raw newlines in its description), «Posted: Sep 12, 2026», «Deadline: Not specified», job-key-info labels, job-details, «Method of Application»
GET https://www.myjobmag.com/jobs/<slug>         200, 79 547 B — an advert: «Open Jobs» 1…4, one <h2 id="jobNNNNNNN"> block per position, no JSON-LD
```

**Every URL with a `?` is refused in writing, so the adapter never sends
one**: the pager is the path `/jobs/page/N` and none of the site's
filters (query strings) is used — `--host` is the only selector. No
Crawl-delay; 2 s is the adapter's own.

## The list states no count — the walk is bounded by date

```
myjobmag.py list --host ng
[myjobmag] 4 464 card(s) emitted over 128 page(s) on www.myjobmag.com (NG), newest-first, stopped at the first card dated 2026-08-14 — older than --days 30; the site states no count and its list is an archive: walked by date, not a shortfall.
[myjobmag] 1 439 of them are adverts holding several positions — `ad --url` reads each and emits one record per position; no contact is emitted on any route.
myjobmag.py list --host gh
[myjobmag] 0 card(s) emitted over 1 page(s) on www.myjobmagghana.com (GH), newest-first, stopped at the first card dated 2026-02-18 — older than --days 30; …
```

| front | `--host` | cards a page | page 1 dated | 30 days on the day |
| :-- | :-- | :-- | :-- | :-- |
| Nigeria `www.myjobmag.com` | `ng` (default) | 35 | 12 September | **4 464** over 128 pages, 1 439 adverts |
| Kenya `www.myjobmag.co.ke` | `ke` | 25 | 13 September | **1 796** over 72 pages, 577 adverts |
| South Africa `www.myjobmag.co.za` | `za` | 18 | 13 September | **1 409** over 79 pages, 1 112 adverts |
| Ghana `www.myjobmagghana.com` | `gh` | 18 | 18 February, then May–June 2024 | **0** — a dormant front, served |
| UK `www.myjobmag.co.uk` | `uk` | 20 | 16 May | **0** — stale |

A card is dated («12 September» this year, «10 June, 2024» otherwise)
and links to `/job/<slug>` — a position — or to `/jobs/<slug>` — an
**advert** of several positions («Medical Consultants at Bergstein
Hospital»: four). The listing record: `kind`, url, title, employer (the
logo's `/jobs-at/<slug>` page, or the title's «at …» tail when the
employer has none), `posted`, the snippet scrubbed. **A 200 page without
one card exits 6** — the template changed; the market did not empty.

## The ad — one record per position

```
myjobmag.py ad --url https://www.myjobmag.com/jobs/medical-consultants-at-bergstein-hospital-1
{"id": "1333338", "url": "https://www.myjobmag.com/job/consultant-cardiologist-bergstein-hospital", "advert_url": "…/jobs/medical-consultants-at-bergstein-hospital-1", "title": "Consultant Cardiologist", "employer": "Bergstein Hospital",
 "job_type": "Full Time", "qualification": "BA/BSc/HND", "experience": null, "location": "Lagos", "city": "Ikorodu", "job_field": "Medical / Healthcare", "salary_text": null, "posted": "2026-09-12", "deadline": "Not specified", "description": "…", "application_method": "…", "contacts_withheld": true}
[myjobmag] 4 position(s) on https://www.myjobmag.com/jobs/medical-consultants-at-bergstein-hospital-1; the «Method of Application» text and the description are scrubbed; no contact is emitted.
```

Each `<h2 id="jobN">` block is a record: the position id, its own
`/job/` address, the labelled fields (Job Type, Qualification,
Experience, Location, City, Job Field, **Salary Range — «₦150,000 -
₦200,000/month», the period printed, so `salary_unit_stated` is true**),
the `job-details` text; the page's «Posted:» and «Deadline:»
(«Not specified» kept as printed), the employer; on a single-position
page the JSON-LD JobPosting too — `validThrough`, `employmentType`,
`industry`, the address — **parsed with `strict=False`, because its
description carries raw newlines and a JobPosting `json.loads` rejects
is not «none»**. **The «Method of Application» block is where an employer
writes «forward your CV to …@…» or a number to call — 2 of 3 sampled
did; it is emitted scrubbed of e-mail addresses and telephone numbers
(Nigerian, Kenyan, South African, Ghanaian, British shapes), like the
description; the site's «Apply Now» form and `/apply-now/` are never
touched; `contacts_withheld` on every record.**

## Configuration

```yaml
boards:
  myjobmag:
    enabled: true
    host: ng               # ng (default) · ke · za · gh · uk
    days: 30               # the walk stops at the first card older than this
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `host` | no | one of the five fronts; a hostname works too |
| `days` | no | 30 by default — 128 pages on Nigeria on the day, 2 s apart |

No credentials, no browser, no login. A 30-day walk is one request a
page; `ad` is one request.

## What is not established

- **A total** — the site prints none; the sitemaps are capped at 45 000;
  the archive's depth was probed to page 1 000 (February) and not to its
  end.
- **Fields the ad may carry beyond the day's sample** — «Salary Range»
  and «City» appear on some blocks only; a label the sample did not show
  is emitted under its own name by `key_info`.
- **Ghana and the UK** — dormant on the day (first cards February and
  May 2026); the fronts answer and the adapter walks them; nothing says
  whether they will fill again.
- **The country of a posting on the UK front** — the front is a UK
  label; the sample's cards were UK employers, not verified beyond page 1.

## 2026-09-14 — shipped

`list`: five fronts walked live — 4 464 / 1 796 / 1 409 / 0 / 0; the
Nigerian, Kenyan and South African outputs scanned: zero e-mail
addresses, zero duplicate ids, every card dated and every employer
named. `ad`: an advert of four, an advert of two, three positions — the
application block scrubbed on two of three. Three tests; six mutations on
a detached worktree (`python3 -B`), six red — the query-string guard
dropped, the date stop made inclusive, the employer not read off the
title, the advert kind not told apart, the application text not
scrubbed, the salary period dropped.
