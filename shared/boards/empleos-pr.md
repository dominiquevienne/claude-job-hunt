# Board adapter — Convocatorias del Gobierno de Puerto Rico (`www.empleos.pr.gov`, Puerto Rico): the OATRH's central register of public-service calls, walked page by page through the Webflow site it is — 12 pages stated, 144 emitted, the State's agencies as employers

<!-- verified: 2026-09-13 -->

<!-- hosts: www.empleos.pr.gov -->
<!-- script: empleos_pr.py -->
<!-- host-forms: www.empleos.pr.gov -->
<!-- host-forms-basis: read — `empleos_pr.py:HOST`, a single literal; the page's own links are root-relative (`/convocatorias/<slug>`, `?<key>_page=N`) and the detail's canonical names `www.empleos.pr.gov` · 2026-09-13 -->
<!-- countries: PR -->
<!-- content: measured · **«Page 1 of 12» stated by the register's own pager, 144 emitted over the 12 pages, 12 a page — every page walked** — read by the declared client through plain GETs (`/`, `/?205b2a0f_page=N`), 23:30–23:31 UTC; page 2 answered «Page 2 of 12», page 12 «Page 12 of 12» with 12 rows; the site states no total, the pages are the witness; 79 of the 144 close «Hasta Nuevo Aviso», the rest on a printed date; the rules — `www.empleos.pr.gov` writes no robots.txt rule (an absence, `certain: False`), no Crawl-delay; **the entity is the employer** (UPR, the Departamento de la Familia, municipalities, the courts) and the OATRH's own footer address is dropped · 2026-09-13 -->
<!-- witness: the pager's own «Page N of M» (`aria-label`), read on every page of every walk and printed beside the emitted count; a bounded walk says so and is never «short»; a page whose pager does not say the page asked is a fault, not a page · 2026-09-13 -->

**Puerto Rico's public service — the Registro Central de Convocatorias of
the Oficina de Administración y Transformación de los Recursos Humanos,
where the State's agencies and municipalities publish their internal and
external calls; the Departamento del Trabajo sends its own «Convocatorias»
page here.** Issue #441, opened by the country search of #414. Measured
2026-09-13 20:17 and 23:30–23:31 UTC by the declared client, the guard on
the exact path first (no rule written, `certain: False`, open).

## Rules and the pages

```
robots.txt                                   no rule read — an absence (certain: False), no Crawl-delay
GET /                                        200, 97 203 B — Webflow, Finsweet cmsload in pagination mode; 12 convocatorias; «Page 1 of 12»; Next = ?205b2a0f_page=2
GET /?205b2a0f_page=2                        200 — «Page 2 of 12», 12 rows
GET /?205b2a0f_page=12                       200 — «Page 12 of 12», 12 rows (Head Start 2020-21 calls, «Hasta Nuevo Aviso»)
GET /convocatorias/upr-sea-26-01ae           200 — one convocatoria: the filter fields, the salary block, six titled sections
```

**A Webflow list turns by a query key the page names itself** — the
adapter reads the key off the «Next Page» link (a second collection on
the same page, the agency select, has its own `5c02fa81`) and never
assumes it; after every turn the pager must say the page asked, or the
walk stops (exit 6). **Webflow's conditional visibility is honoured**: a
block whose class carries `w-condition-invisible` is what the site hides
— the date block when the call closes «Hasta Nuevo Aviso», the maximum
salary when none is set, a type that is not set — and it is not read as
shown; a block bound empty (`w-dyn-bind-empty`) is not read either, even
when Webflow's placeholder text sits in it. No Crawl-delay; 3 s is the
adapter's own. **`--pages` defaults to 20** — 12 is under that, so the
default walks the whole register.

## The row, and the detail

```
<div con-item="titulo-puesto" fs-cmsfilter-field="titulo" class="item-title">Secretaria Administrativa III</div>
<div con-item="agency-name" class="item-data agency-name">Universidad de Puerto Rico  (UPR)</div>   <div con-item="region-name" …>San Juan</div>
<div con-item="jobNumber" class="item-data num-convocatoria-2">UPR-SEA-26-01AE</div>
<div data-filter="closing-date" class="item-data fecha-cierre">September 30, 2026</div><div class="item-data fecha-cierre w-condition-invisible">Hasta Nuevo Aviso</div>
<div con-item="external-internal" class="item-data">Externa</div>   <a href="/convocatorias/upr-sea-26-01ae">Ver detalles</a>
<div id="hiddein-fields"><div fs-cmsfilter-field="salario" class="salario-minimo">1300.00</div>…</div>
```

The row gives the position (`title`), the entity (`employer` — the
State's own agency: the UPR ×5 on the first page, the Departamento de la
Familia ×21 in the register, the Departamento de Corrección, the courts,
the municipalities of Corozal and San Sebastián…), the region, the call
number, the closing («September 30, 2026» as printed, or «Hasta Nuevo
Aviso» — 79 of 144 on the day), the type when the site shows one
(«Externa» ×9, «Interna» ×8, «Reapertura Externa» on the first two
pages; null otherwise), the pilot-plan flag, and the minimum monthly
salary from the hidden filter field (USD, period `MONTH`, `salary_unit_
stated` true — the detail's own label is «Salario Mínimo Mensual»; 70 of
144 rows carry none). The detail adds the occupational group, the salary
block (minimum/maximum, monthly/annual, the authorised recruiting salary)
read only from the blocks the site shows, and the sections «Naturaleza del
Trabajo», «Condiciones de Trabajo», «Requisitos Mínimos», «Requisitos
Especiales», «Naturaleza del Examen», «Notas Importantes». **The «Solicite
a través de Eightfold.ai» button on the detail names the ATS family the
pilot plan applies through (#406) — hidden on the call read, and never
followed.** No recruiter contact is emitted: the footer's OATRH address,
telephone and mailbox are the office's, and they are dropped.

```
empleos_pr.py list
[empleos_pr] 144 emitted over 12 page(s), site states 12 page(s) — every page walked; the site states no total, the pages are the witness.
```

## Configuration

```yaml
boards:
  empleos_pr:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials, no browser, no login. `list` is one request a page at
3 s (12 on the day); `ad` is one.

## What is not established

- **The register's total** — the site states pages, not calls; 12 pages
  of 12 gave 144 on the day, and a last page with fewer rows would give
  fewer. The note says «the pages are the witness».
- **What «Hasta Nuevo Aviso» means for a 2020 call** — the Head Start
  2020-21 calls on page 12 are still listed as open-ended; emitted as
  printed, not judged.
- **The Eightfold.ai route of the pilot plan** — a family adapter's
  matter (#406), not this one's; the button is hidden on every call read.
- **The `w-dyn-bind-empty` placeholder** — Webflow's «This is some text
  inside of a div block.» sits in some unbound blocks on the live detail;
  read as nothing.

## 2026-09-13 — shipped

`list --pages 2`: 24 over 2 of 12; `list`: 144 over 12 of 12; `ad` on
one. Five tests; six mutations on a detached worktree (`python3 -B`),
six red — the visibility check inverted, the pager check dropped, the
key assumed instead of read, the salary period not stated, a bound-empty
section read, a hidden salary block read (the third and fifth inert on
the first draft: the fixture used the live key and left the unbound block
empty; widened, red).
