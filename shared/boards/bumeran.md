# Board adapter — Bumeran / Jobint (seven Latin American brands)

<!-- script: bumeran.py -->
<!-- verified: 2026-09-03 -->
<!-- countries: AR CL PE MX EC VE PA -->

**One platform wearing national brands, and the tell is a filename.** Every one
of them serves `sitemap_avisos_bum.xml` at the same path — **`_bum` for
Bumeran, surviving under names that share nothing with it.** No checksum finds
that; the file names it.

**Discovery is plain HTTP and rich. Reading an ad needs the browser.** The
hybrid shape, like `jobstore.md`.

**Everything below was verified against all seven live sites on 2026-09-03.**

## Eight brands, 71 483 ads

| Site | Country | Sitemap tag | Ads |
| :-- | :-- | :-- | --: |
| `bumeran.com.pe` | Peru | `bum` | **34 809** |
| `laborum.cl` | Chile | `bum` | 15 901 |
| `bumeran.com.ar` | Argentina | `bum` | 6 804 |
| `multitrabajos.com` | Ecuador | `bum` | 5 771 |
| `konzerta.com` | **Panama** | `bum` | 2 814 |
| `zonajobs.com.ar` | Argentina | **`zj`** | 2 832 |
| `bumeran.com.mx` | Mexico | `bum` | 1 795 |
| `bumeran.com.ve` | Venezuela | `bum` | 757 |
| | | | **71 483** |

**The countries are read from the board's own place vocabulary, not assumed
from the domain** — `konzerta.com` is Panama (`bocas-del-toro`, `chiriqui`),
which a `.com` says nothing about, and Chile numbers its regions
(`region-i`…). `sites --check` re-counts every site live rather than quoting
this table: **these are dated measurements, not properties.**

## The member the marker could not find

**`zonajobs.com.ar` serves `sitemap_avisos_zj.xml` and answers `404` on the
`_bum` name.** It was missing from the first version of this adapter — 2 832
Argentine ads left outside a file that already served 6 804 on the neighbouring
domain.

**And the reason it was missed matters more than the site.** The family was
identified by finding `_bum` in a `robots.txt`, and then its members were
looked for **by that same marker**. *A membership test that searches for the
family's own signature cannot find the member that renamed it.* The check
shared the property it was checking — this repository's *blind agreement*, in
a discovery method rather than in a verification.

**The rebrand is still visible, and it is the tell.** zonajobs renamed four of
its five sitemaps and left one behind:

```
Sitemap: https://www.zonajobs.com.ar/sitemap_avisos_zj.xml
Sitemap: https://www.zonajobs.com.ar/sitemap_core_zj.xml
Sitemap: https://www.zonajobs.com.ar/sitemap_empresas_zj.xml
Sitemap: https://www.zonajobs.com.ar/sitemap_listados_ubicacion_zj.xml
Sitemap: https://www.zonajobs.com.ar/sitemap_tags_bum.xml    ← forgotten
```

**So `discover --host` tests the shape, not the marker**: whatever
`sitemap_avisos_<tag>.xml` the file declares, then the count, then the ad URL
grammar. On zonajobs: `zj`, 2 832 `<loc>`, **2 832 of 2 832 matching the
grammar**. It also reports any `_bum` left behind — as a finding about the
rebrand, never as the test.

**Use it before adding a site**, and read the country from `facets` rather than
from the domain.

## A name that looks like the family and is not

**`laborum.pe` is not in this adapter, and the reason is positive evidence
rather than a missing marker** — which is the correction zonajobs forced. Its
own `robots.txt` describes a different stack in its own comments:

```
Sitemap: https://laborum.pe/api/v1/sitemaps/index
# ... see server/v1/sitemap/index.js for the pattern
# For other tenants (e.g. bolsasuniversitarias.com) ...
```

A Node application serving sitemaps from an API path, multi-tenant under an
unrelated brand. **Every other path there answers `403`, and that on its own
would prove nothing** — four identical refusals are agreement produced by
nothing having answered. The `robots.txt` is what settles it. It is named here
so nobody adds it on the strength of its name.

**And the tenants are not identical.** `bumeran.com.mx` and `bumeran.com.ve`
declare **four** sitemaps where the other five declare five: no
`sitemap_tags_bum.xml`. Small, and exactly the assumption to avoid — Indeed is
one template across forty-nine hosts, SuccessFactors serves two URL shapes by
tenant.

