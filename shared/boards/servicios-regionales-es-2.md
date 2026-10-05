# Board measurement — LABORA · SAE · Comunidad de Madrid (`labora.gva.es`, `saempleo.es`, `oficinavirtualempleo.comunidad.madrid`): three more of Spain's seventeen regional employment services — and the country page's "no common base observed" is now **refuted on the one layer that decides the route**: every service measured keeps its portal and its offers on **two different hosts**, the portal publishes long refusals and **the offers host publishes none**; on Valencia the refusal names five of this project's own tokens

<!-- verified: 2026-10-05 -->

<!-- hosts: labora.gva.es, www.gva.es, saempleo.es, www.juntadeandalucia.es, juntadeandalucia.es, oficinavirtualempleo.comunidad.madrid, www.comunidad.madrid, comunidad.madrid, empleocastillayleon.jcyl.es -->
<!-- script: none -->
<!-- countries: ES -->
<!-- host-forms-basis: nine host forms read, and they split into two populations that the brand name does not predict — the PORTALS publish rules and refuse a great deal (`www.gva.es` 2 366 B `state: read` `certain: True` with `Disallow: /` to five of this project's tokens; `www.juntadeandalucia.es` 8 794 B md5 87b7b7a803af `state: read` `certain: True` with 272 `Disallow` to `*`; `www.comunidad.madrid` 4 439 B md5 c40e9b2139f5 `state: read` `certain: True` with 95 `Disallow` and `Crawl-delay: 10`), while the OFFERS hosts publish nothing at all (`saempleo.es`, `oficinavirtualempleo.comunidad.madrid` and `empleocastillayleon.jcyl.es` all answer 404 on the rules file, so `state: absent`, `certain: True` — a knowledge and an open door under #283); `labora.gva.es` is the only one that answers no HTTP status at all — three attempts over 327 s on the rules file, `state: no-rules`, kind `no-rules-timeout`, `certain: False`, which is an absence of rules under #283, and then the ROOT times out too (`URLError: urlopen error timed out` at 45 s, after the module's own 10 s courtesy wait), so the transport is INDETERMINATE and not a refusal; the apex forms `juntadeandalucia.es` and `comunidad.madrid` both redirect to their `www`, so the guard records `www` as the host that answered · 2026-10-05 -->
<!-- content: measured · **577 adverts read from Andalucía in one POST and 314 rows served by Madrid, both on hosts whose portals' rules files never mention them — so the country page's «aucun socle commun observé» is REFUTED on the one layer that decides the route: 3 of the 3 services whose offers were reached keep the portal and the offers on DIFFERENT HOSTS, the portal refusing 272 and 95 and 39 paths while the offers host publishes none at all.** Three for three where the offers were reached: Andalucía's portal refuses 272 paths and its offers are on `saempleo.es` (no rules file); Madrid's portal refuses 95 and writes `Crawl-delay: 10` and its offers are on `oficinavirtualempleo.comunidad.madrid` (no rules file); and `empleocastillayleon.jcyl.es`, the second host the PREVIOUS card recorded as linked-but-not-read, also publishes no rules — so ECyL's 39 refusals, `*/SEResultadosBuscador17` included, bind a host its offers may not use. Neither portal's rules file mentions its own offers host. **AND THE SHARPEST CASE IS THE ONE WHERE THE REFUSAL NAMES US: `www.gva.es` publishes 2 366 B naming 93 agents, and five of them are this project's tokens — `anthropic-ai`, `claude-searchbot`, `claudebot`, `claude-web` and `claude-user` — each with `Disallow: /`.** That is the InfoJobs shape, the second host in Spain to close the class that fetches for a person and the first public administration in this repository to do so, and borne 1 therefore closes `www.gva.es` to every route including the browser. But it binds that host and not `labora.gva.es`, whose own rules file TIMES OUT (3 attempts, 327 s) and is therefore an absence of rules under #283 — open, `certain: False`, transport pending. **Reading the parent as the verdict would have declared the Valencian service closed to every route, and that verdict would have gone to the owner under §2 sexies.** ANDALUCÍA, WHICH IS THE CLEANEST ROUTE OF THE PASS AFTER EURES: the portal's own root carries a link whose TEXT is exactly «Ofertas de empleo» and whose href is ` https://saempleo.es/ags/candidaturas/lista-ofertas-publicas/lista?origin=portal ` — leading and trailing SPACES inside the attribute value, verbatim. That page is a 110 596 B Angular shell (`<app-root>`, `data-critters-container`, a Dynatrace agent whose config declares `domain=juntadeandalucia.es` while being served from `saempleo.es`) with `<base href="/ags/candidaturas/">`, four hashed bundles and 74 characters of visible text. **The `<base href>` trap met on the EURES portal, same pass and same day, with the OPPOSITE consequence: resolving `main.ab9d83fb3136ca25.js` against the page's directory returns 404 here, where EURES returned 200 with the shell — so the same mistake is loud on one host and silent on the other, and what protects is having recorded the shell's 110 596 B and md5 45cf3fef7928 BEFORE comparing.** The real bundle is 4 536 818 B and names three microservices (`MS-HERMES`, `MS-ALERTAS`, `MS-DATOS-MAESTROS`) and five hosts, two of which were NOT requested because they are plainly not public (`webint.sae.junta-andalucia.es`, and `ags-des.sae.junta-andalucia.es` with a Keycloak realm `empresa-des` — a development environment leaked into a production bundle; note also that `junta-andalucia.es` with a hyphen is a different registrable domain from `juntadeandalucia.es`). The endpoint was READ from the host's own config object rather than guessed — `hermes:{baseURL:"MS-HERMES/hermes", ofertasPublicadas:"ofertas/ofertaspublicadas"}` — and its own call site says `postListOffersPublicWeb(j){return this.httpClient.post(\`${this.baseUrl}/${…ofertasPublicadas}\`, j)}` with the caller passing **`{}`**: the app POSTs an EMPTY body and does all filtering, sorting and paging CLIENT-SIDE, re-POSTing only when its store is older than 9e5 ms. **A GET on that path returns 405 whose body names the path it RESOLVED (`/hermes/ofertas/ofertaspublicadas`), which is a better witness than a 404: it proves the composition was right while refusing the verb.** The POST of `{}` returns **200, 948 066 B, 577 adverts, 577 distinct `idOferta`, no duplicate** — no key, no account, no form, answered to the declared client. 22 keys; `salarioMensualBrutoMinimo` filled on **577/577** (min 76, median 1 487, max 3 770 EUR/month) which no other Spanish board in this repository manages, and the low tail is explained by the data rather than broken: **38 of the 39 adverts under 400 EUR carry `jornadaLaboral: PARCIAL`**; `puestosOfertados` sums **1 056** over 577 adverts (max 70, median 1, 158 adverts above one), so an advert is NOT a post — the third board of this pass in that case after Jobandtalent and EURES; `candidatosOrdenInscripcion` and `candidatosOrdenSAE` are present on 577 and non-empty on 313, and they are S/N FLAGS and not counters (read, not inferred from the name); `ubicacionesMultiples` and `ubicacionesItinerantes` are present on 577 and non-empty on 3 and 2; `discapacidad` is ABSENT on 234, `N` on 311, `S` on 32; `fechaInicio`/`fechaFin` are `DD-MM-YYYY HH:mm`, so string-sorting them is wrong and the bench printed the wrong order beside the right one to say so — read as dates, 355 distinct `fechaInicio` over 2026-09-18 → 2026-10-05 and **zero adverts already expired**, so this endpoint serves only live offers; nine provinces, the eight Andalusian ones plus ONE Madrid record, unexplained. MADRID: the portal's root offers exactly one employment link by text (`/empleo`), whose hub leads to `/empleo/busqueda-empleo`, whose link «Ofertas de empleo» points to `https://oficinavirtualempleo.comunidad.madrid/AreaPublica/Ofertas/` — 1 410 554 B for 62 261 characters of visible text, a `$("#tablaTodasOfertas").DataTable({…})` over **314 rows rendered server-side and paginated CLIENT-SIDE**, 314 distinct 12-digit identifiers, each advert linked exactly once so there is no dedup trap. Nine declared columns, measured against the HEADER rather than assumed — a first reading mis-attributed them because `Título` is empty on all 314: `Identificador` 314/314, **`Título` present 314 filled 0**, `Ocupación` 314/314 (170 distinct), `Fecha de publicacíon` 314/314 (67 distinct, **2025-11-03 → 2026-10-05, 336 days** — so unlike SAE this list is NOT limited to live offers), `Nivel formativo requerido` filled on **72/314**, `Localización` 314/314 (58 distinct), `Oficina de empleo` 314/314 (40 distinct), `Oculta discapacitados` filled on 9/314 with ONE distinct value. **No salary column at all** — so the two services that share an architecture share nothing of their record, which is «a shared template predicts the ROUTE, not the analysis» two layers up. AND MADRID'S REFUSALS BITE THE QUERY AND NOT THE PATH: of 95 `Disallow` (36 of them Drupal's stock file — the third stock Drupal file of this pass after empregoxunta.md and eures.europa.eu — and 59 proper to this host), 29 carry a `?`, and the guard was exercised both ways: `/info/servicios/educacion/ciencia-e-investigacion/buscador-empleo-idi` is PERMITTED while the same path with any query is REFUSED by `…buscador-empleo-idi?*`, likewise `/info/servicios/empleo/cursos?*`. So a route that pages through those searchers is closed in writing while their landing pages are open — a third variant of the refusal that lands on the results, after jcyl's path-based `*/SEResultadosBuscador17`. Note also that `/centros?f%5B0%5D=…` is permitted while `/centros/tipos-centro/` is refused: two spellings of one facet, one closed and one not. ANDALUCÍA'S REFUSALS HAVE A SHAPE NOBODY WOULD GUESS: 272 `Disallow` to `*` and 1 to `PetalBot`, and **219 of the 272 — 80.2 % — are individual dated articles of the official gazette** (`/boja/<year>/<issue>/<article>`, 33 distinct years from 1990 to 2026, 3 exact duplicates), withdrawn one at a time over decades. Of the 53 remaining, exactly three name an employment word, and two of those are BOLSAS: `/educacion/apl/consultabolsas/` and `…/paginas/bolsa-unica-comun` are refused in writing, which touches two OTHER lines of the country page (the health-service `bolsas` and the `oposiciones docentes`) before either has been measured. The third is `/empleo/www`, refused — and the guard confirms both directions: `/empleo/www` and `/empleo/www/buscador` False with that exact rule, `/empleo/` True. Eight of the 272 contain an unescaped SPACE. THREE SPECIES OF MALFORMED href, ALL UNDER 200 AND ALL SILENT: Andalucía writes leading and trailing spaces inside the attribute; Madrid's `/empleo` hub writes the LINK TEXT into the href with `https://` prepended, twice (`https://Catálogo de Especialidades Formativas de formación para el empleo`), so the host part is a Spanish sentence; and Madrid's virtual office writes a template ENGINE ERROR into one: `/Area1/MiDemanda/?id=Liquid error: Index was outside the bounds of the array.` A crawler that follows hrefs blindly makes three different nonsense requests and is told nothing. A FOURTH SILENT FAILURE, ON ECyL'S SECOND HOST: `empleocastillayleon.jcyl.es/oficinavirtual` answers 200 with 523 bytes whose whole content is `<meta http-equiv="REFRESH" content="0;url=index.do">` — an HTML-level redirect and not an HTTP one, so a client that traces only 3xx sees a tiny page and concludes there is nothing there. EXPURGATION, MEASURED BY FIELD AND AS A CENSUS: SAE's payload declares no `email`, no `telefono` and no `empresa`; its only free-text field is `textoLibreDifusion` (median 575 characters), and over **577 of 577 adverts — the complete set, not a sample** — it carries zero email addresses, zero runs of nine consecutive digits, zero `+34`, zero DNI/NIE shapes and zero URLs, while 36 adverts contain the words `teléfono`/`móvil`/`contacto` with no value beside them. So here a field-based rule reporting «nothing withheld» is TRUE, which is the exact inverse of jobtoday.md where the same rule reported nothing while coordinates and a named hiring manager shipped on 48 of 48 — and it is the first negative of this pass that is a census rather than an underpowered sample. **BUT THE SAME RULE WRITTEN WITHOUT A WORD BOUNDARY WOULD DESTROY MADRID: `\d{9}` unanchored matches the offer identifier on 314 of 314 adverts, and `(?<!\d)\d{9}(?!\d)` matches 0 of 314** — identical intent, identical field list, and a difference of 314 adverts on one board. That is the Burmese-kyat lesson moved off the monetary field and onto an IDENTIFIER, and the fix is the anchor rather than the field. TWO REGIONAL GOVERNMENTS DECLARE THEIR SITEMAP AS `http://<host>:80/sitemap.xml`: `www.gva.es` here and `inaem.aragon.es` in the previous card — http, with the default port written explicitly. One instance was a quirk; two is a shape, and nothing here depends on either. WHAT IS NOT ESTABLISHED: Madrid's board SIZE is not established — 314 rows are in the markup and the pagination is client-side, which is visible rather than inferred, but no total is announced anywhere on the page, so 314 is what was served and not a count the host confirms; LABORA's board is not measured at all, only its two hosts' rule states; the single Madrid record inside Andalucía's set is recorded and not explained; `index.do` on ECyL's second host was not followed; and the two non-public SAE hosts were deliberately not requested. METHOD: the guard was taken on every one of the nine host forms and on each exact path in turns distinct from the retrievals, and exercised in BOTH directions on both portals (`/buscar.html`, `/empleo/www`, `/educacion/apl/consultabolsas/`, `/search/`, `/buscador?f[0]`, and the two `?*` searchers all refused; the bare searcher paths, `/empleo`, `/sitemap.xml` and the API paths all permitted); DNS was resolved through two public resolvers for every host before any conclusion; the POST reproduces the four disciplines of `bin/fetch-body.py` (which is GET-only on `main` while #999 is open) and its refusal branch was exercised first on a path the guard refuses, writing nothing; `www.comunidad.madrid`'s written 10 s was applied to every request to it and our own 2 s elsewhere, no host writing any other delay; and the readability of every body was checked before any conclusion of absence, the detector being exercised in both directions on both real corpora (0.000 against 1.000, over 419 and 300 possible leads, so the negative is exercised and not a 0/0 default)** · 2026-10-05 -->

