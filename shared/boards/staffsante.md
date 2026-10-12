# Board measurement — Staffsante (`www.staffsante.fr`): the French healthcare job board — **the rules refuse nothing at all** (99 bytes, one comment line, no `User-agent` and no `Disallow`), and the listing route is DECLARED by the root's own markup as `/offres-emploi-<famille>` and `/offres-emploi-chez-<employeur>-<id>`, so it was read rather than guessed

<!-- verified: 2026-10-12 -->

<!-- hosts: www.staffsante.fr, staffsante.fr -->
<!-- script: none -->
<!-- countries: FR -->
<!-- route: http · aucune regle ne refuse quoi que ce soit — 99 o, `state: read`, `certain: True`, et le fichier ne porte QU'UNE ligne de commentaire : zero `User-agent`, zero `Disallow`. Garde EXECUTEE le 2026-10-12 : `/` et `/offres-emploi` rendent `allowed=True`, rule `None`. Route de liste DECLAREE par le balisage de la racine : `/offres-emploi-<famille>` et `/offres-emploi-chez-<employeur>-<id>`. **CE QUI RESTE DU est d'exercer une page de LISTE** : la racine a ete recuperee (136 870 o) et n'est pas une page d'annonce, donc le rendu des annonces n'est PAS etabli -->
<!-- content: measured · **UN FICHIER QUI NE REFUSE RIEN N'EST PAS UN FICHIER QUI AUTORISE TOUT, ET LES 99 OCTETS DISENT MOINS QU'IL N'Y PARAIT.** Regles : 99 o, HTTP 200, md5 6363df73ea66, 2026-10-12T20:55:02Z, comme Claude-User, lues dans un tour distinct. Le corps entier est `# See https://www.robotstxt.org/robotstxt.html for documentation on how to use the robots.txt file` — **donc `state: read` et `certain: True`, et non une absence de fichier** : l'hote a repondu, il n'a simplement rien ecrit. **ET CE N'EST PAS L'INTENTION D'UN EXPLOITANT, C'EST UN GABARIT** : `www.hanploi.com` sert le MEME texte a un `s` pres (98 o contre 99, `http` contre `https`), ce qui est le `robots.txt` par defaut de Rails — donc cet hote n'a pas pese la question de nous ouvrir, il n'a pas touche au fichier. L'absence de `Crawl-delay` ne promet donc aucune absence de limite, et l'allure est la notre a poser. **LA ROUTE DE LISTE A ETE LUE, PAS DEVINEE** : la racine declare elle-meme `href="/offres-emploi-administration-et-direction"` et une serie de `href="/offres-emploi-chez-<employeur>-<id>"`, donc le prefixe vient du balisage de l'hote. **ET LE VERDICT DE RENDU N'EST PAS PRIS** : la racine porte UN `application/ld+json` et ZERO `JobPosting`, ce qui ne dit rien des pages d'annonce — un verdict de rendu pris sur `/` ne decrit pas une annonce, et cette fiche ne pretend donc pas savoir si les annonces sont servies ou rendues cote client · 2026-10-12 -->

<!-- witness: none yet · la racine a ete recuperee (136 870 o, md5 932fa576005d, HTTP 200, 2026-10-12) et elle n'est pas une page d'annonce : elle porte ZERO `JobPosting`. Aucune page de LISTE ni d'ANNONCE n'a ete recuperee, donc aucun temoin n'est etabli — c'est une mesure DUE et nommee, pas une absence constatee · 2026-10-12 -->

## Measured 2026-10-12 — the rules, and the route the host declares itself

```
robots.txt               99 o   state read, certain True, 200, md5 6363df73ea66, as Claude-User
  User-agent                 0   aucun groupe
  Disallow                   0   aucun refus
  MEME TEXTE que www.hanploi.com a un `s` pres -> gabarit Rails, pas une intention

garde EXECUTEE, jeton claude-user :
  /                              allowed=True   rule None
  /offres-emploi                 allowed=True   rule None

racine                136 870 o   200, md5 932fa576005d — 1 application/ld+json, 0 JobPosting
route de liste DECLAREE par son propre balisage :
  /offres-emploi-<famille>                 ex. /offres-emploi-administration-et-direction
  /offres-emploi-chez-<employeur>-<id>     ex. /offres-emploi-chez-anrs
```

**Ce que cette fiche ne dit pas.** Ni combien d'annonces porte ce board — aucun compte n'a ete pris ; ni que les annonces sont servies dans le corps — la racine ne le dit pas et une page de liste n'a pas ete lue ; ni que l'hote nous a ouvert deliberement — son fichier est un gabarit non touche, ce qui est une ouverture de fait et non un consentement ecrit. **Et un fichier muet ne dit pas qu'il n'y a pas de limite de debit** : neuf requetes en deux minutes trente ont deja suffi a declencher un interstitiel sur un hote sans delai ecrit, donc la cadence se pose par nous.
