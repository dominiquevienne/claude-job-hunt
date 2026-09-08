# Board adapter — Zaposli.ME (Montenegro)

<!-- verified: 2026-09-08 -->

<!-- hosts: zaposli.me -->
<!-- host-forms: zaposli.me -->
<!-- host-forms-basis: read — `zaposli.py:BASE` is a literal; `www.zaposli.me` answers under the bare name · 2026-09-08 -->
<!-- script: zaposli.py -->
<!-- countries: ME -->
<!-- content: measured · 423 advertisements under `/posao/` in `sitemap/oglasi.xml`, raw 423 / distinct 423, 0 duplicates; the sibling `pretrage.xml` holds 311 facet URLs and is set aside; 0 `JobPosting` on 4 of 4 advertisements read · 2026-09-08 -->
<!-- witness: served by the site — its own listing states «&nbsp;Svi poslovi (423)&nbsp;» against 423 in the sitemap, agreeing to the unit. **Both numbers come from the same host**, so this corroborates the site with itself, not the count with a second source · 2026-09-08 -->
<!-- hosts-source: named rank 9 of Montenegro by the country page of 2026-09-04, which recorded 433 then · 2026-09-08 -->

**Montenegro's larger of two current stocks, and the first board here read
without `ld+json` since `ofertapune`.**

## The path sorts, and here the explicit word is on the WRONG side

```
sitemap/oglasi.xml     423 <loc>   all under /posao/              ADVERTISEMENTS
sitemap/pretrage.xml   311 <loc>   all under /oglasi-za-posao/    FACETS
```

> **`oglasi-za-posao` means «&nbsp;job advertisements&nbsp;». It is the FACET
> path. The advertisements sit under `posao` — «&nbsp;job&nbsp;» — which says
> less.** *A substring filter on the more explicit word would keep exactly the
> wrong 311.*

**Fifth board where the path decides and the first where the most explicit word
is on the wrong side.** *And it sharpens the rule rather than confirming it:*

> **The path sorts because the TWO files were compared, not because a path can
> be read.** *`shared/robots-policy.md` §7 says the path is what to try first;
> this card is why it is not a rule you apply to one file alone.*

**The child addresses are under `/sitemap/`, not at the root.** *Composing
`/oglasi.xml` from the name would have fetched nothing — the index was read
instead of guessed.*

## The dates: three quantities, and the one that was missing was on another page

```
sitemap <lastmod>        distinct per ad, 22 values, 2026-07-30 -> 2026-09-07
the ADVERTISEMENT page   «&nbsp;10. septembar 2026&nbsp;»  = the DEADLINE
the LISTING page         «&nbsp;01. septembar 2026&nbsp;»  = the posting date
```

**The deadline reading is established by the site's own countdown**, not
inferred: *«&nbsp;ističe prekosjutra&nbsp;» — expires the day after tomorrow —
beside 10 September, read on 8 September; and «&nbsp;ističe za 22 dana&nbsp;»
beside 30 September.*

**This card first concluded that the sitemap dates were «&nbsp;unverifiable,
because the site publishes no posting date&nbsp;». That was wrong, and the
reason is worth keeping: only the ADVERTISEMENT page had been read.** *The
listing pages carry a posting date per advertisement, and they were one fetch
away.*

### Compared over ten advertisements

```
identical to the sitemap's lastmod   7
one day later                        1
three days later                     2
earlier than the lastmod             0
```

**So the sitemap date is the posting date on 7 of 10, and the listing date is
never EARLIER.** *That is consistent with `lastmod` being first publication and
the listing showing a later bump, and this card does not claim more: no
mechanism was measured, only the two columns.*

**Ten advertisements from one city facet is a small and unspread sample**, and
the count is stated rather than the conclusion widened.

## What it does not serve

**Zero `JobPosting` on 4 of 4 advertisements read.** *Two `ld+json` blocks, and
they are `Organization` and `WebSite`.*

**So an adapter here must parse HTML** — title, employer, «&nbsp;Cetinje, Crna
Gora&nbsp;» and the deadline all sit in plain text — **and parse Montenegrin
month names**: `januar … avgust, septembar … decembar`.

### Four anchors, counted before they were trusted

```
title      <h1 class="… fw-semi-bold …">      the SECOND h1 on the page
town       the span after `mdi-location-enter`
deadline   the span after `mdi-calendar`
employer   <h4 class="… mb-1 …">
```

**Each was counted on three advertisements first: exactly one match each, on
all three.**

> **The first `<h1>` is the page banner — «&nbsp;Oglasi za posao&nbsp;» —
> identical on every advertisement.** *An extractor anchored on "the h1"
> returns the banner 423 times and looks like a working adapter.*

**The twelve Montenegrin months are exercised, and five non-dates must return
`None`** — *`ihararejobs` showed that four abbreviations carry a full stop and
one is four letters long, and a `%b` parse read none of its last six months.*

**And the negative control is PRINTED, not swallowed.** *`ofertapune` cost 481
unreadable of 481 to a motif too narrow and it was seen only because the guard
printed what it could not read.* **With no structured data there is no safe
silence: every advertisement missing a field is named on stderr with the field,
and the line prints whether or not anything failed.**

### `--since` is answered from the listing, and this is the only board of seven

**The sitemap date is per-advertisement here, and never LATER than the date the
site shows.** *So the filter keeps an advertisement the site would date later
and never drops one it would date earlier — that asymmetry is the whole reason
it is safe without `--fetch`.*

## Access

`zaposli.me` answers `read` and permits `/`, `/sitemap.xml`, both children,
`/posao/…` and `/oglasi-za-posao/…` — `allowed=True`, `certain=True`, group
`*`, measured 2026-09-08. `www.zaposli.me` answers under the bare name.

**And 368 of these 423 addresses were unreachable by this repository's own
fetcher until 2026-09-08.** *Montenegrin slugs carry `ž`, `č`, `š`, `ć`, `đ`;
`bin/fetch-body.py` passed the raw URL to `urllib`, which raises on non-ASCII.
**87 % of this board** was invisible to `bin/fetch-body.py`, the fetcher every
adapter here goes through — fixed in `786e234`, and this card is the case that found it.*

## What this card does not establish

- **nothing about `prekoveze.me`**, Montenegro's other current stock — 250
  advertisements on 2026-09-04, not re-measured here;
- **no rate.** *423 is a stock read once, and the country page recorded 433 on
  2026-09-04: the board moved by ten in four days and neither reading is a
  flow;*
- **nothing about `berzarada.me`**, whose `robots.txt` is an HTML error page on
  both forms of the host — `unrecognised`, `certain=False`.
