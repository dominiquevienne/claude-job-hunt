# Board measurement — Gi Group (`www.gigroup.it`, Italy): the root is served and links 397 vacancies by itself

<!-- verified: 2026-10-06 -->

<!-- hosts: www.gigroup.it, gigroup.it -->
<!-- script: none -->
<!-- countries: IT -->
<!-- content: measured · read 2026-10-06 — the root answers 200 with 497 590 B and 23 177 characters of text OUTSIDE any script, so it is server-rendered; it carries 669 `href` of which 397 sit under `/offerte-lavoro`, one `application/ld+json` block and an `@graph` key, meaning any check posed at the JSON top level would read NOTHING · 2026-10-06 -->
<!-- witness: none measured — no board-stated total was read, and 397 is a count of links ON THE ROOT and not a count of the board · 2026-10-06 -->

## Measured 2026-10-06 — 397 advert links on the root, and the structure is nested


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
www.gigroup.it/      200   497 590 B   md5 97a854cb674d
texte hors <script>/<style>        23 177 caracteres      -> servi, pas une coquille
href                               669
  /offerte-lavoro                  397      <- le chemin d'annonce
  /lavoro 9 · /orientamento 8 · /offerte-formazione 4 · /formazione 2
application/ld+json   1       @graph   1
```

**THE `@graph` KEY IS THE TRAP AND IT IS WHY IT IS RECORDED HERE.** *On
`somon-tj.md`, measured the day before, the single `ld+json` block had exactly two
top-level keys — `@context` and `@graph` — so reading `@type` at the top level
returned nothing and a check posed there would publish «this page carries no
`JobPosting`».* **The shared reader `_ldjson.postings()` finds it in all three
forms; the hazard is in a hand-written check.** *This card does NOT claim a
`JobPosting` is present: the block was not parsed, only its keys counted.*

## What is NOT established

- **No advert page was fetched**, so the per-advert shape is unread.
- **397 is a link count on ONE page, not the size of the board.** No total was read
  from the site, and `/offerte-lavoro` may paginate or may be a facet.
- **Whether `/offerte-lavoro` enumerates or filters is unknown** — a path prefix
  reads like a NATURE and is not one.
