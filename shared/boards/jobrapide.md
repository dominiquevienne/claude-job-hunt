# Board adapter — JobRapide (Chad, and it does not say so)

<!-- verified: 2026-09-07 -->

<!-- hosts: www.jobrapide.org -->
<!-- script: none -->
<!-- countries: TD CM CG CI BJ BI MR ML SD SN -->
<!-- countries-basis: 30 ad slugs from archive pages 1 / 3000 / 6181 of ~6 182 — 20 name a country, 10 name none; TD is 9 of the 20, a PLURALITY and not the whole · 2026-09-07 -->
<!-- content: measured · homepage 236 373 o, 391 internal link OCCURRENCES — 143 `/region/`, 122 `/offres/`, 33 `/secteur/` — which are only 65 DISTINCT `/offres/` URLs; the paginated archive lives at `/recrutement/offres/<category>/page/N/` and announces 6 182 pages at 10-11 ads each, so of the order of 66 000 items, ESTIMATED and never counted; zero `JobPosting`, the `ld+json` is `@type: Article` · 2026-09-07 -->
<!-- witness: the WordPress theme is `tchadcarriere` (`wp-theme-tchadcarriere`), a SECOND and independent witness for Chad — the country no longer rests on one count of mentions; six paths fetched in total · 2026-09-07 -->

**`countries: TD` was NOT read from the domain. The domain names no country at
all** — `jobrapide.org` could be anywhere in francophone Africa, and that is
why this host sat unattributed in a list of nineteen for two days.

## How the country was attributed, and how strong that is

**By counting country names in the homepage body:**

```
tchad   79      congo 16      togo 13      burkina 10      guinée 9
```

**Chad dominates by a factor of five over the next name.** *That is a
mention count on one page — **not an enumeration of advertisements**, and this
card does not pretend otherwise.*

**What it establishes:** the corpus is Chad-centred. **What it does not:** the
share of advertisements per country, or whether the four other names are
sections, syndication, or noise. **`countries:` carries `TD` alone because that
is what the evidence supports; adding the other four would put four countries
into every aggregate on nine to sixteen mentions of a single page.**

*This is the counterpart of the rule that `countries` lists recruitment
jurisdictions rather than workplaces: a jurisdiction still has to be measured
before it is declared.*

### The measurement this card called for now exists — and it widens the line

**The card above says the mention count establishes *what* the corpus is
centred on and not *the share of advertisements per country*. That share has
now been sampled on a better instrument: the advertisement slugs themselves.**

```
30 ad slugs, from archive pages 1 / 3000 / 6181 of about 6 182
20 name a country · 10 name none

TD 9  ·  CM 2 · CG 2 · CI 1 · BJ 1 · BI 1 · MR 1 · ML 1 · SD 1 · SN 1
```

**Chad is nine of the twenty — a plurality, not the whole — and ten distinct
countries appear in thirty advertisements.** *So `TD` alone was not incomplete,
it was **known false**, and the line now carries the ten.*

**Read the ten as ten countries seen in thirty slugs, not as ten countries
measured.** *Thirty slugs against an inventory of roughly 66 000 is 0.05 % of
it. That is enough to establish that this board serves those jurisdictions; it
is **not** enough to move their coverage denominators, which is why the Atlas
was deliberately left alone on 2026-09-07.*

**And the extractor that produced this was wrong before it was right.** *Its
first form had no `burundi` and reported eleven slugs naming no country instead
of ten — a narrow extractor does not return **less**, it returns **false**, and
its silence has the shape of an absence. It was caught only by printing the
unmatched slugs; no total would ever have shown it.*

## Its rules refuse `ClaudeBot` and it serves us

```
GET /            → 200, 235 373 o, « Offres d'emplois, Bourses d'étude, Stage, Formations »
GET /robots.txt  → 200, 1 850 o, the Cloudflare managed block
                   `claudebot` named once · `claude-user` named zero times
                   NO Sitemap line — the route is the facet pages, not a file
```

**It carries scholarships and training beside jobs** — the title says so — **so
a count of pages under `/offres/` is not a count of advertisements until
someone reads them.** *That is the trap `angolaemprego.com` set with news
articles, and it is named here before anyone counts.*

**Somebody read them on 2026-09-07, and the fear was right: scholarships
outnumber recruitment notices.**

```
65 DISTINCT /offres/ URLs on the homepage  (122 link OCCURRENCES — two numbers)

16  /offres/bourses-etude/       scholarships  <- the largest category
10  /offres/avis-appel-offres/   procurement tenders, not advertisements
10  /offres/avis-recrutement/    recruitment notices
 8  /offres/ (no category)
 5  concours · 5 stage · 5 volontaire · 4 formations · 2 call-for-papers
```

> **Jobs are a minority of what this board posts, and the `/offres/` count in
> `content:` is a count of link occurrences, not of advertisements.**

## The pagination, measured rather than guessed

**Neither the homepage nor `/offres/<category>/` is a listing.**
*`/offres/avis-recrutement/` **redirects to a single article** —
`single-post postid-67526` — and only the provenance record showed it, because
`final_url` differed from `url`. Without that field this card would carry
"5 advertisements on 163 KB" measured on a page that is not a list.*

**The archive is the WordPress category route:**

```
/recrutement/offres/avis-recrutement/          body class = archive category-17
  page 1      10 ads    paginator says 6181
  page 3000   11 ads    paginator says 6182
  page 6181   11 ads    paginator says 6182   <- NOT empty
  page 9999   HTTP 404                        <- the announced bound is honest
```

**And the three pages serve different advertisements — 30 distinct out of 32,
the single common link being a sidebar item.** *Without that check, a paginator
that re-serves the same page reads exactly like one that works.*

**Order of magnitude: about 6 182 pages at roughly 10.7 advertisements each,
so of the order of 66 000 — and that is an ESTIMATE from three samples,
never a count.** *Pages 1 and 6181 are the two worst sampling points on their
own, which is why page 3000 is in the set.*

**No structured job data:** the single `ld+json` block declares
`@type: Article`, and `JobPosting` appears zero times. *An adapter here would
have to parse HTML.*

## Pace

`Crawl-delay` is not set. **Eight requests have been made to this host in
total** — the root and the rules file on 2026-09-07 morning, then six on the
same day for the pagination: the homepage again, `/offres/avis-recrutement/`,
the archive and its pages 3000, 6181 and 9999. **Every one went through
`bin/fetch-body.py`, with the guard taken on the exact path in a turn of its
own.**
