# Board measurement — JobPosting (`www.jobposting.pro`): a multi-country white-label board — **its DECLARED sitemap enumerates 22 988 adverts and its paginated list carries 268 the sitemap does NOT, so neither enumerator contains the other and the board exceeds its own enumerator**; the pager prints a fixed eight pages whose seventh and eighth are the SAME empty body to the byte, every advert carries one platform-emitted `JobPosting` with the REAL employer in it, and the host states no count anywhere

<!-- verified: 2026-11-14 -->

<!-- hosts: www.jobposting.pro, jobposting.pro -->
<!-- script: jobposting.py -->
<!-- countries: FR PL -->
<!-- route: http · 23256 · 2026-11-14 -->
<!-- witness: none — the host states NO count anywhere. The 22 988 the declared sitemap yields is a count of OURS over rows it serves, not a figure the host asserts, and the paginated list carried 268 ids the sitemap lacks — so that number is an ENUMERATOR SIZE and a FLOOR, never a board total. The pager cannot help: it prints a constant eight pages, and `?p=7` and `?p=8` answer 200 with the same 9 263 B «Aucune offre en ce moment» body, md5 `b9b9e6cd4b49` on both · 2026-11-14 -->
<!-- content: measured · **NEITHER ENUMERATOR CONTAINS THE OTHER, and that is what decides the walk.** `/sitemap.xml` (200, 325 B) is an INDEX of two children, read and never composed; `/sitemap-offres.xml` (200, 2 873 607 B) holds **22 988 `<loc>`, 22 988 distinct, every one an advert**, with **68 distinct `lastmod`** — so that field is a real per-advert date and not a build stamp. The paginated list serves **4 000 distinct ids a page**: `/offres` 999 270 B, `?p=2` 1 005 294 B, `?p=3` 981 694 B. Crossed on MEMBERS and never on cardinals: **sitemap ∖ pages = 11 270, pages ∖ sitemap = 268, intersection 11 718** — and the 268 are the NEWEST adverts, ids from 2750294 upward, ALL on page 1, while `p2` and `p3` are both SUBSETS of the sitemap. So the sitemap lags the live list and the list does not reach the sitemap's tail. **THE PAGES ARE NOT STRICTLY DISJOINT**: `p1 ∩ p2 = 0` and `p1 ∩ p3 = 0` but **`p2 ∩ p3 = 14`**, so a reading of one pair would have concluded disjointness and an extractor trusting it would have double-counted fourteen adverts; 4 000 is a PAGE SIZE, not a plateau and not a total. **THE PAGER IS A TEMPLATE CONSTANT**: pages 1–3 are full, `?p=7` and `?p=8` are byte-identical empty bodies still printing «Page 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8», so `4 000 × 8` is not a total and where the content ends — somewhere in 4..6 — is NOT established and was not probed. **THE MARKUP IS THE PLATFORM'S, ESTABLISHED ON TWO EMPLOYERS**: each advert page carries exactly ONE `application/ld+json` `JobPosting` and the LIST carries none at all (raw or HTML-escaped), so a verdict of rendering taken on `/offres` says nothing about an advert page; `/emploi-2750653-1` (14 700 B, ISEC FORMATION OUEST, Le Port 97420 FR, INTERN) and `/emploi-2749564-1` (19 583 B, Algoteque, Warszawa 00-105 PL, CONTRACTOR) carry the SAME fourteen keys and `identifier.name` = `JobPosting.pro` on both. **AND `hiringOrganization.name` IS THE REAL EMPLOYER** — the opposite of `maliemploi`, where it held the board's own name on 5 of 5. Every advert page is at the EMPLOYER's own brand (`<title>` «… | Algoteque»), so it is a white-label career page and nothing outside the `JobPosting` block is read. `JobPosting.url` equals the page asked on 2 of 2 and is still TAKEN from the record. **NO `baseSalary` KEY EXISTS** on either advert, so nothing is emitted for pay. **CONTACTS: zero `mailto:`, zero `tel:`, zero e-mail in clear on both** — two specimens is not a census, so the redaction is theoretical on what was read, exercised in both directions by the suite, and `withheld_fields` is DERIVED from what was actually removed. **THE RULES FORBID NOTHING**: 71 B, one `*` group whose `Disallow:` has an EMPTY VALUE, `ignored_for` empty so no `Host:` directive, and the only `Sitemap:` on the SAME host — so the guard answers `allowed=True` on every path and the restriction is OURS: a POSITIVE floor of four requestable shapes, never a list of refusals · 2026-11-14 -->

## Measured 2026-11-14 — 22 988 declared, 268 the declaration misses, and a pager that prints a constant

