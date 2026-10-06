# Board measurement — Spain's staffing networks (Adecco · Randstad · Eurofirms · Nortempo): the country page's warning about `randstad.es` is **confirmed mechanically and its symmetric case is refuted** — Randstad Spain IS a distinct site the Swiss adapter cannot reach, while `adecco.es` is NOT a site at all but a locale path of the global `.com`, byte-identical on `/` and on `/robots.txt`

<!-- verified: 2026-10-05 -->

<!-- hosts: www.randstad.es, www.adecco.es, www.adecco.com, www.eurofirms.es, www.nortempo.com, nortempo.com, empleo.nortempo.com -->
<!-- script: none -->
<!-- countries: ES -->
<!-- host-forms-basis: seven host forms read and FOUR distinct rule states, one per agency — `www.randstad.es` read, 1 131 B, md5 dc2f00da97fb, `certain: True`, 23 `Disallow` to `*` plus thirteen named-bot groups of which the last is `User-agent: ClaudeBot` with `Disallow: /`, so `claude-user` falls under `*` and `identity()` returns «`claude-user` may fetch this path (`claudebot` may not)» — the 2026-09-07 decision doing its work; `www.adecco.es` **`unrecognised`** because `/robots.txt` answers 200 with 305 111 B whose md5 941cb6ab2055 is IDENTICAL to the home page's, `final_url` being `https://www.adecco.com/es-es` — an absence of rules, open, `certain: False`; `www.eurofirms.es` **`no-rules-tls`**, `certain: False`, the transport then naming the cause exactly — `SSL: CERTIFICATE_VERIFY_FAILED, certificate has expired` — and its apex `eurofirms.es` has NO A record on either public resolver; `www.nortempo.com` read, 116 B, WordPress's stock file, answering from the apex `nortempo.com`, while the offers host `empleo.nortempo.com` serves 67 B whose `Disallow:` is EMPTY — nothing closed, the third instance of that form in this pass after `inaem.aragon.es` at 70 B and `employtt.gov.tt` at 26 B · 2026-10-05 -->
<!-- content: measured · **500 offers in one sitemap child of 13, four agencies, four rule states, and the country page's claim tested in BOTH directions — one half confirmed, the other half refuted.** THE PAGE WARNED: «`randstad.es` est un site distinct de `randstad.ch` : l'adaptateur suisse ne s'y applique pas tel quel». **Confirmed MECHANICALLY rather than by inspection: `randstad.py` hard-codes `BASE = "https://www.randstad.ch"` with no host and no country option, and even its failure string says «could not reach www.randstad.ch» — so pointing it at Spain is not a parameter but a rewrite**, and the URL shapes differ too (`/candidatos/ofertas-empleo/oferta/<slug>-<id>/` against the Swiss `/jobs/<slug>_<uuid>/`, so `CARD` would not match either). **AND THE SYMMETRIC CASE THE PAGE DID NOT ANTICIPATE IS THE OPPOSITE: `adecco.es` is NOT a distinct site.** `/robots.txt` and `/` both answer 200 with **305 111 bytes and the SAME md5 941cb6ab2055**, and `final_url` is `https://www.adecco.com/es-es` — so Adecco Spain is a locale PATH of the global `.com`, its rules file serves the home page, and the guard reads that as `unrecognised`: an absence of rules, open, `certain: False`, a routing accident indistinguishable from a policy. ***The tell was the byte count, and it only worked because `verdict()` had recorded 305 111 B on the rules file BEFORE the home page was ever fetched*** — the second time in this pass that a recorded size caught a catch-all serving the wrong body under 200, the first being an SPA shell under a `.js` URL. RANDSTAD NAMES A CLAUDE TOKEN AND LEAVES THE DOOR OPEN: its 1 131 B file closes `*` on 23 facet and filter paths (`/*/q-*`, `/*/os-*`, `/busqueda/*`, `/search/`, `/?s=`, `/wp-admin/`, six New Relic `*/aggregate` endpoints, and `/candidatos/ofertas-empleo/*/*/*/*/` — four or more filters, which its own comment says) and then names thirteen bots, the last being `ClaudeBot` with `Disallow: /`. **This is the second Spanish host of this pass to name a token of this project — the other named five including `claude-user` and is closed by borne 1 — and this one names only `claudebot`, so the 2026-09-07 decision applies and `identity()` says so in words.** Guard exercised in both directions: `/` and `/candidatos/ofertas-empleo/` permitted under `*`, the four-facet path refused by its own rule under `claude-user`. **AND MEASURING THAT REFUSAL FOUND A DEFECT IN OUR OWN GUARD, OPENED AS ITS OWN ISSUE: with the default agent set, a path refused under BOTH tokens is attributed to the `claudebot` group with `rule: '/'` and `kind: 'host-closed'`** — because `_token_agents()` falls back to `FETCH_TOKENS`, whose first element is `claudebot`, while `PREFERRED_TOKENS` puts `claude-user` first. *Two tuples, the same two tokens, the opposite order, and the fallback uses the one that names us. The verdict is right and the attribution is false in the direction that produces a false closure: a session reading `host-closed` and «a refusal that names this project» on a facet path would write «randstad.es closes everything to us», which `/` and the listing path both refute.* **A SEVENTH WAY A DECLARED SITEMAP FAILS TO BE A WITNESS, AND THE FIRST WHERE THE INDEX LIES WHILE ITS CHILDREN TELL THE TRUTH.** `offers_sitemap.xml` declares **13 children with ONE distinct `lastmod`: `2026-10-05T21:58:20+00:00`, equal TO THE SECOND to the `fetched_at` of my own request.** Child 1 then carries **500 `<loc>`, 500 distinct, and FOUR distinct `lastmod`** spanning 2026-10-02 → 2026-10-05, **none of them equal to my request second**. *So dating quality is not uniform within one sitemap tree, and the half that lies is the INDEX — the half you consult first. An incremental walker reading the index would re-fetch all thirteen children on every pass while believing it was saving work, and nothing in its output would say so.* **And the «offers» sitemap mixes THREE populations**: of child 1's 500, `/candidatos/ofertas-empleo` holds 470, `/unete-al-equipo/ofertas-randstad` 17 — **Randstad's own internal staff jobs** — and `/fundacion-randstad/empleo-discapacidad` 13, its disability-employment foundation. *Three different objects under one enumerator; never aggregate a sitemap by wildcard.* **A NATURAL MOJIBAKE POSITIVE, IN A HOST'S OWN RULES FILE.** `www.randstad.es` writes `# Bloqueo de URLs con 4 o mÃ¡s filtros` — `más` encoded as utf-8, read back as latin-1, re-encoded — and the detector returns part **1.000 on 1 pair over 1 possible lead**. *The denominator is ONE, so this is a detection and not a statistical validation, and it is said that way. What it is worth: every previous positive for this detector was FABRICATED by re-decoding a corpus, and this one comes from the world — which is the «le cas négatif se prend dans un corpus RÉEL» rule satisfied on the positive side for the first time.* THE OFFERS ARE ON THE PORTAL'S OWN HOST FOR EXACTLY ONE OF THE FOUR: Randstad serves them at `/candidatos/ofertas-empleo/`; **Adecco's are at `/es-es/ofertas-trabajo` on ANOTHER registrable domain** (`www.adecco.com`, with `__NEXT_DATA__` present on the root and a separate blog on `adeccorientaempleo.com`); **Nortempo's are on a THIRD host, `empleo.nortempo.com/search_offers/0/`** (found by the link text «Encuentra empleo»; its identity front is Azure AD B2C on `nortempob2cpro.b2clogin.com`, and the portal itself is WordPress with 139 `wp-` references and one JSON-LD block); and Eurofirms serves nothing today. ***So the split this pass keeps meeting in the Spanish public sector — portal on one host, offers on another — holds in the PRIVATE sector too, three of the four. It is not an administrative peculiarity.*** WHAT IS NOT ESTABLISHED, AND IT IS MOST OF THE WORK: **no advert was read on any of the four, and no count is claimed.** Randstad's board SIZE is not established either — 500 in child 1 and 13 children declared puts it near 6 500, but the last child's size is unknown and no total was announced on anything read, so **the product of a page size and a page count is not a measurement and is not published as one**. Eurofirms is not measured at all beyond its expired certificate and its unresolvable apex, which under #283 is an absence of rules and at the transport an INDETERMINATE — a measurement to retake, not a verdict, and an expired certificate is precisely the kind of cause that gets fixed. METHOD: the guard was taken on all seven host forms and on each exact path in turns distinct from the retrievals and exercised in both directions; DNS resolved through two public resolvers for every host, which is what established that `eurofirms.es` has no A record rather than that one resolver was cold; `/robots.txt` and `/` compared on Adecco by SIZE FIRST and md5 second, the size having been recorded by the guard beforehand; readability checked before every conclusion of absence; none of the seven hosts writes a `Crawl-delay`, so the 2 s of our own pace apply throughout · 2026-10-05 -->

