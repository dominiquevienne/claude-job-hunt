# Board adapter — Landing.Jobs (`landing.jobs`, Portugal): a refused search route, a sitemap that holds exactly what the listing states, and a JobPosting on every page

<!-- verified: 2026-09-12 -->

<!-- hosts: landing.jobs -->
<!-- script: landingjobs.py -->
<!-- host-forms: landing.jobs -->
<!-- host-forms-basis: read — `landingjobs.py:BASE`, a single literal; the sitemap serves its addresses on the apex · 2026-09-12 -->
<!-- countries: PT -->
<!-- content: measured · 55 distinct advertisement addresses in `sitemap.xml` (55 `/at/<company>/<slug>` among 2 168 `<loc>`, beside 13 employer pages, 1 505 facet pages, 567 blog posts), **and the open listing `/jobs` states «55 results» — equal**; `landingjobs.py sitemap` at 11:26 UTC · 2026-09-12 -->
<!-- witness: the listing's own count on a second page — `/jobs`, `js-jobAds-count` «55 results», read in the same run and printed beside the sitemap's count («55 emitted, site states 55 — equal»; «k short» when they part) · 2026-09-12 -->

**The Lisbon-based European tech board — 55 advertisements on the day,
from 13 employers, Lisbon and Porto first, Munich and Cologne among the
city facets — and Portugal's third adapter** (after `net-empregos` and
`expressoemprego`). Measured 2026-09-12 11:22–11:27 UTC, every fetch under
the declared identity, the guard on the exact path first. *The Portugal
page (2026-09-11) had it right: `/api/` and `/jobs/search` are refused by
the rules, the sitemap is open — and the sitemap is the whole inventory.*

## Rules, transport, and the routes not taken

```
robots.txt        200, 251 B — `User-agent: *` · Disallow /job_closed.html · /backoffice/ · /employers/request_info · /employers/request_source_access · /employers/search · /api/ · /jobs/search; certain: True; no Crawl-delay
identity("/")     http, claude-user
GET /sitemap.xml  200 — 2 168 <loc>: 55 /at/<company>/<slug> · 13 /at/<company> · 914 /jobs/in/<city> · 571 /jobs/for/<role> · 567 /blog/ · chrome; <lastmod> on all, 2026-09-01 on every /at/ entry — not the advertisement's date (one was created 2026-09-07)
GET /jobs         200, 269 068 B — «55 results» (js-jobAds-count), 50 static cards server-rendered (lj-jobcard-static), the rest loaded through /jobs/search
GET /jobs?page=2  200 — the same 50 cards: paging lives behind the refused route
GET /at/<company>/<slug>   200, ~105–112 kB — one JobPosting in JSON-LD + a React props record (jobPage/JobPage-0)
```

**Two paths the site's own pages use are refused — `/jobs/search` for the
listing past its 50 static cards, `/api/` — and nothing here reads them, by
any route.** *`kariera-mk`-style browser reasoning does not apply: the
refusal is written in the rules, not rendered at the transport.* The
inventory comes from the sitemap, the count from the open listing, and on
2026-09-12 the two agreed to the unit: **55 and 55**.

`/job_closed.html` is refused too — named like the page a closed
advertisement lands on. *Not observed: every advertisement read was live.*
The adapter follows no redirect: a 3xx whose `Location` is that path is
«gone» (exit 3), any other 3xx is indeterminate (exit 6), and the refused
page is never requested either way.

## The sitemap — told apart by shape, not by count

```
2 168 <loc> in sitemap.xml: **55 distinct advertisement(s)** (/at/<company>/<slug>), 13 employer page(s) (/at/<company>), 2 100 other (facets, blog, chrome). The <lastmod> is 2026-09-01 on every /at/ entry — not the advertisement's date; nothing to filter on.
55 emitted, site states 55 on https://landing.jobs/jobs — equal.
```

*A `grep -c '/jobs/'` on this file returns 1 506 and none of them is an
advertisement* — the `/jobs/in/<city>` and `/jobs/for/<role>` entries are
facet pages, and the advertisements live under `/at/`. The id is the
`<company>/<slug>` path (`annea/full-stack-generalist-software-engineer-f-m-x`);
the site's numeric id (`19763`) is in the page's props and is emitted by
`ad` beside it. Advertisements per employer on the day: damia-group-portugal 10 ·
accenture-pt 9 · volkswagen-group-digital-solutions-portugal 9 ·
we-are-meta 8 · inscale 5 · indicium-ai 3 · kyndryl, wellhub, dashlane-pt,
ki-performance 2 each · annea, oralpro-llc, wyden 1 each — 13 employers, 55.

**The 50 static cards on `/jobs` are a strict subset of the sitemap's 55**
(50 shared, 0 listing-only, 5 sitemap-only — all five 200 with a
JobPosting when opened). So the listing's count is a second source and the
sitemap is the inventory; when they part, the adapter says «k short» and
names the refused route the rest sits behind.

## The advertisement — a JobPosting and the page's own record

```
GET /at/annea/full-stack-generalist-software-engineer-f-m-x    200, 112 125 B
JSON-LD  title · description (HTML) · datePosted 2026-09-08 · validThrough 2026-12-07 · employmentType FULL_TIME · directApply
         hiringOrganization {name ANNEA, sameAs https://www.annea.ai} · identifier {value = slug}
         jobLocation.address {Lisbon, Lisbon, PT} · experienceRequirements {monthsOfExperience 72} · educationRequirements
props    jobAd.id 19763 · state_name published · closed_at null · remote_working_label Hybrid · job_type Permanent
         office_locations [{Lisbon, Portugal}] · must_have_skills [Python, TypeScript, React, CI/CD, …] · experience_label Senior, min 6 max 10
         preferred_languages_labels [English] · visa_support false · relocation_paid false · salary null · category Full-stack Developer
```

The JobPosting is the body; the props carry what it lacks — the remote
label, the contract, the skills, the site's state. **`salary` was `null` on
all three pages read**, so its filled shape is unknown here and the adapter
emits it raw as `salary_raw`, never parsed into a min/max by guess. Read in
full on three: `annea/…` (Lisbon, hybrid, senior), `damia-group-portugal/
sap-fico-consultant-in-multiple-locations` (three office locations, one
`addressLocality`), `damia-group-portugal/backend-developer-in-lisbon-2025`
(one of the five the listing does not show — 200, JobPosting present). A page without the props block emits
the JSON-LD fields alone and says on stderr why the site's fields are empty.

## Configuration

```yaml
boards:
  landing-jobs:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials, no browser. `sitemap` is two requests (sitemap, listing);
`--no-site-total` makes it one. `ad` is one.

## What is not established

- **The closed-advertisement redirect** — inferred from the refused path's
  name; no closed advertisement was found to observe it.
- **`salary`'s filled shape** — null on 3 of 3.
- **The facets** (`/jobs/in/<city>`, `/jobs/for/<role>`, 1 485 pages) —
  open paths, not read; they may state per-facet counts.
- **What the sitemap's `<lastmod>` measures** — 2026-09-01 on every
  `/at/` entry, `changefreq: monthly`, yet the file held an advertisement
  created 2026-09-07: neither the advertisement's date nor the file's
  regeneration date. Not established.

## 2026-09-12 — shipped

`landingjobs.py sitemap`: 55 distinct, site states 55 — equal. `ad` on
three. Five tests; seven mutations on a detached worktree (`python3 -B`),
seven red, each on the test written for it.
