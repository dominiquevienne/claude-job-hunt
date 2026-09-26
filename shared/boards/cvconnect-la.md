# Board measurement — CVConnect (`cvconnect.la`, Laos): **the country's first adapter** — Laos had zero. Two of its counters disagree and only one is backed by anything: page 1 states «4 jobs of all 4» and carries four, while every later page states «of all 1700» and carries none. Adapter `cvconnect.py` (#654)

<!-- verified: 2026-09-26 -->

<!-- hosts: cvconnect.la -->
<!-- script: cvconnect.py -->
<!-- countries: LA -->
<!-- route: http -->
<!-- content: measured · **the rules file is served (`state: read`, `certain: True`) on `/` and on `/search_jobs.php`, writes NO Crawl-delay (2 s are ours) and declares no sitemap; `/` and `/search_jobs.php` return the SAME body to the byte (26 044 B, md5 1fe44106c0c7); the page that carries its adverts stated 4 on 2026-09-26 — it stated 7 on 2026-09-17, so this count moves about 40 % a week and every figure here carries its date; pages 2 and 3 state «of all 1700 jobs» and carry nothing at all; ids 2519, 2548, 2552, 2565** · 2026-09-26 -->
<!-- witness: 4 emitted against 4 stated by the page that CARRIES them; the «1700» of the empty pages is printed by the run and never used · 2026-09-26 -->

**Measured 2026-09-26 00:5x–14:2x UTC by the declared client, the guard on the
exact path (query string included), two reads; the adapter then exercised against
the host: 4 emitted, 4 stated.**

## A stated total that no page substantiates is not a measurement

```
/search_jobs.php?page=1   « Show 1 - 4 jobs of all 4 jobs »        4 adverts
/search_jobs.php?page=2   « Show 31 - 60 jobs of all 1700 jobs »   0 adverts
/search_jobs.php?page=3   « Show 61 - 90 jobs of all 1700 jobs »   0 adverts
```

Pages after the first compute their range at thirty a page and announce **1 700**
while carrying nothing. *If the board held 1 700, page 2 would carry thirty.*

> **The danger is not a missing witness: it is two witnesses that each agree with
> themselves.** *An adapter taking «of all N» from any page reports 1 700 against
> 4 emitted and exits partial for ever; one taking page 1 alone is right today and
> would never learn it was lucky.*

So the count is taken **only from a page that carries what it counts**, and the
other figure is **printed anyway** — it is what a future reader will find and
believe.

**This is a FOURTH branch of the stop-rule family**, beside the clamp (Wazifaha
re-serves its last page), the crush (E-Estekhdam returns identical bytes) and the
reset (Melli Kar falls back to the first slice). **It is the only one in which the
board never contradicts itself** — «31 - 60 of 1700» is perfect arithmetic at
thirty a page. **The single rule covering all four: stop on what a page CARRIES,
never on what it STATES.**

## The class names are swapped, and the site corroborates the truth elsewhere

```
<div class="job-des-item-company-name"><h4>ຊ່ວຍຄົວ</h4>       <- the TITLE
<div class="job-des-item-title"><b><p>IMSOUK SUKI</p>         <- the EMPLOYER
```

Reading by the site's own marks would swap them on every record. **What settles it
is that the employer is written in two further places** — the card's
`<a alt="…">` and its `<img title="…">` — and both match `…-title`. *A mark is
evidence, not proof, and a mark contradicted by two others loses.* The record
carries `employer_corroborated` (0, 1 or 2), so a template change appears as **a
number falling**, not as a silently swapped field.

## An icon font stores its glyph's name as text

`<i class="material-icons">location_on</i>` sits inside the place div, so an
ordinary tag-strip yields `"location_on Ban Sibounhueng"`. **Neither empty nor
absurd, merely prefixed — so it survives every human review**, and it was found by
reading the OUTPUT against the browser, not the code.

*The fix is local to this adapter and the defect is general: **every adapter
carries its own `text()`**, so the next author on a Material Icons board will
reproduce it. The rule belongs where `text()` gets written — see `README.md`,
«Writing an adapter».*

## A separator as numerous as the items separates nothing

`<!-- ===== EXPIRED JOBS ===== -->` appears **four times for four adverts**, once
after each: a per-iteration emission, not a section header. *It nearly read as
«three of these four are expired».* **The test is cardinality.** Expiry is read
from the date range the site prints, carried as written.

**WITHHELD:** e-mail addresses and telephone numbers in free text. No salary is
published on the card and none is invented. Titles and places are in Lao and are
not translated.
