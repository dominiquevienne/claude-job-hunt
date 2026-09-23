# Board measurement — HireLebanese (`www.hirelebanese.com`, Lebanon): «Find Jobs / Browse Jobs / Advanced Job Search» — **3 232 adverts emitted against the 3 232 the board states, and the 41 location counts it states are the 41 the rows give**, over 65 pages of a plain GET; `hirelebanese.py` — Lebanon's first adapter, and the board is not only Lebanese

<!-- verified: 2026-09-23 -->

<!-- hosts: www.hirelebanese.com -->
<!-- script: hirelebanese.py -->
<!-- countries: LB -->
<!-- route: http · 3232 · 2026-09-23 -->
<!-- content: measured · **3 232 emitted against the stated «Job Posts 3201 - 3232 of 3232 Results Found», over 65 pages of 50 by a plain GET** (`searchresults.aspx?order=date&…&pg=N`; no POST and no ViewState — those belong to the search form at `/jobsearch.aspx`, not to the browse route). **Every page states its window, so the walk is checked at each page**: the first index must be the pager's own arithmetic, and the total must not move. **And the 41 location counts the site states are the 41 the rows give** — the facets sum to 3 232, the stated total, so they PARTITION the board and «Lebanon» (1 955) and «Lebanon - Beirut» (916) are siblings, not parent and child. 3 232 distinct ids, 750 employers, filed 2026-06-24 → 2026-09-23; 33 featured; Lebanon 1 955, Beirut 916, Tripoli 63, Bekaa 36, and non-Lebanese postings — Iraq 31, Congo 29. Browse page 200 ×2 (110 865 B, md5 25e3856878b4); results page 200 ×2 (39 583 B, md5 5dab6fb7a558). Exercised 2026-09-23: `jobs --country-code LB` → **3 232 emitted, they agree, 41 of 41 places agree** · 2026-09-23 -->
<!-- witness: the page's own window «A - B of T» on EVERY page, and the site's own count per location, both checked against the rows on every unfiltered run · 2026-09-23 -->

**Found by the Lebanon search of #609 (a country never searched), measured
2026-09-17 13:53–13:55 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads, two public resolvers on a DNS
negative.** The method is written on #609: one search naming the boards,
the National Employment Office (ILO and UNESCWA name its e-labour
exchange at `neo.gov.lb`) and the regional aggregators (Bayt — already
`bayt.md`; Naukrigulf, Tanqeeb — regional, left aside), no composed host
names. *A measurement, not an adapter.*

```
_robots.allowed('www.hirelebanese.com', '/jobsearch.aspx')   open, certain
GET https://www.hirelebanese.com/jobsearch.aspx               200 ×2, identical — a WebForms search form, /jseeker/findjobhome.aspx to browse
```

**The search is a POST with a ViewState** — not a URL the plugin replays;
whether «Browse Jobs» lists by GET is the adapter's first line (its
`adapter` issue).

## The route, found 2026-09-22 — and what the next session should not assume

**The walk is a GET.** `searchresults.aspx?order=date&keywords=&category=&type=&duration=&country=&state=&city=&emp=&pg=N` is what the page's own «Next» and «Last» links carry, 50 adverts a page, **65 pages**. The card's earlier note — «an ASP.NET WebForms board, a search by POST» — describes the **search form** at `/jobsearch.aspx`, which is not the road to the board: the browse route needs neither a POST nor a `__VIEWSTATE`.

**Three witnesses, and none of them is ours.** The results page states its total *and* its window («1 - 50 of 3210»), so a walk can be checked at every page rather than once at the end; and the browse page states counts **by location, by sector and by company**, which is the discriminant a total cannot be — *an extraction that drops five rows and doubles five others still states 3 210.*

