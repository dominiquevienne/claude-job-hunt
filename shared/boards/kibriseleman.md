# Board measurement — Kıbrıs Eleman (`www.kibriseleman.com`, Northern Cyprus): «Kuzey Kıbrıs'ın en büyük eleman platformu» — **the live list holds 8 adverts and the undeclared sitemap holds 3042 that are DISJOINT from them and frozen at 2023-02-28**, the fifth board of five whose two enumerators were compared and the first where they share nothing at all; the city filter is inert; no advert page states any date; **the `Maaş` row is COMMENTED OUT in the template, so the board publishes no salary at all** — a correction of this card's own 2026-10-02 reading, which had read a comment as content; `kibriseleman.py` reads the live listing

<!-- verified: 2026-10-02 -->

<!-- hosts: www.kibriseleman.com -->
<!-- script: kibriseleman.py -->
<!-- countries: CYN -->
<!-- content: measured · **THE LIVE LIST HOLDS 8 ADVERTS: `/is-ilanlari` (200 ×2, 177 486 B, md5 bb4a3db56b61 / 4a79273347b9 at constant size — a rendered element moves, so NO md5 comparison means anything here) lists 8 distinct `/is-ilani/<id>-<slug>.html`, ids 4489-4500. The six city facets `?city=1` … `?city=6` are INERT: each returns the SAME 8 ids at the SAME 177 486 B. `?sayfa=2` is ignored (same 8); `?page=2` serves a different page (168 771 B) carrying ZERO adverts. `/sitemap.xml` (200, 675 998 B) carries 3 065 `<loc>` of which 3 042 advert ids, range 2-4407, and `lastmod` max **2023-02-28** (2 705 of them in 2023-02) — the two id ranges DO NOT OVERLAP, intersection 0. Both an advert from the live list and one from the sitemap answer 200, carry NO `ld+json`, NO microdata and NO date of any kind; the fields live in one HTML table whose LIVE rows are `Cinsiyet`, `Yaş`, `Sektör/Bölüm/Pozisyon` and `Alınacak Kişi`; the `Maaş` row is inside an HTML COMMENT (each page carries 12 comments, ~8 500 B, a quarter of the page), so the board publishes NO salary The rules file is served (`state: read`, `certain: True`) on `/`, `/is-ilanlari`, `/sitemap.xml` and an advert path, group `*`, and writes NO Crawl-delay — 2 s are ours; it declares NO sitemap, and `/sitemap.xml` is served all the same.** · 2026-10-02 -->
<!-- content: measured · **`/is-ilanlari` (200, 179 916 B, md5 2c76e654978e / 017e734d7aa4 — a rendered element moves) lists 10 distinct ads as `/is-ilani/<id>-<slug>.html` with a city filter `?city=1` … `?city=6` and «tüm ilanları gör» links; no count («binlerce ilan» is prose), no pager link on page 1, no JobPosting; `_robots.allowed('www.kibriseleman.com','/is-ilanlari')` → open, certain** · 2026-09-18 -->
<!-- witness: no count stated anywhere; the live list enumerates 8 and the sitemap 3042, and the two sets are DISJOINT, so neither is a witness for the other · 2026-10-02 -->

<!-- witness: none — the list states no count · 2026-09-18 -->

## Re-measured 2026-10-02 — 8 live adverts, and 3042 in an archive that shares none of them

```
/is-ilanlari             8 ids     4489-4500     aucune date sur la page
?city=1 .. ?city=6       8 ids     INERTES       memes ids, MEME taille a l'octet
?sayfa=2                 8 ids     ignore
?page=2                  0 annonce                 autre page, aucune annonce
/sitemap.xml          3042 ids     2-4407        lastmod <= 2023-02-28
INTERSECTION             0         les plages ne se chevauchent meme pas
```

