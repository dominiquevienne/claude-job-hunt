# Board measurement — Turkmenportal — work section (`turkmenportal.com/work/…/vakansii-v-turkmenistane`, Turkmenistan): the national portal's classified vacancies, served to the declared client (403 KB), rules open; the ads are free-text notices that carry the advertisers' phone numbers; no count stated; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: turkmenportal.com -->
<!-- script: none -->
<!-- countries: TM -->
<!-- content: measured · **the vacancies page (200, 403 256 B, md5 364902254902 / 88c760486f3e — a rendered element moves) is the portal's classified section: dated notices in Russian («ХО «Зехинли Иш» предлагает следующие вакансии …», an agency's list, employers' calls) with telephone numbers in the text, category links `/ru/advertisement/work/category/<N>-rabota`; no count stated, no JobPosting; `_robots.allowed` → open, certain; the pager and the notice pages not read** · 2026-09-17 -->
<!-- witness: none — the section states no count · 2026-09-17 -->

**Found by the Turkmenistan search of #604 (a country never searched),
measured 2026-09-17 16:25–16:27 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #604: a Russian search («вакансии Ашхабад сайт работа Туркменистан …»)
naming the national portals and classifieds; no composed host names; no
public employment service found online. *A measurement, not an adapter.*

```
_robots.allowed('turkmenportal.com', '/work/rabota-v-turkmenistate/vakansii-v-turkmenistane')   open, certain
GET …/vakansii-v-turkmenistane   200 ×2 — dated free-text notices, phone numbers in the text, category links
```

**The notices carry the advertisers' telephone numbers in their text** —
an adapter scrubs them (Turkmen numbers, `+993`); the pager and what a
notice page carries are the adapter's first line (its `adapter` issue).
