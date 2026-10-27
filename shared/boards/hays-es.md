# Board measurement — Hays España: **467 adverts enumerable in the job sitemap its own `robots.txt` declares**, a whitelist inside a blacklist that opens 68 hand-listed facets, and the CDATA trap of `hays.py` confirmed on a host that module never saw

<!-- verified: 2026-10-05 -->

<!-- hosts: www.hays.es, hays.es -->
<!-- script: none -->
<!-- countries: ES -->
<!-- host-forms-basis: `www.hays.es` read, 7 196 B, md5 05eb5d588c6c, `certain: True`, **24 user-agent groups**: `*` with 52 `Disallow`, **69 `Allow`** and `Crawl-delay: 10`, then 23 named-bot groups of which 18 get `Disallow: /` (trovitBot, spbot, seoscanners, SiteExplorer in four spellings, ltx71, ScoutJet, Feedly, Arquivo-web-crawler, a DomainAppender UA written out in full, Siteimprove…) and 6 get only a `Crawl-delay: 10` — among them `JobCrawlerBot` and `InnovantageBot`, the latter carrying the directive TWICE — and **no token of this project is named anywhere**, so we fall under `*` and `identity()` returns `claude-user` / `http`. Its file also carries **17 exact duplicate `Disallow` lines** and declares **four** sitemaps · 2026-10-05 -->
<!-- content: measured · **467 adverts in the job sitemap this host's own `robots.txt` declares, and the NAIVE `<loc>` pattern returns ZERO on it.** `https://www.hays.es/sitemap/es-ES/job-sitemap.xml` answers 200 with **343 977 B, 467 `<url>` blocks, 467 `<loc>` all distinct** — and all 467 are wrapped in `<![CDATA[ … ]]>`, so `<loc>([^<]+)</loc>` rends **ZERO**: a board that appears to publish nothing, under 200, with a clean parse and no error. *The invariant `hays.py` names catches it — «a sitemap with dates and no URLs is impossible» — and here the figures are **467 `<lastmod>` against 0 naive `<loc>`**, so it fires. Finding the same vendor trap on a sibling locale is the strongest form this confirmation can take: the module's warning, re-measured on a host it never saw.* **AND THE DATING IS GENUINE: 467 `lastmod` carrying 457 DISTINCT values from 2026-07-06T09:19 to 2026-10-02T14:15 — 88 days — and ZERO equal to the second OR the minute of my own request**, so per-advert dating, and an incremental walk restricts for real. **AND ITS RULES FILE CARRIES A WHITELIST INSIDE A BLACKLIST, WHICH DECIDES A ROUTE:** `/busqueda-empleo*` is REFUSED to `*`, and then **68 of the 69 `Allow` lines name employment**, each a complete faceted URL of the form `/busqueda-empleo/<speciality>-empleos-en-<city>-spain` (atención al cliente, construcción, … × Madrid, Barcelona, Bilbao, Sevilla, Valencia). **So a walker that reads `/busqueda-empleo*` as closed skips 68 paths the operator opened BY HAND.** *The guard was exercised nine ways and reads it correctly — longest match wins, `Allow` on a tie: the bare path and an unlisted facet are refused by `/busqueda-empleo*`, each hand-listed facet is permitted by its own longer rule, the advert path `/detalles-vacante/…` is permitted with no rule in the way, and `/detalles-vacante/*/candidatura`, `/Job/Detail/*` and `/jobs-search/` are refused.* **AND THE SIBLING-ADAPTER QUESTION IS ANSWERED HERE, AGAINST THE TWO ADAPTERS THIS REPOSITORY SHIPS, AND THE ANSWERS ARE OPPOSITE:** this host declares `hays.py`'s French route with ONE SEGMENT SWAPPED (`fr-FR` → `es-ES`), so the ROUTE transposes mechanically — **but the CODE does not: `hays.py` hard-codes `BASE = "https://www.hays.fr"` AND `SITEMAP = BASE + "/sitemap/fr-FR/job-sitemap.xml"`, with no host and no locale option** — and a third constant does not transpose at all: `AD_RE = /description-emploi/(.+)$`, while the Spanish adverts live at **`/detalles-vacante/<slug>_<id>`**. *So of the three constants, two swap by locale and one must be rewritten — a PARAMETER problem.* **Against that, `randstad.py` is a REWRITE: its `BASE` is equally hard-coded, the Swiss advert shape is `/jobs/<slug>_<uuid>/` against Spain's `/candidatos/ofertas-empleo/oferta/<slug>-<id>/`, and the Swiss route PAGES `/jobs/page-N/` where Spain declares an offers sitemap — a different enumerator, not a different string.** *The discriminant is therefore whether the URL SHAPE is shared, not whether the brand is — and the brand is shared in both cases, so «the brand is covered elsewhere» predicts nothing.* WHAT IS NOT ESTABLISHED: **no advert page was fetched**, so no per-advert field shape is known and nothing is claimed about salary, employer or location. The **467 is the count this host's own declared sitemap carries** — the host's enumerator and not our extraction — and it is **not** cross-checked against any total the site states, so «467 in the declared job sitemap» is the claim and «the board holds 467» is not. METHOD: DNS resolved through two public resolvers for every host form before any conclusion; the guard taken on the host and on each exact path in turns distinct from the retrievals and exercised in BOTH directions; the host's written **10 s** `Crawl-delay` applied to every request; the CDATA-aware patterns taken from `hays.py` rather than rewritten, and the naive pattern run beside them to MEASURE what the CDATA costs · 2026-10-05 -->

