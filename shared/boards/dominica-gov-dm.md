# Board measurement — Government of Dominica Web Portal (`dominica.gov.dm`, Dominica): its «Vacancies» page — the name does not resolve on 2026-09-18 (SERVFAIL on 1.1.1.1 and on 8.8.8.8, for `dominica.gov.dm` and `www.`), so nothing of the portal was read; a DNS failure, not a missing delegation (the answer is a server failure, not a name error); indeterminate, a measure to redo; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: dominica.gov.dm, www.dominica.gov.dm -->
<!-- script: none -->
<!-- countries: DM -->
<!-- content: indeterminate · **`/vacancies` — the client fails to resolve the name on two reads (08:06:06–08:06:12 UTC, `nodename nor servname provided, or not known`); `dig @1.1.1.1` and `dig @8.8.8.8` both answer `status: SERVFAIL` for `dominica.gov.dm` and `www.dominica.gov.dm` — two public resolvers, the same failure, and it is a server failure, not a name error: the zone exists and its servers do not answer; nothing read, rules not read (`_robots.allowed` → open, `certain: False`)** · 2026-09-18 -->
<!-- witness: none — nothing was read · 2026-09-18 -->

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
