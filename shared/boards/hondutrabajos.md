# Board adapter — HonduTrabajos (`www.hondutrabajos.com`, Honduras): the list paged at the root, three numbers on the front page and the list's own «+4,017 ofertas laborales activas» as the witness

<!-- verified: 2026-09-14 -->

<!-- hosts: www.hondutrabajos.com -->
<!-- script: hondutrabajos.py -->
<!-- host-forms: www.hondutrabajos.com -->
<!-- host-forms-basis: read — `hondutrabajos.py:HOST`, a single literal · 2026-09-14 -->
<!-- countries: HN -->
<!-- content: measured · **3 989 emitted over 335 pages by `hondutrabajos.py list --all` (00:58–01:14 UTC, 17 minutes at 3 s), the site states 4 017 — 28 short, exit 6: a live list that moved under the walk (4 017 → 4 018 during it; page 2 read again 21 minutes later had shifted by exactly one ad; the same page read twice 4 s apart is identical in set and order; the last page holds 10 = 4 018 − 334 × 12, exactly); 3 989 distinct keys, an employer on every row, a modality on 3 272; one ad read** · 2026-09-14 -->
<!-- witness: the list's own «+N ofertas laborales activas en Honduras» (2026-09-14: 4 017, and the pager's last page 335 × 12 agrees), read on the first page and printed beside the emitted count — «N emitted over P page(s), site states N — equal», exit 6 on a gap; the banner «Más de 115 vacantes activas» is a hand-written floor, printed and not compared; the default walk is bounded (`--pages 10`) and says so, `--all` walks to the count · 2026-09-14 -->

**Three numbers on the front page, and the list's is the one the pager
agrees with.** The country search of 2026-09-13 20:12 read «4,016
ofertas», «Ofertas Activas 818» and «Más de 115 vacantes activas» and
carried all three without choosing. On 2026-09-14 00:56 the same page
reads **«+4,017 ofertas laborales activas en Honduras»**, the stat box
«4,017+ Ofertas Activas» (the «818» of the day before is gone from it),
and the banner «Más de 115 vacantes activas» unchanged; the pager's last
link is `?page=335`, and 335 × 12 = 4 020 ≥ 4 017. **The witness is the
list's own «+N ofertas laborales activas»**; the banner is a floor written
by hand and is printed, never compared. Issue #438 (Honduras, #413).

## The route

`/?page=<p>` — the root itself, paged — serves twelve `div.job-card`
blocks: the ad's link `/empleo/<slug>-<key>`, the title, the employer and
its public page (`/empresa/<slug>`), the department, the modality
(«Remoto» / «Oficina» / «Híbrido» / «Presencial»), the badges (contract,
experience, «¡Cierra pronto!», «Nuevo»), «hace N días» (emitted as
`posted_relative`, never turned into a date) and the numeric id of
`toggleSave(N)`. **The ledger key is the URL's own suffix** — the same on
the list and on the ad page, which carries no numeric id. Laravel,
server-rendered; no key, no cookie, no browser.

## The walk, and what 28 short means

```
3 989 emitted over 335 page(s), site states 4 017 — 28 short.
```

00:58–01:14 UTC, 335 requests at 3 s. The list is sorted by date, newest
first, and it moved: the root stated 4 017 when the walk began and 4 018
when it ended; page 2 read again 21 minutes later had shifted by exactly
one ad; the same page read twice 4 s apart is identical in set and order
(page 100); the last page holds 10 cards, 4 018 − 334 × 12 exactly. An
insertion at the top pushes one row onto the next page — a key seen twice
is counted once and the tally now says how many — and what falls out of
a 17-minute window is what the gap measures. **The adapter does not paper
over it: exit 6, the number, the cause named** — a shorter walk (`--pages`)
is bounded and says so; a full one is compared and says how far it got.

## The ad page

A `JobPosting` in JSON-LD — title, description, datePosted, validThrough,
employmentType, hiringOrganization (name and public page), jobLocation —
and a «DATOS TÉCNICOS» block: UBICACIÓN EXACTA, CONTRATO, MODALIDAD,
VACANTES (emitted as `positions`), EXPERIENCIA, REQUISITOS ADICIONALES.
**The description often ends with «Correo para aplicar: <address>»** —
the recruiter's address, withheld; a phone number too (eight digits or
more: Honduran numbers are eight). What the prose says of salary («Salario:
L 16,400 + bono») stays as prose, never parsed.

## The rules

`/robots.txt` (2026-09-14, 71 bytes): `User-agent: * / Allow: /`, a
sitemap. Nothing refused; the guard is taken on the exact path before
every request; 3 s own spacing.

## Invocation

```
hondutrabajos.py list                 # 10 pages, 120 rows, bounded and said so
hondutrabajos.py list --all           # 3 989 emitted over 335 pages, site states 4 017 — 28 short (2026-09-14, a 17-minute walk over a moving list)
hondutrabajos.py ad --url https://www.hondutrabajos.com/empleo/auxiliar-de-cuentas-por-cobrar-tegucigalpa-6aa5932967d63
```

Exits: 2 broken (a malformed URL) · 3 gone (404, or no JobPosting) · 6
partial (a walk short of the count, HTTP ≠ 200, a page that states no
count) · 7 refused by the rules · 8 rules undecidable.
