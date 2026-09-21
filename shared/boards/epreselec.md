# Board adapter — ePreselec (the InfoJobs / Adevinta ATS, one tenant at a time): the tenant's `/Ofertas/Ofertas.aspx` is one WebForms page stating its count («Total ofertas: 16»), `?Id_Oferta=` renders the advert on it; the host's rate control answers a CAPTCHA page as an HTTP 200 — read as the challenge it is, exit 9; `epreselec.py`

<!-- verified: 2026-09-21 -->

<!-- hosts: culligan.epreselec.com, eroski.epreselec.com -->
<!-- host-forms: {tenant}.epreselec.com -->
<!-- host-forms-basis: read — `epreselec.py:DOMAIN` with the tenant as its subdomain (`tenant_of`), one per run, every other host refused before the gate; the vendor's `www.epreselec.com` is not a board · 2026-09-21 -->
<!-- script: epreselec.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants with adverts and one former tenant, 2026-09-21 06:15–06:20 UTC, the declared client, the guard on the exact path first. Rules (`culligan`, 196 B, read once before the challenge): `dotbot` and `trovitBot` refused `/`; `User-agent: *` refuses `/ScriptResource.axd`, `/WebResource.axd`, `/*.axd$` — the framework's resources; no agent of this project named, no Crawl-delay. The list `/Ofertas/Ofertas.aspx` (200; Culligan 72 617 B «Total ofertas: 16», Eroski «34»): one page, a `<li>` per advert (`data_idOferta`, title, date «16 de septiembre, 2026»), the province filter a postback never replayed; `epreselec.py jobs` live: **Culligan 16 emitted, states 16 — equal; Eroski 34 = 34 — equal**, one advert read (Eroski 3217349: DONOSTIA/SAN SEBASTIÁN, Guipúzcoa, 10 vacancies, four sections). `bkspain.epreselec.com` (a Facebook link of 2024) answers its «404 - Page not found» as an HTTP 200 (2 334 B) — not a tenant, exit 3. **The transport serves, then challenges**: after about twelve requests in two minutes (06:15–06:17) every path — `/` and `/robots.txt` included — answered HTTP 200 with the same 11 621 B «Pardon Our Interruption» (md5 f774ef2293e6 on every host and path; «you were a bot … a power user moving with super-human speed», a CAPTCHA to «regain access»); `_robots` reads that body as `unrecognised` (no rules, `certain: False`); ten seconds between requests (06:19–06:20, six requests) were all served** · 2026-09-21 -->
<!-- witness: the page's own «Total ofertas: N» — `epreselec.py jobs` prints it beside the emitted count («16 emitted — the page states 16: equal», «short» when rows are missing); the challenge page is never counted as a page: the run ends with 9 and names the request · 2026-09-21 -->
<!-- route: http · 34 · 2026-09-21 -->

**Issue #490 (under #406, the ATS families — bloc ES/LATAM). Tenants found
by the family's signature `epreselec.com/Ofertas/Ofertas.aspx` in a search
engine on 2026-09-21: `culligan` (16), `eroski` (34), and `fcc`, `dia`,
`compassgroup`, `salesland`, `isprox`, `grupoexterna`, `serviciosreunidos`,
`accessett` listed by the engine and not read; `bkspain` (a 2024 link) is
gone.** Rank: `votes.sh` read at 06:14 UTC — #490 first `adapter` issue
outside cd's #479–#488 series (0 👍 everywhere, the numbers' order).

## What ePreselec is, and where its tenants live

ePreselec (Adevinta Jobs — the ATS «linked with InfoJobs», its «own
employment website» for the employer) publishes an employer's «Ofertas de
empleo» on `<tenant>.epreselec.com` — an ASP.NET WebForms application
(`__VIEWSTATE`, `__doPostBack` on every control): the list, the advert, the
province filter and the application all live on `/Ofertas/Ofertas.aspx`.
**The user names the tenant** by its subdomain (`eroski`), its host or the
list's URL; the vendor's own host is refused before any request.

## The route — one page for the list, one query for the advert

```
GET https://eroski.epreselec.com/Ofertas/Ofertas.aspx                       200 — «Total ofertas: 34», 34 <li>
GET https://eroski.epreselec.com/Ofertas/Ofertas.aspx?Id_Oferta=3217349     200 — the same page with pnlVacancy rendered
GET https://bkspain.epreselec.com/Ofertas/Ofertas.aspx                      200 — «404 - Page not found»: not a tenant (exit 3)
GET https://culligan.epreselec.com/                                         200 — «Pardon Our Interruption», 11 621 B: the challenge (exit 9)
```

The list is complete on its one page (no pager seen at 16 and 34); each
row carries the id (`data_idOferta`), the title (`op-titulo`) and the
date (`op-fecha`, emitted as written and as ISO); the location is on the
advert only. The advert: `<h1>` (`lDescripcion`), «Localidad»,
«Provincia», «Nº Vacantes (puestos)», then «Descripción» (the employer's
presentation, `lDescripcionEmpresa`), «Funciones», «Requisitos», «Se
ofrece» — `description` is «Funciones» (the job) and every section is
under `sections`. No JobPosting. The employer is the page's `<title>`
(«Ofertas de empleo - EROSKI - ePreselec»).

## The challenge — a CAPTCHA served as a 200, and what the adapter does with it

**Twelve requests in two minutes made every path answer the same
«Pardon Our Interruption» page, HTTP 200, `/robots.txt` included** — the
Imperva/Distil shape with a CAPTCHA to «regain access». Two things follow.
*The guard* reads that body as `unrecognised` (the standard since #283:
no rules read, `certain: False`, open) — correct, and it says nothing of
the pages. *The adapter* reads every 200 for the challenge's own title
and, when it is there, **dies with exit 9** (`_ua.browser_fallback`, the
browser exit) naming the request: the CAPTCHA is never answered and never
asked of anyone (borne 2); a tab served without it is the legitimate
route the day the client is refused. Ten seconds between requests
(`_pace`, `own=10.0`) kept six requests served on 2026-09-21; a `jobs`
run is one request, an `ad` one more. Not a verdict of closure.

## Withheld, and the guard

E-mail addresses and telephone numbers scrubbed from the sections; the
application (`Inscribirme a esta oferta`, a postback into an account) and
the «Denunciar» control never touched; `contacts_withheld` on every
record; the site states no country (`--country-code` stamps what the user
names, and says so). Guard in `tests/`: the count beside the emitted
number, a repeated id once, the date as ISO, the employer from the title,
the advert's fields and scrubbed sections, the 200 challenge ending the
real `request()` with 9, the 200 «Page not found» as a non-tenant (3), a
page without the list (6), bad addresses and tenants refused, another host
never sent (7) — 7 mutations on the committed file, 7 red (2026-09-21).
