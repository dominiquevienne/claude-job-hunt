# Board measurement — Mercado Gratis, «Empregos» (`mercado.gratis/pt/categoria/empregos/ofertas-de-emprego`, Guinea-Bissau): the job section of a generic classifieds site, served to the declared client — and EMPTY: the site's own sidebar says «Empregos (0)», no advert link on the page, no posts sitemap for the country; the «497» of the 2026-09-13 reading was the category's id, not a count. No adapter: a route to nothing is not a coverage (#550)

<!-- verified: 2026-09-21 -->

<!-- hosts: mercado.gratis -->
<!-- script: none -->
<!-- countries: GW -->
<!-- content: measured · **2026-09-21 09:26–09:27 UTC, the declared client, the guard on the exact path. Rules (`/robots.txt`): `* Allow: /`, refused `/admin/`, `*/feed`, `/ajax/`, `/assets/`, `/vendor/`; sitemap index `/pt/gw/sitemaps.xml`. `/pt/categoria/empregos/ofertas-de-emprego` 200 (599 201 B, «Empregos e Ofertas de Emprego em Guiné Bissau»): the category's filter form (Área de Emprego, Horário, Intervalo de Salário — «Turismo - Рotelaria» with a Cyrillic Р in the template), fourteen city links `?location=<city>&c=497&sc=799`, the sidebar's category list with its counts — **«Empregos (0)»** beside «Veículos (295)» — and **not one advert link on the page** (every link is a category, a city filter, «registre», «publicados/crio» = post an ad). **The «497 Empregos» of 2026-09-13 (#421, #550) is the `<option value="497">Empregos</option>` of the search form — the category's id — not a counter.** The declared sitemap index for the country lists `pages.xml`, `categories.xml`, `cities.xml` and no posts file. Two reads of the category page: the counts identical** · 2026-09-21 -->
<!-- witness: the site's own sidebar count «Empregos (0)» and the absence of any advert link on its job category page; the country's sitemap index without a posts file · 2026-09-21 -->

**What this is.** A generic classifieds engine (the same template serves
several Lusophone countries — `/pt/gw/` is Guinea-Bissau) with a job
category. On 2026-09-13 the country search read «497 Empregos» and six
advert links; on 2026-09-21 the page shows the category's id 497 in its
form, zero in its sidebar, and no advert at all.

**What was measured, and what it means for #550.** The adapter the issue
describes would walk the category and print the walked count against the
stated one; today the stated one is 0 and the walk has nothing to walk. A
script that emits nothing is not a coverage (the 2026-09-13 decision, #404),
so no script is written; the issue keeps this measurement in its thread and
the next control is the same page — `Empregos (N)` with N > 0 and advert
links under it is what reopens the adapter. **No verdict on the site**: a
category empty on a given day is a measurement, not a closure.

**Not established, consigned as read:** the six links of 2026-09-13 (their
addresses were not kept) and the origin of the Cyrillic glyph in the
template.
