# Board adapter — Undelucram.ro (Romania): 1 468 advertisements over 147 paged listing pages, the stated figure and the closed pager printed as two witnesses that never correct each other

<!-- verified: 2026-09-13 -->

<!-- hosts: www.undelucram.ro, undelucram.ro -->
<!-- script: undelucram.py -->
<!-- countries: RO -->
<!-- content: measured · rules read twice and certain (231 B, `ClaudeBot` named and refused, `*` open; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200: `/ro/locuri-de-munca` states «1.468 rezultate» and pages to `?page=147` (10 a page, 147 × 10 = 1 470, a partial last page); the adapter walked the 147 pages at 1 s between 15:58:37 and 16:01:04 UTC and emitted 1 468 distinct ids — equal to the stated 1 468 — with a place, a work type, a date and an employer on every card; `JobPosting` in the advertisement's JSON-LD, whose `identifier.value` is the EMPLOYER's id, not the advertisement's · 2026-09-13 16:01 UTC -->
<!-- witness: the listing's own «1.468 rezultate» (a Romanian thousands dot) and its closed pager (147 pages × 10) — printed apart by `undelucram.py list` as «n emitted, site states N — equal / k short» and «the pager closes at page P — P × 10 = M», and neither corrects the other -->

**Shipped 2026-09-13 — the card of 2026-09-12 (a transport measurement for
#233, lot 7, «measured, no adapter yet») is replaced by this one.** Every
fetch under the declared identity, the guard on the exact path first.

```
undelucram.py list                      # every advertisement — 147 pages of 10 at 1 s, ~2 min 30 on 2026-09-13
undelucram.py list --pages 5            # a bounded walk: a lower bound, and it says so; not compared
undelucram.py ad --url https://www.undelucram.ro/ro/locuri-de-munca/<slug>/<id>
```

## The rules — 1 468 advertisements behind a file that names ClaudeBot and opens to Claude-User

```
robots.txt      read twice, certain: True, 231 B, md5 4473a06c73ea both times — `ClaudeBot` named and refused, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed()       True on `/`, `/ro/locuri-de-munca`, `/ro/locuri-de-munca?page=2`
crawl_delay     none  -> Pace(HOST, own=1.0), one second between pages, ours
```

## The listing — 147 pages, two witnesses

| question | answer (2026-09-13, 15:58–16:01 UTC) |
| :-- | --: |
| stated | **«1.468 rezultate»** in the filter panel (1 459 on 2026-09-12 — the board moved by nine in a day) |
| pager | closes at **`?page=147`** — 147 × 10 = **1 470**; the last page is partial (146 pages on 2026-09-12) |
| emitted by the walk | **1 468 distinct ids** over 147 pages — «1 468 emitted, site states 1 468 — equal» |
| a card | `<div class="jobs-item …" id="<id>">` → `<a href="…/ro/locuri-de-munca/<slug>/<id>"><h4>TITLE</h4><p>DD.MM.YYYY</p></a>`, `<h5>EMPLOYER</h5>`, the site's rating «3,85» and «68 evaluări», two `other-info-label` blocks whose icon's `aria-label` names the field — **Location**, **Job Type** |
| on the 1 468 rows | place 1 468 / 1 468, work type 1 468 / 1 468 (Full-time 1 436, Part-time 32), date 1 468 / 1 468 (2025-02-07 … 2026-09-13), employer 1 468 / 1 468; the place is free text — «Bucuresti» 179, «Bucharest» 127, «Remote» 120, «Hybrid (Bucharest)» 62 |
| JSON-LD on the listing | none |

**The two witnesses are printed apart and never merged.** *«147 × 10 = 1 470»
against «1.468 stated» is a partial last page — or a board that moved during
a two-and-a-half-minute walk — and the adapter says both numbers and stops
there: the stated figure is compared to what was emitted, the pager is
reported as arithmetic, and neither is corrected by the other.* A bounded
walk (`--pages`) is a lower bound and is **not compared** to either.

## The advertisement — JSON-LD, and an identifier that is not the advertisement's

`/ro/locuri-de-munca/she-regional-manager/100306` (153 073 B) carries one
`JobPosting`: `title`, `description` (HTML), `datePosted` 2026-09-12,
`validThrough` 2026-10-28, `employmentType` FULL_TIME, `hiringOrganization`
(`name` «Henkel Romania», `sameAs` = the employer's review page, `logo`),
`jobLocation` as a list (`addressLocality` «Pantelimon», `addressCountry`
«RO») — and **`identifier.value` = «278», which is the EMPLOYER's id** (the
number of its review page `…-interviu-278`), not the advertisement's. The
adapter keeps the two apart: `id` is the URL's tail (100306), `employer_id`
is the JSON-LD's 278. No salary field, no `mailto:`, no `tel:` — nothing of
the kind is read. `country` comes from `addressCountry`, `RO` as the
fallback.

## What the adapter does, and refuses to do

- **Walks `?page=1` … until the pager's last page**, 1 s apart, dedups on
  the id, stops early on a page without a new card. A non-200 page is a
  partial walk (exit 6) and **no count is printed** — a short count would
  read as a small board.
- **Reads the place and the work type by the icon's `aria-label`, not by
  their order** — the test's card puts the work type first, and the walk
  above found 1 468 of each.
- **Never emits a contact.** No recruiter address, no phone.
- **Not a verdict that anything is closed** — nothing refuses us.

## Tests

`APagedListingWithTwoWitnessesThatNeverCorrectEachOther` in
`tests/test_core.py` — four cases (the walk with the two witnesses and the
label-by-aria reading; equal + a bounded walk not compared; a 500 as a
partial walk with no count; the advertisement's employer id apart from its
own key, and a non-advertisement URL refused). Six mutations under
`python3 -B` on a detached copy, six reds, each on the case that names it:
the aria-label lookup swapped, the dedup removed, `× 10` computed as `× 12`,
the thousands dot kept, `employer_id` taken from the URL's tail, `bounded`
forced to False.

## Provenance

- `ud/p146.html` (page 146, 350 691 B) and `ud/ad1.html` (the Henkel
  advertisement, 153 073 B), 2026-09-13, `bin/fetch-body.py`, provenance
  beside each — scratchpad of `claude-job-hunt-ab`.
- The full walk: `undelucram.py list > full.jsonl`, 15:58:37 → 16:01:04 UTC,
  1 468 lines, the three `[undelucram]` lines quoted above verbatim.