```
robots.txt              71 o   md5 354f7d610479, read, certain, groupe *
  Disallow:                    valeur VIDE — group_for rend ('*', [''], [], [])
  Crawl-delay                  AUCUN  ->  la cadence est a NOUS (6 s posees ici)
  ignored_for                  []     ->  aucune directive Host: a ecarter
  sitemaps_for                 1, sur le MEME hote
/sitemap.xml           325 o   INDEX de 2 enfants, LUS et jamais composes
  sitemap-page.xml             0 annonce
  sitemap-offres.xml     2 873 607 o   22 988 <loc>, 22 988 distincts, TOUS des annonces
                                       68 lastmod DISTINCTS  ->  une vraie date par annonce
/offres                999 270 o  4 000 ids distincts
/offres?p=2          1 005 294 o  4 000 ids distincts
/offres?p=3            981 694 o  4 000 ids distincts
/offres?p=7            9 263 o   0 id   «Aucune offre en ce moment»  md5 b9b9e6cd4b49
/offres?p=8            9 263 o   0 id   MEME md5, MEME pager de huit
  ---- croises sur les MEMBRES, jamais sur les cardinaux ----
  sitemap \ pages       11 270
  pages   \ sitemap        268   <- les PLUS RECENTES, ids 2750294+, TOUTES sur p1
  intersection          11 718
  p1 n p2  0   p1 n p3  0   p2 n p3  14   <- les pages ne sont PAS disjointes
/emploi-2750653-1     14 700 o   1 JobPosting   ISEC FORMATION OUEST  Le Port 97420 FR
/emploi-2749564-1     19 583 o   1 JobPosting   Algoteque             Warszawa 00-105 PL
  memes 14 clefs, identifier.name = JobPosting.pro sur les deux
  baseSalary            ABSENTE de la clef sur les deux
  mailto: / tel: / courriel en clair       0 / 0 / 0 sur les deux
```

### Neither enumerator contains the other, and the direction is readable

**`p2` and `p3` are SUBSETS of the sitemap; `p1` is not.** *The 268 ids the sitemap lacks are
contiguous from 2750294 upward — the adverts published since its last regeneration.* **So the
asymmetry is not noise: the sitemap is a periodic snapshot and the list is live.**

> **The consequence is that there is no witness, in the sense this repository means.** *A count
> of rows in a file we fetched is OUR extraction; the host asserts no number anywhere, and the
> 268 exclusives prove the board exceeds the only enumeration it publishes.* **So a run states
> both sides and declares the size NOT established — and if one side ever became a superset of
> the other, the run's own line is what would say so.**

**Both are walked, and that is not redundancy for its own sake:** *either alone drops members
the other holds, and the union is the only honest answer.* **Each record names its own
enumerator (`list`, `sitemap`, `sitemap+list`), so a future divergence is visible in the run's
output instead of silent.**

### The pager prints a constant, so it cannot say where the content ends

**`?p=7` and `?p=8` answer 200 with the SAME 9 263 bytes, md5 `b9b9e6cd4b49`** — one «Aucune
offre en ce moment.» page that still prints «Page 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8».

| what one could read into it | what is measured |
| :-- | :-- |
| «eight pages × 4 000 = 32 000» | pages 7 and 8 are EMPTY; the eight is a template constant |
| «4 000 is a plateau or a cap» | it is a PAGE SIZE: three pages give 4 000 each |
| «the pages partition the board» | `p2 ∩ p3 = 14` — they overlap, so the walk deduplicates |

**Where the content actually stops, in pages 4..6, is NOT established and was not probed.** *Three
more megabytes would not have changed the design: the stop condition is a page with zero ids, and
that is the only one available.*

### `p2 ∩ p3 = 14` — one pair would have concluded disjointness

**The first two pairs read gave an intersection of ZERO, and the third gave fourteen.** *A sample
where two models coincide decides nothing: had only `p1`/`p2` been read, «the pages are disjoint»
would have been written down and an extractor built on it would have double-counted — a plausible
number and only false.*

### The markup is the platform's, and that is established on two employers rather than one

**Same fourteen keys, two employers, two countries, and `identifier.name` = `JobPosting.pro` on
both** — the platform emits the block, which is why it is consistent across white-label pages.

```
@context @type title description url datePosted validThrough employmentType
directApply educationRequirements experienceRequirements hiringOrganization
jobLocation identifier
```

