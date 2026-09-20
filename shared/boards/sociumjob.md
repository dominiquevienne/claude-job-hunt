# Board measurement — SociumJob (`sociumjob.com`, Senegal): «Trouvez un job en Afrique» — a Dakar HR platform (Socium) whose front is served to the declared client (1.98 MB) with its five latest ads (all Dakar: SETER, the Bureau Organisation et Méthodes; dated 19–20/09/2026) and per-company counts («13 offres publiées»), and whose `/jobs` list is a Nuxt shell («Chargement en cours…», a «Pays» filter); rules open; no count stated; no adapter yet

<!-- verified: 2026-09-20 -->

<!-- hosts: sociumjob.com -->
<!-- script: none -->
<!-- countries: SN -->
<!-- content: measured · **the root (200, 1 977 779 B, md5 8f705f1e41a2 / e49101fda26e — a rendered element moves) is a Nuxt app whose front carries «Les dernières offres sur le marché»: five `/jobs/<slug>-<id>` ads (SETER «Conducteur de trains», CDD, Dakar, 20/09/2026; three of the Bureau Organisation et Méthodes, Dakar, 19/09/2026), partner companies with «N offres publiées» (1, 1, 4, 13); `/jobs` (200, 421 836 B, 12:24 UTC) renders filters (Pays, Contrat, Secteurs) and «Chargement en cours…» — the list is fetched by the app; no JobPosting; `_robots.allowed('sociumjob.com','/jobs')` → open, certain. Listed on #765 (Côte d'Ivoire) by the 2026-09-04 inventory; every ad measured is in Dakar — `countries: SN` by the measure, the «Pays» filter says the board reaches further** · 2026-09-20 -->
<!-- witness: none — no total stated; the front's «N offres publiées» are per company · 2026-09-20 -->

**Named in the Atlas inventory of 2026-09-04 (#147), never carded; measured
for #765 on 2026-09-20 12:23–12:25 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** *A measurement, not an
adapter.*

```
_robots.allowed('sociumjob.com', '/')   open
GET https://sociumjob.com/       200 ×2 — the front, 5 latest ads (Dakar), per-company counts
GET https://sociumjob.com/jobs   200 — a shell, «Chargement en cours…», a Pays filter
```

The adapter's first line: the call the app makes for `/jobs` (a browser's network panel), replayed with its own parameters — with the `Pays` filter, which would settle `countries:` by the measure; the ad `/jobs/<slug>-<id>`.
