# Board adapter — Emploitic (Algeria)

<!-- verified: 2026-09-03 -->
<!-- hosts: emploitic.com, www.emploitic.com -->
<!-- script: emploitic.py -->

Algeria's largest private job board. **No key, no cookie, no browser.**

```
GET /robots.txt        → Sitemap: https://emploitic.com/sitemap.xml
GET /sitemap-jobs.xml  → 4 506 <loc>, every one an advertisement
GET <ad url>           → one JobPosting, plus __NEXT_DATA__
```

`robots.txt` refuses one path family — `/partenaires/` — and nothing else.

## The sitemap is the route here, and it is declared

**The operator names it in its own rules file**, which is the most explicit
permission there is, and it is current to the minute: newest `lastmod`
**2026-09-03T20:37**, minutes before this was written.

**Read `jobivoire.md` beside this.** Its board publishes a sitemap too and it
is five weeks stale — 227 advertisements of 3 884 — so that adapter paginates
instead. **Two neighbouring boards, two opposite routes, each measured.
Carrying the habit of one to the other is the only real risk in the pair.**

## Both URL shapes are advertisements, and that was checked

```
/offres-d-emploi/<sector>/<slug>                          977
/entreprises/<company>/offres-d-emploi/<sector>/<slug>   3 530
```

The second reads like an employer landing page. **It is not** — three sampled
across the range each carry exactly one `JobPosting`. **Counting only the
first shape would have reported a board a fifth of its size**, which is
`hr.ge`'s mistake in the other direction, where 39 247 `<loc>` held 1 062 ads.

## Titles are not always plain text

One employer publishes `𝗧𝗲𝗰𝗵𝗻𝗶𝗰𝗼 𝗰𝗼𝗺𝗺𝗲𝗿𝗰𝗶𝗮𝗹` in mathematical-bold Unicode.
A reader cannot tell; **a keyword match against `Technico` fails.** The title
is emitted as published and flagged `title_is_styled_unicode`, never
normalised in place.

**The first draft of that check used `NFKD` and reported 2 of 2.** `NFKD`
decomposes every French accent, so `Chargé(e) Administration…` came back
styled. **A check that fires on everything is not a check.** `NFKC` composes
the accents back and still folds the mathematical alphabets to ASCII.

## Cost

One request for the sitemap, then **one request per advertisement** — the
sitemap carries URLs and the fields live on the page. `sitemap` returns the
URLs alone for a cheap count.
