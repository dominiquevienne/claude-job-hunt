# Board adapter — JobIvoire (Côte d'Ivoire)

<!-- verified: 2026-09-03 -->
<!-- hosts: www.jobivoire.ci, jobivoire.ci -->
<!-- siblings: jobivoire.ci 2026-09-04 agree -->
<!-- script: jobivoire.py -->
<!-- countries: CI -->

`robots.txt` is two lines and closes nothing: `User-agent: *` and a bare
`Disallow:`. **It declares no sitemap, and the one that exists must not be
used.**

```
GET /job?page=<n>        → 12 advertisement links; 324 pages
GET /job/details/<slug>  → one advertisement, with a clean JobPosting
```

## The sitemap is a trap — this is why the adapter paginates

```
/sitemap.xml    311 <loc>, of which 227 under /job/details/
                newest lastmod  2026-07-28
/job?page=N     324 pages: 323 × 12 + 8 = 3 884 advertisements
```

**227 of 3 884 — six per cent — and the freshest entry is five weeks old**,
while the listing publishes twelve advertisements dated today. An adapter
written on it would miss **94% of the board and never meet an error**: 200s
all the way, a plausible count, nothing to catch.

**`emploitic.md` is the opposite case** — its sitemap is declared in
`robots.txt` and current to the minute, and that adapter uses it. **Two
neighbouring boards, two opposite routes, each measured.**

## The pagination was checked, not assumed

Pages 1, 2, 200 and 324: **12, 12, 12 and 8 links, zero overlap between any
pair**, and page 325 returns none. `323 × 12 + 8 = 3 884` exactly.

## The listing's `ld+json` arrives broken and is repaired by the shared reader

The listing carries one block naming twelve `JobPosting`s, and it is invalid
JSON — a title reads `d\&#039;Atelier`, a **backslash before an HTML entity**,
which is not an escape. `json.loads` refuses it with or without
`strict=False`.

`_ldjson` mends that one malformation (#127) and unwraps the `CollectionPage`
→ `mainEntity` → `ItemList` it sits in, so `postings()` returns the twelve.
**Two occurrences on two continents** — Michael Page's literal newline and
this — **suggest a class rather than an accident: a publisher that escapes one
layer too many.**

**`absent_reason()` caught this before the repair existed**, reporting
`unparseable` with `our_fault=True`, on two independent sessions the same
evening. **The repair does not turn that off** — `repairs()` counts mended
blocks so a run can say so, and anything it cannot fix is still reported.

**The links still come from the markup and the fields from each advertisement
page.** The listing's twelve postings carry **no `url`** — three `url` fields
for twelve postings, none an advertisement — so pairing them to slugs would
rest on the block's order matching the markup's. **That is not verified, so it
is not done.** It would cut the board from 4 208 requests to 324, and it is
the first thing to measure if that cost matters.

## Two fields that do not hold what their names say

**`hiringOrganization` is never the employer.** It reads
`Employeur via JobIvoire.ci` on **12 of 12** sampled, with `sameAs` pointing
at the board itself. **The real employer appears inside the description
text.** The card emits `company: null` and
`company_field_is_the_board_placeholder: true` rather than passing the board's
own name off as an employer.

**The description is a teaser**, not the advertisement — 153 to 158 characters,
**0 of 12 over 200** — and its entities are escaped twice, so `l&#039;offre`
reaches the field as text. Unescaped to a fixed point, as in `employtt.py`.

## Cost

`--urls-only` is one request per page — 324 for the board. Reading the fields
is one request per advertisement on top.
