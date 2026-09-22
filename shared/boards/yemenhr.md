# Board measurement — Yemen HR (`yemenhr.com`, Yemen): «Yemen's Premier Jobs & Tenders Platform» — **50 vacancies and 23 tenders emitted against the 50 and 23 the pages state**, and **the five per-location counts the site's own footer states are the five the rows give**; `yemenhr.py` — Yemen's first adapter, and the site's `Crawl-delay: 3` is recovered from a card that had lost it

<!-- verified: 2026-09-22 -->

<!-- hosts: yemenhr.com -->
<!-- script: yemenhr.py -->
<!-- countries: YE -->
<!-- content: measured · **50 jobs emitted against the stated «Total: 50», 23 tenders against «Total: 23»**, one page each (`?page=N` until a page carries no row; the page holds fifty, which is why 51 needed two pages on 2026-09-17). Two tables of one system — the jobs table has six cells a row, the tenders table **five** (no «Tools», the account actions existing only for jobs) — read by header LABEL, the two date columns checked AS dates so a shifted column is refused and counted instead of emitted askew. **The footer states the board's own count per location, and the run checks them place by place**: it found «Jobs in Lahij (4)» against 2 read, because a cell can name two places («Lahij , Al-Kokhah») and the site counts the row under each — 50 against 50 the whole time, the total right and a field modelled wrong. On the tenders the footer says «Aden (3)» where the rows give 4, and `/tenders?location_id=6` returns 4 and states «Total: 4»: the split is right and the footer is the odd one out. `robots.txt` open and certain with **Crawl-delay: 3**, absent from the 2026-09-17 reading. The two reads of the list differ ONLY in the CSRF token, the Livewire snapshot and the script's `data-csrf` — three lines of diff. Exercised 2026-09-22: `jobs --country-code YE` → 50, `tenders --country-code YE` → 23, `jobs --location-id 11 --details` → 4 with three sections each · 2026-09-22 -->
<!-- witness: the page's own «Total:» AND the footer's own count per location, both printed beside what the rows give on every unfiltered run · 2026-09-22 -->
<!-- route: http · 73 · 2026-09-22 -->

**Found by the Yemen search of #607 (a country never searched), measured
2026-09-17 13:42–13:44 UTC, adapter written and both tables read
2026-09-22 13:29–13:5x UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads of the list.** *Yemen had no route at all
before this one.*

```
robots.txt                                     read — open, certain, and Crawl-delay: 3
GET https://yemenhr.com/jobs/                  200 ×2, 748 022 B, md5 a3056277bc00 / 255909805933
GET https://yemenhr.com/jobs?page=2            200, 81 789 B — the header, and one cell: «No jobs available.»
GET https://yemenhr.com/tenders                200, 372 064 B — 23 rows, «Total: 23»
GET https://yemenhr.com/tenders?location_id=6  200 — 4 rows, «Total: 4» (the third reading, below)
GET .../jobs/icla-officer-nrc-hodiedah-9808fb32  200, 104 726 B — three labelled sections
```

## The adapter

```
yemenhr.py jobs    [--location-id N] [--since YYYY-MM-DD] [--details] [--country-code YE]
yemenhr.py tenders [--location-id N] [--since YYYY-MM-DD] [--details] [--country-code YE]
```

**A witness a total cannot be.** The page states `Total: 50` and the run prints
it beside the emitted count — but *a total cannot see a partial loss*: an
extraction that drops five rows and doubles five others still states fifty. The
footer states the board's own counts **per location**, and the location is in
every row, so the run checks them **place by place** and says how many agree on
how many.

**And it earned itself on the first run.** It said «Jobs in Lahij (4)» where
the rows gave **2**: a location cell can name more than one place — «Lahij ,
Al-Kokhah», «Lahij , Abyan» — and the site counts such a row under **each**.
Fifty were emitted against a stated fifty the whole time. *The total was right
and a field was modelled wrong, and only the per-place count could see it.*

**Then it disagreed the other way, and the site settled it.** On the tenders
the footer says «Aden (3)» where the rows give 4. The site's own filter,
`/tenders?location_id=6`, returns **4 rows and states «Total: 4»** — the fourth
being «Aden , Taiz». So the split is right and the footer's figure is the odd
one out. **A disagreement between two counts a site states about itself is a
question, not a verdict against our reading**, and the run says so and names
the third reading that settles it. The footer names only its largest locations,
so the check is partial and says so; it runs only on an unfiltered walk,
because a filter moves our side of the comparison and not the site's.

**Two tables of one system, read by header label.** The jobs table has six
cells a row; the tenders table has **five** — no «Tools», the account actions
existing only for jobs. Today the column the tenders lack is the LAST, so a
positional read would land correctly **by luck**. The two date columns must
therefore HAVE the shape of a date: a row whose Posted or Deadline does not is
**refused and counted**, never emitted askew. *A guard that depends on luck
reddens the day someone inserts a column in the middle, and not before.*

**A one-cell row is the board speaking.** Page 2 carries the header and a
single cell — «No jobs available.» — which ends the walk and is printed as the
board's own words, not counted as a row we failed to read.

**`Crawl-delay: 3` is the host's, and it is recovered here.** The
2026-09-17 reading of this card did not record it. *An instruction of the host
missing from a card is a breach waiting to happen.* It is applied — and it is
what makes reading fifty adverts one by one a **choice**: `--details` is not
the default.

**«Important Notes» is not carried.** It is word for word the same on every
advert read — the site's standing advice to applicants («Following the
instructions on How to apply will always increase your chances…»), not a
property of the post. A value true of every advert separates nothing, so it is
**counted and dropped**; an advert whose notes are its own keeps them, because
the day one differs that difference is the information.

**The fingerprint is mute by a NAMED cause.** The two reads of the list give
different md5 at identical size, and the diff of the two bodies is **three
lines**: the `<meta name="csrf-token">`, the Livewire `wire:snapshot` and the
script's `data-csrf` — a token per request. *«Mute by a named cause» is not
«mute»*: what held twice — the fifty rows, the same addresses, the same stated
total — is what may be carried, and this body cannot be compared to another
host's or to its own reading tomorrow.

**WITHHELD:** e-mail addresses and telephone numbers in anything emitted, at a
threshold of nine digits (Yemeni mobiles are `7xxxxxxxx`; a date is spared and
the run says how many shorter runs it left). `contacts_withheld` on every
record. The account actions are never touched, `/login` and `/register` are
refused before the gate, and no account is ever created.

**And «Search Total» is not this page's string.** The 2026-09-17 reading of
this card, and #646 with it, record «Search Total: 51»; the markup says
`<span class="font-bold">Total:</span> 50`, «Search» being the label of the
search box just above it, glued on by flattening the page to text. *The figure
was right and the name of the thing was not.*

## What the board holds, 2026-09-22

**50 vacancies** — Confidential 23, NRC 6, IRC 4, Nahda Makers 3; Multiple
Cities 11, Sana'a 10, Aden 10, Hodiedah 5, Lahij 4; 4 posted that day.
**23 tenders** — YRCS 5, LMMPO 2, BCHR 2; Aden 4, Sana'a 4, Taiz 3.
