# Board measurement — «YemenJobs» (`yemenjobsorg.arthajobboard.com`, and `yemenjobs.org`): the search names it «Yemen Jobs | NGO & Private Sector — All Cities»; on 2026-09-17 the hosted board's certificate does not verify and, behind it, the host answers 307 to `www.yemenfunds.com`; `yemenjobs.org` is NXDOMAIN on two public resolvers — not a board today

<!-- verified: 2026-09-17 -->

<!-- hosts: yemenjobsorg.arthajobboard.com, yemenjobs.org -->
<!-- script: none -->
<!-- countries: YE -->
<!-- content: indeterminate · **`yemenjobsorg.arthajobboard.com`: the declared client's TLS handshake fails (`CERTIFICATE_VERIFY_FAILED` ×2); with verification disabled — a control, not a route — the host answers 307 to `https://www.yemenfunds.com/` (27 B): the tenant on the Artha job-board platform redirects elsewhere; `yemenjobs.org` and `www.yemenjobs.org` are NXDOMAIN on 1.1.1.1 and 8.8.8.8; no rules file could be read on the first (absence of rules, `certain: False`); nothing of a board was read** · 2026-09-17 -->
<!-- witness: none — nothing was served · 2026-09-17 -->

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
