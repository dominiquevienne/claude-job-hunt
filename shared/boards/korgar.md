# Board measurement — Korgar (`korgar.tj`, Tajikistan): **adapter delivered — `korgar.py`, and the FILTER is the whole adapter** — the declared sitemap carries 42 851 `<loc>` of which **32 687 are candidate CVs** and 6 701 are advertisements, the rules are 105 bytes with not one `Disallow`, and an unfiltered walk would harvest the CVs; the second declared sitemap is a 404, so there is no locale multiplier; and `hiringOrganization.name` is the WORD «Компания» on three of three, so the employer is a placeholder and comes back null

<!-- verified: 2026-10-06 -->

<!-- hosts: korgar.tj -->
<!-- script: korgar.py -->
<!-- countries: TJ -->
<!-- content: measured · **6 701 annonces sur 42 851 `<loc>`, 32 687 CV écartés, 36 150 URL refusées par le filtre, 3 spécimens lus, 8 cas de garde — ADAPTATEUR LIVRÉ, `korgar.py`, et LE FILTRE EST TOUT L'ADAPTATEUR.** *Invocations&nbsp;: `korgar.py list [--limit N] [--with-ads --max N]` et `korgar.py ad --url <URL>`, exercées sur l'hôte VIVANT le 2026-10-06 06:0x UTC.* **DEUX COUCHES, DÉCLARÉES REDONDANTES&nbsp;: le segment `/vakanciya/` ET un `_<chiffres>` terminal.** *L'une suffirait aujourd'hui — `/vakancii` ne contient pas `/vakanciya/`, et les 6 701 portent tous un identifiant — mais la redondance est ÉNONCÉE parce que `/rezume` prouve qu'une couche ne suffit pas&nbsp;: **959 de ses 33 646 sont des facettes sans identifiant**, donc un filtre de SECTION ne trie pas les NATURES.* **ET `refuse_candidate()` EST ÉCRIT COMME UN REFUS QUI PEUT TIRER et non comme une compréhension qui ne peut pas&nbsp;: il sort en 7 sur `/rezume/`, `/resume/` et `/soiskatel`, et rend `None` sur une annonce — éprouvé dans les DEUX sens.** *`allowed()` dit True sur ces chemins&nbsp;: c'est NOUS qui refusons, et cette décision vit là.* **CORRECTION D'UN CHIFFRE QUE CETTE FICHE PUBLIAIT&nbsp;: elle écrivait «&nbsp;/rezume/ 33 646 + /resume/ 1 248 = 34 894 CV, 81,4 %&nbsp;». C'EST FAUX — `/resume/` porte les pages de FACETTES de la section CV (`/resume/gorod/<ville>`, `/resume/kategorii`), pas des CV, et les deux familles avaient été additionnées sur la RESSEMBLANCE DE LEUR NOM.** *Composition réelle, par premier segment, mesurée le 2026-10-06 06:01 UTC&nbsp;: `/rezume` 33 646 (78,5 %, dont **32 687** portent un identifiant) ; `/vakanciya` **6 701** (15,6 %, 6 701/6 701 avec identifiant) ; `/vakancii` 1 248 (2,9 %, **0** identifiant — facettes) ; `/resume` 1 248 (2,9 %, **0** — facettes) ; 7 pages diverses. **Ancienne valeur 34 894 CV / 81,4 %&nbsp;; valeur juste 32 687 URL de CV portant un identifiant / 76,3 %&nbsp;; raison&nbsp;: `/resume/` est une facette&nbsp;; date&nbsp;: 2026-10-06.*** **Et la phrase de SÛRETÉ ne s'adoucit pas, elle se durcit.** **LE SECOND SITEMAP DÉCLARÉ EST UN 404, DONC IL N'Y A AUCUN MULTIPLICATEUR DE LOCALE&nbsp;: les règles déclarent `/sitemap.xml` ET `/ru/sitemap.xml`, et le second rend HTTP 404 (6 603 o, non enregistré). Vérifié AVANT de publier un compte, la même grappe venant de produire un ×4 par locale sur `yora.tj` et un ×2 sur `isgar.com.tm`&nbsp;; aucun préfixe `/ru/`, `/tj/` ou `/en/` sur les 42 851.** **LA FORME REPOSE SUR TROIS SPÉCIMENS ET NON UN&nbsp;: la première, la MÉDIANE et la DERNIÈRE des 6 701, chaque URL prise DANS le sitemap et jamais composée. Les trois servent exactement UN bloc `application/ld+json` portant un `JobPosting` complet aux MÊMES dix clés.** **ET L'EXERCICE A TROUVÉ UN DÉFAUT DANS CETTE FICHE ET DANS MON PROPRE CODE&nbsp;: `hiringOrganization.name` vaut le MOT littéral «&nbsp;Компания&nbsp;» — «&nbsp;entreprise&nbsp;» — sur 3 sur 3. C'est un LIBELLÉ PAR DÉFAUT, donc l'employeur n'est PAS publié dans un champ&nbsp;; cette fiche disait le contraire et mon premier enregistrement émettait `"employer": "Компания"`, c'est-à-dire une entreprise FABRIQUÉE dans un registre.** *`published_employer()` rend `(None, "Компания")`&nbsp;: le null, et la chaîne de l'hôte à côté pour ne rien cacher et ne rien revendiquer. Le test est une ÉGALITÉ avec une constante nommée et datée et non une appartenance à une liste de refus, donc il cessera de matcher tout seul le jour où cet hôte publiera un vrai nom.* **C'est la famille de `$undefined`&nbsp;: un champ PRÉSENT et REMPLI d'une constante, que `if x` déclare rempli.** *Et `identifier.name` porte LE MÊME MOT pendant que sa VALEUR est l'identifiant de l'annonce&nbsp;: l'hôte écrit le libellé dans DEUX champs `name`. L'identifiant est donc attesté deux fois (suffixe d'URL et JSON-LD), et quand les deux divergent l'URL gagne et la marche le DIT.* **TROIS DÉCISIONS DE CHAMP, CHACUNE MESURÉE&nbsp;: `baseSalary` vaut **0 sur deux des trois**, donc un zéro est «&nbsp;non énoncé&nbsp;» et rend `null` et jamais 0&nbsp;; `jobLocation.address` sert `streetAddress` ET `postalCode` et **ni l'un ni l'autre n'atteint un enregistrement** — le test asserte l'ABSENCE DES CLÉS et non un null, parce qu'un `postal_code` à null reste un champ qui invite à le remplir&nbsp;; `employmentType` vaut «&nbsp;CONTRACTOR&nbsp;» sur les trois, donc porté et non interprété.** **AUCUN CONTACT N'EST PRÉSENT ET AUCUN N'EST RETENU&nbsp;: quatre motifs — forme de courriel, `+992`, suite de neuf chiffres ancrée, messagerie — sur TOUS les champs chaîne du `JobPosting` ET sur le texte visible des trois pages&nbsp;: zéro. Donc l'enregistrement ne porte AUCUN `withheld_fields`, et un cas asserte cette absence** — *un enregistrement affirmant avoir retenu un contact que personne n'a déposé mentirait sur notre propre discrétion, dans la seule direction qu'aucune garde extérieure à l'adaptateur ne peut vérifier.* **UNE ANNONCE DE 2021 EST ENCORE LISTÉE ET LE SITEMAP PORTE ZÉRO `lastmod` sur 42 851 entrées, donc `list` imprime que son compte est «&nbsp;URL d'annonce dans le sitemap déclaré&nbsp;» et jamais «&nbsp;vacances vivantes&nbsp;».** *Le «&nbsp;Более 3000&nbsp;» du site SOUS-estime le sitemap d'un facteur ~2,2, et la marche imprime les deux.* *Huit cas de garde, un par FORME&nbsp;; `/rezume/` n'a jamais été récupéré et ne le sera pas.* · 2026-10-06 -->
<!-- witness: measured — **6 701 URL d'annonce dans le sitemap déclaré**, filtrées sur `/vakanciya/` ET un identifiant terminal, contre le «&nbsp;Более 3000&nbsp;» du site qui SOUS-estime d'un facteur ~2,2. *Le filtre écarte 36 150 des 42 851, dont **32 687 URL de CV portant un identifiant** — et c'est une condition de SÛRETÉ, pas une optimisation.* **Et le sitemap porte ZÉRO `lastmod` avec une annonce de 2021 encore listée&nbsp;: 6 701 n'est donc pas un compte de vacances VIVANTES** · 2026-10-06 -->
<!-- content: measured · **42 851 `<loc>` in the declared sitemap, of which 34 894 — 81.4 % — are CANDIDATE CVs **[CORRECTED 2026-10-06: 32 687 and 76.3 %; `/resume/` 1 248 are facets]** and 6 701 are vacancies; the advert page serves a complete JSON-LD `JobPosting` and NO contact field; and three instrument traps sit on that one page.** THE DECLARED SITEMAP IS THE RIGHT WITNESS AND THE WRONG ROUTE, which is an EIGHTH way a declared sitemap fails to be one and the first where the failure is a HAZARD rather than an irrelevance: `korgar.tj/sitemap.xml` answers 200 with **2 941 163 B and 42 851 `<loc>` (42 761 distinct, so 90 exact duplicates) and ZERO `<lastmod>`**, and its composition by first path segment is **`/rezume/` 33 646 (78.5 %), `/resume/` 1 248 (2.9 %) — **[CORRECTED 2026-10-06: NOT a second spelling of the CVs but the CV section's FACET pages, `/resume/gorod/<city>` and `/resume/kategorii`, 0 of 1 248 carrying an identifier. The CV total is 32 687, not 34 894]** so 34 894 CV URLs in all — `/vakanciya/` 6 701 (15.6 %) and `/vakancii` 1 248 (category lists)**. *So a job board's declared sitemap enumerates, four URLs in five, the résumés of job SEEKERS — and the rules protect none of them: the file is 105 B with **0 `Disallow` and 0 `Allow`**, `read` and `certain`, and the guard returns `allowed=True` with `rule=None` on `/rezume/x_1` exactly as on `/vakanciya/x_1`.* **An adapter that walked the declared sitemap — the cheapest enumerator, and the one this repository's doctrine generally prefers — would harvest **32 687** CVs *(corrected 2026-10-06: 34 894 added `/resume/`, which holds facets)*. NOT ONE `/rezume/` OR `/resume/` URL WAS FETCHED AND NONE WILL BE: what is measured here is the sitemap's COMPOSITION, never its content.** AND THE COUNT PAIR, BOTH STATED AND NEITHER RECONCILED: the sitemap carries **6 701** vacancy URLs against the root's «Более 3000 вакансий» — *so the site's own round marketing claim understates by a factor of about 2.2, the sitemap is the better witness for the size, and because it carries no `lastmod` an unknown share of the 6 701 may be expired.* **THE ADVERT PAGE IS CLEAN AND STRUCTURED, which is what makes the route cheap:** one real URL taken FROM the sitemap (never composed) answers 200 at 83 405 B and carries a JSON-LD **array of three** whose third element is a complete `JobPosting` — `title`, `description` (413 characters), `datePosted`, `employmentType`, **`baseSalary` as an object (`@type`, `currency`, `value`)**, **`hiringOrganization` (`@type`, `logo`, `name`) so the employer is named**, `jobLocation` (`@type`, `address`) and `identifier` (`@type`, `name`, `value`). *The array shape matters: the root of the block is a LIST, not an object, and the first two elements are `WebSite` and `Organization` — a reader that assumes an object crashes, and one that takes element zero gets the site's own identity instead of the advert.* **AND THERE IS NO CONTACT TO WITHHOLD, MEASURED TWICE AND IN TWO PLACES:** on the tag-stripped text (3 110 characters) **0 email addresses, 0 `mailto:`, 0 `tel:`, 0 anchored nine-digit runs, 0 `+992`, 0 runs of seven to twelve digits** — and 2 occurrences of the Russian words for contact/telephone with no value beside them — and in the JSON-LD no `email`, no `telephone`, no `applicationContact` key exists at all. ***So an adapter here must NOT declare that it withheld a contact: declaring you withheld what nobody published is the `withheld_fields` lie, which is a lie about US and not about the board, and it is indetectable by re-reading because the output is identical either way.*** **THREE INSTRUMENT TRAPS ON ONE PAGE, AND TWO WERE CAUGHT ONLY BECAUSE SOMETHING BROKE RATHER THAN BECAUSE ANYTHING WAS RE-READ.** *(1)* **`data-page="1"` IS A PAGER ATTRIBUTE, NOT INERTIA.** My signature dictionary reported «Inertia `data-page`» and it was a FALSE POSITIVE: the single occurrence sits on `<div id="products-container" data-page="1">`, and the page carries **zero** `inertia`, **zero** `"component":` and **zero** `id="app"` bearing the attribute. *Only the JSON parse CRASHING on an integer revealed it; a reading would have recorded a false fact about the host's technology, and this repository's own note tells you to LOOK for `data-page` without saying the attribute alone is ambiguous. **Presence is necessary and not sufficient.*** *(2)* **A CLASS NAME IS NOT A CONTENT TYPE.** The class `manager-resumes-item` appears **22** times on a VACANCY page, and its 20 `onclick` navigations all point at `/vakanciya/` — the résumés template reused for a related-vacancies block. *I nearly wrote that the advert page carries CVs on the strength of that name; what it actually carries, by ordinary `href`, is **9** `/resume/` and **24** `/soiskatel` links, which is a different claim with a different number.* *(3)* **20 NAVIGATIONS ARE BY `onclick="location.href=…"` AND INVISIBLE TO AN href COUNTER**, beside 149 ordinary `<a href>` (43 distinct) — the `__doPostBack` family, on a site where an href count would miss a seventh of the links. **AND THE THREE ERRORS ARE AVOIDED BY ONE DECISION:** read the sitemap, filter it to `/vakanciya/`, fetch each advert and parse the JSON-LD `JobPosting` and nothing else. *An href counter misses the onclick navigations; a whole-page reader picks up candidate pages; the JSON-LD has neither problem and carries the employer, the salary and the date.* WHAT IS NOT ESTABLISHED: **the pager's end was NOT read** — the issue named `/vakancii?page=N` and its last page as the adapter's first line, and the declared sitemap made that unnecessary rather than answered it; **what share of the 6 701 is live is unknown**, there being no `lastmod` anywhere in 2.9 MB; `/ru/sitemap.xml`, the second declared one, was not fetched; and one advert was read, so «the JSON-LD is complete» is a statement about ONE page and not about 6 701 — *a card of FAMILY claims nothing for the family on one specimen, and the same rule holds for one advert of a board*. METHOD: DNS on both host forms through two public resolvers; the rules re-read (105 B, `read`, `certain`, two sitemaps declared — which the issue did not mention); the guard taken on every exact path in turns distinct from the retrievals and exercised in both directions; the advert URL taken FROM the sitemap rather than composed; readability checked before any conclusion of absence, and declared UNEXERCISED here — the body has **no latin lead at all**, so 0/0 reads LISIBLE by default and not by measurement; no `Crawl-delay` anywhere, so our own 2 s applied · 2026-10-06 -->
<!-- witness: the sitemap is the witness for the SIZE and must not be the route: **6 701 `/vakanciya/` URLs** against the root's «Более 3000 вакансий», so the host's own round claim understates by ~2.2× and the sitemap gives the better figure — but it carries **no `lastmod`**, so what share of the 6 701 is live is unknown and 6 701 is published as «vacancy URLs in the declared sitemap» and never as «live vacancies». The advert shape is established on ONE advert · 2026-10-06 -->
<!-- content: measured · **the root (200, 269 096 B, md5 b15ad3af2ae7 identical on two reads) claims «Более 3000 вакансий» (more than 3 000 — a round marketing claim), lists 21 ads as `/vakanciya/<slug>_<id>` (Russian and Tajik titles: «официант», «SEO мутахассиси»), category lists `/vakancii/<category>` and a pager `/vakancii?page=2 … 40`; no exact count, no JobPosting; `_robots.allowed('korgar.tj','/')` → open, certain; the list, the pager's end and the ad not read** · 2026-09-17 -->
<!-- witness: the root's «Более 3000 вакансий» is a claim; the pager's 40 pages are the bound to read · 2026-09-17 -->

## Measured 2026-10-06 — le sitemap déclaré est le bon TÉMOIN et la mauvaise ROUTE

```
korgar.tj/robots.txt    200   105 o   read, certain
  0 Disallow · 0 Allow · aucun Crawl-delay
  Sitemap: https://korgar.tj/sitemap.xml
  Sitemap: https://korgar.tj/ru/sitemap.xml      <- deux, et l'issue n'en nommait aucun

korgar.tj/sitemap.xml   200   2 941 163 o
  <loc>        42 851   (42 761 distincts -> 90 DOUBLONS exacts)
  <lastmod>         0   aucun, dans 2,9 Mo

  sa COMPOSITION, par premier segment d'URL :
    /rezume/      33 646   78,5 %   des CV de CANDIDATS
    /resume/       1 248    2,9 %   une SECONDE orthographe
                 -------
                  34 894   81,4 %   de CV au total   <- FAUX, corrige le 06.10 :
                  32 687   76,3 %   /resume/ 1 248 sont des FACETTES, pas des CV
    /vakanciya/    6 701   15,6 %   les annonces (detail)
    /vakancii      1 248    2,9 %   les listes de categorie
```

> **HUITIÈME façon dont un sitemap déclaré échoue à être un témoin — et la PREMIÈRE où
> l'échec est un DANGER et non une inutilité.** *Les sept précédentes ne donnaient pas ce
> qu'on voulait&nbsp;; celle-ci donne ce qu'il ne faut pas prendre.*

**Et les règles n'en protègent aucun&nbsp;:** 105 octets, **0 `Disallow`**, et la garde rend
`allowed=True` avec `rule=None` sur `/rezume/x_1` **exactement comme** sur `/vakanciya/x_1`.
**Un adaptateur qui marcherait le sitemap déclaré — l'énumérateur le moins cher, et celui
que la doctrine de ce dépôt préfère d'ordinaire — moissonnerait **32 687** CV.** *(chiffre corrigé le 2026-10-06 : 34 894 additionnait `/resume/`, qui porte les facettes de la section CV ; la phrase de sûreté ne change pas, elle se durcit.)*

*AUCUNE URL `/rezume/` ni `/resume/` n'a été récupérée et aucune ne le sera&nbsp;: ce qui est
mesuré ici est la COMPOSITION du sitemap, jamais son contenu.*

```
LE COUPLE DE COMPTES, LES DEUX ENONCES ET AUCUN RECONCILIE

  le sitemap          6 701 URL de vacance
  la racine           « Более 3000 вакансий »     une affirmation ronde
  -> le site SOUS-ESTIME d'un facteur ~2,2, et le sitemap est le meilleur temoin
     de la TAILLE — mais il ne porte aucun lastmod, donc la part des 6 701 qui est
     VIVANTE est inconnue, et 6 701 se publie « URL de vacance dans le sitemap
     declare » et jamais « vacances vivantes »
```

```
LA PAGE D'ANNONCE — propre, structuree, et c'est ce qui rend la route peu chere

une URL REELLE prise DANS le sitemap (jamais composee)   200   83 405 o
  JSON-LD : un TABLEAU de trois elements
    [0] WebSite        [1] Organization        [2] JobPosting
  le JobPosting porte
    title · description (413 car.) · datePosted · employmentType
    baseSalary        { @type, currency, value }
    hiringOrganization{ @type, logo, name }      <- l'employeur est NOMME
    jobLocation       { @type, address }
    identifier        { @type, name, value }
```

*La forme du tableau compte&nbsp;: la racine du bloc est une LISTE et non un objet — un
lecteur qui suppose un objet **plante**, et un lecteur qui prend l'élément zéro obtient
l'identité du SITE au lieu de l'annonce.*

```
ET IL N'Y A AUCUN CONTACT A RETENIR — mesure DEUX fois et en DEUX endroits

sur le texte depouille (3 110 caracteres)
  courriel 0 · mailto: 0 · tel: 0 · neuf chiffres ancres 0 · +992 0
  suite de 7 a 12 chiffres 0
  mots contact/telephone (ru) 2, sans aucune VALEUR a cote
dans le JSON-LD
  aucune cle email, telephone ni applicationContact n'EXISTE
```

> **Donc un adaptateur ici ne doit PAS déclarer avoir retenu un contact.** *Déclarer avoir
> retenu ce que personne n'a déposé est le mensonge de `withheld_fields` — un mensonge sur
> NOUS et non sur le board — et il est indétectable par relecture puisque la sortie est
> identique dans les deux cas.*

```
TROIS PIEGES D'INSTRUMENT SUR UNE SEULE PAGE, et DEUX n'ont ete pris que parce
que quelque chose a CASSE, pas parce qu'on a relu

1. data-page="1" EST UN ATTRIBUT DE PAGEUR, PAS DE L'INERTIA
   mon dictionnaire de signatures a rapporte « Inertia data-page » : FAUX POSITIF
   l'unique occurrence est <div id="products-container" data-page="1">
   et la page porte ZERO `inertia`, ZERO `"component":`, ZERO id="app" porteur
   -> seul le parse JSON PLANTANT sur un entier l'a montre ; une relecture aurait
      consigne un fait faux sur la technologie de l'hote
      PRESENCE NECESSAIRE, PAS SUFFISANTE

2. UN NOM DE CLASSE N'EST PAS UN TYPE DE CONTENU
   la classe `manager-resumes-item` apparait 22 fois sur une page de VACANCE
   et ses 20 navigations onclick pointent toutes vers /vakanciya/
   -> le gabarit des resumes reutilise pour un bloc de vacances liees.
      J'ai failli ecrire que la page porte des CV sur la foi de ce nom ;
      ce qu'elle porte VRAIMENT, par href ordinaire, c'est 9 /resume/ et
      24 /soiskatel — une autre affirmation avec un autre nombre

3. 20 NAVIGATIONS SONT EN onclick="location.href=…", INVISIBLES A UN
   COMPTEUR DE <a href>
   a cote de 149 <a href> ordinaires (43 distincts)
   -> la famille __doPostBack : un compte d'href en manquerait un septieme
```

> **Et les trois erreurs s'évitent par UNE décision&nbsp;: lire le sitemap, le filtrer sur
> `/vakanciya/`, récupérer chaque annonce et ne lire que son `JobPosting`.** *Un compteur
> d'href manque les `onclick`&nbsp;; un lecteur de page entière ramasse des pages de
> candidats&nbsp;; le JSON-LD n'a ni l'un ni l'autre défaut et porte l'employeur, le salaire et
> la date.*

**Ce qui n'est PAS établi&nbsp;:** *la fin du pageur n'a pas été lue — l'issue la nommait
comme la première ligne de l'adaptateur, et le sitemap déclaré l'a rendue **inutile** plutôt
que répondue&nbsp;; la part vivante des 6 701 est inconnue, faute de `lastmod` dans 2,9 Mo&nbsp;;
`/ru/sitemap.xml`, le second déclaré, n'a pas été récupéré&nbsp;; et **une** annonce a été lue,
donc «&nbsp;le JSON-LD est complet&nbsp;» est une phrase sur UNE page et non sur 6 701* — une
fiche de famille ne revendique rien pour la famille sur un seul spécimen, et la même règle
vaut pour une annonce d'un board.

*Lisibilité&nbsp;: contrôlée avant toute conclusion d'absence et **déclarée NON EXERCÉE** ici —
le corps ne porte **aucune tête latine**, donc 0/0 se lit LISIBLE par défaut et non par
mesure.*

**Found by the Tajikistan search of #610 (a country never searched),
measured 2026-09-17 16:21–16:24 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #610: a Russian search («вакансии Душанбе сайт работа Таджикистан …»)
naming the national boards; the Russian networks it also names —
`tajikistan.hh.ru` (the hh network, excluded by the owner on 14.09),
`tj.superjob.ru`, `rabotago.com` — left aside as networks, not Tajik
boards; no public employment service found online. *A measurement, not
an adapter.*

```
_robots.allowed('korgar.tj', '/')   open, certain
GET https://korgar.tj/               200 ×2, identical — 21 ads, /vakanciya/<slug>_<id>, /vakancii?page=2 … 40, «Более 3000 вакансий»
```

The national generalist (Dushanbe, Khujand). `/vakancii?page=N`, its
last page, and the ad are the adapter's first line (its `adapter` issue).
