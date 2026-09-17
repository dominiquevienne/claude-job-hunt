# Board measurement — the Iranian Ministry of Labour's job search (`shoghl.mcls.gov.ir`, «سامانه جستجوی شغل», Iran): the public employment service — the name resolves on two public resolvers and the connection times out twice on 2026-09-17; its predecessor `karyabi.mcls.gov.ir` no longer resolves (NXDOMAIN on both); INDÉTERMINÉ, a control decides

<!-- verified: 2026-09-17 -->

<!-- hosts: shoghl.mcls.gov.ir, karyabi.mcls.gov.ir -->
<!-- script: none -->
<!-- countries: IR -->
<!-- content: indeterminate · **`shoghl.mcls.gov.ir` — the Ministry of Cooperatives, Labour and Social Welfare's «سامانه جستجوی شغل» (job search system, named by the Ministry's own news pages and by three third-party guides found by the search of #600) — resolves on 1.1.1.1 and 8.8.8.8 (NOERROR) and the connection to `/` times out twice under the declared client (`URLError: timed out`, 2026-09-17 09:23–09:25 UTC); `karyabi.mcls.gov.ir` (the older «کاریابی» portal, still linked by the Ministry's pages) answers NXDOMAIN on both resolvers — a name with no delegation; no rules file could be read on either (absence of rules, `certain: False`, #283); nothing of the service was read** · 2026-09-17 -->
<!-- witness: none — nothing was served -->

**Found by the Iran search of #600 as the public employment service —
the entry a country page lists first.** Measured 2026-09-17 09:23–09:26 UTC:
the declared client's connection to `shoghl.mcls.gov.ir` times out twice
(no TCP answer within the client's limit) while the name resolves on two
public resolvers; `karyabi.mcls.gov.ir` is NXDOMAIN on both.

```
dig @1.1.1.1 shoghl.mcls.gov.ir     NOERROR          dig @8.8.8.8 shoghl.mcls.gov.ir     NOERROR
dig @1.1.1.1 karyabi.mcls.gov.ir    NXDOMAIN         dig @8.8.8.8 karyabi.mcls.gov.ir    NXDOMAIN
GET https://shoghl.mcls.gov.ir/     URLError: timed out   ×2 (09:23Z, 09:24Z)
GET https://karyabi.mcls.gov.ir/    nodename nor servname provided — no address to connect to  ×2
```

**A timeout from here is not a refusal and not a verdict** (§2 sexies): an
Iranian government host may answer from inside the country and not from
a Swiss client, or may be down; neither is established by two timeouts.
INDÉTERMINÉ — a control from a tab (the browser was not connected on the
day) and a later client reading decide; if a tab is served, the route is a
browser route and the service goes to the top of Iran's list.

## What this card does not say

Nothing about what the service publishes (the Ministry's pages say: job
offers uploaded by employment agencies and employers, résumés by job
seekers); nothing about its rules — none could be read.