<!-- witness: partial — 500 adverts are enumerated in ONE of 13 declared sitemap children on `www.randstad.es` and every `<loc>` is distinct, but **no total is announced anywhere that was read**, so the board's size is NOT established and 500 × 13 is explicitly NOT published as a count; the other three agencies produced no advert at all — Adecco's and Nortempo's entry points are identified and not enumerated, and Eurofirms could not be reached · 2026-10-05 -->

## Measured 2026-10-05 — four agencies, four rule states, and the page's claim tested both ways

```
CE QUE LA PAGE PAYS AFFIRMAIT, ET CE QUE LA MESURE EN FAIT

« randstad.es est un site distinct de randstad.ch : l'adaptateur suisse
  ne s'y applique pas tel quel »

  CONFIRME, et MECANIQUEMENT plutot que par inspection :
    randstad.py       BASE = "https://www.randstad.ch"    code en dur
                      aucune option d'hote, aucune option de pays
                      son message d'echec dit lui aussi « www.randstad.ch »
    la forme d'URL    ES  /candidatos/ofertas-empleo/oferta/<slug>-<id>/
                      CH  /jobs/<slug>_<uuid>/
                      donc CARD ne matcherait pas non plus
  -> pointer l'adaptateur suisse vers l'Espagne n'est pas un parametre,
     c'est une reecriture

ET LE CAS SYMETRIQUE, QUE LA PAGE N'AVAIT PAS PREVU : adecco.es n'est
PAS un site distinct.

  www.adecco.es/robots.txt   200   305 111 o   md5 941cb6ab2055
  www.adecco.es/             200   305 111 o   md5 941cb6ab2055   <- IDENTIQUE
  final_url                  https://www.adecco.com/es-es

  /robots.txt sert la PAGE D'ACCUEIL. La garde lit `unrecognised` :
  absence de regles, ouvert, certain FALSE — un accident de routage
  indiscernable d'une politique.

  L'INDICE ETAIT LE COMPTE D'OCTETS, et il n'a servi que parce que
  verdict() avait enregistre 305 111 o SUR LE FICHIER DE REGLES avant
  que la page d'accueil ne soit recuperee. Deuxieme fois dans cette
  passe qu'une taille notee attrape un catch-all servant le mauvais
  corps sous 200.
```

