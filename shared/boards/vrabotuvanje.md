# Board adapter — Vrabotuvanje (`vrabotuvanje.com.mk`, North Macedonia): a shared proxy selected by a header, 698 advertisements the board itself states, and a sitemap that is an archive

<!-- verified: 2026-09-12 -->

<!-- hosts: vrabotuvanje.com.mk, www.vrabotuvanje.com.mk -->
<!-- script: vrabotuvanje.py -->
<!-- host-forms: vrabotuvanje.com.mk -->
<!-- host-forms-basis: read — `vrabotuvanje.py:BASE`, a single literal, the apex; `www.` is named in `hosts:` because the sitemap index declares its children there and `ad --url` accepts it, but the script fetches the apex only (both forms serve the same rules, guard taken on both, 2026-09-12) · 2026-09-12 -->
<!-- countries: MK -->
<!-- content: measured · 698 distinct advertisement ids over 7 pages of `/api/proxy/jobs/search` with `x-app: vrabotuvanje.com.mk`, **and the envelope states `total: 698` — equal**; all 698 `isActive`, published 2026-04-24 → 2026-09-11; `vrabotuvanje.py search` at 11:14 UTC · 2026-09-12 -->
<!-- witness: the board's own `total` in the search envelope, printed beside the distinct count in the same run («698 emitted, board states 698 (x-app: vrabotuvanje.com.mk) — equal»; «k short» when they part) — and the negative control: the same URL WITHOUT the header states 2 006, in Croatian · 2026-09-12 -->

**North Macedonia's second card and its first adapter** — `kariera-mk.md`
is measured and refused at the transport; this host answers 200 to the
declared identity on every path read. **An Alma Career board** (the MojPosao
platform: brand assets on `static.mojposao.hr`, `appleClientId:
hr.almacareer.borg.apple.login`), which is exactly why one header decides
what the proxy answers. Measured 2026-09-12 11:08–11:16 UTC, the guard on the
exact path first, every fetch under the declared identity.

## Rules and transport

