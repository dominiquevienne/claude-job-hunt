# Board adapter — Jobvision (`jobvision.ir`, «بزرگترین سایت کاریابی ایران», Iran): les listes vivent derrière des chaînes de requête que les règles refusent PAR ÉCRIT (`disallow: *?*`) — l'inventaire se lit donc là où le site le publie sans requête, son propre sitemap d'annonces (56 095 entrées le 2026-09-21), et chaque annonce porte un JobPosting ; `jobvision.py`, rue, code postal, logo et site de l'employeur retenus

<!-- verified: 2026-09-21 -->

<!-- hosts: jobvision.ir -->
<!-- script: jobvision.py -->
<!-- countries: IR -->
<!-- content: measured · **2026-09-21 14:12–14:16 UTC, le client déclaré, la garde sur le chemin exact. Règles : `user-agent: *` — `disallow: *?*` (TOUTE URL portant une chaîne de requête), `*utm_*`, `*/Login/*` ; `Allow: *.js`, `*.css` ; deux sitemaps déclarés. La racine (310 446 B) est une coquille Angular (`main.<hash>.js`, 554 069 B) : aucun compte dans le HTML, la description meta énonce «۴۸ هزار آگهی شغلی» (48 mille, arrondi) ; le bundle nomme les hôtes d'API (`candidateapi.`, `basedataapi.`, `web.jobvision.ir`) — **une recherche y prend ses paramètres en chaîne de requête, donc elle n'est pas utilisée**. `/sitemap.xml` (UTF-16) déclare quatre sitemaps ; **`/sitemap/jobposts.xml` (23 009 777 B, UTF-16) est l'inventaire : 56 095 `<url>`, chacune avec un `<loc>` `/jobs/<id>/<slug>` et deux `<loc>` d'image (logo d'entreprise, carte générée — jamais émis), `<lastmod>` du 2026-07-23 au 2026-09-21** ; `/sitemap.jobs.xml.gz` (34 KB) n'est PAS les annonces (5 271 pages de catégorie). `jobvision.py jobs --since 2026-09-20` en direct : **3 014 émis** sur les 56 095. L'annonce (`/jobs/1468042/…`, 169 113 B) : un `JobPosting` — titre, `hiringOrganization.name` (+ logo, `sameAs`), `jobLocation.address` (localité, région, pays — **et une rue et un code postal, retenus**), `baseSalary`, `industry`, `employmentType`, `directApply`, `datePosted`, `validThrough`, `description` ; un id absent → 404 (exit 3)** · 2026-09-21 -->
<!-- witness: aucun témoin indépendant — le sitemap est la SOURCE, donc son propre compte ne l'atteste pas («&nbsp;a sum that matches its source is not a check&nbsp;») ; les seuls chiffres extérieurs sont ceux du site : «۴۸ هزار» (arrondi, meta de la racine, 2026-09-21) et «56,781 آگهی» que sa racine imprimait le 2026-09-17 (#600). Le run imprime les trois et dit lequel est arrondi · 2026-09-21 -->
<!-- route: http · 56095 · 2026-09-21 -->

```
jobvision.py jobs [--since YYYY-MM-DD] [--limit N] [--from <sitemap enregistré>]
jobvision.py ad --url https://jobvision.ir/jobs/<id>/<slug>
```

**Aucune chaîne de requête n'est jamais envoyée** — les règles la refusent par
écrit, et l'adaptateur refuse d'en CONSTRUIRE une : `request()` sort en 7 avant
la garde si l'URL en porte une, `ad --url` sort en 2. C'est la raison pour
laquelle l'API de recherche nommée dans le bundle n'est pas utilisée, alors
qu'elle rendrait les mêmes annonces : **un refus écrit est honoré par toutes les
voies**, y compris celle qui serait plus commode.

**Ce que le compte est, et ce qu'il n'est pas.** 56 095 est le nombre d'entrées
d'annonce du sitemap — c'est la source elle-même, pas un témoin. Le site donne
deux chiffres extérieurs, tous deux à lui : «۴۸ هزار» (arrondi) et «56,781» du
17.09. Le run les imprime ensemble et le dit. `--since` et `--limit` bornent la
lecture et le disent aussi : une lecture bornée n'est pas l'inventaire.

**La clé se construit sur ce qui est ÉMIS, pas sur ce qui a été lu.** Un
employeur qui écrit un téléphone ou une adresse dans son TITRE le met dans le
slug — donc dans l'URL, dans la clé lisible et dans le titre rendu, là où
aucune expurgation de la description n'irait le chercher. Mesuré le
2026-09-21 : **0 slug sur 56 095** en porte un. Rare, donc, et pas impossible :
quand cela arrive, le slug et le titre sont épurés **et l'adresse émise est la
canonique `/jobs/<id>/x`**, que le site sert à l'identique (relue deux fois,
169 119 o, le même JobPosting) ; la ligne porte alors `url_neutralised`, parce
qu'un lien qui perd son titre en silence est un mensonge d'une autre espèce.
*(Trouvaille de `cd` du 21.09 sur un autre board, appliquée ici.)*

**Retenu :** la rue et le code postal de l'annonce, le logo et le site de
l'employeur, la route de candidature ; textes épurés des adresses e-mail et des
téléphones (chiffres persans compris) ; `contacts_withheld` sur chaque ligne.

**Garde** `AnInventoryReadWhereTheRulesAllowItBecauseEveryQueryStringIsRefused`
dans `tests/test_core.py` — dans les deux sens (chaîne de requête jamais
envoyée (7) ni construite (2), les `<loc>` d'image jamais pris pour des
annonces, un id répété une fois, `--since` et `--limit` dits, le sitemap nommé
comme source et non comme témoin, un sitemap sans annonce (6), les champs de
l'annonce avec rue, code postal, logo et site retenus, la description épurée,
un 404 (3), l'UTF-16 décidé sur les octets). **Banc de mutations 2026-09-21 :
11 mutations, 11 rouges — dont une écartée en route :** un filtre sur
l'extension d'image ne rougissait pas, parce que sur ce site aucune adresse
`/jobs/…` ne porte d'extension (56 095 mesurées, zéro) ; il a été RETIRÉ plutôt
que gardé — **un filtre qui ne peut pas se déclencher est une garde qui ne peut
pas rougir**, et c'est sa mutation verte qui l'a montré.

**Found by the Iran search of #600 (a country never searched), measured
2026-09-17 09:25–09:26 UTC by the declared client, the guard on the exact
path first, `bin/fetch-body.py`, two reads of the root.** The host was named
by two independent lists (a technology magazine's ranking and a training
centre's list, both found by the search written on #600) and by the search
engine's own result for «سایت کاریابی استخدام ایران». *A measurement, not
an adapter: the adapter is its own `adapter` issue, opened with this card.*

## What was read

```
_robots.allowed('jobvision.ir', '/')     open, certain
GET https://jobvision.ir/                 200 twice — see the content line for sizes and fingerprints
```

«56,781 آگهی» on the root, the site's own figure. Nothing past the root was read: the list route, the pager,
the ad page and what it carries (a JobPosting or the site's own markup) are
the first line of the adapter, as every `adapter` issue of #291 says.

## What this card does not say

Nothing about the board's markup, its ids or its contacts — not read.
Nothing about the operator's intention beyond the rules file, which refuses
nothing on `/`. *A host served today is a host served today.*
