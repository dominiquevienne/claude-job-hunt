# Board measurement — Government of Antigua and Barbuda (`ab.gov.ag`, Antigua and Barbuda): its «Vacancies» page — two Treasury Department vacancies as PDFs (Deputy Accountant General, deadline July 06th 2026; HRM Consultant, deadline March 31st 2026 — both past on the day measured), served to the declared client (13 KB, identical twice), rules open; no count stated; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: ab.gov.ag -->
<!-- script: none -->
<!-- countries: AG -->
<!-- content: measured · **`/detail_template.php?page=media/vacancies` (200, 13 388 B, md5 b352b83c32e9 identical on two reads) lists two vacancies as links to `media/pdf/vacancies/*.pdf` with their deadlines in the page text («Deadline - July 06th 2026 … Deputy Accountant General», «Deadline - March 31st 2026 … HRM Consultant»), both past on 2026-09-18 — the page is served and stale; no count, no JobPosting; `_robots.allowed('ab.gov.ag', '/detail_template.php?page=media/vacancies')` → open, certain** · 2026-09-18 -->
<!-- witness: none — two links, both expired · 2026-09-18 -->

**Found by the Antigua and Barbuda search of #620 (a country never
searched), measured 2026-09-18 07:29–07:34 UTC by the declared client, the guard
on the exact path first, `bin/fetch-body.py`, two reads.** The method is
written on #620: four searches naming the Government, the Labour
Department's One Stop Employment Centre and the private boards, no composed
host names. *A measurement, not an adapter.*

The Government's own site, the public source of public-sector vacancies; the Labour Department's One Stop Employment Centre (OSEC) has no site of its own found by this search — its notices go through Facebook and through `dadlijobs.com`.

```
_robots.allowed('ab.gov.ag', '/detail_template.php?page=media/vacancies')   open
GET https://ab.gov.ag/detail_template.php?page=media%2Fvacancies   200 ×2 — two PDF vacancies, both past their deadline
```

The adapter's first line: the page's list of PDF links with their deadlines (a list of two today, with nothing open), the PDF as the ad; a page that has not changed since the spring is a thin flow to be dated, not a verdict.
