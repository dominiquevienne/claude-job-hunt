# Board adapter — Ostendis (a Swiss ATS, one tenant at a time): the employer's own page embeds the list by a «publication place» token, and the loader fills it by `odm.ostendis.com/ojp/data/<version>/jobs/<token>/<LANG>?domain=<site>` — replayed with the page's own values; each ad carries one JobPosting; `ostendis.py`, postal codes, streets and images never emitted

<!-- verified: 2026-09-21 -->

<!-- hosts: odm.ostendis.com, jobs.ostendis.com, link.ostendis.com -->
<!-- host-forms: odm.ostendis.com, {host} -->
<!-- host-forms-basis: read — `ostendis.py:64` names the data host as a literal; `tenant_of` (`ostendis.py:143`) takes the page that embeds the list (its host is the one the run reads and the `domain` the call carries) or a token with `--domain`; `request()` (`ostendis.py:98`) sends only to the hosts the run has named — the data host, the page's host, the ad's host — and refuses any other before the gate · 2026-09-21 -->
<!-- script: ostendis.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants with jobs and one ad, 2026-09-21 07:38–07:41 UTC, the declared client, the guard on the exact path, two reads each (identical bodies). Rules: `jobs.ostendis.com` and `odm.ostendis.com` answer no rules file (`robots.txt` 404 with an HTML page; `_robots.allowed` open, absent / unrecognised), the tenant's page host has its own (`www.mepersonal.ch` read, open); no Crawl-delay. The vendor has no hosted list: `www.ostendis.com/de/career/` embeds `<script src="https://odm.ostendis.com/ojp/assets/loader" data-token="7ha0m3iy…">` and `OSTENDISJOBS.embed("7ha0m3iy…", "DE", "#ostendisJobs", {})`; the loader (79 993 B) GETs `/ojp/assets/version/<token>` → `{"version":"v55"}` (17 B) and loads `/ojp/assets/v55/script` (33 967 B), which GETs `/ojp/data/v55/jobs/<token>/<LANG>?domain=<hostname>` → `{"jobs": [...], "error": {"message": ""}, "options", "translations"}` — **Ostendis AG 2 jobs (2 782 B), ME Personal (`www.mepersonal.ch/stellenangebote`, three publication places on one page: `blsr7vzf…` 4 jobs (3 754 B), `lcl6leao…`, `6ixx2td0…` — 10 distinct over the three, one listed twice)**; each job: id, reference, title, country, countrycode, city, zip, published, timestamp, type, position, workload with min/max, company, department, detail (the ad's address — on `jobs.ostendis.com` or the tenant's CNAME `jobs.mepersonal.ch`), action, image, text, startdate, language, langcode; no count stated anywhere. An unknown token: `/ojp/assets/version/` answers `{"version": null}` (200) — not a tenant, exit 3. The ad `link.ostendis.com/publication/initiativbewerbung/<64 chars>` (200 ×2, 25 972 B; 406 to an `Accept` without `*/*` or to an `Accept-Language` with spaces) carries one JobPosting — title, description HTML, datePosted, employmentType `["FULL_TIME", "OTHER"]`, hiringOrganization with a logo, jobLocation with streetAddress, postalCode, locality, region, addressCountry «CH», identifier — and the CVdropper link. Exercised: `jobs --tenant https://www.mepersonal.ch/stellenangebote` → 10 emitted over 3 places (5 requests); the bogus token → exit 3; the Lactalis ad → the posting, its street and postal code withheld** · 2026-09-21 -->
<!-- witness: none — no count is stated anywhere; `ostendis.py jobs` prints the jobs the lists carry beside the emitted count, and how many were listed twice across a page's places · 2026-09-21 -->
<!-- route: http · 10 · 2026-09-21 -->

**Issue #484 (opened under #406, the ATS families). Measured 2026-09-21
07:38–07:41 UTC by the declared client, the guard on the exact path, on
two tenants named from the vendor's own customer list and career page
(ME Personal, 10 over three places; Ostendis AG, 2) and one ad found by
the family's signature (`link.ostendis.com/publication/…`, Lactalis
Suisse).** Rank: the pilot's order of 2026-09-21 06:13 UTC — #479 → #488
after the dated controls.

## What Ostendis is, and where its tenants live

Ostendis AG (Boniswil) sells e-recruiting to Swiss SMEs, hotels, clinics
and municipalities. **There is no hosted career site**: the employer's own
page embeds the list with a loader script and a publication-place token,
and the ads live on `jobs.ostendis.com/publication/<slug>/<64 chars>`,
`link.ostendis.com/…`, or the tenant's own CNAME. **The user names the
tenant** by the page that embeds the list — the token(s), the language
and the `domain` the call carries are read from it — or by the token with
`--domain`.

## The route — the page's own calls, replayed

```
GET https://www.mepersonal.ch/stellenangebote                                       200 — data-token blsr7vzf…; OSTENDISJOBS.embed(…) ×3 (three places, "DE")
GET https://odm.ostendis.com/ojp/assets/version/blsr7vzf…                           200 — {"version":"v55"}
GET https://odm.ostendis.com/ojp/data/v55/jobs/blsr7vzf…/DE?domain=www.mepersonal.ch  200 — 4 jobs; then lcl6leao…, 6ixx2td0… — 10 distinct
GET https://link.ostendis.com/publication/initiativbewerbung/t1xhujc6…             200 — one JobPosting (the `ad` command)
GET https://odm.ostendis.com/ojp/assets/version/zzzz…                               200 — {"version":null}: not a tenant, exit 3
```

The token is the tenant's public publication place, printed in every
visitor's page — the same shape as SparkHire's careers token and BeeSite's
`gjbAddress` (the pilot's judgment of 2026-09-14): the plugin replays the
URL the page calls, with the values the page carries — the version from
the version call, the language from the embed call, the `domain` from the
page's host. One data call per place, ids emitted once. No count is stated
anywhere; the run says how many jobs the lists carry. `--country-code`
filters on the job's `countrycode` (every job carries one).

## What the adapter emits, and withholds

`jobs --tenant <page or token> [--domain HOST] [--lang XX] [--country-code
ISO2]`: id, url (`detail`), title, reference, company, department, place
(`city`), country and `country_name`, workload, type, position, start
(`startdate`), published (`timestamp`), language, `publication_place`.
`ad --url`: the page's JobPosting — title, company, reference, place,
region, country, employment_type, published, expires, description (text,
scrubbed).

**Withheld:** `zip` / `postalCode` and `streetAddress`; `image` and the
logo; every e-mail address and telephone in the texts replaced by «[e-mail
withheld]» / «[telephone withheld]» — a date («per 01.11.2026») is left
alone; `contacts_withheld` on every record; the application (the
CVdropper) never touched.

## Tests and mutations

`AnATSWhoseListIsEmbeddedOnTheEmployersOwnPageByATokenAndFilledByAVersionedDataCall`,
both ways on fixtures (a page with two places, the version then one data
call per place with the page's domain, a job listed twice, the country
filter, the empty list, the null version, a page without the loader, an
answer without `jobs` and one with an error message, a token without its
domain, an unnamed host refused; the ad with its street, postal code,
logo and contact, the ad's country filter, the ad gone or changed).
Mutation bench on a detached copy, `python3 -B`, 9 / 9 red: the embed
regex broken · the null-version branch dropped · the domain dropped from
the call · the zip emitted · the duplicate ids kept · the error message
ignored · the country filter dropped · the scrub dropped in the ad · the
street emitted.
