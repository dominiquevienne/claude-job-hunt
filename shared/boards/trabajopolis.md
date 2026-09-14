# Board adapter — Trabajópolis (`www.trabajopolis.bo`, Bolivia): the root is served, every list route and the sitemap answer a robot challenge, and the terms of use forbid automated access in writing — measured 2026-09-14, no adapter, the owner's decision pending (#428)

<!-- verified: 2026-09-14 -->

<!-- hosts: www.trabajopolis.bo -->
<!-- script: none -->
<!-- countries: BO -->
<!-- content: measured · **the root answers 200 (418 KB, «Más de 115.000 ofertas de empleo gestionadas» — a lifetime claim, not a list count); every list route answers HTTP 403 with a 642 KB page titled «Trabajópolis - Trabajos en Bolivia» that says «debemos verificar que usted no es un robot … Enable JavaScript and cookies to continue», md5 moving between two reads of the same address (e33bc678400a / 57788834d653), and the page cites the terms of use: clause V.2 forbids access «mediante bots, arañas o cualquier medio automático»; `/buscar-trabajos`, `/empleos/la-paz`, `/categorias/informatica` and `/sitemap.xml` all answer that page (00:49–00:50 UTC)** · 2026-09-14 -->
<!-- witness: none — no list was ever served to the declared client, so no count of the site's own was read; the root's «115.000» is «ofertas … gestionadas» over fifteen years, not a count of live ads · 2026-09-14 -->
<!-- route: none · every list route and the sitemap answer a robot challenge (borne 2, not defeated, nobody asked to defeat it), and the terms of use forbid automated access in writing; the browser branch is not opened on a challenge — the owner decides whether this host is closed (§2 sexies) · 2026-09-14 -->

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

## If the owner decides otherwise

The day the owner rules that a browser may be pointed at this host, the
measurement is the same as any browser route (`route: browser · N · date`):
a tab on `/buscar-trabajos`, the count the list states, the walk to it. It
is not done here, because the page says what it is.
