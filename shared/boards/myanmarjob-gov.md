# Board measurement — the Labour Exchange Office system (`www.myanmarjob.gov.mm`, Myanmar): the Ministry of Labour's public employment service, established 2012 per the national portal — the name resolves on two public resolvers and the connection times out twice on 2026-09-17; INDÉTERMINÉ, a control decides

<!-- verified: 2026-09-17 -->

<!-- hosts: www.myanmarjob.gov.mm -->
<!-- script: none -->
<!-- countries: MM -->
<!-- content: indeterminate · **`www.myanmarjob.gov.mm` — the «Labour Exchange Office Management System» the national portal (`myanmar.gov.mm`) names as the Ministry of Labour's online employment service — resolves on 1.1.1.1 and 8.8.8.8 (NOERROR) and the connection to `/` times out twice under the declared client (`URLError: timed out`, 09:35–09:36 UTC); no rules file could be read (absence of rules, `certain: False`, #283); nothing of the service was read** · 2026-09-17 -->
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
dig @1.1.1.1 www.myanmarjob.gov.mm   NOERROR        dig @8.8.8.8 www.myanmarjob.gov.mm   NOERROR
GET https://www.myanmarjob.gov.mm/   URLError: timed out  ×2
```

**A timeout from a Swiss client is not a refusal and not a verdict**
(§2 sexies): a Myanmar government host may answer only from inside the
country, or be down. INDÉTERMINÉ — a tab (not connected on the day) and a
later reading decide. The national portal's own vacancies page
(`myanmar-gov-vacancies.md`) is served and stands in as the public entry
until then.
