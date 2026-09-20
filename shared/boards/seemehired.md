# Board adapter — SeeMeHired (`seemehired.com`, a Belfast ATS whose employers' vacancies are published on one board for the UK and Ireland): the list `/jobs?page=N` is server-rendered, 12 cards a page, its count and page stated in a status line; the job page carries a JobPosting; `seemehired.py`, the street and the postal code never emitted

<!-- verified: 2026-09-20 -->

<!-- hosts: seemehired.com -->
<!-- host-forms: seemehired.com -->
<!-- host-forms-basis: read — `seemehired.py:HOST`, a single literal, every other host refused before the gate (`api.seemehired.com`, refused in writing under `/api/`, is never requested) · 2026-09-20 -->
<!-- script: seemehired.py -->
<!-- countries: GB IE -->
<!-- content: measured · **2026-09-20 14:4x–14:5x UTC, the declared client, the guard on the exact path first, the list read twice. Rules (200, 1 713 B): `User-agent: *` / `Allow: /` / `Disallow: /jobs/filtered`, `/internal-opportunities/`, `/healthz`, `/api/`, `/public/indexing/`; `Bytespider` refused `/`; no Crawl-delay; a sitemap index declared. The list `/jobs` (200, 71 514 B ×2, same md5) is a Nuxt page rendered server-side: `<p class="sr-only" role="status">1639 jobs found. Showing page 1 of 137.</p>`, 12 cards `<a href="/jobs/<id>" aria-label="View job: <title> at <company> in <place>" posteddate="7 hours ago" status="Full time">` with tag spans (the schedule, the salary text «From £14.00 Hourly to £18.50 Hourly»), `/jobs?page=2` (72 KB, «Showing page 2 of 137», other cards); `/jobs?company=progressive-building-society` answers the same 1 639 — the per-company filter is not on the permitted list (the filtered list, `/jobs/filtered`, is refused in writing), so the issue's «one tenant at a time» is not available: the board is the unit. The job page `/jobs/10821` (200, 69 943 B) carries one schema.org JobPosting (title, identifier — the employer —, datePosted, validThrough, employmentType «PART_TIME», hiringOrganization, jobLocation.address with streetAddress «Unit 2 Milltown Industrial Estate, Upper Dromore Rd, Warrenpoint», addressLocality «Newry», postalCode «BT34 3PN», addressCountry «GB», directApply, description as HTML). `seemehired.py jobs --max-pages 2` live: 24 emitted of the 1 639 stated, «2 page(s) of 12 walked by request out of 137»** · 2026-09-20 -->
<!-- witness: the page's own status line («N jobs found. Showing page x of y») — `seemehired.py jobs` prints it beside the emitted count on every walk · 2026-09-20 -->
<!-- route: http · 1639 · 2026-09-20 -->

**Issue #475 (opened under #406, the ATS families). The issue named
`<entreprise>.seemehired.com`; measured 2026-09-20: the employers'
vacancies live on the vendor's own board `seemehired.com/jobs` (150+
Northern Irish employers, the UK and Ireland), and the per-employer filter
is on a route refused in writing — so this is a board adapter, not a
tenant adapter, and the card says so.** Rank: the pilot's order of
2026-09-20 12:5x, after #474.

## What SeeMeHired is

SeeMeHired (Belfast, 2020) is an ATS whose employers publish on the
vendor's board: `seemehired.com/jobs` lists every live vacancy, `/jobs/<id>`
is a job, the application is on the job page. The vendor's site is the
board; the employers do not have hosts of their own.

## The route — a server-rendered list, a status line for the count

```
GET https://seemehired.com/jobs                    200 — «1639 jobs found. Showing page 1 of 137.», 12 cards
GET https://seemehired.com/jobs?page=2             200 — «Showing page 2 of 137», 12 other cards
GET https://seemehired.com/jobs/10821              200 — the JobPosting (the `ad` command)
    https://seemehired.com/jobs/filtered           NOT SENT — refused in writing (the per-company filter lives there)
```

The status line is the witness — count and page — printed beside the
emitted number; a page that repeats, or that says it is another page than
the one asked, dies with 6. **137 pages on 2026-09-20: bound the walk with
`--max-pages`**; the user filters at home. Two seconds between requests
are ours.

## What the adapter emits, and withholds

`jobs [--country-code GB|IE] [--max-pages N]`: id, url, title, company,
place, schedule, salary (the tag with a currency or a number), posted_ago
(the card's relative date), tags. **The list states no country: the board
is UK & Ireland, the job page says which; `--country-code` stamps the
rows and says so.** `ad --url`: title, company, place, region, country,
employment_type, posted, closes, description (scrubbed).

**Withheld:** the street and the postal code of the workplace; e-mail
addresses and telephone numbers in the description; the application never
touched; `contacts_withheld` on every record.

## Tests and mutations

`AnATSWhoseEmployersShareOneServerRenderedBoardThatStatesItsCountAndPageInAStatusLine`,
both ways on fixtures (the walk to the stated 15 over two pages, the card
fields and the salary tag, the stamp, the bounded walk, a repeating page,
a page with the right number and the same cards, a page that says it is
another page, the empty board, a page without the status line, the ad's
JobPosting with the street and postcode withheld and the description
scrubbed, the address rebuilt, bad addresses, other hosts refused).
Mutation bench on a detached copy, `python3 -B`, 9 / 9 red: a repeat
tolerated · the page number not checked · the status line not required ·
the salary tag dropped · the label not split · the street emitted · the
description not scrubbed · tracking kept in the ad address · another host
sent.