> **But the location counts must NOT be summed.** They carry «Lebanon (1951)» *and* «Lebanon - Beirut (901)», «Lebanon - Tripoli (63)», «Lebanon - Bekaa (34)», «Lebanon - Saidon (12)» side by side, **and whether the sub-entries are inside the 1 951 or beside it is not established.** Adding them would be the subordination trap this repository has already paid for: two true numbers and a false relation between their denominators. *The next session settles it by asking the site — `country=` for one and the other — before writing any comparison.*

**And the board is not only Lebanese.** Its own location facets name Iraq (30), Congo (29), Ghana (26), Ivory Coast (12), Angola (7) and a dozen more, so `--country-code` must STAMP and the country a record carries is the one the row prints («employer - country»), never one we assume from the host.

*Measured, not built: this is the first line of #657 done, deposited so it is not rediscovered. No adapter was written — the session that took it stopped at its budget floor and said so.*

## The adapter, 2026-09-23

```
hirelebanese.py jobs [--country-id N] [--since YYYY-MM-DD] [--country-code LB] [--max-pages N]
hirelebanese.py locations
```

**3 232 emitted against the 3 232 the board states, and 41 of 41 location counts
agree.** 65 pages, one request each, plus one for the facets.

**Two witnesses, and neither is ours.** Every page states «Job Posts A - B of T»,
so the walk is checked **at each page** — `A` must be the pager's own arithmetic,
and a page whose window starts elsewhere ends the walk rather than being emitted
as if it were in place. *A total compared once at the end cannot say WHERE a walk
went wrong.* And the browse page states a count per location, which is the
discriminant a total cannot be.

### Two defects the witnesses caught, and what each turned out to be

**A featured advert hid from the parser, and the per-page window said so.** The
board sells the placement (`panel-heading featured-job-color`) and puts a star
image **between `<h4>` and the link**; a pattern requiring them adjacent dropped
one panel on **eighteen pages** — 3 199 read against a stated 3 232. *The thing
that hid the adverts turned out to name a field worth carrying*: `featured` is
emitted only when set, 33 of 3 232 on the day.

**Then the total agreed and a field was still wrong.** With 3 232 = 3 232 exact,
the per-place comparison still showed `Democratic Republic: site 3, read 0` and
fourteen rows with no place. **The page cuts its facet labels at twenty
characters** while the rows print the full names — «United Arab Emirates -
Dubai», «Democratic Republic of the Congo», «United States - Wyoming». *A total
that matches can sit on top of a field read wrong; only the place-by-place
comparison could see it.*

**And the cut hid one more turn, inside our own instrument.** One label's
twentieth character is a **space** — `'Democratic Republic '`. The extracting
pattern trimmed it (`\s*([^<]+?)\s*`) and the parser trimmed it again, so it
measured nineteen and stopped looking truncated. **The normalisation was erasing
the thing being measured.** The length is now taken on the label as written, and
the pattern captures it raw. *Same family as the `rstrip()` that once reproduced
three «different» fingerprints exactly.*

**Three ids collapse onto one label.** «United Arab Emirates» is the twenty-character
label of three different facets, so the site's counts are **summed per label**:
our rows carry the label, not the id, and telling the three apart would invent a
distinction the page does not expose. *The record keeps the row's own words
(«United Arab Emirates - Dubai»); the label only buckets it for the count, and
the two are never conflated.*

**The place is read by the site's own vocabulary, not by a separator** — a row
prints «employer - place» and the place itself carries « - », so «shareQ -
Lebanon - Beirut» splits on the longest label it ends with, never on the last
dash. A tail matching none keeps the whole string as the employer, place null
**and counted** (0 on the day).

**WITHHELD:** e-mail addresses and telephone numbers at a threshold of nine
digits, `contacts_withheld` on every record, **0 leaks measured on the 3 232**.
The advert page is never fetched — the panel carries the board's own excerpt,
`detail_read: false` — and `/jseeker/login.aspx` is refused before the gate.

`--country-code` STAMPS: the board carries postings from Iraq, Congo, Ghana,
Ivory Coast and a dozen more, so the place a record holds is the one its row
prints and never one assumed from the host.
