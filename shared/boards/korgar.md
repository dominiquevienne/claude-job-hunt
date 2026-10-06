# Board measurement — Korgar (`korgar.tj`, Tajikistan): **its declared sitemap is the right WITNESS and the wrong ROUTE** — 42 851 `<loc>` of which **81.4 % are candidate CVs** and 6 701 are vacancies, against a root that claims «Более 3000»; the advert page serves a complete JSON-LD `JobPosting` with **no contact field at all**, and three instrument traps sit on that one page

<!-- verified: 2026-10-06 -->

<!-- hosts: korgar.tj -->
<!-- script: none -->
<!-- countries: TJ -->
<!-- content: measured · **42 851 `<loc>` in the declared sitemap, of which 34 894 — 81.4 % — are CANDIDATE CVs and 6 701 are vacancies; the advert page serves a complete JSON-LD `JobPosting` and NO contact field; and three instrument traps sit on that one page.** THE DECLARED SITEMAP IS THE RIGHT WITNESS AND THE WRONG ROUTE, which is an EIGHTH way a declared sitemap fails to be one and the first where the failure is a HAZARD rather than an irrelevance: `korgar.tj/sitemap.xml` answers 200 with **2 941 163 B and 42 851 `<loc>` (42 761 distinct, so 90 exact duplicates) and ZERO `<lastmod>`**, and its composition by first path segment is **`/rezume/` 33 646 (78.5 %), `/resume/` 1 248 (2.9 %) — a SECOND spelling, so 34 894 CV URLs in all — `/vakanciya/` 6 701 (15.6 %) and `/vakancii` 1 248 (category lists)**. *So a job board's declared sitemap enumerates, four URLs in five, the résumés of job SEEKERS — and the rules protect none of them: the file is 105 B with **0 `Disallow` and 0 `Allow`**, `read` and `certain`, and the guard returns `allowed=True` with `rule=None` on `/rezume/x_1` exactly as on `/vakanciya/x_1`.* **An adapter that walked the declared sitemap — the cheapest enumerator, and the one this repository's doctrine generally prefers — would harvest 34 894 CVs. NOT ONE `/rezume/` OR `/resume/` URL WAS FETCHED AND NONE WILL BE: what is measured here is the sitemap's COMPOSITION, never its content.** AND THE COUNT PAIR, BOTH STATED AND NEITHER RECONCILED: the sitemap carries **6 701** vacancy URLs against the root's «Более 3000 вакансий» — *so the site's own round marketing claim understates by a factor of about 2.2, the sitemap is the better witness for the size, and because it carries no `lastmod` an unknown share of the 6 701 may be expired.* **THE ADVERT PAGE IS CLEAN AND STRUCTURED, which is what makes the route cheap:** one real URL taken FROM the sitemap (never composed) answers 200 at 83 405 B and carries a JSON-LD **array of three** whose third element is a complete `JobPosting` — `title`, `description` (413 characters), `datePosted`, `employmentType`, **`baseSalary` as an object (`@type`, `currency`, `value`)**, **`hiringOrganization` (`@type`, `logo`, `name`) so the employer is named**, `jobLocation` (`@type`, `address`) and `identifier` (`@type`, `name`, `value`). *The array shape matters: the root of the block is a LIST, not an object, and the first two elements are `WebSite` and `Organization` — a reader that assumes an object crashes, and one that takes element zero gets the site's own identity instead of the advert.* **AND THERE IS NO CONTACT TO WITHHOLD, MEASURED TWICE AND IN TWO PLACES:** on the tag-stripped text (3 110 characters) **0 email addresses, 0 `mailto:`, 0 `tel:`, 0 anchored nine-digit runs, 0 `+992`, 0 runs of seven to twelve digits** — and 2 occurrences of the Russian words for contact/telephone with no value beside them — and in the JSON-LD no `email`, no `telephone`, no `applicationContact` key exists at all. ***So an adapter here must NOT declare that it withheld a contact: declaring you withheld what nobody published is the `withheld_fields` lie, which is a lie about US and not about the board, and it is indetectable by re-reading because the output is identical either way.*** **THREE INSTRUMENT TRAPS ON ONE PAGE, AND TWO WERE CAUGHT ONLY BECAUSE SOMETHING BROKE RATHER THAN BECAUSE ANYTHING WAS RE-READ.** *(1)* **`data-page="1"` IS A PAGER ATTRIBUTE, NOT INERTIA.** My signature dictionary reported «Inertia `data-page`» and it was a FALSE POSITIVE: the single occurrence sits on `<div id="products-container" data-page="1">`, and the page carries **zero** `inertia`, **zero** `"component":` and **zero** `id="app"` bearing the attribute. *Only the JSON parse CRASHING on an integer revealed it; a reading would have recorded a false fact about the host's technology, and this repository's own note tells you to LOOK for `data-page` without saying the attribute alone is ambiguous. **Presence is necessary and not sufficient.*** *(2)* **A CLASS NAME IS NOT A CONTENT TYPE.** The class `manager-resumes-item` appears **22** times on a VACANCY page, and its 20 `onclick` navigations all point at `/vakanciya/` — the résumés template reused for a related-vacancies block. *I nearly wrote that the advert page carries CVs on the strength of that name; what it actually carries, by ordinary `href`, is **9** `/resume/` and **24** `/soiskatel` links, which is a different claim with a different number.* *(3)* **20 NAVIGATIONS ARE BY `onclick="location.href=…"` AND INVISIBLE TO AN href COUNTER**, beside 149 ordinary `<a href>` (43 distinct) — the `__doPostBack` family, on a site where an href count would miss a seventh of the links. **AND THE THREE ERRORS ARE AVOIDED BY ONE DECISION:** read the sitemap, filter it to `/vakanciya/`, fetch each advert and parse the JSON-LD `JobPosting` and nothing else. *An href counter misses the onclick navigations; a whole-page reader picks up candidate pages; the JSON-LD has neither problem and carries the employer, the salary and the date.* WHAT IS NOT ESTABLISHED: **the pager's end was NOT read** — the issue named `/vakancii?page=N` and its last page as the adapter's first line, and the declared sitemap made that unnecessary rather than answered it; **what share of the 6 701 is live is unknown**, there being no `lastmod` anywhere in 2.9 MB; `/ru/sitemap.xml`, the second declared one, was not fetched; and one advert was read, so «the JSON-LD is complete» is a statement about ONE page and not about 6 701 — *a card of FAMILY claims nothing for the family on one specimen, and the same rule holds for one advert of a board*. METHOD: DNS on both host forms through two public resolvers; the rules re-read (105 B, `read`, `certain`, two sitemaps declared — which the issue did not mention); the guard taken on every exact path in turns distinct from the retrievals and exercised in both directions; the advert URL taken FROM the sitemap rather than composed; readability checked before any conclusion of absence, and declared UNEXERCISED here — the body has **no latin lead at all**, so 0/0 reads LISIBLE by default and not by measurement; no `Crawl-delay` anywhere, so our own 2 s applied · 2026-10-06 -->
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
                  34 894   81,4 %   de CV au total
    /vakanciya/    6 701   15,6 %   les annonces (detail)
    /vakancii      1 248    2,9 %   les listes de categorie
```

> **HUITIÈME façon dont un sitemap déclaré échoue à être un témoin — et la PREMIÈRE où
> l'échec est un DANGER et non une inutilité.** *Les sept précédentes ne donnaient pas ce
> qu'on voulait&nbsp;; celle-ci donne ce qu'il ne faut pas prendre.*

**Et les règles n'en protègent aucun&nbsp;:** 105 octets, **0 `Disallow`**, et la garde rend
`allowed=True` avec `rule=None` sur `/rezume/x_1` **exactement comme** sur `/vakanciya/x_1`.
**Un adaptateur qui marcherait le sitemap déclaré — l'énumérateur le moins cher, et celui
que la doctrine de ce dépôt préfère d'ordinaire — moissonnerait 34 894 CV.**

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
