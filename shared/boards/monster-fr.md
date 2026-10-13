# Board measurement — Monster France (`www.monster.fr`): the French instance serves no board of its own — every path redirects off the host, and **the destination, on another host, answers 403 behind a DataDome challenge**, so borne 2 closes it to every route, the browser included

<!-- verified: 2026-10-13 -->

<!-- hosts: www.monster.fr, monster.fr -->
<!-- script: none -->
<!-- countries: FR -->
<!-- route: none · l'hote ne sert aucun board : il renvoie hors de lui-meme, et la destination (`www.monster.com/fr/`, un AUTRE hote) rend 403 derriere un defi DataDome — borne 2, un controle antirobot ne se dejoue pas et ne se confie pas a l'utilisateur du plugin, donc ferme a toutes les voies, navigateur compris ; les REGLES, elles, sont ouvertes, ce qui est precisement pourquoi le renversement du 07.09 ne s'applique pas ici (mesure du 2026-10-13T12:51:35Z a 12:52:54Z) · reversible le jour ou la destination repond -->
<!-- content: measured · **THREE MEASUREMENTS, AND THE HOST THAT ANSWERS IS NOT THE HOST ASKED**: (1) `https://www.monster.fr/robots.txt` -> **HTTP 403**, 774 B, body not kept, `final_url` **`https://www.monster.com/fr/`** — the French host redirects off itself, and the refusal arrives from the destination. Provenance records `server CloudFront`, `x-cache LambdaGeneratedResponse from cloudfront`, `x-amz-cf-pop ZRH55-P2`. **A 403 on a rules file is an ABSENCE of rules** — the owner's decision of 2026-09-13, #283 — so `certain: False` and **nothing on `monster.fr` closes this board**. (2) `https://www.monster.com/robots.txt` -> **HTTP 200**, 1 804 B, md5 092e113a0d64, as Claude-User: a single `User-agent: *` group, **57 `Disallow`**, `claude-user` not named anywhere, no bare `Disallow: /`, and the guard RUN on the destination path returns `/fr/` -> **`allowed=True`** (`/` , `/jobs`, `/sitemap.xml` likewise; `Allow: /jobs/search?q=` is explicit while the other search parameters are refused). **So the rules are OPEN and borne 1 does not apply.** (3) `https://www.monster.com/fr/` -> **HTTP 403, three times**, 774 B each time, md5 **9aeaf086a1db**, then **40fbad4aa880**, then **c8db33d9fb43** — **the fingerprint MOVES per request, so no md5 comparison can decide borne 0 here** (§3 bis: fetch the same URL twice before comparing two md5, and a moving fingerprint means the body carries a rendering element). The third body was kept with `--allow-refusal` and it names **`geo.captcha-delivery.com`**, asks to *"enable JS and disable any ad blocker"*, and carries a `dd` payload whose `cid` and `hsh` change per request: **a DataDome antirobot challenge. BORNE 2 — it is never defeated and never handed to the plugin's user to defeat**, so the browser route the 2026-09-07 reversal would otherwise open is closed too. **WHAT IS NOT ESTABLISHED, AND THE PAGE SAID IT WAS**: the France page carried *"Fermé, vérifié en direct le 31.08.2026 — il n'y a plus de board français derrière"*. **A challenge says NOTHING about what is behind it** — a 403 once masked a 404 on a Mongolian host, and three dated readings of *"the challenge holds"* could never become a sentence about the board. So the 2026-08-31 finding (every path 301 to one CV-builder page, recorded in `shared/boards/README.md`) stays dated 2026-08-31, and what is measured today is a limit on the ROUTE · 2026-10-13 -->

<!-- witness: none found · and it cannot be otherwise by this route: the French host returns no body of its own, and the destination refused all three retrievals. The only objects measured are two rules files, four guard verdicts and three refusals · 2026-10-13 -->

## Measured 2026-10-13 — the host asked is not the host that answers

```
www.monster.fr/robots.txt    403   774 o   final_url https://www.monster.com/fr/
                                           CloudFront, LambdaGeneratedResponse, pop ZRH55-P2
                                           -> 403 sur les REGLES = ABSENCE de regles (13.09, #283)
                                              certain False, et RIEN n'y ferme ce board

www.monster.com/robots.txt   200  1 804 o  md5 092e113a0d64, as Claude-User
  un seul groupe                 *         57 Disallow, claude-user n'est PAS nomme
  aucun Disallow: / nu                     donc aucune fermeture en gros
garde EXECUTEE sur la DESTINATION, jeton claude-user :
  /fr/                        allowed=True    rule (aucune)   <- REGLES OUVERTES
  /                           allowed=True    rule (aucune)
  /jobs                       allowed=True    rule (aucune)
  /sitemap.xml                allowed=True    rule (aucune)   <- non recupere

www.monster.com/fr/          403   774 o   TROIS fois, md5 DIFFERENT chaque fois :
                                           9aeaf086a1db / 40fbad4aa880 / c8db33d9fb43
                                           -> l'empreinte BOUGE : la borne 0 ne se tranche
                                              PAS par comparaison d'empreintes (§3 bis)
  corps garde (--allow-refusal)            geo.captcha-delivery.com, « Please enable JS »,
                                           charge dd avec cid/hsh par requete
                                           -> DEFI DATADOME, borne 2, TOUTES LES VOIES
```

**Pourquoi ce n'est pas le renversement du 07.09.2026.** Cette décision ouvre la voie navigateur quand *les règles nous ouvrent un chemin et que l'infrastructure refuse ce même chemin* — et les règles nous l'ouvrent bien ici. Mais elle tient quatre bornes, et la **borne 2** en est une : on ne demande jamais à l'utilisateur du plugin de déjouer un contrôle antirobot. Le refus est donc honoré par toutes les voies, et la borne 0 — « ce 403 vise-t-il le client ou tout le monde ? » — n'avait même pas besoin d'être tranchée, ce qui est heureux puisque l'empreinte mouvante l'en empêche.

**Pourquoi aucune issue `adapter` n'accompagne cette fiche.** Tant que le défi tient, il n'y a rien à construire et le ticket porterait un « Done when » que personne ne peut satisfaire. Le jour où la destination répond, la mesure se refait et l'issue devient possible.

**Ce que cette fiche ne dit pas.** Ni que le board américain soit fermé — ses règles nous ouvrent `/jobs/search?q=`, et c'est une autre instance, hors de ce pays — ni que la page de CV du 31.08 ait disparu, ce qu'un défi ne peut pas établir, ni que ce board soit « fermé » au sens où ce verdict appartiendrait au propriétaire (§2 sexies). Et le board américain reste ce que `shared/boards/README.md` en dit : il accepte une localisation française et répond par le Mississippi.
