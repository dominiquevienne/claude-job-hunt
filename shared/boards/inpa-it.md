# Board measurement — InPA (`inpa.gov.it`, Italy): Italy's national portal for public-sector recruitment, read through the sitemap its own rules DECLARE — and the `/wp-json/` route the first measurement named is refused in writing AND is a cookie banner

<!-- verified: 2026-11-09 -->

<!-- hosts: inpa.gov.it, www.inpa.gov.it -->
<!-- script: inpa.py -->
<!-- countries: IT -->
<!-- route: http · 1848 · 2026-11-09 -->
<!-- content: measured · read 2026-11-09: **the detail page carries the vacancy in its SERVED bytes, and the route the 2026-10-06 line prescribed is refused in writing AND is a cookie banner.** Guarded on the EXACT paths in a turn distinct from retrieval, one token: `/wp-json/` and `/wp-json/wcc/v1/` both answer `allowed=False, state=read, certain=True, kind=disallow, rule=/wp-json/` **on both host forms** — a written refusal on our path, so it binds every route, the browser included. *And `wcc` is WebToffee Cookie Consent: the single occurrence of `wcc/v1` in a 103 KB detail page is `var _wccApi = {"base": "…/wp-json/wcc/v1/", "nonce": "…"}`, in a block whose `sourceURL` is `webtoffee-cookie-consent-js-extra`. That namespace would never have served a vacancy.* **The permitted route is the `Sitemap:` the rules file DECLARES** — `_robots.sitemaps_for()` returns it, `group_for()` drops it in silence, and `delay_for()` returns `None`, so no `Crawl-delay` is declared and the 2 s pace is ours. An index of three members, each guarded and permitted; `inpa.py` walks all three rather than trusting the one named `bandi`. **1 848 distinct advertisements on 2026-11-09**, one single path shape — `/bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id=<32 hex>`, the slug being a QUERY STRING and not a path segment — naming the APEX, which contradicts the 2026-10-06 line that every internal link points at `www.`. *It was 1 915 on 2026-11-07: the figure moves and is measured in the run.* The page is server-rendered and carries **no JSON-LD at all** — 0 `JobPosting`, 0 `ld+json`, 0 `__NEXT_DATA__` on four advertisements — so the fields are read from the markup: `Descrizione`, `Area geografica`, `Valutazione`, `Stato`, the two candidature dates, `Numero di posti`, `Ente di riferimento`, the bando PDFs and the apply link. **Dates carry NO offset anywhere and are emitted naive.** `portale.inpa.gov.it` is a third host carrying the apply link and the attachments; it is NOT added to `hosts:` — it has not been guarded, and emitting an address is not retrieving it · 2026-11-09 -->
<!-- content: measured · read 2026-10-06: **the root answers 200 with 149 566 B (md5 125b3dbca532) and names «concorsi» 52 times**, so the public competitions are what this portal publishes. It is a WordPress site, and the route an adapter should be built on is a CUSTOM REST namespace it declares itself: `/wp-json/wcc/v1/` — not the ordinary `/wp/v2/`, so the endpoint under it is the FIRST thing to measure and it is not established here. **TWO HOST FORMS, AND THEY ARE TWO HOSTS: the apex `inpa.gov.it` was fetched, and every internal link points at `www.inpa.gov.it`.** Both were guarded separately and both answer `state: read`, `certain: True`, with no refusal that names us and **no `Crawl-delay`**, so the 2 s of our own pace apply. *Guarding only the apex would have been the `gva.es` error by the other end: there a parent's refusal did not bind a child, and here a parent's permission does not either.* What the page does NOT establish: the listing path, its pagination, whether the REST namespace is readable without a token, and any count · 2026-10-06 -->
<!-- witness: none — the board states no count of its own that the adapter reads, so its 1 848 is its own extraction and nothing corroborates it. *The count fell from 1 915 on 2026-11-07 to 1 848 on 2026-11-09, which is what a sitemap tracking OPEN competitions does and is not a second source.* A count names a SIZE and never a NATURE: the shape was established by opening the first, median and last member of the sorted sitemap, and a fourth advertisement unseen when the adapter was written reads end to end · 2026-11-09 -->
<!-- witness: none — the root states no count; «concorsi» appears 52 times as prose and that is a word frequency, not an inventory · 2026-10-06 -->

## Measured 2026-10-06 under the declared identity, one guard per host

Opened under **#949**, tranche 1 — the five Italian public employment
services. *The owner opened the campaign by tranches on 2026-10-06, verbatim
« oui, ouvre #949 par tranches, commence par l'Italie ».*

**The guard was taken on each host form separately, in a turn distinct from the
retrieval, because `robots.txt` binds a HOST and not a brand.** *That is the
`gva.es` lesson: there a parent's refusal named five of our tokens and did not
bind its child; the same applies to a parent's PERMISSION.*

**No adapter is declared here, and that is the finding rather than an
omission** — what an adapter needs is named in the `content:` line above, and
the issue carries it as its reserve.
