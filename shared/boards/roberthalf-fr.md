# Board measurement — Robert Half France (`www.roberthalf.fr`): the recruitment firm's French board — **its `/robots.txt` answers 404, which is a KNOWLEDGE and not an ignorance**, and the root links its listing at `/fr/fr/offres-emploi`

<!-- verified: 2026-10-09 -->

<!-- hosts: www.roberthalf.fr, roberthalf.fr -->
<!-- script: none -->
<!-- countries: FR -->
<!-- content: measured · **THE RULES ARE ABSENT AND THAT IS A DIFFERENT STATE FROM UNREADABLE**: `/robots.txt` answers 404, so `state: absent` and `certain: True` — the host looked and there is nothing, which the owner's decision of 13.09.2026 (#283) reads as an absence of rules and therefore an open door, **with certainty**. This is NOT the `no-rules`, `certain: False` of a file that could not be read: the two print the same verdict and only `state` separates them, which is why `state` is recorded here and not the prose. **WHAT THE ROOT SERVES**: 200, 155 784 B, md5 e441b6233213, 2026-10-09T07:26:09Z, as Claude-User — `<title>` «Cabinet de recrutement et de recherche d'emploi | Robert Half», **zero `JobPosting`**, no `__NEXT_DATA__`, and **the listing is linked four times at `/fr/fr/offres-emploi`** (beside `/fr/fr/recherche-emploi/candidature-spontanee` and `/fr/fr/recherche-emploi/alerte-emploi`). The locale appears TWICE in the path (`/fr/fr/`), which is the kind of form that a rule written on a single-segment prefix would never match. **NO COUNT IS STATED ANYWHERE in the bytes read** — no figure beside any word for offers, no `ItemList`, no `numberOfItems` — so there is no witness here that does not come from our own extraction, and consequently **no size is recorded**. No `Crawl-delay` can be written where there is no file, so the cadence is entirely ours. METHOD: guard on the exact URL in a turn distinct from the retrieval; `bin/fetch-body.py`, provenance beside the body** · 2026-10-09 -->

<!-- witness: none found · the question was asked and the answer is empty: the 155 784 B read carry NO figure beside any word for offers, no JSON-LD `ItemList` and no `numberOfItems`, so there is nothing on this board that could corroborate a count of ours — which is exactly why no size is written on this card · 2026-10-09 -->

## Measured 2026-10-09 — an absent rules file, and a listing path the root names

```
robots.txt              404   state ABSENT, certain True  <- une connaissance, pas une ignorance
                              (contre `no-rules` + certain False, qui s'imprime pareil)
  Crawl-delay                 impossible a ecrire : il n'y a pas de fichier
/ (racine)        155 784 o   title « Cabinet de recrutement et de recherche d'emploi | Robert Half »
                              0 JobPosting · AUCUN compte enonce par le site
                              liste liee 4 fois : /fr/fr/offres-emploi
                              la locale apparait DEUX fois dans le chemin
```

**Ce qui reste à établir :** ce que `/fr/fr/offres-emploi` sert, comment il pagine, et s'il existe un compte que le board énonce lui-même — **aucun n'a été trouvé dans les octets lus, donc aucune taille n'est écrite ici.**
