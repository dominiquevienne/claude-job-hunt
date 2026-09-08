# Board adapter — Careerical Sierra Leone (`sierra.careerical.com`)

<!-- verified: 2026-09-08 -->

<!-- hosts: sierra.careerical.com -->
<!-- host-forms: sierra.careerical.com -->
<!-- host-forms-basis: read — `careerical_sl.py:BASE`, a single literal. The apex `careerical.com` carries a different rules file and is never fetched · 2026-09-08 -->
<!-- script: careerical_sl.py -->
<!-- countries: SL -->
<!-- content: measured · 2 344 advertisements across three named sitemaps — 1 000 + 1 000 + 344, with 0 duplicates between files; 1 377 distinct dates 2020-12-06 → 2026-08-28, busiest day 6 (0.3 %), 116 in 2026 and 17 since 2026-08-01 · 2026-09-08 -->
<!-- witness: the site's own home-page counter reads 2 350 against the sitemaps' 2 344 — recorded on the country page 2026-09-04 and NOT re-measured here; this card's 2 344 is the sitemap count alone · 2026-09-08 -->

**Sierra Leone's first adapter, and it is not the network node.** The country
page names both and separates them: `sierraleonejobsearch.com` is a node of
the fabricated network; this is *«board local»*, added to that page on the
evening of 2026-09-04 after it had already been written without it.

*This card makes no claim about the network, measures no overlap, and quotes
no overlap figure.*

## The most evenly spread dates measured in this repository

```
2 344 advertisements   1 377 distinct dates   2020-12-06 → 2026-08-28
busiest day              6, which is 0.3 %
in 2026                116        since 2026-08-01   17
```

Against 1.4 % for `jobwebrwanda`, 18.5 % for `jobartis`, 60.5 % for
`ihararejobs`. **A board publishing a few a week for six years leaves a flat
distribution**, and this one is still publishing — the newest advertisement is
eleven days old and its `validThrough` is in the future.

## Three sitemaps by name, and a taxonomy a glob would eat

```
job-sitemap.xml    1 000      <- Yoast's round cap
job-sitemap2.xml   1 000      <- the cap again
job-sitemap3.xml     344      <- partial, so the set is complete
                   -----
                   2 344      0 duplicates BETWEEN files
```

**`job_category-sitemap.xml` sits in the same index** and a `job*` glob takes
it. The three are named individually.

*The cross-file duplicate check is not ceremony*: 403 of 1 783 URLs were
duplicates between files on another board, **under a sum that added up
perfectly**. **Two round caps and a partial third is what a complete set looks
like** — a single file at exactly 1 000 would be a ceiling to distrust.

## The `ld+json` is HTML-escaped and it is not valid JSON

Three problems, and only two can be repaired:

```
1.  written with &quot; instead of "              ->  html.unescape
2.  {"@context":"http:   — the value is truncated ->  one substitution
3.  unescaped " inside `description`              ->  NOT repairable
```

**The third is what a repair cannot reach.** `such as"I will conduct
stakeholder engagement,"explain how` — *the string's own boundaries are the
thing that was lost*, so no rewrite can recover them without already knowing
where the field ends.

**So this module does not parse the document; it extracts the fields it
needs** — and `description`, the field that breaks the JSON, is the one field
it does not want. *What cannot be parsed is also what was not wanted.*

The order is: parse as JSON · repair `@context` and parse · take the fields
directly. **Every advertisement reports its path in `read_by` and `list
--fetch` counts them.**

```
measured on 6:   json                                  0
                 json after `@context` repair          4
                 fields — the block is not valid JSON  2
```

**Not one advertisement parsed as valid JSON, and a third needed the field
reader.** *Without that third path, a third of this board is lost silently* —
and a shift in these counts is the site changing its markup, which would
otherwise be invisible.

## The place is in the wrong fields

```
"addressLocality": ""
"addressRegion":   "Freetown|Sierra Leone"
"postalCode":      "Freetown|Sierra Leone"      <- the same string
```

**A reader that takes `addressLocality` — which is what the schema is for —
gets nothing on this board.** The town and the country are pipe-joined into
`addressRegion` and copied into `postalCode`, which is therefore not a postal
code and is not emitted.

`city_source` says where the value came from, on every row. *One of six reads
`CQX6+VX3,Foday D…` — a Plus Code an employer typed into the field, which the
adapter passes through untouched: it is the site's value, not a parse error.*

## The salary field carries one word

`baseSalary.price` reads **`negotiable`** on 6 of 6, with `salaryCurrency`
`"Le"`. It is emitted as `salary_text` and never as a number, because it is
not one — *and on this sample it carries no information at all.*

## The sitemap date is the posting date — 4 of 4 where both were readable

`lastmod` equals `datePosted` every time both were available, across dates from
2022 to 2026, and `date_conflict` is emitted and counted when they disagree.
**So `--since` costs three requests**, not one per advertisement.

## What was exercised, 2026-09-08

```
list                        2 344 · 1000+1000+344 · 0 duplicates between files
list --fetch --limit 6      6 read · 6 kept · 0 unreadable · 0 date conflicts
                            read_by: repair × 4, fields × 2
list --fetch --limit 4      city Freetown / country Sierra Leone on 3 of 4
```

**Sierra Leone's other hosts, from the country page and not re-measured
here:** `jobsearchsl.com` is a blog, `www.sierraleonejob.com` refuses,
`jobberman.com.sl` · `jobnet.com.sl` · `salonejob.com` do not resolve, and
`jobs.sl` has an unverifiable TLS certificate and was not reached.
