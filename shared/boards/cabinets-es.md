# Board measurement — Spain's specialist recruiters (Hays · Robert Walters · Spring Professional): **467 adverts enumerable on one, a captcha on the second, and no DNS delegation at all on the third** — and the «does the sibling-country adapter transpose?» question answered in BOTH directions against two adapters this repository already ships

<!-- verified: 2026-10-05 -->

<!-- hosts: www.hays.es, hays.es, www.robertwalters.es, robertwalters.es, springprofessional.es, www.springprofessional.es, springprofessional.com -->
<!-- script: none -->
<!-- countries: ES -->
<!-- host-forms-basis: three firms and three rule states that could not differ more — `www.hays.es` read, 7 196 B, md5 05eb5d588c6c, `certain: True`, **24 user-agent groups**: `*` with 52 `Disallow`, **69 `Allow`** and `Crawl-delay: 10`, then 23 named-bot groups of which 18 get `Disallow: /` (trovitBot, spbot, seoscanners, SiteExplorer in four spellings, ltx71, ScoutJet, Feedly, Arquivo-web-crawler, a DomainAppender UA written out in full, Siteimprove…) and 6 get only a `Crawl-delay: 10` — among them `JobCrawlerBot` and `InnovantageBot`, the latter carrying the directive TWICE — and **no token of this project is named anywhere**, so we fall under `*` and `identity()` returns `claude-user` / `http`; `www.robertwalters.es` read, 27 837 B, md5 a11f1dfb5735, `certain: True`, **233 `Disallow` and ZERO `Allow`**, no `Crawl-delay`, one sitemap declared — and nothing in those 233 touches our path, so the guard permits `/` and `/sitemap.xml`, *which is exactly why what the transport does next matters*; `springprofessional.es` and `www.springprofessional.es` answer **NXDOMAIN on all six record types (A, AAAA, NS, SOA, MX, CNAME) from BOTH public resolvers** — no delegation at all, so there is no rules file to have a state; `springprofessional.com` resolves (NOERROR, 149.232.252.3) and its rules file is `no-rules-connection` after 3 attempts (`Errno 61 Connection refused`), `certain: False` · 2026-10-05 -->
<!-- content: measured · **467 adverts in a declared job sitemap on Hays, a PerimeterX captcha on the ROOT of Robert Walters, and NXDOMAIN on six record types for Spring Professional — three firms of one country-page line, three outcomes, nothing in common.** AND THE TRANSPOSITION QUESTION IS ANSWERED BOTH WAYS, WHICH IS THE POINT OF MEASURING THESE TOGETHER: this repository ships `hays.py` for France and `randstad.py` for Switzerland, and the same question — *does the sibling-country adapter apply?* — has OPPOSITE answers. **`www.hays.es` declares `https://www.hays.es/sitemap/es-ES/job-sitemap.xml`, which is `hays.py`'s French route with ONE SEGMENT SWAPPED** (`fr-FR` → `es-ES`), and that sitemap answers 200 with **343 977 B, 467 `<url>` blocks, 467 `<loc>` all distinct**. So the ROUTE transposes mechanically. **But the CODE does not: `hays.py` hard-codes `BASE = "https://www.hays.fr"` AND `SITEMAP = BASE + "/sitemap/fr-FR/job-sitemap.xml"`, with no host and no locale option** — and a third constant does not transpose at all: `AD_RE = /description-emploi/(.+)$`, while the Spanish adverts live at **`/detalles-vacante/<slug>_<id>`**. *So of the three constants, two swap by locale and one must be rewritten — which is a parameter problem.* **Against that, `randstad.py` is a rewrite: `BASE` is equally hard-coded, the Swiss advert shape is `/jobs/<slug>_<uuid>/` against Spain's `/candidatos/ofertas-empleo/oferta/<slug>-<id>/`, and the Swiss route PAGES `/jobs/page-N/` where Spain declares an offers sitemap — a different enumerator, not a different string.** *The discriminant is therefore whether the URL SHAPE is shared, not whether the brand is — and the brand is shared in both cases.* **AND THE CDATA TRAP `hays.py` DOCUMENTS FOR FRANCE IS PRESENT ON THE SPANISH HOST, MEASURED: all 467 `<loc>` are wrapped in `<![CDATA[ … ]]>`, so the naive `<loc>([^<]+)</loc>` returns ZERO on a 343 977-byte sitemap** — a board that appears to publish nothing, under 200, with a clean parse and no error. *The module's own comment names the invariant that catches it — «a sitemap with dates and no URLs is impossible» — and here the figures are **467 `<lastmod>` against 0 naive `<loc>`**, so the invariant fires. Finding the same vendor trap on a sibling locale is the strongest form this confirmation can take: the prior card's warning, re-measured on a host it never saw.* THE HAYS DATING IS GENUINE, WHICH IS THE OPPOSITE OF WHAT THE STAFFING SIDE SHOWED: **467 `lastmod` carrying 457 DISTINCT values from 2026-07-06T09:19 to 2026-10-02T14:15 — 88 days — and ZERO equal to the second OR the minute of my own request.** *Per-advert dating, so an incremental walk restricts for real.* AND ITS RULES FILE CARRIES A WHITELIST INSIDE A BLACKLIST, WHICH DECIDES A ROUTE: `/busqueda-empleo*` is REFUSED to `*`, and then **68 of the 69 `Allow` lines name employment**, each a complete faceted URL of the form `/busqueda-empleo/<speciality>-empleos-en-<city>-spain` (atención al cliente, construcción, … × Madrid, Barcelona, Bilbao, Sevilla, Valencia). **So a walker that reads `/busqueda-empleo*` as closed skips 68 paths the operator opened BY HAND.** *The guard was exercised nine ways and reads it correctly — longest match wins, `Allow` on a tie: the bare path and an unlisted facet are refused by `/busqueda-empleo*`, each hand-listed facet is permitted by its own longer rule, the advert path `/detalles-vacante/…` is permitted with no rule in the way, and `/detalles-vacante/*/candidatura`, `/Job/Detail/*` and `/jobs-search/` are refused.* Its file also carries **17 exact duplicate `Disallow` lines** and declares **four** sitemaps. **ROBERT WALTERS: THE RULES PERMIT AND THE TRANSPORT REFUSES — AND THE REFUSAL IS A CAPTCHA, SO BORNE 2 STOPS HERE.** `/sitemap.xml` and the **ROOT** both answer **403 with 5 998 B**, and three fetches gave **three different md5s at identical length** (7cb90c5f27b5 / 61b8ecd5a4d8 / 961daad2ca82). *Locating the differing offsets — 84 bytes in 12 runs — shows a per-request **`Reference ID` UUID** repeated four times in the page, which is precisely why «fetch twice before comparing any fingerprint» exists: this body cannot be compared against another host's.* The page's title is **«Access to this page has been denied»**, its visible text is **«Please verify you are a human … because we believe you are using automation tools»**, and it contains **`captcha` 23 times and `PerimeterX` 5 times**, served from a Varnish/Fastly edge (`x-served-by: cache-fra-…`). **So this is an anti-robot control, borne 2 forbids answering it and forbids asking a candidate to, and the browser branch the 2026-09-07 decision would otherwise open is closed for the same reason.** *Second interstitial of this pass after Milanuncios — that one was «Pardon Our Interruption» under HTTP 200, this one is PerimeterX under 403, so the vendor page and the status both differ and the borne does not.* **`route: none` here is DATED and expected to be replaced**: revolico and emploi-cm were each challenged on one day and served to a tab on another. **Nothing is declared closed** (§2 sexies: an anti-robot control is a limit of route, never a verdict on a board). Its 233 refusals are also worth one line for what they are: **100 of the 233 contain an unescaped SPACE** — four times Andalucía's eight and fifty times Euskadi's two — and their content is AEM (`/content/dam/robert-walters-redesign/country/<country>/files/…`) withdrawing **Australian job-description templates and Chilean «hot-candidates» PDFs from a SPANISH host**, which is a global file served per country rather than a Spanish policy. **SPRING PROFESSIONAL: THE HOST THE COUNTRY PAGE NAMES DOES NOT EXIST.** `springprofessional.es` answers **NXDOMAIN** — not `SERVFAIL`, not `NOERROR` with no `A` — **on A, AAAA, NS, SOA, MX and CNAME, from both 1.1.1.1 and 8.8.8.8**, and so does its `www`. *There is no delegation, so there is no rules file and no state to record: the page's list has aged.* `springprofessional.com` does resolve and then **refuses the connection** (`Errno 61`, 3 attempts, `no-rules-connection`, `certain: False`). **AND IT IS NOT DECLARED A SUCCESSOR: a guess that resolves is not a discovery, and nothing read says this `.com` serves Spain** — the `.es` host told us nothing because it answered nothing. *Nor does it get a `blocked` ticket: the owner's decision of 18.09.2026, as he extended it on 06.10 (#1021, verbatim «oui, c'est la même règle»), covers a public employment service **national or regional**, and these are PRIVATE firms — extending it a third time would be exactly the over-generalisation that was flagged rather than assumed on LABORA.* WHAT IS NOT ESTABLISHED: **no advert page was fetched on any of the three, so no per-advert field shape is known and no salary, employer or location claim is made.** Hays's **467 is the count its own declared sitemap carries**, which is the host's enumerator and not our extraction — but it is not cross-checked against any total the site states, so it is reported as «467 in the declared job sitemap» and never as «the board holds 467». *Robert Walters produced no advert and no count by any route; Spring Professional produced none and has no host.* METHOD: DNS resolved through two public resolvers for every host form before any conclusion, and the Spring Professional negative QUALIFIED by record type and rcode rather than read off an empty answer; the guard taken on all three hosts and on each exact path in turns distinct from the retrievals and exercised in BOTH directions; Hays's written **10 s** applied to every request to it and our own 2 s on the others; the Robert Walters refusal fetched TWICE on the same path before any fingerprint was compared, and the root fetched separately because the verdict on a board is taken at the root and a refusal on a sitemap would only have had the scope of that sitemap; the CDATA-aware patterns taken from `hays.py` rather than rewritten, and the naive pattern run beside them to MEASURE what the CDATA costs · 2026-10-05 -->

<!-- witness: partial — Hays's 467 adverts come from the job sitemap its own `robots.txt` declares, so the enumerator is the host's and not ours and every `<loc>` is distinct; but **no total stated by the site was found to check it against**, so «467 in the declared job sitemap» is what is claimed and not a board size. Robert Walters yielded nothing by any route — rules open, root 403 behind a captcha, borne 2 — and Spring Professional has no host to yield anything · 2026-10-05 -->

## Measured 2026-10-05 — three firms, three outcomes, and nothing in common

```
LA QUESTION QUE CES TROIS POSENT ENSEMBLE : L'ADAPTATEUR DU PAYS FRERE
TRANSPOSE-T-IL ? — et la reponse est OPPOSEE selon la marque

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

```
HAYS ESPAGNE — 467 annonces, et le motif NAIF en rend ZERO

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
ET SON FICHIER PORTE UNE LISTE BLANCHE DANS UNE LISTE NOIRE — ca decide une route

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
ROBERT WALTERS — les regles PERMETTENT, le transport sert un CAPTCHA

robots.txt         27 837 o  md5 a11f1dfb5735  read, certain TRUE
  groupe * UNIQUE  233 Disallow · ZERO Allow · aucun Crawl-delay
  aucune des 233 ne vise notre chemin -> la garde PERMET / et /sitemap.xml
  100 des 233 portent un ESPACE non echappe
    (4x les 8 de l'Andalousie, 50x les 2 d'Euskadi)
  leur contenu : AEM, /content/dam/robert-walters-redesign/country/<pays>/files/
    des modeles de fiche de poste AUSTRALIENS et des PDF « hot-candidates »
    CHILIENS — retires depuis un hote ESPAGNOL : un fichier GLOBAL servi par pays

le transport, et la RACINE autant que le sitemap
  /sitemap.xml   403   5 998 o   md5 7cb90c5f27b5
  /sitemap.xml   403   5 998 o   md5 61b8ecd5a4d8   <- DEUX lectures du MEME chemin
  /              403   5 998 o   md5 961daad2ca82   <- la RACINE aussi
  84 octets different en 12 intervalles : un « Reference ID » UUID PAR REQUETE,
  repete quatre fois dans la page
  -> empreinte MOUVANTE : ce corps ne se compare a aucun autre hote

ce que la page EST
  titre            « Access to this page has been denied »
  texte visible    « Please verify you are a human … we believe you are using
                     automation tools to browse the website »
  captcha x23 · PerimeterX x5 · servi depuis un bord Varnish/Fastly

  BORNE 2 : on ne repond jamais a un controle antirobot et on ne le demande
  jamais a un candidat — donc la voie navigateur que la decision du 07.09
  ouvrirait est fermee pour la MEME raison.
  `route: none` est DATE et attendu comme remplacable (revolico, emploi-cm).
  RIEN n'est declare ferme (§2 sexies).

  Deuxieme interstitiel de la passe : Milanuncios servait « Pardon Our
  Interruption » sous 200, celui-ci est PerimeterX sous 403 — la page du
  fournisseur et le statut diffèrent, la borne non.
```

```
SPRING PROFESSIONAL — l'hote que la page pays NOMME n'existe pas

springprofessional.es        A AAAA NS SOA MX CNAME  ->  NXDOMAIN
www.springprofessional.es    les six aussi           ->  NXDOMAIN
  sur 1.1.1.1 ET 8.8.8.8     ni SERVFAIL, ni NOERROR-sans-A : AUCUNE delegation
  -> pas de fichier de regles, donc aucun etat a consigner. La liste a vieilli.

springprofessional.com       NOERROR, 149.232.252.3
  robots.txt                 no-rules-connection, 3 tentatives
                             Errno 61 — Connection refused, certain FALSE

  ET IL N'EST PAS DECLARE SUCCESSEUR : une devinette qui resout n'est pas une
  decouverte, et rien de ce qui a ete lu ne dit que ce `.com` sert l'Espagne.
  Ni ticket `blocked` : la decision du 18.09, telle que le proprietaire l'a
  etendue le 06.10 (#1021, « oui, c'est la meme regle »), couvre un service
  public de l'emploi NATIONAL OU REGIONAL. Ce sont des cabinets PRIVES.
```

## What this card does not say

**No advert page was fetched on any of the three**, so no per-advert field shape
is known and nothing is claimed about salary, employer or location.

**Hays's 467 is the count its own declared sitemap carries** — the host's
enumerator, not our extraction, and every `<loc>` distinct. But no total stated
by the site was found to check it against, so «467 in the declared job sitemap»
is the claim and «the board holds 467» is not.

Robert Walters yielded nothing by any route: its rules permit us, its root
answers 403 behind a PerimeterX captcha, and borne 2 ends it there — for the
browser as well as for the declared client. Spring Professional has no host in
Spain to yield anything, and the `.com` that resolves refuses the connection.

**And the transposition lesson cuts both ways, which is why it is worth having
measured:** two adapters this repository already ships, the same question, and
opposite answers — so «the brand is covered elsewhere» predicts nothing, and the
thing to look at is whether the URL shape and the enumerator are shared.
