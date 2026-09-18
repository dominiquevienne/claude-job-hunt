# Board measurement — JobCentre Brunei (`www.jobcentrebrunei.gov.bn`, Brunei): the public employment service's job portal («Pusat Pekerjaan Brunei») — the search page served to the declared client (409 KB) with «Showing 1 to 12 of 579 entries», a Liferay pager and `/web/guest/view-job/-/jobs/<id>/<slug>` ads on 2026-09-18, rules open; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: www.jobcentrebrunei.gov.bn -->
<!-- script: none -->
<!-- countries: BN -->
<!-- content: measured · **`/search-job` (200, 408 595 B, md5 17e40f27ac95 / 48abb2813cf2 — a Liferay portlet id moves) is the portal's search — «Showing 1 to 12 of 579 entries», entries per page 20/30/50/75, a pager, filters (i-Ready, internship, part time, short term), server-rendered cards with `/web/guest/view-job/-/jobs/<id>/<slug>` links (employers: PERUSAHAAN ANJUNG …); no JobPosting; `_robots.allowed('www.jobcentrebrunei.gov.bn','/search-job')` → open, certain; the pager's parameters and the ad not read** · 2026-09-18 -->
<!-- witness: the search page's own «Showing 1 to 12 of 579 entries» · 2026-09-18 -->

**Found by the Brunei search of #611 (a country never searched), measured
2026-09-18 06:37–06:39 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #611: one
search naming the public employment service (JobCentre Brunei, the
Ministry's business portal points at it) and the private portal the
engine names, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('www.jobcentrebrunei.gov.bn', '/search-job')   open, certain
GET https://www.jobcentrebrunei.gov.bn/search-job               200 ×2 — «Showing 1 to 12 of 579 entries», Liferay pager, /web/guest/view-job/-/jobs/<id>/<slug>
```

**The public employment service, served with its count** — at the top of
Brunei's list. The Liferay pager's parameters (`p_p_id=…`, `delta`,
`cur`), and what a `view-job` page carries, are the adapter's first line
(its `adapter` issue).
