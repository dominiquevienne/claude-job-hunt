# Board adapter — GulfTalent (`www.gulftalent.com`, UAE and the Gulf): a listing that states its count twice, two address shapes on one page, and a pager that closes under the reader

<!-- verified: 2026-09-13 -->

<!-- hosts: www.gulftalent.com, gulftalent.com -->
<!-- script: gulftalent.py -->
<!-- host-forms: www.gulftalent.com -->
<!-- host-forms-basis: read — `gulftalent.py:BASE`, a single literal; every address the site writes carries `www.` (listing rows, ItemList, JobPosting `url`) · 2026-09-13 -->
<!-- countries: AE SA QA KW BH OM -->
<!-- content: measured · **15 681 emitted over 628 pages of 25 and the site states «15,681 Jobs found» — equal**, the pager closing under the reader at 628 (page 629 carried no new row) — `gulftalent.py list` for the UAE edition, 15:01–15:22 UTC; the panel's cached `job_count` said 15 680, one apart, printed beside it and not corrected; the morning's tab had the pager at 627 × 25 · 2026-09-13 -->
<!-- witness: the pager closing under the reader — «page M+1 answered 404, pager closes at M» printed at the end of every full walk — beside the page's two own figures, the visible «N Jobs found» and the panel's `job_count`, which differed by one on the day (15 681 / 15 680 at 14:57 UTC) and are both printed, neither corrected · 2026-09-13 -->

**The Gulf's board, one country edition at a time — `/uae/jobs` and five
siblings — read by the declared client, which the rules place under `*
Allow: /` and which the host serves on every path read.** The #222 list
had it as a 403 candidate from the UAE page; measured 2026-09-13 12:35 UTC
(a tab) and 13:27–15:0x UTC (the client), it is not one. Shipped the same
day, replacing the morning's measured card (`route: browser · 15675`),
which counted the pager from a tab — 627 × 25.

## Rules, and the operator's own taxonomy

```
robots.txt   200, 1 448 B — «Blocked — AI training crawlers»: ClaudeBot, anthropic-ai, GPTBot, CCBot … Disallow: /
                             «Allowed — AI search and retrieval»: ChatGPT-User, OAI-SearchBot, PerplexityBot, Bingbot, Applebot — Allow: /
                             «All others»: * Allow: /     ·  Crawl-delay 30 for five SEO crawlers by name, none for *  ·  Sitemap: /sitemap.xml
identity("/uae/jobs")   http, claude-user — under `*`, certain: True  (the 2026-09-07 decision; #230)
```

**`Claude-User` is named in neither group** and falls under `*`. The file's
own headings say what the 07.09 decision says: the operator refuses the
training crawler and allows the agent that retrieves for a person. No
delay binds `*`; the adapter spaces 2 s.

## Transport — served on every path, and the refusal the UAE page expected was not met

```
GET /                              200, 144 682 B, nginx/1.25.5 — twice at 13:27 UTC, md5 moving (a per-request element), size identical
GET /uae/jobs                      200, 172 804 B — 25 rows, ItemList (25), BreadcrumbList, FAQPage; panel-data job_count 15680; pager /uae/jobs/2 … /5 (a sliding window, no «last»)
GET /uae/jobs/2                    200, 164 177 B — 25 rows, NO ItemList; «15,681 Jobs found»; panel-data job_count 15680
GET /uae/jobs/9999                 404, 0 B — past the end the site answers 404
GET /uae/jobs/<slug>-632616        200, 135 656 B — JobPosting + BreadcrumbList; the labelled fields; description under #text-container
GET /uae/jobs/<slug>_632494        200, 133 258 B — BreadcrumbList ONLY, no JobPosting; the same labelled fields
```

## The walk — rows, not the ItemList; two shapes; the pager closing

Each listing page carries 25 `<a class="… job-results-item" data-ga-label="<id>"
href="/uae/jobs/<slug>[-_]<id>">` with the title, `company-name`, `location`
and a dated `date` div («11 Sep 2026»). **The JSON-LD `ItemList` is on page
1 only** — 25 entries there, none on page 2 — so the rows are the route.

**Two address shapes on one page**: `…-632616` and `…_632494`, hyphen or
underscore before the id — **4 rows of 25 on the page read carried the
underscore**. The first pattern, written for the hyphen from the JobPosting
`url`, matched 21 of 25 and printed «22 emitted» over two pages with no
symptom; the id is now read from `data-ga-label` and the address as written.
**And a bounded walk cannot see that shortfall** — «21 of 25» is invisible
to «N emitted of the X the site states — walked by request» — so every page
is checked against its own anchors: fewer rows read than `job-results-item`
on the page is a reader fault and exits 6, never a count.

