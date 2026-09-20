# Board measurement — dubizzle jobs (`uae.dubizzle.com/jobs/`, United Arab Emirates): the classifieds group's jobs vertical — a Next.js page whose own state carries an Algolia query on the index `jobs.com` answering `nbHits: 1784` (full-time 1 711, part-time 43, contract 24, temporary 6) on 2026-09-20; served to the declared client (321 KB), rules open; the domain from the search engine, never composed; no adapter yet

<!-- verified: 2026-09-20 -->

<!-- hosts: uae.dubizzle.com -->
<!-- script: none -->
<!-- countries: AE -->
<!-- content: measured · **`/jobs/` (200, 321 027 / 321 010 B, md5 5ae68986a1ec / e79f1960efee — a rendered element moves) is a Next.js page (`__NEXT_DATA__`) whose Redux state carries the results of the page's own Algolia queries — app id `WD0PTZ13ZS`, index `jobs.com` (the search key is not in `__NEXT_DATA__` — the bundle or a network panel would name it) — including a facet count with `hitsPerPage=0`: `nbHits: 1784`, `required_commitment` FT 1 711, PT 43, CO 24, TP 6 (`exhaustiveNbHits: true`); the list itself (`/jobs/search/`) and the ad were not read; links `/jobs/`, `/ar/jobs/`, `/jobs-wanted/` (job seekers' own ads — not the board); rules read: `*` refused `/report/`, `/profile/*`, `/accounts/*` and nothing under `/jobs/`, no Crawl-delay; `_robots.allowed('uae.dubizzle.com','/jobs/')` → open, certain. Egypt: the prose that named «dubizzle» beside Egypt gave no domain and no source in this search named one — not measured, not composed** · 2026-09-20 -->
<!-- witness: the page's own Algolia `nbHits: 1784` for the index `jobs.com` on 2026-09-20, with its commitment facets summing to 1 784 · 2026-09-20 -->

**Named without a domain on the Egypt page's prose and as a bare line on
the Emirates page (#772); the domain established from the search engine's
results (`uae.dubizzle.com/jobs/`, `dubai.dubizzle.com/jobs-wanted/`,
`abudhabi.dubizzle.com/jobs-wanted/`), never composed; measured 2026-09-20 12:33
UTC by the declared client, the guard on the exact path first,
`bin/fetch-body.py`, two reads.** *A measurement, not an adapter.*

## What it is

dubizzle is the Emirates' classifieds site (the Dubizzle Group, with
Bayut); its jobs vertical lists employers' ads at `/jobs/` and job
seekers' own ads at `/jobs-wanted/` (the latter is not a board). The page
is Next.js; its state carries the Algolia queries the page ran on the
server — the count above is one of them, taken with `hitsPerPage=0` — and
the list page `/jobs/search/` runs the same index with hits.

```
_robots.allowed('uae.dubizzle.com', '/jobs/')   open — /jobs/ not refused, /profile/* and /accounts/* are
GET https://uae.dubizzle.com/jobs/   200 ×2 — __NEXT_DATA__: Algolia jobs.com, nbHits 1784, FT 1711 / PT 43 / CO 24 / TP 6
```

## What an adapter would do, and what it never does

The adapter's first line: the page's own Algolia call (app id and index in
every visitor's page, the search key in the bundle — the shape of
SparkHire's and Cornerstone's tokens, replayed with the page's parameters) on
`/jobs/search/` with hits, paged by `page`, the stated `nbHits` beside the
emitted count; the ad by its page. Never: the seekers' ads
(`/jobs-wanted/`), the contact reveal (a phone behind a button), the
accounts.
