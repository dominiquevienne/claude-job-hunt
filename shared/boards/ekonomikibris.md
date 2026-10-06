# Board measurement — Ekonomi Kıbrıs — iş ilanları (`www.ekonomikibris.com`, Northern Cyprus): the vacancy notices («münhal duyurusu») of an economy news site — **the route is the RSS feed, which carries 50 notices and strictly CONTAINS the 21 of a CLAMPED AJAX pager**, the first of four boards where one enumerator contains the other; section dormant since 2025-01-06; rules open, no count stated; **the adapter reads the feed ONCE for all 50 notices and re-measures the containment at every run**

<!-- verified: 2026-10-02 -->

<!-- hosts: www.ekonomikibris.com -->
<!-- script: ekonomikibris.py -->
<!-- countries: CYN -->
<!-- content: measured · **THE ROUTE IS THE RSS FEED, NOT THE PAGE: `/is-ilanlari/` (200, 56 151 B) carries 21 notices as `/<slug>/<id>/`; its «Daha Fazla Getir» button is AJAX (`data-page="2"`, `data-url=.../news-category-ajax.php?katid=70`) and that pager is CLAMPED — pages 2, 3, 4 and 5 each return 15 ids and ZERO new. `/rss_is-ilanlari_70.xml` (200, 100 917 B) carries 50 `<item>`, and the pager's 21 are ALL inside it: intersection 21, pager-only 0, feed-only 29, union 50. `/is-ilanlari/page/2/` answers 404 and `?sayfa=2` is ignored. The notice page (68 274 B) carries THREE `ld+json` blocks, the third a `NewsArticle` with `articleBody`, `headline`, `datePublished`, `wordCount` — it raises under a STRICT parser (a raw control character in a string) and parses with `strict=False` The rules file is served (`state: read`, `certain: True`) on `/`, `/is-ilanlari/`, the RSS and the AJAX endpoint, and writes no Crawl-delay — 2 s are ours.** · 2026-10-02 -->
<!-- content: measured · **`/is-ilanlari/` (200, 56 151 B, md5 36e906941497 / b68fa58ee731 — a rendered element moves) lists 21 distinct `…-munhal-duyurusu-…` notices as news posts (universities' and companies' vacancy announcements), category links `/kibris-ekonomi/`, `/kibris-haberleri/`; no count stated, no pager link found on the first page, no JobPosting; `_robots.allowed('www.ekonomikibris.com','/is-ilanlari/')` → open, certain** · 2026-09-18 -->
<!-- witness: no count stated anywhere; the FEED is the enumerator at 50 and it strictly CONTAINS the clamped pager's 21, which is the first of four boards where containment actually holds · 2026-10-02 -->

<!-- witness: none — the section states no count · 2026-09-18 -->

## The adapter — one request for the 50 notices, and the containment re-measured at every run

`skills/job-scan/scripts/ekonomikibris.py`

```
python3 ekonomikibris.py jobs --country-code CYN            # 50 notices, 6 requests
python3 ekonomikibris.py jobs --country-code CYN --feed-only   # the feed alone, 1 request
```

**The feed is the enumerator AND the content.** `content:encoded` carries the whole article
text; compared with the notice page's `articleBody` for one notice it agrees to **0.9986 with
no differing run over twelve characters**. *So the adapter reads bodies from the feed and says
so* — it does not claim the two are equal on all 50, which one comparison cannot establish.
**Fifty-one requests become one.**

**Containment is re-measured, never assumed.** The run intersects IDENTIFIERS and prints the
relation it found; a pager-only identifier — none today — is fetched from its own notice page
rather than dropped. *The day the relation changes, the surprise costs one request instead of a
silent loss.*

### A withholding rule loose enough to catch a landline also stamps an ISO certification

