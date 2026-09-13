# Board adapter — Profession.hu (Hungary): 12 415 advertisements in 23 sector sitemaps against the listing's own 19 329, two `/en/` twins never read because the rules refuse them, and an expiry that is a formula

<!-- verified: 2026-09-13 -->

<!-- hosts: www.profession.hu, profession.hu -->
<!-- script: profession.py -->
<!-- countries: HU -->
<!-- content: measured · rules read twice and certain (1 896 B, `*` refused 45 paths — accounts, applications, the PDFs, and **`/en/`** —, no AI agent named; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200: `sitemap-listings-index-hu.xml` names 23 sector files that hold 12 427 `<loc>`, **12 415** distinct advertisements `/allas/<slug>-<id>` (10 in two sectors) and 2 `/en/advertisement/…` twins set aside; `/allasok` titles «19329 db» — 6 914 short, two witnesses never merged; a `JobPosting` on the advertisement with the employer's `Organization/<id>`, no `jobLocation` (the place is page microdata), and a `validThrough` that is the read time plus thirty days · 2026-09-13 17:23 UTC -->
<!-- witness: the listing page's own title «Állások, munkák és állásajánlatok - 19329 db - 2026 Szeptember» (2026-09-13 17:23 UTC) beside the 12 415 advertisement-shaped URLs of the 23 sector sitemaps — «12 415 emitted, site states 19 329 — 6 914 short», printed by `profession.py list`, never merged -->

**Shipped 2026-09-13 under #359 — the first Hungarian adapter.** Every
fetch under the declared identity, the guard on the exact path first.
*Page Hongrie of 2026-09-01 counted 11 451 in the same 23 files; twelve days
later 12 415.*

```
profession.py list                 # 23 sector sitemaps at 1 s, then /allasok for its count — 24 requests, ~25 s
profession.py ad --url https://www.profession.hu/allas/<slug>-<id>
```

## The rules — 45 refusals, one of them a whole language, and nothing that names us

```
robots.txt      1 896 B, md5 1ca7b4acfd86, read twice, certain: True — `*`: 12 Allow, 45 Disallow (*/account/, */jelentkezes/, */munkaado/, */munkavallalo/, /cvgen/, **/en/**, /general/, the ASZF and privacy PDFs, *?rss$ …); an `AdsBot-Google` group; no AI agent named
identity("/")   http, claude-user
verdict()       sweep True, certain True, crawl_delay none  -> Pace(HOST, own=1.0), one second, ours
allowed()       True on `/`, `/allasok`, `/sitemap-listings-index-hu.xml`, `/allas/<slug>-<id>` — **False on `/en/advertisement/<slug>-<id>`**
Sitemap:        six lines — sitemap.xml, directory-listings, listings-index-hu, categories-index-hu, search-intent-hu, blog
```

## The sitemaps — 23 sectors, one id, and two URLs the rules refuse

| question | answer (2026-09-13, 17:20–17:23 UTC) |
| :-- | --: |
| `sitemap-listings-index-hu.xml` | 3 145 B, 23 files `sitemap-listings-<sector>-hu.xml` — admin, banking, building, custrserv, education, engineering, environment, finance, healthcare, hospitality, hr, itdev, itops, labor, legal, logistics, management, manufacturing, marketing, public, sales, skilled, ssc |
| `<loc>` over the 23 | **12 427** (skilled 532 224 B the largest, management 5 217 B the smallest); a `lastmod` per URL |
| advertisements `/allas/<slug>-<id>` | **12 415** distinct ids — **10 sit in two sectors** (the adapter keeps both sector names on the row) |
| `/en/advertisement/<slug>-<id>` | **2**, listed by the sitemap and **refused by `Disallow: /en/`** — set aside, never read, never emitted; `ad --url` on one is refused before any request (exit 2); neither has a Hungarian twin in the files |
| the listing's own count — `/allasok` | **«19329 db»** in the `<title>`, «19329 állás» in the body (423 320 B, 40 advertisement links on the page) → «12 415 emitted, site states 19 329 — 6 914 short» |
| the largest slugs | «shop-eladot-keresunk» 55, «gyorsettermi-diakmunka» 39, «kutkezelot-keresunk» 38 — one employer's many places, one id each |

**The two witnesses are printed apart and never merged.** *6 914 short is a
large gap: whether the listing counts advertisements the sitemaps leave out,
or counts what the sitemaps split, is a question for a walk of `/allasok?page=`
that this adapter does not do — it says both numbers and stops there.*

## The advertisement — a JobPosting, the employer's number, a place outside the JSON, and a formula

`/allas/sales-business-development-specialist-mint-consulting-kft-2999723`
(153 177 B) carries one `JobPosting`: `@id` `…/JobPosting/2999723`, `title`,
`description` (HTML), `datePosted` 2026-09-12, `employmentType`
«Alkalmazotti jogviszony», `occupationalCategory`, `jobLocationType`
`TELECOMMUTE`, `applicantLocationRequirements` «Magyarország»,
`hiringOrganization` with **`@id` `…/Organization/123493` — the EMPLOYER's
number, kept apart from the advertisement's** — and **no `jobLocation`**:
the place is microdata on the page, `itemprop="addressLocality"` «Budapest»
under «Munkavégzés helye», with the mode «Hibrid» before the separator.
**`validThrough` is a formula**: `2026-10-13T19:21:22` on the read of
17:21 UTC, `2026-10-13T19:23:12` on the read of 17:23 — the read time plus
thirty days, not a date the employer set (the Meteojob/HelloWork trap). The
adapter emits `valid_through: null` and `valid_through_as_published`, and
never offers it as an expiry. No salary. No `mailto:`, no `tel:` — the
page's apply link is not emitted.

## What the adapter does, and refuses to do

- **24 requests at 1 s** — the index, the 23 sector files, the listing; a
  sector file that fails is a partial walk (exit 6) and no count is printed.
- **Never reads `/en/`** — refused in writing; a refusal read in the rules
  is honoured by every route.
- **Never emits a contact**, never offers the formula as an expiry.
- **Not a verdict that anything is closed** — nothing refuses us.

## Tests

`TwentyThreeSectorFilesOneIdAndARefusedLanguageNeverRead` in
`tests/test_core.py` — two cases (the sectors merged on the id, the `/en/`
twins set aside and never asked, the title's count printed apart, a file
that disagrees with itself; the advertisement with the employer's number
apart, the place from the page, the formula never offered, no `mailto:`,
and `/en/` refused before any request). Six mutations under `python3 -B`
on a detached copy, six reds: the `/en/` branch dropped, the dedup removed,
the stated figure replaced by the row count, `employer_id` from the
advertisement's id, `valid_through` passed through, `AD_RE` widened to
`/en/advertisement/`.

## Provenance

- `prhu/robots.txt`, `prhu/index.xml`, `prhu/sitemap-listings-*-hu.xml`
  (23), `prhu/list.html`, `prhu/ad.html` — 2026-09-13 17:20–17:21 UTC,
  `bin/fetch-body.py`, provenance beside each; scratchpad of
  `claude-job-hunt-ab`.
- `profession.py list --limit 1` at 17:22:46–17:23:11 UTC: the two
  `[profession]` lines quoted above verbatim; `ad` at 17:23:12 UTC.
