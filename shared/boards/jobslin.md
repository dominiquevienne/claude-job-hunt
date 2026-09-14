# Board adapter — Jobslin (`ph.jobslin.com`, Philippines — and 20 sibling sub-hosts by `--host`): the hub is a country chooser, the Philippine board is served by HTTP — «16,072 Job Vacancies» stated, 12 a page at the host's 2 s, the card's place and date read from its own icons

<!-- verified: 2026-09-14 -->

<!-- hosts: ph.jobslin.com, www.jobslin.com, jobslin.com -->
<!-- script: jobslin.py -->
<!-- host-forms: ph.jobslin.com -->
<!-- host-forms-basis: read — `jobslin.py` builds `<cc>.jobslin.com` from `--host` (ph by default); every link the listing writes is root-relative on the sub-host, and only `ph` was exercised on the day · 2026-09-14 -->
<!-- countries: PH -->
<!-- content: measured · **«1 - 12 of 16,072 Job Vacancies» stated by `ph.jobslin.com/job-offers`, 36 emitted over 3 of 1 340 pages of 12 — bounded by request, at the `Crawl-delay: 2` the host writes** — read by the declared client through plain GETs, 00:10 UTC; page 2 «13 - 24 of 16,072», page 3 «25 - 36», every heading checked; 13 of the 36 are the operator's «Premium» placements, kept and flagged; 28 of the 36 print a monthly salary in ₱, one weekly, 7 none; the hub `www.jobslin.com` is a country chooser with 0 advertisements (21 sub-hosts — `my`, `sg`, `au`, `ke`, `gh` … — the same template by the operator's word, each to be measured before its card claims it); the rules — the Cloudflare managed block naming `ClaudeBot`, `*` open with a Content-Signal, reopened by the doctrine of 2026-09-07; **the ad is a JobPosting, no contact on either page on the day, the description scrubbed of e-mails all the same** · 2026-09-14 -->
<!-- witness: the listing's own «a - b of N Job Vacancies», read on every page of every walk and printed beside the emitted count; a page whose heading does not start where asked is a fault, not a page; a bounded walk says so and is never «short» · 2026-09-14 -->

**Measured 2026-09-13 for #233, lot 8 — a measurement of the transport, not a
decision about the host.** Every fetch under the declared identity, the
guard on the exact path first, `bin/fetch-body.py`.

## The rules — reopened by the doctrine of 2026-09-07, and 10 posts behind them

```
robots.txt      read twice, certain: True, 1836 B, md5 c6370d4bc025 both times — Cloudflare's managed block, `ClaudeBot` named and refused, `*` open
identity("/")   http, claude-user
verdict()       sweep True, sweep_token claude-user
allowed()       True on `/`, `/jobs`; on `ph.jobslin.com`: True on `/`, with `Crawl-delay: 2`
crawl_delay     none on the hub; 2 s on `ph.jobslin.com` (honoured)
```

## The transport

```
GET https://www.jobslin.com/       200 → https://jobslin.com/, 13 468 B   (10:22:23Z, byte-identical at 10:22:25Z)  «New Opportunities, Every Day | Jobslin» — the country chooser
GET https://www.jobslin.com/jobs   404, 6 615 B                       (10:23:32Z, twice)  the site's own 404 — a guessed path
GET https://ph.jobslin.com/        200, 179 496 B                     (10:25:02Z; 179 502 B at 10:25:05Z)  «Jobslin: Job Opportunities in Philippines» — 10 `/job/` links, no stated total
```

## What the pages say

| question | answer |
| :-- | --: |
| what `jobslin.com` is | **a hub** — «Choose Your Country»: `ph.`, `my.`, `sg.` and 18 more sub-hosts; 0 advertisements on it |
| the Philippine board | `ph.jobslin.com` — served, 10 posts on the front page («Full Time · Cavite · 05/08/2026»), no count stated, not paged on the front page |
| the object of #233 | the hub host, which is not a board — the board is a sub-host, one per country |

*The class `labour-gov-bb` opened: a served host whose object is elsewhere. Here the elsewhere is 21 sub-hosts of the same operator.*

## What this card is, and is not

