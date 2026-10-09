# Board measurement — Jooble France (`fr.jooble.org`): the aggregator's French instance — **the enumerator is declared and it is two levels deep, 615 children in THREE families of which 469 are advert files**, and the listing page itself serves an `ItemList` with no `JobPosting` and no advert link at the expected pattern

<!-- verified: 2026-10-09 -->

<!-- hosts: fr.jooble.org, jooble.org -->
<!-- script: none -->
<!-- countries: FR -->
<!-- content: measured · **the declared enumerator is an INDEX OF INDEXES and its children split by family, so a count of its `<loc>` would not be a count of adverts**: `/sitemap.xml` (200, 77 635 B, md5 9f161651e6d2, 2026-10-09T07:10:19Z, as Claude-User) carries 615 `<sitemap>` children, and their file names split into THREE families — `sitemap_tree_jdp_fr_FR_<n>` 469 files, `sitemap_tree_kwserp_fr_FR_<n>` 76, `sitemap_tree_rjdp_fr_FR_<n>` 70. `jdp` reads as job detail page and `kwserp` as keyword SERP, i.e. facets; **`rjdp` is NOT identified and is named rather than guessed.** The MEDIAN child of the `jdp` family (`sitemap_tree_jdp_fr_FR_308.xml`, 200, 111 528 B, md5 d3709f01fef8) carries **1 000 `<loc>`, 1 000 distinct, with a `<lastmod>` on every one**, all of the form `/jdp/<signed 19-digit id>` — 501 with a leading minus and 499 without, which is one id space and not two. **THE SIZE OF THE BOARD IS NOT ESTABLISHED and no figure is published here**: 469 × 1 000 would be an upper bound built on one median file, the last file of each family may be partial, and **no advert page has been opened at all**. WHAT THE LISTING PAGE SERVES, measured separately: `/emploi` (200, 627 986 B, md5 8d875d0fb539) carries ONE JSON-LD `ItemList` and **zero `JobPosting`**, and the only link forms its HTML carries at the advert pattern are navigation (`/post-a-job`, `/jobseeker-reviews`) — **our extraction found no advert link in the bytes served to the declared client**, which is a statement about what this tool read and not about what the host does; the adverts are reached through the enumerator above. THE RULES, read in a turn distinct from every retrieval: the group that applies to `claude-user` is `*`, it writes **no `Disallow` at all**, declares one sitemap, and sets **no `Crawl-delay`** — and an absent delay is not an absence of a rate limit, so the cadence is ours to set. METHOD: guard taken on each exact URL, host included, before each retrieval and in a separate turn; `bin/fetch-body.py` throughout, so every body carries its provenance** · 2026-10-09 -->

<!-- witness: the enumerator dates every entry — 1 000 `<lastmod>` for 1 000 `<loc>` in the median `jdp` child, so an incremental re-walk has a real per-advert signal; there is NO count stated by the site anywhere in the bytes read, so nothing here can be checked against a figure the board publishes about itself, and that is why no size is claimed · 2026-10-09 -->

## Measured 2026-10-09 — the route is established, the size is not

```
robots.txt        1 653 o   state read, certain True
  groupe *                  AUCUN Disallow · aucun Crawl-delay · 1 sitemap declare
/sitemap.xml     77 635 o   615 <sitemap> — un index D'INDEX
  jdp     469              job detail page
  kwserp   76              keyword SERP — des FACETTES
  rjdp     70              NON IDENTIFIE : nomme, pas devine
jdp_308.xml     111 528 o   1 000 <loc> · 1 000 distinctes · 1 000 <lastmod>
                            forme /jdp/<id signe a 19 chiffres>
/emploi         627 986 o   1 ItemList · 0 JobPosting · aucun lien d'annonce au motif attendu
```

**Ce qui reste à établir, et c'est la réserve de l'issue :** la taille du board — il faut compter les `<loc>` des 469 fichiers `jdp` plutôt que de multiplier un médian —, la nature de la famille `rjdp`, et **ce qu'une page `/jdp/<id>` sert réellement**, qu'aucune mesure de cette fiche n'a ouverte.
