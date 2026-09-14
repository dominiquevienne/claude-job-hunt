# Board adapter — Trabajópolis (`www.trabajopolis.bo`, Bolivia): the root is served, every list route and the sitemap answer a robot challenge, and the terms of use forbid automated access in writing — measured 2026-09-14 from a tab: 1 141 advertisements stated and paged, a JobPosting per ad; the owner's decision: a browser route with a disclaimer said to the user when the board is enabled (#428)

<!-- verified: 2026-09-14 -->

<!-- hosts: www.trabajopolis.bo -->
<!-- script: none -->
<!-- countries: BO -->
<!-- content: measured · **the root answers 200 (418 KB, «Más de 115.000 ofertas de empleo gestionadas» — a lifetime claim, not a list count); every list route answers HTTP 403 with a 642 KB page titled «Trabajópolis - Trabajos en Bolivia» that says «debemos verificar que usted no es un robot … Enable JavaScript and cookies to continue», md5 moving between two reads of the same address (e33bc678400a / 57788834d653), and the page cites the terms of use: clause V.2 forbids access «mediante bots, arañas o cualquier medio automático»; `/buscar-trabajos`, `/empleos/la-paz`, `/categorias/informatica` and `/sitemap.xml` all answer that page (00:49–00:50 UTC)** · 2026-09-14 -->
<!-- witness: the list's own «Página N | 1141 ofertas de trabajo (1104 Abiertas, 37 Cerradas)» on `/recientes`, printed on every page and read on page 1 twice and on page 104 — 103 pages of 11 and a last of 8 = 1 141, equal to the statement; read from a connected tab (the declared client is challenged); the root's «115.000» is a lifetime claim, not this count · 2026-09-14 -->
<!-- route: browser · 1141 · 2026-09-14 -->
<!-- terms: forbids-automation · clause V.2 · 2026-09-14 -->

**What was measured, and what was not tried.** Issue #428 was opened
under #411 (Bolivia, never searched) on the root's «115.000 ofertas» — a
claim of the front page, not a list. On 2026-09-14, the declared client,
guard on the exact path:

| address | rules (`*` group) | answer |
| :-- | :-- | :-- |
| `/` | open | **200**, 418 KB — the front page; «✅ Más de **115.000 ofertas** de empleo gestionadas», beside «15 años» and «20.000 empresas»: a lifetime claim |
| `/buscar-trabajos` | open | **403**, 642 250 B then 642 247 B, **md5 moving** — the challenge page |
| `/empleos/la-paz` | open | 403, 642 220 B — the same page |
| `/categorias/informatica` | open | 403, 642 266 B — the same page |
| `/sitemap.xml` (named by `robots.txt`) | open | 403, 642 144 B — the same page, not XML |

The challenge page, in its own words: *«Disculpe la molestia, debemos
verificar que usted no es un robot … Enable JavaScript and cookies to
continue»*, then: *«nuestros términos de uso, en su cláusula V inciso 2,
prohíben explícitamente el acceso a Trabajopolis.bo mediante bots, arañas
o cualquier medio automático»* and clause V.1 and V.10 forbid copying the
ads to republish them elsewhere.

## Why there is no adapter, and why this is not «closed»

- **A challenge is borne 2**: it is not defeated, and nobody — the plugin's
  user included — is asked to defeat it. The browser branch of the
  2026-09-07 doctrine opens on a *static* refusal served to a client while a
  browser is served; it does not open on a page whose purpose is to tell a
  robot from a person. The md5 moves between two reads of the same address:
  the `revolico` family, not the `jobstore` family.
- **The refusal is also written**, not in `robots.txt` — whose `*` group
  refuses only `/find-jobs`, `/search-results-jobs`, `/resultados`,
  `/display-job`, `/oferta-de-trabajo-y-empleo-en-bolivia`, `/*searchId=*`…
  and leaves `/buscar-trabajos`, `/empleos/…`, `/categorias/…` open — but in
  the terms of use the challenge page quotes. A written intention is
  honoured by every route.
