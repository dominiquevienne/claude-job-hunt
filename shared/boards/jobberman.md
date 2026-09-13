# Board adapter — Jobberman and BrighterMonday (ROAM Africa: `www.jobberman.com` Nigeria, `www.brightermonday.co.ke` Kenya, `www.brightermonday.co.ug` Uganda): one template, a sitemap of category files, a listing that states its count, and a pager the rules stop at page 10

<!-- verified: 2026-09-13 -->

<!-- hosts: www.jobberman.com, jobberman.com, www.brightermonday.co.ke, brightermonday.co.ke, www.brightermonday.co.ug, brightermonday.co.ug -->
<!-- script: jobberman.py -->
<!-- host-forms: www.jobberman.com, www.brightermonday.co.ke, www.brightermonday.co.ug -->
<!-- host-forms-basis: read — `jobberman.py:HOSTS`, three literals; every address the three sites write carries `www.` (the sitemaps' `<loc>`, the cards' links, the canonical) · 2026-09-13 -->
<!-- countries: NG KE UG -->
<!-- content: measured · **Nigeria: 4 150 distinct advertisement ids over 27 category sitemap files and «4,194 Jobs Found» stated by the listing — 44 apart; Uganda: 757 in the files and «1,025 Jobs Found» — 268 apart; Kenya: «1,895 Jobs Found» (the files not walked, the index of 27 read)**; `jobberman.py sitemap` 17:55–17:56 UTC, `recent --pages 2` 32 emitted of 4 194 with the walk ending at page 10 by the rules; the rules identical on the three hosts but four lines (`*` refuses `/job/`, `/api/` and every facet query, and allows `page=2…10` by name); the cards carry a currency and a range with no period; the advertisement page carries no JobPosting · 2026-09-13 -->
<!-- witness: the listing's own «N Jobs Found», read on every page of `recent` and once by `sitemap` and printed beside the distinct count («4 150 in the sitemap, the listing states 4 194 «Jobs Found» — 44 more in the listing»); the walk of the listing never claims the whole — the rules end it at page 10 and the note says so · 2026-09-13 -->

**The dominant board of Africa's largest market, and its two East
African siblings — one file, `--host`, `countries:` per host.** Issue
#390 (Nigeria); Kenya and Uganda ride the same file because their rules,
sitemaps, listing and cards are the same template to the byte-shape.
Measured 2026-09-13 17:50–17:56 UTC by the declared client, the guard
on the exact path first (`*`, certain, on every path read).

## Rules — three files, four lines apart, the same answer

```
robots.txt (NG 5c1741d9… · KE b5889e79… · UG cc3cf3ad…)   `User-agent: *` — Disallow /admin/ /account/ /cdn-cgi/ /api/ /job/ /blog /forms /ajax/ /report-job/ · /*q=* /*industry=* /*sort=* /*salary_ids=* /*company_name=* /*experience=* /*keywords=* /*job_type=* /*page=* /discover/page
                                                            Allow: *page=2$ … *page=10$ (and the & forms) — the pager is open to page 10 BY NAME and refused after
                                                            KE/UG add: Allow: * · Disallow /customer/ /checkout/ /salary-report
                                                            Sitemap: sitemap-category-en.xml · sitemap-directory-en.xml · sitemap-listings-index-en.xml · discover/sitemap_index.xml   (each on its own host)
allowed()   /sitemap-listings-index-en.xml True · /listings/<slug>-<id> True · /jobs True · /jobs?page=2 True (rule *page=2$) · /jobs?page=11 FALSE (rule /*page=*) · /job/x FALSE
```

**`/job/` is refused and `/listings/` is the advertisement path** — the
two are not the same prefix. **The listing walk ends at page 10 because
the rules say so**: `recent` never asks for page 11, and its note says
«the rules allow page=2…10 by name and refuse the rest» rather than
«short». The sitemap is the whole.

## The sitemap — 27 category files, an id that is a slug's tail

