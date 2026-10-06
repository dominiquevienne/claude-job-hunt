# Board measurement — Glassdoor España (`www.glassdoor.es`): **closed TWICE over, independently, and the country page named neither reason** — its own rules refuse pagination, the search path, the advert-detail forms and the API in writing, and its transport serves a Cloudflare challenge the EDITOR wrote itself («Humans only»)

<!-- verified: 2026-10-05 -->

<!-- hosts: www.glassdoor.es, glassdoor.es -->
<!-- script: none -->
<!-- countries: ES -->
<!-- route: none · the rules PERMIT `claude-user` and the transport answers 403 on the ROOT with an editor-branded Cloudflare challenge (title «Security | Glassdoor», visible text «Humans only», `window._cf_chl_opt` with a per-request token, `captcha` ×3, `cf-ray … -ZRH`), so borne 2 stops here and the browser branch the 2026-09-07 decision would otherwise open is closed for the same reason; and INDEPENDENTLY of that, the `*` group refuses in writing every paginated listing page (`/Empleos/*_P*.htm*`, `/Empleos/*_IP*.htm*`, `/Empleo/*_IP*`), the search path (`/search/` and `/Search/`), all three advert-detail forms (`/job-listing/details.htm?*`, `/job-listing/*_IE*.htm`, `/job-listing/JV.htm?*`), `/jobview/` and the API (`/api/`, `/api-web/`, `/graph`) — and it declares NO sitemap, so borne 1 closes the walk to every route even if the challenge lifted · 2026-10-05 -->
<!-- host-forms-basis: `www.glassdoor.es` and `glassdoor.es` resolve to the same pair of Cloudflare addresses on both public resolvers; the rules file is read, 4 820 B, md5 12d7961cc842, `state: read`, `certain: True`, and it names **26 agents of which 9 are AI crawlers**, in two classes the operator labels himself — «Partially Block High-Quality AI/LLM Bots» (one multi-agent group of twelve: GPTBot, Google-Extended, Amazonbot, `anthropic-ai`, GoogleOther, `Claude-Web`, `ClaudeBot`, Perplexity, Cohere, cohere-ai, Applebot-Extended, Google-CloudVertexBot) with `Disallow: /` **plus three `Allow`** (`/blog/`, `/About/`, `/empresas/`), and «Block Low-Quality AI/LLM Bots» (nine agents, bare `Disallow: /`). **THREE tokens of this project are named and `Claude-User` is NOT, so under the owner's decision of 2026-09-07 we fall under `*` and `identity()` returns «`claude-user` may fetch this path (`claudebot` may not)»** · 2026-10-05 -->
<!-- content: measured · **26 agents named in its rules file of which 9 are AI crawlers, 17 path forms guarded in both directions, a 403 of 24 836 B on the root — and the board is closed TWICE over, independently, with the country page naming NEITHER reason: it wrote «login fréquent» and «faible priorité en balayage», and neither is what stops a walk.** FIRST CLOSURE, IN WRITING, WHICH BINDS EVERY ROUTE (borne 1): the `*` group — the group that governs `claude-user` — refuses **every paginated listing page** (`/Empleos/*_P*.htm*`, `/Empleos/*_IP*.htm*`, `/Empleo/*_IP*`), **both spellings of the search path** (`/search/`, `/Search/`), **all three advert-detail forms** (`/job-listing/details.htm?*`, `/job-listing/*_IE*.htm`, `/job-listing/JV.htm?*`), the older `/jobview/`, and **the API in three forms** (`/api/`, `/api-web/`, `/graph`) — **and it declares no sitemap at all.** *What is left open is the FIRST page of a listing and nothing after it: the guard was exercised on seventeen path forms and `/Empleos/<slug>-SRCH_…htm` returns True with no rule in the way while `…_IP2.htm` returns False by `/Empleos/*_IP*.htm*`.* **So this board cannot be walked past page one by written rule, which is a closure no captcha and no login accounts for.** *Two details worth keeping: `/Empleos/Glassdoor-Empleos-E100431.htm` is refused BY NAME — the operator withdrawing its own vacancies from non-US domains, per its own comment «Blocking Glassdoor jobs for non-US domains» — and the salary pages carry a HAND-WRITTEN whitelist, `Allow: /Sueldos/*_IP2.htm*` through `_IP5`, so pages two to five of salaries are open and **page six is refused**, measured in both directions.* SECOND CLOSURE, AT THE TRANSPORT, AND IT IS THE EDITOR'S OWN PAGE: the ROOT answers **403 with 24 836 B** twice, **2 035 bytes differing** in a per-request `window._cf_chl_opt` token (`cH`), so the fingerprint MOVES — fetched twice before anything was compared, which is why that discipline exists. The page's title is **«Security | Glassdoor»**, its visible text begins **«Humans only — Glassdoor has been built on the contributions of real employees and job seekers. We use advanced security systems to keep our site safe and prevent misuse or unauthorized access»**, and it carries `captcha` ×3, `challenge` ×3, `Ray ID`, «enable JavaScript», `cf-ray: a45ffccc0ab1ff00-ZRH`, `server: cloudflare`. **This is an anti-robot control, so borne 2 forbids answering it and forbids asking a candidate to — which closes the browser branch the 2026-09-07 decision would otherwise open, for the same reason and not a different one.** *And borne 0 is answered by the page itself: this is NOT a stock vendor interstitial but copy the editor wrote — «Humans only», its own argument about real employees — so it is the editor's refusal and not an infrastructure that does not know who we are.* **THIRD INTERSTITIAL OF THIS SPAIN PASS, AND THE THREE SHARE NO VENDOR, NO STATUS AND NO PAGE:** Milanuncios served «Pardon Our Interruption» under **HTTP 200** with a stable md5; Robert Walters serves PerimeterX under **403** with a per-request `Reference ID`; Glassdoor serves a Cloudflare challenge under **403** with a per-request `_cf_chl_opt` token and the editor's own branding. *Three vendors, two statuses, three bodies — and the borne does not move.* **`route: none` is DATED and expected to be replaced**: revolico and emploi-cm were each challenged on one day and served to a tab on another. **NOTHING IS DECLARED CLOSED** — §2 sexies: an anti-robot control and a written `Disallow` are limits of ROUTE, never verdicts on a board, and the one thing this board would give that Indeed does not (employer reviews and salary bands) remains a reason to come back. AND A THIRD THING, WHICH IS ABOUT OUR OWN INSTRUMENT RATHER THAN THE HOST: **measuring this host produced the second independent instance of the guard-attribution defect, and the first quantified one — on eleven path forms, the verdict is right eleven times out of eleven and the reported `rule` is wrong eleven times out of eleven.** *By default every refusal here is attributed to the `claudebot` group with `rule: '/'` and `kind: host-closed`, while the rules that actually govern `claude-user` are eleven DIFFERENT narrow refusals under `*`. A session reading the default would write «Glassdoor nous ferme tout, et il nous nomme» — and the first page of a listing is permitted, `/empresas/` is open even to the named AI class, and salaries are open to page five.* **So the defect is not a curiosity of one host: it fires on every host that names `claudebot` with `Disallow: /`, and Glassdoor's single multi-agent group shows that class is not marginal.** *Recorded on its own issue with the measurement; the module was not touched.* WHAT IS NOT ESTABLISHED: **no advert, no count, no field shape — nothing of this board was read by any route**, and no inventory is claimed. Whether the first page of a listing would actually SERVE to the declared client is not established either, because the root refused before any listing was requested: the written pagination refusal is what makes a walk impossible, and the transport is what made even one page untested. *The country page's «login fréquent» is neither confirmed nor refuted — no login was reached, and this project creates no accounts.* METHOD: DNS resolved on both host forms through two public resolvers; the guard taken on the exact host and on seventeen path forms in turns distinct from the retrievals and exercised in BOTH directions, then re-run with `agents=('claude-user',)` to obtain the rules that actually govern us rather than the ones the default attributes; the refusal fetched TWICE on the same path before any fingerprint was compared, and the ROOT fetched because the verdict on a board is taken at the root; no `Crawl-delay` is written anywhere in the file, so our own 2 s applied · 2026-10-05 -->