<!-- witness: partial — SAE's 577 adverts are the host's own complete response to an empty filter and its app pages them client-side, so there is no page-versus-total question to answer there and no count is claimed beyond what one POST returned; MADRID HAS NO WITNESS: 314 rows were served, the DataTables pagination is client-side, and the page announces no total anywhere — so its board size is NOT established and this card says so rather than publishing 314 as a count; LABORA produced no advert at all · 2026-10-05 -->

## Measured 2026-10-05 — the portal refuses, the offers live next door, and next door publishes nothing

```
LE SOCLE COMMUN QUE LA PAGE PAYS DISAIT ABSENT — 3 fois sur 3 mesurees

  communaute     PORTAIL (regles longues)        OFFRES (aucune regle)
  Andalousie     www.juntadeandalucia.es         saempleo.es
                   272 Disallow a *                404 -> state absent, certain
  Madrid         www.comunidad.madrid            oficinavirtualempleo.
                   95 Disallow, Crawl-delay 10      comunidad.madrid
                                                   404 -> state absent, certain
  Castille-Leon  empleo.jcyl.es  (fiche prec.)   empleocastillayleon.jcyl.es
                   39 Disallow dont le moteur       404 -> state absent, certain
                   de RESULTATS

  et AUCUN des trois fichiers de regles ne mentionne son propre hote d'offres
```

