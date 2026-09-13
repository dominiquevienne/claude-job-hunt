# Board measurement — OLX Kazakhstan (`www.olx.kz`, Kazakhstan): 403 to the declared client, served to a browser — «более 1 000 объявлений» on a listing capped at 25 pages, 15 290 across 28 categories

<!-- verified: 2026-09-13 -->

<!-- hosts: www.olx.kz, olx.kz -->
<!-- script: none -->
<!-- countries: KZ -->
<!-- content: measured · **a browser tab is served — `/rabota/` 200, 52 advertisement links a page, the page states «Мы нашли более 1 000 объявлений» (a floor) and its pager stops at 25; the 28 category links on the same page carry counts summing to 15 290 — a sum of categories, an upper bound, not the board's size**; the declared client gets a 403 (919 B, md5 moving) on the same path; tab 16:28 UTC · 2026-09-13 -->
<!-- witness: the page's own «более 1 000» and pager (25 × 52), page 25 read by `fetch()`; the category counts are the site's own per-category figures, summed here — a bound · 2026-09-13 -->
<!-- route: browser · 1000 · 2026-09-13 -->
**In the #222 candidate list from the Kazakhstan country page as a «403
to the plain client, browser not measured».** *A measurement and not an
adapter, and a short one: the guard closed the question at the rules
file, the same shape as `kazibongo.md` and `barbadosjobregister.md`.*
Measured 2026-09-13 12:19:40 UTC with the declared client.

## The rules file is refused — twice

```
GET https://www.olx.kz/robots.txt     403 · CloudFront («Error from cloudfront») · 12:19:40 UTC   (bin/fetch-body.py, body not kept by the tool)
GET https://www.olx.kz/robots.txt     403 · the same, 2 s later
_robots.allowed('www.olx.kz', '/')    allowed False · certain True · rule "/" · rule_kind host-closed
```

**A `403` on the rules file is a refusal, and the doctrine keeps it one**
(the 2026-09-09 decision reopened `401` alone). No path is open, so the
browser branch — «the rules open, the transport refuses» — has nothing to
start from: **nothing beyond the rules file was requested, no tab was
opened.** *A refusal at the rules does not say what it refuses — a front
rule on `/robots.txt`, a firewall keyed on our identity, or a host that
serves no rules to anyone look the same from here.*

## What reopens it

- `robots.txt` answering anything but 403 to the declared client;
- a later pair of reads minutes apart (`grabjobs.co` once cleared within
  seconds — `robots-policy.md`);
- a doctrine decision on a 403 *at the rules file* — posed by
  `kazibongo.md`, `barbadosjobregister.md` and this card, not decided by
  them. **Eleven hosts now sit on that question.**

## What this card does not say

Nothing about what the site serves, its size, or whether a browser is
served — a browser was not opened.

## 2026-09-13 — #283: an unread rules file is an absence of rules, and the transport measured

**Owner's decision of 2026-09-13, verbatim: «toutes incapacité d'ouvrir robots.txt
doit aboutir à l'absence de règles et donc à l'ouverture».** This card read
«route: none — CloudFront (13.09)» — a verdict taken on the rules file alone. Since #283 the 403 on
`/robots.txt` is `no-rules-403`, `allowed: True, certain: False`: nothing
was read, nothing forbids, and **the transport decides**. Measured with
`bin/fetch-body.py --allow-refusal` under the new guard, the root (and a
listing path where one was known) twice:

```
GET https://www.olx.kz/                                  403, 919 B, md5 4f15d67f5c63   (15:29:49Z)
GET https://www.olx.kz/                                  403, 919 B, md5 be2312ec4c78   (15:29:50Z)
GET https://www.olx.kz/rabota/                           403, 919 B, md5 f0778d8df2d2   (15:29:51Z)
GET https://www.olx.kz/rabota/                           403, 919 B, md5 83ee0f7ed6f5   (15:29:52Z)
```

**The transport answers a **static 403** — the same bytes on every fetch: a refusal at the transport aimed at the client, family (1) of #222, where a browser is legitimate and is not measured here.** *A verdict of closure was never
this card's to give (§2 sexies); what it gives now is a dated transport
reading, and the class it falls in.*

## 2026-09-13 16:28 UTC — the browser route, MEASURED (#222): served, capped, counted by category

```
tab: /rabota/                      200 «Работа в Казахстане. Вакансии …» — no challenge; 52 /obyavlenie/ links
                                   «Мы нашли более 1 000 объявлений» — MORE THAN 1 000: the floor the site prints on a capped listing
                                   pager … ?page=25 (last link)  ·  fetch ?page=25  200, 52 links
tab: 28 categories with a count each — Транспорт / Логистика / Склад 3 266 · Производство 2 111 · Строительство 1 830 · Бары / рестораны / кафе 1 587 · Розничная торговля 1 547 · Домашний персонал 988 · СТО / автомойки 880 · Работа за рубежом 706 … HR 5 · Топ-менеджмент 5   → **15 290 summed**
```

**The same template as `olx-pl.md`, the same reading**: the 403 is for
the declared client alone, the tab is served without a challenge; the
site states a floor and per-category figures; the listing loops at 25
pages. Four categories are above the 1 000 the route can page
(transport, production, construction, restaurants). **15 290 is the sum
of the site's own per-category figures — a bound on the board, not a
count of what the route reads.** The JSON API the page calls was not
tried (see the Polish card).
