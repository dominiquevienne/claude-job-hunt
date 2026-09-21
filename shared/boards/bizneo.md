# Board adapter — Bizneo HR (a Spanish ATS, one tenant at a time): the employer's career site on `<tenant>.bizneo.com` — or the employer's own host — serves `/jobs?page=N` as a list of five cards a page to an empty page, the advert as labelled rows and an HTML body; `bizneo.py`, the pager's last page as the witness

<!-- verified: 2026-09-21 -->

<!-- hosts: icp.bizneo.com, unete.icp.es, lefties.bizneo.com -->
<!-- host-forms: {tenant}.bizneo.com -->
<!-- host-forms-basis: read — `bizneo.py:DOMAIN` with the tenant as its subdomain (`tenant_of`), or the employer's own host when the user names it (`unete.icp.es`, where ICP's adverts live); one host per run, every other host refused before the gate; the vendor's `www.`, `hello.`, `help.`, `assets.bizneo.com` are not boards · 2026-09-21 -->
<!-- script: bizneo.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants with adverts and one former tenant, 2026-09-20 18:04 UTC and 2026-09-21 04:11 UTC, the declared client, the guard on the exact path first. Rules: the same 130 B on every host read (`icp`, `lefties`, `groundforce`, `unete.icp.es`; md5 2f18bd135435) — `User-agent: *`, `Disallow: /admin`, no agent named, no Crawl-delay. The list `/jobs` (200; ICP 11 750 B, Lefties 10 404 B): `div#job-board` of `a.job-card` cards, five a page, a `location` select of the tenant's provinces, `ul.pagination` numbering the pages (ICP 1 … 8), the page past the last answering 200 with an empty board (`?page=9`, 5 659 B, 0 cards); `bizneo.py jobs` live on 2026-09-21: **ICP 36 emitted over 8 pages, the pager numbered 8 — equal; Lefties 6 over 1 page, pager 1 — equal**. `groundforce.bizneo.com/jobs` (listed by the engine) answers 404 with the vendor's blueprint page (24 433 B) — not a tenant, exit 3; `telepizza.bizneo.com` (the issue's example of 13.09) has no address on 1.1.1.1 nor 8.8.8.8 (NODATA). The advert (200; 17 969 B on `unete.icp.es`, 17 711 B on `lefties.bizneo.com`): `<h1>`, «Publicada <i>15 de Septiembre</i>» (no year), eight labelled rows (Ubicación, Categoría, Subcategoría, Sector, Jornada laboral, Modalidad de trabajo, Nivel profesional, Departamento), the body in `general-content` blocks under bold section titles («Requisitos mínimos»), the employer in the `<title>`'s prefix; no JobPosting** · 2026-09-21 -->
<!-- witness: the page states no count — the pager's last number is read on every page and printed beside the emitted number after the walk: «N emitted over P page(s), the pager numbered Q: equal — the walk stopped on the empty page», or «short» when the walk ended before the pager's last page (a page of repeats, `--max-pages`); the tenant's `--max-pages` cut is said · 2026-09-21 -->
<!-- route: http · 36 · 2026-09-21 -->

**Issue #489 (under #406, the ATS families — bloc ES/LATAM). Tenants found
by the family's signature `bizneo.com/jobs` in a search engine on
2026-09-20: `icp` (ICP Logística, 36 adverts on eight pages, the adverts on
its own host `unete.icp.es`), `lefties` (Lefties, Inditex, 6 on one page),
`groundforce` (no longer a tenant — the vendor's blueprint 404); the
issue's `telepizza.bizneo.com` has left DNS.** Rank: the pilot's reading of
`votes.sh` on 2026-09-20 16:4x — first `adapter` issue outside cd's
#478–#488 series.

## What Bizneo HR is, and where its tenants live

Bizneo HR (Madrid; it absorbed Talent Clue, whose legacy job pages still
answer on `careers.talentclue.com`, Drupal, `Crawl-delay: 10`) is an
all-in-one HR suite whose ATS publishes an employer's «portal de empleo»
on `<tenant>.bizneo.com` — a Rails application (`authenticity_token`,
htmx pagination, assets on `assets.bizneo.com`) — or on the employer's own
host (`unete.icp.es`), the list on one and the adverts on the other when
the employer has both. **The user names the tenant** by its subdomain
(`icp`), its host or its `/jobs` URL; the vendor's own hosts are refused
before any request.

## The route — the list to its empty page

```
GET https://icp.bizneo.com/jobs             200 — 5 cards, pager 1 … 8
GET https://icp.bizneo.com/jobs?page=2      200 — 5 cards
…
GET https://icp.bizneo.com/jobs?page=9      200 — 0 cards, an empty-state icon: the walk ends
GET https://groundforce.bizneo.com/jobs     404 — «32- blueprint-2», the vendor's page: not a tenant (exit 3)
```

A card is `a.job-card[href]` (the advert's address — `/jobs/<slug>-<uuid>`
on the tenant's advert host, or `/jobs/<slug>` with no UUID on some
tenants), `div.title`, and `div.details` spans: the place first, then what
the tenant shows (`Presencial`). **The key is the address**: the trailing
UUID when there is one, the slug otherwise; the site publishes no id.
The logo is a signed S3 URL that expires in five minutes — never emitted.

## The advert — labelled rows, no JobPosting

`bizneo.py ad --url` reads `<h1>`, «Publicada <i>…</i>» as the site writes
it (a day and a month, no year — emitted verbatim, not guessed), the eight
labelled rows (`div[title="…"] span.font-bold`) — each emitted under its
own key and all of them under `fields` with the tenant's own labels — the
first `general-content` block as `description` and the titled ones
(«Requisitos mínimos», …) under `sections`; the employer from the
`<title>`'s prefix («ICP | …», «LEFTIES | …»). Applying («¡Aplica ahora!»,
«Iniciar sesión») is an account, never touched.

## Withheld, and the guard

E-mail addresses and telephone numbers scrubbed from the description and
the sections; the logo and the share links never emitted;
`contacts_withheld` on every record; the site states no country
(`--country-code` stamps the rows with what the user names, and says so).
Guard in `tests/`: the walk to the empty page counted against the pager, a
page of repeats ending it (short), the key from the address, the
non-tenant 404 (3), a page without the board (6), the ad's rows, sections
and scrubbed body, a bad address refused, another host never sent (7), bad
tenants refused before any request — 7 mutations on the committed file,
7 red (2026-09-21).
