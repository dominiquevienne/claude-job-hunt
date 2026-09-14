# Board adapter — Állásportál (`allasportal.hu`, Hungary): the generalist of manual trades and agency work, at the thirty seconds its rules ask — «8661 állás» stated on 2026-09-14, 8 670 hosted ads in its job sitemap, never merged; the ads it gathers from other boards carried as their card, their only address refused in writing and never followed; the hosted ad's contact block scrubbed

<!-- verified: 2026-09-14 -->

<!-- hosts: allasportal.hu, www.allasportal.hu -->
<!-- script: allasportal.py -->
<!-- host-forms: allasportal.hu -->
<!-- host-forms-basis: read — every card link, sitemap row and pager link is absolute on `allasportal.hu` without `www.`; `allasportal.py` names that host as a literal and builds every address on it · 2026-09-14 -->
<!-- countries: HU -->
<!-- content: measured · **`/munka/list` states «8661 állás - összegyűjtöttük a nagy állásoldalak összes találatát» (200, 135 251 B, 02:1x UTC) — 15 cards a page, 722 pages, 13 hosted and 2 redirected on page 1, 30 read in 2 pages; `sitemap_job.xml` (200, 1 167 855 B) carries 8 670 `/munka-<slug>/` rows, no lastmod, no id — 9 more than the list states, and the list counts the redirected ads too: the two witnesses are never merged** — read by the declared client, the guard on the exact path, thirty seconds apart as the rules ask (`Crawl-Delay: 30`, 741 B under `*`, refusing `/munka/redirect/`, `/munka/sendmail/`, `/munka/statclick/`, `/munka/statapply/`, `/munka/track/`, `/munka/add`, `/favorite/`, `/user/new`); the hosted ad (98 485 B) has no JSON-LD — title, employer, county, categories, the body column, the employer's own apply page on `eastmen.hu`; **the body carries the employer's «Kapcsolati adatok» block — telephone and e-mail (Cloudflare's «[email protected]») — scrubbed** · 2026-09-14 -->
<!-- witness: the list's own «N állás», printed beside every walk and beside the sitemap's rows — «8 670 hosted advertisement(s) in the job sitemap …, the list states 8 661 (hosted and redirected together) — 9 more in the sitemap than the list states. The two witnesses are never merged.»; a page serving page 1's cards again exits 6, as does a 200 page without one card · 2026-09-14 -->

**Állásportál gathers Hungary's manual-trade and agency postings —
operators, forklift drivers, student jobs, warehouse staff, cleaners for
the police — 8 661 stated on the day, beside Profession.hu
(`profession.md`) and the public service's Virtuális Munkaerőpiac.**
Issue #360. Measured 2026-09-14 02:13–02:22 UTC by the declared client,
the guard on the exact path before each request, thirty seconds between
requests because the host asks for thirty.

## Rules and the routes

```
allasportal.hu/robots.txt                200, 741 B — User-agent: *; Sitemap ×5 (sitemap.xml, _location, _position, _corporation, _job); Disallow /job|/allas|/munka + /redirect/ /sendmail/ /statclick/ /statapply/ /track/, /munka/add, /favorite/, /user/new; Crawl-Delay: 30
GET https://allasportal.hu/                     200, 131 170 B — «30 000 friss állás» in the title (a slogan), employer cards, the county and category menus
GET https://allasportal.hu/munka/list           200, 135 251 B — «8661 állás»; 15 cards; pager 1 … 5 … 721 722, ?page=N from 2
GET https://allasportal.hu/sitemap_job.xml      200, 1 167 855 B — 8 670 <loc>, all /munka-<slug>/, no lastmod
GET https://allasportal.hu/munka-store-disztribucio-ce-driver/   200, 98 485 B — a hosted ad: h1, card-head employer, .loc, jobad-categs, the order-1 column, JELENTKEZEM → eastmen.hu (data-jobapply="1")
```

**`Crawl-Delay: 30` is honoured as written** — `_pace.Pace` takes the
longer of the host's thirty and the adapter's two — so `list` is one
page every thirty seconds (three pages by default: 90 s) and `sitemap`
two requests (a minute); the whole list at that pace would be six hours,
and the sitemap is the inventory instead.

## Two kinds of card — and the one whose address is refused

```
allasportal.py list --pages 2
[allasportal] 30 emitted over 2 page(s) of 15, the list states 8 661 — walked by request (--pages/--limit), 30 s a page as the host asks; not a shortfall.
[allasportal] 2 of the 30 are ads on other boards whose only address here is refused in writing — carried as the card, url null, never followed; the hosted ads' contact block is scrubbed by `ad`.
```

A card: the employer (`card-head` — a private advertiser has none), the
title, a snippet, the county, an age in the site's words («3 napja»,
«tegnapi», «még aktuális», «3 hónapja - még aktuális»), the id
(`data-job`), and a link that is **`jobshow`** — an ad hosted at
`/munka-<slug>/`, read by `ad` — or **`redirect`** — an ad gathered from
another board whose only address here is `/munka/redirect/<id>`,
**refused in writing: the record carries the card's fields, `url` null,
and `url_withheld` with the reason; nothing is followed** (2 of 15 on
page 1). The guard against a pager that does not page (page 1's cards
again → exit 6) and against a 200 page without a card are the same as on
Jobly.

