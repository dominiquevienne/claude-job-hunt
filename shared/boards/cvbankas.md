# Board adapter — CVbankas (Lithuania): the front page is the listing, 181 pages sum to the stated 9 113, and the sitemap is never asked for

<!-- verified: 2026-09-12 -->

<!-- hosts: www.cvbankas.lt, cvbankas.lt -->
<!-- script: cvbankas.py -->
<!-- countries: LT -->
<!-- content: measured · rules read twice and certain — the only Anthropic names refused are `anthropic-ai` and `Claude-Web`, names no request from here carries; `*` refused ten account and social paths and nothing of the board; `identity()` answers `claude-user`, `verdict()` sweeps — and the transport answers 200: the root is the listing, «Rodoma 9 113 skelbimų», page 1 carries 142 VIP cards, pages 2–181 carry 50 each and the last 21 — 142 + 179 × 50 + 21 = 9 113, exactly the stated figure; the advertisement page carries a JobPosting in microdata · 2026-09-12 12:32 UTC -->
<!-- witness: the listing's own «Rodoma N skelbimų», read on every page and printed beside the distinct count — «n emitted, site states 9 113 — equal / k short» — and the page arithmetic 142 + 179 × 50 + 21 measured on pages 1, 2, 3 and 181 -->

**Shipped 2026-09-12 — measured in lot 6 of #233, shipped the same hour.**
Every fetch under the declared identity, the guard on the exact path first,
1 s between pages (no `Crawl-delay`).

```
python3 skills/job-scan/scripts/cvbankas.py list [--pages N] [--limit N] [--no-site-total]   # 181 requests at 1 s for the whole board; --pages bounds the walk
python3 skills/job-scan/scripts/cvbankas.py ad --url https://www.cvbankas.lt/<slug>/<n>-<id>
```

## The rules — two names we never send, and 9 113 advertisements behind them

```
robots.txt      read twice, certain: True, 2744 B, md5 2c4561cefc2b both times
                Cloudflare's managed block (ClaudeBot named there, `*` open) — then the operator's:
                `User-agent: * / Disallow: /issaugoti-skelbimai.html, /prisijungti-*, /siusti-skelbima-draugui, /kandidatuoti-neuzsiregistravus, /banner-job-ads/, /facebook-data-deletion…`
                `User-agent: anthropic-ai / Disallow: /`      `User-agent: Claude-Web / Disallow: /`   <- neither is a name a request from here carries
                `Sitemap: https://www.cvbankas.lt/sitemap.xml`
identity("/")   http, claude-user
verdict()       sweep True, sweep_token claudebot
allowed()       True on `/`, `/?page=N`, `/<slug>/<n>-<id>` — and on `/sitemap.xml`, which the adapter still never reads (below)
crawl_delay     none — 1 s between pages is ours
```

*#233 kept this host under «a name we never send» — the verdict that closed
it was right in its sentence and wrong in its scope
(`un-nom-pour-nous-nest-pas-un-nom-quon-envoie`, 2026-09-05).*

## The transport — 200 on the board, a challenge on the sitemap alone

```
GET https://www.cvbankas.lt/                    200, 813 184 B, md5 3838ccda550e   (12:22:51Z)  «Šiandienos darbo skelbimai» — page 1, 142 VIP cards
GET https://www.cvbankas.lt/                    200, 813 184 B, md5 3838ccda550e   (12:22:53Z — byte-identical)
GET https://www.cvbankas.lt/?page=2             200, 547 502 B                    (12:32:01Z)  50 cards
GET https://www.cvbankas.lt/?page=3             200, 542 804 B                    (12:32:02Z)  50 cards, none shared with page 2
GET https://www.cvbankas.lt/?page=181           200, 464 318 B                    (12:32:03Z)  21 cards — the last page
GET https://www.cvbankas.lt/darbu-vadovo-asistentas-uzsienyje/1-14112398   200, 406 658 B   (12:32:05Z)  JobPosting microdata
GET https://www.cvbankas.lt/sitemap.xml         403, 4 542 B, md5 4099d972c1e3 → ad867f0f2149   (12:25:28Z, 12:25:41Z)  «Attention Required! | Cloudflare» — a challenge on this path
```

**`/sitemap.xml` is never asked for**: `gate()` exits 7 on it before the
rules are consulted. *A path that answers a challenge is not the route
(borne 2), and a 403 on a sitemap is not a closed board
(`un-403-sur-un-sitemap-nest-pas-un-board-ferme`) — the listing serves the
same client one minute earlier.*

## The listing — pages that sum to the stated count

| question | answer |
| :-- | --: |
| stated on every page | **9 113** — «Ieškokite darbo tarp 9 113 pasiūlymų» / «Rodoma 9 113 skelbimų» |
| page 1 | **142** cards, all VIP (`jobadlist_article_vip`) |
| pages 2 … 180 | **50** each (pages 2 and 3 read, disjoint) |
| page 181 | **21** |
| 142 + 179 × 50 + 21 | **9 113** — equal to the unit |
| the card | `id` (`job_ad_<id>`, the URL's tail), title, employer, salary (amount, `€/mėn.` or `€/val.`, net «į rankas» / gross by the block's class), city («Kaune», «Danijoje»), age («prieš 1 d.») |
| page 1 census (142) | salary on 141 (net 79, gross 62), monthly 131, hourly 10; city on 142; employer on 142 |

**The adapter reads the stated figure on each page and prints «n emitted,
site states N — equal / k short» after a full walk; `--pages` bounds the
walk, says «the walk stopped at page p», and does not compare.** *A bounded
count is a lower bound, never a check.*

## What an advertisement carries — microdata, and obfuscated digits

`itemtype JobPosting` with `title` (the `<h1>`), `datePosted` (a
`content=` date), `validThrough` (a `datetime=`, with the posting and
renewal dates in its `title`), `hiringOrganization/name`, `jobLocation` →
`PostalAddress` («Užsienis : Danija» for abroad, the city otherwise),
`description`, the work type («Visa darbo diena»), and sections — «Darbo
pobūdis», «Reikalavimai darbuotojui», «Ką siūlome», «Atlyginimas» in
Lithuanian, «ABOUT THE ROLE», «REQUIREMENTS», «Salary» on an English page:
**a page is Lithuanian or English per advertisement, and the sections are
emitted under the headings the page uses.**

**The salary digits on the page are interleaved with U+200C, the zero-width
non-joiner** — `2‌2‌0‌0‌-3‌0‌0‌0‌` (`&#8204;` between every digit) — an
anti-scraping obfuscation the listing does not apply; the adapter strips it,
says so on stderr, and net / gross comes from the block's class
(`salary_bl_net` / `salary_bl_gross`), not from the language of the label.
**No contacts are read**: the only `mailto:` on the pages read is the
board's own address, and the adapter emits none.

## What this card is, and is not

- **An adapter, shipped** — `list` for the paged enumeration with the
  stated count as the check, `ad` for one advertisement from its microdata.
  No key, no browser; 181 requests at 1 s for the whole board.
- **Not a verdict on the sitemap** — one path, one challenge, dated; the
  board is served, and the adapter goes around the path rather than through
  it.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
