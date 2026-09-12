# Board adapter — Green (`www.green-japan.com`, Japan): the IT/Web board, one job sitemap, a count the search page states, a JobPosting per advertisement

<!-- verified: 2026-09-12 -->

<!-- hosts: www.green-japan.com -->
<!-- script: greenjapan.py -->
<!-- host-forms: www.green-japan.com -->
<!-- host-forms-basis: read — `greenjapan.py:BASE`, a single literal; addresses come from the sitemap as served · 2026-09-12 -->
<!-- countries: JP -->
<!-- content: measured · 28 284 distinct advertisement ids in `sitemap/jobs.xml` (28 284 `<loc>`, all `/company/<company>/job/<id>`, 3 958 companies, no `<lastmod>`), and **`/search` states 求人を28284件掲載 — equal**; `greenjapan.py sitemap` at 09:36 UTC · 2026-09-12 -->
<!-- witness: the site's own count on a second page — `/search`, meta description «求人を28284件掲載», read in the same run and printed beside the sitemap's count («28 284 emitted, site states 28 284 — equal»; «k short» whenever they part) · 2026-09-12 -->

**Japan's IT/Web board — 28 284 advertisements on the day, all Japanese,
nothing translated, and the third Japanese host with a script here** (after
Mynavi and type). Measured 2026-09-12 09:33–09:40 UTC, every fetch under the
declared identity, the guard on the exact path first.

## Rules, transport, sitemap

```
robots.txt                 read, certain: True — 10 Disallow to `*` (/mypage0*, /messages/, /profiles/, /job_applies/ …); none the sitemap, /search or /company/; no Crawl-delay
identity("/")              http, claude-user
GET /                      200, 249 350 B, <title>IT/Web業界の転職サイトGreen</title> — states no count
GET /sitemap.xml           200, 1 863 B, index of 5 children — jobs, statics, companies, questionnaires, prs
GET /sitemap/jobs.xml      200, 3 850 346 B, 28 284 <loc>, 0 <lastmod>
GET /search                200 — <meta name="Description" content="求人を28284件掲載。…">
```

Behind CloudFront (`x-cache: Miss from cloudfront`, POP ZRH52), 200 to the
declared identity on every path read. **No `<lastmod>` anywhere in the job
file** — nothing to filter on, so the adapter offers no `--since`.

## The count, and its second branch

```
28284 <loc> in sitemap/jobs.xml; 28284 matched the advertisement shape and 0 did not; **28284 distinct advertisement id(s)** across 3958 companies.
28 284 emitted, site states 28 284 on https://www.green-japan.com/search — equal.
```

*The sitemap and the search index are two views of one store, and on
2026-09-12 they agreed to the unit.* The file is live: a first read of the
night (2026-09-12 00:5x UTC) held 28 296 `<loc>`; 09:34 UTC held 28 284.
When the two branches part, the adapter prints «k short» (or «more in the
sitemap than the site states») — never a bare count.

## The advertisement — a JobPosting in JSON-LD, two values as published

```
GET /company/2/job/301424    200, 178 164 B, exactly one JobPosting
title · hiringOrganization · identifier (value = the job id) · datePosted 2025-11-07 · validThrough 2027-09-12
employmentType FULL_TIME · experienceRequirements · jobBenefits · workHours 9:30～18:30
jobLocation.address.addressLocality = postcode + street (141-0032 東京都品川区…) · addressCountry 日本
baseSalary currency "YEN", value {minValue 7 000 000, maxValue 9 000 000, unitText YEAR}
```

**Two values are emitted exactly as the site publishes them, and the adapter
says so on stderr each time:**

- **`validThrough` is the read date plus one year** — 2027-09-12 on a
  2026-09-12 read, on an advertisement posted 2025-11-07. *A rolling value,
  not a deadline.* Emitted as published; not corrected, not dropped.
- **`baseSalary.currency` is `YEN`**, not the ISO code `JPY`. Emitted as
  published, alongside the human-readable `salaryCurrency: 円`.

Everything else as published: title, employer, address, dates, salary
min/max/unit, requirements, hours, benefits, description (`\r\n` kept as
newlines), `language: ja`. **Read in full on one advertisement.**

## Configuration

```yaml
boards:
  green-japan:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials, no browser. `sitemap` is three requests (index, job file,
search page); `--no-site-total` makes it two.

## What is not established

- **Which advertisements are open** — `validThrough` cannot say (see above);
  a page that has gone returns 404 → exit 3, one request each.
- **The search facets** (`/search?…`) — the page states its count in a meta
  tag; no filter was exercised.
- **What `company/<id>` covers** — 3 958 distinct in the sitemap; the
  `companies.xml` child was not read.

## 2026-09-12 — shipped

`greenjapan.py sitemap`: 28 284 distinct, site states 28 284 — equal.
`ad` on 301424: the fields above, `validThrough` and `YEN` flagged.
