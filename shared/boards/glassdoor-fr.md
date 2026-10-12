# Board measurement — Glassdoor France (`www.glassdoor.fr`): **the rules are READ and they refuse, in writing, every job-detail page** — `/job-listing/*_IE*.htm`, `/job-listing/details.htm?*` and `/partner/*` all return `allowed=False`, and the listing's pagination token `_IP` is refused too, so what remains allowed is page one of a sorted search whose items cannot be opened

<!-- verified: 2026-10-12 -->

<!-- hosts: www.glassdoor.fr, glassdoor.fr -->
<!-- script: none -->
<!-- countries: FR -->
<!-- route: none · refus ECRIT au groupe `*`, ou nous tombons, sur les objets memes d'un adaptateur : la PAGE D'ANNONCE (`/job-listing/*_IE*.htm`, `/job-listing/details.htm?*`, `/partner/*`) et la PAGINATION de la liste (`/Emploi/*_IP*`, `/Emplois/*_IP*.htm*`, `/Emplois/*_P*.htm*`), tous rendus `allowed=False` par la garde EXECUTEE le 2026-10-12 ; borne 1, donc ferme a toutes les voies, navigateur compris · reversible le jour ou le fichier change -->
<!-- content: measured · **CE QUI EST ALLOUE NE SUFFIT PAS, ET C'EST LA MESURE QUI LE DIT.** Regles : 4 958 o, `state: read`, `certain: True`, HTTP 200, md5 435f50dbafce, 2026-10-12T20:55:03Z, comme Claude-User, lues dans un tour distinct de toute recuperation. Le fichier nomme **`anthropic-ai`, `Claude-Web` et `ClaudeBot`** et ne nomme **NI `Claude-User` NI `Claude-SearchBot`**, donc nous tombons sous `*` par la decision du proprietaire du 07.09.2026 — et c'est bien sous `*` que le refus nous atteint, pas par emprunt a un groupe sous lequel nous ne nous presenterions pas. **GARDE EXECUTEE, un seul jeton a la fois** : `/Emploi/france-emplois-SRCH_IL.0,6_IN86.htm` `True` ; `/Emploi/france-emplois-SRCH_IL.0,6_IN86_IP2.htm` **`False`** rule `/Emploi/*_IP*` ; `/job-listing/<slug>-JV_IC<n>_KO0,14_IE<n>.htm` **`False`** rule `/job-listing/*_IE*.htm` ; `/job-listing/details.htm?jl=<n>` **`False`** rule `/job-listing/details.htm?*` ; `/partner/jobListing.htm?jl=<n>` **`False`** rule `/partner/`. **`_IP<n>` EST LE JETON DE PAGINATION DE CE PRODUIT ET `_IE<n>` CELUI DE L'EMPLOYEUR D'UNE ANNONCE** : le refus ne porte donc pas sur un recoin administratif, il porte sur la deuxieme page de toute liste et sur toute fiche d'annonce. **AUCUN SITEMAP N'EST DECLARE** — `grep '^Sitemap'` rend ZERO sur les 4 958 o — donc il n'existe meme pas d'enumerateur permis vers lequel se rabattre, et la question « lire un index pour atteindre des objets refuses » ne se pose pas ici. **AUCUN `Crawl-delay` NE NOUS VISE**, ce qui ne promet aucune absence de limite. **ET CE N'EST PAS TRANSPOSE DE L'ESPAGNE** : #1032 avait mesure la meme forme sur `glassdoor.es`, et la convention de ce depot est une fiche par instance pays — Hays FR vers ES et Randstad CH vers ES ont deja montre que la meme question sur une locale soeur peut avoir des reponses opposees, donc le fichier francais a ete lu pour lui-meme · 2026-10-12 -->

<!-- witness: none found · et il ne peut pas en exister par cette route : les pages d'annonce sont refusees par ecrit, aucun sitemap n'est declare, et la page 1 de recherche permise n'a PAS ete recuperee — la sonder pour compter des elements qu'on ne peut pas ouvrir aurait ete une requete pour rien. Les seuls objets mesures sont le fichier de 4 958 o et neuf verdicts de garde · 2026-10-12 -->

## Measured 2026-10-12 — what is allowed, and why it is not a route

```
robots.txt            4 958 o   state read, certain True, 200, md5 435f50dbafce, as Claude-User
  nos jetons NOMMES             anthropic-ai · Claude-Web · ClaudeBot
  nos jetons NON nommes         Claude-User · Claude-SearchBot  -> groupe `*` (decision 07.09)
  Crawl-delay pour nous         AUCUN
  Sitemap declare               AUCUN   (grep '^Sitemap' rend 0)

garde EXECUTEE, jeton claude-user :
  /Emploi/…-SRCH_IL.0,6_IN86.htm        allowed=True    <- la page 1, triee
  /Emploi/…-SRCH_IL.0,6_IN86_IP2.htm    allowed=False   rule /Emploi/*_IP*
  /job-listing/…_IE12345.htm            allowed=False   rule /job-listing/*_IE*.htm
  /job-listing/details.htm?jl=123       allowed=False   rule /job-listing/details.htm?*
  /partner/jobListing.htm?jl=123        allowed=False   rule /partner/
```

**Pourquoi aucune issue `adapter` n'accompagne cette fiche.** Une issue `adapter` existe pour qu'un utilisateur du plugin **vote** pour qu'on construise quelque chose ; ici l'objet a construire est refuse par ecrit, donc le ticket inviterait a batir ce qu'une borne 1 ferme par toutes les voies. Le jour ou le fichier change, la mesure se refait et l'issue devient possible.

**Ce que cette fiche ne dit pas.** Ni que ce board est « ferme » au sens ou ce verdict appartiendrait au proprietaire — un `Disallow` ecrit est justement l'une des choses que cette reserve ne renverse pas ; ni qu'un defi antirobot garde cet hote : #1032 en decrit un sur l'instance espagnole, **il n'a pas ete eprouve ici et ne doit pas l'etre**, puisque le sonder voudrait dire tendre la main vers un objet deja refuse. La seule raison retenue est celle que l'hote a ecrite.

**Et la page 1 permise n'est pas un repli utilisable**, meme si quelqu'un voulait s'en contenter : un taux ou un compte pris sur la page 1 d'une recherche mesure le TRI, pas le board — et ses elements renvoient vers des URL que les regles refusent.