## The sitemap — the inventory in one file

```
allasportal.py sitemap
[allasportal] 8 670 hosted advertisement(s) in the job sitemap (0 other rows set aside), the list states 8 661 (hosted and redirected together) — 9 more in the sitemap than the list states. The two witnesses are never merged.
```

`sitemap_job.xml` names every hosted ad by slug (no id, no lastmod;
repeated slugs counted once) — the sitemap's 8 670 and the list's 8 661
answer two questions (hosted only; hosted and redirected together) and
are printed side by side.

## The ad

```
allasportal.py ad --url https://allasportal.hu/munka-store-disztribucio-ce-driver/
{"id": "2656850", "title": "Store disztribúció CE driver", "employer": "Eastmen Human Resources B.V.", "county": "Pest megye", "categories": ["Logisztika / Beszerzés / Szállítás / Raktározás / Szállítmányozás", "Szakmunkák / Raktározás, szállítás, posta - szakmunka"],
 "apply_url": "https://www.eastmen.hu/allas/store-disztribucio-ce-driver/#d-apply", "description": "… Kapcsolati adatok:\n Telefon: [telephone withheld]\n Email: [e-mail withheld] …", "contacts_withheld": true}
```

No JSON-LD: the `<h1>`, the employer, the county, the categories, the
body column (ended at the apply button or the sidebar — the «Hasonló
állások» cards are not the ad), the id from the page's own statistics
call (`send_statistic("/munka/statclick/JOBID", "2656850" …)` — read,
never sent), and **the employer's own apply page on another host,
named and never fetched; an apply button pointing at the site's own
refused `/munka/redirect/` is not an apply page and is null**. **The
body carries the employer's «Kapcsolati adatok» block — «Telefon: +36 1
808 …», «Email: [email protected]» — scrubbed of Hungarian telephone
numbers (`+36`, `06`, with spaces, dashes or slashes) and e-mail
addresses, Cloudflare's placeholder included; `contacts_withheld` on
every record.** The «Továbbküldöm» mail form (`/munka/sendmail/`) is
refused in writing and never used.

## Configuration

```yaml
boards:
  allasportal:
    enabled: true
    pages: 3              # list: 15 a page, thirty seconds a page
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `pages` | no | 3 by default; the list had 722 on the day |

No credentials, no browser, no login. `sitemap` is two requests (a
minute); `list` one a page (thirty seconds); `ad` one.

## What is not established

- **Which boards the redirected ads come from** — the site says «a nagy
  állásoldalak» (the big boards); the redirect is refused, so the origin
  is not read. Profession.hu (`profession.md`) is a likely one and is
  read directly.
- **The 9 extra sitemap rows** — hosted ads the list no longer counts,
  or a lag; not opened.
- **Whether the age «még aktuális» carries a date** — the site prints
  words, not dates; `ad` has none either on the one read.
- **The county and category sitemaps** (`sitemap_location`,
  `sitemap_position`, `sitemap_corporation`) — facets; not read.

## 2026-09-14 — shipped

`list`: 30 in 2 pages against 8 661 stated, 2 redirected cards carried
without an address, every card with a county and an age; `sitemap`:
8 670 slugs against 8 661, never merged; `ad`: one, its contact block
scrubbed, no number or address in the output. Three tests; six mutations
on a detached worktree (`python3 -B`), six red — the redirected card
given its refused address, the same-cards guard dropped, the count's
thousands dot kept, a repeated slug counted twice, the telephone not
scrubbed, the apply link taken from the site's own host.