```
QUATRE AGENCES, QUATRE ETATS DE REGLES

www.randstad.es        read    1 131 o  md5 dc2f00da97fb  certain TRUE
  groupe *                     23 Disallow : facettes /*/q-* /*/os-* /*/ct-* ...
                               /busqueda/* /search/ /?s= /wp-admin/ /wiki/
                               six points New Relic */aggregate
                               /candidatos/ofertas-empleo/*/*/*/*/   <- « 4 filtres »
  treize groupes de bots nommes, le DERNIER etant
  User-agent: ClaudeBot        Disallow: /
  -> `claude-user` tombe sous * et peut lire. identity() le DIT :
     « claude-user may fetch this path (claudebot may not) »
     (decision du proprietaire du 07.09.2026)
  Sitemap:  /sitemap.xml   ET   /offers_sitemap.xml   <- un index d'OFFRES declare

www.adecco.es          unrecognised   305 111 o   certain FALSE
  /robots.txt sert la page d'accueil ; repond depuis www.adecco.com

www.eurofirms.es       no-rules-tls   certain FALSE
  et le transport NOMME la cause :
    SSL: CERTIFICATE_VERIFY_FAILED — certificate has EXPIRED
  et l'apex eurofirms.es n'a AUCUN enregistrement A, sur les DEUX resolveurs

www.nortempo.com       read      116 o   certain TRUE   repond depuis nortempo.com
  socle WordPress : Disallow /wp-admin/ + Allow /wp-admin/admin-ajax.php
  Sitemap: https://nortempo.com/sitemap_index.xml
empleo.nortempo.com    read       67 o   certain TRUE
  User-agent: *  /  Disallow:  VIDE   -> rien n'est ferme
  troisieme instance de cette forme dans la passe (inaem 70 o, employtt 26 o)
```

