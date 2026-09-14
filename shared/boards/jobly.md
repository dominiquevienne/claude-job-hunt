# Board adapter — Jobly (`www.jobly.fi`, Alma Media, Finland): the private generalist beside Duunitori, at the ten seconds its rules ask — the listing's own «12 737 avointa työpaikkaa» beside every walk, the sitemap's 13 636 ids as the inventory and never merged with it; the recruiters the ad's body names, scrubbed of their numbers and addresses

<!-- verified: 2026-09-14 -->

<!-- hosts: www.jobly.fi, jobly.fi -->
<!-- script: jobly.py -->
<!-- host-forms: www.jobly.fi -->
<!-- host-forms-basis: read — the sitemap's rows and the cards' links are absolute on `www.jobly.fi`; `jobly.py` names that host as a literal and refuses an ad address on any other · 2026-09-14 -->
<!-- countries: FI -->
<!-- content: measured · **`/tyopaikat` states «Tällä hetkellä meillä on 12 737 avointa työpaikkaa» (200, 157 914 B, 02:04 UTC); the sitemap index names two files (`?page=1` 1 879 027 B, 10 000 rows; `?page=2` 845 211 B, 4 511 rows) — 13 813 `/tyopaikka/<slug>-<id>` rows, 13 636 distinct ids (177 repeated across the files), lastmod 2023-04-14 … 2026-09-13, 831 other rows (articles, pages) set aside: 899 more than the listing states, the sitemap keeping expired advertisements** — read by the declared client, the guard on the exact path, ten seconds apart as the rules ask (`Crawl-delay: 10`, Drupal's default file of 2 281 B under `*`, refusing `/search/`, the account pages and `/node/*/apply-external`); the listing 20 cards a page, `?page=N` counted from zero, 40 read in 2 pages; the ad (57 833 B) a JSON-LD JobPosting with `employmentType` and `jobLocation` as lists and an empty `baseSalary`; **the body carries an AI summary and a «Lisätietoja työpaikasta» block naming the recruitment consultants with telephone and e-mail (one as Cloudflare's «[email protected]») — scrubbed** · 2026-09-14 -->
<!-- witness: the listing's own «N avointa työpaikkaa», printed beside every walk of the list and beside the sitemap's count — «13 636 advertisement id(s) … the listing states 12 737 — 899 more in the sitemap than the listing states: the sitemap keeps expired advertisements; the two witnesses are never merged»; a page serving page 1's cards again exits 6, as does a 200 page without one card · 2026-09-14 -->

**Jobly is Alma Media's job board — with Oikotie Työpaikat closed
(`oikotie-tyopaikat.md`), the private generalist beside Duunitori
(`duunitori.md`) in Finland: 12 737 open advertisements stated on the
day.** Issue #376. Measured 2026-09-14 02:03–02:08 UTC by the declared
client, the guard on the exact path before each request, ten seconds
between requests because the host asks for ten.

## Rules and the routes

```
www.jobly.fi/robots.txt                     200, 2 281 B — Drupal's default under *: Crawl-delay: 10; Disallow /search/, /user/login/ …, /node/*/apply-external, /en/node/*/apply-external; Allow the theme assets
GET https://www.jobly.fi/tyopaikat            200, 157 914 B — «Avoimet työpaikat Joblyssa … Tällä hetkellä meillä on 12 737 avointa työpaikkaa»; 20 <article id="node-<id>"> cards; pager ?page=1 … ?page=7 (counted from zero)
GET https://www.jobly.fi/sitemap.xml          200, 389 B — two files, lastmod 2026-09-13T21:41Z
GET https://www.jobly.fi/sitemap.xml?page=1   200, 1 879 027 B — 10 000 rows: 9 553 /tyopaikka/, 405 /artikkelit/, 28 /content/ …
GET https://www.jobly.fi/sitemap.xml?page=2   200, 845 211 B — 4 511 rows: 4 260 /tyopaikka/, 222 /artikkelit/, 23 /en/ …
GET https://www.jobly.fi/tyopaikka/tarjoilija-lapland-hotels-olos-olostunturi-2685791   200, 57 833 B — JSON-LD WebSite, Organization, JobPosting; panes; the body; «Hae paikkaa» → /node/2685791/apply-external (refused, never followed)
```

**`Crawl-delay: 10` is honoured as written** — `_pace.Pace` takes the
longer of the host's ten and the adapter's two — so `list` is one page
every ten seconds and a walk of the whole listing (637 pages on the day)
is not what it is for: `sitemap` gives the inventory in three requests.

