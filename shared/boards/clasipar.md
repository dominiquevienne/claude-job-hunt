# Board adapter — Clasipar, category Empleos (`clasipar.paraguay.com`, Paraguay): a classifieds where «Busco» is the job offer, the category's «Búsqueda y postulación de Empleos (562)» as the witness — and every page is a fresh random draw, so one pass reads 364 of 562 and says so

<!-- verified: 2026-09-14 -->

<!-- hosts: clasipar.paraguay.com -->
<!-- script: clasipar.py -->
<!-- host-forms: clasipar.paraguay.com -->
<!-- host-forms-basis: read — `clasipar.py:HOST`, a single literal · 2026-09-14 -->
<!-- countries: PY -->
<!-- content: measured · **one pass over the 23 pages by `clasipar.py list --all --mode all` (01:55–02:06 UTC, the site answering in ~25 s a page) read 570 cards and 364 distinct ids — 142 «Busco» (employers looking) and 222 «Ofrezco» (workers offering) — against the category page's «Búsqueda y postulación de Empleos (562)»: 198 short, exit 6, because every page is a fresh random draw (page 3 read twice five seconds apart shares one card of 25); the menu says «Empleos (1.248)» on the category page and «Empleos (900)» on the list — printed, not compared; one ad read** · 2026-09-14 -->
<!-- witness: the category page's own «Búsqueda y postulación de Empleos (N)», read before the walk and printed beside the distinct count — «N read over P page(s), category states N (… «busco» emitted, … «ofrezco» passed over) — equal / short», exit 6 on a gap with the cause named; the default walk is bounded (`--pages 10`) and says so, `--all` walks the pager, `--passes N` walks it N times and grows the union · 2026-09-14 -->

**A classifieds, two ways round, and a pager that deals cards at random.**
`/categorias/empleos` states **«Búsqueda y postulación de Empleos (562)»**
— its own count of the job section (the menu beside it says «Empleos
(1.248)», and «Empleos (900)» on the list page minutes later: the site's
figures, written differently on two of its pages, printed and not
compared). The list `/empleos`, `/empleos/page-<p>` (23 pages) serves
`article.box-anuncio` cards: the link `/empleos/<sub>/<slug>-<id>`, the
title, a price («Gs. 4.200.000», text), **«Busco» or «Ofrezco»**,
«Ofrecido por: Particular», the subcategory and town, the advertiser's
page when it has one. **«Busco» is an employer looking for someone;
«Ofrezco» is someone offering their work** — the default emits «Busco»
only and says how many «Ofrezco» were passed over; `--mode all` emits
both with `mode`. Issue #434 (Paraguay, #415).

## The pages are a random sample, not a sequence

`/empleos/page-3` read twice five seconds apart: 25 cards each, **one in
common**, a different order. A full pass over the 23 pages read 570 cards
and **364 distinct ids** — 198 short of 562 — while the same pages read
minutes apart overlap by one to four cards. Every page is a fresh draw of
the category. The adapter dedups across pages, compares the distinct
count to the category's, **exits 6 and names the cause**; `--passes N`
walks the pager N times and grows the union — the expected number of
draws to see every ad is the coupon-collector's (≈ 562 · ln 562 ≈ 3 600
cards, some 145 pages), not the pager's 23. The sitemap index lists
1 611 site-wide ad sitemaps (every category, `ads1…ads1611.xml.gz`) — not
a route to 562. The JS filter form (`ads_list`, a token, a POST) is the
site's own paging and is never posted.

```
364 read over 23 page(s), category states 562 (142 «busco» emitted, 222 «ofrezco» passed over) — 198 short (every page is a fresh random draw of the category — one pass cannot reach the count; --passes N grows the union).
```

## Watermarks, and the contact behind a button

Every title and description is interleaved with spans styled
`font-size:0 !important` — «Encontrá todo lo que buscas en Clasipar.com»,
«Los mejores anuncios clasificados de Autos los encontrás en
Clasipar.com», **«Fuente del anuncio: <url>»** — invisible to a reader,
poison to a copy; they are removed before any text is read (a title read
without the strip would carry the site's own URL in its middle). **The ad
page masks the advertiser's phone and e-mail («*********»,
«*******@********») behind «MOSTRAR LOS DATOS DE CONTACTO»** — a button
this project never presses; what survives in the prose is replaced
(`[e-mail withheld]`, `[phone withheld]`). The ad page carries the
details — Ciudad, Nro. de Anuncio, Zona, Publicado el (dd/mm/yyyy → ISO)
— the price as text and the description.

## The rules

`/robots.txt` (199 bytes, 2026-09-14): `*` refuses `/error/`, `/app/`,
`/config-paper/`; `bingbot` and `ia_archiver` refused `/`; a sitemap index.
Open, `certain: True`; the guard is taken on the exact path before every
request; 3 s own spacing (the site itself answered in 3 to 25 s).

## Invocation

```
clasipar.py list                              # 10 pages, «Busco» only, bounded and said so
clasipar.py list --all                        # the 23 pages once: 364 distinct of 562 on 2026-09-14, exit 6, the cause named
clasipar.py list --all --passes 3 --mode all  # three draws, the union grows
clasipar.py list --sub ventas --all           # one subcategory, walked on its own, not compared
clasipar.py ad --url https://clasipar.paraguay.com/empleos/administracion/buscamos-encargado-administrativo-de-edificio-2959281
```

Exits: 2 broken (a malformed URL) · 3 gone (404, or no «Detalle de») · 6
partial (a pass short of the count — the normal case here, said so —,
HTTP ≠ 200, a category that states no count) · 7 refused by the rules ·
8 rules undecidable.
