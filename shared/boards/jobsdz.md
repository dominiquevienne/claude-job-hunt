# Board — JobsDZ (`jobsdz.com`, Algeria): an Arabic WP Job Manager board, `jobsdz.py` SHIPPED on 2026-11-10 — the ads live at `/job/<slug>/` and `/ar/job/<slug>/` with a full `JobPosting` in their JSON-LD, the only enumerator a plain client can read is `job_listing-sitemap.xml` (1 571 ads), and the AJAX route the issue named answers with the board's OWN count (2 551–2 560) and an EMPTY `html`

<!-- verified: 2026-11-10 -->

<!-- hosts: jobsdz.com -->
<!-- script: jobsdz.py -->
<!-- countries: DZ -->
<!-- route: http · 1571 · 2026-11-10 -->
<!-- content: measured · **le 2026-11-10 l'adaptateur `jobsdz.py` est expédié&nbsp;: `job_listing-sitemap.xml` porte 1 680 `<loc>` pour 1 572 adresses distinctes, dont 1 571 annonces — 1 569 à `/job/<slug>/` et 2 à `/ar/job/<slug>/`, les deux préfixes que ce board sert — et le board compte LUI-MÊME entre 2 551 et 2 560 `job_listing` par le `max_num_pages` de sa route AJAX, lu à deux valeurs de `per_page` (256 pages à 10, 26 pages à 100), un témoin qui VARIE donc qui mesure. Les deux surfaces de liste ne servent AUCUNE annonce à un client simple, et la route AJAX que #787 nommait rend `html` vide sur trois jeux de paramètres, identique à l'octet sur deux d'entre eux** · 2026-11-10 -->
<!-- witness: le `max_num_pages` de la route AJAX du board, qui VARIE avec `per_page` donc qui mesure, intersecté à [2 551 ; 2 560] — un compte qui ne vient PAS de notre extraction · 2026-11-10 -->
<!-- content: measured · **the root redirects to `/ar/` (200, 247 279 B, md5 2042c5a57298 / f4cc269e4ac3 — a rendered element moves): WordPress 7.1.1, «JobsDZ — المنصة الرائدة للوظيف العمومي والتوظيف في الجزائر», a stat «💼 2,400+ وظيفة», sections الوظيف العمومي (public sector) and القطاع الخاص (private sector), `/ar/add-job/`, `/ar/submit-resume/`, `/job-alert`; `/ar/wadifa/` (200, 204 145 B, 12:29 UTC) is WP Job Manager's list shell — `job_listings`, `search_jobs`, `showing_jobs`, filters by category and «كل الولايات» (wilaya) — with the listings fetched by the plugin's AJAX route, no ad in the markup; no JobPosting; `_robots.allowed('jobsdz.com','/ar/wadifa/')` → open, certain** · 2026-09-20 -->
<!-- witness: the front's own «2,400+ وظيفة» (a rounded claim) · 2026-09-20 -->

## 2026-11-10 — l'adaptateur est livré, et la route que l'issue nommait n'en est pas une

**Les règles permettent l'AJAX par un `Allow:` ÉCRIT et non par un silence.** Le fichier
fait 593 o, HTTP 200, `md5 3c58e22b05f0d8fb867bb1b53b204bb2`, lu le 2026-11-10 à 11:33Z&nbsp;:
un groupe `*` dont les trois `Disallow` sont `/wp-admin/` et deux chemins WooCommerce, et
**un `Allow: /wp-admin/admin-ajax.php`** — la recommandation Rank Math. Donc le verdict sur
la route AJAX est `allowed=True`, `kind='allow'`, règle NOMMÉE. *Lire les seuls `Disallow`
aurait fermé ce board sous la borne 1, et il est ouvert&nbsp;: la direction est la
restrictive, celle que personne n'audite.* `ignored_for()` rend `[]`, `delay_for()` rend
`None` — donc la cadence de 2 s est NÔTRE — et l'unique `Sitemap:` vit sur le MÊME hôte.

| ce qui a été rejoué | ce que ça rend |
| :-- | :-- |
| `admin-ajax.php` avec les `data-*` de la coquille | 200, 741 o, `html` **vide** |
| le jeu complet du JS du greffon | 200, 741 o, `html` vide, **identique à l'octet** |
| plus `X-Requested-With` et un `Referer` de la coquille | 200, 741 o, `html` vide |
| `/ar/wadifa/` et `/job-listings/` | coquilles&nbsp;: 0 et 1 annonce dans le marquage |
| `job_listing-sitemap.xml` | 1 680 `<loc>`, 1 572 distinctes, **1 571 annonces** |
| une annonce `/job/<slug>/` | un `JobPosting` JSON-LD complet |

**Et `found_jobs` est un BOOLÉEN, donc le témoin que #787 nommait n'est pas un compte.**
Ce que la route porte est `max_num_pages`, et il est un témoin PARCE QU'IL VARIE —
256 pages à `per_page=10` donne [2 551 ; 2 560], 26 pages à 100 donne [2 501 ; 2 600],
intersection **[2 551 ; 2 560]**. Le «&nbsp;2,400+&nbsp;» du front est une revendication
arrondie et il concorde.

**1 571 contre 2 551–2 560 est un écart d'environ mille, et aucun des deux énumérateurs
n'est établi contenir l'autre**, donc l'adaptateur émet la population du SITEMAP, le dit,
et ne revendique aucune taille de board. Le sitemap porte des annonces périmées — la
dernière par ordre de sitemap est du 2025-12-25 et ne déclare aucun `validThrough`.

