# Board adapter — Eezy (`tyopaikat.eezy.fi`, FI): the Finnish staffing group's board, whose list is the page's own GraphQL query to the group's API — replayed as the page makes it, its text read from the page's script on every run; «236» stated by the answer on 2026-09-14 and printed beside every walk; the client withheld where the site hides it, the recruiter never emitted

<!-- verified: 2026-09-14 -->

<!-- hosts: tyopaikat.eezy.fi, api.eezy.fi -->
<!-- script: eezy.py -->
<!-- host-forms: tyopaikat.eezy.fi -->
<!-- host-forms-basis: read — every ad is `/fi/tyopaikat/<id>` on `tyopaikat.eezy.fi` (the RSS's links, the page's own routes); the query goes to `api.eezy.fi/api`, the address the page's own Apollo client names; `eezy.py` names both as literals and refuses an ad address on any other · 2026-09-14 -->
<!-- countries: FI -->
<!-- content: measured · **The list is filled on the client by the page's own GraphQL query. `/fi` (200, 43 994 B, `__NEXT_DATA__`) ships only the filter values (28 fields of work, the municipalities); its `_app-*.js` (514 225 B) carries the Apollo client (`"https://api.eezy.fi" + "/api"`) and the query — `elasticJobs(filter:{searchStringArr, locations, isTraining, from, to, tags, fieldOfWorks}) { pageResults { available from to showingFallbackAdverts } jobs { id name logo customer customerDescription hideCustomer source fieldOfWorks workLocations { name } } }` — sent with `{locations: [], from: 0, to: 20}` and paged by 20. The adapter reads the text from the script on every run, sends the page's first call, then one call with `to` = `available`: 236 emitted, 236 stated — equal, 4 requests. The two things the site calls sitemaps are not inventories: `eezy.fi/tyopaikat-sitemap.xml` (782 rows) is `?job=…&location=…` facets; `tyopaikat.eezy.fi/sitemap.xml`, the one the rules name, is an RSS feed («Eezy työpaikkailmoitukset», 338 items) of 10 advertisements (the `Personnel` source, with a description and a real lastmod) and 328 location facets whose `lastmod` is the moment of the read.** The row: `id` (22 chars on the `Core` source — 226 —, 5 on `Personnel` — 10), `name`, `customer`, `hideCustomer`, `source`, `fieldOfWorks`, `workLocations`; no date. The ad `/fi/tyopaikat/<id>` (200, ~80 KB) is server-rendered with `pageProps.jobAdvert`: name, worktitle, description (HTML), customer / hideCustomer / customerDescription, `startTime`/`endTime`, `typeOfWorkRelationship`, `workRelationshipMode`, fields, `locationCity`, `locationAddress`, `workLocations`, `isDeleted`, `applyLink` (the ATS — `talent.core.eezy.fi` or `ats.talentadore.com` — never followed) — read by the declared client, the guard on the exact path (the rules: `tyopaikat.eezy.fi` a single `Sitemap:` line, no refusal; `api.eezy.fi` 404, no rules; `eezy.fi` `Disallow:` empty; no Crawl-delay, 2 s ours per host); **the client's name withheld wherever `hideCustomer` is true — the site hides it on 159 of 236, so does the adapter; `recruitmentPerson` {firstname, lastname, photo, email, phoneNumber} on the ad never emitted; the text scrubbed of e-mail addresses and Finnish telephone numbers, and a line that carried one is withheld whole — the consultant's name with it («Lisätietoja tehtävästä antaa … rekrytointikonsultti <name> p. … tai …»); `contacts_withheld` on every record** · 2026-09-14 -->
<!-- witness: the answer's own `pageResults.available` — printed beside every walk («236 emitted, the site states 236 (the page's own elasticJobs query, `available`) — equal»); a page whose script no longer carries the query exits 6, an answer without `available` exits 6 — a changed page, never an empty market · 2026-09-14 -->

**Eezy is a large Finnish staffing group — 236 advertisements stated on the
day, hospitality, metal, retail and construction first, Uusimaa on 151 rows;
the client named on 77 and hidden by the site on 159.** Issue #379. Measured
2026-09-14 04:0x–04:1x UTC by the declared client, the guard on the exact
path before each request, two seconds apart per host.

## Where the list is, and what the sitemaps are

```
eezy.fi/robots.txt                        200 — User-Agent: *, Disallow: (empty); Sitemap sitemap_index.xml, tyopaikat-sitemap.xml
eezy.fi/tyopaikat-sitemap.xml             200, 81 930 B — 782 rows tyopaikat.eezy.fi/fi?job=…&location=… : facets, not ads
tyopaikat.eezy.fi/robots.txt              200 — Sitemap: https://tyopaikat.eezy.fi/sitemap.xml (nothing else)
tyopaikat.eezy.fi/sitemap.xml             200, 99 204 B — an RSS feed: 338 items, 10 ads (/fi/tyopaikat/<id>) and 328 location facets
GET tyopaikat.eezy.fi/fi                  200, 43 994 B — __NEXT_DATA__: fieldOfWorks, locations; the jobs are fetched on the client
GET /_next/static/chunks/pages/_app-<hash>.js   200, 514 225 B — the Apollo client and the elasticJobs query text
POST api.eezy.fi/api  {"query": <the page's text>, "variables": {"locations": [], "from": 0, "to": 20}}   200 — available 236, 20 jobs
POST api.eezy.fi/api  … "to": 236                                                                        200 — 236 jobs, 236 distinct
GET /fi/tyopaikat/<id>                    200, ~80 KB — __NEXT_DATA__.props.pageProps.jobAdvert
```

**The call is the page's own query, to the address the page's own client
names, with the page's own variables** — nothing is guessed. What is fragile
is the build: the script's name changes at every deploy, so the query is
read from the page's script each run, exactly as a browser would, and a
page whose script no longer carries `elasticJobs` exits 6 rather than
printing zero. The same form as StaffPoint's server action (`staffpoint.md`),
judged «a route the page calls» on 2026-09-14.

## The record, and what is withheld

The list row carries the site's own fields; the ad's `jobAdvert` adds the
type and mode, the town and the address, the dates, the description and the
ATS the site sends to (its host named, never followed). **The client's name
goes out only when the site shows it; `recruitmentPerson` is never emitted;
a line of the text that carried a telephone or an e-mail is withheld whole,
because on this board that line names the consultant.**

## Running it

```
python3 skills/job-scan/scripts/eezy.py list                 # 236 rows, 4 requests
python3 skills/job-scan/scripts/eezy.py list --limit 20
python3 skills/job-scan/scripts/eezy.py ad --url https://tyopaikat.eezy.fi/fi/tyopaikat/<id>
```

Exit codes: 0 all read · 3 the ad is gone · 6 the page no longer lists as it
did, or an answer without its count (a changed page, never an empty market)
· 7 a refused path. No key, no browser, no login.
