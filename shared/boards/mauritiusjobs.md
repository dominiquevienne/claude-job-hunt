# Board measurement — Mauritius Jobs (`mauritiusjobs.govmu.org`, Mauritius): the National Employment Department's portal (Ministry of Labour and Industrial Relations) — **its search is a POST the page makes on itself, and one request returns the board whole: 587 adverts on 2026-09-21, «Total Jobs Available : 587 jobs» stated**, each row's advert unfolded in the same page; `mauritiusjobs.py` — the **age range is never emitted** (464 of the 587 carry one, #183)

<!-- verified: 2026-09-21 -->

<!-- hosts: mauritiusjobs.govmu.org -->
<!-- script: mauritiusjobs.py -->
<!-- countries: MU -->
<!-- content: measured · **the board read by the declared client, 2026-09-21 14:05–14:15 UTC, the guard on the exact path, two POSTs: `GET /jobsearch` 200 (138 641 B) is the FORM ALONE and lists nothing; the form POSTs to `/index.php/jobsearch` with its own seven fields and **no token of any kind**, and that answer is 200 ×2 (2 209 039 B both, md5 d51540fa42a8 / b66cc5275b2e — a rendered element moves) carrying **587 rows, 587 advert blocks and its own «Total Jobs Available : 587 jobs»**, the same ids in the same order on both reads. A row names #, Job Title, Economic Sector, Company, Country and Closing Date; the advert block is a label/value table read BY LABEL — Employer, Economic Sector, District in Mauritius, Country, Job Summary and Duties on all 587, then Salary Proposed 395, Qualifications 363, Skills 340, State / Province 251, Experience 81, a website link 69, and **Age Range 464 — never emitted**. Three stated figures, three questions: the search says 587 (21.09), the root says «More Than 575 Jobs Available» the same day, the first reading recorded «650 Jobs» (18.09) — none is corrected into the others. Exercised: `jobs --country-code MU` → **587 emitted, «587 read, the board states 587 — they agree» and «464 declare age_range withheld» said** · 2026-09-21 -->
<!-- witness: the search's own «Total Jobs Available : 587 jobs», printed beside the emitted count on every run · 2026-09-21 -->
<!-- route: http · 587 · 2026-09-21 -->

**Found by the Mauritius search of #618 (a country never searched),
measured 2026-09-18 06:45–06:47 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #618: one search naming the National Employment Department's portal
and the private boards, no composed host names. *A measurement, not an
adapter.*

```
_robots.allowed('mauritiusjobs.govmu.org', '/')   open
GET https://mauritiusjobs.govmu.org/   200 ×2 — see the content line
```

## The adapter — `mauritiusjobs.py` (#696, 2026-09-21)

```
GET  /jobsearch                200, 138 641 B — the FORM alone: not one vacancy
POST /index.php/jobsearch      200 ×2, 2 209 039 B — 587 rows, 587 adverts, «Total Jobs Available : 587 jobs»
     search_by_local= search_by_international= search_by_district= search_by_keyword=
     search_by_jobtitle= search_by_qualification= search_by_sector=          (the form's own fields, no token)
```

**The search is the board.** The GET page lists nothing; the POST the page
makes on itself returns everything in one request — and not only the rows:
**each advert is unfolded in the same page**, so there is no second request
per vacancy and no id to compose.

**The advert is read by LABEL, never by position.** Six labels are on all
587 (Employer, Economic Sector, District in Mauritius, Country, Job Summary,
Duties of Job) and six are not (Salary Proposed 395, Qualifications 363,
Skills 340, State / Province 251, Experience 81, a website link 69). A
positional read would put a district where a summary is, on 224 adverts, and
nothing in the output would say so.

**The age range is never emitted, and the record says which ones had one.**
464 of the 587 adverts state «Age Range 18 - 39» or the like; the criterion
is dropped and `withheld_fields: ["age_range"]` names it — #183, as Brunei's
age range and Bhutan's gender. *Salary Proposed is what the employer offers,
not a criterion about a person: it is emitted as written.*

**Three stated figures, three questions, none reconciled**: the search states
**587** (2026-09-21); the portal's root says «More Than **575** Jobs
Available» the same day; the card's first reading recorded «**650** Jobs» on
2026-09-18. The run prints the one it read beside the rows it read, and says
«N short» if they differ rather than choosing between them.

`--district`, `--local` and `--international` filter on what the advert
itself states — **our filters, applied after the one request**, never the
portal's own codes composed — and the run says how many they dropped.
`--country-code` STAMPS: the board is Mauritius's and carries postings
abroad (one on the day, in Madagascar), which the record's own `country`
names. Applying needs an account on the portal; the plugin creates none and
never logs in.

**Tests and mutations.**
`APublicEmploymentServiceWhoseSearchPostReturnsTheWholeBoardUnfolded`, both
ways on fixtures (the POST carrying the form's own fields, the labels read in
any order and four of them absent, the age range withheld by name and its
value nowhere in the output, an advert without one declaring nothing, the
three filters and their drop counts, the stated count agreeing, differing by
585 and absent, a row of the wrong width, a 200 without the result table, a
404, `--local --international` together, the `www.` host refused). Mutation
bench on a detached copy, `python3 -B`, **11 / 11 red**: the age label not
recognised · the withheld declaration emptied · the age emitted as a field ·
the labels read by position · the stated count ignored · the «short» branch
removed · the row width check dropped · the scrub dropped · the POST body
dropped · the host check dropped · the filter drop count silenced.
