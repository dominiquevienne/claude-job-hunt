# Board measurement — Albania Jobs (Albania): the rules refuse a name we never send, the transport is OPEN, and the job sitemap holds 123 advertisements last touched 2026-08-17

<!-- verified: 2026-09-12 -->

<!-- hosts: albaniajobs.al, www.albaniajobs.al -->
<!-- script: none -->
<!-- countries: AL -->
<!-- content: measured · rules read twice and certain — `anthropic-ai` is the only Anthropic name refused, a name no request from here carries; `*` open bar the WordPress paths and `/*?s=*`, `Crawl-delay: 10`; `identity()` answers `claude-user` and `verdict()` sweeps — and the transport answers 200 at the root, at `/gjej-pune/` and at the sitemap: 123 `/job/<n>-<slug>/` URLs in `job_listing-sitemap.xml`, 123 distinct, 59 distinct `<lastmod>`, the newest 2026-08-17 · 2026-09-12 11:23 UTC -->
<!-- witness: the AIOSEO job sitemap, 123 entries — the listing page `/gjej-pune/` renders its cards by script and shows 2 links to a plain client, so the sitemap is the enumeration; no adapter yet -->

**Measured 2026-09-12 at 11:18:43Z UTC for #233, lot 4 — a measurement of
the transport, not a decision about the host.** Every fetch under the
declared identity, the guard on the exact path first, `bin/fetch-body.py`,
**the host's `Crawl-delay: 10` honoured on every request** (the tool waits).

## The rules — a name we never send, the fourth form of #233, and a `Crawl-delay: 10`

```
robots.txt      read twice, certain: True, 1064 B, md5 3f494e1b8543 both times
                `User-agent: anthropic-ai / Disallow: /`  <- the only Anthropic name in the file; no request from here carries it
                `User-agent: * / Disallow: /wp-admin/ … /*?s=* / Crawl-delay: 10`
identity("/")   http, claude-user
verdict()       sweep True, sweep_token claudebot   <- neither of our tokens is named; both fall under `*`
allowed("/")    True      allowed("/gjej-pune/") True      allowed("/job_listing-sitemap.xml") True
crawl_delay     10 s for `*` — 5 s for Googlebot, Bingbot, Slurp
```

*This host was read as closed on a refusal addressed to `anthropic-ai` — a
name for us that is not a name we send
(`un-nom-pour-nous-nest-pas-un-nom-quon-envoie`, 2026-09-05). The verdict
was right in its sentence and wrong in its scope; this card is the first time
the transport was asked.*

## The transport — 200, and the site is served

```
GET https://albaniajobs.al/                        200, 409 116 B, md5 797a9679594b   (11:18:43Z)  «Albania Jobs Gateway - Connecting Talent with Opportunity», WordPress (AIOSEO 5.0.1.1)
GET https://albaniajobs.al/                        200, 409 116 B, md5 272c362492a0   (11:18:55Z — same size, a per-response nonce)
GET https://albaniajobs.al/gjej-pune/              200, 283 740 B, md5 62977ac55efc   (11:20:56Z)  the listing — 2 `/job/` links in the HTML, the cards are rendered by script
GET https://albaniajobs.al/gjej-pune/              200, 283 740 B, md5 67401a1a49ff   (11:21:07Z)
GET https://albaniajobs.al/sitemap.xml             200, 2 715 B,   md5 07f561adebc9   (11:22:37Z)  index of 15 children
GET https://albaniajobs.al/job_listing-sitemap.xml 200, 30 064 B,  md5 edf23b07ffbc   (11:23:36Z)  123 <loc>
```

## What the sitemap says — 123 advertisements, and the newest is a month old

| question | answer |
| :-- | --: |
| `<loc>` in `job_listing-sitemap.xml` | **123**, all `/job/<n>-<slug>/`, 123 distinct URLs |
| the leading `<n>` | **not an id** — `13` on most entries, `544` on one; the key is the slug |
| distinct `<lastmod>` | 59 — real dates, not a rebuild stamp |
| newest `<lastmod>` | **2026-08-17** (then 2026-07, 2026-05, 2026-02, 2025-12, 2025-07 …) |
| the listing's own count | none found on `/gjej-pune/` — the page renders its cards by script |

*A small board, and a quiet one: nothing touched in the four weeks before
the read — which is not the same as broken (`ejobsfiji`).* **Company pages,
regions, categories and types have sitemaps of their own; only
`job_listing-sitemap.xml` is the enumeration.**

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE:
  the sitemap enumerates, the `<lastmod>` are real dates, and a `/job/` page
  is WordPress with AIOSEO — whether it carries a `JobPosting` is the
  adapter's first question, not asked here. **Candidate adapter, at 10 s a
  request.**
- **Not a verdict that the host is closed** — nothing here refuses us; the
  only refusal in the rules names a token we do not send.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
