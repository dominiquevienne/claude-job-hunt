# Board adapter — Caribbean Jobs Online (`www.caribbeanjobsonline.com`, twelve territories with cards on the day): one list per territory, «Page 1 of 4» as the witness, the pages after the first read through the site's own session loader

<!-- verified: 2026-09-14 -->

<!-- hosts: www.caribbeanjobsonline.com -->
<!-- script: caribbeanjobsonline.py -->
<!-- host-forms: www.caribbeanjobsonline.com -->
<!-- host-forms-basis: read — `caribbeanjobsonline.py:HOST`, a single literal; the 28 territory lists are paths under it · 2026-09-14 -->
<!-- countries: AG AW BS BB BM KY GY HT JM LC SR TT -->
<!-- content: measured · **28 territory lists read on 2026-09-14 00:39–00:44 UTC, twelve carry cards and state a page count, fifteen carry none and state nothing; Bahamas walked — 34 emitted over 4 pages, site states 4 pages, equal; Jamaica walked — 128 emitted over 13 pages, site states 13 pages, equal (00:41–00:42 UTC); one ad read** · 2026-09-14 -->
<!-- witness: the list page's own `page_max_count` («Page 1 of N») — a PAGE count, the site states no item count — read on the first page of every walk and printed beside the emitted count: «N emitted over P page(s), site states P page(s) — pages equal», exit 6 when a stated page comes back empty; the default walk is bounded (`--pages 10`) and says so, `--all` walks to the stated pages · 2026-09-14 -->

**A regional board with one list per territory, and its pagination lives
in the session.** `GET /jobs/<slug>` renders ten cards and states
`page_max_count = N` («Page 1 of N»); the next pages are placeholders the
page fills by `POST /include/ajax_vacResults.asp?nextID=results_page<p>`
against the ASP session the first GET opened (`ASPSESSIONID…`). The
`?pageno=` links on the pager are decoration: `?pageno=2` answers the
first page again (the same ten ids, «Page 1 of 4», measured 2026-09-14
00:39 UTC). So a walk is one GET and N−1 POSTs on one cookie jar; a POST
past the last page answers an empty grid (160 bytes). No key, no browser —
a cookie the site itself sets. Issue #449 (Bahamas, #410).

## The 28 lists, and what each stated on 2026-09-14

| list | ISO | cards p.1 | pages stated | | list | ISO | cards p.1 | pages stated |
| :-- | :-- | --: | --: | :-- | :-- | :-- | --: | --: |
| `jamaica` | JM | 10 | **13** | | `anguilla` | AI | 0 | — |
| `bahamas` | BS | 10 | **4** | | `belize` | BZ | 0 | — |
| `aruba` | AW | 10 | 2 | | `bonaire` | BQ | 0 | — |
| `guyana` | GY | 10 | 2 | | `bvi` | VG | 0 | — |
| `trinidad-tobago` | TT | 10 | 2 | | `caribbean-netherlands` | BQ | 0 | — |
| `bermuda` | BM | 8 | 1 | | `dominica` | DM | 0 | — |
| `barbados` | BB | 4 | 1 | | `grenada` | GD | 0 | — |
| `suriname` | SR | 4 | 1 | | `martinique` | MQ | 0 | — |
| `cayman-islands` | KY | 2 | 1 | | `montserrat` | MS | 0 | — |
| `haiti` | HT | 2 | 1 | | `puerto-rico` | PR | 0 | — |
| `antigua` | AG | 1 | 1 | | `saba` | BQ | 0 | — |
| `st-lucia` | LC | 1 | 1 | | `sint-maarten` | SX | 0 | — |
| | | | | | `st-kitts-nevis` | KN | 0 | — |
| | | | | | `st-vincent-grenadines` | VC | 0 | — |
| | | | | | `turks-caicos` | TC | 0 | — |
| | | | | | `virgin-islands` | VI | 0 | — |

All 28 answer 200 and all 28 are accepted by `--country`; **`countries:`
declares the twelve that listed something on the day** — an empty list
that states no page count is a measurement, not a coverage, and the
adapter says so: «0 emitted, the page lists nothing and states no page
count». The ad page's own location filter names the territories with live
vacancies — Antigua, Aruba, Bahamas, Barbados, Bermuda, Cayman Islands,
Guyana, Haiti, Jamaica, St Lucia, Suriname, Trinidad & Tobago, plus
«Cruise Ship» — the same twelve. Puerto Rico's list is empty here; the
island's own boards are in its `country-search` table (#441, #442).

## The two walks

```
34 emitted over 4 page(s), site states 4 page(s) (bahamas, BS) — pages equal.
128 emitted over 13 page(s), site states 13 page(s) (jamaica, JM) — pages equal.
```

2026-09-14 00:41–00:42 UTC, 4 s between requests; ids distinct on both;
every row carries an employer («Posted by …»); the summary line on 113 of
128 Jamaican rows; salary and contract are empty on every card read (the
list's «Contract Type» span is an HTML comment on the pages read — the ad
page carries it).

## The ad page

`div.jobKeyPoints` rows — Organisation, Reference (`VAC-<id>`), Contract
Type, Industries, Location, Salary & Benefits, Date Posted, Expiry Date
(dd/mm/yyyy, emitted ISO) — then the summary and the details. The apply
and print routes (`/candidate/externalApply.asp?`, `printPreview.asp?`) are
refused by the rules and never touched. The page also leaks a SQL
statement in its location filter (`SELECT *, dbo.fn_getLangItem(…) FROM
l_locations …`) — the site's, not read.

## The rules

`/robots.txt` (2026-09-14): `*` refuses `/database/`, `/admin/`,
`/scripts/`, `/rss/`, `/upload/`, `/apply/`, `/candidate/*.asp?*`,
`/client/…`, `/jobs/sitemap.asp`, `/directory/…`; the list `/jobs/<slug>`,
the loader `/include/ajax_vacResults.asp?nextID=…` and `/job/<slug>-<id>.htm`
match no `Disallow` — open, `certain: True`. The guard is taken on the
exact path before every request; 4 s own spacing.

## What is withheld

Addresses and phone numbers in the prose are replaced (`[e-mail
withheld]`, `[phone withheld]` — nine digits or more, so a date stays).
Salary is the site's text (`salary_text`), never parsed.

## Invocation

```
caribbeanjobsonline.py countries                             # the 28 lists and their ISO code
caribbeanjobsonline.py list --country bahamas --all          # 34 emitted over 4 pages, site states 4 pages — pages equal (2026-09-14)
caribbeanjobsonline.py list --country jamaica                # 10 pages of 13, bounded and said so
caribbeanjobsonline.py ad --url https://www.caribbeanjobsonline.com/job/supervisor-annual-review-65987.htm
```

Exits: 2 broken (an unknown list, a malformed URL) · 3 gone (404, or no
key points on the ad page) · 6 partial (a stated page that comes back
empty, HTTP ≠ 200, cards without a page count) · 7 refused by the rules ·
8 rules undecidable.
