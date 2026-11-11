# Board measurement — Jwennjob (`jwennjob.com`, Haiti): «Plateforme de recherche d'emploi en Haïti» — a Next.js app whose `/jobs/` page is a shell, and whose list is served by the site's OWN Next proxy — `/api/proxy/jobs?page=N`, a Laravel envelope that PRINTS its own total; 238 advertisements over 20 pages of 12, the walk agreeing with that total; rules absent (404, certain) on BOTH hosts; recruiter mail on every record, withheld. Shipped (#778)

<!-- verified: 2026-11-11 -->
<!-- script: jwennjob.py -->
<!-- route: http · 238 · 2026-11-11 -->
<!-- content: measured · **the list is the site's OWN Next route — `GET https://jwennjob.com/api/proxy/jobs?page=N` (200, 80 289 B, md5 eb00d4bcf068), a Laravel envelope declaring `total 238, per_page 12, last_page 20`; the walk closed on 19 pages of 12 plus a tail of 10 = 238 and AGREES with that total. The bundle's base `https://api.jwennjob.com/api/v1` answers 401 to a plain client — a technical entry condition on an upstream we never call (#100) — and `x-proxy-api-key-required` is a FLAG and not a key: the body is identical with it and without. Advertisements read by ID (`/api/proxy/jobs/348`, 4 453 B); a SLUG is a 404, and the page builds its own link on the id too. The detail route adds exactly two fields, `languages` and `skills`, measured by differencing the key sets. Rules absent on BOTH hosts (404, certain, 2026-11-11). NO publication date exists on this route: `deadline` is the only advertisement date, `recruiter.created_at` dates a company, and `posted` is emitted absent.** · 2026-11-11 -->
<!-- witness: the board PRINTS its own total — `meta.total` 238 against 238 emitted, so a short read is nameable · 2026-11-11 -->
<!-- verified: 2026-09-20 -->

<!-- hosts: jwennjob.com -->
<!-- script: none -->
<!-- countries: HT -->
<!-- content: measured · **the root (200, 92 698 B, md5 df8719056b52 identical on two reads) and `/jobs/` (200, 59 243 B, 12:16 UTC) are a Next.js app (`self.__next_f`, hashed chunks) — the list page renders «Trouvez le job qui vous ressemble vraiment … Chargement» and sector links `/jobs/?q=Commercial|Communication|Data|Développeur|Finance|Graphiste`, no ad, no count, no `/api/` or API host in the markup; no JobPosting; `_robots.allowed('jwennjob.com', '/jobs/')` → open, certain (the rules file is a 404)** · 2026-09-20 -->
<!-- witness: none — a shell · 2026-09-20 -->

**2026-11-11 — #778: the call is read, and «Pas de donnée» is a sentinel.**
`recruiter.email` is a real address on **34 of 34** of a spread sample (pages 1,
10 and 20), so the issue's «ce qu'il ne donnera jamais: les contacts recruteur»
was false of this route; it is withheld and the witness is DERIVED from what the
redaction took. **And the floor is POSITIVE because this board writes
«Pas de donnée» into its empty columns — 47 times on page 1 alone.** Measured:
`if x` would name a withheld telephone on **28** of those 34 records where the
floor names **8**, so twenty records would have declared a discretion nobody
exercised. *`api.jwennjob.com` is NOT in `hosts:` on purpose: it is a host of
this board that nothing here interrogates, and a reader that guards what nobody
queries is the trap `_cards` documents.*

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