**2 of the 50 bodies carry a TRNC landline (`0392 …`), so a mobile-only rule leaks them.** But
the repository's broad pattern also takes `9001-2015` and `22000-2018` — **ISO standard
references** — and `[telephone withheld]` printed over a quality certification *is a claim
about the employer that the board never made*. **The rule is therefore anchored on what the
country NUMBERS: `+90`/`0` then `5xx` or `392`.** *Measured in both directions on the real
corpus: the anchored rule bites the same 17 bodies, splits `0548 838 10 53 / 0392 227 51 96`
into the two numbers it is, and leaves both citations intact.*

**And no salary is carried, for a measured reason: the only money-shaped string in 50 bodies is
`14.000m2` — a FLOOR AREA in square metres.** *This board states no pay anywhere, so the row
carries none rather than mine one out of prose.* **Nor is a `JobPosting` pretended**: the
notices are `NewsArticle`s, the row says `markup: NewsArticle` and `structured_posting: false`,
and it omits `salary`, `valid_through` and `employment_type` instead of emitting them empty —
*empty fields would give a PRESS template the look of a structured advert whose fields merely
happened to be missing.*

## Re-measured 2026-10-02 — the feed is the route, and it CONTAINS the pager

```
/is-ilanlari/            21 ids      the AJAX pager (pages 2-5)   15 each, ZERO new -> CLAMPED
/rss_is-ilanlari_70.xml  50 ids      intersection 21 · pager-only 0 · feed-only 29
UNION                    50          -> the feed strictly contains the pager
```

**This is the fourth board in four days whose two enumerators were compared, and the first where one
CONTAINS the other.** *Lambda 50/30 intersecting in 2 (#661), İş Kıbrıs 12/12 in 6 (#719), Work Link
12/20 in 4 (#722) — in none of those did either hold the other.* **Here the feed holds all 21 of the
pager and 29 besides.**

> **So the rule is not «&nbsp;a feed is incomplete&nbsp;»: it is that the relation between two
> enumerators is unpredictable in BOTH directions and must be measured each time.** *Three failures
> could have hardened into «&nbsp;never trust a feed&nbsp;», which would have been the same error with the
> sign reversed — and here it would have cost a pointless walk of a clamped pager.*

### The pager is AJAX and it is clamped

The «&nbsp;Daha Fazla Getir&nbsp;» button carries `data-page="2"` and
`data-url=…/news-category-ajax.php?katid=70`. **Asking that endpoint for pages 2, 3, 4 and 5 returns
15 ids each and not one new identifier** — all 15 already sit in the page's 21. *`/is-ilanlari/page/2/`
answers 404, and `?sayfa=2` is ignored (same size, same ids).* **So the HTML page is the pager's whole
extent, and the feed is what reaches the rest.**

### The section has been dormant for twenty-one months

**All 50 feed items date between 2024-12-31 and 2025-01-06** — 46 in January 2025, 4 in December 2024.
*The route works and the section has stopped publishing*, which is a statement about the board and
carries the board's own dates as its bound. **Far more dormant than `kktcportal` (#724), whose newest
was twelve weeks old.**

### A `ld+json` block that RAISES is not a block that is absent

The notice's third block is a `NewsArticle` carrying `articleBody`, `headline`, `datePublished`,
`dateModified` and `wordCount`. **It fails `json.loads` with «&nbsp;Invalid control character&nbsp;» — a raw
newline inside a string — and parses cleanly with `strict=False`.** *A first reading recorded it as
malformed and unusable, which would have sent an adapter scraping HTML for data that was already
there.* **The repository's decode lesson, inverted: there a broken decode returned text and looked
like absent content; here a working block raised and looked like absent data.**


**Found by the Northern Cyprus search of #606 (a country never searched),
measured 2026-09-18 07:20–07:22 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #606: two searches in Turkish naming the Labour Department and the
private boards, no composed host names. *A measurement, not an adapter.*

A newspaper's vacancy-notice section, not a board: employers' announcements as articles.

```
_robots.allowed('www.ekonomikibris.com', '/is-ilanlari/')   open
GET https://www.ekonomikibris.com/is-ilanlari/   200 ×2 — see the content line
```

The adapter's first line: how the section pages, the notice as the ad (employer, post, deadline in the article's text).