<!-- witness: none — nothing of this board was read by any route, so there is no count to publish and none is claimed. The figures here are the rules file's own (4 820 B, 26 agents named, 9 of them AI crawlers), the refusal body's (24 836 B twice, 2 035 bytes moving), and seventeen guard verdicts · 2026-10-05 -->

## Measured 2026-10-05 — fermé DEUX fois, indépendamment, et la page pays ne nommait ni l'une ni l'autre

```
CE QUE LA PAGE PAYS DISAIT
  « Offres largement redondantes avec Indeed (meme groupe), mais salaires et
    avis employeur. Site public, login frequent. Faible priorite en balayage. »

CE QUI FERME REELLEMENT CE BOARD — et le login n'en fait pas partie
  1. ses propres REGLES refusent la pagination, la recherche, le detail
     d'annonce et l'API — par ECRIT, donc toutes les voies (borne 1)
  2. son TRANSPORT sert un defi Cloudflare que l'EDITEUR a redige (borne 2)
```

```
PREMIERE FERMETURE — PAR ECRIT, dans le groupe * qui nous gouverne

robots.txt   4 820 o  md5 12d7961cc842  read, certain TRUE, AUCUN sitemap declare

refuse       /Empleos/*_P*.htm*        toute page paginee d'une liste
             /Empleos/*_IP*.htm*
             /Empleo/*_IP*
             /search/   et   /Search/  les deux casses
             /job-listing/details.htm?*        les TROIS formes de detail
             /job-listing/*_IE*.htm
             /job-listing/JV.htm?*
             /jobview/                         l'ancienne vue
             /api/  /api-web/  /graph          l'API, trois formes
ouvert       /Empleos/<slug>-SRCH_....htm      la PREMIERE page, et rien apres

  -> ce board ne se MARCHE PAS au-dela de la page une, par regle ecrite.
     Aucun captcha et aucun login n'explique cette fermeture-la.

deux details que le fichier dit lui-meme
  /Empleos/Glassdoor-Empleos-E100431.htm   REFUSE PAR SON NOM
    son commentaire : « Blocking Glassdoor jobs for non-US domains »
    -> l'exploitant retire ses PROPRES offres des domaines non americains
  Allow: /Sueldos/*_IP2.htm*  ... jusqu'a _IP5     une liste blanche A LA MAIN
    donc les pages 2 a 5 des salaires sont OUVERTES
    et la page 6 est REFUSEE — eprouve dans les deux sens
```

