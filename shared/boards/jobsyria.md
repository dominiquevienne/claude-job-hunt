# Board measurement — Syria Jobs Network (`jobsyria.org`, Syria) — **adapter SHIPPED 2026-11-06 (#1278), reading the API this site's own bundle declares, the root not being the enumerator**: «شبكة وظائف سوريا» — on 2026-09-17 the root stated «+6356 فرصة» with its category counts and the newest NGO ads (844 470 B); **on 2026-09-22 the same root serves 293 545 B with no advert and no count, `/jobs/list` renders «لم يتم العثور على وظائف», and the board's own API answers HTTP 500 — a dated state of the site, not an empty board**; **on 2026-11-06 that API answers 200 again and states its own counters, while the root still carries no advert**; **the adapter of #1278 reads that API and never the root, the root being no enumerator**

<!-- verified: 2026-11-06 -->

<!-- hosts: jobsyria.org -->
<!-- script: jobsyria.py -->
<!-- countries: SY -->
<!-- route: http · 6493 · 2026-11-06 -->
<!-- witness: the paginator's OWN `meta.total` from `api/jobs?page=1&size=20`, **6 493**, and its arithmetic checks against itself rather than against us: `last_page = 325`, and page 325 returns 13 records at `from 6481 · to 6493`, so 324 × 20 + 13 = 6 493 exactly. The parameter is HONOURED and not ignored -- page 326 returns ZERO records with ZERO overlap with page 1, where a parameter that is ignored would have served page 1 again. **Our own extraction has enumerated 93 of them** (pages 1/81/163/244/325) plus 20 full records, so 6 493 is the BOARD's count of what its list serves and never ours. **`api/home` states a SECOND and different total** -- `counters.jobs = 6538`, read two minutes later -- and the two are 45 apart for a reason that is NOT established (drafts, hidden, deleted look alike from here); the list honours 6 493, so that is the one this line carries, and a ratio built on 6 538 would be plausible and false · 2026-11-06 -->
<!-- content: measured · **the list serves CLOSED adverts, and page 1 cannot show it** -- a spread sample of 93 over pages 1/81/163/244/325 is 40 `open` and 53 `closed`, where page 1 alone reads 100 % open. **And `status` is not a freshness signal either: 23 of those 40 `open` are already past their `deadline`**, so only 17 of 93 are both open and unexpired, and a filter on `status` alone leaves 58 % of what it keeps expired. The two are independent and the adapter counts them apart. `monthly_salary` is EMPTY on 93 of 93 and `application_method` is `link` on 93 of 93; the prose of the 20 full records carries ZERO e-mail, telephone or messaging host, and the whole contact exposure is in `application_link` -- 26 hrefs over 20 adverts, of which **2 are `mailto:`** · 2026-11-06 -->
<!-- route: http · the board's own API answers again — `api.jobsyria.org/api/home` 200, 121 344 B, md5 `62bb56f29b71`, valid JSON, `success: true` — and the ROOT is not the enumerator (four «لم يتم العثور», zero advert link), so what an adapter would read is the API and not the root; no listing endpoint has been exercised, so no count is published · 2026-11-06 -->
<!-- content: measured · **the condition this card named for its own lifting is SATISFIED** — it said « What would lift it: `api/home` answering 200 », and on 2026-11-06 `api.jobsyria.org/api/home` answers **200, 121 344 B, md5 `62bb56f29b71`**, valid JSON with `success: true` and `counters = {jobs: 6538, tenders: 291, clients: 619, categories: 31}`; the root answers **200, 855 668 B, md5 `5808c6adbc04`** against 293 545 B on 2026-09-22, and it is still NOT the enumerator — four «لم يتم العثور» and zero advert link — so the route is the API. The 6538 is the BOARD's own counter and never our extraction, and nothing of ours has been enumerated, so this card publishes no count of its own · 2026-11-06 -->
<!-- witness: the host's OWN `counters` object from `api/home`, `jobs: 6538` stated by the site itself and read by the declared client on 2026-11-06 00:52–00:53 UTC — our own extraction has enumerated nothing, so no figure of ours stands beside it · 2026-11-06 -->
<!-- content: measured · **not an empty board — a BROKEN one**; the page is rendered SERVER-side, so this is not a shell waiting for its JS; it prints «no result» four times and its API answers 500 naming a missing PHP class; it stated «+6356 فرصة» on 2026-09-17. What would lift it: `api/home` answering 200. **2026-09-22, two reads of each path by the declared client, the guard on the exact path: the root 200 twice, 293 545 B, md5 707947a623f1 identical — server-rendered (`ng-server-context="ssr"`, 42 hydration markers) and carrying «لم يتم العثور» four times, no advert link, no «6356» anywhere; `/jobs/list` 200 twice, 264 984 B, md5 a4c35401a112 identical, «لم يتم العثور على وظائف — نأسف, لا توجد سجلات توافق معطيات بحثك»; the site's own API `api.jobsyria.org` answers HTTP 500 on `/api/home` (twice, 1 116 994 and 1 116 990 B) and on `/api/settings` (1 117 152 B), each a PHP fatal-error page naming `Class "Monolog\Logger" not found`. On 2026-09-17 the same root was 844 470 B, md5 3fc6d37c571c twice, and stated «+6356 فرصة» with category counts (136, 306, 1324, 409). Rules open and certain on `jobsyria.org` and on `api.jobsyria.org`, no Crawl-delay** · 2026-09-22 -->
<!-- witness: the root's own «+6356 فرصة» and category counts on 2026-09-17; on 2026-09-22 the root's own «لم يتم العثور» and the API's own 500 · 2026-09-22 -->

