# Board adapter — Vacatures bij de Overheid van Suriname (`gov.sr/vacatures/`, Suriname): the State's own vacancy cards, read at the sixty seconds the host asks — 133 stated by the register, 12 read in two pages by request, the ministry as employer, the posting's own page bare

<!-- verified: 2026-09-13 -->

<!-- hosts: gov.sr -->
<!-- script: govsr.py -->
<!-- host-forms: gov.sr -->
<!-- host-forms-basis: read — `govsr.py:HOST`, a single literal; every link on the site is `https://gov.sr/…` (no `www.`), the API's `link` field included · 2026-09-13 -->
<!-- countries: SR -->
<!-- content: measured · **`X-WP-Total: 133` stated by the register's own REST route, 12 emitted over 2 pages of 6 — bounded by request at the `crawl-delay: 60` the host writes** — read by the declared client, 23:44–23:47 UTC (three requests, one a minute); page 1 dated 07/09/2026 back to 24/07/2026, page 2 to 29/05/2026; the whole register is 23 pages, twenty-three minutes, a choice and not the default; the rules `user-agent: *` / `disallow:` (nothing) / `crawl-delay: 60`; **the posting's own page is bare** — the title and the ministry, an empty content widget — and the deadline, the location, the summary and the terms-of-reference PDF live on the list card, which is what the adapter reads · 2026-09-13 -->
<!-- witness: the register's own `X-WP-Total` header, asked once per walk (`/wp-json/wp/v2/vacature?per_page=1`) and printed beside the emitted count; a bounded walk says so and names the page count of the whole register; a 404 past the last page is the end, not a fault · 2026-09-13 -->

**Suriname's public service — the government portal's «Vacatures», one
card per posting from the ministries (Natuurlijke Hulpbronnen, Onderwijs,
Arbeid en Werkgelegenheid, Landbouw…), the only living board found for
the country that is served to the declared client (`vacaturebank.sr`
refuses it, #444).** Issue #443, opened by the country search of #416.
Measured 2026-09-13 20:21–20:24 and 23:39–23:47 UTC by the declared
client, the guard on the exact path first (`*` open, certain,
`crawl-delay: 60`).

## Rules and the pages — sixty seconds, because the host says so

```
robots.txt                                     200, 53 B — user-agent: * / disallow: / crawl-delay: 60
GET /wp-json/wp/v2/vacature?per_page=1         200 — X-WP-Total: 133, X-WP-TotalPages: 133; the record: id, date, slug, link, title, categories; no content, no deadline (acf: [])
GET /wp-json/wp/v2/vacature?per_page=2&_embed=wp:term   200 — the ministry embedded as a category term («Natuurlijke Hulpbronnen»)
GET /vacatures/                                200, 254 335 B — 6 cards (Elementor loop items, `post-<id> vacature type-vacature category-<ministry>`); pager to /vacatures/5/ in view
GET /vacatures/2/                              200 — 6 cards
GET /vacature/energy-consultant/               200 — the title, «Ministerie van Natuurlijke Hulpbronnen» above it, an EMPTY theme-post-content widget
```

**The card is where the posting lives.** The REST route counts the
register and names the posting, but the deadline («Inleverdatum tot»),
the location («Locatie»), the publication date («Gepubliceerd»), the
summary and the «Meer info» PDF are custom fields Elementor renders on
the list card only; the posting's own page renders nothing beyond the
title and the ministry. So `list` asks the API once — for `X-WP-Total`,
the witness — and walks the list pages, six cards each. **`_pace` reads
the host's `crawl-delay: 60` and waits it between requests** (the
adapter's own 3 s never wins). **`--pages` defaults to 5** — thirty cards
in five minutes — and the note says the walk was bounded by request and
how many pages the whole register is (`--pages 23` on the day). No
Crawl-delay is shortened by anything in this adapter, and it never
sleeps on its own.

## The card, and the bare page

```
<div data-elementor-type="loop" class="elementor elementor-15459 post-161900 vacature type-vacature status-publish hentry category-natuurlijke-hulpbronnen">
  <h1 class="elementor-heading-title">Energy Awareness Consultant</h1>
  <span class="elementor-icon-list-text">Categorie: Ministerie van Natuurlijke Hulpbronnen</span>
  <span class="elementor-icon-list-text">Het Ministerie van Natuurlijke Hulpbronnen (NH) is op zoek naar een ervaren Energy Consultant …</span>
  <span class="elementor-icon-list-text">Locatie:   The Ministry of Natural Resources , Mr. Dr. J. C. de Mirandastraat 13-15 Paramaribo, Suriname</span>
  <span class="elementor-icon-list-text">Locatie:  </span>          <- a second, empty Locatie line on every card; the first is kept
  <span class="elementor-icon-list-text">Gepubliceerd: 07/09/2026</span>
  <span class="elementor-icon-list-text">Inleverdatum tot:  30/09/2026</span>
  <a href="https://gov.sr/wp-content/uploads/2026/09/7-08-26_CS_Final-TOR-Energy-Awareness-Consultant.pdf">Meer info</a>
```

The card gives the title, the ministry (`employer` — the State's own
service), the summary (an e-mail inside it is withheld), the location as
printed (a ministry's street address — `workplace`), the publication and
the deadline (`DD/MM/YYYY`, as printed; null when the card gives none —
the Onderwijs and Arbeid cards on the day), and the PDF the «Meer info»
button points to (`terms_of_reference` — a link, never fetched). The
address emitted is WordPress's `?p=<id>`, which the site resolves to the
pretty permalink. `ad --url` reads the posting's own page and says what
it is: the title, the ministry (its name taken from the page's own menu
by the category slug — never composed from the slug), `detail_is_bare`.

```
govsr.py list --pages 2
[govsr] 12 emitted of the 133 the register states — 2 page(s) of 6 walked by request (--pages/--limit) at the 60 s the host asks, not a shortfall; the whole register is --pages 23.
```

## Configuration

```yaml
boards:
  govsr:
    enabled: true
    pages: 5             # 6 cards a page, one page a minute — the whole register is 23 on the day
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `pages` | no | the host's minute per page is the cost; 5 by default |

No credentials, no browser, no login. `list` is 1 + pages requests, one a
minute; `ad` is one.

## What is not established

- **The 133 against the pages** — the register's count includes every
  published `vacature`; whether the loop renders all of them (23 pages of
  6 = 138 slots) was not walked on the day — twenty-three minutes; the
  note prints the count beside whatever was walked.
- **Whether the cards without «Inleverdatum tot» are open** — the
  Onderwijs and Arbeid postings give a publication date only; emitted
  with a null deadline, not judged.
- **What the PDF says** — the terms of reference are the posting's full
  text; the link is emitted and never fetched.
- **`_embed=wp:term` on the API** — read once on the day (the ministry
  name comes back embedded); the adapter does not use it, the card names
  the ministry itself.

## 2026-09-13 — shipped

`list --pages 2`: 12 of 133, bounded by request, three requests in three
minutes; `ad` on one. Four tests; six mutations on a detached worktree
(`python3 -B`), six red — `X-WP-Total` not read, the empty second
«Locatie» line clearing the first, the e-mail not withheld, the 404 past
the end not treated as the end, the page-size stop dropped, the id read
from the template's own `post-308` (three inert on the first draft — the
fixture's two headers were equal, its register never exceeded its pages,
its 404 was never reached; widened, red).
