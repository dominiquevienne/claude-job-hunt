# Board adapter — Le Nouvelliste — Emploi (`emploi.lenouvelliste.com`, Haiti): `emploilenouvelliste.py` since 2026-11-03 (#777) — the whole history on ONE page (118 ads, ids 1–118 contiguous, no pager, served OLDEST first), **the board states no count and its three numbers that look like one are template literals**, and it declares no date in any form, so the closing date is read from the ad's prose; tenders live apart under `/appels-offres`

<!-- verified: 2026-11-03 -->

<!-- hosts: emploi.lenouvelliste.com -->
<!-- script: emploilenouvelliste.py -->
<!-- host-forms: emploi.lenouvelliste.com -->
<!-- host-forms-basis: read — `emploilenouvelliste.py:HOST`, a single literal; the list and every ad are paths under it · 2026-11-03 -->
<!-- countries: HT -->
<!-- content: measured · **`emploilenouvelliste.py` shipped. `/recherche/offres-emploi` (200, 129 111 B, md5 e70ba749b299, 19:16 UTC) lists 118 distinct `/offre-emploi/<id>/<slug>` ads, ids 1 to 118 with NO gap — the site's entire history, 111 on 2026-09-20, so the board grew by 7 — and there is NO pager: seven candidate forms (`?page=`, `&page=`, `pagination`, `rel="next"`, `page-link`, «Suivant», «suivante») return zero each. The page serves them OLDEST first, so the adapter emits newest first. **The board declares NO DATE anywhere**: no JobPosting, no `application/ld+json`, no `<time>`, no `datetime`, no `datePosted`, no `validThrough`, no `article:published`, and no `Last-Modified` on the wire — measured on 13 ads drawn across the whole id range (1, 10, 20, 30, 40, 50, 60, 69, 79, 89, 99, 109, 118). The ad carries NO `<h1>` (0 of 13): the title is the `<h3>` and the employer the `<p>` that follows, inside `div.col-lg-8.job-post` (once on 13 of 13, always before the aside). FOUR live blocks on 13 of 13 — «Description des responsabilités», «Profil recherché», «Composition du dossier de candidature», «Autre remarque» — and a FIFTH heading, «Lieu de dépôt des candidatures», is 13 of 13 in the markup and **0 of 13 live**, sitting inside an HTML comment on every ad. An empty section is written as a bare full stop, so a filled floor is required. Six of 13 embed base64 images inline, up to 54 % of their own bytes (ad 89: 14 068 of 26 014). A prose closing date, read after «au plus tard» / «date limite», is present on 12 of 13 — ad 89 states none — and the motif must be CASE-INSENSITIVE: ad 118 writes «16 octobre 2026» in lower case where 1 and 60 write «28 Septembre 2024», and the capitalised motif rendered ZERO on an ad carrying two. `/robots.txt` 200 is `User-agent: *` with an EMPTY `Disallow:`, no Crawl-delay and no sitemap declared; `_robots.allowed('emploi.lenouvelliste.com', …)` → open, certain, `state: read`; 3 s is ours** · 2026-11-03 -->
<!-- witness: none — **the board states no count, and its three candidate witnesses are all template literals**: «44554 résultat(s)» inside an HTML comment on the list, «Plus de 4500 offres» on the root, and «80 jobs» printed IDENTICALLY on three different employers' tiles (OCCED'H, the Conseil Électoral Provisoire, SOFALAM) — that repetition is what proves it. The only witness is OURS: ids contiguous 1..N with N ads read certifies the extraction is complete by its PRESENCE, and says nothing by its absence, a deleted ad leaving the same gap as a parse that dropped one · 2026-11-03 -->
<!-- content: measured · **the root (200, 34 425 B, md5 3c9ef16fa3ba / d09a7926a79b — a rendered element moves) is the board's front («Offres d'emploi, appel d'offres et recrutement en Haïti»; prose «Plus de 4500 offres d'emploi vous attendent» and «80 jobs» tiles); `/recherche/offres-emploi` (200, 121 967 B, 12:16 UTC) lists 111 distinct `/offre-emploi/<id>/<slug>` ads whose ids run 1 to 111 with no gap — the site's entire history — and carries, inside an HTML comment, «44554 résultat(s)» (a template's number, not the list's); the ad `/offre-emploi/1/…` (200, 12 181 B) is a job description (COTEM's Directeur Général) dated «28 Septembre 2024»; tenders are a separate section (`/appels-offres`); no JobPosting; `_robots.allowed('emploi.lenouvelliste.com', '/recherche/offres-emploi')` → open, certain** · 2026-09-20 -->
<!-- witness: none — «4500» and «44554» are the template's numbers; the list is 111 ads counted, ids 1–111 · 2026-09-20 -->

## 2026-11-03 — #777: the adapter ships, and three of the things this card predicted are refuted on the object

The head this card carried until today read «**no adapter yet**» and «lists 111 ads … ids 1 to 111»; both are now history. The route held six weeks later and the board had grown to 118.

**What the measurement changed in the code, and none of it was predictable from the 2026-09-20 reading:**

- **A heading inside an HTML comment counted as a live block.** «Lieu de dépôt des candidatures» is 13 of 13 in the markup and 0 of 13 live. Found by RUNNING the adapter, not by reading it — the same shape as counting `<script>` tags on a page that writes the word in its prose.
- **A block that exists is not a block that is filled.** On the procurement-style ads the whole text sits in «Description des responsabilités» and the next two carry a bare full stop, so `if value` emits «.» as content.
- **The redaction had to be ANCHORED, and the object is not an amount.** On the same 13 ads the bare phone motif used elsewhere in this repository takes 7 strings of which **5 are not telephones** — the grant numbers `2000004110` and `200005176`, the contract number `106-2026`, the publication reference `527-05/19` — and the date guard saves none of them. Anchored on `+509` or a written label it takes 2 of the 2 real numbers and 0 of the 5 references. Haiti's public-procurement ads are built out of those references, and they are how a candidate names the post he is applying for. `shared/boards/adecco-it.md` reached the same remedy for an AMOUNT written in threes; this is that conclusion applied to an administrative reference.
- **The prose date motif is case-insensitive, and the case was the whole defect.** The capitalised form rendered ZERO on ad 118, which carries two dates, because 118 writes «16 octobre 2026» in lower case.

**What #777 asked and what the answer is.** Its «ce qui bloque» was *savoir ce qui est ouvert dans les 111*. The board does not answer it and will not: it declares no date in any form, its list carries neither date nor location, and it is served oldest first. What the adapter can give is the closing date the ad's own prose states, on 12 of the 13 measured, labelled `deadline_stated_in_prose` with the phrase it was read from — prose-derived, never a field. *Weaker, and declared weaker.*

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
