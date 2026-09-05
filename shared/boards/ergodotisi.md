# Board adapter — Ergodotisi (Cyprus)

<!-- verified: 2026-09-05 -->

<!-- hosts: ergodotisi.com -->
<!-- script: ergodotisi.py -->
<!-- countries: CY -->
<!-- content: measured · sitemap read in full, 2 644 advertisements, 25 of 25 sampled pages parsed · 2026-09-05 -->
<!-- witness: the site's own "2 573 open jobs" against 2 644 in the sitemap — the gap runs as the mechanism predicts -->

**The cleanest index of the twenty-eight boards measured across Asia and Africa
on 2026-09-04.** `/sitemap.xml` declares three children and names them honestly
— `jobs.xml`, `companies.xml`, `other.xml` — so the advertisements are
reachable without counting companies, categories or site furniture. **Two of
twenty-eight do that.** The rest put everything in one file, and one of them,
`jobnet.com.mm`, puts fifty thousand entries there of which five are
advertisements.

```
ergodotisi.py list                                  # the sitemap alone, no titles
ergodotisi.py list --since 2026-08-05 --fetch       # with titles, one request each
ergodotisi.py ad --id vacancy-7f53159c-63758277
```

## 2 644, and the file says 5 302

`jobs.xml` holds **5 302 `<loc>` for 2 644 advertisements**: each appears once
under `/en-CY/jobs/` and once under `/el-CY/jobs/`. The split is exact — 2 644
on each side, measured, not assumed.

**They are not translations, and that was checked rather than inferred.** One
advertisement fetched under both prefixes on 2026-09-05: the documents differ by
**475 characters out of 77 000**, and the difference is `<html lang='en-CY'>`
against `<html lang='el-CY'>`. **The title, the employer and the body are
identical.** It is one advertisement under two paths; the prefix changes the
interface, not the content. So the adapter reads `/en-CY/` only.

*Had the two been translations, halving would have been wrong and the right
answer would have been to keep both with a language field. The measurement is
what decided it.*

## The only count in the series with an independent witness

The site advertises **"2 573 open jobs"** on its own pages. The sitemap yields
**2 644**. **Two provenances, and the gap runs the way the mechanism predicts**
— a sitemap keeps recently closed advertisements for a while, so it should sit
slightly above a live counter, and it does.

**A number that agrees with a second source it does not depend on is worth more
than a larger number that agrees with nothing.** Of every figure produced across
fifty-five countries on 2026-09-04, this is the only one with a witness.

**Freshness, measured 2026-09-05**: 53 distinct dates from `2026-06-26` to
`2026-09-04`, and **5 214 of the 5 302 entries dated within thirty days**. The
busiest day carries 854, 16 % of the file — lumpy, but a current stock rather
than an archive.

## Where the fields come from, and what is not there

**There is no `ld+json` on an advertisement page.** No `JobPosting`, no
`hiringOrganization`, no salary. The fields are parsed out of the document
title, which follows one shape:

    <role> at <employer> | Ergodotisi

**That is a parse of a title and the card says so.** Measured on 25 pages:

| field | rate | note |
| :-- | :-- | :-- |
| title | 25/25 | |
| employer | 25/25 | `None` when ` at ` is absent — never guessed |
| posted | 25/25 | from the sitemap's `lastmod`, not the page |
| city | 8/25 | only the parenthesised form is read |

**The city rate is low on purpose.** `Σύμβουλος Πωλήσεων Καταστήματος (Πάφος)`
parses; `Πωλητές/Πωλήτριες - Λεμεσός` does not, because the dash form was seen
and not measured. **Widening a pattern on an unmeasured form is how an
extractor starts returning wrong instead of returning less** — the raw title is
emitted beside the fields so the split is auditable.

**Titles are frequently in Greek even under `/en-CY/`**, because the prefix is
the interface. `--search` folds accents and matches either script as written;
it does not translate.

## Access

`robots.txt` reads, the host sweeps, and every path used here was asked about
**per path**, not per host. `/sitemap/jobs.xml`, `/en-CY/jobs` and an
advertisement URL: all permitted, 2026-09-05.

## What this adapter does not do

`list` without `--fetch` costs **one request** and returns ids and dates with
no titles. With `--fetch` it costs one request per advertisement, so
`--since` and `--limit` exist to bound it: the whole board is 2 644 pages and
reading all of them is not something to do by accident.
