# Board adapter — Trenkwalder Slovakia (`sk.trenkwalder.com`, SK): the staffing network's Slovak front, whose rules name `Claude-User` and open everything but `/api/*` at `Crawl-delay: 10`; the listing server-rendered with its search state — `nbHits` 32 on 2026-09-14, printed beside every walk — and the jobs sitemap for what the first page does not carry; the `recruiter` object on every record never emitted

<!-- verified: 2026-09-14 -->

<!-- hosts: sk.trenkwalder.com -->
<!-- script: trenkwalder.py -->
<!-- host-forms: sk.trenkwalder.com -->
<!-- host-forms-basis: read — every hit carries `web.jobUrl` on the host and the sitemap names `/jobs/<objectID>` on it; `trenkwalder.py` names the host in `BOARDS["sk"]` and builds every address on it · 2026-09-14 -->
<!-- countries: SK -->
<!-- content: measured · **`/jobs` (200, 620 647 B) is a Next.js page whose `__NEXT_DATA__` carries the Algolia search state the site rendered — `initialResults[<index>].results[0]`: `hits` (30, one page) and `nbHits` (32 on the day), the number the page prints («Našli sme pre Vás 32 možných výsledkov»); the pager is client-side (`?page=2` serves the same first page, byte-identical), so the ids the first page does not carry come from `/sitemap-jobs` (6 694 B, 32 rows with lastmod 2026-06-24 … 2026-09-11) and are read from their pages, whose `pageProps.job` is the same object; 32 emitted, 32 stated — equal** — read by the declared client, the guard on the exact path (the rules, 878 B: `Claude-User` named with `Allow: /` and `Disallow: /api/*`, `/_next/*`, `/admin/*` — the same for `*`, OAI-SearchBot, PerplexityBot, Claude-SearchBot; Semrush, Dotbot, Bytespider and Scrapy refused; `Crawl-delay: 10`, honoured); the record is the site's object: title, place, postal code, region and country in the national language (29 Slovakia, 3 Austria), category, industry, blue/white collar, placement (27 «Interná pozícia u klienta», 4 leasing, 1 payroll), schedule and hours, tags, the branch office, `startDate`/`endDate`/`lastChange`, and the four HTML texts (company, description, requirements, benefits) scrubbed of e-mails and Slovak/Czech/Austrian/German telephone numbers; **the salary — `salaryMin`/`salaryMax`, `currency`, `salaryPeriod` — read only when `publishSalary` is true: 13 of 32 (10 per month, 3 per hour, all EUR), `salary_unit_stated` on each; `recruiter` {firstName, lastName, email, phone, mobilePhone, contactInfo, quote} on every record — never emitted; `applicationUrl` a form, never touched; the client employer described in the text and never named (`account.logoShow` false), the agency as employer** · 2026-09-14 -->
<!-- witness: the page's own `nbHits` — printed beside every walk («32 emitted (30 from the listing's first page, 2 read from their pages, 0 gone), the site states 32 — equal»); a page without a search state exits 6, a job page without its `job` exits 6; `/api/*` refused before the gate (exit 7) · 2026-09-14 -->

**Trenkwalder is an Austrian staffing group with a Slovak front of a few dozen
advertisements — production, logistics, engineering, some white-collar — 32
stated on the day, three of them for Austrian plants.** Issue #349. Measured
2026-09-14 03:3x UTC by the declared client, the guard on the exact path
before each request, ten seconds apart as the rules ask.

## What the rules say, and what the page carries

```
sk.trenkwalder.com/robots.txt             200, 878 B — User-Agent: Claude-User: Allow /, Disallow /api/*, /_next/*, /admin/*; Crawl-delay: 10 (the `*` group the same; Sitemap ×4)
GET https://sk.trenkwalder.com/jobs         200, 620 647 B — __NEXT_DATA__: serverState.initialResults[PROD_SK_New_Index_1_date].results[0]: hits[30], nbHits 32, hitsPerPage 30, nbPages 2
GET https://sk.trenkwalder.com/jobs?page=2  200, 620 647 B — the same bytes: the pager is client-side, the state is page 0 whatever is asked
GET https://sk.trenkwalder.com/sitemap-jobs 200, 6 694 B — 32 <url> rows /jobs/<objectID> with lastmod
GET https://sk.trenkwalder.com/jobs/<id>    200, 195 440 B — __NEXT_DATA__: pageProps.job (the same object as a hit), a JobPosting JSON-LD
```

The site's search runs on Algolia from the browser; the page ships the first
page of results in its state. **The plugin reads that state and never calls
`/api/*`, which the rules refuse to `Claude-User` by name** — `request()`
exits 7 on any `/api/` path before the gate. The second page of results is
not reachable by a URL: the adapter takes `/sitemap-jobs` as the list of ids,
reads from their pages the ones the first page did not carry, and prints
emitted against `nbHits`.

## The record, and what is withheld

Every hit is one object of ~40 fields. The adapter emits the site's own
values in the national language (`{en, national}` pairs → `national`), the
agency as employer, and the salary only when the site publishes it —
`publishSalary` false on 19 of 32, and their `salaryMin`/`salaryMax` are in
the object anyway, unread. **`recruiter` — first and last name, e-mail,
telephone, mobile, a quote and a photo — is on every record and never
emitted; the four texts are scrubbed; the application form is never touched.**

## Running it

```
python3 skills/job-scan/scripts/trenkwalder.py list                 # 32 rows, ~3 requests + 10 s each
python3 skills/job-scan/scripts/trenkwalder.py list --limit 10
python3 skills/job-scan/scripts/trenkwalder.py sitemap              # the 32 ids with lastmod, no page read
python3 skills/job-scan/scripts/trenkwalder.py ad https://sk.trenkwalder.com/jobs/<objectID>
```

Exit codes: 0 all read · 3 the ad is gone · 6 a 200 without the state (the
template changed, never an empty market) · 7 a refused path. No key, no
browser, no login. Other Trenkwalder fronts (`www.trenkwalder.com/at`, `.cz`,
`.hu`, `.pl`, …) are the same stack and are not measured here; a `--host`
entry in `BOARDS` is the shape, each with its own `adapter` issue first.
