# Board measurement — JobNet (`www.jobnet.com.mm`, Myanmar): «Myanmar no.1 Jobs, Vacancies and Career site» — **2 077 adverts read over 70 pages on 2026-09-22 against the «2,077 Jobs Found» the list states itself**, 567 employers, 15 locations; `jobnetmm.py` — the «Verified» badge is on all 2 077 and is therefore NOT carried, and the salary is behind a login the record declares

<!-- verified: 2026-09-22 -->

<!-- hosts: www.jobnet.com.mm -->
<!-- script: jobnetmm.py -->
<!-- countries: MM -->
<!-- content: measured · **the board walked by the declared client, 2026-09-22 12:5x–13:1x UTC, the guard on the exact path: `/jobs` 200 (493 307 B, md5 45e0116c3a21) and `/jobs-in-myanmar` render the same list server-side — **«2,077 Jobs Found» stated**, 30 `div.serp-item` a page, each an `a.search__job-title` to `/job/<slug>/<id>`, a second title line in brackets, the employer, the number of posts («1 Post»), the location, and excerpts labelled Benefits and Highlights. **The page prints NO pager link** and `?page=N` answers anyway: page 2 (490 433 B) carries 30 other adverts, **none shared with page 1**, and states the same total. The walk read **2 077 over 70 pages — the stated total to the unit**: 567 employers, 15 locations (Yangon 1 817, Mandalay 150, NayPyiTaw 33), 496 adverts stating more than one post, benefits and highlights on all of them. **The «Verified» badge is on 2 077 of 2 077** and the salary is «Login to view Salary» on every card. Exercised: `jobs --country-code MM` → **2 077 emitted, «they agree» said** · 2026-09-22 -->
<!-- witness: the list's own «2,077 Jobs Found», printed beside the count read on every run · 2026-09-22 -->
<!-- route: http · 2077 · 2026-09-22 -->

**Found by the Myanmar search of #601 (a country never searched), measured
2026-09-17 09:35–09:39 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads of the root, two public resolvers on
a DNS negative.** The method is written on #601: one search for the
country's boards (a recruiting vendor's ranking of ten, cross-read with
the engine's own results) and one for the public employment service (the
Ministry of Labour's Labour Exchange Office system, named by the national
portal). *A measurement, not an adapter.*

```
_robots.allowed('www.jobnet.com.mm', '/')     open, certain
GET https://www.jobnet.com.mm/                 200 twice — see the content line
```

Nothing past the root was read: the list route, the pager, the ad page
and what it carries are the first line of the adapter, as its `adapter`
issue says.

## The adapter — `jobnetmm.py` (#635, 2026-09-22)

```
GET /jobs-in-myanmar           200 — «2,077 Jobs Found», 30 cards, NO pager link
GET /jobs-in-myanmar?page=N    200 ×69 — 30 a page, none shared with the page before
    → 2 077 read, 2 077 stated, they agree
```

**What it changes for Myanmar is the country's coverage, not a count.** The
only other route measured here is the State's own portal (`myanmargov.py`,
182 notices of which 181 already closed): *a live private board is the
difference between a market observed and a market inferred.*

**The «Verified» badge is on every card, so it is not carried.** 30 of 30 on
page 1, then **2 077 of 2 077** over the whole walk. *A value that is true of
everything separates nothing*, and a field that never varies reads like
information while carrying none — the run counts it and says so, the record
does not hold it. **The number is the point**: at 30 of 30 it could have been
a page's accident; at 2 077 of 2 077 it is the template.

**The salary is behind a login, and the record says so.** Every card shows
«Login to view Salary» pointing at `/login?redirect=…`; `salary_behind_login:
true` is on every record, and the login path is refused **before** the guard —
no account is ever created. *A field a site hides is not a field the site
lacks, and only the record can tell those apart.*

**No pager link, and `?page=N` answers anyway** — the same shape as Guyana's
DPI: the absence of a «next» link is not the end of the list, and a walk that
trusted the markup would have stopped at the first thirty.

**The location and the «N Post» count share one class** (`search__job-location`),
so they are told apart by what they SAY: «1 Post» is a count, a place is not.

**Withheld:** e-mail addresses and telephone numbers in a title, an employer
name or an excerpt; `contacts_withheld` on every record.

**Tests and mutations.**
`ABoardWhoseBadgeIsOnEveryCardAndWhoseSalaryIsBehindALogin`, both ways on
fixtures (two pages walked against the stated count, the badge counted and not
emitted, the salary declared, the «N Post» not taken for a place, an address
and a number scrubbed out of fields that ARE emitted, a repeating page, a first
page with no card, a 404, the `/login` path refused, the apex host refused).
Mutation bench on a detached copy, `python3 -B`, **9 / 9 red**: the badge
carried as a field · `salary_behind_login` dropped · the «N Post» taken for a
location · the stated count ignored · the repeat guard dropped · the login
refusal removed · the badge-count note dropped · the scrub dropped · the host
check dropped.
