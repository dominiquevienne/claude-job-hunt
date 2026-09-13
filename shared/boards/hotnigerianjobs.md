# Board measurement — HotNigerianJobs (Nigeria): reopened by the 2026-09-07 doctrine, the transport is OPEN, and the weekly sitemap holds 4 190 posts — each a recruitment digest of «N positions»

<!-- verified: 2026-09-12 -->

<!-- hosts: www.hotnigerianjobs.com, hotnigerianjobs.com -->
<!-- script: none -->
<!-- countries: NG -->
<!-- content: measured · rules read twice and certain (2 302 B, Cloudflare's managed block naming `ClaudeBot`, `*` open bar `/kgb/` and `/images/`; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200 at the root (250 096 B, twice) and on the sitemaps: an index of 21 weekly files, `sitemap-37-2026.xml` alone 4 190 `/hotjobs/<id>/` URLs, 4 190 distinct ids, 5 distinct `<lastmod>`; the root lists 50 posts and `/jobs/7days/` 50; a post is a digest — «BIC Nigeria Job Recruitment (4 Positions)», «(124 Positions)» — so 4 190 posts is not 4 190 advertisements; `/jobs` answers the site's own 404 · 2026-09-12 15:30 UTC -->
<!-- witness: none the site states — no total on any page read; the weekly sitemap is the only enumeration, and its unit is the post, not the position; no adapter yet -->

**Measured 2026-09-12 at 15:27:55Z UTC for #233, lot 7 — a measurement of
the transport, not a decision about the host.** Every fetch under the
declared identity, the guard on the exact path first, `bin/fetch-body.py`.

## The rules — reopened by the doctrine of 2026-09-07, and 4 190 posts behind them

```
robots.txt      read twice, certain: True, 2302 B, md5 f98a071dcf74 both times — the managed block (`ClaudeBot` named and refused, `*` open) plus `Disallow: /kgb/`, `/images/`; `Sitemap: http://www.hotnigerianjobs.com/sitemap.xml`
identity("/")   http, claude-user
verdict()       sweep True, sweep_token claude-user
allowed()       True on `/`, `/jobs`, `/jobs/7days/`, `/sitemap.xml`, `/sitemap-37-2026.xml`
crawl_delay     none
```

## The transport — 200

```
GET https://www.hotnigerianjobs.com/                     200, 250 096 B   (15:27:55Z, 15:27:56Z — same size, a per-response token)  «Search for jobs & find your dream job | HotNigerianJobs»
GET https://www.hotnigerianjobs.com/jobs                 404, 18 260 B    (15:28:53Z, twice)  the site's own «404 - Page not found» — a guessed path
GET https://www.hotnigerianjobs.com/sitemap.xml          200, 3 005 B     (15:29:48Z)  index of 21 weekly files, `sitemap-37-2026.xml` first (lastmod 2026-09-11)
GET https://www.hotnigerianjobs.com/sitemap-37-2026.xml  200, 730 202 B   (15:30:03Z, byte-identical twice)  4 190 <loc>
GET https://www.hotnigerianjobs.com/jobs/7days/          200, 179 233 B   (15:30:04Z)  50 `/hotjobs/<id>/` links
```

## What the sitemap says — posts, not positions

| question | answer |
| :-- | --: |
| files in the index | 21, one a week (`sitemap-<week>-<year>.xml`), 37/2026 first |
| `<loc>` in `sitemap-37-2026.xml` | **4 190**, all `/hotjobs/<id>/<slug>.html`, 4 190 distinct ids, 5 distinct `<lastmod>` |
| posts on the root and on `/jobs/7days/` | 50 each; 1 006 links on the root, 318 of them `/role/<n>/`, 162 `/discipline/`, 63 `/field/`, 39 `/location/` — facets |
| the unit | **a post** — «BIC Nigeria Job Recruitment (4 Positions)», «(124 Positions)», «HNJ Exclusive Job Goody Bag — September Week Two»: a digest that bundles positions, and a weekly bag |
| a stated total | none found on any page read |

**4 190 posts a week is not 4 190 advertisements** — the position count is
inside each post's title and body, and a digest of 124 positions is one
`<loc>`. *The adapter's first question is the post page: what a «position»
looks like there, and whether one post can be emitted as many rows.*

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE.
  **Candidate adapter**, with the unit named: the weekly sitemaps enumerate
  posts, the post page is the object. *Nigeria is at zero adapters.*
- **Not a verdict that the host is closed** — nothing refuses us; the 404 on
  `/jobs` is the site's own page, served.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
