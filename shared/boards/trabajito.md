# Board adapter — Trabajito (`www.trabajito.com.bo`, Bolivia): the department page states its count on the server («736 ofertas de empleo en Bolivia» on 2026-09-16), the list is a client route the rules refuse, the sitemap names every advertisement with its department — 728 on the day — and each ad carries a JobPosting; `trabajito.py`, the count printed beside every walk

<!-- verified: 2026-09-16 -->

<!-- hosts: www.trabajito.com.bo, trabajito.com.bo -->
<!-- script: trabajito.py -->
<!-- host-forms: www.trabajito.com.bo, trabajito.com.bo -->
<!-- host-forms-basis: read — the pages and the sitemap live on `www.`, the sitemap's ad rows on the apex (`https://trabajito.com.bo/trabajo/…`), and both serve the ad; `trabajito.py` reads the sitemap on `www.` and the ads where the sitemap puts them, and accepts an ad address on either · 2026-09-16 -->
<!-- countries: BO -->
<!-- content: measured · **rules read (993 B): `User-Agent: *` — `Allow: /`, then `/api/`, `/user/`, `/dashboard`, `/login`, `/register`, `/candidato/`, `/manage-jobs`, `/crud-job`, `/company-profile`, `/applicants` … refused; `ClaudeBot` and `anthropic-ai` named with `Allow: /` in the AI-crawlers block; no Crawl-delay; `Sitemap:` declared. The root (200, 106 641 B) and `/trabajo` (200, 123 787 B) name not one advertisement — the list is a client fetch to `/api/`, refused in writing; `/empleos/bolivia` (200, 144 581 B) carries «736 ofertas de empleo en Bolivia» in its meta description and a hundred ad links in its flight data; `sitemap.xml` (200, 147 005 B) 967 rows, 728 `/trabajo/<departamento>/<slug>-<CODE>` distinct (santa-cruz 502, la-paz 99, cochabamba 67, tarija 13, chuquisaca 13, oruro 11, remoto 7, beni 6, potosi 6, pando 4; lastmod on 909 rows) and 239 facets and pages; the ad (200, 114 236 B) a JobPosting JSON-LD — title, description, identifier (name = employer, value = CODE), employmentType, hiringOrganization (name, sameAs, logo), jobLocation (locality, region, BO), datePosted, validThrough — beside a FAQPage; `trabajito.py list --limit 2` on the day: «2 emitted of the 736 the site states … (728 in the sitemap, 0 gone)»** · 2026-09-16 -->
<!-- witness: the department page's own «736 ofertas de empleo en Bolivia» in its meta, printed on the server and read by `trabajito.py list` beside the sitemap's rows; on the day 728 in the sitemap against 736 stated — 8 short, two clocks · 2026-09-16 -->
<!-- route: http · 736 · 2026-09-16 -->

**Issue #429 (opened under #411, Bolivia searched on 2026-09-13). Measured
2026-09-16 06:00–06:01 UTC by the declared client, the guard on the exact
path first, `bin/fetch-body.py`; the script exercised on the same minute.**
Rank: the pilot's risk order of 2026-09-14 10:4x, after Empléate VE (#426).

## The rules, and the one route they refuse — the list's own

```
robots.txt        200, 993 B — `*`: Allow: /, then the app's routes and the accounts refused; ClaudeBot, anthropic-ai: Allow: /; Sitemap: https://www.trabajito.com.bo/sitemap.xml
allowed('/')      open, certain          allowed('/api/…')  refused, certain — the route `/trabajo` calls to fill its cards
```

**The count is on the server, the cards are not.** `/trabajo` is a Next.js
page whose markup carries no `/trabajo/<dept>/…` link: the cards arrive by
a client fetch to `/api/`, and `/api/` is refused in writing to `*` — so
the adapter never sends it (`REFUSED_RE`, exit 7 before the gate). What the
server does print is the department page's meta: «736 ofertas de empleo en
Bolivia» on `/empleos/bolivia`, «99 ofertas de empleo en La Paz» on
`/empleos/la-paz` — the count `trabajito.py` reads and prints beside the
walk; and the sitemap is the inventory.

## The transport, dated

```
GET /                         200, 106 641 B, md5 48152c354750   (06:00:01Z)   no ad link
GET /trabajo                  200, 123 787 B, md5 c032f6708246   (06:00:13Z)   no ad link — the list is `/api/`, refused
GET /sitemap.xml              200, 147 005 B, md5 5b9e7e9ae730   (06:00:28Z)   967 rows, 728 ads distinct, 239 facets/pages
GET /empleos/bolivia          200, 144 581 B, md5 5a8f030695dd   (06:01:00Z)   «736 ofertas de empleo en Bolivia», 100 ad links in the flight data
GET https://trabajito.com.bo/trabajo/santa-cruz/reponedor-mercados-cexperiencia-santa-cruz-grupo-lucky-KBN9
                              200, 114 236 B, md5 a9b9989d970f   (06:00:42Z)   JobPosting: GRUPO LUCKY, Santa Cruz, 2026-03-09 → 2026-11-30, FULL_TIME
```

**728 in the sitemap against 736 stated — 8 short.** The two are different
clocks (the sitemap is regenerated, the counter is live); `list` prints the
verdict and does not guess which is right.

## What the adapter emits, and withholds

`sitemap` (one request): id = the CODE, url, department, slug, lastmod.
`list` (the count, the sitemap, then N ads 2 s apart — 20 unless `--limit`;
`--dept santa-cruz` narrows both the sitemap and the count): the JobPosting
— title, company, company_site, employment_type, department, place, region,
posted, valid_through, a scrubbed description. `ad --url`: the same record
for one address, on `www.` or the apex.

**Withheld:** the description is scrubbed of e-mail addresses and Bolivian
telephone numbers (`+591`, mobiles `6`/`7` + 7 digits, landlines) — a mobile
travelled in the ad page's flight data on the day and is not in the
JobPosting; `contacts_withheld` on every record; the application (a
candidate account, `/candidato/`, refused in writing anyway) never touched;
the employer's logo URL not emitted.

## Tests and mutations

`ABolivianBoardWhoseCountIsInTheDepartmentPagesMetaAndWhoseListIsARefusedClientRouteSoTheSitemapIsTheInventory`,
both ways on fixtures (the walk with a duplicate sitemap row read once, the
department filter, `--limit`, the two exit-6 cases, the refused paths, the
ad on either host). Mutation bench on a detached copy, `python3 -B`, 6 / 6
red: the stated count not read · the department filter dropped · the
description not scrubbed · the refused-path guard dropped · non-ad rows
counted as ads · the dedup on CODE dropped.
