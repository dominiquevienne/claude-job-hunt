# Board measurement — L'Étudiant (`www.letudiant.fr`): student jobs, internships and work-study — **the adverts are not on the host the country page names, and the two hosts carry DIFFERENT rules whose effects are opposite**: the parent NAMES `Claude-User` and opens it while closing `ClaudeBot`, and the adverts host, which publishes no AI group at all, writes `Disallow: /offres?` — refusing exactly the URL form the parent's own home page links

<!-- verified: 2026-10-11 -->

<!-- hosts: jobs-stages.letudiant.fr, www.letudiant.fr, letudiant.fr -->
<!-- script: none -->
<!-- countries: FR -->
<!-- route: http · `jobs-stages.letudiant.fr/offres/<contrat>` — the PATH form, `allowed=True` by the guard EXECUTED, served server-side and EXERCISED once (`/offres/contrat-stage`, 200, 244 947 B, 55 advert links in the raw body); the QUERY form `/offres?...` that the parent's home page links is `allowed=False`, rule `/offres?`, so an adapter copying those links would walk refused URLs · `Crawl-delay: 2` is WRITTEN on this host and binds us; the parent writes none · board size NOT established: no total is declared anywhere on the page · 2026-10-11 -->
<!-- content: measured · **55 advert links in the raw body of 1 list page, 2 rules files across 3 host forms, 1 `Crawl-delay` of 2 s that only one of them writes, and NO total declared anywhere — so the road is real and the size of this board is NOT established.** **AND THE ADVERTS ARE ON A HOST THE COUNTRY PAGE NEVER NAMED.** The page named `letudiant.fr`; the adverts live on `jobs-stages.letudiant.fr`, and `robots.txt` binds a host and not a brand — the `merojob.com`/`sg.merojob.com` and `db.bast.af` shape, here with the DANGEROUS polarity: the parent is PERMISSIVE for us, so reading the parent as the verdict would have been a FALSE OPENING on a host whose own rules were never read (`www.gva.es`/`labora.gva.es` the other way round). **PARENT, `www.letudiant.fr` and `letudiant.fr`** — same body to the byte: 2 578 B, `state: read`, `certain: True`, HTTP 200, md5 982dfc6969487b1acd9ef298a9c37203, 2026-10-11T12:50:18Z, as Claude-User. **IT NAMES OUR TOKENS AND SORTS THEM, WHICH IS THE STRONGEST CORROBORATION YET OF THE OWNER'S DECISION OF 07.09.2026** — taken against the pilot's advice: one group lists eleven agents that fetch FOR A PERSON (`Applebot`, `ChatGPT-User`, `Claude-SearchBot`, **`Claude-User`**, `MistralAI-User`, `Perplexity-User`, `YouBot`…) and gives them a restricted but OPEN set; a second group lists seventy-odd crawlers and gives them `Disallow: /` — **`ClaudeBot`, `Claude-Web` and `anthropic-ai` are in THAT one.** The guard, EXECUTED one token at a time (§3 bis), returns for `/`: `claude-user` True (group `claude-user`), `claude-searchbot` True, and `claudebot` / `claude-web` / `anthropic-ai` False with `kind=host-closed`. *The host drew the distinction the decision asserts, in its own file.* **WHAT THE PERMITTED GROUP REFUSES, AND NONE OF IT IS AN ADVERT**: `/cdn-cgi/`, one hash path, `/fiches/` (with `Allow: /fiches/etudes/fiche/` honoured by the guard), `/etudes/annuaire-enseignement-superieur`, `/etudes/annuaire-alternance`, `/college/annuaire-des-colleges`, `/lycee/annuaire-des-lycees`, `/classements`, `/resultat`. **THE DECLARED SITEMAP IS NOT AN ENUMERATOR OF ADVERTS**: the index names five children and not one is named for jobs; `sitemap-general-1.xml.gz` read in full — 13 228 833 B decompressed, **50 000 `<loc>`**, prefixes `/etudes` 39 576, `/college` 8 733, `/bac` 1 689 — **zero advert path**; `general-2` and `general-3` were NOT read, so this says «no jobs file is DECLARED», never «the adverts are not in the sitemap». And `sitemap-annuaire-lycees-diplomes` enumerates the very subtree our group is refused, so it was left unread (letter against intention, §3 bis). **`/jobsstages` IS EDITORIAL, NOT A LIST — and that is the §3 bis trap caught in the act**: eleven links on the home page, `allowed=True`, and what they serve is advice articles, testimonials («mon job d'été moniteur de kayak»), letter templates and a salary simulator. *A prefix reads like a nature and it is not.* **ADVERTS HOST, `jobs-stages.letudiant.fr`** — 422 B, `state: read`, `certain: True`, 200, md5 31b31fafdd679210cc9b80e0f12ad956, 2026-10-11T12:53:45Z. **No AI group at all, so every one of our tokens falls under `*`** — the opposite regime from the parent, on the same brand. It opens `/`, `/offres/`, `/jobs/`, `/entreprises/`, `/sitemap.xml`, `/sitemaps/` and refuses `/me/`, `/job-alert/`, **`/offres?`, `/jobs?`, `/entreprises?`, `/companies?`** — the query forms. Guard exercised both ways on fifteen paths: `/offres/contrat-stage` True, `/offres?contracts=<id>` False with rule `/offres?`. **AND IT WRITES `Crawl-delay: 2` WHILE THE PARENT WRITES NONE** — the EURES shape (`eures.europa.eu` silent, `europa.eu` at 10): reading the obvious host would have run the adverts host with no delay at all. **EXERCISED ONCE**: `/offres/contrat-stage`, 200, 244 947 B, md5 360b697216425185c892f3d5a501ef8e — **55 `/offres/<slug>` links in the RAW body**, so the list is rendered server-side; 6 `application/ld+json` blocks of which **none is a `JobPosting`**; `self.__next_f` ×5, so the payload is React Server Components — *whoever writes the adapter inherits the `"$undefined"` sentinel family, and a positive floor is required, never a list of refusals.* **NO TOTAL IS DECLARED**: `totalCount`, `nbHits`, `numberOfItems`, `ItemList` all zero on the page, so the board size is NOT established and 55 is one facet's first page, never a count. **AND `/offres` ON THE PARENT ANSWERS 404 WITH 331 710 BYTES** — a readable body that `fetch-body.py` refused to keep; the record carries `body_kept: false`, md5 3eb6ed768c7655bbb10a4e1b8fe8c878, and vendor headers `server: cloudflare`, `cf-ray … -ZRH`, `via: 1.1 google`. *My own instrument hid the subdomain for one turn: a prefix tally that split URLs on the string `letudiant.fr` collapsed `jobs-stages.letudiant.fr/offres` into `/offres`, which is why the 404 happened at all — printing the hrefs RAW is what found it.* **The platform behind the adverts host is PILOTY** (`piloty-public.s3.eu-west-3.amazonaws.com` serves its media) — recorded as a LEAD for #406 and claimed for nothing: one tenant establishes nothing about a family · 2026-10-11 -->
<!-- witness: none · the page states no total in any form, and the only counts held are our own extraction (55 advert links on one facet's first page), which is not a witness · 2026-10-11 -->

## Measured 2026-10-11 — three host forms, two rules files, opposite effects

```
PARENT  www.letudiant.fr = letudiant.fr   2 578 o  200  md5 982dfc696948…  read/certain
  notre groupe       claude-user  NOMME, avec 10 autres agents « pour une personne »
  refus de CE groupe /cdn-cgi/ · <hash> · /fiches/ (sauf /fiches/etudes/fiche/) ·
                     /etudes/annuaire-* · /college/annuaire-des-colleges ·
                     /lycee/annuaire-des-lycees · /classements · /resultat
  Crawl-delay        AUCUN
  sitemap declare    5 enfants, AUCUN nomme pour les offres ; general-1 lu : 50 000 loc,
                     prefixes /etudes /college /bac, ZERO chemin d'annonce (2 et 3 NON lus)
  /offres            404, 331 710 o, body_kept false      <- ce n'est pas l'hote des annonces

ANNONCES  jobs-stages.letudiant.fr          422 o  200  md5 31b31fafdd67…  read/certain
  notre groupe       *            AUCUN groupe d'agent IA sur cet hote
  Crawl-delay        2            ECRIT, donc il nous lie — le parent n'en ecrit aucun
  sitemap declare    https://jobs-stages.letudiant.fr/sitemap.xml   <- NON lu

garde EXECUTEE, un seul jeton a la fois (§3 bis) :
  www.letudiant.fr          /  claude-user       True   group claude-user
  www.letudiant.fr          /  claude-searchbot  True   group claude-searchbot
  www.letudiant.fr          /  claudebot         False  host-closed  rule /
  www.letudiant.fr          /  claude-web        False  host-closed  rule /
  www.letudiant.fr          /  anthropic-ai      False  host-closed  rule /
  www.letudiant.fr   /fiches/                    False  disallow     rule /fiches/
  www.letudiant.fr   /fiches/etudes/fiche/x      True   allow        rule /fiches/etudes/fiche/
  jobs-stages…  /offres/contrat-stage            True   (aucune regle)   delay 2.0
  jobs-stages…  /offres/contrat-alternance       True   (aucune regle)   delay 2.0
  jobs-stages…  /offres?contracts=<id>           False  disallow  rule /offres?
  jobs-stages…  /jobs?page=2                     False  disallow  rule /jobs?
  jobs-stages…  /me/                             False  disallow  rule /me/

liste EXERCEE : /offres/contrat-stage  200  244 947 o  md5 360b69721642…
  55 liens /offres/<slug> dans le corps BRUT      -> rendu cote SERVEUR
  6 blocs application/ld+json, AUCUN JobPosting   -> les annonces ne sont pas en LD
  self.__next_f x5                                -> React Server Components
  totalCount / nbHits / numberOfItems / ItemList  -> 0 partout : AUCUN total declare
```

**Ce que cette fiche ne dit pas.** Ni combien d'annonces porte ce board — aucun total n'est déclaré et 55 est la première page d'une facette — ni que les trois facettes (`contrat-stage`, `contrat-alternance`, `contrat-job-etudiant`) soient disjointes, ni que `general-2` et `general-3` du sitemap parent ne contiennent aucune annonce : ils n'ont pas été lus. Elle ne dit pas non plus que Piloty se comporte ainsi ailleurs — un locataire ne dit rien d'une famille.

**Pourquoi le refus du parent sur `ClaudeBot` ne change rien ici.** La décision du propriétaire du 07.09.2026 sépare les deux jetons, et cet hôte les sépare lui-même ; nous nous présentons sous `claude-user`, par la voie HTTP ordinaire, et le navigateur n'a aucune raison d'être piloté (§2 quater). Sur l'hôte des annonces la question ne se pose même pas : il ne nomme aucun agent d'IA.
