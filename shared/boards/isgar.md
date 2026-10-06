# Board measurement — ISGAR (`isgar.com.tm`, Turkmenistan): **the board declares `{page, limit, total, totalPages}` in every response and `?page=N` is honoured** — 406 then 412 vacancies over 23 pages of 18, page 2 disjoint from page 1, page 99 honestly empty; its declared sitemap AGREES at 407 and carries no candidate CV; `/api/` is refused in writing and holds only uploaded media; and its `robots.txt` argues its own reasoning in Russian

<!-- verified: 2026-10-06 -->

<!-- hosts: isgar.com.tm -->
<!-- script: none -->
<!-- countries: TM -->
<!-- route: http · 412 · 2026-10-06 -->
<!-- content: measured · **406 PUIS 412 ANNONCES SUR 23 PAGES DE 18, ET LA PAGINATION EST UNE URL ORDINAIRE — l'inverse exact de `tmcars.md`, même pays, même semaine.** Mesuré le 2026-10-06 entre 03:17 et 03:2x UTC, garde prise sur chaque chemin exact dans des tours distincts et éprouvée dans les DEUX sens (5 ouverts avec `rule=None`, 3 refusés par `/api/`). *`/vacancies` rend 200 et **781 606 o** — contre 688 838 le 2026-09-17, donc le board a GROSSI — et c'est une application Next.js à composants serveur, 34 `push` pour une charge décodée de 384 456 caractères.* **L'HÔTE DÉCLARE SES QUATRE NOMBRES DANS CHAQUE RÉPONSE&nbsp;: `"meta":{"page":1,"limit":18,"total":406,"totalPages":23}` — et notre extraction rend EXACTEMENT 18 annonces, soit le `limit` annoncé, avec 41 champs par annonce.** *18 × 23 = 414 ≥ 406&nbsp;: l'arithmétique du board est cohérente avec elle-même, ce qui est un contrôle et pas une coïncidence.* **PRÉDICTION ÉCRITE AVANT LA MESURE, PREMIÈRE BRANCHE GAGNANTE&nbsp;: `?page=2` rend `meta.page=2` et 18 annonces **0/18 communes** avec la page 1 — entièrement disjointes&nbsp;; `?page=23` rend `meta.page=23` et **16** annonces&nbsp;; `?page=99`, hors des 23, rend `meta.page=99` et **ZÉRO** annonce en 568 080 o — une page honnêtement vide, pas un 404 et pas un repli sur la page 1.** *Et ma prédiction chiffrée était fausse de six pour une raison que le board lui-même corrige&nbsp;: j'attendais 10 à la page 23 (406 − 22×18) et j'ai eu 16, parce que `total` valait **412** dans cette réponse — 412 − 396 = 16, exact. **Le total a bougé de 406 à 412 en trois minutes**, donc ce nombre porte son heure à la minute, et une prédiction calculée sur un dénominateur déjà périmé accuse un board sain.* **LES 41 CHAMPS D'UNE ANNONCE, MESURÉS UN À UN SUR LES 18 (présent / non vide / réel)&nbsp;:** `id` `number` `headline` `headlineTm` `positionId` `description` `descriptionTm` `salaryType` `showSalary` `employmentType` `workSchedule` `status` `viewsCount` `expiresAt` `publishedAt` `createdAt` `updatedAt` à **18/18/18**&nbsp;; `salaryFrom` **18/13/13** et `salaryTo` **18/10/10** (donc des fourchettes et des valeurs seules)&nbsp;; `experienceLevel` et `autoReplyEnabled` réels sur 9, `autoRaise` sur 7, `allowApplyWithoutResume` sur 4, `isNationwide` sur 1, `isPremium` et `isRemotePossible` sur **0**&nbsp;; `labels` présent sur 18 et **jamais rempli**&nbsp;; `location` présent sur **17** et non 18&nbsp;; `contactPhones` présent sur **13**&nbsp;; `languageRequirements` sur 4&nbsp;; `latitude`/`longitude` sur **1 seule**. *Et trois champs de MODÉRATION voyagent dans la charge publique — `rejectedAt`, `rejectionReasonCode`, `rejectionReasonText`, `None` sur les 18&nbsp;: le board expédie son schéma interne, ce qui dit ce qu'un refus porterait sans qu'aucun refus ne soit visible.* **TROIS SOUS-OBJETS, ET C'EST `company` QUI DÉCIDE DE L'EXPURGATION&nbsp;:** `company` (21 clés, dont `phone`, `email`, `website`, `isAnonymous`, `isVerified`, `userId`, `logoUrl`), `position` (10 clés, bilingue `name`/`nameTm`), `location` (9 clés, bilingue, avec `parentId`, `region`, `type` — donc une hiérarchie administrative). **ET CE BOARD PORTE LES DEUX DANGERS D'EXPURGATION À LA FOIS, ce qu'aucun des trois autres turkmènes ni `somon-tj` ne faisait&nbsp;: le CHAMP NOMMÉ — `company.phone` porte un `+993` sur **18/18**, `company.email` une forme de courriel sur **10/18**, `contactPhones` est présent sur 13/18 — ET le TEXTE LIBRE, `description` et `descriptionTm` portant un `+993` sur **6/18** chacun.** *Somon n'avait que le texte libre, SAE que les champs (recensement 0/577), TMCARS quasi rien&nbsp;: quatre boards, quatre répartitions, et aucune ne se transpose.* **ET `showContacts` EST LE CONSENTEMENT DU DÉPOSANT, PAS UNE PERMISSION POUR NOUS&nbsp;: il vaut `true` sur 13/18 et la clé `contactPhones` est présente sur 13/18, les deux s'accordant sur **18/18**. Donc il PRÉDIT exactement où un contact existe — et un `withheld_fields` ne se déclare que sur ces 13, jamais sur les 5 où la clé n'existe pas, sinon il mentirait sur notre propre discrétion.** **DEUX FAUX POSITIFS DE MON PROPRE MOTIF, ET ILS DÉCIDENT DE LA LISTE DE CHAMPS&nbsp;: `company.brandBannerUrl` et `company.userId` déclenchent «&nbsp;huit chiffres ancrés&nbsp;» — le format d'un numéro turkmène — alors que l'un est un fragment de CHEMIN d'URL et l'autre le premier bloc d'un UUID. Appliquer la règle de chiffres à ces champs détruirait l'identifiant, exactement comme les 314/314 madrilènes.** *Ce qui répare n'est donc pas le motif mais la LISTE DE CHAMPS, et elle doit EXCLURE `id`, `number`, `userId`, `logoUrl`, `brandBannerUrl` et les cinq dates — tous des champs dont le SENS est connu.* **LE SITEMAP DÉCLARÉ EST UN VRAI TÉMOIN, ET C'EST LE PREMIER DE LA GRAPPE&nbsp;: 1 426 981 o, `urlset`, **2 534 `<loc>` tous distincts**, ZÉRO CDATA. Composition&nbsp;: `/ru` 1 267 (le miroir russe, soit la moitié), `/companies` 780, `/vacancies` **407**, `/career` 52, `/help` 21, et des singletons.** *Donc **407 sous `/vacancies` pour les 406 que l'API déclare** — la page d'index faisant le 407ᵉ&nbsp;: **le sitemap et la charge s'accordent**, et ce dépôt n'avait pas encore vu un sitemap confirmer un compte d'API.* **ET LE MULTIPLICATEUR DE LOCALE EST ×2 ET NON ×4&nbsp;: 812 URL `/vacancies/<uuid>` pour ~406 annonces, parce que chaque annonce existe sous `/vacancies/` et sous `/ru/vacancies/`.** *C'est le piège de `yora.md` à moitié amplitude, et il se dédoublonne par l'UUID.* **ET LE DANGER DE `korgar.md` EST ABSENT, MESURÉ ET NON SUPPOSÉ&nbsp;: `/resumes` apparaît **UNE** fois dans le sitemap — la page d'index — et pas un seul CV de candidat, là où Korgar en déclarait 34 894 soit 81,4 %.** **DEUX RÉGIMES DANS LE CHAMP `lastmod`, ET LA MILLISECONDE EST LE SEUL TÉMOIN&nbsp;: 2 510 `lastmod` pour **638 millisecondes distinctes** et un étalement de près de trois ans (2024-01-06 → 2026-10-06), donc le champ est RÉEL — mais **24 valeurs (1,0 %) finissent exactement par `:30:00.014Z`**, toutes à l'heure 01, et **7 des 38 `updatedAt` de la page** portent la même signature à 02:30. Un travail récurrent estampille un LOT à la milliseconde identique, et rien dans le champ ne le distingue d'une édition réelle.** *Donc `lastmod` est utilisable en incrémentiel pour la grande majorité et faux pour un petit lot — beaucoup plus faible que les 400/416 de Yora, et c'est la première fois de la grappe qu'un `lastmod` vaut quelque chose.* **`/api/` EST REFUSÉ PAR ÉCRIT ET CE REFUS NE COÛTE QUE DES IMAGES&nbsp;: les 15 chemins `/api/` que la page référence sont tous des `/api/v1/uploads/files/…` — logos d'entreprise et vignettes de catégorie. La ROUTE DE DONNÉES n'est pas là&nbsp;: les annonces arrivent rendues côté serveur dans la charge.** *Donc la borne 1 ferme les médias et rien d'autre, et c'est exactement ce que l'auteur du fichier de règles écrit.* **ET CE FICHIER DE RÈGLES ARGUMENTE SON PROPRE RAISONNEMENT, EN RUSSE, ET NOMME SON CODE&nbsp;: 580 o, `Allow: /`, un seul `Disallow: /api/`, un sitemap, et quatre lignes de commentaire disant que `/applicant`, `/employer`, `/login`, `/register`, `/forgot-password` ne sont PAS bloqués ici mais servent un en-tête `X-Robots-Tag: noindex` (voir `middleware.ts`), parce qu'un blocage dans `robots.txt` laisserait l'URL dans les résultats sans contenu — et que «&nbsp;on ne ferme que l'API, ce ne sont pas des pages&nbsp;».** *Donc l'hôte DISTINGUE par écrit «&nbsp;ne pas indexer&nbsp;» de «&nbsp;ne pas récupérer&nbsp;», et un `X-Robots-Tag: noindex` rencontré sur ces chemins **n'est pas la borne 1**.* **CE QUI N'EST PAS ÉTABLI&nbsp;: aucune page d'ANNONCE n'a été lue, donc la forme de `/vacancies/<uuid>` est inconnue et il n'est pas établi qu'elle porte un `JobPosting`** (la liste n'en porte aucun&nbsp;: deux blocs JSON-LD seulement). *Le miroir `/ru/vacancies` n'a pas été comparé par CONTENU, seulement par jeu de chemins dans le sitemap. Les `/companies` n'ont pas été touchées. Et `description` est de **3 caractères sur 7 des 18** et de 503 à 1 008 sur les 11 autres&nbsp;: la liste porte la description COMPLÈTE pour certaines et un talon pour les autres, donc ce n'est ni un extrait ni un champ fiable.* Lisibilité contrôlée par la PART avec arité avant toute conclusion d'absence&nbsp;: 6 268 têtes latines, 0 paire, part 0,000, zéro U+FFFD sur 23 363 octets non-ASCII → LISIBLE, mesuré. Aucune valeur de contact, de salaire, d'entreprise ou de déposant n'est reproduite ici. · 2026-10-06 -->
<!-- witness: measured — **l'hôte déclare `{page, limit, total, totalPages}` dans CHAQUE réponse** et notre extraction rend exactement le `limit` annoncé (18 sur la page 1, 16 sur la page 23, 0 sur la page 99), donc le compte émis se compare à un chiffre qui ne vient PAS de notre extraction&nbsp;: **406 puis 412 annonces sur 23 pages**, et `?page=2` est **0/18 commun** avec la page 1. *Le total a bougé de 406 à 412 en trois minutes&nbsp;: il porte son heure.* **ET LE SITEMAP DÉCLARÉ CONFIRME&nbsp;: 407 `<loc>` sous `/vacancies` pour 406 annonces plus la page d'index — un second témoin indépendant, le premier de cette grappe** · 2026-10-06 -->
<!-- content: measured · **`/vacancies` (200, 688 838 / 689 842 B, md5 887e7dc2e037 / 6bb13dcb6d97 — a rendered element moves) is a Tailwind-built board titled «Türkmenistanda wakansiýalar — Aşgabatda, Maryda, Türkmenabatda …» with `/vacancies/<uuid>` ad links and a Russian mirror `/ru/vacancies`; no count stated, no JobPosting; `_robots.allowed('isgar.com.tm','/vacancies')` → open, certain; the pager and the ad not read** · 2026-09-17 -->
<!-- witness: none — the page states no count · 2026-09-17 -->

