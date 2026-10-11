# Board measurement — JobTeaser France (`www.jobteaser.com`): the campus-and-graduate platform — **the rules are READ and they OPEN the listings by name**, `Allow: /*/job-search/*` and `Allow: /*/job-offers?locale=*`, with no `Disallow: /` anywhere; and they close the subtree of **nine** locales of which `fr` is not one

<!-- verified: 2026-10-11 -->

<!-- hosts: www.jobteaser.com, jobteaser.com -->
<!-- script: none -->
<!-- countries: FR -->
<!-- content: measured · **THE RULES ARE OPEN ON EXACTLY WHAT AN ADAPTER WOULD READ, AND THE LISTING WAS NOT EXERCISED**: 763 B of rules, `state: read`, `certain: True`, HTTP 200, md5 5e9f87bdd614969cfa9ecd9253fcd755, 2026-10-11T04:56:47Z, as Claude-User, read in a turn distinct from any retrieval; one single group, `*`, with 17 `Allow` and 18 `Disallow` and **no `Disallow: /`**. **THE GUARD WAS RUN, NOT READ**, with one token at a time (`claude-user`): `/fr/job-search` → `allowed=True`; `/fr/job-search/offers` → `allowed=True`; `/fr/job-offers?locale=fr` → `allowed=True` on an explicit `Allow` rule, `/*/job-offers?locale=*`; `/fr/job-offers/12345` → `allowed=True`. The file goes further than tolerating us: it writes `Allow: /*/job-search/*` and re-opens paginated query strings (`Allow: /*?page=*`, `Allow: /*?p=*`) that its own broad `Disallow: /*?*` would otherwise have closed — so pagination is contemplated by the host rather than merely unforbidden. **WHAT IT DOES CLOSE IS A NAMED SET OF NINE LOCALES, AND FRANCE IS NOT IN IT**: `ca`, `cs`, `fi`, `gl`, `it`, `no`, `pl`, `pt`, `sv` each get `Allow: /xx$` then `Disallow: /xx/` — the locale root readable, its subtree refused. `fr`, like `en`, `de` and `es`, has no such pair, so nothing in these rules refuses the French subtree. *That asymmetry is recorded so that a later session does not infer `fr` from `it`* — the same rules file answers the same question differently per locale. Also refused: `*/apply_to_extern_url` (the outbound apply redirect), `/system`, `/cdn-cgi/`, `/*advice_search/*`. **THE SITEMAP LIVES ON ANOTHER HOST, AND THAT HOST WAS GUARDED SEPARATELY**: the rules declare `https://assets-cf.jobteaser.com/sitemaps/sitemap.xml` — `assets-cf.jobteaser.com`, not `www` — and `robots.txt` lie un HÔTE, pas une marque, so the guard was taken there too: `state: absent`, `certain: True`, i.e. no rules file at all, which the owner's decision of 13.09.2026 (#283) reads as an absence of rules and therefore open. **NO `Crawl-delay` ANYWHERE**: `crawl_delay_s` is `null` in our provenance, so the cadence is ours to set — and a file that says no delay does not promise there is no limit; the only way to learn where an unstated threshold sits is to cross it, so we do not learn it. **NOTHING BUT THE TWO RULES FILES WAS RETRIEVED**: no listing, no offer page, no sitemap. So this card establishes a ROUTE that the rules permit and **not** a board: its size, its pagination, what an offer page serves, and whether a school account gates the offers are all unestablished — and «une route vers rien n'est pas une couverture» · 2026-10-11 -->

<!-- witness: none · no enumerator was read, so there is no count to check against anything, and the declared sitemap was deliberately left for the pass that will exercise the host. The France country page carried «accès souvent lié à un compte école» — that sentence is NOT corroborated here and NOT refuted: the rules say nothing about authentication, the page itself declares it unverified, and it is repeated nowhere in this card as a fact · 2026-10-11 -->

## Measured 2026-10-11 — the rules name the listings, and nothing else was touched

```
robots.txt          763 o   state read, certain True, 200, md5 5e9f87bdd614, as Claude-User
  groupes               1   * seul — aucun agent nomme, aucun Disallow: /
  Allow / Disallow  17/18   dont Allow: /*/job-search/*
  Crawl-delay          AUCUN (crawl_delay_s null) — l'allure est la notre
  sitemap declare       assets-cf.jobteaser.com/sitemaps/sitemap.xml   <- AUTRE hote

garde EXECUTEE, jeton claude-user, un seul jeton a la fois (§3 bis) :
  www.jobteaser.com        /fr/job-search              True    (aucune regle)
  www.jobteaser.com        /fr/job-search/offers       True    (aucune regle)
  www.jobteaser.com        /fr/job-offers?locale=fr    True    Allow /*/job-offers?locale=*
  www.jobteaser.com        /fr/job-offers/12345        True    (aucune regle)
  assets-cf.jobteaser.com  /sitemaps/sitemap.xml       True    state ABSENT -> #283

locales dont le SOUS-ARBRE est refuse, et fr n'y est pas :
  ca cs fi gl it no pl pt sv      Allow: /xx$  puis  Disallow: /xx/
```

**Ce qui reste à établir, et c'est la réserve de l'issue.** Ce que `/fr/job-search` sert à un client simple ; si les annonces sont énumérables par le sitemap de l'hôte frère, par la pagination, ou par les deux — et dans ce cas s'ils se contiennent l'un l'autre, parce que deux énumérateurs quasi disjoints ne laissent **aucun témoin** ; ce qu'une page d'annonce porte ; et si un compte école garde les offres, ce que la page pays affirmait sans l'avoir vérifié. **Aucun de ces points ne se devine depuis le fichier de règles**, et un `allowed=True` n'est pas une couverture : c'est une porte dont on n'a pas encore franchi le seuil.
