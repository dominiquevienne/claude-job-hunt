# Board adapter — Cyprus Work (Cyprus): one sitemap seven times the board, 1 475 advertisements, and the listing states the same 1 475

<!-- verified: 2026-09-12 -->

<!-- hosts: www.cypruswork.com, cypruswork.com -->
<!-- script: cypruswork.py -->
<!-- countries: CY -->
<!-- content: measured · rules read twice and certain — `ClaudeBot` named and refused, `*` open, so `identity()` answers `claude-user` and since #230 `verdict()` sweeps under it — and the transport answers 200: 1 475 distinct `/job/<id>/` URLs in `/sitemap.xml` (10 708 `<loc>` in all, 8 874 of them `/company/`) against the listing's own `<h1>1475 jobs</h1>`, equal; a `JobPosting` JSON-LD on every advertisement, 10 of 10 sampled · 2026-09-12 11:12 UTC -->
<!-- witness: the listing's `<h1>N jobs</h1>` on `/jobs/`, printed by the adapter beside its distinct count — «1 475 emitted, site states 1 475 — equal» on 2026-09-12 11:12 UTC, «k short» when they part -->

**Shipped 2026-09-12 — the first host of #233 whose transport answers under
the permitted token, and it became an adapter the same morning.** Measured
11:00–11:13 UTC; every fetch under the declared identity, the guard on the
exact path first.

```
python3 skills/job-scan/scripts/cypruswork.py sitemap [--limit N] [--no-site-total]   # 1 request, 2 with the listing's count
python3 skills/job-scan/scripts/cypruswork.py ad --url https://www.cypruswork.com/job/<id>/<slug>/
```

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True, 2531 B, md5 d9cad68a6c11 both times — `User-agent: ClaudeBot / Disallow: /`, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed("/")    True      allowed("/jobs/") True      allowed("/sitemap.xml") True      allowed("/download/x") False
crawl_delay     none — the adapter paces itself at 2 s
```

*Cloudflare's managed content block — nine named crawlers refused,
`ClaudeBot` among them — followed by the operator's own lines: for `*`,
`/files/files/`, `/download/` and `/application-redirect/` closed, the same
three for `bingbot`, a dozen SEO crawlers refused by name, and
`Sitemap: https://www.cypruswork.com/sitemap.xml`.* Before the decision this
host was read as closed by name (#233 lists it under «another managed block
naming ClaudeBot»); the decision reopened it on paper, and the transport
answers. **Its sibling `www.cyprusjobs.com`, under the same managed block,
refused the client two seconds later with the 25-byte static 403** — the
rules file predicts nothing about the transport; only the fetch does.

## The transport — 200, and the site is served

```
GET https://www.cypruswork.com/              200, 177 806 B, md5 62981f5d5fb7    (11:00:31Z)   «Jobs in Cyprus - Cyprus Jobs & Recruitment | Cyprus Work»
GET https://www.cypruswork.com/              200, 177 945 B, md5 57eecffb02c3    (second fetch — dynamic page, sizes differ)
GET https://www.cypruswork.com/jobs/         200, 146 956 B, md5 7437d68828af    (11:01:15Z)   `<h1>1475 jobs</h1>`, 20 `/job/<id>/` links
GET https://www.cypruswork.com/jobs/         200, 146 956 B, md5 efe66be8fc24    (second fetch — same size, a per-response token)
GET https://www.cypruswork.com/sitemap.xml   200, 1 770 253 B, md5 c3198f2f783f  (11:01:18Z)   10 708 <loc>
```

## The sitemap — one file, seven times the board

| question | answer | where |
| :-- | --: | :-- |
| `<loc>` in `/sitemap.xml` | **10 708** | one `urlset`, no index |
| of the shape `/job/<id>/<slug>/` | **1 475** | `AD_RE` |
| distinct ids among them | **1 475** | the `\d+` after `/job/` |
| the rest | 8 874 `/company/`, 256 `/jobs/…` facets, 47 `/categories/`, 19 `/blog/`, 11 `/cities/`, 6 `/states/`, 3 `/countries/`, 1 root | first path segment |
| jobs stated by the board | **1 475** | `/jobs/`, `<h1>1475 jobs</h1>`, and the same figure in `description` / `og:description` |
| `lastmod` on the 1 475 | `2026-09-12` on all — **one value, the day of the read** | measured in the run, not assumed |

**Counting the file would report the board 7× larger** — the widest such gap
after `myjobsfiji` (16.6×). *The adapter matches the advertisement shape and
says how many `<loc>` did not match, so the 9 233 company pages and facets are
counted out loud, never silently.*

**Two counts from two documents, taken three seconds apart, equal to the
unit** — and the adapter carries the check: «1 475 emitted, site states 1 475
on `/jobs/` — equal», or «k short» when they part. *The `<lastmod>` is a
rebuild stamp — one value on every entry, the day of the read
(`deux-lastmod-muets-pour-deux-raisons`) — so there is no `--since` here; the
date is `datePosted` on the advertisement.* **The adapter measures the stamp
each run and says «rebuild stamp» only when it IS one value**; two or more
values are reported as such and still not read as dates.

## What an advertisement carries — 10 of 10 sampled, 11:13 UTC

Every page carries three JSON-LD blocks — **`JobPosting`**, `BreadcrumbList`,
`WebSite`. Ten advertisements drawn at random (seed 20260912) from the 1 475:

| field | 10 of 10 | what it says |
| :-- | --: | :-- |
| `title`, `description` (HTML), `datePosted` (with `+03:00`) | 10 | present and filled |
| `employmentType` | 10 | a list, `["FULL_TIME"]` on all ten |
| `hiringOrganization.name` | 10 | filled; `sameAs` is the employer's site when given |
| `jobLocation.address.addressLocality` / `addressRegion` | 10 | Nicosia 5, Limassol 4, Paphos 1 |
| `addressCountry` | 10 | **the name «Cyprus», not a code** — emitted as `CY` by name; any other name as published |
| `validThrough` | 10 | **`datePosted` + 60 days on all ten** — a policy, not an employer's deadline; emitted as published |
| `baseSalary` | 9 | present with `currency: EUR`, `unitText: YEAR` — **and empty `minValue` / `maxValue` on all 9**; the tenth has no `baseSalary` at all |
| `occupationalCategory` | 10 | a list of 1–3 labels (`Legal`, `Fintech`, `Sales`…); `industry` is the same joined |
| `directApply` | 10 | `true` |

*The one page read at 11:03 outside the sample (`/job/110094/`) carried
`45 000–90 000 EUR / YEAR`, so the field is filled sometimes: the shape is
there, the fill is the employer's.* **The board is bilingual and says nothing
per advertisement**: 3 of the 10 are Greek (title and body in Greek script),
7 English — the adapter emits `language: el` when the title or body carries
Greek script, `en` otherwise; a reading, not a field.

## What this card is, and is not

- **An adapter, shipped** — `sitemap` for the enumeration and the check
  against the stated count, `ad` for one advertisement from its JSON-LD. No
  key, no browser; two requests for the enumeration, one per advertisement.
- **Not a verdict on the sibling** `www.cyprusjobs.com`, which has its own
  card and its own dated read (#233, lot 3).
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`; the page is served to the plugin's client.
