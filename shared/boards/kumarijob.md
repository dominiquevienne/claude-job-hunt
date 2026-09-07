# Board adapter — Kumari Job (Nepal)

<!-- verified: 2026-09-07 -->

<!-- hosts: www.kumarijob.com -->
<!-- host-forms: www.kumarijob.com -->
<!-- host-forms-basis: read — `kumarijob.py:BASE` is a literal and no tenant or country is substituted into it · 2026-09-07 -->
<!-- script: kumarijob.py -->
<!-- countries: NP -->
<!-- content: measured · 167 advertisements in `sitemap-jobs.xml`, raw 167 / distinct 167, 0 duplicates, across 106 distinct employers; 3 of 3 ads read carry a full `JobPosting` with `validThrough` · 2026-09-07 -->
<!-- witness: none found — the site serves no total, and the two neighbouring files whose names say "job" are facets rather than a second count · 2026-09-07 -->

**Nepal had four boards measured on 2026-09-04 and no adapter. One of the four
closed since, and this is the cleanest of the three that remain.**

## Three files say "job" and one holds advertisements

```
sitemap-jobs.xml                167 advertisements   lastmod 2026-09-06/07
sitemap-job-listings.xml         21 FACETS           lastmod 2026-05-22
sitemap-other-job-listings.xml   39 FACETS           lastmod 2026-05-22
```

**`sitemap-job-listings.xml` holds `/job-listing/banking-jobs-in-nepal` and
`/job-listing/government-jobs-in-nepal`. The other holds `jobs-by-city`,
`employment-types`, `job-levels`.** *Neither is an advertisement.*

> **Reading "every sitemap whose name says job" would report 227 instead of
> 167.**

**This is `merojob.com`'s trap with the categories inverted.** *There,
`sitemap-tender_post-1.xml.gz` — 15 940 tenders — sits beside the jobs file,
and a name that does NOT say "job" holds non-jobs. Here two names that DO say
job hold none.* **`shared/robots-policy.md` records the first; this card records
the second, because a filename filter built against one lets the other
through.**

*The stale `lastmod` — 2026-05-22 against a daily one — is a second and
independent signal that the facet files are not the same kind of object. The
adapter does not rely on it: it names one file and never globs.*

## The listing's date is the FILE's, not the advertisement's

```
sitemap-jobs.xml    167 entries, 2 distinct <lastmod>       the regeneration
the advertisements  2026-08-20 → 2026-09-07 on 3 read       their own datePosted
```

**So `--since` is refused without `--fetch`, in code, with exit 8.** *A filter
on a regeneration date returns all or nothing and looks like a working filter
either way.*

**This is the opposite of `jobsearchzm.py`**, whose listing carries 23 real
dates and answers `--since` in one request. *The difference was measured before
either file was written, not assumed from the shape of a sitemap.*

## Two vocabularies for one field, on the same board

```
ad 76693   employmentType  "FULL_TIME"    schema.org's enumeration
ad 76273   employmentType  "Full Time"    free text
ad 75603   employmentType  "Full Time"
```

**One publisher, two spellings, on three advertisements from three different
employers.** `norm_type()` folds them to `FULL_TIME` **and keeps the original in
`employment_type_raw`** — *a fold that loses its source cannot be audited later.*

## Shapes read before the adapter was written

| field | shape here | shape on the Zambian neighbour |
| :-- | :-- | :-- |
| `jobLocation.address` | **PostalAddress object** | a plain string |
| `employmentType` | string, two spellings | a list |
| `validThrough` | **present 3 of 3** | often absent |
| `baseSalary` | absent 3 of 3 | absent |

**Assuming any of these would have produced empty fields in silence**, which is
the failure this repository names in `shared/never-fail-silently.md`.

## The address carries the employer, so no URL is composed

```
/<employer-slug>/<id>-<title-slug>
    /man-i-corp-pvt-ltd/76693-sales-development-manager-1
```

**`ad` takes `--url` and not `--slug`.** *The employer segment is part of the
address; composing it from a title would fabricate a path, which is the naming
motif this repository counts as a defect.*

## Access

Guard taken per exact path before every fetch. `www.kumarijob.com` answers
`read` and permits `/`, `/sitemap.xml`, the three children and the
advertisement paths — `allowed=True`, `certain=True`, measured 2026-09-07.

## What this card does not establish

- **nothing about the other three Nepali boards.** *`jobsnepal.com` REFUSES as
  of 2026-09-07 — `allowed=False`, `certain` — where the country page of
  2026-09-04 measured it open at 123 jobs and 55 tenders. `merojob.com` and
  `merorojgari.com` remain open and unadapted.*
- **no rate.** *167 is a stock read once; the country page establishes that two
  of the four Nepali boards date their own regeneration rather than their ads,
  and this is one of them.*
- **nothing about tenders here.** *1 of 145 on 2026-09-04 per the country page;
  not re-measured, and the adapter does not filter on it.*