- **«Fermé» is the owner's word** (§2 sexies): this card records the
  measurement, dated, with the two md5 and the tool; the verdict that the
  host is closed to this project is the owner's to give, and #428 stays open
  until then. Bolivia's other boards are in its `country-search` table —
  #429 Trabajito, #430 Trabajando Bolivia, #431 BoliviaTrabajo, #432
  TumomoPegas, and `www.buscojobs.com.bo` (2 ads on the day) through
  `buscojobs.py`.

## The rules, for the record

`/robots.txt` (2026-09-14): nineteen named crawlers refused `/`; neither
`ClaudeBot` nor `Claude-User` among them; the `*` group refuses the routes
listed above plus `/api-proxy/v1/job/user-job-info`, `/html-dispatcher`
and `/js/stats/hit.js` — a SmartJobBoard-style platform. `Sitemap:
https://www.trabajopolis.bo/sitemap.xml`, which answers the challenge page
to the declared client.

## The owner's decision, 2026-09-14 04:4x UTC — a browser, with a disclaimer

Verbatim to the pilot: «&nbsp;4. navigateur avec disclaimer à l'utilisateur
lors de la souscription&nbsp;». Two consequences, one done here and one
waiting:

1. **The header line `terms: forbids-automation · clause V.2 · 2026-09-14`
   is declared on this card**, and `shared/setup.md` §5j reads it: when the
   user enables `trabajopolis`, the flow **says the clause** — the terms of
   use forbid access «&nbsp;mediante bots, arañas o cualquier medio
   automático&nbsp;» (V.2, read 2026-09-14 on the challenge page) — and that
   the reading happens **in the user's own browser, under the user's own
   responsibility**; a disclaimer, not a risk assessment; the user writes
   `boards.trabajopolis.terms_acknowledged: true` themselves or the board
   stays off, and the skip says why. The guard
   `ACardThatDeclaresForbiddingTermsIsSaidToTheUserAtEnabling` keeps the
   card and the flow together in both directions.
2. **The measurement, 2026-09-14 09:2x UTC, from a connected tab** — the
   extension answered later the same day: `route: browser · 1141 · 2026-09-14`
   (the section below).

## Browser reading, 2026-09-14 09:24–09:28 UTC (#428)

No challenge to a tab on any of these; the declared client gets the
642 KB «debemos verificar que usted no es un robot» page on the same
addresses (05:5x UTC of the day before, unchanged).

```
/buscar-trabajos           served — the search form; «1141 Empleos» printed beside it; the category and city facets link /categorias/<x> and /empleos/<city>
/empleos/cochabamba        served — «Página 1 | 110 ofertas de trabajo (107 Abiertas, 3 Cerradas)», ?page=N, cards /trabajo/<id>/<slug>
/recientes                 served — «Página 1 | 1141 ofertas de trabajo (1104 Abiertas, 37 Cerradas)», 11 cards a page, ?page=2 … ?page=104
/recientes?page=104        served — «Página 104 | 1141 …», 8 cards, no page 105: 103 × 11 + 8 = 1 141, equal to the statement
/trabajo/1238084/asesor-de-servicios   served — a JobPosting JSON-LD: title, description, datePosted / validThrough (30 days), employmentType, hiringOrganization («Toyosa S.A. - Sucursal Cochabamba»), identifier, jobLocation with region, directApply
```

**`route: browser · 1141 · 2026-09-14`.** The routes read — `/recientes`,
`/empleos/<city>`, `/trabajo/<id>/` — are not among the paths the rules
refuse (`/find-jobs`, `/search-results-jobs`, `/resultados`,
`/display-job`, `/*searchId=*`), so nothing written in `robots.txt` is
crossed; what the conditions of use forbid (clause V.2) is why this is a
browser route with the disclaimer of `setup.md` §5j and not a script.
What a session does from a tab: `/recientes?page=N` from 1 until the pager
ends, the id from `/trabajo/<id>/`, the count the page prints beside the
walk, the ad's JobPosting; closed ads («Cerradas», 37) are in the count
and marked on the card.

