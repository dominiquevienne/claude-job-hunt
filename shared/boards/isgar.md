# Board measurement — ISGAR (`isgar.com.tm`, Turkmenistan): «Работа в Туркменистане» — a job board in Turkmen and Russian (Ashgabat, Mary, Türkmenabat, Daşoguz, Balkanabat) whose vacancies page is served to the declared client (689 KB) with `/vacancies/<uuid>` ads, rules open; no count stated; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: isgar.com.tm -->
<!-- script: none -->
<!-- countries: TM -->
<!-- content: measured · **`/vacancies` (200, 688 838 / 689 842 B, md5 887e7dc2e037 / 6bb13dcb6d97 — a rendered element moves) is a Tailwind-built board titled «Türkmenistanda wakansiýalar — Aşgabatda, Maryda, Türkmenabatda …» with `/vacancies/<uuid>` ad links and a Russian mirror `/ru/vacancies`; no count stated, no JobPosting; `_robots.allowed('isgar.com.tm','/vacancies')` → open, certain; the pager and the ad not read** · 2026-09-17 -->
<!-- witness: none — the page states no count · 2026-09-17 -->

**Found by the Turkmenistan search of #604 (a country never searched),
measured 2026-09-17 16:25–16:27 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #604: a Russian search («вакансии Ашхабад сайт работа Туркменистан …»)
naming the national portals and classifieds; no composed host names; no
public employment service found online. *A measurement, not an adapter.*

```
_robots.allowed('isgar.com.tm', '/vacancies')   open, certain
GET https://isgar.com.tm/vacancies               200 ×2 — the board, /vacancies/<uuid>, /ru/vacancies
```

The country's purpose-built job board (categories, salary, schedule per
its description). The pager and the ad are the adapter's first line.
