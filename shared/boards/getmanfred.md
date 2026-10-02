# Board measurement — Manfred (`www.getmanfred.com`, Spain): tech and product, salaries shown on the offers — **the declared `sitemap-offers.xml` enumerates 1 661 offers, but it spans 2021→2026 and is NOT a live-inventory witness: only 96 carry a `lastmod` since July 2026 and 9 in October**; rules fully open with no AI agent named; the adapter's first line is how an offer page states its own status, because the sitemap does not

<!-- verified: 2026-10-02 -->

<!-- hosts: www.getmanfred.com -->
<!-- script: none -->
<!-- countries: ES -->
<!-- content: measured · **1 661 offer URLs are enumerable and the enumerator is DECLARED, but the count is NOT a live inventory: `sitemap-offers.xml` (200, 286 142 B, md5 2502b8414781) carries 1 661 `<loc>`, all `/ofertas-empleo/<id>/<slug>`, ids 12→8496, all distinct — and its `lastmod` spans SIX YEARS (2021: 54 ; 2022: 296 ; 2023: 413 ; 2024: 372 ; 2025: 290 ; 2026: 236), with only 96 at `lastmod` ≥ 2026-07, 44 ≥ 2026-09 and 9 in 2026-10. WHAT THE ROUTE DOES NOT RETURN: any statement of whether an offer is OPEN — `lastmod` records when a page last changed, not its status, so a 2022 entry and a live one are indistinguishable from the sitemap alone and share an identical URL shape. METHOD: `robots.txt` 183 B (`state: read`, `certain: True`, group `*`, `Disallow` EMPTY, `Allow: /`, **no AI agent named**, no `Crawl-delay` — so 2 s are ours) and it DECLARES both `sitemap.xml` and `sitemap-offers.xml`; guard open and certain on `/`, `/es/job-offers`, `/sitemap.xml` and `/sitemap-offers.xml`; the newest entries are dated 2026-10-02, the day of this reading** · 2026-10-02 -->

<!-- witness: none yet — 1 661 is the sitemap's extent across six years, NOT a count the board states of its live inventory; no stated total has been found · 2026-10-02 -->

## Measured 2026-10-02 — the enumerator is declared, and it is an ARCHIVE as much as an index

```
robots.txt              183 o   groupe *, Disallow VIDE, Allow: /, aucun agent d'IA nomme
                                declare sitemap.xml ET sitemap-offers.xml
sitemap-offers.xml  286 142 o   1 661 <loc>, /ofertas-empleo/<id>/<slug>, ids 12 a 8496
lastmod                 2021  54 · 2022 296 · 2023 413 · 2024 372 · 2025 290 · 2026 236
                        >= 2026-07  96      >= 2026-09  44      2026-10  9
```

**Found by the Spain pass of #949** — the country page carried this host as «&nbsp;à construire&nbsp;» with
the note «&nbsp;la cible la plus propre de cette page&nbsp;: un board qui publie son propre index
d'annonces n'a besoin d'aucune rétro-ingénierie&nbsp;». **That is confirmed on the rules and on the
enumerator, and qualified on the count.**

### 1 661 is the sitemap's extent, not the board's inventory

*The page's note was right that no reverse-engineering is needed. It did not say how far back the
index goes.* **Six years, and only 96 entries touched in the last three months.** A walk that
emitted all 1 661 as current openings would publish mostly offers closed years ago —
**the `kibriseleman` hazard (#721), but harder here: there the stale index was DISJOINT from the
live list and its ids stopped below theirs, so the two populations separated cleanly. Here they
are INTERLEAVED in one file under one URL shape.**

> **And `lastmod` cannot settle it.** *It records when a page last changed, not whether the offer
> is open* — so it is a proxy for freshness and never a status. **The discriminant has to come from
> the offer page itself**, and establishing that is the adapter's first line.

### What the adapter would do, and the one thing it must establish first

```
route   : http — sitemap-offers.xml is DECLARED, so discovery costs one request
          rules fully open, no agent named, no Crawl-delay -> 2 s are OURS
FIRST   : how an offer page states its own STATUS (open / closed / filled). Until that is
          measured, no count of live offers can be emitted and none is claimed here.
then    : the offer (title, employer, city, date) and — the reason this board matters —
          THE SALARY, which the country page notes is «la donnée qui manque partout
          ailleurs en Espagne». To be verified on the page, not assumed from the claim.
NEVER   : the recruiters' contacts.
```

*Volume is low and quality high: this is tech and product, Madrid and Barcelona, with named
employers.* **It does not replace a generalist — Spain's first board refuses our agents in
writing (InfoJobs) — and it is not a substitute for the seventeen regional public services.**

**Measured 2026-10-02 by the declared client, the guard on each exact path first,
`bin/fetch-body.py`, provenance beside every body.** *A measurement, not an adapter — and the
count above is the enumerator's, never the market's.*

```
_robots.verdict('www.getmanfred.com')  state: read, certain: True, group '*',
                                       disallow: [], allow: ['/'], delay: None,
                                       sitemaps: [sitemap.xml, sitemap-offers.xml]
GET /sitemap-offers.xml                200, 1 661 <loc>
```
