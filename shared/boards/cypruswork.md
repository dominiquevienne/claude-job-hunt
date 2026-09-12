# Board measurement — Cyprus Work (Cyprus): reopened by the 2026-09-07 doctrine, and the transport is OPEN — 1 475 jobs stated, 1 475 job URLs in the sitemap

<!-- verified: 2026-09-12 -->

<!-- hosts: www.cypruswork.com, cypruswork.com -->
<!-- script: none -->
<!-- countries: CY -->
<!-- content: measured · rules read twice and certain — `ClaudeBot` named and refused, `*` open, so `identity()` answers `claude-user` and since #230 `verdict()` sweeps under it — and the transport answers 200: 1 475 jobs stated by the listing's own `<h1>1475 jobs</h1>` and 1 475 distinct `/job/<id>/` URLs in `/sitemap.xml` (10 708 `<loc>` in all, 8 874 of them `/company/`), the two counts taken from two documents in the same minute and equal; a job page carries a full `JobPosting` JSON-LD · 2026-09-12 11:01 UTC -->
<!-- witness: the sitemap — 1 475 `/job/<id>/` entries, 1 475 distinct ids, against the listing's stated 1475; no adapter yet, this card is the measurement that precedes one -->

**Measured 2026-09-12 at 11:00:31Z UTC for #233, lot 3 — the one host of
the lot whose transport answers.** Every fetch under the declared identity,
the guard on the exact path first, by `bin/fetch-body.py`; the records carry
status, bytes, md5 and the answering `cf-ray`.

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True, 2531 B, md5 d9cad68a6c11 both times — `User-agent: ClaudeBot / Disallow: /`, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed("/")    True      allowed("/jobs/") True      allowed("/sitemap.xml") True      allowed("/download/x") False
```

*Cloudflare's managed content block — nine named crawlers refused,
`ClaudeBot` among them — followed by the operator's own lines: for `*`,
`/files/files/`, `/download/` and `/application-redirect/` closed, the same
three for `bingbot`, a dozen SEO crawlers refused by name, and
`Sitemap: https://www.cypruswork.com/sitemap.xml`.* Before the decision this
host was read as closed by name (#233 lists it under «another managed block
naming ClaudeBot»); the decision reopened it on paper, and **this is the first
host of #233 whose transport answers under the permitted token.**

## The transport — 200, and the site is served

```
GET https://www.cypruswork.com/              200, 177 806 B, md5 62981f5d5fb7    (11:00:31Z)   «Jobs in Cyprus - Cyprus Jobs & Recruitment | Cyprus Work»
GET https://www.cypruswork.com/              200, 177 945 B, md5 57eecffb02c3    (second fetch — dynamic page, sizes differ)
GET https://www.cypruswork.com/jobs/         200, 146 956 B, md5 7437d68828af    (11:01:15Z)   `<h1>1475 jobs</h1>`, 20 `/job/<id>/` links
GET https://www.cypruswork.com/jobs/         200, 146 956 B, md5 efe66be8fc24    (second fetch — same size, a per-response token)
GET https://www.cypruswork.com/sitemap.xml   200, 1 770 253 B, md5 c3198f2f783f  (11:01:18Z)   10 708 <loc>
GET https://www.cypruswork.com/job/110094/…  200, 78 312 B,  md5 575883cede48    (11:03:38Z)   JobPosting JSON-LD
```

**Same managed block as `www.cyprusjobs.com`, measured two seconds apart —
and that sibling answers the 25-byte static 403.** *The rules file predicts
nothing about the transport; only the fetch does.*

## What the board declares, and what a second document says

| question | answer | where |
| :-- | --: | :-- |
| jobs stated by the board | **1 475** | `/jobs/`, `<h1>1475 jobs</h1>`, and the same figure in `description` / `og:description` |
| `/job/<id>/` URLs in the sitemap | **1 475** | `/sitemap.xml`, one `urlset`, no index |
| distinct ids among them | **1 475** | the `\d+` after `/job/` |
| other `<loc>` | 8 874 `/company/`, 256 `/jobs/…` facets, 47 `/categories/`, 19 `/blog/`, 11 `/cities/`, 6 `/states/`, 3 `/countries/`, 1 root | first path segment |
| `lastmod` on the job URLs | `2026-09-12` on all 1 475 — **one value, the day of the read** | a rebuild stamp, not a posting date (`deux-lastmod-muets-pour-deux-raisons`) |

**Two counts from two documents, taken three seconds apart, equal to the
unit.** *That is the check the adapter will carry: emitted against stated,
and the sitemap is the enumeration — 1 475 URLs, no pagination to walk.*

## What a job page carries

`https://www.cypruswork.com/job/110094/business-development-manager/` (one
page, 11:03:38Z): three JSON-LD blocks — **`JobPosting`** with `title`,
`description`, `datePosted`, `validThrough`, `employmentType`,
`hiringOrganization`, `jobLocation`, `baseSalary`, `industry`,
`occupationalCategory`, `directApply`, `url` — plus `BreadcrumbList` and
`WebSite`. *Which of these fields are populated and which are a hollow
`baseSalary` is the adapter's measurement, not this card's — one page shows
the shape, not the fill.*

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, and that is a
  measurement DUE, not a renunciation (owner, 2026-09-08: «there is never any
  reason not to use a board»). **Candidate adapter, named to the pilot in
  the lot-3 report**: sitemap enumeration of 1 475 `/job/<id>/` URLs, the
  `JobPosting` JSON-LD on each, the stated total on `/jobs/` as the witness.
- **Not a verdict on the sibling** `www.cyprusjobs.com`, which has its own
  card and its own dated read.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter` today; the page is served to the plugin's client.
