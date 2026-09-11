# Board adapter — Enbek.kz (Kazakhstan): the state employment portal, and every listing route is refused in writing

<!-- verified: 2026-09-11 -->

<!-- hosts: enbek.kz, www.enbek.kz -->
<!-- script: none -->
<!-- countries: KZ -->
<!-- content: indeterminate · 2 hosts (`enbek.kz`, `www.enbek.kz`), same rules, read twice and certain: open on 4 permitted paths tried (`/`, `/ru`, `/kk`, 1 vacancy page) and **closed in writing on every listing route, 5 paths tried** — `Disallow: /*/search/*` and `/*/вакансии/*` to `User-agent: *`; no sitemap is declared and `/sitemap.xml` redirects to the home page; so nothing enumerates the board by a permitted path, and its size is what the site says it is, not what was counted · 2026-09-11 13:12 UTC -->
<!-- witness: none by a permitted route — the site states counters (below) and no permitted path returns advertisements to compare them with · 2026-09-11 -->

**Kazakhstan's public employment service — Электронная биржа труда, «the
electronic labour exchange» — and the first Kazakh host on a card here.**
Russian and Kazakh interfaces (`/ru`, `/kk`), UTF-8, Cyrillic paths for the
CV and vacancy sections. *Measured 2026-09-11, 13:12–13:16 UTC, every fetch
through `bin/fetch-body.py` under the declared identity, the guard taken on
the exact path first.*

## The rules — read twice, certain, and they name the listing

```
GET https://enbek.kz/robots.txt        200, fetched twice, same body
User-agent: *
# Disallow: /*?                        <- commented out, so a query string is NOT refused
Disallow: /*.pdf$
Disallow: /*/index.php/*
Disallow: /*/search/*                  <- every listing: /ru/search/vacancy, /ru/search/vac, /ru/search/resume
Disallow: /*/вакансии/*                <- «vacancies», the Cyrillic section
Disallow: /*/резюме/*                  <- «CVs»
Disallow: /docs/*/node/*
```

No `Crawl-delay`, no `Sitemap:` line, no group naming this project's agents.

| path | `_robots.allowed()` | rule |
| :-- | :-- | :-- |
| `/` | **True** | — |
| `/ru` · `/kk` | **True** | — |
| `/ru/vacancy/inspektor-po-kadram~5979588` | **True** | — |
| `/ru/search/vacancy` | **False** | `/*/search/*` |
| `/ru/search/vac` · `/ru/search/vacancy?source[0]=7` · `/ru/search/vacancy/?pou=…` | **False** | `/*/search/*` |

**This is a refusal written in the rules, addressed to everybody.** *Under
`shared/robots-policy.md` and the doctrine of 2026-09-07 it binds every
route — the plugin's HTTP client and a driven browser alike (borne 1). It is
not the case of #222, where the rules open and the transport refuses the
client; here the operator has written the refusal, and no layer change undoes
it.*

## What is open, and why it does not enumerate anything

```
GET https://enbek.kz/ru               200, 142 872 B, md5 be80985f48…
GET https://enbek.kz/sitemap.xml      200 — REDIRECTED to https://enbek.kz/kk, 143 178 B: the home page, 0 <loc>
```

**The home page links the listing only through the refused paths** —
`/ru/search/vacancy`, its `?pou=<employer>` variants, `/ru/search/vac` — and
links **three** vacancy pages directly (`/ru/vacancy/<slug>~<id>`, ids
5979583, 5979588, 5979589). It declares no API and no JSON endpoint: the
scripts it loads are Bootstrap, jQuery, select2, slick, a feedback widget and
an assistant widget on `aidana.enbek.kz`.

**A vacancy page is permitted, so `ad` would be readable given an id.** *But
there is no permitted route that yields ids: no listing, no sitemap, no feed.*
Composing `/ru/vacancy/x~<n>` over a range of integers would be discovering
the inventory of a section the operator closed, by another door — **not done,
and not to be done.** What is left is exactly what is written above: the rules
permit reading one advertisement somebody hands you, and refuse the list.

## The counters — three on the home page, two on the search page, and they are not one quantity

**On the home page, 2026-09-11:**

```
133 556   рабочих мест              «work places» — positions, not advertisements
220 514   актуальных резюме         «current CVs»
305 965   трудоустройств            «placements»
```

**On the search page, 2026-09-02** (`shared/plausible-and-false.md`, read
before the guard was taken on exact paths — that page is refused today):

```
 44 521   ads
 78 421   posts
```

*Five figures, at least three quantities — advertisements, positions within
them, and cumulative placements — and none of them is confirmed against a
count of advertisements, because no permitted path returns any.* **This card
chooses none of them.** A number quoted from here is «the site states», with
its label and its date, never «the board has».

## What this card is, and is not

- **Not a verdict that the board is closed.** A written refusal on the listing
  is a limit of route; whether this host is *written off* is the owner's
  decision — the rule of 2026-09-08, *no host is declared closed without his
  express validation* — and the measurement is what this card
  records.
- **Not an adapter.** `script: none`, and no invocation is documented because
  none exists that respects the rules.
- **What would change it:** a `Sitemap:` line or a feed on a permitted path;
  an open-data export (the home page links `/ru/analytical-data`, not fetched
  here — it is a statistics page, not a listing, on its label); or the operator
  narrowing `/*/search/*`.

## Configuration

None — there is nothing to enable. A user who has an enbek.kz vacancy URL can
hand it to `cover-letter`, which reads one page; that page is permitted.
