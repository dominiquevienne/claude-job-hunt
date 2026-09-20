# Board adapter — Mabumbe (Tanzania): a challenge to the declared client on every path, the user's tab served — and from inside it the WordPress REST collection `noo_job` answers, 100 a page, `after=` for the window; `mabumbe.py jobs --from` normalises what the tab hands over, the archive's 44 523 named as an archive

<!-- verified: 2026-09-20 -->

<!-- hosts: mabumbe.com, www.mabumbe.com -->
<!-- script: mabumbe.py -->
<!-- countries: TZ -->
<!-- content: measured · **2026-09-20 14:16–14:22 UTC, the declared client and a connected tab.** Rules (`/robots.txt`, 200, 1 956 B — no longer the Cloudflare managed file of 11.09): `ChatGPT-User`, `python`, `curl`, `wget` and some thirty SEO crawlers refused `/`; `User-agent: *` closes `/wp-admin/`, `/wp-includes/`, `/cgi-bin/` only — neither `Claude-User` nor `ClaudeBot` named, the `*` group applies, `/jobs/` and `/wp-json/` permitted. Transport to the client: `/jobs/`, `/sitemap.xml`, `/wp-json/wp/v2/posts`, `/wp-json/wp/v2/noo_job` — HTTP 403 ×2 each, 5 652–5 790 B «Just a moment...», md5 moving at constant size (the challenge of 11.09, unchanged; never defeated). The tab: `/jobs/` served, «44,523 jobs found», 14 cards on page 1 (`article.ajzjp-card`, `data-job-id`, the employer in `.ajzjp-card-company`), pager to `/jobs/page/3425/`; and from inside the page `fetch('/wp-json/wp/v2/noo_job?per_page=100&page=N&_embed=wp:term')` answers 200 — `x-wp-total` **44 523** (= the page's counter: the archive since the site began), `x-wp-totalpages` 446, `per_page` capped at 100 (101 → 400), ten calls in a row served; `after=2026-08-21T00:00:00` → **619** (7 pages), `after=2026-09-13T00:00:00` → **146** over 2 pages, 146 distinct ids — equal; 133 of the 146 titles carry « at <employer> », 78 of 146 a deadline in one of three prose forms. Each item: `date`/`date_gmt`, `modified`, `link`, `title`, `content` (the whole advert, 2 000–16 000 characters), `excerpt`, and the terms `job_category` (NGO and Social Work 8 053, Administration 5 991, Government 5 123, Banking and Finance 4 558 …), `job_location` (60; Dar es Salaam 26 956, Arusha 3 230, Dodoma 2 807), `job_type` (Full time Jobs; the rest SEO tags). No JobPosting, no employer field · 2026-09-20 -->
<!-- witness: none — nothing was served. The site's own «44 156» (2026-09-02, `shared/plausible-and-false.md`) is a WordPress archive counter with expired advertisements inside it, cited there and not re-read here · **browser, 2026-09-14 10:04 UTC: `/jobs/` served to a connected tab without the interstitial — «44,393 jobs found», WordPress posts 15 a page, `/jobs/page/2/ … /3415/`, the last carrying 14; the count is the archive's (posts since the site began — tenders, notices and results among them), not a count of live advertisements; the ad page carries a WebPage / BreadcrumbList / WebSite / Organization graph and no JobPosting** · **the bound, one page, 10:16 UTC: page 1 of `/jobs/` holds 15 posts, every title dated «September 2026» (the cards render no `<time>`; the month lives in the title), 13 of them vacancies (a job at a named employer, or a recruitment digest of a named body — TIRA 9 posts, NSI 13, councils 59), 1 a tender, 1 a digest of other posts; the archive's 44 393 is the site's counter, the live fraction is what a walk stopped at the first older month yields** -->
<!-- route: browser · 619 · 2026-09-20 -->

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

## 2026-09-20 — #332: the collection behind the archive page, from the tab; `mabumbe.py`

**Measured 2026-09-20 14:16–14:22 UTC.** The challenge to the declared
client is what it was on the 11th and the 14th — `/jobs/`, `/sitemap.xml`
and two REST routes answer 403 with «Just a moment...» twice each, md5
moving — and the tab is served as on the 14th. What is new is what the tab
can reach: **the WordPress REST collection of the site's job post type,
`noo_job`**, from inside the page:

```
fetch('/wp-json/wp/v2/noo_job?per_page=100&page=1&_embed=wp:term')                      200 · x-wp-total 44523 · x-wp-totalpages 446
fetch('/wp-json/wp/v2/noo_job?per_page=100&page=1&_embed=wp:term&after=2026-08-21T00:00:00')   200 · 619 · 7 pages
fetch('/wp-json/wp/v2/noo_job?per_page=100&page=1&_embed=wp:term&after=2026-09-13T00:00:00')   200 · 146 · 2 pages — 146 distinct ids read
fetch('/wp-json/wp/v2/noo_job?per_page=101')                                             400 (the cap is 100)
```

**44 523 is the page's own «jobs found» — and it is the archive**: every
post ever filed as a job (the count grew from 44 393 on the 14th to 44 523
on the 20th, 130 posts in six days — 146 in the seven days `after=` reads,
tenders, exam notices and «Call for Interview» digests among them). The
`route:` line now carries **619, the posts of the last 30 days**, the window
`mabumbe.py` reads by default; the archive is named beside it, never
counted as live advertisements. `_embed=wp:term` resolves the taxonomies
in the same answer: `job_location` (60 terms), `job_category`, `job_type`
(one real value, «Full time Jobs», among SEO tags), `job_tag` (Swahili SEO
phrases — dropped). **No employer field**: the title's own shape carries it
(«Executive Secretary at NEEC September 2026» → NEEC; 133 of 146 titles have
an « at »), null otherwise; the deadline is prose in three forms («Deadline
is 30th September 2026», «Application deadline: 30 September 2026»,
«Application Period 18/09/2026 – 01/10/2026»), read when present (78 of
146), null otherwise.

**The adapter, `mabumbe.py` (#332).** `jobs` over HTTP takes the guard, asks
the route once, meets the 403 and **dies with exit 9** — the browser exit of
`_ua.browser_fallback` — printing the procedure: open `https://mabumbe.com/jobs/`
in the user's own Chrome, run the `fetch()` above one page at a time (2 s
apart), save each answer to a file, and `mabumbe.py jobs --from p1.json
p2.json … --stated <x-wp-total>`. `--from` normalises the tab's JSON — id,
url, title (the « at » part removed) and `title_as_posted`, `company`,
`posted` (`date_gmt` as UTC), `modified`, `closes`, `locations`,
`categories`, `job_type`, the description as text — and prints «N emitted,
the route states M for the window» beside it. `ad --url
https://mabumbe.com/jobs/<slug>/` asks the same route by `slug=` and dies
the same way; `ad --from` reads the saved answer. **Never another agent
string, never the challenge answered.**

**Withheld.** E-mail addresses and telephone numbers scrubbed from the
description (the adverts end with «Applications … should be sent via e-mail
to …» — the sentence stays, the address does not); the site's apply link
(«CLICK HERE TO APPLY») never emitted; `job_tag` dropped;
`contacts_withheld` on every record. Guard in `tests/`: the challenge and
its exit, the paged walk against `x-wp-total`, the tab's JSON normalised
both with and without `_embedded`, the employer from the title, the three
deadline forms and their absence, the scrub, the apply link, a repeated id
once, a bad file refused, another host never sent — 6 mutations, 6 red
(2026-09-20).

