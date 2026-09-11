# Board adapter — Wuzzuf (Egypt): the sitemap is served, the pages answer a challenge

<!-- verified: 2026-09-11 -->

<!-- hosts: wuzzuf.net -->
<!-- script: wuzzuf.py -->
<!-- host-forms: wuzzuf.net -->
<!-- host-forms-basis: read — `wuzzuf.py:BASE`, a single literal; the addresses come from the sitemap as served · 2026-09-11 -->
<!-- countries: EG SA -->
<!-- content: measured · 5 491 advertisement ADDRESSES in `sitemap-job-1.xml`, 5 491 distinct — 5 321 under `/jobs/p/`, 89 under `/saudi/jobs/p/`, 81 under `/internship/`; by the slug's tail 5 272 Egypt, 84 Saudi Arabia, 34 UAE; **none of the pages readable by this client (challenge)**, so these are addresses, not verified advertisements; `wuzzuf.py sitemap` at 13:49 UTC · 2026-09-11 -->
<!-- witness: none — no route this adapter may take states how many advertisements are open; every `<lastmod>` in the file carries the same value (`2026-09-11T02:04:48+03:00`), a regeneration stamp, so a second reading would compare a rebuild with a rebuild · 2026-09-11 -->

**Egypt's largest board and the first Egyptian host with a script here** — a
hundred million people, two cards before this one (`bayt`, `tanqeeb`) and no
adapter. Measured 2026-09-11, 13:45–13:50 UTC, every fetch through
`bin/fetch-body.py` or the adapter under the declared identity, the guard on
the exact path first, the host's own `Crawl-delay: 10` applied.

## The rules — the Cloudflare managed file, `ClaudeBot` refused, `*` open, and a Sitemap

```
GET /robots.txt        200 — the managed preamble (twice, as robots-policy.md records), then:
                       User-agent: *  … Allow: /   Crawl-delay: 10   Sitemap: https://wuzzuf.net/sitemap.xml
                       User-agent: ClaudeBot (with CCBot, GPTBot, …)   Disallow: /
```

`identity("wuzzuf.net", "/jobs/egypt")` → `http`, `claude-user`
(`claudebot False (rule /), claude-user True`) — **the owner's decision of
2026-09-07: the group naming one token does not bind the other.**
`allowed()`: `/`, `/jobs/egypt`, `/search/jobs`, `/jobs/p/<id>-<slug>`,
`/sitemap.xml` all `True`, `certain: True`; `/search/jobs/?q=…` **False** —
a query string on the search is refused in writing.

## The transport splits — HTML answers a challenge, XML is served

```
GET /jobs/egypt                          403, 5 666 B, «Just a moment...», md5 eb5e257b… then d604418d…
                                         ← same URL twice, same size, different md5: a challenge
GET /jobs/p/reb7hiksiwdr-…-cairo-egypt   403, 5 949 B, «Just a moment...»
GET /sitemap.xml                         200, 4 520 B, 37 children
GET /sitemap-job-1.xml                   200, 1 642 641 B, 5 491 <loc>, 5 491 <lastmod>
```

**The pages are the `revolico` / `mabumbe` family** — an interstitial with the
`cf-ray` inside the body, where borne 2 keeps the browser branch out. **The
sitemap is not behind it.** So the route is the sitemap, and what it yields is
an inventory of addresses:

```
https://wuzzuf.net/jobs/p/<12-char id>-<title>-<company>-<city>-<country>
https://wuzzuf.net/internship/<id>-<slug>
https://wuzzuf.net/saudi/jobs/p/<id>-<slug>
```

*The slug carries a title, an employer, a city and a country in the site's own
words, run together with hyphens — the tail is mapped to an ISO-2 code
(`egypt` → EG, `saudi-arabia` → SA …), and the rest is emitted as `slug`,
unsplit, because nothing reads the page to check a split.*

## The count is a count of addresses, and it says so

```
5491 <loc> in 1 file(s); 5491 matched the advertisement shape and 0 did not; 5491 distinct id(s).
by shape: jobs/p 5321, saudi/jobs/p 89, internship 81 · by country tail: EG 5272, SA 84, ? 38, AE 34, US 26, GB 12, LY 10, CA 9
every <lastmod> carries the same value (2026-09-11T02:04:48+03:00) — a regeneration stamp, not a posting date.
```

**`--country eg` reduces 5 491 to 5 272** — the filter is shown to reduce
(#219). **No route this adapter may take states how many advertisements are
open**, so nothing anchors 5 491 to the board: `shared/boards/README.md`'s
warning stands — *a count of `<loc>` is not a count of advertisements* — and
`readable_by_script: false` rides on every row. A zero here would be «the
sitemap held no address», said with the byte count, exit 6.

**The index also declares `sitemap-saudi-job-1.xml`** (`--saudi` reads it too)
and 26 `sitemap-talent-N.xml` files — CVs, never read. `careers/sitemap_index.xml`
is a separate product.

## `ad` reads nothing, and says why

`wuzzuf.py ad --url …` fetches the address and, on the challenge, exits 9
naming it: *the rules permit this path and the server answers an anti-robot
challenge; this adapter does not attempt to pass it and does not ask anyone
to.* If the host ever serves a page to this client, the branch says the host
changed and stops rather than emit fields nobody verified.

## Configuration

```yaml
boards:
  wuzzuf:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials. `sitemap` is two requests ten seconds apart (three with
`--saudi`).

## What is not established

- **Whether the addresses are live**: the pages cannot be read by this client,
  and the `<lastmod>` is a rebuild stamp. The file is regenerated (2 a.m.
  local, by its stamp); whether it drops closed advertisements is not measured.
- **The title, employer, date and text** of any advertisement — only the slug.
- **Whether a real browser passes the managed challenge without a person** —
  not measured, and this card claims nothing either way.
- **`/search/jobs` and its filters** — the path is permitted without a query
  string and answers the challenge like every page.

## 2026-09-11 — shipped, as an inventory of addresses

Measured 13:45–13:50 UTC. Rules twice; `/jobs/egypt` twice (challenge, moving
md5); one advertisement page (challenge); `/sitemap.xml` and
`sitemap-job-1.xml` once each. `wuzzuf.py sitemap`: 5 491 addresses, 5 491
distinct, `--country eg` 5 272.
