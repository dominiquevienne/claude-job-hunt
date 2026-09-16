# Board adapter — TumomoPegas (`tumomopegas.com`, Bolivia): a generalist on a job-board engine that serves ten cards a page with its count («37 Empleos» on 2026-09-16 — a small board whose oldest live card is from 2021) and an ad of labelled fields without a JobPosting; `tumomopegas.py`, the count printed beside every walk

<!-- verified: 2026-09-16 -->

<!-- hosts: tumomopegas.com, www.tumomopegas.com -->
<!-- script: tumomopegas.py -->
<!-- host-forms: tumomopegas.com -->
<!-- host-forms-basis: read — `www.` redirects to the apex (301 on 2026-09-13), every card and company link is on the apex; `tumomopegas.py` names it as a literal and rewrites a `www.` ad address · 2026-09-16 -->
<!-- countries: BO -->
<!-- content: measured · **rules read (1 048 B): `User-Agent: *` — `Disallow: /files/files/` only; a dozen scrapers refused by name (Zealbot, WebStripper, Teleport …), none of ours; no Crawl-delay. The root (200, 156 546 B) is the engine's front (categories, departments, `/rss/`); `/todos-los-empleos/` (200, 83 142 B) prints «37 Empleos» and ten `title-job-list` cards — `<a id="listing_<id>">`, the employer a `/company/<id>/<slug>/` link (empty name on two cards), «dd.mm.yyyy», «City, DPT» — with a `?searchId=…&page=2` pager; `?page=N` alone is honoured: 4 pages, 10 + 10 + 10 + 7 = 37, equal; the per-page selector is a POST form, not sent; `/rss/` (200, 16 191 B) the ten newest; the ad (200, 62 594 B) `<h1>`, the employer link, then `<h3>Label:</h3><div class="displayField">` — ID Oferta, Ciudad, Rango Salarial («Salario Negociable»), Vistas, Tipo de contrato, Publicado, Categorías, Descripción del puesto — no JSON-LD JobPosting (MonetaryAmount fragments only); the 37 live cards date from 2026-09-04 back to 2021-06-02: a small board that keeps old ads; `tumomopegas.py list` on the day: «37 emitted from 4 page(s), the site states 37 — equal»** · 2026-09-16 -->
<!-- witness: the list's own «37 Empleos», printed on the server and read by `tumomopegas.py list` beside the walk; 10 + 10 + 10 + 7 = 37 on the day, equal · 2026-09-16 -->
<!-- route: http · 37 · 2026-09-16 -->

**Issue #432 (opened under #411, Bolivia searched on 2026-09-13). Measured
2026-09-16 06:15–06:17 UTC by the declared client, the guard on the exact
path first, `bin/fetch-body.py`; the script exercised on the same minutes.**
Rank: the pilot's risk order of 2026-09-14 10:4x, after Trabajando Bolivia
(#430) — the third and smallest of Bolivia's three generalists issued that day.

## The rules, and what the adapter refuses on its own

```
robots.txt      200, 1 048 B — `*`: Disallow: /files/files/ ; Zealbot, MSIECrawler, SiteSnagger, WebStripper, WebCopier, Fetch, Offline Explorer, Teleport … Disallow: /
allowed('/todos-los-empleos/')   open, certain        allowed('/display-job/38186/…')   open, certain
```

The rules refuse almost nothing; the adapter refuses on its own the
accounts (`/ingresar/`, `/registrarse/`, `/add-listing/`), the banner
redirects (`/go-link/`) and the social login (`/social/`) — exit 7 before
the gate — and never sends the per-page form (a POST).

## The transport, dated

```
GET /                                   200, 156 546 B, md5 bd468c218c51   (06:15:52Z)   the engine's front
GET /todos-los-empleos/                 200,  83 142 B, md5 ba7626ef8124   (06:16:08Z)   «37 Empleos», 10 cards (38186 … ), pager
GET /todos-los-empleos/?page=2          200,  81 618 B, md5 5df65cb24972   (06:16:35Z)   10 cards (38171 …) — ?page=N alone is honoured
GET /todos-los-empleos/?listings_per_page2=100   200 — still 10 cards: the selector is a POST, not a query
GET /rss/                               200,  16 191 B, md5 615e3aaaad62   (06:16:21Z)   10 items, the newest
GET /display-job/38186/Afiliado(a)-Comercial-Freelance.html
                                        200,  62 594 B, md5 65b9f0fb9a2a   (06:16:53Z)   the labelled fields; no JobPosting
```

**A small board that keeps its old ads:** the 37 live cards run from
2026-09-04 back to 2021-06-02 («Ejecutivo de ventas», EMPRESA INDUSTRIAL)
— the count is honest about the list, not about the market. The card
carries `posted`, so a reader can bound the age itself.

## What the adapter emits, and withholds

`list` (`?page=1 …` until a page brings nothing new or the stated count is
reached, 2 s apart, `--pages N` a bound printed as such): id, url (the
`searchId` stripped), title, company, company_id, posted (ISO from
«dd.mm.yyyy»), place. `ad --url`: title, company, place, salary /
`salary_negotiable`, contract, posted, categories («family : speciality»),
the description flattened and scrubbed. Guards: a page without a card exits
6; page 1 served again exits 6; the stated count missing exits 6.

**Withheld:** the description is scrubbed of e-mail addresses and Bolivian
telephone numbers; «Vistas» (the site's view counter) is not emitted;
`contacts_withheld` on every record; the application («Postular a
Empleo», a candidate account) never touched; the employer's logo not
emitted.

## Tests and mutations

`ABolivianBoardOnAJobBoardEngineWhoseListIsTenCardsAPageWithItsCountAndWhoseAdIsLabelledFieldsWithoutAJobPosting`,
both ways on fixtures (the dedup across pages and the walk's end on a page
that brings nothing new, an empty employer name, `--pages`, the three
exit-6 cases, five refused addresses, the ad with its flag and its
categories). Mutation bench on a detached copy, `python3 -B`, 6 / 6 red: the
stated count not read · the same-cards guard dropped · the dedup dropped ·
the date not turned ISO · the description not scrubbed · the
negotiable-salary flag inverted.
