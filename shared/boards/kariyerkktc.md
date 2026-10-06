# Board measurement — Kariyer KKTC (`kariyerkktc.com`, Northern Cyprus): «İş İlanları - Kariyer KKTC» — a WordPress 7.1 site (Elementor) whose `/is-ilanlari/` page carries no ad, count or listing (its schema dates it modified 2023-09-20), a `/jobs/` link and a posting form, served to the declared client (112 KB), rules open; **`/jobs/` is now READ and it lists NOTHING of its own: its 11 `/job/` links all point to `apusthemes.com/wp-demo/superio/`, the THEME VENDOR'S DEMO SITE** — and no sitemap of the eight declared carries a single advert URL, while the blog is maintained to 2026-01-06; a live site with employers and articles and zero vacancies of its own; no adapter, and the write-off is NOT declared here

<!-- verified: 2026-10-02 -->

<!-- hosts: kariyerkktc.com -->
<!-- script: none -->
<!-- countries: CYN -->
<!-- content: measured · **`/jobs/` (200, 55 985 B) is READ at last and carries NO advert of this site: zero `<article>`, zero internal advert link, and its **11 `/job/<slug>` matches are menu items whose `href` is `https://apusthemes.com/wp-demo/superio/job/…` — the Superio theme's DEMO site on the vendor's own domain** (junior-graphic-designer-web, finance-manager-health, software-engineer…). Its whole visible text is that demo navigation («Job - Single 1» … «Job - Apply Email»), 298 characters. The declared sitemap is an INDEX of 8: post (79 `<loc>`, lastmod to **2026-01-06**, real Turkish articles on the KKTC job market), page, product, employer (10 `<loc>`, 9 real `/işveren/<slug>/` profiles, lastmod to 2025-01-24), apus_megamenu, category, employer_category, candidate_location — **and NOT ONE of the eight is a job sitemap; advert-shaped URLs across all of them: ZERO**. `/is-ilanlari/` (200, 111 362 B) still carries no `<article>` and no advert link The rules file is served (`state: read`, `certain: True`, group `*`, NO Crawl-delay — 2 s are ours) and it DECLARES `sitemap.xml`.** · 2026-10-02 -->
<!-- content: measured · **`/is-ilanlari/` (200, 111 528 B, md5 acde7f199e9d / 3a2da960fe74 — a rendered element moves) is a WordPress 7.1 page with Elementor and no `<article>`, no ad link, no count; its JSON-LD `@graph` is Organization / WebSite / WebPage / Person / Article (dateModified 2023-09-20), no JobPosting; links `/jobs/`, `/is-olustur/` (post a job), `/giris-yap-kayit-ol/`; `_robots.allowed('kariyerkktc.com','/is-ilanlari/')` → open, certain** · 2026-09-18 -->
<!-- witness: none, and now for a MEASURED reason: no advert exists to count — the site's only job links belong to its theme vendor's demo · 2026-10-02 -->

<!-- witness: none — the page lists nothing · 2026-09-18 -->

**Found by the Northern Cyprus search of #606 (a country never searched),
measured 2026-09-18 07:20–07:22 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #606: two searches in Turkish naming the Labour Department and the
private boards, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('kariyerkktc.com', '/is-ilanlari/')   open
GET https://kariyerkktc.com/is-ilanlari/   200 ×2 — see the content line
```

## Re-measured 2026-10-02 — `/jobs/` is read, and it is the THEME's demo, not a listing

```
/jobs/                 55 985 o   0 <article>   11 liens /job/  ->  TOUS vers apusthemes.com
/is-ilanlari/         111 362 o   0 <article>   0 lien d'annonce
sitemap.xml (INDEX)    8 sous-sitemaps          0 sitemap d'annonces, 0 URL d'annonce
  post-sitemap          79 <loc>   lastmod -> 2026-01-06   des articles REELS
  employer-sitemap      10 <loc>   lastmod -> 2025-01-24   9 profils /isveren/ REELS
```

**The question this card left open on 2026-09-18 is answered: `/jobs/` lists nothing of this
site.** *Its eleven `/job/<slug>` matches are menu items pointing at
`https://apusthemes.com/wp-demo/superio/job/…` — the **Superio theme's demonstration site, on the
theme author's own domain**.* **The whole visible text of the page is that demo navigation —
«Job – Single 1», «Job – Apply Email» — 298 characters.**

> **Counting a URL pattern can measure the THEME rather than the board.** *Same family as
> «counting a keyword measures the translation» and «a taken-over domain keeps its robots.txt»: the
> pattern matched eleven times, every match was real, and **not one of them was this board's
> advert**.* **And following them would have left the host entirely** — our guard refuses another
> host, which is the control that would have caught it mechanically.

### The site is ALIVE, and that is what makes the absence meaningful

**This is not an abandoned install.** *The post sitemap carries **79 real Turkish articles** on the
Northern Cyprus job market with `lastmod` up to **2026-01-06**, and the employer sitemap carries
**9 real employer profiles**.* **So «no advert» is not «nobody looked» and not «the site is
gone»: it is a maintained site that publishes articles and employer pages and no vacancies.**

### No write-off is declared here

**Eight sitemaps are declared and NOT ONE is a job sitemap; advert-shaped URLs across all eight:
zero.** *That is a dated measurement.* **It is NOT a verdict that the host is closed — §2 sexies
reserves that to the owner's express validation**, and the measurement is carried to #725 for that
decision. *A route to nothing is not coverage, so no adapter is written; and «no adapter» here
means «there is nothing to enumerate», not «nobody measured».*

**Re-measured 2026-10-02 by the declared client, the guard on each exact path first,
`bin/fetch-body.py`, provenance beside every body.** *A measurement, not an adapter.*

```
_robots.verdict('kariyerkktc.com')   state: read, certain: True, group '*', delay: None,
                                     sitemaps: ['https://kariyerkktc.com/sitemap.xml']
GET /jobs/ · /is-ilanlari/ · /sitemap.xml · /post-sitemap.xml · /employer-sitemap.xml   — all 200
```
