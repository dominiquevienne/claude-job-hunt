# Board measurement — Yenibiriş (`www.yenibiris.com`, Turkey — the Hürriyet group's board): a moving Cloudflare challenge to the declared client, and a browser served the whole board — «6344 iş ilanı listelendi» stated, 25 a page, a pager capped at 100 pages, a JobPosting per ad; `route: browser`, no script

<!-- verified: 2026-09-14 -->

<!-- hosts: www.yenibiris.com -->
<!-- script: none -->
<!-- countries: TR -->
<!-- content: measured · **the declared client gets a 403 of 5 651 B with a moving md5 on the root and on the rules (2026-09-13 — the Cloudflare challenge family, borne 2: never defeated, nobody asked to defeat it); a connected tab is served without any challenge or interaction: the front page (city, category and «İş Bulma Makinesi» facets, ads `/is-ilani/<slug>/<id>`, employers `/firma/<slug>/is-ilanlari/<id>`), `/is-ilanlari` with the site's own «6344 iş ilanı listelendi» (Türkiye 5 287 — the rest abroad), 25 cards a page (title, employer or «Şirket Bilgileri Gizli», city and district, «Sponsorlu», age — «Bugün», «Son 1 Hafta», «Son 1 Ay» —, working time and place), facet counts for 81 cities, 40 categories and 50 sectors, a pager `?sayfa=2 … 100` — page 100 exists and is the last, `?sayfa=254` is rewritten to page 1: the plain walk reaches 2 500 of the 6 344, the city or category facets partition the rest; each ad carries a JobPosting JSON-LD (jobBenefits, datePosted, description, educationRequirements, employmentType, experienceRequirements, industry, jobLocation, occupationalCategory, title, hiringOrganization, validThrough, url) beside WebSite / BreadcrumbList / Organization (the employer's telephone and address in the Organization node — never to be emitted); the application («BAŞVUR») is the candidate account, never touched** · 2026-09-14 -->
<!-- witness: the site's own «6344 iş ilanı listelendi» on `/is-ilanlari`, read on page 1 and page 100 (09:4x UTC); the pager caps at 100 × 25 = 2 500, so a walk prints its own figure against the 6 344 and says what the cap leaves to the facets; nothing was served to the declared client, so no script prints anything · 2026-09-14 -->
<!-- route: browser · 6344 · 2026-09-14 -->

**Yenibiriş is the Hürriyet group's generalist — 6 344 advertisements
stated on the day, education first (2 849), then sales and hospitality.**
Issue #386. Measured 2026-09-14 09:41–09:45 UTC from a connected tab —
begun before the pilot's risk order of 09:4x reached this session, and
finished rather than dropped.

## What the client gets, and what a tab gets

```
client, GET /robots.txt, GET /        403, 5 651 B, md5 moving between two reads (2026-09-13) — a challenge, never defeated
tab, /                                served — the front page, no challenge shown, no interaction
tab, /is-ilanlari                     served — «6344 iş ilanı listelendi.», 25 cards, pager ?sayfa=2 … 8 … 100, «Sonraki»
tab, /is-ilanlari?sayfa=100           served — «Sayfa 100» in the title, the last page (no «Sonraki»)
tab, /is-ilanlari?sayfa=254           rewritten to /is-ilanlari — page 1 again: the pager caps at 100
tab, /is-ilani/temizlik-personeli/1164367   served — a JobPosting: AÇI EĞİTİM KURUMLARI, 2026-09-12 → 2026-12-31
```

**`route: browser · 6344 · 2026-09-14`.** What a session does from a tab:
`/is-ilanlari?sayfa=N` to 100, then the city facets (81, each its own
pager) for what the cap leaves, the id from `/is-ilani/<slug>/<id>`, the
page's «N iş ilanı listelendi» beside the walk, the ad's JobPosting — the
Organization node's telephone and address withheld. No script: nothing is
served to a client (#404). Turkey's other measured fronts are `secretcv.md`,
`eleman.md` and `iskur.md`; Kariyer.net (#383) is the same challenge
family, not measured here.