```
15 681 emitted over 628 page(s), site states 15 681 («Jobs found», uae) — equal; page 629 carried no new row, pager closes at 628; panel `job_count` 15 680 — 1 apart, neither corrected.
  15681 distinct ids, 45 with the underscore shape; `gulftalent.py list` 15:01–15:22 UTC, 629 requests 2 s apart
```

**The witness is the pager closing under the reader**, not a figure copied
from the page: the walk continues until a page answers 404 or carries no
new row, and prints where it closed. **Both ends were met on the day**:
`/uae/jobs/9999` answers 404, and page 629 — one past the last full page —
answered 200 with rows already seen; the walk stops on either. The page's two figures are printed
beside it: the visible «N Jobs found» and the panel's `job_count`. **They
differed by one on the day** — page 2 read six minutes after page 1
(«15,681» vs 15680), one advertisement posted in between (id 632 622 first
seen at 14:56 UTC, absent from the 14:51 read), and the panel's
`this_page` is the edition's first page: a cached figure. Neither is
corrected into the other.

## The advertisement — page fields on both shapes, JSON-LD on one

```
<h2> Black Pearl </h2></a> <p>Dubai, UAE</p> <p>Posted on: 12 Sep 2026</p>      <- header: employer, place, date
<span style="color: #6c757d">Job Type: </span><span> Full Time</span>              <- then Job Location · Nationality · Salary «1000 - 2000 AED» · Gender · Arabic Fluency · Job Function · Company Industry
<div id="text-container" class="job-description"><span class="truncate-text"><p>…</p></span></div>
JobPosting (hyphen shape only): datePosted 2026-09-13T00:00:00+00:00 · validThrough 2026-12-11 · baseSalary {AED, 15000–20000, unitText MONTH} · directApply true · identifier.value 632616 (= the URL id)
```

`ad` reads the page first and the JobPosting as a supplement, and says
which it had (`jsonld: true/false`). The labelled salary states a currency
and a range and **no period** — `salary_unit_stated` is false unless the
JobPosting gave `MONTH`; the description's own «per month inclusive of
fixed allowances» is left in the description. `posted` (ISO) comes from
the JobPosting only; `posted_label` is the page's «12 Sep 2026» on both.
Read in full on two: `632616` (hyphen, JobPosting) and `632494`
(underscore, none).

## Configuration

```yaml
boards:
  gulftalent:
    enabled: true
    country: uae        # or saudi-arabia · qatar · kuwait · bahrain · oman
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `country` | no | one edition per run; `uae` by default |

No credentials, no browser. A full UAE walk is ~630 requests at 2 s
(~21 min); `--pages N` bounds it and the note says so; `ad` is one.

## What is not established

- **The five other editions** — `/saudi-arabia/jobs` … `/oman/jobs` are
  the same template by the site's navigation and were not walked;
  `countries:` lists them on that basis.
- **Whether the underscore shape is a different kind of listing** — it
  carries no JobPosting where the hyphen shape does; both carry the same
  page fields, both open, and nothing on the page says why.
- **`/sitemap.xml`** — declared, not read; the listing is the route.
- **Whether `job_count` ever catches up with «Jobs found»** — two pairs
  read (14:57 and 15:01 UTC), one apart both times.
- **How far back the listing runs** — the 15 681 rows carry `posted_label`
  from 2025 to 13 Sep 2026 (year and month only from the label's shape);
  whether the oldest are still open was not read.
- **What page 629 serves** — 200 with rows already seen, where page 9999
  answers 404; the walk stops on either and nothing distinguishes «the last
  page repeated» from «a page of stragglers» without a second read.

## 2026-09-13 — shipped

`gulftalent.py list --pages 2`: 22 emitted with the hyphen-only pattern,
then 50 with both shapes. Full walk 15:01–15:22 UTC: **15 681 emitted over
628 pages, site states 15 681 — equal**; 45 of them under the underscore
shape. `ad` on both shapes. Four
tests; six mutations on a detached worktree (`python3 -B`), six red, each
on the test written for it — the underscore dropped from the pattern, the
dedup dropped, the 404 branch dropped, the «Jobs found» regex broken, the
JSON-LD supplement dropped, the `--pages` bound ignored.
