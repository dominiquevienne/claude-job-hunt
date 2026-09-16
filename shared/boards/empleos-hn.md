# Board adapter — Empleos.hn (`empleos.hn`, Honduras): the Red de Desarrollo Sostenible's free board, a Drupal site whose advanced search pages to its last page on the server (20 pages of 16 on 2026-09-16, no total printed) and whose ad carries a JobPosting, labelled fields and the employer's application address — never emitted; `empleos_hn.py`

<!-- verified: 2026-09-16 -->

<!-- hosts: empleos.hn, www.empleos.hn -->
<!-- script: empleos_hn.py -->
<!-- host-forms: empleos.hn -->
<!-- host-forms-basis: read — every card link is `https://empleos.hn/jobs/<slug>`, the canonical on the apex (`www.` appears only in the 404 sitemap's canonical); `empleos_hn.py` names the apex as a literal and rewrites a `www.` ad address · 2026-09-16 -->
<!-- countries: HN -->
<!-- content: measured · **rules read (2 027 B, Drupal's file for `*`): the engine's directories, `/admin/`, `/search/`, `/node/add/`, `/user/login`, `/user/register` … refused; no Crawl-delay. The root and `/empleos` (200, 83 125 B) show six cards and no pager; `/busqueda-avanzada` (200, 65 830 B) — a Drupal view, not `/search/` — serves sixteen `tarjeta` cards a page (the class names are swapped on the site: `nombre-empresa` holds the title, `nombre-posicion` the employer; a department in `ubicacion`; «Fecha Max. Postulación» as a `<time>`; «Ver Más» to `/jobs/<slug>`) and a pager `?page=0 … 19`: 20 pages, 320 the bound, no total printed anywhere; `?page=3` 16 cards; `/sitemap.xml` 404; the ad `/jobs/<slug>` (200, 52 269 B) a JobPosting — title, datePosted, validThrough, employmentType («Indefinido»), hiringOrganization (name, @id), jobLocation (the department, HN), a baseSalary skeleton (HNL, MONTH, no value) — beside Drupal fields «Nivel de experiencia», «Número de Vacantes», «Modalidad», «Género», «Vehículo o Licencia», «Categoría», «Departamento», «Tipo de Contrato», «Fecha max. de Postulación», «Descripción» and «Correo para aplicar:» (the employer's address, Cloudflare-obfuscated); `empleos_hn.py list --pages 2` on the day: «32 emitted from 2 page(s) of the 20 the pager names (the site prints no total; 20 × 16 = 320 is the bound)»** · 2026-09-16 -->
<!-- witness: none — the site prints no total; the pager's last page (19, 0-based) read on page 0 is the walk's bound, 20 × 16 = 320, printed by `empleos_hn.py list` beside the emitted · 2026-09-16 -->
<!-- route: http · 320 · 2026-09-16 -->

**Issue #439 (opened under #413, Honduras searched on 2026-09-13). Measured
2026-09-16 06:25–06:27 UTC by the declared client, the guard on the exact
path first, `bin/fetch-body.py`; the script exercised on the same minutes.**
Rank: the pilot's risk order of 2026-09-14 10:4x, after PIVOT (#433). *A
free board of a development NGO («portal gratuito … donde empresas publican
vacantes. No manejamos procesos de selección ni recibimos CVs»): the ad
carries the employer's own application address, and that is exactly what
the adapter never emits.*

## The rules, and the one route that is not the search

```
robots.txt      200, 2 027 B — `*`: /core/, /profiles/, /admin/, /search/, /node/add/, /user/login, /user/register, /user/password, /user/logout, /comment/reply/, /filter/tips, /media/oembed
allowed('/busqueda-avanzada?page=3')   open, certain — a Drupal view at its own path, not `/search/`
allowed('/search/node')                refused, certain — never sent (exit 7 before the gate), with /user/, /register_asp, /register_emp, /cdn-cgi/
```

## The transport, dated

```
GET /                          200, 83 125 B, md5 f23aaa3790d5   (06:25:52Z)   6 cards, no pager, «2026 empleos» is the copyright line, not a count
GET /empleos                   200, 83 125 B, md5 22bf2dc97f89   (06:26:05Z)   the same 6
GET /busqueda-avanzada         200, 65 830 B, md5 cb879cd97170   (06:26:20Z)   16 cards, pager ?page=0 … 19
GET /busqueda-avanzada?page=3  200, 66 187 B, md5 4fb31a561b6e   (06:26:45Z)   16 cards, the pager still to 19
GET /sitemap.xml               404, 38 657 B                      (06:26:23Z)
GET /categorias-empleos        200, 48 752 B                      (06:26:26Z)   the category index, no card
GET /jobs/director-casa-hogar  200, 52 269 B, md5 5f52644a3b81   (06:26:48Z)   JobPosting + fields; «Correo para aplicar: [email protected]» (cf-obfuscated)
```

**The site prints no total.** `list` walks to the pager's last page and
prints emitted against the bound `pages × 16`; a bounded walk (`--pages`)
says so. *A count that comes only from our own walk is written as the walk,
never as the site's figure.*

## What the adapter emits, and withholds

`list`: id = the slug, url, title, company, department, valid_through
(from the card's `<time>`). `ad --url`: the JobPosting and the fields —
title, company, company_id, employment_type, department, salary currency /
unit / value (the value is absent on the day), posted, valid_through,
experience, openings, modality, gender, vehicle, category, the description
flattened and scrubbed. Guards: a page without a card exits 6; page 0
served again exits 6.

**Withheld:** «Correo para aplicar:» — the employer's application address,
obfuscated by Cloudflare on the page — is never emitted, not even
obfuscated (the test asserts the field's label, the `cfemail` token and the
placeholder are absent from the output); the description is scrubbed of
e-mail addresses and Honduran telephone numbers (`+504`, 8 digits);
`contacts_withheld` on every record; the logo not emitted; the accounts
(`/user/`, `/register_asp`, `/register_emp`) never sent.

## Tests and mutations

`AHonduranDrupalBoardWhoseSearchPagesToItsLastPageWithoutATotalAndWhoseAdCarriesTheApplicationAddressThatIsNeverEmitted`,
both ways on fixtures (the walk to the pager's last page with a repeated
slug read once, the swapped class names, `--pages`, the two exit-6 cases,
four refused addresses, the ad with its fields and the address's absence).
Mutation bench on a detached copy, `python3 -B`, 6 / 6 red: the pager's
last page not read · the same-cards guard dropped · the dedup dropped · the
swapped classes «corrected» the wrong way · the description not scrubbed ·
the application field emitted.