## Re-measured 2026-10-06 — the host declares its pager, and `?page=N` is honoured

**Four readings, each guarded on its exact path in a turn distinct from the
retrieval, the prediction written before the measurement:**

```
chemin demande          code    octets  ann  meta                                        communs/p1
/vacancies               200   781606   18  page 1  limit 18  total 406  totalPages 23    ---
/vacancies?page=2        200   771212   18  page 2  limit 18  total 406  totalPages 23    0/18
/vacancies?page=23       200   719536   16  page 23 limit 18  total 412  totalPages 23    0/16
/vacancies?page=99       200   568080    0  page 99 limit 18  total 406  totalPages 23    0/0
```

**The first branch of the prediction won**: page 2 is entirely disjoint from
page 1, page 23 is short as a last page must be, and page 99 — outside the
declared 23 — returns an honestly **empty** list rather than a 404 or a silent
fall back to page one.

> **And my own arithmetic was wrong by six for a reason the board itself
> corrects: I predicted 10 on page 23 from `total: 406`, and got 16 — because
> that response declares `total: 412`. 412 − 22×18 = 16, exact.** *The total
> moved by six in three minutes, so a prediction computed on a denominator that
> has already moved accuses a healthy board.*

### The exact inverse of `tmcars.md`, same country, same cluster, same week

