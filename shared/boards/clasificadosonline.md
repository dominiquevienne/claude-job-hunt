# Board adapter — Clasificados Online, section Empleos (`www.clasificadosonline.com`, Puerto Rico): a classifieds list of thirty a page, two numbers of the site's own — the section's «3,581 Oportunidades» and the list's «1 al 30 de 3000» — and the list's is the one walked, to the byte

<!-- verified: 2026-09-14 -->

<!-- hosts: www.clasificadosonline.com -->
<!-- script: clasificadosonline.py -->
<!-- host-forms: www.clasificadosonline.com -->
<!-- host-forms-basis: read — `clasificadosonline.py:HOST`, a single literal · 2026-09-14 -->
<!-- countries: PR -->
<!-- content: measured · **3 000 emitted over 100 pages by `clasificadosonline.py list --all` (01:26–01:31 UTC, 3 s between requests), the list states «1 al 30 de 3000» — equal; the section page states «3,581 Oportunidades de Empleos Puerto Rico» — 581 more than the unfiltered list serves, and `offset=3000` answers the last page again («2971 al 3000»): the list is capped at 3 000, the difference is the site's own and is printed, never resolved; 3 000 distinct ids, an employer on 2 998, a salary text on 1 731, an expiry on all; three ads read** · 2026-09-14 -->
<!-- witness: the list's own «A al B de N empleos en Puerto Rico», read on the first page and printed beside the emitted count — «N emitted over P page(s), list states N — equal», exit 6 on a gap — with the section page's «N Oportunidades de Empleos» printed beside it and the difference named; the default walk is bounded (`--pages 10`) and says so, `--all` walks to the list's count · 2026-09-14 -->

**A classic ASP classifieds, and its Empleos section states two numbers
that are both its own.** `/empleos/` says **«3,581 Oportunidades de
Empleos Puerto Rico»** (3,520 the day before); the listing it links to,
`/Empleos/Listing.asp?JobsCat=%&subcat=%&Pueblo=&txkey=&…&offset=<0,30,…>`,
says **«1 al 30 de 3000 empleos en Puerto Rico»** and serves thirty rows a
page. The adapter walks the list to its own count — **3 000 over 100
pages, equal** — and prints the section's figure beside it: *«the list
states 3 000; the section page states 3 581 — 581 more than the list
serves, a difference of the site's own»*. `offset=3000` answers «2971 al
3000» again: **the unfiltered list is capped at 3 000**, and what lies
beyond is reached by category or town (`--cat`, `--town`, `--q` — the
site's own `JobsCat`, `Pueblo`, `txkey`). Issue #442 (Puerto Rico, #414).

## The row, and a date that is not what its name says

Each row is a schema.org `JobPosting` microdata block followed by the
`record-row` table: the ad's link `Detail.asp?JobId=<id>`, the title, the
employer (a partner page `/PartnersListingJobsID.asp?ID=`), the category in
two languages, the town, the salary as the site writes it («$10.5 / hr»),
the schedule («Full Time», «Part Time», «Temporada - Season Full Time»).
**The row's `itemprop="datePosted"` is the ad's expiry**: on three ads
read 2026-09-14 (2242590, 2088314, 2248279) the ad page's `validThrough`
equals the row's `datePosted` to the second, while the ad's own
`datePosted` reads 2026-09-13 21:24–21:35 on all three — a refresh stamp
more than a posting date. So the list emits `valid_through` and never
`posted`; the ad emits both as the site states them. Dates are US
`m/d/yyyy h:mm:ss AM/PM`, emitted ISO. 3 000 of 3 000 rows carry an
expiry (2026-09-13 → 2029-12-05).

## The ad page

`Detail.asp?JobId=<id>` — microdata (title, datePosted, validThrough,
hiringOrganization, employmentType, workHours, salaryCurrency) and two
prose spans (`Roboto comment`: the description, then the requirements),
«Desde $10.50 Hasta $10.50 hr» as `salary_text`. A classifieds carries
phone numbers in the prose: addresses and numbers are replaced (`[e-mail
withheld]`, `[phone withheld]` — seven digits or more). The three ads read
carried none; 22 of the 3 000 list rows carry an `@` — inclusive Spanish
(«Costurer@», «Psicolog@s»), not an address.

## The rules

`/robots.txt` (292 bytes, 2026-09-14): `*` refuses only `/tomtom-sdk/`;
`anthropic-ai`, `Claude-Web`, `CCbot`, `FacebookBot`, `Google-Extended`,
`GPTBot`, `PiplBot` are refused `/` — **none is a token this project
sends** (`ClaudeBot`, `Claude-User`): a name that looks like ours is not
a name we send. Open, `certain: True`; the guard is taken on the exact
path (query included) before every request; 3 s own spacing. Pages are
heavy — ~0.9 MB each, ~94 MB for the full walk — so the default is
bounded.

## Invocation

```
clasificadosonline.py list                 # 10 pages, 300 rows, bounded and said so
clasificadosonline.py list --all           # 3 000 over 100 pages, list states 3 000 — equal; section states 3 581 (2026-09-14, 5 min)
clasificadosonline.py list --cat 10 --all  # one category, to its own count
clasificadosonline.py ad --url "https://www.clasificadosonline.com/Empleos/Detail.asp?JobId=2242590"
```

Exits: 2 broken (a malformed URL) · 3 gone (404, or no microdata) · 6
partial (a walk short of the list's count, HTTP ≠ 200, a list that states
no count) · 7 refused by the rules · 8 rules undecidable.