```
VALENCE — le cas ou le refus NOUS NOMME, et ou il ne lie pas le bon hote

www.gva.es         2 366 o, state read, certain TRUE
  93 agents nommes, dont CINQ des jetons de ce projet :
    anthropic-ai · claude-searchbot · claudebot · claude-web · CLAUDE-USER
  chacun  Disallow: /        -> borne 1 : ferme a TOUTES les voies, navigateur compris
  Sitemap: http://www.gva.es:80/sitemap.xml      <- http, port par defaut explicite

labora.gva.es      4 adresses A, deux resolveurs d'accord — le NOM resout
  robots.txt       AUCUN statut HTTP, 3 tentatives, 327 s
                   state no-rules · kind no-rules-timeout · certain FALSE
                   -> absence de regles (#283) : ouvert, le transport decide ensuite
  la racine        URLError: urlopen error timed out, a 45 s, apres les 10 s
                   de courtoisie que le module s'impose sur un no-rules-timeout
                   -> INDETERMINE au transport, et un indetermine n'est pas un refus
  la page pays le notait injoignable le 31.08.2026 ; mesure de nouveau le 05.10.2026,
  depuis une autre session, le NOM resolvant chez deux resolveurs publics.
  Donc ce n'est pas le nom : c'est le transport, et ca fait deux observations
  a 35 jours d'ecart. C'est la forme que la decision du proprietaire du 18.09.2026
  nomme — « un hote national dont le transport n'aboutit pas » — et pour laquelle
  elle prescrit un ticket `blocked` motive plutot qu'une issue assignable.

  Lire le refus du PARENT comme le verdict aurait declare le service valencien
  ferme a toutes les voies — et ce verdict serait parti au proprietaire (§2 sexies).
  `robots.txt` lie un HOTE, pas une marque, et ici le refus nomme notre propre jeton.
```

