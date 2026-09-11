# Board adapter — Great Uganda Jobs: a live stream behind a cumulative counter

<!-- verified: 2026-09-11 -->

<!-- hosts: www.greatugandajobs.com -->
<!-- script: greatugandajobs.py -->
<!-- host-forms: www.greatugandajobs.com -->
<!-- host-forms-basis: read — `greatugandajobs.py:BASE`, a single literal; assets come from `cdn.greatugandajobs.com`, never fetched · 2026-09-11 -->
<!-- countries: UG -->
<!-- content: measured · 57 distinct advertisements over 3 listing pages (83 rows read, 26 repeated — 10 Gold cards pinned on every page and a stream that moved between requests), **56 live and 1 expired by the deadline every card carries**; the listing's «Total jobs: 102 836» and the home page's «103 391 Jobs Posted» are cumulative counters, not this figure; `greatugandajobs.py list --pages 3 --live` at 13:32 UTC · 2026-09-11 -->
<!-- witness: none on the quantity counted — the two site counters (102 836 on the listing, 103 391 on the home page, 102 924 on 2026-09-02) count everything ever posted and move by hundreds a week; no page states how many advertisements are open. The live/expired split is the adapter's own reading of each card's deadline against the day, printed beside the count, and it is a second branch, not a second source · 2026-09-11 -->

**Uganda's largest board by volume, and the first Ugandan host on a card.**
Joomla with the JS Jobs component (`com_jsjobs`), server-rendered HTML,
**no key, no cookie, no account, no browser.** Measured 2026-09-11,
13:27–13:40 UTC, every fetch through `bin/fetch-body.py` or the adapter under
the declared identity, the guard taken on the exact path first.

## Rules and transport — open, stable, no delay

```
GET /robots.txt        200, twice, same body — Joomla's default: 12 technical paths refused
                       (/administrator/, /bin/, /cache/, … /jsjobsdata/data/jobseeker/), the listing open,
                       no Crawl-delay, no Sitemap line, no group naming this project
GET /                  200, 202 267 B, md5 04b0929a43fc — twice, same md5
GET /jobs/             200, ~804 kB, 28 cards
```

`_robots.allowed()` under `claude-user`: `/`, `/jobs/`, `/search`,
`/sitemap.xml`, one advertisement — all `True`, `certain: True`.
`identity()` → `http`, `claude-user`.

## The counter counts everything ever posted — «102 924 → 103 391» in nine days

`shared/plausible-and-false.md` recorded «102 924 Jobs Posted — a historical
cumulative total» on 2026-09-02. **On 2026-09-11 the home page says 103 391 and
the listing header says «Total jobs: 102 836»** — two cumulative counters that
do not even agree with each other, and neither says how many advertisements are
open. *The adapter prints the listing's figure as what it is and never beside
its count as a witness.*

## The anchor is the deadline, on every card

```
Deadline of this Job: Thursday, October 8 2026      ← on every card, absolute
Posted: 1 Day Ago                                    ← relative on the card; dd-mm-yyyy on the ad page
```

**Live versus expired is each card's deadline against today**, printed beside
the count: `live 56 · expired 1 · undated 0`. `--live` emits only the live
ones. *This is the adapter's own reading — a second branch of the same page,
not a second source — and the card says so rather than calling it a witness.*

## The listing is a live stream read through a window

```
/jobs/                       28 cards:  8 Gold pinned + 20 regular
/jobs/?start=28              28 cards:  8 Gold pinned + 20 regular, disjoint from page 1's
/jobs/?start=20              27 cards:  9 Gold + 18 regular, 11 of them page 1's   ← N counts the whole page
```

**`start=N` counts the whole page, Gold included** — `STEP = 28`. **And the
stream moves between requests**: `start=20`, fetched a minute after page 1,
carried id 107 444 at its head while page 1 topped at 107 435 — new
advertisements had been posted meanwhile, pushing everything down. So
consecutive pages overlap or skip by however many arrived; the adapter keys
on the id, prints `rows read` beside `distinct` and `repeated across pages`,
and **promises nothing about completeness**. *Page 1 fetched twice a minute
apart was identical — the same 28, the same order — so the movement is the
board's, not a shuffle.*

**Gold cards** (`bg-gold`) are paid placement pinned on every page — 8 to 10
of the 28 — and are emitted once, flagged `gold: true`.

## The advertisement — labelled pairs, no schema

```
GET /jobs/job-detail/job-<slug>-<id>       200, 266 407 B, 0 JobPosting, 1 BreadcrumbList
js_job_data_title / js_job_data_value:      Job Category · Job Type · Deadline of this Job · Duty Station ·
                                            Posted (09-09-2026) · No of Jobs · Start Publishing · Stop Publishing
```

The description is the page's visible text between «JOB DETAILS:» and «Job
application procedure» — *a layout, not a schema*, and `description_source`
says so on every row. The page has no `<h1>`; the title is `<title>` without
its «Job - » prefix. **Read in full on one advertisement (107326) — the layout
is asserted on one page, not on a sample.**

## Configuration

```yaml
boards:
  greatugandajobs:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials. `list --pages N --live` is the sweep: N requests, 2 s apart.

## What is not established

- **How many advertisements are open** — no page states it; the live count
  is the adapter's window, and the stream moves.
- **The end of the stream**: the adapter stops when a page brings nothing new
  or carries no card; how deep the archive goes was not walked.
- **Search and category filters**: `/search` and `/job-categories/...` exist
  and are permitted; none was exercised, so none is documented.
- **The advertisement layout beyond one page.**

## 2026-09-11 — shipped

Measured 13:27–13:40 UTC. Rules twice, root twice (stable), listing three
times (page 1 stable, the stream moving), `start=20` and `start=28` once
each, one advertisement. `list --pages 3 --live`: 56 emitted of 57 distinct,
83 rows read (28+28+27), 26 repeated, 10 Gold pinned, 1 expired.
