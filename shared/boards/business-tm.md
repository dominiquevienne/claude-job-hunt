# Board measurement — Business Turkmenistan — vacancies (`business.com.tm/ru/work/rabota/vakansii`, Turkmenistan): the business portal's job notices served to the declared client (43 KB, identical twice) — ten `/ru/work/<id>` notices dated on the day, a pager `/ru/work/a/index?path=rabota/vakansii&p=N`, rules open; no count stated; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: business.com.tm -->
<!-- script: none -->
<!-- countries: TM -->
<!-- content: measured · **`/ru/work/rabota/vakansii` (200, 43 128 B, md5 f6c46cd30e8a identical on two reads) lists ten notices `/ru/work/<id>` («Помощник генерального директора», 17.09.2026, «Описание вакансии …») with a pager `/ru/work/a/index?path=rabota%2Fvakansii&p=N`; no count stated, no JobPosting; `_robots.allowed` → open, certain; the pager's end and the notice not read** · 2026-09-17 -->
<!-- witness: none — the page states no count · 2026-09-17 -->

**Found by the Turkmenistan search of #604 (a country never searched),
measured 2026-09-17 16:25–16:27 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #604: a Russian search («вакансии Ашхабад сайт работа Туркменистан …»)
naming the national portals and classifieds; no composed host names; no
public employment service found online. *A measurement, not an adapter.*

```
_robots.allowed('business.com.tm', '/ru/work/rabota/vakansii')   open, certain
GET https://business.com.tm/ru/work/rabota/vakansii               200 ×2, identical — ten /ru/work/<id> notices, a pager
```
