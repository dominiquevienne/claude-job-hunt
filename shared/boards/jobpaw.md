# Board measurement — JobPaw (`jobpaw.com`, Haiti): «Opportunités en Haïti — Offres d'Emploi, Appels d'offres, Formations & Services» — the generalist whose front claims «+20,000 offres d'emploi» (a cumulative), and whose list `/professionals/find-job` is served to the declared client (1.18 MB) with 32 distinct ads (`/professionals/job-details?idj=<id>`, ids around 17 8xx); rules open; no adapter yet

<!-- verified: 2026-09-20 -->

<!-- hosts: jobpaw.com -->
<!-- script: none -->
<!-- countries: HT -->
<!-- content: measured · **the root (200, 182 771 B, md5 8ddd53324951 identical on two reads) links `/professionals/find-job`, `/entreprises/trouver-un-appel` (tenders, a separate section) and 12 `/professionals/job-details` ads; its prose states «+20,000 offres d'emploi, +5,000 appels d'offres» — a cumulative, not the open count; `/professionals/find-job` (200, 1 177 977 B, 12:16 UTC) lists 32 distinct `job-details?idj=<id>` ads with no pager link and no stated count; no JobPosting; `_robots.allowed('jobpaw.com', '/professionals/find-job')` → open, certain** · 2026-09-20 -->
<!-- witness: none — the front's «+20,000» is a cumulative; the list states no count (32 ads counted on it) · 2026-09-20 -->

**Named on the Haiti page since the Atlas inventory of 2026-09-04 (#147),
never carded; measured for #771 on 2026-09-20 12:15–12:18 UTC by the declared
client, the guard on the exact path first, `bin/fetch-body.py`, two reads.**
*A measurement, not an adapter.*

The page's 2026-09-04 note («48 annonces, le seul compte vivant») was a count of links, not a count the site states.

```
_robots.allowed('jobpaw.com', '/professionals/find-job')   open
GET https://jobpaw.com/                              200 ×2 — the front, «+20,000 offres» (cumulative)
GET https://jobpaw.com/professionals/find-job        200 — 32 ads, no pager, no count
```

The adapter's first line: whether `find-job` pages (a hidden parameter, a load-more call) or lists everything, the ad `job-details?idj=<id>` — and the tenders kept apart (the `/entreprises/trouver-un-appel` section is not the board).
