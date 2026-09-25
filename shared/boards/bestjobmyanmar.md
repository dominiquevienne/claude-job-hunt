# Board measurement — BestJobMyanmar (`www.bestjobmyanmar.com`, Myanmar): a small DJ-Classifieds board that **enumerates itself** — its own RSS feed is the route, and on 2026-09-25 three independent readings agree it publishes **three** live adverts. Adapter `bestjobmyanmar.py` (#637)

<!-- verified: 2026-09-25 -->

<!-- hosts: www.bestjobmyanmar.com -->
<!-- script: bestjobmyanmar.py -->
<!-- countries: MM -->
<!-- route: http -->
<!-- content: measured · **Joomla + DJ-Classifieds (`com_djclassifieds`), server-rendered — no `__NEXT_DATA__`, no `data-page`, no JSON carrier; the root answers 200, 63 062 B, md5 f12de9a76dc3 then 41de5c313125 on two reads — the fingerprint MOVES, so no md5 comparison means anything here; `/find-jobs-in-myanmar` 200, 73 726 B, states no count and carries no pager; `/jobs` 404; `/sitemap.xml` 404; the feed `/find-jobs-in-myanmar?format=feed&type=rss` 200, 3 176 B, 3 items; a connected tab shows the same three, so nothing hides behind JavaScript; `_robots.allowed('www.bestjobmyanmar.com','/jobs')` → open, certain, `state: read`, and NO Crawl-delay is written (2 s are ours)** · 2026-09-25 -->
<!-- witness: 3 adverts emitted against 3 `<item>` stated by the site's own feed; the category select names exactly three categories (Customer Service 24, Engineering/Technology 106, Sale 51) under the parent «Jobs» (110) — one advert each · 2026-09-25 -->

**Measured 2026-09-25 07:44–08:1x UTC by the declared client, the guard on the
exact path (query string included), `bin/fetch-body.py`, two reads of the root;
and by a connected tab, which was needed twice — once to establish that the
three adverts are not a JavaScript truncation, once to read the field labels
after three regex attempts on the raw markup had failed.** The adapter was then
run against the host: 3 emitted, 3 stated.

```
GET /                                        200, 63 062 B, md5 f12de9a76dc3 / 41de5c313125  (deux lectures — l'empreinte BOUGE)
GET /find-jobs-in-myanmar                    200, 73 726 B — 3 annonces, aucun compte, aucun pager
GET /find-jobs-in-myanmar?format=feed&type=rss  200,  3 176 B — 3 <item>
GET /jobs                                    404          <- le chemin que l'issue nommait
GET /sitemap.xml                             404
```

## The issue's premise was wrong, and the site published the answer

**#637 named «&nbsp;une liste `/jobs`&nbsp;». That path is a 404.** The listing is
`/find-jobs-in-myanmar`, and it states no count and offers no pager — so a walk
would have had to guess at Joomla internals. **It does not have to: the page
links the site's own RSS feed**, and the «&nbsp;Save search&nbsp;» control
base64-decodes to the board's own all-items query
(`option=com_djclassifieds&view=items&cid=0:all&se=1&se_cats=110`). *The
enumerator was published all along; the issue had simply named the wrong path.*

## Three traps, and two of them are already written in this repository

**A link count is not an advert count.** The same advert appears under two URL
shapes on one page — `/find-jobs-in-myanmar/ad/sale-51/<slug>-4628` (canonical,
the feed's) and `/find-jobs-in-myanmar/sale/ad/<slug>-4628` (the home page's).
Counting `/ad/` links gives a number that looks like an inventory. **The
identity is the trailing id.**

**A number in a path belongs to a namespace.** `sale-51` is category 51 (Sale).
`51` is also **Bago** in the location select. *Same integer, two vocabularies* —
resolved by reading the site's own `<option>` lists, never by inferring from the
path.

**The salary is a labelled field, and it keeps its currency.** The board writes
`<span class='price_val'>Up to 550,000</span> <span class='price_unit'>Kyats</span>`:
a pattern stopping at the first `</span>` returns an amount **without its
unit**, and a pattern closing on the row's `</div>` runs across the following
rows and swallows the employer. *The first correction was worse than the
defect — a pattern that overruns does not return less, it returns wrong, and it
damages a different field than the one being fixed.* The salary is read from
the two spans the site marks, and nothing else.

## Withheld

**Contacts** — e-mail addresses and telephone numbers in free text; the board's
«&nbsp;Contact Now&nbsp;» form is never touched.

**A personal criterion** — the board prints `Gender` on its adverts («&nbsp;Male&nbsp;»,
«&nbsp;Female&nbsp;», «&nbsp;Male/Female&nbsp;»); #183 says such a criterion is not propagated,
so it is withheld and **named** in `criteria_withheld`. **The declaration follows
the ADVERT, never the board**: all three carried one on 2026-09-25 and all three
declare it, but an advert printing none declares nothing — naming what was never
deposited would lie about our own discretion rather than about the board, and
the output is identical either way.

*The board is small and that is not a reason to skip it (§2 sexies). What it
publishes is three adverts, in Burmese, with salaries in kyats; the adapter
emits them and prints the feed's own count beside its own.*
