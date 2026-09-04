# Assessed — Bayt.com: the rules permit, Cloudflare refuses, the browser reads

<!-- verified: 2026-09-03 -->
<!-- hosts: www.bayt.com -->
<!-- countries: AE SA EG JO LB KW QA BH OM MA -->

The largest job site in the Middle East and North Africa. **No adapter, and
the reason is a layer, not a policy.**

## Three answers, from three different layers

**`robots.txt` permits the country paths and refuses the generic search.**
Checked per path, which is the only way to see it:

```
True   /en/saudi-arabia/jobs/            (country listing)
True   /en/saudi-arabia/jobs/?page=2     (its pagination)
True   /en/uae/jobs/
False  /en/jobs/?page=2                  Disallow: /en/jobs/?
False  /en/jobs/engineering-jobs/        Disallow: /en/jobs/*-jobs/
```

The refusals are the **generic** search and the category landings, in all
three languages; the country listings are open. A host-level check says
`sweep: True` and tells you nothing about either.

**Cloudflare refuses every scripted request.** 403 with a 5 507-byte
*"Attention Required!"* interstitial on `/`, on `/en/jobs/`, on
`/en/uae/jobs/`, and on `/sitemap.xml` — with ordinary browser headers.
`robots.txt` itself is served normally, which is how the two layers are told
apart: **the rules are readable and the site is not.**

**The browser reads it in full.** `/en/saudi-arabia/jobs/` renders 30
advertisements with title, employer, city, salary band, seniority, experience
and posting age. **So this is a bot wall, not a refusal** — and the two must
not be recorded as the same thing. `shared/robots-policy.md` is the file that
governs consent; this is not a consent question.

## Three different totals on one page, and they do not agree

Read 2026-09-03 on `/en/saudi-arabia/jobs/`:

| where on the page | Saudi Arabia | Riyadh | Jeddah | Qatif |
|---|---|---|---|---|
| header | **5.8K jobs found** | | | |
| SEO prose, foot of page | **6 876** | 1 703 | 345 | 210 |
| sidebar facet counts | | **1 664** | **332** | **153** |

**Every pair disagrees.** The header and the prose differ by about a thousand;
the prose and the facets differ city by city, by 39, 13 and 57. The date facet
adds a fourth: *Past 30 days (2 857)* against a total of 5 800.

**Whichever number a person quotes, the page contains at least two that
contradict it.** This is the shape this repository keeps meeting — *a board's
reported total is not a count* — with the unusual courtesy of publishing the
contradiction in one view. **Anyone writing an adapter here must count rows.**

## Why there is no adapter

Not consent, and not shape. **The site is unreachable from a script and
readable in the browser**, so any read happens in the user's own session — the
same conclusion `shared/robots-policy.md` records for other walled hosts.
There is no scripted route to build on, and building one that pretends
otherwise would produce a Cloudflare interstitial parsed as a board.

**The check that separates the layers is one request**: fetch `robots.txt`
and one page. If the first is served and the second is a 5 507-byte
interstitial, the wall is Cloudflare's and the rules have said nothing.
