# Board adapter — Go Zambia Jobs (Zambia)

<!-- verified: 2026-09-05 -->

<!-- hosts: www.gozambiajobs.com, gozambiajobs.com -->
<!-- script: none -->
<!-- countries: ZM -->
<!-- content: measured · 368 advertisements in `sitemap-jobs-1.xml`, raw 368 / distinct 368, 0 duplicates · 2026-09-05T11:45:51Z -->
<!-- witness: none found — see below, and that is a finding rather than an omission -->
<!-- hosts-source: named by a "best job sites in Zambia" listing; no hostname composed · 2026-09-04 -->

**The first Zambian board this repository carries. There were none.**

## Two hosts, and the second is not the first

The sitemap index is served from `www.gozambiajobs.com`; **every one of its 41
entries points at the apex `gozambiajobs.com`, without `www`.** The guard was
asked separately on the apex before anything was fetched from it — a verdict
taken at `www` covers nothing on the bare host.

    identity(www.gozambiajobs.com, /sitemap.xml)   -> claude-user
    identity(gozambiajobs.com,     /sitemap-jobs-1.xml) -> claude-user

## The measurement

Both bodies were fetched with `bin/fetch-body.py`, which wrote their provenance
beside them.

    https://www.gozambiajobs.com/sitemap.xml
      2026-09-05T11:45:01Z · HTTP 200 · 3 714 o · md5 488c4c007f4e
      INDEX · 41 sub-sitemaps, all on the apex

    https://gozambiajobs.com/sitemap-jobs-1.xml
      2026-09-05T11:45:51Z · HTTP 200 · 32 339 o · md5 f70bcf9c3174
      368 <loc> · 368 distinct · 0 duplicates · every one under /jobs/

**368 is a count of advertisements, not of `<loc>`** — the index separates
`sitemap-jobs-1`, `sitemap-companies-1..3`, `sitemap-blog-1`, `sitemap-tags`,
`sitemap-locations` and thirty-four others, and only the first was read.

## The file carries no dates, and that has a consequence

**Not one `<lastmod>` in 368 entries.** So the two questions this repository has
learned to ask cannot be asked here:

- **stock or flow?** Undecidable. A board's sitemap total measures how long it has
  existed unless dates say otherwise, and these do not.
- **are the dates a regeneration stamp?** Unanswerable, and therefore not a risk
  either — there is nothing to misread.

**Write `368 advertisements at 2026-09-05T11:45:51Z` and never a rate.**

## `witness: none found`, and why that is a measurement

The homepage carries **no global counter**. It carries per-employer and
per-category counts — *Accounting & Auditing 15 jobs, Banking & Financial
Services 18 jobs* — and summing those would be a **facet partition**.

**A facet partition is a witness only when it is exhaustive, and a homepage
widget is not.** Measured on five hosts of the `<pays>jobsearch.com` network:
their homepage facets summed to 303, 360, 256, 209 and 336 against totals of
451, 327, 339, 478 and 466 — **one of them exceeded its own total.**

So the count stands on one reading of one file. **That is stated, not hidden.**

## Not to be confused with the other Zambian domain

`www.bestzambiajobs.com` carries the same Cloudflare managed `robots.txt` and is
**not a job board**: on 2026-09-05 it served a Turkish sports-streaming page
whose sitemap index pointed entirely at a third domain, with zero occurrences of
*zambia*, *job* or *vacancy*. It appears in host lists because the file survived
the domain's change of use. **No adapter, and no country page should count it.**

## What remains unmeasured

`jobsearchzm.com` and `jobzambia.com` were guarded on 2026-09-04 and both permit;
**neither has been counted.** They are named here so that a later reader knows
the country was not exhausted.
