# Board adapter — Jobtoolz (a Belgian ATS, one tenant at a time): the employer's jobsite on `<tenant>.jobtoolz.com/<lang>` carries its whole list inline in the page (`window.jobComponent([jobs], 8, …)`) — one request is the board; its rules refuse every query string, and none is ever sent; the job page on the same host carries a JobPosting; `jobtoolz.py`, the street and the postal code never emitted

<!-- verified: 2026-09-21 -->

<!-- hosts: cnh-industrial.jobtoolz.com, altebra.jobtoolz.com -->
<!-- host-forms: {tenant}.jobtoolz.com -->
<!-- host-forms-basis: read — `jobtoolz.py:DOMAIN` with the tenant as its subdomain (`tenant_of`), one per run, every other host refused before the gate; `api.jobtoolz.com` (the page's bearer-token API, refused `/*?` in writing) is never requested; the vendor's `jobs.jobtoolz.com` is its own jobsite, not a board · 2026-09-21 -->
<!-- script: jobtoolz.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants named, one read, 2026-09-20 14:5x and 2026-09-21 04:1x UTC, the declared client, the guard on the exact path first, the page read twice. Rules (`cnh-industrial.jobtoolz.com/robots.txt`, 78 B, the same on `api.jobtoolz.com`): `googlebot` `Allow: *`; `User-agent: *` / `Disallow: /*?` / `Disallow: /*.pdf$` — every address with a query string is refused in writing to `*`, on the tenant host and on the API host; no Crawl-delay. The jobsite `/en` (200, 127 483 B ×2, same md5) is server-rendered with `Jobtoolz.api = {url: 'https://api.jobtoolz.com', token: 'eyJ…'}` (a public page token, never used — its calls would carry query strings) and the list INLINE: `<div id="jobs" x-data="window.jobComponent([{id, title, button, url, image_url, location, types, filters: {filterIds, locationId, types}}, …], 8, [locations], [types], [filter groups])">` — five jobs for CNH Industrial Belgium, paged client-side 8 a page, filtered by location, type and category groups («Filter by type»: Engineering, Internship, Service, Software); the jobs' `url` point at the employer's white-labelled domain (`www.cnhind-belgium.be/en/<slug>`), whose `build/jobsites/assets/app.js` (181 853 B, read once) carries no list call; the same slug is served on the tenant host — `/en/harvesting-automation-concept-systems-engineer` (200, 88 884 B) with one schema.org JobPosting (title, datePosted, employmentType ["FULL_TIME"], hiringOrganization «CNH», jobLocation.address with streetAddress «Léon Claeysstraat 3a», addressLocality «Zedelgem», postalCode «8210», addressCountry «BE», description). `altebra.jobtoolz.com` (Altenova): TLS `tlsv1 alert internal error` to the declared client on 20.09 and no answer to `curl` on 21.09 — not read. `jobtoolz.py jobs` live: CNH Industrial 5 emitted, «the inline list is the board: no count is stated»; `ad` on the job above** · 2026-09-21 -->
<!-- witness: none — the page states no count; the inline list is the board and `jobtoolz.py jobs` says so · 2026-09-21 -->
<!-- route: http · 5 · 2026-09-21 -->

**Issue #478 (opened under #406, the ATS families). Tenants found by the
signature `<tenant>.jobtoolz.com` in a search engine on 2026-09-20 (CNH
Industrial Belgium, Altenova `altebra`, the vendor's own); one measured
twice, the other unreachable at the transport (TLS) — the README's
two-tenant rule is short of one, said here.** Rank: the pilot's order of
2026-09-20 12:5x, after #477; delivered on the resume of 2026-09-21 04:1x
UTC, the point in flight when the owner's pause came.

## What Jobtoolz is, and where its tenants live

Jobtoolz (Kortrijk) is a Belgian ATS whose jobsites live on
`<tenant>.jobtoolz.com/<lang>` (en, nl, fr) and are often white-labelled on
the employer's own domain (`www.cnhind-belgium.be`, `jobs.h2ogroup.be`);
a job at `/<lang>/<slug>`, the application on the job page. **The user
names the tenant by its subdomain**, its host or the jobsite's URL.

## The route — the page's own inline list, and never a query string

```
GET https://cnh-industrial.jobtoolz.com/en                                         200 — window.jobComponent([5 jobs], 8, …)
GET https://cnh-industrial.jobtoolz.com/en/harvesting-automation-concept-systems-engineer   200 — the JobPosting (the `ad` command)
    https://api.jobtoolz.com/…?…  ·  https://cnh-industrial.jobtoolz.com/en?page=2   NOT SENT — refused in writing (Disallow: /*?)
```

**The rules refuse every query string to every agent**, and the adapter
refuses to send one before the gate (exit 7): the language is a path, the
list is inline, the API the page holds a token for is never called. No
count is stated: the inline list is the board and the note says so. Two
seconds between requests are ours.

## What the adapter emits, and withholds

`jobs --tenant <name> [--lang en|nl|fr] [--country-code ISO2]`: id, url (the
job on the tenant host), employer_url (the white-labelled address the page
links), title, place (the town), schedule, categories (the filter groups'
labels). **The list states a town, no country: `--country-code` stamps the
rows and says so; the job page says which.** `ad --url`: title, company,
place, region, country, employment_type, posted, closes, description
(scrubbed).

**Withheld:** the street and the postal code of the workplace; the header
image; e-mail addresses and telephone numbers in the description; the
application never touched; `contacts_withheld` on every record.

## Tests and mutations

`AnATSWhoseJobsiteCarriesItsWholeListInlineAndWhoseRulesRefuseEveryQueryString`,
both ways on fixtures (the five JSON arguments decoded, one request, the
rows with both addresses and the category labels, a repeated id, the stamp
and the language path, the empty list, a page without the component, a
404, a query string refused before any request, other hosts refused, bad
tenants, the ad with the street and postcode withheld and the description
scrubbed, the query string dropped from the ad address, the vendor's hosts
refused). Mutation bench on a detached copy, `python3 -B`, 9 / 9 red: a
query string sent · duplicate ids emitted · the categories not resolved ·
the tenant-host address not rebuilt · a missing component read as empty ·
the street emitted · the description not scrubbed · the query kept in the
ad address · the vendor's host read in `ad`.
