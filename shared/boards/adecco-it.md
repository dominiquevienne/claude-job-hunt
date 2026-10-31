# Board measurement — Adecco Italy (`www.adecco.com/it-it`): the Italian sitemap EXISTS and the adapter refuses Italy, so this country is one line of a table

<!-- verified: 2026-10-31 -->

<!-- hosts: www.adecco.com -->
<!-- script: adecco.py -->
<!-- countries: IT -->
<!-- route: http · OUVERT — garde EXÉCUTÉE le 2026-10-31 sur chaque URL exacte, hôte compris, un seul jeton à la fois, dans un tour DISTINCT de la récupération&nbsp;: `state: read`, `certain: True`, groupe `*`, et la raison est explicite — **aucun `Disallow` ne vise nos chemins dans le groupe de tout le monde**, donc `crawl_delay: None` et l'allure est la NÔTRE (posée à 10 s). **ET MON CONTRÔLE POSITIF N'A RIEN TROUVÉ QUI TIRE, Y COMPRIS POUR `claudebot`&nbsp;: c'est `state` qui tranche et jamais `allowed`**, un `allowed: True` sans règle nommée se lisant exactement comme un fichier illisible. Énumérateur `https://www.adecco.com/sitemap-jobs-italy-it.xml`, **DÉCLARÉ dans `jobsindex.xml`** et non deviné. Annonces sous `/it-it/cerca-lavoro/<slug>/<id>`, **un seul** bloc `application/ld+json` SERVI, `JobPosting` rendu côté SERVEUR · 2026-10-31 -->

<!-- content: measured · **7 719 annonces déclarées** par le sitemap que l'index du site déclare lui-même, et **l'adaptateur les lit désormais** — une entrée de `BOARDS`, comme cette fiche l'annonçait, et la RÉSERVE EST LEVÉE PAR LA MESURE&nbsp;: trois annonces récupérées aux trois FORMES d'identifiant, et l'adaptateur EXÉCUTÉ contre l'hôte vivant par `search --host it --all --limit 2`. **ET TROIS CHIFFRES DE CETTE FICHE ONT BOUGÉ, DONC C'ÉTAIENT DES LECTURES DATÉES&nbsp;:** le sitemap déclare **7 719** `<loc>` contre 6 260 le 12.10 — **+1 459 en vingt-cinq jours** — l'index en déclare **60** enfants contre 59 dans la docstring, et le fichier italien y est **DÉCLARÉ** quand la fiche le donnait pour deviné depuis la forme des trois autres. **L'IDENTIFIANT A TROIS FORMES ET NON UNE&nbsp;:** UUID **5 559**, `xxxx-xxxx` **1 246**, `xxxx-xxx` **744** — donc un motif ancré sur l'UUID manquerait **2 190 sur 7 719, soit 28 %** — et la fixture norvégienne en porte une quatrième (`ts-f7697975`). Le code est immune parce qu'il clefe sur le **dernier segment de l'URL** et d'une seule source&nbsp;: **`jobId` est en MAJUSCULES quand l'URL porte le même identifiant en minuscules, et 0 des 7 719 derniers segments du sitemap portent une majuscule**, donc une clef prise sur `jobId` et comparée à l'URL ne se joindrait pas pour les 72 % en forme UUID. **ET CE QUE LES FICHES SŒURS PRÉDISAIENT EST RÉFUTÉ SUR DEUX POINTS&nbsp;: les salaires italiens sont RÉELS** — 1 979,3 / 25 000 / 27 500 EUR avec `unitText` `mensile`, `giornaliero`, `Annui` — là où FR/NO/FI portent des zéros, **et ZERO contact ne voyage dans la prose** — aucun courriel, aucun téléphone sur **7 959 caractères** de description. La sentinelle `"null"` n'apparaît que sur UNE des trois, les deux autres portant un `industryTypeTitle` réel. `clean()` et `money()` absorbent la forme italienne sans retouche&nbsp;: `"null"` → `None`, espaces de fin rognés, zéros annulés · 2026-10-31 -->

