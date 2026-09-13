# Board adapter — The Ugandan Jobline (Uganda): a listing that counts its archive — 84 248 — never compared, the newest pages walked, and the closing date read on every card

<!-- verified: 2026-09-13 -->

<!-- hosts: theugandanjobline.com, www.theugandanjobline.com -->
<!-- script: ugandanjobline.py -->
<!-- countries: UG -->
<!-- content: measured · rules read twice and certain (1 743 B, Cloudflare's managed block naming `ClaudeBot`, `*` open bar nine operator paths; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200: `/jobs-in-uganda` states «84,248 jobs» and pages to `/page/8425` (10 a page), 85 `post-sitemap` files say the same — the archive since the site began, never compared; the newest 3 pages read at 10:59 UTC carry 50 posts, 50 with a closing date, 50 closing on or after 2026-09-13; a `JobPosting` in the post page's JSON-LD `@graph`, the country as the name «Uganda» · 2026-09-13 -->
<!-- witness: the card's own «Closes DD Mon» on every row, read into a date and counted — «50 still close on or after 2026-09-13» over 3 pages; the stated 84 248 is the archive and the adapter says so instead of comparing -->

**Shipped 2026-09-13 — measured in lot 8 of #233 with a number that was
not a board (84 248), and shipped with the number named for what it is.**
Every fetch under the declared identity, the guard on the exact path first,
1 s between pages (no `Crawl-delay`).

```
python3 skills/job-scan/scripts/ugandanjobline.py list [--pages N] [--limit N] [--no-site-total]   # the newest N pages of 10 (default 20), 1 s apart
python3 skills/job-scan/scripts/ugandanjobline.py ad --url https://theugandanjobline.com/<yyyy>/<mm>/<slug>.html
```

## The rules — reopened by the doctrine of 2026-09-07, and 84 248 posts behind them

```
robots.txt      read twice, certain: True, 1743 B, md5 15b15b9c0a1c both times — the managed block (`ClaudeBot` named and refused, `*` open) then
                `User-agent: * / Disallow: /wp-admin/, /wp-login.php, /xmlrpc.php, /api, /oauth-check, /link, /boost/job, /*?s=, /*&s=`
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user
allowed()       True on `/`, `/jobs-in-uganda`, `/jobs-in-uganda/page/2`, `/sitemap_index.xml`, `/<yyyy>/<mm>/<slug>.html`
crawl_delay     none — 1 s between pages is ours
```

*#233 recorded on 2026-09-11 a refusal «written by hand, motive: crawl
cost»; the file read on 2026-09-13 names `ClaudeBot` only through the
managed block and carries no motive. Both are readings, each dated; the
route is the same.*

## The transport — 200

```
GET https://theugandanjobline.com/                       200, 50 158 B    (10:22:29Z, 10:22:30Z — same size)  «Jobs in Uganda - The Ugandan Jobline», WordPress
GET https://theugandanjobline.com/jobs-in-uganda         200, 74 101 B    (10:23:38Z, 10:23:40Z — same size)  «Latest jobs in Uganda — 84,248 jobs», pager to /page/8425
GET https://theugandanjobline.com/jobs-in-uganda/page/2  200, 50 213 B    (10:58:12Z)  10 cards, «Closes 1 Oct» … «24 Sep»
GET https://theugandanjobline.com/sitemap_index.xml      200, 11 896 B    (10:58:08Z; `/wp-sitemap.xml` and `/sitemap.xml` serve the same bytes)  88 children — 85 post-sitemap, category, page, post_tag
GET https://theugandanjobline.com/2026/09/lodge-chef-jobs-ngonzi-crater-escape.html   200, 58 790 B   (10:58:41Z)  JobPosting in a JSON-LD @graph
```

## The number that is not the board, and the one that is

| question | answer |
| :-- | --: |
| jobs stated | **84 248** — «Latest jobs in Uganda 84,248 jobs», `/page/8425` × 10; 85 `post-sitemap` files of a thousand |
| what it counts | **every post since the site began** — an archive, not a live board; the adapter prints it as such and never compares its count to it |
| the card | `<article class="jc">`: title → `/<yyyy>/<mm>/<slug>.html`, employer, «Posted N days ago», **«Closes DD Mon»**, category pills; the key is `yyyy/mm/slug` |
| the live window | «Closes» read into an ISO date (the card names no year: the nearest future reading, a close more than two months past is next year's) and counted: **3 pages, 50 posts, 50 with a date, 50 closing on or after 2026-09-13** at 10:59 UTC |
| page 1 | 30 cards (featured + 20) where the pager's pages carry 10 |

**The adapter walks the newest pages (`--pages`, default 20 = ~200 posts)
and says, each run, how many of the rows read still close in the future.**
*A full walk is not offered: 8 425 pages at 1 s is the archive, not the
board.*

## What a post carries

A `JobPosting` in the page's JSON-LD `@graph` (beside `Article`, `WebPage`,
`Organization`, `Place`): `title`, `description` (HTML), `datePosted` and
`validThrough` (with a time, no zone — «2026-09-11T08:22», «2026-09-22T00:00»),
`employmentType`, `hiringOrganization` (`name`, `sameAs`),
`jobLocation.address` (`addressLocality` Kampala, `addressRegion`,
`addressCountry` **as the name «Uganda»** → `UG`), `industry`, `workHours`
(«8am-5pm»), `monthsOfExperience`, `baseSalary` (`currency: UGX`, **an
empty `value`** → `null`, `unitText: MONTH`), an empty `identifier`. The
page's `mailto:` links are its share buttons; nothing of a recruiter's
contacts is read.

## What this card is, and is not

- **An adapter, shipped** — `list` for the newest pages with the live
  window said, `ad` for one post from its JSON-LD. No key, no browser; N + 0
  requests for the listing.
- **Not a count of the board**: the site states its archive and the adapter
  refuses to pretend that is a size — the live set is what the closing dates
  say, on the pages read.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
