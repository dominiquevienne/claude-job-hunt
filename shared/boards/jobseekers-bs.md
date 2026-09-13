# Board adapter — Dept of Labour Online Skills Bank (`jobseekers.bahamas.gov.bs`, Bahamas): the public employment service's PCRecruiter board, paged by the form its own page submits — 220 stated, 220 emitted, the employer on neither page

<!-- verified: 2026-09-13 -->

<!-- hosts: jobseekers.bahamas.gov.bs -->
<!-- script: jobseekers_bs.py -->
<!-- host-forms: jobseekers.bahamas.gov.bs -->
<!-- host-forms-basis: read — `jobseekers_bs.py:HOST`, a single literal; the list's own detail links and the page's `globalJobUrl` write `https://jobseekers.bahamas.gov.bs/…` and nothing else · 2026-09-13 -->
<!-- countries: BS -->
<!-- content: measured · **«1-24 of 220» stated by the list, 220 emitted over 10 pages of 24 — equal** — read by the declared client through the page's own `googlePage` POST, 23:21–23:22 UTC (the same list stated 221 at 20:28 UTC); page 2 answered «25-48 of 220» and every turn was checked on the heading; `/robots.txt` 404 — an absence, certain, open; **the employer's name is on neither the list nor the detail page** — the Department mediates — and `employer` is null with the reason · 2026-09-13 -->
<!-- witness: the page's own «a-b of N» heading (`#resultcount`), read on every page of every walk and printed beside the emitted count; a bounded walk says so and is never «short»; a page whose heading did not move is a fault, not a page · 2026-09-13 -->

**The Bahamas' public employment service — the Department of Labour's
«Online Skills Bank», the most furnished board found for the country
(220 on the day, against «Page 1 of 4» at a regional aggregator and a
suspended «largest portal»), served to the declared client, no key, no
login.** Issue #447, opened by the country search of #410. Measured
2026-09-13 20:27–20:28 and 23:21–23:22 UTC by the declared client, the
guard on the exact path first (`/robots.txt` 404, `certain: True`).

## Rules and the form

```
robots.txt                                                        404 — an absence of rules, certain, open; no Crawl-delay
GET /                                                             200, 35 759 B — the Department's landing («Seeking A Job», «I'm Hiring»)
GET /pcrbin/jobboard.aspx?uid=labour%20database.txt               200, 143 840 B — «1-24 of 221» (20:28), «1-24 of 220» (23:21); 24 rows; forms `searchForm`, `googlePage`
POST /pcrbin/jobboard.aspx  action= · showjobs=Y · pcr-id · morecount=24$$1 · sortorder · unifiedsearch   200 — «25-48 of 220»
POST … morecount=216$$9                                            200 — «217-220 of 220», 4 rows
POST /pcrbin/jobboard.aspx  action=search · Keyword · Island/State · pcr-id · locale                     200 — a filtered first page
GET /pcrbin/jobboard.aspx?action=detail&recordid=153976228221339&pcr-id=<token>   200, 28 742 B — one posting
GET /pcrbin/jobboard.aspx?action=detail&recordid=153976228221339                  200, 4 302 B — a shell without the posting (no token)
```

**A PCRecruiter board turns by re-posting its own pager form.** The
page's `goToPage(p)` sets `morecount` to `(p-1)*24 + "$$" + (p-1)` and
submits `googlePage`, whose hidden fields carry the token (`pcr-id`),
the search key (`unifiedsearch`) and the sort — the adapter posts
exactly those fields with `morecount` rewritten, and reads the «a-b of
N» heading back after every turn: a heading that did not move is a
fault (exit 6), not a page. `--island` and `--keyword` post the search
form first, as the site's own «SEARCH» button does. No Crawl-delay; 3 s
is the adapter's own. **`--pages` defaults to 10** (240 rows) — 220 is
under that, so the default walks the whole board; a bounded walk says so
in the note.

## The row, and the detail

```
<tr><td><a href="/pcrbin/jobboard.aspx?action=detail&recordid=153976228221339&pcr-id=fHR4dC4U…">Cook- Airport VIP Lounge</a></td>
    <td>New Providence</td><td>Full-Time Regular</td><td>9/13/2026</td></tr>
```

The row gives the position (`title`), the island (`New Providence` ×165,
`Grand Bahama` ×28, `Exuma`, `Eleuthera`, `Abaco`, `Berry Islands`,
one `Nassau`, ten blank → null), the type (`Full-Time Regular` ×209,
part-time and contract for the rest) and the date posted (`M/D/YYYY`,
as printed). **`employer` is null on every row and `employer_hidden`
says why: the board shows the posting without the employer — the
Department mediates.** The detail page (`ad --url` with the address the
list wrote, token included) adds the description as posted (its
`jd-description-text` block), a workplace line («Location: National
Airport, New Providence, Bahamas»), and the «Job Brief» pairs — Job Type,
Salary, Industry, Benefits, Vacation, Degree, Years Experience — and
«Posted N Hours ago». **«$0.00 — $0.00» is the board's blank and is
emitted as no salary, never as zero**; a real range gives `salary_min`/
`salary_max` in BSD (the board prints «$» and names no code; the
Bahamian dollar is at par) with `salary_unit_stated` false — no period
is printed. No contact is on either page; the «APPLY» is the
Department's own form and the adapter never touches it.

```
jobseekers_bs.py search
[jobseekers_bs] 220 emitted over 10 page(s), site states 220 (the whole board) — equal.
[jobseekers_bs] the employer is on no row — the board shows the posting without the employer — the Department of Labour mediates; no name on the list or the detail page; `employer` is null on all 220.
```

## Configuration

```yaml
boards:
  jobseekers_bs:
    enabled: true
    island: "New Providence"    # optional — Abaco · Berry Islands · Eleuthera · Exuma · Grand Bahama · New Providence, as the site's select names them
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `island` | no | posted to the site's search form; none = the whole board |
| `keyword` | no | the site's keyword box |

No credentials, no browser, no login. `search` is 1 + (pages − 1)
requests at 3 s (2 + … with a filter); `ad` is one.

## What is not established

- **How long the `pcr-id` token lives** — every walk read on the 13th
  handed a different token and every detail address worked within the
  minute; an old address may serve the 4 302-byte shell, which the
  adapter names (exit 6) rather than reads.
- **Whether the ten blank islands are «Nationwide» or unfilled** — the
  cell is empty on the site; emitted as null.
- **The employer behind a posting** — on neither page by design; a
  candidate learns it through the Department.
- **`Posted N Hours ago` on the detail against `M/D/YYYY` on the list** —
  the list's date is the one emitted as `posted`; the detail's relative
  phrase is kept as `posted_relative`.

## 2026-09-13 — shipped

`search --pages 2`: 48 of 220, bounded by request; `search`: 220 of 220,
equal; `ad` on one. Five tests; six mutations on a detached worktree
(`python3 -B`), six red — `morecount` not rewritten, the heading check
dropped, the count regex broken, the employer filled from the title,
the blank salary emitted as zero, the shell not refused.