```
ANDALOUSIE — la route la plus propre de la passe apres EURES

le portail                 lien dont le TEXTE est « Ofertas de empleo »
  href tel qu'ecrit        " https://saempleo.es/ags/candidaturas/..."
                           espaces en tete ET en fin, dans l'attribut
saempleo.es                coquille Angular 110 596 o, md5 45cf3fef7928
  <app-root>               74 caracteres de texte visible
  <base href>              "/ags/candidaturas/"   <- PAS le repertoire de la page
  agent Dynatrace          domain=juntadeandalucia.es, servi depuis saempleo.es

le piege du <base href>, et son issue OPPOSEE a celle d'EURES
  main.js resolu contre le REPERTOIRE   -> 404, 196 o        ici, bruyant
  main.js resolu contre <base href>     -> 200, 4 536 818 o  le vrai
  (EURES rendait 200 AVEC LA COQUILLE : meme faute, aucun symptome)
  ce qui protege : avoir note 110 596 o AVANT de comparer

l'endpoint LU dans la configuration de l'hote, jamais devine
  hermes.baseURL           "MS-HERMES/hermes"
  hermes.ofertasPublicadas "ofertas/ofertaspublicadas"
  son propre appelant      postListOffersPublicWeb({})   <- corps VIDE
                           filtre, tri et pagination COTE CLIENT

GET  /ags/api/MS-HERMES/hermes/ofertas/ofertaspublicadas
  -> 405, et le corps nomme le chemin RESOLU : /hermes/ofertas/ofertaspublicadas
     un 405 qui nomme sa resolution vaut mieux qu'un 404 : il prouve la composition
POST le meme chemin, corps {}
  -> 200, 948 066 o, 577 annonces, 577 idOferta DISTINCTS, aucun doublon
```

