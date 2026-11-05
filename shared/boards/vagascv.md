# Board measurement — Vagas CV (`www.vagascv.info`, Cabo Verde): «VAGAS CABO VERDE» — «the largest employment portal in Cabo Verde» by its own description, a Blogger blog of vacancies, internships, competitions and visas (labels), served to the declared client (494 KB, identical twice) whose Blogger feed it declares and whose rules REFUSE it in writing while an explicit `Allow: /*.html` opens the posts — so `vagascv.py` enumerates by the SITEMAP and reads each POST PAGE since 2026-11-05, the JSON-LD being the theme’s own authoring artefact and a bonus

<!-- verified: 2026-11-05 -->

<!-- hosts: www.vagascv.info -->
<!-- script: vagascv.py -->
<!-- route: http · 405 · 2026-11-05 -->
<!-- countries: CV -->
<!-- content: measured · **the root (200, 494 326 B, md5 57874207610e identical on two reads) is a Blogger blog — posts with «1 vaga» in their text, labels (`/search/label/Vistos` …), the feeds `/feeds/posts/default` and `?alt=rss` declared; no total on the root, no JobPosting; `_robots.allowed('www.vagascv.info','/')` → open, certain; the feed and the posts not read** · 2026-09-18 -->
<!-- witness: NONE, and the one this card promised is REFUSED IN WRITING — the Blogger feed’s `openSearch:totalResults` is unreachable, `www.vagascv.info` writing `Disallow: /feeds*` to `User-agent: *` (measured 2026-11-05, `state: read`, `certain: True`). The allowed enumerator is `/sitemap.xml`, which states nothing and LISTS 405 post paths; a count of `<loc>` names a SIZE and never a nature, and the 405 are now ESTABLISHED to exhaust the posts — `?page=1` returns them so the parameter is HONOURED, `?page=2` returns an EMPTY urlset, and `sitemap-pages.xml` holds 16 static pages and ZERO post · 2026-11-05 -->

## The adapter, shipped — the sitemap enumerates and the POST PAGE is the record

**`vagascv.py` is shipped.** The route this card and #694 both named is refused IN
WRITING, and the section above measures that; what follows is the route that works.

**THE THREE QUANTITIES THE SECTION ABOVE LEFT UNESTABLISHED ARE NOW MEASURED**, on 26
posts spread across the whole sitemap — every 15th, index 0 to 375 — and never the
newest 26, because a date-ordered sample selects a GENRE and not a rate:

```
no `application/ld+json` block at all   18/26   69 %
a block that will not parse              7/26   27 %
a clean block                             1/26    4 %
```

**And all eighteen without a block are plainly vacancies** — «Su-Chef de Cozinha»,
«Engenheiro Civil», «Rececionista», «Mecânico de Primeira». *So the hypothesis that an
absent block means «this is not a vacancy» is REFUTED*: an adapter built on the JSON-LD
would emit 8 of 26 and lose eighteen real adverts. **The cause is in the page, and it
settles the design: the theme's own script GENERATES the block at authoring time**
(`return { html: html, code: html + '<script type=…ld+json'`), so it is absent when the
author skipped the widget and malformed when a field was left blank. Hence the record is
read from the PAGE and the block is a BONUS the record never depends on.

The malformations are TWO superposed defects: a bare control character inside the
`description` string, which `strict=False` accepts, and then `"minValue": ,` /
`"maxValue": ,` — an empty value it does not. Both are handled; an irreparable block
returns `None` rather than a guess.

**And the sitemap EXHAUSTS the posts**, which is measured and not assumed: `?page=1`
returns the 405 — so the parameter is HONOURED — while `?page=2` returns an EMPTY
`urlset`, so the empty page is an answer and not an ignored argument; and the second
declared sitemap, `sitemap-pages.xml`, holds **16 static `/p/` pages and ZERO post**.

**THE PAGE CARRIES EVERYTHING, 26/26** on the same spread sample: `<h1
class='vcv-vsrc__title'>`, `og:title`, `og:url`, `data-id`, `data-url`, an ISO timestamp
beside `data-id`, the post's own label anchors, and a named body container
(`vcv-vsrc__body`, 26/26) whose extracted text runs 1 117 to 4 134 characters.

> **The attributes are written with SINGLE quotes, and a first probe that assumed double
> ones reported every field ABSENT.** The motif is tried on the form the data has AT THE
> POINT OF CALL — and the same lesson bit twice more here: an unscoped label motif named
> the BLOG's taxonomy while claiming the POST's (29 label links on one page — 11 in a
> dropdown, 11 in the sidebar, 5 in the footer, and two from a template COMMENT that
> mentions `/search/label/` in prose, **the third time on this host that the page talks
> about itself**), and a motif written through a shell heredoc arrived with a doubled
> backslash and could match nothing. *What caught the last one was that the field
> CONTRADICTED a specimen already measured, never a re-reading.*

**THE CONTACTS ARE REAL, AND THE AFFILIATE BLOCK IS DROPPED CONDITIONALLY.** 21 of those
26 bodies (81 %) carry a recruiter's e-mail and 3 a telephone. `withheld_fields` names
what was ACTUALLY removed and the declaration goes through the repository's single point
of judgement, never the truthiness of that list. The phone pattern is Cabo Verde's own
(`+238`, seven digits beginning 2, 5 or 9) and was tried **in both directions against the
escudo**, the country's currency: `50.000$00`, `100 000$00`, `CVE 60000`,
`1.500.000$00` and `75.000 escudos` are untouched. *Residue declared: a BARE seven-digit
amount beginning 2, 5 or 9 would be taken for a number; zero such amount appears in the
26 bodies, so this is a measured risk and not a measured defect.*

And the author pastes an `elementskit_alert` box of `go.hotmart.com` affiliate links
INSIDE the advert — 17 of 26 bodies carried it. It is dropped **only when it carries an
affiliate link**, never on the class alone, because a legitimate notice is written in the
same box and an over-redaction is the one defect whose output does not differ from a
well-conducted discretion. The close is found by COUNTING `<div>`/`</div>`, the block
nesting an `alert_message`.

```
GET /sitemap.xml                       200, 50 137 B — 405 <loc>, all distinct, all post paths
GET /sitemap.xml?page=1 / ?page=2      200 — 405 <loc> / an EMPTY urlset (so the param is honoured)
GET /sitemap-pages.xml                 200, 1 776 B — 16 static /p/ pages, ZERO post
GET /<yyyy>/<mm>/<slug>.html  x26      200 x26 — spread every 15th over the 405
vagascv.py list --max 3                3 emitted, labels per post, contacts withheld on 3/3
vagascv.py ad --url <a blockless post> a COMPLETE record with `ldjson: false`
```

*What it will never give: the recruiters' contacts, and the employers' own application
routes are never followed. `/feeds*` and `/search*` are never requested — the labels are
read from the LINK TEXTS of a page already held — and the apex is never asked, its
`allowed=True` on the refused paths being a sibling-host circumvention and not an opening.*


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
