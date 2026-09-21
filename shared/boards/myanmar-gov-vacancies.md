# Board measurement — the Myanmar National Portal's «Job & Vacancy» (`myanmar.gov.mm/vacancies`, Myanmar): the government's own vacancy notices on a Liferay asset publisher — **the portlet STATES its total («Job & Vacancy - 183 items») and 182 entries were read over 19 pages on 2026-09-21**, the pager token taken from the page's own links; `myanmargov.py` — no document downloaded, and the portal's closed notices counted, never dropped in silence

<!-- verified: 2026-09-21 -->

<!-- hosts: myanmar.gov.mm -->
<!-- script: myanmargov.py -->
<!-- countries: MM -->
<!-- content: measured · **the portlet walked by the declared client, 2026-09-21 15:0x–15:2x UTC, the guard on the exact path, two reads of page 1 and one of each other page: `/vacancies` 200 ×2 (225 332 B, md5 c9711170b6d4 — a news block moves) carries the asset publisher whose heading states **«Job &amp; Vacancy - 183 items»**, 10 entries a page, and a pager naming the portlet's INSTANCE token (`idasset460` on the day, READ from the page, never composed); page 19 200 (222 430 B) carries 3 — 18 × 10 + 3 = 183, the stated total to the unit. The walk emitted **182 over 19 pages and said «1 short»**: one card carries no address or no title, and the run counts it. An entry is a `div.col-md-12.smallcardstyle` — a link, a Burmese `h2` title, «Agency:» and «Closing Date::» read as labels; the link is a PDF under `/documents/`, a ministry's own site (mopf 39, surveydepartment 8, mol 7…) or a `myanmarjob.gov.mm/job/view/<id>` page, and none is downloaded. The portal keeps closed notices — 181 of the 182 state a date already past, the oldest 2018 — which is the ministries' filing, not a fault. Exercised: `jobs --country-code MM` → **182 emitted, «the portlet states 183 — 1 short» and «181 closed» said** · 2026-09-21 -->
<!-- witness: the portlet's own «Job &amp; Vacancy - 183 items», printed beside the emitted count on every run · 2026-09-21 -->
<!-- route: http · 182 · 2026-09-21 -->

**Found by the Myanmar search of #601 (a country never searched), measured
2026-09-17 09:35–09:39 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads of the root, two public resolvers on
a DNS negative.** The method is written on #601: one search for the
country's boards (a recruiting vendor's ranking of ten, cross-read with
the engine's own results) and one for the public employment service (the
Ministry of Labour's Labour Exchange Office system, named by the national
portal). *A measurement, not an adapter.*

```
_robots.allowed('myanmar.gov.mm', '/vacancies')   open, certain
GET https://myanmar.gov.mm/vacancies              200 ×2 — Liferay, «Jobs & Vacancies», facets by ministry
```

The public sector's own notices, on the portal that also names the Labour
Exchange Office system (unreachable from here today, see
`myanmarjob-gov.md`). What a notice carries, how the publisher pages, and
whether a list route serves the client are the first line of the adapter.

## The adapter — `myanmargov.py` (#634, 2026-09-21)

```
GET /vacancies                              200 ×2 — «Job & Vacancy - 183 items», 10 entries, the pager's token
GET /vacancies?…_INSTANCE_idasset460_cur=N  200 ×18 — 10 a page, 3 on page 19, 0 on page 20
    → 182 emitted, 183 stated, «1 short» said: one card carries no address or no title, and it is counted
```

**The token is read, never composed.** `idasset460` is this deployment's, and
it changes when they rebuild: a token we invent is a guess about someone
else's server. The pager links print it, and the walk uses those.

**The parameter names carry a LEADING UNDERSCORE**
(`_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_idasset460_cur`).
Without it Liferay ignores them and serves page 1 again — **and the repeat
guard then fires on a walk that was never walking**, which reads like a board
that repeats itself rather than like a request that was malformed. That cost
a run, and it is now a guard.

**The titles are Burmese, and a key slugged from ASCII letters is EMPTY** —
twenty records shared one identifier that way. The key is the address plus
the title folded by its **digest**, which is as distinct as the title
whatever the script; `key_is_ours` says so, because the portal publishes no
identifier and **one address can carry two notices** (a call and its result
both point at the same PDF).

**The portal keeps closed notices**, and that is not a fault: 181 of the 182
state a closing date already past, the oldest from 2018. They are emitted
with their date and **counted in the run**; `--closing-after` filters on the
date the entry itself states and says how many it dropped. *A board that
silently dropped them would look smaller and cleaner than it is.*

**No document is downloaded** — a PDF under `/documents/`, a ministry's own
site, or a `myanmarjob.gov.mm/job/view/<id>` page (the Labour Exchange
system, which does not answer from here) is named as the portal publishes
it. **Withheld:** e-mail addresses and telephone numbers in a title or an
agency name; `contacts_withheld` on every record.

**Tests and mutations.**
`ANationalPortalWhosePortletStatesItsTotalAndPagesByAnUnderscoredToken`, both
ways on fixtures (the underscored parameters in the second request, the token
from the page's own pager, one address carrying two notices, a Burmese title,
a card without an address, `--closing-after` and its drop count, the stated
total agreeing, differing and absent, a repeating page, a page with no pager,
a 404, a bad `--lang` and a bad date, the `www.` host refused). Mutation bench
on a detached copy, `python3 -B`, **11 / 11 red**: the leading underscore
dropped · the token composed · the key slugged in ASCII · the stated total
ignored · the «short» branch removed · the skipped-card count silenced · the
closed count silenced · the filter's drop count silenced · the repeat guard
dropped · the scrub dropped · the host check dropped.
