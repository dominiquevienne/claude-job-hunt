# Board adapter — JobRapide (Chad, and it does not say so)

<!-- verified: 2026-09-07 -->

<!-- hosts: www.jobrapide.org -->
<!-- script: none -->
<!-- countries: TD -->
<!-- content: measured · homepage read in full, 235 373 o, 391 internal links — 143 `/region/`, 122 `/offres/`, 33 `/secteur/` — and one `ld+json` block; no sitemap is declared and none was read · 2026-09-07 -->
<!-- witness: none found — nothing beyond the homepage and `robots.txt` was fetched -->

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

## Pace

`Crawl-delay` is not set. Two requests were made in total: the root and the
rules file.
