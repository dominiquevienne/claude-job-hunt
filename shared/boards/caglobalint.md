# Board measurement — CA Global (`www.caglobalint.com`): «Africa Recruitment | Africa Jobs» — a pan-African recruitment agency's board, WordPress, `/jobs/` paged 15 a page to `?paged=12` (about 180 ads), each ad `/recruitmentafrica/job/<slug>/` with a region («Southern Africa»), a reference and «Posted N days ago»; page 1 locates ads in South Africa, Nigeria, Guinea, Morocco, Egypt, Congo, Angola, Djibouti, Eritrea, Ethiopia; served to the declared client (438 KB), rules open; no count stated — **SHIPPED 2026-11-04 as `caglobal.py` (#786), and THE COUNTRY DOES NOT LIVE IN THE FIELD THE ISSUE DESIGNATED: `jobpost_location` declares 70 terms, all of them REGIONS at every granularity, naming no country at all — so it is derived from the TITLE, 128 of 199 records resolving one and the other 71 emitting `country: null` rather than a guess**

<!-- verified: 2026-11-04 -->

<!-- hosts: www.caglobalint.com -->
<!-- script: caglobal.py -->
<!-- countries: ZA AU EG GN NG NA SA SL ZM MG AE RW GW BW ZW GH AO MA SN US VE CD MZ TG MW KY UG TZ ET CI FR -->
<!-- content: measured · **the list is the WordPress REST route `wp/v2/jobpost` (`per_page=100`, `orderby=date`), whose `X-WP-Total` states 199 records over 2 pages at 16:30Z — a PUBLISHED STOCK and not an inventory: all 199 are `publish` and they span 2021-06-22 to 2026-11-04, and the total MOVED from 196 at ~13:00Z to 199 at 16:30Z the same day, so it is reported with its hour and never used as a completeness gate. Taken on the WHOLE population: 100 + 99 records with **0 overlapping id** and 199 distinct ids. **THE PLACE TAXONOMY NAMES NO COUNTRY**: `jobpost_location` DECLARES 70 terms of which 13 are assigned, and all seventy are REGIONS at every granularity, 57 of them multi-region names glued by a `#` (`Western Africa#Southern Africa#Eastern Africa#Central Africa`) — South Africa, with 34 ads, is not among them. The type's three other taxonomies answer no better: `jobpost_category` is a sector (Mining 106, Finance 34, Other 25, Banking 12, IT 5, Agriculture 3, NGO 3, Manufacturing 2, Engineering 1), and `jobpost_job_type` and `jobpost_tag` are DECLARED BY THE SCHEMA AND EMPTY on 199/199. So the country is derived from the TITLE, where the host writes it: 128 of 199 resolve (6 through a city alone) and 71 emit `country: null`, about 40 of those stating a REGION instead. **AND THE PREVIOUS `countries:` LINE WAS WRONG IN BOTH DIRECTIONS**: it named eleven (ZA NG GN MA EG CG AO DJ ER ET RW) of which **CG, DJ and ER carry 0 ads on this stock**, while the board serves 31 countries including **Australia with 16** (`Expression of Interest … – Australia`, DAMA sponsorship), which it did not name — a `countries:` line for a recruitment agency is a STOCK SNAPSHOT, not a property of the board. `robots.txt` 200/486 B, `state: read`, `certain: True`, group `*` carrying an EMPTY `Disallow:` so it refuses NOTHING, the host naming and ALLOWING `ClaudeBot`, `anthropic-ai` and `Claude-Web` but not `claude-user`, which falls under `*`; NO `Crawl-delay` written, so the rate is ours. `date` (local) and `date_gmt` (UTC) differ on 199/199. 172 of 199 titles arrive HTML-escaped. Expurgation: 107 of 199 descriptions carry an e-mail, 0 a phone number. Exercised: 100 records over 1 page, 2026-07-24 to 2026-11-04** · 2026-11-04 -->
<!-- witness: `X-WP-Total`, the host's own number and not our extraction — it answers «is this route still the whole type», NEVER «did we read everything»: it is a PUBLISHED STOCK reaching 2021, so completeness is measured against the `--since-days` boundary. **And it is DATED TO THE HOUR, having moved 196 → 199 in three hours on 2026-11-04** · 2026-11-04 -->
<!-- content: measured · **the root (200, 213 234 B, md5 504e47c5d14c identical on two reads) is the agency's front (Rwanda, Kenya, Botswana, Djibouti, Eritrea among the countries it names, `/banking-africa-recruitment-jobs/`, `/internship-page/`); `/jobs/` (200, 437 960 B, 12:29 UTC) lists 15 distinct `/recruitmentafrica/job/<slug>/` ads with a region, a reference number and «Posted N days ago», and a pager `?paged=2` … `?paged=12` (at most 180, not stated); the ads' places on page 1 — Northern Cape (South Africa), Nigeria, Guinea, Morocco, Egypt, Congo, Angola, Djibouti, Eritrea, Ethiopia — give `countries:` by the measure (Rwanda kept from the front, where the agency names it, and from the country pages that named the host); no JobPosting; `_robots.allowed('www.caglobalint.com','/jobs/')` → open, certain** · 2026-09-20 -->
<!-- witness: none — no count stated; the pager bounds the list (12 pages of 15) · 2026-09-20 -->

