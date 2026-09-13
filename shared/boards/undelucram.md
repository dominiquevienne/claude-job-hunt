# Board measurement — Undelucram.ro (Romania): reopened by the 2026-09-07 doctrine, the transport is OPEN, and the listing states 1 459 results over 146 pages

<!-- verified: 2026-09-12 -->

<!-- hosts: www.undelucram.ro, undelucram.ro -->
<!-- script: none -->
<!-- countries: RO -->
<!-- content: measured · rules read twice and certain (231 B, `ClaudeBot` named and refused, `*` open; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200 at the root (→ `/ro`, 237 664 B) and at `/ro/locuri-de-munca` (348 974 B, twice, same size): the listing states «1.459 rezultate» and «1-10 din 1459 rezultate», pages `?page=2` … `?page=146`, 10 a page (146 × 10 = 1 460, within one of the stated); advertisement links of the shape `/ro/locuri-de-munca/<slug>/<id>`; the root states counts by city — București 435, Timișoara 160, Iași 89, Cluj-Napoca 74, Brașov 44, Oradea 35 · 2026-09-12 15:29 UTC -->
<!-- witness: the listing's own «1.459 rezultate», in the filter panel and in the pager line («1-10 din 1459»); 146 pages × 10 = 1 460 as the arithmetic; no adapter yet -->

**Measured 2026-09-12 at 15:28:07Z UTC for #233, lot 7 — a measurement of
the transport, not a decision about the host.** Every fetch under the
declared identity, the guard on the exact path first, `bin/fetch-body.py`.

## The rules — reopened by the doctrine of 2026-09-07, and 1 459 results behind them

```
robots.txt      read twice, certain: True, 231 B, md5 4473a06c73ea both times — a short file: `ClaudeBot` named and refused, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed()       True on `/`, `/ro/locuri-de-munca`, `/ro/locuri-de-munca?page=2`
crawl_delay     none
```

## The transport — 200

```
GET https://www.undelucram.ro/                       200, 237 664 B   (15:28:07Z)  → https://www.undelucram.ro/ro — «Undelucram.ro - Descoperă angajatorii…»
GET https://www.undelucram.ro/                       200, 237 670 B   (15:28:08Z — dynamic, sizes differ)
GET https://www.undelucram.ro/ro/locuri-de-munca     200, 348 974 B   (15:29:05Z)  «Vezi ultimele locuri de muncă și aplică informat!» — «1.459 rezultate»
GET https://www.undelucram.ro/ro/locuri-de-munca     200, 348 974 B   (15:29:07Z — same size, a per-response token)
```

## What the listing says

| question | answer |
| :-- | --: |
| results stated | **1 459** — «1.459 rezultate» in the filter panel, «1-10 din 1459 rezultate» in the pager line, «Vezi joburi (1459)» on the button |
| pages | **146** (`?page=2` … `?page=146`), 10 a page — 146 × 10 = 1 460, within one of the stated |
| by city, on the root | București 435 · Timișoara 160 · Iași 89 · Cluj-Napoca 74 · Brașov 44 · Oradea 35 — «Joburi pe locații», a partial partition |
| the advertisement link | `/ro/locuri-de-munca/<slug>/<id>` (`/she-regional-manager/<id>`) — the trailing number is the key |
| JSON-LD | none on the listing |

*An employer-review site with a job board attached (Undelucram = «where we
work»): the listing is paged and stated, and a job page's markup is the
adapter's first question.*

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE.
  **Candidate adapter**: 146 pages at 1 s, the stated 1 459 as the witness,
  the id in the URL's tail. *Romania is at zero adapters.*
- **Not a verdict that the host is closed** — nothing refuses us.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
