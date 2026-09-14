# Board measurement — Tecoloco (`www.tecoloco.com.hn`, Honduras; one domain per country — Guatemala reached, five others not this session): the provider's static 403 to the declared client, and a browser served the whole board — `/empleos` 40 a page, 33 pages, 1 300 advertisements on 2026-09-14, a JobPosting per ad; `route: browser`, no script

<!-- verified: 2026-09-14 -->

<!-- hosts: www.tecoloco.com.hn, www.tecoloco.com.gt -->
<!-- script: none -->
<!-- countries: HN GT -->
<!-- content: measured · **the declared client gets the provider's static 403 (25 B, `9ccabba20b9f`, the `jobstore`/`hays` bytes) on the root — the rules open (`_robots.allowed('www.tecoloco.com.hn','/')` → open, certain); a connected tab is served everything: `/empleos` lists 40 advertisements a page with a pager `?Page=N` to 33 (page 33: 20) and a `PerPage=40|80|100` switch — 32 × 40 + 20 = 1 300 on the day; the page prints no total but the counts of its 19 job areas (Mercadeo | Ventas 412, Finanzas 181, Banca 89 … Telecomunicaciones 5 — 1 317 in all, an ad may sit in more than one) and of 15 industries; each ad `/<id>/<slug>.aspx` (ids 1 098 212 … 1 108 661) carries a JobPosting JSON-LD — title, url, datePosted, validThrough, description, industry, employmentType, baseSalary, hiringOrganization (the employer — «MERHONSA»), jobLocation with locality, country and geo — and prints «Ubicación», «Tipo de contratación», «Fecha de Publicación», «Fecha de Expiración», «Nivel de experiencia»; the root's `/listado` is the area index, `/trabajos-en-<departamento>` and `/empleo-<area>` the facets; the country selector is a form (Costa Rica 16, El Salvador 21, Guatemala 29, Nicaragua 41, Panamá 45, República Dominicana 53) over one domain per country: `www.tecoloco.com.gt/empleos` served to the tab too — 40 a page, a pager to 100; `www.tecoloco.com.sv` refused by the extension's own domain permission (not by the site), `www.tecoloco.com.pa` a connection error in the tab; CR, NI, DO not tried** · 2026-09-14 -->
<!-- witness: none the list prints as a total — the pager's last page is the count (32 × 40 + 20 = 1 300, read on page 1 and page 33), beside the site's own area counts (1 317 with overlap); nothing was served to the declared client, so no script prints anything · 2026-09-14 -->
<!-- route: browser · 1300 · 2026-09-14 -->

**Tecoloco calls itself «la plataforma #1 de empleo en la Región» — seven
Central American and Caribbean fronts on one platform, Honduras
1 300 advertisements on the day.** Issue #440. Measured 2026-09-14
09:28–09:34 UTC from a connected tab, after the declared client's static
403 of 2026-09-13.

## What the client gets, and what a tab gets

```
_robots.allowed('www.tecoloco.com.hn','/')     open, certain — the rules do not refuse the list
client, GET /                                   403, 25 B, md5 9ccabba20b9f ×2 (2026-09-13) — the provider default seen on eleven hosts
tab, /                                          served — the front page, 20 areas, the country selector (a form)
tab, /listado                                   served — the area index, no cards
tab, /empleos                                   served — 40 cards, pager ?Page=2 … 33 and PerPage=40|80|100, area counts (412, 181, 89 …), industry counts
tab, /empleos?Page=33                           served — 20 cards, the last page: 32 × 40 + 20 = 1 300
tab, /1108661/vendedor-rutero.aspx              served — a JobPosting: MERHONSA, Comayagua, 13/09/2026 → 28/10/2026, Tiempo completo
tab, www.tecoloco.com.gt/empleos                served — 40 cards, pager to 100
tab, www.tecoloco.com.sv/empleos                not navigated: the extension's domain permission refused it (the session's allowlist, not the site)
tab, www.tecoloco.com.pa/empleos                chrome-error: the tab could not connect
```

**`route: browser · 1300 · 2026-09-14`** for Honduras. What a session
does from a tab: `/empleos?PerPage=100&Page=N` until the pager ends, the
id from `/<id>/<slug>.aspx`, the pager's last page as the count beside the
walk (the site prints none), the ad's JobPosting; the same procedure on
each country's domain once that domain is measured (`.gt` reached, 100
pages; `.sv`, `.pa`, `.cr`, `.ni`, `.do` not measured). No script: nothing
is served to a client (#404).

## What is withheld

The ad page prints the employer and its location — public — and no
recruiter line was seen on the ad read; the application («APLICAR A ESTA
PLAZA») is a login on `empresas.` / the candidate account, never touched.
