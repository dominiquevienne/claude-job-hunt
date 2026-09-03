# Board adapter — JobIvoire (Côte d'Ivoire)

<!-- verified: 2026-09-03 -->
<!-- hosts: www.jobivoire.ci, jobivoire.ci -->

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

## The listing's own `ld+json` does not parse; the advertisement's does

The listing carries one block naming twelve `JobPosting`s, and it is invalid
JSON — a title reads `d\&#039;Atelier`, a **backslash before an HTML entity**,
which is not an escape. `json.loads` refuses it with or without
`strict=False`.

So the adapter takes the links from the markup and the fields from each
advertisement page, where the block is well formed. **`_ldjson.absent_reason()`
reports the listing block as `unparseable` with `our_fault=True`**, which is
correct and is why nothing silently returns zero: *a page that says
`JobPosting` and yields none has been misread.*

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
