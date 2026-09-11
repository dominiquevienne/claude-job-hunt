# Board adapter — Expresso Emprego (`expressoemprego.pt`): the live listing states 1 917, the declared sitemap died in 2019

<!-- verified: 2026-09-11 -->

<!-- hosts: expressoemprego.pt, www.expressoemprego.pt -->
<!-- script: expressoemprego.py -->
<!-- host-forms: expressoemprego.pt -->
<!-- host-forms-basis: read — `expressoemprego.py:HOST`, a single literal; `www` redirects its rules file to the apex and is never built · 2026-09-11 -->
<!-- countries: PT -->
<!-- content: measured · 1 917 advertisements the site states in its own listing («1 917 empregos para a sua pesquisa», `expressoemprego.py search`, 18:40 UTC), 15 a page; 45 distinct ids over the first 3 pages, and the total follows every filter — `--localizacao lisboa` 469, `--q jurista` 2 · 2026-09-11 -->
<!-- witness: the declared sitemap is NOT one — 5 873 `<url>`, 1 513 of them advertisements, every one with a `lastmod` of October–November 2019 (ids 1 606 727–1 998 140 against 2 466 6xx live): a fossil, never read by the adapter. No second source states 1 917 · 2026-09-11 -->

**The board says how many it holds, on every listing page, and the number
follows the filter.** *What it also declares — a sitemap — is seven years
dead, and a reader that trusted the declaration would count 1 513
advertisements from 2019.*

## Step 1 — the rules twice on both hosts, and 1 513 sitemap URLs that all date from 2019 (2026-09-11 18:38–18:39 UTC)

```
https://expressoemprego.pt/robots.txt        200   118 o   md5 d6d89b11dac16fe0e3898f1a2fced780   ×2
https://www.expressoemprego.pt/robots.txt    -> the apex, same file                                ×2

User-agent: AhrefsBot     Disallow: /
User-agent: *             Disallow:            (empty — nothing refused)
Sitemap: https://expressoemprego.pt/sitemap.xml
```

**No AI agent named, no `Crawl-delay`; `verdict: sweep True, certain
True`**; the guard on `/`, `/sitemap.xml`, `/ofertas-emprego`,
`/emprego/pesquisa/…` and `/emprego/<slug>/<id>`: all `allowed True, certain
True`.

**The declared sitemap:** 1 133 696 bytes, md5 `1ee5b02f…` stable ×2, a
`<urlset>` of 5 873 `<url>` — 3 874 `/noticias`, **1 513 `/emprego/<slug>/<id>`**,
429 `/carreiras`, 41 `/formacao`, 15 `/artigos`. **Every one of the 1 513
carries `<lastmod>` in 2019** — 1 411 in November, 102 in October — with ids
from 1 606 727 to 1 998 140, while the live listing shows 2 466 610 and up.
*A sitemap that has not been regenerated in seven years is a declaration,
not an inventory* (`shared/robots-policy.md`) — **and this one is the trap
where the count of `<loc>` is not a count of advertisements, in its purest
form: they were advertisements, once.** The adapter never reads it.

## The live route — the listing, 15 a page, the site's total on the page

```
/ofertas-emprego            200   143 723 o   15 rows   «1 917 empregos para a sua pesquisa»
/ofertas-emprego?page=2     200                15 rows, ids 2466778…       (`?page=1` serves the FIRST page again — 1-based, 0 and 1 alias)
/emprego/pesquisa/jurista/  200    90 356 o    2 rows   «2 empregos para a sua pesquisa»
/emprego/pesquisa/query/lisboa/                          «469 empregos»
/emprego/pesquisa/zzqxjkwvv/  200  80 552 o    0 rows   «Não foram encontradas Ofertas de Emprego para a sua pesquisa»
/emprego                    200    43 566 o    0 rows, no total — an «Oops, a página que procura não se encontra disponível» page
```

**Each row** (`div.resultadosBox`): `h3 > a` — the title and the URL
`/emprego/<slug>/<id>`; `h4` — the employer; a span with the date
(`11.09.2026`) and, when the ad states one, `Localidade, Portugal` (4 of 15
rows on page 1 carried none); `Referência: <id>` — **the id is the URL's last
segment, the stable key.**

**The search is the site's own routing, read off its `main.js`**
(`getURLCriteriosPesquisa`): `/emprego/pesquisa/<query>/<localizacao>/
<reference>/<data>/<tipo>/…`, each empty criterion replaced by its NAME and the
trailing names trimmed. The adapter builds the first two segments —
`--q juristas` → `/emprego/pesquisa/juristas/`; `--localizacao lisboa` alone
→ `/emprego/pesquisa/query/lisboa/` — and nothing else; the advanced
criteria exist and are not exposed here.

**Filters shown to reduce (#219), 18:43 UTC:**

```
listing                 1 917
--localizacao lisboa      469
--q jurista                 2
--q zzqxjkwvv               0   the site's sentence
```

## Zero-shaped answers, and the anchor

| what comes back | what the adapter does |
| :-- | :-- |
| rows, and the total | `N emitted, M distinct over P page(s) of 15; the site states T empregos for this search` — **two counters from two branches** |
| «Não foram encontradas Ofertas de Emprego para a sua pesquisa», 0 rows | **a real zero, in the site's words** — exit 0, nothing on stdout, the sentence on stderr |
| 0 rows, no total, no sentence — the «Oops» page | **dies 6** through `empty_first_page`, the size beside the zero, naming the «Oops» shape |
| 0 rows and a positive total | **dies 6** — the two disagree |
| a later page with no row | the end of the listing, said with the page count |

## The ad page — no `JobPosting`, the text in `div.wucAnuncioDet`

`/emprego/juristas/2466610`: 200, 97 374 bytes, **0 `ld+json` of any type**.
The text is HTML between the `wucAnuncioDet` container and the «EMPREGOS
SEMELHANTES» block — «Descrição da Empresa», the body, the deadline in
prose («até às 23h59m do dia 20 de setembro de 2026»). `ad --id` builds
`/emprego/oferta/<id>` — the site routes on the id, the slug is cosmetic —
and dies 6 when the container is missing (the «Oops» page has none).

## Pace

One request per page, one per ad, spaced 2 s by `_pace.Pace` (no
`Crawl-delay` declared). The measurement above was 14 requests between 18:38
and 18:44 UTC, all 200.

## What is not established

**Whether the listing's `DD.MM.YYYY` is the posting or a re-listing** — every
row on page 1 carried the day of the read. **Whether 1 917 counts only live
advertisements** — the site's word, not a reader's. **The advanced criteria**
(`tipo`, `exp`, `habilitacao`, `funcao`, `setor`) — named in the JS, not
exercised.
