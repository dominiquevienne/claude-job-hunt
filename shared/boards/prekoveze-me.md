# Board adapter — Prekoveze.me (Montenegro)

<!-- verified: 2026-09-08 -->

<!-- hosts: prekoveze.me -->
<!-- script: prekoveze.py -->
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

**Built 2026-09-08, and it needed every one of those things**: its own five
anchors, a numeric date parser, and a second reading of the deadline to check
the first. See *The adapter, and what running it on all 243 established* below.

```bash
S=skills/job-scan/scripts/prekoveze.py
python3 $S list --limit 5
python3 $S list --fetch                  # 243 requests, one a second
python3 $S ad --url https://prekoveze.me/posao/51173/trademax/asistent-u-prodaji-mž
```

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

## The adapter, and what running it on all 243 established

**`prekoveze.py list --fetch`, 2026-09-08, every advertisement in the sitemap:**

```
sitemap_entries 243   read 243   kept 243
unreadable        0   incomplete  0   deadline_disagreements 0
113 employers · 53 place names · deadlines 2026-09-08 -> 2026-10-31
```

**None of the 243 deadlines is in the past.** *So this is a current stock and
not an archive — the card said so from the sitemap's date range, and reading
every advertisement confirms it from the other end.*

### Two ways this board hands out a wrong value, and neither returns a blank

**They belong together: both fail by producing something plausible.** *An
extractor that returns nothing gets noticed. These return a value on every
advertisement.*

**① The visible cell is truncated and the tooltip is not.** A category renders
as `Administracija, Nekr&hellip;` while `data-original-title` carries
`Kategorije: Administracija, Nekretnine, Prodaja`. **Reading the link text
returns a silently shortened string, never an empty one.** *One advertisement
gives `Podgorica, Budva, Radanovići` as its place; the visible text cuts it
after the first, and «&nbsp;Podgorica&nbsp;» is a perfectly ordinary answer.*

**② The `ld+json` is not missing data — it is wrong data.** There are two
blocks and neither is a `JobPosting`: an `Organization` and a `WebSite`.
**Their `addressLocality` is `Podgorica` on every advertisement, including the
ones in Bar and Budva** — it is the publisher's own office.

> **An extractor that asks «&nbsp;is there `ld+json`?&nbsp;» instead of
> «&nbsp;is there a `JobPosting`?&nbsp;» fills the town field with the
> publisher's address on all 243.** *A user would apply to Podgorica for a post
> in Budva, and nothing in the output would look wrong.*

**So every field here is read from the tooltip, and the structured data is
read for nothing.**

### The anchors

```
title       <h1>                     one per page, and it IS the title
employer    global.firma = "…"       a JS global, not markup
deadline    fas fa-calendar-alt      22.9.2026.
   and      <meta name="googlebot" content="unavailable_after: 2026-09-22">
town        data-original-title="Mjesta: …"
categories  data-original-title="Kategorije: …"
```

**The deadline has two independent sources, so the adapter parses both and
names every disagreement.** *A `d.m.yyyy` is exactly the format where a day and
a month swap without producing anything invalid.* **They agreed on 243 of 243**,
and the line saying so prints whether or not anything failed.

### 86 % of the addresses cannot be sent as written

```
243 URLs in the sitemap
210 non-ASCII                 = 86 %
```

**Without `wire_url`, `urllib` raises on 210 of 243.** *The neighbouring board
lost 87 % to exactly this defect the day before, which is why the encoder now
lives in `_robots` beside `full_path` rather than at each call site.*

### `zaposli.py` does not read this board, checked in both directions

```
its four anchors on three prekoveze advertisements   0 · 0 · 0 · 0
the same four on one zaposli advertisement           all four fields
```

*The negative alone would have proved only that the test was wrong.*

### What `--since` cannot say here

**This board publishes no posting date — a deadline and nothing else, on 243
of 243.** So the sitemap's `<lastmod>` has nothing on the page to be checked
against. `--since` filters on it and **prints that limitation every time**.
*On `zaposli.me` the same filter is honest because `lastmod` was compared to
the site's own posting date on ten advertisements. The difference between the
two boards is evidence, not carelessness.*
