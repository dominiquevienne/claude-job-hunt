# Board measurement — U.S. Embassy in The Gambia — Job Opportunities (`gm.usembassy.gov/jobs/`): an employer's page that lists no position — it sends applicants to the State Department's ERA site («To view a current list of all available positions … please visit our ERA site»); served to the declared client (165 KB, identical twice); not a board, and no list served here; out of the country's denominators

<!-- verified: 2026-09-20 -->

<!-- hosts: gm.usembassy.gov -->
<!-- script: none -->
<!-- countries: GM -->
<!-- content: out-of-domain · **`/jobs/` (200, 165 430 B, md5 e5178ea5338d identical on two reads) is the Mission's «Job Opportunities» page: prose, a link to the Electronic Recruitment Application (ERA) site and an applicant guide PDF on `common.usembassy.gov`; no position listed, no count, no JobPosting; `_robots.allowed('gm.usembassy.gov','/jobs/')` → open, certain** · 2026-09-20 -->
<!-- witness: none — no list on this host · 2026-09-20 -->

**Named in the Atlas inventory of 2026-09-04 (#147), never carded; measured
for #767 on 2026-09-20 12:23–12:25 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** *A measurement, not an
adapter.*

**Not a board, and not a list**: one employer's page that points to another host for its openings (#767 asked whether it publishes a served list — it does not). Out of The Gambia's denominators.

```
_robots.allowed('gm.usembassy.gov', '/jobs/')   open
GET https://gm.usembassy.gov/jobs/   200 ×2 — prose and a link to ERA
```
