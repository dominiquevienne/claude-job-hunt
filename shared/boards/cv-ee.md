# Board measurement — CV.ee (Estonia): reopened by the 2026-09-07 doctrine, the transport is OPEN, the search states 3 853 vacancies and the job sitemap lists 1 426

<!-- verified: 2026-09-12 -->

<!-- hosts: www.cv.ee, cv.ee -->
<!-- script: none -->
<!-- countries: EE -->
<!-- content: measured · rules read twice and certain — `ClaudeBot` named and refused, `*` open, so `identity()` answers `claude-user` and since #230 `verdict()` sweeps under it — and the transport answers 200 at the root (→ `/et`), at `/et/search` and on the sitemaps: the search page's inlined state says `"total":3853` («Kuva 3853 tööpakkumist») while `jobs-sitemap.xml` lists 1 426 `/et/vacancy/<id>/` URLs, 1 426 distinct, 71 distinct real `<lastmod>` — two numbers, two questions, not yet reconciled · 2026-09-12 11:58 UTC -->
<!-- witness: the Next.js state of `/et/search` (`total`, `searchMode: ELASTIC`, the first page's vacancy objects inlined) against the job sitemap — 3 853 ≠ 1 426, the gap is the adapter's first question; no adapter yet -->

**Measured 2026-09-12 at 11:56:24Z UTC for #233, lot 5 — a measurement of
the transport, not a decision about the host.** Every fetch under the
declared identity, the guard on the exact path first, `bin/fetch-body.py`.

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True, 1875 B, md5 d892cbb47388 both times — Cloudflare's managed block (`ClaudeBot` named and refused, `*` open) plus the operator's lines
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed()       True on `/`, `/et/search`, `/sitemap.xml`, `/jobs-sitemap.xml`, `/api/v1/vacancy-search-service/search?limit=1`
crawl_delay     none
```

## The transport — 200, and the site is served

```
GET https://www.cv.ee/                    200, 1 155 284 B   (11:56:24Z)  → https://www.cv.ee/et — Next.js (`__NEXT_DATA__`), no <title> in the shell
GET https://www.cv.ee/                    200, 1 155 242 B   (11:56:26Z)
GET https://www.cv.ee/et/search           200, 1 159 006 B   (11:57:39Z)  state: "total":3853, searchMode ELASTIC, the first page's vacancies inlined (id, salaryFrom/To, remoteWork, townId, countyId, countryId)
GET https://www.cv.ee/et/search           200, 1 159 006 B   (11:57:40Z)
GET https://www.cv.ee/sitemap.xml         200, 430 B         (11:58:14Z)  index: companies, jobs, search, pages
GET https://www.cv.ee/jobs-sitemap.xml    200, 236 441 B     (11:58:28Z)  1 426 <loc>
```

## Two numbers, two questions

| question | answer | where |
| :-- | --: | :-- |
| vacancies the search states | **3 853** | `/et/search`, `"total":3853` in the state and «Kuva 3853 tööpakkumist» in the text |
| `/et/vacancy/<id>/` URLs in `jobs-sitemap.xml` | **1 426**, 1 426 distinct ids, all `et` | one file, `<lastmod>` real — 71 distinct dates, 154 on 2026-09-08 |
| the gap | 2 427 | **not explained here** — a sitemap that lists a third of the store (a window, a tier, a language?) or a search total that counts more than one store: the adapter's first question, and it is answered by reading, not by choosing |

**Neither number is copied as the board's size.** *The `revolico` lesson in
the other direction: two true numbers, and the sentence that relates them is
where the error would live (`trois-nombres-trois-questions`).*

## A family, and a stack

CV-Online runs `www.cv.ee` (EE), `www.cv.lv` (LV) and `www.cvonline.lt` (LT)
— **three of the 61 hosts of #233**, one Next.js stack, one
`/api/v1/vacancy-search-service/search` behind the page (permitted by the
rules, not called here). *One adapter would be three countries; `cv.lv` and
`cvonline.lt` are measured in their own lot, not assumed from this one.*

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE.
  **Candidate — and a family candidate** with `cv.lv` and `cvonline.lt`:
  the search state carries the vacancy objects, the sitemap carries ids and
  real dates, and the 3 853 / 1 426 gap is the first thing to establish.
- **Not a verdict that the host is closed** — nothing refuses us.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
