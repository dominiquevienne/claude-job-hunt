# Board measurement — Expectra (`www.expectra.fr`): Randstad's French white-collar brand — **the board states 1 714 offers in its own `<h1>` and links its adverts at `/emploi/<slug>/id=<n>/`**, and the three paths its rules refuse are a *different* brand prefix, not that one

<!-- verified: 2026-10-09 -->

<!-- hosts: www.expectra.fr, expectra.fr -->
<!-- script: none -->
<!-- countries: FR -->
<!-- content: measured · **1 714 offers are stated by the board itself, in the `<h1>` of its own root** — «trouver un emploi. parmi nos 1 714 offres» (200, 130 420 B, md5 e523742f0da4, 2026-10-09T07:25:51Z, as Claude-User) — a figure that does NOT come from our extraction, which is the only kind worth writing down. The root carries **zero `JobPosting`** and no `__NEXT_DATA__`, and its advert links take the form `/emploi/<slug>/id=<n>/`, so the adverts are reachable from the served bytes without any client rendering. **WHAT THE RULES REFUSE, AND IT IS NOT THAT PATH**: the group that applies to `claude-user` is `*` (1 876 B, `state: read`, `certain: True`, read in a turn distinct from every retrieval) and it carries exactly three refusals — `/randstad-professional-search/recherche_offres/`, `/randstad-professional-search/nos-bureaux/` and `/candidature_spontanee/$`. **All three sit under a DIFFERENT brand prefix or on the spontaneous-application form; none matches `/emploi/`**, so the advert path is not refused — and the refusal that does exist targets a SEARCH route, which is the shape to re-read before any walk that would use one. **No `Crawl-delay` is written and no sitemap is declared**, so the cadence is ours to set and the enumerator is the listing rather than an index. THE BRAND IS RANDSTAD'S and the bytes say so: the root links `randstadprofessional.fr` four times, and the refused prefix names `randstad-professional-search` — which matters because `randstad-fr.md` already exists and **a shared brand predicts nothing about a shared URL form** (Hays FR→ES transposed its route, Randstad CH→ES transposed neither). **THE SIZE IS STATED, NOT VERIFIED**: 1 714 is the board's own figure and no advert page has been opened, so nothing here establishes what one serves. METHOD: guard on the exact URL, host included, in a turn distinct from the retrieval; `bin/fetch-body.py`, provenance beside the body** · 2026-10-09 -->

<!-- witness: the figure is the board's own — «parmi nos 1 714 offres» printed in the root's `<h1>` — and it is NOT our count of anything; there is no `ItemList` and no `numberOfItems` on the page that could be mistaken for a board total, so the only number recorded is the one the site states about itself · 2026-10-09 -->

## Measured 2026-10-09 — the stated figure, and a refusal that misses the advert path

```
robots.txt           1 876 o   state read, certain True · groupe *
  3 refus                      /randstad-professional-search/recherche_offres/
                               /randstad-professional-search/nos-bureaux/
                               /candidature_spontanee/$
  Crawl-delay                  AUCUN — l'allure est la notre
  sitemaps                     aucun declare
/ (racine)         130 420 o   h1 « trouver un emploi. parmi nos 1 714 offres »
                               0 JobPosting · forme de lien /emploi/<slug>/id=<n>/
                               4 liens vers randstadprofessional.fr
```

**Ce qui reste à établir :** ce qu'une page `/emploi/<slug>/id=<n>/` sert, et par quelle route les 1 714 se paginent — **le refus écrit porte sur un chemin de recherche d'une autre marque, donc il ne ferme pas la liste, et c'est précisément ce qu'il faut vérifier avant d'écrire une marche.**
