# Board adapter — Eleman.net (`www.eleman.net`, Türkiye): the old generalist of manual trades and the provinces, its server-rendered list open under rules that refuse the search — 243 pages of 30 stated by the pager on 2026-09-14, no total stated; the ad's JobPosting and boxes read, the masked «İletişim» block never

<!-- verified: 2026-09-14 -->

<!-- hosts: www.eleman.net, eleman.net -->
<!-- script: eleman.py -->
<!-- host-forms: www.eleman.net -->
<!-- host-forms-basis: read — every card's address and the pager's options are absolute on `www.eleman.net`; `eleman.py` names that host as a literal and refuses an ad address on any other · 2026-09-14 -->
<!-- countries: TR -->
<!-- content: measured · **`/is-ilanlari` (200, 284 279 B) prints 30 cards a page and a pager whose select reads «1 / 243» — the site's own page count; `?sy=243` answers 18 cards, so the list held about 7 278 postings, inferred from the pager, not stated; `/is-ilanlari/istanbul?sy=2` 30 cards, «2 / 125»** — read by the declared client, the guard on the exact path, 01:5x UTC; the rules (473 B, `*`) refuse the legacy `.asp/.html/.htm` addresses, the search and its parameters (`*?t=*`, `*?ilan_id=*`, `*?tip=*` …) and the application pages (`basvuru_yap.php`, `cv_guncelle.php`), nothing of the list, its `?sy=` pager or `/is-ilani/<slug>-i<id>`; no sitemap (`/sitemap.xml` 404, 2026-09-01); 90 read in 3 pages, 45 of them «Telefonla başvuru», 20 with a salary stated, 1 urgent; the ad (108 250 B) carries a JSON-LD JobPosting with `baseSalary` (`45000`, `unitText` MONTH) beside the box «Maaş: 45.000 TL», «Kişi Sayısı: 2», the gender wanted, the age range; **the «İletişim» block prints telephone numbers the site masks («0537 611 ** **») and unmasks to a signed-in account only — never read; one of four descriptions read carried a number in clear, scrubbed** · 2026-09-14 -->
<!-- witness: the pager's own «N / 243» — the site's page count, printed beside every walk («90 emitted over 3 of the 243 page(s) the pager states … walked by request»); the site states no total, and the adapter says so rather than sum the pages; a 200 page without one card exits 6 · 2026-09-14 -->

