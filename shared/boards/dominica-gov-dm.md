# Board measurement — Government of Dominica Web Portal (`dominica.gov.dm`, Dominica): its «Vacancies» page — the name failed (SERVFAIL on two resolvers) on 2026-09-18 and resolves again on 2026-09-21 (107.190.139.58 on 1.1.1.1 and 8.8.8.8); `/vacancies` is served twice and states in its own words that there is no vacancy today («There are no vacancies to display at the moment because their respective deadlines have all expired.»), its RSS feed is empty; a Joomla category, read; no adapter yet

<!-- verified: 2026-09-21 -->

<!-- hosts: dominica.gov.dm, www.dominica.gov.dm -->
<!-- script: none -->
<!-- countries: DM -->
<!-- content: measured · **2026-09-21: `dig @1.1.1.1` and `@8.8.8.8` answer NOERROR, 107.190.139.58, for `dominica.gov.dm` and `www.` (06:37 UTC); `/vacancies` 200 ×2 by the declared client (06:26:30, 06:27:01 UTC; 25 464 B, md5 moving between reads) — a Joomla category page titled «Vacancies - Government of Dominica Web Portal» whose body says «There are no vacancies to display at the moment because their respective deadlines have all expired. There are no articles in this category.»; `/vacancies?format=feed&type=rss` 200 ×2 (06:30:35, 06:31:06 UTC; 625 B) — a channel with `lastBuildDate` and no `<item>`; no JobPosting; rules read, `*` open on the path, `Crawl-delay: 30` — honoured by the two feed reads (31 s apart)** · 2026-09-21 -->
<!-- content-2026-09-18: indeterminate · **`/vacancies` — the client fails to resolve the name on two reads (08:06:06–08:06:12 UTC, `nodename nor servname provided, or not known`); `dig @1.1.1.1` and `dig @8.8.8.8` both answer `status: SERVFAIL` for `dominica.gov.dm` and `www.dominica.gov.dm` — two public resolvers, the same failure, and it is a server failure, not a name error: the zone exists and its servers do not answer; nothing read, rules not read (`_robots.allowed` → open, `certain: False`)** · 2026-09-18 -->
<!-- witness: the portal's own sentence — «There are no vacancies to display at the moment because their respective deadlines have all expired» — and an RSS channel with zero items, both read twice · 2026-09-21 -->
<!-- route: none · the host answers and states zero today — a route to nothing is not a coverage, and the zero is the portal's, read twice, not ours; #753 stays `blocked` with a new reason — the host answers, the portal states zero, and a script that renders nothing does not count (#404): the ticket waits for a published vacancy, next control 2026-09-28 · 2026-09-21 -->
<!-- route-2026-09-19: none · non faisable — décision du propriétaire du 18.09.2026, #753 · reason changed 2026-09-21 (the host answers, states zero) -->

**Found by the Dominica search of #615 (a country never searched),
measured 2026-09-18 08:06–08:11 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #615: one search naming the Government portal and the private boards, no
composed host names. *A measurement, not an adapter.*

The Government portal is the public source the search engine names for public-sector vacancies (`/vacancies`); the country page cited a public employment service on 2026-09-03 and no card carried it until this one.

```
_robots.allowed('dominica.gov.dm', '/vacancies')   open, certain False (the rules file did not answer)
dig @1.1.1.1 dominica.gov.dm      SERVFAIL      dig @8.8.8.8 dominica.gov.dm      SERVFAIL
dig @1.1.1.1 www.dominica.gov.dm  SERVFAIL      dig @8.8.8.8 www.dominica.gov.dm  SERVFAIL
```

**A SERVFAIL is neither a refusal nor a permission, and it is not a missing delegation** — the zone's own servers failed today. Not «closed»: the next control is 2026-09-21 (a deferred task of the session that measured).

## The control three days on — the zone answers, and the portal says «none today»

```
dig @1.1.1.1 / @8.8.8.8 dominica.gov.dm, www.   NOERROR — 107.190.139.58 (06:37 UTC)
GET https://dominica.gov.dm/vacancies                        200 ×2 (06:26:30, 06:27:01 UTC) — 25 464 B, Joomla; «There are no vacancies to display at the moment because their respective deadlines have all expired.»
GET https://dominica.gov.dm/vacancies?format=feed&type=rss   200 ×2 (06:30:35, 06:31:06 UTC) — 625 B, a channel, zero <item>
```

**The SERVFAIL of 2026-09-18 was the zone's servers; three days later they
answer and the page is served.** The board is a Joomla category of
vacancies with deadlines — the portal's own sentence says every one has
expired today, and its RSS feed has no item. That is the portal's zero,
read twice by two routes, not a reader's silence. The vacancies, when there
are some, will be Joomla articles in this category (`/vacancies/<id>-<slug>`
by convention, not observed today) and the feed's `<item>`s. Issue #753
stays `blocked`, its reason rewritten: not «the name does not resolve» but
«the portal states zero, and a script that renders nothing does not count»
(#404) — the event that lifts it is a vacancy published; next control
2026-09-28.
