# Board adapter — type (`type.jp`, Japan): one job sitemap, category counts on the home page, a full JobPosting per advertisement

<!-- verified: 2026-09-12 -->

<!-- hosts: type.jp -->
<!-- script: typejp.py -->
<!-- host-forms: type.jp -->
<!-- host-forms-basis: read — `typejp.py:BASE`, a single literal; addresses come from the sitemap as served · 2026-09-12 -->
<!-- countries: JP -->
<!-- content: measured · 2 335 distinct advertisement ids in `sitemaps-job-detail.xml` (2 335 `<loc>`, every `<lastmod>` the one stamp `2026-09-12`), against **2 715 summed over the 11 category counts the home page states** («IT・Webエンジニア（1005件）» …) — an upper bound, since an advertisement may sit in several categories; `typejp.py sitemap` at 09:25 UTC · 2026-09-12 -->
<!-- witness: second source on a related quantity — the home page's per-category counts, 2 715 summed over 11 categories, printed beside the sitemap's 2 335 and named as a sum with overlap (an upper bound), never as «the board states» · 2026-09-12 -->

**A mid-sized Japanese board with a clean structure — the second Japanese
host with a script here, after Mynavi.** Japanese interface, UTF-8, nothing
translated. Measured 2026-09-11 18:37 UTC (rules, root) and 2026-09-12
00:38–09:25 UTC (sitemap, advertisement, adapter), every fetch under the
declared identity, the guard on the exact path first.

## Rules, transport, sitemap

```
robots.txt               read twice, certain: True — 10 Disallow to `*` (/skillsheet/, /experience…), none the sitemap or /job-N/; no Crawl-delay; Sitemap: https://type.jp/sitemap.xml
identity("/")            http, claude-user
GET /                    200, 71 745 B, <title>転職ならtype…</title> (md5 moving — session tokens, not a challenge)
GET /sitemap.xml         200, index of 21 children — sitemaps-job-detail.xml, -company-detail, -job-interview, -industry…
GET /sitemaps-job-detail.xml   200, 374 109 B, 2 335 <loc>, all /job-<n>/<id>_detail/, 2 335 <lastmod> = one value
```

**The `<lastmod>` is a regeneration stamp** (one value on all 2 335) — the
adapter says so and offers no `--since`; `datePosted` and `validThrough` are
on each page.

## The count, and the home page's categories

```
2335 <loc>; 2335 matched; 2335 distinct advertisement id(s)
site states 2 715 across 11 categories on its home page (IT・Webエンジニア 1005, プロジェクトマネージャー・ITコンサル 195, 営業系 482, 販売員・サービススタッフ系 300 …)
   — a sum of categories an advertisement may belong to several of: an upper bound, not the size
```

*2 715 ≥ 2 335, and the gap is what overlap looks like.* **Neither figure
is called the board's size**; the sitemap's distinct ids are the count, the
site's sum is the second source, named for what it is.

## The advertisement — a JobPosting in JSON-LD

```
GET /job-1/765997_detail/    200, 103 055 B, exactly one JobPosting
title · hiringOrganization · identifier (the employer's id: 5119) · datePosted 2026-08-28 · validThrough 2026-09-24
employmentType FULL_TIME · industry · occupationalCategory · jobLocation[] (prefecture + city, deduplicated)
baseSalary JPY 4 500 000 – 8 000 000 / YEAR · skills · workHours · jobBenefits · description (HTML in the JSON)
```

Emitted as published, tags stripped, `<br>` to newlines, `language: ja`.
**Read in full on one advertisement.**

## Configuration

```yaml
boards:
  type-jp:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials, no browser. `sitemap` is three requests (index, job file,
home page).

## What is not established

- **Which of the 2 335 are open** — `validThrough` per page, one request each.
- **The `/job-<n>/` prefix's meaning** (`job-1` on every entry read) — carried
  as `kind`, not interpreted.
- **Search and filters** — `/job/` category paths exist in the index's other
  children; none exercised.

## 2026-09-12 — shipped

`typejp.py sitemap`: 2 335 distinct; site states 2 715 across 11 categories.
`ad` on 765997: the fields above.
