# Board adapter — d.vinci (an ATS, one tenant at a time): the tenant's list on `<tenant>.dvinci-easy.com/<lang>/jobs` carries every publication as JSON in the page (`DvinciData.jobPublications` — the list is the board), each ad the same object plus a JobPosting; `dvinci.py`, the addresses, coordinates and application routes never emitted

<!-- verified: 2026-09-21 -->

<!-- hosts: fi-ts-karriere.dvinci-easy.com, holzapfel-group.dvinci-easy.com, sicrystal.dvinci-easy.com, altmann.dvinci-easy.com -->
<!-- host-forms: {tenant}.dvinci-easy.com -->
<!-- host-forms-basis: read — `dvinci.py:98` (`host_of`: `--tenant` is REQUIRED, a subdomain, a host or an address on it, resolved to `<tenant>.dvinci-easy.com`; the vendor's own subdomains refused, `dvinci.py:66`; `request()` refuses any other host before the gate) · 2026-09-21 -->
<!-- script: dvinci.py -->
<!-- countries: * -->
<!-- content: measured · **three tenants with publications, one without, and an unknown name, 2026-09-21 07:14–07:16 UTC, the declared client, the guard on the exact path, two reads each. Rules: every tenant publishes `User-agent: * / Allow: /` and its sitemaps (155 B), no Crawl-delay. The list `/de/jobs` (200; FI-TS 108 082 B, Holzapfel 18 262 B, SICrystal 4 934 B — md5 moving between reads, a nonce) renders the tenant's own template around `var DvinciData = { "jobPublications": [...] }` — **FI-TS 46, Holzapfel 6, SICrystal 0** («Sie haben aktuell keine passende Stelle gefunden?»), Altmann `/en/jobs` 29 (the publications' own `language` is `de`); each publication: id, language, position, subtitle, pageDescription, jobPublicationURL, three application URLs (form, applyApi, WhatsApp), startDate, endDate, and `jobOpening` — name, reference, `location` (the tenant's label), `locations[]` (name, `country.isoA2`, latitude/longitude, `address` with street, zip, city), categories, targetGroups, workingTimes, contractPeriod, earliestEntryDate, orgUnit, company, department, salary, salaryRange, createdDate; no count stated anywhere, no JobPosting on the list. The ad `/de/jobs/71095/<slug>` (200 ×2, 24 705 B) carries `var DvinciData = { jobPublication: {...} }` (the key unquoted — a JavaScript literal, decoded from its value) and one JobPosting (description as HTML with inline styles, datePosted, hiringOrganization with a logo, jobLocation with street and postal code, employmentType `[]`); a Holzapfel ad (12 212 B) prints two telephones in its page text outside the posting. `zzz-not-a-tenant-2026.dvinci-easy.com`: the name does not resolve (no wildcard) — «not a tenant», exit 3. Exercised: `jobs --tenant fi-ts-karriere` → 46 emitted, 46 listed (1 request); `holzapfel-group --country-code AT` → 0 of 6, «6 carry no country» said; `sicrystal` → 0, not an error; the Holzapfel ad → the object and the posting's text** · 2026-09-21 -->
<!-- witness: none — the page's `jobPublications` list is the board; `dvinci.py jobs` prints its length beside the emitted count and says no count is stated anywhere · 2026-09-21 -->
<!-- route: http · 46 · 2026-09-21 -->

**Issue #481 (opened under #406, the ATS families). Measured 2026-09-21
07:14–07:16 UTC by the declared client, the guard on the exact path, on
four tenants named by the family's signature (`dvinci-easy.com` in a
search engine): FI-TS (46), Holzapfel Group (6), SICrystal (0), Altmann
(29 on `/en/jobs`).** Rank: the pilot's order of 2026-09-21 06:13 UTC —
#479 → #488 after the dated controls.

## What d.vinci is, and where its tenants live

d.vinci HR-Systeme (Hamburg) sells an applicant-tracking system; the
employer's career page is hosted on `<tenant>.dvinci-easy.com` (a tenant
may frame it under its own `jobs.<employer>` host — the same page). **The
user names the tenant** by its subdomain (`fi-ts-karriere`), its host, or
any address on it; `--lang` picks the list's language path (`de` by
default — the publications carry their own `language`).

## The route — the list's own JSON, one request

```
GET https://fi-ts-karriere.dvinci-easy.com/de/jobs            200 — var DvinciData = { "jobPublications": [46] }
GET https://sicrystal.dvinci-easy.com/de/jobs                 200 — "jobPublications": [] → «0 publications», not an error
GET https://fi-ts-karriere.dvinci-easy.com/de/jobs/71095/…    200 — var DvinciData = { jobPublication: {…} } + one JobPosting (the `ad` command)
GET https://zzz-not-a-tenant-2026.dvinci-easy.com/de/jobs     the name does not resolve — not a tenant, exit 3
```

The page's own data literal is decoded from its value (`json.JSONDecoder
.raw_decode` after the key — quoted on the list, unquoted on the ad); no
API, no widget, no key. The adapter emits the ids once (a duplicated id is
one publication) and prints «N emitted, the N publications the page lists»;
`--country-code` keeps a publication with a location in that country
(`locations[].country.isoA2`, any of them) and says how many carry none.

## What the adapter emits, and withholds

`jobs --tenant <tenant> [--lang de] [--country-code ISO2]`: id, url, title
(`position`), subtitle, company (`company.name`), org_unit, reference,
location (the tenant's label), places (each location's city), country
(one code when the locations agree) and `countries`, categories,
target_groups, working_times, contract, earliest_entry, salary (as the
tenant states it), language, published (`startDate`, else `createdDate`),
expires. `ad --url`: the same record from the page's object, plus
description (the JobPosting's text, scrubbed) and the posting's
organisation when the object names no company.

**Withheld:** every location's `address` (street, zip — only its `city` is
read), `latitude` / `longitude`, `applicationFormURL`,
`applicationApplyApiURL`, `applicationApplyWhatsAppURL`, the logo; every
e-mail address and telephone in the description replaced by «[e-mail
withheld]» / «[telephone withheld]» — a date («ab 01.10.2026») is left
alone; `contacts_withheld` on every record; the application never touched.

## Tests and mutations

`AnATSWhoseListPageCarriesEveryPublicationAsJSONWithItsAddressesAndApplicationRoutes`,
both ways on fixtures (the list with a publication without a country, one
with two countries and a duplicated id; the country filter and its note;
the empty list; a page without the data; a language refused before any
request; the vendor's hosts and another host refused; a name that does
not resolve; the ad with its addresses, routes and logo, the wrong
publication on the page, the ad gone or changed). Mutation bench on a
detached copy, `python3 -B`, 9 / 9 red: the list regex broken · the
country filter dropped · the address emitted · the apply route emitted ·
the scrub dropped in the ad · the duplicate ids kept · the ad's id check
dropped · the vendor-host check dropped · the no-country note dropped.