## What the host serves now, and what this card said before

**Measured by the declared client, the guard on each exact URL in a tour DISTINCT from the
retrieval, one token (`claude-user`): open and certain on every path, no written rule, no
`Crawl-delay` — so the cadence is ours to set.** The reading lives in #1278.

What the header said until today, kept because a correction cites what it corrects:

    verified: 2026-09-22
    content:  measured · **not an empty board — a BROKEN one** … What would lift it: `api/home` answering 200 · 2026-09-22

**The condition was its own, and it is met.** What does NOT follow is a board: the root is
bigger and still prints « no result », so the enumerator remains to be found — on the API, which
is where the next reading goes. *A measurement, not an adapter.*

**Found by the Syria search of #608 (a country never searched), measured
2026-09-17 13:46–13:47 UTC and again 2026-09-22 13:00–13:06 UTC by the declared
client, the guard on the exact path first, `bin/fetch-body.py`, two reads of
each path.** The method is written on #608: one Arabic search («مواقع التوظيف
في سوريا …»), the hosts the engine names kept, the Tanqeeb front
(`syria.tanqeeb.com`, HTTP 202 with an empty body again — the state
`tanqeeb.md` records since 2026-09-05) not duplicated. *A measurement, not an
adapter.*

```
2026-09-17
_robots.allowed('jobsyria.org', '/')       open, certain
GET https://jobsyria.org/                  200 ×2, 844 470 B, md5 3fc6d37c571c — «+6356 فرصة», category counts, the newest ads, /jobs/list

2026-09-22
_robots.allowed('jobsyria.org', '/')       open, certain, no Crawl-delay
_robots.allowed('jobsyria.org', '/jobs/list')   open, certain
_robots.allowed('api.jobsyria.org', '/')   open, certain
GET https://jobsyria.org/                  200 ×2, 293 545 B, md5 707947a623f1 — SSR, «لم يتم العثور» ×4, no advert, no «6356»
GET https://jobsyria.org/jobs/list         200 ×2, 264 984 B, md5 a4c35401a112 — «لم يتم العثور على وظائف»
GET https://api.jobsyria.org/api/home      500 ×2, 1 116 994 / 1 116 990 B — PHP fatal: Class "Monolog\Logger" not found
GET https://api.jobsyria.org/api/settings  500,   1 117 152 B — the same fatal
```

## What today's reading is, and what it is not

**The front is Angular (`main.fa349d6e6f8df30c.js`, 976 908 B, read
2026-09-22), `assets/config.json` is `{"API_URL":""}`, and the bundle names
`https://api.jobsyria.org/api` with the calls `home`, `jobs/filters`,
`settings` and the editorial pages.** The root served today is *rendered*, not
a shell awaiting JavaScript — `ng-server-context="ssr"` and forty-two
hydration markers — and what it renders is the empty state, four times over.
**So the page does not say the country has no work: it says its own back end
returned nothing, and that back end answers 500 to us directly.**

**The two md5 of `/api/home` differ by four bytes between reads** — the error
page carries something per-request — **so no fingerprint comparison is worth
anything on it**; the HTTP code and the class name are what is stable, and
both were the same twice.

*This is «before comparing two md5, fetch twice» used in the direction it is
rarely written in.* The rule usually **licenses** a comparison: two reads
agree, so the fingerprint means something, so two hosts can be compared by it.
Here the two reads **disagree**, and the rule therefore **forbids** the
comparison outright — this body cannot be matched against another host's, or
against its own reading tomorrow, and any «the refusal changed» drawn from it
would be an artefact of the page's own per-request content. **What held twice
is what may be carried: the code, and the name of the missing class.**

**This is a state of the site on 2026-09-22, not a verdict on the board.** The
17.09 reading stands as read: the same root, the same client, 844 470 B and
«+6356 فرصة». Nothing here says the adverts are gone; it says the service that
carries them is down.

## What would lift it

**The API answering again** — `GET https://api.jobsyria.org/api/home` returning
200 — after which `/jobs/list`, its pager and the advert page are the adapter's
first line, exactly as #649 describes. Until then the adapter cannot be written
against anything: a walk built today would be written against the empty state.
Issue #649 carries this measurement and is labelled `blocked` for that reason
alone.
