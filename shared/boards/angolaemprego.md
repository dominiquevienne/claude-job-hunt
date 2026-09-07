# Board adapter — Angola Emprego (Angola)

<!-- verified: 2026-09-07 -->

<!-- hosts: angolaemprego.com -->
<!-- host-forms: angolaemprego.com -->
<!-- host-forms-basis: read — `angolaemprego.py:BASE`, a single literal; no tenant and no second host · 2026-09-07 -->
<!-- script: angolaemprego.py -->
<!-- countries: AO -->
<!-- content: measured · 3 724 advertisements under `/vagas/` in a flat sitemap of 9 111 <loc>; `lastmod` on 3 724 of 3 724, busiest day 103 (2.8 %) · 2026-09-07 -->
<!-- witness: none found — the site states no total, and the country page's 3 694 of 2026-09-04 is an earlier reading of this same file rather than a second source · 2026-09-07 -->

**Angola's first adapter.** Its country page named three boards on
2026-09-04 and left all three `à construire`; this is the one it measured as
the most active by flow.

## The sitemap is one flat file and most of it is not advertisements

```
9 111 <loc> in a single sitemap.xml
  5 334  /noticias/    news articles
  3 724  /vagas/       advertisements      <- the only ones counted
      6  /cursos/ · /company/ · /sobre · /empresas
```

**Counting the file would report 9 111 and be wrong by a factor of 2.4.**
This is a news outlet with a jobs section — the country page had established
that, and the adapter **prints the raw figure beside the kept one** so the
ratio stays visible instead of becoming a number nobody can check.

## The busiest day is a check, not a statistic

```
lastmod        3 724 of 3 724 · 2025-03-29 … 2026-09-07
distinct days  355
busiest day    2026-08-14 · 103 advertisements · 2.8 % of the total
since 01.08    1 026     (the country page read 996 on 2026-09-04)
```

**`jobartis.com`, the largest board in this country, carries 2 525 distinct
dates *and* 7 130 advertisements on one day of 2018 — 18 % of its archive in
a single import.** So a high count of distinct dates satisfies the instrument
that separates an archive from a stock **and does not protect against an
import**; the busiest day does.

**Here it is 2.8 %. This is a flow.**

## Without the non-strict fallback, every advertisement reports no data

The `JobPosting` block carries a raw control character:

```
json.loads(...)  ->  Invalid control character at: line 5 column 33
```

**`strict=False` is not decoration on this board — it is the difference
between reading every advertisement and reading none.** *A parser that tries
once returns a confident zero, and that zero looks exactly like a site
publishing no structured data.*

## What is emitted

```
title · employer · city · employment_type
posted (datePosted) · valid_through (validThrough)
ledger_id — from identifier.value, which is the slug: the board's own
```

**A redirect is refused rather than counted.** Nothing here redirected, and
the check is present because five of six listed URLs bounced to the root on
`emploisburkina.bf` the same day and only `final_url` showed it.

## What is not measured

**The other two Angolan boards, both built since.** `www.jobartis.com`
(40 882 archive, 216 since 1 August — see `jobartis.md`) and
`angoemprego.com` (1 451 archive, 874 since 1 August) were named on the
country page, guarded open, and unbuilt when this card was written.

**Corrected 2026-09-07: 38 547 -> 40 882.** *That figure counted the `/emprego-<slug>` form alone; the board serves 2 294 more under a bare `/<slug>`, and they are advertisements — see `jobartis.md`, which was built from the same sitemap.* **The flow moved too, 202 -> 216, and that is not a correction**: both were right on their days, two days apart. *One number changed because it had been measured wrongly and the other because the board grew, and nothing in either number says which.* *And the overlap
between the three was measured at 0.0 %, 0.1 % and 0.0 % on matched windows —
the first conclusive negative of that instrument, because Angola is the first
country where both of its preconditions held: one language throughout, and
windows cut at the same date.*
