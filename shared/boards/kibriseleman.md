# Board measurement — Kıbrıs Eleman (`www.kibriseleman.com`, Northern Cyprus): «Kuzey Kıbrıs'ın en büyük eleman platformu» — `/is-ilanlari` served with 10 ads (`/is-ilani/<id>-<slug>.html`: «Grafik Tasarımcı», «Muhasebe Personeli», «Emlak Tanıtım Hostes»), a city filter (`?city=1..6`) and no count or pager on the first page («binlerce ilan» in prose), served to the declared client (180 KB), rules open; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: www.kibriseleman.com -->
<!-- script: none -->
<!-- countries: CYN -->
<!-- content: measured · **`/is-ilanlari` (200, 179 916 B, md5 2c76e654978e / 017e734d7aa4 — a rendered element moves) lists 10 distinct ads as `/is-ilani/<id>-<slug>.html` with a city filter `?city=1` … `?city=6` and «tüm ilanları gör» links; no count («binlerce ilan» is prose), no pager link on page 1, no JobPosting; `_robots.allowed('www.kibriseleman.com','/is-ilanlari')` → open, certain** · 2026-09-18 -->
<!-- witness: none — the list states no count · 2026-09-18 -->

**Found by the Northern Cyprus search of #606 (a country never searched),
measured 2026-09-18 07:20–07:22 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #606: two searches in Turkish naming the Labour Department and the
private boards, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('www.kibriseleman.com', '/is-ilanlari')   open
GET https://www.kibriseleman.com/is-ilanlari   200 ×2 — see the content line
```

The adapter's first line: how the list pages (a `sayfa=` parameter or a load-more call), the ad's fields, a total if a filtered list states one.
