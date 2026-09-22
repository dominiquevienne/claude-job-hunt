# Board adapter — IranTalent (`www.irantalent.com`, Iran) : le board nomme LinkedInBot, TelegramBot et WhatsAppBot et **leur AUTORISE `*?*`** ; le groupe `*` — le nôtre — se le voit refuser, donc le pager n'est jamais demandé et la marche passe par les **6 726 pages de filtre** que le site publie en chemins simples dans son propre sitemap, l'union étant comparée aux «آگهی استخدام 1744 نتیجه» que la liste énonce ; `irantalent.py`

<!-- verified: 2026-09-22 -->

<!-- hosts: www.irantalent.com -->
<!-- script: irantalent.py -->
<!-- countries: IR -->
<!-- content: measured · **2026-09-22 08:09–08:20 UTC, le client déclaré, la garde sur le chemin exact. Règles : trois agents nommés (LinkedInBot, TelegramBot, WhatsAppBot) sont AUTORISÉS `*?*` ; le groupe `*`, qui est le nôtre, porte `Disallow: *?*`, `*utm_*`, `/jobs-search/`, `/jobs-search*`, `/*result`, `/*?keyword=`, `/*job-fair`, `/admin-panel/` — **être nommé ailleurs ne change rien : notre groupe est `*`, et aucune chaîne de requête n'est jamais envoyée**. `/jobs` 200 (929 874 B) énonce **«آگهی استخدام 1744 نتیجه»** (1 745 une heure plus tard : liste vivante) et rend 32 liens d'annonce ; **aucun lien de pager dans le HTML** (front Angular), et `/jobs/page/2` comme `/jobs/2` répondent une page sans annonce : le reste est derrière la requête refusée. Le sitemap du site (`/sitemap.xml`) déclare `fa|en/sitemap.xml` (pages), `company/sitemap.xml` et **`fa/job-filter/sitemap.xml` — 6 726 pages de filtre, toutes en chemins simples sous `/jobs/`** (banking-investment-jobs, agriculture-…-jobs), chacune rendant ses propres annonces (22 et 4 sur les deux lues). `irantalent.py jobs --filters 6` en direct : **90 émis** (32 de la liste + le reste des six filtres). L'annonce (`/job/<slug>/<id>`, 397 901 B) porte un `JobPosting` — titre, `identifier.value`, `datePosted`, `employmentType`, `hiringOrganization.name` (+ logo, `sameAs`), `jobLocation.address` (région, pays — **et une rue et un code postal, retenus**), `baseSalary` — **avec `description: null`** ; un id absent → 404 (exit 3)** · 2026-09-22 -->
<!-- witness: le compte que la liste énonce elle-même, «آگهی استخدام 1744 نتیجه», lu dans le TEXTE de la page (les deux mots vivent dans deux balises différentes, une recherche sur le HTML brut ne trouve rien) ; une marche bornée par `--filters` le DIT et n'est PAS comparée à ce compte · 2026-09-22 -->
<!-- route: http · 1744 · 2026-09-22 -->

```
irantalent.py jobs [--filters N | --all-filters]   # la liste, puis les pages de filtre du sitemap du site
irantalent.py ad --url https://www.irantalent.com/job/<slug>/<id>
```

**Être nommé ailleurs n'est pas être autorisé.** Trois robots de réseaux
sociaux ont leur propre groupe, qui leur ouvre les chaînes de requête. Le
nôtre est `*`, et il les refuse : la route passe donc par ce que le site
publie sans requête — ses pages de filtre — et non par le pager, qui serait
plus commode. C'est la même conduite que sur `jobvision.ir` (refus écrit
`*?*`) et l'inverse de `jobinja.ir` (directive vide : requête permise) :
**trois boards du même pays, trois règles différentes, trois routes**.

**`description: null` n'est pas une annonce sans texte.** Le JSON-LD porte
ce `null` ; le texte vit dans l'état Angular transféré, sous
`role_description` (HTML échappé). Émettre `null` aurait dit « cette annonce
n'a pas de description » là où la mesure disait « ce champ-là est vide » —
deux affirmations différentes, dont une fausse.

**Retenu :** la rue et le code postal, le logo et le site de l'employeur, la
route de candidature ; e-mails et téléphones de tous les textes (chiffres
persans compris) ; `contacts_withheld` sur chaque ligne. **La clé est l'id
que le site met au bout de son adresse**, jamais le slug (dont le repli ASCII
est vide et collisionne — 50 097 sur 56 095 mesurés sur Jobvision la même
semaine).

**Garde** `ABoardNamedForOthersAndRefusedForUsWhoseTextLivesInATransferredState`
dans `tests/test_core.py` — dans les deux sens (requête jamais envoyée ni
construite, compte lu dans le texte et non dans le balisage, marche bornée
dite et NON comparée, marche complète comparée et `short` → 6, id répété une
fois, clé jamais repliée depuis le slug, texte pris dans l'état transféré,
rue et code postal retenus, liste sans annonce nommée comme défaut de
lecture, 404 → 3). Banc de mutations 2026-09-22 : **11 mutations, 11
rouges** — dont une restée verte au premier tour : « liste sans annonce »
sortait bien en 6, mais par la branche suivante ; l'assertion nomme
désormais la branche et le compte de requêtes.

**Found by the Iran search of #600 (a country never searched), measured
2026-09-17 09:25–09:26 UTC by the declared client, the guard on the exact
path first, `bin/fetch-body.py`, two reads of the root.** The host was named
by two independent lists (a technology magazine's ranking and a training
centre's list, both found by the search written on #600) and by the search
engine's own result for «سایت کاریابی استخدام ایران». *A measurement, not
an adapter: the adapter is its own `adapter` issue, opened with this card.*

## What was read

```
_robots.allowed('www.irantalent.com', '/')     open, certain
GET https://www.irantalent.com/                 200 twice — see the content line for sizes and fingerprints
```

no count stated on the root. Nothing past the root was read: the list route, the pager,
the ad page and what it carries (a JobPosting or the site's own markup) are
the first line of the adapter, as every `adapter` issue of #291 says.

## What this card does not say

Nothing about the board's markup, its ids or its contacts — not read.
Nothing about the operator's intention beyond the rules file, which refuses
nothing on `/`. *A host served today is a host served today.*
