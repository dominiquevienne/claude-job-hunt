# Board measurement — Tecoloco (`www.tecoloco.com.hn`, Honduras; one domain per country — Guatemala reached, five others not this session): the provider's static 403 to the declared client, and a browser served the whole board — `/empleos` 40 a page, 33 pages, 1 300 advertisements on 2026-09-14, a JobPosting per ad; `route: browser`, no script

<!-- verified: 2026-09-16 -->

<!-- hosts: www.tecoloco.com.hn, www.tecoloco.com.gt, www.tecoloco.com.sv, www.tecoloco.com.ni, www.tecoloco.com.do -->
<!-- script: none -->
<!-- countries: HN GT SV NI DO -->
<!-- content: measured · **the declared client gets the provider's static 403 (25 B, `9ccabba20b9f`, the `jobstore`/`hays` bytes) on the root — the rules open (`_robots.allowed('www.tecoloco.com.hn','/')` → open, certain); a connected tab is served everything: `/empleos` lists 40 advertisements a page with a pager `?Page=N` to 33 (page 33: 20) and a `PerPage=40|80|100` switch — 32 × 40 + 20 = 1 300 on the day; the page prints no total but the counts of its 19 job areas (Mercadeo | Ventas 412, Finanzas 181, Banca 89 … Telecomunicaciones 5 — 1 317 in all, an ad may sit in more than one) and of 15 industries; each ad `/<id>/<slug>.aspx` (ids 1 098 212 … 1 108 661) carries a JobPosting JSON-LD — title, url, datePosted, validThrough, description, industry, employmentType, baseSalary, hiringOrganization (the employer — «MERHONSA»), jobLocation with locality, country and geo — and prints «Ubicación», «Tipo de contratación», «Fecha de Publicación», «Fecha de Expiración», «Nivel de experiencia»; the root's `/listado` is the area index, `/trabajos-en-<departamento>` and `/empleo-<area>` the facets; the country selector is a form (Costa Rica 16, El Salvador 21, Guatemala 29, Nicaragua 41, Panamá 45, República Dominicana 53) over one domain per country: `www.tecoloco.com.gt/empleos` served to the tab too — 40 a page, a pager to 100; on 2026-09-16 05:3x UTC the other fronts measured from a tab: `.sv` «TOTAL DE OFERTAS ACTIVAS: 3855», 97 pages (96 × 40 + 15 = 3 855, equal); `.ni` 1 579, 40 pages (39 × 40 + 19); `.do` 124, 4 pages; `.gt` 1 267, 32 pages (its pager read «to 100» on 2026-09-14); `.pa` DNS SERVFAIL on 1.1.1.1 and 8.8.8.8 (the tab's «could not connect» of 2026-09-14), `.cr` NXDOMAIN on both — the selector's Costa Rica (value 16) points at no `www.tecoloco.com.cr`; the 2026-09-14 «domain permission» refusal of `.sv` was the `navigate` tool inside a `browser_batch`, not the site** · 2026-09-16 -->
<!-- witness: none the list prints as a total — the pager's last page is the count (32 × 40 + 20 = 1 300, read on page 1 and page 33), beside the site's own area counts (1 317 with overlap); nothing was served to the declared client, so no script prints anything · 2026-09-14 -->
<!-- route: browser · 1300 · 2026-09-16 -->

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
tab, www.tecoloco.com.sv/empleos                2026-09-14: «Navigation to this domain is not allowed» — the tool, see below; 2026-09-16: served, «TOTAL DE OFERTAS ACTIVAS: 3855», 97 pages, ?Page=97 lists 15 (96 × 40 + 15 = 3 855)
tab, www.tecoloco.com.ni/empleos                2026-09-16: served, 1 579, 40 pages (39 × 40 + 19)
tab, www.tecoloco.com.do/empleos                2026-09-16: served, 124, 4 pages
tab, www.tecoloco.com.gt/empleos                2026-09-16: served, 1 267, 32 pages
tab, www.tecoloco.com.pa/empleos                chrome-error both days: `dig @1.1.1.1` and `@8.8.8.8` answer SERVFAIL for www. and apex (2026-09-16 05:38 UTC)
    www.tecoloco.com.cr                         NXDOMAIN on both resolvers — the selector's «Costa Rica» has no such front
```

**`route: browser · 1300 · 2026-09-14`** for Honduras. What a session
does from a tab: `/empleos?PerPage=100&Page=N` until the pager ends, the
id from `/<id>/<slug>.aspx`, the pager's last page as the count beside the
walk (the site prints none), the ad's JobPosting; the same procedure on
each country's domain: `.hn` 1 300 (14.09), `.sv` 3 855, `.gt` 1 267, `.ni` 1 579,
`.do` 124 (16.09) — five fronts served, `.pa` and `.cr` do not resolve. No script: nothing
is served to a client (#404).

## What is withheld

The ad page prints the employer and its location — public — and no
recruiter line was seen on the ad read; the application («APLICAR A ESTA
PLAZA») is a login on `empresas.` / the candidate account, never touched.

## 2026-09-16 — «Navigation to this domain is not allowed» is the tool, not the site

**The owner, 2026-09-14: «le plugin brave valide l'ensemble des sites. ce doit
être autre chose».** It is. Measured today, same tab, same tool, no click:

```
browser_batch [navigate .sv (1st item), wait, find]                 .sv served
browser_batch [navigate .sv, wait, find, navigate .pa (4th item)]   item 4: «Navigation to this domain is not allowed» — the tab never moved
navigate .pa (standalone), 1 minute later                            navigated — then chrome-error (DNS SERVFAIL, both public resolvers)
browser_batch [navigate .sv, wait, find, navigate .ni (4th item)]   item 4: «Navigation to this domain is not allowed»
navigate .ni (standalone)                                            served, 1 579
navigate .do (standalone, first visit)                               served, 124
browser_batch [wait, find, navigate .gt (3rd item)]                  item 3: «Navigation to this domain is not allowed»
browser_batch [navigate .gt (1st item), wait, find]                  served, 1 267
```

**Four refusals, four passes, one variable:** the text is printed by the
`navigate` tool when it runs as a NON-FIRST item of a `browser_batch` toward
a domain the session has not visited yet; the same URL as the batch's first
item, or standalone, is navigated. No HTTP request is made on the refusal
(the tab's URL does not change), so the site never saw it, and no browser
allowlist is involved. **Conduct:** a first visit to a domain goes standalone
or first in its batch; a «not allowed» from a later item is re-read
standalone before anything is written about the host.
