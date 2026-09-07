# Board adapter — Ango Emprego (Angola)

<!-- verified: 2026-09-07 -->

<!-- hosts: angoemprego.com -->
<!-- host-forms: angoemprego.com -->
<!-- host-forms-basis: read — `angoemprego.py:BASE`, a single literal; no tenant and no second host · 2026-09-07 -->
<!-- script: angoemprego.py -->
<!-- countries: AO -->
<!-- content: measured · 1 434 advertisements across two named `job_listing` sitemaps, all distinct, all under `/vagas/`; 1 085 dated 2026-07-29…09-07 and 349 in a 2020 block, with nothing between · 2026-09-07 -->
<!-- witness: none found — the site states no total; the country page's 1 451 of 2026-09-04 is an earlier reading of the same files, not a second source · 2026-09-07 -->

**The smallest archive of the three Angolan boards and the largest flow.**
`jobartis.com` holds 38 547 advertisements and published 202 since 1 August;
this one holds 1 434 and published 924. **That inversion is why it was built
second and the largest was not built at all.**

## The advertisements are in their own files, and the files are named

```
job_listing-sitemap.xml    1 000 <loc>
job_listing-sitemap2.xml     434 <loc>
                           -----
                           1 434, all distinct, all under /vagas/
post-sitemap1..8.xml       NOT read — blog posts
job_listing_region · job_listing_tag · category · misc   NOT read
```

**A `job_listing*` wildcard would be one keystroke and would also sweep
`job_listing_region` and `job_listing_tag`, which are taxonomies.** *A sibling
file is not the same kind of thing as its neighbour*, and this repository has
swept 15 940 tenders into a job count that way once.

## Two blocks, and six years of nothing between them

```
2020   349 advertisements ·  9 dates · 2020-10-15 … 2020-11-23
                                       226 on one day — 65 % of the block
       ——— nothing at all between 2020-11-23 and 2026-07-29 ———
2026 1 085 advertisements · 35 dates · 2026-07-29 … 2026-09-07
                                       busiest 96 — 8.8 % of the block
                                       median 30 a day
```

**The busiest-day check fired first at 15.8 % of the whole file** — the
instrument written the same afternoon in `shared/plausible-and-false.md` after
`jobartis` was found carrying 18 % in one 2018 import.

**Reading the distribution said what it was: a launch block of 2020, not a
defect in the current flow.** *The check flags; it does not conclude.* **So
`--since` is what makes this board usable**, and the default listing carries
both blocks with their dates so the gap stays visible rather than being
averaged away.

## A suspicion checked and refuted

**44 distinct dates for 1 434 advertisements, and not one day carrying a
single advertisement.** *That is what a regeneration stamp looks like* —
`myjobsfiji.com` gave all 3 187 of its entries one `lastmod`, and a freshness
count taken from it would have counted one afternoon's rebuild.

```
lastmod 2026-08-18 · datePosted 2026-08-18     4 of 4 sampled
lastmod 2026-08-26 · datePosted 2026-08-26
lastmod 2026-08-20 · datePosted 2026-08-20
lastmod 2026-08-18 · datePosted 2026-08-18
```

**It is not a stamp: the sitemap's date is the advertisement's own.** *A
suspicion checked and refuted is worth as much as one confirmed* — and it is
why `--since` can be trusted here.

## Three shapes that differ from the Angolan neighbour, and each is a decision

**`jobLocation.address` is a bare string** — `"Luanda"` — where
`angolaemprego` writes a `PostalAddress` object. A reader that knows only the
object form returns `None` on every advertisement, **and `None` reads as *this
board states no place***, which is false.

**`identifier.value` is not an identifier**: it holds
`https://angoemprego.com/?post_type=job_listing&#038;p=…`, a query URL escaped
twice. The `ledger_id` is built from the slug, which is the board's own, is in
the URL, and is stable.

**`baseSalary` is present and is not emitted**: `currency: USD` with an empty
`value`, on a board in a country whose currency is the kwanza. *The same shape
as `négociable XPF` on `burundijobs`.* **A field present and wrong is worse
than one absent.**

## What remains

**`jobartis.com` is unbuilt and its 38 547 are an archive**, not a market.
And the country page records that it serves 435 bytes to the guard and 14 050
bytes of HTML to a browser identity — **that has not been re-verified here,
and checking it would mean presenting a second identity after a first
verdict**, which the policy forbids. *The fact stands consigned and unchecked,
which is the honest state.*