| | `tmcars.md` | `isgar.md` |
| :-- | :-- | :-- |
| the host's own counts | `totalCount` + `perPage` | **`{page, limit, total, totalPages}`** |
| `?page=` / `?offset=` | **accepted and INERT** (same 150 ids) | **honoured** (0/18 common) |
| out-of-range page | — | **honestly empty** |
| reachable by HTTP | **150 of 15 278 — 0,98 %** | **all 23 pages** |
| the pager | one server action `$h49` | a plain query string |
| declared sitemap | `/sitemap/index.xml`, unread | **2 534 `<loc>`, AGREES at 407** |

*A shared country, a shared stack (both Next.js RSC) and a shared object class
predicted neither the route nor the analysis.*

### `/api/` is refused in writing, and the refusal costs only images

The 15 `/api/` paths the page references are all
`/api/v1/uploads/files/…` — company logos and category thumbnails. **The DATA
route is not there: the adverts arrive server-rendered in the payload.** So
borne 1 closes the media and nothing else.

**And the rules file argues its own reasoning, in Russian, naming its own code:**
580 bytes, `Allow: /`, a single `Disallow: /api/`, one sitemap, and four comment
lines saying that `/applicant`, `/employer`, `/login`, `/register` and
`/forgot-password` are deliberately *not* blocked here but serve an
`X-Robots-Tag: noindex` header instead (see `middleware.ts`), because blocking in
`robots.txt` would leave the URL in results without content — and that «we close
only the API, those are not pages».