**Named in the Atlas inventory of 2026-09-04 (#147), never carded; measured
for #768 on 2026-09-20 12:28–12:29 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** *A measurement, not an
adapter.*

One card for the many pages that name it (Rwanda, Djibouti, Eritrea, Guinea-Bissau, Equatorial Guinea in prose; `jobsbotswana.md` and `keejob.md` in passing): **a pan-African agency board, `countries:` by the ads measured** — a multi-country adapter appears on every page it covers (the 13.09 decision). Guinea-Bissau and Equatorial Guinea are not among the places on page 1; the twelve pages would settle them.

```
_robots.allowed('www.caglobalint.com', '/jobs/')   open
GET https://www.caglobalint.com/        200 ×2 — the agency's front
GET https://www.caglobalint.com/jobs/   200 — 15 ads, ?paged=2 … 12
```

The adapter's first line: the 12 pages, the ad's fields (title, region, reference, posted, the text), the WordPress REST if the job type is exposed with `X-WP-Total`.

## 2026-11-04 — #786 SHIPPED as `caglobal.py`: the country does NOT live in the field the issue designated

**MEASURED ON THE WHOLE POPULATION BEFORE A LINE WAS WRITTEN, and that is what
refuted the premise of the rank.** Two REST pages, `per_page=100`: 100 + 99
records, **0 overlapping id**, 199 distinct ids. Not a sample — the board.

**The place taxonomy cannot give a country, and that is not a gap in the data
but its design.** `jobpost_location` DECLARES **70** terms of which **13** are
assigned, and all seventy are REGIONS at every granularity — 57 of them
multi-region names glued by a `#`:

```
Western Africa#Southern Africa#Eastern Africa#Central Africa
United Kingdom#Southern Africa#Europe#Eastern Africa#Central Africa
Northern Africa#Middle East · Southern Africa#Indian Ocean#Eastern Africa
```

**No country is named among the seventy — not even South Africa, which carries
34 ads.** And the glued names explain a measurement from the morning that was
true and misleading: «0 ads with several places» holds because the
multi-membership is encoded INSIDE the term name, not as a list.

The type's three other taxonomies answer no better: `jobpost_category` is a
sector, and `jobpost_job_type` and `jobpost_tag` are **declared by the schema
and EMPTY on 199/199**.

**So the country is derived from the TITLE**, where the host writes it — and
the filter #786 asks for is therefore sound, just not off the field it named.

```
… - Guinea                      the country alone, after an en-dash
… - Cairo, Egypt                city, country
… - South Africa, Johannesburg  country, city -- the REVERSE order
… Gauteng - South Africa        the city BEFORE the dash
… ( / Port Operations) Togo     NO separator at all
… - West Africa                 a REGION, not a country
Finance Manager · CFO           NOTHING
```

**A first model of that form came from THREE records and was wrong**: the three
newest posts carry a `|`, and only **3 of 199** do — one client's. The real
separator is the en-dash. So no separator is parsed at all: each title is
searched for a known name, **longest key first and on word boundaries**.

**AND THE TWO CONDITIONS ARE NOT REDUNDANT, which a mutation had to say
because a test could not.** Stripping the boundary while keeping the length
left `Nigeria`/`Niger` and `Malawi`/`Mali` GREEN — the longer key wins first.
What isolates the boundary is a word that CONTAINS a key without being one:
**`Woman` contains `oman`**, so «Woman in Mining Leadership Programme» files as
**Oman** without the look-around, and `Romania` does too.

**128 of 199 titles resolve a country** (6 through a city alone); the other 71
emit `country: null` and are never guessed, about 40 of them stating a region.

**AND `--country` REPORTS WHAT IT COULD NOT RESOLVE.** Exercised on the issue's
own case: `--country DJ` emits **0 ads** and says *«199 read; 128 resolved to
another country, 71 resolved to none»*. A bare zero there would read as «this
board has nothing for Djibouti», which is a zero that asserts instead of
missing — and Djibouti is the country that put this issue at the top of the
owner's order of 27.09.

**THE PREVIOUS `countries:` LINE WAS WRONG IN BOTH DIRECTIONS.** It named
**eleven** — `ZA NG GN MA EG CG AO DJ ER ET RW` — of which **CG, DJ and ER
carry 0 ads on this stock**, while the board serves **31 countries** including
**Australia with 16** (`Expression of Interest … – Australia`, DAMA
sponsorship), which it did not name. *The README already knew «24 countries» at
its own line 1469: this measurement recoups and extends that, it does not
discover it.* For a recruitment agency, `countries:` describes what was in the
window on the day it was measured, never a property of the board.

**`X-WP-Total` IS A PUBLISHED STOCK, NOT AN INVENTORY**: all 199 are `publish`
and they span **2021-06-22 to 2026-11-04**. So completeness is measured against
the `--since-days` boundary, or against **reading the last page the host
declares** — a third kind of ending, added because without it a sweep that read
199 of 199 exited **partial**, and an alarm that fires always is worth no more
than one that never fires. When `X-WP-TotalPages` is missing, the tool does NOT
claim completeness: ignorance does not free.

**And the total MOVED while we measured it** — 196 at ~13:00Z, 199 at 16:30Z —
so it is reported with its hour.

**A CORRECTION OF THE MORNING'S OWN COMMENT, on the object.** It said the group
`*` «refuses one path that is not ours». It refuses **nothing**: the body
carries `User-agent: *` then an EMPTY `Disallow:`. And it said «its 70 resolved
terms», above a list of **13** — both numbers are right and answer different
questions, the taxonomy DECLARING 70 and only 13 being ASSIGNED. A denominator
was missing, not a figure wrong.

```
_robots.allowed('www.caglobalint.com','/wp-json/wp/v2/jobpost')   open, certain
GET /wp-json/wp/v2/jobpost?per_page=100&page=1   200, 1 537 519 B, 16:30:20Z
GET /wp-json/wp/v2/jobpost?per_page=100&page=2   200, 1 523 665 B, 16:30:43Z
GET /wp-json/wp/v2/jobpost_location?per_page=100 200,    56 421 B, 16:34:03Z
```

**WHAT REMAINS OPEN, and it is not ours to close**: this adapter cannot deliver
**Djibouti**, which is why #786 held rank 1 of the owner's order of 27.09
(«continue à couvrir les pays à zéro»). Djibouti becomes a zero-adapter country
with no carrier in the queue. *To be raised with the owner* — opening another
vehicle for DJ is a decision about what we undertake. And withdrawing DJ's
coverage from the country page belongs to the pages session, not to code.