**Eleman.net is the Turkish generalist of the manual trades and the
provinces — waiters, warehouse staff, CNC turners, security guards, from
Çankaya to Çorlu — with 243 pages of 30 on the day, half of them
applied to by telephone.** Issue #384. Measured 2026-09-14 01:5x UTC by
the declared client, the guard on the exact path before each request.
Beside İŞKUR (`iskur.md`, the public service) and İşin Olsun
(`isinolsun.md`, not feasible under #404), it is Turkey's first readable
private generalist.

## Rules and the routes

```
www.eleman.net/robots.txt                 200, 473 B — User-agent: *: Disallow /*.asp$ /*.html$ /*.htm$  *?t=arama*  *?yazi=*  *?uyelik_tipi=*  *?tip=*  *?ilan_id=*  *?t=*  *?wbtrck=*  /favori.php /resim_goster.php /uye_yorum.php /dogrulama_kodu.php /basvuru_yap.php /cv_guncelle.php /eleman.php /is_ilanlari.php /firmalar.php /arama_complete.php
GET https://www.eleman.net/                       200, 327 009 B — the front: career pages, «Maaş: 35.000 ₺» salary guides, the newest cards
GET https://www.eleman.net/is-ilanlari            200, 284 279 B — «iş ilanları», 30 cards, pager «1 / 243», «Sonraki» → ?sy=2
GET https://www.eleman.net/is-ilanlari?sy=243     200, 354 655 B — 18 cards, «243 / 243», no «Sonraki»
GET https://www.eleman.net/is-ilanlari/istanbul?sy=2   200, 394 778 B — «İstanbul iş ilanları», 30 cards, «2 / 125»
GET https://www.eleman.net/is-ilani/tecrubeli-garson-sinpas-cankaya-net-45-000-tip-i4762495   200, 108 250 B — JSON-LD JobPosting + BreadcrumbList, boxes, description, «İletişim» masked
```

**The rules refuse the site's search parameters by name and leave the
pager's `sy` alone: `sy` is the only parameter the adapter ever sends,
and any other is refused before the gate (exit 7).** The legacy
`.asp/.html` addresses are refused too; the current ones carry no
extension. No Crawl-delay; 2 s is the adapter's own.

## The list — the pager is the witness

```
eleman.py list --pages 3
[eleman] 90 emitted over 3 of the 243 page(s) the pager states for /is-ilanlari, 30 a page — walked by request (--pages/--limit), not a shortfall; the site states no total.
[eleman] the ad's «İletişim» block — telephone numbers the site masks — is never read; descriptions scrubbed; the application form is refused in writing and never touched.
eleman.py list --city istanbul --pages 2 --limit 45
[eleman] 45 emitted over 2 of the 125 page(s) the pager states for /is-ilanlari/istanbul, 30 a page — walked by request …
```

The site prints no total; **the pager's «N / 243» is its own page
count, and the adapter prints it beside the pages walked** rather than
multiply it (the last page held 18, so ~7 278 on the day — inferred,
never printed as the site's). A card: the ad's address with the id at
its tail (`-i4762495`), title, employer, place («Ankara - Çankaya»), the
benefits line («Servis, Yemek, Prim»), a snippet scrubbed, and three
badges — `urgent` («ACİL İLAN»), `apply_by_telephone` («Telefonla
başvuru yapabilirsiniz» — the badge, never the number), `salary_stated`
(«Maaş Bilgisi Olan») — and `highlighted` for a paid, coloured card
(`renkli-ilan`, 6 of 18 on the last page). No date on the card; the
list is newest-first and the ad carries the dates. `--city <slug>` walks
`/is-ilanlari/<slug>` (istanbul, ankara, izmir … the site's own slugs).
**A 200 page without one card exits 6** — a changed template, never an
empty market.

## The ad

```
eleman.py ad --url https://www.eleman.net/is-ilani/tecrubeli-garson-sinpas-cankaya-net-45-000-tip-i4762495
{"id": "4762495", "title": "Tecrübeli Garson / Sinpaş Çankaya / Net 45 000+Tip", "employer": "Sinpaş John Filippo", "employer_url": "https://www.eleman.net/firma/sinpas-john-filippo-f2118906", "locations": ["Ankara - Çankaya"], "region": "Ankara",
 "employment_type": "Tam Zamanlı", "industry": ["Restorancılık"], "salary_text": "45.000 TL", "salary_min": 45000, "salary_max": 45000, "salary_currency": "TRY", "salary_unit": "month", "salary_unit_stated": true,
 "benefits": "Yemek", "positions": 2, "gender_wanted": "Kadın veya Erkek", "age_range": "24 - 55 arası", "posted": "2026-09-14", "valid_through": "2026-10-14", "description": "…", "contacts_withheld": true}
```

The JSON-LD JobPosting gives title, `datePosted`, `validThrough`,
`employmentType`, `jobBenefits`, `industry`, the employer and its
`/firma/` page, the addresses («Ankara,Çankaya» + region → «Ankara -
Çankaya»), and `baseSalary` with `unitText` MONTH — **a period, so
`salary_unit_stated` is true; when the posting carries no `baseSalary`
the box «Maaş: 1.250.000 TL» is read — «45.000» is forty-five thousand,
the dot a thousands separator — with no period stated**. The boxes give
«Kişi Sayısı» (positions), the gender wanted, the age range, the
contract. The description (`d-information`) is scrubbed of Turkish
telephone numbers — `0537 611 22 33`, `0 (212) …`, `+90 …`, and the
site's own masked shape — and of e-mail addresses. **The «İletişim»
block is never read: the site masks the numbers and unmasks them only to
a signed-in account, and the plugin never signs in; the application form
(`basvuru_yap.php`) is refused in writing.**

## Configuration

```yaml
boards:
  eleman:
    enabled: true
    city: istanbul        # optional — the site's slug; the whole country otherwise
    pages: 10             # 30 a page
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `city` | no | `/is-ilanlari/<slug>` |
| `pages` | no | 10 by default; the pager states 243 for the country |

No credentials, no browser, no login. `list` is one request a page;
`ad` is one.

## What is not established

- **A total** — the site prints none; 243 × 30 − 12 is arithmetic on the
  pager, not a statement.
- **The order of the list** — newest-first by the ids and dates seen on
  page 1 and page 243; not asserted by the site.
- **Fields beyond the day's sample** — an ad without a JSON-LD block
  falls back to the description block; none seen without both.
- **Whether the front's «Maaş: 35.000 ₺» salary guides relate to the
  ads** — they are career pages, not read.

## 2026-09-14 — shipped

`list`: 90 of 3 pages against the pager's 243, 45 on the Istanbul list
against 125; every card with an id, an employer and a place, no address
in the output. `ad` on four: one description carried a telephone number
in clear — scrubbed; the masked block never in the output. Two tests;
six mutations on a detached worktree (`python3 -B`), six red — the
parameter guard dropped, the highlighted card's class tail not matched,
the pager's count not read, the thousands dot read as a decimal
(bitten once the fixture carried a posting without `baseSalary`), the
description not scrubbed, the positions box not read.
