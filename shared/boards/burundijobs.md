# Board adapter — BurundiJobs (Burundi)

<!-- verified: 2026-09-07 -->

<!-- hosts: www.burundijobs.bi -->
<!-- script: none -->
<!-- countries: BI -->
<!-- content: measured · homepage read in full, 237 083 o, WP Job Manager shape — 28 `/job/`, 34 `/employer/`, 18 `/location/` links and one `ld+json` block; the declared sitemap index was NOT read · 2026-09-07 -->
<!-- witness: none found — nothing beyond the homepage and `robots.txt` was fetched, so no second path to any count exists yet -->

**Burundi had zero boards in this repository until today.** No card declared a
single Burundian host, and this one serves us.

## It was classed "refuses at transport" for two days, and it never refused

**Its `robots.txt` names `ClaudeBot` at `Disallow: /` and never names
`Claude-User`**, which the `*` group leaves open. **Under the owner's decision
of 2026-09-05 — one permitted token is enough — the permitted token is
`Claude-User`, and the host answers `200` to it.**

```
GET /            → 200, 237 083 o, « offres d'emplois - burundijobs »
GET /robots.txt  → 200, 2 012 o, the Cloudflare managed block plus its own lines
                   `claudebot` named once · `claude-user` named zero times
Sitemap: https://www.burundijobs.bi/sitemap_index.xml
```

**Why it was wrong before.** *This host sat in a population of nineteen filed
as "the rules open and the transport refuses". **That measurement was taken by
a tool that sent a Chrome `User-Agent` and returned success on any HTTP code**,
and it left no provenance record. When the population was re-measured on
2026-09-07 with the declared identity and a record, **four of the nineteen
answered `200`. This is one of them.***

**The lesson is not "re-verify": it is that both faults of that tool pushed
toward the same conclusion.** A browser identity passes where ours would be
refused, and a success on any code turns a refusal into a body.

## What is measured and what is not

**Measured:** the homepage, in full, and the rules file. **Its shape is WP Job
Manager** — the same family as `jobsearchzm.md` and `jobzambia.md`, which
suggests `/job/<slug>/` advertisement pages and a `job_listing` sitemap, **and
that is a suggestion, not a reading.**

**Not measured:** the sitemap index, any advertisement, any count. **No number
of advertisements appears in this card on purpose** — the homepage carries 28
`/job/` links and that is a page of links, not an inventory.

## Pace

`Crawl-delay` is not set. One request per host per pass was used to write this.
