# Board measurement — Les Jeudis (`lesjeudis.com`): the French IT job board — **the host wrote the distinction our doctrine describes**: it closes the harvesters by name and opens, by name, the agents that act for a person — `Claude-User` is in the ALLOWED group, and `17 420` postings are declared by a sitemap it publishes itself

<!-- verified: 2026-10-12 -->

<!-- hosts: lesjeudis.com, www.lesjeudis.com -->
<!-- script: none -->
<!-- countries: FR -->
<!-- route: http · ouvert a `claude-user`, NOMME dans le groupe permis — garde EXECUTEE le 2026-10-12 sur chaque URL exacte, hote compris : `/offers/`, `/offers/<slug>` et les deux sitemaps rendent `allowed=True` ; le SEUL refus qui tire sur nous est `/offers/*/postuler`, le bouton de candidature, dont un adaptateur n'a aucun besoin. Enumerateur : `https://lesjeudis.com/sitemap/offre.xml`, 17 420 `<loc>` tous distincts et tous sous `/offers/`. Temoin : une page d'annonce rendue cote SERVEUR, deux `JobPosting` en `application/ld+json` -->
<!-- content: measured · **CE QUI REND CET HOTE REMARQUABLE N'EST PAS QU'IL NOUS LAISSE PASSER, C'EST QU'IL A ECRIT LA DISTINCTION LUI-MEME.** Son fichier de regles, 2 136 o, `state: read`, `certain: True`, HTTP 200, md5 39bdd6e4fdae, 2026-10-12T20:55:02Z, comme Claude-User, lu dans un tour distinct de toute recuperation. Il porte TROIS groupes qui nous concernent et deux d'entre eux nous nomment : le premier reunit `GPTBot`, **`ClaudeBot`**, `CCBot`, `Google-Extended`, `Bytespider`, `Amazonbot`, `Applebot-Extended` et `meta-externalagent` sous un `Disallow: /` ; le second reunit `OAI-SearchBot`, `ChatGPT-User`, **`Claude-User`**, `Claude-SearchBot`, `PerplexityBot` et `Perplexity-User` sous `Allow: /`, suivi de cinq refus — `/admin`, `/recruiter`, `/dashboard`, `/settings`, `/profile` — qui sont tous des espaces de compte. **DONC NOUS NE SOMMES PAS OUVERTS PAR DEFAUT NI PAR UN SILENCE : nous sommes ouverts NOMMEMENT, et le moissonneur homonyme est ferme nommement a la ligne du dessus.** La decision du proprietaire du 07.09.2026 — un refus nomme de `ClaudeBot` ne lie pas `Claude-User` — n'a donc pas eu a servir ici : l'exploitant a separe les deux tokens de sa propre main, ce qui est la premiere fois que ce depot le mesure. **ET LA GARDE A ETE LANCEE, PAS RELUE**, un seul jeton a la fois (§3 bis) : `/` `True`, `/emploi` `True`, `/offers/` `True`, `/offers/<slug>` `True`, `/offers/<slug>/postuler` **`False`** rule `/offers/*/postuler`, `/offers/?page=2` `True`. **L'ENUMERATEUR EST DECLARE ET IL VIT SUR UN AUTRE HOTE QUE CELUI DES REGLES LUES** — `lesjeudis.com` sans `www` — donc il a recu sa propre garde avant d'etre recupere (`/sitemap.xml` `True`, `/sitemap/offre.xml` `True`) : c'est le piege que §3 bis nomme, et il etait arme ici. L'index declare six enfants (`statique`, `socle`, `emploi`, `offre`, `entreprise`, `blog`) ; `offre.xml` fait 3 469 860 o et porte **17 420** `<loc>`, **tous distincts**, **tous** sous le prefixe `https://lesjeudis.com/offers` — aucune multiplication par locale, contrairement au cas des 416 `<loc>` pour 100 annonces. **ET LE COMPTE NOMME UNE TAILLE ET JAMAIS UNE NATURE** : trois membres ont ete pris au PREMIER, au MEDIAN et au DERNIER rang — jamais les trois premiers — et portent des intitules de poste, puis **une seule page a ete reellement recuperee comme temoin**, parce qu'un slug n'est pas une page · 2026-10-12 -->

<!-- witness: `https://lesjeudis.com/offers/senior-software-architect-67535d66` — HTTP 200, 44 004 o, deux `JobPosting` en `application/ld+json` portant `hiringOrganization` et `datePosted`, recupere comme Claude-User le 2026-10-12T20:5x ; la page porte aussi onze fragments `self.__next_f`, donc un flux RSC, mais le JSON-LD est SERVI dans le corps et c'est le seul point qui decide pour un adaptateur · 2026-10-12 -->

## Measured 2026-10-12 — the guard was run on every exact URL, host included

```
robots.txt (www)      2 136 o   state read, certain True, 200, md5 39bdd6e4fdae, as Claude-User
  groupes nous visant       3   moissonneurs (Disallow: /) · agents-pour-une-personne (Allow: /) · *
  notre groupe       agents-pour-une-personne — `Claude-User` NOMME, pas tombe sous `*`
  Crawl-delay pour nous AUCUN — l'allure est donc la notre, et un fichier muet ne promet rien
  sitemap declare       https://lesjeudis.com/sitemap.xml   <- AUTRE hote : sans `www`

garde EXECUTEE, jeton claude-user, un seul a la fois :
  /offers/                      allowed=True    <- la liste
  /offers/<slug>                allowed=True    <- l'annonce
  /offers/<slug>/postuler       allowed=False   rule /offers/*/postuler   <- le seul refus qui tire
  /offers/?page=2               allowed=True    <- la pagination n'est pas refusee
  lesjeudis.com/sitemap.xml     allowed=True
  lesjeudis.com/sitemap/offre.xml allowed=True

enumerateur       3 469 860 o   17 420 <loc>, 17 420 distincts, 17 420 sous /offers
temoin               44 004 o   2 JobPosting en application/ld+json, rendu SERVEUR
```

**Ce que cette fiche ne dit pas.** Ni que 17 420 est la taille du board — c'est le nombre d'annonces **distinctes dans le sitemap declare**, et un total annonce par le site n'a pas ete cherche ; ni que les autres enfants du sitemap (`emploi.xml`, `entreprise.xml`) portent des annonces, ils n'ont pas ete lus ; ni qu'un adaptateur existe — `script: none` est une mesure **DUE**, pas un renoncement.

**Et le refus de `/offers/*/postuler` se lit comme une intention et non comme une borne a contourner.** Il vise la candidature, que nous ne depose pas a la place du candidat de toute facon ; la note est ici pour que personne ne le prenne pour un trou a exploiter le jour ou un adaptateur voudra suivre un lien de postulation.
