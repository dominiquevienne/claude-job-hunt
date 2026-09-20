# Board measurement — Le Nouvelliste — Emploi (`emploi.lenouvelliste.com`, Haiti): the newspaper's job board — a board, not a tender section: `/recherche/offres-emploi` lists 111 ads (`/offre-emploi/<id>/<slug>`, ids 1 to 111 — the site's whole run), tenders live apart under `/appels-offres`; ad 1 is dated 28 septembre 2024; served to the declared client (122 KB), rules open; no adapter yet

<!-- verified: 2026-09-20 -->

<!-- hosts: emploi.lenouvelliste.com -->
<!-- script: none -->
<!-- countries: HT -->
<!-- content: measured · **the root (200, 34 425 B, md5 3c9ef16fa3ba / d09a7926a79b — a rendered element moves) is the board's front («Offres d'emploi, appel d'offres et recrutement en Haïti»; prose «Plus de 4500 offres d'emploi vous attendent» and «80 jobs» tiles); `/recherche/offres-emploi` (200, 121 967 B, 12:16 UTC) lists 111 distinct `/offre-emploi/<id>/<slug>` ads whose ids run 1 to 111 with no gap — the site's entire history — and carries, inside an HTML comment, «44554 résultat(s)» (a template's number, not the list's); the ad `/offre-emploi/1/…` (200, 12 181 B) is a job description (COTEM's Directeur Général) dated «28 Septembre 2024»; tenders are a separate section (`/appels-offres`); no JobPosting; `_robots.allowed('emploi.lenouvelliste.com', '/recherche/offres-emploi')` → open, certain** · 2026-09-20 -->
<!-- witness: none — «4500» and «44554» are the template's numbers; the list is 111 ads counted, ids 1–111 · 2026-09-20 -->

**Named on the Haiti page since the Atlas inventory of 2026-09-04 (#147),
never carded; measured for #771 on 2026-09-20 12:15–12:18 UTC by the declared
client, the guard on the exact path first, `bin/fetch-body.py`, two reads.**
*A measurement, not an adapter.*

**Answer to #771's question: a job board, not a tender section.** The 2026-09-04 note («Disallow vide, 12 liens d'appels d'offres») read the front, where the tenders section is linked; the search page lists jobs only and the tenders live under `/appels-offres`. Whether the 111 are open or an archive is the adapter's first question — ad 1 is from September 2024, and the list carries no date.

```
_robots.allowed('emploi.lenouvelliste.com', '/recherche/offres-emploi')   open
GET https://emploi.lenouvelliste.com/                          200 ×2
GET https://emploi.lenouvelliste.com/recherche/offres-emploi   200 — 111 ads, ids 1–111, no pager
GET https://emploi.lenouvelliste.com/offre-emploi/1/…          200 — «28 Septembre 2024»
```
