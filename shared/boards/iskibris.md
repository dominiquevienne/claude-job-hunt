# Board measurement — İş Kıbrıs (`www.iskibris.com`, Northern Cyprus): the reference portal, and **its two lists of facets have the SAME SIZE and DIFFERENT MEMBERS** — sitemap 12, home page 12, intersection 6, union 18. The adverts are on neither the sitemap nor `/jobs` but on `/quick-links/<slug>`, whose pager is CLAMPED. Adapter `iskibris.py` (#719)

<!-- verified: 2026-10-01 -->

<!-- hosts: www.iskibris.com -->
<!-- script: iskibris.py -->
<!-- countries: CYN -->
<!-- route: http -->
<!-- content: measured · **the root (200, 112 950 B, md5 cbd1b1e54d58 identical on two reads) is a Next.js app rendered on the server (`/_next/static`, MUI): 12 sector cards each with «N iş ilanı» (40, 9, 43, 43, 44, 33, 24, 16, 2, 55, 2, 4 — sum 315, a sum of sector counters and not a stated total), `/jobs`, one `/jobs/25824`, quick-links `/quick-links/jobs-in-nicosia|kyrenia|magusa|iskele|guzelyurt|lefke`; no JobPosting; `_robots.allowed('www.iskibris.com','/')` → open, certain** · 2026-09-18 -->
<!-- witness: the front's own sector counters, summing to 315 (a sum, not the site's total) · 2026-09-18 -->
<!-- content: measured · **the adverts are on NEITHER the sitemap NOR `/jobs`: the rules file is served (`state: read`, `certain: True`) with `Allow: /*` and **no Crawl-delay** — 2 s are ours, and the API host writes none either; `/sitemap.txt` (200, 893 B, 20 lines) holds ZERO `/jobs/<id>`, and `/jobs` (200 ×2, 79 431 / 79 443 B — a generated MUI class name moves) ships `pageProps` with only an empty `query`, so counting links there returns zero about the markup and nothing about the board. They live in `/quick-links/<slug>`, server-rendered with a Laravel paginator (`data`, `total`, `per_page` 24, `last_page`, `current_page`). THE TWO LISTS OF SLUGS HAVE THE SAME SIZE AND DIFFERENT MEMBERS: sitemap 12 (6 sectors + 6 districts), home-page `jobsStats` 12 (the same 6 sectors + education, health, internship, mass-media, part-time, student) — intersection 6, union 18. THE PAGER IS CLAMPED: `?page=2` returns `current_page: 1` with identical ids. `api.iskibris.com`, which `next_page_url` names, serves its own rules (open, certain) and answers 403, 1 558 B, md5 46e4fde5d0ba IDENTICAL twice — a stable fingerprint, so a bare application refusal and not a challenge; never called** · 2026-10-01 -->
<!-- witness: per facet, its own stated `total` against what it served — 187 distinct adverts over 18 facets, 9 facets short by 312 in all (the clamp). NO board total: the home-page counters summed 315 on 2026-09-18 and 301 on 2026-10-01 but count overlapping facets; and the districts, the one family that could carry a total, measured 0 adverts under two and 98 under none — BOTH figures downstream of the clamp, so neither settles it · 2026-10-01 -->

## Adapter delivered 2026-10-01 — and the route is the union of two facet lists

```
iskibris.py jobs --country-code CY
  -> 187 distinct advert(s) emitted over 18 facet(s)
  -> sitemap names 12, home page counts 12, 6 in common, 18 distinct
  -> 9 facet(s) served fewer than they state, 312 short — THE PAGER IS CLAMPED
```

**Twelve against twelve is the most seductive form of the same-cardinal trap.** *On Lambda (#661) it
was 50 against 30, which at least looked like two different things; here the two lists are the same
SIZE, which reads as agreement.* They are not: six district pages exist only in the sitemap, and six
facets (`education`, `health`, `internship`, `mass-media-communication`, `part-time`, `student`) only
in the home page's counters. **Walking either alone loses what the other serves**, and no count would
have shown it — only intersecting the slugs did.

**The pager is clamped.** `/quick-links/<slug>?page=2` returns `current_page: 1` and the identical 24
ids, because the page's `getServerSideProps` forwards only the slug to the API. *So the HTML route
carries the first page of each facet and no more*, and the run says how far short of each stated
total it fell rather than looping on a pager that cannot advance.

**The remainder is on `api.iskibris.com`, and that host is not defeated.** `next_page_url` names it;
it serves its own rules file (open, `certain: True`, no `Disallow`) and the application answers
**403, 1 558 B, md5 `46e4fde5d0ba` identical on two reads**. *A STABLE fingerprint is the
discriminant: this is a bare application refusal, not an anti-robot challenge*, so borne 2 is not
engaged — and on an API host a blocked entry is technical, which is not ours to adjudicate. The
adapter refuses the host in code and never calls it.

### No board total, and the reason is measured rather than asserted

The home page's twelve counters summed to **315** on 2026-09-18 and **301** on 2026-10-01 — but they
count *facets*: `sales-jobs` is a sector, `part-time-jobs` an employment type, `jobs-in-kyrenia` a
district, so one advert is counted by several. *A sum over overlapping facets counts nothing.*
**Measured: 77 of 187 adverts were served by more than one facet.**

The districts are the one family that could carry a total, and they do not: **0 adverts appeared
under two districts, 98 under none.** *That reads as «disjoint but not exhaustive» — and the clamp
forbids concluding it:* an advert past position 24 of its district page is invisible to this route,
so «under no district» is inflated and the zero cannot establish disjointness. **A witness downstream
of a filter cannot see the filter**, and only the API host could settle either.

### Two defects fixed before shipping, both of which read like measurements

- **`--max 6` emitted 23.** The cap was tested only between facets, so the first facet ran to its end.
- **And the shortfall note then claimed «42 short»** — *a false witness manufactured by our own
  option*, indistinguishable in the output from a measured shortfall. Under `--max` the run now
  states nothing about what the facets serve.

**Found by the Northern Cyprus search of #606 (a country never searched),
measured 2026-09-18 07:20–07:22 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #606: two searches in Turkish naming the Labour Department and the
private boards, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('www.iskibris.com', '/')   open
GET https://www.iskibris.com/   200 ×2 — see the content line
```

The adapter's first line: `/jobs` and its pager (server-rendered or the Next data route), the ad `/jobs/<id>`, the stated total if `/jobs` states one beside the emitted count.
