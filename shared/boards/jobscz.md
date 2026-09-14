# Board adapter — Jobs.cz (`www.jobs.cz`, Czechia, Alma Career): the largest Czech board, its search cards rendered by the server — 16 019 stated for the country, 7 681 for Prague, the country's page 1 the client's and said so, the contact block on every ad withheld

<!-- verified: 2026-09-14 -->

<!-- hosts: www.jobs.cz -->
<!-- script: jobscz.py -->
<!-- host-forms: www.jobs.cz -->
<!-- host-forms-basis: read — `jobscz.py:HOST`, a single literal; every card link is `https://www.jobs.cz/rpd/<id>/…` and the pager root-relative · 2026-09-14 -->
<!-- countries: CZ -->
<!-- content: measured · **«Našli jsme 16 019 nabídek» stated for the whole country and «7 681» for Prague, 60 emitted from each in two pages of 30 — bounded by request** — read by the declared client through plain GETs, 00:21 UTC; **the country-wide page 1 (`/prace/`, `/prace/?page=1`) is the site's entry page rendered on the client and carries no card — the walk without a locality starts at page 2 by the site's own behaviour and the note says so; `--locality praha` is served from page 1**; the salary tag («45 000 – 60 000 Kč») read as a CZK range without a period on 19 of 30 country cards and 18 of 30 Prague cards; the rules (349 B) `*` with `/api/`, `/iapi/`, account paths refused, nothing touched, no sitemap, no Crawl-delay; **the ad's contact block — a person's name, an address, a telephone — is never read, and the text is scrubbed** · 2026-09-14 -->
<!-- witness: the page's own «Našli jsme N nabídek» (the figure in a `<strong>` with a no-break space — read from the text), printed beside the emitted count on every walk; a bounded walk says so; the country walk names the 30 of page 1 it cannot reach · 2026-09-14 -->

**The first Czech board by size — 16 019 open offers on the day, in a
country whose two shipped adapters are a second front (`profesia-cz`,
1 094) and an aggregator (`easy-prace`).** Issue #351. Measured
2026-09-14 00:1x–00:21 UTC by the declared client, the guard on the exact
path first (`*`, nothing refused on `/prace/` or `/rpd/`).

## Rules and the pages

```
robots.txt                          200, 349 B — User-agent: * ; Disallow: /muj/ /asmt/ /api/ /iapi/ /status/ /translations/ /js/ /nabidky-podle-cv/ /session-log/ /prihlasit-se/?ref= /kontakt/?reportJobAdId= ; no Sitemap, no Crawl-delay
GET /prace/                         200, 94 601 B — the entry page (`SearchNoUserInputEntry`): 0 cards, no count
GET /prace/?page=1                  200 — the same entry page: 0 cards
GET /prace/?page=2                  200, 244 657 B — «Našli jsme 16 019 nabídek», 30 <article class="SearchResultCard">, pager /prace/?page=1 … 5
GET /prace/praha/                   200, 256 524 B — «Našli jsme 7 681 nabídek», 30 cards, pager with locality[code]=R200000 …
GET /rpd/2001424002/                200 — the ad: <h1>, jd-info-item, jd-info-location, jd-salary, jd-benefits, jd-body-richtext — and jd-contact-company / -address / -phone
```

**The site renders its list on the server — except the country-wide
first page**, which is the client's entry page; the server sends no card
for it under any parameter tried (`?page=1`, `?page=0`, `?sort=date`,
`?q[]=`). The adapter does not pretend: a walk with no `--locality`
begins at page 2 and its note says that 30 of the count are not reachable
by HTTP this way; **`--locality <slug>`** — a path the site itself serves
(`praha`, `brno`, `ostrava` …) — is served from page 1. No Crawl-delay;
2 s is the adapter's own. **`--pages` defaults to 10** (300 rows) and the
note says the walk was bounded by request.

## The card, and the ad

