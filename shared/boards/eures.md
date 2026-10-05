# Board measurement — EURES (`europa.eu/eures`, the European employment network): **a PUBLIC REST API that answers our declared client with no key and no account**, and the host DECLARES its own ceiling — `jvse.max.faj.search.results: 10000` against 1 940 004 vacancies stated; Spain is 28 499 and Switzerland 44 670 by the host's own facet; and the editorial host and the offers host ask for DIFFERENT rates, the offers one writing `Crawl-delay: 10`

<!-- verified: 2026-10-05 -->

<!-- hosts: europa.eu, eures.europa.eu -->
<!-- script: none -->
<!-- countries: AT BE CH CZ DE ES FR NL NO PL SE SK -->
<!-- route: http · the portal's own public REST API answers the declared client (200) with no key, no account and no form · 2026-10-05 -->
<!-- host-forms-basis: read — TWO hosts, and they do not ask for the same rate: `eures.europa.eu` serves 1 638 B (md5 598e6bf4d601, `state: read`, `certain: True`) which is DRUPAL'S STOCK FILE and writes NO `Crawl-delay`; `europa.eu`, where the offers and the API live, serves 4 930 B (`state: read`, `certain: True`) and writes `Crawl-delay: 10`, with none of its 129 `Disallow` touching `/eures/portal/` or `/eures/api/` · 2026-10-05 -->
<!-- content: measured · **1 940 004 vacancies are stated by the host's own search endpoint and only 10 000 of them are reachable per query, because the host DECLARES that ceiling itself: `GET /eures/api/jv-searchengine/public/properties` returns `jvse.max.faj.search.results: '10000'`, and the pager shows 1 000 pages of 10 — so the limit is a published property and not an inference from a pager. THE ROUTE IS A PUBLIC REST API AND IT ANSWERS THE DECLARED CLIENT: 17 `/eures/api/` calls were observed from the portal, every one under `/public/` and every one 200; `GET …/jv-searchengine/public/statistics/getNumberOfJobs` answers our own client with `{numberOfJobs: 2603942}`, and `POST …/jv-searchengine/public/jv-search/search` answers 200 to a body of `{resultsPerPage, page}` ALONE, returning `numberRecords`, `jvs` and `facets`. THREE OF THE HOST'S OWN TOTALS, AND THEY DISAGREE: `getNumberOfJobs` says 2 603 942; an unfiltered search says `numberRecords` 1 940 004 (the page displayed 1 940 005 a minute earlier); the POSITION_LOCATION facet sums to 1 940 303, which EXCEEDS `numberRecords` by 299 — while the EURES_FLAG facet sums to 1 940 004 EXACTLY. So one facet partitions the total cleanly and another overshoots it, and a separate endpoint reports 663 938 more. None of the three gaps is explained here. SPAIN AND SWITZERLAND, FROM THE HOST'S FACET: `es` 28 499 over 20 NUTS-2 children (`es51` 7 255; `es30` 3 423; `es52` 2 844; `es41` 2 665; `es61` 2 331; `es-NS` 1 401 unspecified) and `ch` 44 670 over 8 — so Switzerland carries MORE than Spain here, which matters for a candidate reading from Switzerland. 32 countries appear in that facet and only 12 of their codes were captured, so the `countries:` line of this card UNDERSTATES by construction and says so. THE DEFAULT ORDERING IS NOT NEUTRAL AND THE FACET PROVES IT: `euresFlag` is true on 42 of the 50 records of page one, against 83 844 of 1 940 004 in the population — a factor of about twenty — so NO field rate taken from page one is a rate of this board. THE RECORD: `id` (base64), `title`, `description`, `employer` as an object (`name` filled on 48 of 50, `website` filled on 0 of 50 — a field that exists and is never filled), `euresFlag`, `locationMap` keyed by country and holding NUTS codes, `numberOfPosts` (summing 156 over 50 records, maximum 12 — so an advert is NOT a post), `positionOfferingCode`, `positionScheduleCodes`, `jobCategoriesCodes`, `creationDate` and `lastModificationDate` as epoch milliseconds, `availableLanguages`, `translations`, `translationType`, `score`. METHOD: guard taken on both host forms and on each exact path in turns distinct from the retrievals and exercised in BOTH directions (`/search/` and `/search/node` refused, the portal and API paths permitted); `bin/fetch-body.py` at the offers host's written 10 s for every GET; the search endpoint called from the portal's own origin, which is a read and not a form submission** · 2026-10-05 -->

