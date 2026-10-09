# Board measurement — Talent.com France (`fr.talent.com`): the aggregator's French instance — **`/emploi` answers 404 and the enumerator is elsewhere**: the rules declare four sitemaps, and the one named `view-fr` is a 79-file index whose median child carries 10 000 advert addresses

<!-- verified: 2026-10-09 -->

<!-- hosts: fr.talent.com, talent.com -->
<!-- script: none -->
<!-- countries: FR -->
<!-- content: measured · **the path we interrogated first answers 404, and that describes THE PATH and not the host**: `GET /emploi` returned **HTTP 404 with a 299 300 B body** (2026-10-09T07:08Z, as Claude-User) — a readable body is not an answer, the code decides, and the body was NOT kept. **THE ENUMERATOR IS DECLARED AND IT IS NAMED BY USE**: the `*` group declares FOUR sitemaps — `/sitemaps/serp-fr/sitemap.xml`, `/sitemaps/salary-fr/sitemap.xml`, `/sitemaps/tax-calculator-fr/sitemap.xml`, `/sitemaps/view-fr/sitemap.xml` — and their names separate the facet family (`serp` = search result pages) from the advert family (`view`), so reading all four would over-count by construction. `view-fr/sitemap.xml` (200, 10 224 B, md5 d515a0ee6481) is an INDEX of 79 children `view-fr-<n>/sitemap.xml`; its MEDIAN child (`view-fr-40`, 200, 1 150 109 B, md5 fd426f4e7230) carries **10 000 `<loc>`, 10 000 distinct, with a `<lastmod>` on every one**, every one of the form `/view?id=<18-digit id>` — a query parameter and not a path segment, which matters for any rule written on a prefix. **THE SIZE IS NOT ESTABLISHED**: 79 × 10 000 would be an upper bound from one median file, the last child may be partial, the `serp-fr` and `salary-fr` families are deliberately left aside, and **no advert page has been opened**. THE RULES, read in a turn distinct from every retrieval: the group that applies to `claude-user` is `*`, with **no `Disallow`** and **no `Crawl-delay`** — the cadence is ours to set, an absent delay being no promise of absent limits. Each of the four sitemap URLs was guarded on its own host and path before anything was fetched. METHOD: `bin/fetch-body.py` throughout; the 404 travels as a refusal and its body was not saved** · 2026-10-09 -->

<!-- witness: 10 000 `<lastmod>` for 10 000 `<loc>` in the median `view-fr` child, so freshness is per advert; and the four sitemap families are named BY THE HOST itself (`serp`, `salary`, `tax-calculator`, `view`), which is the only reason the facet family can be set aside without reading it — the site's own naming, not our inference · 2026-10-09 -->

## Measured 2026-10-09 — the 404 is a fact about `/emploi`, not about the host

```
robots.txt                        2 019 o   state read, certain True
  groupe *                                  AUCUN Disallow · aucun Crawl-delay
  4 sitemaps declares                       serp-fr · salary-fr · tax-calculator-fr · view-fr
/emploi                                     HTTP 404 (corps de 299 300 o NON garde)
view-fr/sitemap.xml              10 224 o   79 <sitemap> — un index
view-fr-40/sitemap.xml        1 150 109 o   10 000 <loc> · 10 000 distinctes · 10 000 <lastmod>
                                            forme /view?id=<id a 18 chiffres>
```

**Ce qui reste à établir :** le chemin de liste réel — `/emploi` n'en est pas un —, la taille du board en comptant les 79 enfants plutôt qu'en multipliant un médian, et ce qu'une page `/view?id=` sert. *Et `serp-fr` est la famille de facettes : la lire ferait sur-compter le board, ce que son propre nom suffit à annoncer.*
