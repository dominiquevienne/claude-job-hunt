# Board measurement — PIVOT (`www.pivot.com.py`, Paraguay): a Nuxt shell in front of a JSF/PrimeFaces application on `app.pivot.com.py:8080` — the declared client gets an empty frame with a session id, a connected tab gets «Mostrando 1-12 de 920 avisos de empleo»; `route: browser`, no script

<!-- verified: 2026-09-16 -->

<!-- hosts: www.pivot.com.py, app.pivot.com.py -->
<!-- script: none -->
<!-- countries: PY -->
<!-- content: measured · **`/robots.txt` 404 on `www.` (no rules, certain); the root (200, 80 957 B, identical to the 13.09 read) is a Nuxt shell — `#nuxt-loading`, no card, links to `https://app.pivot.com.py:8080/AvisosEmpleos/` and to the JSF menu `Empleos/faces/app/menu/MainEmpleos.xhtml`; `app.pivot.com.py:8080/AvisosEmpleos/` (200, 9 197 B) is a page with one iframe, `faces/appLib/lib/runProcedure1.xhtml?…paraProcName=/app/update/EmpleosBrw.xhtml`; that frame (200, 9 643 B) is a PrimeFaces 12 page with a `jsessionid`, a ViewState and no row — the list arrives by the application's partial-submit POSTs, stateful, bound to the session; a connected tab on 2026-09-16 06:23 UTC was served the browse: «Mostrando 1-12 de 920 avisos de empleo», a pager 1 … 10 ⏭ and a per-page selector (12), cards with the title, «Localidad», «Área Ocupacional», «Ocupación», «Aviso #» (58316 …), «Días publicados» and a «Más información» button that opens a dialog — «Cargo ofrecido», «Localidad/Ciudad», «Perfil/Funciones/Requisitos», «Área laboral», «Aviso #» — with NO employer and no contact on the ad (the «vidriera» is anonymised; «Solicitar este empleo» is a candidate account)** · 2026-09-16 -->
<!-- witness: the browse's own «Mostrando 1-12 de 920 avisos de empleo», read from a connected tab · 2026-09-16 -->
<!-- route: browser · 920 · 2026-09-16 -->

**Issue #433 (opened under #415, Paraguay searched on 2026-09-13). Measured
2026-09-16 06:22–06:24 UTC — the declared client by `bin/fetch-body.py`,
the guard on the exact path (no rules file: open, certain), then a
connected tab.** Rank: the pilot's risk order of 2026-09-14 10:4x, after
Bolivia's three (#429, #430, #432).

## What the client gets — a shell, a frame, a session, no row

```
GET https://www.pivot.com.py/robots.txt                 404, 4 790 B — no rules
GET https://www.pivot.com.py/                           200, 80 957 B, md5 751bf4eab823 (identical to 2026-09-13)   Nuxt: «Loading...», no card
GET https://app.pivot.com.py:8080/AvisosEmpleos/         200,  9 197 B   one <iframe src="faces/appLib/lib/runProcedure1.xhtml?…paraProcName=/app/update/EmpleosBrw.xhtml">
GET …/AvisosEmpleos/faces/appLib/lib/runProcedure1.xhtml?…EmpleosBrw.xhtml
                                                         200,  9 643 B   PrimeFaces 12, jsessionid in every resource URL, ViewState, 0 <tr>, title «Título de la faceta»
```

**The list is not a route the page calls: it is a JavaServer Faces
conversation** — the browse table is filled by partial-submit POSTs that
carry the session's ViewState, and every later page of the pager is another
such POST on the same session. *That is a stateful application, not an
address; the plugin replays a URL the page calls (the 14.09 judgment on
StaffPoint and Eezy), it does not drive a server-side session.* No `/api/`,
no sitemap (none declared, none found), no JSON-LD.

## What a tab gets — the whole board

```
tab, https://app.pivot.com.py:8080/AvisosEmpleos/    served — «Mostrando 1-12 de 920 avisos de empleo», pager 1 … 10 ⏭, per-page selector (12 ▾)
     a card                                          AUDITOR SENIOR · Localidad: Fernando de la Mora · Área Ocupacional: Contabilidad y Auditoría · Ocupación: Auditor Senior · Aviso #: 58316 · Días publicados: 1 · «Más información»
     «Más información»                                a dialog «Detalles del Aviso de Empleo»: Cargo ofrecido, Localidad/Ciudad, Perfil/Funciones/Requisitos (a bulleted text), Área laboral, Aviso #; «Solicitar este empleo» (an account), «Cancelar»
```

**`route: browser · 920 · 2026-09-16`.** What a session does from a tab:
open `app.pivot.com.py:8080/AvisosEmpleos/`, read «Mostrando … de N» as the
count, raise the per-page selector, page through the PrimeFaces pager, read
each card (the id is «Aviso #»), open «Más información» for the requirements
text. **The ad carries no employer and no contact** — the board is a
«vidriera», the employer is behind the application — so there is nothing to
withhold beyond the candidate account, never touched.

## What this card does not say

Nothing about the employers (not published); nothing about the ads' dates
beyond «Días publicados» (a relative age). «+800» on the marketing root is
the site's claim; 920 is the browse's own figure on the day.
