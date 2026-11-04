# Board — Zhiyog Recruitment System (`jobs.rcsc.gov.bt`, Bhutan): the Royal Civil Service Commission's vacancies, `zrs.py`, searched with its four filter sets IN FULL — the board opens them fully checked, so an EMPTY field means «no value matches» and answers `[]`; 16 of 16 against the count it states itself

<!-- verified: 2026-11-04 -->

<!-- hosts: jobs.rcsc.gov.bt -->
<!-- script: zrs.py -->
<!-- countries: BT -->
<!-- content: measured · **`zrs.py` shipped. 16 of 16 vacancies emitted over 2 pages on 2026-11-04 01:0x UTC, against the **16** the board states itself in every row's `totaL_ROW_COUNT` — the field the page reads as `ret[0].totaL_ROW_COUNT`, so the witness is the BOARD's and not our extraction; the browser header read «16 Jobs» the day before. The four filter sets come from four endpoints the page's own dropdown descriptors name — `/AgencyCommon/GetSuperStructureData` 6, `GetEmploymentTypeData` 2, `GetCategoryData` 5, `GetDzongkhagData` 20 — and all four must be sent IN FULL, each field ending in the comma `GetCondition()` appends, because the multi-selects open FULLY CHECKED: an empty `ConditionNN` is read as «no value matches» and answers `[]`. `Condition10` (order, D/C/A) is REQUIRED; `Condition11`/`12` are skip/take, page size 10. **`/Application/GetVacancyCondition` is NOT the carrier of those lists and its `null` has no bearing on the route** — it restores a PREVIOUSLY SAVED search and the page guards against its own `null`. Fields per row: 64, including position level, pay scale, agency, qualification, slots, application window and twenty `loc*` booleans for the dzongkhag. **Deriving those twenty names naively is wrong on exactly ONE: `Pema Gatshel`'s field is `locPemagatshel` with a lowercase `g`**, so the map is built case-insensitively from the host's own list and asserted a total bijection. Zero e-mail and zero telephone on all 16 rows. Dates are recorded AS WRITTEN — the host states no offset and Bhutan's `+06:00` would be ours.** · 2026-11-04 -->
<!-- witness: the board's OWN `totaL_ROW_COUNT`, 16, read from every row as the page itself reads it — 16 emitted over 2 pages, 16 distinct, zero overlap. That is the count of the FULL-SET search, never «the size of the board». The `witness: none` of 2026-09-17 is retired by it. · 2026-11-04 -->
<!-- content: measured · **the root (200, 40 518 B, md5 32b4134380b4 identical on two reads) and `/Application/Vacancy` (200, 56 569 B) — «Vacancy Announcement», a search by field, type, category, location, agency, title and salary, a card template (Position Level, Employment Type, Pay Scale, Closing Date, Applicant(s)) with no vacancy in the markup; the page's script calls `/Application/GetVacancyAnnouncement` and `/Application/GetVacancyCondition` — GET answers 405, the page POSTs; no count stated, no JobPosting; `_robots.allowed('jobs.rcsc.gov.bt','/')` → open, certain** · 2026-09-17 -->
<!-- witness: none — no count stated · 2026-09-17 -->

**Found by the Bhutan search of #605 (a country never searched), measured
2026-09-17 16:57–17:31 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #605: two
searches — the public services (the Ministry's BLMIS, the Royal Civil
Service Commission's ZRS and vacancy pages) and the private portals the
engine names, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('jobs.rcsc.gov.bt', '/')             open, certain
GET https://jobs.rcsc.gov.bt/Application/Vacancy       200 — the search and the card template, no vacancy in the markup
GET https://jobs.rcsc.gov.bt/Application/GetVacancyAnnouncement   405 — the page POSTs it
```

**The civil service's vacancies — a public source.** The POST the page
makes, replayed with the page's own parameters, is the adapter's first
line.