**`experienceRequirements.monthsOfExperience` is FILLED and discriminates** — 1 against 60 on the
two — and it is read with a floor on the VALUE, because `if x` would also swallow a legitimate 0.
*`educationRequirements.credentialCategory` is present on both.* **`baseSalary` is ABSENT from the
key set**, so nothing is emitted for pay rather than a currency being guessed.

> **Still two adverts and not a census.** *A shared gabarit predicts the ROUTE and never the
> ANALYSE, so every field is read defensively and a missing one is ABSENT rather than invented.*

### No `language` is emitted, and that is a decision

**The two adverts read are in FRENCH and POLISH, nothing in the markup declares a language, and
`addressCountry` is a country and not a tongue.** *A field derived from the country would be wrong
on the first advert written in English for a French employer.*

### What the rules permit is not what is ours to take

**71 bytes, one `*` group, `Disallow:` with an empty value — this host forbids NOTHING**, so the
guard answers `allowed=True` on `/`, `/offres`, `/offres?p=N`, `/emploi-<N>-1`, `/sitemap.xml`,
`/sitemap-offres.xml` and `/sitemap-page.xml` alike.

> *The Tajik board where 34 894 of 42 851 `<loc>` were real people's CVs sat behind a 105-byte
> file with no `Disallow` at all.* **A list of forbidden paths bets that the problem has been
> enumerated; a POSITIVE floor bets nothing.**

**Only four SHAPES are ever requested** — `/offres`, `/offres?p=N`, `/emploi-<N>-1`,
`/sitemap*.xml` and `/robots.txt` — *so the client area, and any account or applicant path this
board may grow, are refused by construction and not by an enumeration anyone must keep current.*

### The id motif was false by its FORM, and only a disagreement showed it

**A first version of the adapter anchored the id on `(?:[/?#]|$)` and rendered ZERO on the
list** — the address there is followed by the APOSTROPHE closing the `href` attribute — *while
still rendering 22 988 from the sitemap, because there the match is taken on the PARSED path,
which ends the string.*

```
/emploi-(\d+)-1(?:[/?#]|$)    liste 0       sitemap (chemin parse) 22 988
/emploi-(\d+)-1(?!\d)         liste 4 000   sitemap 22 988        <- et refuse -10, -11, -2
```

> **The run was perfectly well formed: «page 1 carries ZERO advert ids», the walk stopped, and
> three records came out of the sitemap.** *A zero that affirms instead of missing.* **Nothing
> caught it by reading; what caught it is that the adapter's anchored motif DISAGREED with a
> hand-rolled one on the same held bytes, 0 against 4 000.**

### What the adapter does

```
route   : http — no key, no account, no form.
RATE    : none written for any agent, so 6 s are OURS.
walk    : the DECLARED sitemap index -> its children -> the adverts they name,
          PLUS the paginated list, default ONE page (p1 is the fresh head the
          sitemap lacks). Stops on a page with zero ids. Union, DEDUPLICATED,
          each record naming its enumerator.
witness : none. The run prints the sitemap's row count AND the ids the list
          carried beyond it, and declares the size NOT established.
address : TAKEN from `JobPosting.url` (equal to the page asked on 2 of 2).
carries : title, employer (REAL here), city, postal_code, country PER RECORD
          (FR and PL read), published, valid_through, employment_type,
          direct_apply, months_of_experience (floored on the VALUE), text.
NEVER   : anything outside the four requestable shapes; no pay field, since no
          `baseSalary` key exists; no `language`, since nothing declares one.
```

### What this card does NOT say, and the three reserves that stay open

**It does not say where the content stops.** *Pages 1–3 are full and 7–8 are the same empty body;
pages 4, 5 and 6 were NOT probed, and three more megabytes would not have changed the design —
the stop condition is a page with zero ids and that is the only one available.*

**It does not say what a SEARCH on this board looks like.** *No search URL form was observed at
all: only the paginated list and the declared sitemap were walked, so this board is reachable by
ENUMERATION and not by query.* **An adapter that needed to filter before fetching would have to
measure that form first, and nothing here establishes it exists.**

**It does not say the redaction has ever fired on this host.** *Zero `mailto:`, zero `tel:` and
zero e-mail in clear on the two adverts read — two specimens is not a census, so the rule is
exercised by the suite in both directions and not by this board.* **A field PRESENT is not a
field FILLED, and `withheld_fields` is derived from what was actually removed.**

**Measured 2026-11-14 by the declared client, the guard taken on every exact path in a turn
distinct from the retrieval, `bin/fetch-body.py` throughout with provenance kept, and the adapter
RUN end to end — `ad --id 2750653` and `list --max 3 --pages 1`, whose own output reproduced the
4 000, the 22 988 and the 268 independently of the held bodies.**