```
robots.txt      200, 567 B — `User-agent: *` · `Allow: /` · 9× `Disallow: /*?source=…` · `Disallow: /*?utm_source`
                `facebookexternalhit`/`Facebot` Allow: / · `Amazonbot` Disallow: / · Sitemap · `Crawl-delay: 1` (last line, after the Amazonbot group)
identity("/")   http, claude-user — both tokens fall in `*`; certain: True
GET /                          200, 221 338 B — Nuxt SSR, home; `featured-jobs` in the payload states total 678 (a subset, not the board)
GET /rabotni-mesta             200,  90 681 B — the listing page: chrome, 1 advertisement link, results fetched client-side
GET /api/proxy/jobs/search     200 — the route: JSON envelope {total, totalPages, items[].jobs[]}, 100 a page
GET /api/proxy/jobs/<uuid>     200 — the advertisement in full
GET /sitemap.xml               200, 755 B — 5 children on www.: sitemap-job-1, -job-2, -position-1, -company-1, -location-1
```

**The refusals are the nine `?source=` tracking variants the site's own cards
carry (`?source=jobs_page`, `?source=job_details_recommended`, …) and
`?utm_source`.** The adapter never appends one: the canonical address is
rebuilt from the id and slug, and a `?source=` URL given to `ad` is stripped
to its uuid. `Crawl-delay: 1` sits at the foot of the file after the
`Amazonbot` group — whichever group it belongs to, the adapter spaces 2 s.

## The route, and the header that IS the board

The Nuxt bundle creates its client with `baseURL: "/api/proxy"` and sends
`x-app: <project.domain>` on every call (`CcyFDE_X.js`, `dj()` — read, not
guessed). **The proxy is shared across Alma Career's boards, and the header
selects which one answers:**

```
GET /api/proxy/jobs/search                                     total 2 006 — «Voditelj smjene / Rukovodeće osoblje (m/ž)», Rijeka   <- no x-app: another country
GET /api/proxy/jobs/search   x-app: vrabotuvanje.com.mk        total   698 — «Водоводџија / Водоинсталатер», Скопје              <- this board
```

*Both are 200, both are well-formed, both are plausible.* A count taken
without the header is a number about Croatia filed under North Macedonia,
and nothing in the envelope says so — `search`, `searchSource`, `sortBy`
read the same. **So the adapter always sends the header and prints it beside
the count**, and the negative control above is the witness that the header
is load-bearing.

Parameters, from the app's own schema (`aX = w.object({…})`): `query`
(strings), `locations` (place names as the site writes them — `Скопје`),
`positions` (ids), `newJobs`, `sortBy: adtype | relevance`, `page`. The
adapter exposes `--query`, `--location`, `--sort`, `--pages`, `--limit`.

## The count

```
698 emitted, board states 698 (x-app: vrabotuvanje.com.mk) over 7 page(s) of 7 declared — equal.
```

100 per page, 7 pages, 698 distinct uuids, zero overlap between pages (checked
pages 1–2 by hand before the walk: 0 shared ids). All 698 `isActive`;
`publishedAt` from 2026-04-24 to 2026-09-11. Format mix on the day:
FEATURED-HOME 654 · EXCLUSIVE-HOME 22 · BASIC 19 · HIGHLIGHTED 2 · FEATURED 1.
Location: Скопје 489, Штип 25, Тетово 17, Битола 16, Струмица 15, Куманово 14.
`--location Битола` → 23 emitted, board states 23 — equal (the filter
reduces, and the board's total follows it).

**One advertisement in 698 carries a salary** (`30 000–35 000 mkd`); the
other 697 have `salary: {from: 0, to: 0}` or `null`, emitted as `null`, never
as zero.

**Ten of 698 have `organization: "incognito"`** — a bare string where the
others carry an object. The adapter emits `employer: null,
employer_hidden: true` for them, never the placeholder word. *On the
advertisement record the same ten carry `employer.name: "Vrabotuvanje.com за
клиентот"` — the board recruiting for an unnamed client.* **That name is the
intermediary, not the employer**, and the row says so with `employer_hidden`;
`ВРАБОТУВАЊЕ ХР СОЛУТИОНС Скопје` (18 advertisements) reads as an agency name
related to the board — a reading, not established — and is emitted as published.

## The sitemap is an archive

```
sitemap-job-1.xml   50 000 <loc>, <lastmod> 2025-02 → 2026-07   (49 979 dated 2025)
sitemap-job-2.xml   31 360 <loc>, <lastmod> 2025-06 → 2026-09
```

81 360 `/rabota/<uuid>/<slug>` URLs — **116 times the live count**. The
uuids are v1 (time-based); the file lists what was ever published, and a
`<lastmod>` is not a liveness. Not the route, and no `sitemap` command.

## The advertisement

```
GET /api/proxy/jobs/7a0397f8-add9-11f1-97ec-022a7f4ce407   x-app: vrabotuvanje.com.mk
title · employer {name} · organization {id, name, logoUrl, web} · position {id, name} · rootPosition {id, name}
location {summary: "Скопје", items: [{address: "Skopski, North Macedonia"}, {address: "Skopje, North Macedonia"}]}
employmentTypes ["На неопределено време"] · workTypes ["on-site"] · salary null | {from, to, currency: "mkd"}
publishedAt · startsAt · endsAt · isActive · isDesigned · html (the designed body) · description · requirements · benefits
```

**On a designed advertisement (`isDesigned: true`, most of them)
`description` is the title repeated and the body is in `html`** — a table
layout with empty cells. The adapter emits the text of whichever is longer,
says which on stderr (`body read from html (1 311 characters)`), and
collapses the table's blank runs. Read in full on three: a hidden-employer
one (`9af7781b`), a BASIC one (`7429e943`, 960 characters), the salaried one
(`99cae94d`, 30 000–35 000 mkd, `benefits` filled). `rootPosition` is absent
on some (`position_group: null`).

The SSR page `/rabota/<uuid>/<slug>` embeds the same record in its Nuxt
payload (`mk/jobs/<uuid>` key, devalue-serialised) — a second way to the
same data; the adapter takes the JSON route because it is the one the page
itself takes.

## Configuration

```yaml
boards:
  vrabotuvanje:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials, no browser. `search` is one request per 100 advertisements
— 7 for the whole board on the day; `ad` is one.

## What is not established

- **The `positions` facet** — ids from `/api/proxy/jobs/search/filters`, not
  read; `--query` and `--location` were exercised, `positions` was not.
- **Whether `total` counts what the walk counts under a `query`** — equal
  on the empty search and on `--location Битола`; a text query was not
  compared.
- **What `Crawl-delay: 1` binds** — the line follows the `Amazonbot` group;
  the guard reports no delay for our tokens, and the adapter spaces 2 s
  either way.
- **`www.` vs apex** — same rules, same proxy; only the apex was walked.

## 2026-09-12 — shipped

`vrabotuvanje.py search`: 698 distinct, board states 698 — equal; without
`x-app`, 2 006 in Croatian. `ad` on three records. Six tests; seven
mutations on a detached worktree (`python3 -B`), seven red — an eighth,
on the URL regex, was green because the canonical address is built from the
record and not from the input, and was replaced by one on the builder.
