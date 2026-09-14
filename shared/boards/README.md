# Board adapters

`job-scan` is board-agnostic: it owns the scoring, the ledger and the reporting,
and each adapter owns one site. Sixty-seven ship today, each verified against
the live site — count the rows below rather than trusting this sentence, which
has gone stale before.

## The adapter you are missing is an issue you can vote for

**Every board and every ATS family without an adapter has its own issue on the
plugin repository, labelled `adapter`** — one per board since 2026-09-13 (#291)
and one per ATS family since the same evening (#406). *An ATS is the software
behind an employer's "Careers" page — Greenhouse, Workday, iCIMS, Avature,
BambooHR…: one adapter covers every employer that runs on it, in every country.*

**Open the list and press 👍 on the one you need**:
<https://github.com/dominiquevienne/claude-job-hunt/issues?q=is%3Aopen+label%3Aadapter>.
The issues are worked in decreasing order of votes (owner's rule of
2026-09-13); an issue nobody has voted for waits behind the ones people have.
If your board or ATS is not there, `board-request` files it — say
"add support for <board>" or paste an ad URL from a site `job-scan` cannot sweep.

## The uncovered-board queue cannot be re-derived from this directory

**Re-derived 2026-09-08 on request, and the result is that the question has the
wrong source.** *Written down because «the queue is empty» and «the queue is not
here» read alike and are not the same.*

### What the derivation gives

```
129 cards · 199 hosts declared by a `hosts:` field, `www.` normalised
 23 cards declare no script
      of those:  4 measured · 8 indeterminate · 3 out-of-domain · 8 no content field
212 hosts named in a card's prose and declared by no `hosts:` field
 40 of those named in a sentence that mentions a board, advertisements or a sitemap
  0 that are a buildable board this repository has measured and not built
```

**Each of the forty was opened.** They are CDNs (`cdn.kosovajob.com`), sitemap
hosts (`info.jobartis.com`), vendor sites (`cegid.com`, `talentsoft.com`),
application shells (`rozeegpt.ai`, `recruit-ai.co`), network nodes
(`sierraleonejobsearch.com`), hosts already measured as empty (`career.ge`,
`bankers.ge` — *«a full sitemap and no advertisement»*), and one excluded on
positive evidence (`laborum.pe`, whose own `robots.txt` describes a different
stack, in a country two adapters already reach).

### Why that is a statement about the directory and not about the world

**The queue of nineteen built on 2026-09-05 came from the country pages — 186
artefacts — not from `shared/boards`.** *This derivation reads only the
directory, so it can only find a board some card already mentions.* **A host
measured in a thread and never written up is invisible to it**, which is issue
#162 on this object.

> **«Empty from here» is not «empty».** *The instrument and the population do
> not match, and saying so is the result.*

### The instrument, and the two defects it passed through

**A host pattern is bounded from below, not from above** — and bounding it
twice introduced a new over-count each time:

```
grep -rl 'job.am'          9 files, incl. bestzambiajobs.md   `.` is a wildcard
grep -rlF 'job.am'         still over-counts: substring of `job.amazon`
text match, any card       json.loads · value.value · html.unescape
+ real-TLD requirement     robots-policy.md · ats.py · workday.py
                           **`.md` is Moldova and `.py` is Paraguay**
+ exclude by file EXISTENCE — not by extension, which would lose two countries
```

**Four controls, both directions, all passing:** `sptojobslink.com` must appear
(named everywhere, declared nowhere); `rozee.pk` must not (declared as
`www.rozee.pk`); `robots-policy.md` and `ats.py` must not.

*And the decisive instrument is neither `grep` nor `grep -F`: it is the
`hosts:` field.* **On the four files a text search returns for `job.am`, one
declares it and three merely mention it** — which is the difference between a
board being covered and a card naming it.

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
| Batiactu | `batiactu.md` | **Shipped.** French BTP — **9 984 ads**, a sector with no other coverage here. **No browser.** Browses by path because the `robots.txt` closes the search page. Publishes **coordinates on every ad**, and its pagination is exact and terminates — rare enough to note. But **the region filter matches the employer's name, not the job's address**: a third of the Île-de-France page was 300 km away, so the adapter filters on the postcode afterwards. `streetAddress` is the employer's head office, repeated across twenty communes | **2026-09-13: 403 to the declared client, served to a tab — «10 300 offres d'emploi», the region pagers close under the reader (Île-de-France 10 182); `route: browser · 10300`, the script's own walk driven from a tab**
| ANEFA | `anefa.md` | **Shipped.** French agricultural and seasonal work — **2 818 ads** the generalists do not gather. **No browser**, and **no `robots.txt` at all**. Carries `Hébergement possible` and `Repas sur place` on every ad, which no other board here has. **No employer field exists** — the farm is prose, so `company` is null by design. Its department parameter is an **ordinal, not the number**: Corsica takes two slots, so `29` returns the Eure-et-Loir; the map is read from the site's own select every run |
| Welcome to the Jungle | `wttj.md` | **Shipped — cut in two.** **88 222 ads**, two thirds French-language. Discovery is `wttj.py`, plain HTTP on the sitemap `robots.txt` advertises, with a **real per-ad `lastmod`** — 7 691 distinct values in 10 000 — so `--since` narrows a re-scan properly. Reading needs the user's Chrome: every HTML page answers **`202` + `x-amzn-waf-action: challenge`**, a 2xx with no ad in it, and slowing to one request per 12 s does not help. **In-page `fetch()` is not the Figaro shortcut** — it works twice then challenges; navigation is what holds. Publishes `hiringOrganization.sameAs`, the employer's own site, which nothing else here does |
| Adecco France | `adecco.md` | **Shipped.** **13 293 French ads**, from the country sitemap `robots.txt` declares — the country is in the *file name*, the cleanest geography here. **No browser.** Salary on 11 of 17, full descriptions, and a retired ad answers an honest **410 Gone**. But the employer is `adecco` on every ad, `postalCode` is empty on every ad, `currency` holds **"France "**, `employmentType` is French text or the string `"null"`, and the department in the URL is truncated — `loire` ends 1 065 ads spanning six departments, so `--region` reads it off the ad and costs a fetch |
| Adecco Norway (Norway) | `adecco-no.md` | **Shipped — #369, the staffing network's Norwegian front on the French platform: `adecco.py --host no` — 189 ads in `sitemap-jobs-norway-nb.xml` on 2026-09-14 (`www.adecco.no` → `www.adecco.com/nb-no`).** The agency as employer on every ad; **the consultant the description names scrubbed (a correction for France too).** No key, no browser, no login |
| Manpower Norway (Norway) | `manpower-no.md` | **Shipped — #368, the staffing network's Norwegian front: 96 jobs named by its sitemap on 2026-09-14, the inventory where the search states no count a client reads; each job page read — JobPosting (compact dates, the county and the town in each other's field, emitted as written), the labelled list, the body.** The agency as employer on every ad, the client never named; **the body scrubbed.** No key, no browser, no login |
| Adecco Finland (Finland) | `adecco-fi.md` | **Shipped — #380, the same platform: `adecco.py --host fi` — 74 ads in `sitemap-jobs-finland-fi.xml` on 2026-09-14.** The consultant's e-mail in the description scrubbed. No key, no browser, no login |
| Albedis (Switzerland) | `albedis.md` | **Shipped, and #189 recorded this host as unstructured.** It is not: **every advertisement carries a `JobPosting`** and a plain `json.loads` reads none — the malformation is a type confusion, mended in `_ldjson` since `ed57b58`, so a parse failure was read as an absence. **95 advertisements, each in four languages, 380 `<loc>` matched 380–0.** `hiringOrganization` is the AGENCY on every one measured — the ads say *«Notre client»* — so it ships as `depositor`, not employer. *No running total is declared, and `95 × 4 = 380` checks the sitemap against itself* |
| État de Genève (`ge.ch`) | `ge-ch.md` | **Shipped.** One employer — the canton's own list — and admissible for that (#204: an adapter also serves to read ONE segment). **82 advertisements on a single server-rendered page**, every advertisement page carrying a `JobPosting` in JSON-LD with `experienceRequirements`, the field an aggregator's card does not carry. **No browser, no key**; two requests for the whole sweep, the RSS feed as the anchor (same 82 ids). Five filters from the site's own form — contract, department, salary class, rate, domain — each shown to reduce. Three shapes of the entity block on one page; «À définir» is a salary class; `jobStartDate` is the day of the read when the page says «Dès que possible» |
| Randstad France | `randstad-fr.md` | **Shipped.** **6 755 ads**, from the three job-detail sitemaps `robots.txt` declares. **No browser.** Better than its sibling on every axis: postcode on every ad, the town in the URL matches the ad 22 of 22 so `--ville` is free, `EUR`, `CONTRACTOR`, and **no `validThrough` at all** rather than a formula. Its `ld+json` tag uses **single quotes** — a double-quote pattern reports `json_ld: false` on every ad, so the adapter errors when a page says `JobPosting` and none parses. Employer is the agency, as ever |
| Randstad Czechia (Czechia) | `randstad-cz.md` | **Shipped — #357, the staffing network's Czech front on the French platform: `randstadfr.py --host cz` — 348 ads in the Czech job-detail files on 2026-09-14 (344 public, 4 internal), the `/en/` copies of the same ads set aside.** The agency as employer on every ad; **the consultant the description names scrubbed (a correction for France too).** No key, no browser, no login |
| Grafton Czechia (Czechia) | `grafton-cz.md` | **Measured, no adapter — route none (2026-09-14): the list is a Vue app querying an Elasticsearch index on `search.skinner.freely.agency` with a read-only login the page hands every visitor — a credential that is not the user's, not used without the owner's decision; the sitemap the rules name is dated 2026-02-25 and its newest job is archived.** The job pages are readable but nothing names the live ones (#404). One decision covers the Slovak front |
| Grafton Slovakia (Slovakia) | `grafton-sk.md` | **Measured, no adapter — route none (2026-09-14): the same backend, index and embedded login as the Czech front (`data-domain` tells them apart); the sitemap dated 2023-09-05, its last page without a job row.** The owner's call on the embedded login is named on the card |
| Randstad Hungary (Hungary) | `randstad-hu.md` | **Shipped — #363, the same platform: `randstadfr.py --host hu` — 364 ads in the Hungarian job-detail files on 2026-09-14 (363 public, 1 internal), the `/en/` copies set aside.** «Kapcsolattartó / Information» — the consultant's e-mail and telephone in the description — scrubbed. No key, no browser, no login |
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
| Expresso Emprego (Portugal) | `expressoemprego.md` | **Shipped.** The daily Expresso's board — **1 917 advertisements, stated by the site on every listing page and following every filter** (469 for Lisboa, 2 for `jurista`), 15 a page, the search routed by path segments read off the site's own JS. **The declared sitemap is a fossil**: 1 513 advertisement URLs, every one with a `lastmod` of 2019 — never read. The site's zero is a sentence, read as such; the «Oops» page is a 200 with no row and dies. **No browser, no key**; no `JobPosting` on the ad page, the text is HTML |
| Net-Empregos (Portugal) | `net-empregos.md` | **Shipped.** Portugal's first adapter. The host declares **seven sitemaps and serves two**: `rss.asp` — **1 000 items, the employer on 1 000 of 1 000**, zone, category, date — and `Sitemap.asp`, **5 000 advertisement URLs**; **four answer the home page with a 200 and 71 KB**, and only the count of items extracted sees it — the adapter dies through `empty_first_page` and says «HOME PAGE». RSS ⊂ sitemap (1 000 of 1 000). **No browser, no key.** The ad page carries a `JobPosting` **whose `datePosted` is the reader's clock** (15:24 then 15:25 on two reads a minute apart) — emitted as `rendered_at_as_datePosted`, never as a date; the date is the feed's. Filters compare to the feed's own spelling and print it when they empty |
| Jobindex (Denmark) | `jobindex.md` | **Shipped — page 1 only, by the site's own rules.** Denmark's first adapter. The board states **37 600 ads** in its header and **8 949** for `udvikler` as `hitcount`; the adapter returns **20 per query** because `Disallow: /jobsoegning*page=` is written on `www` — bound 1, honoured. **No browser, no key.** The data is a JSON the search page embeds (`Stash`), twenty objects with a stable `tid`, headline, employer, area, `firstdate`/`lastdate`, deadline. **The apex `jobindex.dk` publishes `Disallow: /`** — every URL is built on `www`. The sitemaps hold **7 181 `<loc>` and zero ads** (the ads sitemap is an honest empty `<urlset/>`); the ad has two pages and neither carries a `JobPosting` — the full Danish text is read from `/jobannonce/<tid>/<slug>` through the canonical `/vis-job/<tid>`. Filters shown to reduce: 8 949 → 502 on an area path |
| Platsbanken | `platsbanken.md` | **Shipped.** **39 865 ads offering 67 109 posts** — Arbetsförmedlingen, Sweden's public employment service, through the JobTech Dev open API. Sixth national public service here, first Swedish adapter. **No browser, no account, and no key at all** — an open-data product of the state. **The richest record in the repository**: a full description, an application deadline on 300 of 300, coordinates, and **`organization_number`, a legal company identifier no other board publishes** — the cross-board dedup key the ledger has never had. Two honesty points: the salary states its **type** on 300 of 300 and its **amount on 0 of 300**; and the structured `must_have` requirement schema, which nothing else here has, is filled on well under a fifth of ads. **The window is 2 100 of 39 865** — a place alone overflows, a field alone overflows, it takes two — but unlike Germany it refuses with a 400 instead of truncating |
| Personio | `personio.md` | **Shipped.** One employer at a time, by tenant — **the DACH ATS**, and the one most German, Austrian and **Swiss** SMEs run their careers page on. **No browser, no account, no key**, and no window: one request returns the whole board with descriptions **already split into the employer's own named sections**. Its trap is the sharpest of its kind: **`?language=fr` returns the same 7 positions with the same ids and 0 of them carrying any text** — same count, HTTP 200, valid XML, no error — so the adapter fetches both feeds and refuses a language whose text has gone. `<value>` is CDATA-wrapped, a second independent sighting of issue #55's wrapper in a new element. `additionalOffices` is a sibling element on 2 of 7. No salary, no closing date, and **no tenant directory** — ask for the URL |
| Recruitee | `recruitee.md` | **Shipped.** One employer at a time, by tenant — a European ATS (NL, BE, DE, PL). **No browser, no account, no key**, and one request returns the whole board with descriptions; 145 offers in 454 KB on the largest tenant measured. **A real salary figure on 133 of 238** — better than every national board here except SwissDevJobs — but `period` is **`month`** on 124 of them, so a figure read as annual is wrong by twelve. Two traps that generalise: **`country` is written in the tenant's own language** and the values mix inside one sweep (*Nederland*, *Duitsland*, *Switzerland*), so only `country_code` is a key; and **`remote`/`hybrid`/`on_site` are three overlapping booleans**, not an enum — treating them as exclusive misclassifies 51 of 238. `requirements` is a separate field from the description. `close_at` exists and is set on 0 of 238 |
| Pinpoint | `pinpoint.md` | **Shipped.** One employer at a time, by tenant — **the 5th most common ATS in a 360-card HiringCafe sample**, ahead of ADP and Taleo. **No browser, no account, no key.** Its trap is a pair of endpoints: `postings.json` (publications) and `jobs.json` (requisitions) have **disjoint id spaces**, and on one tenant both return 281 — equal counts that would convince anyone they are two views of one list. Fifteen requisitions in 684 postings are published more than once. `province` holds *London*, *United Kingdom*, *Maharashtra*, *Bolton* and *uk* in one field. **Where it gets things right, and few do**: `compensation_visible` actually tracks the figure (337 flags, 333 amounts), and `workplace_type` is a real enum where `recruitee.md` has overlapping booleans. `key_responsibilities` is a separate field on **684 of 684** |
| Oracle Recruiting Cloud | `oraclecloud.md` | **Shipped.** One employer at a time, by host — **the biggest ATS family the repo did not cover**: 164 cards of 2 838 across twelve countries, and one of four families present in *all twelve*. **No browser, no account, no key**, and the whole board is reachable — no window. Four traps: without `expand=requisitionList` it reports **1 428 jobs and returns none**, in valid JSON with a 200; **`siteNumber` does nothing** and a bogus value returns the same board as the right one; the field named **`Distance` is the posting date** in milliseconds, identical on 100 of 100; and the ad URL is built from `SiteURLName`, not `SiteNumber` — while the first site listed can be the INACTIVE one. `ShortDescriptionStr` repeats the title on 88 of 100; the real text needs the details resource, one request per job |
| StepStone | `stepstone.md` | **Shipped.** **One platform, eleven domains, six inventories, six countries** — Totaljobs, Jobsite, Caterer, IrishJobs, NIJobs, Jobs.ie and StepStone DE/AT/BE/NL run the same bundle, the same card contract and the same ad schema, told apart by `siteId` alone. **No browser, no account, no key.** Its headline finding is a **result list padded with ads that do not match**: the page's own analytics payload splits the total into `main`, `semantic` and `regional`, and **stepstone.nl holds 1 literal match for *software developer* while serving a full page of 25 cards** — 497 of 607 on .be, 796 of 1 862 on a located Totaljobs search. Nothing in the markup marks them. **A request can also fail with no HTTP status at all** — `HTTP/2 INTERNAL_ERROR` cold, a read timeout after a burst — so the script speaks HTTP/1.1, warms the host, retries once and then declares the sweep truncated. Depth is a **per-site** robots ceiling, four different regimes; **CWJobs is not a board** (50 of 50 cards link to totaljobs.com); Jobsite hides its ad URLs behind a disallowed `/tp-out`, so the id is rebuilt from the card. Salary is a two-state absence: **not rendered at all on the four StepStone sites**, and on IrishJobs present but saying `€ Not Disclosed` on **73 of 100** cards. `validThrough` on 108 of 108 ads |
| MyCareersFuture | `mycareersfuture.md` | **Shipped.** **96 778 ads of 96 869 reachable — the whole corpus**, Singapore's national portal (SWDA). **No key, no cookie, no account, no browser**, and a `robots.txt` of 87 bytes with an **empty `Disallow:`**. Also **the most restrictive adapter here**: SWDA's terms forbid storing Website Content "in a retrieval system" and prohibit caching, so the card carries identifiers, URLs and scoring fields and **never the text of an ad** — `description_chars`, then read it at its URL. Its trap is a filter that lies by silence: **an unknown parameter *name* is accepted, ignored and answered 200** (`employmentType` singular returns the whole board, `employmentTypes` returns 71 850 of 97 091) while an unknown *value* is a loud 400 — `total == countWithoutFilters` is the only tell. **`Re-open` is a fifth of the board** and sits deep in a newest-first sort, so `status == "Open"` silently drops it. Salary on 997/997, all monthly; closing date on 997/997; **the employer named on ~5%**. The sitemap index declares six files, **two are 7 923-byte HTML skeletons named `.xml`** |
| Kalibrr | `kalibrr.md` | **Shipped.** **Two countries in one adapter** — **1 116 Indonesian and 777 Philippine ads, 2026-09-08** (1 045 / 778 on 2026-09-02). Public JSON, **no key, no cookie, no browser**; `robots.txt` is 59 bytes of `text/plain` closing two non-job paths. **A search that matches nothing is answered with somebody else's ads**: `country=Singapore` and `text=zzzzqqqq` both return **the same 818**, HTTP 200, full payload, and the only sign is the boolean `from_alternative`. **No country at all returns that same 818 — smaller than either market** — so the default is the fallback set, not the board; `--country` is required and a substituted response is refused, not scored. **Salary is converted to pesos and mislabelled**: Indonesian ads carry `salary_currency: "PHP"` with twelve-decimal floats, and only the older `/api` endpoint keeps `salary_currency_orig: "IDR"` — so the card emits `salary_php_min`, never `salary_min`. `salary_shown` is true on 88% while **20% carry a figure**. Employer named on 1 139/1 139 and a real closing date on 1 139/1 139 |
| JOBBKK | `jobbkk.md` | **Shipped.** Thailand's largest board, **no key, no cookie, no browser** — `robots.txt` is 275 bytes of `text/plain` closing CVs, uploads and `/jobs/apply/`, and naming no AI agent. **The listing is the payload**: the Next.js flight data carries the whole record for all 25 cards, so one request buys 25 ads. Its trap is the end of results — **page 5 000 answers 200 with page 5's ads**, identical, for ever; there is no 404 and no empty list, so the sweep stops on repetition. The HTML of a page showing 25 ads also contains a hidden **'no position found'** message. `created_at` runs back to **2010** while `updated_at` is 2026 on 133 of 133 — read `refreshed`, not `created`. Salary is stated on **59%**, the best rate in this repository — but `salary_not_show` asks for 17 of them to be hidden and the payload sends them anyway, so **the adapter withholds those** |
| Adzuna | `adzuna.md` | **Shipped.** **One API, nineteen countries** — ch fr de at be nl it es pl gb us ca au nz in sg za br mx — and **the smallest budget here: 250 calls a day for everything together**, 25 a minute, with `results_per_page` **silently capped at 50**. Needs a free self-service key, read from `~/.adzuna.env` and the environment only. **The description is a 500-character teaser** by design, so this is discovery, not scoring: the text is at `redirect_url`, where the terms require the user to be sent. **`salary_is_predicted` means Adzuna's estimator wrote the figure, not the employer** — 6 of 16 salaried GB ads — so the card separates `salary_min_stated` from `salary_min_adzuna_estimate` and has no `salary_min` at all. Errors are **HTML, not JSON**: 400 with no key, 503 under load, the same page; bad keys are 401 where the spec says 410. Coverage is uneven by language — on Switzerland `Entwickler` returns 12 666 and `développeur` returns **0** |
| Computrabajo | `computrabajo.md` | **Shipped.** **Eighteen Latin American countries, one adapter** — and one `robots.txt`, **874 bytes, md5 identical on all eighteen with no exception**, the most uniform family measured here. **No key, no cookie, no browser**; Colombia alone carried 74 399 offers. The rule file **closes the filters and leaves the search open**: every disallowed listing rule names a query parameter — `sal=`, `pubdate=`, `cont=`, `dis=`, `by=` — while `q=` and `p=` are not among them, so the adapter searches and pages and **refuses to build the site's own filters**, quoting the rule. **No `JobPosting` anywhere** — the only `ld+json` is Computrabajo's own `Organization` graph — so it is DOM extraction on `article.box_offer[data-id]`. Employer named on 69 of 80, **salary on 0 of 80**, and every date is relative with no timestamp behind it. Pagination **ends honestly**. In Colombia the public API's origin URL carries this board's own 32-hex id on **484 of 484** measured entries, so the two join by string parsing with no request — the overlap's size is **not** established, since the corpus is grouped by operator (83.5% on the first pages, 0% on page 900). Enable one until the join is built |
| Jobstore | `jobstore.md` | **Shipped, hybrid.** 26 country sites on one host; Switzerland carries **52 128 ads**. **Discovery is plain HTTP, reading an ad needs the browser** — the ad page answers a plain client with 403 and a "Just a moment…" interstitial while the sitemaps and the search page answer 200. Its first trap is arithmetic: the sitemap index declares twelve files and **only the six `job-*.xml` are ads**; summing every `<loc>` reports **250 000+ Swiss ads instead of 52 128**, silently. The search page's `ItemList` carries **URLs and nothing else**, so the HTTP half yields an id and a slug — the card says `title_from_slug` and `needs_browser_to_read`. The ledger URL is a **Jobstore** URL, marked as such, never the employer's. And the button reading **"Apply on company site" links to `/jobseeker/apply/` on jobstore.com** — applying needs a Jobstore account, and the plugin corrects the label instead of repeating it. Overlap with the covered Swiss boards is ~25% HiringCafe, 18.6% jobs.ch, 15.5% jobup |
| iCIMS | `icims.md` | **Shipped.** One employer per site, **no key, no cookie, no browser** — and the family four country surveys named as the commonest one missing here. **The default ad URL is not the ad**: the bare `/jobs/<id>/<slug>/job` answers 200 with 90 KB of the employer's portal and no `JobPosting`, while `?in_iframe=1` returns it — and **the sitemap publishes the bare form**, so an adapter written the obvious way reports an empty board. **The same id is a different vacancy on every host** and the wrong host answers 200, so the key is `icims:<host>:<id>` — the mirror of the Workday defect, and the worse half: one key, two ads. Three host shapes including the employer's own domain (3 of 10 sampled ads), and **the platform host is read from the page, never built** — the prefix has been `careers-`, `apply-`, `field-` and nothing. **The first adapter here to read a tenant's `robots.txt` at run time** (issue #73): two of six hosts refused everything |
| Eightfold | `eightfold.md` | **Shipped — #451, an ATS family read one employer at a time (`--host`, the tenant the user names): the JSON route the tenant's own page calls, `count` as the count it states.** `bayer.eightfold.ai` (= `talent.bayer.com`): **602 emitted over 61 pages of 10, tenant states 602 — equal** (2026-09-14); `num` capped at 10 by the server; the employer's `domain` read from the careers page. **Two shapes of tenant**: `micron.eightfold.ai` answers the same route with 403 «Not authorized for PCSX» — named, exit 7, a second shape to measure. `country` null, the location text says which; descriptions reduced to text, contacts withheld, the apply route never followed |
| Vieclam24h | `vieclam24h.md` | **Shipped.** One of Vietnam's largest boards, **no key, no cookie, no browser** — results in the page's own `__NEXT_DATA__`, 30 a page, and a sitemap of **17 089 ad URLs**. **The richest record here — 110 fields — and the one that most needs an allow-list**: `employer_info` (the board's own named account manager) and `contact_name`/`email`/`phone`/`address` are filled on **90 of 90** ads, so the card names the sixteen fields it emits and copies nothing else. Dropping `employer_info` by name would have left four of the five behind. **Salary counted on values**: the pair is a key on 100% and a figure on **98.9%**. A bare request answers **403** and the same URL with `Accept`/`Accept-Language` answers 200 — header sniffing, not a bot wall |
| PhilJobNet | `philjobnet.md` | **Shipped.** The Philippines' public employment service (DOLE), **5 145 vacancies**, employer named on every card, **no key and no browser** — the **eighth national public service** here. Its trap is the purest `never-fail-silently` case yet: **`?page=2` is accepted, ignored, and answers 200 with page one**, so an adapter written the obvious way loops for ever over the same ten ads while reporting a complete sweep. Pagination is an ASP.NET WebForms postback whose `__VIEWSTATE` must come from the last response, and **the check that matters is that a page's ids do not intersect the previous page's** — not that it answered 200. Two more found while writing: **each card's anchor sits before its block**, so a naive parse pairs every title with the next ad's id (`slug_matches_title` keeps the check in the row); and **`www` presents Azure's default certificate** while the apex serves the site — the TLS case from `robots-policy.md`, exercised for the first time |
| Applifly | `applifly.md` | **Shipped.** A Swiss ATS, one employer per vanity domain — **recognised by the path, never by the host**. **No key, no cookie, no browser**, and the ad carries a full `JobPosting` **in microdata rather than JSON-LD**, coordinates on 8 of 8. **A `source=` parameter that reads as tracking is what renders the page**: without it the same URL answers `200` with 718 bytes of referrer-capture JavaScript |
| Bumeran / Jobint | `bumeran.md` | **Shipped, hybrid.** **Eight Latin American brands on one platform, 71 483 ads** — Peru, Chile, Argentina ×2, Ecuador, Panama, Mexico, Venezuela — found by the shape and not by a marker: `zonajobs` renamed its sitemaps to `_zj` and `404`s on `_bum`, so a search for the family's own signature could never have found it. **Discovery is plain HTTP and rich; reading an ad needs the browser** — the ad page is 64 KB of React shell with 56 characters of text, and `/api/` is blocked at the edge. Yields ad URLs, ids, slugs and **the board's own language-independent facet vocabulary** |
| Encuentra24 | `encuentra24.md` | **Shipped.** Central American and Caribbean classifieds with a real jobs section — **twelve countries on one host**, as `/<country>-<lang>/` prefixes **read from `robots.txt` rather than composed** (`dominican-en` sits beside `dominicana-es`). **No key, no cookie, no browser**, a full `JobPosting` in JSON-LD on every ad — and **past its last page it serves page one with `200`**, so the sweep compares every page against the first |
| HR.ge | `hr-ge.md` | **Shipped.** Georgia's main board and **five sibling brands on one API**, discovered from a tenant number in `robots.txt`. **No key, no cookie, no browser.** And three corrections to this repository's own record, all the same shape: **1 062 ads, not 39 247** — 36 593 `<loc>` are employer pages; **`career.ge` has no ads at all** and was credited with hr.ge's corpus because its robots.txt declares hr.ge's tenant; and the listing serves **800 links for 281 ads** |
| jobs.ge | `jobs-ge.md` | **Shipped.** Georgia's independent generalist — **the whole board in one request**, 308 live ads and **no pagination at all**. **No key, no cookie, no browser**, and `robots.txt` publishes `Crawl-delay: 5`, which the adapter uses as a value read rather than chosen. **The site declares its own stub**: 11 English pages in 12 carry one sentence pointing at the Georgian text — **and the twelfth is the mirror**, so the adapter follows the pointer instead of trusting a language |
| ss.ge | `ss-ge.md` | **Shipped, enumeration only — on purpose.** Georgia's largest classifieds: **1 705 job ads found without fetching one advertisement page.** **Three hosts and three different `robots.txt` files**, the permissive one on the host you are redirected to; the board itself answers `403` behind a Cloudflare challenge, **and a challenge that asks for a click is a stop**. Discovery runs on the unchallenged apex, through a jobs sitemap declared only by the subdomain's robots.txt and absent from the apex's own index |
| LMIS Jamaica | `lmis-jm.md` | **Shipped.** Jamaica's public employment service — **the whole board in one request**, 16 ads, no key and no browser. **The first in this series whose access is not refused, and the permission is accidental**: its `robots.txt` is Drupal's shipped default and says nothing about vacancies — the mirror of `empleate.gob.hn`, where a file copied from Google's documentation forbids them. **And its endpoint accepts every filter and applies none**, so the adapter offers none |
| BNE Chile | `bne-cl.md` | **Shipped.** Chile's national employment service — **7 928 ads, and a sitemap in which every entry is one**. **No key, no cookie, no browser**: the search renders client-side, the ad pages do not and carry a `JobPosting`. **And the board is not UTF-8** — `decode("utf-8", "replace")` loses 37 to 93 characters an ad without failing, which is why `_decode.py` exists |
| Emploitic | `emploitic.md` | **Shipped.** Algeria's generalist board. The operator **names this project in its own rules file**, which is the most explicit permission the repository holds |
| EmployTT | `employtt.md` | **Shipped.** Trinidad and Tobago's public employment service. **The status code cannot be the check** — a withdrawn advertisement still answers 200 |
| JobIvoire | `jobivoire.md` | **Shipped.** Côte d'Ivoire's generalist board. **227 of 3 884 sitemap entries are advertisements**, and the freshest was five weeks old when measured |
| NEXT (jobs.gov.pk) | `jobs-gov-pk.md` | **Shipped.** Pakistan's federal job portal. **The same counter label carries different numbers on two pages** — read the data, never the counter |
| Mihnati | `mihnati.md` | **Shipped.** Saudi Arabia. **Ten ads out of ten quote `PKR` on Saudi jobs** — a currency field that is not the country's |
| ONAPE (Chad) | `onape.md` | **Shipped.** Chad's public employment service. **30 advertisements, and its sitemap says 32** — one is listed three times. No key, no browser; the employer field is empty on every advertisement and is emitted as `null` |
| Ergodotisi (Cyprus) | `ergodotisi.md` | **Shipped.** **2 644 advertisements, and the sitemap says 5 302** — every one appears under `/en-CY/` and `/el-CY/`, and the two are the same document with a different `lang`. The only count in the series with an independent witness: the site's own "2 573 open jobs" |
| Keejob (Tunisia) | `keejob.md` | **Shipped.** **808 advertisements, all within thirty days, no duplicates** — the sitemap held 827 eleven hours earlier and converged on the site's own counter, which reads 808 in two places — the only readable board of eight Tunisian ranks. Salaries in `TND` where given; `employmentType` is `OTHER` on every advertisement and is not emitted |
| Rozgar (Pakistan) | `rozgar.md` | **Investigated, not countable.** Third brand of the same house. **Sitemap of three URLs, frozen since 2020**, on a site in production; homepage 327 kB with zero `JobPosting`. `content: indeterminate` — not disqualified, not qualifiable, and the card says which two paths were looked at. Blue-collar where `rozee.pk` is white-collar, so it is not a mirror |
| Enbek.kz (Kazakhstan) | `enbek-kz.md` | **Investigated — every listing route refused in writing.** The state employment portal; the rules are read and certain, open on the root and on a single vacancy page, **`Disallow: /*/search/*` and `/*/вакансии/*` to everybody** — no sitemap (`/sitemap.xml` redirects to the home page), no API. A written refusal binds every route, browser included, so this is not the #222 case. Five site counters on two pages (133 556 «work places», 44 521 ads, 78 421 posts …) that are not one quantity; the card chooses none. No script; the first Kazakh host here |
| Rozee (Pakistan) | `rozee.md` | **Investigated, not built.** Found because `mihnati.com` declares *its* sitemap index. The index holds **4 292 URLs of which 1 685 are not advertisements**, and of the 2 607 in `jobs.xml` the readable order of magnitude is **52** — the `.php` form serves a `JobPosting` 4 times out of 4, the rest 0 out of 4. **Last `lastmod`: 7 June 2026**, so it is an archive. `postalCode: 54000` — Lahore — is stamped on advertisements from other cities |
| KosovaJob (Kosovo) | `kosovajob.md` | **Shipped, and the larger of Kosovo's two.** **566 advertisements from one request**, 516 distinct slugs, 391 employers, 0 unreadable; no sitemap declared, none composed. **It shares ofertapune's markup and not its database** — the same advertisement leads both homepages, and its id is `109849` there and `47268` here. **148 advertisements are on both**, slug match confirmed on the employer 148 of 148, so the two boards do not add up to 1 047. Two places where the shared template diverges and both bite: `jobListExpires` is a countdown (`15 ditë`) here and a date there, and `ids=` is a position counter here and the ad's id there |
| Oferta Pune (Kosovo) | `ofertapune.md` | **Shipped, and Kosovo's first adapter.** **481 advertisements from one request** — no sitemap is declared and none was composed; the homepage carries every row server-rendered, with the board's own numeric id, and 0 of 481 blocks unreadable. **The only date is a deadline**, so no `--since` is offered: a filter on a posting date this board does not publish would return everything in silence. **No `ld+json` and no `JobPosting` anywhere** — the first board here parsed from Albanian class names. Its neighbour `kastori.net` has a sitemap of 24 application routes and **not one advertisement**, frozen 16 months, on a client-rendered export |
| Yellocu (Cuba) | `yellocu.md` | **Not a job board — and that is the finding.** Cuba's country page ranked it 5th among the country's job sources, «ouvert — à construire». It calls itself *Local Business Network in Cuba | Online Business Directory*, and its homepage carries **0 occurrences of `empleo`, `trabajo`, `oferta`, `vacante`, `curriculum` or `contratar`**; its categories are Restaurants, Doctors, Hotels. The rules open and the host answers: the object is not advertisements. *The verdict of «is this a board» is taken by fetching, not by guarding* |
| Revolico (Cuba) | `revolico.md` | **Rules open, transport serves a challenge — and that is where the browser branch stops.** `Allow: /` with five account paths refused; the root answers 403 with a 5 642-byte `Just a moment...` interstitial. **Fetched twice before any comparison**: same size, different md5, `cf-ray` in the body — so the fingerprint is void across hosts, and filing it as this operator's own refusal page would have been the opposite of the truth. Unlike `kariera-mk`, **not** a browser candidate: the 07.09 reversal forbids asking the plugin's user to defeat an anti-robot control |
| Mabumbe (Tanzania) | `mabumbe.md` | **Rules open to `Claude-User`, transport serves a challenge.** The Cloudflare managed file names `ClaudeBot` and leaves `*` open; under the 2026-09-07 decision the permitted token exists and was tried — **4 paths, 4 × HTTP 403 with a 5.6 KB `Just a moment...` interstitial, md5 moving at constant size**: the `revolico` family, where borne 2 stops the browser branch. The site's «44 156» is a WordPress archive counter; if the host opens, the anchor is live vs archive. No script; the first Tanzanian host here |
| Forasna (Egypt) | `forasna.md` | **Rules open to `Claude-User`, a challenge on every path — the sitemap included.** The Cloudflare managed file, `ClaudeBot` named, `*` open, no `Sitemap:` line; the root and two guessed sitemap paths all answer 403 «Just a moment...» with a moving md5. Where its sibling `wuzzuf.net` serves its XML from behind the same interstitial, this host does not — no inventory, no script. Not a verdict of closure |
| Emploi Bénin (Benin) | `emploibenin.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root answers a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure | **Browser measured 2026-09-13 16:36 UTC: served to a tab — 177 distinct over eight pages, site states 177, equal. `route: browser · 177`**
| Job Cameroun (Cameroon) | `job-cameroun.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root answers a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure | **Browser measured 2026-09-13 16:38–16:48 UTC: NOT an AfricaWork host — a classifieds-style board behind the same vendor 403; served to a tab, one-based pager of 20, 3 982 distinct over 200 pages, site states 3 982, equal; a JobPosting per advertisement, applications by WhatsApp. `route: browser · 3982`**
| Emploi.cm (Cameroon) | `emploi-cm.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root answers a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure | **Browser measured 2026-09-13 16:35 UTC: a challenge to the tab too («Un instant…», not lifted in 10 s) — borne 2, `route: none`; its four sisters were served the same ten minutes**
| Sudan Careers (Sudan) | `sudancareers.md` | **Reopened by the 2026-09-07 doctrine, and the transport answers a challenge.** `ClaudeBot` named, `*` open — `identity()` says `claude-user` — and the root answers 403 «Attention Required! \| Cloudflare» with a moving md5: the `revolico` family, where borne 2 stops the browser branch. Not a verdict of closure | **Browser measured 2026-09-13 16:55 UTC: served to a tab, no challenge — 25 + 3 = 28 distinct, site states 28, equal. `route: browser · 28`**
| Emploi Sénégal (Senegal) | `emploisenegal.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root answers a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure | **Browser measured 2026-09-13 16:37 UTC: served to a tab — 173 distinct over seven pages, site states 173, equal. `route: browser · 173`**
| Duapune (Albania) | `duapune.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root answers a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Emploi.ci (Côte d'Ivoire) | `emploi-ci.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Emploi.cd (DR Congo) | `emploi-cd.md` | **Reopened by the 2026-09-07 doctrine, and the transport answers a challenge.** `ClaudeBot` named, `*` open — `identity()` says `claude-user` — and the root and a listing path answer 403 «Attention Required! \| Cloudflare» with a moving md5: the `revolico` family, where borne 2 stops the browser branch. Not a verdict of closure | **Browser measured 2026-09-13 16:35 UTC: served to a tab, no challenge — 70 distinct over `/recherche-jobs-congo-rdc?page=0…2`, site states 70, equal; six addresses without a trailing id, keyed by path. `route: browser · 70`**
| RwandaJob (Rwanda) | `rwandajob.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| SierraLeoneJob (Sierra Leone) | `sierraleonejob.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Emploi.ga (Gabon) | `emploi-ga.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| EmploiGuinée (Guinea) | `emploiguinee.md` | **Reopened by the 2026-09-07 doctrine, and the transport answers a challenge.** `ClaudeBot` named, `*` open — `identity()` says `claude-user` — and the root and a listing path answer 403 «Attention Required! \| Cloudflare» with a moving md5: the `revolico` family, where borne 2 stops the browser branch. Not a verdict of closure |
| JobGuinée Pro (Guinea) | `jobguinee-pro.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Staff.am (Armenia) | `staff-am.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Cyprus Work (Cyprus) | `cypruswork.md` | **Shipped — reopened by the 2026-09-07 doctrine, and the first host of #233 whose transport answers.** One sitemap of 10 708 `<loc>` holding **1 475 distinct advertisements** beside 8 874 company pages (counting the file would report the board 7× larger); `/jobs/` states the same 1 475 in its `<h1>`, printed beside the count — «equal», or «k short». `<lastmod>` is one value on all, a rebuild stamp measured each run; `JobPosting` JSON-LD on 10 of 10, `baseSalary` present on 9 and empty on all 9, `validThrough` = `datePosted` + 60 days. Greek or English per advertisement, read from the script. No key, no browser; two requests |
| CyprusJobs (Cyprus) | `cyprusjobs.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| INFOTEP (Dominican Republic) | `infotep.md` | **Reopened by the 2026-09-07 doctrine, and the transport answers a challenge.** `ClaudeBot` named, `*` open — `identity()` says `claude-user` — and the root and a listing path answer 403 «Attention Required! \| Cloudflare» with a moving md5: the `revolico` family, where borne 2 stops the browser branch. Not a verdict of closure | **Browser measured 2026-09-13 16:55 UTC: served — and it is the national vocational-training institute (Joomla, «oferta formativa» = courses, «Plazas Vacantes» = its own hiring), not a board; `/empleo` is a 404. `route: none`, out-of-domain**
| AlgérieJob (Algeria) | `algeriejob.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| 3amal (Egypt) | `3amal.md` | **Reopened by the 2026-09-07 doctrine, and the transport answers a challenge.** `ClaudeBot` named, `*` open — `identity()` says `claude-user` — and the root and a listing path answer 403 «Attention Required! \| Cloudflare» with a moving md5: the `revolico` family, where borne 2 stops the browser branch. Not a verdict of closure |
| GjejPunë24 (Albania) | `gjejpune24.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Albania Jobs (Albania) | `albaniajobs.md` | **Shipped — Albania's first adapter, on a host read as closed for refusing `anthropic-ai`, a name we never send.** WordPress + WP Job Manager, `Crawl-delay: 10` honoured: the REST collection is the route — **123 advertisements**, 123 distinct post ids — and the job sitemap the check, «123 emitted, sitemap lists 123 — equal»; region and type term counts sum to 123 too. The URL carries no id (a leading `13` on most); the post id is the key, read back from the page's `JobPosting`. Employer on the page, not in the collection; salary fields exist and are empty on all 123. No key, no browser; six requests at ten seconds |
| foundit Gulf (Gulf + Egypt) | `founditgulf.md` | **Shipped under a recorded condition — a hand-written `ClaudeBot: Disallow /jobs/ /search/`, `Claude-User` under `*`, and the adapter never reads those two paths.** Three active-jobs sitemaps, **58 930 distinct advertisements** — AE 29 360, SA 13 600, **EG 12 080**, QA 2 215, KW 777, BH 263, OM 32 by the slug — today's sitemap (1 041) checked against them each run; the root's «Over 800,000+ jobs» printed as a slogan, never compared. `JobPosting` on 10 of 10, dates `DD-MM-YYYY` emitted as published and as ISO, the country from each advertisement, no salary field at all. No key, no browser; four to six requests. Since 2026-09-13 `--host www.foundit.com.ph` reads the Philippine franchise too (`foundit-ph.md`) |
| GulfTalent (UAE and the Gulf) | `gulftalent.md` | **Shipped, on the day it was measured as a #222 browser candidate — and the declared client is served on every path.** `ClaudeBot` and `anthropic-ai` under «Blocked — AI training crawlers», `Claude-User` under `* Allow: /`; one country edition per run (`/uae/jobs/N`, 25 rows a page, past the end a 404). **Two address shapes on one page** (`…-632616`, `…_632494`) — a hyphen-only pattern emitted 21 of 25 with no symptom. The page states its count twice («N Jobs found» and a cached `job_count`, one apart on 2026-09-13) — both printed, neither corrected; the witness is the pager closing under the reader (**15 681 emitted over 628 pages, site states 15 681 — equal**, 2026-09-13 15:22 UTC). `ad` reads the page fields on both shapes and the JobPosting on the hyphen one only. No key, no browser; ~630 requests for a full UAE walk, 2 s apart |
| Nationale Vacaturebank (Netherlands) | `nationalevacaturebank.md` | **Shipped, on the day it was measured as a #222 browser candidate — served to the declared client, its search refused in writing and never taken.** `*` refuses every queried or paginated listing (`/vacature/zoeken?*`, `/vacatures/*?page=`); `ClaudeBot` named and refused, `Claude-User` under `*`. The route is the declared advertisement sitemap — an index whose one element carries two `<loc>` on the apex host — **89 733 distinct uuids, and of 40 drawn at random 24 served, 12 answered 410, 4 answered 404** (2026-09-13 15:31 UTC): the file lists what has left the board, and `--sample K` prints that proportion as the witness. The site's «88.909 banen» is rendered in a tab from the API behind the refused search — not taken, not copied. A full JobPosting per page (EUR/MONTH, hours, experience). No key, no browser; three requests plus the sample; **since #295 the recruiter's e-mail (`hiringOrganization.email`) is not a field, and `--host intermediair` reads the sister board** |
| Pracuj.pl (Poland) | `pracuj.md` | **Measured browser route — the declared client meets a Cloudflare challenge (403, «Just a moment...», md5 moving), the tab is served.** Rules open and naming no one. **The pager closes at page 926 — 925 × 50 + 17 = 46 267, equal to the page's own `groupedOffersTotalCount`**; the same page states 59 534 offers (a group once per location) and «78 403» in its heading, which is 59 534 + 18 869 JobCenter offers by addition — three figures, none corrected (2026-09-13 16:22 UTC). A JobPosting per advertisement (`@content` for `@context`, salary null on the one read). Sitemaps declared, not tried by HTTP |
| OLX Poland (Poland) | `olx-pl.md` | **Measured browser route — 403 to the declared client, served to a tab.** «Znaleźliśmy ponad 1000 ogłoszeń» — a floor — on a listing that loops at 25 pages × ~52; **40 categories state 83 725 between them, a sum and a bound, ten of them above the 1 000 a page walk can reach** (2026-09-13 16:27 UTC). `route: browser · 1000`. The JSON API the page calls was not tried; if it answers the declared client, that is an HTTP route and its `adapter` issue |
| OLX Kazakhstan (Kazakhstan) | `olx-kz.md` | **Measured browser route — the same template as OLX Poland.** «Мы нашли более 1 000 объявлений» on a listing capped at 25 pages; **28 categories state 15 290 between them, four above 1 000** (2026-09-13 16:28 UTC). `route: browser · 1000` |
| Intermediair (Netherlands) | `intermediair.md` | **Shipped — #295, DPG Media's second board by `nationalevacaturebank.py --host intermediair`: 2 160 distinct uuids in the declared sitemap on 2026-09-14, 10 of 10 sampled served open.** The same template to the line — the index on the named host, the file on the apex host guarded on its path, `source`/`ledger_id` keyed `intermediair`, `ad` reading the board off the address; the site states no figure by HTTP. **The recruiter's e-mail in `hiringOrganization` is no longer a field on either board.** Rules `*` open on the sitemap and the ads (the search refused in writing, never taken), no key, no browser, no login |
| Emploi Burkina (Burkina Faso) | `emploiburkina.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| rabota.by (Belarus) | `rabota-by.md` | **Measured, no adapter yet — HeadHunter's Belarusian front, `claudebot` kept off `/vacancy/*` by a hand-written line, `Claude-User` under `*`, and the transport is OPEN behind ddos-guard.** `/search/vacancy?area=16` states **30 406 vacancies** (the unfiltered page states the network's 1 025 175 — Russia included), 50 a page, 100 pages reachable. A FAMILY candidate with `hh.ru`, `hh.kz`, `hh.uz` (#233, lot 4) |
| Ministry of Labour (Barbados) | `labour-gov-bb.md` | **Not a board — measured, open, 0 advertisements.** The ministry's WordPress site; its «Online Job Centre» page describes the Barbados Job Register and links out to `barbadosjobregister.gov.bb` (#222's list). Rules refuse nothing, `Crawl-delay: 10`. Nothing to enumerate here (#233, lot 4) |
| CV.ee (Estonia) | `cv-ee.md` | **Shipped — CV-Online's Estonian board, and the 3 853 / 1 426 gap explained before the adapter was written.** The search service counts 1 426 by default and **3 853 with `showHidden=true`**, the flag the page's own bundle adds; the 2 427 hidden are Töötukassa's mediated advertisements (the public employment service, syndicated), none in the job sitemap, which lists exactly the 1 426 own. `search` emits the visible set with `mediated_by` on those rows, `--own` the 1 426; both checks printed each run. Town and country from the site's own locations table (16 of the own are FI, DE, LV, NO). `ad` reads the page's state — text, file, url or styled details — and never its `contacts`. `cv.lv` and `cvonline.lt`, same stack, refuse today. No key, no browser; 40 requests at 2 s |
| CV.lv (Latvia) | `cv-lv.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| CV-Online.lt (Lithuania) | `cvonline-lt.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Public Service Commission (Kenya) | `publicservice-go-ke.md` | **Indeterminate — the rules file timed out three times on two reads; nothing was asked.** `verdict()` answers `sweep: None`; an INDETERMINATE is not probed. A measurement to redo, not a verdict (#233, lot 6) |
| NEA Career Fair (Cambodia) | `careerfair-nea-gov-kh.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Khmer24 (Cambodia) | `khmer24.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| LiberiaWork (Liberia) | `liberiawork.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Emploi.ma (Morocco) | `emploi-ma.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| CVbankas (Lithuania) | `cvbankas.md` | **Shipped — Lithuania's first adapter, on a host read as closed for refusing `anthropic-ai` and `Claude-Web`, names we never send.** The front page is the listing: 142 VIP cards, then 50 a page to page 181 — **142 + 179 × 50 + 21 = 9 113, exactly the stated «Rodoma 9 113 skelbimų»**, printed beside the count each run — the full walk of 2026-09-12 12:40–12:59 UTC: **«9 111 emitted, site states 9 113 — 2 short»**, a live board over twenty minutes (a bounded walk is a lower bound, not compared). `/sitemap.xml` answers a challenge and is never asked for. The page's JobPosting is microdata; its salary digits are interleaved with U+200C and stripped; net/gross from the block's class, Lithuanian or English per advertisement. No key, no browser; 181 requests, ~20 min measured |
| Asako.mg (Madagascar) | `asako.md` | **Measured, no adapter yet — reopened by the 2026-09-07 doctrine, and the transport is OPEN** (Vercel). `/emploi` states **251 offers** and shows 20 in an RSC payload behind a «Charger plus» script — 0 offer links in the HTML; the app router's data route is the adapter's first question. Candidate adapter (#233, lot 7) |
| HotNigerianJobs (Nigeria) | `hotnigerianjobs.md` | **Shipped — the post is the unit, and «N positions» is a field, never a multiplier.** The newest weekly sitemap (`sitemap-37-2026.xml`, 4 190 posts over 5 days on 2026-09-13) is read once; 228 digests declare 1 208 positions in their slugs, and those positions are single posts in the same file — so posts and positions are printed apart, never summed. `post --url` reads a single's `JobPosting` (`totalJobOpenings`) or a digest's numbered list as ONE row. No total stated anywhere; no key, no browser; 2 s between requests |
| Federal Civil Service Commission (Nigeria) | `fedcivilservice.md` | **Measured, no adapter — route none (2026-09-14):** the commission's site is served and lists nothing — «Vacancies» is prose, the application process «under construction», the circulars empty, the adverts 404; recruitment notices, when an exercise runs, are news items with a PDF. A script would render nothing (#404); the card names the two observations that would reopen it |
| PNG JobSeek (Papua New Guinea) | `pngjobseek.md` | **Shipped — the country's first adapter, on a server-rendered listing with no JSON-LD anywhere.** Cards read as rendered cells (title, employer, «City, Province», type, a date by its shape), pages walked until one adds nothing — **«31 emitted, site states 31 — equal» on 2026-09-13**; the first walk lost 6 cards to a 200-byte window before the card's tag was tested, and the stated count is what caught it. `ad` reads the head cells and the Description / Requirements blocks. No key, no browser; three requests |
| Undelucram.ro (Romania) | `undelucram.md` | **Shipped — two witnesses printed apart, never merged: «1.468 rezultate» stated, and a pager that closes at page 147 (× 10 = 1 470).** The adapter walks the 147 pages at 1 s, dedups on the id in the URL's tail — 1 468 emitted, site states 1 468, equal, on 2026-09-13 — and reads place and work type by the icon's `aria-label`, not by order. The advertisement's JSON-LD `identifier.value` is the EMPLOYER's id, kept apart from the advertisement's key. No key, no browser |
| Profesia.sk (Slovakia) | `profesia.md` | **Shipped — Slovakia's first adapter (#343): one 7 MB generated sitemap sorted by the SHAPE of its URLs — 14 749 advertisements `/praca/<employer>/O<id>` on 2026-09-13, 5 658 facets set aside — against the listing's own `"count":14773`, 24 short, two witnesses never merged; the capped «10000» popup is never read.** No JSON-LD: the `<h1>`, `datePosted` microdata, the employer's `C<id>` kept apart from the advertisement's `O<id>`, salary and labels in two page layouts. The Czech front is the same stack under `--host` (`profesia-cz.md`). No key, no browser; 1 s between requests |
| Profesia.cz (Czechia) | `profesia-cz.md` | **Shipped with `profesia.md` — the Czech front of the same stack, `profesia.py list --host www.profesia.cz`: 1 094 advertisements `/prace/<employer>/O<id>` against the listing's own 1 095 on 2026-09-13.** It serves Slovak-written advertisements for Slovak places too, so `countries` carries SK beside CZ; the labels are read in both languages |
| Profession.hu (Hungary) | `profession.md` | **Shipped — Hungary's first adapter (#359): 23 sector sitemaps deduped on the id — 12 415 advertisements on 2026-09-13, 10 in two sectors — against the listing's own title «19329 db», 6 914 short, two witnesses never merged; the 2 `/en/` twins the sitemaps list are refused by `Disallow: /en/` and never read.** `JobPosting` on the advertisement with the employer's `Organization/<id>` kept apart, the place as page microdata, and a `validThrough` that is the read time plus thirty days — kept as published, never offered as an expiry. No key, no browser; 1 s between requests |
| Állásportál (Hungary) | `allasportal.md` | **Shipped — #360, the generalist of manual trades and agency work, at the thirty seconds its rules ask: «8661 állás» stated on 2026-09-14, 8 670 hosted ads in its job sitemap (never merged — the list counts the redirected ads too).** Two kinds of card: hosted ads read by `ad`; **ads gathered from other boards whose only address here is `/munka/redirect/`, refused in writing — carried as the card, `url` null, never followed.** No JSON-LD; **the hosted ad's «Kapcsolati adatok» block scrubbed of Hungarian numbers and e-mails; the employer's own apply page named, never fetched.** No key, no browser, no login |
| CVOnline Hungary (Hungary) | `cvonline-hu.md` | **Shipped — #362, Alma Career's Hungarian board on the very template of Alma's Finnish Jobly: `jobly.py --host cvonline-hu` — «5 681 ÁLLÁS VÁR» stated on 2026-09-14, 40 read in 2 pages at the ten seconds the rules ask.** The listing, the count, the ad's address (`/hu/allas/`, `/hu/<tier>/allas/`), the sitemap and the body pane named per board; a card whose address is not the board's ad shape is not a card; **the employer's template body scrubbed of Hungarian numbers and e-mails; the «Jelentkezem» link never followed.** No key, no browser, no login |
| easy-prace.cz (Czechia) | `easyprace.md` | **Shipped (#352) — two stores in two sitemaps, keyed apart: 10 121 of the board's own (`/nabidka/`) and 24 546 republished from the Úřad práce ČR (`/volne-misto/`) on 2026-09-13, the largest Czech inventory measured; against the listing's own «34 575 výsledků», 92 more emitted than stated, never merged.** No JSON-LD: one `NabidkaDetail-*` template for both stores — title, employer, salary, labelled fields, content rows as fields or description; the contact person the page names is never read. No key, no browser; 1 s between requests |
| Úřad práce ČR (Czechia) | `uradprace.md` | **Shipped — #350, the public employment service's whole register through the Ministry's open-data file: 39 887 postings, 101 207 positions in one 190 MB daily file (`Last-Modified` 2026-09-13 20:07 UTC), the largest Czech inventory measured; easy-prace.cz republishes 24 546 of them.** **The portal's own search POSTs `*/rest/*`, refused in writing by `up.gov.cz` — never sent, no `ad`.** Places resolved through the published code lists (municipality → district → region); the anonymous employer (`anosp`) null with a reason; **the contact person every record carries never emitted; every free text scrubbed — one profession was an e-mail address**; a body shorter than `Content-Length` exits 6. `--cache DIR` keeps the file 24 h. No key, no browser, no login |
| İşin Olsun (Turkey) | `isinolsun.md` | **Shipped, half by construction (#382): two job-detail sitemaps — 87 504 advertisement keys on 2026-09-13, one nightly generation — against the root's own «87.394 İş İlanı», 110 more emitted than stated, never merged; the advertisement page stalls without a byte for every plain client (declared identity or curl's own name), so `ad --url` attempts once and REPORTS rather than pretending to read — a browser measurement is the next step.** The slug is title and employer run together, emitted as is; eight slugs carry a literal tab and their keys are kept. No key, no browser for the list; 2 s between requests | **Browser measured 2026-09-13 18:05 UTC: the advertisement page stalls for a tab too (no byte in 25 s and 40 s on the root's own link) — a dated fact on two clients, `route: none` for the page** **NON FAISABLE at 13.09.2026 (#404, owner): a script that yields nothing does not count — `route: none` primes over `script:`; reopens the day a page answers**
| Eleman.net (Turkey) | `eleman.md` | **Shipped — #384, the generalist of the manual trades and the provinces: 243 pages of 30 stated by the pager on 2026-09-14 (~7 278 inferred, no total stated), 90 read in 3 pages by request.** The rules refuse the search parameters by name and leave the pager's `sy` alone — the only parameter ever sent; a highlighted card is a card; the ad's JobPosting (`baseSalary` with `unitText` MONTH, «45.000» read as forty-five thousand) and boxes (positions, gender wanted, age range). **The «İletişim» block of masked telephone numbers is never read; descriptions scrubbed.** No key, no browser, no login |
| SecretCV (Turkey) | `secretcv.md` | **Shipped — #385, a generalist stating «20.409 İş İlanı Listelendi» on 2026-09-14 whose every parameterised address answers 410 to this client (the page's cards in the 410 body — the code decides): read one first page at a time, the country's and the 33 city and sector lists it links, never paged, never a shortfall claimed.** No parameter ever sent. The ad answers 200 to anyone — JobPosting, labelled table, the description ended at the login button; **scrubbed; the application is a login, never touched.** The pages beyond the first: a browser candidate. No key, no browser, no login |
| Työmarkkinatori (Finland) | `tyomarkkinatori.md` | **Shipped on a stub, under the user's own key (#371, on #403) — measured, no request under `/api/` from here — the public employment service's every data route is under `/api/`, refused in writing to `*`:** the open-jobs page is a shell for a widget whose client has `baseURL: "/api"` — the search POSTs to `/api/jobpostingfulltext/search/v2/search`, the posting comes from `/api/jobposting-new/v1/public/jobpostings/<id>` (read from the widget's code, never requested); no sitemap, no server-rendered listing, `avoindata.fi` a static 403. A written refusal is honoured by every route; the exit is an owner's override key, as for SmartRecruiters and HiringCafe — #371 stays open and `blocked` | **Since #403 (2026-09-13) the exit is the user's own `override_robots` key, not the owner's decision; #371 builds the adapter behind it**
| Duunitori (Finland) | `duunitori.md` | **Shipped — Finland's first adapter (#374), on rules that refuse `*` and name `Claude-User` to let it in.** 92 job sitemap pages at 1 s: 18 298 slots for 16 152 distinct ids on 2026-09-13 — the paging is not a partition (consecutive pages overlap by 56–61 URLs), and the adapter says how many repeated — against the listing's own «Löysimme 18 302 työpaikkaa», 2 150 short, never merged. `JobPosting` on the advertisement whose `title` is the normalised occupation (the `<h1>` is the title), a real `validThrough`, and a recruiter's address in the prose withheld. No key, no browser; 1 s between requests |
| Oikotie Työpaikat (Finland) | `oikotie-tyopaikat.md` | **Measured, no adapter — route none (2026-09-14): the board has closed and its only page says so in writing («Oikotie Työpaikat on sulkeutunut»)** — a saved Vite shell, 17 499 B at the same fingerprint on two days, no data route, `www.oikotie.fi/tyopaikat` → `/404`. Nothing to render (#404); the card names what would reopen it |
| Jobly (Finland) | `jobly.md` | **Shipped — #376, Alma Media's generalist, the private board beside Duunitori now that Oikotie has closed: «12 737 avointa työpaikkaa» stated on 2026-09-14; the sitemap's two files carry 13 636 distinct ids (899 more — expired ads kept), never merged with the listing's count.** `Crawl-delay: 10` honoured as written; the listing's pager counted from zero with a guard against a pager that does not page; the ad's JobPosting (types and places as lists, a salary stated only with a value and a period). **The body names the recruitment consultants with telephone and e-mail (Cloudflare's placeholder included) — scrubbed; the apply link refused in writing, never followed.** No key, no browser, no login |
| Barona (Finland) | `barona.md` | **Measured, no adapter (2026-09-14): the staffing group's postings live on `www.baronacareers.com`, whose rules open the list, the browse API and the sitemap and whose transport answers the provider's 25-byte 403 (`9ccabba20b9f`) to this client on every path — a browser candidate, named and not measured (no browser on the day).** The marketing site `www.barona.fi` lists no posting a client may read (its widget is filled from `/wp-json/`, refused in writing, or from the careers host). Nothing to render (#404) |
| Služby zamestnanosti (Slovakia) | `sluzbyzamestnanosti.md` | **Shipped — the Slovak public employment service's board (#342), the inventory no private board republishes:** the ÚPSVaR points to `sluzbyzamestnanosti.gov.sk`, whose page calls a JSON search that carries the site's own count beside the rows — 12 126 of the state's own on 2026-09-13, «12 126 emitted, site states 12 126 — equal»; 25 563 with the republished profesia.sk / kariera.sk / worki.sk / eures.sk rows under `--source all`, each linked out to its portal. The advertisement page is a `<dl>` of forty fields, cut at «Kontaktná osoba» before reading. No key, no browser; 1 s between requests |
| SouthSudanJob (South Sudan) | `southsudanjob.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Emploi.tg (Togo) | `emploi-tg.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| NodeFlair (Singapore) | `nodeflair.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| MyWork (Vietnam) | `mywork.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Tecnoempleo (Spain) | `tecnoempleo.md` | **Shipped — under the 2026-09-07 doctrine, with a reservation recorded: the rules refuse the whole site to six Anthropic names by hand, and `Claude-User` is not among them.** One sitemap of 30 891 `<loc>` holding **2 145 offers** keyed by their `rf-` hash, real `<lastmod>`; the listing states **2 592** (a Spanish thousands dot parsed) — «447 short» on 2026-09-13, two views of one store. `JobPosting` with the country per offer; `identifier.value` is the employer's id, kept apart. No key, no browser; two requests |
| foundit Philippines (Philippines) | `foundit-ph.md` | **Shipped as the second host of `founditgulf.py`, under the same recorded condition — the same hand-written `ClaudeBot: Disallow /jobs/ /search/`, never read on this host either.** Two active-jobs sitemaps, **42 504 distinct advertisements** — PH 40 491, SG 78, MY 57 by the slug; today's file (1 031) checked against them each run, and on 2026-09-13 **23 of them were NOT among the active** — the adapter says so. `JobPosting` on 10 of 10, `PH` on all ten, no salary field. Rows keyed `foundit-ph:`. No key, no browser; three to five requests |
| Jobslin (Philippines, and 20 sibling sub-hosts by `--host`) | `jobslin.md` | **Shipped — #299: `ph.jobslin.com` states «1 - 12 of 16,072 Job Vacancies» on 2026-09-14, 36 read in three pages by request at the host's `Crawl-delay: 2`.** The listing by `?page=N`, the heading checked after every turn; the card's place and date read from the spans its own icons label, the salary with its sign and its printed period, «Premium» flagged; the ad a JobPosting. The hub `www.jobslin.com` is a country chooser (0 advertisements); the 20 siblings are `--host <cc>` and wait for their own measurement. Rules `*` open (the managed block names `ClaudeBot` only), no key, no browser, no login |
| MyJobMag (Nigeria, Kenya, South Africa, Ghana, UK — five fronts by `--host`) | `myjobmag.md` | **Shipped — #391, one generalist on five hosts: the site states no count and its list is an archive, so the walk is newest-first and stops at the first card older than `--days` (30): 4 464 cards over 128 pages on Nigeria, 1 796 Kenya, 1 409 South Africa on 2026-09-14; Ghana and the UK dormant (first cards February and May), served and said.** Every query string refused in writing, so the pager is the path and no filter is sent; a card is a position or an advert of several, and `ad` emits one record per position with the labelled fields and the salary period the site prints; **the «Method of Application» block — where employers write the address to send a CV to — scrubbed, no contact emitted.** No key, no browser, no login |
| The Ugandan Jobline (Uganda) | `theugandanjobline.md` | **Shipped — with the stated number named for what it is: «84,248 jobs» is the archive since the site began (8 425 pages, 85 post-sitemaps), never compared.** The adapter walks the newest pages (default 20), reads «Closes DD Mon» on every card into a date and says how many still close in the future — 50 of 50 over 3 pages on 2026-09-13. `JobPosting` in the post's `@graph`, «Uganda» → `UG`, an empty salary stays `null`. No key, no browser; 1 s between pages |
| TopDev (Vietnam) | `topdev.md` | **Shipped — Vietnam's IT board through 249 paged job sitemaps (20 a page, the same ids in `en` and `vi`).** The search page states **4 942** «[Update 13/9/2026]» and the adapter prints its distinct count beside it after a full walk — **«4 525 emitted, site states 4 942 — 417 short» on 2026-09-13** (4 980 slots, 455 repeats across pages of a sitemap regenerated as the walk runs); a bounded walk is a lower bound, not compared. `JobPosting` JSON-LD with salary in VND and the country per advertisement; its `identifier.value` is the employer's id, kept apart from the advertisement's. No key, no browser; 251 requests at 2 s |
| CareerLink (Vietnam) | `careerlink.md` | **The root is served and the listing answers 200 with a Cloudflare Turnstile — a challenge in the body, not in the status; 0 advertisements read.** Borne 2 on the one path that matters; not a candidate by HTTP (#233, lot 8) |
| KarriereStart (Norway) | `karrierestart.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Halo oglasi (Serbia) | `halooglasi.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Ezega (Ethiopia) | `ezega.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| EthiopiaWork (Ethiopia) | `ethiopiawork.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Kariera (Greece) | `kariera-gr.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Skywalker (Greece) | `skywalker-gr.md` | **Reopened by the 2026-09-07 doctrine, and the transport answers a challenge.** `ClaudeBot` named, `*` open — `identity()` says `claude-user` — and the root and a listing path answer 403 «Just a moment...» with a moving md5: the `revolico` family, where borne 2 stops the browser branch. Not a verdict of closure |
| Ministry of Labour (Guyana) | `labour-gov-gy.md` | **Reopened by the 2026-09-07 doctrine, refused at the transport.** `ClaudeBot` named, `*` open — `identity()` says `claude-user`, `verdict()` sweeps since #230 — and the root and a listing path answer a **static 403 of 25 bytes**, the provider default shared to the byte with `jobstore` and `hays`: family (1) of #222, where a browser is legitimate and not measured here. Not a verdict of closure |
| Great Uganda Jobs | `greatugandajobs.md` | **Shipped.** Uganda's largest board — Joomla + JS Jobs, server-rendered, **no browser, no key**. The site's «103 391 Jobs Posted» is a cumulative counter (102 924 nine days earlier) and is printed as such, never as the size; **the anchor is the deadline every card carries — live vs expired, per card, against the day**. The listing is a live stream paginated by `start=N` over the whole page (8–10 Gold cards pinned on every page), and it moves between requests: keyed on the id, rows read beside distinct, no completeness claimed. No JobPosting on the ad; labelled pairs and the visible text |
| Mynavi Tenshoku (Japan) | `mynavi.md` | **Shipped — Japan's first adapter.** Seven job sitemaps, 346 385 URLs for **77 504 distinct advertisements** with a real `<lastmod>` each — **against 掲載求人数 61 989 件 the home page states the same day: the sitemap is a superset, closed advertisements still declared**, and the adapter prints both side by side. Every advertisement page carries a full `JobPosting` in Japanese — salary in JPY, dates, prefectures, category — emitted as published, nothing translated. No key, no browser; nine requests for the whole count |
| Rikunabi NEXT (Japan) | `rikunabi-next.md` | **Investigated — no listing route found.** Recruit's flagship board: rules open (64 query-string patterns refused, and `_robots` keeps all 64 wildcards after the blank line), no sitemap, and the root sends a session-less client to `/session/destroy` — a Next.js shell that links nothing; the old listing paths 404. Not a refusal, not a challenge, not a verdict of closure |
| Townwork (Japan) | `townwork.md` | **Investigated — the SSO's exit with an AWS WAF challenge on top.** Recruit's part-time board: rules open, no sitemap, the root redirects a session-less client to `/session/destroy` — a 5 460 B shell that loads `awswaf.com/…/challenge.js`. A passive challenge is still a challenge (borne 2); nothing of the board was served. Not a verdict of closure |
| type (Japan) | `type-jp.md` | **Shipped.** One job sitemap, **2 335 distinct advertisements**, every advertisement a full `JobPosting` in Japanese (salary in JPY, dates, prefectures, the employer's id). The home page states a count per category — 2 715 summed over 11, an upper bound with overlap — printed beside the count, never as the board's size. No key, no browser; three requests |
| Green (Japan) | `green-japan.md` | **Shipped.** Japan's IT/Web board: one job sitemap, **28 284 distinct advertisements** across 3 958 companies, and `/search` states the same 28 284 in its meta description — the adapter prints both and says «k short» when they part. Every advertisement a full `JobPosting` in Japanese; `validThrough` (read date + 1 year) and `currency: YEN` emitted as published and flagged, not corrected. No key, no browser; three requests |
| Hello Work (Japan) | `hellowork-jp.md` | **Shipped — #304, the public employment service, the country's largest inventory: «検索結果 1082197件» stated for 一般 on 2026-09-13.** A session-bound JSP form walked by its own fields (a GET for the session, a POST per page; the form's own `action` replaced on the first request, `screenId` never appended on the next — each doubled field answers the site's error page); the free word goes full-width. `search --pref 13 --word python`: **33 emitted over 2 pages, site states 33 — equal**; `--pages` defaults to 10 and the note says bounded. Contact rows (address, telephone, representative, corporate number) are dropped from the detail and listed as dropped. No rules file, 3 s own spacing, no key, no browser. Not `hellowork.com` (the French board, `hellowork.py`) |
| NAV Arbeidsplassen (Norway) | `arbeidsplassen.md` | **Shipped — #365, the public employment service, Norway's first script adapter.** The declared sitemap (**13 615 uuids with lastmod**) and the unkeyed search API the page calls (**hits.total 13 620** the same minute — 5 apart, both printed); `size` to 100, `from` capped at 10 000 and the adapter says where the window ends; `positioncount.sum` (27 406) named a headcount, never compared; a 429 stops the run. `search --q python`: 58 / 58 — equal. Half the inventory is FINN.no's through the State's door (`listed_via`). The page's «Kontaktperson» section is dropped whole; the street address is never emitted. Rules `*` open, no key, no browser |
| Jobbnorge (Norway) | `jobbnorge.md` | **Shipped — #366, the public-sector and academic board: `/v1/jobs/count` 2 321 positions and `/v3/jobs` 1 078 postings summing to 2 321 on 2026-09-14 — equal.** The two requests the search page itself makes, the whole list in one answer; the department as employer when the site says so, the primary location first. **The ad's data route carries the contact persons (name, telephone) — never emitted; text scrubbed.** Rules refuse the posting PDF only; no key, no browser, no login |
| Jobberman / BrighterMonday (Nigeria, Kenya, Uganda) | `jobberman.md` | **Shipped — #390, one file for ROAM Africa's three boards (`--host`).** The declared listings index (27 category files, ids deduped across files) and the listing's own «N Jobs Found» beside every walk: **Nigeria 4 150 in the files / 4 194 stated; Uganda 757 / 1 025; Kenya 1 895 stated** (2026-09-13). The rules allow the pager to page 10 by name and refuse the rest — `recent` ends there by the rules and says so. Cards read by their structure (a first draft read the text lines in order and shifted every field by one); salary a currency and a range, no period. No JobPosting on the page; no contact on it. No key, no browser; 29 requests for a sitemap walk |
| İŞKUR (Türkiye) | `iskur.md` | **Shipped — #381, the public employment agency, the country's largest open inventory: «Toplam Kayıt: 34049» stated on 2026-09-13.** A WebForms search turned page by page by postback (the results form re-posted with `btnNext`; the pager's `txtCurrentPage` checked after every turn); the rows read from the share buttons' data attributes. `search --il 34 --pages 2`: 30 of 3 847, bounded by request. **The employer's name is behind a login on every row and stays there** — `employer` null with the reason; the public detail gives the education bounds only. Rules `*` open, no key, no browser, no login |
| Dept of Labour Online Skills Bank (Bahamas) | `jobseekers-bs.md` | **Shipped — #447, the public employment service, the country's most furnished board: «1-24 of 220» stated on 2026-09-13, 220 emitted — equal.** A PCRecruiter board paged by its own `googlePage` form (`morecount` rewritten as the page's `goToPage` does; the «a-b of N» heading checked after every turn); the `pcr-id` token carried from the list to the detail, a detail without it is a shell the adapter refuses. **The employer is on neither page — the Department mediates** — `employer` null with the reason; «$0.00 — $0.00» is no salary, never zero. Rules absent (404), no key, no browser, no login |
| Convocatorias del Gobierno de Puerto Rico (Puerto Rico) | `empleos-pr.md` | **Shipped — #441, the OATRH's central register of public-service calls: «Page 1 of 12» stated on 2026-09-13, 144 emitted over the 12 pages — every page walked.** A Webflow site walked by plain GETs, the list's query key read off the page's own «Next Page» link, the pager checked after every turn; Webflow's hidden blocks (`w-condition-invisible`) and unbound blocks never read as shown — the closing date is «Hasta Nuevo Aviso» when the site hides the date. **The entity is the employer**; the salary period is the page's own «Mensual»; the OATRH's footer address is dropped. No rule written, no key, no browser, no login |
| Vacatures bij de Overheid van Suriname (Suriname) | `govsr.md` | **Shipped — #443, the State's own vacancy cards: `X-WP-Total: 133` stated by the register on 2026-09-13, 12 read in two pages by request — at the `crawl-delay: 60` the host writes and `_pace` obeys.** The REST route counts and names, the LIST CARD is where the posting lives (ministry, summary, location, publication, «Inleverdatum tot», the terms-of-reference PDF); the posting's own page is bare and `ad` says so. **The ministry is the employer**; an e-mail inside a card's text is withheld. Rules `*` open, no key, no browser, no login — one request a minute |
| Kuntarekry (Finland) | `kuntarekry.md` | **Shipped — #373, the municipalities' and wellbeing counties' recruitment service: «count: 1356» stated by the site's own counter on 2026-09-13, 72 read in three pages by request.** The list is rendered by the server (`<job-card>` attributes), the four promoted cards skipped by their own attribute, the pager checked after every turn, the counter asked on the walk's own path (`--filter espoo`). **The contact person on every ad never leaves** — block dropped, text and salary line scrubbed of e-mails and Finnish numbers; the salary is the posting's own text in EUR, never a number. Rules `*` open, no key, no browser, no login |
| Valtiolle (Finland) | `valtiolle.md` | **Shipped — #372, the State's own board by `kuntarekry.py --host valtiolle`: «count: 212» stated by the site on 2026-09-14, 212 emitted — equal.** The municipalities' template and operator to the line — the counter and the list asked on the named host, `source`/`ledger_id` keyed `valtiolle`, `ad` reading the board off the address; Puolustusvoimat, Ulosottolaitos, the police among the employers. **The contact person on every ad never leaves.** Rules `*` open, no key, no browser, no login |
| Trabaja en el Estado (Chile) | `trabajaenelestado.md` | **Shipped — #302, the Servicio Civil's public-service calls: `hits.total` 349 stated by the index on 2026-09-14, 349 emitted — equal.** The Elasticsearch route the page posts to itself (`elastic.serviciocivil.cl`, no rule written), the page's own filters and page size with a plain sort in place of its Painless script; 28 records without the site's id take the index's `_id` and say so. **`Ganador` (the appointed person) never emitted; the addresses on `www.empleospublicos.cl` (`Disallow: /`) emitted as data and never fetched — no `ad` command.** No key, no browser, no login |
| Jobs.cz (Czechia) | `jobscz.md` | **Shipped — #351, the largest Czech board: «Našli jsme 16 019 nabídek» stated for the country and 7 681 for Prague on 2026-09-14, 60 read from each by request.** Server-rendered search cards; **the country-wide page 1 is the client's entry page and the walk says so, starting at page 2 — `--locality praha` is served from page 1**; the count read from the text (a `<strong>` with a no-break space), the salary tag as a CZK range without a period, the search token stripped. **The ad's contact block never leaves**; text scrubbed. Prace.cz (#353) is a different stack, not a `--host`. Rules `*` open on the list, no key, no browser, no login |
| Prace.cz (Czechia) | `pracecz.md` | **Shipped — #353, the group's second Czech generalist: «Našli jsme 19 005 nabídek» stated on 2026-09-14, 120 read in three pages by request.** Cards served from page 1 that label their own fields (the salary with its printed period); the UUID read from all three link shapes; **employer-hosted ads (13 of 40) named by the card and their other host never read — `ad` stops at the redirect**; the JobPosting's own `unitText`. **The «Kontaktní údaje» block never leaves.** Rules `*` open on `/nabidky/`, no key, no browser, no login |
| StartupJobs (Czechia) | `startupjobs.md` | **Shipped — #354, the Czech tech and start-up board: 392 offers named by its sitemap on 2026-09-14, each read from its own server-rendered page (the offer object in the page's `__NUXT_DATA__`), because the listing's API lives on `back.startupjobs.cz` which refuses everything in writing — never sent.** No count stated on a page this client may read: the sitemap is the inventory and the note says so. Salary with its period, locations, skills, languages, benefits; **no contact field, the text scrubbed all the same; the employer's own link never fetched.** No key, no browser, no login |
| Práce za rohem (Czechia) | `pracezarohem.md` | **Shipped — #355, Alma Career's board of jobs near home: «20 758» stated by the page's own state on 2026-09-14 and printed beside every walk with the regions the site counts; one Next.js stack with the Slovak Práca za rohom (`--host`).** 50 a page, `?page=N`, only `page` ever sent; the 90 facet sitemaps not read. **The ad's `recruiter` object (name, e-mail, telephone) never emitted; texts scrubbed; the app deep link never followed.** No key, no browser, no login |
| Práca za rohom (Slovakia) | `pracazarohom.md` | **Shipped — #347, the same stack on the Slovak host: `pracezarohem.py --host sk` — «18 586» stated on 2026-09-14 (Bratislavský 6 666 …), 100 read in two pages.** The host serves the Czech facet sitemaps — not ads, not read. `recruiter` never emitted. No key, no browser, no login |
| Trenkwalder Slovakia | `trenkwalder-sk.md` | **Shipped — #349, the staffing network's Slovak front: the rules name `Claude-User` (open but `/api/*`, `Crawl-delay: 10`); the listing's server-rendered search state carries `nbHits` — 32 on 2026-09-14 — and 30 hits, the sitemap's other ids read from their pages: «32 emitted, the site states 32 — equal».** The salary only when the site publishes it (13 of 32); `recruiter` on every record never emitted. No key, no browser, no login; 10 s between requests |
| Virtuális Munkaerőpiac (Hungary) | `vmp.md` | **Shipped — #358, the public employment service: it states its count in the very sentence that refuses to list — «A lista túl sok elemet tartalmaz (1806)»** (2026-09-13); a narrow search is listed and walked against «(N találat)» (Budapest 141), a wide one prints the site's N and stops — `categories` sums the 25 and calls it a bound. The employer is «Bejelentkezés után látható» on every row and stays null; the detail states the salary as monthly gross HUF. **After 14 requests at 2 s the host answered 404 on every path, the root included** — spacing 5 s since, the 404 named for what it may be. No rules file, no key, no browser, no login |
| HeadHunter (Russia, Kazakhstan, Belarus, Uzbekistan) | `hh.md` | **Shipped on a stub — #337, one file for the network's five fronts through `api.hh.ru`, under the user's own `boards.hh.contact`** (the API requires a contact address; the plugin never fabricates one, sends the user's in `HH-User-Agent`, prints it nowhere; without it nothing is requested). **On 2026-09-13 the API answered 403 `{"type":"forbidden"}` to the owner's address on all four areas, in both header forms** — a dated fact, not a verdict; `found` is the witness when it answers; `contacts` dropped from a vacancy. The fronts' figures are `rabota-by.md`'s |
| Uruguay Concursa (Uruguay, the public service) | `uruguayconcursa.md` | **Shipped — #435, the ONSC's calls for candidates («llamados») through the JSON API the page itself posts to (`POST /api-backend/llamados/find`), no key, no cookie, no browser.** `list`: **363 emitted over 8 pages of 50, the API states «Mostrando TODOS los Llamados Abiertos (363)» — equal** (2026-09-13); the unfiltered walk is the 42 217-record archive and is not the default. The state body is the employer and is public; **88 e-mail addresses in the 50 records of page 1 are withheld**, phone numbers too. Salary kept as the state writes it (`salary_text`), never parsed; posts per body summed as `positions`. `/robots.txt` unreadable → no written rule, 3 s own spacing |
| Buscojobs (21 countries — VE UY PR PY BO NI DO EC GT PA AR CL CO ES BR PT HN SV CR MX PE) | `buscojobs.md` | **Shipped — #425, one Next.js platform on 22 hosts, the listing page's own `__NEXT_DATA__` payload: the stated count and 15 full records per page, the JSON-LD `ItemList` for the public URLs.** `--host` names the front, the front names the country. Paraguay walked to the count on 2026-09-13: **41 emitted over 3 pages, site states 41 — equal**; the default walk is bounded (`--pages 10`) and says so — Spain states 2 858 489, Brazil 1 556 164, Mexico 1 646 877 (aggregates, `source_feed`). **A burst is challenged (AWS WAF «Human Verification», HTTP 405) and 30 s spacing is served: 20 s per host is the pace**, a challenge met exits 7. The employer's contact fields are dropped, age and sex are not propagated (#183) |
| Un Mejor Empleo (13 countries — VE AR HN CL CR CO EC GT MX PA PE SV ES) | `unmejorempleo.md` | **Shipped — #427, one PHP template, one front per country; the listing's twenty cards are the route and the header's «Empleos 1 a 20 de 1,519» the witness.** `--host` names the front, the front names the country; the chooser `www.unmejorempleo.com` answers 404 on `/empleos` and is not a front. Thirteen fronts read 2026-09-13/14, 11 716 stated in all (GT 2 466, CO 1 727, SV 1 590, VE 1 519 …); Venezuela walked to its count. `Crawl-delay: 4` honoured, 5 s own. The ad page's labelled pairs (employer, contract, description, education, English, experience); salary as the card's text, never a number; e-mails and phones in the prose withheld |
| Caribbean Jobs Online (12 territories — AG AW BS BB BM KY GY HT JM LC SR TT) | `caribbeanjobsonline.md` | **Shipped — #449, one regional board, one list per territory (`/jobs/<slug>`, 28 lists), `--country` names the list.** The first page states `page_max_count` («Page 1 of 4») — **a page count, the witness; the site states no item count** — and the next pages are loaded through the site's own session loader (`POST /include/ajax_vacResults.asp?nextID=…` on the cookie the first GET set; the `?pageno=` links answer page 1 again). Bahamas walked: **34 over 4 pages, site states 4 — pages equal**; Jamaica 128 over 13, equal (2026-09-14). Fifteen lists carry nothing and state nothing — measured, not declared. Ad page: organisation, reference, contract, industry, location, posted and expiry dates; e-mails and phones withheld; salary as text |
| Trabajópolis (Bolivia) | `trabajopolis.md` | **Measured 2026-09-14, no adapter — the owner's decision pending (#428).** The root is served («Más de 115.000 ofertas gestionadas», a lifetime claim); **every list route and the sitemap answer HTTP 403 with a 642 KB robot challenge** («debemos verificar que usted no es un robot … Enable JavaScript and cookies»), md5 moving between two reads — borne 2, not defeated — and the page quotes the terms of use: clause V.2 forbids access «mediante bots, arañas o cualquier medio automático». `route: none`, dated; «fermé» is the owner's word (§2 sexies) |
| HonduTrabajos (Honduras) | `hondutrabajos.md` | **Shipped — #438, the list paged at the root (`/?page=<p>`, twelve cards), three numbers on the front page and the list's own «+4,017 ofertas laborales activas» as the witness (the pager's 335 × 12 agrees; the «818» of the day before was a stat box, the «Más de 115» a hand-written floor — printed, not compared).** **Walked 2026-09-14: 3 989 over 335 pages, site states 4 017 — 28 short, exit 6, a 17-minute walk over a list that moved (4 017 → 4 018 during it; the same page twice 4 s apart is identical).** The ad page's JobPosting and «DATOS TÉCNICOS»; the recruiter's address the description ends with («Correo para aplicar: …») withheld, phones too; the ledger keyed on the URL's suffix for list and ad alike. `Allow: /`, 3 s own |
| Clasificados Online — Empleos (Puerto Rico) | `clasificadosonline.md` | **Shipped — #442, a classic ASP classifieds, thirty rows a page (microdata + record-row), two numbers of the site's own: the section's «3,581 Oportunidades» and the list's «1 al 30 de 3000».** Walked 2026-09-14: **3 000 over 100 pages, list states 3 000 — equal**; the section's 581 more are beyond a cap the unfiltered list has (`offset=3000` answers the last page again) — printed, named, never resolved; `--cat` / `--town` / `--q` reach past it. The row's `datePosted` meta is the ad's expiry (three ads checked) and is emitted as `valid_through`. Phones and addresses withheld; salary as text; `anthropic-ai` and `Claude-Web` refused in `robots.txt` — neither is a token we send; 3 s own |
| BoliviaTrabajo (Bolivia) | `boliviatrabajo.md` | **Shipped — #431, «949 ofertas publicadas en Bolivia» on the list, twelve cards a page; walked 2026-09-14: 949 over 80 pages, site states 949 — equal.** The badges are named by their class (a card without a contract shows the salary second); the page mixes «12 Sep» and «01 Aug» and both go ISO. The ad page's JobPosting carries `baseSalary` with its currency (BOB) and unit; phones and addresses withheld. The most complete Bolivian board that stays open — Trabajópolis challenges (#428), Buscojobs BO holds two |
| Clasipar — Empleos (Paraguay) | `clasipar.md` | **Shipped — #434, a classifieds where «Busco» is the job offer and «Ofrezco» a worker offering (the default emits «Busco», says how many were passed over); witness = the category's «Búsqueda y postulación de Empleos (562)».** **Every page of the pager is a fresh random draw** (page 3 twice, 5 s apart: one card in common) — one pass over 23 pages read 364 distinct of 562, exit 6 with the cause named, `--passes N` grows the union. Invisible watermark spans («Fuente del anuncio: <url>») stripped from every title and description; the contact behind the site's button never pressed, phones and addresses withheld; price as text |
| Kariéra (Slovakia) | `kariera.md` | **Shipped — #345, the Zoznam portal's board: the list paged by offset (30 a page), the site's two figures read side by side — its offers sitemap (8 159 URLs with `lastmod`) and its pager's end (page 272).** Walked 2026-09-14: **8 159 over 272 pages, sitemap lists 8 159 — equal, the same id set to the last one**; `sitemap` enumerates in one request. The public employment service republishes this board with the same ad ids (194 of 202 rows checked) — the direct read adds the salary text, the date, «Top», the ad's sections. Free-text search refused in writing, so no `--q`; phones withheld, salaries and «Ref. č.» numbers not mistaken for them |
| Práca SME (Slovakia) | `pracasme.md` | **Measured 2026-09-14, no adapter — a browser candidate not yet measured (#346).** `/robots.txt` answers a moving «Security Verification» challenge (403, 22 955 B) — an absence of rules under #283; `/`, `/ponuky` and the `praca.sk` redirect answer a **static 402 of 55 B** «Please contact the site owner for access», the same md5 on four reads over two days: the `jobstore` family, where borne 0 asks what a real browser is served. No `route:` line: the session had no browser attached; the issue stays open for one that has |
| Jobline (Hungary) | `jobline.md` | **Measured 2026-09-14, no adapter — `route: none` by the site's own statement (#361).** What bloc C read as a client-rendered shell is the operator's notice: «Jobline.hu … üzemeltetését 2026. január 31-től szüneteltetjük, az oldal a továbbiakban nem érhető el» — HVG suspended the portal from 2026-01-31; the root is a saved page of tracking scripts and that text (md5 stable since 2026-09-13), every other path 404. The verdict of closure is the owner's; the measurement is dated |
| kode24 jobs — kodejobb.no (Norway) | `kode24.md` | **Shipped — #367, the developers' newspaper's board lives on its own host `kodejobb.no`, one list page of every open ad under the menu's «Alle stillinger N»: 16 emitted, site states 16 — equal (2026-09-14).** Next.js on Sanity, server-rendered; the ad page's JobPosting and prose (deadline d.m.yyyy → ISO); places rendered twice for two themes, emitted once. `kodejobb.no/robots.txt` is a 404 — no rules, certain; the newspaper's refuses nothing. Phones and addresses withheld |
| Toptalent (Türkiye) | `toptalent.md` | **Shipped — #388, the graduates' board read the way its page reads itself: `POST /Job/SearchJob` nine a page until an empty page, the site's sitemap (nine ad pages by their six-digit id) as the count it states — 9 emitted, 9 listed, equal (2026-09-14).** A «build your CV» banner between two cards cost the first draft a card, caught by the witness. The ad page's fields (department, place, who may apply, days left, body); its JSON-LD is malformed and not read; the recruiter's address at the end of the body withheld |
| Jobsgarden (Hungary) | `jobsgarden.md` | **Shipped — #364, a recruitment agency's board that is a WordPress category, read through the REST API the site publishes: `X-WP-Total` as the count it states — 77 emitted, 77 stated, equal (2026-09-14), the category's own `count` agreeing.** The reference in the title's brackets emitted as such; the place from the ad page's header line («2026-08-25 • Budapest • IT»), which the API does not carry; the client never named (the agency's choice); the agency's own footer contacts in no field, phones and addresses in the prose withheld |
| Suli (Greenland) | `suli.md` | **Shipped — Greenland's first adapter, and the government's portal.** Three culture sitemaps, **392 distinct advertisements** (`<lastmod>` on all; 353 slugs carry the first 8 hex of the job GUID, 39 do not and are all dated 2026-07-08 — counted apart, never dropped); en · da · kl printed side by side as the second view, since the site's own count sits behind `/api/`, which its rules refuse — **and every advertisement body sits there too, so nothing here reads it by any route**. `ad` reads the head only: title, headline, a ~150-character snippet, GUID. No key, no browser; four requests |
| Landing.Jobs (Portugal) | `landing-jobs.md` | **Shipped — Portugal's third adapter, the European tech board.** `/jobs/search` and `/api/` are refused by the rules and never taken; the sitemap holds **55 advertisements** told apart by shape from 13 employer pages, 1 505 facets and 567 blog posts, **and the open listing states 55 — equal** (it renders 50 static cards, the rest sit behind the refused route). Every page a JobPosting plus the site's own record (numeric id, state, remote label, skills); `salary` null on every page read, emitted raw. No redirect followed — the closed page is a refused path. No key, no browser; two requests |
| Emprego XL (Portugal) | `empregoxl.md` | **Shipped — Portugal's fourth adapter, and a board that never deletes.** The sitemap holds **84 876 advertisements** and the footer states 84 876 — equal, **and both count the archive** (a 2022 advertisement is still served, labelled «mais de 90 dias»); the adapter says so on both lines. The live inventory is the dated listing (`recent --days N`, 20 cards a page, day-and-month labels — the year inferred for the stop rule only, never emitted). Microdata on the page, the employer's e-mail decoded from Cloudflare's obfuscation. `/rss/all/` answers 500. No key, no browser |
| エン転職 en-japan (Japan) | `en-japan.md` | **Shipped.** One of Japan's largest boards: the job sitemap holds **10 811 dated advertisements**, the front page states **125 248** — one twelfth, and the adapter prints both as two questions (the crawler's file vs the whole store), never one corrected into the other. `ClaudeBot` refused everything, `Claude-User` under `*`; `/desc_eng*` is a written refusal and is never fetched. A JobPosting per page, description escaped twice, `places` = a whole prefecture. No key, no browser; three requests |
| ITJobs (Portugal) | `itjobs.md` | **Shipped on a stub — the first keyed run measures.** Portugal's IT board through its documented read-only API (`api.itjobs.pt/job/list|search|get.json`); `ITJOBS_API_KEY` from the environment or `~/.itjobs.env`, **exit 7 without it, never printed, never asked for**. «Job not found.» in a 200 body is read as the answer. The URL shape is rebuilt and flagged unconfirmed. No count cited until a key exists |
| SAPO Emprego (Portugal) | `sapo-emprego.md` | **Shipped.** Portugal's general board: `/offers/search` is refused in writing and captcha-gated — never taken; the route is `offers.xml`, **22 838 distinct uuids** (the slug is not the key: 1 743 slugs under more than one id), and the count is **`offers_total: 23 555`** embedded on the open listing page — 717 short, both printed (its `total: 9999` is a page cap). A JobPosting per page. The host answered 429 at three requests in ten seconds: 5 s spacing, stop on 429 |
| Wuzzuf (Egypt) | `wuzzuf.md` | **Shipped — as an inventory of addresses.** Egypt's largest board. The Cloudflare managed rules name `ClaudeBot` and leave `*` open (`Crawl-delay: 10`), so the route is `Claude-User`; **every HTML page answers a challenge** (403, «Just a moment...», moving md5 — the `revolico` family) **and the sitemap is served**: 5 491 advertisement addresses, 5 272 of them Egypt by the slug's tail, all stamped with one `<lastmod>` (a rebuild). No title, date or text is read; `ad` names the challenge and exits 9. No key, no browser; two requests |
| SPTOJobsLink (Pacific, Fiji first) | `sptojobslink.md` | **Measured — browser route, no script.** The fourth host of the 25-byte vendor refusal, served to a tab with no challenge. The sitemap its rules declare holds **2 548 job posts** with dates (2025-08 → 2026-09-11) — **and its second file answers HTTP 404 with the newest 548 in its body**: the code is wrong and the body is right, and the adapter reports both. `/jobs/` shows exactly 100 cards and stops; the site states no count. No JobPosting on the page |
| eJobsFiji (Fiji) | `ejobsfiji.md` | **Shipped — Fiji's second board, small and quiet.** 9 advertisements in a sitemap of 397; **nothing published since 2026-08-03**, which is not the same as broken. **The id is in the query string** (`/jobs/view?id=1120`) — every ad shares the path, so `full_path()` is what makes the guard meaningful here. Its `lastmod` is real — 6 distinct dates over 9 ads — where `myjobsfiji` stamps 3 152 entries with one: **the same field is load-bearing on one board and worthless on the other, in one country.** **6 of its 9 are also on `myjobsfiji`**, confirmed on the employer 6/6; the relation is asymmetric — two thirds of one board, 3 % of the other |
| MyJobsFiji (Fiji) | `myjobsfiji.md` | **Shipped, and Fiji's first adapter.** **190 advertisements inside a sitemap of 3 152 URLs** — 2 790 of the rest are company pages, so **counting the file would report the board 16.6× larger**, the widest such gap measured here. **All 3 152 `lastmod` carry one value**, today's: a regeneration stamp, so `--since` is refused on the sitemap and reads `datePosted` from the schema instead. `baseSalary` is present on every ad and **empty on 9 of 10**, the empty ones carrying `unitText: YEAR` beside no value; the one filled row is correct at `6.10`/`HOUR`. **1 of 10 sampled is in Honiara, `addressCountry: Solomon Islands`** — the country is read from the advertisement, not the board |
| Cubisima Empleos (Cuba) | `cubisima.md` | **Shipped, and Cuba's first adapter** — its country page had three open hosts, no sitemap and no measurement. **6 068 advertisement ids for La Habana from one request**: the listing page writes its whole result set into a `searchAnuncios` array while rendering thirty cards. **No URL is guessed** — the listing paths and the `empleo-api/<id>` endpoint are declared by the site's own links and click handler. **An unknown `--place` returned the whole country, 9 486 ads, under the name you typed**, so the slug is validated against the site's 199 declared places. Contact details (e-mail, mobile, WhatsApp) are emitted on `ad` and **withheld from every sweep**. The card's date is relative («Hoy»), so `--since` requires `--fetch` |
| Vrabotuvanje (North Macedonia) | `vrabotuvanje.md` | **Shipped — North Macedonia's first adapter.** An Alma Career board whose same-origin proxy `/api/proxy/jobs/search` serves several countries: **the `x-app` header selects the board** — without it the same URL states 2 006 Croatian advertisements, with it **698 Macedonian, and the envelope states 698 — equal**. Ten `organization: "incognito"` rows emitted as a hidden employer, never the word. The sitemap is an archive (81 360 URLs), not the route. No key, no browser; seven requests for the whole board |
| Shaqo.com (Somaliland / Somalia) | `shaqo.md` | **Measured — browser route, no script.** Refused to our client (25-byte 403), served to a tab; a Nuxt/Hasura app whose explore page asks for a list filtered on `closing_date > now` and a count that is not — **the count says 4 574 (the archive), the page's own filter applied to the page's own counter says 23, and 23 rows come back**. 5 of the 23 are tenders. Hargeisa-based, Somalia-wide. One GraphQL POST from the tab is the adapter |
| Maliemploi (Mali) | `maliemploi.md` | **Measured — no adapter, and the reason is the host.** Served to the declared client (four requests, four 200 — the country page's «403 intermittent» not met), **and every path is the front page**: `/robots.txt`, `/wp-json/…` and `/` return the same 193 913 bytes, the feed holds «Hello world!». Seven posts on that page, all Bamako, linked to `/` — no address per post, so no stable id and no second page. Re-measure the day permalinks resolve |
| Kazibongo (Tanzania) | `kazibongo.md` | **Measured — the rules file itself answers 403** (openresty, twice, 2 s apart), so the guard is `host-closed` and nothing past it was requested: no root, no listing, no browser tab. Not a verdict on the board — a refusal at the rules does not say what it refuses. Reopens when `robots.txt` answers anything but 403 | **Browser measured 2026-09-13 16:25 UTC: the same 9-byte «Forbidden» to a tab — a refusal to everyone (borne 0), `route: none`**
| Ghanajob.com (Ghana) | `ghanajob.md` | **Measured — browser route, no script.** AfricaWork family: managed template, 25-byte 403 to the declared client (twice), served to a tab with no challenge. **«262 Job ads found», 262 distinct addresses walked — equal, once the walk starts at `?page=0`**: the pager is zero-based, and a walk from `?page=1` is exactly one page short. The page carries a JobPosting a strict JSON parser rejects (control characters) — read it tolerantly, never report «none» |
| Namijob.com (Namibia) | `namijob.md` | **Measured — browser route, no script.** AfricaWork family: managed template, 25-byte 403 to the declared client (twice), served to a tab. **«144 Job ads found», 144 distinct addresses from `?page=0`** — equal; the host where the zero-based pager was caught (119 from `?page=1`). A JobPosting behind malformed JSON, read tolerantly. The only board of its country here |
| Sierraleonejob.com (Sierra Leone) | `sierraleonejob.md` | **Measured — browser route, no script.** AfricaWork family: managed template, 25-byte 403 to the declared client (twice), served to a tab with no challenge. **«52 Job ads found», 52 distinct addresses from `?page=0` — equal.** A JobPosting behind malformed JSON, read tolerantly. Procedure = `ghanajob.md`'s with this host's paths |
| Rwandajob.com (Rwanda) | `rwandajob.md` | **Measured — browser route, no script.** AfricaWork family: managed template, 25-byte 403 to the declared client (twice), served to a tab with no challenge. **«84 Job ads found», 84 distinct addresses from `?page=0` — equal.** A JobPosting behind malformed JSON, read tolerantly. Procedure = `ghanajob.md`'s with this host's paths |
| Emploi.ga (Gabon) | `emploi-ga.md` | **Measured — browser route, no script.** AfricaWork family: managed template, 25-byte 403 to the declared client (twice), served to a tab with no challenge. **«67 Offres d'emploi trouvées», 67 distinct addresses from `?page=0` — equal.** A JobPosting behind malformed JSON, read tolerantly. Procedure = `ghanajob.md`'s with this host's paths |
| Emploi.ci (Côte d'Ivoire) | `emploi-ci.md` | **Measured — browser route, no script.** AfricaWork family: managed template, 25-byte 403 to the declared client (twice), served to a tab with no challenge. **«392 Offres d'emploi trouvées», 392 distinct addresses from `?page=0` — equal.** A JobPosting behind malformed JSON, read tolerantly. Procedure = `ghanajob.md`'s with this host's paths |
| Wantedly (Japan) | `wantedly.md` | **Not a board, by its own description — no adapter.** «共感でつながるビジネスSNS», 4.5 million users and 40 000 companies: a business social network whose unit is a company's «project» inside a signed-in graph, not a vacancy. Rules open, transport 200 to the declared client — the door is not the reason. `/projects/` not walked, on purpose |
| Barbados Job Register (Barbados) | `barbadosjobregister.md` | **Measured — no open path.** The register the Ministry of Labour points to: `www.` refuses its rules file (403 ×2, `x-cache: CONFIG_NOCACHE`) and the apex fails its TLS certificate (INDETERMINATE, not probed). Nothing past the rules was requested, no browser opened — the same shape as `kazibongo.md`, and the same doctrine question | **Browser measured 2026-09-13 16:26 UTC: «Request is Blocked by Firewall» to a tab as well — everyone from here (borne 0), `route: none`; a reader inside Barbados is the untested route**
| Kariera.mk (North Macedonia) | `kariera-mk.md` | **Not shipped — measured and closed at the transport.** Root *and* sitemap answer 403 with 25 bytes, `Your request was blocked.`, md5 `9ccabba2…` — **the same body byte for byte as `jobstore` and `hays`**, so it is a vendor default and not this operator's words; the table in `robots-policy.md` now lists three. Its rules file names only `Googlebot-Image`: no `*` group and no record for us, which is **silence towards us, not a permission** — the second groupless shape found that day, and not the one that opened #180. Rules open, transport closed: a **candidate** for the browser branch, not a plan |
| iHarare Jobs (Zimbabwe) | `ihararejobs.md` | **Shipped — the country's only reachable board**, its rank-1 answering HTTP 500. **Reading it changes it**: `lastmod` moves when a page is fetched, and of the 6 dates that moved between two reads 7 min 41 s apart, **6 were pages we had fetched and 0 of the 6 286 we had not**. That is why 60.5 % of the file carried the current date. `--since` is refused on the sitemap and offered only with `--fetch`. **The rules file has no `User-agent:` line**, so its seven `Disallow:` bind nobody and the guard opens all seven (#180) — the adapter refuses them itself. Dates are Django AP style (`Sept.` is four letters); **6 of 8 need `strict=False`**; an unknown slug answers **200 with the listing page** |
| JobWeb Rwanda (Rwanda) | `jobwebrwanda.md` | **Shipped — Rwanda's first adapter.** *A first version of this row called it «the control board of the fabrication screen» and quoted 1 % against 19–40 %; **neither figure was measured here**, they are quoted from the country page, and the network transversal reports 53–61 % for the same quantity — see the correction on the card.* **558 advertisements, 167 distinct dates, busiest day 1.4 %** — the most evenly spread board measured here — **and 0 since 2026-08-01**: it published for seven years and stopped in June. **The host asks `Crawl-delay: 30` and gets it**, so `--fetch` is half a minute per ad. **The root redirects into a login loop and the advertisements are public anyway** — the verdict is taken where the ads are, and no account is created. `lastmod == datePosted` on 3 of 3, so `--since` costs one request |
| Careerical Sierra Leone | `careerical-sl.md` | **Shipped — Sierra Leone's first adapter, and NOT the network node** (the country page names both and separates them). **2 344 advertisements across three named sitemaps**, 1000+1000+344 with **0 duplicates between files**; 1 377 distinct dates and a busiest day of **0.3 %**, the flattest measured here, still publishing. **Its `ld+json` is HTML-escaped and invalid** — `@context` truncated on all, unescaped quotes inside `description` on a third, **0 of 6 parsed as valid JSON** — so the adapter extracts fields rather than parsing the document, and counts which path each ad took. **The place is in the wrong fields**: `addressLocality` empty, town and country pipe-joined into `addressRegion` and copied into `postalCode` |
| UzJobs (Uzbekistan) | `uzjobs.md` | **Shipped — Uzbekistan's first adapter, and Central Asia's.** The country page recorded it as answering *«200 et du charabia»*; measured today there is **no redirect chain and one correct declaration**, `charset=windows-1251`, and `decode_body` returns clean XHTML. **One request to the feed the site links returns 21 advertisements complete** — employer, region, salary and **both ends of the posting period** — with no page opened. **21 is the feed's window, not the board**: the vacancy list paginates through a form that was not exercised, and its ids run to 33951. **The board publishes age and gender requirements**; they are emitted plainly and cannot be filtered on |
| XpressJobs (Sri Lanka) | `xpressjobs.md` | **Shipped, and Sri Lanka's first adapter.** **2 761 distinct advertisements** over 219 pages of the JSON API its own front end calls — the path is not in the 4.3 MB bundle and was found by loading one page in a browser, but every fetch goes through the ordinary guarded fetcher. **The board's own `recordCount` says 4 364 and that counts ROW SLOTS**: the pager serves exactly 4 364 and **1 603 of them are repeats**, so the declared total and `218 × 20 + 4` agree with each other and neither counts the board. *Paced at 3 s — measured: 1.5 s took HTTP 400 at the 26th request* |
| Emplois Congo (RD Congo) | `emploiscongo.md` | **Shipped, and RD Congo's first adapter — a closed archive rather than a board.** 446 advertisements, 2019→2026, **1 since 1 August and it is closed**; 7 of 7 sampled closed, the three most recent included. **Same operator as `jobartis`**: the two rules files are byte-identical once the first-party host is normalised, and this one names `info.jobartis.com`. **The template transposed and the defect did not** — `jobartis` hides 2 294 ads under a bare slug, this host has **zero**, checked. **The slug is not canonical**: a truncated one resolves to the same id, so the ledger key is `data-job-id`. No state is ever reported «open» — that marker has never been observed here |
| Jobartis (Angola) | `jobartis.md` | **Shipped, and it raises a figure two other cards carry.** **40 882 advertisements, not 38 547**: the board serves them under *two* URL forms — 38 588 under `/emprego-<slug>` and **2 294 under a bare `/<slug>`**, and only the first had ever been counted. They are not the same ads twice: of the 113 slugs in both forms, the pair fetched is two different vacancies from one employer, 2014 and 2015. **The largest archive in Angola and the smallest flow** — 216 since 1 August against `angoemprego`'s 924, with 18.5 % of the file on one 2018 day and the bare corpus frozen since 2026-07-30. **One second between requests draws alternating 503s**; it paces at five, and `list` needs one request |
| Ango Emprego (Angola) | `angoemprego.md` | **Shipped.** **The smallest archive of the three Angolan boards and the largest flow** — 1 434 held against `jobartis`'s 40 882 (corrected 2026-09-07 from 38 547, which counted one of its two URL forms), and 924 published since 1 August against its 216. **Two blocks with six years of nothing between**: 349 from a 2020 launch and 1 085 from 2026-07-29 onward, so `--since` is what makes it usable. The busiest-day check fired at 15.8 % and reading the distribution said what it was. **Its dates were suspected of being regeneration stamps and are not** — `lastmod` equals `datePosted` on 4 of 4. Two named job sitemaps, never a `job_listing*` wildcard: the taxonomies match it |
| Angola Emprego (Angola) | `angolaemprego.md` | **Shipped, and Angola's first adapter.** **3 724 advertisements under `/vagas/` in a flat sitemap of 9 111** — the rest is a news site, so counting the file would be wrong by a factor of 2.4. `lastmod` on 3 724 of 3 724, so `--since` costs one request. **The busiest day is 2.8 %**, which is the check that `jobartis` fails at 18 % in a single 2018 import: a high count of distinct dates does not protect against one. **`strict=False` is load-bearing** — the `JobPosting` block carries a raw control character and a single-attempt parser reads every advertisement as having no data |
| GLMIS (Ghana) | `glmis.md` | **Shipped, and Ghana's first adapter** — its only other card, `melr-gh.md`, is the ministry site and is not a board. **The hostname was read, not composed**, and the card records how: a search summary attributed it to an article that, when fetched, names no address at all. **No pagination exists**: the listing is a GET form, and reach comes from its declared filters — 12 distinct advertisements over 7 requests, ids 2312–5424. **Two queries returned exactly ten, so a per-query cap is not ruled out and no total is stated.** No `ld+json` anywhere; `JobPosting` appears nine times on the homepage and every one is a path segment |
| Jobrapide (francophone Africa) | `jobrapide.md` | **Shipped.** No sitemap, no `JobPosting` — the route is the WordPress category archive and the parsing is HTML. **Consecutive pages overlap and not by a fixed amount** (2, 0, 1 over three boundaries; 40 rows, 37 distinct), so the adapter deduplicates and reports what it dropped. The posting date is on the archive page, so `--since` costs no extra request. **No country is emitted per advertisement**: reading it from the slug called `mamoudzou-france` and `grand-est-strasbourg` *no country*, so the board's scope is wider than the ten its card declares. Scholarships and tenders outnumber vacancies, hence a `--category` that defaults to the recruitment archive |
| Go Zambia Jobs (Zambia) | `gozambiajobs.md` | **Shipped.** **358 advertisements**, `JobPosting` on 10 of a random 10 — larger than `jobsearchzm` and `jobzambia` together, **and the overlap between the three is unmeasured**, so their sum is three readings and not a count of Zambian vacancies. **The sitemap lost ten entries in two days**, so it is not an archive that only grows. It carries no `lastmod` and the advertisements carry `datePosted` and `validThrough` on 10 of 10: the dates live one level down, and `--since` / `--live` need `--fetch`. `baseSalary` is emitted here — `ZMW` with real figures, against the `négociable XPF` that gets it dropped on `burundijobs` |
| Job Search Zambia | `jobsearchzm.md` | **Shipped.** **153 advertisements** in `job_listing-sitemap.xml`, raw 153 / distinct 153, no duplicates, measured 2026-09-05. No site-served counter to check it against, and the card says so rather than leaving the figure unwitnessed. Its neighbour `bestzambiajobs.com` carries the same managed `robots.txt` and serves a Turkish sports-streaming page — **a Zambian-sounding name does not make a Zambian board**, and the body was read before the count was believed |
| Kumari Job (Nepal) | `kumarijob.md` | **Shipped, and Nepal's first adapter.** **167 advertisements** in `sitemap-jobs.xml`, raw 167 / distinct 167, no duplicates, across 106 employers, measured 2026-09-07. **Three of its eight sitemap children have "job" in the name and one holds advertisements** — the other two are facets (`/job-listing/banking-jobs-in-nepal`, `jobs-by-city`), so reading every file whose name says job would report 227. *That is `merojob.com`'s sibling-tender trap with the categories inverted, and a filename filter built against one lets the other through.* And its listing dates the FILE, not the ads — 2 distinct `<lastmod>` over 167 entries against ads spanning 2026-08-20 to 2026-09-07 — so `--since` refuses without `--fetch` rather than filtering on a regeneration date |
| MeroJob (Nepal) | `merojob.md` | **Shipped.** **239 advertisements** in `sitemap-job_post-1.xml.gz`, raw 239 / distinct 239, no duplicates, measured 2026-09-07. **The index is on `merojob.com` and all fourteen children on `sg.merojob.com`** — the host `robots-policy.md` rule 5 was written about — and both are declared. Its sibling `sitemap-tender_post-1.xml.gz` holds **15 940 tenders**, so tenders are rejected **by path** (`/etender/`, depth 2) and never by filename: *`lastmod` separates facets from content but not tenders from jobs, since both regenerate*. And its sitemap dates are **inert** — an ad posted 2026-09-07 carries 2026-09-04 — so `--since` refuses without `--fetch` |
| Mero Rojgari (Nepal) | `merorojgari.md` | **Shipped.** **583 advertisements** counted in 3 of its 9 `job_listing-sitemap*.xml`, all under `/job/`, measured 2026-09-07. **Its nine files all carry `lastmod 2026-07-20` — forty-nine days stale — and the board is ALIVE**: a sample spread across the files keeps 3 of 3 that carry a `JobPosting`, expiring into November, and `--file 1 --fetch --live --limit 4` keeps 4 of 4. *The stock and the flow classify in opposite directions, so "archive" was a description and not a measurement.* Every ad is posted LATER than the entry listing it, so `--since` refuses without `--fetch`; `--file N` reads one of the nine date windows rather than 1 766 pages |
| Todas Vagas (Mozambique) | `todasvagas.md` | **Shipped, and Mozambique's first adapter.** **855 advertisements** under `/vaga/` in a FLAT `sitemap.xml` of 914 `<loc>` — not an index — raw 855 / distinct 855, measured 2026-09-08. **The other 59 are 52 `/dicas/` articles and 7 site pages, and the path is what sorts them**: one file, and almost all its dates are the same day, so neither a filename nor a `lastmod` could. Its sitemap stamps **900 of 914 rows with the regeneration date** while the ads span 2026-01-19 to 2026-09-08, so `--since` refuses without `--fetch`. **And its file runs NEWEST first** — the opposite of `merojob` — so `--limit` reads the fresh end here and the stale end there; each adapter says which |
| Zaposli.ME (Montenegro) | `zaposli-me.md` | **Shipped, and Montenegro's first adapter** — **423 advertisements** under `/posao/`, raw 423 / distinct 423, measured 2026-09-08. **The sibling `pretrage.xml` holds 311 facet URLs under `/oglasi-za-posao/` — the path that says "job advertisements" while the advertisements say only "job"**, so a substring filter keeps exactly the wrong ones. **No `JobPosting`**: four markup anchors, each counted unique on three ads first, and the *first* `<h1>` is a page banner identical on all 423. Its twelve month names are exercised and the negative control is PRINTED. **`--since` is answered from the listing** — the one board of seven whose sitemap date is per-ad and never later than the site's own |
| Prekoveze.me (Montenegro) | `prekoveze-me.md` | **Shipped — Montenegro's second current stock, and the same sitemap skeleton as `zaposli.me` with none of its anchors.** Identical child file names and identical URL scheme, and **`zaposli.py`'s four anchors return nothing on three of three pages here while returning all four fields on one of its own** — checked in both directions. **243 advertisements, raw 243 / distinct 243, read 243, incomplete 0, across 113 employers and 53 place names, 2026-09-08**; no deadline is in the past, so it is a stock and not an archive. **Every field is read from the tooltip, because the visible cell is truncated** — `Administracija, Nekr&hellip;` against a `data-original-title` carrying all three categories, and one advertisement whose place is `Podgorica, Budva, Radanovići`; a text extractor would have returned a shortened string, never an empty one. **The `ld+json` is a decoy**: two blocks, no `JobPosting`, and their `addressLocality` is the publisher's own Podgorica office on every advertisement including those in Bar and Budva. **The deadline is read twice** — `22.9.2026.` and `unavailable_after: 2026-09-22` — and every disagreement is named; they agreed 243 of 243. **210 of the 243 addresses are non-ASCII (86 %)**, so `wire_url` is load-bearing, not a precaution. **`--since` prints its own limitation**: this board publishes no posting date at all, so `<lastmod>` has nothing on the page to be checked against |
| ROCKEN (Switzerland) | `rocken.md` | **Shipped — the largest Swiss inventory this repository has met, and the cheapest to reach: plain HTTP, no key, no cookie, no browser.** The board declares its own count in its `<title>` — *«&nbsp;N offene Stellen&nbsp;»* — and the adapter prints it beside its own, which is issue #181's column one. **That count moved four times in one morning** (5 802 → 5 807), so a gap of one or two is the board drifting under the read and a gap of ten is not; and the comparison is made only on a complete walk, because after one page the difference is 5 796 and says nothing. **Each advertisement is linked TWICE on its page** — 20 links for 10 advertisements — and the first version of this adapter reported 20 duplicates for 20 advertisements, noise that would have hidden the one real drift among it; a repeat inside a page is a rendering artefact, a repeat across pages is the board moving. **`hiringOrganization.name` is `ROCKEN` on every advertisement**, so the field is emitted as `poster` and never as `employer` — blanking it by rule would be wrong on `jobeo-ch.md`, a board of the same kind where the same field carries the real employer. Two traps in the JSON-LD: `jobLocation` is a LIST, and reading it as a dict returns `None` for every field; and there is no `identifier`, so the id comes from the URL |
| BeBee (aggregator, 99 countries) | `bebee.md` | **Shipped — and the list was never missing, we were looking in the markup.** The card said `indeterminate` because the home page carries no enumerable list; **`robots.txt` declares `Sitemap: /sitemaps`, and that index IS the list** — 2 494 job files over 99 countries, plain HTTP, no browser. *The asymmetry matters: `/*?*page=`, `/*?*q=`, `/*?*sort=` and `/*?*location=` are disallowed, so the paginated search is closed and the sitemap is not.* **The anchor is the file's own length printed beside our count** — `50000 <loc> in this file: 50000 advertisement(s)` — counted before anything is parsed, and **no total is claimed from a bounded run**. **It is an aggregator and the poster is sometimes the origin BOARD**: three Swiss advertisements name `Equal.Jobs` (itself a Swiss board), `MAAG Group` and a housing cooperative, so the field is emitted as `poster` and never as `employer`. **The duplicate rate against the origin boards is NOT established and is not guessed** — a duplicate needs employer, title and city together, never a date two publishers set apart. The `delta-` files are counted and deliberately not read, because merging them would make a run's denominator unreproducible; `countries: CH` because Switzerland is the only one exercised |
| MyCareer (Maldives) | `mycareer-mv.md` | **Shipped — the Maldives' government employment service, which our country page of 2026-09-03 concluded did not exist.** Reached because `jobcenter.mv` went from `allowed=False` to `allowed=True` when the 2026-09-07 decision freed `Claude-User` from a refusal naming `ClaudeBot` — **the host did not change, the rule did** — and it redirects here. **Two quantities, both the site's own**: 1 397 unfiltered pages back to 2019-11-17, against **13 pages and 107 distinct live advertisements** under the site's own `filter[active]`. Counting the archive would overstate the live market by a factor of a hundred. **The obvious heuristic is wrong** — each dead card carries a `badge-expired` and the order looks newest-first, but pages 12 and 13 read `XXXXVXXXX` and `VVXXXVVXX`, so stopping at the first badge loses live advertisements behind dead ones; pages 1 and 2 agree with the heuristic and are adjacent, which is why they are not a sample. The filter is exercised **in both directions** — `active` gives 0 expired, `expired` gives 9 of 9 and shares nothing with it. **The walk returns 109 rows and 107 distinct addresses, and 109 is exactly what the home page prints**, so that agreement is not a check: both counts may double the same pair, and the adapter prints `rows_read` beside `found` and names each duplicate with its pages. Every field is on the listing card — **13 requests for the whole live market** — and `--since` refuses without `--fetch` (exit 8) because the dates are not. |
| Burundi Jobs (Burundi) | `burundijobs.md` | **Shipped, and the first adapter for Burundi.** The host was not undiscovered — **our own guard reported it closed** until the owner's decision of 2026-09-07 that a named refusal binds only the token it names; the managed block closes `ClaudeBot` and never mentions `Claude-User`. **The sitemap is an archive index, not a list of live pages** — all 160 entries fetched once and **52 answer 200 against 108 gone**, with a JobPosting on 52 of 52; `lastmod` does not separate them, so `--since` narrows and cannot replace fetching. `baseSalary` reads `négociable XPF` on every posting (the CFP franc, in Burundi) and `addressCountry` holds a province, so neither is emitted. Procurement notices share the file and are counted, not silently filtered |
| Jobs Botswana | `jobsbotswana.md` | **Shipped.** **367 advertisements, and the sitemap holds 368** — the extra is the listing page. Rank 1 in the country refuses us by the managed default, so this is Botswana's readable market. `--live` drops the expired, which stay in the file |
| Job Zambia | `jobzambia.md` | **Shipped.** 45 advertisements, all dated in the sitemap, so `--since` costs one request. **`--live` is refused here and implemented on `jobsearchzm`**: none of twelve advertisements read carried a `validThrough`, and a filter that drops nothing reads exactly like a board on which nothing expires |
| HelloJob (Azerbaijan) | `hellojob.md` | **Shipped.** **588 live advertisements, separated by the site itself** from 27 402 expired — the only board of the series that does the freshness work for us. No `JobPosting`; fields come from a labelled list, 8/8 on a sample |
| job.am (Armenia) | `jobam.md` | **Shipped.** **A rolling thirty-day window, not a size** — 1 185 advertisements on 2026-09-04, and the window lost a whole day between two readings two hours apart. Rank 1 refuses us. `employmentType` is Armenian free text and is renamed rather than passed on |
| *your board here* | — | See *Writing an adapter* below |

**Three rows above rest on a HiringCafe measurement that can no longer be
taken.** *`job-room` («&nbsp;the Swiss SMEs and foundations HiringCafe
misses&nbsp;»), `umantis` («&nbsp;HiringCafe does not index at all&nbsp;») and
`Pinpoint` («&nbsp;5th most common ATS in a 360-card HiringCafe sample&nbsp;»)
were measured 2026-09-03; since 2026-09-05 the licit route answers zero,
re-measured 2026-09-07 and unchanged (`hiringcafe.md`).*

**The figures stand and so do the three adapters. What is gone is the ability to
re-take them** — and for the two that are zeros, that matters more than for the
sample: **a zero of indexation is not a property of the board it is about, it is
the state of an index on a date.** *A stale percentage invites a challenge; a
stale zero is simply believed.*

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

### `witness:` — name the species, because they are immune to different things

A witness is not one thing. **Three kinds, and what each survives:**

| kind | vulnerable to | immune to |
| :-- | :-- | :-- |
| **second reading** of the same source | the net-to-flow ratio | — |
| **second source** on the same quantity | the two sides answering different questions | the flow |
| **conservation** over a closed partition | — | both |

**A second reading compares a net to a flow that is usually unknown.** `wttj`
moved +691 against 42 637 entries with a recent `lastmod` — 1.6 %, and the
argument closes on both branches: real dates make the net a sixtieth of the
gross, regeneration stamps make the flow illegible. `taleez` cannot even state
its flow; obtaining it costs 14 020 requests, and **naming that price is the
useful part of the line.**

**A second source is immune to the flow and exposed to a mismatch of
question.** `jobsbotswana`'s site says 5 123 against a sitemap of 367 — a
factor of fourteen, which **refutes rather than confirms**: it establishes the
figure was mis-named. *Somebody looked* is not *the figure is confirmed.*

**A conservation needs neither.** `hellojob`: 591 + 27 399 = 588 + 27 402
across a closed partition, where advertisements moving between live and expired
preserve the total and any other cause breaks the sum. It compares no net to
any flow.

**`keejob` is the model because it is both** — the sitemap read twice converged
on the site's own counter, so the agreement is on the value rather than on the
change, and the net-to-flow objection does not arise.

**Write the kind in the line.** A reader who knows which one it is knows what
it does not protect against; a line that only says *witness* invites the
strongest reading of the weakest evidence.

### A figure about another board is cited by reference, never by value

**A card owns the counts of its own board. Everywhere else, the same number is a
quotation with no provenance** — no unit, no command, no hour — *and those are
the three things a published count must carry.*

**Measured 2026-09-08.** `myjobsfiji.com`'s sitemap size appeared in **six**
files — three cards and three adapter docstrings — **and in none of them was it
dated**, while `myjobsfiji.md` itself published a different number *and*
separated its 190 advertisements from its other URLs. **None of the six was
wrong relative to the others**, which is exactly the failure: *six copies of one
measurement age together, so no comparison between them ever reveals it.* The
owning card had superseded them without ever declaring a correction, because its
author was measuring their own board and had no reason to look outward.

**And two of the six were docstrings**, which no re-reading of a card reaches.

> **Delete the number, keep the argument.** The six all carried the same
> methodological point — *«&nbsp;every entry shares one `lastmod`, so a freshness
> count would count one afternoon&nbsp;»* — **and that point is true whatever the
> count is.** The figure was decoration, and decoration that ages.

**So: name the other board and point at its card.** *If a reader needs the
count, `myjobsfiji.md` has it, dated, with the distinction the borrowed copies
had lost.*

**The check runs on the old value, after the cards are fixed:**

```bash
grep -rn '<the superseded figure>' shared/ skills/ bin/
```

*A correction made in the cards is complete from the point of view of whoever
makes it, and incomplete without any symptom.*

### `countries:` — the markets the board serves, not the market we measured

```
<!-- countries: CH -->
<!-- countries: MY SG -->
<!-- countries: * -->
```

**`*` means *more than a short list can carry*** — a worldwide aggregator, or
an ATS family whose tenants are wherever their employers are. Twenty-three of
the ninety-seven cards using this key already carry it.

**The country our figure came from goes in `content:`, with its date.** They
are two different facts and they were one key until 2026-09-05, when
`jobstore.md` was found declaring `countries: MY SG` four lines above three
`overlap:` declarations all saying **Swiss** — two formal declarations of the
same header contradicting each other, with nothing comparing them.

*That is not an author's slip: it is a key used ninety-seven times with no
definition written anywhere.* This paragraph is the definition, and it was
settled as an **arbitration** — the three readings available were `MY SG CH`,
the twenty-six, and `*`. The reasons for `*`: it answers the question a reader
actually asks — *does this repository cover my country* — the twenty-three
existing wildcards are exactly the multi-country boards, so majority practice
already meant markets; and the measured country now has its own key.

**The ninety-four other cards are not retro-corrected.** None is demonstrated
wrong, and a mass edit under a definition written afterwards would be worse
than the vagueness it replaced. `AnOverlapIsDeclaredOnBothSidesAndTheCopiesAgree`
catches the disagreements as they are declared.

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

**Declare the hosts your card is about**, on a line beside `verified:`:

```
<!-- hosts: www.example.com, api.example.com -->
```

`bin/host-drift.py` reads it and reports **the host that answered** against the
one declared. **A card without the line is reported UNDECLARED — not skipped,
and not guessed at**: `adapter-age.sh` already carries the reason a tool must
read a field and not prose, and the first draft of this one repeated the
mistake by pulling a hostname out of a regex literal.

**It found four on its first run**, three of them acquisitions nobody had
recorded — `jobs.recruitee.com` answering as `careers.tellent.com`,
`talent-soft.com` as `www.cegid.com`, and `entreprise.francetravail.fr` as
`pro.francetravail.fr`. **A card describing the access policy of a host that
no longer serves anything describes nothing**; the rules that apply are the
receiving host's.

**And where a host was not obvious, say where it was read** — optional, and one
line per card:

```
<!-- hosts-source: footer-countries block of a Sierra Leonean ad · 2026-09-03 -->
<!-- hosts-source: named by careerical.com's top-ten article, no domain given · 2026-09-04 -->
```

`<where it was read> · <YYYY-MM-DD>`. **The absence of this field is what let an
eighth host sit for two days inside files already held.** Seven siblings were
declared by a `footer-countries` block; `egyptjobsearch.com` was in the same
block, in fifty-one held files, and the count went from four to five to seven
without its provenance ever being written — so nobody could see that the number
had a source that could be re-read. **A count whose provenance is unwritten
cannot be audited by the person who produced it, which is the only person who
will.**

It is also where a host that has **no** resolvable domain is recorded rather
than dropped: *"named by \<source\>, no domain given"*. `Wzayef`, `Dubizzle` and
`Jobisland` were named in prose without one, and the rule against inventing a
TLD — which does not change — deleted them. **A deleted host and a host that
does not exist read the same afterwards.**

**And where a board's *content* has been examined, say what state that
examination is in** — on the same line block, optional, and meaningful by its
absence:

```
<!-- content: measured · fabrication sieve, 0.3% shared titles of 300 · 2026-09-04 -->
<!-- content: out-of-domain · the sieve assumes one labelling language · 2026-09-04 -->
<!-- content: assumed · read from the ad pages, no instrument run · 2026-09-04 -->
<!-- content: indeterminate · rules unreadable on 5 of 5 hosts, HTTP 202 with a 0-byte body · 2026-09-05 -->
```

`<state> · <method or reason, with the figure and its unit> · <YYYY-MM-DD>` — **three fields, and the state is one of four,
not two.** `shared/plausible-and-false.md` carries the reasoning; the short
version is that **an inapplicable result and a conclusive one are
indistinguishable once written down.** The fabrication sieve compares sets of
title words and *assumes the corpora label in the same language* — true by
accident across eight anglophone African nodes, false in Armenia, where three
boards write in transliterated Armenian, English and percent-encoded Armenian.
**A 0.3 % that cannot separate *independent* from *written differently* is not
a weak measurement; it is a measurement of something else.**

**The date and the unit are part of the value.** A share measured over 300 ads
on one day is true dated and false refreshed — the counter that expires by the
growth of its own denominator. **And where the denominator is small, publish
the composition rather than the quotient**: `20 : 2`, never 91 %, because the
number a reader would need to check the claim has already been divided away.

**No card carries this line yet, and that is deliberate.** Writing one requires
having run the examination; the declaration exists so that the day someone does,
the result has somewhere to live that is not a published artefact — which is
where the last one lived, readable by nobody holding the repository. Issue #140.

**Ask `skills/job-scan/scripts/_robots.py` before you fetch, and ask it about
the path — `verdict()` answers *is this host closed in one block*, and
`allowed(host, path)` answers the question an adapter actually has.** They are
different questions, and until #101 only the first existed:
`empleate.gob.hn` refuses `/Vacantes/` and `/Candidatos/` to `User-agent: *`
while `/` is absent, so `sweep` is **True** and every vacancy on it is
refused. **A green light on the host is not a green light on the path.**

**And say what you do with a refusal.** Counted 2026-09-03 across 61 adapters: **16 ask, 45 do
not.** The module was corrected three times that week — #96, #98, #99 — and
those corrections reach the sixteen.

**And the first thing to establish was whether it mattered today.** It does
not, yet: `verdict()` was run against the **40 public hosts** those adapters
read, and **0 refuse the sweep**. *So this is about knowing, not about a
breach* — and it is the shape of #82 and #91 once more: **the rule exists and
nothing calls it.**

**Three classes, and which one an adapter is in belongs in its board card:**

| Class | Adapters | Why |
| :-- | :-- | :-- |
| **1 — a published API with its own terms** | `adzuna`, `labonnealternance` (both load a key), `francetravail`, `arbeitsagentur`, `platsbanken` | The operator publishes the interface for programmatic use, through a developer portal or a state open-data programme. **`robots.txt` governs crawling a website; it does not govern an API published to be called.** Write that reason in the card — do not merely omit the call |
| **2 — public pages, and the host's file applies** — **wired, one exception** | the bulk: `computrabajo`, `hellowork`, `hiringcafe`, `randstad`, `randstadfr`, `stepstone`, `turijobs`, `wttj`, `jobstore`, `kalibrr`, `infoempleo`, `jobbkk`, `swissdevjobs`, `sozialinfo`, `fachkraft`, `freework`, `oposiciones`, `empleate`, `mycareersfuture`, `jobroom`, `apec`, `adecco`, `anefa`, `batiactu`, `crit`, `emploiterritorial`, `fhf`, `hays`, `jobology`, `jobsireland`, `meteojob`, `michaelpage`, `persigo` | **A keyless JSON endpoint on a site's own domain is the site's backend, not a published API.** `mycareersfuture` and `jobroom` are in this class for that reason |
| **3 — a family of tenants, one verdict each** — **wired** | `flatchr`, `recruitee`, `talentsoft`, `pinpoint`, `digitalrecruiters`, `solique`, `persigo` | **The verdict is per tenant**, which is the module's stated reason for existing — and `icims` and `taleez` already did it. Two Teamtailor tenants set `ai-input=no` while the repository recorded the permissive one as platform policy (#73) |

**Do not wire all forty-five at once.** A call added without the adapter
knowing what to do with the answer **is worse than no call: it looks like a
control.** Every wiring says what a `sweep: False` does — stop, and exit with a
code the caller reads.

**`hiringcafe` is the one class-2 adapter left unwired, and that is a refusal
to decide rather than a deferral.** `allowed()` returns **False** on the URL
shape it builds — `/*?searchState=*`, refused to `User-agent: *` — so adding
the gate would make it exit 7 on every request. **The adapter would stop
working, which is one of the three options #102 puts to the user, chosen by
default and dressed as a technical fix.** That decision is the user's; the
issue is open; the file is untouched. **This paragraph exists so nobody later
reads the omission as an oversight.**

**Class 2 and class 3 are done, and the shape each adapter took is the one to
copy.**
A `_robots_gate(url, tag)` sits inside the adapter's own fetch function, so
**every request is covered rather than the first one**, and it asks
`allowed(host, path)` — per tenant *and* per path, because a careers site that
refuses its ad path while leaving its root open passes a host-level check and
refuses every advertisement. A refusal exits **7** with the module's words,
and **a host whose rules could not be read exits 8** — see below.

**`sweep` and `allowed` have three values, not two.** `True`, `False`, and
`None` for *the rules could not be read*. **A failure to fetch used to come
back as a permission**: `nea.gov.kh` serves Cloudflare's managed block with
`User-agent: ClaudeBot / Disallow: /` — it closes everything to this project
by name — and a timed-out request produced `allowed: True` with the reason
*no rules were read*. Measured on the same host within the hour: when the
fetch worked, `allowed: False`; when it timed out, `allowed: True`. **The
permission was a function of the network, not of the policy.** Issue #118.

`None` is falsy, so `if not v["sweep"]` and `if v["sweep"]` both fail closed;
**the naive reading is the safe one**, which is what thirty-six call sites
needed. Exit **8** is the unknown, distinct from **7** because a host that
could not be reached has not refused anything, and reporting it as a refusal
puts words in an operator's mouth.

**Every record that names us binds us, not the longest-named one.** Measured
across 70 hosts, 2026-09-03: three name a token of this project, and
`www.linkedin.com` names **five** and does not answer them alike — `ClaudeBot`,
`Claude-Web`, `Claude-User` and `anthropic-ai` all get `Disallow: /`, while
`Claude-SearchBot` gets a path list and no blanket refusal. The selector took
the longest token, so it picked **the one permissive record out of five**, and
the module answered `sweep: True` on a host that closes itself to this project
by name four times over. **A test had pinned that rule.** RFC 9309 assumes one
product token per crawler; this project answers to six, so no record is
discarded: disallows are unioned and an `Allow` survives only where every
matching record grants it. `groups` lists them and `group_conflict` says when
they disagreed. Issue #117.

**Three formulations, not one.** *Named and refused* — the refusal is aimed at
this project. *Named and permitted* — `taleez.com` writes `User-agent:
ClaudeBot / Allow: /` under a `*` group that refuses thirteen paths, and that
is **consent written down, not the absence of a refusal**; the verdict now
says so, and says why the `*` refusals do not apply, before someone later
"corrects" an adapter into obeying them. *Not named* — the general policy.
The middle one had `reason: None`, which is also what a file saying nothing
about us produces.

**And a 403 is not an absence.** `barbadosjobregister.gov.bb` answers its
robots.txt with 403 and thirty bytes, "Request is Blocked by Firewall". That
used to be filed as `unreadable`, whose reason reads *absence of a file is not
a refusal* — true of a 404 and false here: **a server that says blocked has
replied, and it replied no.** It is now its own state and exits 7.

Measured after wiring: none of the seven platforms refuses today, and one
reports a cross-host redirect — `jobs.recruitee.com` answers from
**`careers.tellent.com`**. **A tenant platform that has been bought reaches an
adapter as a redirect before it reaches it as a rename**, and the gate prints
that rather than swallowing it.

`ssge.py` is the worked example, and it was the argument: it hard-coded its
refusals while `ss.ge`, `home.ss.ge` and `jobs.ss.ge` publish **three
different files**. It now calls `check_robots()` on the host it is about to
read, exits **7** on a refusal with the module's own words, and keeps its
Cloudflare stop **separate** — because that host says `Allow: /` and answers
`403`, so **the stop is not a robots verdict** and must not be written as one.

**`employtt.md` (Trinidad and Tobago) is the worked example of a listing that
looks complete.** Its `/jobs/list` serves 21 advertisements in one request; two
of them expired the day before and are still there, while `/jobs/view/2618`
renders a complete advertisement that expires *later* and is not listed.
**Membership tracks neither expiry nor recency**, so the adapter reports the
listing's count as the listing's and does not call it the board.

**`bayt.md` is where three layers give three answers.** Its `robots.txt`
permits the country listings and refuses the generic search — visible only per
path; **Cloudflare 403s every scripted request** including `/`; and the browser
renders the page in full. **A bot wall is not a refusal**, and the two are not
recorded as the same thing. The same card carries three mutually inconsistent
totals published in one view — header `5.8K`, prose `6 876`, and facet counts
that differ from the prose city by city — so **whichever number a person
quotes, the page contains two that contradict it.**

**When a page carries more than one `JobPosting`, say which one you take and
why.** Measured across seven boards' own advertisement pages on 2026-09-03:
six carry exactly one, and `mihnati.com` carries **two, byte-identical**. But
the adapters do not agree on which to take — nine use
`(postings(page) or [None])[-1]` and the rest take the first, four of them
written as a `for … return` loop. **Nobody wrote down why**, and on a page
holding two *different* postings — a main advertisement beside a related one —
the two choices are different jobs.

**Nothing doubles a total**: every `for d in postings(...)` loop in this
repository returns on its first iteration, so the duplicate is dropped rather
than counted twice. That was checked, not assumed. **The first-versus-last
split is left as it is** — changing twenty adapters on a difference that is
inconsequential on every page measured would be a rewrite in search of a
defect. A new adapter should take the first and say so.

**`emploitic.md` and `jobivoire.md` are a pair, and the pair is the lesson.**
Two neighbouring African boards, read in **opposite** ways, each for a reason
measured on it. Emploitic's sitemap is **declared in its own `robots.txt` and
current to the minute**, so the adapter uses it. JobIvoire's is undeclared,
holds **227 advertisements of 3 884, and its freshest entry is five weeks
old** — so that adapter paginates, and an adapter written on the sitemap would
have missed **94% of the board with 200s all the way and no error to catch.**

**Carrying the habit of one to the other is the only real risk in the pair**,
which is why each card names the other. **A sitemap is a route when it is
declared and fresh, not because it is a sitemap.**

**Two different requests must produce two different bodies.** Before trusting
any listing route, ask for something that cannot exist and compare. It is the
check `melr-gh.md` turns on — `/index.php/99/99/complete-nonsense-xyzzy` is
line-for-line identical to the real page — and `employtt.md` needs the same one
in another form, where a missing advertisement answers 200 with the listing.
**Neither the status code nor the response size separates them.** A router that
ignores the path, a CDN error page, an SPA shell and a real answer all return
200 with plausible bytes; **something answered, so it feels measured.** The
comparison is cheap, it can fail, and on two boards in one day it did.

**`mihnati.md` is where the platform underneath shows through the data.** Ten
of ten Saudi advertisements publish `baseSalary.currency: "PKR"` — the
Pakistani platform's default, on Jeddah and Riyadh salaries — and ten of ten
put the **employer's name** in schema.org's `identifier`. The adapter passes
both through under names that say what they hold, flags the currency, and
**converts nothing**: guessing the intended currency would be a second
invention on top of the first.

**`skillingpakistan.md` is a board that is empty and says so.** Its `/jobs`
table contains the words `No jobs available` under every filter, including
values drawn from its own occupation vocabulary — **a zero the board states,
not one a parser inferred**. The same page prints `Total Jobs 302,613` above
that empty table, under an *Employment Trends* heading: **a labour-market
statistic that reads as an advertisement count.** No adapter yet, because no
row has ever been available to parse and a parser written on column headers
alone would ship unverified.

**`saudi-labour-platforms.md` stops before an authentication wall, on purpose.**
Musaned and Ajeer both permit reading and neither is a board: Musaned's
marketplace lists **recruitment offices**, Ajeer exists so establishments can
lend workers to each other. The assessment stops at *not a board* rather than
at *needs a login*, because the second invites someone to make one — and the
records behind Musaned's login are individual migrant domestic workers, which
an adapter has no business collecting.

**`jobs-gov-pk.md` is where two counts of the same thing disagree.** The
board's own header says `1511 total` on one page and `5 total` on another,
while the markup carries 1 511 cards — and `5 total` beside `1506 expired` is
not arithmetic. **The adapter counts the cards and prints the header next to
them**, saying when they differ rather than picking one. Merging them would
have hidden it.

**`melr-gh.md` is the other shape of the same lesson.** Ghana's labour
ministry answers **200 with its home page under every URL** — including
`/index.php/99/99/complete-nonsense-xyzzy`, which is line-for-line identical to
`/index.php/6/7/job-seekers`. An adapter written there would have parsed the
home page's navigation as job data and reported a steady count for ever.
**The check that settles it is not the status and not the size: it is whether
two different requests produce two different bodies.**

**Not every portal becomes an adapter, and the ones that do not are worth a
card.** `chile-public-sector.md` records five Chilean government portals
assessed on 2026-09-03 and **why none of them yields one** — a training service
that is not a board, two publishing `Disallow: /`, one answering 403 on its own
rules file, and one whose data belongs to a host that refuses. **Without the
card, "no adapter" reads as "nobody looked"**, and the next person spends the
same day.

**Decode a response with `skills/job-scan/scripts/_decode.py`, not with
`utf-8`.** `decode("utf-8", "replace")` was this repository's house pattern —
32 adapters used it and none read the declared charset. **It is wired now**:
every remaining site reads the declaration, and `hiringcafe.py` is the one
exception, left alone because #102 is the user's decision. Issue #115.

**Chile's national employment service does not.** `bne.gob.cl` declares
`ISO-8859-1` in its header and `windows-1252` in its markup, and the house
pattern **loses 37 to 93 characters per advertisement, on eight of eight
sampled, without failing.** `errors="replace"` cannot fail: it returns
plausible text with holes, which is `shared/plausible-and-false.md`'s class
arriving in the transport layer.

`decode_body(raw, headers)` follows the header, then the markup — **an XML
prolog counts, which is how a sitemap declares itself** — then **strict** UTF-8,
then a total fallback, **and returns which one it used**, so a run that had to
guess says so.

**Measured before editing fifty-one files, on the 70 declared hosts,
2026-09-03**: 59 declare UTF-8, **3 declare something else**, 8 were
unreachable. `bne.cl` and `www.bne.gob.cl` say `ISO-8859-1`; `www.cadremploi.fr`
says **`ISO-8859-15`**, which is not the same thing — 8859-15 puts the euro
sign where 8859-1 has the generic currency mark, on a French board that quotes
salaries.

**And `www.cadremploi.fr` serves two charsets on two paths.** Its root declares
`ISO-8859-15` and loses **327 characters** when read as UTF-8; its listing page
declares UTF-8 and loses none. **So a per-site constant is wrong by
construction** — the declaration belongs to the response, and that is the
argument for reading it every time rather than fixing the three sites that
looked Latin-1 today.

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

### A regional aggregator is not discarded for being regional

**"It is not the country's board" is not a reason, and for a while it was one
that nobody had written down** — so from the outside it was indistinguishable
from an oversight. Issue #147.

**The decisive property is not scope, it is reach.** An aggregator carrying ads
in a country the plugin cannot otherwise read is not discardable at all, whatever
its shape. *Measured 2026-09-04 by the country survey, not re-measured here:*
`caglobalint.com` carries 183 ads across 24 countries — sixteen of them
Egyptian, where Wuzzuf, Jobzella and 3amal all refuse us; two Sudanese; and
**one Namibian, the only country in the corpus for which no host is known at
all.** `afriqueemplois.com` carries 149 across 17 national sitemaps.

**Discarding one is a conclusion, and it carries its evidence like any other.**
`africajobboard.com` is discardable because *it publishes no advertisement
sitemap* — a property of the site, checkable by whoever doubts it. That is the
shape a rejection takes here; "regional" is not.

**And it follows from a rule already on this page**: the criterion is whether
the population is *already covered by something shipped*. A regional host is
the case where it most often is not — it reaches exactly the countries where
nothing else answers.

### A host named without a domain is a third state, not a deletion

`Wzayef`, `Dubizzle` and `Jobisland` were named in prose with no domain. **The
rule not to invent a TLD is right and must not change** — but applying it
deleted them, and a deleted host and a host that does not exist read the same
afterwards.

**They are neither measured nor forgotten: they are unresolved**, and that is a
state worth writing. *An assertion of non-existence carries the search that
established it* — the section below says so for boards, and it applies here to
a name: **the honest record is "named by <source>, no domain found", never
silence.**

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

## An adapter that fetches twice consults the host's rate

**Use `skills/job-scan/scripts/_pace.py` in the fetch wrapper**, keyed by host,
so every request through it is spaced — including ones added later.

```python
from _pace import Pace
_PACERS = {}
def pace_for(host):
    return _PACERS.setdefault(host, Pace(host, own=<whatever this adapter already slept>))
```

**The delay comes from the host and never from a number we picked.** When the
host asks for nothing, `Pace` waits the adapter's own existing spacing and
nothing more: *a default of one second is a choice, not a measurement.* Where
both exist the longer wins, so an adapter's own politeness is never weakened.

**Pacing and back-off stay two things.** They had to be separated even to
count — 47 adapters carrying `time.sleep` turned out to be 43 spacing plus 4
backing off from 429/503. A retry answers the response; pacing answers the
rules.

Measured 2026-09-05: 65 of 71 adapters whose fetch wrapper could be identified
make several requests to one host — **92 %, the normal shape of a board adapter**
— and 33 had no spacing at all. `careers.icims.com` asks `crawl-delay: 5` and
`icims.py` gave none.

## A fetched body is saved with its provenance, or it is not saved

**Use `bin/fetch-body.py`, not an ad-hoc script.** It takes the guard on the
exact path, declares this project's identity, **tests the HTTP code**, honours
`Crawl-delay`, and writes the provenance beside the body:

```bash
bin/fetch-body.py https://host.example/robots.txt -o scratch/h.txt
bin/fetch-body.py https://host.example/s.xml -o s.xml --allow-refusal
```

**The population that loses provenance is not the adapters.** Enumerated
2026-09-05: of the 78 scripts in this repository that touch the network, **not
one writes a fetched body to disk** — they parse and emit. The only binary
write is `render-plain.py`, and it writes a PDF it generated. Every lost body
came from a one-off script in a scratchpad, and an audit of one session's
scratchpad the same day read **365 bodies, 0 with provenance**.


**Use `skills/job-scan/scripts/_provenance.py` whenever a retrieved body is
written to disk.** Not the filename — the filename is what failed.

```python
from _provenance import save, load, audit
save(path, body, url=exact_url, status=code, agent=UA)
body, prov = load(path)          # refuses a body with no sidecar
audit(directory)                 # names the orphans, and its own denominator
```

**What it cost to learn.** On 2026-09-05 a recount of the Cloudflare managed
default found **28 bodies identical to the byte**. Eighteen could be
attributed; ten could not, and **eight of those are unrecoverable** — the file
contains no reference to the host serving it, so nothing inside it will ever
say where it came from.

**The filename was the only place the host existed, and it had been
abbreviated.** `sl_rb` meant Somaliland. The obvious repair — read sibling
files sharing the country prefix — answers *Sierra Leone*, because the other
`sl_*` files are Sierra Leonean. **That is the single case where the
instrument's answer could be checked, and it is wrong**, which is the only
reason anyone knows it is wrong.

So: `url`, `status`, `agent` are keyword-only **with no defaults** — a call
that forgets one fails where it is written rather than producing a file that
looks complete and is unattributable tomorrow. `bytes` and `md5` are of the
**raw** body: no strip, no newline normalisation, no decode. A md5 of a
stripped body differs too, and three files appeared to have changed overnight
on exactly that.

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
