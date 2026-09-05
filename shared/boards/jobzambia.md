# Board adapter — JobZambia

<!-- verified: 2026-09-05 -->

<!-- hosts: jobzambia.com -->
<!-- script: none -->
<!-- countries: ZM -->
<!-- content: measured · 45 advertisements in `job_listing-sitemap.xml`, raw 45 / distinct 45, 0 duplicates · 2026-09-05T11:48Z -->
<!-- witness: none found — no site-served counter; the homepage facet is not exhaustive -->
<!-- hosts-source: named by a "best job sites in Zambia" listing; no hostname composed · 2026-09-04 -->

**The smallest of the three Zambian boards, and the only one publishing
structured data** — its homepage references `schema.org`, which the other two do
not.

**What it serves was checked first:** title *JobZambia – Job Opportunities in
Zambia.*, 52 673 bytes, hosts referenced almost entirely its own.

## The measurement

    https://jobzambia.com/sitemap.xml             HTTP 200 ·    908 o · INDEX, 5 entries
    https://jobzambia.com/job_listing-sitemap.xml HTTP 200 · 13 220 o · md5 b83e16040f96
      45 <loc> · 45 distinct · 0 duplicates · all under /job/
      18 distinct dates · 2026-07-21 → 2026-09-03 · heaviest day 4 on 2026-07-28
      26 of 45 dated on or after 2026-08-01

**Eighteen distinct dates over forty-five entries, heaviest day four** — the
flattest date distribution of the three, and the clearest case of per-ad dates
rather than a rebuild stamp.

Both bodies fetched with `bin/fetch-body.py`; provenance written beside them.

## `witness: none found`

Same reason as its two neighbours: no global counter, and a homepage facet is
not an exhaustive partition.

## Scale, stated with its unit

**45 advertisements at 2026-09-05T11:48Z**, of which 26 carry a date in the last
five weeks. *That is a stock with a date, not a rate: no second reading exists
yet, so nothing here supports "per week".*
