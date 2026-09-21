# Board adapter — Gupy (Brazil's main ATS, one career page at a time): the career page's root ships every published job in its Next.js data and prints the count it ships («161 vagas»), `/jobs/<id>` ships the whole job the same way; `gupy.py`, the street never emitted

<!-- verified: 2026-09-21 -->

<!-- hosts: farm.gupy.io, renner.gupy.io, motiva.gupy.io -->
<!-- host-forms: {tenant}.gupy.io -->
<!-- host-forms-basis: read — `gupy.py:DOMAIN` with the career page as its subdomain (`tenant_of`), one per run, every other host refused before the gate; the vendor's `www`, `portal`, `suporte`, `attachments`, `front-statics-assets` hosts are refused as tenants · 2026-09-21 -->
<!-- script: gupy.py -->
<!-- countries: * -->
<!-- content: measured · **three career pages, 2026-09-21 06:26–06:28 UTC, the declared client, the guard on the exact path first. Rules: `/robots.txt` on a tenant answers the application's own HTML (21 525 B, a Next.js route named `robots`), not a rules file — `_robots` reads it `unrecognised` (no rules, `certain: False`); `portal.gupy.io` publishes 67 B allowing everything (04.09); no Crawl-delay. The root (200; FARM 179 064 B, Lojas Renner 160 204 B) is a Next.js page whose `__NEXT_DATA__` `pageProps.jobs` carries every published job — id, title, type, department, `workplace.address` (country, state, city), `workplaceType` — and whose text prints the count: `gupy.py jobs` live — **FARM 161 emitted, the page prints 161 — equal; Lojas Renner 92 = 92; Motiva 114 = 114**; one request is the board, no paging, no search call. `/jobs/<id>` (200, 105 487 B): `pageProps.job` — name, description, responsibilities, prerequisites, relevantExperiences (HTML), publishedAt, expiresAt, jobType, workplaceType, handicapped, city/state/country, `addressLine` (a street and a postcode), `jobSteps`, `company.subdomain` (`gruposoma` behind `farm`), `careerPage.name`; no JobPosting. An unknown subdomain answers 404 (exit 3)** · 2026-09-21 -->
<!-- witness: the page's own «N vagas» — `gupy.py jobs` prints it beside the emitted count («161 emitted — the page prints 161 vagas: equal», «short» when the data holds fewer, «prints no count» when the text has none) · 2026-09-21 -->
<!-- route: http · 161 · 2026-09-21 -->

**Issue #491 (under #406, the ATS families — bloc BR/LATAM). Career pages
found by the family's signature `<tenant>.gupy.io` in a search engine on
2026-09-21: `farm` (FARM, 161), `renner` (Lojas Renner's group page, 92,
which links its sister pages `lojasrenner`, `youcom`, `realize`,
`camicadocarreiras`, `uello`, `encantech` — each a tenant of its own),
`motiva` (114); `penso`, `randon`, `unimedjf`, `carreirasallos`,
`tech-career` listed, not read.** Rank: `votes.sh` read at 06:25 UTC —
#491 first `adapter` issue outside cd's #479–#488 series.

## What Gupy is, and where its tenants live

Gupy (São Paulo) is the ATS most Brazilian employers publish through:
each employer — or each brand of a group — has a career page on
`<tenant>.gupy.io`, a Next.js application whose server-rendered page
carries its data in `__NEXT_DATA__`. **The user names the career page**
by its subdomain (`farm`), its host or its URL; the job's
`company.subdomain` (the group behind the page) is emitted as `group`.
The aggregated `portal.gupy.io` is the vendor's portal, not a tenant.

## The route — one request for the whole board, one per job

```
GET https://farm.gupy.io/               200 — __NEXT_DATA__ pageProps.jobs: 161 · the text prints «161 vagas»
GET https://farm.gupy.io/jobs/12057784  200 — pageProps.job: the whole job
GET https://nao-existe-xyz123.gupy.io/  404 — not a career page (exit 3)
```

`jobs`: every item of `pageProps.jobs` — `id`, `url` (`/jobs/<id>`; the
page links it with `?jobBoardSource=gupy_public_page`, a tracking
parameter never added), `title`, `company` (the page's name),
`department`, `country` (`workplace.address.country` → ISO2), `state`,
`place`, `job_type`, `workplace_type`. `ad`: `title`, `company`, `group`,
`code`, `status`, `posted` (`publishedAt`), `closes` (`expiresAt`),
`country` (`addressCountryShortName`), `state`, `place`, `job_type`,
`workplace_type`, `open_to_disabled` (`handicapped`), `description`, the
three other texts under `sections`, the process `steps` (names only).

## Withheld, and the guard

The street and postcode (`addressLine`) never emitted; the pictures and
logos never emitted; e-mail addresses and telephone numbers scrubbed from
the texts; the application (an account) never touched; `contacts_withheld`
on every record. Guard in `tests/`: the list from the page data against
the printed count (equal, short, no count), a repeated id once, the
country from the job, the job page's fields with the street never emitted
and the texts scrubbed, a page without the data (6), a 404 (3), the
vendor's hosts and bad tenants refused before any request, another host
never sent (7) — 7 mutations on the committed file, 7 red (2026-09-21).
