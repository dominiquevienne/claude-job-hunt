# Board measurement — KKTC Portal — iş ilanları (`kktcportal.net`, Northern Cyprus): «KKTC İş İlanları - Bölge Bölge Güncel İş Fırsatları» — the jobs section of a regional portal, `/is-ilanlari` served with 24 ads (`/is-ilanlari/<slug>-<district>-<id>`: «Muhasebe Personeli Lefkoşa», «Depo Personeli», «Bilgi Teknolojileri IT Uzmanı») and a pager `?sayfa=2` … `?sayfa=17`, no count stated, served to the declared client (375 KB), rules open; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: kktcportal.net -->
<!-- script: none -->
<!-- countries: CYN -->
<!-- content: measured · **`/is-ilanlari` (200, 375 033 B, md5 d0f24e297e25 / 1cdab24cea82 — a rendered element moves) lists 24 distinct ads as `/is-ilanlari/<slug>-<district>-<id>` with a pager `?sayfa=2`, `?sayfa=3` … `?sayfa=17` (at most 17 × 24 = 408, not stated); no JobPosting; `_robots.allowed('kktcportal.net','/is-ilanlari')` → open, certain** · 2026-09-18 -->
<!-- witness: none — no count stated; the pager bounds the list (17 pages) · 2026-09-18 -->

**Found by the Northern Cyprus search of #606 (a country never searched),
measured 2026-09-18 07:20–07:22 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #606: two searches in Turkish naming the Labour Department and the
private boards, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('kktcportal.net', '/is-ilanlari')   open
GET https://kktcportal.net/is-ilanlari   200 ×2 — see the content line
```

The adapter's first line: the 17 pages, the ad's fields (the dates in the markup are odd — «26/05/1779» — and to be read on the ad).
