# Board adapter — easy-prace.cz (Czechia): two stores in two sitemaps — 10 121 of its own and 24 546 republished from the Úřad práce ČR — keyed apart, against the listing's own 34 575

<!-- verified: 2026-09-13 -->

<!-- hosts: www.easy-prace.cz, easy-prace.cz -->
<!-- script: easyprace.py -->
<!-- countries: CZ -->
<!-- content: measured · rules read twice and certain (90 B: `Allow: /` and one Sitemap line, no agent named; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200: the index names two advertisement files, `easyprace-aktivni-easy.xml` (1 829 519 B, **10 121** `/nabidka/<slug>/<id>`, the board's own) and `easyprace-aktivni-up.xml` (4 196 733 B, **24 546** `/volne-misto/<slug>/<id>`, the Úřad práce ČR republished) — 34 667 rows keyed by store, two ids colliding across the stores; `/nabidka-zamestnani` states «34 575 výsledků» (34 578 three minutes earlier) and pages to `/strana/865` — 92 more emitted than stated, two witnesses never merged; no JSON-LD on the advertisement, one template for both stores, a contact person named on the page and never read · 2026-09-13 17:31 UTC -->
<!-- witness: the listing page's own «34 575 výsledků» on `/nabidka-zamestnani` (2026-09-13 17:31 UTC; 34 578 at 17:29) beside the 34 667 rows of the two sitemaps — «34 667 emitted, site states 34 575 — 92 more emitted than the site states», printed by `easyprace.py list` and never merged; a single-store run is not compared, since the listing counts both -->

**Shipped 2026-09-13 under #352.** Every fetch under the declared identity,
the guard on the exact path first. *Page Tchéquie of 2026-09-01 counted
9 862 + 23 620 = 33 482 in the same two files; twelve days later
10 121 + 24 546 = 34 667.*

```
easyprace.py list                  # both stores — two requests of 1.8 and 4.2 MB, then the listing for its count; ~20 s
easyprace.py list --store up       # the Úřad práce republication alone (not compared: the listing counts both)
easyprace.py ad --url https://www.easy-prace.cz/nabidka/<slug>/<id>        # or /volne-misto/<slug>/<id>
```

## The rules — ninety bytes

```
robots.txt      90 B, md5 67a8379e07df, read twice, certain: True — `User-agent: *` / `Allow: /` / `Sitemap: https://www.easy-prace.cz/data/sitemap/easyprace-index.xml`
identity("/")   http, claude-user — no agent named
verdict()       sweep True, certain True, crawl_delay none  -> Pace(HOST, own=1.0), one second, ours
allowed()       True on `/`, `/nabidka-zamestnani`, the four sitemap files, `/nabidka/…/<id>`, `/volne-misto/…/<id>`
```

## The sitemaps — two stores, named by their file

| question | answer (2026-09-13, 17:28–17:31 UTC) |
| :-- | --: |
| `easyprace-index.xml` | 605 B, four files: `vyhledavani` (search facets, never read), **`aktivni-easy`**, **`aktivni-up`**, `clanky` (articles, never read) |
| `aktivni-easy` — the board's own | **10 121** `<loc>`, all `/nabidka/<slug>/<id>`, a `lastmod` and a `priority` each; ids in the 6xx xxx range |
| `aktivni-up` — the Úřad práce ČR, republished | **24 546** `<loc>`, all `/volne-misto/<slug>/<id>`; ids in the 1 4xx xxx range; «dělníci v oblasti výstavby a údržby» 642, «pomocní kuchaři» 355, «kuchař-ka» 250 — one record per place |
| the two id spaces | **separate — two numbers collide across the stores**, so the ledger key carries the store: `easyprace:easy:<id>` / `easyprace:up:<id>`; `--store` reads one |
| the listing's own count — `/nabidka-zamestnani` | **«34 578 výsledků»** at 17:29, **«34 575»** at 17:31 (279 388 B, 40 links a page, pager to `/strana/865`) → «34 667 emitted, site states 34 575 — 92 more emitted than the site states» |
| the root | per-employer counts only («Advantage Consulting, s.r.o. 1971 nabídek», «ManpowerGroup s.r.o. 601») — no total; not read by the adapter |

**The two witnesses are printed apart and never merged.** *92 more in a
sitemap than in a listing that lost three in three minutes is two clocks —
the file regenerated on one, the listing counted on another.*

## The advertisement — one template for two stores, and a person the page names

`/nabidka/stevard-ka-mezinarodni-vlaky-…/620969` (82 626 B) and
`/volne-misto/zdravotni-sestra/1469963` (70 745 B) — **no JSON-LD** on
either; the same `NabidkaDetail-*` template: the `<h1>` title; the employer
in `NabidkaDetail-company` («JLV, a.s.», «DentLive s.r.o.»); the salary in
`NabidkaDetail-salary` («33 000 - 44 000 Kč») when published; label/value
pairs `NabidkaDetail-infoLabel` / `-infoValue` — «Lokalita» (an address, «…
a další»), «Úvazek», «Vzdělání», «Vhodné pro», «Ubytování»; then content
rows with an `<h2>` each: on the board's own advertisements «Popis pracovní
nabídky», «Požadujeme», «Nabízíme», «Jiná sdělení» — joined as the
description —, on the Úřad práce records «Směnnost», «Pracovní období» —
fields — and **no description**. «Aktualizováno před pár hodinami» is
relative: the date is the sitemap's `lastmod`. **The page names a contact
person under «Kontaktní osoba» — a name, never read, never emitted**
(tested). No `mailto:`, no `tel:`.

## What the adapter does, and refuses to do

- **Two sitemap requests and one listing request** — no page walk. A file
  of one store that lists a URL of the other store's shape sets it aside
  (counted, said); a file that disagrees with itself prints no count.
- **Never compares a single store to the listing** — the listing counts
  both.
- **Never emits the contact person, nor any contact.**
- **Not a verdict that anything is closed** — nothing refuses us.

## Tests

`TwoStoresInTwoSitemapsKeyedApartAndTheContactPersonNeverRead` in
`tests/test_core.py` — two cases (two stores with a colliding id keyed
apart, a foreign shape set aside, the listing compared to both and not to
one, a file that disagrees with itself; the advertisement read by its
blocks, the rows split into fields and description, the person absent from
the output, a non-advertisement URL refused). Six mutations under
`python3 -B` on a detached copy, six reds: the store key dropped from the
ledger, the store check dropped, the single-store comparison allowed, the
stated figure replaced by the row count, the row field mapping dropped, the
fields joined into the description.

## Provenance

- `ep/robots.txt`, `ep/easyprace-index.xml`, `ep/easyprace-aktivni-{easy,up}.xml`,
  `ep/root.html`, `ep/list.html`, `ep/ad-{easy,up}.html` — 2026-09-13
  17:28–17:30 UTC, `bin/fetch-body.py`, provenance beside each; scratchpad
  of `claude-job-hunt-ab`.
- `easyprace.py list --limit 1` at 17:31:29–17:31:49 UTC: the two
  `[easyprace]` lines quoted above verbatim.

## 2026-09-14 — the register itself is direct now

The Úřad práce ČR store this board republishes (24 546 `/volne-misto/` on
2026-09-13) is read at its source by `uradprace.py` (`uradprace.md`, #350):
the Ministry's open-data file carried 39 887 postings for 101 207 positions
on 2026-09-13 — 15 341 more than the republication. The `--store up` run
here stays what it is: the board's copy, keyed apart.
