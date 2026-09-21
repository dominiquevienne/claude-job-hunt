# Board measurement — Ministry of Employment and Social Affairs (`www.employment.gov.sc`, Seychelles): its «National Vacancies» page — the public employment service publishes **ONE weekly PDF and no HTML list**, and the week of 2026-09-15 to 21 carries **209 vacancies from 85 employers under 7 sectors**, read from the document's own text layer with the standard library; `employmentgovsc.py` — every employer's e-mail and telephone number withheld, and named

<!-- verified: 2026-09-21 -->

<!-- hosts: www.employment.gov.sc -->
<!-- script: employmentgovsc.py -->
<!-- countries: SC -->
<!-- content: measured · **the week's document read by the declared client, 2026-09-21 14:2x–14:4x UTC, the guard on the exact path, two reads of the page and one of the document: `/job-opportunities/national-vacancies` 200 ×2 (34 169 / 34 240 B, md5 2be626f4ed64 / 8d3959a869db — a rendered element moves) is a download category with ONE item and no HTML list; its `/download` answers 200 `application/pdf`, 387 382 B, md5 9d0146be3c05, `attachment; filename="Weekly Vacancy List - 15th to 21st September 2026 .pdf"; modification-date="Tue, 15 Sep 2026 08:34:02 +0400"`. The PDF is read IN MEMORY and never written to disk: 13 pages of text, **209 bulleted vacancies, 85 employers, 7 sectors**, 41 lines that are none of those. The layout is the structure — a sector at the left margin, an employer centred, a bulleted vacancy, its wrapped second line, and a contact column that is read only to be withheld. Nothing anywhere states a count. Exercised: `jobs --country-code SC` → **209 emitted, «the page and the document state no count» said, 209 records naming what was dropped** · 2026-09-21 -->
<!-- witness: none — neither the page nor the document states a count; `employmentgovsc.py jobs` prints the pages read, the vacancies, the employers and the sectors · 2026-09-21 -->
<!-- route: http · 209 · 2026-09-21 -->

**Found by the Seychelles search of #617 (a country never searched),
measured 2026-09-18 07:10–07:17 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #617: one search naming the Ministry and the private boards, no
composed host names. *A measurement, not an adapter.*

The public employment service of the Seychelles; the country page cited it on 2026-09-03 and no card carried it until this one.

```
_robots.allowed('www.employment.gov.sc', '/job-opportunities/national-vacancies')   open
GET  …/national-vacancies                                              200 ×2 — one weekly item, see the content line
HEAD …/national-vacancies/weekly-vacancy-list-15th-to-21st-september-2026/download   200 application/pdf, 387 382 B, attachment
```

## The adapter — `employmentgovsc.py` (#714, 2026-09-21)

```
GET /job-opportunities/national-vacancies                          200 ×2 — one item, no HTML list
GET …/weekly-vacancy-list-15th-to-21st-september-2026/download     200 application/pdf, 387 382 B
    → 13 pages of text, 209 vacancies, 85 employers, 7 sectors
```

**The link is read from the page, never composed**: it carries the week's
dates and changes every Tuesday. **The document is read in memory and never
written to disk.**

**The layout IS the structure**, and the adapter reads it as the ministry
typesets it:

```
x = left        ADMINISTRATIVE AND OTHER RELATED SERVICES:     the sector
x = centred              PROPERTY MANAGEMENT CORPORATION       the employer
x = left        • Financial Controller                         a vacancy
x = left+18       Administrator                                its second line
x = right col                        Email: … / Contact: …     read only to be WITHHELD
x = right col                        Closing Date: 18th September 2026
```

**Four defects were found by building it, and each is now a guard**:

* **a `ToUnicode` CMap maps a range to an ARRAY of destinations** —
  `<0003> <0004> [<0020> <0041>]` is where this document keeps its space and
  its «A». Reading only the single-destination form turned «REBA'S MOTOR
  MECHANIC» into «REB'S MOTOR MECHNIC» *in silence*, on three employers;
* **a font name is per PAGE**: `/F3` is one font here and another there.
  A code the CMap does not name is now SHOWN (U+FFFD), never dropped — *a
  loss that cannot be seen is worse than a loss*;
* **a vacancy and a telephone number share a baseline** («• Guest Service
  Agent» at x=87, «Contact: 2522265» at x=293), so the baseline is cut where
  a run STARTS the contact block — not at a fixed x, because a centred
  employer name runs past that column («OCEANICA RESORT - GLACIS» ends at
  x=337);
* **the space between two runs is measured, not guessed**, with the font's
  own `/Widths` and `/W`: an estimate glued «Food andBeverage» and split
  «SERVIC ES».

**Withheld:** every employer's e-mail address and telephone number — this
document is a contact sheet as much as a vacancy list — and
`withheld_fields` NAMES which of the two was dropped (110 records both, 74 a
number, 25 an address, on the day). **The key is built from what is
emitted**, not from what was read: a vacancy line that ran into an address
would otherwise carry it into the identifier, where nobody looks for one.
The closing date IS emitted (87 of 209 carry one): it is the vacancy's, not
a person's. The ministry publishes no identifier, so the key is ours —
document slug, employer, title — and `key_is_ours` says so on every record.

**Tests and mutations.**
`APublicEmploymentServiceWhoseWeekIsAPdfAndWhoseLayoutIsItsStructure`, both
ways on **a PDF built by the test itself** (the array form of `bfrange`, a
code the CMap does not name, a centred employer running past the contact
column, a vacancy sharing a baseline with a number, a wrapped second line,
two runs typeset apart, a title that runs into an address, a PDF with no
text layer, a body that is not a PDF, a page linking no document, a 404, the
`www.`-less host refused). Mutation bench on a detached copy, `python3 -B`,
**13 / 13 red**: the array form dropped · the unmapped code dropped in
silence · the fonts resolved globally · the contact cut removed · the
measured space removed · the widths ignored · the WinAnsi bullet lost · the
scrub dropped · the withheld declaration emptied · the «no count» note
dropped · the PDF check dropped · a text-less PDF accepted · the host check
dropped.