<!-- witness: trois annonces, **une par FORME d'identifiant** et jamais les trois premières — `/it-it/cerca-lavoro/30-addett-produzione-settore-metalmeccanico-cremona-cremona/1298-1421` (forme `xxxx-xxxx`, 440 415 o), `…/impiegato-a-ufficio-acquisti-villongo-bergamo/23777333-e8b2-46bc-ae49-43471d816704` (UUID, 446 479 o) et `…/zobele-holding-s-p-a-trento-operaio-a-generico-produzione-trento-trento/1303-99` (forme `xxxx-xxx`, 443 587 o), les trois à HTTP 200, récupérées comme Claude-User à une allure posée par nous de 10 s. **Les trois rendent la MÊME structure&nbsp;: UN bloc `ld+json` SERVI et la chaîne n'apparaît qu'UNE fois** — donc le mécanisme mesuré chez Les Jeudis, où la chaîne apparaît DEUX fois pour un bloc servi, **NE SE TRANSPOSE PAS ICI**, et c'est mesuré et non supposé. Champs&nbsp;: `jobId`, `datePosted`, `validThrough`, `employmentType`, `industryTypeTitle`, `isRemote`, `country`, `hiringOrganization.name` = `adecco` (l'agence, jamais l'employeur), `jobLocation.address` avec localité et région mais `postalCode` VIDE sur les trois, et un `baseSalary` complet. **`validThrough` et `employmentType` portent des espaces en FIN** (`"…Z "`, `"Permanent  "`) · 2026-10-31 -->
<!-- content: measured · read 2026-10-06 — `sitemap-jobs-italy-it.xml` answers 200 with 1 242 193 B and carries 6 260 `<loc>`, ALL DISTINCT and all under the single path segment `it-it`, so there is no per-language over-count; the first, median and last were opened and all three are real Italian vacancies. `adecco.py` exists and REFUSES this country before any request, so `script: none` is this country's true state and the fix is a table entry and not a rewrite · 2026-10-06 -->
<!-- witness: the board states no total of its own here; 6 260 is OUR count of distinct `<loc>` in the sitemap it publishes, and it is not a board-stated figure · 2026-10-06 -->

## Measured 2026-10-06 — 6 260 distinct adverts, and the adapter cannot address them

Opened under **#949**, tranche 3 — the Italian staffing agencies, the ATS and the
sector board. *The owner opened the campaign by tranches on 2026-10-06, verbatim
« oui, ouvre #949 par tranches, commence par l'Italie ».*

**The guard was taken on EVERY host form separately, in a turn DISTINCT from the
retrieval, because `robots.txt` binds a HOST and not a brand.** Eleven forms were
guarded across this tranche; nine answered `state: read` and two `unrecognised`,
all open, **and not one carries a `Crawl-delay`** — so the pace is ours, and an
absent delay is not an absence of rate limiting. *Retrieval through
`bin/fetch-body.py` under the declared identity, provenance written beside each
body.* No contact value is reproduced anywhere below; counts only.

**THIS CARD DECLARES `script: none` FOR A HOST THAT THREE OTHER CARDS COVER WITH A
LIVING SCRIPT, AND THAT IS NOT AN OVERSIGHT — it is measured.** `adecco.md` (FR),
`adecco-no.md` (NO) and `adecco-fi.md` (FI) all declare `www.adecco.com` and all
run `adecco.py`. **Calling `adecco.py`'s own `use_board()` refuses Italy before any
request**, in four spellings:

```
use_board('fr' | 'no' | 'fi')                 -> ACCEPTED
use_board('it') / ('IT') / ('it-it')          -> REFUSED, SystemExit 2
use_board('www.adecco.it')                    -> REFUSED, SystemExit 2
  « not a front this adapter reads — fr (France, sitemap-jobs-france-fr.xml), … »
```

