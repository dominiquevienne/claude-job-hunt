# Board adapter — Un Mejor Empleo (thirteen countries on one template): the listing's cards, «Empleos 1 a 20 de 1,519» as the witness, `--host` names the front

<!-- verified: 2026-09-14 -->

<!-- hosts: www.unmejorempleo.com.ve, ar.unmejorempleo.com, hn.unmejorempleo.com, www.unmejorempleo.cl, www.unmejorempleo.co.cr, www.unmejorempleo.com.co, www.unmejorempleo.com.ec, www.unmejorempleo.com.gt, www.unmejorempleo.com.mx, www.unmejorempleo.com.pa, www.unmejorempleo.com.pe, www.unmejorempleo.com.sv, www.unmejorempleo.es -->
<!-- script: unmejorempleo.py -->
<!-- host-forms: www.unmejorempleo.com.ve, ar.unmejorempleo.com, hn.unmejorempleo.com, www.unmejorempleo.cl, www.unmejorempleo.co.cr, www.unmejorempleo.com.co, www.unmejorempleo.com.ec, www.unmejorempleo.com.gt, www.unmejorempleo.com.mx, www.unmejorempleo.com.pa, www.unmejorempleo.com.pe, www.unmejorempleo.com.sv, www.unmejorempleo.es -->
<!-- host-forms-basis: read — `unmejorempleo.py:HOSTS`, thirteen literals; the Venezuelan root names fourteen hosts in its «Cambiar país» list, the fourteenth (`www.unmejorempleo.com`) is the chooser and answers 404 on `/empleos` · 2026-09-14 -->
<!-- countries: VE AR HN CL CR CO EC GT MX PA PE SV ES -->
<!-- content: measured · **thirteen fronts served their listing with a stated count on 2026-09-13/14 (VE 1 519, AR 224, HN 422, CL 214, CR 380, CO 1 727, EC 807, GT 2 466, MX 741, PA 160, PE 1 017, SV 1 590, ES 449 — 11 716 in all); Venezuela walked to the count — «1 519 emitted over 76 page(s), site states 1 519 (VE) — equal», 00:22–00:28 UTC, 1 519 distinct ids, a `posted` date on every row (2026-06-16 → 2026-09-13), 423 with a salary text; one Honduran ad read** · 2026-09-14 -->
<!-- witness: the listing header's own «Empleos A a B de N» (else the masthead's «Tenemos N ofertas»), read on the first page of every walk and printed beside the emitted count — «N emitted over P page(s), site states N (CC) — equal», exit 6 on a gap; the default walk is bounded (`--pages 10`) and says so, `--all` walks to the count and is compared · 2026-09-14 -->

**One PHP template, one front per country, and the listing page is the
route.** `/empleos?np=<p>` (p from 0) serves twenty cards — the ad's link
`empleo-en_<region>_<slug>-<id>.html`, the title, «Ubicación: X | Estado:
Y», an excerpt, «Publicación: dd/mm/yyyy - Salario: <text>» — under a
header that states **«Empleos 1 a 20 de 1,519»**. No key, no cookie, no
browser. Issue #427 (Venezuela, #418); Honduras named `hn.unmejorempleo.com`
(«422 ofertas») in its own `country-search` table; Puerto Rico has no front
(`pr.unmejorempleo.com` NXDOMAIN on two resolvers, 2026-09-13).

## The fronts, and what each stated

| front | country | stated | | front | country | stated |
| :-- | :-- | --: | :-- | :-- | :-- | --: |
| `www.unmejorempleo.com.ve` | VE | 1 519 | | `www.unmejorempleo.com.gt` | GT | 2 466 |
| `ar.unmejorempleo.com` | AR | 224 | | `www.unmejorempleo.com.mx` | MX | 741 |
| `hn.unmejorempleo.com` | HN | 422 | | `www.unmejorempleo.com.pa` | PA | 160 |
| `www.unmejorempleo.cl` | CL | 214 | | `www.unmejorempleo.com.pe` | PE | 1 017 |
| `www.unmejorempleo.co.cr` | CR | 380 | | `www.unmejorempleo.com.sv` | SV | 1 590 |
| `www.unmejorempleo.com.co` | CO | 1 727 | | `www.unmejorempleo.es` | ES | 449 |
| `www.unmejorempleo.com.ec` | EC | 807 | | `www.unmejorempleo.com` | — | 404 on `/empleos`: the chooser |

VE read 2026-09-13 23:5x UTC, the twelve others 2026-09-14 00:19–00:21 UTC,
one listing page each. Twenty cards a page on every front; the biggest walk
(Guatemala, 124 pages) is ten minutes at 5 s.

## The walk, and the two counts on the page

The header's «Empleos A a B de N» is the witness; the masthead's «Tenemos N
ofertas» is the fallback and said the same number on every page read. The
pager's own links carry `t=<total>` — a client-supplied echo the adapter
never sends: `np` alone pages the same twenty (measured 2026-09-13, page 2
with and without `t`: the same twenty ids, «Empleos 21 a 40 de 1,519»). The
page's JSON-LD is malformed (raw newlines inside a string) and is not read.

## The ad page

`<h4>Label</h4> value` pairs inside `article.trabajo`: Empresa (a link to
the employer's page), Descripción de la Empresa, Estado, Localidad, Tipo de
Contratación, Descripción de la Plaza, Mínimo Nivel Académico / de Inglés /
Experiencia — emitted under `employer`, `employer_description`, `region`,
`location`, `contract`, `description`, `education`, `english`,
`experience`. No date on the ad page — that is the card's; the Venezuelan ad
read carries no «Salario» label, the Honduran one does («L. 16,000», emitted
as `salary_text`). An ad slot sits inside the Localidad value and is stripped. The employer's
page is not read.

## The rules

`/robots.txt` on the Venezuelan front (2026-09-13): `User-agent: *`,
`Crawl-delay: 4`, no `Disallow`. The delay is the host's and `Pace` honours
it; 5 s is the adapter's own. The guard is taken on the exact path before
every request.

## What is withheld

Addresses and phone numbers in the prose are replaced (`[e-mail
withheld]`, `[phone withheld]` — nine digits or more, so a date stays); the
front's own `candidatos@` / `empresas@` addresses are the operator's and sit
in no field this file emits. Salary is the card's text — «A convenir»,
«Pago por comisiones» — as `salary_text`, «----------» as null, never parsed
into a number.

## Invocation

```
unmejorempleo.py hosts                                              # the 13 fronts and their country
unmejorempleo.py list --host www.unmejorempleo.com.ve               # 10 pages, 200 rows, bounded and said so
unmejorempleo.py list --host www.unmejorempleo.com.ve --all         # 1 519 emitted over 76 pages, site states 1 519 — equal (2026-09-14, 6 min)
unmejorempleo.py ad --url https://www.unmejorempleo.com.ve/empleo-en_distrito_capital_gerente_de_diseno_estructural_para_empresa_torres_de_telecomunicaciones-5897877.html
```

Exits: 2 broken (an unknown host, a malformed URL) · 3 gone (404, or no
`article.trabajo`) · 6 partial (a walk short of the count, HTTP ≠ 200, a
page that states no count) · 7 refused by the rules · 8 rules undecidable.
