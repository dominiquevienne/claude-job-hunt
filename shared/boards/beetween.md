# Board adapter — Beetween (a French ATS, one career site at a time): the career site's own JSON API — `POST /api/job/list` stating `numFound`, one hundred a page — and the vendor's apply page (the address France Travail and FHF relay) read through the backend's `jobs/byWid`; `beetween.py`, the employer named where the aggregators do not name it

<!-- verified: 2026-09-21 -->

<!-- hosts: proxiserve.jobs.beetween.com, welcoop.jobs.beetween.com, joker-interim.jobs.beetween.com, comptoir.jobs.beetween.com, app.beetween.com, apehi.beetween.com -->
<!-- host-forms: {tenant}.jobs.beetween.com -->
<!-- host-forms-basis: read — `beetween.py:DOMAIN` with the career site as its subdomain (`tenant_of`), or the employer's own host when the user names it (`welcoop.nos-recrutements.fr`, the address Welcoop's adverts link — the same API); one host per run, every other refused before the gate; `app.beetween.com` (the vendor's apply page) and `apehi.beetween.com` (its backend) only for `ad` on a relayed address · 2026-09-21 -->
<!-- script: beetween.py -->
<!-- countries: * -->
<!-- content: measured · **three career sites with adverts and one empty, 2026-09-21 06:49–06:53 UTC, the declared client, the guard on the exact path first. Rules: `<tenant>.jobs.beetween.com/robots.txt` 22 B `User-agent: * / Allow: /` on every site (md5 f77c87f977e0); `app.beetween.com/robots.txt` the Nuxt shell (4 065 B, the same for every path — `unrecognised`, no rules, `certain: False`); `apehi.beetween.com/robots.txt` a 74 B 404. The career site (Vue, `/js/app.<hash>.js`, API `/api` on the same host — read in the bundle: `hl.post("job/list")`, `hl.get("job/<wid>")`, `client/information`): `GET /api/client/information` names the employer (`completeName`); `POST /api/job/list` {page, rows} answers `numFound` and full records — `beetween.py jobs` live: **Proxiserve 216 emitted over 3 pages (100 + 100 + 16), numFound 216 — equal; Welcoop 31 = 31 (adverts linking `welcoop.nos-recrutements.fr`, the same API answers there); Joker Interim 31 = 31; Comptoir Des Voyages 0 = 0**; `rows=500` answered all 216 at once. A record: `id`, `wid` (ten characters), `title`, three HTML texts, `creationDate`, `city`, `region`, `country`, `gpsCoordinates`, `logo`, `contractType`, `salaryMin`/`Max`/`Unit`, `language`, `url`, `agency`, `categories`; `GET /api/job/<wid>` the same with `salaryCurrency`, an unknown wid HTTP 500. The vendor's apply page `app.beetween.com/WeaselWeb/p/#/apply/job/<wid>xx/<slug>` (the FHF and France Travail address; a hash route, nothing reaches the server) calls `GET https://apehi.beetween.com/WeaselWeb/api/jobs/byWid/<wid>` (its chunk `87ea881.js`, `fetchPost`): 200, 10 937 B — `recruitmentTitle`, `description`, `location`, `company` («Centre Hospitalier Coeur de Corrèze»), `locale`; an unknown subdomain answers 404 on `/api/client/information` (exit 3)** · 2026-09-21 -->
<!-- witness: the site's own `numFound` — `beetween.py jobs` walks one hundred a page to it and prints it beside the emitted count («216 emitted — the site states 216: equal», «short» when the pages end before it) · 2026-09-21 -->
<!-- route: http · 216 · 2026-09-21 -->

**Issue #493 (under #406, the ATS families — France). Career sites found
by the family's signature `jobs.beetween.com` in a search engine on
2026-09-21: `proxiserve` (216), `welcoop` (31), `joker-interim` (31),
`comptoir` (0), and `aismt13`, `voyageursdumonde`, `groupe-la-boite-immo`
listed, not read; the apply addresses come from `fhf.py` (4 of 18 ads on
2026-09-21) and, per `france-travail.md`, from the partner feed (BEETWEEN
38 of 150 Paris ads, the employer unnamed there).** Rank: `votes.sh` read
at 06:44 UTC — #493 first `adapter` issue outside cd's #479–#488 series.

## What Beetween is, and where its tenants live

Beetween (Rennes, since 2007) is an ATS whose employers publish in two
places: **a career site** on `<tenant>.jobs.beetween.com` — or under the
employer's own host (`welcoop.nos-recrutements.fr`) — a Vue application
with its own JSON API; and **the vendor's apply page** on
`app.beetween.com/WeaselWeb/p/#/apply/job/<wid>…`, the address the
multiposting sends to France Travail, FHF and the boards, a Nuxt
application whose backend is `apehi.beetween.com`. **The user names the
career site** by its subdomain, its host or its URL; the vendor's own
hosts are refused as tenants and used only for `ad` on a relayed address.

## The routes

```
GET  https://proxiserve.jobs.beetween.com/api/client/information          200 — completeName «Proxiserve», website
POST https://proxiserve.jobs.beetween.com/api/job/list  {page:1, rows:100} 200 — numFound 216, jobs[100]  · page 2: 100 · page 3: 16
GET  https://proxiserve.jobs.beetween.com/api/job/jd2k8y01a8              200 — the job (500 for an unknown wid: exit 6)
GET  https://apehi.beetween.com/WeaselWeb/api/jobs/byWid/gwbgkau3f0       200 — the relayed advert: title, description, location, company
GET  https://nope-xyz.jobs.beetween.com/api/client/information            404 — not a career site (exit 3)
```

**The key is the `wid`** (ten characters; the relayed address carries two
more — `gwbgkau3f04n` for `gwbgkau3f0` — the page's, not the wid's); the
ledger key `beetween:<wid>` on both routes, so the same advert read from
the career site and from a France Travail relay is one row. `jobs` emits
`url` as the site gives it (on its host or the employer's own), `title`,
`company` (the site's `completeName`), `agency`, `posted`
(`creationDate`), `country` (→ ISO2 when named) and `country_name`,
`region`, `place`, `lat`/`lon` (the city's coordinates), `contract_type`,
`contract_duration`, `salary` (min, max, unit, currency), `language`,
`categories`, `description` (the mission) and `sections` (Entreprise,
Profil). `ad` on a relayed address emits `title`, `company`, `location`
(«19000 Tulle, Nouvelle-Aquitaine»), `language`, `description`.

## Withheld, and the guard

The three texts scrubbed of e-mail addresses and telephone numbers; the
logo never emitted; the application (`/apply/job/`, an account or a form)
never touched; `contacts_withheld` on every record. Guard in `tests/`:
the walk to `numFound` (equal, short), a repeated wid once, the record's
fields with the logo never emitted and the texts scrubbed, an empty board,
the unknown tenant (3), a shell instead of JSON (6), the unknown wid's 500
(6, named), the apply page's wid with and without its suffix read on the
backend host and the relayed address kept, bad addresses and tenants
refused, another host never sent (7) — 8 mutations on the committed file,
8 red (2026-09-21).
