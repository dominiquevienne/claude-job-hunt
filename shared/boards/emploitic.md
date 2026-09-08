# Board adapter — Emploitic (Algeria)

<!-- verified: 2026-09-08 -->
<!-- hosts: emploitic.com, www.emploitic.com -->
<!-- siblings: emploitic.com 2026-09-04 agree -->
<!-- script: emploitic.py -->
<!-- countries: DZ -->
<!-- content: measured · 4 237 advertisements — every `<loc>` of `sitemap-jobs.xml`, and the adapter's output is SET-IDENTICAL to the raw file (0 in the sitemap and not returned, 0 returned and not in the sitemap); the tool's own partition sums to it, 890 under `/offres-d-emploi/` + 3 347 under `/entreprises/<company>/offres-d-emploi/` = 4 237 · 2026-09-08 -->
<!-- witness: 4 237, and the adapter was RUN rather than read — both halves of the route, the listing and one advertisement, which returned company, title, region, employment_type and valid_through · 2026-09-08 -->

Algeria's largest private job board. **No key, no cookie, no browser.**

```
GET /robots.txt        → Sitemap: https://emploitic.com/sitemap.xml
GET /sitemap-jobs.xml  → 4 237 <loc>, every one an advertisement (2026-09-08;
                             4 506 on 2026-09-03 — the board lost 269 in five days)
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


## 2026-09-08 — exercised for the first time, and it works

**This card carried a `script:` and had never been run.** *Exercising it means
launching it, not re-reading it, and the result is that the adapter is sound:*

```
emploitic.py sitemap        4 237 advertisement URLs, all distinct
emploitic.py ad --url ...   company · title · region · employment_type
                            valid_through · posted · location_text
```

**The count was checked against the file rather than trusted.** *`sitemap-jobs.xml`
fetched directly holds **4 237** `<loc>`, all distinct, and the two sets are
identical:* **0 URLs in the sitemap that the tool drops, 0 the tool returns that
the sitemap lacks.** *Compared as sets and not as totals — two counts that agree
can still describe different members.*

**The tool states a partition — `890 + 3 347 = 4 237` — and an earlier version
of this card called it "the count that does not come from re-reading its
output". That was wrong.** *`emploitic.py:156` prints
`note(f"{len(urls)} advertisement URL(s): {direct} under …")`: all three numbers
are `len()` of the same extraction.* **A partition of one's own output is an
arithmetic identity, not a second source** — it cannot fail while the extraction
fails.

**What IS a second source here is the check made in this card and not by the
tool**: `sitemap-jobs.xml` fetched directly, 4 237 `<loc>`, set-identical to the
adapter's output. *That is external, and it lives in this file rather than in
the adapter* — **so `emploitic.py` is nude at the list level: if its reader
broke, 4 237 and 0 would be two outputs of one instrument.** (#181)

### The board lost 269 advertisements in five days

**4 506 on 2026-09-03, 4 237 on 2026-09-08.** *Both are counts of `<loc>` in the
same file by the same method, so the grandeur is the same one and the drop is
the board's, not ours.* **Corrected in this card and in
`emploitic.py`'s docstring in the same pass** — *a figure fixed in the card
alone leaves the module's own copy contradicting it, and a docstring is visible
only from inside its module.*

**The date on this card moved because it was exercised.** *It stayed at
2026-09-03 for five days while the adapter had never been launched, which was
the honest record at the time: an unexercised card that keeps its date is the
one place where "nobody looked" stays legible.*
