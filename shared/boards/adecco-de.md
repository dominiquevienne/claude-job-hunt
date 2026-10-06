# Board measurement — Adecco Germany (`www.adecco.de`): the country-sitemap pattern that works for France, Norway, Finland and Italy does NOT extend here

<!-- verified: 2026-10-07 -->

<!-- hosts: www.adecco.de, adecco.de -->
<!-- script: none -->
<!-- countries: DE -->
<!-- content: measured · read 2026-10-06 — both host forms answer as `www.adecco.com`, the very host the French, Norwegian, Finnish and Italian fronts live on, so the pattern `sitemap-jobs-<country>-<lang>.xml` was the obvious candidate and it is REFUTED: `/sitemap-jobs-germany-de.xml` answers 404 with 146 B. the rules that govern both forms were read from `www.adecco.com` — the tool says so itself, the bare form being redirected — and they are open with no rule touching our paths and no `Crawl-delay`, and `adecco.py` refuses this country before any request in four spellings, so the German route is UNESTABLISHED rather than merely unwritten · 2026-10-07 -->
<!-- witness: none — nothing was counted on this host, and the 404 is a statement about ONE guessed path and never about what the board publishes · 2026-10-07 -->

## Measured 2026-10-06 — the guess that worked for Italy fails here

Opened under **#949**, first German tranche. *The campaign runs by tranches on the
owner's word of 2026-10-06, verbatim « oui, ouvre #949 par tranches, commence par
l'Italie » — Italy is finished and the country was chosen by MEASURING the gap
«hosts named on the page minus hosts carded», not by judgement.*

**Every host form was guarded SEPARATELY in a turn distinct from the retrieval,
because `robots.txt` binds a HOST and not a brand** — 28 forms across this tranche,
**26 open and 2 refused in writing**. *Retrieval through `bin/fetch-body.py` under
the declared identity, provenance written beside each body.* No contact value is
reproduced below; counts only.

```
adecco.de  et  www.adecco.de        repondent comme  www.adecco.com   (state: read, ouvert)
www.adecco.com/sitemap-jobs-germany-de.xml      404, 146 o, NON enregistre
use_board('de'|'DE'|'www.adecco.de'|'germany')  -> REFUSE, SystemExit 2
```

**THE SAME GUESS SUCCEEDED IN ITALY THE DAY BEFORE** — `sitemap-jobs-italy-it.xml`
answered 200 with 6 260 distinct adverts, and the Italian front became a one-line
table entry. *Here the identical reasoning, on the identical host, returns 404.*

> **A naming pattern confirmed on four fronts is still a guess on the fifth.** *And
> the cheapness of the guess is exactly what makes it tempting to call a rule.*

**Pair this with `randstad-de.md`, measured in the same tranche**: Randstad answered
**200** in Germany where it answered 404 in Italy, and Adecco answered **404** in
Germany where it answered 200 in Italy. **The pair INVERTS between the two
countries, so «it is already covered elsewhere» predicts nothing in either
direction.**

## What is NOT established

**The German route.** Nothing says Adecco Germany has no sitemap — only that it is
not at the name the other four fronts use. *Unlooked-at: `www.adecco.com/sitemap.xml`
(guarded, open, not fetched), what `adecco.de` serves at its root, and whether the
German offering lives under a `/de-de/` path as Italy's lives under `/it-it/`.*