<!-- witness: the host states its own totals and they are not one number — `getNumberOfJobs` 2 603 942; an unfiltered `jv-search/search` 1 940 004; the location facet 1 940 303; the EURES_FLAG facet exactly 1 940 004. Each is reported with the endpoint that produced it and none is offered as «the size of EURES». Spain's 28 499 and Switzerland's 44 670 are facet counts from the same unfiltered response, read 2026-10-05 · 2026-10-05 -->

## Measured 2026-10-05 — 1 940 004 stated, 10 000 reachable by the host's own declaration, and Spain at 28 499

```
eures.europa.eu  robots.txt   1 638 o  md5 598e6bf4d601, read, certain
                                       = LE FICHIER PAR DEFAUT DE DRUPAL (2e de la passe)
                                       22 Disallow / 18 Allow · AUCUN Crawl-delay
                                       declare /sitemap.xml
  /sitemap.xml             2 017 951 o  1 302 loc / 1 301 distincts
                                       1 301 lastmod, 425 DISTINCTS, 2021-12-14 -> 2026-10-02
                                       …et il enumere de l'EDITORIAL : webinaires,
                                       conseils, journees de l'emploi. Aucune offre.
europa.eu        robots.txt   4 930 o  read, certain, Crawl-delay: 10
                                       129 Disallow, aucun ne vise /eures/portal/ ni /eures/api/
  -> DEUX hotes d'un meme portail, DEUX allures ; celui des offres demande 10 s
la coquille  /eures/portal/jv-se/home  200, 68 924 o, 10 CARACTERES visibles
                                       app-root -> Angular
  main-TD4BKMNS.js resolu sur le REPERTOIRE   200 … et c'est LA COQUILLE
                                       68 924 o identiques, md5 different au seul
                                       offset 847 (une balise Dynatrace rid=/rpid=)
  <base href="/eures/portal/">         c'est LUI qui decide
  le vrai bundle                       235 539 o de modules ES, 84 chunks nommes
l'API publique, 17 appels observes, tous /public/, tous 200
  GET  …/public/statistics/getNumberOfJobs   200  {"numberOfJobs":2603942}
  GET  …/public/properties                   200  jvse.max.faj.search.results = 10000
  POST …/public/jv-search/search             200  avec {resultsPerPage, page} SEULS
                                       -> numberRecords 1 940 004 · jvs · facets
les comptes de l'hote, et ils DIFFERENT
  getNumberOfJobs                      2 603 942
  recherche sans critere               1 940 004   (la page affichait 1 940 005)
  facette POSITION_LOCATION, somme     1 940 303   (+299)
  facette EURES_FLAG, somme            1 940 004   EXACTEMENT
  -> une facette partitionne juste, l'autre depasse ; ecarts NON expliques
par pays, facette de l'hote (32 pays listes)
  de 661 883 · fr 443 442 · nl 261 140 · be 251 603 · at 64 961
  ch  44 670   (8 regions)        <- plus que l'Espagne
  es  28 499   (20 regions NUTS-2 : es51 7 255 · es30 3 423 · es52 2 844
                es41 2 665 · es61 2 331 · es-NS 1 401 …)
le tri par defaut n'est PAS neutre
  euresFlag vrai sur la page 1         42 / 50     (84 %)
  euresFlag dans la population         83 844 / 1 940 004  (4,3 %)
  -> un facteur ~20 : aucun taux de la page 1 n'est un taux du board
l'enregistrement, sur 50 lues
  employer.name                        48/50     ·  employer.website  0/50
  numberOfPosts                        somme 156, max 12  -> annonce != poste
  locationMap                          pays -> codes NUTS ; 50/50 a UN seul pays
```

**Found by the Spain pass of #949**, where the country page listed it with an open question —
*«&nbsp;doublonne les services régionaux plutôt qu'il ne les complète — à évaluer avant de
construire&nbsp;»*. **That question is now answerable in one direction: EURES states 28 499 Spanish
vacancies of its own accord, which is more than any single regional service measured in this pass
could show.** *Whether those 28 499 overlap the regional services is NOT measured — the overlap
would need identifiers from both sides, and three of the four regional services measured today
serve no enumerable list at all.*

