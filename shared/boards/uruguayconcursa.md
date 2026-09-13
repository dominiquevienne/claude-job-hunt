# Board adapter — Uruguay Concursa (`www.uruguayconcursa.gub.uy`, Uruguay): the state's calls for candidates through the API its own page posts to — «Mostrando TODOS los Llamados Abiertos (363)», walked to the count and equal

<!-- verified: 2026-09-13 -->

<!-- hosts: www.uruguayconcursa.gub.uy -->
<!-- script: uruguayconcursa.py -->
<!-- host-forms: www.uruguayconcursa.gub.uy -->
<!-- host-forms-basis: read — `uruguayconcursa.py:HOST`, a single literal; the API and the public page `/llamado/<id>` are relative to it · 2026-09-13 -->
<!-- countries: UY -->
<!-- content: measured · **363 open llamados emitted by `uruguayconcursa.py list` over 8 pages of 50, and the API states `cntTotal` 363, its `Resultado` sentence ending «…los Llamados Abiertos (363)» — equal** (23:16 UTC, 363 distinct ids, page 1 ∩ page 2 = ∅); the unfiltered `find` states 42 217 (the archive, every status) and `recientes` 410; `get/?Llaid=42528` returns the very record `find` carried; `statuses` answers 404; `/robots.txt` unreadable → no written rule, `certain: False`, nothing refuses `/api-backend/` · 2026-09-13 -->
<!-- witness: the API's own `cntTotal` (and the «(N)» its `Resultado` sentence ends with), read on the first page of every walk and printed beside the emitted count — «363 emitted over 8 page(s), site states 363 — equal», exit 6 on a gap; a bounded walk (`--pages`/`--limit`) says so and is not compared · 2026-09-13 -->

**Uruguay's public service for state recruitment — the ONSC's portal of
«llamados a concurso» — and the first adapter of a country that had none
(#417 → #435).** The page is an Angular shell of 699 bytes; every list it
shows comes from `POST /api-backend/llamados/find`, and that is the route:
plain JSON, no key, no cookie, no browser.

## What the API states, and what the adapter emits

| question | answer on 2026-09-13 |
| :-- | :-- |
| `find` with `ListaLlaEstWeb: ["Abierto"]` | **«Mostrando TODOS los Llamados Abiertos (363)»**, `cntTotal` 363, `cntPaginas` 8 |
| `find` unfiltered | «Mostrando los Llamados que cumplen las condiciones de búsqueda (42217)» — **the archive**, 4 222 pages; `list --status all` walks it (≈ 42 min at 3 s) and is not the default |
| `recientes` (`PaginadoFiltrosSDT`) | 410 — a third count, recent across statuses, not used |
| `get/?Llaid=42528` | one record, **the same 33 fields as the list row** — `ad` reads it, adds nothing |
| `statuses` | **404** (44 B `{"error":{"code":404}}`) — the page falls back to its hard-coded list, so does the adapter (`Abierto`, `Inscripciones Cerradas`, `Finalizado UC`, `No Publicado`) |

The 363: **227 of the Universidad de la República, 81 of ASSE (public
health), 17 UTEC, 10 ANEP, 5 the Ministry of Economy** — the state as
employer, named on every record (`Inciso` · `UnidadEjecutora`). 252
records state posts per body (`listaOrganismoCantPuestos`, summed as
`positions`, 462 in all); 363 of 363 carry a closing date
(`LlaFchCieIns`, 2026-09-13 → 2027-06-01); **5 of 363 state a salary**,
and it is kept as the state writes it — «$60.610 nominales a valores de
Enero 2026» — in `salary_text`, never parsed into a number. Quota flags
(Afro 6, Trans 3) are emitted as `quotas`.

## What is withheld

The prose fields carry recruiters' addresses — **88 e-mail addresses in
the 50 records of page 1** (`LlaMedPos`, `LlaReqExc`, `LlaConTra`) — and
some carry phone numbers. `redact()` replaces both before anything is
emitted; the emitted 363 carry none. `LlaMedPos` («how to apply») is
reduced to `application: "www.uruguayconcursa.gub.uy"` when it names the
portal, null otherwise. **No contact leaves this adapter.**

## The route, and its rules

`/robots.txt` was unreadable on 2026-09-13 (the guard returns
`allowed=True, certain=False` — an absence of written rules under #283);
`/api-backend/llamados/find` and `/get/` are gated on their exact path
before every request. 3 s between requests is the adapter's own pace.
The guard's `None` (rules unreadable AND undecided) exits 8; a written
refusal, should one appear, exits 7.

## Invocation

```
uruguayconcursa.py list                       # the 363 open llamados, 8 pages, ~25 s
uruguayconcursa.py list --q enfermer --pages 1
uruguayconcursa.py list --status "Inscripciones Cerradas"
uruguayconcursa.py ad --url https://www.uruguayconcursa.gub.uy/llamado/42528
```

Exits: 2 broken · 3 gone (`get` returns no record or 404) · 6 partial
(a walk that does not reach the stated count, or a non-JSON answer) · 7
refused by the rules · 8 rules undecidable.
