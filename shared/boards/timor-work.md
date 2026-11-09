# Board measurement — Timor.Work (`timor.work`, Timor-Leste): «Job vacancies in Timor-Leste. Private sector, NGOs, UN» — a DJANGO/WAGTAIL board, not Ghost: the `ghost` in its pages is a `btn-ghost` CSS class. 1 304 vacancy addresses in a sitemap that is NOT pruned, and the deadline is the only thing that says which are open

<!-- verified: 2026-11-09 -->

<!-- hosts: timor.work -->
<!-- script: timorwork.py -->
<!-- countries: TL -->
<!-- route: http · 1304 · 2026-11-09 -->
<!-- content: measured · read 2026-11-09: **this is DJANGO and WAGTAIL, not Ghost, and the Ghost reading came off a CSS class.** `robots.txt` says so in its own comments — `Disallow: /admin/  # disable crawling django admin`, `Disallow: /cms/  # and wagtail admin` — and every vacancy body is a Wagtail StreamField whose blocks carry `data-block-key`. *The word `ghost` occurs in a vacancy page exactly once, as `class="btn btn-ghost"`, a DaisyUI button.* **And there is no `/page/N/` pager**: `?page=` and `/page/` occur ZERO times on the front, and the bare `/jobs/` is a **404** (12 727 B, body not kept). The facets the 2026-09-18 line named do exist one level down: `/jobs/tag/<slug>/` and `/jobs/employer/<slug>/`. **The route is the sitemap**, 102-byte rules file with two `Disallow:` lines, no `Sitemap:` declared and no `Crawl-delay`, so the 2 s pace is ours; guard `state: read, certain: True` on every exact path, `www.` failing at the connection and left alone. `/sitemap.xml` is a flat `urlset`: **1 306 `<loc>`, 1 305 distinct — the duplicate is the ROOT, listed twice — so 1 304 vacancy addresses**, all apex, all a flat `/<slug>/`, and no slug is a page name or carries a second segment (the shortest are `driver`, `accountant`, `ofisial-kampu`). **THE SITEMAP IS NOT PRUNED**: `lastmod` spans 2024-02-04 to 2026-11-07 (523 in 2024, 378 in 2025, 397 in 2026) and the first, median and last members all carried EXPIRED deadlines — so 1 304 counts ADDRESSES over three years and never open vacancies, and the sitemap carries no deadline at all. The front lists **30** with every field inline — employer and its facet slug, title, city, a clamped description and `Deadline:` — of which **15 were open on 2026-11-09**. Pages are server-rendered with **no JSON-LD**. **Dates are Django AP-style `N`: March, April, May, June and July are spelled in FULL and unpunctuated and `Sept.` is four letters, so the stdlib abbreviated-month directive rejects them — it lost 13 of the 36 values held, all `June`** · 2026-11-09 -->
<!-- content: measured · **the root (200, 107 027 B, md5 1ab9f3099bce / 07a3d90c80a9 — a rendered element moves) is a Ghost publication of vacancies with `/jobs/tag/<tag>/` (international, gedsi, mid-level…) and `/jobs/employer/<slug>/` facets; no count stated, no JobPosting; `_robots.allowed('timor.work','/')` → open, certain; the posts and the pager not read** · 2026-09-18 -->
<!-- witness: none — no count is stated anywhere, which the 2026-09-18 line already said. *What IS established is that the two enumerators NEST: all 30 front cards are in the sitemap, difference empty, so the sitemap is a genuine superset and not a partly disjoint second view.* So the 1 304 is the adapter's own extraction with nothing corroborating it, and the 15 open on 2026-11-09 is a reading of the front page and not of the board · 2026-11-09 -->
<!-- witness: none — the front states no count · 2026-09-18 -->

**Found by the Timor-Leste search of #612 (a country never searched),
measured 2026-09-18 06:33–06:36 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #612: one search naming the national portals, the Government's
recruitment page and the UN aggregators (UNjobs, UNjobnet — global, left
aside), no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('timor.work', '/')   open, certain
GET https://timor.work/               200 ×2 — a Ghost publication, tag and employer facets
```

The country's NGO/UN vacancy board. The post list, its pager (Ghost pages
by `/page/N/` and serves an RSS at `/rss/`) and what a post carries are
the adapter's first line (its `adapter` issue).