> **So this host distinguishes, in writing, «do not index» from «do not fetch».**
> *An `X-Robots-Tag: noindex` met on those paths is NOT borne 1, and this card is
> the written evidence that the distinction is the host's own and not ours.*

### Expurgation: this is the first of the four to carry BOTH hazards

| | named field | free text |
| :-- | :-- | :-- |
| `isgar` | `company.phone` **18/18** · `company.email` **10/18** · `contactPhones` **13/18** | `description` **6/18** · `descriptionTm` **6/18** |
| `somon-tj` | none exists | 17/60 · 11/60 · 10/60 · 9/60 |
| `tmcars` | none exists | 1/150 |
| SAE (`servicios-regionales-es-2`) | census **0 of 577** | — |

**`showContacts` is the POSTER's consent, not a permission for us.** It is `true`
on 13 of 18 and the `contactPhones` key is present on 13 of 18, the two agreeing
on **18/18** — so it predicts exactly where a contact exists. *A
`withheld_fields` therefore declares itself on those 13 and never on the 5 where
the key does not exist, or it lies about our own discretion.*

**AND TWO FALSE POSITIVES OF MY OWN PATTERN DECIDE THE FIELD LIST:**
`company.brandBannerUrl` and `company.userId` both trip «eight anchored digits» —
the shape of a Turkmen number — while one is a URL path fragment and the other
the first block of a UUID. *Applying the digit rule to them would destroy the
identifier, exactly as the 314/314 Madrid case.* **The repair is the FIELD LIST,
which must exclude `id`, `number`, `userId`, `logoUrl`, `brandBannerUrl` and the
five dates — every field whose MEANING is known.**

