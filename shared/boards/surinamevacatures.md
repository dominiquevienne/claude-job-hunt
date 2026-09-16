# Board adapter — Suriname Vacatures (`surinamevacatures.com`, Suriname): «Stageplekken en vacatures in Suriname», a small board for Dutch-speaking students and graduates — two lists served whole (13 vacancies and 16 internships on 2026-09-16, no pager, no count printed: the lists are the count), an ad of `acf:` fields and titled sections; `surinamevacatures.py`

<!-- verified: 2026-09-16 -->

<!-- hosts: surinamevacatures.com -->
<!-- script: surinamevacatures.py -->
<!-- host-forms: surinamevacatures.com -->
<!-- host-forms-basis: read — every list, card and company link is on the apex; `surinamevacatures.py` names it as a literal and accepts a `www.` ad address by rewriting it · 2026-09-16 -->
<!-- countries: SR -->
<!-- content: measured · **rules read (122 B): `User-agent: *` — `Disallow: /wp-admin/`, `Allow: /wp-admin/admin-ajax.php`, `Sitemap: /wp-sitemap.xml` (which answers 404 with its index in the body); no Crawl-delay. The root (200, 60 894 B, identical to 2026-09-13); `/vacatures-suriname` (200, 67 080 B) 13 `vacatures-item-wrapper` cards and `/stageplekken-suriname` (200, 75 595 B) 16 — `<h2 item="title">`, `acf:text="plaatsnaam"` (the place), `acf:text="uren"` (the hours, absent on internships), an `inline-text` level («MBO», «MBO, HBO, WO»), `categ` labels, a `/vacatures/<slug>/` link (the internships live under the same path) — no pager, no total anywhere; the ad `/vacatures/<slug>/` (200, 35 311 B) `<h2 item="title">`, `acf:text="bedrijfsnaam"` (the employer), `plaatsnaam` twice (the place, then the level — the site reuses the attribute), `uren`, `loon` («€ Uurloon vanaf 25,- srd per maand»), `acf:textarea="periode"`, `acf:richtext` sections under `*_titel` headings («Bedrijfsprofiel», «Wie ben jij?», «Wat ga je doen?», «Wat bieden wij?», «Geïnteresseerd in deze functie?» — the last names the site's own address); no JobPosting, no dates; `surinamevacatures.py list` on the day: «29 emitted — 13 vacatures and 16 stages on the list(s), the site prints no total: the lists are the count»** · 2026-09-16 -->
<!-- witness: none — the site prints no total; each list's own card count is printed by `surinamevacatures.py list` beside the emitted, and that is the count · 2026-09-16 -->
<!-- route: http · 29 · 2026-09-16 -->

**Issue #446 (opened under #416, Suriname searched on 2026-09-13). Measured
2026-09-16 21:42–21:43 UTC by the declared client, the guard on the exact
path first, `bin/fetch-body.py`; the script exercised on the saved bodies
and on the host.** Rank: the pilot's risk order of 2026-09-14 10:4x, after
Werkstraat (#445).

## What the board is

A bridge board («Met Suriname vacatures slaan wij een brug tussen
buitenlandse expertise en het Surinaams bedrijfsleven»): Surinamese
employers post vacancies and internships aimed at students and graduates
from the Netherlands. Two lists, twenty-nine cards on the day, the whole
inventory on two pages — small, and exactly the kind of board the 08.09
rule says is used anyway.

## The rules, the transport

```
robots.txt                  200, 122 B — `*`: Disallow: /wp-admin/, Allow: /wp-admin/admin-ajax.php, Sitemap: /wp-sitemap.xml
GET /                       200, 60 894 B, md5 adffd5287554   (21:42:18Z)   identical to 2026-09-13
GET /vacatures-suriname     200, 67 080 B, md5 4c6df086ca5e   (21:42:35Z)   13 cards, no pager
GET /stageplekken-suriname  200, 75 595 B, md5 303597275659   (21:42:40Z)   16 cards, no pager
GET /wp-sitemap.xml         404, 845 B — the index in the body (pages, bedrijven, blog, vacatures, social-media, filters, users)
GET /vacatures/admin-officer/   200, 35 311 B, md5 30dc9a82f384   (21:43:10Z)   the fields and sections
```

`/wp-admin/`, `/wp-json/`, `/xmlrpc.php` are never sent (exit 7 before the
gate).

## What the adapter emits, and withholds

`list [--kind vacatures|stages|all]` (one request per list): id (the slug),
url, kind, title, place, hours, level, categories; a card on both lists is
read once and the note says so. `ad --url`: title, company, place, level,
hours, pay (as written), period, and the sections as a map of heading →
scrubbed text. Guards: a list without a card exits 6; an ad without its
title and `bedrijfsnaam` exits 6.

**Withheld:** the sections are scrubbed of e-mail addresses (the site's
own `info@` in «Geïnteresseerd in deze functie?» included) and Surinamese
telephone numbers; `contacts_withheld` on every record; «Solliciteren» (a
form on the site) never touched; the employer's logo not emitted.

## Tests and mutations

`ASmallSurinameseBoardWhoseTwoListsAreServedWholeWithoutACountAndWhoseAdIsACFFieldsAndTitledSections`,
both ways on fixtures (the two lists with a card on both read once, three
categories on one card and none on another, an internship without hours,
`--kind`, the exit-6 cases, three refused addresses, the ad with the level
under the second `plaatsnaam`, the period, the sections scrubbed). Mutation
bench on a detached copy, `python3 -B`, 6 / 6 red: the card's tail cut
early · the level not read · the sections not scrubbed · the second
`plaatsnaam` not read as the level · the dedup across lists dropped · the
kind not set.
