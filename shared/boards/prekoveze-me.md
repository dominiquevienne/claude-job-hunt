# Assessed, adapter not built — Prekoveze.me (Montenegro)

<!-- verified: 2026-09-08 -->

<!-- hosts: prekoveze.me -->
<!-- script: none -->
<!-- countries: ME -->
<!-- content: measured · 243 advertisements under `/posao/` in `sitemap/oglasi.xml`, raw 243 / distinct 243, 0 duplicates, across 113 employers; 21 distinct `<lastmod>` from 2026-07-08 to 2026-09-07 · 2026-09-08 -->
<!-- witness: none found — no site-served total was read here · 2026-09-08 -->
<!-- overlap: zaposli-me.md · 37 advertisements share an employer AND a title slug; zaposli holds 423 and prekoveze 243 · 2026-09-08 -->

**Montenegro's second current stock, and the same URL scheme as its neighbour
under a different theme.**

## The same skeleton, and it is not the same site

```
prekoveze.me/sitemap.xml -> /sitemap/oglasi.xml   +  /sitemap/pretrage.xml
zaposli.me/sitemap.xml   -> /sitemap/oglasi.xml   +  /sitemap/pretrage.xml
both serve ads at        /posao/<id>/<employer>/<title>
```

**But the markup differs, and `zaposli.py`'s anchors return `None` on three of
three pages here.**

```
zaposli      two <h1> (the first a banner) · `mdi-` icons · "10. septembar 2026."
prekoveze    ONE <h1>, the real title      · no `mdi-`   · "10.9.2026."
```

> **Same platform skeleton, different theme and different date format.** *An
> adapter written for one does not read the other, and the resemblance of the
> sitemaps is exactly what would make someone assume it does.*

**No adapter is built here tonight** — it needs its own four anchors and a
numeric date parser, and that is a session's work rather than a reuse.

## The overlap is measured, and the identifiers are NOT comparable

**The two boards number their advertisements independently:**

```
zaposli    ids around 105 000 – 107 000
prekoveze  ids around  51 000
```

**Disjoint ranges are per-board sequences, so joining on the id returns zero by
construction.** *That mistake was made and caught here: a first extractor keyed
on the id and reported an empty intersection — the shape of a finding, produced
by the key.*

**The fallback key is `(employer slug, title slug)`, and its limit was measured
INSIDE each board first:**

```
zaposli    338 distinct title slugs for 423 ads — `prodavac-mž` carried by 14
prekoveze  192 distinct title slugs for 243 ads — `kuvar-mž` carried by 3
composite  411 distinct of 423, and 225 of 243: still 8 and 9 collisions
```

**A title slug is not an identifier even within one board**, so the composite is
a candidate key and not a proof of identity — *and this card says so rather than
publishing 37 as a count of duplicates.*

### The candidates were opened, three of three

```
                 titre                            ville       echeance
paire 1  zaposli Prodavac (m/ž)                   Podgorica   18. septembar
       prekoveze Prodavac (m/ž)                   Podgorica   11.9.2026
paire 2  zaposli Supervizor za ljudske resurse    Budva       10. septembar
       prekoveze Supervizor za ljudske resurse    Budva       10.9.2026
paire 3  zaposli Terenski komercijalista          —           18. septembar
       prekoveze Terenski komercijalista          —           18.9.2026
```

**Same title, same employer, same city where a city is given — and two of three
carry the SAME deadline to the day.** *So these are the same advertisements
published on both boards, and the numeric date on this side is the same
quantity as the spelled-out one on the other.*

**Pair 1 differs by a week**, which is why the third field mattered: *a
duplicate is established by employer, title and city agreeing, not by the date,
which the two publishers set independently.*

### The four numbers, and the asymmetry that one number would hide

```
|zaposli| = 423     |prekoveze| = 243     shared = 37     union <= 629
9 % of zaposli                            15 % of prekoveze
```

> **Adding the two boards would claim 666 advertisements for Montenegro where
> at most 629 exist.** *And the smaller board shares a sixth of its inventory
> while the larger shares under a tenth — a single overlap figure hides which
> way the dependence runs.*

## What this card does not establish

- **the 37 were not all opened** — three were, and the other 34 are candidates
  on a key with measured collisions;
- **no rate**, and no reading of this board's own totals;
- **nothing about `berzarada.me`**, Montenegro's third named host, whose
  `robots.txt` is an HTML error page on both forms.
