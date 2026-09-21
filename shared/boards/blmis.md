# Board measurement — BLMIS (`www.blmis.gov.bt`, Bhutan): the Ministry of Industry, Commerce and Employment's Labour Market Information System — the public employment service where employers post vacancies and job seekers search them; served to the declared client, and **the jobseeker page carries every vacancy in its own Livewire `wire:initial-data`** — three groupings of one board, 471 distinct on 2026-09-21, no POST replayed; `blmis.py`, the ministry's audit fields and any personal criterion never emitted

<!-- verified: 2026-09-21 -->

<!-- hosts: www.blmis.gov.bt -->
<!-- script: blmis.py -->
<!-- countries: BT -->
<!-- content: measured · **the board read from the page itself, 2026-09-21 13:25–13:26 UTC, the declared client, the guard on the exact path, two reads: `/jobseeker_page/mispage` 200 ×2, **2 331 252 B both times** (md5 4d80c27ccfd3 / 81aa1a8c944f — the Livewire id and checksum move), and its `wire:initial-data` (component `frontpage.jobseeker`) carries `serverMemo.data` with three vacancy lists — `job_by_company` **401**, `job_by_categories` **176**, `job_by_location` **17** — three groupings of ONE board whose union by `application_no` is **471 distinct**; the markup shows no vacancy (the component renders them after boot) and **the page states no total anywhere**. Each vacancy: application_no, designation, business_name (the employer as the ministry registered it; `company_name` is null on all 471), job_category, qualification, dzongkhag_name / gewog_name / placement, starting_salary (Ngultrum a month, «15000.00»), slot, employment_type (Regular 398 — Contract 65 — Training and Employment 5 — Intern 2 — Casual/Freelance 1), last_date_registration (some reach 2049), job_description (471 of 471 non-empty), remarks, and the ministry's own bookkeeping (created_by, updated_by, action_remarks…); `gender` present as a field and **null on all 471 today**; 23 of 471 descriptions or remarks carry an e-mail or a telephone. Districts: Thimphu 192, Sarpang 103, Paro 64. Exercised: `jobs --country-code bt` → **471 emitted of 471**, one request** · 2026-09-21 -->
<!-- witness: none — the page states no total; `blmis.py jobs` prints the union's size and the three groupings' sizes beside the emitted count · 2026-09-21 -->
<!-- route: http · 471 · 2026-09-21 -->

**Found by the Bhutan search of #605 (a country never searched), measured
2026-09-17 16:57–17:31 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #605: two
searches — the public services (the Ministry's BLMIS, the Royal Civil
Service Commission's ZRS and vacancy pages) and the private portals the
engine names, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('www.blmis.gov.bt', '/')            open, certain
GET https://www.blmis.gov.bt/                       200 ×2 — a Livewire front
GET https://www.blmis.gov.bt/jobseeker_page/mispage  200, 2 439 212 B — «Search Job», 253 occupations, no vacancy in the markup
```

**The public employment service, at the top of Bhutan's list.** Its list
arrives by Livewire calls the page makes (a POST with the component's
state) — whether that call replays as the page makes it (the 14.09
judgment) or needs a tab is the adapter's first line (its `adapter`
issue).

## The adapter — `blmis.py` (#680, 2026-09-21)

```
GET /jobseeker_page/mispage    200 — wire:initial-data → job_by_company 401 · job_by_categories 176 · job_by_location 17 → 471 distinct
```

**One request for the whole board.** The Livewire POST route
(`/livewire/message/<component>`) drives the site's own filtering and **is not
replayed**: everything those filters would narrow is already in the page. The
three lists are groupings of one board — the adapter takes their **union by
`application_no`**, prints the three sizes beside the emitted count, and says
the site states no total.

**Emitted:** id, title (`designation`), employer (`business_name`), category,
qualification, place (dzongkhag · gewog · placement), dzongkhag,
`salary_month_nu` as the ministry recorded it, posts (`slot`),
employment_type, closes, posted, description, remarks.

**Withheld — two kinds, both declared:**

- **the ministry's audit fields** — `created_by`, `updated_by`, `edited_by`,
  `deleted_by`, `action_remarks`, `is_deleted`, `is_completed`, `deleted_at`,
  `edited_at`: user ids and desk notes about the people who keyed the record
  in, not the vacancy;
- **a personal criterion**: the vacancy's `gender` field. Null on all 471
  today, and **withheld by name when a record carries one** —
  `withheld_fields: ["gender"]` — so that a silent drop cannot look like a
  board that publishes none (#183, the same shape as JobCentre Brunei's age
  range).

E-mail addresses and telephones in the description and the remarks are
replaced; `contacts_withheld` on every record; the jobseeker area (a login) is
never touched. `--country-code` stamps and says so; `--dzongkhag` keeps one
district and says how many it kept.

**Tests and mutations.**
`APublicServiceWhoseVacanciesAreInThePagesOwnLivewireDataUnderThreeGroupings`,
both ways on fixtures (the three groupings' union, a vacancy in two of them,
the district filter, a vacancy carrying a gender, a page without the lists, a
page without Livewire, a 404, an empty board, the apex refused). Mutation
bench on a detached copy, `python3 -B`, 7 / 7 red: the criterion emitted ·
the withheld list dropped · an audit field emitted · the union taken from one
grouping · the scrub dropped · the «no total stated» note dropped · another
host sent.

