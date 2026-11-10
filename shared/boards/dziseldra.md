# Board — DziSeldra (`dziseldra.com`, Bhutan): a community classifieds platform whose vacancies ARE served to the declared client, `dziseldra.py` SHIPPED on 2026-11-10 — the route `/jobs` calls returns the records (`/api/getjobs/`, a BARE LIST of 16 a page, `?page=N` honoured, page 2 disjoint from page 1), the advertisement address is `/seldra/<id>` ESTABLISHED by retrieving it, and ONE flat schema is shared across cars, property and vacancies — so four column names LIE and `likers` serves a real person's name, mail, mobile, address and api_token

<!-- verified: 2026-11-10 -->

<!-- hosts: dziseldra.com -->
<!-- script: dziseldra.py -->
<!-- countries: BT -->
<!-- route: http · 32 · 2026-11-10 -->
<!-- content: measured · **the route the September card named as "the adapter's first line" DOES serve the client: `/jobs` (200, 116 842 B — it was 128 440 B on 2026-09-17) calls `axios.get('/api/getjobs/')`, which returns a BARE LIST of 16 records, no envelope, no meta, no links, so NOTHING declares a total; `?page=2` is honoured and its 16 ids intersect page 1 in ZERO. ONE enumerator, established by INCLUSION and not by two counts: the 9 `/seldra/<id>` links `/jobs` renders server-side are a STRICT SUBSET of the 16. Advertisement address `/seldra/<id>`, ESTABLISHED by retrieving 59505 (200, 93 373 B, titled with the ad's own title) and never composed from the `posturl` the Vue component names — `url` is null on 16/16. The ad page ADDS NOTHING: 8 of 8 long words of the JSON `content` appear in it, so the adapter never fetches one. Rules: `User-agent: *` and ONE EMPTY `Disallow:`, 24 B, md5 b6216d61c03e6ce0c9aea6ca7808f7ca — it refuses nothing, and `group_for` returns the empty string INSIDE the disallow list, so `if disallows:` is TRUTHY and would conclude the host refuses something; no Crawl-delay, no Sitemap, no Allow, 14 exact paths all `allowed=True certain=True regle=None`. Bounded to the vacancy nature, and the discriminant was a page of ANOTHER nature: `/cars` calls NO api route at all (zero call verbs, zero api-ish paths, three motifs of different shapes) and renders its 16 listings as `/seldra/<id>` links — a POSITIVE finding, not a silent zero; `category_id` is CONSTANT on 16/16 and reads 2 on the ad page** · 2026-11-10 -->
<!-- witness: none — this route declares no total (bare list, no meta, no links), so the walk names its own end: cut by the transport, capped, or ended of itself, and the board size is only claimed in the third case · 2026-11-10 -->
<!-- content: measured · **`/jobs` (200, 128 440 B, md5 04c83742bd0a / 6966d12da983 — a rendered element moves; the host answers slowly, minutes for a read) is a community app's front — a navigation (Job Vacancies, Scholarships, Training, Tenders, Announcements, Properties, Cars, Companies) and one `/jobs` link, no card, no count, no JobPosting in the markup; `_robots.allowed('dziseldra.com','/jobs')` → open, certain; whether the route the page calls serves the client is the adapter's first line** · 2026-09-17 -->
<!-- witness: none — the page is client-rendered · 2026-09-17 -->


## 2026-11-10 — la route sert bien le client, et quatre noms de colonnes mentent

**L'adaptateur est livré (#682).** La question que la fiche de septembre laissait
ouverte — « whether the route the page calls serves the client is the adapter's
first line » — est tranchée : **elle sert**. `/jobs` appelle
`axios.get('/api/getjobs/')`, et cette route rend **une liste NUE** de 16
enregistrements — aucune enveloppe, aucun `meta`, aucun `links`, donc **rien ne
déclare de total**.

```
/jobs                 200   116 842 o   (128 440 o le 2026-09-17 : le corps a change)
/api/getjobs/?page=1  200    53 095 o   liste NUE de 16
/api/getjobs/?page=2  200               16 ids, intersection ZERO avec la page 1
/seldra/59505         200    93 373 o   titre = celui de l annonce
/cars                 200   128 492 o   AUCUN appel /api, 16 liens /seldra/<id> rendus
```

**UN seul énumérateur, établi par INCLUSION et non par deux comptes.** Les 9
liens `/seldra/<id>` que `/jobs` rend côté serveur sont un **sous-ensemble
STRICT** des 16 de l'API : `page − api` est vide. *Deux cardinaux ne l'auraient
pas dit — 9 et 16 sont compatibles avec deux ensembles qui se coupent seulement,
ce qui est le cas de `jobsdz` la veille, où 1 571 adresses de sitemap et
2 551–2 560 enregistrements ne se contenaient ni l'un ni l'autre.*

**La portée de la route est tranchée par une page d'une AUTRE nature, et par un
POSITIF.** `/cars` n'appelle **aucune** route `/api/` — zéro verbe d'appel, zéro
chemin api-ish, par trois motifs de formes différentes — et porte ses 16
annonces en liens `/seldra/<id>` rendus côté serveur. Ce n'est donc pas un zéro
muet : les liens sont là. Et `category_id` est CONSTANT sur 16/16 et vaut `2` sur
la page d'annonce.

**L'adresse d'annonce est ÉTABLIE par récupération, jamais composée.** `url` est
`null` sur 16/16, le composant Vue nomme `posturl: '…/seldra'`, et c'est la
lecture de `/seldra/59505` qui tranche. **Et la page d'annonce n'ajoute RIEN** :
8 des 8 mots longs du `content` du JSON y figurent, donc l'adaptateur n'en
récupère aucune — ce qui est mesuré et non supposé, sur un hôte qui répond en
60 à 108 s.

**QUATRE NOMS DE COLONNES MENTENT, et un adaptateur bâti sur la correspondance
des noms émettrait des vides en jetant les vraies dates.** Un seul schéma plat
est partagé par les voitures, l'immobilier, les services et les vacances.

| colonne | ce que son nom dit | ce qu'elle PORTE, sur 16 |
| :-- | :-- | :-- |
| `vacancy_salary` | un salaire | rempli **1/16** |
| `vacancy_job_type` | un type de poste | rempli **1/16** |
| `tender_opening_date` | un appel d'offres | **16/16, 14 valeurs distinctes** — de vraies dates |
| `car_manufacturer` | un constructeur | l'entier `1` sur **16/16**, donc CONSTANT |
| `dzongkhag` | le district, que cette fiche promettait | l'entier `1` sur **16/16**, CONSTANT |

*Un plancher positif seul appelle `car_manufacturer` et `dzongkhag` RÉELS : ce
qui les démasque est le compte des valeurs DISTINCTES à côté du taux de
remplissage. Un nom de colonne se lit comme une nature exactement comme un
préfixe de chemin, et n'en est pas une.*

**`likers` sert les données personnelles de tiers qui ne sont ni recruteurs ni
candidats, et rien n'en sera jamais émis.** C'est la liste des personnes ayant
simplement **aimé** une annonce, 28 champs par personne dont `name`, `email`,
`mobile`, `address`, `birthday`, `gender` **et un `api_token`**. Ampleur sur
cette page : **1 personne au total sur 16 enregistrements**. Le filtre de chemin
est ici une **condition de sécurité** et non une optimisation — la leçon des
34 894 CV du board tadjik, obtenue sur une COLONNE au lieu d'un chemin.

**Le contact est dans la PROSE autant que dans les colonnes.** `content` porte un
courriel sur **10/16** et un téléphone sur **10/16**, et sur **10/16** les
chiffres de `contact_mobile` lui-même reparaissent dans `content`. Expurger les
seules colonnes aurait republié le contact qu'on venait de retirer. Exercé sur
les 32 enregistrements détenus : **29/32** portent un retrait atteignant une
personne, **25/32** par la prose, et **0/32** des descriptions émises porte
encore un courriel ou un téléphone.

**Le motif de téléphone est le STRICT, et le kyat est la raison.** Un
`[2-8]\d{6}` lâche atteint sept chiffres nus, et le ngultrum est indexé sur la
roupie : une valeur de contrat de 2 500 000 le satisfait. Sur un contingent
fabriqué où les deux motifs DOIVENT différer, le lâche prend deux spans et le
strict un ; sur le corpus réel ils coïncident — **18 spans chacun, ZÉRO pris par
le lâche seul**. *Résidu déclaré : un fixe bhoutanais de sept chiffres écrit sans
son indicatif `+975` lui échappe, et il n'en existe aucun sur ce corpus de 16 —
une lecture datée, pas une propriété.*

**La taille du board n'est pas déclarée par un champ**, donc la marche nomme sa
propre fin — coupée par le transport, plafonnée, ou terminée d'elle-même — et la
taille ne s'affirme que dans le troisième cas.

**Règles, lues ENTIÈRES avant tout bundle :** `User-agent: *` et un unique
`Disallow:` **VIDE**, 24 octets, `md5 b6216d61c03e6ce0c9aea6ca7808f7ca`. Il ne
refuse rien — et `group_for` rend la chaîne vide **À L'INTÉRIEUR** de la liste
des `Disallow`, donc `if disallows:` est **TRUTHY** et conclurait que cet hôte
refuse quelque chose. Aucun `Crawl-delay`, aucun `Sitemap:`, aucune ligne
`Allow`. Quatorze chemins exacts gardés sous le seul jeton `claude-user`, dans un
tour distinct de chaque récupération : les quatorze `allowed=True certain=True
state=read regle=None`.

**Route nommée et NON interrogée :** la page d'annonce nomme `/api/posts/`,
`/api/save_post/` et `/api/unsave_post/`. Rien n'établit qu'elles soient bornées
à une nature, et `likers` a montré ce qu'une route non bornée sert ici. *« La
garde permet » n'est pas « c'est à nous de le prendre ».*

**Found by the Bhutan search of #605 (a country never searched), measured
2026-09-17 16:57–17:31 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #605: two
searches — the public services (the Ministry's BLMIS, the Royal Civil
Service Commission's ZRS and vacancy pages) and the private portals the
engine names, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('dziseldra.com', '/jobs')   open, certain
GET https://dziseldra.com/jobs               200 ×2 (each read took minutes) — a community app's front, no card in the markup
```
