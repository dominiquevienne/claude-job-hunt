# Board measurement — PNG JobSeek (Papua New Guinea): reopened by the 2026-09-07 doctrine, the transport is OPEN, and `/jobs` states 31 jobs — 25 on the page, `/jobs/<id>` links

<!-- verified: 2026-09-12 -->

<!-- hosts: www.pngjobseek.com, pngjobseek.com -->
<!-- script: none -->
<!-- countries: PG -->
<!-- content: measured · rules read twice and certain (3 695 B, Cloudflare's managed block naming `ClaudeBot`, `*` open bar the operator's paths; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200 at the root (263 145 B, «31 Jobs are waiting for you») and at `/jobs` (415 307 B, «31 jobs found — Showing 1 – 25 of 31», 25 `/jobs/<id>` links, no pager link in the HTML) · 2026-09-12 15:29 UTC -->
<!-- witness: the page's own «31 jobs found» on `/jobs` and «31 Jobs are waiting for you» on the root — two pages, one number, three seconds apart; the 25 links on page 1 are the first page of it; no adapter yet -->

**Measured 2026-09-12 at 15:28:03Z UTC for #233, lot 7 — a measurement of
the transport, not a decision about the host.** Every fetch under the
declared identity, the guard on the exact path first, `bin/fetch-body.py`.

## The rules — reopened by the doctrine of 2026-09-07, and 31 jobs behind them

```
robots.txt      read twice, certain: True, 3695 B, md5 a8efc8bf9a7a both times — the managed block (`ClaudeBot` named and refused, `*` open) plus the operator's lines
identity("/")   http, claude-user
verdict()       sweep True, sweep_token claude-user
allowed()       True on `/`, `/jobs`, `/jobs/<id>`
crawl_delay     none
```

## The transport — 200

```
GET https://www.pngjobseek.com/        200, 263 145 B, md5 f8cc3359bd0b   (15:28:03Z)  «Find Jobs in Papua New Guinea | PNG JobSeek» — «31 Jobs are waiting for you»
GET https://www.pngjobseek.com/        200, 263 176 B, md5 f1db2311df01   (15:28:05Z — dynamic, sizes differ)
GET https://www.pngjobseek.com/jobs    200, 415 307 B, md5 4f1deeea1e9e   (15:29:01Z)  «Job Search | PNG JobSeek» — «31 jobs found», «Showing 1 – 25 of 31», 25 `/jobs/<id>` links
GET https://www.pngjobseek.com/jobs    200, 415 307 B, md5 22f06570da7c   (15:29:04Z — same size, a per-response token)
```

## What the listing says

| question | answer |
| :-- | --: |
| jobs stated | **31** — «31 jobs found» on `/jobs`, «31 Jobs are waiting for you» on the root |
| on page 1 | 25 `/jobs/<id>` links (`/jobs/18254` …), «Showing 1 – 25 of 31» |
| page 2 | announced by the count, no `?page=2` link in the served HTML — the pager is a script or a query the adapter will find |
| companies | 12 `/companies/<id>` links on the root |
| JSON-LD | none on the root or the listing |

**A small board, and a served one.** *Thirty-one is the whole of it on
2026-09-12; the ids are the key, and a job page's markup is the adapter's
first question.*

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE.
  **Candidate adapter**: 31 advertisements, ids in the URL, the stated count
  as the witness. *Papua New Guinea is at zero adapters.*
- **Not a verdict that the host is closed** — nothing refuses us.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
