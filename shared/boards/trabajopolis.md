# Board adapter — Trabajópolis (`www.trabajopolis.bo`, Bolivia): the root is served, every list route and the sitemap answer a robot challenge, and the terms of use forbid automated access in writing — measured 2026-09-14; the owner's decision: a browser route with a disclaimer said to the user when the board is enabled (#428)

<!-- verified: 2026-09-14 -->

<!-- hosts: www.trabajopolis.bo -->
<!-- script: none -->
<!-- countries: BO -->
<!-- content: measured · **the root answers 200 (418 KB, «Más de 115.000 ofertas de empleo gestionadas» — a lifetime claim, not a list count); every list route answers HTTP 403 with a 642 KB page titled «Trabajópolis - Trabajos en Bolivia» that says «debemos verificar que usted no es un robot … Enable JavaScript and cookies to continue», md5 moving between two reads of the same address (e33bc678400a / 57788834d653), and the page cites the terms of use: clause V.2 forbids access «mediante bots, arañas o cualquier medio automático»; `/buscar-trabajos`, `/empleos/la-paz`, `/categorias/informatica` and `/sitemap.xml` all answer that page (00:49–00:50 UTC)** · 2026-09-14 -->
<!-- witness: none — no list was ever served to the declared client, so no count of the site's own was read; the root's «115.000» is «ofertas … gestionadas» over fifteen years, not a count of live ads · 2026-09-14 -->
<!-- route: none · a browser route is the owner's decision of 2026-09-14 04:4x UTC («navigateur avec disclaimer à l'utilisateur lors de la souscription») and is not measured yet — a tab on the list, once the extension answers, gives `route: browser · N · date`; until then every list route answers a robot challenge to the declared client (borne 2, not defeated, nobody asked to defeat it) and nothing is rendered · 2026-09-14 -->
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
2. **The measurement waits for the extension**: a tab on `/buscar-trabajos`,
   the count the list states, a stable key, a JobPosting or not — then
   `route: browser · N · date` replaces the `route: none` line above. Not done
   here: the extension did not answer this session.
