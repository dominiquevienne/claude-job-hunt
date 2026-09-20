# Board measurement — JobsHQ Sierra Leone (`jobshq.com.sl`, Sierra Leone): named in the prose of the 2026-09-04 inventory, never carded — the name has no delegation on 2026-09-20 (NXDOMAIN on 1.1.1.1 and on 8.8.8.8); nothing read; a silent host, its ticket #781 blocked

<!-- verified: 2026-09-20 -->

<!-- hosts: jobshq.com.sl -->
<!-- script: none -->
<!-- countries: SL -->
<!-- content: indeterminate · **the declared client fails to resolve the name on two reads (12:20:57–12:21:04 UTC, «nodename nor servname provided, or not known»); `dig @1.1.1.1` and `dig @8.8.8.8` both answer NXDOMAIN — two public resolvers, the same negative, a name error and not a server failure; nothing read, rules not read (`_robots.allowed` → open, `certain: False`)** · 2026-09-20 -->
<!-- witness: none — nothing was read · 2026-09-20 -->
<!-- route: none · non faisable — nom sans délégation, NXDOMAIN sur 1.1.1.1 et 8.8.8.8 le 20.09.2026, #781 (décision du propriétaire du 18.09 : hôte muet = ticket adapter+blocked) · 2026-09-20 -->

**Measured for #764 on 2026-09-20 by the declared client, the guard on the exact
path first, and two public resolvers on the DNS negative.** *A
measurement, not a verdict: a name without delegation today may be
delegated tomorrow; the ticket #781 says what would lift it, and the
control of 2026-09-23 (with #740–#744, #773) reads it again.*

```
_robots.allowed('jobshq.com.sl', '/')   open, certain False (the rules file could not be read)
dig @1.1.1.1 jobshq.com.sl   NXDOMAIN      dig @8.8.8.8 jobshq.com.sl   NXDOMAIN
GET https://jobshq.com.sl/   the name does not resolve ×2
```
