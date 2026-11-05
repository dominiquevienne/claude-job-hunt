# Board measurement — Vagas CV (`www.vagascv.info`, Cabo Verde): «VAGAS CABO VERDE» — «the largest employment portal in Cabo Verde» by its own description, a Blogger blog of vacancies, internships, competitions and visas (labels), served to the declared client (494 KB, identical twice) with its Blogger feed declared, rules open; no adapter yet

<!-- verified: 2026-11-05 -->

<!-- hosts: www.vagascv.info -->
<!-- script: none -->
<!-- countries: CV -->
<!-- content: measured · **the root (200, 494 326 B, md5 57874207610e identical on two reads) is a Blogger blog — posts with «1 vaga» in their text, labels (`/search/label/Vistos` …), the feeds `/feeds/posts/default` and `?alt=rss` declared; no total on the root, no JobPosting; `_robots.allowed('www.vagascv.info','/')` → open, certain; the feed and the posts not read** · 2026-09-18 -->
<!-- witness: NONE, and the one this card promised is REFUSED IN WRITING — the Blogger feed’s `openSearch:totalResults` is unreachable, `www.vagascv.info` writing `Disallow: /feeds*` to `User-agent: *` (measured 2026-11-05, `state: read`, `certain: True`). The allowed enumerator is `/sitemap.xml`, which states nothing and LISTS 405 post paths; a count of `<loc>` names a SIZE and never a nature, and whether a second sitemap page exists beyond the 405 is NOT established · 2026-11-05 -->

## The route this card and its issue both name is refused in writing

*Measured on the fifth of November, two thousand and twenty-six, under the adapter issue for Vagas CV — the heading carries no figure on purpose, so this card stays OUT of the population of the heading/`content:` guard rather than inside it on an accident: that guard is satisfied by ANY shared digit, and the sibling card `vagaservisu.md` passes it on a digit of an `md5`.*

**Measured 11:1x–11:2x UTC by the declared client, the guard taken on the exact
path in a turn DISTINCT from the retrieval.** The 2026-09-18 line above says the
guard was «open, certain» — that was true of the **root** and is false of the
**feed**, and nothing in the phrase separates the two.

```
_robots.allowed('www.vagascv.info', '/feeds/posts/default')
  -> allowed=False  state=read  certain=True  kind=disallow  rule='/feeds*'
```

The host **writes** this refusal and it aims at `User-agent: *`, not at a named
crawler, so **borne 1** applies: a `Disallow` on our path blocks every route, the
browser included. `bin/fetch-body.py` refuses it of its own accord, so the borne is
held by the instrument and not only by discipline.

> **And the apex is not a loophole.** `vagascv.info` without `www` returns
> `allowed=True` for the same path. Using it would circumvent a written refusal
> through a sibling host, which borne 1 forbids by every route. Written down here so
> that nobody «discovers» it as an opening.

**The refusal is ARTICULATE, so it changes the route instead of closing the board** —
this is «not by that path», never a §2 sexies closure, and nothing here needs the
owner's validation:

| path | what the rules write |
| :-- | :-- |
| `/feeds*` | **refused** — the route this card and #694 both name |
| `/search*` | **refused** — the label and search pages, so the labels are not a route either |
| `/*.html` | **an EXPLICIT `Allow`** — the editor deliberately opened the posts |
| `/sitemap.xml` | allowed, by absence of any rule |

**And the allowed route is RICHER than the refused one.** The enumerator is the
sitemap — `https://www.vagascv.info/sitemap.xml`, 200, 50 137 B — which lists **405
`<loc>`, all distinct, all post paths `/yyyy/mm/slug.html`**, no CDATA, no
per-language over-counting (first segments 2026 ×207, 2025 ×188, 2024 ×8, 2023 ×2),
`lastmod` from 2024-10-31 to 2026-11-04. *A single `urlset` and not a
`sitemapindex`: whether a second page exists beyond the 405 is **NOT established**.*

And the posts carry a structured `JobPosting`, which the feed would not have given.
Three members opened — the **first, the median and the last** of the sitemap, never
the first three — and they return **three different results**:

| member | its `application/ld+json` |
| :-- | :-- |
| `2026/11/camareira-andares-lavanderia` | a **clean** `JobPosting`: `title`, `datePosted`, `validThrough`, `employmentType: FULL_TIME`, `description`, `hiringOrganization: Barceló Hotel Group`, `addressRegion: Santiago`, `addressCountry: CV` |
| `2025/12/comercial-gestor-de-clientes` | **UNREADABLE** — `json.loads` raises `Invalid control character at line 5 column 2065`: bare control characters inside a JSON string |
| `2023/10/comunicado` | **ZERO block** |

**And the first count said «JobPosting: True» on all three, which was a false positive
of our own motif** — it searched for `application/ld+json` anywhere in a page whose
template mentions it. *Counting a string on a page that TALKS about that string yields
a false fact* — the same defect this repository already records for `<script>`,
one object further along. *The rule is not cited by name here: no file of the
repository may cite the local rules file, which is gitignored, so the citation
resolves on a working copy and NOT on a checkout — and the guard that catches it
reads names in BACKTICKS only, which is why five cards carry the bare name and
escape it.*

**WHAT IS NOT ESTABLISHED, and each of the three decides a branch of the adapter.** A
denominator of **3** is not a rate: the share of posts whose `JobPosting` is
MALFORMED — a bare `json.loads` would lose them in silence, and «0 adverts» reads
like an empty board; the share with NO block, and whether an absence means «this is
not a vacancy», which would be a better discriminant than the labels but is a
hypothesis and not a measurement; and whether a second sitemap page exists.

**THE GROUP THAT BINDS US, READ WHOLE — and it carries two things a path-by-path
probe does not show.** The rules were READ (`state: read`, `certain: True`), so the
answer about the rate is definite and not an ignorance:

```
User-agent: *                 # to select all crawling bots and search engines
Disallow: /search*            # to block all user generated query item
Disallow: /20*                # this line will disallow archieve section of Blogger
Disallow: /feeds*             # this line will disallow feeds
Allow:    /*.html             # allow all post and pages of the blog
Sitemap:  https://www.vagascv.info/sitemap.xml
Sitemap:  https://www.vagascv.info/sitemap-pages.xml
```

**NO `Crawl-delay` is written, for any agent** — so the host says «yes» without
saying «at this rate», and **the rate is OURS: 3 s, as on the sibling Blogger
card.** A rules file that writes its delay tells us how to respect it; a file that
is silent does not tell us there is none, and the only way to learn where an
unwritten threshold sits is to cross it, so we do not learn it.

> **`Disallow: /20*` would read as forbidding every post** — every post path begins
> `/2026/`, `/2025/` — and it does NOT, because `Allow: /*.html` is the more
> specific match and the library resolves the post paths to `allowed=True` with
> `rule='/*.html'`. **And here the standard's resolution and the editor's INTENTION
> coincide, which is why it is safe**: the intention is written in the comments —
> block Blogger's month ARCHIVE listings (`/2026/11/`, which carry no `.html`),
> allow the posts. So §3 bis's «honour the intention, not the prefix match» is
> satisfied in the same direction, not against it. *Written down because a card that
> showed only `/20*` would read as a closed board.*

**And a SECOND sitemap is declared** — `sitemap-pages.xml` beside `sitemap.xml` —
which answers one of the three open questions above: the 405 are the POSTS, and the
pages are enumerated apart. Neither was walked today.

*So this card's route line stays unwritten rather than carrying a figure that
describes something else, and the work that remains is an adapter on a NEW route —
sitemap plus the posts' `JobPosting`, with a JSON repair and an HTML fallback — and
not the `empleosenuruguay.py` shape that #694's body announces.*


**Found by the Cabo Verde search of #614 (a country never searched),
measured 2026-09-18 06:42–06:45 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #614: one Portuguese search naming the public employment institute
(IEFP and its PEPE platform) and the private aggregator, no composed host
names. *A measurement, not an adapter.*

```
_robots.allowed('www.vagascv.info', '/')   open, certain
GET https://www.vagascv.info/               200 ×2, identical — a Blogger blog, labels, the feed declared
```

**A Blogger blog, the `empleosenuruguay.md` shape**: the feed on the
blog's own host states its total and pages by `start-index` — the
adapter's first line (its `adapter` issue).