```
L'INDEX MENT, SES ENFANTS DISENT VRAI — 7e forme d'echec d'un sitemap

offers_sitemap.xml      2 367 o   13 <loc>, 13 <lastmod>
  valeurs DISTINCTES de lastmod : UNE
    2026-10-05T21:58:20+00:00
  l'heure de MA requete (provenance) : 2026-10-05T21:58:20Z
  -> identiques A LA SECONDE : le champ n'est pas une date de contenu,
     c'est l'horloge du rendu

candidate-offers_sitemap_1.xml   111 499 o   500 <loc>, 500 DISTINCTS
  valeurs distinctes de lastmod : QUATRE,  2026-10-02 -> 2026-10-05
  combien egalent la seconde de ma requete : ZERO
  -> la datation est VRAIE au niveau de l'annonce

  Donc la qualite de datation n'est pas uniforme DANS UN MEME ARBRE, et
  la moitie qui mente est l'INDEX — celle qu'on consulte en premier.
  Un marcheur incremental qui lit l'index re-recupere les treize enfants
  a chaque passe en croyant economiser, et rien dans sa sortie ne le dit.

ET L'ENUMERATEUR « DES OFFRES » MELE TROIS POPULATIONS
  sur les 500 de l'enfant 1
    /candidatos/ofertas-empleo             470   les annonces clients
    /unete-al-equipo/ofertas-randstad       17   les postes de Randstad ELLE-MEME
    /fundacion-randstad/empleo-discapacidad 13   sa fondation
  trois objets sous un seul enumerateur ; on n'agrege jamais par joker
```

```
UN POSITIF NATUREL POUR LE DETECTEUR DE MOJIBAKE, dans le fichier de
regles de l'hote lui-meme

www.randstad.es/robots.txt, ligne 10, telle que l'HOTE l'a ecrite :
  # Bloqueo de URLs con 4 o mÃ¡s filtros
  « más » encode en utf-8, relu en latin-1, re-encode

  part = 1 paire / 1 tete possible = 1.000  -> MOJIBAKE

  LE DENOMINATEUR EST UN : c'est une detection, pas une validation
  statistique, et c'est dit ainsi. Ce qu'elle vaut : tous les positifs
  precedents de ce detecteur etaient FABRIQUES en re-decodant un corpus.
  Celui-ci vient du monde — la regle « le cas negatif se prend dans un
  corpus REEL » satisfaite du cote POSITIF pour la premiere fois.
```

```
OU VIVENT LES OFFRES : sur l'hote du portail pour UNE des quatre

randstad    www.randstad.es/candidatos/ofertas-empleo/        le MEME hote
adecco      www.adecco.com/es-es/ofertas-trabajo             un AUTRE domaine
                                                             enregistrable
                                                             (__NEXT_DATA__ present)
nortempo    empleo.nortempo.com/search_offers/0/             un TROISIEME hote
                                                             (identite : Azure AD B2C
                                                              nortempob2cpro.b2clogin.com)
eurofirms   —                                                 rien ne repond aujourd'hui

  Donc la separation que cette passe rencontre sans arret dans le secteur
  PUBLIC espagnol — portail sur un hote, offres sur un autre — tient aussi
  dans le secteur PRIVE, trois fois sur quatre. Ce n'est pas une
  particularite administrative.
```

## What this card does not say

**No advert was read on any of the four, and no count is claimed.** Randstad's
board size is not established: 500 adverts sit in one of thirteen declared
children, which puts it near six thousand five hundred — **and the product of a
page size by a page count is not a measurement, so it is not published as one.**
The last child's size is unknown and nothing read announced a total.

Eurofirms is not measured beyond its expired certificate and its unresolvable
apex. Under #283 an unreadable rules file is an absence of rules — open,
`certain: False` — and at the transport this is an INDETERMINATE: a measurement
to retake rather than a verdict on the board (§2 sexies), and an expired
certificate is precisely the kind of cause that gets fixed.

Adecco's and Nortempo's entry points are identified and not enumerated. The
Azure AD B2C front on Nortempo was named by the page and not followed: it is an
identity provider, and this project creates no accounts.
