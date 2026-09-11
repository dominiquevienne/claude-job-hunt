# Board adapter — Jobindex (`www.jobindex.dk`): Denmark's first, and page 1 is the cap by the site's own rules

<!-- verified: 2026-09-11 -->

<!-- hosts: www.jobindex.dk -->
<!-- script: jobindex.py -->
<!-- host-forms: www.jobindex.dk -->
<!-- host-forms-basis: read — `jobindex.py:HOST`, a single literal; the apex `jobindex.dk` publishes `Disallow: /` and is never fetched · 2026-09-11 -->
<!-- countries: DK -->
<!-- content: measured · 8 949 advertisements the site states as `hitcount` for the query `udvikler` (`jobindex.py search --q udvikler`, 13:28 UTC), and 37 600 stated by its header for the whole board («37.600 job i dag», read off the same page) — both the site's numbers, neither this adapter's; the adapter returns 20 per query, page 1, because page 2 is refused in writing · 2026-09-11 13:28 UTC -->
<!-- witness: second branch of the same operator — the RSS the page declares, `/jobsoegning.rss?q=udvikler`, lists 20 `<item>` for the same query at 13:25 UTC, the same page-1 cap; it corroborates the cards, NOT the hitcount — no second source states 8 949, and the sitemaps carry no advertisement at all · 2026-09-11 -->

**The board is 37 600 advertisements by its own header, 8 949 for one query by
its own `hitcount`, and this adapter reads twenty of them per query — not
because it stops, but because the site's rules stop it.** *Every number here is
the site's, and the gap between them is written in `robots.txt`.*

## Two hosts, and only one is ours to read — measured 2026-09-11 13:22–13:23 UTC

```
https://jobindex.dk/robots.txt        47 bytes    User-agent: * / Disallow: /     certain: True
                                       -> the guard refuses even the rules file (rules-refusal, rule "/")
https://www.jobindex.dk/robots.txt  4 218 bytes    md5 a386fea74e6744fec2a68f0a69c43815, stable across two reads
                                       a detailed `*` group, a `sitemap:` line, no Crawl-delay
```

**Every URL this adapter builds is on `www`**, and the guard is asked on each
exact path inside `get()`. *This is the case `shared/robots-policy.md` names
as its residue — «one blanket refusal hidden behind a `www`» — and it is
handled by never building a URL on the apex.*

**What the `www` rules refuse, and what it bounds (guard on each, 13:23 UTC):**

| path | verdict | consequence |
| :-- | :-- | :-- |
| `/`, `/jobsoegning`, `/jobsoegning?q=…`, `/jobsoegning/<area>`, `/vis-job/<tid>`, `/jobannonce/<tid>/<slug>`, `/sitemap.gz` and its five children | **allowed, `certain: True`** | the routes below |
| `/jobsoegning*page=`, `*sort=`, `*jobage=`, `*archive=`, `*radius=` | **Disallow, written** | **page 1 only, no sort, no age filter** — bound 1, honoured by every route |
| `/jobsoegning?*&*&`, `/jobsoegning/*?*&` | **Disallow, written** | **one query parameter** — `q` OR an area path, never two params |
| `/api/`, `/job/*?`, `/jobannonce/korrektur/`, `/jobannonce/embed/` | Disallow | never built |

## The sitemaps carry no advertisement — 7 181 `<loc>`, zero ads

`/sitemap.gz`: 283 bytes ×2, same md5 `23d90aa522cffba4a065e737719f28dc`,
magic `1f 8b` — **decompressed by the bytes, never by the header** (the gzip
trap `shared/never-fail-silently.md` records on this host) — 906 bytes, five
children, all permitted, all read once at 13:23–13:24 UTC:

```
googleforjobs.gz      167 o gz     275 o xml       0 <url>   an honest empty <urlset …/> — the ads sitemap is EMPTY
company.gz         55 218 o gz  598 917 o xml   3 915 <url>   /virksomhed/<id>/<slug>#om-virksomhed — employer pages
content.gz         31 523 o gz  236 227 o xml   1 508 <url>   /cms, /virksomheder, /jobglaede — editorial
area.gz             6 513 o gz   96 686 o xml     759 <url>   /jobsoegning/<area> — search pages, one per area
salaryindex.gz      6 666 o gz  134 398 o xml     999 <url>   /tjek-din-loen/<title> — salary pages
```

**A count of `<loc>` on this host is a count of pages ABOUT jobs.** *The
sitemap route, which was the assignment's expected route, is closed by
content and not by rules: it carries nothing to sweep.*

## Where the data is — the JSON the search page embeds

`/jobsoegning?q=udvikler` answers 200, 393 912 bytes, and its first `<script>`
carries `var Stash = {…}`. Under `jobsearch/result_app.storeData.searchResponse`:

```
hitcount      8949        the site's own total for the query
page_size     20
total_pages   448
results       [20 objects]
link_rss      /jobsoegning.rss?q=udvikler
archive_toggle → ?jobage=archive     (refused in writing; not built)
```