**This is the fifth board in five days whose two enumerators were compared, and the first where
they share NOTHING.** *Lambda 50/30 intersecting in 2 (#661), İş Kıbrıs 12/12 in 6 (#719), Work
Link 12/20 in 4 (#722), Ekonomi Kıbrıs 21 ⊂ 50 (#726)* — **and here 8 against 3042 with an
intersection of zero.** The relation is not merely unpredictable in both directions: *it can be
EMPTY.*

> **And the stale side is 380 times the live one.** A union would turn 8 current vacancies into
> 3 050 rows of which **99.7 % are three and a half years dead** — and **nothing on those pages
> would contradict it**, because no advert page carries a date at all.

**The disjointness is not a namespace difference, it is a TIME gap**: the sitemap stops at id
4407 and the live list starts at 4489. *The sitemap is an artefact frozen in February 2023 that
is still served, and its entries still answer 200.*

### The prose is right and the front page is right, and they describe different things

The site calls itself «Kuzey Kıbrıs'ın en büyük eleman platformu» and writes «binlerce ilan» —
thousands. **The 18.09 reading found 10 adverts and recorded the prose as unsupported.** *Both
readings were correct about what they measured.* **The sitemap settles it: the board DID hold
thousands, and it currently lists 8.**

> **A board that looks tiny through its own front page can be large through its sitemap — and
> large in the past tense.** *«Dormant with a big archive» and «small» are indistinguishable from
> the listing alone, and the first is what this is.*

### Serving is not being current, and this board gives no other signal

**An advert from the live list and an advert from the 2023 sitemap are byte-for-byte alike in
kind**: 200, ~30 KB, no `ld+json`, no microdata, **no date anywhere on the page**. *The sitemap's
`lastmod` is the ONLY thing that dates any advert on this host.* **So an adapter that reads the
sitemap must carry that `lastmod` as the advert's only date, and one that emits the archive
without it would publish 2023 vacancies as today's with nothing to catch it.**

### CORRECTION of 2026-10-02 — `Maaş: TL` was a COMMENT, not a field

| | |
| :-- | :-- |
| **written earlier today** | «`Maaş: TL` — a currency with no amount, this time in an HTML table» |
| **true** | **the `Maaş` row is inside an HTML comment: the board publishes no salary at all** |
| **why the first reading said it** | `re.sub(r"<[^>]+>", " ", …)` renders the CONTENT of a comment as text |
| **corrected** | 2026-10-02, within the hour, by reading the raw markup instead of the extracted string |

```html
<!-- <tr>
        <td>Maaş</td>
        <td> TL</td>
     </tr>-->
```

**Measured: `Maaş` occurs exactly ONCE on each advert page and that occurrence is inside a
comment, on both the live advert and the 2023 one; the other four labels are live.** *Each page
carries **12 comments totalling ~8 500 bytes — about a quarter of a 30 KB page**, so this is not a
corner case on this host.*

> **A tag-stripping extractor reads HTML comments as content, and a field invented out of
> disabled template code is worse than a missing one** — a missing field is visible, a fabricated
> one is believed.

**The tell was present and was passed over**: the extracted table string ended in a stray `-->`.
*The guard now asserts both halves — that `text()` on the raw table still shows `Maaş` and `-->`
(the defect, reproduced), and that nothing survives `sans_commentaires()`.*

**The `baseSalary.currency` family is therefore NOT extended by this board.** *It keeps three
variants — a currency that is wrong (#638/#655), a currency on null values (#722) — and this host
contributes none: it has no salary field at all.* **The adapter handles a re-enabled row in both
forms anyway (an amount is carried, a bare currency is flagged), so the case is ready before it is
met in the clear.**

### The age and sex criteria are not propagated

The table carries `Cinsiyet` («Fark Etmez») and `Yaş` («18 - 50 Arası»). **#183 settled the field
treatment for exactly this pair: we do not propagate the criterion, and we keep serving the
advert.** *That issue rested on Uzbek labour law, and **the law of Northern Cyprus has NOT been
checked here** — the field treatment is carried over because propagating an age or sex
requirement serves no candidate, not because a statute has been established.* **Flagged for the
owner rather than asserted as a legal fact.**

### What the adapter does, and the one thing it must not do

```
route : http — the live list is the inventory, 8 adverts, enumerated_by: listing
        the advert's fields come from ONE HTML table; there is no structured markup
        no salary (a bare «TL»), no date (the page states none), no age/sex criteria
archive : the 3042 sitemap ids are reachable and UNDATED except by `lastmod`
          they are emitted only on an explicit option, each carrying its `lastmod`
          and a flag — NEVER unioned into the live list
```

**The pager question raised by the 18.09 card is answered: there is no pager.** *`?sayfa=` is
ignored, `?page=` serves an advert-less page, the city facets are inert, and the list is its own
whole extent.*

**Measured 2026-10-02 by the declared client, the guard on each exact path first, two reads of
the list, `bin/fetch-body.py`, provenance written beside every body.** *A measurement, not an
adapter.*

```
_robots.verdict('www.kibriseleman.com')  state: read, certain: True, group '*', delay: None, sitemaps: []
GET /is-ilanlari ×2 · ?city=1..6 · ?sayfa=2 · ?page=2 · /sitemap.xml · 2 advert pages  — all 200
```
