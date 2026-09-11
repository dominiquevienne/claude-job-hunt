# Board adapter — Net-Empregos (`www.net-empregos.com`): Portugal's first, two feeds that hold, four that answer the home page

<!-- verified: 2026-09-11 -->

<!-- hosts: www.net-empregos.com -->
<!-- script: netempregos.py -->
<!-- host-forms: www.net-empregos.com -->
<!-- host-forms-basis: read — `netempregos.py:HOST`, a single literal; the apex `net-empregos.com` redirects its `robots.txt` to `www` and is never built · 2026-09-11 -->
<!-- countries: PT -->
<!-- content: measured · 5 000 advertisement URLs in the declared `Sitemap.asp` (one per line, 5 000 distinct ids, md5 stable across two reads) and 1 000 `<item>` in the declared `rss.asp`, the 1 000 most recent with the employer on 1 000 of 1 000 — both are the feeds' own caps, not the board's size, which the site states nowhere read (`netempregos.py list` / `netempregos.py feed`) · 2026-09-11 -->
<!-- witness: second route of the same operator — RSS ∩ Sitemap = 1 000 of 1 000: every RSS link is in the sitemap. That corroborates the feed's addresses, NOT a total; no second source states the board's size, and four of the seven declared feeds serve the home page · 2026-09-11 -->

**The board declares seven sitemaps and serves two.** *The other four answer
`200` with the home page — a status check passes them, a size check passes
them, and only the count of advertisements extracted sees them.* **That count
is printed beside every read, and a zero from tens of kilobytes dies rather
than reporting an empty board.**

## Step 1 — the rules twice on both hosts, and 7 declared feeds of which 2 hold: 5 000 URLs and 1 000 items (2026-09-11 14:22 UTC)

```
https://net-empregos.com/robots.txt        -> https://www.net-empregos.com/robots.txt   (redirect)
https://www.net-empregos.com/robots.txt    200   808 o   md5 7fdd748d009fc9b74e72ebf8081704f6   ×4, identical

User-agent: *
Allow: /
Sitemap: ×7           see below
User-agent: Yandex / MJ12bot / AhrefsBot / grapeshot / VelenPublicWebCrawler / CriteoBot/0.1 / PetalBot / Jaunt   Disallow: /
Disallow:             (empty — followed by bare paths `/loginc.asp`, `/get_fav_c.asp`, …: not directives)
```

**No AI agent is named, no `Crawl-delay`; `verdict: sweep True, certain
True`.** The guard was taken on the exact URL of each of the seven declared
sitemaps, the root and an advertisement path: **all `allowed True, certain
True`.** *The trailing `Disallow:` with paths on the lines below it is
malformed — a field with no value, then lines with no field — and the guard
reads it as nothing, which is what it is.*

## The seven declared feeds — six read twice, one not read on purpose

```
Sitemap.asp             200   454 414 o   md5 9f680ac3… stable ×2   text, one URL per line         5 000 advertisement URLs, 5 000 distinct ids
rss.asp                 200 1 251 967 o   md5 MOVES (1 251 978 o on the second read, 11 bytes later)   RSS 2.0, iso-8859-1   1 000 <item>, dc:creator on 1 000/1 000
rss_pesquisas.asp       200    71 193 o   md5 3c7a9f0c… stable ×2   HTML — «Emprego  Rss_pesquisas.asp  - Setembro 2026»   0 item, 0 URL
trovit_all.asp          200    71 169 o   md5 a4838095… stable ×2   HTML — the home page                                  0 item, 0 URL
careerjet_all.asp       200    71 193 o   md5 3f58c7b2… stable ×2   HTML — the home page                                  0 item, 0 URL
listagem_livre3.asp     200    71 209 o   md5 dd7ef7a3… stable ×2   HTML — the home page                                  0 item, 0 URL
listagem_cv_livre.asp   NOT READ — by its name a listing of candidates' CVs, not of advertisements; this project reads offers, not people
```

**Four `200`s that are not answers.** *The country page of 2026-08-31 counted
three; there are four, and the fourth (`listagem_livre3`) was found by
reading all seven rather than the three the page named.* The tell is the
`<title>` — `Emprego <feed name> - <month> <year>` — and the adapter says
**«this body is the HOME PAGE»** when a feed yields zero items and carries it.

