# Board measurement — Korgar (`korgar.tj`, Tajikistan): «Работа в Душанбе, Худжанде, в Таджикистане, вакансии и резюме» — the root served to the declared client (269 KB, identical twice) claims «Более 3000 вакансий», lists 21 ads and a pager `/vakancii?page=N` to 40, rules open; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: korgar.tj -->
<!-- script: none -->
<!-- countries: TJ -->
<!-- content: measured · **the root (200, 269 096 B, md5 b15ad3af2ae7 identical on two reads) claims «Более 3000 вакансий» (more than 3 000 — a round marketing claim), lists 21 ads as `/vakanciya/<slug>_<id>` (Russian and Tajik titles: «официант», «SEO мутахассиси»), category lists `/vakancii/<category>` and a pager `/vakancii?page=2 … 40`; no exact count, no JobPosting; `_robots.allowed('korgar.tj','/')` → open, certain; the list, the pager's end and the ad not read** · 2026-09-17 -->
<!-- witness: the root's «Более 3000 вакансий» is a claim; the pager's 40 pages are the bound to read · 2026-09-17 -->

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
_robots.allowed('korgar.tj', '/')   open, certain
GET https://korgar.tj/               200 ×2, identical — 21 ads, /vakanciya/<slug>_<id>, /vakancii?page=2 … 40, «Более 3000 вакансий»
```

The national generalist (Dushanbe, Khujand). `/vakancii?page=N`, its
last page, and the ad are the adapter's first line (its `adapter` issue).
