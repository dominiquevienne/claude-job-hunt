# #195 — what the 186 country pages actually are, counted

**Counted 2026-09-08 by `claude-job-hunt-82`. Two denominators, and they are not
the same: 186 COUNTRIES and 143 distinct ARTEFACTS.** *A count of pages and a
count of countries differ here by 43, and quoting either as "the pages" is
wrong.*

## The partition, computed without opening a single artefact

```
source   ~/.claude/projects/…/atlas-pages.txt, column 4
command  collections.Counter(url for each of the 186 rows)

186 countries · 143 distinct URLs
135 countries hold a URL of their own
 51 countries share 8 URLs
control  135 + 51 = 186
```

**Under the owner's decision of 2026-09-08 — one page per country, boards
repeating across pages — a page serving seventeen countries cannot be the page
of any of them.** *So those 51 need a page written, and that is established on
an external sign with no artefact read at all.*

```
17  Onze prédictions, onze réfutations     AFG BRN BTN CHN CYN IRN LAO LBN MMR
                                           MNG PRK PSE SYR TJK TKM TLS YEM
 9  Le gabarit, pas le pays                DJI ERI ESH GNB GNQ LBY MRT NER TCD
 8  Neuf le même jour                      LSO MOZ MWI NAM SOM SWZ TUN ZWE
 5  Cinq pays couverts, non mesurés        BOL HND PRY URY VEN
 4  Quatre pays, un seul fichier de refus  BDI BWA CAF COG
 3  Bahamas, Porto Rico, Suriname          BHS PRI SUR
 3  (title not obtained)                   BHR KWT OMN
 2  Boards d'emploi — Salomon et Vanuatu   SLB VUT
```

**The 51 are not uniform work.** *Seven of those eight are transversals with no
country in the title. The eighth is a deliberately two-country PAGE — it needs
splitting, not writing.*

## The sample, declared before it was drawn

```
frame   the 135 countries holding their own URL
seed    195, python random.sample
drawn   BEN CHE GRC GTM LTU PNG
variable  A   the four canonical columns are present
          B   a per-board table exists under other headings
          C'  no per-board table at all
```

**Result: A = 3 · B = 2 · C′ = 1, of 6.**

```
CHE  A   Board · Ce qu'il couvre · Accès · Statut  — present, three times over
GRC  A   idem
LTU  A   idem
BEN  B   Témoin · Rend · Lieu · Annonces · Nature · Pays — no canonical column
PNG  B   Rang · Hôte · Garde · Ce qui répond
GTM  C'  Capitale · Forme anglaise · Forme espagnole · Part anglaise · Source
```

**Six pages cannot establish a rate**: 3/6 leaves the true share of A wide. *The
draw dimensions the work; it does not conclude it, and #195 is a census — all
186 will be opened anyway.*

## Two corrections this count produced, both of claims I had already sent

**"Bucket A may be empty" was wrong.** *It rested on ONE page, Angola, whose
FIRST table carries `Board` without the other three columns.* **Angola has 13
headers across four tables and I had looked at five of them.** *Read whole, it
is B — and three of the six drawn are A.* **The error was not the reading; it
was generalising a bucket from a single page.**

**"About ten thousand tokens of preamble per artefact read" was an estimate
offered as a measurement.** *Measured since, on thirteen saved artefacts: the
`frame-runtime` block is **13 908 bytes, byte-identical in all thirteen** — a
fixed cost per read, between 27 % and 53 % of each file.* **The body does not
cross the context: the tool saves the full HTML locally and prints a bounded
head.** *So the real per-read cost is roughly half what I reported, and the
campaign is correspondingly cheaper.*

## What is not established

**A title is not a bucket.** *`Boards d'emploi — Bénin` does not exist: BEN's own
page is titled `Cinquante-deux, quatre fois` and is a transversal by title yet
carries a per-board table.* **Sole-URL pages include transversals**, so the 135
are not all country pages, and the 51 are a floor for the writing work rather
than its total.

**`Artifact action=list` is capped at 50 and its ordering is unknown.** *It is
demonstrably not ordered by the `updated` date it prints — the first row is
2026-09-01 and the second 2026-09-08.* **A sample drawn inside that listing has
a bias that cannot be described, so the draw above was made in the 135, never in
the 41 titles the listing returned.**
