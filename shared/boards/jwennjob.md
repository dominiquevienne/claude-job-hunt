# Board measurement — Jwennjob (`jwennjob.com`, Haiti): «Plateforme de recherche d'emploi en Haïti» — a Next.js app whose `/jobs/` page is served to the declared client (59 KB) as a shell («Chargement…», sector links `/jobs/?q=<secteur>`) with no ad, no count and no API host in its markup; rules absent (404, certain); the list route to measure; no adapter yet

<!-- verified: 2026-09-20 -->

<!-- hosts: jwennjob.com -->
<!-- script: none -->
<!-- countries: HT -->
<!-- content: measured · **the root (200, 92 698 B, md5 df8719056b52 identical on two reads) and `/jobs/` (200, 59 243 B, 12:16 UTC) are a Next.js app (`self.__next_f`, hashed chunks) — the list page renders «Trouvez le job qui vous ressemble vraiment … Chargement» and sector links `/jobs/?q=Commercial|Communication|Data|Développeur|Finance|Graphiste`, no ad, no count, no `/api/` or API host in the markup; no JobPosting; `_robots.allowed('jwennjob.com', '/jobs/')` → open, certain (the rules file is a 404)** · 2026-09-20 -->
<!-- witness: none — a shell · 2026-09-20 -->

**Named on the Haiti page since the Atlas inventory of 2026-09-04 (#147),
never carded; measured for #771 on 2026-09-20 12:15–12:18 UTC by the declared
client, the guard on the exact path first, `bin/fetch-body.py`, two reads.**
*A measurement, not an adapter.*

The 2026-09-04 note («58 Ko, 1 322 caractères, coquille») still holds: the list is fetched by the app.

```
_robots.allowed('jwennjob.com', '/jobs/')   open, certain (404 rules)
GET https://jwennjob.com/        200 ×2 — the front
GET https://jwennjob.com/jobs/   200 — «Chargement», no card
```

The adapter's first line: the call the app makes (a browser's network panel), replayed with the page's own parameters, or a browser route.
