# Board adapter — MyJobsFiji (Fiji)

<!-- verified: 2026-09-07 -->

<!-- hosts: myjobsfiji.com -->
<!-- host-forms: myjobsfiji.com -->
<!-- host-forms-basis: read — `myjobsfiji.py:BASE`, a single literal; `www.` serves the same rules and is never fetched · 2026-09-07 -->
<!-- script: myjobsfiji.py -->
<!-- countries: FJ SB -->
<!-- countries-basis: measured — `FJ` from the board's jurisdiction, `SB` because 1 of 10 sampled advertisements declares `addressCountry: "Solomon Islands"` and the adapter reads the country from the advertisement rather than the board · 2026-09-07 -->
<!-- content: measured · 190 advertisements inside a sitemap of 3 152 URLs; the other 2 962 are 2 790 company pages, 45 blog posts, 37 categories, 34 job-search pages, 23 cities, 14 states, 11 countries and 8 more · 2026-09-07 -->
<!-- witness: none published by the site; 190 is the count of `/job/<id>/<slug>/` entries in its own sitemap, and Fiji's country page recorded 224 on 2026-09-04 · 2026-09-07 -->

**Fiji's first adapter**, and the widest gap this repository has measured
between a sitemap's length and a board's size.

## 3 152 URLs, 190 advertisements

```
/company/…   2 790      /categories/…   37      /countries/…   11
/job/…         190      /jobs/…         34      /cities/…      23
/blog/…         45      /states/…       14      other            8
```

**Counting the file would report the board 16.6 times larger.** *`jobsbotswana`
was 368 against 367 and `ihararejobs` 6 503 against 6 295; here the excess is
not noise, it is a directory of employers* — and it is the majority of the
file, which is what makes the mistake easy rather than careless.

**190 today against 224 recorded on 2026-09-04.** Both are counts of the same
thing three days apart; neither is a correction of the other.

## The sitemap's `lastmod` is one value, and it is today

**All 3 152 entries carry `2026-09-07`.** A single distinct value across the
whole file: it stamps the file's regeneration, not anything's publication.
Fiji's country page recorded this on 2026-09-04 and it is unchanged.

**So `--since` is refused on the sitemap** and offered only with `--fetch`,
where it filters `datePosted` from the advertisement's own schema — real and
spread, eight distinct days across ten sampled, 2026-08-16 to 2026-09-05.

> **This is the second board measured on 2026-09-07 whose sitemap date says
> nothing, and the two say nothing for different reasons.**

*`ihararejobs` moves its dates when a page is read; this one stamps every row
with one rebuild.* **A `lastmod` is not evidence of anything until it has been
looked at** — and the two failure modes need different tests, so neither
check would have caught the other board.

## The schema is complete, and one of its fields is not

```
datePosted      10/10      validThrough              10/10
employmentType  10/10      hiringOrganization.name   10/10
strict JSON     10/10      baseSalary.value.minValue  1/10
```

`strict` parsed all ten — no lax pass needed here, unlike `ihararejobs` at six
of eight. **The count is reported on every `--fetch` rather than assumed
stable.**

**`baseSalary` is present on every advertisement and empty on nine of ten**,
and the empty ones carry `unitText: "YEAR"` beside no value at all. *A reader
that emitted the object would hand a consumer a yearly salary structure
containing nothing* — worse than absence, because it looks like a schema that
was filled in.

**The one filled example is correct**: `6.10` with `unitText: "HOUR"`, a
Fijian hourly wage. So `salary_fjd_min` / `salary_fjd_max` are emitted only
when non-empty, with `salary_unit_text` beside them.

### A claim this card nearly carried, and how it fell

An earlier draft said the filled row read `6.10` against `YEAR` and called it
*«an hourly rate under a yearly label»* — a tidy finding, and false. **The
`YEAR` came from an empty record and the `6.10` from a different
advertisement.** *Two records, one conclusion.*

**It fell because the salary branch was exercised rather than re-read**: the
first advertisement tried carried no salary at all, so the branch had not
fired, and running it on the one that does printed `HOUR`.

## The board is Fijian and some advertisements are not

**One of ten sampled is a UNICEF post in Honiara, `addressCountry: "Solomon
Islands"`.** A country taken from the board rather than the advertisement
would file it under Fiji.

So `countries` is read from the advertisement under `--fetch`, with
`country_name` verbatim beside it. **A country name the module has no code for
yields an empty `countries` and says why** — an empty list is honest, a wrong
ISO code is not, and a name-to-ISO table that grows by guessing is how a row
ends up in the wrong jurisdiction.

Without `--fetch` no country has been read at all, and the rows carry the
board's own jurisdiction with `country_basis` saying exactly that.

## What was exercised, 2026-09-07

```
list                                190 ads · 2 962 other · lastmod ["2026-09-07"]
list --since without --fetch        exit 2, and it says why
list --live  without --fetch        exit 2
list --fetch --limit 4              4 read · 4 kept · 0 unreadable · 0 lax
list --fetch --limit 4 --since 2027-01-01     4 read · 0 kept · 4 dropped
ad 51471 education-officer          Honiara · Solomon Islands · ["SB"]
ad 51290 sawmill-worker             salary_fjd_min 6.10 · unit HOUR
ad 999999 pas-une-annonce           exit 3
```

**Fiji's three other named hosts are not covered here.** `ejobsfiji.com` is
open with 14 advertisements; `sptojobslink.com` serves the 25-byte
`Your request was blocked.` body — **in HTTP 200**, which is the one place a
status-code check cannot see it; `fiji.gov.fj` is indeterminate and was not
probed.