```
ANDALOUSIE — les 22 cles, PRESENT contre REMPLI sur 577

salarioMensualBrutoMinimo   577/577   min 76 · mediane 1 487 · max 3 770 EUR/mois
  la queue basse s'EXPLIQUE              39 sous 400 EUR, dont 38 en jornada PARCIAL
puestosOfertados            577/577   somme 1 056, max 70, mediane 1
  -> une ANNONCE n'est pas un POSTE     158 annonces portent plus d'un poste
  (3e board de la passe : jobandtalent 117/149, EURES 50/156, SAE 577/1 056)
candidatosOrden{Inscripcion,SAE}  present 577, non vide 313
  et ce sont des DRAPEAUX S/N, pas des compteurs — lu, pas deduit du nom
ubicacionesMultiples        present 577, non vide   3
ubicacionesItinerantes      present 577, non vide   2
discapacidad                ABSENT 234 · N 311 · S 32
fechaInicio / fechaFin      DD-MM-YYYY HH:mm  -> le tri en CHAINE est faux
  le banc imprime le mauvais ordre A COTE du bon pour le dire
  lus comme dates            355 fechaInicio distinctes, 18-09 -> 05-10-2026
  annonces deja expirees     0 sur 577  -> l'endpoint ne sert que du vivant
provinces                   9 : les 8 andalouses + UN enregistrement MADRID
                            consigne, pas explique
```

