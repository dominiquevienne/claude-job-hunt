# Board measurement — CVbankas (Lithuania): the rules refuse two names we never send, the transport is OPEN, the front page IS the listing — 9 113 advertisements stated, 181 pages — and the sitemap alone answers a challenge

<!-- verified: 2026-09-12 -->

<!-- hosts: www.cvbankas.lt, cvbankas.lt -->
<!-- script: none -->
<!-- countries: LT -->
<!-- content: measured · rules read twice and certain — the only Anthropic names refused are `anthropic-ai` and `Claude-Web`, names no request from here carries; `*` refused ten account and social paths and nothing of the board; `identity()` answers `claude-user`, `verdict()` sweeps — and the transport answers 200 at the root, twice, byte-identical (813 184 B): the root is the listing, «Rodoma 9 113 skelbimų», 54 advertisement links of the shape `/<slug>/<n>-<id>`, `rel=next` to `/?page=2`, the last page link `?page=181`; `/sitemap.xml` answers 403 «Attention Required! | Cloudflare» twice (4 542 B, moving md5) — a challenge on that one path, not on the board · 2026-09-12 12:25 UTC -->
<!-- witness: the listing's own «Rodoma 9 113 skelbimų» against 181 pages of ~50 — the enumeration is the paged listing, not the sitemap; no adapter yet -->

**Measured 2026-09-12 at 12:22:51Z UTC for #233, lot 6 — a measurement of
the transport, not a decision about the host.** Every fetch under the
declared identity, the guard on the exact path first, `bin/fetch-body.py`.

## The rules — two names we never send, and 9 113 advertisements behind them

```
robots.txt      read twice, certain: True, 2744 B, md5 2c4561cefc2b both times
                Cloudflare's managed block (ClaudeBot named there, `*` open) — then the operator's:
                `User-agent: * / Disallow: /issaugoti-skelbimai.html, /prisijungti-*, /siusti-skelbima-draugui, /kandidatuoti-neuzsiregistravus, /banner-job-ads/, /facebook-data-deletion…`
                `User-agent: anthropic-ai / Disallow: /`      `User-agent: Claude-Web / Disallow: /`   <- neither is a name a request from here carries
                `Sitemap: https://www.cvbankas.lt/sitemap.xml`
identity("/")   http, claude-user
verdict()       sweep True, sweep_token claudebot
allowed()       True on `/`, `/?page=2`, `/sitemap.xml`, `/<slug>/<n>-<id>`
crawl_delay     none
```

*#233 keeps this host under «a name we never send» — the verdict that closed
it was right in its sentence and wrong in its scope
(`un-nom-pour-nous-nest-pas-un-nom-quon-envoie`, 2026-09-05).*

## The transport — 200 on the board, a challenge on the sitemap alone

```
GET https://www.cvbankas.lt/                    200, 813 184 B, md5 3838ccda550e   (12:22:51Z)  «Šiandienos darbo skelbimai | CVbankas.lt» — the listing
GET https://www.cvbankas.lt/                    200, 813 184 B, md5 3838ccda550e   (12:22:53Z — byte-identical)
GET https://www.cvbankas.lt/sitemap.xml         403, 4 542 B,  md5 4099d972c1e3   (12:25:28Z)  «Attention Required! | Cloudflare»
GET https://www.cvbankas.lt/sitemap.xml         403, 4 542 B,  md5 ad867f0f2149   (12:25:41Z)  moving md5 — a challenge, on this path
GET https://www.cvbankas.lt/darbo-skelbimai     404, 340 246 B                    (12:25:41Z)  a guessed path; «Puslapis nerastas» — the site's own 404, served
```

**A 403 on a sitemap is not a closed board**
(`un-403-sur-un-sitemap-nest-pas-un-board-ferme`): the root serves the
listing to the same client one minute earlier, and the 404 on a guessed path
is the site's own page. *The challenge sits on `/sitemap.xml` — a WAF rule
on one path; borne 2 stops there and nowhere else.*

## What the listing says

| question | answer | where |
| :-- | --: | :-- |
| advertisements stated | **9 113** | «Ieškokite darbo tarp 9 113 pasiūlymų» and «Rodoma 9 113 skelbimų» on the root |
| pages | **181** (`/?page=2` … `/?page=181`, `rel=next`) | ~50 a page: 181 × 50 = 9 050, within a page of the stated 9 113 |
| advertisement links on page 1 | 54, of the shape `/<slug>/<n>-<id>` (`/sandelio-darbuotojas-a-kaune/<n>-<id>`) | the trailing number is the key |
| JSON-LD on the listing | none | a job page was not read in this lot |

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE.
  **Candidate adapter**: the paged listing enumerates (181 requests at 2 s,
  or fewer with a filter), the stated 9 113 is the witness, and a job page's
  markup is the adapter's first question. *Lithuania is at zero adapters;
  `cvonline.lt`, the same country's other host of #233, refuses today.*
- **Not a verdict that the sitemap is closed** — one path, one challenge,
  dated; the board is served.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
