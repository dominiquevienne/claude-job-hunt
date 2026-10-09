# Board measurement — Jobijoba France (`www.jobijoba.com`): the aggregator's French instance — **the rules open a group that NAMES `claude-user` and give it `Disallow: /fr/query/`**, and `/fr/emploi` is a directory of categories rather than a result list

<!-- verified: 2026-10-09 -->

<!-- hosts: www.jobijoba.com, jobijoba.com -->
<!-- script: none -->
<!-- countries: FR -->
<!-- content: measured · **884 BYTES OF RULES THAT NAME ONE OF THIS PROJECT'S OWN TOKENS AND WRITE A REFUSAL FOR IT**: the group that applies is `claude-user` itself — not `*` — and it carries exactly 1 rule, **`Disallow: /fr/query/`** (`state: read`, `certain: True`, read in a turn distinct from every retrieval), and **no `Crawl-delay` anywhere in the file**, so the cadence is ours to set and an absent delay is no promise of absent limits. **THE SCOPE IS THE PATH AND NOTHING WIDER**: a `Disallow` that targets our path is borne 1 and binds EVERY route, the browser included, **on that path**; it is not a verdict on the board, and a closure verdict belongs to the owner (§2 sexies). *`/fr/query/` is, in all likelihood, where the result pages live — but this tool has not exercised it and cannot, so the inference is named as one.* WHAT `/fr/emploi` SERVES, measured: 200, 79 799 B, md5 cf71eb4770f3, 2026-10-09T07:08:31Z, as Claude-User — `<title>` «Toutes les offres d'emploi par métiers ou entreprises», `<h1>` «Vos offres d'emploi en temps réel», **zero `JobPosting`**, and the link forms its HTML carries are category directories (`/fr/offres-d-emploi-par-metier`, `/fr/offres-d-emploi-par-societe`, `/fr/interim`) plus the signed-in paths. So the path is a DIRECTORY and our extraction found no advert link in it — a statement about what this tool read. **A COUNT THE SITE STATES ABOUT ITSELF, AND IT IS NOT A FRENCH FIGURE**: the page prints «2 492 840 offres», which is the aggregator's own total **across every country it serves**; it bounds nothing on this page and is recorded here only so that nobody later reads it as a count of French adverts. NO SITEMAP IS DECLARED by the rules, so there is no index to follow. METHOD: guard on the exact URL before the retrieval and in a separate turn; `bin/fetch-body.py`, provenance beside the body** · 2026-10-09 -->

<!-- witness: the only figure read is the one the site states about ITSELF — «2 492 840 offres», all countries — and it is deliberately NOT used as a bound; there is no per-country count in the bytes read, and no enumerator at all, so nothing here can be checked against anything the board publishes about France · 2026-10-09 -->

## Measured 2026-10-09 — it names us, and the refusal has a scope

```
robots.txt          884 o   state read, certain True
  groupe applique           **claude-user** — nous sommes NOMMES
  sa seule regle            Disallow: /fr/query/      <- borne 1 SUR CE CHEMIN
  Crawl-delay              AUCUN — l'allure est la notre
  sitemaps declares         aucun
/fr/emploi       79 799 o   title « Toutes les offres d'emploi par metiers ou entreprises »
                            h1    « Vos offres d'emploi en temps reel »
                            0 JobPosting · liens de CATEGORIES, pas d'annonces
                            « 2 492 840 offres » — annonce par le site, TOUS PAYS
```

**Ce qui reste à établir, et la réserve est double :** par quel chemin autre que `/fr/query/` une liste d'annonces serait atteignable — s'il en existe un —, et ce qu'une page d'annonce sert. **Le refus écrit porte sur `/fr/query/` et sur rien de plus large :** dire « cet hôte est fermé » dépasserait ce qui est mesuré, et ce verdict-là appartient au propriétaire.
