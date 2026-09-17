# Board measurement — JobsInYangon (`www.jobsinyangon.com`, Myanmar): «the #1 job search website in Myanmar for SMEs» per its own search snippet — on 2026-09-17 the name answers SERVFAIL on two public resolvers (apex and `www.`): a DNS failure, not NXDOMAIN; INDÉTERMINÉ, a control decides

<!-- verified: 2026-09-17 -->

<!-- hosts: www.jobsinyangon.com -->
<!-- script: none -->
<!-- countries: MM -->
<!-- content: indeterminate · **`www.jobsinyangon.com` and `jobsinyangon.com` answer `SERVFAIL` on 1.1.1.1 and on 8.8.8.8 (09:37 UTC) — the zone's servers fail, the name is not declared absent (that would be NXDOMAIN); the declared client gets `nodename nor servname provided` twice; nothing was read, no rules file** · 2026-09-17 -->
<!-- witness: none — nothing was served · 2026-09-17 -->

**Found by the Myanmar search of #601 (a country never searched), measured
2026-09-17 09:35–09:39 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads of the root, two public resolvers on
a DNS negative.** The method is written on #601: one search for the
country's boards (a recruiting vendor's ranking of ten, cross-read with
the engine's own results) and one for the public employment service (the
Ministry of Labour's Labour Exchange Office system, named by the national
portal). *A measurement, not an adapter.*

```
dig @1.1.1.1 www.jobsinyangon.com   SERVFAIL      dig @8.8.8.8 www.jobsinyangon.com   SERVFAIL
dig @1.1.1.1 jobsinyangon.com       SERVFAIL      dig @8.8.8.8 jobsinyangon.com       SERVFAIL
```

**`SERVFAIL` is not `NXDOMAIN`** (the 05.09 rule): the authoritative
servers fail today, the delegation is not gone. INDÉTERMINÉ — a later
`dig` decides whether the site is back or the zone is dead; no adapter
issue until it answers.
