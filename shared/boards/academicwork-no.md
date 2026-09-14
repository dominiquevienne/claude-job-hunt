# Board adapter — Academic Work Norway (`www.academicwork.no`, NO): the Nordic staffing and recruitment network's Norwegian front, whose listing states its count on the server («40 treff» on 2026-09-14) but pages by a server action — the jobs sitemap as the inventory, each ad read for the `advert` object its page ships; the consultant (`owningCm`) never emitted

<!-- verified: 2026-09-14 -->

<!-- hosts: www.academicwork.no -->
<!-- script: academicwork.py -->
<!-- host-forms: www.academicwork.no -->
<!-- host-forms-basis: read — every sitemap row and every advert's `absoluteUrl` is on `www.academicwork.no`; `academicwork.py` names the host in `BOARDS["no"]` and refuses an ad address on any other · 2026-09-14 -->
<!-- countries: NO -->
<!-- content: measured · **`/ledige-stillinger` (200, 365 554 B) is a React Server Components page (Next.js on Payload CMS, tenant `NO`) whose flight data states «Søk blant 40 ledige stillinger», «40 treff» and the pager's props `{"currentPage":1,"pageSize":10,"totalItems":40,"setPage":"$h4f"}` — `setPage` is a server action, not a link, and `?page=2` serves the same ten cards; the ten cards are rendered markup, not objects. `/sitemap.xml` (200, 159 rows) names 40 `/ledige-stillinger/j/<slug>/<id>` jobs with lastmod (2026-05-08 … 2026-09-11) beside 119 pages, articles and programmes. Each ad (200, ~256 KB) ships `"advert":{…}` in the same flight data — id, title, `publishTimestamp`/`unpublishTimestamp`, start date and its wording, `locations[]` with coordinates, `locationCity`, business area, category, role, `jobType` (23 «Bemanning» staffing, 16 «Rekruttering» recruitment, 1 English «Staffing»), `workExtent` (38 full-time, 1 part-time), a labelled summary («Andre»: hybrid), `companyName` when `showCompanyName` (37 of 40), `externalApplicationUrl` (none on the day), and `advertText` {leadIn, yourNewWorkplace, workTasks, requirements, clientInformation} whose long texts are `$<id>` references to `T<hex>,` chunks read by byte length (Markdown); no JSON-LD, no salary field. 40 emitted, 40 stated — equal, 42 requests in 83 s** — read by the declared client, the guard on the exact path (the rules, 319 B: `*` `Allow: /`, `Disallow: /api/`, `/admin/`, `/auth/`, `*/auth/`, `/_next/`, `/public/`, the seven `/<lang>/auth/`; no Crawl-delay, 2 s ours; `/api/` refused before the gate); **`owningCm` {employeeRef, name, email} — the consultant manager — on every advert and never emitted; the five texts scrubbed of e-mail addresses and Norwegian telephone numbers (50 withheld on the day — «kandidat@academicwork.no» in every recruitment-process paragraph); `contacts_withheld` on every record; the application form (`/auth/`) never touched; the client named only when the site names it, the agency as employer on staffing ads** · 2026-09-14 -->
<!-- witness: the listing's own `totalItems` (else «N treff») — printed beside every walk («40 emitted (40 in the sitemap, 0 gone), the site states 40 — equal»); a listing without the count exits 6, an ad page without its `advert` exits 6 — a changed template, never an empty market · 2026-09-14 -->

**Academic Work is the Nordic staffing and recruitment network for young
professionals — 40 advertisements stated on the Norwegian front on the day,
technology and IT first (25 of 40), Oslo and Trondheim most, the client named
on 37.** Issue #370. Measured 2026-09-14 03:4x–03:5x UTC by the declared
client, the guard on the exact path before each request, two seconds apart.

## What the page states, and why the sitemap is the inventory

```
www.academicwork.no/robots.txt              200, 319 B — User-Agent: *: Allow /, Disallow /api/, /admin/, /auth/, */auth/, /_next/, /public/, /<lang>/auth/ ×7; Sitemap: /sitemap.xml
GET https://www.academicwork.no/ledige-stillinger          200, 365 554 B — flight data: «40 treff», {"currentPage":1,"pageSize":10,"totalItems":40,"setPage":"$h4f"}, 10 cards as markup
GET https://www.academicwork.no/ledige-stillinger?page=2   200 — the same ten cards: the pager is a server action, not an address
GET https://www.academicwork.no/sitemap.xml                200, 159 rows — 40 /ledige-stillinger/j/<slug>/<id> with lastmod, 119 other
GET https://www.academicwork.no/ledige-stillinger/j/<slug>/<id>   200, ~256 KB — "advert":{…} in the flight data, its texts as $<id> references to T chunks
```

The count is stated and read; the pages beyond the first are not addressable
by a URL, and the CMS's own routes under `/api/` are refused in writing. So
the adapter prints the listing's `totalItems`, takes the sitemap's job rows
as the inventory, reads each ad from its page's own object, and prints
emitted against the stated count.

## The record, and what is withheld

The advert object is emitted as the site wrote it — title, lead-in, the
client when shown (`company`, `company_site`), `agency` «Academic Work»,
`job_type` with its id (`employer_is_the_agency` on staffing ads), place and
located cities with coordinates, business area / category / role, extent,
start date and wording, «Andre», posted and valid-through, and the four
sections (about the job, tasks, requirements, about the company). **`owningCm`
— the consultant manager's employee reference, name and e-mail — is on every
advert and never emitted; the texts are scrubbed; the application form is
never touched.**

## Running it

```
python3 skills/job-scan/scripts/academicwork.py list                # 40 rows, 42 requests, ~85 s
python3 skills/job-scan/scripts/academicwork.py list --limit 10
python3 skills/job-scan/scripts/academicwork.py sitemap             # the 40 ids with lastmod, 1 request
python3 skills/job-scan/scripts/academicwork.py ad --url https://www.academicwork.no/ledige-stillinger/j/<slug>/<id>
```

Exit codes: 0 all read · 3 the ad is gone · 6 a 200 without the count or
without the advert (the template changed, never an empty market) · 7 a
refused path. No key, no browser, no login. The other fronts (`.se`, `.fi`,
`.dk`, `.de`, `.ch`) are the same stack under another tenant — a `--host`
entry in `BOARDS` is the shape, each with its own `adapter` issue first;
only `no` is measured.
