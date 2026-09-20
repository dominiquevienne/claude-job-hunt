# Board measurement — JobConnect Africa (`africa-jobconnect.com`): «Emploi Afrique 2025 - +50 000 Offres d'Emploi … Sénégal, Côte d'Ivoire, Mali» — a 14 KB React shell (`<div id="root">`, one bundle, a service worker) with a 90-byte body, no link, no ad and no API host in its markup, served to the declared client; the «+50 000» / «+15 000» are the page's own marketing claims; rules open; the app's call to read; no adapter yet

<!-- verified: 2026-09-20 -->

<!-- hosts: africa-jobconnect.com -->
<!-- script: none -->
<!-- countries: CI SN ML -->
<!-- content: measured · **the root and `/jobs` (200, 14 121 B, md5 41ed9d1cb76c identical on three reads) are the same React shell — `<div id="root">`, `/assets/index-BS0RXuXE.js`, `/registerSW.js`, a FAQ JSON-LD and meta tags claiming «+50 000 offres» and «+15 000 offres d'emploi en Afrique … 54 pays» — with 11 links in the head and none in the body; no card, no count in the markup, no JobPosting; `_robots.allowed('africa-jobconnect.com','/')` → open, certain. `countries:` by the page's own title («Emploi Sénégal, Côte d'Ivoire, Mali»), not by a measured ad** · 2026-09-20 -->
<!-- witness: none — the numbers in the meta tags are claims, no list was read · 2026-09-20 -->

**Named in the Atlas inventory of 2026-09-04 (#147), never carded; measured
for #765 on 2026-09-20 12:23–12:25 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** *A measurement, not an
adapter.*

```
_robots.allowed('africa-jobconnect.com', '/')   open
GET https://africa-jobconnect.com/       200 ×2 — a React shell, 90 B of body
GET https://africa-jobconnect.com/jobs   200 — the same shell
```

The adapter's first line: the call the bundle makes (a browser's network panel), replayed with the page's own parameters; whether the claimed «+15 000» are ads or a marketing number is settled by that call, not by the page.
