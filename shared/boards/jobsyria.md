# Board measurement — Syria Jobs Network (`jobsyria.org`, Syria): «شبكة وظائف سوريا» — on 2026-09-17 the root stated «+6356 فرصة» with its category counts and the newest NGO ads (844 470 B); **on 2026-09-22 the same root serves 293 545 B with no advert and no count, `/jobs/list` renders «لم يتم العثور على وظائف», and the board's own API answers HTTP 500 — a dated state of the site, not an empty board**; no adapter yet

<!-- verified: 2026-09-22 -->

<!-- hosts: jobsyria.org -->
<!-- script: none -->
<!-- countries: SY -->
<!-- content: measured · **2026-09-22, two reads of each path by the declared client, the guard on the exact path: the root 200 twice, 293 545 B, md5 707947a623f1 identical — server-rendered (`ng-server-context="ssr"`, 42 hydration markers) and carrying «لم يتم العثور» four times, no advert link, no «6356» anywhere; `/jobs/list` 200 twice, 264 984 B, md5 a4c35401a112 identical, «لم يتم العثور على وظائف — نأسف, لا توجد سجلات توافق معطيات بحثك»; the site's own API `api.jobsyria.org` answers HTTP 500 on `/api/home` (twice, 1 116 994 and 1 116 990 B) and on `/api/settings` (1 117 152 B), each a PHP fatal-error page naming `Class "Monolog\Logger" not found`. On 2026-09-17 the same root was 844 470 B, md5 3fc6d37c571c twice, and stated «+6356 فرصة» with category counts (136, 306, 1324, 409). Rules open and certain on `jobsyria.org` and on `api.jobsyria.org`, no Crawl-delay** · 2026-09-22 -->
<!-- witness: the root's own «+6356 فرصة» and category counts on 2026-09-17; on 2026-09-22 the root's own «لم يتم العثور» and the API's own 500 · 2026-09-22 -->

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