- **A measurement, not an adapter** — and the hub is **not a board**: 0 advertisements by object. **Candidate: `ph.jobslin.com`** (and its siblings `my.`, `sg.` …), a served front page with `/job/` links; its listing and count are the adapter's first question. *Only `ph.` was read, once.*
- **Not a verdict that the host is closed** — nothing in the rules refuses `Claude-User`.
- **No configuration.** A user with a URL from this host can hand it to `cover-letter`.

## 2026-09-13 16:58 UTC — the Philippine board by HTTP: served, counted, paged (#222, for #299)

```
GET https://ph.jobslin.com/robots.txt          200 — the Cloudflare managed block: `*` Allow: / with Content-Signal search=yes, ai-train=no, use=reference; ClaudeBot and eight others Disallow: /; Crawl-delay 2 (honoured)
GET https://ph.jobslin.com/job-offers           200, 324 503 B — «1 - 12 of 16,072 Job Vacancies» · 12 /job/<id>/<slug> links · JSON-LD Organization + WebPage + ItemList · pager ?t=16072&page=2…6, rel="next"
GET https://ph.jobslin.com/job-offers?page=2    200, 318 479 B — «13 - 24 of 16,072 Job Vacancies» · 12 links, none shared with page 1
GET https://ph.jobslin.com/sitemap.xml          200 — an HTML page, not a sitemap (34 970 B); no Sitemap: line in the rules
```

**This is an HTTP route** — the declared client is served, the page
states its count, the pager is a query string. The adapter is #299's
(the owner's rule of 2026-09-13: an adapter has its issue before its
first line); what it would print is «n emitted, site states 16 072» over
`?page=N` at 2 s, and the same shape on `my.`, `sg.` and the other
sub-hosts if they are the same template — not read here. The `t=16072`
in the pager is the count carried along, not a token.

## 2026-09-14 — shipped (#299)

`jobslin.py search [--host ph] [--pages N] [--limit N]` and `ad --url`. The
listing is one GET a page (`/job-offers`, then `?page=N`), the heading
«a - b of N Job Vacancies» read on every page and checked to start where
the page was asked; the card's title, employer and summary are read by
their classes, **the place and the date by the spans the card's own
icons label (`bi-geo-alt`, `bi-calendar`) — the first draft guessed the
place from the first line with a comma and took a summary for it**; the
salary as the card prints it («₱17,000.00 / Monthly» → 17 000 PHP a
month, `salary_unit_stated` true only when a period is printed; the sign
mapped to a code, `RM` → MYR for the Malaysian host); «Premium» — the
operator's paid placement — kept and flagged. `_pace` applies the host's
`Crawl-delay: 2`. **`--pages` defaults to 10** (120 rows); 1 340 pages is
a choice.

```
jobslin.py search --pages 3
[jobslin] 36 emitted of the 16 072 ph.jobslin.com states — 3 page(s) of 12 walked by request (--pages/--limit) at the host's 2 s, not a shortfall.
```

`ad` reads the JobPosting the posting page carries (title, employer,
locality and region, `datePosted`, `validThrough`, `employmentType`,
`totalJobOpenings`, the description scrubbed of e-mail addresses); no
contact was on either page on the day, and the «Apply» is the site's own
form, never touched.

**The 20 sibling sub-hosts are `--host <cc>` and nothing more until each
is read**: the operator says «same template», this card says `ph` — a
sibling's card names its own count, its own rules and its own currency
sign on the day it is measured.

### Configuration

```yaml
boards:
  jobslin:
    enabled: true
    host: ph               # the operator's country code — ph by default; my, sg, au, ke, gh … once measured
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `host` | no | `ph` by default |

No credentials, no browser, no login. `search` is one request a page at
2 s; `ad` is one.

### What is not established

- **The siblings** — `my.`, `sg.` and the others: not read; the adapter
  takes them and every claim waits for its measurement.
- **The count against a full walk** — 16 072 stated, 1 340 pages of 12
  at 2 s (45 minutes) not walked on the day.
- **The tags beyond the six seen** — Full Time, Remote, Part Time, No
  Experience …; unknown badges are dropped from `tags`, never invented.

Three tests; six mutations on a detached worktree (`python3 -B`), six red
— the place read from the first comma line, the heading check dropped,
the period stated without a printed one, the sign not mapped, `--host`
ignored, the premium flag dropped.