```
GET /sitemap-listings-index-en.xml     200 — 27 <sitemap>, one per category, lastmod on the hour (2026-09-13T16:00 / 17:00)
GET /sitemap-listings-accounting-auditing-finance-en.xml   200 — 374 <url>: /listings/<slug>-<id>, <lastmod> each
jobberman.py sitemap --limit 1                         **4 150 distinct advertisement id(s)** over 27 category file(s) (4 150 entries, 0 filed under a second category)
                                                        4 150 in the sitemap, the listing states 4 194 «Jobs Found» — 44 more in the listing; the files are rebuilt hourly (their lastmod), the listing is live.
jobberman.py sitemap --host www.brightermonday.co.ug --limit 1    757 distinct over 27 files; the listing states 1 025 — 268 more in the listing
```

The id is the six characters after the last hyphen (`-x8gn9q`); an
advertisement filed under two categories would appear in two files and
is keyed once — none was, on the day, on either host walked. **The gap
between the files and the listing is the listing's** (44 on Nigeria,
268 on Uganda — a quarter): the files are rebuilt on the hour and the
listing counts live, or the listing counts what the files do not carry;
which is not read here, and neither figure is corrected.

## The listing and the card

```
GET /jobs            200, 713 670 B — «Jobs in Nigeria 4,194 Jobs Found», 16 cards, pager to 263 (KE: 1,895 → 119; UG: 1,025 → 65)
card                 aria-labelledby="job-1260774-title" · <a data-cy="listing-title-link" href=…/listings/sales-executive-8m99ej> · <p>employer</p> · <span>location</span><span>type</span><span>NGN <span>70,000 - 150,000</span></span> · <p>function</p> · <p>2 days ago</p> · an excerpt
```

The card is read **by its structure**, not by the order of its text
lines: the title link, then the employer `<p>`, then the span row, then
the function `<p>` — a first draft read the lines in order and put «>»
(a tag's remnant) in the title, the title in the employer, and so on
down the row, with nothing wrong-looking about any single value.
**Salary is a currency and a range with no period** (`NGN 70,000 -
150,000`): `salary_unit: null, salary_unit_stated: false`. 7 of 16 cards
carried one on the first page.

## The advertisement page — no JobPosting, fields on the page

```
GET /listings/account-admin-officer-x8gn9q     200, 551 876 B — JSON-LD WebPage / Organization / Person (the site's, not the job's); no JobPosting
breadcrumbs (anchors on /jobs…)                function · ?industry= · location · type       <- the home link is a glyph, filtered by its href
<h1 data-cy="title-job">, <h2> employer, «1 month ago», «NGN 400,000 - 600,000»
Job summary · Min Qualification · Experience Level · Experience Length · Language Requirement · Working Hours · Applicant Location · Job descriptions & requirements · Log In and Apply · Important safety tips
```

`ad` reads the breadcrumb anchors (function, industry, location, type),
the title and employer, the salary line, the labelled facts, the summary
and the description up to «Log In and Apply»; the safety tips are not
part of the advertisement. **No contact is on the page** — applications
are behind a login — and none is read.

## Configuration

```yaml
boards:
  jobberman:
    enabled: true
    host: www.jobberman.com        # or www.brightermonday.co.ke · www.brightermonday.co.ug
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `host` | no | one of the three; `www.jobberman.com` by default |

No credentials, no browser. `sitemap` is 29 requests at 2 s (index, 27
files, the listing); `recent` is up to 10; `ad` is one.

## What is not established

- **Why the listing states more than the files carry** — 44 on Nigeria,
  268 on Uganda; featured or promoted cards, or an hourly lag, not read.
- **Kenya's file count** — the index of 27 was read, the files were
  not walked (the same template; `--host www.brightermonday.co.ke`
  walks them).
- **The salary's period** — none on the card or the page; monthly is
  the country's convention and is not stated.
- **ROAM's other hosts** (Ghana `jobberman.com.gh`, Tanzania
  `brightermonday.co.tz`) — not read; the same template is likely and
  a fourth `HOSTS` entry is the form.

## 2026-09-13 — shipped

`sitemap --limit 1`: NG 4 150 / 4 194; UG 757 / 1 025. `recent --pages
2`: 32 of 4 194, the walk ending by the rules. `ad` on one. Five tests;
six mutations on a detached worktree (`python3 -B`), six red — the
dedup across files dropped, `PAGES_ALLOWED` raised to 11, the count regex
broken, the `--host` table reduced, the breadcrumb filter dropped, the
salary regex allowing a bare comma.
