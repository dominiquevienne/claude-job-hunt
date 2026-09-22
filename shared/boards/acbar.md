# Board measurement — ACBAR Jobs (`www.acbar.org/en/jobs`, Afghanistan): the Agency Coordinating Body for Afghan Relief and Development's job list — the historic first Afghan job portal, **268 posts read over 14 pages on 2026-09-22 against the «268 jobs found» it states itself**, 123 employers and 25 provinces; `acbar.py` — the advert's `Gender` and `Nationality` are never emitted and are named, and the key is the board's numeric id because the titles are Dari and Pashto

<!-- verified: 2026-09-22 -->

<!-- hosts: www.acbar.org -->
<!-- script: acbar.py -->
<!-- countries: AF -->
<!-- content: measured · **the board walked by the declared client, 2026-09-22 09:2x–09:5x UTC, the guard on the exact path: `/en/jobs` 200 (84 972 B, md5 6ae74824df7a) states **«268 jobs found»** and carries 20 `div.job-card` a page — the advert's address `/en/jobs/details/<id>/<slug>`, its title, the employer, the contract type, the province, a RELATIVE age («34 minutes ago», kept as written: a relative age is not a date) and the closing date — with a `?page=N` pager read from its own links. **268 read over 14 pages, 268 stated, they agree**; 123 employers, 25 provinces, 255 Full Time and 13 Part Time, every post carrying a closing date. An advert (`/en/jobs/details/145755/haul-truck-operator`, 200, 96 600 B) carries ten information rows and four blocks (About the Company, Job Summary, Job Requirements, Submission Guideline) — **including `Gender: Male` and `Nationality: Afghan`, read so they can be dropped by name**. Exercised: `jobs --country-code AF` → **268 emitted, «they agree» said**; `ad --url …` → «does NOT carry: gender, nationality» · 2026-09-22 -->
<!-- witness: the board's own «268 jobs found», printed beside the count read on every run · 2026-09-22 -->
<!-- route: http · 268 · 2026-09-22 -->

**Found by the Afghanistan search of #613 (the private boards beside
`jobs.af`, which the country page already carries), measured 2026-09-17
13:38–13:39 UTC by the declared client, the guard on the exact path first,
`bin/fetch-body.py`, two reads.** The method is written on #613: two
searches (the NGO coordination body's portal, which the first Afghan
portal grew from; and the portals the engine returns by name), no composed
host names. *A measurement, not an adapter.*

```
_robots.allowed('www.acbar.org', '/en/jobs')   open, certain
GET https://www.acbar.org/en/jobs               200 ×2, identical — «260 jobs», location and category filters, employer pages
```

The NGO and UN sector's board (DACAAR: «open vacancies are announced
through www.ACBAR.org»); NETLINKS, jobs.af's operator, built its first
version. The pager, the ad page and what it carries are the adapter's first
line (its `adapter` issue).

## The adapter — `acbar.py` (#641, 2026-09-22)

```
GET /en/jobs            200 — «268 jobs found», 20 cards, a pager to page 14
GET /en/jobs?page=N     200 ×13 — 268 read, 268 stated, they agree
GET /en/jobs/details/<id>/<slug>   the advert: 10 information rows, 4 blocks
```

**The advert states who may apply, and the record does not carry it.**
`Gender: Male` and `Nationality: Afghan` are **read so they can be dropped by
name**: `withheld_fields` lists them on the record and the run says «does NOT
carry: gender, nationality». *A record that simply lacked them would be
indistinguishable from an advert that states none* — #183, as Bhutan's `gender`
and Brunei's age range.

**The address to write to sits OUTSIDE the four blocks**, in its own
`p.acbar-jd__email`. Matching only the tidy `</div></article>` shape lost the
whole «Submission Guideline» block — *the one written around an e-mail* — so
both the block and the paragraph are read, and both are scrubbed.

**The key is the board's numeric id, never the slug.** The titles are Dari and
Pashto («teller به نمایندگی های ولایت پکتیکا»); an ASCII fold of them is empty,
and two different posts then collide on one key.

**The posted age is relative** («34 minutes ago») and is kept as the board
writes it. *Turning it into a date would invent a precision the board never
published* — the closing date, which the board does state, is the date.

**Why this board matters for its country**: Afghanistan's other measured routes
are a JavaScript shell with no card (`bast-af`), a 403 to every client
(`afgjobs`), a broken TLS chain (`afghanjobfinder`) and a browser-only API
(`jobs-af`). **This is the one an ordinary HTTP client can read.**

**Tests and mutations.**
`ABoardWhoseAdvertStatesWhoMayApplyAndWhoseTitlesAreNotLatin`, both ways on
fixtures (two pages walked against the stated count, two Dari titles sharing a
slug and not a key, the relative age kept, the criteria named and absent, an
address inside the emitted block AND in the paragraph that is not emitted, a
repeating page, a first page with no card, a 404, `ad` on a query string and on
a non-advert path, the apex host refused). Mutation bench on a detached copy,
`python3 -B`, **10 / 10 red**: the criteria emitted instead of withheld · the
withheld list emptied · the e-mail paragraph not read · the key taken from the
slug · the relative age dropped · the stated count ignored · the repeat guard
dropped · the blocks read only in the tidy shape · the scrub dropped · the host
check dropped.