**RSS ⊂ Sitemap.** 1 000 of the 1 000 RSS links are among the sitemap's
5 000: the RSS is the 1 000 most recent WITH fields (employer, category,
zone, date, a teaser); the sitemap is 5 000 addresses WITHOUT. *The two caps
are the feeds' own — by construction — and the site states no total on the
home page, the feed or an advertisement.*

## What a feed item carries, and what the card takes

| RSS field | card | 1 000 of 1 000 |
| :-- | :-- | :-- |
| `<link>` — `/<id>/<slug>/` | `id`, `ledger_id: net-empregos:<id>`, `url` | yes — the stable key is the numeric id |
| `<title>` | `title` | yes |
| `<dc:creator>` | `company` — **the employer, never the board** | yes |
| description `Zona:` | `location` — as the feed spells it (`Lisboa` 306, `Porto` 169, `Faro` 93, `Setubal` 83 …) | yes |
| description `Categoria:` | `category` — 40 values, spelled the feed's way: `Informática ( Programação )`, not «Informática / Programação» | yes |
| description `Data:` | `date` — `11-9-2026`, the feed's | yes |
| `<pubDate>` | `pubdate` — `Fri, 11 Sep 2026 15:19:31 GMT` | yes |
| description text | `teaser` — truncated by the feed («…»), the full text is on the ad page | yes |

**Filters compare to what the feed spells, and an emptied filter prints the
spellings** with their counts — so `--categoria "Informática / Programação"`
returns zero AND the line `Informática ( Programação ) 21`, which is the
answer. Shown to reduce (#219), 14:37 UTC: `--zona Porto` 178 of 1 000;
`--categoria "Informática ( Programação )"` 3 of 1 000 (18:28 UTC; 21 items
carried the category at 14:37 — the feed moves).

## The ad page — a `JobPosting`, and its dates are the reader's clock

```
/15978698/…/    200   79 151 o   <script type = "application/ld+json" >   (spaces around `=` — `_ldjson.postings` reads it)
  JobPosting: title · hiringOrganization.name · jobLocation.address.addressLocality · employmentType · description 1 607 chars
  datePosted   2026-9-11 15:24 UTC   on a read at 14:24:44Z
               2026-9-11 15:25 UTC   on a read at 14:25:21Z      <- the clock, Lisbon local labelled UTC
  validThrough that + 30 days
```

**`datePosted` is minted at render time and `validThrough` is thirty days
after it.** *The advertisement's date is the feed's — `pubDate 15:19:31 GMT`,
`Data: 11-9-2026` — and the adapter emits the page's two dates as
`rendered_at_as_datePosted` and `rendered_plus_30d_as_validThrough`, never as
a date.* A scorer that read `datePosted` would find every ad on this board
posted today.

`ad --id <id>` builds `/<id>/oferta/` — the site serves the page on the id,
the slug is cosmetic — and dies 6 when the page carries no `JobPosting`.

## Zero-shaped answers

| what comes back | what the adapter does |
| :-- | :-- |
| a feed with zero `<item>` / zero advertisement URL | **dies 6** through `empty_first_page`, the size beside the zero — and names the HOME PAGE when the body is one |
| a filter that matches nothing | exit 0, nothing on stdout, *«the feed is not empty — every item was filtered out»* and the values the feed spells |
| an ad page with no `JobPosting` | **dies 6** with the size |
| an ad that answers 404 | dies 3 — filled or pulled, record it as discarded |

## Pace

One request per feed, one per ad, spaced 2 s by `_pace.Pace` (no
`Crawl-delay` declared). The measurement above was 20 requests between 14:22
and 14:38 UTC, all 200 — and the RSS is 1.25 MB per read.

## What is not established

**The board's size.** 5 000 is the sitemap's cap and 1 000 the feed's; the
site states no total anywhere read. **Whether `Sitemap.asp` is the most
recent 5 000 or another order** — the RSS's 1 000 are all in it, which is
consistent with «most recent» and does not prove it. **Whether the feed's
`Data:` is the posting or a re-listing** — not measured.
