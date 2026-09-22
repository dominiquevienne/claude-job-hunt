# Board measurement — Department of Public Information (`dpi.gov.gy`, Guyana): the Government's «Vacancies» category of its government adverts — **746 notices over 75 pages on 2026-09-22** (GuySuCo, the Bureau of Statistics, the Guyana Marketing Corporation, the Defence Force…), from 2021-02-18 to 2026-09-18, the walk ending on the 404 WordPress serves past the last page; `dpigovgy.py` — each notice IS a document, named and never downloaded

<!-- verified: 2026-09-22 -->

<!-- hosts: dpi.gov.gy -->
<!-- script: dpigovgy.py -->
<!-- countries: GY -->
<!-- content: measured · **the category walked by the declared client, 2026-09-22 08:0x–08:3x UTC, the guard on the exact path: `/category/government-adverts/vacancies/` 200 (307 102 B, md5 a3a231007eee) renders ten `div.item` blocks inside `div.fn-archive-content`, each an `.item-title` link and an `.item-date`; **the theme prints NO pager link**, and `/page/N/` answers anyway — page 2 (305 664 B) ten, page 20 ten, page 60 ten — while `/page/100/`, `/page/120/`, `/page/150/` and `/page/300/` answer **404** (241 022 B, the theme's own not-found page). The walk read **746 notices over 75 pages and ended on the 404 of page 76**; nothing on the site states a count. Dated 2021-02-18 to 2026-09-18 (2026: 100, 2025: 107, 2024: 144, 2023: 101, 2022: 159, 2021: 135). A notice's body is the ADVERT itself — a PDF in the post's `algori-pdf-viewer` iframe (the address in its `?file=` parameter) or the post's image — and the site's REST answers `[]` for the category AND for a post read from the HTML, so the HTML is the route. Exercised: `jobs --country-code GY` → **746 emitted, «page 76 answered 404 — the end of the category» said**; `ad --url …/bureau-of-statistics-vacancy-human-resources-clerk/` → the PDF named · 2026-09-22 -->
<!-- witness: none — the category states no count; `dpigovgy.py jobs` prints the entries read, the pages walked and how the walk ended · 2026-09-22 -->
<!-- route: http · 746 · 2026-09-22 -->
**Found by the Guyana search of #621 (a country never searched), measured
2026-09-18 06:54–06:56 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #621:
three searches naming the public sources and the private boards, no
composed host names. *A measurement, not an adapter.*

A public source, not a board: the Government's information department republishes the vacancy notices of state bodies. The National Job Bank of the Ministry of Labour (CRMA) lives on `labour.gov.gy/jobs-bank` — its card (`labour-gov-gy.md`) carries its own measurement and control date, and this search did not remeasure it.

```
_robots.allowed('dpi.gov.gy', '/category/government-adverts/vacancies/')   open
GET https://dpi.gov.gy/category/government-adverts/vacancies/   200 ×2 — see the content line
```

## The adapter — `dpigovgy.py` (#703, 2026-09-22)

```
GET /category/government-adverts/vacancies/          200 — 10 notices, newest 2026-09-18, NO pager link
GET …/page/2/ … /page/75/                            200 — 10 a page
GET …/page/76/                                       404 — the end of the category
    → 746 notices, 2021-02-18 to 2026-09-18, nothing stating a count
GET /<slug>/                                         the notice: a PDF in its viewer, or its image
```

**Three traps, and each is now a guard.**

**The theme prints no pager link at all** — and `/page/N/` answers anyway.
*A walk that trusted the markup would have stopped at ten and called it the
board*: the first reading of this card, on 2026-09-18, recorded «no pager
link on page 1» and seven notices. **The end is the 404** WordPress serves
past the last page, and a 404 on page ONE is the opposite thing — the
category is gone.

**The sidebar uses the same `item item-N` class as the archive.** A
page-wide read counted **41 blocks where the archive holds 10**, the extra
ones being the theme's «popular» and «recent» widgets — news, not vacancies.
The items are read inside `fn-archive-content` and nowhere else.

**The REST is not the route, and that is measured**:
`wp/v2/posts?categories=39092` and `wp/v2/posts?slug=<a post read from the
HTML>` both answer **200 with `[]`** (2026-09-21 and 2026-09-22) while those
same posts render in the archive. *The REST is not «empty» — it is closed to
this reading*, and «no posts» from it would have been a false negative about
the board with no symptom at all.

**The archive is deep** — six years — so `--since` bounds it on the date each
entry states: the posts are newest-first, so the walk stops at the first one
older, and the run says **the bound was OURS**, never the category's
(exercised: `--since 2026-08-01` → 29 emitted over 3 pages, «1 older not
emitted»).

**A notice is a document.** `ad --url <post>` names the address of the PDF in
the post's viewer iframe — read from its `?file=` parameter, **not** from the
iframe's own `src`, which is the viewer's URL and not the advert — or of the
post's image. **Nothing is downloaded.** **Withheld:** e-mail addresses and
telephone numbers in a title; `contacts_withheld` on every record.

**Tests and mutations.**
`AGovernmentCategoryWithNoPagerWhoseEndIsA404AndWhoseRestIsClosed`, both ways
on fixtures (the walk ending on the 404 with the 404 page not counted as
walked, a sidebar block of the same class left out, `--since` declared as
ours, the PDF taken from `?file=`, a title carrying an address and a number,
a repeating page, a 200 without the archive region, a 404 on page 1, a bad
`--since`, `ad` on a query string and on the root, the `www.` host refused).
Mutation bench on a detached copy, `python3 -B`, **10 / 10 red**: the
404-ends-the-walk branch removed · the items read page-wide · the `--since`
bound not declared ours · the «nothing states a count» note dropped · the PDF
taken from the viewer's `src` · the older-count silenced · the repeat guard
dropped · the scrub dropped · a query string accepted by `ad` · the host
check dropped.
