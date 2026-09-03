# Board adapters

`job-scan` is board-agnostic: it owns the scoring, the ledger and the reporting,
and each adapter owns one site. Sixty-seven ship today, each verified against
the live site — count the rows below rather than trusting this sentence, which
has gone stale before.

## Which boards are available

| Board | File | Status |
| :-- | :-- | :-- |
| HiringCafe | `hiringcafe.md` | **Shipped.** Worldwide meta-board over ~40 ATS. Search sweep and description reading, **with no browser and no login** — plain HTTP. No apply flow to support: every ad links to the employer's own ATS |
| job-room.ch | `job-room.md` | **Shipped.** Switzerland's public employment service portal (SECO). Public REST API — **no browser, no login**. Reaches the Swiss SMEs and foundations HiringCafe misses; heavily overlaps jobup, and says exactly which row each duplicate is |
| Greenhouse | `greenhouse.md` | **Shipped.** One employer at a time, by tenant token. Public JSON, **no browser**. Targeting, not discovery |
| Lever | `lever.md` | **Shipped.** Same family. Two disjoint hosts (US / EU) — the wrong one looks exactly like a missing employer |
| Ashby | `ashby.md` | **Shipped.** Same family. Multi-city postings hide their other locations in `secondaryLocations` |
| Solique | `solique.md` | **Shipped.** One employer at a time, by tenant. **No browser.** Three different architectures behind one host — two JSON routes and a truncatable HTML one; the adapter says which answered and how complete it was |
| SAP SuccessFactors | `successfactors.md` | **Shipped.** One employer at a time, by host. Public JSON, **no browser** — the client-rendered `/search/` page is backed by an endpoint that answers unauthenticated. A locale the tenant does not publish empties the board **with no error** |
| SmartRecruiters | `smartrecruiters.md` | **Shipped.** Same family, and the one `ats.py resolve` used to name and then stop at. The only one where a wrong tenant is **indistinguishable** from an employer with nothing open |
| Workable | `workable.md` | **Shipped.** Same family, by tenant. **No browser.** One request returns the employer's whole board *with descriptions*. Publishes the residency rule behind a remote ad — `remote` alone is a trap — and distinguishes `published_on` from `created_at`, which aggregators confuse |
| Teamtailor | `teamtailor.md` | **Shipped.** Same family, by tenant. **No browser.** Whole board in one JSON Feed request, descriptions included. Publishes the employer's **full postal address** — the field a PRE misses most — but no salary, contract type or expiry. Read `<tenant>.teamtailor.com`: the employer's own `careers.` host is a **stale mirror** |
| SwissDevJobs | `swissdevjobs.md` | **Shipped.** A real multi-employer board, **no browser**. Whole board in one request. **A salary on 169 of 170 ads** — the only board here where the money is known before applying — and coordinates on 170 of 170, so `--near` filters by real distance. Carries **no description**, and is overwhelmingly German-speaking Switzerland: 2 of 170 ads in Suisse romande |
| Free-Work | `freework.md` | **Shipped.** French IT, permanent **and** contract, **no browser**. Public JSON API; `robots.txt` allows it explicitly. The only board here carrying a **contractor day rate**, and one of the very few with a real **`expiredAt`**. Three traps documented: `searchKeywords` is the only keyword parameter that filters, the page number never runs out, and the numeric id 404s — the slug is the key |
| FHF Emploi | `fhf.md` | **Shipped.** France's public hospitals and medico-social sector — CHUs, EHPADs, USLDs — **no browser, no account, no key**. The employer is always the hospital itself. **A full postal address on 36 of 36 sampled ads**, the field a PRE misses most, and a named contact on half. Its first page was served **four days stale from the edge cache**, announcing 345 ads more than the board held, so every request carries a cache-buster. The site's own `department[]` and `contract[]` field names return an empty board as GET parameters; the scalars work. Also a **listing for Beetween and a tenant directory for Softy**: 17 of 36 ads link out to an ATS, with the employer named here and anonymous there |
| JOIN | `join.md` | **Shipped.** One employer at a time, by tenant. **No browser, no account, no key** — but no JSON feed either: it is a Next.js app and the whole payload rides in the page's own `__NEXT_DATA__`. **The largest ATS family in Switzerland** — 108 of 223 HiringCafe cards, ahead of Workday. The only provider here that hands the description over **already split into `intro` / `tasks` / `requirements` / `benefits`**, and the only one whose money is in **minor units**: `2035` means `20.35`, an error that reads like a monthly salary. `showSalary` is true on 15 of 22 ads and an amount is present on 1. An ad carries **two numbers and both address it**; the stable one is the ledger key. **No search exists** — `/jobs` is a login and the declared job sitemap answers 403 |
| Workday | `workday.md` | **Shipped.** One employer at a time, by host + tenant + site. Public JSON, **no browser**. Where the large Swiss employers are |
| Haufe / Abacus umantis | `umantis.md` | **Shipped.** One employer at a time, by host. Public HTML, **no browser**. The Swiss SMEs, communes, clinics and institutes **HiringCafe does not index at all**. No tenant resolution exists — the user supplies the careers URL |
| LinkedIn | `linkedin.md` | **Shipped.** Search sweep, description reading, assisted Easy Apply |
| jobup.ch | `jobup.md` | **Shipped.** Search sweep and description reading, and **no browser needed for either** — the file said otherwise until 2026-09-02, which left users without the extension with no Swiss sweep at all. Listing and ads answer plain `curl`; every ad carries a `JobPosting` in `ld+json` and the listing carries a full JSON record per card, city and coordinates included. **`baseSalary` is a shell with no amount**, and the ad page's `addressLocality` is empty — read the value, and take the geography from the listing. No login needed to scan; the in-site apply flow is *not* supported |
| randstad.ch | `randstad.md` | **Shipped.** A staffing **agency** board, **no browser**, 985 ads over 33 pages. Pagination is a **path segment** (`/jobs/page-2/`), and past the last page it silently repeats page 1 — the stop condition is that repeat |
| persigo.ch | `persigo.md` | **Shipped.** A staffing **agency** board, **no browser**, whole board (890 ads) in one request. **No `validThrough` and no date on the listing**, and it keeps ads for over a year — freshness needs `--with-detail` |
| sozialinfo.ch | `sozialinfo.md` | **Shipped.** Switzerland's social-sector portal — a genuine multi-employer board, **no browser**, whole board in one request. **The only board here that names the employer**, so the ledger's employer dedup works on it |
| fachkraft.ch | `fachkraft.md` | **Shipped.** A staffing **agency** board — the whole listing in one request (~3 500 ads), **no browser**. The umbrella for sta.jobs and stellenpartner.ch, whose numeric ids are disjoint from its own; the `<n>-STAxx` / `-SPxxx` reference is the only key that crosses |
| Michael Page | `michaelpage.md` | **Shipped.** A recruitment **agency** board — one search across many employers, country-scoped, **no browser**. The employer is described and **never named**, so no dedup key crosses to their own ATS |
| jobs.ch | `jobs-ch.md` | **Shipped.** jobup's German-language sibling on the same platform — **and the same ad ids**, so an ad on both boards is one row, matched by UUID. **No browser needed**, same measurement and same two traps as jobup. Three times the national volume, thinner in Romandie: it does not replace jobup |
| Indeed | `indeed.md` | **Shipped.** Search sweep and description reading, country-scoped. **Serves anti-bot challenges** — the user solves them, never the plugin |
| France Travail | `france-travail.md` | **Shipped.** France's public employment service (ex-Pôle emploi) — **no browser**, but the only adapter here that needs an API key, free from francetravail.io. A search that does not name `origineOffre` returns France Travail's own ads and **silently omits the partner ads that are 77% of the board**, finishing early enough to look complete — so the sweep runs both passes |
| Meteojob | `meteojob.md` | **Shipped.** French generalist board, **no browser, no account**. Its robots.txt opens exactly one door — `Allow: /jobs?*` against a blanket `Disallow: /*?` — and pages 2+ live behind the disallowed API, so **one search is 20 ads and there is no second page**: a targeted probe, not a sweep. Names the employer on every ad, unlike its France Travail feed |
| HelloWork | `hellowork.md` | **Shipped.** France's largest private generalist board — the SMEs and the regions. **No browser, no account.** The most restrictive robots.txt here: `Disallow: /*?` with **no** search carve-out, and the sitemap it advertises answers 403. What is open is its path-based facet system, so coverage is a **facet list** — `facets` enumerates the ones each sector publishes. Richest `JobPosting` of any board: skills as a list, experience in months, a real remote flag |
| APEC | `apec.md` | **Shipped.** France's executive employment agency — 77 023 ads, **no browser, no key, no cookie**. The only French board here with **no pagination ceiling**: `startIndex` walked to 76 900 and still returned disjoint ads. But `texteOffre` is a fixed 283-character teaser and the detail endpoint sits behind a DataDome captcha, so it is **triage, not ad text** — with a salary on every single ad, which no other board manages |
| Cadremploi | `cadremploi.md` | **Shipped — browser only.** The other French cadre board. Cloudflare answers **403 to every scripted request, `robots.txt` included**, so there is no script and cannot be one; it runs in the user's own Chrome like `linkedin.md`. Its location parameter has a decoy that is accepted and ignored, and its card list drifts out of the search area with nothing marking where |
| Figaro Emploi | `figaro-emploi.md` | **Shipped — browser only.** Large French generalist, **244 815 ads**; `keljob.com` redirects here and answers `410` on its retired paths. Cloudflare answers **403 to every scripted request, `robots.txt` included** — same edge as `cadremploi.md`, same group. Sweeps the **allowed browse hierarchy** (`/d/fr-69/m/<metier>`, 28 855 of them) and never `/recherche/offres-emploi` or `/services/search/jobs`, both of which robots.txt closes. Counts are exact — no cap. Its JSON-LD is **emptier than its HTML**: hollow `baseSalary`, and CDI and CDD both arrive as `FULL_TIME` |
| Jobology | `jobology.md` | **Shipped.** One contract, **nine French sector boards** — Distrijob, Jobvitae, Jobtransport, Clicandtour, Clicandpower, Clicandsea, Clicandsport, Clicandearth, Supply-Chain — **72 667 ads**, **no browser**. Browses by path because the `robots.txt` closes the facet parameters. Its pagination **never ends**: page 9999 answers with twenty on-topic ads, and the same URL answers differently twice, so the sweep needs two bounds at once. A wrong slug is an empty board with no error |
| Batiactu | `batiactu.md` | **Shipped.** French BTP — **9 984 ads**, a sector with no other coverage here. **No browser.** Browses by path because the `robots.txt` closes the search page. Publishes **coordinates on every ad**, and its pagination is exact and terminates — rare enough to note. But **the region filter matches the employer's name, not the job's address**: a third of the Île-de-France page was 300 km away, so the adapter filters on the postcode afterwards. `streetAddress` is the employer's head office, repeated across twenty communes |
| ANEFA | `anefa.md` | **Shipped.** French agricultural and seasonal work — **2 818 ads** the generalists do not gather. **No browser**, and **no `robots.txt` at all**. Carries `Hébergement possible` and `Repas sur place` on every ad, which no other board here has. **No employer field exists** — the farm is prose, so `company` is null by design. Its department parameter is an **ordinal, not the number**: Corsica takes two slots, so `29` returns the Eure-et-Loir; the map is read from the site's own select every run |
| Welcome to the Jungle | `wttj.md` | **Shipped — cut in two.** **88 222 ads**, two thirds French-language. Discovery is `wttj.py`, plain HTTP on the sitemap `robots.txt` advertises, with a **real per-ad `lastmod`** — 7 691 distinct values in 10 000 — so `--since` narrows a re-scan properly. Reading needs the user's Chrome: every HTML page answers **`202` + `x-amzn-waf-action: challenge`**, a 2xx with no ad in it, and slowing to one request per 12 s does not help. **In-page `fetch()` is not the Figaro shortcut** — it works twice then challenges; navigation is what holds. Publishes `hiringOrganization.sameAs`, the employer's own site, which nothing else here does |
| Adecco France | `adecco.md` | **Shipped.** **13 293 French ads**, from the country sitemap `robots.txt` declares — the country is in the *file name*, the cleanest geography here. **No browser.** Salary on 11 of 17, full descriptions, and a retired ad answers an honest **410 Gone**. But the employer is `adecco` on every ad, `postalCode` is empty on every ad, `currency` holds **"France "**, `employmentType` is French text or the string `"null"`, and the department in the URL is truncated — `loire` ends 1 065 ads spanning six departments, so `--region` reads it off the ad and costs a fetch |
| Randstad France | `randstad-fr.md` | **Shipped.** **6 755 ads**, from the three job-detail sitemaps `robots.txt` declares. **No browser.** Better than its sibling on every axis: postcode on every ad, the town in the URL matches the ad 22 of 22 so `--ville` is free, `EUR`, `CONTRACTOR`, and **no `validThrough` at all** rather than a formula. Its `ld+json` tag uses **single quotes** — a double-quote pattern reports `json_ld: false` on every ad, so the adapter errors when a page says `JobPosting` and none parses. Employer is the agency, as ever |
| Crit | `crit.md` | **Shipped.** **16 175 ads**, the largest French interim board here. **No browser.** Best salary data of any French board — a **min and a max in euros on every ad** — and the best `lastmod` ratio in the repo, 13 893 distinct in 16 175. **Half the ad is outside the JSON-LD**: *Profil recherché* is a sibling DOM section, anchored on the heading text because the MUI classes are build hashes. `addressCountry` is `"France"`, not `FR`; `employmentType` is `OTHER` on 14 of 20; URLs are UUIDs so `--since` is the only free narrowing |
| Hays France | `hays-fr.md` | **Shipped.** **3 193 ads** of qualified profiles — a different population from the interim networks. **No browser.** Thinnest of the five agency boards: `postalCode` is the literal string **`"NA"`** on 22 of 22, a salary figure on 5 of 22, and `addressLocality` == `addressRegion` holding a town *or* a department *or* a region. Two lessons outlive it: its sitemap wraps `<loc>` in **CDATA**, so the usual pattern returns **0 of 3 193** from a valid 2.37 MB file; and its pay sits in `baseSalary.value.value` as prose, where the previous four boards use `minValue`/`maxValue` |
| Taleez | `taleez.md` | **Shipped.** A French ATS for SMEs and ETI — the counterpart of `umantis` on the French side, and the family `README` called the biggest blind spot left. **No browser, no key**: one unauthenticated request returns a tenant's whole careers site, 412 ads for one of them. **No tenant directory exists**, so the user supplies the careers URL. The listing carries no description at all |
| Flatchr | `flatchr.md` | **Shipped.** The other French SME/ETI ATS, next to Taleez. **No browser, no key**, and **one request per employer is the whole sweep**: the careers site is Next.js and the job list is server-rendered with the descriptions in it — 55 fields per ad, the richest listing here. No tenant directory; its sitemap is the marketing site's and carries zero vacancies |
| Softy | `softy.md` | **Shipped — browser only, by choice.** The third French SME/ETI ATS, after Taleez and Flatchr. Its robots.txt allows `*` everything and then **disallows the AI agents by name, Anthropic's twice** — so the sweep runs in the user's own Chrome rather than as a script. An ad can span seven towns and the page shows one: the rest live in a tooltip that only a **real hover** opens |
| DigitalRecruiters | `digitalrecruiters.md` | **Shipped.** The Cegid-owned ATS of French retail and franchise networks — **948 ads on the tenant sampled**, the most per employer here. **No browser, no key.** Careers sites are white-labelled on the employer's own domain, so the tenant key is the hostname and no directory exists. `job_ad_id` is **not unique** — one posting across five towns shares it — so the ledger keys on the composite id |
| Cegid Talentsoft | `talentsoft.md` | **Shipped**, verified on two tenants. The last of the five French ATS — and **`choisirleservicepublic.gouv.fr` is one of them** (`place-ep-recrute`, 51 708 posts), so the state portal needs no board of its own. The listing's fields mean different things per tenant, so the parser labels only what it can identify and hands the rest back unnamed — ministries, airports, energy, large agencies. **No browser, no key.** Server-rendered ASP.NET with no JSON and no JSON-LD, but the ad pages carry Talentsoft's **field model as element ids**, which outlive any restyling. A **full street address on the listing**, and a location rule that must not assume a French postcode |
| Emploi Territorial | `emploi-territorial.md` | **Shipped.** France's **territorial** civil service — communes, departments, regions, CCAS. 26 613 posts, carried by no private board. **No browser, no key.** Search is a *session*, not a URL: the filter is POSTed once and the server remembers it. Publishes a **real closing date**, unlike the boards that print `datePosted` plus a constant |
| La Bonne Alternance | `labonnealternance.md` | **Shipped.** French state API for **apprenticeship**. **No browser**, one free self-service key. Returns posted ads *and* **companies that take apprentices without advertising** — 150 of them in the Rhône, which no other board here carries. A **sandbox key hands out staging apply URLs**, and the department code takes exactly two characters: `069`, `1` and `075` each fail differently and silently |
| Empléate (SEPE, Spain) | `empleate.md` | **Shipped.** **28 099 live ads** — the first Spanish board here, and the third public employment service after job-room and France Travail. **No browser, no key**, and the cheapest board in the repo per ad: one request returns **100 complete ads, full text included**. Three silent failures, all HTTP 200: **omit `fq` and it returns 131 510 ads, 103 411 of them dead**; `FAIL!` is a five-byte non-JSON body served as `application/json`; `rows` is capped at 100 without saying so. `url:"#"` matches all 28 099. **29% of its live ads are over a year old**, so `--desde` is correctness, not tuning. Salary in two comma notations at once. Carries 2 436 **Tecnoempleo** ads — the board `robots-policy.md` closed the door on — so the ad URL emitted is never the partner's |
| Oposiciones (Empléate, public sector) | `oposiciones.md` | **Shipped.** **1 558 live announcements** of Spanish public-sector recruitment — the sibling index to `empleate.md`, and a different board. **No browser, no key.** Its `estadoPlazoF` reads **"Abierto" on all 76 050 records**, including **498 live ones whose deadline has already passed**, so the state is computed from the date and never read from the field. Its endpoint **injects no live filter**, unlike its sibling — so `empleate.md`'s base clause `checkVisible:1` returns **0** here, and no filter at all returns 76 050, 98% dead. `--provincia MADRID` returns **42 jobs, none of them in Madrid**. No ad text (median 118 characters), so `cover-letter` has nothing to read; Catalan in practice, 1 334 of 1 558 from CIDO |
| Infoempleo | `infoempleo.md` | **Shipped.** **7 621 active ads**, Spain's generalist private board and the first Spanish adapter here that is not a public register. **No browser, no key.** Geography is **free** — 1 201 places in the URL. Its trap is the most dangerous in the repo because it is **intermittent**: the site answers `Content-Encoding: deflate` **unsolicited on a fraction of requests**, so an undecompressed body reads as *an ad page with no structured data* — 200, right content type, no exception. Measured raw it reported 5 of 45 ads as dataless; decompressed, 44 of 45 carry a JobPosting. Also **`baseSalary.value.value` is `0.0` on every salaried ad**, the exact inverse of `hays-fr.md` — read the object, not last board's sub-field. `robots.txt` declares a sitemap that is 0 bytes. Employer named on every ad but 32 of 44 are ETTs, and 60 ads carried just 23 employers |
| Turijobs | `turijobs.md` | **Shipped.** **2 863 active ads** in Spanish tourism and hospitality — the first sector board of the Spanish series, and the chains post here directly. **No browser, no key.** Two free filters, place *and* date (2 506 distinct `lastmod` in 2 863). **The only board here that publishes how many people already applied** — median 10, up to 156 — and it carries a real postcode on 38 of 40 where `infoempleo.md` and `hays-fr.md` have none. Its salary field reads three ways: the object is present on 40 of 40, `salaryVisible` is true on 27, **a figure exists on 2**. `company.name` **does not exist** — the employer is in `brandName`, filled on 35 of 35. No JSON-LD: the ad is in `__NEXT_DATA__`, 6 KB inside a 706 KB page, and a JSON-LD reader scores 0 of 25. 10 of 40 ads are outside Spain |
| Bundesagentur für Arbeit | `arbeitsagentur.md` | **Shipped.** **994 348 live ads** — Germany's federal employment service, the fourth national public service here and **the first German adapter**. Thirty-five times the largest board this repo had. **No browser, no account**, and the key is printed in the state's own OpenAPI spec on `bund.dev`. **But you cannot read it**: the API returns at most **10 000 ads per query** (`page=101` → 400) while reporting the true match count, so Berlin answers *45 901* and delivers 10 000. The adapter checks every count against that ceiling **before paging** and refuses a query it cannot deliver whole. `berufsfeld=Informatik` is 10 002 — it looks like it fits. Carries what no other board does: **`istArbeitnehmerUeberlassung`**, the employer's own legally-required declaration that the work is temp-agency, plus the syndication channel and a career-changer flag. Salary figures are **hourly** on most ads that state one |
| JobsIreland | `jobsireland.md` | **Shipped.** **4 934 live ads** — Ireland's public employment service (DSP), the **fifth national public service** here and the first Irish adapter. **No browser, no key**, and a `robots.txt` with **no `Disallow` at all**. **More than half the board is not a job**: 135 of the 250 newest are Community Employment Scheme placements, 106 ordinary vacancies, 9 WPEP — a distinction that lives only in a CSS class and a reference prefix, so the card carries `offer_kind` and every run prints the split. Its trap outlives it: **the card class changes with the ad type**, so anchoring on the first variant returns 136 of 251 cards, all correctly parsed and 135 of them CES — a full-looking result set of the wrong population. Some responses also carry an **uninterpolated template row** whose fields are the literal `#StartDate`. Eircode on 195 of 251 |
| Platsbanken | `platsbanken.md` | **Shipped.** **39 865 ads offering 67 109 posts** — Arbetsförmedlingen, Sweden's public employment service, through the JobTech Dev open API. Sixth national public service here, first Swedish adapter. **No browser, no account, and no key at all** — an open-data product of the state. **The richest record in the repository**: a full description, an application deadline on 300 of 300, coordinates, and **`organization_number`, a legal company identifier no other board publishes** — the cross-board dedup key the ledger has never had. Two honesty points: the salary states its **type** on 300 of 300 and its **amount on 0 of 300**; and the structured `must_have` requirement schema, which nothing else here has, is filled on well under a fifth of ads. **The window is 2 100 of 39 865** — a place alone overflows, a field alone overflows, it takes two — but unlike Germany it refuses with a 400 instead of truncating |
| Personio | `personio.md` | **Shipped.** One employer at a time, by tenant — **the DACH ATS**, and the one most German, Austrian and **Swiss** SMEs run their careers page on. **No browser, no account, no key**, and no window: one request returns the whole board with descriptions **already split into the employer's own named sections**. Its trap is the sharpest of its kind: **`?language=fr` returns the same 7 positions with the same ids and 0 of them carrying any text** — same count, HTTP 200, valid XML, no error — so the adapter fetches both feeds and refuses a language whose text has gone. `<value>` is CDATA-wrapped, a second independent sighting of issue #55's wrapper in a new element. `additionalOffices` is a sibling element on 2 of 7. No salary, no closing date, and **no tenant directory** — ask for the URL |
| Recruitee | `recruitee.md` | **Shipped.** One employer at a time, by tenant — a European ATS (NL, BE, DE, PL). **No browser, no account, no key**, and one request returns the whole board with descriptions; 145 offers in 454 KB on the largest tenant measured. **A real salary figure on 133 of 238** — better than every national board here except SwissDevJobs — but `period` is **`month`** on 124 of them, so a figure read as annual is wrong by twelve. Two traps that generalise: **`country` is written in the tenant's own language** and the values mix inside one sweep (*Nederland*, *Duitsland*, *Switzerland*), so only `country_code` is a key; and **`remote`/`hybrid`/`on_site` are three overlapping booleans**, not an enum — treating them as exclusive misclassifies 51 of 238. `requirements` is a separate field from the description. `close_at` exists and is set on 0 of 238 |
| Pinpoint | `pinpoint.md` | **Shipped.** One employer at a time, by tenant — **the 5th most common ATS in a 360-card HiringCafe sample**, ahead of ADP and Taleo. **No browser, no account, no key.** Its trap is a pair of endpoints: `postings.json` (publications) and `jobs.json` (requisitions) have **disjoint id spaces**, and on one tenant both return 281 — equal counts that would convince anyone they are two views of one list. Fifteen requisitions in 684 postings are published more than once. `province` holds *London*, *United Kingdom*, *Maharashtra*, *Bolton* and *uk* in one field. **Where it gets things right, and few do**: `compensation_visible` actually tracks the figure (337 flags, 333 amounts), and `workplace_type` is a real enum where `recruitee.md` has overlapping booleans. `key_responsibilities` is a separate field on **684 of 684** |
| Oracle Recruiting Cloud | `oraclecloud.md` | **Shipped.** One employer at a time, by host — **the biggest ATS family the repo did not cover**: 164 cards of 2 838 across twelve countries, and one of four families present in *all twelve*. **No browser, no account, no key**, and the whole board is reachable — no window. Four traps: without `expand=requisitionList` it reports **1 428 jobs and returns none**, in valid JSON with a 200; **`siteNumber` does nothing** and a bogus value returns the same board as the right one; the field named **`Distance` is the posting date** in milliseconds, identical on 100 of 100; and the ad URL is built from `SiteURLName`, not `SiteNumber` — while the first site listed can be the INACTIVE one. `ShortDescriptionStr` repeats the title on 88 of 100; the real text needs the details resource, one request per job |
| StepStone | `stepstone.md` | **Shipped.** **One platform, eleven domains, six inventories, six countries** — Totaljobs, Jobsite, Caterer, IrishJobs, NIJobs, Jobs.ie and StepStone DE/AT/BE/NL run the same bundle, the same card contract and the same ad schema, told apart by `siteId` alone. **No browser, no account, no key.** Its headline finding is a **result list padded with ads that do not match**: the page's own analytics payload splits the total into `main`, `semantic` and `regional`, and **stepstone.nl holds 1 literal match for *software developer* while serving a full page of 25 cards** — 497 of 607 on .be, 796 of 1 862 on a located Totaljobs search. Nothing in the markup marks them. **A request can also fail with no HTTP status at all** — `HTTP/2 INTERNAL_ERROR` cold, a read timeout after a burst — so the script speaks HTTP/1.1, warms the host, retries once and then declares the sweep truncated. Depth is a **per-site** robots ceiling, four different regimes; **CWJobs is not a board** (50 of 50 cards link to totaljobs.com); Jobsite hides its ad URLs behind a disallowed `/tp-out`, so the id is rebuilt from the card. Salary is a two-state absence: **not rendered at all on the four StepStone sites**, and on IrishJobs present but saying `€ Not Disclosed` on **73 of 100** cards. `validThrough` on 108 of 108 ads |
| MyCareersFuture | `mycareersfuture.md` | **Shipped.** **96 778 ads of 96 869 reachable — the whole corpus**, Singapore's national portal (SWDA). **No key, no cookie, no account, no browser**, and a `robots.txt` of 87 bytes with an **empty `Disallow:`**. Also **the most restrictive adapter here**: SWDA's terms forbid storing Website Content "in a retrieval system" and prohibit caching, so the card carries identifiers, URLs and scoring fields and **never the text of an ad** — `description_chars`, then read it at its URL. Its trap is a filter that lies by silence: **an unknown parameter *name* is accepted, ignored and answered 200** (`employmentType` singular returns the whole board, `employmentTypes` returns 71 850 of 97 091) while an unknown *value* is a loud 400 — `total == countWithoutFilters` is the only tell. **`Re-open` is a fifth of the board** and sits deep in a newest-first sort, so `status == "Open"` silently drops it. Salary on 997/997, all monthly; closing date on 997/997; **the employer named on ~5%**. The sitemap index declares six files, **two are 7 923-byte HTML skeletons named `.xml`** |
| Kalibrr | `kalibrr.md` | **Shipped.** **Two countries in one adapter** — 1 045 Indonesian and 778 Philippine ads. Public JSON, **no key, no cookie, no browser**; `robots.txt` is 59 bytes of `text/plain` closing two non-job paths. **A search that matches nothing is answered with somebody else's ads**: `country=Singapore` and `text=zzzzqqqq` both return **the same 818**, HTTP 200, full payload, and the only sign is the boolean `from_alternative`. **No country at all returns that same 818 — smaller than either market** — so the default is the fallback set, not the board; `--country` is required and a substituted response is refused, not scored. **Salary is converted to pesos and mislabelled**: Indonesian ads carry `salary_currency: "PHP"` with twelve-decimal floats, and only the older `/api` endpoint keeps `salary_currency_orig: "IDR"` — so the card emits `salary_php_min`, never `salary_min`. `salary_shown` is true on 88% while **20% carry a figure**. Employer named on 1 139/1 139 and a real closing date on 1 139/1 139 |
| JOBBKK | `jobbkk.md` | **Shipped.** Thailand's largest board, **no key, no cookie, no browser** — `robots.txt` is 275 bytes of `text/plain` closing CVs, uploads and `/jobs/apply/`, and naming no AI agent. **The listing is the payload**: the Next.js flight data carries the whole record for all 25 cards, so one request buys 25 ads. Its trap is the end of results — **page 5 000 answers 200 with page 5's ads**, identical, for ever; there is no 404 and no empty list, so the sweep stops on repetition. The HTML of a page showing 25 ads also contains a hidden **'no position found'** message. `created_at` runs back to **2010** while `updated_at` is 2026 on 133 of 133 — read `refreshed`, not `created`. Salary is stated on **59%**, the best rate in this repository — but `salary_not_show` asks for 17 of them to be hidden and the payload sends them anyway, so **the adapter withholds those** |
| Adzuna | `adzuna.md` | **Shipped.** **One API, nineteen countries** — ch fr de at be nl it es pl gb us ca au nz in sg za br mx — and **the smallest budget here: 250 calls a day for everything together**, 25 a minute, with `results_per_page` **silently capped at 50**. Needs a free self-service key, read from `~/.adzuna.env` and the environment only. **The description is a 500-character teaser** by design, so this is discovery, not scoring: the text is at `redirect_url`, where the terms require the user to be sent. **`salary_is_predicted` means Adzuna's estimator wrote the figure, not the employer** — 6 of 16 salaried GB ads — so the card separates `salary_min_stated` from `salary_min_adzuna_estimate` and has no `salary_min` at all. Errors are **HTML, not JSON**: 400 with no key, 503 under load, the same page; bad keys are 401 where the spec says 410. Coverage is uneven by language — on Switzerland `Entwickler` returns 12 666 and `développeur` returns **0** |
| Computrabajo | `computrabajo.md` | **Shipped.** **Eighteen Latin American countries, one adapter** — and one `robots.txt`, **874 bytes, md5 identical on all eighteen with no exception**, the most uniform family measured here. **No key, no cookie, no browser**; Colombia alone carried 74 399 offers. The rule file **closes the filters and leaves the search open**: every disallowed listing rule names a query parameter — `sal=`, `pubdate=`, `cont=`, `dis=`, `by=` — while `q=` and `p=` are not among them, so the adapter searches and pages and **refuses to build the site's own filters**, quoting the rule. **No `JobPosting` anywhere** — the only `ld+json` is Computrabajo's own `Organization` graph — so it is DOM extraction on `article.box_offer[data-id]`. Employer named on 69 of 80, **salary on 0 of 80**, and every date is relative with no timestamp behind it. Pagination **ends honestly**. In Colombia the public API's origin URL carries this board's own 32-hex id on **484 of 484** measured entries, so the two join by string parsing with no request — the overlap's size is **not** established, since the corpus is grouped by operator (83.5% on the first pages, 0% on page 900). Enable one until the join is built |
| Jobstore | `jobstore.md` | **Shipped, hybrid.** 26 country sites on one host; Switzerland carries **52 128 ads**. **Discovery is plain HTTP, reading an ad needs the browser** — the ad page answers a plain client with 403 and a "Just a moment…" interstitial while the sitemaps and the search page answer 200. Its first trap is arithmetic: the sitemap index declares twelve files and **only the six `job-*.xml` are ads**; summing every `<loc>` reports **250 000+ Swiss ads instead of 52 128**, silently. The search page's `ItemList` carries **URLs and nothing else**, so the HTTP half yields an id and a slug — the card says `title_from_slug` and `needs_browser_to_read`. The ledger URL is a **Jobstore** URL, marked as such, never the employer's. And the button reading **"Apply on company site" links to `/jobseeker/apply/` on jobstore.com** — applying needs a Jobstore account, and the plugin corrects the label instead of repeating it. Overlap with the covered Swiss boards is ~25% HiringCafe, 18.6% jobs.ch, 15.5% jobup |
| iCIMS | `icims.md` | **Shipped.** One employer per site, **no key, no cookie, no browser** — and the family four country surveys named as the commonest one missing here. **The default ad URL is not the ad**: the bare `/jobs/<id>/<slug>/job` answers 200 with 90 KB of the employer's portal and no `JobPosting`, while `?in_iframe=1` returns it — and **the sitemap publishes the bare form**, so an adapter written the obvious way reports an empty board. **The same id is a different vacancy on every host** and the wrong host answers 200, so the key is `icims:<host>:<id>` — the mirror of the Workday defect, and the worse half: one key, two ads. Three host shapes including the employer's own domain (3 of 10 sampled ads), and **the platform host is read from the page, never built** — the prefix has been `careers-`, `apply-`, `field-` and nothing. **The first adapter here to read a tenant's `robots.txt` at run time** (issue #73): two of six hosts refused everything |
| Vieclam24h | `vieclam24h.md` | **Shipped.** One of Vietnam's largest boards, **no key, no cookie, no browser** — results in the page's own `__NEXT_DATA__`, 30 a page, and a sitemap of **17 089 ad URLs**. **The richest record here — 110 fields — and the one that most needs an allow-list**: `employer_info` (the board's own named account manager) and `contact_name`/`email`/`phone`/`address` are filled on **90 of 90** ads, so the card names the sixteen fields it emits and copies nothing else. Dropping `employer_info` by name would have left four of the five behind. **Salary counted on values**: the pair is a key on 100% and a figure on **98.9%**. A bare request answers **403** and the same URL with `Accept`/`Accept-Language` answers 200 — header sniffing, not a bot wall |
| PhilJobNet | `philjobnet.md` | **Shipped.** The Philippines' public employment service (DOLE), **5 145 vacancies**, employer named on every card, **no key and no browser** — the **eighth national public service** here. Its trap is the purest `never-fail-silently` case yet: **`?page=2` is accepted, ignored, and answers 200 with page one**, so an adapter written the obvious way loops for ever over the same ten ads while reporting a complete sweep. Pagination is an ASP.NET WebForms postback whose `__VIEWSTATE` must come from the last response, and **the check that matters is that a page's ids do not intersect the previous page's** — not that it answered 200. Two more found while writing: **each card's anchor sits before its block**, so a naive parse pairs every title with the next ad's id (`slug_matches_title` keeps the check in the row); and **`www` presents Azure's default certificate** while the apex serves the site — the TLS case from `robots-policy.md`, exercised for the first time |
| Applifly | `applifly.md` | **Shipped.** A Swiss ATS, one employer per vanity domain — **recognised by the path, never by the host**. **No key, no cookie, no browser**, and the ad carries a full `JobPosting` **in microdata rather than JSON-LD**, coordinates on 8 of 8. **A `source=` parameter that reads as tracking is what renders the page**: without it the same URL answers `200` with 718 bytes of referrer-capture JavaScript |
| *your board here* | — | See *Writing an adapter* below |

## When a shipped adapter stops working

Boards redesign, and an adapter that was verified against the live site stops
matching it. **That is a bug in the plugin, not in the user's setup, and it is
reported upstream** — invoke `board-request` in its broken-adapter mode
(section 2b). `job-scan` does this on its own when a sweep fails.

The reason it goes upstream rather than getting patched locally: the installed
plugin lives in a cache directory that the next update overwrites, and the site
changed for every user, not just this one. **One issue fixes it for everybody;
a local edit fixes it for nobody, twice.**

## Without any adapter, the plugin still works

`cover-letter <ad URL>` needs no adapter and no browser: give it a URL from any
board on earth — or paste the ad text when the page is gated — and it scores the
fit, gates on go/no-go, and writes the resume and letter. It is the full
workflow minus the automatic sweep.

So the answer to *"can it do <board X>?"* is never a flat no. It is: *"not
automatically yet — give me an ad URL from it and I'll do everything else."*

## Nothing is enabled by default

**An unconfigured workspace scans no board at all.** Scanning drives the user's
own browser, in their own logged-in session, under their own account — so it
only ever touches a site they explicitly switched on.

Each board is enabled *and configured* in `config.yml`:

```yaml
boards:
  linkedin:
    enabled: true
    profile_url: "https://www.linkedin.com/in/adalovelace"
```

Four states, four different behaviours — never improvise a fifth:

| State | What `job-scan` does |
| :-- | :-- |
| No board enabled | Scans nothing. Says so, lists the adapters available, and offers `/job-setup boards` |
| Enabled but a required setting is empty | Skips that board, names the missing key, and offers to fill it. **Never half-runs** |
| Enabled and complete | Sweeps it |
| **Dormant** — `enabled: false` **plus** the four `dormant_*` keys | Does not sweep it, and says nothing about it — **until its `recheck_after` date passes**, when it offers one cheap yield re-check. See below |

`enabled: false` **with no `dormant_since` is a hard off**: never swept, never
probed, never mentioned. That state predates dormancy and keeps its meaning
exactly — a user who said no to a board is not asked again.

## The fourth state: dormant, or "wrong month, not wrong board"

**A board can come back empty for two completely different reasons**, and until
this state existed the config could only record one of them.

- *This board does not serve this candidate.* sozialinfo.ch carries social-work
  ads; a backend engineer will still be finding none of them in five years.
- *This board serves this candidate and had nothing open that week.* On
  2026-08-30, `jobs.bobst.com` — BOBST, **25 minutes** from that user's home,
  on an adapter that worked perfectly — had ten vacancies, and all ten were
  apprenticeships and internships.

Both produce the same zero, and switching both off the same way throws the
second one away permanently. **Dormancy is the state for a board whose zero is
about timing, and it is the user's own measured evidence that puts it there.**

```yaml
boards:
  umantis:
    enabled: false
    dormant_since: "2026-08-30"
    dormant_reason: "the 10 vacancies on jobs.bobst.com are all apprenticeships"
    recheck_after: "2026-11-28"
    recheck_count: 0
    employers: ["jobs.bobst.com"]
```

| Key | Meaning |
| :-- | :-- |
| `dormant_since` | When the run that measured the zero happened. **Its presence is what makes the board dormant rather than off** |
| `dormant_reason` | The measurement, in one line — counts, not adjectives. This is what the user reads months later when deciding, and *"nothing relevant"* tells them nothing |
| `recheck_after` | The date `job-scan` may offer a re-check. Required: a dormant board with no date never comes back, which is a hard off wearing dormancy's clothes |
| `recheck_count` | How many re-checks have already found nothing. Drives the back-off |

**Its own configuration is kept, not deleted.** The tenant list, the domain, the
cantons — waking a board must be one line changed, not a setup interview
repeated.

`skills/job-scan/scripts/dormant.py` reads these back:

```bash
dormant.py list --config "$JOB_HUNT_HOME/config.yml"   # all dormant boards
dormant.py due  --config "$JOB_HUNT_HOME/config.yml"   # only those now due
dormant.py next --count 0                              # the next date to write
```

**Do the date arithmetic with `dormant.py`, not by hand.** *"Is 2026-11-28 in
the past?"* is exactly the question a language model answers confidently and
wrongly, and both wrong answers are bad: one nags the user about a board they
just parked, the other buries it forever.

### The back-off, and why there is one

A re-check that finds nothing pushes the next one out: **90 days → 180 → 365,
then 365 forever.** A board that is genuinely wrong for this candidate therefore
costs one decision this quarter, one next spring, and then roughly one a year —
while a board that comes good is still caught within a season.

Without the back-off this feature becomes a recurring chore, and a recurring
chore gets switched off wholesale — taking the BOBST case down with it.

### What a re-check is, and what it is not

**A yield check, not a scan.** One listing call at the adapter's cheapest
setting, capped. **No descriptions are opened, no scoring is done beyond
title-and-location screening, and nothing whatsoever is written to the ledger.**
A re-check that quietly turned into a sweep would make dormancy expensive, which
is the one thing it must not be.

**Never re-check a browser board silently.** LinkedIn and Indeed drive the
user's own Chrome under their own account; for those, dormancy expiry means
*offering* the re-check and waiting for a yes — never running one because a
date passed. (jobup and jobs.ch were in this sentence until 2026-09-02, when
their sweep turned out to need no browser at all.)

**A re-check that fails is not a re-check that found nothing**, and the two must
never be reported the same way. A dormant board whose probe errors, 404s or hits
a login wall goes to `board-request` in its broken-adapter mode like any other
failure — its dormancy says the board was *empty*, and that claim is now
unverified rather than confirmed.

A board named in `config.yml` with no adapter file is an error, not a fallback:
the skill says so and skips it rather than improvising selectors against a site
nobody has tested. **Guessing at a board's DOM produces a scan that silently
returns nothing, or worse, returns the wrong ads** — and the user has no way to
tell.

## What the skill expects from an adapter

The skill is board-agnostic. It asks each adapter for five things and does the
scoring, the ledger and the reporting itself.

| Contract | What the adapter must document |
| :-- | :-- |
| **0. Its config keys** | Everything it needs under `boards.<name>` in `config.yml`, which of those are **required**, and what to ask the user to obtain each one. An adapter that reads an undocumented key is a bug |
| **1. Prerequisites** | Whether it needs the browser, whether the user must be logged in, and what to say to them before starting |
| **2. Search** | How to build a search URL from `keywords`, `location`, `posted_within` and `remote_only`; how to extract the result cards; what a card yields (**a stable id**, title, company, location, work mode, posting age) |
| **3. Description** | How to open one ad and extract its full text |
| **4. Ad URL** | How to rebuild a canonical ad URL **from the id** — never by scraping a URL out of the page |
| **5. Its zero-shaped answers** | Every way this board says *no* while answering `200`, and every way it says *yes* while answering an error. **This is not optional and not a nicety**: it is the failure mode every adapter built so far has turned up, and an adapter that documents only the happy path hands the next reader a zero with no way to read it. See *HTTP 200 is not a yes* in `shared/never-fail-silently.md` |

Optionally, a sixth: **assisted application**, if the board has an in-site apply
flow. It must follow the same gate as LinkedIn's — the user validates every
send, and nothing is reported as sent without a visible confirmation.

**Compare cities through `skills/job-scan/scripts/_locations.py`, never by
string equality.** One city arrives under several labels in a single result
set — `Hanoi, Hanoi`, `Hanoi, Ha Noi`, `Hanoi, Hà Nội` — and on Bogotá's 103
cards an exact match recovered 17%, the first segment 51%, and the first
segment **with diacritics folded 100%**. The helper does both, and
`drop_report` names what a filter excluded, so a city filter that drops rows
says how many. Issue #65.

**Read a board's `robots.txt` for what it names, not only for what it
forbids.** A Workday tenant lists its career sites in `Allow:` lines — Swisscom
publishes three where a meta-board lookup found two — and a syndicating board
names its outbound feeds, which is where the duplicates will come from.
`shared/robots-policy.md` holds the rule, and its two guards: **a name found
that way is a candidate and never a target** (a tenant lists what it opened to
robots, not what a candidate should read), and **a `Sitemap:` line is a
declaration, not an inventory.** Issue #74.

**A field whose meaning depends on a caveat gets a name that carries the
caveat** — `shared/plausible-and-false.md` holds the class and its rules. A
converted salary is not `salary_min`, an estimate is not a quoted figure, and a
fill rate counts values rather than keys. Eight mechanisms have produced a
value that parses cleanly and is false, and **two of them came from tooling
written to hunt exactly that**: plausibility is not a check, provenance is.

**Say what a date measures, not just where it comes from.** A relative label —
*"Il y a 3 semaines"*, *"Posted 30+ Days Ago"*, *"il y a 2 heures"* — reads as
the age of the ad. **On a re-listed ad it is the age of the re-listing**, and
nothing on the card distinguishes the two. So an adapter that exposes one must
say which of the two it is, and name the absolute field where the board has one.

Measured on jobup, 2026-09-02: a ledger row carried `2026-09-01` for an ad
whose real `datePosted` is `2026-07-14` — **seven weeks out**. Two ads were
tied at 62% and the tie was broken by the most recent date, so **the older one
came out on top of a ranking that decides what gets drafted**. The adapter had
already said to prefer the ad page's date; it had not said what the card's date
*was*, and that is the sentence that would have prevented it. Issue #84.

**`jobbkk` is the same phenomenon from the other side**, and its treatment is
the model: an ad created in 2010 and refreshed yesterday would be aged by
sixteen years by a scorer reading `created_at`, so the card carries **both**
dates named for what they are — `created` and `refreshed` — and the file says
which to read.

**When only a relative date exists, say so and leave the ledger's date empty**
rather than deriving one: an empty field is a question, a wrong date is an
answer.

**Name what the card emits, never what it drops.** A deny-list is a bet that
you enumerated the problem correctly; an allow-list is a bet that you
enumerated the *need* correctly, and **the two failure modes are not
symmetric**: an allow-list that is too narrow produces a **missing field** —
visible, reported, fixed in one line — while a deny-list that is too narrow
produces a **leak**, invisible and found by somebody else. When two errors are
possible, prefer the one that announces itself. Issue #75.

The case that produced the rule: `vieclam24h`'s ad record carries **110
fields**, including a named recruiter's phone, email and address *and the
board's own account manager*. The obvious implementation — drop
`employer_info` by name — **would have let four of the five contact fields
through**. `KEEP` names the sixteen the card emits, so a field the board adds
tomorrow cannot appear in a ledger.

**And the five fields were not one problem.** The account manager is the
board's internal staff data, in nobody's advert; the employer's own
`contact_email` and `contact_phone` were published *so that candidates would
use them*. The allow-list is right about both, but for different reasons, and
an adapter file should say which — stripping an ad's stated contact as though
it were a leak removes exactly what the employer put there for the reader.

```bash
bin/emit-audit.py     # every adapter, and whether it enumerates what it emits
```

**54 of 54 pass** as of 2026-09-02 — six of them read by hand, named and dated
in that file, because a site the tool cannot follow must never be reported as a
clean one. The single exception it names is `talentsoft`'s `other_fields`: the
one emitted field here whose *content* is not enumerable, carrying unlabelled
fragments of a card's visible text, capped, and deliberate — that board's rows
vary by tenant and a wrong label is worse than an unnamed string.

**Read a board's terms through `shared/reading-terms.md`, and quote the clause
before concluding anything from it.** A sweep is one candidate's own search,
run at their request, under their criteria, and nothing is republished or
resold — so a clause written against commercial harvesting does not describe
it, and reading it as though it did refuses the user work they are entitled to
do. **A clause that forbids automated access *as such* is a different clause
and it binds**, as does a rate limit, a login wall, and any `robots.txt`
refusal — the position changes how an ambiguous clause is read, it never
creates permission a board withheld. Issues #48 and #81.

**Read `<loc>` through `skills/job-scan/scripts/_sitemap.py`, never with a
pattern of your own** — and the reason is the same failure, one file later.
Three ways a populated sitemap reads as empty, all measured:

- **CDATA.** `hays.fr` wraps its URLs, and `<loc>\s*([^<\s]+)` matches
  **nothing at all** on a valid 200-OK 2.37 MB file. Issue #55.
- **One line.** `grep -c '<loc>'` counts **lines**, not elements: a 91-URL
  sitemap served without newlines reports **1**.
- **A namespace prefix** — `<ns:loc>` — which a pattern anchored on `<loc>`
  misses entirely.

**And the audit is why it is a module rather than a fourth patch.** On
2026-09-03, **13 scripts read `<loc>`: seven carried the corrected pattern —
five of them with the same comment block copied verbatim — and five still
carried the naive one.** #55 fixed four adapters and left the rest, because
there was nowhere for the fix to live. Use `locs()`, and print `count_says()`
on a zero: **a sitemap is never reported empty**, because a zero has four
causes and only one of them is an empty sitemap.

**Read `application/ld+json` through `skills/job-scan/scripts/_ldjson.py`,
never with a pattern of your own.** Two independent deviations have already
cost this repository whole boards, and each was patched where it was found and
nowhere else:

- **The parse.** Michael Page and a Chilean public service embed literal
  newlines inside JSON strings, which is invalid JSON. Measured 2026-09-02:
  `json.loads` reads **0 of 3** Michael Page ads and **0 of 5** Chilean ones;
  with `strict=False`, **3 of 3** and **5 of 5**. Two boards of ten measured
  need it — *and you do not know which board will be the third*. The argument
  costs nothing; its absence costs the whole ad.
- **The extraction.** One site writes `<script type='application/ld+json'>`
  with single quotes, and a pattern demanding double ones matches nothing —
  the adapter then reports `json_ld: false` on every ad. **Ten of the
  eighteen readers here had that pattern**, and three more lacked `re.I`.
  Thirteen outages waiting on a punctuation change. Quote style is not a
  contract.

Both fail the same silent way: the block is skipped inside a
`try/except: continue`, and the run concludes *this board publishes no
structured data*. **So when there is no JobPosting, call `absent_reason()` and
act on `our_fault`** — a block that is present and unreadable, or a page that
says `JobPosting` and yields none, is a bug here and exits loudly; only a page
with no structured data at all is a fact about the board. Issue #76.

The **id is the load-bearing part**. It is the ledger's dedup key, so it must be
stable across visits and rebuildable into a URL. A board with no stable per-ad
id needs a documented composite key (company + title + posting date) and a note
saying it will occasionally miss a duplicate.

## Choosing which board to build next

**This is a tool for anyone, and no contributor's own job search is a reason to
build anything.** Whoever writes an adapter has a country, a language and a
shortlist of employers, and none of that is an argument. The board that is
convenient to the person holding the keyboard is not the board that is missing.

Decide on properties of the board and of the gap instead:

- **How many people it reaches** — the size of the board, and whether the
  population it carries is already covered by something shipped. A sector board
  in a sector nothing else reaches beats a bigger generalist that overlaps.
- **Whether there is a door**, and whether it is a *sanctioned* one — see
  *Reading a robots.txt* below and `shared/robots-policy.md`. An open endpoint
  that leaks its storage layer is not the same as a published API.
- **Whether it can be verified.** An adapter that cannot be measured against
  the live site does not ship, however valuable it looks. Better recorded as
  *investigated, buildable, not built* than shipped on trust.

The same rule governs the writing. A trap is serious because of **what it
does** — returning empty ads, truncating in silence, matching every document —
not because of who it happens to inconvenience. Write *"anybody who asks for
the language they read"*, never *"our user"*.

**What this does not mean.** Geography that is a measured property of a board
stays: *jobup.ch is French-speaking Switzerland*, *randstad.ch's structured
data is missing exactly where Romandie is*, *the `/es/` sitemap is the
Spanish-language board and 10 of 40 ads are outside Spain*. Those are facts
about the site, they are useful to whoever searches there, and removing them
would make the tool worse. The rule is about the **reasoning**, not the map.

## An ATS-family adapter is verified against two tenants, never one

**What does not vary at the first client is not a property of the API.** One
tenant validates the shape of the response and nothing that differs between
customers — and what differs between customers is exactly what a family adapter
exists to handle.

Two cases, found the same day from opposite directions:

- **`oraclecloud.md`.** The first version built ad URLs from `SiteNumber` and
  took the first site in the list. Correct on ClubCorp, which publishes at
  `/sites/CX/` with `SiteURLName` null and lists one active site. **Wrong on
  FMOLHS**, which publishes at `/sites/fmolhs-careers/` from a site numbered
  `CX_3001` and lists an `ORA_INACTIVE` portal *first*. Both mistakes produce
  links that 404 for the user rather than an error in the run.
- **Operator fingerprints** (a sibling session's country series).
  `bumeran.com.ar`, `zonajobs.com.ar` and `bumeran.com.mx` share **eleven
  directive lines of eleven** — one file, two brands, two countries — while
  carrying **6 560 ads against 1 816**. Identical policy, unrelated volume:
  measuring either one alone and generalising gets the other wrong.

So: **before shipping a family adapter, run it against a second tenant you did
not develop against**, and prefer one that looks unlike the first — another
country, another size, an employer with several career sites. The failures this
catches are the ones that look like success on the tenant in front of you.

`recruitee.md`, `pinpoint.md`, `personio.md` and `oraclecloud.md` each state
how many tenants they were measured on, and that number is part of the claim.

## Writing an adapter

Copy the shape of `linkedin.md`. It is not a spec document — it is a field
report, and that is what makes it useful. Write down:

- the **constraints you hit**, and what happens when you ignore them
  (virtualized lists, hidden-tab throttling, synthetic clicks that do nothing,
  endpoints that return an error code instead of data);
- the **selectors and snippets that actually worked**, verbatim;
- the **traps**: geocoding that lies, aggregator reposts, stale form fields,
  anything that produced a wrong result once;
- what the board does about **rate limiting**, and the pace that stays under it.

**A fix applied to one caller is not applied to the service.** On 2026-09-02
`hiringcafe.py` grew a timed backoff for HiringCafe's 403 throttle, and
`ats.py resolve` — which reads the same site, for the same reason — kept dying
on a raw 403 for the rest of the day. **The same board behaved differently
depending on which script asked.** Forty-eight scripts live here and several
speak to the same hosts: before closing a fix, `grep` for the host, not for
the function you just edited.

Two rules for anything added here:

1. **Only document what you have run against the live site.** An adapter that
   describes a plausible DOM is worse than no adapter.
2. **Date what you verified**, and say when a selector was last confirmed.
   Boards change their markup; a dated note lets the next person tell a broken
   adapter from a broken assumption.

3. **When you re-verify a file in part, date the part you did not touch.** A
   header saying *"re-verified 2026-08-28"* over sections nobody re-ran makes
   the file read as fresh when half of it is not — and `bin/adapter-age.sh`
   reports each file by its **oldest** standing date, so an undated old section
   is invisible to it. `linkedin.md` carries the worked example: its Easy Apply
   sections say in their own heading that they date from 2026-08-26 and were
   deliberately left out, because exercising them means driving a real
   application on the user's real account.

## Which adapters are due for re-verification

```
bin/adapter-age.sh [days]      # default 30
```

**Every board file declares when it was last run, in one line near the top:**

```
<!-- verified: 2026-09-02 -->
```

That field, and nothing else, sets the age. `adapter-age.sh` reads it out of
every file here plus `shared/ats-open-check.md`, sorts by the oldest, and
flags anything past the threshold. A file with **no header** is reported
`UNDECLARED` — not stale, not fresh, *unknown* — and the line is added the
next time the file is touched, carrying the date it was actually re-run.

**Why a field and not a date in the prose.** The script used to read any date
it could find and take the oldest. On 2026-09-02 it called `jobbkk` 1 384 days
stale, because `jobbkk.md` quotes `created_at: 2022-11-17` — a date this
repository *measured* on a live ad, to document a board that refreshes ancient
postings. A present, well-formed value that does not mean what the reader
thinks: **issue #67, in our own tooling, after five board files had documented
the pattern.** Parsing prose after a marker would have been the same mistake
as anchoring on `[data-cy="…"]` instead of `ld+json` — a convention the next
turn of phrase breaks. A field is a contract.

It has a good side effect: **recording a verification is now deliberate**. A
file cannot be refreshed by accident because somebody quoted a date in it.

**A file may also decline verification, and say so**: `<!-- verified: never -->`
puts it in its own bucket, *Not verified by choice*. `softy.md` is the case —
its `robots.txt` bans every AI agent, this repository obeys, and **there is no
re-verification that would not itself be the violation**. Without the marker
the gap reads as an oversight and somebody closes it by probing the site.

## An assertion of non-existence carries the search that established it

"No directory exists", "the site never returns an error status", "the browser
is required" — **none of these can be checked by reading the file**, and each
one has already rotted here: Jobvite's "never an error status" was a `302`,
`jobup`'s browser prerequisite cost every extension-less user their Swiss
sweep, and `jobsireland`'s "a dozen countries" was four.

So a negative claim is written as **the search, dated**, not as the
conclusion:

> *No tenant directory was found. Searched 2026-09-02: the vendor domain
> redirects `robots.txt` and `sitemap.xml` into a product page,
> `/careers/v1/careers-sites` answers 404, `/public/v1/careers-sites` answers
> 403 with a JSON refusal, and a tenant host serves an empty `robots.txt` and
> a 404 sitemap.*

That form is refutable by anyone in five minutes. *"No directory exists"* is
not refutable at all, which is exactly what makes it dangerous. And where
nothing turned up, write **"was not found"** rather than **"does not
exist"** — the difference is an observation against a claim nobody can
support. `digitalrecruiters.md` and `talentsoft.md` carry the worked
examples.

### And a script must not write the same line for both

**"Searched and found nothing" and "did not search" are two different facts,
and a tool that emits one row for both manufactures the confusion at the
source.** Measured 2026-09-02: a triage over twenty-seven countries wrote
**twelve zeros, and none of them was an empty market** — twelve collection
refusals, recorded in the same shape as a genuine zero, on countries nobody
would have had a reason to re-open.

**And the search had produced its own certificate of failure.** The adapter
printed *"THE SWEEP IS PARTIAL … Do not report this as a complete pass"* for
every one of the twelve, and exited non-zero. **The caller read stdout and
logged stderr.**

So the assertion of non-existence formed **not because nothing warned, but
because the number and its validity travelled on different channels** — see
*A value and its validity must travel in the same object* in
`shared/never-fail-silently.md`. A wrong negative that nobody has a motive to
revisit is precisely what "rots without announcing itself" means, and this one
had a certificate attached that nobody was reading.

So a table with a zero in it says **which zero it is** — *measured* against
*not collected* — and a script that cannot tell them apart must exit non-zero
rather than write a row.

*(The repository's adapters already work this way — `_zero.py` prints what a
zero cannot distinguish, and a refusal exits 2, 6 or 7 rather than returning an
empty list. **A static audit of that property was attempted and abandoned**: a
check for handlers that swallow an error flagged 34, of which nearly all were
returning a status code for the caller to read. The number was clean and
useless, which is the class `shared/plausible-and-false.md` names.)*

**This limits what the `verified:` header proves.** It records when a file was
re-run; it does not record which assertions that run actually tested. Running
an adapter's happy path re-tests nothing about something absent, so **a
negation needs its own dated evidence, beside the header rather than inside
it.** A file whose heading says it was **never verified against the
live site** is pulled out of the age ranking entirely and listed under its own
`[ !! ]` — a draft is not a stale adapter, and its drafting date is not a
verification date. It changes nothing and always exits 0: **a stale adapter is
not a broken one, it is one nobody has re-run.**

Re-verifying means *running* the adapter against the live site, not re-reading
it. That distinction is the whole point: every defect found on 2026-08-28 —
umantis's per-vacancy segment, the unanchored `externalUrl`, LinkedIn's
`^with verification` anchor — was a rule generalised one step past what had been
observed, and **none of them were visible on re-reading.**

## ATS hosts — not boards, but useful for a different question

`shared/ats-open-check.md` records hosts that answer *"is this ad still open?"*
in one unauthenticated request — Haufe/Abacus umantis, Jobvite, SAP
SuccessFactors, Refline, Prospective, Solique, and the ATSs already named in
`cover-letter` step 1b. It also records which hosts publish a **stated expiry
date**, which answers the question without any request at all.

**Those are deliberately not adapters, and adding one here would be a mistake.**
An adapter exists so `job-scan` can **sweep many employers**; an ATS host serves
**one employer per tenant** and has no cross-employer search, so there is nothing
to sweep. What it does have is an authoritative answer about a single ad, which
is what step 1b needs and what a board is worst at providing.

Keep the two apart: **sweepable board → an adapter here. Employer ATS → a row in
`shared/ats-open-check.md`.** That file also records the hosts investigated and
**rejected**, with why — a negative costs as much to establish as a positive and
saves the next person from repeating it. When a `board-request` turns out to be an ATS, that
file is where its findings belong.

## Reading a robots.txt, and the one case that overrides it

The sections below decide individual boards. **The rule they are decided by
lives in `shared/robots-policy.md`** — four questions, answered in the board's
own file before any code, and a default of *obey* that four of the five cases
land on. Read it before concluding anything about a board that names AI agents;
the answer stopped being binary at `leboncoin`, and the file records why.

**Before any of that, `shared/robots-policy.md` now opens with the checks that
decide whether there is anything to judge**: a `robots.txt` verdict is not an
access verdict, a file that is not `text/plain` is not a file (58 to 275 bytes
is what a real one weighs; 126 015 was a sign-in page), a browser only changes
failures that sit above it — with TLS as its own case, because three live
boards were written off over an expired certificate — and the failure with no
status code at all. It closes with **five words every board file should use
identically**: *open*, *refused*, *inaccessible*, *not sanctioned*,
*substituted*.

The one board decided the other way is the Austrian **AMS**, whose `robots.txt`
grants `LinkedInBot` the employer pages and refuses every other agent. That
override is **opt-in and off by default** (`override_robots: true`), it must
announce itself in the run's output, and its full reasoning — including the
open-data check that came back empty rather than negative — is in the policy
file, not here.

## Investigated and closed — leboncoin.fr

**Verified 2026-08-31, from `robots.txt` alone** — once the rule was read,
nothing else on the site was fetched.

Leboncoin is the largest French audience with no adapter, and it will not get
one. Its `robots.txt` **declares no `User-agent: *` group at all**, and opens
with a prose statement rather than a rule:

> *"It's forbidden to use search robots or other automatic methods to access
> Leboncoin.fr. Access is only permitted with special permission from
> Leboncoin.fr."*

Everything after that is the list of exceptions they have granted — and it is
the most considered file this repository has read, because it **splits AI
agents into three classes**:

| Group | Agents | Treatment |
| :-- | :-- | :-- |
| AI **search / retrieval** | `Claude-User`, `Claude-SearchBot`, `ChatGPT-User`, `Perplexity-User`, `Applebot`… | Allowed, **except `/recherche`** |
| AI **training** | `ClaudeBot`, `anthropic-ai`, `GPTBot`, `CCBot`, `Google-Extended` | Allowed, **except `/recherche` and `/ad/`** |
| `Bytespider` | — | `Disallow: /` |

**`Claude-User` is precisely the class this plugin falls into**: a fetch a
person asked for, on their own behalf. Leboncoin permits it — and still closes
`/recherche`, which is the results page, which is the sweep.

That is not an obstacle to route around, it is a considered position: *read an
ad a human pointed you at; do not harvest our search results.* **A browser
adapter changes nothing here** — what is refused is not the access, it is the
sweeping. `cadremploi.md` uses a browser because a script is blocked; nothing
of the kind applies.

**What remains true and useful:** individual ad pages are not disallowed to the
retrieval class. That is exactly the `cover-letter <URL>` case — the user finds
an ad, hands over the link, and the plugin does everything else. It needs no
adapter and works today.

**Worth carrying to other adapters:** this is the first site here to
distinguish *user-initiated retrieval* from *training crawls*, and to allow the
first while refusing the second on the pages that matter. `softy.md` banned
every AI agent outright; `taleez.md` allowed `ClaudeBot` explicitly. When a
`robots.txt` names AI agents, read which class it is talking about before
concluding anything — the answer is no longer binary.

## Investigated and closed — Monster

**Verified 2026-08-31, live.** Monster gets no French adapter, and the reason is
not access: **there is no French job board left to adapt.** Monster still
exists, still calls itself a job board, and still answers to `monster.fr` — the
name is the only thing that survived.

### `monster.fr` is a CV advert

Every path on the domain answers `301` to **one** destination, discarding the
path and the query with it:

| Asked | Sent to |
| :-- | :-- |
| `www.monster.fr/emploi/recherche?q=developpeur` | `www.monster.com/fr/` |
| `www.monster.fr/emploi/annonce/12345` | `www.monster.com/fr/` |
| `www.monster.fr/entreprises/` | `www.monster.com/fr/` |
| `jobview.monster.fr/...`, `job-openings.monster.fr/...` | `www.monster.com/` |

And `www.monster.com/fr/` is not a job board. Its `<title>` is **"Monster et
monCVparfait CV designer"**, its body sells a CV builder, and it contains **no
search form and not one link to a job** — the only outbound links are to
`moncvparfait.fr`, the affiliate. The footer's language switcher confirms it is
not a French accident: **every non-US locale points at a CV page** —
`fr`, `de`, `es`, `it`, `nl`, `se` at `/xx/`, and Canada, Ireland and the United
Kingdom at `/resume/`. The US board is the only board.

**This matters to `cover-letter <URL>` even with no adapter.** An old Monster
France link does not 404 and does not say *"offre expirée"*. It returns **200**
and a CV advertisement — a page with a title, prose and a call to action, which
is exactly the shape a fetch-and-summarise step mistakes for an ad. If a user
hands over a `monster.fr` URL, say the ad is gone; do not describe the page.

### The US board accepts a French location and answers with Mississippi

This is worth recording in full, because it is the most convincing wrong answer
any board in this repository has given.

`www.monster.com/jobs/search` accepts `where=` without validating it. Measured:

| Searched | Header echoed back | What came back |
| :-- | :-- | :-- |
| `q=engineer&where=Lyon, France` | *"Engineer Jobs in Lyon, France"* | 7 ads: **Lyon, MS**, Clarksdale MS, West Helena AR |
| `q=ingénieur&where=France` | *"Ingénieur Jobs in France"* | Huntsville AL, Boise ID, Houston TX, Kassel DE |
| `q=developpeur&where=Paris, France` | *"Developpeur Jobs in Paris, France"* | **1 ad**, Sabattus, **Maine** |
| `q=Paris, France` (empty `where`) | *"…Jobs in **Remote**"* | Palo Alto CA, and **France, ID** |

It matched **Lyon, Mississippi** — a Delta town of a few hundred people — and
returned its neighbours within 30 miles. `France` was dropped. An empty `where`
silently became `Remote`. Nothing errored, nothing warned, and the page kept
repeating the French location back in its own heading while serving Arkansas.

A handful of genuinely European rows are in the index (*"Systems Engineer,
Territory South (Lyon Based) France"*, a Kassel ad in German) — but they surface
because their **title** contains the word, never because the location filter
found them. There is no French inventory to sweep, only French words in US ads.

### A browser adapter does not rescue this one

`indeed.md`, `cadremploi.md` and `softy.md` each use the user's own Chrome
because a script is blocked. Monster is blocked too — **DataDome** guards every
page and the underlying API alike:

```
POST https://appsapi.monster.io/jobs-svx-service/v2/monster/search-jobs/samsearch/en-US?apikey=…
```

From a script that answers `403` with a **`geo.captcha-delivery.com` URL**, and
this plugin does not solve CAPTCHAs. From inside the browser it answers
normally — so the browser route is *technically* open, exactly as it was for
Indeed.

**It is still the wrong build**, and the distinction is the point: for Indeed
the browser buys access to French ads. Here it would buy access to
**Mississippi**. The blocker is not the wall, it is the inventory. Note also
that the locale is a path segment (`…/samsearch/en-US`) — `fr-FR` and `fr` were
tried and are not a way in.

### What would reopen this

A French Monster job board coming back — a `monster.fr` that serves its own
search again, or a `www.monster.com/fr/jobs/…` that returns French locations.
Re-check by asking one question, which takes ten seconds and no adapter:

```bash
curl -sI 'https://www.monster.fr/emploi/recherche?q=x' | grep -i location
```

While that answers `https://www.monster.com/fr/`, there is nothing here. Until
then Monster is a brand licensed onto a CV builder in France, and the honest
answer to *"can it scan Monster?"* is **"Monster no longer publishes French
jobs"** — not *"not yet"*, which invites the user to wait for something that is
not coming.

## Investigated and not built — Beetween

**Verified 2026-08-31.** Beetween is the fifth French ATS name on the list, and
the only one of the five investigated that **cannot have a platform adapter** —
for a reason worth writing down, because it is not a wall, it is an absence.

The other four each have one contract that holds across every customer:
Taleez's `/api/careez`, Flatchr's `__NEXT_DATA__`, Talentsoft's `fld*` element
ids, DigitalRecruiters' single API keyed by hostname. **Beetween has none.** It
sells careers sites *"from basic to fully customised"*, and its own —
`recrutement.beetween.fr` — is a bespoke **WordPress + Elementor** build whose
pages call no Beetween service at all: the only host they talk to is their own.

What was established:

- Ads live at `/poste/<id>-<slug>/` **on that site**, and the ad page carries a
  standard schema.org `JobPosting` — description, `baseSalary`, `datePosted`,
  education and experience requirements.
- **The sitemap contains no ads** — only posts, pages, categories and tags — so
  there is no enumeration route even on that one site.
- The single hosted-looking domain found in the markup,
  `<tenant>.nous-recrutons.fr`, answers **403 in a real browser as well as to a
  script**. Not bot protection: that host is not served publicly.
- No Beetween *customer* careers site was found to verify against.

An adapter written now would be an adapter for **one WordPress theme**, and
would break on the next customer. Rule 1 forbids shipping that.

### There *is* a platform surface — and it still does not make a board

Followed up 2026-08-31, from the France Travail partner links: **79 BEETWEEN
ads across four departments all pointed at one host**,
`app.beetween.com/WeaselWeb/p/#/apply/job/<id>/<slug>`. So Beetween does have a
shared surface after all — the customer careers sites vary, the *apply* pages
do not.

Three things about it, all measured:

- It is a **hash-route Vue SPA**. The shell is 1.3 KB with no data and no
  JSON-LD, so plain HTTP gets nothing.
- Its backend is `https://apehi.beetween.com` — read out of
  `window.__NUXT__.config.backendApiBaseUrl` — and it answers unauthenticated:
  `/WeaselWeb/api/publicoffer/detail` returns a **RESTEasy 404**, which is a
  live backend rejecting a wrong path, not a refusal. The exact call was not
  established.
- **It is a detail surface, not a listing.** One ad at a time, keyed by ad id.
  No per-tenant index was found on that host.

So even fully reverse-engineered, Beetween would not be a board: **France
Travail would still be doing the enumerating**, and Beetween would only add the
employer's name and the full ad text to rows the partner feed already carries
anonymously. Real, but modest — and resting on an undocumented internal
application API with no contract and no versioning.

**Two routes remain, and neither is blocked:** finish reverse-engineering
`apehi.beetween.com`, or read the SPA in the user's own browser as
`cadremploi.md` does. Both were left unbuilt deliberately: the value is small
and the foundation is unstable.

**What would change that:** one working Beetween *customer* careers URL with a
real listing on it. That puts Beetween back in the shape of every other ATS
here — a per-tenant adapter — and most plausibly a `JobPosting` reader, since
schema.org is identical whoever emits it.

**And Beetween ads already reach the ledger.** It is the **largest single
supplier** of France Travail's partner feed — 38 of 150 sampled Paris partner
ads, ahead of METEOJOB — so `france-travail.md` with `origineOffre=2` carries
them today, without the employer being named.

## Investigated, buildable, not built

**jobeo.ch** — a staffing-agency board (Adecco and others), verified 2026-08-29
over the same job-room sweep that produced `fachkraft.md`.

What is established: the listing lives at **`/jobsearch/offers`** (also `/jobs`)
and serves **20 ads per page**; every ad page carries a `JobPosting` block whose
`hiringOrganization` is the agency, with a **GUID** as `identifier`. There is
**no `validThrough`**.

What is not: pagination was never exercised, and it is unclear which of the slug
or the GUID is the stable key — so the ledger contract cannot be met yet.

One trap already worth knowing: **`/candidat/offres/` — the path job-room
publishes in its `externalUrl` — answers `200` with a "Page non trouvée" page.**
The ad URLs under it work; the directory itself does not.

Built when someone needs it; the remaining work is one session, not a project.

## Investigated and closed — eight national public employment services

Measured 2026-09-01, while looking for the country to build after Germany. **The
national-public-service pattern is the highest-yield heuristic in this
repository — four of the six adapters that use it are the largest board in their
country — and it has a hit rate, not a guarantee.** These eight were probed and
none of them yielded a board. Recorded so nobody repeats the work.

| Country | Service | What was measured |
| :-- | :-- | :-- |
| Portugal | IEFP | `netemprego.gov.pt` does not resolve (DNS); `iefponline.iefp.pt` answers 302, and its offers path a 404 |
| Netherlands | UWV | `werk.nl` — every path redirects to `login.werk.nl`, Oracle Access Manager SSO |
| Denmark | Jobnet / STAR | `job.jobnet.dk` redirects to `jobnet.dk`, which serves a **NemLog-in** error page — national identity |
| United Kingdom | DWP *Find a job* | Serves a `/waf_failover/` page **as HTTP 200**, including on `/robots.txt` |
| Poland | praca.gov.pl | `oferty.praca.gov.pl` serves a `/TSPD/` script and `bobcmn` — F5 Shape anti-bot |
| Finland | Työmarkkinatori | `robots.txt`: **`Disallow: /api/`** and `Disallow: /*/api/`. Explicit, and obeyed |
| Norway | NAV | `arbeidsplassen.nav.no/stillinger/api/search` answers 200 with no key and `robots.txt` is open — **but it returns the raw Elasticsearch envelope** (`_shards`, `_index`, `took`, `_score`) and **429s after a dozen requests**. See below |
| Italy | Cliclavoro | **No longer a board at all** — see below |

**Three different states, and they are not interchangeable.** *Inaccessible*
(Portugal, Netherlands, Denmark, UK, Poland) is the operator's infrastructure.
*Accessible and refused* (Finland) is the operator's stated wish, and
`shared/robots-policy.md` governs it. **Accessible and not sanctioned**
(Norway) is the only one where the decision is ours.

**Norway is the case worth reading.** The door is open and the file permits it,
so nothing forbids the fetch. It was still not built: an endpoint that returns
its storage layer verbatim was not designed as an interface, and question 2 of
`shared/robots-policy.md` asks for a *sanctioned* door rather than an open one.
The 429 under a light probe is the empirical half of the same conclusion — an
operator throttling at that volume is not expecting the traffic. Building on it
would be betting that nobody closes it.

**Italy is a fourth state, and it is the one that will waste someone's time.**
`cliclavoro.gov.it` is accessible, its `robots.txt` is permissive towards us —
it refuses `ClaudeBot`, does **not** name `Claude-User`, and sets
`Content-Signal: search=yes, ai-train=no, use=reference` — and it publishes
**zero vacancies**. It is now a news and guidance portal; `/offerte-di-lavoro`
is a 404, and `/concorsi` is fourteen editorial links, half of them photography
prizes and poetry competitions. A portal that still exists and no longer
publishes anything will keep appearing in every list of national resources.
**It is not a closed door. It is a door that no longer leads anywhere.**

*(One thing found here is worth more than the closure: Cliclavoro is the second
site in this repository to use `Content-Signal`, and the first public body. See
`shared/robots-policy.md`.)*

## Boards without an adapter

The user can still apply to an ad from any board: `cover-letter` takes a URL,
and falls back to asking for pasted ad text when the page is gated. It is only
the *scan* — the automated sweep that fills the ledger — that needs an adapter.

So a reasonable answer to "can it do <board X>?" is: *"not automatically yet;
give me an ad URL from it and I'll do everything else."* Say that, rather than
attempting a scan that has never worked.

**Two boards are exceptions, and "not yet" is the wrong answer for both.**
Leboncoin has declined the sweep on purpose, and **Monster no longer publishes
French jobs at all** — telling either user to wait invites them to wait for
something that is not coming. Read their sections above and say what is
actually true.