*The `--host` help reads «the country's front, or its hostname», which SOUNDS like
it takes any hostname; the implementation enumerates.* **The refusal is honest and
it names what a new front needs, which is exactly what made the next measurement
cheap.**

**WHAT THE REFUSAL ASKED FOR, AND WHAT THE HOST ANSWERED.** The three known fronts
are `sitemap-jobs-<country>-<lang>.xml`. Guessed from that shape and guarded on the
exact path:

```
www.adecco.com/sitemap-jobs-italy-it.xml   200   1 242 193 B   md5 4ab9fb34611c
<loc> 6 260        distinct 6 260          no CDATA
first path segment   it-it : 6 260 of 6 260      <- one segment, so no language twin
```

**The three members opened were the FIRST, the MEDIAN and the LAST, never the first
three** — Adecco Healthcare Italia; fast-food staff at Gallarate, Varese; a waiter
at a fish restaurant in Pescara. *A count of `<loc>` names a SIZE and never a
NATURE, and the path that carries them does not say it either.*

**So Italy is a PARAMETER and not a rewrite** — one `BOARDS` entry naming the file,
the language, the ledger key and the country. *And the contrast inside this very
tranche is the point: `randstad.it` answered the same question with a **404**.
«&nbsp;It is already covered elsewhere&nbsp;» predicts nothing, and the two measured
together say opposite things.*

## CORRECTION DU 31.10.2026 — la section ci-dessous est LEVÉE sur ses trois points, et elle est gardée mot pour mot parce qu'une correction CITE ce qu'elle corrige

*Une page d'annonce A été récupérée — trois, une par forme d'identifiant — donc la forme des champs par annonce est LUE et la question du contact est TRANCHÉE&nbsp;: **zéro contact sur 7 959 caractères de prose**. Le 6 260 est devenu **7 719**, donc il était bien une lecture datée, et il reste NOTRE compte&nbsp;: aucun total n'est annoncé par le site. Et la forme FR **ne tient PAS** ici — les salaires italiens sont réels — ce que cette section avait précisément refusé de supposer, et elle avait raison.*

**TROIS OBSERVATIONS QUI NE SONT PAS À CETTE FICHE ET QUI SONT REMONTÉES, PARCE QU'ELLES TOUCHENT LES QUATRE FRONTS ET NON L'ITALIE&nbsp;:** *(1) `contacts_withheld` est codé à `True` en dur et il est asserté vrai dans plus de QUARANTE adaptateurs de la suite — c'est donc une déclaration de POLITIQUE de l'adaptateur et non une mesure par ligne, et le lire comme une mesure ferait croire qu'un contact a été retiré des 7 719 annonces italiennes où il n'y en a aucun&nbsp;; (2) le champ `currency_field_holds_a_country` porte ici `"EUR "`, une vraie devise, donc son NOM est faux pour l'Italie — mais il encode une mesure faite sur les autres fronts et le renommer changerait le schéma de trois adaptateurs expediés&nbsp;; (3) deux des annonces lues portent `salary_min` à **0.01** et à **10**, que `money()` laisse passer puisqu'il n'annule que le zéro exact — trois témoins ne sont pas un dénominateur, donc c'est DECLARÉ et non corrigé.* **Aucune des trois ne se répare sur la foi de trois témoins, et aucune n'est propre à l'Italie.**

## What is NOT established

- **No advert page was fetched.** The guard was taken on an advert path and on its
  parents — `allowed=True`, `state: read`, no rule — but nothing was retrieved, so
  the per-advert field shape is UNREAD and so is whether a contact travels in it.
- **6 260 is our count, not a board statement.** No total was read from the site.
- **Whether the FR `JobPosting` shape holds here is unmeasured.** The sibling cards
  record «the agency as `hiringOrganization`, «null» strings, zero salaries» for
  FR/NO/FI; a shared sitemap shape predicts the ROUTE, not the extraction.
