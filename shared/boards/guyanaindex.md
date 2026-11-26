# Board measurement — GuyanaIndex Jobs (`www.guyanaindex.com`, Guyana): «Current jobs in Guyana 2026» — the jobs section of a business directory, paged by PATH (`/jobs/all/<n>`, 20 a page; `?page=N` is silently ignored), whose list STATES «We found 48 job offers» on 2026-11-26; adapter `guyanaindex.py`

<!-- verified: 2026-11-26 -->

<!-- hosts: www.guyanaindex.com -->
<!-- script: guyanaindex.py -->
<!-- countries: GY -->
<!-- content: measured · **ADAPTER DELIVERED 2026-11-26 (#708): `guyanaindex.py jobs` walks `/jobs/all`, `/jobs/all/2`, `/jobs/all/3` — 20, 20, 8 — then a page with no ad: 48 distinct `/job/<id>/<slug>` against the list's own «We found 48 job offers». `/jobs/all?page=2` to `?page=7` returned the SAME bytes six times (one md5), so the query form is ignored and the tool refuses any query. Not a mirror of SkilledGuyanese, measured member by member the same evening: 3 shared normalised titles out of 42 and 167, at three distinct employers. The card carries title, employer, excerpt, a relative date and two fields named by their icons; the place and the absolute date are in each ad's JobPosting.** · 2026-11-26 -->
<!-- content: measured · **`/jobs` (200, 12 203 B, md5 c421d797c26a identical on two reads) lists 8 «Latest Job Vacancies» as `/job/<id>/<slug>` (ids around 32066) with sector links `/jobs/<sector>`; `/jobs/all` (200, 23 650 B, 06:56 UTC) lists 20 ads and a pager `/jobs/all/2` … `/jobs/all/6` — at most 120 ads, not stated; no JobPosting; `_robots.allowed('www.guyanaindex.com','/jobs')` → open, certain** · 2026-09-18 -->
<!-- witness: 48 · **the list's own «We found 48 job offers», read by `guyanaindex.py` on the page it walks; 48 against 48 emitted on 2026-11-26** · 2026-11-26 -->
<!-- witness: none — no count stated; the pager bounds the list (6 pages of 20) · 2026-09-18 -->
**Found by the Guyana search of #621 (a country never searched), measured
2026-09-18 06:54–06:56 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #621:
three searches naming the public sources and the private boards, no
composed host names. *A measurement, not an adapter.*

```
_robots.allowed('www.guyanaindex.com', '/jobs')   open
GET https://www.guyanaindex.com/jobs   200 ×2 — see the content line
```
GET https://www.guyanaindex.com/jobs/all   200 — 20 ads, pager to /jobs/all/6

Observed, not concluded: the first titles are those of `skilledguyanese.com`'s root, in the same order — see that card; the adapter's first line is to open one ad on each and compare.
