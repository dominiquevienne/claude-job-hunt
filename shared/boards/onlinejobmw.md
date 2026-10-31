# Board measurement — Online Job Malawi (`onlinejobmw.com`, Malawi): «Job Vacancies | Online Job Vacancies» — a LIVE, server-rendered WordPress board whose job ads live under `/vacancies/SLUG/` and whose taxonomy declares 967 of them; the REST collection `/wp-json/wp/v2/vacancies` serves them 100 at a time but mixes FOUR categories, so only `?job-category=1` is job ads; rules open and no `Crawl-delay` written, yet the host answers 429 — remeasured 2026-10-30; no adapter yet — **and what follows is what it WAS on 2026-09-17, not what it is**: a WordPress board whose vacancies category is served to the declared client (396 KB, identical twice) with `/job-vacancies/`, a `/page/N/` pager and an RSS feed, rules open; no count stated; no adapter yet

<!-- verified: 2026-10-31 -->

<!-- hosts: onlinejobmw.com -->
<!-- script: onlinejobmw.py -->
<!-- countries: MW -->
<!-- content: measured · **AND THE ENUMERATOR CANNOT TELL A LIVE ADVERT FROM AN EXPIRED ONE — measured 2026-10-31 (#1222), one hour after the adapter was delivered.** An advert page carries a labelled `Expiry Date`; the REST record carries NO field of that kind, and all 100 records of the filtered page 1 are `status: publish`, so a uniform status separates nothing. **The median record of that page (id 13832, `captain`) states an expiry of 2026-10-30 and WAS STILL IN the collection on 2026-10-31: the collection is not filtered on expiry, and one specimen establishes that direction because a single expired record present proves it.** *The direction costs the CANDIDATE — a dead advert offered as a live one — so `list` emits what the host serves and claims nothing about availability.* NOT established: the RATE of expired adverts among the 967, which one specimen cannot give. The advert page also carries a labelled `Location` and `Company:`, and ZERO third-party contact inside the advert block against one address and four numbers elsewhere on the page — the operator's own, repeated by the layout · 2026-10-31 -->
<!-- content: measured · **ADAPTER DELIVERED 2026-10-31 (#676), AND THE FILTER IS THE ADAPTER.** `onlinejobmw.py` reads `/wp-json/wp/v2/job-category` first and matches the jobs term on its SLUG (`job_vacancies`) resolved at runtime — never by id, which belongs to this installation and happens to be the `1` a fresh WordPress hands to whatever was created first. The filtered collection ANSWERED: 200, 124 123 B, md5 `096dc56f303f`, 100 records, **every one of the 100 carrying the jobs term and no other**. The API is an ENUMERATOR and not a source of ad text — the record carries no `content`, no `excerpt` and no `meta` at all — so each row says `body_source: page` and the text lives under `/vacancies/<slug>/` · 2026-10-31 -->
<!-- witness: 967 · **the `job-category` term `job_vacancies` states `count: 967`, re-read on the object on 2026-10-31 and unchanged since 2026-10-30; the post type carries FOUR terms whose counts are 967 · 279 · 13 · 13, so 305 of its records are not advertisements and an unfiltered walk would emit them.** Their sum, 1 272, is NOT the board's size: a record may carry several terms and no total is stated anywhere. *Coincidence measured on both objects and not explained: `ntchito`, the other Malawi board here, sums its FOURTEEN terms to 1 272 as well.* · 2026-10-31 -->
<!-- witness: none — no contact is exposed on this route · **0 e-mail addresses in the whole 124 123-byte payload, and the record has no `meta` dictionary in which an application address could hide. So `contacts_exposed` is DERIVED from the record's own values at runtime rather than from a list borrowed from another board** — the day this host serves a field holding an address, the row says so by itself · 2026-10-31 -->
<!-- content: measured · **THE HOST ANSWERS AND THE BOARD GREW, and the 2026-09-17 line below is WRONG ON TWO POINTS.** `/job-category/job_vacancies/` 200, 415 037 B, md5 26340fea5d8c identical on two reads 8 s apart (17.09: 395 801 B, md5 f250998c379b); root 200, 370 986 B — not a parked domain. **(1) the ads live under `/vacancies/SLUG/`, never `/job-vacancies/SLUG/`: 0 of the latter in the served body, 10 of the former. (2) a count IS stated — by the TAXONOMY, not by the archive.** WordPress + Elementor + JetEngine, rendered SERVER-side: the titles sit in `jet-listing-dynamic-field__content` in the served HTML; 0 JobPosting, 1 ld+json (Organization, WebSite, BreadcrumbList, CollectionPage). REST: post type `vacancies`, rest_base `vacancies`, has_archive, taxonomy `job-category`; `/wp-json/wp/v2/vacancies?per_page=100` renders 100 records, newest first, 132 340 B. **TRAP FOR THE ADAPTER: that post type is NOT a job board — it carries FOUR terms (job_vacancies 967, edication_trainings 279, annoucements 13, tender_consultancy 13 = 1 272), and page 1 of the UNFILTERED collection is school-admission copy. The taxonomy filter is a condition of CORRECTNESS, not an optimisation.** · 2026-10-30 -->
<!-- witness: 967 · **the `job-category` term `job_vacancies` declares `count: 967`, and WP refuses `?job-category=1&per_page=100&page=11` with `rest_post_invalid_page_number` ("larger than the number of pages available"), so the filtered set holds at most 1 000: two facts the board states itself, and they agree. Neither comes from our extraction.** NOT established: a single 200 on the filtered route — the host began refusing first, so ZERO records of the 967 have been seen. · 2026-10-30 -->
<!-- content: measured · **`/job-category/job_vacancies/` (200, 395 801 B, md5 f250998c379b identical on two reads) is a WordPress category archive — posts under `/job-vacancies/`, a pager `/job-category/job_vacancies/page/N/`, a feed `/job-category/job_vacancies/feed/`; no count stated, no JobPosting; `_robots.allowed` → open, certain; the pager's end and the post not read** · 2026-09-17 -->
<!-- witness: none — the archive states no count · 2026-09-17 -->

**Remeasured 2026-10-30 19:17–19:22 UTC for #676, by the declared client, the guard
taken first on each exact URL in a turn of its own, `bin/fetch-body.py`, two reads of
the archive.** Guard: open and `certain`, `state: read` on all of `/`,
`/job-category/job_vacancies/`, its `/page/N/` and `/feed/`, `/vacancies/`,
`/sitemap.xml`, `/wp-json/...` and `www.onlinejobmw.com/` — group `*`, no rule, **no
`Crawl-delay`, and no sitemap declared**. *The 17.09 measurement stands as a measurement;
what it says about where the ads live does not.*

**AND THE HOST RATE-LIMITS WITHOUT EVER WRITING A DELAY: HTTP 429, 41 bytes, `Rate limit
exceeded. Please retry later.`** The first 429 arrived on the **12th request in 4 min
51 s** — 9 bodies, which the provenance records, plus 5 reads of `robots.txt`, derived
from `_robots._CACHE` keying on `(host, _FETCH)` inside one process, so one read per host
per guard turn. *A threshold is only ever learnt by crossing it, and crossing it once
gives one point and not a limit: nothing here says where it is.* **It was not re-probed —
a 429 on a list stops the retrieval — so the retrieval stopped with ZERO of the 967
records seen, and the filtered route carries no 200.** The next act therefore paces
itself: the 100-at-a-time page is the whole point of the REST route, 10 pages cover 967,
and that is **20 requests, not 10, and the line this replaces said 10**: `fetch-body.py` runs as a SUBPROCESS and takes its OWN guard, while `_robots._CACHE` keys on `(host, _FETCH)` inside one process — so every page is a fresh rules read plus a body. *This card had derived the per-process scope of that cache in the paragraph above and had not applied it to its own forward estimate.* An HTML `/page/N/` walk would need about 97 pages.

```
_robots.allowed('onlinejobmw.com', '/wp-json/wp/v2/vacancies')   open, certain, state read
GET /wp-json/wp/v2/types                      200    12 589 B — post type `vacancies`
GET /wp-json/wp/v2/job-category?per_page=100  200     2 713 B — the 967 witness
GET /wp-json/wp/v2/vacancies?per_page=100     200   132 340 B — 100 records, FOUR terms mixed
GET ...?job-category=1&per_page=100&page=11   400       146 B — beyond the last page
GET ...?job-category=1&per_page=100&page=1    429        41 B — the host had had enough
```

**Found by the Malawi search of #622 (a country never searched), measured
2026-09-17 16:49–16:52 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #622: one
search naming the national boards and aggregators, no composed host
names; no public employment service found online by that search. *A
measurement, not an adapter.*

```
_robots.allowed('onlinejobmw.com', '/job-category/job_vacancies/')   open, certain
GET https://onlinejobmw.com/job-category/job_vacancies/   200 ×2 — see the content line
```

**AND THE TOOLING NOW READS THIS CARD AS `indetermine`, FOR A CAUSE THAT IS FALSE:
`country-boards.refusal_of()` matches any prose line carrying a 403/429/451, and the line
it keeps is this card's own H1 — so the gloss a country page would print is «refus daté»
on 2026-09-17.** *This board refused nothing: it answered 200 on every path measured, and
the 429 is the trace of OUR cadence on 2026-10-30.* Measured by calling the function:
**22 of the 555 cards are `indetermine` through `refusal_of`, 19 of them on a 403
and 3 on a 429 — and one of those three is this card.** *CORRECTION OF 2026-10-31,
AND THE LINE THIS REPLACES SAID «15 … 13 on a 403 and 2 on a 429», WHICH WAS FALSE
BY ITS MEMBERS IN BOTH DIRECTIONS: it omitted `108-jobs`, whose retained line IS a
declared `content:` field reporting a real «Vercel Security Checkpoint» and which is
therefore classed RIGHTLY. The count was composed instead of being derived, which is
the fault this card documents, committed inside its own diagnosis.* Measured twice
independently — by the pilot on #1219 and by the coding session before writing this —
and concordant to the name. **AND THE DEFECT IS REPAIRED, 2026-10-31 (#1219): the
floor on `refusal_of()` is POSITIVE — only a DECLARED field is read — so the lines of
this very paragraph can carry a status without planting a refusal, which is the
property that was missing.** *Measured on the corpus: 103 cards lose the gloss, 5
move class, and across the 185 country pages 53 change while NOT ONE RATIO MOVES.* Nothing was changed in the
tooling on that warrant: the exemption that would fit is a POSITIVE one on a declared
field, the shape `ROBOTS_WITNESS` already has, and it is not for the card that benefits
from it to install it. **Neither ratio moves** — `faisable = total - écartés -
non faisables`, so indeterminates count in «faisable» — but the gloss and the «dont N
indéterminé(s)» line do, and the Malawi page carries them.

The list, its pager and the ad are the adapter's first line (its `adapter` issue).