**TROIS CHAMPS CHANGENT DE FORME, mesurés sur le PREMIER, le MÉDIAN et le DERNIER rang du
sitemap — jamais les trois premiers, qui sont un seul genre.** `jobLocation.address` est une
CHAÎNE nue sur deux (`Alger`, `Blida`) et un `PostalAddress` sur la troisième, et un lecteur
écrit pour l'une rend `None` sur l'autre&nbsp;; `validThrough` et `employmentType` sont
présents sur deux et ABSENTS sur la troisième (11 clés contre 9)&nbsp;;
`hiringOrganization.name` est **présent et VIDE** sur la troisième, ce que `if x` ne sépare
pas d'absent. *Dénominateur 3, un jour&nbsp;: ce sont des FORMES observées, pas des
fréquences.*

**L'échappement n'est pas uniforme, donc la description est dés-échappée UNE fois et le
dit.** Une passe vide toutes les entités sur deux annonces (172 et 148 à zéro)&nbsp;; sur la
troisième il en survit UNE, `&#8217;` dans «&nbsp;Oued S’mar&nbsp;», donc cette annonce est
doublement échappée à la source. *Elle reste dés-échappée une seule fois&nbsp;: deux passes
transformeraient un `&amp;` littéral du texte d'un employeur en `&`, ce qui est une
corruption silencieuse, quand un `&#8217;` visible est honnête.* `description_entities`
porte le compte résiduel.

**CE QUI N'EST PAS PRIS, et la première raison n'est pas technique.** L'index nomme aussi
`resume-sitemap.xml`, `resume_category-sitemap.xml` et `resume_region-sitemap.xml`&nbsp;: ce
sont les **CV de candidats**. Les trois rendent `allowed=True` et aucun n'est récupéré — un
hôte qui n'interdit rien n'a pas pour autant consenti à ce qu'on prenne tout ce qu'il
expose. `/ar/submit-resume/` et `/ar/add-job/` sont déclinés au même titre. Et trois enfants
— `jobpost-sitemap1.xml`, `jobpost-sitemap2.xml`, `emlpois-hors-algerie-sitemap.xml` —
ressemblent à un deuxième et un troisième type d'annonce&nbsp;: **leur nature n'est PAS
établie, aucun membre n'a été ouvert**, donc ils sont nommés dans une note et laissés.

**SEPT MUTATIONS, SEPT ROUGES, chacun depuis sa PROPRE sonde et chacun ayant CRÉÉ son
défaut** (balayage sur une copie, jamais dans l'arbre partagé)&nbsp;: `is_urlset` désarmé
accepte un corps qui n'est pas un sitemap&nbsp;; l'enfant pris par POSITION rend
`post-sitemap1.xml`&nbsp;; la dédup retirée rend 1 677 au lieu de 1 571&nbsp;; la branche
`PostalAddress` retirée rend `location` NULLE sur la troisième annonce&nbsp;; le plancher
positif remplacé par `if x` rend «&nbsp;absent&nbsp;» là où l'objet porte une chaîne vide&nbsp;;
`TEL_RE` desserré à cinq chiffres expurge **une paie en dinars** comme un numéro — le piège
du kyat&nbsp;; et dés-échapper deux fois fait disparaître le signal qui DIT que l'hôte double
son échappement.

**DEUX DÉFAUTS TROUVÉS EN EXERÇANT ET PAS EN RELISANT.** `text_of` écrasait la chaîne vide
en `None` AVANT que le plancher positif la voie, donc la branche
«&nbsp;présent mais vide&nbsp;» était verte sur fixture et MORTE sur le corpus&nbsp;; et la
dédup d'adresse portait sur l'égalité, donc `Algiers, Algeria` et `Algeria` survivaient les
deux. Les deux sont corrigés et les deux branches tirent désormais sur le corpus.

**RÉSIDUS DÉCLARÉS&nbsp;:** la taille du board n'est pas établie (deux énumérateurs, aucun
contenant l'autre)&nbsp;; la nature des trois enfants `jobpost`/`emlpois` n'est pas
établie&nbsp;; `employmentType` vaut `['TEMPORARY']` sur les DEUX annonces qui le portent,
donc il est CONSTANT sur un dénominateur de 2 et ne discrimine rien — il ne se lit pas comme
«&nbsp;ce board est tout en intérim&nbsp;»&nbsp;; aucun contact n'a été trouvé dans les trois
descriptions décodées, dénominateur 3, donc l'expurgation est atteignable et silencieuse sur
ce corpus.

**Named in the Atlas inventory of 2026-09-04 (#147), never carded; measured
for #770 on 2026-09-20 12:28–12:29 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** *A measurement, not an
adapter.*

```
_robots.allowed('jobsdz.com', '/')   open
GET https://jobsdz.com/            200 ×2 → /ar/ — «2,400+ وظيفة»
GET https://jobsdz.com/ar/wadifa/  200 — WP Job Manager's shell, filters by wilaya
```

The adapter's first line: WP Job Manager's `admin-ajax.php?action=job_manager_get_listings` (the route the shell calls, with its own parameters — page, per_page, the wilaya filter) and its `found_jobs` total against the front's «2,400+», the ad `/ar/<post>/`.
