# Board adapter — Go Zambia Jobs (Zambia)

<!-- verified: 2026-09-07 -->

<!-- hosts: www.gozambiajobs.com, gozambiajobs.com -->
<!-- script: gozambiajobs.py -->
<!-- countries: ZM -->
<!-- content: measured · 358 advertisements in `sitemap-jobs-1.xml`, raw 358 / distinct 358, 0 duplicates, JobPosting on 10 of a random 10 · 2026-09-07T14:00:13Z -->
<!-- witness: none found — the site serves no global counter, and the homepage facets are a partition that is not exhaustive; see below · 2026-09-07 -->
<!-- host-forms: gozambiajobs.com, www.gozambiajobs.com -->
<!-- host-forms-basis: read — `gozambiajobs.py:APEX` fetches the apex for every advertisement, and the index that names them is served from `www`; the two are guarded separately · 2026-09-07 -->
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

**Write `358 advertisements at 2026-09-07T14:00:13Z` and never a rate.**

## Re-measured 2026-09-07, and two of this card's conclusions move

**368 became 358. The file LOST ten entries in two days.**

```
2026-09-05T11:45:51Z   368 <loc>   32 339 o   md5 f70bcf9c3174
2026-09-07T14:00:13Z   358 <loc>   31 609 o   md5 f455257b4b04
```

**So it is not an archive that only grows: advertisements leave it.** The
card's own question — *stock or flow?* — was called undecidable; it is now
answered at least this far, and a total taken from this file is a reading at
an instant rather than a ceiling.

**And the second conclusion moves further.** This card recorded *"not one
`<lastmod>` in 368 entries"* and concluded that freshness could not be asked.
**That is true of the sitemap and false of the board:**

```
datePosted      2026-08-21T09:25:03.000000Z     10 of a random 10
validThrough    2026-09-20T09:25:03.000000Z     10 of a random 10
```

**The dates live one level down.** `--since` and `--live` both work, and both
need `--fetch` — a filter reading a field the sitemap does not carry would
silently return everything, which reads exactly like a board on which nothing
expires.

*The card was right about what it measured and wrong about what it concluded
from the absence. **An absence in one file is not an absence in the board.***

## What the adapter emits, and one field that is a decision

```
title · datePosted · validThrough · hiringOrganization
identifier · employmentType                            10/10
jobLocation                                             9/10
baseSalary                                              2/10
```

**`baseSalary` IS emitted here**, and that is a judgement about this board
rather than about the field: its currency is `ZMW` — the kwacha, which is
Zambia's — with real `minValue`/`maxValue` and a `unitText`. *On
`burundijobs.md` the same key reads `négociable XPF`, a Pacific franc in
Burundi, and is dropped.* **What a field is worth is a property of the
board.**

`identifier.value` is the numeric id that opens the URL, so `ledger_id` is the
board's own and not one the adapter invented.

## Procurement notices: five of 358, and the test was tuned against itself

`invitation-to-bid`, `tender-for-`, `request-for-proposal`,
`call-for-expression-of-interest`.

**The first version of the pattern matched `procurement` and caught two
`procurement-manager` postings — real vacancies, one in four of its hits.**
The word was removed and both are spared, checked in both directions. They are
counted and reported; `--jobs-only` drops them and is never the default.

## The Zambian overlap, attempted 2026-09-07 — a FLOOR, not a count

**Three boards, three list invocations, no advertisement opened.**

```
gozambiajobs  357        jobsearchzm  160        jobzambia  45
raw sum 562              intersection: see below
```

*The counts moved again while this was written: 357 here against 358 an hour
earlier and 368 two days before; `jobsearchzm` reads 160 against the 153 on
its own card. **Three boards that move, so this is dated to the hour.***

### There is no shared identifier, and the only available key is title-derived

Each adapter emits an id in **its own** namespace — `gozambiajobs:<numeric>`,
`jobsearchzm:<slug>`, `jobzambia:<slug>` — and no board declares another's
row. Without opening 562 pages there is no employer field either. **What
remains is the slug, and a slug is made from the title.**

**So this is not an identifier comparison and it is not fuzzy matching
either**: it is exact equality of the full slug, after stripping the numeric
prefix `gozambiajobs` puts in front of its own.

### The key's limit is measured inside one board, which settles it

```
slugs carried by MORE THAN ONE gozambiajobs advertisement : 28
    accountant ×5 · multiple-positions ×4 · security-guards ×3 · chef ×3
```

**A title-derived key is demonstrably not an advertisement identifier — not
even within a single board.** *The weight of a match is the improbability of
the string, exactly as a shared 25-byte refusal body says less than a shared
1 836-byte rules file.*

### What the key finds, weighed one by one

```
jobsearchzm ∩ gozambiajobs   5 matches
    senior-infrastructure-engineer-improving-access-activity      56 ch · 1:1
    senior-programs-officer-entrepreneurship-and-graduate-…       67 ch · 1:1
    finance-and-administration-assistant-front-office-manager     57 ch · 1:1
    environmental-social-specialist                               31 ch · 1:1
    legal-company-secretary                                       23 ch · 1:1  <- short
jobzambia   ∩ gozambiajobs   1 match
    multiple-positions                                            18 ch · 1:4  <- AMBIGUOUS
jobsearchzm ∩ jobzambia      0
triple                        0
```

**`multiple-positions` matches one `jobzambia` advertisement against four
distinct `gozambiajobs` ones. That is not an intersection, it is a generic
label**, and it is the negative control this measurement needed.

### The number, with the direction of its error

> **At least four advertisements are shared between `jobsearchzm` and
> `gozambiajobs`. Nothing is established between `jobzambia` and either.**

**Four is a FLOOR.** The key can only see an overlap when two boards slugify
the *same title text*; the same vacancy posted under differently-worded
titles is invisible to it. **So the true overlap is ≥ 4 and its ceiling is
unknown**, and `562 − 4 = 558` is an **upper** bound on the union, never the
union.

*What this does establish: the three are not each other's mirrors. What it
does not: any rate, any percentage, any statement that the overlap is small.*
**Measuring it properly costs 562 page fetches for the employer field, and
that price is the finding too.**

## What this adds that `jobsearchzm` does not — unmeasured, and named as such

**Zambia already has `jobsearchzm.md` (153 advertisements) and
`jobzambia.md` (45).** This board is larger than both together, and **the
overlap between them has not been measured.** *Two boards of one country are
not two markets until somebody counts the intersection*, and until then
`358 + 153 + 45` is a sum of three readings and not a count of Zambian
vacancies.

**This card's own line about `jobsearchzm.com` being "not counted" is now out
of date**: it has had an adapter since 2026-09-05.

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

*`verified:` corrected 2026-09-08 from 2026-09-05 to 2026-09-07 (#188-adjacent guard): this card's `content:` carries a measurement of 2026-09-07 and the commit that wrote it exercised the host, so the card's age was understated. **The measurement was right and the header was behind** — `adapter-age.sh` was filing it older than it is.*
