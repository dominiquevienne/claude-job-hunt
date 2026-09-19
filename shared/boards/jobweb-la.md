# Board measurement — Jobweb (`jobweb.la`, Laos): named by the search with a Vientiane office address — on 2026-09-17 the name is NXDOMAIN on two public resolvers: no delegation, not a board today

<!-- verified: 2026-09-17 -->

<!-- hosts: jobweb.la -->
<!-- script: none -->
<!-- countries: LA -->
<!-- content: indeterminate · **`jobweb.la` answers NXDOMAIN on 1.1.1.1 and on 8.8.8.8 (13:51 UTC); the declared client gets `nodename nor servname provided` twice; nothing was read, no rules file** · 2026-09-17 -->
<!-- witness: none — no address · 2026-09-17 -->
<!-- route: none · non faisable — décision du propriétaire du 18.09.2026 (un hôte muet reçoit un ticket adapter+blocked qui dit pourquoi et ce qui lèverait), #742 · 2026-09-19 -->

**Found by the Laos search of #602 (a country never searched), measured
2026-09-17 13:49–13:51 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads, two public resolvers on a DNS
negative.** The method is written on #602: one search naming the country's
boards and agencies (the UN aggregators left aside), no composed host
names. *A measurement, not an adapter.*

```
dig @1.1.1.1 jobweb.la   NXDOMAIN      dig @8.8.8.8 jobweb.la   NXDOMAIN
```

**A name with no delegation** (the 05.09 rule: `NXDOMAIN` on two public
resolvers, not `SERVFAIL`). No issue; the search engine's snippet is
stale.
