# Board measurement — SkilledGuyanese (`skilledguyanese.com`, Guyana): «Guyana Jobs, Vacancies, Careers, Companies, Skills» — a Nuxt board rendered on the server, 50 cards a page under `/?page=N`, whose header STATES «206 Jobs» on 2026-11-26, rules open; adapter `skilledguyanese.py`

<!-- verified: 2026-11-26 -->

<!-- hosts: skilledguyanese.com -->
<!-- script: skilledguyanese.py -->
<!-- countries: GY -->
<!-- content: measured · **ADAPTER DELIVERED 2026-11-26 (#704): `skilledguyanese.py jobs` walks `/?page=N`, 50 cards a page — 50, 50, 50, 50, 6, then an empty page — 206 distinct `/job/<opaque id>`, against the header's own «206 Jobs». It is NOT a mirror of GuyanaIndex, measured member by member the same evening: `guyanaindex.com/jobs/all/<n>` carried 48 ads over 3 pages, and the two share 3 normalised titles out of 167 and 42 (accountant, executive assistant, sales representative), whose SkilledGuyanese employers are three distinct companies. The card carries title, employer (`/company/<id>`), place, contract type and «Expire <date>»; `ad <id>` reads the JobPosting body with contacts taken out and named.** · 2026-11-26 -->
<!-- content: measured · **the root (200, 573 310 B, md5 ff368ec36569 / 11ff8f6cf187 — a rendered element moves) is a Nuxt app rendered on the server: 50 distinct `/job/<opaque id>` links in `job-list__item` cards (titles «Human Development Officer», «Terminal Clerk»; places Berbice, Georgetown), a «Next» control, `?page=2` in the search results' second page; no count stated, no JobPosting; `_robots.allowed('skilledguyanese.com','/')` → open, certain** · 2026-09-18 -->
<!-- witness: 206 · **the list header's own «206 Jobs», read by `skilledguyanese.py` on the page it walks; 206 against 206 emitted on 2026-11-26** · 2026-11-26 -->
<!-- witness: none — the root states no count · 2026-09-18 -->
**Found by the Guyana search of #621 (a country never searched), measured
2026-09-18 06:54–06:56 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #621:
three searches naming the public sources and the private boards, no
composed host names. *A measurement, not an adapter.*

```
_robots.allowed('skilledguyanese.com', '/')   open
GET https://skilledguyanese.com/   200 ×2 — see the content line
```

Observed, not concluded: the first titles of the root are the same, in the same order, as `www.guyanaindex.com/jobs` («Human Development Officer», «Terminal Clerk», «Van Sales Representatives», «Clerk») — one of the two republishes the other, or both draw on one source; the adapter's first line is to open one ad on each and compare.