## The ad page is a React shell, and this one really is

```
GET /empleos/<slug>-<id>.html   → 200, 64 180 bytes
    <title></title>   no og:title   no ld+json
    <noscript>You need to enable JavaScript to run this app</noscript>
    56 characters of visible text
```

The facet pages return **the same shell, byte for byte**.

**And the check that separates this from a fixable case was run.** Applifly
looked identical from one request and turned out to be missing a query
parameter. Here, `/api/…` under four different shapes answers **`403` with the
same 5 516 bytes every time — including for a path that cannot exist.** *Four
identical sizes are agreement produced by nothing having answered*, so the
`403` says the edge blocks `/api`; it does not say an endpoint is missing.
**`robots.txt` never mentions `/api`: this is a WAF rule and not a refusal.**

## What you get without a browser, and it is not nothing

**1. Every ad's URL and id** — 68 651 across seven countries, from one file per
site.

**2. The slug, which is not the title.** It carries words from the posting and
is worth filtering on; `bumeran.py` emits it as **`slug_words`** and never as
`title`, because nothing here has read a title. *A row with the right words and
a wrong claim is worse than a row with fewer fields.*

**3. The board's own facet vocabulary** — province, city, and a tail mixing
area, subarea, contract and seniority — parsed from the listings sitemap:
**3 953 URLs on Ecuador, 9 767 on Chile, and 100% of them read.** These facets
are **language-independent where a keyword is not**, which is the answer
`shared/search-language.md` asks for when a search in the user's own language
returns nothing (#70).

**The tail is reported as written and never split.** The site does not delimit
area from subarea from contract, and inventing a grammar nobody has documented
is a guess.

## Two patterns that were too tight, and both failed towards "empty"

**The ad slug.** `[a-z0-9-]+` **silently dropped 1 160 of 5 771 URLs — 20% of
one board** — because company names put dots and pipes in the slug:
`vita-alimentos-c.a.`, `aceroscenter-cia.-ltda`,
`recepcionista-|-hombre-mujer`. Every one was a real ad. With `[^/]+` all seven
sites read **every URL their sitemap declares**, and the script now **reports
the skipped count** whenever one does not match.

**The facet URL, three times over.** The place prefix has three forms —
province and city, province alone, neither — and the facet segment is itself
optional. Demanding the city read **1 260 of 3 953 (32%)**; allowing the
missing city left 597; allowing `empleos-` without `area-` left 77, which were
the bare `/en-<province>/<city>/empleos.html`.

**Each round's remainder was a regular form, not noise** — and each round's
message said *"forms this file has not measured"*, which was true and useless.
**A count that improves three times under inspection was never a property of
the site.**

## Configuration

```yaml
boards:
  bumeran:
    enabled: true
    sites: [multitrabajos.com, bumeran.com.pe]
    searches:
      - keyword: "contador"
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `sites` | yes | One or more of the seven. **There is no cross-country search**: each brand is its own index |
| `searches` | no | `keyword` filters on the **slug**, not the description |

No credentials, no login. **A browser is needed to read an ad, never to find
one.**

## Zero-shaped answers

**1. A slug pattern that is too tight** — 20% of a board, silently.

**2. A facet pattern that is too tight** — 68%, with a message that sounded
like diligence.

**3. `/api/…` answering 403 identically for four paths**, one of them
impossible. That agreement is produced by nothing having answered.

**4. A 64 KB ad page with 56 characters of text.** It is `200` and it is not
the ad.

**5. A keyword that matches no slug on a board of thousands.** The slug is not
the title; use `facets` before concluding the market is empty.

## Applying

Through the ad URL, in the user's own browser — which is also where the
description is read. **The plugin does not create accounts and does not fill
credential fields.**

## Pace

The ads sitemap is 0.15 to 7.2 MB per site and one request; the facets file is
0.1 to 2 MB. **A whole country costs two requests**, so the sweep is unusually
cheap in requests and heavy in bytes. No `429` seen.

## Verification

```bash
S=skills/job-scan/scripts/bumeran.py
python3 $S sites --check
python3 $S discover --host zonajobs.com.ar      # member: true, tag `zj`
python3 $S discover --host laborum.pe           # no avisos sitemap declared
python3 $S search --site multitrabajos.com --keyword contador --limit 3
python3 $S facets --site konzerta.com --limit 10
```
