# Board adapter — Kariéra (`kariera.zoznam.sk`, Slovakia — the Zoznam portal's board): the list paged by offset, the offers sitemap and the pager's end as the site's two figures; walked 8 159 over 272 pages against a sitemap of 8 159 — the same ids, to the last one

<!-- verified: 2026-09-14 -->

<!-- hosts: kariera.zoznam.sk -->
<!-- script: kariera.py -->
<!-- host-forms: kariera.zoznam.sk -->
<!-- host-forms-basis: read — `kariera.py:HOST`, a single literal · 2026-09-14 -->
<!-- countries: SK -->
<!-- content: measured · **8 159 emitted over 272 pages by `kariera.py list --all` (02:17–02:30 UTC, 3 s between requests), the offers sitemap lists 8 159 — equal, and the two id sets are identical (0 walk-only, 0 sitemap-only); the pager ends at `?od=8130` (page 272 of 30, 8 160 at most); an employer and a date on every row, a salary text on 7 557, «Top» on 814; one ad read; the public employment service republishes this board with the same ad ids — 194 of 202 kariera rows in three pages of its all-sources list are in this sitemap** · 2026-09-14 -->
<!-- witness: the site states no count in words — its offers sitemap (`/sitemap-29052025/offers`, one request, `lastmod` per ad) is read before every walk and its distinct count printed beside the emitted count, with the pager's last page beside both: «N emitted over P page(s), sitemap lists N — equal», exit 6 on a gap; `sitemap` enumerates the file and says whether the pager's end is consistent with it; the default walk is bounded (`--pages 10`) and says so, `--all` walks the pager · 2026-09-14 -->

**The Zoznam portal's board, and a site that states no count — so both of
its figures are read and put side by side.** `/pracovne-ponuky?od=<0,30,…>`
serves thirty `div.offer` cards — the ad's link `pracovna-ponuka/<id>/<slug>`,
the title, the employer and its page, the locality, the salary as written
(«od 1524 EUR/Mesiac»), the date «14.09.2026», a «Top» badge — under a
pager whose last link is `?od=8130` (page 272). The site's other figure is
its **offers sitemap**: `/sitemap-29052025/offers`, 1.36 MB, **8 159 URLs
with `lastmod`**. `list --all` walks the pager and compares its distinct
ids to the sitemap's count; `sitemap` enumerates the file in one request.
Issue #345 (Slovakia; #291 bloc C).

## The walk

```
the offers sitemap lists 8 159 ads; the pager ends at page 272 of 30 (8 160 at most).
8 159 emitted over 272 page(s), sitemap lists 8 159 — equal.
```

2026-09-14 02:17–02:30 UTC, 3 s between requests, 272 pages. **The set of
ids read from the pages is exactly the set of ids in the sitemap** (0 on
one side only) — the sitemap is a faithful index of the list, which is
what makes `sitemap` a legitimate one-request enumeration (id, url,
`lastmod`) and `list` the read that adds the card: employer, locality,
salary text (7 557 of 8 159), date (2026-02-09 → 2026-09-14), «Top»
(814). «Top» ads repeat across pages; a key seen twice is counted once and
the tally says how many.

## The public employment service republishes this board

`sluzbyzamestnanosti.md` names kariera.sk among the six external sources
its all-sources list carries, with `urlExternyPortal` pointing at these ad
pages. Measured 2026-09-14 02:1x UTC: three pages of `sluzbyzamestnanosti.py
list --source all` (300 rows) carried **202 kariera.sk rows, all with
`https://kariera.zoznam.sk/pracovna-ponuka/<id>/…` as their URL — 194 of
the 202 ids are in this sitemap** (the 8 others: expired or not yet
indexed). **So the ids coincide, and this adapter is worth what the direct
read adds**: the state's row carries a title, an employer, a place and a
salary; the direct read carries the salary as the board writes it, the
date, the «Top» flag, the ad page's sections (description, benefits,
requirements, education, languages, employer description) and the
sitemap's `lastmod`. A user who runs `sluzbyzamestnanosti.py --source all`
and `kariera.py` sees the same ad twice under two ledgers (`sz:<uuid>`,
`kariera:<id>`); the URL is the join key.

## The ad page

`/pracovna-ponuka/<id>/<slug>`: `ul.offer-detail-info` of labelled blocks
— «Miesto práce», «Ponúkaný plat (základná mzda)», «Druh pracovného
pomeru», «Termín nástupu do práce» — then `<h2>`/`<h3>` sections:
«Informácie o pracovnom mieste», «Benefity a ďalšie výhody», «Informácie
pre uchádzača», «Všeobecne požadované znalosti», «Požiadavky na
zamestnanca» (education, languages, skills as blocks), «Informácie o
spoločnosti». Emitted by name; salary as the site's text, never parsed.

## The rules

`/robots.txt` (1 208 B, 2026-09-14): the seven translated mutations
(`/en/`, `/de/`, `/cs/`, `/pl/`, `/hu/`, `/ua/`, `/ro/`, `/ru/`), the
English routes (`/job-offers/`, `/job-offer/`…), `/*?q=*` (the free-text
search), `/rss/`, `/export/`, `/cv/`, `/salary/` are refused; the Slovak
list, its `?od=` paging, the ad pages and the sitemap are open, `certain:
True`. The guard is taken on the exact path before every request; 3 s
own spacing. The free-text search being refused in writing, the adapter
has no `--q`.

## What is withheld

A contact person's address or phone number in the prose is replaced
(`[e-mail withheld]`, `[phone withheld]` — nine digits or more, Slovak
numbers are nine); a salary («od 1 700 - 2 200 EUR», eight digits) is
never redacted, and a reference number announced by «Ref. č.:» (5 of
8 159 titles) is not a phone. One title of 8 159 carried a phone number
(«volaj 0911 …») — withheld. The employer's name and its public page are
the board's own and are emitted.

## Invocation

```
kariera.py sitemap                       # 8 159 ids with lastmod in one request, the pager's end beside it
kariera.py list                          # 10 pages, 300 rows, bounded and said so
kariera.py list --all                    # 8 159 over 272 pages, sitemap lists 8 159 — equal (2026-09-14, 14 min)
kariera.py ad --url https://kariera.zoznam.sk/pracovna-ponuka/1497703/posudkovy-lekar-posudkovy-lekar
```

Exits: 2 broken (a malformed URL) · 3 gone (404, or no `offer-detail-info`)
· 6 partial (a walk short of the sitemap's count, HTTP ≠ 200, a list
without a pager end, a sitemap without ads) · 7 refused by the rules · 8
rules undecidable.