### The declared sitemap is a real witness — the first in this cluster

**2 534 `<loc>`, all distinct, zero CDATA.** `/ru` 1 267 (the Russian mirror, half
the file), `/companies` 780, `/vacancies` **407**, `/career` 52, `/help` 21.

*407 under `/vacancies` for the 406 the payload declares, the index page making
the 407th — **the sitemap and the API agree**, and this repository had not yet
seen a declared sitemap confirm an API count.* **The locale multiplier is ×2 and
not ×4** (812 `/vacancies/<uuid>` URLs for ~406 adverts, each advert existing
under `/vacancies/` and `/ru/vacancies/`), and it dedups by UUID.

**And `korgar.md`'s hazard is ABSENT, measured and not assumed: `/resumes`
appears ONCE — the index page — and not a single candidate CV**, where Korgar
declared 34 894 of them, 81,4 % of its sitemap.

### Two regimes in one `lastmod`, and the millisecond is the only witness

```
2 510 lastmod · 638 millisecondes DISTINCTES · etalement 2024-01-06 -> 2026-10-06
  -> le champ est REEL
MAIS  24 valeurs (1,0 %) finissent exactement par :30:00.014Z, toutes a l'heure 01
      et 7 des 38 updatedAt de la page portent la meme signature a 02:30
  -> un travail recurrent estampille un LOT a la milliseconde identique
```

**Nothing in the field distinguishes a scheduler touch from a real edit except
the identical millisecond.** *So `lastmod` is usable incrementally for the great
majority and false for a small batch — far weaker than Yora's 400 of 416, and the
first time in this cluster that a `lastmod` is worth anything at all.*

**Found by the Turkmenistan search of #604 (a country never searched),
measured 2026-09-17 16:25–16:27 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #604: a Russian search («вакансии Ашхабад сайт работа Туркменистан …»)
naming the national portals and classifieds; no composed host names; no
public employment service found online. *A measurement, not an adapter.*

```
_robots.allowed('isgar.com.tm', '/vacancies')   open, certain
GET https://isgar.com.tm/vacancies               200 ×2 — the board, /vacancies/<uuid>, /ru/vacancies
```

The country's purpose-built job board (categories, salary, schedule per
its description). The pager and the ad are the adapter's first line.