### Two hosts of one portal, and only one of them asks for a rate

| host | rules | rate |
| :-- | :-- | :-- |
| `eures.europa.eu` | 1 638 B, **Drupal's stock file** | **no `Crawl-delay`** |
| **`europa.eu`** | 4 930 B, 129 `Disallow` | **`Crawl-delay: 10`** |

**The offers and the API live on `europa.eu`.** *So a reading that took the obvious host's rules —
no delay written, two seconds ours — would have walked the OFFERS host five times faster than it
asks.*

> **This is the host lesson with a RATE consequence rather than a permission one.** *`robots.txt`
> binds a host; so does `Crawl-delay`, and the slower of the two hosts is the one that serves what
> we want.*

*And the rules of `eures.europa.eu` are Drupal's stock file — the second of this pass after
`empregoxunta.md`.* **Its `Disallow: /search/` was checked rather than assumed, and the guard
refuses `/search/` and `/search/node` while permitting the portal and API paths.**

### The declared sitemap dates beautifully and enumerates the wrong thing

**1 302 `<loc>`, and 1 301 `lastmod` carrying 425 DISTINCT values from 2021-12-14 to 2026-10-02.**
*That is real per-page dating — the opposite of the single build stamps `hosco.md` and `jobtoday.md`
both carry.*

**And it enumerates editorial content**: webinars, career advice, European Job Day announcements.
*The 301 paths that match an offer keyword are article slugs — «&nbsp;five-ways-ai-can-help-your-job-search&nbsp;».*

> **So dating quality and enumerator relevance are independent axes.** *A sitemap can be
> impeccably dated and name nothing you want, and a sitemap can name exactly what you want and be
> undatable. Checking one tells you nothing about the other.*

### A `<base href>` and an SPA catch-all made a wrong URL look like a success

**The shell is 68 924 B for ten characters of visible text.** *Resolving `main-TD4BKMNS.js` against
the page's own directory returned **200 — and it was the shell again**, 68 924 bytes identical, the
md5 differing at a single offset (847) where a Dynatrace beacon carries a per-request id.*

> **`<base href="/eures/portal/">` is what relative sources resolve against, not the page's path —
> and an SPA catch-all turns the resulting wrong URL into a 200 with the shell instead of a 404.**
> *So the error never surfaces: a plausible size, a clean parse, and an analysis that reported «no
> API paths in the bundle» when the bundle had never been fetched.*

**The discriminant was the byte count being identical to the shell's**, and that only worked
because the shell's size had been recorded first. *The real bundle is 235 539 B of ES modules
naming 84 chunks — 86 files at the host's 10 s would be fourteen minutes, which is why the
portal's own network requests were read instead.*

### The route: a public API, and the host declares its own ceiling

**17 `/eures/api/` calls, every one under `/public/`, every one 200** — and the two that matter
answer **our declared client**, not only a browser:

```
GET  /eures/api/jv-searchengine/public/statistics/getNumberOfJobs  -> {"numberOfJobs":2603942}
GET  /eures/api/jv-searchengine/public/properties                  -> jvse.max.faj.search.results 10000
POST /eures/api/jv-searchengine/public/jv-search/search            -> numberRecords, jvs, facets
```

**The search endpoint answers 200 to `{resultsPerPage, page}` alone.** *Three earlier attempts
returned 400 because they carried criteria keys I had INVENTED — `sortSearch`, `keywordsEverywhere`,
`locationCodes`. The minimal body worked where the richer one failed, and the fix was to read the
response's own field names instead of guessing more.*

> **The ceiling is DECLARED, which is rare and worth saying plainly:
> `jvse.max.faj.search.results: '10000'`.** *So «&nbsp;10 000 of 1 940 004 are reachable per
> query&nbsp;» is the host's own statement, not a limit inferred from a pager — and the facets are
> the only way to subdivide under it.*

### Three of the host's own totals, and they do not agree

| figure | endpoint | value |
| :-- | :-- | :-- |
| jobs in the system | `statistics/getNumberOfJobs` | **2 603 942** |
| records matching an unfiltered search | `jv-search/search` | **1 940 004** |
| sum of the location facet | same response | **1 940 303** (+299) |
| sum of the EURES_FLAG facet | same response | **1 940 004** — exact |

