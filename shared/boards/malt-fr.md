# Board measurement — Malt (`www.malt.fr`): the French freelance marketplace — **the rules are READ and they refuse, in writing to the `*` group, exactly the objects an adapter would need**: `Disallow: /missions`, `Disallow: /mission/` and `Disallow: /s?`, so borne 1 closes the listings and the search to every route, the browser included

<!-- verified: 2026-10-11 -->

<!-- hosts: www.malt.fr, malt.fr -->
<!-- script: none -->
<!-- countries: FR -->
<!-- route: none · refus ECRIT au groupe `*` sur les objets memes d'un adaptateur — `/missions`, `/mission/` et `/s?` rendus `allowed=False` par la garde EXECUTEE (`state: read`, `certain: True`, mesure le 2026-10-11) ; borne 1, donc ferme a toutes les voies, navigateur compris · reversible le jour ou le fichier change -->
<!-- content: measured · **THE REFUSAL IS NARROW IN FORM AND DECISIVE IN EFFECT**: 1 073 B of rules, `state: read`, `certain: True`, HTTP 200, md5 39fe55dde99edbe1ba544c4f888c7a1b, 2026-10-11T04:56:47Z, as Claude-User, read in a turn distinct from any other retrieval. There is **no `Disallow: /`** anywhere — the host refuses nothing wholesale — and `allowed(host, "/")` returns **True**, which is precisely the trap §3 bis names: *a guard taken on the root says nothing about the listing path.* **THE GUARD WAS RUN, NOT READ**, on the paths an adapter would actually use, and three of them come back refused: `/missions` → `allowed=False`, rule `/missions`; `/mission/<id>` → `allowed=False`, rule `/mission/`; `/s?q=...` → `allowed=False`, rule `/s?` (the search). The `*` group carries **41** `Disallow` lines and that is where ours lands, because **`claude-user` is not named**: the only named AI agent is `GPTBot`, given `Disallow: /`, and the owner's decision of 07.09.2026 is that a named refusal of one token does not bind another — so we are *not* refused as a class, we are refused on these paths, which is borne 1 all the same. **WHAT IS ALLOWED, AND WHY IT WAS NOT FOLLOWED**: `/sitemap.xml` is declared by the rules and returns `allowed=True`; it was **deliberately not retrieved**, because every object it could name is refused, and reading an index in order to reach refused objects honours the letter against the intention (§3 bis). `/freelance/<slug>` is also `allowed=True` and **what it serves is NOT established and was NOT probed**: on this host an allowed prefix could serve freelances' own profiles, and «a path prefix reads like a nature and it is not» has already cost 34 894 people's CVs elsewhere — so the unknown is recorded as an unknown rather than resolved by a request. **NO `Crawl-delay` APPLIES TO US**: the only one in the file is `Crawl-delay: 5` under `User-Agent: FacebookBot`, a third group; `crawl_delay_s` is `null` in our provenance, so the cadence would be ours to set — and an absent delay is no promise of absent limits. **AND THIS IS A LIMIT ON THE ROUTE, NOT A VERDICT ON THE BOARD**: §2 sexies reserves closure verdicts for the owner and names a written `Disallow` as one of the things it does *not* reverse. This card says «not by this road», dated, and nothing wider · 2026-10-11 -->

<!-- witness: none found · and it cannot be otherwise by this route: the refused paths were never retrieved, and the one allowed index was deliberately left unread, so no page exists from which a witness could come. The only objects measured are the 1 073-byte rules file and five guard verdicts · 2026-10-11 -->

## Measured 2026-10-11 — the guard was run on the paths, not on the host

```
robots.txt        1 073 o   state read, certain True, 200, md5 39fe55dde99e, as Claude-User
  groupes               3   GPTBot (Disallow: /) · * (41 Disallow) · FacebookBot (Crawl-delay: 5)
  notre groupe          *   claude-user n'est PAS nomme -> decision du 07.09.2026
  Crawl-delay pour nous AUCUN (crawl_delay_s null) — l'allure serait la notre
  sitemap declare       https://www.malt.fr/sitemap.xml   <- permis, NON lu, expres

garde EXECUTEE, jeton claude-user, un seul jeton a la fois (§3 bis) :
  /missions                   allowed=False   rule /missions     <- borne 1
  /mission/abc-123            allowed=False   rule /mission/     <- borne 1
  /s?q=developpeur            allowed=False   rule /s?           <- la recherche
  /sitemap.xml                allowed=True    rule (aucune)      <- non recupere
  /freelance/developpeur-php  allowed=True    rule (aucune)      <- nature INCONNUE, non sonde
```

**Pourquoi aucune issue `adapter` n'accompagne cette fiche.** Une issue `adapter` existe pour qu'un utilisateur du plugin **vote** pour qu'on construise quelque chose ; tant que le refus écrit tient, il n'y a rien à construire, et ouvrir le ticket inviterait à bâtir ce qu'un `Disallow` ferme par toutes les voies. Le jour où le fichier change, la mesure se refait et l'issue devient possible — c'est pour cela que cette fiche est **datée** et non conclue.

**Ce que cette fiche ne dit pas.** Ni que ce board ne nous intéresse pas, ni qu'il est « fermé » au sens où ce verdict appartiendrait au propriétaire, ni que les annonces de Malt vivent **uniquement** sous `/missions` et `/mission/` — cela n'est pas établi. Et elle n'utilise pas « marketplace mal adapté au modèle du plugin », que la page pays portait : §2 sexies dit qu'un tel motif n'est pas une raison. La seule raison retenue est celle que l'hôte a écrite.
