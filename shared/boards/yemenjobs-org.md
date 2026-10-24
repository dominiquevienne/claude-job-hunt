# Board measurement — «YemenJobs» (`yemenjobsorg.arthajobboard.com`, and `yemenjobs.org`): the search names it «Yemen Jobs | NGO & Private Sector — All Cities»; on 2026-09-17 the hosted board's certificate does not verify and, behind it, the host answers 307 to `www.yemenfunds.com`; `yemenjobs.org` is NXDOMAIN on two public resolvers — not a board today

<!-- verified: 2026-09-17 -->

<!-- hosts: yemenjobsorg.arthajobboard.com, yemenjobs.org -->
<!-- script: none -->
<!-- countries: YE -->
<!-- content: indeterminate · **`yemenjobsorg.arthajobboard.com`: the declared client's TLS handshake fails (`CERTIFICATE_VERIFY_FAILED` ×2); with verification disabled — a control, not a route — the host answers 307 to `https://www.yemenfunds.com/` (27 B): the tenant on the Artha job-board platform redirects elsewhere; `yemenjobs.org` and `www.yemenjobs.org` are NXDOMAIN on 1.1.1.1 and 8.8.8.8; no rules file could be read on the first (absence of rules, `certain: False`); nothing of a board was read** · 2026-09-17 -->
<!-- witness: partial — CONTROL OF 2026-10-24 18:16–18:22 UTC (both clock readings taken in the same turn) on `yemenjobsorg.arthajobboard.com` ALONE: the host VERIFIES today. `openssl s_client -showcerts` serves THREE certificates and ends on `Verify return code: 0 (ok)`, and `curl` reads `/robots.txt` at 200 for 83 B with `ssl_verify_result` 0 — where 2026-09-17 recorded `CERTIFICATE_VERIFY_FAILED` twice to the declared client and had to disable verification to see anything at all. Which of the two moved — the served chain or our trust store — is NOT established from here, and the 2026-09-17 reading is not retracted: it was true of its client at its date. What does NOT change: the 307 to `https://www.yemenfunds.com/`, the NXDOMAIN of `yemenjobs.org` and `www.yemenjobs.org` on both resolvers, and `route: none` by the owner's decision of 2026-09-18 (#744). Tool: curl and openssl s_client, never the declared client. -->
<!-- witness: none — nothing was served · 2026-09-17 -->
<!-- route: none · non faisable — décision du propriétaire du 18.09.2026 (un hôte muet reçoit un ticket adapter+blocked qui dit pourquoi et ce qui lèverait), #744 · 2026-09-19 -->

**Found by the Yemen search of #607 (a country never searched), measured
2026-09-17 13:42–13:44 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads, two public resolvers on a DNS
negative.** The method is written on #607: one search naming the national
boards and the UN/NGO aggregators (ReliefWeb, UNjobs, Impactpool — global
aggregators, not Yemeni boards, left to their own cards if any), no
composed host names. *A measurement, not an adapter.*

```
GET https://yemenjobsorg.arthajobboard.com/   SSL: CERTIFICATE_VERIFY_FAILED ×2 ; curl -k → 307 https://www.yemenfunds.com/
dig @1.1.1.1 yemenjobs.org   NXDOMAIN      dig @8.8.8.8 yemenjobs.org   NXDOMAIN   (and www.)
```

**A board the search engine still indexes and that no longer answers as
one**: the Artha tenant redirects to a funding site, the apex has no
delegation. INDÉTERMINÉ on the tenant (a certificate and a redirect are
not a verdict), absent on the apex; no adapter issue until something
serves a list.
