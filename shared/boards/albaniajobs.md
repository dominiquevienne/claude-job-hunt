# Board adapter — Albania Jobs (Albania): a WordPress board read through its REST collection at ten seconds a request — 123 advertisements, and the job sitemap lists the same 123

<!-- verified: 2026-09-12 -->

<!-- hosts: albaniajobs.al, www.albaniajobs.al -->
<!-- script: albaniajobs.py -->
<!-- countries: AL -->
<!-- content: measured · rules read twice and certain — `anthropic-ai` is the only Anthropic name refused, a name no request from here carries; `*` open bar the WordPress paths and `/*?s=*`, `Crawl-delay: 10` honoured; `identity()` answers `claude-user`, `verdict()` sweeps — and the transport answers 200: 123 listings in the REST collection `/wp-json/wp/v2/job-listings` (2 pages), 123 distinct post ids, against 123 `/job/` URLs in `job_listing-sitemap.xml`, equal; a `JobPosting` JSON-LD on the page read · 2026-09-12 11:36 UTC -->
<!-- witness: the AIOSEO job sitemap, printed by the adapter beside its distinct count — «123 emitted, sitemap lists 123 — equal» on 2026-09-12 11:37 UTC, «k short» when they part; and the taxonomy term counts sum to 123 on both region and type -->

**Shipped 2026-09-12 — Albania's first adapter, on the host #233 had read
as closed for refusing a name we never send.** Measured 11:18–11:37 UTC;
every fetch under the declared identity, the guard on the exact path first,
**the host's `Crawl-delay: 10` honoured on every request** (`_pace.Pace`
reads it from the rules).

```
python3 skills/job-scan/scripts/albaniajobs.py list [--limit N] [--no-terms] [--no-site-total]   # 2 REST pages + 3 taxonomies + the sitemap: 6 requests, ~55 s
python3 skills/job-scan/scripts/albaniajobs.py ad --url https://albaniajobs.al/job/<slug>/
```

## The rules — a name we never send, the fourth form of #233, and a `Crawl-delay: 10`

```
robots.txt      read twice, certain: True, 1064 B, md5 3f494e1b8543 both times
                `User-agent: anthropic-ai / Disallow: /`  <- the only Anthropic name in the file; no request from here carries it
                `User-agent: * / Disallow: /wp-admin/ … /*?s=* / Crawl-delay: 10`
identity("/")   http, claude-user
verdict()       sweep True, sweep_token claudebot   <- neither of our tokens is named; both fall under `*`
allowed()       True on `/`, `/gjej-pune/`, `/job/<slug>/`, `/wp-json/wp/v2/job-listings?…`, `/job_listing-sitemap.xml`
crawl_delay     10 s for `*` — 5 s for Googlebot, Bingbot, Slurp
```

*This host was read as closed on a refusal addressed to `anthropic-ai` — a
name for us that is not a name we send
(`un-nom-pour-nous-nest-pas-un-nom-quon-envoie`, 2026-09-05). The verdict
was right in its sentence and wrong in its scope.*

## The transport — 200, and the site is served

```
GET https://albaniajobs.al/                                              200, 409 116 B   (11:18:43Z)  «Albania Jobs Gateway», WordPress + AIOSEO 5.0.1.1 + WP Job Manager
GET https://albaniajobs.al/gjej-pune/                                    200, 283 740 B   (11:20:56Z)  the listing — 2 `/job/` links in the HTML, the cards are rendered by script
GET https://albaniajobs.al/job_listing-sitemap.xml                       200, 30 064 B    (11:23:36Z)  123 <loc>
GET https://albaniajobs.al/job/544-account-manager-60-100-fully-remote/  200, 191 365 B   (11:33:02Z)  JobPosting JSON-LD in the AIOSEO @graph
GET https://albaniajobs.al/wp-json/wp/v2/job-listings?per_page=100&page=1   200, 2 521 935 B   (11:33:41Z)  100 listings
GET https://albaniajobs.al/wp-json/wp/v2/job-listings?per_page=100&page=2   200, 559 509 B     (11:33:54Z)  23 listings
GET https://albaniajobs.al/wp-json/wp/v2/{job_listing_region,job-types,job-categories}?per_page=100   200   (11:34:45–11:35:13Z)  64 / 14 / 74 terms
```

## Two enumerations of one store, and a third agreement

| question | answer | where |
| :-- | --: | :-- |
| listings in the REST collection | **123** over 2 pages — 123 distinct post ids | `job-listings?per_page=100&page=N`; WordPress answers 400 past the last page |
| `/job/` URLs in the job sitemap | **123** | `job_listing-sitemap.xml` — 59 distinct `<lastmod>`, real dates, the newest 2026-08-17 |
| region term counts, summed | 123 — Tiranë 91 · Shqipëri 11 · Vlorë 11 · Durrës 2 · Kavajë 2 · Kosovë 1 | `job_listing_region` |
| type term counts, summed | 123 — «Kohë e Plotë» 118 · «E përkohshme / Sezonale» 3 · «Full Time» 1 · «Kohë e Pjesshme» 1 | `job-types` |
| the listing page's own count | none — `/gjej-pune/` renders its cards by script | |

**The URL carries no id.** `/job/13-truck-driver-poland/`: the leading
number is `13` on most entries and `544` on one — not a key. *The key is
the WordPress post id (`3248`, `2993`…) from the REST `id`; `ad` reads it
back from the page's `JobPosting` `identifier.value`
(`…?post_type=job_listing&p=2993`).*

## What the collection holds, measured on the 123

| field | filled | what it says |
| :-- | --: | :-- |
| `title`, `link`, `date_gmt`, `modified_gmt`, `content`, `excerpt` | 123 | present; `date_gmt` carries no zone marker and is emitted with a `Z` |
| `job_listing_region`, `job-types` | 123 | term ids, resolved to names by three more requests (`--no-terms` keeps the ids) |
| `job-categories` | 115 | 0 on 8, 1 on 112, 2–4 on 3 |
| `_company_name` | **2** | **the employer is not in the collection** — the page's `hiringOrganization.name` has it, so `ad` is where it comes from |
| `_job_salary`, `_currency`, `_unit` | **0** | the fields exist and nobody fills them |
| `_remote_position` | 1 | and the page says `jobLocationType: TELECOMMUTE` on that one |
| `_filled` | 2 | emitted as `filled: true` — a listing the board marks taken, not dropped |

**A small and quiet board**: 123 published since 2023-09, 20 in 2023-10, then
a trickle — 2025-12 ×2, 2026-04, 2026-07, 2026-08 ×1 each. *Nothing touched
in the four weeks before the read, which is not the same as broken
(`ejobsfiji`).* **The board is bilingual (Albanian / English) and says
nothing per listing: no `language` is emitted.**

## What this card is, and is not

- **An adapter, shipped** — `list` for the enumeration through REST with
  the sitemap as the check, `ad` for one advertisement from the page's
  JSON-LD (employer, place «Shqipëri» as a string, remote, description). No
  key, no browser; six requests at ten seconds for the enumeration.
- **The refusal in the rules is recorded as written**: it names
  `anthropic-ai`, and nothing this adapter sends.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