```
MADRID — 314 lignes servies, paginees COTE CLIENT, et aucun total annonce

www.comunidad.madrid       95 Disallow (36 du socle Drupal, 59 propres), 32 Allow
                           Crawl-delay: 10        <- 2e hote de la passe a en ecrire
                           Sitemap declare sur l'APEX, qui redirige vers www
  29 des 95 portent un `?`, et le refus mord la REQUETE et pas le CHEMIN :
    /...­/buscador-empleo-idi            PERMIS
    /...­/buscador-empleo-idi?page=0     REFUSE   par `...buscador-empleo-idi?*`
    /info/servicios/empleo/cursos?*     REFUSE
  et deux orthographes d'une meme facette :
    /centros?f%5B0%5D=...               PERMIS
    /centros/tipos-centro/              REFUSE

la chaine d'entree, trouvee par le TEXTE et jamais devinee
  /                 -> un seul lien d'emploi par le texte : « Empleo » -> /empleo
  /empleo           -> « Búsqueda de empleo » -> /empleo/busqueda-empleo
  /empleo/busqueda- -> « Ofertas de empleo »  -> oficinavirtualempleo.comunidad.madrid
                                                  /AreaPublica/Ofertas/

oficinavirtualempleo       1 410 554 o pour 62 261 caracteres de texte  (95,6 % de
                           gabarit) · $("#tablaTodasOfertas").DataTable({...})
  315 <tr>                 1 en-tete + 314 annonces
  314 identifiants         12 chiffres, 314 DISTINCTS, chaque annonce liee UNE fois
  AUCUN total annonce      -> la taille du board n'est PAS etablie

les 9 colonnes declarees, mesurees contre l'EN-TETE et non supposees
  Identificador               314/314    314 distincts
  Titulo                      314/  0    declaree, jamais remplie
  Ocupacion                   314/314    170 distinctes
  Fecha de publicacion        314/314     67 distinctes · 03-11-2025 -> 05-10-2026
                                         336 JOURS : pas seulement du vivant
  Nivel formativo requerido   314/ 72
  Localizacion                314/314     58 distinctes
  Oficina de empleo           314/314     40 distinctes
  Oculta discapacitados       314/  9     UNE seule valeur distincte
  (sans en-tete)              314/  0     la colonne d'action

et AUCUNE colonne de salaire — l'architecture est commune, le registre ne l'est pas
```

```
TROIS ESPECES DE href MALFORME, toutes sous 200, toutes muettes

Andalousie        " https://saempleo.es/ags/... "     espaces DANS l'attribut
Madrid /empleo    "https://Catálogo de Especialidades Formativas de ..."  x2
                  le TEXTE du lien colle dans le href, hote = une phrase espagnole
Madrid oficina    "/Area1/MiDemanda/?id=Liquid error: Index was outside the
                   bounds of the array."
                  une erreur de MOTEUR DE GABARIT rendue comme une URL

et une QUATRIEME defaillance silencieuse, sur le second hote d'ECyL
empleocastillayleon.jcyl.es/oficinavirtual   200, 523 o
  tout son contenu : <meta http-equiv="REFRESH" content="0;url=index.do">
  une redirection HTML et non HTTP -> un client qui ne trace que les 3xx
  voit une page minuscule et conclut qu'il n'y a rien
```

