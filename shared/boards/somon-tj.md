# Board measurement — Somon.tj jobs (`somon.tj/vakansii/dushanbe/`, Tajikistan): **the tab is served WITHOUT A CLICK, the same Larixon template as Mongolia's Unegui — and its two on-page counters DISAGREE (5 507 against 8 202) where Unegui's agreed, so «the same figure twice» was a coincidence of one instance and not a property of the template**; and the expurgation hazard is entirely in the FREE TEXT, where no single digit pattern covers it

<!-- verified: 2026-10-06 -->

<!-- hosts: somon.tj -->
<!-- script: none -->
<!-- countries: TJ -->
<!-- route: browser · 5562 · 2026-10-06 -->
<!-- content: measured · **3 ADVERT PAGES FETCHED OF THE 60 THE LIST SERVES, and the reserve this card carried («no advert page was fetched, so the per-advert field shape comes from the LIST and the detail page is unread») is LIFTED, and three of its four findings correct this card.** *Three adverts read in a tab, the FIRST, the MEDIAN and the LAST of the 60 `/adv/` links the list serves — `/adv/17101345_menedzher-po-prodazham/`, `/adv/16038137_hr-spetsialist-otdela-kadrov/`, `/adv/16376037_farrosh/` — each URL taken FROM the list and never composed, and no interstitial on any of them.* **THE `JobPosting` LIVES INSIDE `@graph` AND NOT AT THE TOP LEVEL, WHICH IS THE TRAP: the single `application/ld+json` block has exactly two top-level keys, `@context` and `@graph`, so reading `@type` at the top level returns NOTHING and a check posed there publishes «this page carries no JobPosting».** *Measured in that order: the first read printed `types_ld: []`, and only looking inside `@graph` found `BreadcrumbList`, **`JobPosting`** and `WebPage`. It is the «a path prefix reads like a NATURE and is not one» family moved onto a JSON key — and the false negative it produces is a board declared structureless.* **AND THE HAZARD IS IN AD-HOC CHECKS AND NOT IN THE SHARED READER, WHICH WAS MEASURED RATHER THAN SUSPECTED: `_ldjson.postings()` — imported by 81 of our adapters — finds the `JobPosting` in ALL THREE forms, flat `@type`, nested in `@graph`, and inside a top-level array.** *So the false negative was mine, in a hand-written browser check, and the repo-wide defect I went looking for does not exist. One command answered it, and reading the source would not have.* THE `JobPosting`, KEY BY KEY ON THREE: `@id`, `@type`, `url`, `title`, `description`, `datePosted`, `validThrough`, `hiringOrganization` (`@type`, `name`), `identifier` (`@type`, `name`, `value`), `jobLocation` (`@type`, `address`), `mainEntityOfPage` — **eleven keys on two of the three and TWELVE on the third, which carries `baseSalary`.** ***So `baseSalary` is CONDITIONAL, and reading only two adverts would have produced exactly this card's neighbour's claim — «there is NO `baseSalary` at all». The third refuted it, and it is the one whose list title carries a figure («Фаррош 1 800 c.») where the other two are `Договорная`.*** **AND THE LIST IS RICHER THAN THE STRUCTURED BLOCK ON EXACTLY THAT FIELD**: the list shows a salary on 60 of 60 (37 negotiable, 23 a somoni figure) while the structured block carries one on 1 of 3 — *so an adapter that read only the JSON-LD would lose the negotiable majority, and one that read only the list would have no `validThrough`.* **`jobLocation.address` is `addressLocality` + `addressCountry` on 3 of 3 and carries NO `streetAddress`** — *the opposite of `yora.md` measured the same day, where a street arrived on 2 of 3: same country, same week, and the address granularity is not predicted by either.* **A CONTACT IS IN THE `description` OF 2 OF 3, AND THE TWO USE DIFFERENT PATTERNS — one an e-mail, the other a `+992` prefix, with the anchored nine-digit run touching NEITHER.** *So «no single pattern covers it», measured on the list over 60, is now measured again on the detail pages, and the field list is still empty: there is no `phone` and no `email` key to withhold. Counts only; no contact value is reproduced.* THE THREE COUNTERS MOVED WITHIN THE SAME DAY, AND THEIR GAP IS NOT CONSTANT: heading **5 507 → 5 562**, filter button **8 202 → 8 293**, site-wide placeholder **541 766 → 548 294**, read at 13:0x UTC against this card's own earlier reading. ***The heading/button difference went 2 695 → 2 731, so it is NOT a fixed offset — which REFUTES the most natural explanation of the discrepancy, that a filter button counts a constant other filter state.*** *The discrepancy stays recorded and unexplained, and the `route:` count is corrected from 5 507 to 5 562 with that reason: a board counter is a reading with an hour, not a state.* **AND ONE INSTRUMENT FINDING THAT WOULD READ THIS BOARD AS EMPTY: `document.body.innerText` returns 407 characters on the LIST page and 407 on every advert page, while `document.body.textContent` returns 151 976** — *so any emptiness or readability check built on `innerText` calls this template blank on every page it serves, and the 60 adverts are in the DOM the whole time. «Zero link is not zero content» moved onto the text accessor.* **A count taken on that 151 976 does NOT attribute to the advert either** — 71 anchored nine-digit runs, 8 e-mail-shaped strings and 10 messaging mentions for ONE advert page, because it carries the site chrome and the neighbouring adverts; *the attempt to narrow it to the advert's own container walked up to `body` in three steps and measured the same 151 976, so the per-advert instrument is the `JobPosting`'s own fields and nothing else.* **NO SCRIPT, AND THE REASON IS MEASURED RATHER THAN DEFERRED: the declared HTTP client is answered 403 on every path including `/robots.txt`, so a Python adapter would emit nothing and be classified NON FAISABLE under #404 — and 73 of the 75 cards carrying `route: browser` carry no script at all.** *A browser route is a procedure a session follows, and the owner's decision of 2026-09-13 counts it as delivered. Writing `somon.py` would SUBTRACT from coverage.* · 2026-10-06 -->
<!-- content: measured · **60 adverts read in the DOM, two on-page counters that DISAGREE (5 507 against 8 202), and a contact in the FREE TEXT of a large minority — 17 of 60 email-shaped, 11 of 60 carrying `+992`.** THE TAB IS SERVED WITHOUT A CLICK, which closes the question this card left open on 2026-09-17: no interstitial, no interaction, so borne 2 is respected rather than worked around and the 2026-09-07 decision applies — *the rules file still answers **403** to the declared client (`no-rules-403`, `certain: False`, an absence of rules and an open door under #283) and the transport still refuses it, while the tab renders.* **AND THE LARIXON FAMILY IS NOW MEASURED RATHER THAN HYPOTHESISED: the footer names `larixonclassifieds.com` → `larixon.com`, the same vendor `www.unegui.mn` names**, and the page architecture is the same to the element — a breadcrumb (`Все объявления` → `Вакансии`), a heading carrying a count, eight sub-categories each carrying a count beside a «show all» button, a sidebar of salary/schedule/experience facets, a `Loading` status, `/map/<section>/<city>/`, `onelink.me` app links and `/profile/login/?next=` gating. *So the template predicted the ROUTE and the shape of the WITNESS, exactly as a shared template is supposed to — and nothing else.* **AND WHAT IT DID NOT PREDICT IS THE WITNESS ITSELF, WHICH IS THE POINT: Unegui's heading and filter button carried the SAME figure (7 761 twice); here the heading reads `Вакансии Душанбе 5 507` and the filter button reads `Показать 8 202 объявлений` — a difference of 2 695 on one page, with a search placeholder stating 541 766 for all categories.** *So «the same number in two elements» was a coincidence of one instance and not a property of the template, and a witness is named PER ELEMENT or not at all. The discrepancy is recorded and NOT explained: a filter button may count a different filter state than a city heading, and that is a reading from outside which this card does not make.* **60 adverts were read in the DOM (60 distinct `/adv/` links) against 5 507 or 8 202 stated — PARTIAL and declared partial.** THE ADVERT SHAPE: title, VIP flag, **a salary on 60 of 60** (37 `Договорная` — negotiable — and 23 a somoni figure), a description excerpt, a poster display name, a date-and-city string at CITY level (`Вчера Душанбе`), and a detail link `/adv/<id>_<slug>/`. *Unlike Unegui's, the location does NOT descend below the city — same template, different granularity, which is again the analysis the template does not predict.* **AND THE EXPURGATION QUESTION IS SETTLED HERE IN THE OPPOSITE WAY FROM KORGAR, WHICH IS WHY BOTH WERE WORTH MEASURING: there is no `phone` or `email` FIELD to withhold — and the FREE TEXT carries contacts on a large minority of adverts.** Counted over the 60 in the DOM: **17 email-shaped strings, 11 `+992` prefixes, 10 anchored nine-digit runs, 4 runs of ten to thirteen digits, 9 mentions of WhatsApp or Telegram**, and 24 containing a Russian or Tajik word for telephone. ***So no single pattern covers it: the anchored nine-digit rule catches 10 of 60, `+992` catches 11, a long-digit run catches 4, and the three overlap only partially — a field list is empty here and the hazard is entirely in prose the poster typed.*** **And the Burmese collision was CHECKED rather than assumed: the somoni salary is written with spaces (`25 000 - 50 000 c.`), so a digit-run rule does not destroy it — measured on this board, not transported from another.** *No contact value is reproduced anywhere in this card; only counts.* A FOURTH MALFORMED href OF THE NIGHT, for the record: the footer links «Наши вакансии» («our vacancies», the operator's own hiring) as `Https://job.somon.tj/` — **a capital-H scheme**. *Named, not followed: it is the operator's own recruitment and not this board.* WHAT IS NOT ESTABLISHED: **no advert page was fetched**, so the per-advert field shape comes from the LIST and the detail page is unread; the scroll or pagination behaviour is not established; the 5 507 / 8 202 discrepancy is not explained; `/map/vakansii/dushanbe/` was not followed; and the rules file remains unreadable, so what this host would refuse in writing is unknown rather than absent. METHOD: DNS on both host forms through two public resolvers — **and the addresses are NOT Cloudflare's** (82.39.253.10/.11), where `www.unegui.mn` sits on 104.18.1.50, so the «Just a moment...» copy is not by itself proof of which vendor fronts a host; the guard taken on the exact host and on three exact paths in a turn distinct from the retrieval; the tab read and then closed; the contact counts taken in the page by a script that returns COUNTS and never values · 2026-10-06 -->
<!-- witness: partial and MOVING — the heading reads **5 562** and the filter button **8 293** at 13:0x UTC, against 5 507 and 8 202 earlier the same day; **their difference went 2 695 → 2 731, so it is not a fixed offset** and the natural explanation of the discrepancy is refuted rather than confirmed. *60 adverts in the DOM against 5 562 or 8 293 stated, so the walk is PARTIAL and the board's size is not established.* **Three advert pages were fetched — first, median and last of the 60 — so the per-advert shape is now a statement about three pages and not about one**, and `baseSalary` being on 1 of 3 is why three were read rather than two · 2026-10-06 -->
<!-- witness: partial and PER ELEMENT — the heading states **5 507** for Dushanbe and a filter button states **8 202** on the same page, a difference of 2 695 that is recorded and not explained, with 541 766 stated site-wide for all categories; **60 adverts were read in the DOM**, so the walk is PARTIAL and the board's size is not established. *On the sister instance of the same template the two counters AGREED, so their agreement is not a property of the template and cannot be used as a check* · 2026-10-06 -->
<!-- content: indeterminate · **`/vakansii/dushanbe/` answers HTTP 403, 5 649 B, md5 5ef196ba98b9 / 7270f89cf0ec — «Just a moment...», a Cloudflare managed challenge (the `revolico` class) — under the declared identity, twice; the rules file could not be read (absence of rules, `certain: False`); nothing of the section was read** · 2026-09-17 -->
<!-- witness: none — nothing was served · 2026-09-17 -->

## Measured 2026-10-06 — l'onglet est servi SANS CLIC, et les deux compteurs de la page NE S'ACCORDENT PAS

```
le client HTTP declare, inchange depuis le 17.09
  /robots.txt            403   ->  no-rules-403, certain FALSE
                                   absence de regles, porte ouverte (#283)
  la garde                /, /vakansii/, /vakansii/dushanbe/  ->  TRUE, rule=None

l'onglet
  /vakansii/dushanbe/    SERVI, aucun interstitiel, AUCUNE interaction
  -> borne 2 respectee et non contournee ; decision du 07.09 appliquee
```

> **ET LA FAMILLE LARIXON EST MESURÉE, PLUS SUPPOSÉE&nbsp;:** *le pied de page nomme
> `larixonclassifieds.com` → `larixon.com`, **le même éditeur que `www.unegui.mn`**, et
> l'architecture est la même à l'élément près — fil d'Ariane `Все объявления` → `Вакансии`,
> un en-tête portant un compte, huit sous-catégories portant chacune le sien à côté d'un
> bouton «&nbsp;tout afficher&nbsp;», une colonne de facettes salaire/horaire/ancienneté, un état
> `Loading`, `/map/<section>/<ville>/`, des liens `onelink.me` et un
> `/profile/login/?next=`.*

**Donc le gabarit a prédit la ROUTE et la FORME du témoin — ce qu'un gabarit partagé est
censé prédire. Et rien d'autre.**

```
CE QU'IL N'A PAS PREDIT, ET C'EST LE POINT

Unegui   en-tete « Ажлын зар 7,761 »      bouton « 7,761 зар харуулах »   ACCORD
Somon    en-tete « Вакансии Душанбе 5 507 »
         bouton  « Показать 8 202 объявлений »                           DESACCORD
         placeholder « Поиск по 541 766 объявлениям »   (toutes categories)

  2 695 d'ecart sur une MEME page.
  -> « le meme chiffre dans deux elements » etait une COINCIDENCE d'une instance,
     pas une propriete du gabarit. Un temoin se nomme PAR ELEMENT ou pas du tout,
     et leur accord ne peut pas servir de controle.
  L'ecart est CONSIGNE et NON EXPLIQUE : un bouton de filtre peut compter un autre
  etat de filtre qu'un en-tete de ville, et c'est une lecture de l'exterieur que
  cette fiche ne fait pas.
```

```
60 ANNONCES LUES DANS LE DOM (60 liens /adv/ distincts) contre 5 507 ou 8 202
enonces -> PARTIEL, declare partiel

la forme d'une annonce
  titre · drapeau VIP · SALAIRE sur 60 sur 60 (37 « Договорная », 23 un chiffre
  en somonis) · extrait de description · un nom d'affichage de deposant ·
  une chaine date-et-ville au niveau de la VILLE (« Вчера Душанбе ») ·
  un lien /adv/<id>_<slug>/

  Contrairement a Unegui, le lieu ne descend PAS sous la ville.
  Meme gabarit, granularite differente : encore l'analyse que le gabarit ne predit pas.
```

```
L'EXPURGATION, TRANCHEE ICI A L'INVERSE DE KORGAR — et c'est pourquoi les deux
valaient d'etre mesurees

  aucun champ `phone` ni `email` n'existe : la liste de champs est VIDE
  et le TEXTE LIBRE porte des contacts sur une large minorite

  compte sur les 60 du DOM
    chaines en forme de courriel        17 / 60
    prefixe +992                        11 / 60
    suite de neuf chiffres ancree       10 / 60
    suite de dix a treize chiffres       4 / 60
    whatsapp ou telegram                 9 / 60
    un mot « telephone » (ru/tj)        24 / 60

  -> AUCUN motif unique ne couvre : l'ancre a neuf chiffres en prend 10, le +992
     en prend 11, la suite longue en prend 4, et les trois ne se recouvrent que
     partiellement. Le danger est entierement dans la prose que le deposant a tapee.

  ET LA COLLISION BIRMANE A ETE VERIFIEE, PAS SUPPOSEE :
     le salaire en somonis s'ecrit avec des espaces — « 25 000 - 50 000 c. » —
     donc une regle de suite de chiffres ne le detruit pas. Mesure sur CE board,
     pas transportee d'un autre.

  Aucune valeur de contact n'est reproduite ici : seulement des comptes.
```

**Un QUATRIÈME `href` malformé de la nuit, pour mémoire&nbsp;:** le pied de page lie
«&nbsp;Наши вакансии&nbsp;» («&nbsp;nos postes&nbsp;», le recrutement de l'exploitant lui-même) comme
**`Https://job.somon.tj/`** — *un schéma à H majuscule.* **Nommé, non suivi&nbsp;: c'est son
propre recrutement et non ce board.**

**Et le DNS dit quelque chose que la copie de la page ne dit pas&nbsp;:** `somon.tj` résout sur
**82.39.253.10/.11**, qui ne sont **pas** des adresses Cloudflare, là où `www.unegui.mn` est
sur 104.18.1.50 qui en est une. *Donc le texte «&nbsp;Just a moment...&nbsp;» n'est pas à lui seul
la preuve de quel fournisseur se tient devant un hôte.*

**Ce qui n'est PAS établi&nbsp;:** *aucune page d'annonce n'a été récupérée, donc la forme par
annonce vient de la LISTE et la page de détail est non lue&nbsp;; le défilement n'est pas
établi&nbsp;; l'écart 5 507 / 8 202 n'est pas expliqué&nbsp;; `/map/vakansii/dushanbe/` n'a pas été
suivi&nbsp;; et le fichier de règles reste illisible, donc ce que cet hôte refuserait par écrit
est **inconnu** et non **absent**.*

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
GET https://somon.tj/vakansii/dushanbe/   403, 5 649 B, md5 moving ×2 — «Just a moment...»
```

**A challenge in front of a classifieds site** (the same class as
`unegui.md`, `revolico.md`): not defeated, not asked of the user (borne 2);
a tab decides whether it is served without a click. INDÉTERMINÉ; the
issue says what blocks.
