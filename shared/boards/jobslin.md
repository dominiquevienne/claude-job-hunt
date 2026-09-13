# Board measurement — Jobslin (`ph.jobslin.com`, Philippines and 20 other countries): the hub is a country chooser, the Philippine board is served by HTTP — «16,072 Job Vacancies», 12 a page, an ItemList on every page

<!-- verified: 2026-09-13 -->

<!-- hosts: www.jobslin.com, jobslin.com -->
<!-- script: none -->
<!-- countries: PH -->
<!-- content: measured · **`ph.jobslin.com/job-offers` states «1 - 12 of 16,072 Job Vacancies» and is served to the declared client** (200, 324 503 B; page 2 «13 - 24 of 16,072», 12 new `/job/<id>/<slug>` links, none shared with page 1; the pager is `?t=16072&page=N`, `rel="next"`); a JSON-LD ItemList per page; `Crawl-delay: 2` on the sub-host, honoured; the hub `www.jobslin.com` is a country chooser with 0 advertisements (21 sub-hosts); `bin/fetch-body.py` 16:58–16:59 UTC; the rules as on the 13th — the managed block naming `ClaudeBot`, `*` open with `Content-Signal: search=yes,ai-train=no,use=reference`, reopened by the doctrine of 2026-09-07, and 10 posts on the front page behind them · 2026-09-13 -->
<!-- witness: the page's own «of 16,072 Job Vacancies», printed on every listing page; a walk was not made (1 340 pages of 12 at 2 s) — the count is the site's, read on two pages, and the adapter that ships prints it beside its own · 2026-09-13 -->

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
