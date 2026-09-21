# Board measurement — the Iranian Ministry of Labour's job search (`shoghl.mcls.gov.ir`, «سامانه جستجوی شغل», Iran): the public employment service — the name resolves on two public resolvers and the connection times out twice on 2026-09-17; its predecessor `karyabi.mcls.gov.ir` no longer resolves (NXDOMAIN on both); INDÉTERMINÉ, a control decides

<!-- verified: 2026-09-21 -->

<!-- hosts: shoghl.mcls.gov.ir, karyabi.mcls.gov.ir -->
<!-- script: none -->
<!-- countries: IR -->
<!-- content: indeterminate · **`shoghl.mcls.gov.ir` — the Ministry of Cooperatives, Labour and Social Welfare's «سامانه جستجوی شغل» (job search system, named by the Ministry's own news pages and by three third-party guides found by the search of #600) — resolves on 1.1.1.1 and 8.8.8.8 (NOERROR) and the connection to `/` times out twice under the declared client (`URLError: timed out`, 2026-09-17 09:23–09:25 UTC); `karyabi.mcls.gov.ir` (the older «کاریابی» portal, still linked by the Ministry's pages) answers NXDOMAIN on both resolvers — a name with no delegation; no rules file could be read on either (absence of rules, `certain: False`, #283); nothing of the service was read** · 2026-09-17 -->
<!-- content: indeterminate · **CONTRÔLE DU 2026-09-21 13:53–14:05 UTC, le client déclaré, cinq tentatives sur trois adresses — rien n'aboutit, et le mutisme est plus large qu'au 17.09 : `shoghl.mcls.gov.ir` résout toujours sur 1.1.1.1 et 8.8.8.8 (mêmes deux adresses, 77.237.84.46 et 185.192.114.203), `robots.txt` expire, `/` expire deux fois, `/` en HTTP simple expire, **et l'apex `mcls.gov.ir` — le site du ministère lui-même — expire aussi**. `karyabi.mcls.gov.ir` reste NXDOMAIN sur les deux résolveurs. Aucune page n'est servie, donc aucun script de page à lire : il n'y a pas de route que la page s'appellerait à elle-même (ni bundle, ni appel de widget) — il n'y a pas de page. Ce n'est pas un refus écrit ni un défi : c'est un transport qui n'aboutit pas depuis ici, et la forme est celle des cinq hôtes muets du 18.09** · 2026-09-21 -->
<!-- witness: none — nothing was served -->
<!-- route: none · non faisable — décision du propriétaire du 18.09.2026 (un hôte muet reçoit un ticket adapter+blocked qui dit pourquoi et ce qui lèverait), contrôlé une seconde fois le 21.09 sur cinq tentatives dont l'apex, #625 · 2026-09-21 -->

**Found by the Iran search of #600 as the public employment service —
the entry a country page lists first.** Measured 2026-09-17 09:23–09:26 UTC:
the declared client's connection to `shoghl.mcls.gov.ir` times out twice
(no TCP answer within the client's limit) while the name resolves on two
public resolvers; `karyabi.mcls.gov.ir` is NXDOMAIN on both.

```
dig @1.1.1.1 shoghl.mcls.gov.ir     NOERROR          dig @8.8.8.8 shoghl.mcls.gov.ir     NOERROR
dig @1.1.1.1 karyabi.mcls.gov.ir    NXDOMAIN         dig @8.8.8.8 karyabi.mcls.gov.ir    NXDOMAIN
GET https://shoghl.mcls.gov.ir/     URLError: timed out   ×2 (09:23Z, 09:24Z)
GET https://karyabi.mcls.gov.ir/    nodename nor servname provided — no address to connect to  ×2
```

**A timeout from here is not a refusal and not a verdict** (§2 sexies): an
Iranian government host may answer from inside the country and not from
a Swiss client, or may be down; neither is established by two timeouts.
INDÉTERMINÉ — a control from a tab (the browser was not connected on the
day) and a later client reading decide; if a tab is served, the route is a
browser route and the service goes to the top of Iran's list.

## What this card does not say

Nothing about what the service publishes (the Ministry's pages say: job
offers uploaded by employment agencies and employers, résumés by job
seekers); nothing about its rules — none could be read.

## 2026-09-21 — deuxième contrôle, plus large, même silence (#625)

```
dig @1.1.1.1 / @8.8.8.8 shoghl.mcls.gov.ir   NOERROR — 77.237.84.46, 185.192.114.203 (inchangé depuis le 17.09)
dig @1.1.1.1 / @8.8.8.8 karyabi.mcls.gov.ir  NXDOMAIN ×2
GET https://shoghl.mcls.gov.ir/robots.txt    timed out          13:53:47 → 13:56:08 UTC
GET https://shoghl.mcls.gov.ir/              timed out ×2       13:56:17 → 14:01:00 UTC
GET http://shoghl.mcls.gov.ir/               timed out          14:03:31 → 14:05:52 UTC
GET https://mcls.gov.ir/   (l'apex)          timed out          14:01:09 → 14:03:31 UTC
```

**Ce que ce contrôle ajoute au précédent :** le silence ne vise pas le
sous-domaine du service, il couvre **le site du ministère lui-même**, en HTTP
comme en HTTPS. Un hôte gouvernemental iranien qui résout partout et ne
répond nulle part depuis ici se lit comme une joignabilité de réseau, pas
comme une décision de l'éditeur : **aucun verdict de fermeture n'est écrit
ici** (§2 sexies), et la ligne reste « non faisable, daté et motivé ».

**Ce qui lèverait le blocage :** une réponse — n'importe laquelle, même un
refus — à `https://shoghl.mcls.gov.ir/` depuis un client de ce dépôt, ou
l'adresse actuelle du service si un utilisateur la connaît (un commentaire
sur #625 suffit). Prochain contrôle : avec la famille des hôtes muets, pas
avant, et jamais en avance « parce qu'on est libre » — un contrôle avancé
mesure autre chose que ce qu'il devait mesurer.

**Ce que ce contrôle n'établit PAS :** qu'un navigateur depuis un autre
réseau n'y arriverait pas ; qu'il n'y a pas d'annonces derrière ; que le
service a cessé. Rien n'a été lu.
