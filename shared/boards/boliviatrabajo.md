# Board adapter — BoliviaTrabajo (`trabajo.info.bo`, Bolivia): «949 ofertas publicadas en Bolivia» on the list, twelve cards a page, walked to the count — equal; a JobPosting with its currency on the ad page

<!-- verified: 2026-09-14 -->

<!-- hosts: trabajo.info.bo, www.trabajo.info.bo -->
<!-- script: boliviatrabajo.py -->
<!-- host-forms: trabajo.info.bo -->
<!-- host-forms-basis: read — `boliviatrabajo.py:HOST`, a single literal; `www.` is the canonical the page names for itself and the ad's `AD_RE` accepts both · 2026-09-14 -->
<!-- countries: BO -->
<!-- content: measured · **949 emitted over 80 pages by `boliviatrabajo.py list --all` (01:40–01:44 UTC, 3 s between requests), the site states «949 ofertas publicadas en Bolivia» — equal; 949 distinct ids, an employer and a posting date on every row, a salary text on 677; one ad read** · 2026-09-14 -->
<!-- witness: the list's own «N ofertas publicadas en Bolivia», read on the first page of every walk and printed beside the emitted count — «N emitted over P page(s), site states N (all | q=…) — equal», exit 6 on a gap; the pager's last link (80) stops the walk when the count is not reached; the default walk is bounded (`--pages 10`) and says so, `--all` walks to the count · 2026-09-14 -->

**The most complete Bolivian board that stays open** — Trabajópolis
answers a robot challenge (#428), the Buscojobs front holds two ads —
and the plainest of the night. `/ofertas?q=<text>&page=<p>` serves twelve
`<article>` cards under **«949 ofertas publicadas en Bolivia»** (the
country search read the same 949 on 2026-09-13 19:56): a category badge, a
contract badge, a salary badge («5.500 Bs.», «3.300 - 6.000 Bs.» — each
named by its own class, not its position, because a card without a
contract shows the salary second), the title and its link
`oferta/<id>-<slug>`, «<employer> · <city> · Publicado: 12 Sep 2026». The
pager's last link is `page=80` (80 × 12 = 960 ≥ 949); `/buscar` is the
same list under another name. No key, no cookie, no browser. Issue #431
(Bolivia, #411).

## The walk

```
949 emitted over 80 page(s), site states 949 (all) — equal.
```

2026-09-14 01:40–01:44 UTC, 3 s between requests. 949 distinct ids; an
employer on every row (Santa Cruz de la Sierra 388, La Paz 168, Santa Cruz
124, Cochabamba 99); a posting date on every row, 2026-08-01 → 2026-09-12
— written «12 Sep 2026» on 649 rows and «01 Aug 2026» on 300: the page
mixes Spanish and English month abbreviations, and both go ISO; a salary
text on 677; no `@` in any row.

## The ad page

`/oferta/<id>-<slug>` carries a `JobPosting` in JSON-LD — title,
identifier, datePosted, validThrough, description, hiringOrganization,
jobLocation (city, region, street), employmentType, **`baseSalary` with
its currency (BOB) and unit (MONTH)** — emitted as `salary_min`,
`salary_max`, `salary_currency`, `salary_unit`, beside the prose's
«Salario 5.500 Bs.» as `salary_text` and «Modalidad Presencial» as
`modality`. The employer's page (`/empresa/<slug>`) is not read.

## The rules

`/robots.txt` (313 bytes, 2026-09-14): `*` refuses `/mi-cuenta`,
`/ingresar`, `/registro`, `/confirmar`, `/cerrar-sesion`, `/postular`,
`/favorito`, `/ver-cv`, `/base-talentos`, `/gestion-postulantes`,
`/suscribirse`, `/captcha.php`, then `Allow: /`; a sitemap. The list and
the ad pages are open, `certain: True`; the guard is taken on the exact
path before every request; 3 s own spacing.

## What is withheld

Addresses and phone numbers in the prose are replaced (`[e-mail
withheld]`, `[phone withheld]` — seven digits or more). The site's own
`web@boliviatrabajo.bo` and WhatsApp number sit in its footer, in no field
this file emits.

## Invocation

```
boliviatrabajo.py list                       # 10 pages, 120 rows, bounded and said so
boliviatrabajo.py list --all                 # 949 emitted over 80 pages, site states 949 — equal (2026-09-14, 4 min)
boliviatrabajo.py list --q contador --all    # the site's own `q`, to its own count
boliviatrabajo.py ad --url https://trabajo.info.bo/oferta/4037-analista-junior-bi-y-automatizacion
```

Exits: 2 broken (a malformed URL) · 3 gone (404, or no JobPosting) · 6
partial (a walk short of the count, HTTP ≠ 200, a page that states no
count) · 7 refused by the rules · 8 rules undecidable.