<!-- witness: partial — the 467 adverts come from the job sitemap this host's own `robots.txt` declares, so the enumerator is the host's and not ours and every `<loc>` is distinct; but **no total stated by the site was found to check it against**, so «467 in the declared job sitemap» is what is claimed and not a board size · 2026-10-05 -->

## Split out of a grouped card on 2026-10-27 — #1205

This card and its two siblings — `robertwalters-es.md` and `springprofessional-es.md` — were **one** card declaring **seven** host forms on a single `hosts:` line. The three firms were never in the same state, so no single card could tell the truth about all three: a verdict that fitted one was false of the others. **Nothing measured here changed in the split**; the dates, the figures and the method are those of 2026-10-05.

## Measured 2026-10-05

```
robots.txt            7 196 o  md5 05eb5d588c6c  read, certain TRUE
  24 groupes user-agent
  groupe *            52 Disallow · 69 Allow · Crawl-delay: 10
  18 robots nommes    Disallow: /   trovitBot, spbot, seoscanners, ltx71,
                      ScoutJet, Feedly, Arquivo-web-crawler, SiteExplorer
                      (quatre orthographes), Siteimprove, DomainAppender…
  6 robots nommes     Crawl-delay: 10 SEULEMENT — dont JobCrawlerBot et
                      InnovantageBot, qui le porte DEUX fois
  aucun jeton de ce projet n'est nomme -> on tombe sous *, qui permet
  17 Disallow en DOUBLON exact · 4 sitemaps declares

/sitemap/es-ES/job-sitemap.xml      200, 343 977 o
  <url>                             467
  <loc>  motifs de hays.py          467, 467 DISTINCTS, tous en CDATA
  <loc>  motif NAIF ([^<]+)         ZERO
  -> un board qui PARAIT ne rien publier, sous 200, analyse propre, sans erreur
     et l'invariant que hays.py nomme TIRE : 467 <lastmod> contre 0 <loc> naifs
     « un sitemap avec des dates et zero URL est impossible »

  <lastmod>                         467, 457 DISTINCTS
                                    2026-07-06T09:19 -> 2026-10-02T14:15, 88 jours
  egaux a la seconde de ma requete  0        a la minute  0
  -> datation PAR ANNONCE, donc un rebalayage incremental restreint vraiment
```

```
UNE LISTE BLANCHE DANS UNE LISTE NOIRE — ca decide une route

  /busqueda-empleo*                                            REFUSE a *
  puis 68 des 69 Allow nomment l'emploi, chacune une URL COMPLETE :
  /busqueda-empleo/<specialite>-empleos-en-<ville>-spain
    atencion-al-cliente, contruccion, … x madrid, barcelona, bilbao,
    sevilla, valencia

  Donc un marcheur qui lit `/busqueda-empleo*` comme ferme saute 68 chemins
  que l'exploitant a ouverts A LA MAIN.

garde eprouvee NEUF fois, et elle lit juste (match le plus long, Allow a egalite)
  /busqueda-empleo                                         False  /busqueda-empleo*
  /busqueda-empleo/contable            (non listee)        False  /busqueda-empleo*
  /busqueda-empleo/atencion-al-cliente-empleos-en-madrid-spain
                                                           TRUE   sa propre Allow
  /busqueda-empleo/contruccion-empleos-en-bilbao-spain     TRUE   sa propre Allow
  /detalles-vacante/demand-planner-barcelona_1129636       TRUE   aucune regle
  /detalles-vacante/x/candidatura                          False  sa regle exacte
  /Job/Detail/42                                           False  /Job/Detail/*
  /jobs-search/                                            False  /jobs-search/
  /sitemap/es-ES/job-sitemap.xml                           TRUE   aucune regle
```

```
L'ADAPTATEUR DU PAYS FRERE TRANSPOSE-T-IL ? — repondu dans les DEUX sens

HAYS      la ROUTE transpose, le CODE non
  l'hote declare   https://www.hays.es/sitemap/es-ES/job-sitemap.xml
  hays.py          BASE    = "https://www.hays.fr"            en dur
                   SITEMAP = BASE + "/sitemap/fr-FR/job-sitemap.xml"   en dur
                   AD_RE   = /description-emploi/(.+)$
  l'annonce ES     /detalles-vacante/<slug>_<id>
  -> DEUX constantes se permutent par locale, la TROISIEME doit etre reecrite
     c'est un probleme de PARAMETRE

RANDSTAD  ni l'une ni l'autre
  randstad.py      BASE = "https://www.randstad.ch"           en dur
  l'annonce CH     /jobs/<slug>_<uuid>/
  l'annonce ES     /candidatos/ofertas-empleo/oferta/<slug>-<id>/
  la route CH      pagine /jobs/page-N/     la route ES  declare un sitemap
  -> un ENUMERATEUR different, pas une chaine differente : c'est une REECRITURE

  LE DISCRIMINANT est que la FORME D'URL soit partagee, pas que la MARQUE le soit
  — et la marque l'est dans les deux cas.
```

## What this card does not say

**No advert page was fetched**, so no per-advert field shape is known and nothing is claimed about salary, employer or location.

**The 467 is the count this host's own declared sitemap carries** — the host's enumerator, not our extraction, and every `<loc>` distinct. But no total stated by the site was found to check it against, so «467 in the declared job sitemap» is the claim and «the board holds 467» is not.
