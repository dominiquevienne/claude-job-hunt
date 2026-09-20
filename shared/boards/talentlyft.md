# Board adapter — TalentLyft (a Croatian ATS, one tenant at a time): the employer's careers site on `<tenant>.talentlyft.com` writes a rules file without a group that refuses the page's own list call (`/JobList`) and asks `Crawl-delay: 150`; the sitemap it declares names every `/jobs/<slug>` page, each with a JobPosting — the sitemap is the list, read at the written delay; `talentlyft.py`, the street line and the postal code never emitted

<!-- verified: 2026-09-20 -->

<!-- hosts: secret-level.talentlyft.com, flyer-one-ventures.talentlyft.com -->
<!-- host-forms: {tenant}.talentlyft.com -->
<!-- host-forms-basis: read — `talentlyft.py:DOMAIN` with the tenant as its subdomain (`tenant_of`), one per run, every other host refused before the gate; the vendor's `www.`, `help.`, `careers.` and `app.` are not tenants · 2026-09-20 -->
<!-- script: talentlyft.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants with jobs, 2026-09-20 14:3x–14:4x UTC, the declared client, the guard on the exact path first, each site read twice. Rules (`<tenant>.talentlyft.com/robots.txt`, 200, 202 B, the same on both): `Crawl-delay: 150` / `Disallow: /JobList` / `/ArticleList` / `/joblist` / `/articlelist` / `/JobsSimple` / `/js` / `Sitemap: https://<tenant>.talentlyft.com/sitemap.xml` — **and no `User-agent:` line**: `_robots.allowed()` reads a file without a group as addressed to nobody (allowed on `/`, `/jobs/<slug>` and `/sitemap.xml`; `/JobList` INDETERMINATE — «writes Disallow: /JobList, which matches this path» — and an indeterminate is not probed), `crawl_delay` None (no group to carry it). The site (200; Secret Level 263 009 B ×2 same md5, Flyer One Ventures 269 009 B ×2 same md5) is a server-rendered shell whose `#jobs-list-<id>` is empty at load and filled by the page's script from `window.tlApp` (`pageId`, `websiteId`, `subdomain`, `jobs: [{id, layoutId, filterDepartments…}]`) — the list call is the refused `/JobList`, never requested. The sitemap (200; Secret Level 1 157 B: 5 `/jobs/<slug>` entries with `lastmod` + the root; Flyer One 3 574 B: 16 + the root); the job page `/jobs/full-stack-engineer-ceUz` (200, 285 159 B) carries one schema.org JobPosting (title, datePosted, employmentType «FULL_TIME», hiringOrganization, jobLocation.address with streetAddress «Los Angeles, CA, United States of America (Remote)», addressLocality, addressRegion, postalCode, addressCountry «US», description as escaped HTML). `talentlyft.py` live: `ad` on that page; `jobs --max-pages 1` on Secret Level — «the sitemap names 5 job page(s); reading 1 at the written Crawl-delay of 150 s», 1 emitted, the second request waited the 150 s** · 2026-09-20 -->
<!-- witness: the sitemap's own list of `/jobs/` entries — a count of pages named, not a count the site states; `talentlyft.py jobs` prints it beside the emitted number and says so · 2026-09-20 -->
<!-- route: http · 21 · 2026-09-20 -->

**Issue #474 (opened under #406, the ATS families). Tenants found by the
signature `<tenant>.talentlyft.com` in a search engine on 2026-09-20
(Secret Level, Flyer One Ventures, Taleolithic, TalentLyft's own); two
measured twice, as the README's two-tenant rule asks.** Rank: the pilot's
order of 2026-09-20 12:5x, after #473.

## What TalentLyft is, and where its tenants live

TalentLyft (Zagreb) is an ATS with hosted careers sites on
`<tenant>.talentlyft.com`, a job at `/jobs/<slug>`, the application on the
job page. **The user names the tenant by its subdomain**, its host or the
site's URL.

## The route — the declared sitemap, at the written delay

```
GET https://secret-level.talentlyft.com/sitemap.xml                          200 — 5 /jobs/<slug> entries with lastmod, the root
GET https://secret-level.talentlyft.com/jobs/full-stack-engineer-ceUz         200 — the JobPosting (also the `ad` command)
    https://secret-level.talentlyft.com/JobList                               NOT SENT — refused in a file without a group: INDETERMINATE, not probed
```

**The rules file has no group.** Its `Disallow: /JobList` is addressed to
nobody, so the guard answers INDETERMINATE on that path — and an
indeterminate is not probed: the page's own list call is never made. Its
`Crawl-delay: 150` is addressed to nobody too, and the adapter honours it
as written — 150 s between requests, the pace built with the file's own
number — because the operator's intention is legible even where the
file's grammar is not. A run says how long the walk will take before it
starts; `--max-pages` bounds it. The sitemap names pages, it states no
count: the note says so.

## What the adapter emits, and withholds

`jobs --tenant <name> [--country-code ISO2] [--max-pages N]`: id (the
slug), url, title, company, place, region, country (`addressCountry`; a
posting without one is stamped with `--country-code`, said aloud), remote
(when the street line says so), employment_type, posted, closes, updated
(the sitemap's lastmod), description (scrubbed). `ad --url`: the same for
one page.

**Withheld:** the street line («Los Angeles, CA, United States of America
(Remote)») and the postal code; e-mail addresses and telephone numbers in
the description; `contacts_withheld` on every record.

## Tests and mutations

`AnATSWhoseRulesRefuseTheListCallInAFileWithoutAGroupSoTheDeclaredSitemapIsTheListAtTheWrittenDelay`,
both ways on fixtures (the sitemap's `/jobs/` entries walked in order,
once each, the root and other paths left out; the JobPosting mapped with
the street and postcode withheld; the remote flag; the country and the
stamp; a gone page counted and named; the bounded walk; the empty sitemap;
a host without a sitemap; a non-sitemap answer; the real `request()`
building its pace with the written 150 s; the ad; other hosts and the
vendor's hosts refused; bad tenants). Mutation bench on a detached copy,
`python3 -B`, 10 / 10 red: the written delay ignored · other paths walked
· duplicate slugs read twice · the postcode emitted · the street emitted ·
the description not scrubbed · the country filter dropped · gone pages
unnamed · a non-sitemap read as empty · the vendor's host read in `ad`.
