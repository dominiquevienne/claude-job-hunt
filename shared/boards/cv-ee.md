# Board adapter — CV.ee (Estonia, CV-Online): 3 853 visible advertisements = 1 426 own + 2 427 mediated by Töötukassa, read through the search service the page calls

<!-- verified: 2026-09-12 -->

<!-- hosts: www.cv.ee, cv.ee -->
<!-- script: cvonline.py -->
<!-- countries: EE -->
<!-- content: measured · rules read twice and certain — `ClaudeBot` named and refused, `*` open, so `identity()` answers `claude-user` and since #230 `verdict()` sweeps under it — and the transport answers 200: the search service states 1 426 by default and 3 853 with `showHidden=true`, the flag the page's own bundle adds; the 2 427 hidden ones are Töötukassa's mediated advertisements (91 of 91 sampled), none in `jobs-sitemap.xml`, which lists exactly the 1 426 own — «own 1 426, sitemap lists 1 426 — equal», «total 3 853 = own 1 426 + hidden 2 427» on 2026-09-12 12:09 UTC; 1 410 of the 1 426 own are EE, 16 elsewhere (FI 7, DE 6, LV 1, NO 1, by the site's own countries table) · 2026-09-12 12:10 UTC -->
<!-- witness: the job sitemap against the service's default count, and the visible total against own + hidden — both printed by the adapter each run; a vacancy page's Next.js state for `ad` -->

**Shipped 2026-09-12 — measured in lot 5 of #233 with two numbers that did
not agree (3 853 / 1 426), explained before a line of adapter was written,
and shipped the same hour.** Every fetch under the declared identity, the
guard on the exact path first, 2 s between requests (no `Crawl-delay`).

```
python3 skills/job-scan/scripts/cvonline.py search [--host www.cv.ee] [--own] [--limit N] [--no-site-total]   # 1 + 39 requests for the 3 853 visible; --own: 1 + 15 for the 1 426
python3 skills/job-scan/scripts/cvonline.py ad --url https://www.cv.ee/et/vacancy/<id>/<employer>/<slug>
```

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True, 1875 B, md5 d892cbb47388 both times — Cloudflare's managed block (`ClaudeBot` named and refused, `*` open) plus the operator's lines
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed()       True on `/`, `/et/search`, `/et/vacancy/<id>/…`, `/jobs-sitemap.xml`, `/api/v1/vacancy-search-service/search?…`, `/_next/static/…`
crawl_delay     none — the adapter paces itself at 2 s
```

## The transport — 200, and the site is served

```
GET https://www.cv.ee/                                                       200, 1 155 284 B   (11:56:24Z)  → /et — Next.js
GET https://www.cv.ee/et/search                                              200, 1 159 006 B   (11:57:39Z)  state: "total":3853, the locations table (countries with ISO, counties, towns)
GET https://www.cv.ee/jobs-sitemap.xml                                       200, 236 441 B     (11:58:28Z)  1 426 <loc>, 71 distinct real <lastmod>
GET https://www.cv.ee/api/v1/vacancy-search-service/search?limit=1&offset=0                  200   (12:03:48Z, twice)  "total":1426
GET …/search?limit=1&offset=0&showHidden=true                                                200   (12:05:49Z, twice)  "total":3853
GET https://www.cv.ee/_next/static/chunks/pages/_app-*.js                    200                (12:04Z)      the bundle: every search adds `showHidden: true`
GET https://www.cv.ee/et/vacancy/1656067/x/y                                 200, 711 320 B     (12:06:31Z)  a hidden one — served, with its state
```

## The gap, explained — one store, and a flag

| question | answer | where |
| :-- | --: | :-- |
| the service's default count | **1 426** | `search?limit=1` — twice, equal |
| with `showHidden=true` | **3 853** | the flag the page's `_app-*.js` adds to every search; «Kuva 3853 tööpakkumist» is this figure |
| `/et/vacancy/` URLs in `jobs-sitemap.xml` | **1 426** — the own ones, exactly | none of the hidden ids is in it (0 of 91 sampled) |
| the hidden ones are | **«Töötukassa vahendatud pakkumised»** on 91 of 91 sampled — advertisements mediated by Töötukassa, Estonia's public employment service, syndicated into the board | every one with an external id, none with a promotion; the employer's name sits inside the text («Tööandja nimi: …») |
| own rows, by the site's own countries table | EE 1 410 · FI 7 · DE 6 · LV 1 · NO 1 | `countryId` → `locations.countries[].iso` |
| salary on own rows | a figure on 763 of 1 426, a range (both ends) on 428, hourly on 185 | `salaryFrom` / `salaryTo` / `hourlySalary`; EUR |
| remote | 192 of 1 426 | `remoteWork`, `remoteWorkType` |

**The adapter emits what the visitor sees — the 3 853, with `mediated_by:
"Töötukassa"` on the syndicated rows — and `--own` restricts to the 1 426.**
*Both checks are printed each run: «own N, sitemap lists M — equal / k
short» and «total T = own N + hidden H — this run emitted E of T».* Nothing
is dropped: a Töötukassa row is a real vacancy at a real employer named in
its text.

## What `ad` reads — the page's state, and never its contacts

A vacancy page inlines its object: `position`, `employerName`, `employer`
(`about`, `webpageUrl`), `settings` (`dateStart`, `dateTo`, `categories`,
`applyingUrl`), `highlights` (`location`, `salaryFrom/To`, `ratePer`,
`remoteWorkType`), `languageIso`, `status` — **and `details`, whose body is
in one of four places, said in `details_kind`**: `text` (`standardDetails`,
title/content pairs), `file` (an image or PDF behind
`/api/v1/files-service/<id>` — `details_url`), `url` (the employer's page),
`styled`. *On the two pages read: the Töötukassa one is text, the library's
is a file.* **The state also carries `contacts` — a recruiter's e-mail and
phone. It is not emitted, and the test asserts it.**

## The other two hosts of the stack — measured, and refused today

`www.cv.lv` (LV) and `www.cvonline.lt` (LT) publish the same rules shape
(1 875 / 1 881 B, `ClaudeBot` named, `*` open — `cvonline.lt` adds
`Content-Signal: ai-train=no, use=reference`; the use here is reference)
**and both answer the 25-byte static 403 (`9ccabba20b9f`) on the root and on
the search service, twice each, 2026-09-12 12:06:59–12:07:05 UTC** — family
(1) of #222, a browser legitimate and not measured. The adapter accepts
`--host www.cv.lv` / `www.cvonline.lt`, names the refusal on a 403 (exit 6),
and `countries:` declares EE alone until a transport answers. Their cards:
`cv-lv.md`, `cvonline-lt.md`.

## What this card is, and is not

- **An adapter, shipped** — `search` for the visible set with the two
  checks, `ad` for one advertisement from the page's state. No key, no
  browser; 40 requests at 2 s for the visible set, 16 for the own set.
- **Not a verdict on `cv.lv` or `cvonline.lt`** — their own dated reads, on
  their own cards.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
