# Board adapter — Prace.cz (`www.prace.cz`, Czechia, Alma Career): the group's second generalist, its job cards served from the first page — 19 005 stated, 120 read in three pages by request, the employer-hosted ads named and their other host never read, the contact block withheld

<!-- verified: 2026-09-14 -->

<!-- hosts: www.prace.cz -->
<!-- script: pracecz.py -->
<!-- host-forms: www.prace.cz -->
<!-- host-forms-basis: read — `pracecz.py:HOST`, a single literal; the listing's own links are root-relative, and the employer-hosted cards link out to `<employer>.jobs.cz`, which the adapter names and never reads · 2026-09-14 -->
<!-- countries: CZ -->
<!-- content: measured · **«Našli jsme 19 005 nabídek» stated by `/nabidky/`, 120 emitted over 3 pages of 40 — bounded by request** — read by the declared client through plain GETs, 00:30 UTC; the first page served with its cards (unlike `jobs.cz`); 40 cards a page with no overlap between pages 1 and 2; **13 of the first 40 are employer-hosted** (`o2.jobs.cz`, `albert.jobs.cz`, `kaufland.jobs.cz` …) — the card says so, the site's own `/nabidka/<uuid>/` redirects there, and `ad` stops at the redirect; the salary printed with its period on 26 of 40 («35 000 – 45 000 Kč/měsíc», `salary_unit_stated` true); the rules refuse `/search/` and `/hledat/`, not `/nabidky/`; no Crawl-delay; **the ad's «Kontaktní údaje» block is never read, the text scrubbed** · 2026-09-14 -->
<!-- witness: the page's own «Našli jsme N nabídek» (the figure in a `<strong>` with a no-break space — read from the text), printed beside the emitted count on every walk; a bounded walk says so · 2026-09-14 -->

**The second Czech generalist by size — 19 005 offers stated on the
day, more than `jobs.cz` states (16 019), on the same group's other
board.** Issue #353. Measured 2026-09-14 00:1x–00:30 UTC by the declared
client, the guard on the exact path first (`*` refuses `/auth/`,
`/search/`, `/hledat/`, `/muj/`, `/asmt/` and two form paths — nothing
this adapter touches).

## Rules and the pages

```
robots.txt                                         200 — User-Agent: * ; Disallow: /auth/ /search/ /hledat/ /muj/ /asmt/ /odpovedni-formular/ /presmerovani-na-formular/ ; Sitemap: d2260mt3awrr7p.cloudfront.net/prace.cz/sitemap-index.xml (facets, no ads — 2026-09-01)
GET /nabidky/                                      200, 566 369 B — «Našli jsme 19 005 nabídek», 40 <article class="JobCard-module-scss-module__…">, pager ?page=2 …
GET /nabidky/?page=2                               200, 572 305 B — 40 cards, none shared with page 1
GET /nabidka/a94cd5e8-…/                           200, 239 415 B — the ad: a JobPosting (baseSalary as a QuantitativeValue with unitText MONTH), benefits, the text, «Kontaktní údaje»
GET /nabidka/01e136fe-…/  (an O2 card)             200 → https://o2.jobs.cz/detail-pozice?r=detail&id=…&originJobAdUuid=…  — the employer's own host, «Detail pozice», no JobPosting
```

**Not the same build as `jobs.cz`**: CSS-module cards, UUID addresses,
the first page served with its cards; the group's second board is its
own script. No Crawl-delay; 2 s is the adapter's own. **`--pages`
defaults to 10** (400 rows) and the note says the walk was bounded by
request.

## The card, and the ad

```
<article class="JobCard-module-scss-module__…"><h2 data-testid="job-card-title"><a data-testid="advert-link" href="/nabidka/a94cd5e8-…/?rps=2078">Práce ve skladu a příprava objednávek</a></h2>
  <li><span class="accessibility-hidden">Lokalita:</span><span>Praha-Horní Počernice</span></li>
  <li><span class="accessibility-hidden">Název firmy:</span><span>LAMPS, a.s.</span></li>
  <li><span class="accessibility-hidden">Typ úvazku:</span><span>Plný úvazek</span></li>
  <li><span><span class="accessibility-hidden">Plat:</span>35 000 – 45 000 Kč/měsíc</span></li>
```

**The card labels its own fields** — the adapter reads the label and the
text beside it, never a position in a list. The link is one of three
shapes — `/nabidka/<uuid>/`, `/firma/<slug>/nabidka/<uuid>/`, or the
employer's own host with `originJobAdUuid=<uuid>` — and the UUID is the
id in all three (a reader of the first shape alone loses 13 of 40). The
address emitted is always the site's `/nabidka/<uuid>/`; **for an
employer-hosted card, `hosted_by_employer` names the other host and `ad`
stops at the redirect (exit 6) rather than read a page that is not this
board's.** The salary is read with its period when the card prints one
(«Kč/měsíc» → MONTH, «Kč/hod» → HOUR), so `salary_unit_stated` is the
card's own. The ad is its JSON-LD JobPosting — title, employer, locality
and postal code, ISO dates, employment type, **`baseSalary.value` as a
`QuantitativeValue` with `unitText`** — plus the benefits and the text.
**The «Kontaktní údaje» block (a company, an address, sometimes a person
and a telephone) is never read, and the description is scrubbed of
e-mail addresses and Czech telephone numbers; `contacts_withheld` on
every ad record.**

```
pracecz.py search --pages 3
[pracecz] 120 emitted of the 19 005 the site states — 3 page(s) of 40 walked by request (--pages/--limit), not a shortfall.
```

## Configuration

```yaml
boards:
  pracecz:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials, no browser, no login. `search` is one request a page at
2 s; `ad` is one.

## What is not established

- **The employer-hosted ads' content** — 13 of 40 on the first page live
  on `<employer>.jobs.cz` (Alma Career's white-label career sites); the
  card gives title, employer, place, type and salary, and the rest is on
  a host this adapter does not read.
- **The count against the pages** — 19 005 stated, 476 pages of 40 not
  walked; the note prints the count beside whatever was walked.
- **Whether the cards' order is stable across a walk** — no overlap on
  the two pages read; every id is emitted once regardless.

## 2026-09-14 — shipped

`search --pages 3`: 120 of 19 005, bounded by request; `ad` on one site-
hosted ad, and the refusal on one employer-hosted ad (`o2.jobs.cz`). Two
tests; six mutations on a detached worktree (`python3 -B`), six red —
the UUID read from the site's shape only, the period stated without a
printed one, the redirect to another host followed, the QuantitativeValue's
unit dropped, the e-mail scrub dropped, the count read from the raw markup.
