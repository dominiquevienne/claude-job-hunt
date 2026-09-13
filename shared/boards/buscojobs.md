# Board adapter — Buscojobs (twenty-one countries on one platform): the listing's own Next.js payload, `--host` names the front, «41 emitted over 3 pages, site states 41 — equal» on Paraguay

<!-- verified: 2026-09-13 -->

<!-- hosts: ve.buscojobs.com, www.buscojobs.com.uy, www.buscojobs.com, www.buscojobs.com.pr, www.buscojobs.com.py, www.buscojobs.com.bo, ni.buscojobs.com, www.buscojobs.com.do, www.buscojobs.com.ec, www.buscojobs.com.gt, www.buscojobs.com.pa, www.buscojobs.com.ar, www.buscojobs.cl, www.buscojobs.com.co, www.buscojobs.com.es, br.buscojobs.com, www.buscojobs.pt, www.buscojobs.hn, www.buscojobs.com.sv, www.buscojobs.cr, www.buscojobs.mx, www.buscojobs.pe -->
<!-- script: buscojobs.py -->
<!-- host-forms: ve.buscojobs.com, www.buscojobs.com.uy, www.buscojobs.com, www.buscojobs.com.pr, www.buscojobs.com.py, www.buscojobs.com.bo, ni.buscojobs.com, www.buscojobs.com.do, www.buscojobs.com.ec, www.buscojobs.com.gt, www.buscojobs.com.pa, www.buscojobs.com.ar, www.buscojobs.cl, www.buscojobs.com.co, www.buscojobs.com.es, br.buscojobs.com, www.buscojobs.pt, www.buscojobs.hn, www.buscojobs.com.sv, www.buscojobs.cr, www.buscojobs.mx, www.buscojobs.pe -->
<!-- host-forms-basis: read — `buscojobs.py:HOSTS`, twenty-two literals, one per front; the front's root page names all twenty-two in its footer and no other · 2026-09-13 -->
<!-- countries: VE UY PR PY BO NI DO EC GT PA AR CL CO ES BR PT HN SV CR MX PE -->
<!-- content: measured · **every one of the 22 hosts read on 2026-09-13 (23:31–23:47 UTC) served its listing page with `__NEXT_DATA__` and a stated count; Paraguay walked to the count — 41 emitted over 3 pages, site states 41, equal; one ad read**; the counts per front are in the script's docstring (VE 6 262, UY 1 943, PR 8 901, …, ES 2 858 489, BR 1 556 164, MX 1 646 877); a burst of 21 fronts in 80 s was answered by an AWS WAF challenge on five of them, and 30 s spacing was served seven of seven five minutes later · 2026-09-13 -->
<!-- witness: the payload's own `resultadosIniciales.count`, read on the first page of every walk and printed beside the emitted count — «N emitted over P page(s), site states N (CC) — equal», exit 6 on a gap; the default walk is bounded (`--pages 10`) and says so, `--all` walks to the count and is compared · 2026-09-13 -->

