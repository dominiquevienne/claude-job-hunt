# Board measurement — TMCARS — vacancies (`tmcars.info/others/rabota/vakansii`, Turkmenistan): **the HTTP route reaches 150 adverts of the 15 278 the host declares — 0,98 % — and no URL addresses the rest**: `?offset=`, `?page=` and the twenty city prefixes are all accepted and all inert, the host's only pager being a single Next.js server action, while `/api/` is refused in writing; and the card's own «более 17132» has fallen to 15 278 in nineteen days

<!-- verified: 2026-10-06 -->

<!-- hosts: tmcars.info -->
<!-- script: none -->
<!-- countries: TM -->
<!-- content: measured · **150 ANNONCES SERVIES SUR 15 278 DÉCLARÉES — 0,98 %, ET LE RESTE N'A AUCUNE ADRESSE URL.** Mesuré le 2026-10-06 entre 00:51 et 00:58 UTC, garde prise sur chaque chemin exact dans des tours distincts et éprouvée dans les DEUX sens. *`/others/rabota/vakansii` rend 200 et 1 133 411 o — **141 KB DE MOINS** que les 1 274 078 du 2026-09-17 — et c'est une application Next.js à composants serveur (`self.__next_f` ×24, charge décodée de 484 922 caractères).* **L'HÔTE DÉCLARE SES TROIS NOMBRES DANS SA PROPRE CHARGE, donc le témoin n'est pas notre extraction : `totalCount` 15 279, `perPage` 150, `offset` 0 — et notre extraction rend EXACTEMENT 150 annonces, 150 identifiants distincts, zéro échec de parse, soit le `perPage` que l'hôte annonce.** *Et `totalCount` est passé de 15 279 à 15 278 **entre deux de mes requêtes espacées de cinq minutes**, donc ce nombre porte son heure à la minute ou il ne se publie pas.* **LA PAGINATION N'EST PAS UNE URL&nbsp;: c'est `"loadMore":"$h49"`, UNE SEULE référence d'action serveur dans toute la charge — aucun `href` ne porte `page`, `offset` ni `p=` dans le HTML ni dans la charge.** Trois adresses ont été essayées avec la prédiction écrite AVANT la mesure, et les trois rendent 200 avec les **MÊMES 150 identifiants** (150/150 communs, 0 nouveau), `offset: 0` et le même `canonical` `https://tmcars.info/others/all/rabota/vakansii`&nbsp;: `?offset=150`, `?offset=15270` (qui devrait rendre 9 si l'offset était honoré) et `/ashgabat/others/rabota/vakansii`. **ET LE PRÉFIXE DE VILLE EST VALIDE ET POURTANT INERTE, ce qui est pire qu'un catch-all&nbsp;: mon hypothèse de catch-all a été RÉFUTÉE par son contrôle — `/zzz-pas-une-ville/others/rabota/vakansii` rend **404** (360 397 o), donc l'hôte RECONNAÎT `ashgabat` et refuse un premier segment inventé, et sur le chemin reconnu il sert quand même les VINGT villes (Ашхабад 87, Туркменабат 21, Мары 11, Дашогуз 8 sur 150) au lieu d'une seule.** *Donc un adaptateur qui marcherait les vingt miroirs de ville émettrait les mêmes 150 annonces vingt fois — un sur-comptage ×20 sans aucune erreur, sur une route que l'hôte valide.* **ET LE « miroir par ville `/ashgabat/…` (более 6 175) » QUE CETTE FICHE PORTAIT DEPUIS LE 17.09 EST RÉFUTÉ&nbsp;: cette URL sert la page NON filtrée. La forme `/others/<ville>/rabota/vakansii`, qui aurait filtré, rend 404 (331 901 o pour `ashgabat`, 331 893 pour `mary`).** *`/api/` est refusé PAR ÉCRIT au groupe `*` (143 o de règles&nbsp;: `Allow: /` puis `Disallow:` sur `/profile/`, `/api/`, `/chat/`, `/tmcars/` — l'hôte refuse un chemin portant son propre nom), donc la borne 1 ferme cette route à TOUTES les voies&nbsp;; et la page ne la demande jamais — « api » n'apparaît que DEUX fois dans 1,13 Mo. Garde éprouvée dans les deux sens&nbsp;: 5 chemins ouverts avec `rule=None`, 7 refusés chacun par sa règle étroite (`/api/v1/ads` → `/api/`, `/profile/login` → `/profile/`).* **UNE SENTINELLE QUE CE DÉPÔT N'AVAIT PAS&nbsp;: `"$undefined"`, l'encodage RSC de `undefined`, **654 fois** dans la charge — et elle a défait MON PROPRE test de champ réel, qui n'excluait que `undefined`/`null`/`none` et a donc compté `isLiked`, `videoExist` et `badgeLabel` « réels sur 150 » alors que `badgeLabel` ne porte une valeur que **2 fois sur 150** et les deux autres JAMAIS.** *Le `$` suffit à passer sous la liste de sentinelles que ce dépôt a écrite, et le faux rendu est un 150 confiant.* **ET `price` DONNE QUATRE NOMBRES POUR UNE QUESTION&nbsp;: 150 présents, 96 non nuls, 88 vrais au sens de `if x`, 54 explicitement `None`.** *Un champ PRÉSENT n'est pas un champ REMPLI, et `vip` le montre dans l'autre sens&nbsp;: booléen réel, 150 « remplis » et **26** vrais.* **LE SLUG N'EST PAS UN IDENTIFIANT, ET C'EST LE PIÈGE DE YORA À L'ENVERS&nbsp;: 150 annonces portent **108** slugs distincts — `isgar-gerek` en couvre **23** et `isgar` 12 — donc un dédoublonnage par slug perd 42 annonces sur 150 (28 %), là où l'identifiant numérique en rend 150.** *Chez Yora quatre URL désignaient un objet (sur-comptage ×4 par la langue)&nbsp;; ici vingt-trois objets partagent une clé (sous-comptage par la clé de dédoublonnage), et le préfixe de ville en fait un troisième (×20). Même famille — « l'identifiant n'est pas ce qu'il paraît » — trois directions.* **LA FORME D'UNE ANNONCE DE LISTE, quatorze champs mesurés un à un&nbsp;: `id` (entier), `name`, `href` `/others/<id>/<slug>`, `image`, `price` (ou `None`), `vip` (booléen), `description` (un extrait — 73 caractères sur l'exemple), `cityName`, `elapsedTime`, `reviewEnabled`, `reviewCount`, `badgeLabel`, `isLiked` et `videoExist` (ces deux-ci `$undefined` partout).** *AUCUN champ ne nomme un contact et il n'y a NI `JobPosting` NI `ItemList`&nbsp;: les trois seuls blocs JSON-LD sont `WebSite`, `Organization` et `BreadcrumbList` — et la chaîne `application/ld+json` apparaît SIX fois pour trois blocs, parce que la charge RSC la répète, donc compter la chaîne aurait annoncé six blocs.* **LA DATE EST RELATIVE ET EN TURKMÈN&nbsp;: `elapsedTime` vaut `8 sag öň` («&nbsp;il y a 8 heures&nbsp;»), 20 valeurs distinctes et **le maximum est 8 heures**, donc la première page entière a moins de huit heures — un `datePosted` ne peut être que DÉRIVÉ de notre propre horloge, et aucun taux pris sur cette page n'est un taux de ce board.** *Et un même enregistrement mêle les langues&nbsp;: `cityName` en russe (`Ашхабад`) à côté d'`elapsedTime` en turkmène.* **L'EXPURGATION EST L'INVERSE DE `somon-tj.md`, MESURÉE ET NON TRANSPOSÉE&nbsp;: sur les 150 descriptions, ZÉRO courriel, ZÉRO `+993`, ZÉRO mention de messagerie, et **UNE** suite de huit chiffres ancrée (le format d'un numéro turkmène).** *Somon, même classe d'objet et même semaine à une frontière près, portait 17/60 courriels, 11/60 `+992` et 10/60 suites de neuf chiffres&nbsp;: «&nbsp;petites annonces donc contacts en texte libre&nbsp;» NE SE TRANSPOSE PAS.* **Mais la description de liste est un EXTRAIT de 73 caractères&nbsp;: ce compte porte sur la LISTE et ne dit rien de la page d'annonce, qui n'a pas été lue.** Lisibilité contrôlée par la PART avec arité avant toute conclusion d'absence&nbsp;: 2 321 têtes latines, 0 paire, part 0,000, zéro U+FFFD sur 117 162 octets non-ASCII → LISIBLE, mesuré. Aucune valeur de contact, de salaire ou d'annonceur n'est reproduite ici. **LA ROUTE N'EST PAS ÉTABLIE ET AUCUNE N'EST DÉCLARÉE&nbsp;: 0,98 % du board par HTTP n'est pas une couverture, et les deux seuls candidats restants sont l'action serveur `$h49` rejouée en POST (son identifiant est un condensat de BUILD, donc il périme à chaque déploiement) et un onglet qui clique «&nbsp;Загрузить ещё&nbsp;» — ni l'un ni l'autre n'a été essayé.** *Et ce libellé-là n'est PAS une preuve de bouton&nbsp;: `Следующая`, `Предыдущая` et `Загрузить ещё` vivent dans le DICTIONNAIRE i18n de la page, pas dans un contrôle — un site entièrement localisé contient tous les mots du domaine, et j'ai failli lire ces deux occurrences comme un pageur.* · 2026-10-06 -->
<!-- witness: partial — **l'hôte déclare `totalCount` 15 278 et `perPage` 150 dans sa propre charge RSC, et notre extraction rend exactement 150 annonces / 150 identifiants distincts / 0 échec**, donc le compte émis se compare à un chiffre qui ne vient PAS de notre extraction&nbsp;: 150 sur 15 278, **0,98 %**, et le manque est DÉCLARÉ parce qu'aucune URL n'adresse la suite. *Le total a bougé de 15 279 à 15 278 en cinq minutes&nbsp;: il porte son heure.* Le «&nbsp;более 17132&nbsp;» du 2026-09-17 n'est plus vrai — **−1 853 en dix-neuf jours** — et le «&nbsp;более 6 175&nbsp;» du prétendu miroir d'Achgabat est RÉFUTÉ, cette URL servant la page non filtrée · 2026-10-06 -->
<!-- content: measured · **`/others/rabota/vakansii` (200, 1 274 078 / 1 272 960 B, md5 0b6ff9b7ffdc / ca52c21695d5 — a rendered element moves) is the classifieds site's vacancies category, titled «Вакансии, более 17132 объявлений в категории Вакансии, свежие объявления в Туркменистане» (17 132+ notices — the site's own figure, a category of classifieds, employers and private advertisers mixed), a city mirror `/ashgabat/…` («более 6 175»); no JobPosting; `_robots.allowed` → open, certain; the pager and the notice not read** · 2026-09-17 -->
<!-- witness: the title's own «более 17132 объявлений» — a classifieds category's count, employers and private advertisers mixed · 2026-09-17 -->

## Re-measured 2026-10-06 — 150 of 15 278, and the other 15 128 have no address

**Six readings, each guarded on its exact path in a turn distinct from the
retrieval, the prediction written before the measurement:**

```
chemin demande                               code    octets  ids  totalCount  villes  communs/p1
/others/rabota/vakansii                       200   1133411  150      15279      20    ---
/others/all/rabota/vakansii   (le canonical)  200   1133411  150      15278      20   150/150
/others/rabota/vakansii?offset=150            200   1133462  150      15278      20   150/150
/others/rabota/vakansii?offset=15270          200   1133468  150      15278      20   150/150
/ashgabat/others/rabota/vakansii              200   1133411  150      15278      20   150/150
/others/ashgabat/rabota/vakansii              404    331901    -          -       -    ---
/others/mary/rabota/vakansii                  404    331893    -          -       -    ---
/zzz-pas-une-ville/others/rabota/vakansii     404    360397    -          -       -    ---   <- le CONTROLE
```

**The prediction, written first, had two branches and the second won:** if
`offset` were honoured, `?offset=150` would carry `"offset":150` and 150 ids
disjoint from page one, and `?offset=15270` would carry about nine; if it were
ignored, both would carry `"offset":0` and the same 150 ids. Both carry
`"offset":0` and 150 of 150 identical ids.

### The city prefix is VALID and inert, which is worse than a catch-all

My first reading of the `/ashgabat/…` 200 was that the host has a leading-segment
catch-all. **That hypothesis is refuted by its own control:**
`/zzz-pas-une-ville/others/rabota/vakansii` answers **404**. So the host
*recognises* `ashgabat` and *refuses* an invented first segment — and on the
recognised path it serves all twenty cities anyway (Ашхабад 87, Туркменабат 21,
Мары 11, Дашогуз 8 of 150).

> **An address the host validates and then does not filter is the dangerous
> shape: a walk of the twenty city mirrors would emit the same 150 adverts
> twenty times, with no error anywhere, on a route the host says yes to.**

*And the form that WOULD have filtered — `/others/<city>/rabota/vakansii`, the
shape the host's own canonical suggests with its `all` segment — is a 404. So the
honest 404 sits on the path I invented and the misleading 200 sits on the path
this card has recorded since 2026-09-17.*

### Three multipliers, one family, three directions

| board | the trap | direction |
| :-- | :-- | :-- |
| `yora.md` | 4 locale URLs name 1 advert, all strings distinct | **over**-count ×4 |
| `tmcars.md` slug | 23 adverts share the slug `isgar-gerek` | **under**-count, 150 → 108 |
| `tmcars.md` city | 20 validated prefixes serve 1 result set | **over**-count ×20 |

*The common cause is that the identifier is not what it looks like, and in all
three cases nothing fails: the counts stay plausible.* **Only the numeric `id`
dedups to 150 here.**

### `$undefined` — a sentinel this repository did not have, and it defeated my own test

**React Server Components encode `undefined` on the wire as the literal string
`"$undefined"`, and this payload carries it 654 times.** This repository has
recorded the literal `"undefined"` as a stored sentinel; the `$` is enough to
pass under that list.

```
champ          PRESENT  REMPLI  « REEL » par mon test   la VERITE
isLiked            150     150                    150           0   ($undefined x150)
videoExist         150     150                    150           0   ($undefined x150)
badgeLabel         150     150                    150           2   ($undefined x148)
price              150      96                     88          96   (None x54)
vip                150     150                     26          26   (booleen REEL)
```

> **My own field test printed a confident `150` on three fields that carry
> nothing — and `withheld_fields` written on it would have claimed a value
> withheld on 148 adverts where nobody deposited one.**

*`price` gives four numbers to one question — 150 present, 96 non-null, 88 truthy,
54 explicitly `None` — and `vip` gives the mirror case: a real boolean where
«present» and «filled» both say 150 and the answer is 26.*

### What this board gives, and the date it cannot give

Fourteen fields per list advert, each measured one at a time: `id`, `name`,
`href` as `/others/<id>/<slug>`, `image`, `price`, `vip`, `description` (an
excerpt — 73 characters on the example), `cityName`, `elapsedTime`,
`reviewEnabled`, `reviewCount`, `badgeLabel`, `isLiked`, `videoExist`.

**There is no `JobPosting` and no `ItemList`: the three JSON-LD blocks are
`WebSite`, `Organization` and `BreadcrumbList`.** *The string
`application/ld+json` occurs six times for three blocks, because the RSC payload
repeats it — counting the string would have announced six.*

**And the date is RELATIVE: `elapsedTime` reads `8 sag öň` («8 hours ago»), 20
distinct values with a maximum of eight hours.** So the whole first page is less
than eight hours old, a `datePosted` can only be DERIVED from our own clock, and
no rate taken on this page is a rate of this board. *One record mixes languages:
`cityName` in Russian beside `elapsedTime` in Turkmen.*

### Expurgation measured, not transposed — and it comes out the opposite way

| | `somon-tj.md` (2026-10-06) | `tmcars.md` (2026-10-06) |
| :-- | --: | --: |
| e-mail shaped | **17 of 60** | **0 of 150** |
| national prefix | 11 of 60 (`+992`) | **0 of 150** (`+993`) |
| anchored national digit run | 10 of 60 (nine digits) | **1 of 150** (eight digits) |
| messaging app named | 9 of 60 | **0 of 150** |

**Two classifieds job sections, the same week, one border apart, and «classifieds
therefore contacts in free text» does not transpose.** *But the list description
is a 73-character EXCERPT: this count is about the LIST and says nothing about
the advert page, which was not read.*

### The route is not established, and no route is declared

**0,98 % of a board is not a coverage**, so this card declares no `route:` line.
The two remaining candidates are named and neither was tried: replaying the
server action `$h49` by POST — *its identifier is a BUILD digest, so it expires
at every deployment* — and a tab clicking «Загрузить ещё».

*And that label is not evidence of a button: `Следующая`, `Предыдущая` and
`Загрузить ещё` live in the page's i18n DICTIONARY, not in a control. A fully
localised site contains every word of its domain, and I nearly read two
occurrences of «Следующая» as a pager.*

**Rules, re-read: 143 bytes, `state: read`, `certain: True` — `Allow: /` then
`Disallow:` on `/profile/`, `/api/`, `/chat/` and `/tmcars/`, the host refusing a
path that carries its own name. No `Crawl-delay`, so our own pace applies. One
sitemap declared, and at `/sitemap/index.xml` rather than `/sitemap.xml` — the
guard I had first taken on `/sitemap.xml` was on a path this host never
declared.** *Guard exercised both ways: five paths open with `rule=None`, seven
refused each by its own narrow rule (`/api/v1/ads` → `/api/`, `/profile/login` →
`/profile/`). `/api/` is refused in writing, so borne 1 closes that route to every
path including the browser — and the page never asks for it: «api» occurs twice
in 1,13 MB.*

**Found by the Turkmenistan search of #604 (a country never searched),
measured 2026-09-17 16:25–16:27 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #604: a Russian search («вакансии Ашхабад сайт работа Туркменистан …»)
naming the national portals and classifieds; no composed host names; no
public employment service found online. *A measurement, not an adapter.*

```
_robots.allowed('tmcars.info', '/others/rabota/vakansii')   open, certain
GET https://tmcars.info/others/rabota/vakansii               200 ×2 — «более 17132 объявлений», the notices
```

The largest figure in the country by far — a classifieds category, so a
notice is anything from an employer's vacancy to a private advertiser's
line; the pager and what a notice carries (phone numbers, likely) are the
adapter's first line.
