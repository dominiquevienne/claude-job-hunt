# Board measurement — Hanploi (`www.hanploi.com`): the French job board for disabled candidates — **the rules refuse nothing** (98 bytes, one comment line), and that is the easy half: the root was retrieved and carries **103 links of which NOT ONE names a job**, zero `JobPosting` and zero `ld+json`, so the listing route is **NOT established** — and it was deliberately not guessed

<!-- verified: 2026-10-12 -->

<!-- hosts: www.hanploi.com, hanploi.com -->
<!-- script: none -->
<!-- countries: FR -->
<!-- content: measured · **98 OCTETS DE REGLES QUI NE REFUSENT RIEN, 103 LIENS EN RACINE, 0 ANNONCE NOMMEE — ET AUCUNE LIGNE `route:` N'ACCOMPAGNE CETTE FICHE, CE QUI EST UN CHOIX MESURE.** Le vocabulaire du depot en admet trois — `browser`, `http`, `none` — et les trois mentiraient ici : `none` dirait non faisable quand rien ne refuse, `http` revendiquerait une route qui n'est pas etablie, et un quatrieme mot a ete ECRIT puis RETIRE parce que la garde du depot l'a refuse dans le tour meme (`test_the_repository_declares_every_browser_reading_and_no_route_to_nothing`) — ce qui est la bonne issue : une fiche a deja porte douze jours un etat hors vocabulaire avec toute la suite au vert. Donc la ligne se RETIRE plutot que de porter un mot qui decrit autre chose, et son absence est ce fait-ci. **AUCUN `Crawl-delay` N'EST ECRIT dans les 98 octets** — ni pour nous ni pour personne — donc l'allure serait la notre a poser, et un fichier muet sur le debit ne promet aucune absence de limite. **ZERO LIEN N'EST PAS ZERO CONTENU, ET C'EST EXACTEMENT POURQUOI CETTE FICHE NE CONCLUT PAS.** Regles : 98 o, HTTP 200, md5 bb355737b4d2, 2026-10-12T20:55:03Z, comme Claude-User, lues dans un tour distinct. Le corps entier est `# See http://www.robotstxt.org/robotstxt.html for documentation on how to use the robots.txt file` — le MEME gabarit Rails que `www.staffsante.fr` a un `s` pres, donc ni l'un ni l'autre n'a pese la question de nous ouvrir. Garde EXECUTEE, un seul jeton : `/` `True`, `/offres` `True`, rule `None` dans les deux cas. **LA RACINE A ETE EXERCEE ET ELLE NE PORTE PAS SES ANNONCES** : 198 555 o, md5 937d7a1a3c3c, **103** `href`, et le seul qui nomme un emploi part vers un site TIERS (`thransition.com`) ; zero `application/ld+json`, zero `JobPosting`, zero `ld&#x2B;json` (la forme echappee, cherchee parce qu'une entite HTML a deja fait conclure a tort qu'une page ne portait pas de JSON-LD). **CE QUE SON BALISAGE UTILISE A ETE CHERCHE PLUTOT QUE SUPPOSE, et le resultat est negatif sur tous les porteurs connus** : pas de `__NEXT_DATA__`, pas de `data-page` (Inertia), pas de `self.__next_f`, pas de `window.__`, aucun `id="root"` ni `id="app"`, aucun marqueur React, Angular ou Vue. Ce qui est la : une empreinte d'actif `/assets/front-<sha256>.js` et un jeton `csrf`, donc une application **Rails rendue cote serveur** — ce qui rend l'absence de liens d'annonce informative : les annonces sont derriere un chemin ou un formulaire que la racine ne nomme pas. **ET CE CHEMIN NE SE DEVINE PAS** : un prefixe de chemin se lit comme une nature et n'en est pas une, et sonder au hasard produit soit un 404 derriere un 403, soit un chemin qui marche et masque celui qui ne marche pas · 2026-10-12 -->

<!-- witness: none found · la racine a ete recuperee et elle ne porte aucune annonce — ni en liens, ni en JSON-LD, ni dans aucun porteur de donnees connu. Aucun autre chemin n'a ete recupere, donc aucun temoin n'est etabli et aucun ne peut l'etre avant que la route de liste soit trouvee · 2026-10-12 -->

## Measured 2026-10-12 — the rules are the easy half

```
robots.txt               98 o   state read, certain True, 200, md5 bb355737b4d2, as Claude-User
  User-agent                 0   ·   Disallow   0        gabarit Rails, cf. www.staffsante.fr

garde EXECUTEE, jeton claude-user :
  /                              allowed=True   rule None
  /offres                        allowed=True   rule None

racine                198 555 o   200, md5 937d7a1a3c3c
  href                     103   dont 0 nommant une annonce (le seul part vers thransition.com)
  application/ld+json        0   ·  ld&#x2B;json  0  ·  JobPosting  0
  __NEXT_DATA__ · data-page · self.__next_f · window.__ · id=root|app · React|Angular|Vue   0
  ce qui EST la            /assets/front-<sha256>.js  +  csrf   -> Rails, rendu cote serveur
```

**Ce que cette fiche ne dit pas.** Ni que ce board est vide — c'est precisement la lecture qu'un « zero lien » invite a faire et qu'elle refuse ; ni qu'il est ferme — rien ne refuse quoi que ce soit ; ni par quel chemin ses annonces vivent. **L'indetermine porte sur la ROUTE INTERROGEE, c'est-a-dire la racine, et jamais sur l'hote.**

**Ce qui leverait l'indetermine, et qui coute une requete chacune** : le formulaire de recherche de la racine (sa methode et sa cible, lisibles dans les 198 555 o deja detenus, donc sans requete), un `sitemap.xml` non declare mais usuel, ou le chemin que le menu de navigation designe. **Rien de cela n'a ete fait dans ce tour et c'est declare ici plutot que laisse en silence**, parce qu'une route indeterminee et une route absente se lisent pareil dans une colonne.