```
EXPURGATION — par CHAMP, et ici en RECENSEMENT et non en echantillon

la charge de SAE ne declare ni `email`, ni `telefono`, ni `empresa`.
son seul champ de texte libre : textoLibreDifusion, mediane 575 caracteres
  sur 577 sur 577 — l'ENSEMBLE COMPLET, pas un echantillon :
    une adresse de courriel            0 / 577
    neuf chiffres consecutifs ancres   0 / 577
    un prefixe +34                     0 / 577
    une forme de DNI/NIE               0 / 577
    une URL                            0 / 577
    les mots telefono/movil/contacto  36 / 577   sans aucune VALEUR a cote

  donc ici « rien n'a ete retenu » est VRAI — l'inverse exact de jobtoday.md,
  ou la meme regle ne rapportait rien pendant que des coordonnees et le nom
  d'un recruteur partaient sur 48 sur 48.
  et c'est le premier negatif de la passe qui soit un RECENSEMENT.

MAIS LA MEME REGLE SANS FRONTIERE DE MOT DETRUIRAIT MADRID
  \d{9}            NON ancre   ->  314 / 314 identifiants d'offre touches
  (?<!\d)\d{9}(?!\d)  ancre    ->    0 / 314
  meme intention, meme liste de champs, 314 annonces d'ecart sur un board.
  la lecon du kyat deplacee du champ MONETAIRE vers un IDENTIFIANT :
  ce qui repare n'est pas la liste des champs, c'est l'ANCRE.
```

```
ANDALOUSIE — la forme de ses 272 refus, que personne ne devinerait

272 Disallow au groupe *          1 Disallow au groupe PetalBot          1 Allow
  219 des 272 — 80,2 % — sont un ARTICLE DATE du journal officiel
    /boja/<annee>/<numero>/<article>   33 annees distinctes, 1990 -> 2026
    3 doublons exacts
  8 des 272 contiennent un ESPACE non echappe (/export/drupaljda/almeria agosto)
  sur les 53 restants, TROIS nomment un mot d'emploi — et deux sont des BOLSAS :
    /educacion/apl/consultabolsas/                     REFUSE
    /.../paginas/bolsa-unica-comun                     REFUSE
    /empleo/www                                        REFUSE
  -> ce refus touche DEUX AUTRES lignes de la page pays — les `bolsas` sanitaires
     et les `oposiciones docentes` — avant que l'une ou l'autre soit mesuree.
  garde eprouvee dans les deux sens : /empleo/www et /empleo/www/buscador False
  avec cette regle exacte, /empleo/ True.
```

## What this card does not say

No advert was read on LABORA, and its board is not measured: its rules file and
its root both time out, which is an INDETERMINATE and a measurement to retake
rather than a verdict on the board (§2 sexies) — and the only thing established
about the Valencian service is the rule state of its two hosts. Madrid's board SIZE is not established: 314 rows were served,
the pagination is client-side and that is visible in the markup rather than
inferred, but the page announces no total, so 314 is what was served and not a
count the host confirms. The single Madrid record inside Andalucía's 577 is
recorded and not explained. `index.do` on ECyL's second host was not followed.
And the two SAE hosts that are plainly not public — `webint.sae.junta-andalucia.es`
and `ags-des.sae.junta-andalucia.es` — were named by the bundle and deliberately
not requested.

**This is six of seventeen, and the socle found here is architectural, not
formal.** Knowing that a community keeps its offers on a separate unruled host
predicts where to look; it predicts nothing about what will be there. Andalucía
publishes a salary on every advert and Madrid publishes no salary column at all,
on the same architecture — which is «a shared template predicts the ROUTE, not
the analysis», two layers above the template. The health-service `bolsas` and
the `oposiciones docentes` remain on a different axis again, and the one thing
now known about them is a refusal written against two of their paths.
