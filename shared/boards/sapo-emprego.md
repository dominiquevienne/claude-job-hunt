# Board adapter — SAPO Emprego (`emprego.sapo.pt`, Portugal): a refused, captcha-gated search never taken, an offer sitemap of 22 838 uuids, and a count the open listing states — 23 555

<!-- verified: 2026-09-13 -->

<!-- hosts: emprego.sapo.pt -->
<!-- script: sapoemprego.py -->
<!-- host-forms: emprego.sapo.pt -->
<!-- host-forms-basis: read — `sapoemprego.py:BASE`, a single literal; every address in the sitemap is on it · 2026-09-13 -->
<!-- countries: PT -->
<!-- content: measured · **22 838 distinct offer ids** (uuid) in `offers.xml` — 22 890 `<loc>`, 52 repeated, 19 518 distinct slugs (1 743 slugs carried by more than one id: the slug is not the key), `<lastmod>` on all, 15 381 in September 2026 and 7 489 in August — **against `offers_total: 23555` in the `:pagination` prop the open `/offers` page embeds — 717 short**, both printed; `sapoemprego.py sitemap` at 10:30 UTC · 2026-09-13 -->
<!-- witness: the site's own `offers_total` on the open listing page, read in the same run and printed beside the file's count («22 838 emitted, site states 23 555 — 717 short»); the page's `total: 9999` is a page-count cap and is not read as a count · 2026-09-13 -->

**Portugal's general board on the SAPO portal — 23 555 offers by its own
count, from Prosegur to a school in Alvito — and the fifth Portuguese host
with a script here.** Measured 2026-09-13 10:18–10:33 UTC, every fetch
under the declared identity, the guard on the exact path first, **5 s
apart after the host answered 429 to the third request in ten seconds**.

## Rules — the search is refused in writing, and the app guards it with a captcha

```
robots.txt      200, 791 B — `*`: Allow / · /offers · /offers/ · /courses · /career/ · /news/ · /offers/company/
                Disallow /offers/search · /courses/search · /offers/*/report · /offers/*/contact · /offers/*/email · /apply-job/ · /user/ · /logged/ · /frontoffice/ …
                and six lines refusing `*net-empreg*` in every spelling (a competitor's name in a query); Sitemap: /sitemap.xml; no Crawl-delay
identity("/")   http, claude-user — nothing binds either token
```

**`/offers/search` is the route the listing's own app posts to, and it is
refused** — by the rules, which is enough, and by an hCaptcha on the search
form (`offers.search.validation` posts a `g-recaptcha-response`), which is
borne 2 besides. *Neither is touched, by any route.* The two things the
rules leave open are what the adapter reads: the sitemap, and `/offers`
itself.

## The transport — a 429 at the third request

```
10:18:15 UTC   GET /robots.txt   →  429 Too Many Requests, 162 B, nginx     (the third request in ten seconds, after two guard reads)
10:27:20 UTC   GET /robots.txt   →  200, 791 B                              (nine minutes later, one request)
then           /offers · /sitemap.xml · /offers.xml · one offer page — 200 each, 3–5 s apart
```

**A 429 is a refusal that asks for less**, and the 09.09 table keeps it a
refusal: the adapter spaces 5 s and **stops on a 429 without retrying**
(exit 7). *What triggered it was our own pace; the next reader keeps the
spacing rather than measuring the limit.*

## The sitemap — uuids, not slugs

```
/sitemap.xml      index of 9: static, companies, company-offers, company-courses, **offers**, courses, career-categories, career-articles, news-articles
/offers.xml       5 243 186 B — 22 890 <loc> /offers/<canonical>?id=<uuid>, <lastmod> on all, changefreq always
                  22 838 distinct uuids (52 entries repeated) · 19 518 distinct slugs · 1 743 slugs under more than one uuid
                  by month: 2026-09 15 381 · 2026-08 7 489 · 2026-05 9 · 2026-07 6 · 2025-10 2
```

**The `?id=<uuid>` is the key; the canonical slug is not** — the same
job posted twice (an agency's «Comercial (m/f) – Grande Lisboa» in
several districts) carries one slug and two uuids, 1 743 times. *An
adapter keyed on the path would fold them; this one is keyed on the
uuid and reports the slug count beside it.* `<lastmod>` is the offer's
own date on the one checked (2025-10-28 in the file, `datePosted
2025-10-28` on the page).

## The count — `offers_total`, embedded on the open listing

```
GET /offers      200, 264 467 B — a Vue app served with its first rows and its pagination as component props:
                 <search-results-component :offers='[{…9 rows…}]' :pagination='{"total":9999,"page":1,"size":9,"offers_total":23555}' …>
22 838 emitted, site states 23 555 (`offers_total` on https://emprego.sapo.pt/offers) — 717 short; the listing's search is refused by the rules and captcha-gated, so the file is what a reader can reach.
```

**`offers_total` is the site's count; `total` is 9 999 and is a
page-count cap** — a round number beside the right word, which is the
count of nothing. The 717 the file lacks are behind the refused search;
the adapter says so and reaches what it can. *The nine embedded rows carry
`id`, `offer_name`, `company_name`, `publication_date`, `job_district`,
`job_work_hours`, `canonical` — the same fields the page shows — but a
walk of `/offers?page=N` at nine a page (2 617 pages) is not built; the
file is.*

## The advertisement — a JobPosting

```
GET /offers/mentora-musica-…?id=b58b3ec5-…    200, 265 136 B — one JobPosting in JSON-LD
title · description (HTML) · datePosted 2025-10-28 · validThrough 2026-10-28 · industry «Formação, Ensino e Educação»
employmentType PART_TIME · jobLocation {Beja, Beja, PT} · hiringOrganization {name, logo} · url
no salary field on the page read — nothing invented
```

## Configuration

```yaml
boards:
  sapo-emprego:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials, no browser. `sitemap` is three requests 5 s apart (index,
offer file — 5 MB —, listing page); `--no-site-total` makes it two; `ad`
is one.

## What is not established

- **Which 717 the file lacks** — behind the refused search.
- **The rate limit itself** — one 429 at three requests in ten seconds;
  5 s spacing has not been refused; the threshold was not measured.
- **Whether every page carries a JobPosting** — one read.
- **The other editions** (`/internacional/`, `/universitarios/`,
  `/executivo/` routes in the app) — not read.

## 2026-09-13 — shipped

`sapoemprego.py sitemap`: 22 838 distinct, site states 23 555 — 717 short,
both printed. `ad` on one. Three tests; five mutations on a detached
worktree (`python3 -B`), five red, each on the test written for it.