**One facet partitions the total exactly and the other exceeds it by 299, in the same response.**
*A plausible cause — a vacancy located in several countries, which `locationMap` can represent
since it is keyed by country — was tested and the test establishes nothing:* **299 of 1 940 004 is
0.0154 %, so 50 records expect 0.0077 instances and about 6 488 would be needed to expect one.**
*Fifty records showed one country each, which is neither evidence for nor against; reporting «0 of
50, therefore not multi-country» would have been a false refutation of my own hypothesis.*
**The three gaps are recorded and none is explained.**

### The default ordering is not neutral, and the facet is what proves it

**`euresFlag` is true on 42 of the 50 records of page one — 84 % — against 83 844 of 1 940 004 in
the population, 4.3 %.**

> **A factor of about twenty.** *So no field rate taken from page one is a rate of this board* —
> and it is only visible because the same response carries the population figure beside the sample.
> **Most boards give no such check; here the facet is the control group.**

*Which is also why the field counts below are written as «on 50 records» and never as rates.*

### What an adapter would do

```
route   : http on europa.eu — NOT on eures.europa.eu, which serves the editorial
          site and writes no rate. 10 s between requests, written by the offers
          host under `*`.
witness : getNumberOfJobs AND the search's numberRecords — report BOTH with the
          endpoint that produced each. They differ by 663 938 and neither is
          «the size of EURES».
ceiling : the host declares 10 000 per query (jvse.max.faj.search.results).
          Subdivide by the POSITION_LOCATION facet, which gives per-country and
          per-NUTS counts in the same response as the results.
Spain   : the `es` facet (28 499 on 2026-10-05) and its 20 NUTS-2 children, each
          under the 10 000 ceiling, so Spain is fully walkable facet by facet.
carries : title, description, employer.name, locationMap (country + NUTS),
          numberOfPosts, the schedule and offering codes, creationDate and
          lastModificationDate as epoch ms, the languages and translations
counts  : report adverts and posts SEPARATELY — 50 records summed 156 posts,
          one carrying 12. An advert is not a post, as on Jobandtalent (card pending).
NEVER   : no field rate from page one — the default ordering boosts EURES-flagged
          adverts about twentyfold, and the facet proves it. And never trust
          `employer.website`: the field exists and was filled on 0 of 50.
```

### What this card does NOT say

**It does not say how many vacancies EURES holds, nor that EURES overlaps or does not overlap the
Spanish regional services.** *Four of the host's own figures were read and they disagree; the
overlap question needs identifiers from both sides, and three of the four regional services
measured in this pass serve no enumerable list at all.*

**And the `countries:` line understates by construction.** *The location facet lists **32**
countries; only twelve of their codes were captured in the reading, so twelve are declared.* **The
missing twenty are a measurement not taken, not an absence** — one further call to the same
unfiltered search would list them all.

**Measured 2026-10-05 by the declared client for every GET, the guard taken on both host forms and
each exact path in a turn distinct from the retrieval and exercised in both directions,
`bin/fetch-body.py` at the offers host's written 10 s, the search endpoint called from the portal's
own origin at the same pace.** *A measurement, not an adapter.*

```
_robots.verdict('eures.europa.eu')  state: read, certain: True, 1 638 B, no Crawl-delay
_robots.verdict('europa.eu')        state: read, certain: True, 4 930 B, Crawl-delay 10.0
allowed('eures.europa.eu', '/search/')      False  (rule '/search/')
allowed('europa.eu', '/eures/api/jv-searchengine/public/jv-search/search')   True
GET  eures.europa.eu/sitemap.xml            200, 2 017 951 B, 1 302 <loc>, 0 vacancy
GET  europa.eu/eures/portal/jv-se/home      200, 68 924 B, «Loading...»
GET  europa.eu/eures/portal/jv-se/main-TD4BKMNS.js   200 — THE SHELL, not the bundle
GET  europa.eu/eures/portal/main-TD4BKMNS.js         200, 235 539 B, 84 chunks
GET  …/public/statistics/getNumberOfJobs    200, {"numberOfJobs":2603942}
GET  …/public/properties                    200, jvse.max.faj.search.results 10000
POST …/public/jv-search/search              200, numberRecords 1 940 004, 32 countries faceted
```