## The three commands and their witness

```
jobly.py sitemap
[jobly] 13 636 advertisement id(s) in 2 file(s) (lastmod 2023-04-14 … 2026-09-13; 831 other rows set aside), the listing states 12 737 — 899 more in the sitemap than the listing states: the sitemap keeps expired advertisements; the two witnesses are never merged.
jobly.py list --pages 2
[jobly] 40 emitted over 2 page(s) of 20, the listing states 12 737 — walked by request (--pages/--limit), 10 s a page as the host asks; not a shortfall.
```

`sitemap` reads the listing for its count (one request), then the index
and its two files: every `/tyopaikka/<slug>-<id>` row once (177 ids are
repeated across the two files), with its lastmod; articles and pages set
aside and counted. **The listing's count and the sitemap's count are
printed side by side and never merged** — 899 apart on the day, the
sitemap's oldest job row dated April 2023 while the listing says «open».
`list` walks `/tyopaikat` — **`?page=N` counted from zero, so `?page=1`
is the second page** (the AfricaWork lesson), with a guard: a page that
serves page 1's cards again exits 6, as does a 200 page without one
card. A card: id, url, title, employer, «13.09.2026» → `posted`, the
location line («95900 Kolari, Lappi» — towns, then the region).

## The ad

```
jobly.py ad --url https://www.jobly.fi/tyopaikka/tarjoilija-lapland-hotels-olos-olostunturi-2685791
{"id": "2685791", "title": "Ski Shop-työntekijä, Ylläs Ski Resort, Äkäslompolo", "employer": "Lapland Hotels", "employment_type": ["TEMPORARY"], "employment_type_term": "Määräaikainen ja projektityö",
 "locations": ["95900 Kolari", "Lappi"], "category": "Hotelli- ja ravintola-ala, Matkailu", "salary_min": null, "salary_unit_stated": false, "posted": "2026-09-13", "valid_through": "2026-11-01", "direct_apply": false, "description": "…", "contacts_withheld": true}
```

The JSON-LD JobPosting: title, dates, employer, `employmentType` and
`jobLocation` as the lists they are (a town with its postcode, then the
region), `occupationalCategory`, `directApply`; `baseSalary` was empty on
the day — **a salary is stated only when a value AND a period are
printed** (`unitText` alone is not a salary). The panes give the region
items and the employment-type term. **The body carries an AI summary
(«Tämä tiivistelmä on luotu tekoälyn avulla») that names the recruitment
consultant with telephone and e-mail, and a «Lisätietoja työpaikasta»
block that names another: the text is emitted scrubbed of e-mail
addresses — Cloudflare's «[email protected]» placeholder included — and
Finnish telephone numbers; the persons' names remain as the site prints
them, their numbers and addresses do not; `contacts_withheld` on every
record; the «Hae paikkaa» link is refused in writing and never followed.**

Observed on the day and left as served: node 2685791's slug and AI
summary describe a waiter's post at Lapland Hotels Olos while its title
and body describe a ski-shop post at Ylläs — the record carries the
title and the body the page serves, and says nothing about which is
right.

## Configuration

```yaml
boards:
  jobly:
    enabled: true
    pages: 5              # list: 20 a page, ten seconds a page
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `pages` | no | 5 by default; the listing had 637 on the day |

No credentials, no browser, no login. `sitemap` is four requests (40 s);
`list` one a page; `ad` one.

## What is not established

- **Which of the 899 extra sitemap rows are expired** — the sitemap's
  lastmod says when a row moved, not whether the ad is open; opening one
  would tell, and none was on the day.
- **Filters** — the site's search is `/search/`, refused; the adapter
  takes the listing as the site orders it.
- **The English front** (`/en/`) — 23 sitemap rows; not read.
- **The pane names beyond the two read** — region and employment type
  were on the one ad; salary panes were not seen.

## 2026-09-14 — shipped

`sitemap`: 13 636 ids against 12 737 stated, never merged; `list`: 40 in
2 pages, every card with an employer, a date and a location; `ad`: one,
two recruiters named in its text and both scrubbed, no number or address
in the output. Three tests; six mutations on a detached worktree
(`python3 -B`), six red — the pager counted from one, the same-cards
guard dropped, a repeated id counted twice, the article rows not set
aside, the placeholder not scrubbed, the salary period taken as stated
without a value.
