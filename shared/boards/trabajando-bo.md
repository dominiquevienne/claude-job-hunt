# Board adapter — Trabajando Bolivia (`trabajando.com.bo`, Bolivia): a Drupal front of the Trabajando.com network that serves its list on the server («encontrarás 344 trabajos y ofertas de empleo en toda Bolivia» on 2026-09-16, 23 pages of 15) and a JobPosting per ad; `trabajando_bo.py`, the count printed beside every walk; the search, the sort and the facets refused in writing

<!-- verified: 2026-09-16 -->

<!-- hosts: trabajando.com.bo -->
<!-- script: trabajando_bo.py -->
<!-- host-forms: trabajando.com.bo -->
<!-- host-forms-basis: read — every list link, card link and JSON-LD `@id` is on the apex; `trabajando_bo.py` names it as a literal and accepts a `www.` ad address by rewriting it · 2026-09-16 -->
<!-- countries: BO -->
<!-- content: measured · **rules read (4 115 B, Drupal's file for `*`): the engine's directories, `/admin/`, `/search/`, `/search?`, `/node/add/`, `/user/logout` refused, and `/*buscar=`, `/*sort=`, `/*f[` — the keyword search, the sort and the facets — refused in writing; the plain list and its `?page=` open; no Crawl-delay. The root (200, 124 767 B) states «344 ofertas»; `/trabajo` (200, 167 881 B) serves 18 `<article data-nid>` cards — title, employer (a `/empresa/` link, a plain name, or «Empresa confidencial»), hours, city, `<time datetime>` — with a pager `?page=0 … 22` and the count in prose; `?page=1` 15 cards, `?page=22` 14: 22 × 15 + 14 = 344, equal to the stated; the ad (200, 59 996 B) a JobPosting in an `@graph` — title, employmentType, datePosted, validThrough, identifier (the nid), hiringOrganization, jobLocation (locality, region, BO), description (HTML), industry — beside a BreadcrumbList; `trabajando_bo.py list --pages 2` on the day: «33 emitted from 2 page(s) of the 23 the pager names; the site states 344»** · 2026-09-16 -->
<!-- witness: the list's own prose «encontrarás 344 trabajos y ofertas de empleo en toda Bolivia», printed on the server and read by `trabajando_bo.py list` beside the walk; 22 × 15 + 14 = 344 on the day, equal · 2026-09-16 -->
<!-- route: http · 344 · 2026-09-16 -->

**Issue #430 (opened under #411, Bolivia searched on 2026-09-13). Measured
2026-09-16 06:08–06:09 UTC by the declared client, the guard on the exact
path first, `bin/fetch-body.py`; the script exercised on the same minutes.**
Rank: the pilot's risk order of 2026-09-14 10:4x, after Trabajito (#429).

## The rules — what Drupal refuses, and the three lines that matter

```
robots.txt      200, 4 115 B — `*`: /core/, /profiles/, /admin/, /search/, /search?, /node/add/, /user/logout …, then /*buscar=  /*sort=  /*f[  (and /user/login, /user/register, /user/password re-allowed)
allowed('/trabajo')          open, certain           allowed('/trabajo?page=1')   open, certain
allowed('/trabajo?buscar=x') refused, certain        — the adapter refuses `buscar=`, `sort=`, `f[` and the accounts before the gate (exit 7)
```

**So the adapter walks the plain list and nothing else:** no keyword, no
sort, no facet — the site's own filters are the refused routes, and the
city and the category travel in the ad's path (`/trabajo/<city>/<category>/
<slug>-<nid>`) for free.

## The transport, dated

```
GET /                      200, 124 767 B, md5 bf1f6116f66a   (06:08:26Z)   «344 ofertas», the city counts
GET /trabajo               200, 167 881 B, md5 ba5111955e0d   (06:08:51Z)   18 cards (3 «Destacado» repeated from later pages), pager ?page=0 … 22, «encontrarás 344 trabajos y ofertas de empleo»
GET /trabajo?page=1        200, 155 322 B, md5 ff264d7efd14   (06:09:24Z)   15 cards
GET /trabajo?page=22       200, 151 360 B, md5 a1a633ce1657   (06:09:22Z)   14 cards — the last: 22 × 15 + 14 = 344
GET /trabajo/cochabamba/administracion-y-oficina/administrador-general-71787
                           200,  59 996 B, md5 66c0b5d2df30   (06:09:27Z)   JobPosting (@graph): «Importante Empresa», Cochabamba, 2026-09-14 → 2026-09-30, FULL_TIME
```

## What the adapter emits, and withholds

`list` (`?page=0 …` until the pager ends or a page brings nothing new, 2 s
apart, `--pages N` a bound printed as such): id = the nid, url, title,
company (three forms), company_profile, city, category, hours («Jornada
completa», «Contrato», «Pasantía», «Media jornada»), place, posted,
featured. `ad --url`: the JobPosting — title, company, employment_type,
industry, place, region, posted, valid_through, the description flattened
and scrubbed. Guards: a page without a card exits 6; page 0 served again
exits 6; the stated count missing exits 6.

**Withheld:** the description is scrubbed of e-mail addresses and Bolivian
telephone numbers — the ad read on the day carried «Enviar CV … al
76469326» in its own text; `contacts_withheld` on every record; the
application («Postular ahora», a candidate account) never touched; the
employer's logo not emitted.

## Tests and mutations

`ABolivianDrupalBoardWhoseListIsServedWithItsCountInProseAndWhoseSearchSortAndFacetsAreRefusedInWriting`,
both ways on fixtures (the three employer forms, the dedup across pages,
`--pages`, the three exit-6 cases, six refused addresses, the ad on either
host). Mutation bench on a detached copy, `python3 -B`, 6 / 6 red: the
stated count not read · the same-cards guard dropped · the dedup dropped ·
the plain-name employer form dropped · the description not scrubbed · the
query guard dropped.
