# Board adapter — Job Search Zambia

<!-- verified: 2026-09-05 -->

<!-- hosts: jobsearchzm.com -->
<!-- script: jobsearchzm.py -->
<!-- countries: ZM -->
<!-- content: measured · 153 advertisements in `job_listing-sitemap.xml`, raw 153 / distinct 153, 0 duplicates · 2026-09-05T11:48Z -->
<!-- witness: none found — no site-served counter, and the only candidate is a homepage facet, which is not exhaustive -->
<!-- hosts-source: named by a "best job sites in Zambia" listing; no hostname composed · 2026-09-04 -->

**What the body serves was checked before the count was believed.** Title *Jobs
in Zambia — Job Search Zambia*, 99 180 bytes, every linked host its own. The
neighbouring domain `bestzambiajobs.com` carries the same managed `robots.txt`
and serves a Turkish sports-streaming page: **a Zambian-sounding name does not
make a Zambian board**, and that was established on 2026-09-05 rather than
assumed.

## The measurement

Fetched with `bin/fetch-body.py`, provenance written beside each body.

    https://jobsearchzm.com/sitemap.xml            HTTP 200 ·    911 o · INDEX, 5 entries
    https://jobsearchzm.com/job_listing-sitemap.xml HTTP 200 · 41 535 o · md5 45698d8aa506
      153 <loc> · 153 distinct · 0 duplicates · all under /job/
      23 distinct dates · 2026-07-15 → 2026-09-04 · heaviest day 24 on 2026-09-02
      151 of 153 dated on or after 2026-08-01

**The dates are the advertisements', not a regeneration stamp** — 23 distinct
values across 153 entries, and the heaviest single day carries 24. *A file whose
dates all collapse onto today is stamping its own rebuild; this one is not.*

The index also declares `post-`, `page-`, `category-` and `author-` sitemaps.
**Only `job_listing` was read, and 153 is a count of advertisements rather than
of `<loc>`.**

## `witness: none found`

No global counter on the homepage. Per-category counts exist and summing them
would be a **facet partition**, which is a witness only when exhaustive — measured
elsewhere, homepage facets summed to between 45 % and 92 % of their own totals,
and one exceeded it. **The count stands on one reading of one file, and says so.**

## Zambia has three boards and none had a sheet

`gozambiajobs.com` (368, undated) and `jobzambia.com` (45) are the other two.
None of the three had ever been counted before 2026-09-05.
