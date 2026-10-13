# Board measurement — Leboncoin Emploi (`www.leboncoin.fr`): the largest French audience with no adapter — **the rules are READ, they name us, and they refuse both objects an adapter would need**: `/recherche` (the results page, the sweep) and, since this measurement, `/ad/` (the ad page itself), so borne 1 closes it to every route, the browser included

<!-- verified: 2026-10-13 -->

<!-- hosts: www.leboncoin.fr, leboncoin.fr -->
<!-- script: none -->
<!-- countries: FR -->
<!-- route: none · refus ECRIT dans un groupe qui NOUS NOMME, sur les deux objets d'un adaptateur — `/recherche` et `/ad/` rendus `allowed=False` par la garde EXECUTEE (`state: read`, `certain: True`, mesure du 2026-10-13T12:50:04Z) ; borne 1, donc ferme a toutes les voies, navigateur compris · reversible le jour ou le fichier change, et il a DEJA change une fois -->
<!-- content: measured · **THE FILE NAMES US, AND THE REFUSAL MOVED SINCE 2026-08-31**: 12 745 B of rules, `state: read`, `certain: True`, HTTP 200, md5 b7ec70c54a64, 2026-10-13T12:50:04Z, as Claude-User, read in a turn distinct from any other retrieval. There is **no `User-agent: *` group at all** — the file opens on prose, *"It's forbidden to use search robots or other automatic methods to access Leboncoin.fr"*, and everything after it is the list of exceptions granted. `Claude-User` is named, in a stack headed **`# LLMs / AI SEARCH / RETRIEVAL`** (lines 503-512, beside `OAI-SearchBot`, `PerplexityBot`, `Claude-SearchBot`, `Applebot`, `DuckAssistBot`, `MistralAI-Index`, `ChatGPT-User`, `Perplexity-User`, `MistralAI-User`), and that stack's rules (lines 513-531) are **17 `Disallow` lines** closing with `Allow: /ad/voitures/`, then `Disallow: /ad/`, then `Allow: /`. **THE GUARD WAS RUN, NOT READ**, one token at a time (§3 bis), on the paths an adapter would use: `/` -> `allowed=True`; `/recherche` -> `allowed=False`, rule `/recherche`; `/recherche/emploi` -> `allowed=False`, rule `/recherche`; `/ad/offres_d_emploi/<id>` -> **`allowed=False`, rule `/ad/`**; `/ad/voitures/<id>` -> `allowed=True` by the one carve-out, cars and not job ads; `/sitemap.xml` -> `allowed=True`, **deliberately not retrieved**, because every object it could name is refused and reading an index to reach refused objects honours the letter against the intention; `/offres-d-emploi` -> `allowed=True` and **what it serves is NOT established and was NOT probed** — on this host an allowed prefix is exactly the shape that has cost 34 894 people's CVs elsewhere, so the unknown is recorded as an unknown. **WHAT CHANGED, AND WHAT CANNOT BE ESTABLISHED**: `shared/boards/README.md` records, from the 2026-08-31 reading, a three-class table in which `/ad/` was refused to the TRAINING class only and ad pages stayed open to the retrieval class — which made `cover-letter <URL>` on a Leboncoin link a capability the README advertised as working *today*. Today the retrieval class is refused `/ad/` as well, verified on the raw block and not on the instrument's output. **Whether the file changed since 2026-08-31, or the 2026-08-31 table misread it, is NOT established and never will be: no body from that day was kept**, only the verdict. No `Crawl-delay` applies to our token. **AND THIS IS A LIMIT ON THE ROUTE, NOT A VERDICT ON THE BOARD**: §2 sexies reserves closure verdicts for the owner and names a written `Disallow` among the things it does not reverse · 2026-10-13 -->

<!-- witness: none found · and it cannot be otherwise by this route: the two refused paths were never retrieved, the one allowed index was deliberately left unread, and the one allowed prefix of unknown nature was not probed. The only objects measured are the 12 745-byte rules file and six guard verdicts · 2026-10-13 -->

## Measured 2026-10-13 — the guard was run on the paths, not on the host

```
robots.txt        12 745 o  state read, certain True, 200, md5 b7ec70c54a64, as Claude-User
  groupe *              AUCUN — le fichier n'en declare pas, il ouvre sur une phrase
  notre groupe          la pile « LLMs / AI SEARCH / RETRIEVAL », qui NOUS NOMME (l. 503-512)
  ses regles            17 Disallow (l. 513-531), dont Disallow: /ad/
  la seule derogation   Allow: /ad/voitures/   <- les voitures, pas les annonces d'emploi
  Crawl-delay pour nous AUCUN — l'allure serait la notre
  sitemap               permis, NON lu, expres

garde EXECUTEE, jeton claude-user, un seul jeton a la fois (§3 bis) :
  /                           allowed=True    rule (aucune)
  /recherche                  allowed=False   rule /recherche    <- borne 1, le balayage
  /recherche/emploi           allowed=False   rule /recherche    <- borne 1
  /ad/offres_d_emploi/<id>    allowed=False   rule /ad/          <- borne 1, NOUVEAU
  /ad/voitures/<id>           allowed=True    Allow: /ad/voitures/
  /sitemap.xml                allowed=True    rule (aucune)      <- non recupere
  /offres-d-emploi            allowed=True    rule (aucune)      <- nature INCONNUE, non sonde
```

**Ce que cette fiche RETIRE au dépôt.** La lecture du 31.08 laissait une capacité ouverte et le dépôt l'annonçait : la fiche par annonce, c'est-à-dire `cover-letter <URL>` sur un lien que l'utilisateur tend lui-même. Elle est fermée. Un utilisateur du plugin qui aurait suivi notre README se serait fait refuser par borne 1 — **une permission périmée fait AGIR à tort, et c'est la direction que personne n'audite.**

**Pourquoi aucune issue `adapter` n'accompagne cette fiche.** Une issue `adapter` existe pour qu'un utilisateur du plugin **vote** pour qu'on construise quelque chose. Tant que le refus écrit tient, il n'y a rien à construire, et le ticket porterait un « Done when » que personne ne peut satisfaire — le compte de §2 bis le proposerait alors à une session de plus, qui frapperait le même mur. Le jour où le fichier change, la mesure se refait et l'issue devient possible : c'est pour cela que cette fiche est **datée** et non conclue.

**Ce que cette fiche ne dit pas.** Ni que ce board ne nous intéresse pas — il est la plus grosse audience française sans adaptateur — ni qu'il est « fermé » au sens où ce verdict appartiendrait au propriétaire (§2 sexies), ni que les annonces d'emploi vivent **uniquement** sous `/recherche` et `/ad/` : `/offres-d-emploi` est permis et sa nature n'est pas établie. Et elle n'avance aucun motif du genre « mal adapté au modèle du plugin » : la seule raison retenue est celle que l'hôte a écrite.
