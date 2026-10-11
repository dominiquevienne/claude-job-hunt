# Board measurement — Studyrama Emploi (`www.studyrama-emploi.com`): the French student and first-job title of the Studyrama group — **the rules close NOTHING, in the minimal form that says so: 73 bytes whose only directive is an EMPTY `Disallow:`** — and the root is served and read, while the advert list sits behind a legacy PHP search form that was NOT exercised, so this is a road the rules permit and not a coverage

<!-- verified: 2026-10-11 -->

<!-- hosts: www.studyrama-emploi.com, studyrama-emploi.com -->
<!-- script: none -->
<!-- countries: FR -->
<!-- route: http · nothing is refused — `User-Agent: *` with an EMPTY `Disallow:`, guard EXECUTED on five paths, all `allowed=True` under group `*` — and the ROOT is exercised (200, 126 381 B); but the advert list lives behind `home_job_moteur.php`, a search form that was NOT exercised, so taille, pagination and advert shape are NOT established and no coverage is claimed · no `Crawl-delay` applies to us (the only one in the file is `Crawl-delay: 5` under `bingbot`), so the cadence would be ours to set · 2026-10-11 -->
<!-- content: measured · **THE SMALLEST RULES FILE OF THE FRANCE PASS, AND IT IS THE PATHOLOGICAL MINIMAL FORM**: 73 B, `state: read`, `certain: True`, HTTP 200, md5 6138b2307c83f3e7f0ded99396888389, 2026-10-11T12:50:25Z, as Claude-User; the apex `studyrama-emploi.com` serves the same body to the byte (same md5, 12:50:26Z), so the two host forms give one answer. Its whole content is `User-Agent: *` / **`Disallow:` with NO value** — which closes nothing — plus a second group naming `bingbot` to give it `Crawl-delay: 5` and forbid it nothing. **No AI agent is named anywhere, so every token of this project falls under `*`**, and no sitemap is declared. *This is the `inaem.aragon.es` (70 B, empty `Disallow:`) and `employtt.gov.tt` shape, and it is worth saying that our parser reads it RIGHT: the guard was EXECUTED, not read, and returns `allowed=True` with `group=*` and `rule=None` on `/`, `/offres`, `/offre`, `/emploi` and `/recherche` — an empty directive is not an empty FILE and not an absence of rules, and the three states print the same word.* **AND «THE RULES PERMIT» IS NOT «IT IS OURS TO TAKE»** (§3 bis, measured on a Tajik board): a host that forbids nothing has not consented to everything it exposes, and no `Crawl-delay` is no promise of no limit — Milanuncios replaced every answer with a captcha after about nine requests in two and a half minutes while writing no delay at all. **THE ROOT IS EXERCISED AND IT IS A LEGACY PHP SITE**: 200, 126 381 B, md5 2fa780da9d250da1fe3c1e3e2d5697f4, 2026-10-11T12:54:35Z; 169 distinct `href`, almost all `home_<chose>.php?id=<n>` — `home_rubrique.php` alone accounts for about a hundred of them — with `home_article.php`, `home_breve.php`, `home_interview.php`, `home_chaine.php`, `home_dossier.php` and `home_agenda.php` beside it. **Zero `application/ld+json`, zero `itemtype`, five `<form>`**: there is no structured data to read and the list is behind a form, which is the opposite of the sibling in this tranche. **THE ADVERT LIST WAS NOT REACHED, AND THAT IS DELIBERATE**: the home page's own links name `home_job_moteur.php` and `home_moteur.php` — a *moteur* is a search, so the enumeration is almost certainly a query and possibly a POST, and #999 taught that a board whose search is a POST needs `--method POST --form …` with the schema recorded and never the values. One request would have told us; it would also have been a guess at the form's field names, and an unknown written as an unknown is worth more than a fabricated entry (`fetch-body.py` would have had to be handed invented parameters). **So this card carries a ROUTE and no figure, and the reserve is in the issue.** *My own instrument failed twice in this tranche and both times by treating a URL as a path: here a filter looking for employment words in the whole URL matched **every** link on the host, because the word `emploi` is in the HOST NAME — the discriminant is to filter on the PATH, never on the URL, which is the same error that collapsed a subdomain on the sibling host.* · 2026-10-11 -->
<!-- witness: none · no total is stated on the root and the list was not reached, so there is nothing to confront an extraction with · 2026-10-11 -->

## Measured 2026-10-11 — 73 bytes, and nothing is closed

```
robots.txt   www.studyrama-emploi.com = studyrama-emploi.com
             73 o   200   md5 6138b2307c83…   state read, certain True
             User-Agent: *      Disallow:            <- VALEUR VIDE : rien n'est ferme
             User-agent: bingbot  Crawl-delay: 5     <- un autre groupe, pas le notre
             aucun agent d'IA nomme · aucun sitemap declare · aucun Crawl-delay pour nous

garde EXECUTEE, jeton claude-user, un seul a la fois (§3 bis) :
  /            True   group *   rule (aucune)
  /offres      True   group *   rule (aucune)
  /offre       True   group *   rule (aucune)
  /emploi      True   group *   rule (aucune)
  /recherche   True   group *   rule (aucune)

racine EXERCEE : 200, 126 381 o, md5 2fa780da9d25…
  169 href distincts, forme home_<chose>.php?id=<n>   -> site PHP historique
  home_rubrique.php      ~100 des 169                 -> editorial
  home_job_moteur.php · home_moteur.php                -> la recherche, NON exercee
  application/ld+json 0 · itemtype 0 · <form> 5        -> rien de structure a lire
```

**Ce que cette fiche ne dit pas.** Ni combien d'annonces porte ce board, ni qu'il en porte — la liste n'a pas été atteinte — ni que `home_job_moteur.php` soit bien l'énumérateur : c'est le candidat que la page nomme, et il reste à exercer. Elle ne reprend pas non plus le « recoupe La Bonne Alternance sur l'apprentissage, pas sur les stages » que portait la page pays : c'est une appréciation, pas une mesure, et rien ici ne l'établit.

**Pourquoi « rien n'est refusé » n'est pas une conclusion sur le board.** Un fichier de règles qui ne ferme rien dit ce que l'exploitant permet aux robots ; il ne dit pas que l'hôte publie des annonces, ni combien, ni par quelle route. Les deux questions se mesurent séparément, et seule la première l'est ici.
