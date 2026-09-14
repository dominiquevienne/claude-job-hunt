# Board adapter — Manpower Norway (`www.manpower.no`): the staffing network's front on ManpowerGroup's platform, read through its sitemap — 96 `/nb/jobb/` rows on 2026-09-14, the inventory where the search states no count a client reads — and each job page's JobPosting, list and body; the agency as employer on every ad; the text scrubbed

<!-- verified: 2026-09-14 -->

<!-- hosts: www.manpower.no -->
<!-- script: manpowerno.py -->
<!-- host-forms: www.manpower.no -->
<!-- host-forms-basis: read — every sitemap row and every page link is on `www.manpower.no`; `manpowerno.py` names the host as a literal and refuses an ad address on any other · 2026-09-14 -->
<!-- countries: NO -->
<!-- content: measured · **`/sitemap.xml` (200, 235 496 B, 588 rows) names 96 `/nb/jobb/<id>/<slug>` jobs with a per-row lastmod (94 distinct), their 96 `/en/job/` twins, 62 `/sok/…` facet pages and the site's pages; the search `/nb/sok` (200, 116 023 B) renders no card and no count on the server — a React app; a facet page (`/sok/ledig-stilling-bergen`, 200, 182 242 B) renders 7 cards** — read by the declared client, the guard on the exact path (the rules, 2 406 B: thirty named crawlers, `*` → `Allow: /`, `Disallow: /candidate`); the job page (200, 123 092 B) carries a JSON-LD graph with a JobPosting — reference, title, a one-line teaser, `datePosted` `20260910T125613`, `validThrough`, `employmentType`, `workHours`, industry ids, `addressLocality` «Vestland» and `addressRegion` «Bergen» (the county and the town in each other's field — emitted as written), an empty `baseSalary` — the labelled list («Referansenummer», «Publisert: 10 september, 2026», «Ansettelsesform», «Bransje» as names, «Søknadsfrist», «Antall stillinger», «Heltid/deltid») and the body; 3 read live; **no contact on the pages read; the body is scrubbed all the same; the agency is the employer, the client never named** · 2026-09-14 -->
<!-- witness: none the site states — the search's count is client-side; the sitemap's job rows are printed as the inventory on every run, never as the site's statement; `list` counts the jobs gone since the sitemap; a page without a JobPosting or a body exits 6 · 2026-09-14 -->

**Manpower is Norway's largest staffing agency by its own account; its
front lists 96 postings on the day — a small board beside NAV's
Arbeidsplassen (`arbeidsplassen.md`) and Jobbnorge (`jobbnorge.md`),
and the agency's own inventory, the client employer never named.**
Issue #368. Measured 2026-09-14 03:2x UTC by the declared client, the
guard on the exact path before each request.

## Rules and the routes

```
www.manpower.no/robots.txt              200, 2 406 B — Slurp, teoma, Google, msnbot … thirty named groups; User-agent: * + facebookexternalhit: Allow: /, Disallow: /candidate; Sitemap: /sitemap.xml
GET https://www.manpower.no/sitemap.xml            200, 235 496 B — 588 rows: 96 /nb/jobb/<id>/<slug> (lastmod), 96 /en/job/<id>/<slug>, 62 /sok/… facets, 163 blog posts, the pages
GET https://www.manpower.no/nb/sok                 200, 116 023 B — the search: a React app, no card and no count rendered
GET https://www.manpower.no/sok/ledig-stilling-bergen   200, 182 242 B — an SEO facet: 7 server-rendered cards (title, Manpower, place, type, industry, date)
GET https://www.manpower.no/nb/jobb/53700/radgiveroffentligeanskaffelser   200, 123 092 B — <script data-react-helmet type="application/ld+json"> graph: BreadcrumbList + JobPosting; job-details-list; details-rich-text
```

**The search states no count a client reads** — its results and its
total are fetched by the app after the page loads — so the sitemap's
`/nb/jobb/` rows are the inventory, printed as such and never as the
site's statement; the English twins (`/en/job/`, the same ids) and the
facet pages are set aside and counted. No Crawl-delay; 2 s is the
adapter's own.

## The three commands

```
manpowerno.py sitemap
[manpowerno] 96 job row(s) in the sitemap (492 other rows set aside — pages, facets, the English twins) — the site's search renders no count a client reads: the sitemap is the inventory, not the site's statement.
manpowerno.py list --limit 3
[manpowerno] 3 job(s) read from their pages, 0 gone since the sitemap, of the 96 the sitemap names — 3 read by request (--limit), not a shortfall; the site states no count a client reads.
manpowerno.py ad --url https://www.manpower.no/nb/jobb/53700/radgiveroffentligeanskaffelser
{"id": "53700", "reference": "53700", "title": "Rådgiver, offentlige anskaffelser", "teaser": "Erfaring fra offentlige anskaffelser?", "company": "Manpower", "employer_is_the_agency": true,
 "locality_as_written": "Vestland", "region_as_written": "Bergen", "postal_code": "5014", "place_text": "Bergen", "employment_type": "Vikariat/ engasjement", "work_hours": "Heltid", "sector": "Offentlig administrasjon , Økonomi og regnskap", "positions": 1,
 "posted": "2026-09-10", "posted_on_page": "2026-09-10", "valid_through": "2026-09-17", "deadline_on_page": "2026-09-16", "salary_min": null, "salary_unit_stated": false, "description": "…", "contacts_withheld": true}
```

The JobPosting's dates are the site's compact form (`20260910T125613`,
`20260917T215959Z`) — read to ISO — and the page's own «Publisert» and
«Søknadsfrist» («10 september, 2026», a Norwegian month) are emitted
beside them: **the two deadlines differed by a day on the ad read
(validThrough 17 September, Søknadsfrist 16 September) — both kept, as
printed.** The county sits in `addressLocality` and the town in
`addressRegion` on the page read — emitted under names that say so
(`locality_as_written`, `region_as_written`), and the town read again
from the body's «Arbeidssted: Bergen» as `place_text` when printed. The
sector is the labelled list's names (the JSON-LD carries ids). **The
agency is the employer on every ad (`employer_is_the_agency`), the
client described and never named; the body is scrubbed of e-mail
addresses and Norwegian telephone numbers; `contacts_withheld` on every
record; «SØK PÅ STILLINGEN» is a form, never touched.**

## Configuration

```yaml
boards:
  manpower-no:
    enabled: true
    limit: 50             # list: jobs read from their pages, 2 s apart
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `limit` | no | 20 by default; the sitemap named 96 on the day |

No credentials, no browser, no login. `sitemap` is one request; `list`
is one plus one a job.

## What is not established

- **The site's own count** — client-side; not read. A browser on
  `/nb/sok` would print it.
- **Whether every `/nb/jobb/` row is live** — the sitemap's lastmod is
  recent on the day (94 distinct in 96); `list` counts a 404 as gone.
- **The salary** — empty on every ad read; the field is emitted null.
- **The other ManpowerGroup fronts** (`manpower.fi`, `manpower.se` …) —
  likely the same Sitecore template; not measured.

## 2026-09-14 — shipped

`sitemap`: 96 rows; `list --limit 3`: three jobs read from their pages,
sectors, dates and places resolved, no address or number in the output;
`ad`: one. Three tests; six mutations on a detached worktree (`python3
-B`), six red — the English twin counted as a job, a repeated id counted
twice, the compact date not read, the Norwegian month not read, the
scrub dropped, a gone job counted as read.
