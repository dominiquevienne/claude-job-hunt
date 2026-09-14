# Board measurement — Gallito Trabajo (`trabajo.gallito.com.uy`, Uruguay — El Libro de los Clasificados' job board): the provider's static 403 to the declared client, and a browser served the whole board — «738 Avisos activos» stated, `/buscar/page/N` 20 a page to page 37 (36 × 20 + 18 = 738, equal), a JobPosting per ad; `route: browser`, no script

<!-- verified: 2026-09-14 -->

<!-- hosts: trabajo.gallito.com.uy -->
<!-- script: none -->
<!-- countries: UY -->
<!-- content: measured · **the declared client gets the provider's static 403 (25 B, `9ccabba20b9f`, the `jobstore`/`hays` bytes) on the root — the rules open (`_robots.allowed('trabajo.gallito.com.uy','/')` → open, certain); a connected tab is served everything: the front page states «Más de 738 ofertas laborales para ti», «738 Avisos activos» (beside «1.185.861 Postulantes», «25.420 Empresas») and 14 areas; `/buscar` lists 20 advertisements a page with «Mostrando 1 de 738 resultados» and a pager `/buscar/page/2 … /37`; page 37 says «Mostrando 37 de 738 resultados», carries 18 and no page 38 — 36 × 20 + 18 = 738, equal to the statement; the areas are `/buscar/areas/<slug>`; each ad `/anuncio/<slug>-<5-char id>` carries a JobPosting JSON-LD — title, description, datePosted, validThrough (60 days), employmentType, hiringOrganization (the employer — «Soldent»), jobLocation — and prints the age («Hace 2 semanas») and «Avisos similares»; no page reached carried a recruiter line; the application («Postular») is the candidate account, never touched** · 2026-09-14 -->
<!-- witness: the site's own «738 Avisos activos» on the front page and «Mostrando N de 738 resultados» on every list page, read on page 1 and page 37 — 36 × 20 + 18 = 738, equal; nothing was served to the declared client, so no script prints anything · 2026-09-14 -->
<!-- route: browser · 738 · 2026-09-14 -->

**Gallito is Montevideo's classifieds house; its job board states 738
active advertisements on the day and pages them exactly.** Issue #436.
Measured 2026-09-14 09:33–09:37 UTC from a connected tab, after the
declared client's static 403 of 2026-09-13.

## What the client gets, and what a tab gets

```
_robots.allowed('trabajo.gallito.com.uy','/')   open, certain
client, GET /                                    403, 25 B, md5 9ccabba20b9f ×2 (2026-09-13) — the provider default seen on eleven hosts
tab, /                                           served — «738 Avisos activos», 14 areas, 5 recent ads /anuncio/<slug>-<id>
tab, /buscar                                     served — «Mostrando 1 de 738 resultados», 20 cards, pager /buscar/page/2 … /37
tab, /buscar/page/37                             served — «Mostrando 37 de 738 resultados», 18 cards, no page 38: 36 × 20 + 18 = 738
tab, /anuncio/odontologo-a-r9gqd                 served — a JobPosting: Soldent, 2026-09-13 → 2026-11-12
```

**`route: browser · 738 · 2026-09-14`.** What a session does from a tab:
`/buscar/page/N` from 1 until the pager ends, the id from the
`/anuncio/<slug>-<id>` tail, the page's «Mostrando N de M» beside the walk,
the ad's JobPosting. No script: nothing is served to a client (#404).
