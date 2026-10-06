# Board measurement — Randstad Italy (`www.randstad.it`): the sitemap index the delivered adapter requires answers 404

<!-- verified: 2026-10-06 -->

<!-- hosts: www.randstad.it, randstad.it -->
<!-- script: none -->
<!-- countries: IT -->
<!-- content: measured · read 2026-10-06 — `/sitemaps/sitemap.xml`, the index that `randstadfr.py` reads on its three known fronts, answers 404 on this host, so Italy is NOT the same route; the rules are read and open on both host forms with no rule touching our paths, and `randstadfr.py` refuses this country before any request, so the route here is UNESTABLISHED and not merely unwritten · 2026-10-06 -->
<!-- witness: the FR front answers the SAME `sitemaps_for()` emptiness as this one, so that instrument cannot separate them and is not used as evidence here · 2026-10-06 -->

## Measured 2026-10-06 — the same question as Adecco, the opposite answer


Opened under **#949**, tranche 3 — the Italian staffing agencies, the ATS and the
sector board. *The owner opened the campaign by tranches on 2026-10-06, verbatim
« oui, ouvre #949 par tranches, commence par l'Italie ».*

**The guard was taken on EVERY host form separately, in a turn DISTINCT from the
retrieval, because `robots.txt` binds a HOST and not a brand.** Eleven forms were
guarded across this tranche; nine answered `state: read` and two `unrecognised`,
all open, **and not one carries a `Crawl-delay`** — so the pace is ours, and an
absent delay is not an absence of rate limiting. *Retrieval through
`bin/fetch-body.py` under the declared identity, provenance written beside each
body.* No contact value is reproduced anywhere below; counts only.

```
www.randstad.it/sitemaps/sitemap.xml    404    146 310 B, NOT saved
   (`fetch-body.py` exits on a non-2xx before writing: a readable body is not an answer)
use_board('it') / ('www.randstad.it') / ('IT')   -> REFUSED, SystemExit 2
   « not a front of this platform — fr (www.randstad.fr), cz, hu »
```

**AND ONE INSTRUMENT FINDING THAT KEPT A FALSE NEGATIVE OUT OF THIS CARD.**
*`sitemaps_for('www.randstad.it')` returns `[]` — and so does
`sitemaps_for('www.randstad.fr')`, **the front the adapter reads successfully every
day via that very index**.* **So `[]` is the same answer for the working front and
for the unknown one, and it proves nothing.** *Without the FR control it would have
become «this host declares no sitemap», which reads like a fact.*

> **The control was to ask the instrument about an object whose answer we already
> know.** *A zero that affirms instead of missing — and here the comparison, not a
> re-reading, is what caught it.*

**WHAT THIS PAIR ESTABLISHES, BECAUSE IT WAS MEASURED TOGETHER.** Adecco Italy was
a one-line table entry; Randstad Italy is not. *Same tranche, same country, same
«a sibling front already works» premise, opposite answers* — which is the point
already recorded for Hays FR→ES (a PARAMETER) against Randstad CH→ES (a REWRITE).
**«It is already covered elsewhere» predicts nothing.**

## What is NOT established

The Italian route itself. **Nothing says Randstad Italy has no sitemap** — only
that it is not at the FR path and not declared in `robots.txt`, which the FR
control shows is normal for this brand. A root reading and a search path remain.