**Each result object, and what the card takes from it:**

| field | card | 20 of 20 |
| :-- | :-- | :-- |
| `tid` — `h1697049`, `o41080` | `id`, `ledger_id: jobindex:<tid>`, `url: /vis-job/<tid>` | yes — the stable key |
| `headline` | `title` | yes |
| `companytext` (else `company.name`) | `company` | yes |
| `area` | `location` — the site's own label, e.g. «København Ø og mulighed for hjemmearbejde» | yes |
| `firstdate` | `firstdate` — the day it went up | yes |
| `lastdate` | `lastdate` — the last day it is shown | yes |
| `apply_deadline` | `apply_deadline` | when the ad has one |
| `is_archived`, `home_workplace` | as named | yes |

**The two dates are the listing's, named for what the site calls them.**
*`firstdate` is the day the ad went up on Jobindex, not the day it was
written; nothing on the card says whether a re-listing resets it, and the
adapter does not derive an age from it.*

**The zero paths, and the anchor beside every count (`_zero.empty_first_page`):**

| what the page carries | what the adapter does |
| :-- | :-- |
| no `Stash` JSON | **dies 6** — size beside the zero, INDETERMINATE (markup moved, or a shell) |
| `results: []` and `hitcount: 0` | **a real zero, said**: the query matched nothing and the site said so — `zzqxjkwvv` at 13:29 UTC |
| `results: []` and `hitcount > 0` | **dies 6** — the two disagree |
| 20 results | `N emitted of 20 returned on page 1; the site states hitcount H over P page(s) of 20. Page 1 is the cap, by the site's own rules` |

**Filters shown to reduce (#219), 13:28–13:29 UTC, one request each:**

```
--q udvikler                  hitcount 8 949   448 pages
--q udvikler --area it        hitcount   502    26 pages
--q sygeplejerske             hitcount 1 768    89 pages
--q zzqxjkwvv                 hitcount     0    a real zero
```

*`--area` takes a path the site's `area.gz` declares (759 of them) or a
category path such as `it/systemudvikling`; with `--q` it is one path plus one
parameter, which the rules permit.*

## The ad has two pages, and neither carries a `JobPosting`

```
/vis-job/h1697049                   200   116 841 o   the canonical page the site shares: teaser + company block
                                                        0 ld+json JobPosting (one WebSite block), 13:26 UTC
/jobannonce/h1697049/ai-udvikler    200    57 567 o   the full text: <h1>, then `<!-- jobtext -->` … the share block
                                                        4 159 characters of Danish, 13:28 UTC
```

**`ad --id <tid>` reads the second through the first**: the slug lives on the
canonical page as a link, and contract 4 (the URL from the id) holds for
`/vis-job/<tid>`; the text page is reached, never composed. Two requests per
ad. When the marker is missing the adapter returns the whole page's text and
says the markup moved.

## Traps

**1. The apex is a wall and the `www` is a door.** `jobindex.dk/robots.txt`
refuses everything; an adapter that read the apex's rules would call the
whole board closed, and one that ignored them would read a refused host.
Build on `www`, ask the guard on every URL.

**2. `hitcount` is the query's, «37.600 job i dag» is the board's.** Two
numbers on the same page, two denominators; the adapter prints the first with
its query and never adds them.

**3. Twenty per query is the RULES' cap, not the adapter's and not the
board's.** `total_pages: 448` is what the site would serve; page 2 is
`Disallow: /jobsoegning*page=`. **A sweep that wants more asks a narrower
question** — an area path, a category path — not a later page.

**4. The RSS is the same twenty.** A second branch for the cards, not a second
source for the total; it says nothing a page-1 read does not.

**5. The sitemaps are honest and empty of ads.** `googleforjobs.gz` is a
self-closing `<urlset/>` — *a complete, valid sitemap holding nothing* — and
the other four hold pages. A reader that counted their 7 181 `<loc>` would
report a board it never saw.

**6. `tid` prefixes.** `h…` and `o…` were seen on 2026-09-11 (`r…` appears in
the rules' own `Disallow: /vis-job/r1671788`); the adapter accepts one letter
and digits and asserts nothing about the letter.

## Pace

One request per query, two per ad with `--with-text`, **spaced 2 s by
`_pace.Pace`** — the host declares no `Crawl-delay`, so the spacing is the
adapter's own, and the host's would replace it the day it declares one. The whole measurement above was 14 requests between 13:22 and 13:29 UTC,
all 200.

## What is not established

**Nothing about the 8 929 advertisements page 1 does not show.** The count is
the site's; the adapter cannot read past 20 by any route the rules permit, and
this card does not claim the 759 area pages partition the board.
**`firstdate` on a re-listed ad** — whether it resets — was not measured.
**The `o…` and `h…` prefixes** — what distinguishes them — was not asked.
