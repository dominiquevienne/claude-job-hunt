# Board adapter — JobIvoire (Côte d'Ivoire)

<!-- verified: 2026-09-08 -->
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

## The board moved its URL scheme, and the adapter reported an empty market

**On 2026-09-08 `search` returned ZERO** and printed its «&nbsp;a search that
matches nothing and a market that has nothing look identical from here&nbsp;»
line — **while already holding the fact that distinguishes them**:

```
[jobivoire] page 1: HTTP 404 — stopping.
[jobivoire] ZERO RESULTS for this search. **This is a finding, not an answer** …
```

> **The adapter knew the page was gone and its summary said the market might be
> empty.** *A 404 is not an absence of advertisements; the information existed
> one line above and did not reach the conclusion.*

**Three things had moved, and each hid the next:**

```
listing   /job?page=N        -> 404   |  /jobs?page=N        -> 200
ad links  /job/details/<id>              /job/<id>
ad URL    built inline at THREE call sites
```

*The site itself answered 200 with twelve advertisement links on its front
page throughout* — **the board never went quiet, one path moved.**

**The address is now built by `ad_url` in one place**, because a repair that is
per-call-site and whose datum is central has to be made three times or not at
all — and the usual way the second occurrence is found is by re-reading.
`tests/test_core.py::TheAdvertisementAddressIsBuiltInOnePlace` fails if a call
site rebuilds it, and reddens under exactly that mutation. **The reader accepts
both forms and the builder emits one**; a third form stops the adapter rather
than being swallowed.

## The volume, and the comparison this card refuses to make

```
2026-09-03   /job?page=N     324 pages, 323 x 12 + 8 = 3 884       (path now 404)
2026-09-08   /jobs?page=N      8 pages,   7 x 12 + 5 =    89
2026-09-08   /sitemap.xml    235 <loc>, of which        89 ads     0 under /job/details/
```

**Two independent instruments agree on 89 today** — the listing's own
pagination, which ends cleanly at page 8 (pages 9, 20 and 100 return the same
156 769-byte empty page), and the sitemap, which is a different mechanism
entirely. *That is corroboration; the two do not share a reader.*

> **What this card does NOT say is that the board fell from 3 884 to 89.** *The
> 3 884 was counted on a path that now answers 404, so the two figures have
> different provenances and no comparison between them is licit.* **Whether the
> old listing paginated over the same population is not established, and
> nothing measured here would settle it.**

**And the card's old warning has inverted**: it said the sitemap was a trap
holding 227 of 3 884 — six per cent. **Today the sitemap holds all 89**, and
its two `lastmod` dates are 2026-09-06 and 2026-09-07.
