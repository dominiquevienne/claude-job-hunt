# Board adapter — Toptalent (`toptalent.co`, Türkiye — the graduates' board): the list's own loader nine a page until it answers nothing, the site's sitemap as the count it states — 9 emitted, 9 listed, equal on 2026-09-14

<!-- verified: 2026-09-14 -->

<!-- hosts: toptalent.co, www.toptalent.co -->
<!-- script: toptalent.py -->
<!-- host-forms: toptalent.co -->
<!-- host-forms-basis: read — `toptalent.py:HOST`, a single literal; `www.` is accepted on an ad URL · 2026-09-14 -->
<!-- countries: TR -->
<!-- content: measured · **9 emitted over 1 page by `toptalent.py list --all` (03:05 UTC), the sitemap lists 9 ad pages — equal; the loader's page 2 answers six bytes, a page size of 50 or 100 the same nine; every card carries a title, an employer, a place and a «Son N Gün» badge; one ad read, its recruiter address withheld** · 2026-09-14 -->
<!-- witness: the site states no count in words — its sitemap (`/sitemap.xml`, 3 145 URLs, the ad pages among them by their six-digit id) is read before every walk and its count printed beside the emitted count: «N emitted over P page(s), sitemap lists N — equal», exit 6 on a gap; a walk with `--q` is a search and is not compared; the default walk is bounded (`--pages 10`) and says so · 2026-09-14 -->

**A board for students and graduates, small on the day, and read the way
its page reads itself.** `/is-ilanlari` renders nine cards and scrolls the
rest in through **`POST /Job/SearchJob`** (a JSON body: `PageSize 9,
PageNumber, IsCardView, SearchKey, DepartmentIds, CityIds,
PositionLevelIds, OrderBy "newests", FilterTags, DepartmentSeo, CitySeo`)
answering an HTML fragment of `a.position` cards — the ad's link
`/<slug>-<id>`, the title, the employer, the place, a «Son N Gün» badge
(days left). The adapter posts the same body page after page until the
loader answers nothing. Issue #388 (Türkiye; #291 bloc C had counted a
3 140-URL sitemap «site entier confondu»: nine of them are ads, the id
six digits — a slug ending in a year is an article).

## The walk, and the site's figure

```
9 emitted over 1 page(s), sitemap lists 9 — equal.
```

2026-09-14 03:05 UTC. The site states no count in words; **its sitemap
lists nine ad pages**, and the loader's second page answers six bytes; a
`PageSize` of 50 or 100 answers the same nine (the loader ignores it or
the inventory ends there); a `DepartmentSeo` the page does not name
answers 500. Nine cards, nine distinct ids, an employer and a place on
each («Tüm Türkiye», «Ankara», «İstanbul Avrupa»), badges from «Son 5 Gün»
to «Son 40 Gün». A «build your CV» banner sits between two cards in the
fragment — the card pattern ends at it, and the ninth card is read (the
first draft lost one to that banner; the walk said «8 emitted, sitemap
lists 9 — 1 short» and the pattern was fixed before the card was written).

## The ad page

`/<slug>-<id>`: the title and the employer in the header card («Toptalent.co
| <title> - <employer>» in the `<title>`), «Departman», «Lokasyon»,
«Kimler Başvurabilir?» (who may apply: the years of study, as buttons —
emitted as `who_may_apply`), the «Son N Gün» badge, and the body in
`div.job-content`. **Its JSON-LD `JobPosting` is malformed** (raw control
characters inside a string) and is not read; the page is. The site
double-encodes entities («&amp;ouml;»): decoded twice. The description
ends with the recruiter's address («contact@…») — withheld.

## The rules

`/robots.txt` (594 B, 2026-09-14): `*` refuses `/App_Data/`, `/Areas/`,
`/images/`, `*/feed/`, `/Account/`, the business-school routes and one
named ad; the list, the loader `/Job/SearchJob`, the ad pages and the
sitemap are open, `certain: True`. The guard is taken on the exact path
before every request; 3 s own spacing.

## What is withheld

Addresses and phone numbers in the prose are replaced (`[e-mail
withheld]`, `[phone withheld]` — ten digits or more, Turkish numbers are
ten). The apply button needs an account and is never pressed.

## Invocation

```
toptalent.py list --all                  # 9 emitted over 1 page, sitemap lists 9 — equal (2026-09-14)
toptalent.py list --q stajyer --all      # the site's own SearchKey — a search, not compared
toptalent.py sitemap                     # the ad URLs the sitemap lists
toptalent.py ad --url https://toptalent.co/fiss-ai-video-produksiyon-stajyeri-121756
```

Exits: 2 broken (a malformed URL) · 3 gone (404, or no `job-content`) · 6
partial (a walk short of the sitemap's count, HTTP ≠ 200, a sitemap that
is not one) · 7 refused by the rules · 8 rules undecidable.
