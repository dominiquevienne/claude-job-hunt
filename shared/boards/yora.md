# Board measurement — Yora (`yora.tj`, and `vazifa.tj` which serves the same page, Tajikistan): a job platform whose front is a Next.js shell to the declared client (186 KB, the same body on both hosts), rules open; `vazifa.tj/latest-jobs` — the address the search engine still indexes — answers 404; no adapter yet, the list route to measure

<!-- verified: 2026-09-17 -->

<!-- hosts: yora.tj, vazifa.tj -->
<!-- script: none -->
<!-- countries: TJ -->
<!-- content: measured · **`yora.tj/ru` and `vazifa.tj/` answer the same body (200, 185 823 B, md5 f09b601fb5dc on both, identical on two reads each) — a Next.js shell titled «Yora», icons and chunks, no card, no count, no JobPosting; `vazifa.tj/latest-jobs` (the engine's «Все вакансии в Таджикистане») answers 404 (29 989 B, a themed not-found page); `_robots.allowed` → open, certain on both hosts; whether the route the shell calls serves the client is the adapter's first line — Vazifa has become Yora** · 2026-09-17 -->
<!-- witness: none — the front is a shell · 2026-09-17 -->

**Found by the Tajikistan search of #610 (a country never searched),
measured 2026-09-17 16:21–16:24 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #610: a Russian search («вакансии Душанбе сайт работа Таджикистан …»)
naming the national boards; the Russian networks it also names —
`tajikistan.hh.ru` (the hh network, excluded by the owner on 14.09),
`tj.superjob.ru`, `rabotago.com` — left aside as networks, not Tajik
boards; no public employment service found online. *A measurement, not
an adapter.*

```
GET https://yora.tj/ru               200 ×2, 185 823 B, md5 f09b601fb5dc — a Next.js shell «Yora»
GET https://vazifa.tj/               200,    185 823 B, md5 f09b601fb5dc — the same body: vazifa.tj serves Yora
GET https://vazifa.tj/latest-jobs    404 ×2, 29 989 B — the indexed address is gone
```
