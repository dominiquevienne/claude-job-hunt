# Board measurement — The Ugandan Jobline (Uganda): the transport is OPEN, and the listing states 84 248 jobs over 8 425 pages — an archive, by the number

<!-- verified: 2026-09-13 -->

<!-- hosts: theugandanjobline.com, www.theugandanjobline.com -->
<!-- script: none -->
<!-- countries: UG -->
<!-- content: measured · rules read twice and certain (1 743 B, the managed block naming `ClaudeBot`, `*` open; the written crawl-cost motive #233 recorded on 2026-09-11 is not in the file read today; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200 at the root (50 158 B) and at `/jobs-in-uganda` (74 101 B, twice, same size): «Latest jobs in Uganda — 84,248 jobs», paged to `/page/8425` (10 a page); a WordPress site with `Offer` / `Service` JSON-LD for its employer products, none for jobs · 2026-09-13 -->
<!-- witness: the listing's own «84,248 jobs» and its last page link `/page/8425` — 8 425 × 10 = 84 250, within two of the stated; a number that size on a national board is an archive, and the live window is the adapter's first question; no adapter yet -->

**Measured 2026-09-13 for #233, lot 8 — a measurement of the transport, not a
decision about the host.** Every fetch under the declared identity, the
guard on the exact path first, `bin/fetch-body.py`.

## The rules — reopened by the doctrine of 2026-09-07, and 84 248 jobs behind them

```
robots.txt      read twice, certain: True, 1743 B, md5 15b15b9c0a1c both times — the managed block (`ClaudeBot` named and refused, `*` open) plus the operator's lines
identity("/")   http, claude-user
verdict()       sweep True, sweep_token claude-user
allowed()       True on `/`, `/jobs-in-uganda`, `/jobs-in-uganda/page/2`
crawl_delay     none
```

## The transport

```
GET https://theugandanjobline.com/                 200, 50 158 B   (10:22:29Z, 10:22:30Z — same size, a per-response token)  «Jobs in Uganda - The Ugandan Jobline», WordPress
GET https://theugandanjobline.com/jobs-in-uganda   200, 74 101 B   (10:23:38Z, and the same size at 10:23:40Z)  «Latest jobs in Uganda — 84,248 jobs», pager to /page/8425
```

## What the pages say

| question | answer |
| :-- | --: |
| jobs stated | **84 248** — «Latest jobs in Uganda 84,248 jobs» |
| pages | **8 425** (`/page/8425` in the pager), 10 a page — 84 250 |
| the unit | posts on a WordPress board since its beginning: **an archive by the number** — how many are live is not stated and not read here |
| JSON-LD | `Offer` and `Service` (the employer products), `PostalAddress`; no `JobPosting` on the listing |

*#233 recorded on 2026-09-11 a refusal «written by hand, motive: crawl cost»; the file read on 2026-09-13 (1 743 B) is the managed block plus operator lines and names no motive. Both are readings, each dated.*

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE. **Candidate adapter**, with the archive named: the paged listing enumerates everything ever posted, and the first question is what marks a post as live (a date, a closing date, a sitemap of recent posts). *Uganda has one adapter (`greatugandajobs`).*
- **Not a verdict that the host is closed** — nothing in the rules refuses `Claude-User`.
- **No configuration.** A user with a URL from this host can hand it to `cover-letter`.
