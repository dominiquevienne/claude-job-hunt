# Board adapter — MeroJob (Nepal)

<!-- verified: 2026-09-07 -->

<!-- hosts: merojob.com, sg.merojob.com -->
<!-- host-forms: merojob.com, sg.merojob.com -->
<!-- host-forms-basis: read — `merojob.py:BASE` and `:JOBS` are literals; the index is served by the apex and every child by `sg.`, so BOTH are declared · 2026-09-07 -->
<!-- script: merojob.py -->
<!-- countries: NP -->
<!-- content: measured · 239 advertisements in `sitemap-job_post-1.xml.gz`, raw 239 / distinct 239, 0 duplicates, 0 under `/etender/`; a sample spread over the file keeps 4 of 5 on `validThrough` · 2026-09-07 -->
<!-- witness: none found — the site serves no total, and the sibling file's 15 940 tenders are a different grandeur rather than a second count · 2026-09-07 -->

**Nepal's largest board, and the second of its four to get an adapter.**

## The index is on one host and every child on another

```
https://merojob.com/sitemap.xml          the index, 14 children
https://sg.merojob.com/sitemap-*.xml.gz  ALL FOURTEEN
```

**`sg.merojob.com` is the host `shared/robots-policy.md` rule 5 was written
about** — *it is not in any card's `hosts:` line and the guard had only ever
been asked about `merojob.com`.* **Both hosts are declared here, and each URL is
gated on the host that will actually be fetched.**

## Tenders are rejected BY PATH, never by filename

```
jobs     https://merojob.com/<slug>            depth 1   239 of 239
tenders  https://merojob.com/etender/<slug>    depth 2   15 940 of 15 940
```

**`sitemap-tender_post-1.xml.gz` sits beside the jobs file in the same index.**
*Reading "every sitemap in the index" would report 16 179 Nepali jobs.*

**But the filename is not what this adapter trusts, because a filename is not a
predicate.** *The path is one, it was measured on both files, and `/etender/` is
rejected explicitly with a count — so the check reports whether the named file
stayed clean instead of assuming it.*

**And the `lastmod` is not a predicate either**, which is worth writing because
it looks like one:

```
sitemap-job_post-1.xml.gz     2026-09-07T03:00   the ads
sitemap-tender_post-1.xml.gz  2026-09-02T11:04   the tenders — also recent
sitemap-job_by_category-1     2025-07-24         a facet
six of the fourteen           no <lastmod> at all
```

> **`lastmod` separates facets from content. It does not separate tenders from
> jobs — both regenerate.** *`kumarijob.md` carries the mirror case, where two
> files whose names DO say "job" hold only facets and `lastmod` does separate
> them. Neither signal generalises; the path did.*

## Three layers of date, and only the deepest is true

```
the index's <lastmod> for the child   2026-09-07T03:00   regenerated today
the child's own <lastmod> per entry   2 values over 239: 09-03 and 09-04
the advertisement's datePosted        2026-08-24 -> 2026-09-07, spread
```

**An advertisement posted 2026-09-07 carries `2026-09-04` in the sitemap.** *So
the middle layer is neither the regeneration nor the posting: it is inert — and
it is the one a reader would take for a date.* **`--since` refuses without
`--fetch`, in code, exit 8**, and the field travels as `sitemap_lastmod_inert`
so nothing downstream mistakes it.

*This also corrects the country page of 2026-09-04, which read "210 of 239 carry
the file's regeneration date". That was true then; the file has regenerated
since and those dates did not move.*

## `--limit` takes the head, and the head is the stalest

```
list --fetch --live --limit 5    kept 0, expired 5
entries 0 / 60 / 120 / 180 / 238  4 live of 5
```

**The first rows of this file are its oldest advertisements**, so truncating
reads exactly the wrong end. *The adapter says so on every run that uses
`--limit`.*

**This card nearly said the opposite.** *The first two advertisements read were
adjacent in the file and both expired, which suggested a frozen archive of dead
ads. A spread sample refuted it.* **Two adjacent rows are not a sample** — the
defect `jobsbotswana.md` already carries, reproduced here before it was caught.

## Shapes read before the adapter was written

| field | shape here | on `kumarijob.com` |
| :-- | :-- | :-- |
| `employmentType` | **a list** — `["FULL_TIME"]` | a string, in two spellings |
| `datePosted` | full ISO with milliseconds | a bare date |
| `validThrough` | present 5 of 5 | present 3 of 3 |
| `baseSalary` | absent 5 of 5 | absent 3 of 3 |

*The page ships more than one `ld+json` block and four occurrences of the word
`JobPosting`; `posting_on()` skips a block it cannot parse rather than giving up
on the page.*

## What this card does not establish

- **no rate.** *239 is a stock read once. The sitemap's own dates cannot give a
  flow here, which is the whole point of the section above.*
- **nothing about the tenders' content** — 15 940 entries were counted and
  none was opened.
- **nothing about the other two Nepali boards.** *`merorojgari.com` is open and
  unadapted, an archive of 1 766 on 2026-09-04. `jobsnepal.com` REFUSES as of
  2026-09-07 — `allowed=False`, `certain` — where that same page measured it
  open.*