```
ET LE FICHIER RANGE LES ROBOTS D'IA EN DEUX CLASSES QU'IL NOMME

#### Partially Block High-Quality AI/LLM Bots      un seul groupe, DOUZE agents
  GPTBot · Google-Extended · Amazonbot · anthropic-ai · GoogleOther ·
  Claude-Web · ClaudeBot · Perplexity · Cohere · cohere-ai ·
  Applebot-Extended · Google-CloudVertexBot
  Disallow: /
  Allow: /blog/    Allow: /About/    Allow: /empresas/      <- une liste blanche

#### Block Low-Quality AI/LLM Bots                 neuf agents, Disallow: / nu
  CCBot · Omgilibot · Omgili · FacebookBot · Bytespider · Diffbot ·
  Youbot · FriendlyCrawler · img2dataset

26 agents nommes en tout, dont 9 sont des robots d'IA.
TROIS jetons de ce projet sont nommes — anthropic-ai, claudebot, claude-web —
et `Claude-User` n'apparait NULLE PART.

  -> decision du proprietaire du 07.09.2026 : nous tombons sous `*`.
     identity() le dit : « claude-user may fetch this path (claudebot may not) »

  Et c'est le CONTRASTE avec InfoJobs, qui nomme aussi trois jetons — mais
  `claude-user` EN FAIT PARTIE, donc il ferme. Meme cardinal, membres
  differents, verdict oppose : aucun total ne distingue les deux.
```

