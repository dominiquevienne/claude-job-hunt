# Board adapter — Profesia.sk (Slovakia): 14 749 advertisements sorted out of a 7 MB sitemap by the shape of their URL, against the listing's own count of 14 773 — and the Czech front `profesia.cz` on the same stack, 1 094 against 1 095

<!-- verified: 2026-09-13 -->

<!-- hosts: www.profesia.sk, profesia.sk, www.profesia.cz, profesia.cz -->
<!-- script: profesia.py -->
<!-- countries: SK CZ -->
<!-- content: measured · rules read twice and certain on both hosts (2 204 B on `.sk`, 2 201 B on `.cz`, the same file to a few lines: `*` refused 44 paths — language facets, forms, CV routes, `search_offers*form=` — no AI agent named; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200: `/sitemap.php` (7 264 199 B on `.sk`, 645 638 B on `.cz`) holds 20 407 `<loc>` of which **14 749** advertisements `/praca/<employer>/O<id>` and 5 658 facets on `.sk`, 1 844 of which 1 094 `/prace/…/O<id>` and 750 facets on `.cz`; the listing pages' own search payload states `"count":14773` and `"count":1095` — 24 short and 1 short, two witnesses, neither corrected by the other; no JSON-LD on the advertisement, microdata `datePosted` and labels in two layouts, the employer's `C<id>` apart from the advertisement's `O<id>` · 2026-09-13 17:13 UTC -->
<!-- witness: the listing page's own `"count":N … "scenario":"standard"` (14 773 on `.sk`, 1 095 on `.cz`, 2026-09-13 17:13 UTC) beside the sitemap's advertisement-shaped URLs (14 749, 1 094) — printed by `profesia.py list` as «n emitted, site states N — k short», never merged; the visible «10000 pracovných ponúk» is a capped popup and is never read -->

**Shipped 2026-09-13 under #343 — the first Slovak adapter, and its Czech
twin under `--host`.** Every fetch under the declared identity, the guard on
the exact path first. *Page Slovaquie of 2026-09-01 counted 14 040 of 19 648;
twelve days later the same sort gives 14 749 of 20 407.*

```
profesia.py list                              # every advertisement of profesia.sk — one 7 MB sitemap, then the listing for its count; ~5 s
profesia.py list --host www.profesia.cz       # the Czech front, same stack — 1 094 on 2026-09-13
profesia.py ad --url https://www.profesia.sk/praca/<employer>/O<id>
```

## The rules — the same file on two hosts, and nothing that names us

```
robots.txt      .sk 2 204 B md5 dab75ad5bf2f · .cz 2 201 B md5 7bfd3825ad96 — read twice each, certain: True
                `*` refused 44 paths: /banner/ /images/ /wap/, the language facets (/sk/ /cz/ /de/ /en/*? /hu/*?), /partner/, /documents/…, *company_details.php, *search_offers*form=, *search_cv.php, *print=1, *ajax …
                the diff between the two: which language prefixes are refused, one `search_cv_submit.php`, one `/registrace-firmy`, and the Sitemap lines
identity("/")   http, claude-user — no AI agent named on either host
verdict()       sweep True, certain True, crawl_delay none  -> Pace(host, own=1.0), one second, ours
allowed()       True on `/`, `/sitemap.php`, `/praca/`, `/praca/<employer>/O<id>`, `/prace/…`
Sitemap:        http://www.profesia.sk/sitemap.php (+ kariera-v-kocke/sitemap_index.xml, editorial) · http://www.profesia.cz/sitemap.php
```

## The sitemap — one file, two shapes, and the shape decides

| question | `.sk` (17:09 → 17:12 UTC) | `.cz` (17:09 → 17:13 UTC) |
| :-- | --: | --: |
| `sitemap.php` | 7 264 199 B, 20 409 `<loc>` at 17:09, 20 407 at 17:12 — generated on the fly, it moves | 645 638 B, 1 844 `<loc>` |
| advertisements — `/praca/<employer-slug>/O<id>` | **14 749** distinct ids (14 751 at 17:09) | **1 094** (`/prace/…/O<id>`) |
| facets set aside — `/praca/<place>/`, `/praca/<position>/`, `/praca/<region>/` | 5 658 | 750 |
| `lastmod` | one per URL, 2026-08-13 07:29 … 2026-09-13 17:30 (+01:00) on the advertisements | idem |
| the listing's own count — `/praca/` → `"count":14773 … "scenario":"standard"` | **14 773** → «14 749 emitted, site states 14 773 — 24 short» | **1 095** → «1 094 emitted, site states 1 095 — 1 short» |
| the popup «Vybraným kritériám vyhovuje 10000 pracovných ponúk» | a capped figure in the e-mail agent's form — **never read** | — |
| the id space | shared: `O5338670` on `.sk`, `O5339846` on `.cz` — one sequence, two fronts; `ledger_id` is `profesia:<id>` on both | |
| the employer | **in the URL** (`manpowergroup-slovensko`, `lidl-slovenska-republika`) — 206 advertisements under `index-noslus`, 166 under `lugera-makler` | 385 under `manpowergroup`, 233 under `predvyber-cz` |

**The two witnesses are printed apart and never merged.** *24 short on a
file that moved by two URLs between two reads three minutes apart is the
listing being written while the sitemap is generated — the adapter says
both numbers and stops there.*

## The advertisement — no JSON-LD, two layouts, and an id that is the employer's

`/praca/manpowergroup-slovensko/O5338670` (112 245 B) and
`/prace/hana-cosmetics/O5339846` (99 295 B) — **no `JobPosting`** on
either; microdata and labels in **two layouts**: the board's own
(`itemprop` `title`, `hiringOrganization`, `jobLocation/address`,
`employmentType`, `description`, the labels in `<strong>`) and the one
used for advertisements «prevzatá z inej stránky» (taken over from another
site: `upper-info-box-title` / `-content`, `datePosted` and `industry` as the
only microdata). Common to both, and what the adapter reads: the `<h1>`;
«ID: N»; `itemprop="datePosted"` (ISO); «lokalita: <a>PLACE</a>»;
**«Spoločnosť: <a href="…/C<employerId>">NAME</a>» — the `C<id>` is the
EMPLOYER's page, kept apart from the advertisement's `O<id>`** (20401 for
ManpowerGroup, 227927 for Hana Cosmetics); `salary-range` when a salary is
published («1 700 - 2 000 EUR/mesiac»); «Druh pracovného pomeru» and «Termín
nástupu» by their label; the description from «Informácie o pracovnom
mieste» to «Základná zložka mzdy» / «Reagovať na ponuku». **The `.cz` front
serves Slovak-written advertisements for Slovak places** (Malý Cetín,
Slovensko, on 2026-09-13): `country` is the host's and `place` is the text,
which names the country when it is not the host's. No `mailto:`, no `tel:`
— nothing of the kind is read (the page's apply link is a `mailto:` on the
imported layout, and it is not emitted).

## What the adapter does, and refuses to do

- **One sitemap request, one listing request** — no page walk. The
  advertisement shape of ITS host only: a `.cz` URL in the `.sk` file is
  set aside, not emitted under `SK`.
- **`_sitemap.count` checks `<loc>` against `<url>`** and a file that
  disagrees with itself prints no count (exit 6).
- **Never emits a contact.** Never turns the popup's 10 000 into a count.
- **Not a verdict that anything is closed** — nothing refuses us.

## Tests

`OneSitemapSortedByShapeAndTheListingsOwnCountOnTwoHosts` in
`tests/test_core.py` — four cases (the shape of the host kept, facets set
aside, the listing's count printed apart and the popup never read; the
Czech front under its own host saying equal, a file that disagrees with
itself; the imported layout read by its labels with the employer's id apart
and no `mailto:` emitted; the board's own layout with its microdata). Six
mutations under `python3 -B` on a detached copy, six reds: the host check
dropped, the dedup removed, the `standard` scenario turned into `hot`,
`employer_id` taken from the advertisement's id, the description's stop
words dropped, the facet count replaced by the row count — *this last one
stayed green on a first fixture that had 3 facets for 3 rows; the fixture
was inert, not the guard, and it now has 4 against 3.*

## Provenance

- `prof/www.profesia.{sk,cz}.robots.txt`, `prof/www.profesia.{sk,cz}.sitemap.xml`,
  `prof/list-{sk,cz}.html`, `prof/ad-{sk,cz}.html` — 2026-09-13 17:09–17:11
  UTC, `bin/fetch-body.py`, provenance beside each; scratchpad of
  `claude-job-hunt-ab`.
- `profesia.py list --limit 2` and `--host www.profesia.cz --limit 1` at
  17:12:57–17:13:01 UTC: the four `[profesia]` lines quoted above verbatim.
