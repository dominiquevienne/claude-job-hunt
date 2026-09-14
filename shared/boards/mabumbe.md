# Board adapter — Mabumbe (Tanzania): rules open to `Claude-User`, and an anti-robot challenge on every path

<!-- verified: 2026-09-14 -->

<!-- hosts: mabumbe.com, www.mabumbe.com -->
<!-- script: none -->
<!-- countries: TZ -->
<!-- content: indeterminate · 2 hosts, same rules; 4 paths tried under the permitted token and all 4 answer HTTP 403 with a 5 637-byte Cloudflare interstitial titled `Just a moment...`, md5 different on two fetches of the same URL at constant size — a challenge, not a page; nothing of the site was read · 2026-09-11 13:20 UTC -->
<!-- witness: none — nothing was served. The site's own «44 156» (2026-09-02, `shared/plausible-and-false.md`) is a WordPress archive counter with expired advertisements inside it, cited there and not re-read here · **browser, 2026-09-14 10:04 UTC: `/jobs/` served to a connected tab without the interstitial — «44,393 jobs found», WordPress posts 15 a page, `/jobs/page/2/ … /3415/`, the last carrying 14; the count is the archive's (posts since the site began — tenders, notices and results among them), not a count of live advertisements; the ad page carries a WebPage / BreadcrumbList / WebSite / Organization graph and no JobPosting** · **the bound, one page, 10:16 UTC: page 1 of `/jobs/` holds 15 posts, every title dated «September 2026» (the cards render no `<time>`; the month lives in the title), 13 of them vacancies (a job at a named employer, or a recruitment digest of a named body — TIRA 9 posts, NSI 13, councils 59), 1 a tender, 1 a digest of other posts; the archive's 44 393 is the site's counter, the live fraction is what a walk stopped at the first older month yields** -->
<!-- route: browser · 44393 · 2026-09-14 -->

**Tanzania's first host on a card.** *The rules open and the transport serves a
challenge — two different kinds of «no», and the second is the one that
decides here.* Measured 2026-09-11, 13:19–13:21 UTC, every fetch through
`bin/fetch-body.py` under the declared identity, the guard taken on the exact
path first.

## The rules — the Cloudflare managed file, and it names this project

```
GET https://mabumbe.com/robots.txt      200, fetched twice, same body
# BEGIN Cloudflare Managed content
User-agent: *
Content-Signal: search=yes,ai-train=no,use=reference
Allow: /
User-agent: Amazonbot · Applebot-Extended · Bytespider · CCBot · ClaudeBot ·
            CloudflareBrowserRenderingCrawler · Google-Extended · GPTBot · meta-externalagent
Disallow: /
# END Cloudflare Managed Content
User-agent: Googlebot          Disallow:
User-agent: Bingbot            Crawl-delay: 15   Disallow:
```

No `Sitemap:` line. **`ClaudeBot` is named and refused everything; `Claude-User`
is not named and falls in `*`, which allows `/`.** Under the owner's decision of
2026-09-07 the two tokens are distinct and the group naming one does not bind
the other — `identity("mabumbe.com", "/jobs/")` answers `http`, token
`claude-user`, `per_token: claudebot False (rule /), claude-user True`. **So
the permitted route exists on paper, and it is the one that was tried.**
`Content-Signal: ai-train=no` is a reservation about training; this project
reads for one person's search and stores nothing of the content.

| path | `_robots.allowed()` under `claude-user` |
| :-- | :-- |
| `/` · `/jobs/` · `/feed/` | True |
| `/wp-json/wp/v2/posts` | True |
| `/sitemap_index.xml` · `/job-sitemap.xml` · `/wp-sitemap.xml` | True |

## The transport — a challenge, on every path, with a moving fingerprint

```
GET https://mabumbe.com/                          403, 5 637 B, md5 7a4bddc9…   «Just a moment...»
GET https://mabumbe.com/                          403, 5 637 B, md5 21178ecf…   «Just a moment...»   <- same URL, second fetch
GET https://mabumbe.com/sitemap_index.xml         403, 5 709 B
GET https://mabumbe.com/wp-json/wp/v2/posts?per_page=1   403, 5 784 B
```

**Two fetches of the same URL, same size, different md5 — the `cf-ray` and a
`challenge-platform` script are inside the body.** *That is the measurement
`shared/robots-policy.md` requires before comparing fingerprints across hosts,
and it says the comparison is void here: this body carries an element of
rendering.* **It is the family of `www.revolico.com` (5 642 B, same title, same
behaviour), not the 25-byte static `Your request was blocked.` of
`www.jobstore.com` and `www.hays.fr`.**

**A challenge is where the browser branch stops.** *The 2026-09-07 decision
opens the browser for a host whose rules permit and whose transport refuses the
client — a static 403 says the infrastructure does not know who we are. An
interstitial that asks the client to prove itself is an anti-robot control,
and the plugin neither defeats one nor asks the user to* (borne 2). **Whether a
real browser passes this managed challenge without a person is not measured
here, and this card does not claim it either way.**

## The counter — 44 156, and what it counts

`shared/plausible-and-false.md` recorded on 2026-09-02: **«44 156 — a
WordPress archive counter inflated with expired ads»**. *A WordPress site
counts what its archive holds, and a job board's archive holds what expired.*
**If this host ever opens, the anchor to build is «live vs archive» — a
publication date on every advertisement, a closing date or an expired status
if the theme carries one — and the site's counter goes beside the count as
what it is, an archive figure, never as the board's size.** Not re-read here:
the page that carries it was not served.

## What this card is, and is not

- **Not a verdict that the board is closed** — that is the owner's decision,
  on his express validation (rule of 2026-09-08). This card records that four
  permitted paths answered a challenge on one day, twice, from one client.
- **Not the #222 case as measured here**: #222 collects hosts whose transport
  refuses the *client* with a static 403 and serves a browser; this host serves
  a challenge, which borne 2 keeps out of the browser branch. *If the owner
  measures that a real browser passes it without a person, the host moves
  families and the card says so with the date.*
- **No script, no configuration.** A user who has a mabumbe.com URL from
  elsewhere can hand it to `cover-letter`; whether that page is served to a
  browser is not established here.

## 2026-09-14 10:03–10:06 UTC — no interstitial to a connected tab

```
tab, /                       served — the front page: a job search form (locations, 150 categories), «Featured Jobs», «Sponsored Jobs»
tab, /jobs/                  served — «44,393 jobs found», 15 posts a page, pager /jobs/page/2/ … /3415/
tab, /jobs/page/3415/        served — 14 posts, no page 3416
tab, /jobs/<slug>/           served — WebPage / BreadcrumbList / WebSite / Organization JSON-LD; no JobPosting
```

**`route: browser · 44393 · 2026-09-14`**, with the caveat written on the
line and a bound of one page (10:16 UTC): page 1 holds 15 posts, every
title dated «September 2026» — 13 vacancies (a job at a named employer,
or a recruitment digest of a named body), 1 tender, 1 digest of other
posts; no `<time>` on the cards, the month is in the title. The count is
the archive's — every post the site ever filed under
«jobs», tenders and exam notices among them — not a count of live
advertisements; a session reading from a tab walks `/jobs/page/N/` from 1
and stops at the first post older than the window it wants, the slug as
the key, the post's own date and employer from its title («… job at
<employer> <month> <year>»). The declared client gets the moving «Just a
moment…» (2026-09-11, 2026-09-13) — never defeated; the tab was not
challenged today.

