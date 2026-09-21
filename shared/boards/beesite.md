# Board adapter — BeeSite (milch & zucker; an ATS, one tenant at a time): the employer's «Karriereportal» names its search API in `/script/gjb_scripts.js`, and its list page fills itself by `<api>search/?data=<JSON>` — replayed with the page's own parameters to the stated count; `beesite.py`, the ad's contact block and street never emitted

<!-- verified: 2026-09-21 -->

<!-- hosts: karriere.johanniter.de, jobs.lvr.de -->
<!-- host-forms: {host}, {tenant}.beesite.de -->
<!-- host-forms-basis: read — `beesite.py:139` (`tenant_of`: `--tenant` is REQUIRED, the host the user names, and `request()` refuses any other host before the gate); the API host is whatever that host's `gjb_scripts.js` names, accepted only under `.beesite.de` (`beesite.py:68`) · 2026-09-21 -->
<!-- script: beesite.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants with positions and one former tenant, 2026-09-21 06:52–06:56 UTC, the declared client, the guard on each path, two reads each. Rules: `karriere.johanniter.de` no robots.txt (404 — absent, open), `jobs.lvr.de` read, `*` open on `/index.php` and `/script/`, the API hosts absent; no Crawl-delay anywhere. The list page `/index.php?ac=search_result` (200; 32 886 B Johanniter, 81 863 B LVR) holds no position — «Suchergebnis : 0 Treffer … Bitte warten» — and loads milch & zucker's `global-jobboard-client`; `/script/gjb_scripts.js` (200, ~1.4 KB) ends with `var gjbAddress = "https://api02-johanniter.beesite.de/"` (LVR: `https://lvr-beesite-gjb.app.beesite.de/`); the client GETs `<gjbAddress>search/?data=<JSON>` (`LanguageCode`, `SearchParameters` {FirstItem, CountItem, Sort, MatchedObjectDescriptor}, `SearchCriteria` []), the field list from `/assets/js/jobboard.config.json`. The API answers `SearchResult.SearchResultCountAll` — **Johanniter 1 272, LVR 320** — and items with ID, PositionTitle, PositionURI (`index.php?ac=jobad&id=<n>`), PositionLocation (CountryCode DE, CountryName, CountrySubDivisionName, CityName), JobCategory, CareerLevel, PositionIndustry, PositionSchedule, PositionOfferingType, ParentOrganizationName, PublicationStartDate, PublicationEndDate; a 100-item page is accepted (LVR page 4 → 20 items). The ad page (200; 95 373 B LVR, 135 514 B Johanniter) carries one JobPosting (description HTML-escaped, datePosted, validThrough, employmentType, hiringOrganization, jobLocation with streetAddress and postalCode, identifier `J0000<id>`) and a `job-ad-contact` block (a name, a telephone). `jobs.pwc.de`: 404 on the script and on `?ac=search_result` — a former tenant, «not a tenant» (exit 3). `karriere.klinikum.uni-heidelberg.de`: CERTIFICATE_VERIFY_FAILED to the client (the leaf without its intermediate — the `_tls` shape), not measured. Exercised: `jobs --tenant jobs.lvr.de` → 320 emitted, states 320 (5 requests); Johanniter `--max-pages 1` → 100 of 1 272; `--country-code AT` → 0 of 100 read, said so** · 2026-09-21 -->
<!-- witness: the API's own `SearchResultCountAll` (1 272 Johanniter, 320 LVR), printed beside the emitted count on every run · 2026-09-21 -->
<!-- route: http · 320 · 2026-09-21 -->

**Issue #479 (opened under #406, the ATS families). Measured 2026-09-21
06:52–06:56 UTC by the declared client, the guard on the exact path, on
three hosts named by the family's signature (`index.php?ac=jobad&id=` in a
search engine, never composed): Die Johanniter (1 272), Landschaftsverband
Rheinland (320), PwC Germany (a former tenant, 404).** Rank: the pilot's
order of 2026-09-21 06:13 UTC — #479 → #488 after the dated controls.

## What BeeSite is, and where its tenants live

BeeSite Recruiting is milch & zucker's applicant management system, the
software behind a German employer's «Karriereportal» — large accounts,
hospitals, welfare organisations, public bodies. The portal lives on the
employer's own host (`karriere.johanniter.de`, `jobs.lvr.de`,
`karriere.klinikum.uni-heidelberg.de`); its signature is the PHP front:
`index.php?ac=search_result` (the list), `index.php?ac=jobad&id=<n>` (an
ad), `index.php?ac=application&jobad_id=<n>` (the application — never
touched). **The user names the tenant by its careers host.**

## The route — the page's own call, replayed

```
GET https://jobs.lvr.de/script/gjb_scripts.js                              200 — var gjbAddress = "https://lvr-beesite-gjb.app.beesite.de/"
GET https://lvr-beesite-gjb.app.beesite.de/search/?data={"LanguageCode":"DE","SearchParameters":{"FirstItem":1,"CountItem":100,"Sort":[{"Criterion":"PublicationStartDate","Direction":"DESC"}],"MatchedObjectDescriptor":[…]},"SearchCriteria":[]}
                                                                            200 — SearchResultCountAll 320, 100 items; FirstItem 101, 201, 301 → the rest (20 on the last)
GET https://jobs.lvr.de/index.php?ac=jobad&id=20817                         200 — one JobPosting (the `ad` command)
GET https://jobs.pwc.de/script/gjb_scripts.js                              404 — not a tenant (today), exit 3
```

The API address is the tenant's, printed in every visitor's script — the
same shape as SparkHire's careers token (the pilot's judgment of
2026-09-14): the plugin replays the URL the page calls, with the
parameters the page carries. The adapter asks 100 an item (the client asks
10 for its table and 10 000 for its map) and walks `FirstItem` to the
stated count; a page that repeats the previous page's ids ends the walk
(exit 6); an address outside `beesite.de` is refused before any request
(exit 7); the API's `PositionLocation.Latitude` / `Longitude` /
`StreetName` / `PostalCode`, which the page's client asks for, are not
asked.

## What the adapter emits, and withholds

`jobs --tenant <host> [--country-code ISO2] [--max-pages N]`: id, url,
title, company (`ParentOrganizationName`), place, region, country
(`CountryCode`) and `country_name`, category, career_level, industry,
schedule, contract (`PositionOfferingType`), published, expires;
«N emitted, the API states M» on every run, «— K short» when the walk
stopped early. `ad --url`: the page's JobPosting — title, company, place,
region, country, employment_type, published, expires, reference
(`J0000<id>`), description (text, scrubbed).

**Withheld:** the `job-ad-contact` block (a name and a telephone) never
read into a record; the JobPosting's `streetAddress` and `postalCode`
never emitted; every e-mail address and telephone in the text replaced by
«[e-mail withheld]» / «[telephone withheld]» — a date («ab 15.11.2026»)
is left alone; `contacts_withheld` on every record; the application
never touched.

## Tests and mutations

`AnATSWhoseTenantScriptNamesItsSearchAPIAndWhoseAdsCarryAContactBlock`,
both ways on fixtures (the script, the two-page walk with the stated
count, the country filter and the case without a code, the empty tenant,
`--max-pages`, the repeating page, the non-tenant, a script without the
address, an address outside the vendor, another host refused, the ad with
its street and contact block, the ad gone or changed, the list without
its stated count). Mutation bench on a detached copy, `python3 -B`, 9 / 9
red: the address regex broken · the vendor-domain check dropped · the
repeat check dropped · the country filter dropped · the scrub dropped in
the ad · the date exception dropped · the street emitted · another host
sent · the stated count not checked.
