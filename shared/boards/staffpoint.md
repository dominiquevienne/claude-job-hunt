# Board adapter — StaffPoint (`www.staffpoint.fi`, FI): the Finnish staffing group's own board, whose job list is filled by the page's own server action and never rendered — replayed as the page makes it, its id read from the page's script on every run; «153» stated by the call on 2026-09-14 and printed beside every walk; the consultant's e-mail on the ad never emitted

<!-- verified: 2026-09-14 -->

<!-- hosts: www.staffpoint.fi -->
<!-- script: staffpoint.py -->
<!-- host-forms: www.staffpoint.fi -->
<!-- host-forms-basis: read — every row's `jobAdBaseUrl` and every JobPosting `url` is on `www.staffpoint.fi`; `staffpoint.py` names the host as a literal and refuses an ad address on any other · 2026-09-14 -->
<!-- countries: FI -->
<!-- content: measured · **`/sitemap.xml` (200, 648 rows) names the site's pages, 323 articles and the English twins — not one job. `/tyopaikat` (200, 383 421 B) is a React Server Components page whose flight data carries only the 15 «open applications» (`openApplications.jobs`, `totalCount` 15 — standing invitations, not advertisements); its job list starts empty and is filled on the client by `fetchJobs`, a Next.js server action: a POST to `/tyopaikat` itself with `Next-Action: <id>` and `[{"sortBy":"startDate","sortOrder":"desc","openApplications":"false","size":"9"}]`, answered as `text/x-component` whose line `1:` is `{"jobs":[…],"totalCount":153}`. The id is bound to the build, so the adapter reads it from the page's own `app/[locale]/jobs/page-*.js` on every run and replays the call with the page's own parameters, `size` = `totalCount` (the page's pager is «load more»). 153 emitted, 153 stated — equal, 4 requests.** The row: `id`, `name`, `validFrom`/`validUntil` (dd.mm.yyyy or «Jatkuva haku»), `employmentType` (84 «Määräaikainen», 32 «Toistaiseksi voimassa oleva», 28 «Keikkatyö», 9 English), `locations` (region → cities), `fields`, `language` (144 fi, 9 en). The ad `/tyopaikat/<slug>-<id>` (200, ~290 KB) carries a JobPosting JSON-LD: `identifier` (the list's id), title, plain-text description, `datePosted`/`validThrough`, `employerOverview` (the type), `industry`, `jobLocation[]` (region as `name`, town as `addressLocality`), `hiringOrganization` (the client when named — «K-Citymarket» — else «StaffPoint Oy»), `baseSalary` min/max when stated (EUR, no unit written; the text says «€/h») — read by the declared client, the guard on the exact path (the rules, 823 B: `*` `Disallow: /search` only, SEO crawlers and scanners refused; no Crawl-delay, 2 s ours; `/search` refused before the gate); **`applicationContact.email` — a named consultant on most ads — never emitted; the description scrubbed of e-mail addresses and Finnish telephone numbers; `contacts_withheld` on every record; the application (`my.staffpoint.fi`, a login) never touched** · 2026-09-14 -->
<!-- witness: the call's own `totalCount` — printed beside every walk («153 emitted, the site states 153 (the page's own fetchJobs call, `totalCount`) — equal»); one reading of 176 between four of 153 at 06:00 local — the count moved or a variant was served, the adapter prints what it reads; a page whose script no longer names `fetchJobs` exits 6, a call without `totalCount` exits 6 — a changed page, never an empty market · 2026-09-14 -->

**StaffPoint is one of Finland's largest staffing groups — 153 advertisements
stated on the day, retail, snow work, industry and hospitality across Lapland
(69 rows name a Lappi town), Uusimaa and Varsinais-Suomi, 84 fixed-term.**
Issue #378. Measured 2026-09-14 03:5x–04:0x UTC by the declared client, the
guard on the exact path before each request, two seconds apart.

## Where the list is, and where it is not

```
www.staffpoint.fi/robots.txt                  200, 823 B — User-agent:*: Disallow /search; SEO crawlers, scanners refused; Sitemap /sitemap.xml
GET /sitemap.xml                              200, 648 rows — pages, 323 articles, the English twins: 0 jobs
GET /tyopaikat                                200, 383 421 B — flight data: openApplications {jobs[15], totalCount 15}; the job list: {}
GET /_next/static/chunks/app/[locale]/jobs/page-<hash>.js   200, 66 429 B — createServerReference("<id>", …, "fetchJobs")
POST /tyopaikat  Next-Action: <id>  [{"sortBy":"startDate","sortOrder":"desc","openApplications":"false","size":"153"}]
                                              200, text/x-component — 1:{"jobs":[153], "totalCount":153}
GET /tyopaikat/<slug>-<id>                    200, ~290 KB — JobPosting JSON-LD (twice, identical)
```

**The call is the page's own, to the page's own address, with the page's own
parameters** — nothing is guessed, no other host is asked, and `/search`
(refused in writing) is never sent. What makes it fragile is the build, not
the rules: the action id changes at every deploy, so it is read from the
page's script each run, exactly as a browser would, and a page whose script
no longer names `fetchJobs` exits 6 rather than printing zero. The `/haku`
page is a site-wide text search («Haku sivustolta»), not the job list.

## The record, and what is withheld

The list row carries the site's own fields; the ad's JobPosting adds the
client, the salary range when stated, the dates and the description.
**`applicationContact.email` — a named consultant on most ads — is never
emitted; the description is scrubbed; the application, a login on
`my.staffpoint.fi`, is never touched.** Open applications («avoin haku») are
not emitted: they are invitations, not advertisements, and the site keeps
them apart (`openApplications: "false"`).

## Running it

```
python3 skills/job-scan/scripts/staffpoint.py list                 # 153 rows, 4 requests
python3 skills/job-scan/scripts/staffpoint.py list --limit 20 --lang en
python3 skills/job-scan/scripts/staffpoint.py ad --url https://www.staffpoint.fi/tyopaikat/<slug>-<id>
```

Exit codes: 0 all read · 3 the ad is gone · 6 the page no longer lists as it
did, or a call without its count (a changed page, never an empty market) ·
7 a refused path. No key, no browser, no login.
