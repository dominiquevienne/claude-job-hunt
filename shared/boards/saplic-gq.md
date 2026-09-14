# Board measurement — Saplic Guinea Ecuatorial (`saplic.com/gq`, Equatorial Guinea): the provider's static 403 to the declared client, and a browser served the board — «25 vacantes activas» stated on 2026-09-14, ten listed and a «Ver Más» that did not extend in the tab, the employers' pages summing to 24; `route: browser`, no script

<!-- verified: 2026-09-14 -->

<!-- hosts: saplic.com -->
<!-- script: none -->
<!-- countries: GQ -->
<!-- content: measured · **the declared client gets the provider's static 403 (25 B, `9ccabba20b9f`, the `jobstore`/`hays` bytes — the GNQ country search of 2026-09-13, #422); a connected tab is served: `/gq` states «25 VACANTES ACTIVAS» and «13 EMPRESAS CONTRATANDO» («En Guinea Ecuatorial hay actualmente 25 vacantes activas de 13 empresas»), nine categories with counts (Administración y Oficina 6, Contabilidad y Finanzas 4, Docencia 3 … — 25 in all), ten «Oportunidades» cards, the cities (Malabo 23) and twelve employers with their counts (Chevron 4, GITGE 4, CONEXXIA 2, Fundación IDENTIC 2, Gecotel 2, GEPetrol Seguros 2, GEPsing 2, KGE KITEA 2, AIMUGE 1, Clínica Jacobo Hanna 1, Sector Alimentario 1, AAUCA 1 — 24); `/busqueda-ofertas-empleo.php?pais=86` («Empleos en Guinea Ecuatorial — 25 vacantes activas») lists ten cards `/empleo/<slug>-<id>` (ids 2733 … 2754: title, employer, «Presencial», «Malabo, Guinea Ecuatorial») and a «Ver Más» link that did not add a row after three clicks in the tab; the per-city page `/gq/empleos-en/malabo` and the employer pages `/empresa/<slug>` are the other routes to the rest; a Saplic front exists per country (`?pais=<id>`, 86 for Equatorial Guinea) — the same platform, «IP Geolocation by DB-IP» choosing the front; the application is a candidate account (`/ingresar-oferente.php`), never touched** · 2026-09-14 -->
<!-- witness: the site's own «25 vacantes activas» on `/gq` (twice on the page) and in the list page's title, read from a connected tab at 10:07–10:10 UTC; ten rendered on the list, the load-more inert in the tab; the employers' counts sum to 24; nothing is served to the declared client, so no script prints anything · 2026-09-14 -->
<!-- route: browser · 25 · 2026-09-14 -->

**Saplic's Equatorial Guinea front is the country's one job board found by
the search of 2026-09-13 (#422) — 25 active vacancies stated, thirteen
employers, Malabo almost all of it.** Measured 2026-09-14 10:07–10:10 UTC
from a connected tab, after the declared client's static 403; named by
the pilot as a browser candidate without an issue («une route navigateur
mesurée est livrée sans issue», the 13.09 decision).

## What the client gets, and what a tab gets

```
client, GET /gq                              403, 25 B, md5 9ccabba20b9f ×2 (2026-09-13) — the provider default seen on eleven hosts
tab, /gq                                     served — «25 VACANTES ACTIVAS», «13 EMPRESAS CONTRATANDO», 9 categories (25), 10 cards, 12 employers (24)
tab, /busqueda-ofertas-empleo.php?pais=86    served — title «25 vacantes activas»; 10 cards /empleo/<slug>-<id>; «Ver Más» (href="#") inert after three clicks
tab, /gq/empleos-en/malabo, /empresa/<slug>  named, not read — the city (23) and the employers (24) as the second route to the rest
```

**`route: browser · 25 · 2026-09-14`** — the site's own count; the walk
from a tab reached ten on the list and would take the employers' pages for
the rest. What a session does from a tab: `/busqueda-ofertas-empleo.php?pais=86`
and «Ver Más» while it adds rows, else the twelve `/empresa/<slug>` pages;
the id from the `/empleo/<slug>-<id>` tail; the ad page for its fields.
No script: nothing is served to a client (#404).
