# Board measurement — Government of Timor-Leste — Recruitment (`timor-leste.gov.tl/?cat=44`, Timor-Leste): the Government's WordPress category of recruitment notices, served to the declared client (33 KB) with four posts on the day, rules open; the tenders app it also uses (`timorleste-jobs.tenderwell.app`) answers 404 at its root; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: timor-leste.gov.tl, timorleste-jobs.tenderwell.app -->
<!-- script: none -->
<!-- countries: TL -->
<!-- content: measured · **`/?cat=44&lang=en` (200, 33 434 B, md5 5e17334171c6 / 90f88ad16f5f — a rendered element moves) is the Government portal's «Recruitment» category — a WordPress archive with four `<h2>` posts on the day, no pager link seen, no count; `timorleste-jobs.tenderwell.app` (named by the search as the Government's recruitment platform) answers 404, 19 B at its root ×2 — an application that lists nothing at its root; `_robots.allowed` → open, certain on both; the posts not read** · 2026-09-18 -->
<!-- witness: none — a category page of four posts on the day · 2026-09-18 -->

**Found by the Timor-Leste search of #612 (a country never searched),
measured 2026-09-18 06:33–06:36 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #612: one search naming the national portals, the Government's
recruitment page and the UN aggregators (UNjobs, UNjobnet — global, left
aside), no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('timor-leste.gov.tl', '/?cat=44&lang=en')   open, certain
GET https://timor-leste.gov.tl/?cat=44&lang=en             200 ×2 — WordPress «Recruitment», four posts
GET https://timorleste-jobs.tenderwell.app/                 404, 19 B ×2 — nothing at the root
```

**The public entry found**: the Government's own recruitment notices —
few, on the portal. Whether the category pages by `paged=N` and what a
post carries are the adapter's first line; a national employment service
portal was not found by this search.