```
SECONDE FERMETURE — AU TRANSPORT, ET C'EST LA PAGE DE L'EDITEUR

la RACINE, deux lectures du MEME chemin
  403   24 836 o   md5 52ec8953ee42
  403   24 836 o   md5 (autre)        2 035 octets different
  ce qui bouge : window._cf_chl_opt { cH: '<jeton PAR REQUETE>' }
  -> empreinte MOUVANTE : recuperee deux fois AVANT toute comparaison

ce que la page EST
  titre          « Security | Glassdoor »
  texte visible  « Humans only — Glassdoor has been built on the contributions
                   of real employees and job seekers. We use advanced security
                   systems to keep our site safe and prevent misuse or
                   unauthorized access. »
  captcha x3 · challenge x3 · Ray ID · « enable JavaScript »
  cf-ray a45ffccc0ab1ff00-ZRH · server cloudflare

  BORNE 0, et la page y repond elle-meme : ce n'est PAS un interstitiel
  generique de fournisseur, c'est une copie que l'EDITEUR a ecrite — « Humans
  only », son propre argument sur les vrais salaries. Donc c'est le refus de
  l'editeur et non une infrastructure qui ne sait pas qui nous sommes.

  BORNE 2 : on n'y repond pas et on ne le demande pas a un candidat — ce qui
  ferme aussi la voie navigateur que la decision du 07.09 ouvrirait, pour la
  MEME raison.
```

```
TROISIEME INTERSTITIEL DE LA PASSE, ET LES TROIS NE PARTAGENT RIEN

                 statut   empreinte            page
Milanuncios      200      STABLE               « Pardon Our Interruption »
Robert Walters   403      mouvante (UUID)      PerimeterX, « verify you are a human »
Glassdoor        403      mouvante (_cf_chl)   Cloudflare, redigee par l'EDITEUR

  Trois fournisseurs, deux statuts, trois corps — et la borne ne bouge pas.
  `route: none` est DATE et attendu comme remplacable (revolico, emploi-cm).
  RIEN n'est declare ferme (§2 sexies) : un controle antirobot et un `Disallow`
  ecrit sont des limites de ROUTE, jamais des verdicts sur un board — et ce que
  ce board donnerait et qu'Indeed ne donne pas (avis employeur, fourchettes de
  salaire) reste une raison d'y revenir.
```

```
ET UNE TROUVAILLE SUR NOTRE PROPRE INSTRUMENT, PAS SUR L'HOTE

onze formes de chemin, deux lectures de la MEME garde
  defaut                      rule = /          kind = host-closed    x11
  agents=('claude-user',)     onze regles DIFFERENTES, toutes etroites, sous *

  verdicts identiques         11 / 11      <- la garde ne laisse rien passer
  regles MAL ATTRIBUEES       11 / 11      <- et elle accuse l'hote a tort

  Une session qui lit le defaut ecrirait « Glassdoor nous ferme tout, et il nous
  nomme ». Or la premiere page d'une liste est PERMISE, /empresas/ est ouvert
  meme a la classe IA nommee, et les salaires sont ouverts jusqu'a la page 5.
  Le defaut tire sur TOUT hote qui nomme `claudebot` avec Disallow: / — et le
  groupe multi-agents de Glassdoor montre que cette classe n'est pas marginale.
  Consigne sur son issue avec la mesure ; le module n'a pas ete touche.
```

## What this card does not say

**Nothing of this board was read by any route**, so there is no advert, no count
and no field shape, and no inventory is claimed.

**Whether the first page of a listing would actually SERVE to the declared client
is not established either** — the root refused before any listing was requested.
The written pagination refusal is what makes a walk impossible; the transport is
what left even one page untested. Those are two separate findings and neither
implies the other.

**And the country page's «login fréquent» is neither confirmed nor refuted:** no
login was reached, and this project creates no accounts. What the page got wrong
is not the login — it is that it filed this board under «faible priorité» when
what actually stops it is written into its own rules.
