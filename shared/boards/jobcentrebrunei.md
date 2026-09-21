# Board measurement — JobCentre Brunei (`www.jobcentrebrunei.gov.bn`, Brunei): the public employment service's job portal («Pusat Pekerjaan Brunei») — the search page served to the declared client with «Showing … of N entries» (607 on 2026-09-21, 579 on 2026-09-18), walked by the Liferay pager the page itself prints; `jobcentrebrunei.py` — the advert's age range never emitted (#183)

<!-- verified: 2026-09-21 -->

<!-- hosts: www.jobcentrebrunei.gov.bn -->
<!-- script: jobcentrebrunei.py -->
<!-- countries: BN -->
<!-- content: measured · **the board walked by the declared client, 2026-09-21 13:14–13:16 UTC, the guard on each path, two reads of the list and of one advert. `/search-job` (200, 437 124 B ×2, md5 98acba9488c0 / 4b098963c4cf — the portlet's instance id moves) states **«Showing 1 to 12 of 607 entries»** (579 on 2026-09-18 — the count moves with the board) and prints its search portlet's id in its own pager links (`com_liferay_portal_search_web_search_results_portlet_SearchResultsPortlet_INSTANCE_8nOy3KJMzV3M`); asking that portlet `cur=2&delta=75` (its «entries per page» maximum) answers 200, 1 166 291 B, «Showing 76 to 150 of 607 entries», 75 cards. A card carries the title, the employer, `jp_job_salary` («$ 500 - 600 Monthly»), `jp_vacancy` («VACANCY: 4» — posts, not adverts), `jp_time`, `jp_job_location` (district, mukim, kampong), `jp_closing-date` and the advert's link; no JobPosting. The advert `/web/guest/view-job/-/jobs/211200374/shop-assistant` (200 ×2, 200 814 B) renders a `job-viewer` block: the description, then a «Job Overview» of labelled rows — Date Posted, Hours, Industry Type, Position, Salary, Experience, District, Mukim, Kampong, Allowances Range, Driving License Class, **Age (20-28)**, Last date to apply — and the portal's own hotline in the footer. Exercised: `jobs --max-pages 2 --country-code bn` → **150 emitted, the portal states 607** (2 pages of 75, «457 short» said); `ad` → the overview read, `withheld_rows: ["age"]`** · 2026-09-21 -->
<!-- route: http · 607 · 2026-09-21 -->
<!-- witness: the search page's own «Showing … of N entries» — 607 on 2026-09-21 (579 on 2026-09-18), printed beside the emitted count on every run · 2026-09-21 -->

**Found by the Brunei search of #611 (a country never searched), measured
2026-09-18 06:37–06:39 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #611: one
search naming the public employment service (JobCentre Brunei, the
Ministry's business portal points at it) and the private portal the
engine names, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('www.jobcentrebrunei.gov.bn', '/search-job')   open, certain
GET https://www.jobcentrebrunei.gov.bn/search-job               200 ×2 — «Showing 1 to 12 of 579 entries», Liferay pager, /web/guest/view-job/-/jobs/<id>/<slug>
```

**The public employment service, served with its count** — at the top of
Brunei's list. The Liferay pager's parameters (`p_p_id=…`, `delta`,
`cur`), and what a `view-job` page carries, are the adapter's first line
(its `adapter` issue).

## The adapter — `jobcentrebrunei.py` (#690, 2026-09-21)

```
GET /search-job                                                        200 — «Showing 1 to 12 of 607 entries» + the portlet's INSTANCE id in its pager links
GET /web/guest/search-job?p_p_id=<portlet>&…_cur=N&…_delta=75&…_resetCur=false   200 — 75 cards a page, to the stated count
GET /web/guest/view-job/-/jobs/<id>/<slug>                             200 — the `job-viewer` block (the `ad` command)
```

**The portlet's instance token is read from the page, never composed** — it
is this deployment's, and a composed one would ask for a portlet that does
not exist. The walk is `ceil(stated / 75)` pages and prints «N emitted, the
portal states M»; a page repeating the previous ids ends it (exit 6). Each
card's cells are read **one class at a time**: a single scanning regex lets
the wrapper `jp_job_post_right_cont` swallow the salary nested inside it —
measured, and pinned by the guard.

**Emitted:** id, url, title, employer, place (district, mukim, kampong),
salary as the portal prints it, schedule, `posts` (the advert's vacancy
count), closing date; and from the advert: position, industry, allowances,
experience, driving licence class, posted, closes, the description.

**Withheld — and this one is a decision, not an omission:** the advert's
**`Age` row** («Age 20-28»). The portal publishes an age range on some
vacancies; the plugin **serves the advert and does not carry the criterion**
(#183, 2026-09-04: a law that forbids what a board publishes does not stop
us serving the ad — it stops us propagating the criterion). The record says
which rows were withheld (`withheld_rows: ["age"]`) so that a silent drop is
not mistaken for a board that publishes none. Also withheld: e-mail
addresses and telephones in the texts (the portal prints its own hotline on
every page), the employer's logo, the jobseeker area (a login, never
touched). `--country-code` **stamps** (the board is Brunei's and states no
country) and the run says so.

**Tests and mutations.**
`APublicEmploymentServiceWhoseLiferayPagerIsReadFromThePageAndWhoseAdvertPrintsAnAgeRange`,
both ways on fixtures (the pager built from the page's own token, the walk
against a stated count, `--max-pages` and its «short» line, the repeating
page, a page without the token, a page without the count, the apex refused;
the advert with its age row, its e-mail and its telephone, the advert gone
or changed). Mutation bench on a detached copy, `python3 -B`, 7 / 7 red: the
age row emitted · the withheld list dropped · the portlet id composed
instead of read · the stated count ignored · the repeat check dropped · the
cells read by one scanning regex (the salary is lost) · another host sent.