```
<article class="SearchResultCard"><h2 data-test-ad-title="Všeobecná / psychiatrická sestra"><a data-jobad-id="2001424002" href="https://www.jobs.cz/rpd/2001424002/?searchId=…&amp;rps=233">…</a></h2>
  <div data-test-ad-status="default">Přidáno včera</div>
  <span class="Tag Tag--success …">45 000 – 60 000 Kč</span><span class="Tag Tag--neutral …">Odpovězte teď a budete mezi prvními</span>
  <li class="SearchResultCard__footerItem"><span translate="no">Fokus Labe, z.ú.</span></li><li data-test="serp-locality">Ústecký kraj + 3 další lokality</li>
```

The card gives the id, the title, the address (the search token
`?searchId=…&rps=` stripped — the ad is served without it), the employer
(the footer's `translate="no"` span), the locality as the card prints it
(«Ústecký kraj + 3 další lokality»), the status («Přidáno včera»,
«Aktualizováno včera», «Příležitost dne» — the last is the site's paid
placement), and the tags: a salary tag is read as a range in CZK
(`salary_unit_stated` false — the card prints no period), the rest kept.
The ad adds the company (`jd-info-item` «Společnost»), the workplace
address (`jd-info-location` — an employer's street, not a person's), the
salary line, the info lines (education asked, contract type, duration),
the benefits, and the text. **The contact block — `jd-contact-company`
(a person's name), `jd-contact-address`, `jd-contact-phone` — is not
read, and the text is scrubbed of e-mail addresses and Czech telephone
numbers; `contacts_withheld` is on every ad record.** The «Odpovědět»
application is the site's own form, never touched.

```
jobscz.py search --pages 2
[jobscz] the country-wide page 1 is the site's entry page, rendered on the client — the server sends no card; the walk starts at page 2 by the site's own behaviour, and 30 of the count are not reachable by HTTP this way. `--locality <slug>` is served from page 1.
[jobscz] 60 emitted of the 16 019 the site states (the whole country) — 2 page(s) of 30 walked by request (--pages/--limit), not a shortfall.
jobscz.py search --locality praha --pages 2
[jobscz] 60 emitted of the 7 681 the site states (praha) — 2 page(s) of 30 walked by request (--pages/--limit), not a shortfall.
```

## Prace.cz is not the same stack

`www.prace.cz` — the group's second board, #353 — was read the same
night: `/nabidky/` serves «Našli jsme 19 005 nabídek» from page 1, with
`<article class="JobCard-module-scss-module__…">` cards, UUID addresses
(`/nabidka/<uuid>/`) and a `?page=N` pager — a different template on a
different build; its rules refuse `/search/` and `/hledat/`, not
`/nabidky/`. **Not a `--host` of this script; its own adapter, its own
measurement.**

## Configuration

```yaml
boards:
  jobscz:
    enabled: true
    locality: praha        # optional — a path the site serves; served from page 1. None = the country, from page 2
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `locality` | no | `praha`, `brno`, `ostrava` … as the site's own `/prace/<slug>/` |

No credentials, no browser, no login. `search` is one request a page at
2 s; `ad` is one.

## What is not established

- **The 30 of the country's page 1** — what the site shows a browser
  there; the adapter reaches them through a locality or not at all, and
  says so.
- **The locality slugs beyond `praha`** — the site's own paths; the
  adapter passes what it is given and a wrong slug is the site's 404.
- **`/fp/` and `/pd/` addresses** — company-profile and premium-detail
  ads; the pattern is accepted, only `/rpd/` was read on the day.
- **Whether «Aktualizováno» moves the order** — the list's order is the
  site's; the adapter emits every id once.

## 2026-09-14 — shipped

`search --pages 2`: 60 of 16 019 (from page 2); `search --locality praha
--pages 2`: 60 of 7 681; `ad` on one. Three tests; six mutations on a
detached worktree (`python3 -B`), six red — the country walk started at
page 1, the count read from the raw markup, the range's upper figure
dropped, the search token kept on the address, the contact block read as
the employer, the phone scrub dropped (a first M3, «the no-break space
not stripped in `num()`», was equivalent — `text()` normalises it before
any figure is read — and was replaced, not counted).
