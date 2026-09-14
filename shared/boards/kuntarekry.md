# Board adapter — Kuntarekry (`kuntarekry.fi`, Finland): the municipalities' and wellbeing counties' recruitment service, its job cards rendered by the server — 1 356 counted by the site, 72 read in three pages by request, the contact person on every ad withheld

<!-- verified: 2026-09-13 -->

<!-- hosts: kuntarekry.fi, www.kuntarekry.fi -->
<!-- script: kuntarekry.py -->
<!-- host-forms: kuntarekry.fi -->
<!-- host-forms-basis: read — `kuntarekry.py:HOST`, a single literal; `www.kuntarekry.fi` answers the rules and redirects the root to the apex, and every link the pages write is root-relative · 2026-09-13 -->
<!-- countries: FI -->
<!-- content: measured · **«count: 1356» stated by the site's own counter (`/fi/tyopaikat/?view=count&format=json` — what its `<job-counter>` asks), 72 emitted over 3 of 57 pages of 24 — bounded by request** — read by the declared client through plain GETs, 23:54 UTC; page 2 answered `current="2"`; 28 `<job-card>` a page of which 4 are the site's own «Mainostetut» (`is-promoted="true"`, repeated on every page and skipped); `--filter espoo` walked `/fi/tyopaikat/espoo/`; the rules (113 B) `*` Allow: / with two sitemaps that are HTML pages, no Crawl-delay; **the contact person — name, e-mail, telephone — is on every ad and never leaves**: the block is not read, the text and the salary line are scrubbed · 2026-09-13 -->
<!-- witness: the site's own counter, asked once per walk on the same path as the walk and printed beside the emitted count; the pager's `current`/`total` checked after every turn; a bounded walk says so and is never «short» · 2026-09-13 -->

**Finland's public sector below the State — every municipality and
wellbeing-services county recruits through Kuntarekry; 1 356 open
postings on the day, in a country whose national public service
(Työmarkkinatori, #371) is under the user's own key and whose private
generalist (Duunitori) is the only other script.** Issue #373. Measured
2026-09-13 23:50–23:55 UTC by the declared client, the guard on the exact
path first (`*` Allow: /, certain).

## Rules and the pages

```
robots.txt                                       200, 113 B — User-agent: * / Allow: / ; Sitemap: /fi/sivukartta/ and /se/sitemap/ (HTML pages, not job sitemaps)
GET /                                            200, 216 968 B (www → apex) — «Kuntarekry - Avoimet työpaikat»
GET /fi/tyopaikat/?view=count&format=json        200 — {"count":1356}
GET /fi/tyopaikat/                               200, 226 463 B — 28 <job-card …>: 24 postings + 4 is-promoted="true"; <ip-pagination current="1" total="57" next="/fi/tyopaikat/sivu2/">
GET /fi/tyopaikat/sivu2/                         200 — current="2", 28 cards (the same 4 promoted)
GET /fi/tyopaikat/jopo-luokan-ohjaaja-742318/    200, 218 897 B — a JobPosting in JSON-LD, <job-view job-ext-id="742318">, the text, the contact block
GET /dist/js/app.lnsWl1.js                       200, 407 959 B — read once to learn what <job-counter> asks: /fi/tyopaikat/[<filter>/]?view=count&format=json → count
```

**A Lit site whose list the server renders**: the cards are `<job-card>`
elements with the posting in their attributes, the pager an
`<ip-pagination current total next>`, the next page `/sivuN/`. The site
marks its four promoted cards itself and repeats them on every page —
the adapter skips them by that attribute and emits every id once. The
counter is what the page's own `<job-counter>` fetches, asked on the same
path as the walk (`--filter espoo` → `/fi/tyopaikat/espoo/`). No
Crawl-delay; 2 s is the adapter's own. **`--pages` defaults to 10** (240
rows) and the note says the walk was bounded by request; 57 pages is a
choice.

## The card, and the ad

```
<job-card profit-center="Espoon kaupunki" title="Luokanopettaja, Soukan koulu" publication-date="14.9.2026" publication-time="00:01"
          publication-end="28.9.2026" publication-end-time="15:45" ext-id="ESPOO-03-1327-26" url="/fi/tyopaikat/luokanopettaja-soukan-koulu-espoo-03-1327-26/"
          job-id="1912999" job-key="ESPOO-03-1327-26" published="24h"></job-card>
```

The card gives the title, the hiring unit (`employer` — «Espoon
kaupunki», «Saimaan Tukipalvelut Oy», «Kristiinankaupunki»), the
publication date, the application deadline with its time (`DD.M.YYYY
HH:MM`, as printed; null when the card gives none), the site's own key
and id, and the address. The ad's JSON-LD adds the employer as the
posting names it («Kristiinanseudun koulu»), the locality and region,
the postal code, `datePosted`/`validThrough` in ISO, the employment type
(«Osa-aikatyö, Määräaikainen…»), and **the salary as the posting writes
it — «Palkkaus määräytyy KVTES palkkaluokan 5KOU62A1 mukaan … 2 312,36
e» — emitted as `salary_text` in EUR, never parsed into a number,
`salary_unit_stated` false.** **The contact person is on every ad** —
«Eeva K… eeva.k…@krs.fi, 040…» in a block below the text and often
inside it: the block is not read, and the description and the salary
line are scrubbed of e-mail addresses and Finnish telephone numbers
(dates such as `1.10.2026-5.6.2027` are left alone); `contacts_withheld`
says so on every record. The «Hae työpaikkaa» application is the site's
own form, never touched.

```
kuntarekry.py search --pages 3
[kuntarekry] 72 emitted of the 1 356 the site counts (the whole site) — 3 of 57 page(s) walked by request (--pages/--limit), not a shortfall.
```

## Configuration

```yaml
boards:
  kuntarekry:
    enabled: true
    filter: "espoo"        # optional — a path segment the site itself links: a town, a region (pirkanmaa), a field (sosiaaliala), an organisation
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `filter` | no | the site's own slug; none = the whole site, 10 pages |

No credentials, no browser, no login. `search` is 1 + pages requests at
2 s; `ad` is one.

## What is not established

- **The count against the pages** — 1 356 counted, 57 pages of 24 = 1 368
  slots; the last page is short and a full walk was not made on the day
  (57 requests); the note prints both.
- **Whether `organisation-title` is ever set** — null on all 72 read; the
  card's `profit-center` carried the employer every time.
- **The English and Swedish routes** (`/en/`, `/se/`) — the same site;
  the adapter reads Finnish.
- **The 48-a-page option** the page's `<count-dropdown>` offers — its
  parameter was not read; 24 is what the plain page serves.

## 2026-09-13 — shipped

`search --pages 3`: 72 of 1 356, bounded by request; `search --filter
espoo --pages 1 --limit 5`: 5 of the town's count; `ad` on one. Four
tests; six mutations on a detached worktree (`python3 -B`), six red —
the promoted cards not skipped, the pager check dropped, the counter
read from `total` instead of `count`, the e-mail scrub dropped, the
telephone scrub dropped, the filter not put on the counter's path (the
fixture's counter carries a second number and a `+358` form beside the
`040` one — no symmetric sample this time).