**One Next.js application — the same `buildId` `5d4757de…` on every front
read — serving twenty-one national job boards under twenty-two hostnames,
and the listing page carries its results as data.** `/ofertas/<p>`
(`/vagas/<p>` in Brazil and Portugal) renders `pageProps.resultadosIniciales`
into `__NEXT_DATA__`: the **count the site states**, fifteen full records
(id, title, employer, city, department, country, start date, a
150-character excerpt, the flags) and the facets; the page's JSON-LD
`ItemList` carries the fifteen public URLs, `…-ID-<IdOferta>`. No key, no
cookie, no browser. Issue #425 (Venezuela, #418) — and Bolivia (#428…),
Paraguay (#433…), Honduras, Puerto Rico and Uruguay named the same host in
their own `country-search` tables.

## The fronts, and what each stated on 2026-09-13

| front | country | stated | | front | country | stated |
| :-- | :-- | --: | :-- | :-- | :-- | --: |
| `ve.buscojobs.com` | VE | 6 262 | | `www.buscojobs.com.ar` | AR | 108 822 |
| `www.buscojobs.com.uy` (= `www.buscojobs.com`) | UY | 1 943 | | `www.buscojobs.cl` | CL | 73 966 |
| `www.buscojobs.com.pr` | PR | 8 901 | | `www.buscojobs.com.co` | CO | 129 610 |
| `www.buscojobs.com.py` | PY | 41 | | `www.buscojobs.com.es` | ES | 2 858 489 |
| `www.buscojobs.com.bo` | BO | 2 | | `br.buscojobs.com` | BR | 1 556 164 |
| `ni.buscojobs.com` | NI | 28 | | `www.buscojobs.pt` | PT | 498 335 |
| `www.buscojobs.com.do` | DO | 2 375 | | `www.buscojobs.com.gt` | GT | 2 234 |
| `www.buscojobs.com.ec` | EC | 2 586 | | `www.buscojobs.com.pa` | PA | 988 |
| `www.buscojobs.hn` | HN | 1 | | `www.buscojobs.mx` | MX | 1 646 877 |
| `www.buscojobs.com.sv` | SV | 842 | | `www.buscojobs.pe` | PE | 34 141 |
| `www.buscojobs.cr` | CR | 1 262 | | | | |

The six- and seven-figure fronts — Spain, Brazil, Mexico, Colombia,
Argentina, Chile, Portugal — are **aggregates by their size**, and the
record says where a row comes from: `Fuente`, emitted as `source_feed` —
**on the 306 rows read across the 22 fronts, 144 null (the front's own
postings), 86 `Whatjobs_Ppc`, 29 `Talent_Dynamic-Ppc`, 13 `Indeed`, 9
`Lever_Co`, 9 `Radancy`, 6 `Buskeros`, 4 `Clasipar2`, …** The walk is
therefore **bounded by default** (`--pages 10`, 150 rows, and the note
says so); `--all` walks to the count and is compared. `www.buscojobs.com`
is the Uruguayan front under the bare name (`lang="es-UY"`, the same
count): it is a host, not a twenty-second country.

## The challenge is behavioural, and it was measured twice

Twenty-one fronts read in 80 seconds (23:31–23:32 UTC, two requests each)
left **five** answering the listing with **HTTP 405, 2 103 bytes titled
«Human Verification»** (AWS WAF, `gokuProps`, md5 moving between two
reads) while their root page was served; the Venezuelan front served
three listing pages and one ad, then challenged the fourth request of the
same minute. **Five minutes later, one request every 30 seconds: seven of
seven served, the Honduran listing included**; the four others were read
at 20 s (23:45–23:47). So: **20 s between requests, per host, is the
adapter's pace** — the figure the challenge answered — and a challenge met
on a walk prints what was emitted, names the page, and exits 7. It is not
defeated and nobody is asked to defeat it (borne 2).

## The rules

`/robots.txt` on `ve.buscojobs.com` (627 bytes, 2026-09-13): `ClaudeBot`
is named and refused `/` — a refusal that does not bind `Claude-User`
(decision of 2026-09-07); the `*` group refuses only `*.asp$`, `*.aspx$`
and `/ofertas/*fechainicio=` (and the `/jobs`, `/vagas`, `/offerte`
twins). The listing and the ad pages are under `*` and open, `certain:
True`. The guard is taken on the exact path before every request.

## What is withheld

The ad payload carries the employer's contact fields — `EmailEmpresa`,
`TelefonoEmpresa`, `NombreContactoEmpresa`, `EmailContactoEmpresa`,
`DireccionEmpresa`, `PaginaWebEmpresa` — **dropped before the record is
built**, and the `Empresa` object is reduced to its id and name; addresses
and phone numbers in the prose are replaced (`[e-mail withheld]`,
`[phone withheld]` — nine digits or more, so a date or a salary stays).
`EdadDesde`/`EdadHasta`/`Sexo` — an age band and a sex — are criteria this
project does not propagate (#183): not emitted. `Confidencial` employers
are emitted as `employer: null, confidential: true`. `SueldoDesde`/
`SueldoHasta` travel as `salary_min`/`salary_max` with **`salary_currency:
null`** — the payload names no unit and the front's country is not one.

## Invocation

```
buscojobs.py hosts                                          # the 22 hosts, their country and listing path
buscojobs.py list --host ve.buscojobs.com                   # 10 pages, 150 rows, bounded and said so
buscojobs.py list --host www.buscojobs.com.py --all         # to the count: 41 emitted, site states 41 — equal (2026-09-13)
buscojobs.py ad --url https://www.buscojobs.com.py/sales-manager-remoto-en-paraguay-ID-127138
```

Exits: 2 broken (an unknown host, a malformed URL) · 3 gone · 6 partial
(a walk short of the count, HTTP ≠ 200, a page without the payload) · 7
refused by the rules, or a challenge met · 8 rules undecidable.
