# Board adapter — TopDev (Vietnam): 4 942 IT jobs stated, read through 249 paged job sitemaps in two languages, and an `identifier` that names the employer rather than the advertisement

<!-- verified: 2026-09-13 -->

<!-- hosts: topdev.vn, www.topdev.vn -->
<!-- script: topdev.py -->
<!-- countries: VN -->
<!-- content: measured · rules read twice and certain (2 190 B, Cloudflare's managed block naming `ClaudeBot`, `*` open bar eight operator paths; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200: `/viec-lam/tim-kiem` states «Tuyển dụng 4942 việc làm lương cao [Update 13/9/2026]», `/sitemap-jobs.xml` is an index of 249 `en` and 249 `vi` pages of 20 `<loc>` (page 1 en = vi by id, page 249 has 20), every `<lastmod>` the day of the read; a `JobPosting` JSON-LD on the advertisement page with salary in VND, the country as `VN`, and `identifier.value` = the employer's id — the full `en` walk of 2026-09-13 10:36:08–10:44:31 UTC: 4 980 `<loc>` over the 249 pages, **4 525 distinct ids** (455 repeats across pages), «4 525 emitted, site states 4 942 — 417 short» · 2026-09-13 -->
<!-- witness: the search page's own «Tuyển dụng N việc làm», dated by the site («[Update 13/9/2026]»), printed by the adapter beside its distinct count after a full walk — «4 525 emitted, site states 4 942 — 417 short» on 2026-09-13 10:44 UTC: two numbers, and the 417 is the result, not a defect; a bounded walk is a lower bound and is not compared -->

**Shipped 2026-09-13 — measured in lot 8 of #233 and shipped the same
hour.** Every fetch under the declared identity, the guard on the exact
path first, 2 s between requests (no `Crawl-delay`).

```
python3 skills/job-scan/scripts/topdev.py sitemap [--lang en|vi] [--pages N] [--limit N] [--no-site-total]   # 1 + 249 + 1 requests, ~9 min
python3 skills/job-scan/scripts/topdev.py ad --url https://topdev.vn/detail-jobs/<slug>-<id>      # or /viec-lam/<slug>-<id>
```

## The rules — reopened by the doctrine of 2026-09-07, and 4 942 jobs behind them

```
robots.txt      read twice, certain: True, 2190 B, md5 3bf3b2ef1857 both times — the managed block (`ClaudeBot` named and refused, `*` open) then
                `User-Agent: * / Allow: / / Disallow: /job-seeker/login, /employers/search, /partners/, /job/getApply, /affiliate/, /challenge/, /topdemy/, /socket.io`
                `Sitemap: https://topdev.vn/sitemap.xml`
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed()       True on `/`, `/viec-lam/tim-kiem`, `/sitemap.xml`, `/sitemap-jobs.xml`, `/sitemap/jobs_desc_en_page_1.xml`, `/detail-jobs/<slug>-<id>`, `/viec-lam/<slug>-<id>`
crawl_delay     none — the adapter paces itself at 2 s
```

## The transport — 200, and the site is served

```
GET https://topdev.vn/                                 200, 1 873 351 B   (10:22:34Z, 10:22:36Z — same size)  «TopDev - Việc Làm Lương Cao Hàng Đầu»
GET https://topdev.vn/viec-lam/tim-kiem                200, 1 449 130 B   (10:23:45Z, 10:23:48Z — same size)  «Tuyển dụng 4942 việc làm lương cao [Update 13/9/2026]», 29 advertisement links, no pager link in the HTML
GET https://topdev.vn/sitemap.xml                      200, 1 098 B       (10:33:23Z)  7 children — homepage, blog, jobs, companies, skills, fresher, interview
GET https://topdev.vn/sitemap-jobs.xml                 200, 78 254 B      (10:33:53Z)  an index: 249 `jobs_desc_en_page_<n>.xml` + 249 `jobs_desc_vi_page_<n>.xml` + the skills file
GET https://topdev.vn/sitemap/jobs_desc_en_page_1.xml  200, 7 382 B       (10:33:53Z)  20 <loc>, `/detail-jobs/<slug>-<id>`, every <lastmod> 2026-09-13
GET https://topdev.vn/sitemap/jobs_desc_vi_page_1.xml  200, 7 322 B       (10:34:32Z)  20 <loc>, `/viec-lam/<slug>-<id>` — the same 20 ids
GET https://topdev.vn/sitemap/jobs_desc_en_page_249.xml 200, 7 443 B      (10:34:32Z)  20 <loc> — the last page is full
GET https://topdev.vn/detail-jobs/…-mbbank-2125929     200, 796 127 B     (10:34:31Z)  JobPosting JSON-LD
```

## The sitemap — 249 pages a language, one store

| question | answer |
| :-- | --: |
| jobs stated | **4 942** — «Tuyển dụng 4942 việc làm lương cao», with the site's own «[Update 13/9/2026]» |
| sitemap pages | **249** `en` + **249** `vi`, 20 `<loc>` each (pages 1 and 249 read) — 249 × 20 = 4 980, an upper bound before dedup |
| the two languages | the same ids — page 1 `en` = page 1 `vi` by the URL's tail; `en` links `/detail-jobs/`, `vi` `/viec-lam/`; one language is read |
| `<lastmod>` | the day of the read on every entry — a rebuild stamp, not a date; no `--since` |
| the full walk (`en`, 10:36:08–10:44:31 UTC, 8 min 23 s) | **4 980 `<loc>`, 4 525 distinct ids — 455 repeats across pages**; «4 525 emitted, site states 4 942 — 417 short» |

**The adapter walks one language, dedups on the URL's tail and prints the
distinct count beside the stated one; `--pages` bounds the walk, says «the
walk stopped at page p», and does not compare.**

*Two numbers, and the sentence that relates them is where an error would
live: 4 980 slots minus 455 repeats is 4 525 distinct in a sitemap that is
regenerated as the walk runs (every `<lastmod>` is today — page 1 was read
at 10:36 and page 249 at 10:44, and an advertisement that moves between
pages in the «desc» order is counted twice or not at all); the search page
counts 4 942 in its own index. Neither is copied as the board's size: the
adapter prints both, and «417 short» is the finding of 2026-09-13, not a
defect of the walk.* **A repeat across pages is the sitemap's, not ours —
the dedup is what makes 4 525 a count.**

## What an advertisement carries — and whose id the `identifier` is

`JobPosting` JSON-LD with `title`, `description` (HTML), `datePosted`,
`validThrough`, `employmentType` (`["OTHER"]` on the page read), `industry`
(«Information Technology»), `skills` (a comma-joined string, split),
`jobBenefits` (HTML), `hiringOrganization` (`name`, `sameAs` = the company
page), `jobLocation.address` (`addressLocality`, `addressRegion`,
`addressCountry: VN`), `baseSalary` (`currency: VND`, `minValue` 9 000 000,
`maxValue` 55 000 000, `unitText: MONTH`, and a `value` sentence «9.000.000
VND to 55.000.000 VND» — emitted as published beside the parsed ends).

**`identifier.value` is the EMPLOYER's id** — `94346` for MBBANK, the number
in its company URL — **not the advertisement's**, which is the URL's tail
(`2125929`). *The adapter keeps the two apart (`employer_id`, `id`); the
test asserts it, and the mutation that confuses them reddens.* The page is
served under both language paths; `page_language` says which was read, the
text is the employer's in either.

## What this card is, and is not

- **An adapter, shipped** — `sitemap` for the enumeration with the stated
  count as the check, `ad` for one advertisement from its JSON-LD. No key,
  no browser; 251 requests at 2 s for the whole board.
- **Not a verdict on the other Vietnamese hosts of #233** — `mywork.com.vn`
  (static 403) and `careerlink.vn` (a Turnstile on the listing) have their
  own cards.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
